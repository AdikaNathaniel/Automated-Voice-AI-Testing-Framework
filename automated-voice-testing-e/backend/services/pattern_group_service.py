"""
Service layer for managing PatternGroup records.

Provides CRUD operations and query utilities for pattern groups.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID
from datetime import datetime

from sqlalchemy import and_, select, desc, func
from sqlalchemy.orm import Session

from models.pattern_group import PatternGroup, EdgeCasePatternLink
from models.edge_case import EdgeCase


class PatternGroupService:
    """Encapsulates PatternGroup persistence and query operations."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create_pattern_group(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        pattern_type: Optional[str] = None,
        severity: str = "medium",
        status: str = "active",
        suggested_actions: Optional[List[str]] = None,
        pattern_metadata: Optional[Dict[str, Any]] = None,
    ) -> PatternGroup:
        """
        Create a new pattern group.

        Args:
            name: Pattern group name
            description: Detailed description
            pattern_type: Type of pattern (semantic, entity, etc.)
            severity: Severity level (critical, high, medium, low)
            status: Status (active, resolved, monitoring)
            suggested_actions: List of recommended actions
            pattern_metadata: Additional metadata

        Returns:
            Created PatternGroup instance
        """
        pattern_group = PatternGroup(
            name=name.strip(),
            description=description.strip() if description else None,
            pattern_type=pattern_type,
            severity=severity,
            status=status,
            suggested_actions=suggested_actions or [],
            pattern_metadata=pattern_metadata or {},
            first_seen=datetime.utcnow(),
            last_seen=datetime.utcnow(),
            occurrence_count=0,
        )

        self.session.add(pattern_group)
        self.session.commit()
        self.session.refresh(pattern_group)

        return pattern_group

    def get_pattern_group(self, pattern_group_id: UUID) -> PatternGroup:
        """
        Retrieve pattern group by ID.

        Args:
            pattern_group_id: Pattern group UUID

        Returns:
            PatternGroup instance

        Raises:
            ValueError: If pattern group not found
        """
        stmt = select(PatternGroup).where(PatternGroup.id == pattern_group_id)
        pattern_group = self.session.execute(stmt).scalar_one_or_none()

        if not pattern_group:
            raise ValueError(f"Pattern group {pattern_group_id} not found")

        return pattern_group

    def update_pattern_group(
        self,
        pattern_group_id: UUID,
        **updates: Any,
    ) -> PatternGroup:
        """
        Update pattern group fields.

        Args:
            pattern_group_id: Pattern group UUID
            **updates: Fields to update

        Returns:
            Updated PatternGroup instance

        Raises:
            ValueError: If pattern group not found
        """
        pattern_group = self.get_pattern_group(pattern_group_id)

        for field, value in updates.items():
            if hasattr(pattern_group, field):
                if field == "name" and value:
                    value = value.strip()
                elif field == "description" and value:
                    value = value.strip()
                setattr(pattern_group, field, value)

        pattern_group.updated_at = datetime.utcnow()
        self.session.commit()
        self.session.refresh(pattern_group)

        return pattern_group

    def delete_pattern_group(self, pattern_group_id: UUID) -> None:
        """
        Delete pattern group by ID.

        Args:
            pattern_group_id: Pattern group UUID

        Raises:
            ValueError: If pattern group not found
        """
        pattern_group = self.get_pattern_group(pattern_group_id)
        self.session.delete(pattern_group)
        self.session.commit()

    def list_pattern_groups(
        self,
        filters: Optional[Dict[str, Any]] = None,
        pagination: Optional[Dict[str, int]] = None,
    ) -> Tuple[List[PatternGroup], int]:
        """
        List pattern groups with optional filters and pagination.

        Args:
            filters: Filter criteria (status, severity, pattern_type)
            pagination: Pagination params (skip, limit)

        Returns:
            Tuple of (pattern_groups, total_count)
        """
        filters = filters or {}
        pagination = pagination or {}

        conditions = []

        if "status" in filters:
            conditions.append(PatternGroup.status == filters["status"])
        if "severity" in filters:
            conditions.append(PatternGroup.severity == filters["severity"])
        if "pattern_type" in filters:
            conditions.append(PatternGroup.pattern_type == filters["pattern_type"])

        stmt = select(PatternGroup)
        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.session.execute(count_stmt).scalar() or 0

        # Apply ordering (most recent first, then by occurrence)
        stmt = stmt.order_by(
            desc(PatternGroup.last_seen),
            desc(PatternGroup.occurrence_count)
        )

        # Apply pagination
        skip = pagination.get("skip", 0)
        limit = pagination.get("limit", 50)
        stmt = stmt.offset(skip).limit(limit)

        pattern_groups = list(self.session.execute(stmt).scalars().all())

        return pattern_groups, total

    def get_pattern_with_edge_cases(
        self,
        pattern_group_id: UUID,
        limit: int = 50
    ) -> Tuple[PatternGroup, List[EdgeCase], int]:
        """
        Get pattern group with its linked edge cases.

        Args:
            pattern_group_id: Pattern group UUID
            limit: Maximum edge cases to return

        Returns:
            Tuple of (pattern_group, edge_cases, total_count)
        """
        pattern_group = self.get_pattern_group(pattern_group_id)

        # Query edge cases linked to this pattern
        stmt = (
            select(EdgeCase)
            .join(
                EdgeCasePatternLink,
                EdgeCasePatternLink.edge_case_id == EdgeCase.id
            )
            .where(EdgeCasePatternLink.pattern_group_id == pattern_group_id)
            .order_by(desc(EdgeCasePatternLink.added_at))
        )

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.session.execute(count_stmt).scalar() or 0

        # Apply limit
        stmt = stmt.limit(limit)
        edge_cases = list(self.session.execute(stmt).scalars().all())

        return pattern_group, edge_cases, total

    def get_trending_patterns(self, days: int = 7, limit: int = 10) -> List[PatternGroup]:
        """
        Get trending patterns (recently active with high occurrence).

        Args:
            days: Number of days to look back
            limit: Maximum patterns to return

        Returns:
            List of trending PatternGroup instances
        """
        cutoff = datetime.utcnow() - timedelta(days=days)

        stmt = (
            select(PatternGroup)
            .where(
                and_(
                    PatternGroup.status == "active",
                    PatternGroup.last_seen >= cutoff
                )
            )
            .order_by(
                desc(PatternGroup.occurrence_count),
                desc(PatternGroup.last_seen)
            )
            .limit(limit)
        )

        return list(self.session.execute(stmt).scalars().all())


from datetime import timedelta
