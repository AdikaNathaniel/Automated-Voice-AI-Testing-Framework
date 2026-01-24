"""
Utility for recording execution metrics via MetricsService (TASK-219).

The ExecutionMetricsRecorder extracts timing and validation metadata from
MultiTurnExecution and ValidationResult objects and persists them through the
MetricsService, normalising timestamps and dimensions for downstream analytics.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional
from uuid import UUID

from services.dashboard_service import invalidate_dashboard_cache
from services.metrics_service import MetricsService


class ExecutionMetricsRecorder:
    """Record execution metrics for dashboard analytics."""

    def __init__(
        self,
        *,
        metrics_service: MetricsService,
        clock: Optional[Callable[[], datetime]] = None,
    ) -> None:
        if metrics_service is None:
            raise ValueError("metrics_service is required")
        self._metrics_service = metrics_service
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    async def record_execution_metrics(
        self,
        *,
        execution: Any,
        validation_result: Any,
        review_status: Optional[str] = None,
    ) -> None:
        """
        Persist execution metrics derived from execution and validation objects.
        """
        timestamp = self._ensure_timezone(self._clock())
        dimensions = self._base_dimensions(execution)

        execution_time = self._extract_duration_seconds(execution, "execution")
        if execution_time is not None:
            await self._record_metric_with_aggregates(
                metric_type="execution_time",
                metric_value=execution_time,
                base_dimensions=dimensions,
                timestamp=timestamp,
            )

        response_time = self._extract_duration_seconds(execution, "response")
        if response_time is not None:
            await self._record_metric_with_aggregates(
                metric_type="response_time",
                metric_value=response_time,
                base_dimensions=dimensions,
                timestamp=timestamp,
            )

        confidence = getattr(validation_result, "confidence_score", None)
        if confidence is not None:
            await self._record_metric_with_aggregates(
                metric_type="validation_confidence",
                metric_value=float(confidence),
                base_dimensions=dimensions,
                timestamp=timestamp,
            )

        accuracy = getattr(validation_result, "accuracy_score", None)
        pass_value = self._pass_value(review_status, accuracy)
        if pass_value is not None:
            extra_dimensions = {"status": review_status} if review_status else None
            await self._record_metric_with_aggregates(
                metric_type="validation_pass",
                metric_value=pass_value,
                base_dimensions=dimensions,
                timestamp=timestamp,
                extra_dimensions=extra_dimensions,
            )

        await invalidate_dashboard_cache()

    async def _record_metric(
        self,
        *,
        metric_type: str,
        metric_value: float,
        dimensions: Dict[str, Any],
        timestamp: datetime,
    ) -> None:
        await self._metrics_service.record_metric(
            metric_type=metric_type,
            metric_value=metric_value,
            dimensions=dict(dimensions),
            timestamp=timestamp,
        )

    @staticmethod
    def _ensure_timezone(value: datetime) -> datetime:
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            return value.replace(tzinfo=timezone.utc)
        return value

    def _base_dimensions(self, execution: Any) -> Dict[str, Any]:
        execution_id = getattr(execution, "id", None)
        suite_run_id = getattr(execution, "suite_run_id", None)

        dimensions: Dict[str, Any] = {}

        if isinstance(execution_id, UUID):
            dimensions["execution_id"] = str(execution_id)
        elif execution_id is not None:
            dimensions["execution_id"] = str(execution_id)

        if isinstance(suite_run_id, UUID):
            dimensions["suite_run_id"] = str(suite_run_id)
        elif suite_run_id is not None:
            dimensions["suite_run_id"] = str(suite_run_id)

        language_code = None
        if hasattr(execution, "get_audio_param"):
            language_code = execution.get_audio_param("language_code")
        if language_code:
            dimensions["language_code"] = str(language_code)

        return dimensions

    async def _record_metric_with_aggregates(
        self,
        *,
        metric_type: str,
        metric_value: float,
        base_dimensions: Dict[str, Any],
        timestamp: datetime,
        extra_dimensions: Optional[Dict[str, Any]] = None,
    ) -> None:
        raw_dimensions = dict(base_dimensions)
        raw_dimensions["aggregation"] = "raw"
        if extra_dimensions:
            raw_dimensions.update(extra_dimensions)
        await self._record_metric(
            metric_type=metric_type,
            metric_value=metric_value,
            dimensions=raw_dimensions,
            timestamp=timestamp,
        )

        for bucket in ("hour", "day"):
            bucket_dimensions = {
                key: value
                for key, value in base_dimensions.items()
                if key != "execution_id"
            }
            bucket_dimensions["aggregation"] = bucket
            if extra_dimensions:
                bucket_dimensions.update(extra_dimensions)

            bucket_timestamp = self._truncate_timestamp(timestamp, bucket)
            await self._record_metric(
                metric_type=metric_type,
                metric_value=metric_value,
                dimensions=bucket_dimensions,
                timestamp=bucket_timestamp,
            )

    def _extract_duration_seconds(self, execution: Any, metric: str) -> Optional[float]:
        context = {}
        if hasattr(execution, "get_all_context"):
            context = execution.get_all_context()
        elif getattr(execution, "context", None):
            context = dict(execution.context)

        if not context:
            return None

        ms_keys = [
            f"{metric}_duration_ms",
            f"{metric}_time_ms",
            f"{metric}_latency_ms",
        ]
        s_keys = [
            f"{metric}_duration_seconds",
            f"{metric}_time_seconds",
            f"{metric}_latency_seconds",
        ]

        for key in ms_keys:
            value = context.get(key)
            if isinstance(value, (int, float)):
                return float(value) / 1000.0
        for key in s_keys:
            value = context.get(key)
            if isinstance(value, (int, float)):
                return float(value)

        start_key = f"{metric}_started_at"
        end_key = f"{metric}_finished_at"
        if start_key in context and end_key in context:
            try:
                start = self._parse_datetime(context[start_key])
                end = self._parse_datetime(context[end_key])
                delta = (end - start).total_seconds()
                if delta >= 0:
                    return float(delta)
            except ValueError:
                return None

        return None

    @staticmethod
    def _truncate_timestamp(timestamp: datetime, bucket: str) -> datetime:
        ts = ExecutionMetricsRecorder._ensure_timezone(timestamp)
        if bucket == "hour":
            return ts.replace(minute=0, second=0, microsecond=0)
        if bucket == "day":
            return ts.replace(hour=0, minute=0, second=0, microsecond=0)
        raise ValueError(f"Unsupported aggregation bucket '{bucket}'")

    @staticmethod
    def _parse_datetime(value: Any) -> datetime:
        if isinstance(value, datetime):
            return ExecutionMetricsRecorder._ensure_timezone(value)
        if isinstance(value, str):
            parsed = datetime.fromisoformat(value)
            return ExecutionMetricsRecorder._ensure_timezone(parsed)
        raise ValueError("Unsupported datetime value")

    @staticmethod
    def _pass_value(review_status: Optional[str], accuracy: Optional[float]) -> Optional[float]:
        if review_status == "auto_pass":
            return 1.0
        if review_status == "auto_fail":
            return 0.0
        if review_status == "needs_review":
            return 0.0
        if accuracy is not None:
            return float(accuracy >= 0.8)
        return None
