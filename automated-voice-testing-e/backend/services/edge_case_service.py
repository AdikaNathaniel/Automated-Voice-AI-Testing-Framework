"""
Service layer for managing EdgeCase records.

Provides CRUD helpers, lightweight categorisation heuristics, and search
utilities to support the edge case library workflows.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from models.edge_case import EdgeCase
from models.pattern_group import EdgeCasePatternLink
from services.notification_service import (
    get_notification_service,
    NotificationServiceError,
)

logger = logging.getLogger(__name__)


def _normalise_tags(tags: Optional[Iterable[str]]) -> List[str]:
    """Lower-case, deduplicate, and sort tag values."""
    if not tags:
        return []
    cleaned = {tag.strip().lower() for tag in tags if tag and tag.strip()}
    return sorted(cleaned)


def _normalise_title(title: str) -> str:
    """Trim whitespace and collapse repeated spaces in titles."""
    collapsed = " ".join(title.strip().split())
    return collapsed


def _normalise_description(description: Optional[str]) -> Optional[str]:
    if description is None:
        return None
    return " ".join(description.strip().split())


# NOTE: Severity is now manual-only - no auto-calculation
# Users assign severity based on their organization's priorities and context

CATEGORY_KEYWORDS: Dict[str, Sequence[str]] = {
    "audio_quality": ("audio", "noise", "static", "distortion", "volume"),
    "ambiguity": ("ambiguous", "ambiguity", "multiple", "confus", "unclear"),
    "context_loss": ("context", "memory", "follow-up", "previous"),
    "localization": ("locale", "language", "translation"),
}


class EdgeCaseService:
    """Encapsulates EdgeCase persistence and domain-specific helpers."""

    def __init__(self, session: Session) -> None:
        self.session = session

    # ---------------------------------------------------------------------
    # CRUD operations
    # ---------------------------------------------------------------------
    def create_edge_case(
        self,
        *,
        tenant_id: UUID,
        title: str,
        description: Optional[str] = None,
        scenario_definition: Optional[Dict[str, Any]] = None,
        tags: Optional[Iterable[str]] = None,
        severity: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        script_id: Optional[UUID] = None,
        discovered_date: Optional[Any] = None,
        discovered_by: Optional[UUID] = None,
    ) -> EdgeCase:
        edge_case = EdgeCase(
            tenant_id=tenant_id,
            title=_normalise_title(title),
            description=_normalise_description(description),
            scenario_definition=scenario_definition or {},
            tags=_normalise_tags(tags),
            severity=severity.lower() if isinstance(severity, str) else severity,
            category=category,
            status=(status or "active").lower() if isinstance(status, str) else (status or "active"),
            script_id=script_id,
            discovered_date=discovered_date,
            discovered_by=discovered_by,
        )
        self.session.add(edge_case)
        self.session.commit()
        self.session.refresh(edge_case)

        # Send notification for edge case discovery (critical/high severity only)
        try:
            notification_service = get_notification_service()
            edge_case_url = f"/edge-cases/{edge_case.id}"  # Relative URL for frontend
            # Get scenario name from script if available
            scenario_name = None
            if script_id:
                scenario_name = str(script_id)  # Use script_id as fallback

            asyncio.run(notification_service.notify_edge_case_created(
                edge_case_id=str(edge_case.id),
                title=edge_case.title or "Untitled Edge Case",
                category=edge_case.category or "uncategorized",
                severity=edge_case.severity or "medium",
                edge_case_url=edge_case_url,
                scenario_name=scenario_name,
                description=edge_case.description,
            ))
            logger.info(f"Sent notification for edge case {edge_case.id}")
        except NotificationServiceError as e:
            # Log but don't fail - notifications shouldn't break core functionality
            logger.warning(f"Failed to send edge case notification: {e}")
        except Exception as e:
            logger.warning(f"Unexpected error sending edge case notification: {e}")

        return edge_case

    def get_edge_case(
        self,
        edge_case_id: UUID,
        tenant_id: UUID,
    ) -> EdgeCase:
        """
        Get edge case by ID, scoped to tenant.

        Args:
            edge_case_id: The edge case UUID
            tenant_id: REQUIRED - The tenant UUID for data isolation

        Returns:
            EdgeCase if found within tenant scope

        Raises:
            ValueError: If edge case not found or not owned by tenant
        """
        stmt = select(EdgeCase).where(
            and_(
                EdgeCase.id == edge_case_id,
                EdgeCase.tenant_id == tenant_id,
            )
        )
        result = self.session.execute(stmt).scalar_one_or_none()
        if result is None:
            raise ValueError(f"Edge case {edge_case_id} not found")
        return result

    def update_edge_case(
        self,
        edge_case_id: UUID,
        tenant_id: UUID,
        **data: Any,
    ) -> EdgeCase:
        """Update edge case, scoped to tenant."""
        edge_case = self.get_edge_case(edge_case_id, tenant_id=tenant_id)

        for field, value in data.items():
            if field == "title" and value is not None:
                setattr(edge_case, "title", _normalise_title(value))
            elif field == "description":
                setattr(edge_case, "description", _normalise_description(value))
            elif field == "tags" and value is not None:
                setattr(edge_case, "tags", _normalise_tags(value))
            elif field == "scenario_definition" and value is not None:
                setattr(edge_case, "scenario_definition", value)
            elif hasattr(edge_case, field):
                setattr(edge_case, field, value)

        self.session.commit()
        self.session.refresh(edge_case)
        return edge_case

    def delete_edge_case(self, edge_case_id: UUID, tenant_id: UUID) -> bool:
        """Delete edge case, scoped to tenant."""
        edge_case = self.get_edge_case(edge_case_id, tenant_id=tenant_id)
        self.session.delete(edge_case)
        self.session.commit()
        return True

    # ---------------------------------------------------------------------
    # Listing & searching
    # ---------------------------------------------------------------------
    def list_edge_cases(
        self,
        tenant_id: UUID,
        filters: Optional[Dict[str, Any]] = None,
        pagination: Optional[Dict[str, int]] = None,
    ) -> Tuple[List[EdgeCase], int]:
        """
        List edge cases scoped to tenant.

        Args:
            tenant_id: REQUIRED - The tenant UUID for data isolation
            filters: Optional filters (status, category, severity, etc.)
            pagination: Optional pagination (skip, limit)

        Returns:
            Tuple of (list of EdgeCases, total count)
        """
        filters = filters or {}
        pagination = pagination or {}

        entries = self._fetch_filtered_entries(tenant_id, filters, include_tags=True)
        total = len(entries)
        sliced = self._apply_pagination(entries, pagination)
        return sliced, total

    def search_edge_cases(
        self,
        *,
        tenant_id: UUID,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        pagination: Optional[Dict[str, int]] = None,
    ) -> Tuple[List[EdgeCase], int]:
        """
        Search edge cases scoped to tenant.

        Args:
            tenant_id: REQUIRED - The tenant UUID for data isolation
            query: Search query string
            filters: Optional filters
            pagination: Optional pagination

        Returns:
            Tuple of (list of matching EdgeCases, total count)
        """
        filters = filters or {}
        pagination = pagination or {}

        candidates = self._fetch_filtered_entries(tenant_id, filters, include_tags=True)
        lowered = query.lower().strip()
        filtered = [
            edge_case
            for edge_case in candidates
            if (
                lowered in (edge_case.title or "").lower()
                or lowered in (edge_case.description or "").lower()
                or any(lowered in tag.lower() for tag in edge_case.tags or [])
            )
        ]
        total = len(filtered)
        sliced = self._apply_pagination(filtered, pagination)
        return sliced, total

    # ---------------------------------------------------------------------
    # Categorisation
    # ---------------------------------------------------------------------
    def categorize_edge_case(
        self,
        edge_case_id: UUID,
        tenant_id: UUID,
        *,
        signals: Optional[Dict[str, Any]] = None,
    ) -> EdgeCase:
        """Categorize edge case, scoped to tenant."""
        edge_case = self.get_edge_case(edge_case_id, tenant_id=tenant_id)
        signals = signals or {}

        corpus = " ".join(
            filter(
                None,
                [
                    edge_case.title or "",
                    edge_case.description or "",
                    " ".join(edge_case.tags or []),
                ],
            )
        ).lower()

        inferred_category = edge_case.category
        for category, keywords in CATEGORY_KEYWORDS.items():
            if any(keyword in corpus for keyword in keywords):
                inferred_category = category
                break
        if inferred_category is None:
            inferred_category = "other"

        # Update category only - severity remains manual-only
        edge_case.category = inferred_category
        self.session.commit()
        self.session.refresh(edge_case)
        return edge_case

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _fetch_filtered_entries(
        self,
        tenant_id: UUID,
        filters: Dict[str, Any],
        *,
        include_tags: bool = False,
    ) -> List[EdgeCase]:
        """Fetch edge cases filtered by tenant and additional filters."""
        stmt = select(EdgeCase)
        # ALWAYS filter by tenant_id first for data isolation
        conditions = [EdgeCase.tenant_id == tenant_id]

        status = filters.get("status")
        if status:
            conditions.append(EdgeCase.status == status)

        category = filters.get("category")
        if category:
            conditions.append(EdgeCase.category == category)

        severity = filters.get("severity")
        if severity:
            conditions.append(EdgeCase.severity == severity)

        discovered_by = filters.get("discovered_by")
        if discovered_by:
            conditions.append(EdgeCase.discovered_by == discovered_by)

        script_id = filters.get("script_id")
        if script_id:
            conditions.append(EdgeCase.script_id == script_id)

        # Filter by pattern group - edge cases linked to a specific pattern
        pattern_group_id = filters.get("pattern_group_id")
        if pattern_group_id:
            # Subquery to get edge_case_ids belonging to the pattern group
            linked_ids_subquery = (
                select(EdgeCasePatternLink.edge_case_id)
                .where(EdgeCasePatternLink.pattern_group_id == pattern_group_id)
            )
            conditions.append(EdgeCase.id.in_(linked_ids_subquery))

        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.order_by(EdgeCase.created_at.desc())
        entries = list(self.session.execute(stmt).scalars())

        tags_filter = filters.get("tags") or []
        if include_tags and tags_filter:
            required_tags = {tag.strip().lower() for tag in tags_filter if tag}

            def has_tags(edge_case: EdgeCase) -> bool:
                available = {tag.lower() for tag in edge_case.tags or []}
                return required_tags.issubset(available)

            entries = [edge_case for edge_case in entries if has_tags(edge_case)]

        return entries

    @staticmethod
    def _apply_pagination(
        items: List[EdgeCase],
        pagination: Dict[str, int],
    ) -> List[EdgeCase]:
        if not items:
            return []
        skip = max(pagination.get("skip", 0), 0)
        limit = pagination.get("limit")
        if limit is None or limit < 0:
            return items[skip:]
        return items[skip : skip + limit]
