"""
Persistent regression tracking service.

This service manages the lifecycle of regression records in the database,
providing functionality for:
- Creating/updating regression records when regressions are detected
- Resolving regressions manually or automatically when tests pass
- Creating defects from regressions
- Querying regression history and trends
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from models.regression import Regression
from models.defect import Defect
from models.scenario_script import ScenarioScript
from services.regression_detection_service import RegressionFinding


class RegressionTrackingService:
    """Service for managing persistent regression records."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def record_regression(
        self,
        *,
        finding: RegressionFinding,
        tenant_id: Optional[UUID],
        baseline_version: Optional[int] = None,
    ) -> Regression:
        """
        Record a detected regression or update existing record.

        Args:
            finding: RegressionFinding from detection service
            tenant_id: Tenant UUID
            baseline_version: Version of baseline used for detection

        Returns:
            Created or updated Regression record
        """
        # Check if regression already exists for this script
        stmt = (
            select(Regression)
            .where(
                and_(
                    Regression.script_id == finding.script_id,
                    Regression.status == "active",
                )
            )
        )
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()

        now = datetime.now(timezone.utc)

        if existing:
            # Update existing regression
            existing.update_occurrence(finding.detail)
            await self.session.commit()
            await self.session.refresh(existing)
            return existing

        # Create new regression record
        severity = self._determine_severity(finding)
        regression = Regression(
            tenant_id=tenant_id,
            script_id=finding.script_id,
            category=finding.category,
            severity=severity,
            status="active",
            baseline_version=baseline_version,
            detection_date=now,
            last_seen_date=now,
            occurrence_count=1,
            details=finding.detail,
        )

        self.session.add(regression)
        await self.session.commit()
        await self.session.refresh(regression)
        return regression

    async def resolve_regression(
        self,
        *,
        regression_id: UUID,
        resolved_by: UUID,
        note: Optional[str] = None,
    ) -> Regression:
        """
        Manually resolve a regression.

        Args:
            regression_id: Regression UUID
            resolved_by: User UUID
            note: Optional resolution note

        Returns:
            Updated Regression record

        Raises:
            ValueError: If regression not found
        """
        stmt = select(Regression).where(Regression.id == regression_id)
        result = await self.session.execute(stmt)
        regression = result.scalar_one_or_none()

        if not regression:
            raise ValueError(f"Regression {regression_id} not found")

        regression.resolve(resolved_by, note)
        await self.session.commit()
        await self.session.refresh(regression)
        return regression

    async def auto_resolve_passing_tests(
        self,
        *,
        script_id: UUID,
    ) -> List[Regression]:
        """
        Auto-resolve regressions when test passes again.

        Args:
            script_id: Scenario script UUID

        Returns:
            List of resolved Regression records
        """
        stmt = (
            select(Regression)
            .where(
                and_(
                    Regression.script_id == script_id,
                    Regression.status == "active",
                )
            )
        )
        result = await self.session.execute(stmt)
        regressions = list(result.scalars().all())

        resolved_regressions = []
        for regression in regressions:
            regression.resolve(
                resolved_by=None,
                note="Auto-resolved: test passed in subsequent run"
            )
            resolved_regressions.append(regression)

        if resolved_regressions:
            await self.session.commit()

        return resolved_regressions

    async def create_defect_from_regression(
        self,
        *,
        regression_id: UUID,
        created_by: UUID,
        severity_override: Optional[str] = None,
        additional_notes: Optional[str] = None,
    ) -> Defect:
        """
        Create a defect to track a regression.

        Args:
            regression_id: Regression UUID
            created_by: User UUID
            severity_override: Override defect severity
            additional_notes: Additional context for defect

        Returns:
            Created Defect record

        Raises:
            ValueError: If regression not found
        """
        stmt = (
            select(Regression)
            .options(joinedload(Regression.script))
            .where(Regression.id == regression_id)
        )
        result = await self.session.execute(stmt)
        regression = result.scalar_one_or_none()

        if not regression:
            raise ValueError(f"Regression {regression_id} not found")

        # Build defect title and description
        script_name = regression.script.name if regression.script else str(regression.script_id)
        title = f"Regression in {script_name}"

        description = self._build_defect_description(regression, additional_notes)

        # Create defect
        defect = Defect(
            tenant_id=regression.tenant_id,
            script_id=regression.script_id,
            execution_id=None,  # Regression doesn't track specific execution
            severity=severity_override or regression.severity,
            category="regression",
            title=title,
            description=description,
            detected_at=regression.detection_date,
            status="open",
        )

        self.session.add(defect)

        # Link defect to regression
        regression.link_defect(defect.id)

        await self.session.commit()
        await self.session.refresh(defect)
        await self.session.refresh(regression)

        return defect

    async def list_regressions(
        self,
        *,
        tenant_id: Optional[UUID] = None,
        status_filter: Optional[str] = None,
        category_filter: Optional[str] = None,
        script_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        List regression records with filters.

        Args:
            tenant_id: Filter by tenant
            status_filter: Filter by status (active, resolved, etc.)
            category_filter: Filter by category (status, metric, llm)
            script_id: Filter by specific script
            skip: Number of records to skip
            limit: Maximum records to return

        Returns:
            Dict with total counts and regression items
        """
        # Build base query
        stmt = select(Regression).options(joinedload(Regression.script))

        # Apply filters
        filters = []
        if tenant_id:
            filters.append(Regression.tenant_id == tenant_id)
        if status_filter:
            filters.append(Regression.status == status_filter)
        if category_filter:
            filters.append(Regression.category == category_filter)
        if script_id:
            filters.append(Regression.script_id == script_id)

        if filters:
            stmt = stmt.where(and_(*filters))

        # Get total count
        count_stmt = select(func.count()).select_from(Regression)
        if filters:
            count_stmt = count_stmt.where(and_(*filters))
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar() or 0

        # Get active/resolved counts
        active_stmt = select(func.count()).select_from(Regression).where(
            and_(
                Regression.status == "active",
                *(filters if filters else [])
            )
        )
        active_result = await self.session.execute(active_stmt)
        active_count = active_result.scalar() or 0

        resolved_stmt = select(func.count()).select_from(Regression).where(
            and_(
                Regression.status == "resolved",
                *(filters if filters else [])
            )
        )
        resolved_result = await self.session.execute(resolved_stmt)
        resolved_count = resolved_result.scalar() or 0

        # Get paginated items
        stmt = stmt.order_by(
            Regression.status.asc(),  # Active first
            Regression.detection_date.desc()
        ).offset(skip).limit(limit)

        result = await self.session.execute(stmt)
        regressions = list(result.scalars().all())

        # Serialize
        items = [self._serialize_regression(r) for r in regressions]

        return {
            "total": total,
            "active": active_count,
            "resolved": resolved_count,
            "items": items,
        }

    def _determine_severity(self, finding: RegressionFinding) -> str:
        """Determine regression severity based on finding details."""
        if finding.category == "status":
            # Status regressions (pass → fail) are high severity
            return "high"

        if finding.category == "llm":
            # LLM regressions (final decision changed) are medium severity
            return "medium"

        if finding.category == "metric":
            # Metric regressions - check magnitude of change
            delta_pct = finding.detail.get("change_pct")
            if delta_pct and abs(delta_pct) > 20:
                return "high"
            elif delta_pct and abs(delta_pct) > 10:
                return "medium"
            return "low"

        return "medium"

    def _build_defect_description(
        self,
        regression: Regression,
        additional_notes: Optional[str],
    ) -> str:
        """Build defect description from regression details."""
        lines = [
            "This defect was created from a detected regression.",
            "",
            f"**Regression Category:** {regression.category}",
            f"**First Detected:** {regression.detection_date.isoformat()}",
            f"**Occurrences:** {regression.occurrence_count}",
            "",
        ]

        # Add regression-specific details
        details = regression.details or {}

        if regression.category == "status":
            baseline = details.get("baseline_status")
            current = details.get("current_status")
            lines.append(f"**Status Change:** {baseline} → {current}")

        elif regression.category == "llm":
            baseline = details.get("baseline_decision")
            current = details.get("current_decision")
            lines.append(f"**LLM Decision Change:** {baseline} → {current}")

        elif regression.category == "metric":
            metric = details.get("metric")
            baseline_val = details.get("baseline_value")
            current_val = details.get("current_value")
            change_pct = details.get("change_pct")
            lines.append(f"**Metric:** {metric}")
            lines.append(f"**Baseline Value:** {baseline_val}")
            lines.append(f"**Current Value:** {current_val}")
            if change_pct:
                lines.append(f"**Change:** {change_pct:.1f}%")

        if additional_notes:
            lines.extend(["", "**Additional Notes:**", additional_notes])

        return "\n".join(lines)

    def _serialize_regression(self, regression: Regression) -> Dict[str, Any]:
        """Serialize Regression model to dict."""
        data = regression.to_dict()

        # Add script name if available
        if regression.script:
            data["script_name"] = regression.script.name

        return data
