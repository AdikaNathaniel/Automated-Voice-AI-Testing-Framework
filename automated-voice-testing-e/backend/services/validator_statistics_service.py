"""
Validator statistics aggregation helpers.

Provides orchestration logic to build the payload that powers the
validator statistics dashboard, combining daily performance records
with raw human validation data to compute totals, average timing,
and lightweight leaderboard/trend placeholders suitable for a pilot.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.human_validation import HumanValidation
from services.validator_performance_service import ValidatorPerformanceService


@dataclass
class DecisionMetrics:
    """Container for aggregated validation decision metrics."""

    total: int = 0
    approvals: int = 0
    rejections: int = 0
    average_time_seconds: Optional[float] = None


class ValidatorStatisticsService:
    """
    Aggregates validator performance metrics for analytics endpoints.
    """

    def __init__(
        self,
        performance_service: Optional[ValidatorPerformanceService] = None,
    ) -> None:
        self.performance_service = performance_service or ValidatorPerformanceService()

    async def build_validator_statistics(
        self,
        db: AsyncSession,
        validator_id: UUID,
        display_name: str,
        history_days: int = 30,
    ) -> Dict[str, Any]:
        """
        Build validator statistics payload consumed by the frontend dashboard.
        """
        summary = await self.performance_service.get_validator_summary(
            db=db,
            validator_id=validator_id,
            days=history_days,
        )
        history = await self.performance_service.get_performance_history(
            db=db,
            validator_id=validator_id,
            limit=history_days,
        )
        decision_metrics = await self._fetch_decision_metrics(db, validator_id)

        accuracy = self._derive_accuracy(summary, decision_metrics)
        avg_time = self._derive_average_time_seconds(summary, decision_metrics)
        streak = self._calculate_streak_from_history(history)

        personal_stats = {
            "completedValidations": decision_metrics.total,
            "approvals": decision_metrics.approvals,
            "rejections": decision_metrics.rejections,
            "accuracy": accuracy,
            "averageTimeSeconds": avg_time,
            "currentStreakDays": streak,
        }

        return {
            "personal": personal_stats,
            "leaderboard": self._build_leaderboard_entries(
                validator_id=validator_id,
                display_name=display_name,
                personal_stats=personal_stats,
            ),
            "accuracyTrend": self._build_accuracy_trend(
                history=history,
                fallback_accuracy=accuracy,
            ),
        }

    async def _fetch_decision_metrics(
        self,
        db: AsyncSession,
        validator_id: UUID,
    ) -> DecisionMetrics:
        """
        Aggregate validation decision counts and timing for a validator.
        """
        stmt = (
            select(
                func.count(HumanValidation.id).label("total"),
                func.sum(
                    case(
                        (
                            HumanValidation.validation_decision.in_(
                                ["pass", "approve"]
                            ),
                            1,
                        ),
                        else_=0,
                    )
                ).label("approvals"),
                func.sum(
                    case(
                        (
                            HumanValidation.validation_decision.in_(
                                ["fail", "reject"]
                            ),
                            1,
                        ),
                        else_=0,
                    )
                ).label("rejections"),
                func.sum(HumanValidation.time_spent_seconds).label("total_time"),
            )
            .where(
                HumanValidation.validator_id == validator_id,
                HumanValidation.submitted_at.isnot(None),
            )
        )

        result = await db.execute(stmt)
        row = result.one()

        total = int(row.total or 0)
        approvals = int(row.approvals or 0)
        rejections = int(row.rejections or 0)

        average_time = None
        if total > 0 and row.total_time:
            average_time = float(row.total_time) / float(total)

        return DecisionMetrics(
            total=total,
            approvals=approvals,
            rejections=rejections,
            average_time_seconds=average_time,
        )

    @staticmethod
    def _derive_accuracy(
        summary: Dict[str, Any],
        metrics: DecisionMetrics,
    ) -> float:
        """
        Determine accuracy ratio (0-1) using peer agreement if available,
        otherwise fall back to approval ratio.
        """
        peer_avg = summary.get("avg_peer_agreement")
        if peer_avg is not None:
            return round(float(peer_avg) / 100.0, 4)

        if metrics.total == 0:
            return 0.0

        return round(metrics.approvals / metrics.total, 4)

    @staticmethod
    def _derive_average_time_seconds(
        summary: Dict[str, Any],
        metrics: DecisionMetrics,
    ) -> int:
        """
        Resolve average time spent per validation in seconds.
        """
        source_value = metrics.average_time_seconds
        if source_value is None:
            source_value = summary.get("avg_time_seconds")

        if source_value is None:
            return 0

        return int(round(float(source_value)))

    @staticmethod
    def _build_leaderboard_entries(
        validator_id: UUID,
        display_name: str,
        personal_stats: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Build placeholder leaderboard entries for pilot usage.
        """
        return [
            {
                "rank": 1,
                "validatorId": str(validator_id),
                "displayName": display_name or "Current Validator",
                "completedValidations": personal_stats["completedValidations"],
                "accuracy": personal_stats["accuracy"],
                "averageTimeSeconds": personal_stats["averageTimeSeconds"],
            }
        ]

    @staticmethod
    def _build_accuracy_trend(
        history: List[Any],
        fallback_accuracy: float,
    ) -> List[Dict[str, Any]]:
        """
        Convert performance history into chronological accuracy trend points.
        """
        if not history:
            return []

        # Historical data is returned most-recent first; reverse for display.
        ordered = sorted(
            (record for record in history if record.date),
            key=lambda record: record.date,
        )

        points: List[Dict[str, Any]] = []
        for record in ordered:
            accuracy_value: Optional[float] = None
            if record.agreement_with_peers_pct is not None:
                accuracy_value = float(record.agreement_with_peers_pct) / 100.0
            elif fallback_accuracy is not None:
                accuracy_value = fallback_accuracy
            else:
                accuracy_value = 0.0

            points.append(
                {
                    "date": record.date.isoformat(),
                    "accuracy": round(accuracy_value, 4),
                    "validations": int(record.validations_completed or 0),
                }
            )

        return points

    @staticmethod
    def _calculate_streak_from_history(history: List[Any]) -> int:
        """
        Calculate current streak of consecutive active days ending today.
        """
        if not history:
            return 0

        unique_days = sorted(
            {record.date for record in history if record.date},
            reverse=True,
        )
        today = date.today()
        streak = 0
        cursor = today

        for day in unique_days:
            if day > cursor:
                continue
            if day == cursor:
                streak += 1
                cursor = cursor - timedelta(days=1)
            else:
                break

        return streak
