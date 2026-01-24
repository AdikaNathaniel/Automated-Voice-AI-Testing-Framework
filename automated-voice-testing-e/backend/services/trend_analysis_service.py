"""
Trend analysis helpers for advanced analytics (TASK-309).

The service aggregates metrics and defect records to surface pass-rate,
defect, and performance trends used by forthcoming analytics endpoints.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Dict, List, Optional, Sequence

from sqlalchemy import func, or_, select, case, and_
from sqlalchemy.ext.asyncio import AsyncSession

from models.defect import Defect
from models.multi_turn_execution import MultiTurnExecution, StepExecution
from models.validation_result import ValidationResult
from services.metrics_service import MetricsService
from services.anomaly_detection_service import AnomalyDetectionService

_SUPPORTED_GRANULARITIES = {"day", "hour", "raw"}
_DIRECTION_EPSILON = 1e-6


@dataclass
class _TrendPoint:
    """Internal representation of a numeric trend point."""

    timestamp: datetime
    value: float
    sample_size: int


class TrendAnalysisService:
    """Aggregate historical metrics for analytics visualisations."""

    def __init__(self, db: Optional[AsyncSession]) -> None:
        if db is None:
            raise ValueError("TrendAnalysisService requires a database session")
        self._db = db
        self._metrics = MetricsService(db)

    async def analyze_pass_rate_trend(
        self,
        *,
        start_date: date,
        end_date: date,
        granularity: str,
    ) -> List[Dict[str, Any]]:
        """
        Return pass rate trend data between the supplied dates inclusive.

        Results are sorted chronologically and expressed as percentages.
        Falls back to execution data if no TestMetric records exist.
        """
        normalized_granularity = self._normalize_granularity(granularity)
        start_time, end_time = self._date_range(start_date, end_date)

        # Try to get metrics from TestMetric table first
        metrics = await self._metrics.get_metrics(
            metric_type="validation_pass",
            start_time=start_time,
            end_time=end_time,
            granularity=normalized_granularity,
            dimensions={"aggregation": normalized_granularity},
        )

        # If no TestMetric records, fall back to execution data
        if not metrics:
            return await self._analyze_pass_rate_from_executions(
                start_time=start_time,
                end_time=end_time,
                granularity=normalized_granularity,
            )

        points = [
            _TrendPoint(
                timestamp=self._ensure_timezone(entry["timestamp"]),
                value=float(entry.get("metric_value", 0.0)) * 100.0,
                sample_size=int(entry.get("count", 0) or 0),
            )
            for entry in metrics
        ]

        return self._serialise_numeric_trend(
            points,
            value_key="pass_rate_pct",
            change_key="change_pct",
            count_key="total_executions",
        )

    async def analyze_defect_trend(
        self,
        *,
        start_date: date,
        end_date: date,
        granularity: str,
    ) -> List[Dict[str, Any]]:
        """
        Return defect trend data grouped by the requested granularity.
        """
        normalized_granularity = self._normalize_granularity(granularity)
        if normalized_granularity == "raw":
            normalized_granularity = "day"

        start_time, end_time = self._date_range(start_date, end_date)
        periods = self._generate_periods(start_time, end_time, normalized_granularity)
        if not periods:
            return []

        detected_counts = await self._collect_defect_counts(
            column_name="detected_at",
            start_time=start_time,
            end_time=end_time,
            granularity=normalized_granularity,
        )
        resolved_counts = await self._collect_defect_counts(
            column_name="resolved_at",
            start_time=start_time,
            end_time=end_time,
            granularity=normalized_granularity,
        )
        running_open = await self._count_open_defects_before(start_time)

        trend: List[Dict[str, Any]] = []
        previous_net: Optional[int] = None

        for period_start in periods:
            detected = detected_counts.get(period_start, 0)
            resolved = resolved_counts.get(period_start, 0)
            running_open += detected - resolved
            if running_open < 0:
                running_open = 0

            change = None if previous_net is None else running_open - previous_net
            direction = self._direction_from_delta(change)

            trend.append(
                {
                    "period_start": period_start,
                    "detected": detected,
                    "resolved": resolved,
                    "net_open": running_open,
                    "change_open": change,
                    "direction": direction,
                }
            )
            previous_net = running_open

        return trend

    async def analyze_performance_trend(
        self,
        *,
        start_date: date,
        end_date: date,
        granularity: str,
    ) -> List[Dict[str, Any]]:
        """
        Return average response time trend (in milliseconds) between the dates.
        Falls back to StepExecution data if no TestMetric records exist.
        """
        normalized_granularity = self._normalize_granularity(granularity)
        start_time, end_time = self._date_range(start_date, end_date)

        metrics = await self._metrics.get_metrics(
            metric_type="response_time",
            start_time=start_time,
            end_time=end_time,
            granularity=normalized_granularity,
            dimensions={"aggregation": normalized_granularity},
        )

        # If no TestMetric records, fall back to StepExecution data
        if not metrics:
            return await self._analyze_performance_from_step_executions(
                start_time=start_time,
                end_time=end_time,
                granularity=normalized_granularity,
            )

        points = [
            _TrendPoint(
                timestamp=self._ensure_timezone(entry["timestamp"]),
                value=float(entry.get("metric_value", 0.0)) * 1000.0,
                sample_size=int(entry.get("count", 0) or 0),
            )
            for entry in metrics
        ]

        return self._serialise_numeric_trend(
            points,
            value_key="avg_response_time_ms",
            change_key="change_ms",
            count_key="sample_size",
        )

    async def get_summary_statistics(
        self,
        *,
        start_date: date,
        end_date: date,
    ) -> Dict[str, Any]:
        """
        Get summary statistics for the period.

        Returns:
            - total_executions: Count of MultiTurnExecution records
            - total_validations: Count of ValidationResult records
            - avg_pass_rate_pct: Average pass rate across all validations
        """
        start_time, end_time = self._date_range(start_date, end_date)

        # Count actual executions (MultiTurnExecution records)
        execution_stmt = select(func.count(MultiTurnExecution.id)).where(
            and_(
                MultiTurnExecution.created_at >= start_time,
                MultiTurnExecution.created_at < end_time,
            )
        )
        execution_result = await self._db.execute(execution_stmt)
        total_executions = execution_result.scalar() or 0

        # Count validations and calculate pass rate
        validation_stmt = select(
            func.count(ValidationResult.id),
            func.sum(case((ValidationResult.final_decision == 'pass', 1), else_=0)),
            func.sum(case((ValidationResult.final_decision == 'fail', 1), else_=0)),
        ).where(
            and_(
                ValidationResult.created_at >= start_time,
                ValidationResult.created_at < end_time,
                ValidationResult.final_decision.in_(['pass', 'fail']),
            )
        )
        validation_result = await self._db.execute(validation_stmt)
        total_validations, passed, failed = validation_result.one()

        total_validations = int(total_validations or 0)
        passed = int(passed or 0)
        failed = int(failed or 0)

        # Calculate average pass rate
        total_decided = passed + failed
        avg_pass_rate = (passed / total_decided * 100.0) if total_decided > 0 else 0.0

        # Calculate average response time from StepExecution
        response_time_stmt = select(
            func.avg(StepExecution.response_time_ms),
            func.count(StepExecution.id),
        ).where(
            and_(
                StepExecution.executed_at >= start_time,
                StepExecution.executed_at < end_time,
                StepExecution.response_time_ms.isnot(None),
            )
        )
        response_time_result = await self._db.execute(response_time_stmt)
        avg_response_time, response_time_samples = response_time_result.one()

        avg_response_time_ms = float(avg_response_time or 0.0)
        response_time_samples = int(response_time_samples or 0)

        return {
            "total_executions": total_executions,
            "total_validations": total_validations,
            "avg_pass_rate_pct": round(avg_pass_rate, 2),
            "avg_response_time_ms": round(avg_response_time_ms, 2),
            "response_time_samples": response_time_samples,
        }

    async def analyze_trends_with_anomalies(
        self,
        *,
        start_date: date,
        end_date: date,
        granularity: str,
        anomaly_service: Optional[AnomalyDetectionService] = None,
    ) -> Dict[str, Any]:
        """
        Aggregate trends and detect anomalies in a single call.
        """
        pass_rate = await self.analyze_pass_rate_trend(
            start_date=start_date,
            end_date=end_date,
            granularity=granularity,
        )
        defects = await self.analyze_defect_trend(
            start_date=start_date,
            end_date=end_date,
            granularity=granularity,
        )
        performance = await self.analyze_performance_trend(
            start_date=start_date,
            end_date=end_date,
            granularity=granularity,
        )

        detector = anomaly_service or AnomalyDetectionService()
        anomalies = detector.detect_anomalies(
            pass_rate_trend=pass_rate,
            defect_trend=defects,
            performance_trend=performance,
        )

        return {
            "pass_rate": pass_rate,
            "defects": defects,
            "performance": performance,
            "anomalies": anomalies,
        }

    @staticmethod
    def _normalize_granularity(granularity: str) -> str:
        candidate = (granularity or "").lower()
        if candidate not in _SUPPORTED_GRANULARITIES:
            raise ValueError(f"Unsupported granularity '{granularity}'")
        return candidate

    @staticmethod
    def _date_range(start: date, end: date) -> tuple[datetime, datetime]:
        if end < start:
            raise ValueError("end_date must be greater than or equal to start_date")

        start_time = datetime.combine(start, time.min, tzinfo=timezone.utc)
        end_time = datetime.combine(end + timedelta(days=1), time.min, tzinfo=timezone.utc)
        return start_time, end_time

    @staticmethod
    def _ensure_timezone(value: datetime) -> datetime:
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    def _serialise_numeric_trend(
        self,
        points: Sequence[_TrendPoint],
        *,
        value_key: str,
        change_key: str,
        count_key: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        trend: List[Dict[str, Any]] = []
        previous_value: Optional[float] = None

        for point in sorted(points, key=lambda item: item.timestamp):
            rounded_value = round(point.value, 2)
            change: Optional[float] = None
            direction = "flat"

            if previous_value is not None:
                delta = rounded_value - previous_value
                direction = self._direction_from_delta(delta)
                change = round(delta, 2)
                if abs(change) <= _DIRECTION_EPSILON:
                    change = 0.0

            entry: Dict[str, Any] = {
                "period_start": point.timestamp,
                value_key: rounded_value,
                change_key: change,
                "direction": direction,
            }

            if count_key:
                entry[count_key] = point.sample_size

            trend.append(entry)
            previous_value = rounded_value

        return trend

    def _generate_periods(
        self,
        start_time: datetime,
        end_time: datetime,
        granularity: str,
    ) -> List[datetime]:
        delta = timedelta(hours=1) if granularity == "hour" else timedelta(days=1)
        periods: List[datetime] = []
        current = start_time
        while current < end_time:
            periods.append(current)
            current += delta
        return periods

    async def _collect_defect_counts(
        self,
        *,
        column_name: str,
        start_time: datetime,
        end_time: datetime,
        granularity: str,
    ) -> Dict[datetime, int]:
        column = getattr(Defect, column_name)
        stmt = select(column).where(
            column.is_not(None),
            column >= start_time,
            column < end_time,
        )

        result = await self._db.execute(stmt)
        counts: Dict[datetime, int] = {}
        for timestamp in result.scalars():
            if timestamp is None:
                continue
            normalized = self._ensure_timezone(timestamp)
            bucket = self._truncate_to_period(normalized, granularity)
            counts[bucket] = counts.get(bucket, 0) + 1
        return counts

    async def _count_open_defects_before(self, start_time: datetime) -> int:
        stmt = select(func.count()).select_from(Defect).where(
            Defect.detected_at < start_time,
            or_(Defect.resolved_at.is_(None), Defect.resolved_at >= start_time),
        )
        result = await self._db.execute(stmt)
        count = result.scalar_one_or_none()
        return int(count or 0)

    @staticmethod
    def _direction_from_delta(delta: Optional[float]) -> str:
        if delta is None or abs(delta) <= _DIRECTION_EPSILON:
            return "flat"
        return "up" if delta > 0 else "down"

    @staticmethod
    def _truncate_to_period(timestamp: datetime, granularity: str) -> datetime:
        if granularity == "hour":
            return timestamp.replace(minute=0, second=0, microsecond=0)
        return timestamp.replace(hour=0, minute=0, second=0, microsecond=0)

    async def _analyze_pass_rate_from_executions(
        self,
        *,
        start_time: datetime,
        end_time: datetime,
        granularity: str,
    ) -> List[Dict[str, Any]]:
        """
        Calculate pass rate trend from ValidationResult.final_decision.

        This is a fallback when TestMetric records are not available.
        Groups validation results by time period and calculates pass rate per period.
        Uses actual validation outcomes (pass/fail) not execution status.
        """
        # Query validation results with final_decision (pass/fail)
        stmt = select(
            ValidationResult.created_at,
            ValidationResult.final_decision,
        ).where(
            and_(
                ValidationResult.created_at >= start_time,
                ValidationResult.created_at < end_time,
                ValidationResult.final_decision.in_(['pass', 'fail']),
            )
        ).order_by(ValidationResult.created_at)

        result = await self._db.execute(stmt)
        rows = result.all()

        if not rows:
            return []

        # Group validation results by period
        period_data: Dict[datetime, Dict[str, int]] = {}

        for created_at, final_decision in rows:
            if created_at is None:
                continue
            normalized = self._ensure_timezone(created_at)
            bucket = self._truncate_to_period(normalized, granularity)

            if bucket not in period_data:
                period_data[bucket] = {"passed": 0, "failed": 0}

            if final_decision == "pass":
                period_data[bucket]["passed"] += 1
            else:
                period_data[bucket]["failed"] += 1

        # Build trend points
        trend: List[Dict[str, Any]] = []
        previous_rate: Optional[float] = None

        for period_start in sorted(period_data.keys()):
            data = period_data[period_start]
            total = data["passed"] + data["failed"]
            pass_rate = (data["passed"] / total * 100.0) if total > 0 else 0.0
            rounded_rate = round(pass_rate, 2)

            change: Optional[float] = None
            direction = "flat"

            if previous_rate is not None:
                delta = rounded_rate - previous_rate
                direction = self._direction_from_delta(delta)
                change = round(delta, 2)
                if abs(change) <= _DIRECTION_EPSILON:
                    change = 0.0

            trend.append({
                "period_start": period_start,
                "pass_rate_pct": rounded_rate,
                "change_pct": change,
                "direction": direction,
                "total_executions": total,
            })

            previous_rate = rounded_rate

        return trend

    async def _analyze_performance_from_step_executions(
        self,
        *,
        start_time: datetime,
        end_time: datetime,
        granularity: str,
    ) -> List[Dict[str, Any]]:
        """
        Calculate performance trend from StepExecution.response_time_ms.

        This is a fallback when TestMetric records are not available.
        Groups step executions by time period and calculates avg response time.
        """
        stmt = select(
            StepExecution.executed_at,
            StepExecution.response_time_ms,
        ).where(
            and_(
                StepExecution.executed_at >= start_time,
                StepExecution.executed_at < end_time,
                StepExecution.response_time_ms.isnot(None),
            )
        ).order_by(StepExecution.executed_at)

        result = await self._db.execute(stmt)
        rows = result.all()

        if not rows:
            return []

        # Group by period and calculate averages
        period_data: Dict[datetime, Dict[str, Any]] = {}

        for executed_at, response_time_ms in rows:
            if executed_at is None:
                continue
            normalized = self._ensure_timezone(executed_at)
            bucket = self._truncate_to_period(normalized, granularity)

            if bucket not in period_data:
                period_data[bucket] = {"total_ms": 0.0, "count": 0}

            period_data[bucket]["total_ms"] += float(response_time_ms)
            period_data[bucket]["count"] += 1

        # Build trend points
        trend: List[Dict[str, Any]] = []
        previous_avg: Optional[float] = None

        for period_start in sorted(period_data.keys()):
            data = period_data[period_start]
            avg_ms = data["total_ms"] / data["count"] if data["count"] > 0 else 0.0
            rounded_avg = round(avg_ms, 2)

            change: Optional[float] = None
            direction = "flat"

            if previous_avg is not None:
                delta = rounded_avg - previous_avg
                direction = self._direction_from_delta(delta)
                change = round(delta, 2)
                if abs(change) <= _DIRECTION_EPSILON:
                    change = 0.0

            trend.append({
                "period_start": period_start,
                "avg_response_time_ms": rounded_avg,
                "change_ms": change,
                "direction": direction,
                "sample_size": data["count"],
            })

            previous_avg = rounded_avg

        return trend
