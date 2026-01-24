"""
Metrics collection service for recording time-series metrics.

Provides async helpers for persisting metric datapoints and retrieving
aggregated results for dashboard visualisations.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, Iterable, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.test_metric import TestMetric


class MetricsService:
    """Service responsible for storing and retrieving metric datapoints."""

    def __init__(self, db: Optional[AsyncSession]):
        if db is None:
            raise ValueError("MetricsService requires a database session")
        self.db = db

    async def record_metric(
        self,
        *,
        metric_type: str,
        metric_value: float,
        dimensions: Optional[Dict[str, Any]],
        timestamp: datetime,
    ) -> TestMetric:
        """
        Persist a new metric datapoint.

        Raises:
            ValueError: If timestamp is not timezone-aware.
        """
        if timestamp.tzinfo is None or timestamp.tzinfo.utcoffset(timestamp) is None:
            raise ValueError("timestamp must be timezone-aware")

        normalized_dimensions = dict(dimensions or {})
        decimal_value = (
            Decimal(str(metric_value))
            .quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        )

        metric = TestMetric(
            metric_type=metric_type,
            metric_value=decimal_value,
            dimensions=normalized_dimensions,
            timestamp=timestamp,
        )

        self.db.add(metric)
        await self.db.commit()
        await self.db.refresh(metric)

        stored_timestamp = metric.timestamp
        if stored_timestamp is not None and (
            stored_timestamp.tzinfo is None
            or stored_timestamp.tzinfo.utcoffset(stored_timestamp) is None
        ):
            # Normalise to UTC for databases that drop timezone metadata (e.g. SQLite).
            metric.timestamp = stored_timestamp.replace(tzinfo=timezone.utc)

        return metric

    async def get_metrics(
        self,
        *,
        metric_type: str,
        start_time: datetime,
        end_time: datetime,
        granularity: str,
        dimensions: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve metrics aggregated by the requested granularity."""
        if start_time.tzinfo is None or start_time.tzinfo.utcoffset(start_time) is None:
            raise ValueError("start_time must be timezone-aware")
        if end_time.tzinfo is None or end_time.tzinfo.utcoffset(end_time) is None:
            raise ValueError("end_time must be timezone-aware")
        if end_time <= start_time:
            raise ValueError("end_time must be greater than start_time")

        granularity_key = granularity.lower()
        if granularity_key not in {"raw", "hour", "day"}:
            raise ValueError(f"Unsupported granularity '{granularity}'")

        stmt = (
            select(TestMetric)
            .where(
                TestMetric.metric_type == metric_type,
                TestMetric.timestamp >= start_time,
                TestMetric.timestamp < end_time,
            )
            .order_by(TestMetric.timestamp)
        )

        result = await self.db.execute(stmt)
        metrics = [
            metric
            for metric in result.scalars().all()
            if self._matches_dimensions(metric, dimensions)
        ]

        if granularity_key == "raw":
            return [
                {
                    "timestamp": self._normalise_timestamp(metric.timestamp),
                    "metric_value": float(metric.metric_value),
                    "count": 1,
                }
                for metric in metrics
            ]

        buckets = self._bucket_metrics(metrics, granularity_key)
        return self._serialize_buckets(buckets)

    @staticmethod
    def _matches_dimensions(metric: TestMetric, dimensions: Optional[Dict[str, Any]]) -> bool:
        if not dimensions:
            return True
        metric_dims = metric.dimensions or {}
        return all(metric_dims.get(key) == value for key, value in dimensions.items())

    def _bucket_metrics(
        self,
        metrics: Iterable[TestMetric],
        granularity: str,
    ) -> Dict[datetime, Tuple[Decimal, int]]:
        buckets: Dict[datetime, Tuple[Decimal, int]] = {}
        for metric in metrics:
            timestamp = self._normalise_timestamp(metric.timestamp)
            bucket_start = self._truncate_timestamp(timestamp, granularity)
            current_sum, current_count = buckets.get(bucket_start, (Decimal("0"), 0))
            metric_value = (
                Decimal(str(metric.metric_value))
                .quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            )
            buckets[bucket_start] = (
                current_sum + metric_value,
                current_count + 1,
            )
        return buckets

    @staticmethod
    def _normalise_timestamp(timestamp: datetime) -> datetime:
        if timestamp.tzinfo is None or timestamp.tzinfo.utcoffset(timestamp) is None:
            return timestamp.replace(tzinfo=timezone.utc)
        return timestamp.astimezone(timezone.utc)

    @staticmethod
    def _truncate_timestamp(timestamp: datetime, granularity: str) -> datetime:
        if granularity == "hour":
            return timestamp.replace(minute=0, second=0, microsecond=0)
        if granularity == "day":
            return timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        raise ValueError(f"Unsupported granularity '{granularity}'")

    def _serialize_buckets(
        self,
        buckets: Dict[datetime, Tuple[Decimal, int]],
    ) -> List[Dict[str, Any]]:
        serialized: List[Dict[str, Any]] = []
        for bucket_start in sorted(buckets.keys()):
            total, count = buckets[bucket_start]
            average = (total / count).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            serialized.append(
                {
                    "timestamp": bucket_start,
                    "metric_value": float(average),
                    "count": count,
                }
            )
        return serialized
