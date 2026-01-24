"""
Edge Case Analytics Service for Phase 5.

Provides aggregated analytics and metrics for edge case trends, distributions,
and performance tracking. Supports time-based filtering for historical analysis.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, func, select, case, extract
from sqlalchemy.orm import Session

from models.edge_case import EdgeCase
from models.pattern_group import EdgeCasePatternLink, PatternGroup


class EdgeCaseAnalyticsService:
    """
    Aggregates edge case metrics for analytics dashboards.

    Provides:
    - Time-series data for trend charts
    - Category and severity distributions
    - Resolution rate tracking
    - Top patterns identification
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_analytics(
        self,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> Dict[str, Any]:
        """
        Retrieve comprehensive edge case analytics.

        Args:
            date_from: Start date filter (inclusive). Defaults to 30 days ago.
            date_to: End date filter (inclusive). Defaults to today.

        Returns:
            Dictionary containing all analytics metrics
        """
        # Set default date range to last 30 days
        if date_to is None:
            date_to = date.today()
        if date_from is None:
            date_from = date_to - timedelta(days=30)

        # Convert dates to datetime for comparison with timestamp columns
        dt_from = datetime.combine(date_from, datetime.min.time())
        dt_to = datetime.combine(date_to, datetime.max.time())

        return {
            "date_range": {
                "from": date_from.isoformat(),
                "to": date_to.isoformat(),
            },
            "summary": self._get_summary(dt_from, dt_to),
            "count_over_time": self._get_count_over_time(dt_from, dt_to),
            "category_distribution": self._get_category_distribution(dt_from, dt_to),
            "severity_distribution": self._get_severity_distribution(dt_from, dt_to),
            "status_distribution": self._get_status_distribution(dt_from, dt_to),
            "resolution_metrics": self._get_resolution_metrics(dt_from, dt_to),
            "top_patterns": self._get_top_patterns(dt_from, dt_to),
            "auto_vs_manual": self._get_auto_vs_manual(dt_from, dt_to),
        }

    def _get_summary(
        self,
        dt_from: datetime,
        dt_to: datetime,
    ) -> Dict[str, int]:
        """Get overall summary counts."""
        stmt = select(func.count(EdgeCase.id)).where(
            and_(
                EdgeCase.created_at >= dt_from,
                EdgeCase.created_at <= dt_to,
            )
        )
        total_in_range = self.session.execute(stmt).scalar() or 0

        # Total all time
        total_all = self.session.execute(
            select(func.count(EdgeCase.id))
        ).scalar() or 0

        # Active count
        active_count = self.session.execute(
            select(func.count(EdgeCase.id)).where(EdgeCase.status == "active")
        ).scalar() or 0

        # Resolved count in range
        resolved_in_range = self.session.execute(
            select(func.count(EdgeCase.id)).where(
                and_(
                    EdgeCase.status == "resolved",
                    EdgeCase.updated_at >= dt_from,
                    EdgeCase.updated_at <= dt_to,
                )
            )
        ).scalar() or 0

        # Critical severity count
        critical_count = self.session.execute(
            select(func.count(EdgeCase.id)).where(
                and_(
                    EdgeCase.severity == "critical",
                    EdgeCase.status == "active",
                )
            )
        ).scalar() or 0

        return {
            "total_in_range": total_in_range,
            "total_all_time": total_all,
            "active_count": active_count,
            "resolved_in_range": resolved_in_range,
            "critical_active": critical_count,
        }

    def _get_count_over_time(
        self,
        dt_from: datetime,
        dt_to: datetime,
    ) -> List[Dict[str, Any]]:
        """
        Get daily edge case counts for time-series chart.

        Returns list of {date, count, cumulative} for each day in range.
        """
        # Group by date (truncate timestamp to date)
        stmt = (
            select(
                func.date(EdgeCase.created_at).label("date"),
                func.count(EdgeCase.id).label("count"),
            )
            .where(
                and_(
                    EdgeCase.created_at >= dt_from,
                    EdgeCase.created_at <= dt_to,
                )
            )
            .group_by(func.date(EdgeCase.created_at))
            .order_by(func.date(EdgeCase.created_at))
        )

        rows = self.session.execute(stmt).all()

        # Build full date range with zero-fill for missing days
        result = []
        current_date = dt_from.date()
        end_date = dt_to.date()
        date_counts = {row.date: row.count for row in rows}
        cumulative = 0

        while current_date <= end_date:
            count = date_counts.get(current_date, 0)
            cumulative += count
            result.append({
                "date": current_date.isoformat(),
                "count": count,
                "cumulative": cumulative,
            })
            current_date += timedelta(days=1)

        return result

    def _get_category_distribution(
        self,
        dt_from: datetime,
        dt_to: datetime,
    ) -> List[Dict[str, Any]]:
        """Get edge case counts grouped by category."""
        stmt = (
            select(
                func.coalesce(EdgeCase.category, "uncategorized").label("category"),
                func.count(EdgeCase.id).label("count"),
            )
            .where(
                and_(
                    EdgeCase.created_at >= dt_from,
                    EdgeCase.created_at <= dt_to,
                )
            )
            .group_by(EdgeCase.category)
            .order_by(func.count(EdgeCase.id).desc())
        )

        rows = self.session.execute(stmt).all()
        total = sum(row.count for row in rows) or 1  # Avoid division by zero

        return [
            {
                "category": row.category,
                "count": row.count,
                "percentage": round((row.count / total) * 100, 1),
            }
            for row in rows
        ]

    def _get_severity_distribution(
        self,
        dt_from: datetime,
        dt_to: datetime,
    ) -> List[Dict[str, Any]]:
        """Get edge case counts grouped by severity level."""
        severity_order = {"critical": 1, "high": 2, "medium": 3, "low": 4}

        stmt = (
            select(
                func.coalesce(EdgeCase.severity, "unassigned").label("severity"),
                func.count(EdgeCase.id).label("count"),
            )
            .where(
                and_(
                    EdgeCase.created_at >= dt_from,
                    EdgeCase.created_at <= dt_to,
                )
            )
            .group_by(EdgeCase.severity)
        )

        rows = self.session.execute(stmt).all()
        total = sum(row.count for row in rows) or 1

        result = [
            {
                "severity": row.severity,
                "count": row.count,
                "percentage": round((row.count / total) * 100, 1),
            }
            for row in rows
        ]

        # Sort by severity order
        return sorted(
            result,
            key=lambda x: severity_order.get(x["severity"], 5)
        )

    def _get_status_distribution(
        self,
        dt_from: datetime,
        dt_to: datetime,
    ) -> List[Dict[str, Any]]:
        """Get edge case counts grouped by status."""
        stmt = (
            select(
                EdgeCase.status,
                func.count(EdgeCase.id).label("count"),
            )
            .where(
                and_(
                    EdgeCase.created_at >= dt_from,
                    EdgeCase.created_at <= dt_to,
                )
            )
            .group_by(EdgeCase.status)
            .order_by(func.count(EdgeCase.id).desc())
        )

        rows = self.session.execute(stmt).all()
        total = sum(row.count for row in rows) or 1

        return [
            {
                "status": row.status,
                "count": row.count,
                "percentage": round((row.count / total) * 100, 1),
            }
            for row in rows
        ]

    def _get_resolution_metrics(
        self,
        dt_from: datetime,
        dt_to: datetime,
    ) -> Dict[str, Any]:
        """
        Calculate resolution rate and metrics.

        Resolution rate = resolved / (resolved + active) for edge cases created in range.
        """
        # Count by status for edge cases created in date range
        stmt = (
            select(
                EdgeCase.status,
                func.count(EdgeCase.id).label("count"),
            )
            .where(
                and_(
                    EdgeCase.created_at >= dt_from,
                    EdgeCase.created_at <= dt_to,
                )
            )
            .group_by(EdgeCase.status)
        )

        rows = self.session.execute(stmt).all()
        status_counts = {row.status: row.count for row in rows}

        resolved = status_counts.get("resolved", 0)
        active = status_counts.get("active", 0)
        wont_fix = status_counts.get("wont_fix", 0)
        total = resolved + active + wont_fix

        resolution_rate = 0.0
        if total > 0:
            resolution_rate = round((resolved / total) * 100, 1)

        return {
            "total_created": total,
            "resolved": resolved,
            "active": active,
            "wont_fix": wont_fix,
            "resolution_rate_percent": resolution_rate,
        }

    def _get_top_patterns(
        self,
        dt_from: datetime,
        dt_to: datetime,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get top patterns by edge case count.

        Returns patterns with most linked edge cases in the date range.
        """
        # Get pattern groups with their edge case counts for the date range
        stmt = (
            select(
                PatternGroup.id,
                PatternGroup.name,
                PatternGroup.pattern_type,
                PatternGroup.severity,
                PatternGroup.occurrence_count,
                func.count(EdgeCasePatternLink.edge_case_id).label("linked_count"),
            )
            .outerjoin(
                EdgeCasePatternLink,
                PatternGroup.id == EdgeCasePatternLink.pattern_group_id
            )
            .outerjoin(
                EdgeCase,
                EdgeCasePatternLink.edge_case_id == EdgeCase.id
            )
            .where(
                and_(
                    PatternGroup.status == "active",
                    # Include patterns regardless of when edge cases were created
                    # but filter by edge case creation date for count
                )
            )
            .group_by(
                PatternGroup.id,
                PatternGroup.name,
                PatternGroup.pattern_type,
                PatternGroup.severity,
                PatternGroup.occurrence_count,
            )
            .order_by(func.count(EdgeCasePatternLink.edge_case_id).desc())
            .limit(limit)
        )

        rows = self.session.execute(stmt).all()

        return [
            {
                "id": str(row.id),
                "name": row.name,
                "pattern_type": row.pattern_type,
                "severity": row.severity,
                "occurrence_count": row.occurrence_count,
                "linked_edge_cases": row.linked_count,
            }
            for row in rows
        ]

    def _get_auto_vs_manual(
        self,
        dt_from: datetime,
        dt_to: datetime,
    ) -> Dict[str, Any]:
        """Get breakdown of auto-created vs manually-created edge cases."""
        stmt = (
            select(
                EdgeCase.auto_created,
                func.count(EdgeCase.id).label("count"),
            )
            .where(
                and_(
                    EdgeCase.created_at >= dt_from,
                    EdgeCase.created_at <= dt_to,
                )
            )
            .group_by(EdgeCase.auto_created)
        )

        rows = self.session.execute(stmt).all()

        auto_count = 0
        manual_count = 0
        for row in rows:
            if row.auto_created:
                auto_count = row.count
            else:
                manual_count = row.count

        total = auto_count + manual_count or 1

        return {
            "auto_created": auto_count,
            "manually_created": manual_count,
            "auto_created_percent": round((auto_count / total) * 100, 1),
            "manually_created_percent": round((manual_count / total) * 100, 1),
        }

    def get_trend_comparison(
        self,
        date_to: Optional[date] = None,
        period_days: int = 30,
    ) -> Dict[str, Any]:
        """
        Compare current period vs previous period for trend analysis.

        Args:
            date_to: End date for current period. Defaults to today.
            period_days: Number of days in each period.

        Returns:
            Comparison metrics showing change between periods.
        """
        if date_to is None:
            date_to = date.today()

        # Current period
        current_from = date_to - timedelta(days=period_days - 1)
        current_dt_from = datetime.combine(current_from, datetime.min.time())
        current_dt_to = datetime.combine(date_to, datetime.max.time())

        # Previous period
        previous_to = current_from - timedelta(days=1)
        previous_from = previous_to - timedelta(days=period_days - 1)
        previous_dt_from = datetime.combine(previous_from, datetime.min.time())
        previous_dt_to = datetime.combine(previous_to, datetime.max.time())

        # Count current period
        current_count = self.session.execute(
            select(func.count(EdgeCase.id)).where(
                and_(
                    EdgeCase.created_at >= current_dt_from,
                    EdgeCase.created_at <= current_dt_to,
                )
            )
        ).scalar() or 0

        # Count previous period
        previous_count = self.session.execute(
            select(func.count(EdgeCase.id)).where(
                and_(
                    EdgeCase.created_at >= previous_dt_from,
                    EdgeCase.created_at <= previous_dt_to,
                )
            )
        ).scalar() or 0

        # Calculate change
        change = current_count - previous_count
        change_percent = 0.0
        if previous_count > 0:
            change_percent = round(((current_count - previous_count) / previous_count) * 100, 1)

        return {
            "current_period": {
                "from": current_from.isoformat(),
                "to": date_to.isoformat(),
                "count": current_count,
            },
            "previous_period": {
                "from": previous_from.isoformat(),
                "to": previous_to.isoformat(),
                "count": previous_count,
            },
            "change": change,
            "change_percent": change_percent,
            "trend": "up" if change > 0 else ("down" if change < 0 else "stable"),
        }
