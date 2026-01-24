"""
SQLAlchemy model for time-series test metrics.

Backs the MetricsService and dashboard analytics with structured storage
of metric points keyed by metric_type and dimensions.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from models.base import Base, GUID


DIMENSIONS_TYPE = postgresql.JSONB().with_variant(sa.JSON(), "sqlite")


class TestMetric(Base):
    """ORM model representing a single recorded metric datapoint."""

    __test__ = False  # Prevent pytest from collecting as a test case
    __tablename__ = "test_metrics"

    id = sa.Column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Primary identifier for the metric point",
    )

    metric_type = sa.Column(
        sa.String(length=100),
        nullable=False,
        comment="Metric name such as execution_time or pass_rate",
    )

    metric_value = sa.Column(
        sa.Numeric(precision=10, scale=2),
        nullable=False,
        comment="Numeric value observed for the metric",
    )

    dimensions = sa.Column(
        DIMENSIONS_TYPE,
        nullable=False,
        default=dict,
        comment="Dimension key/value pairs (language, environment, etc.)",
    )

    timestamp = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        comment="When the metric was recorded",
    )

    created_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        comment="Insert timestamp for the metric point",
    )

    def to_dict(self) -> Dict[str, Any]:
        """Return a serialisable representation of the metric."""
        return {
            "id": str(self.id),
            "metric_type": self.metric_type,
            "metric_value": float(self.metric_value),
            "dimensions": dict(self.dimensions or {}),
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
