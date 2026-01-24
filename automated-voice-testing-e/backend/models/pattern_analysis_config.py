"""
PatternAnalysisConfig SQLAlchemy model for tenant-specific pattern analysis settings.

Controls how the automated pattern discovery job behaves for each organization.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from datetime import datetime

import sqlalchemy as sa

from models.base import Base, GUID, BaseModel


class PatternAnalysisConfig(Base, BaseModel):
    """
    ORM representation of pattern analysis configuration per tenant.

    Each organization/tenant can configure how pattern analysis runs:
    - Time windows for edge case analysis
    - Pattern formation thresholds
    - LLM usage and budget limits
    - Scheduling preferences
    - Notification settings

    Attributes:
        tenant_id: Organization that owns this configuration
        lookback_days: Maximum age of edge cases to analyze (in days)
        min_pattern_size: Minimum edge cases to form a pattern
        similarity_threshold: Semantic similarity threshold (0.0-1.0)
        defect_auto_creation_threshold: Consecutive failures before auto-creating defect
        enable_llm_analysis: Whether to use LLM-powered analysis
        llm_confidence_threshold: Minimum LLM confidence for matching
        analysis_schedule: Cron expression for analysis schedule
        enable_auto_analysis: Whether to run automatic pattern analysis
        notify_on_new_patterns: Send notifications for new patterns
        notify_on_critical_patterns: Send alerts for critical patterns
        response_time_sla_ms: Response time SLA threshold in milliseconds
    """

    __test__ = False  # Prevent pytest auto-discovery
    __tablename__ = "pattern_analysis_configs"

    tenant_id = sa.Column(
        GUID(),
        nullable=True,
        unique=True,
        index=True,
        comment="Organization/tenant that owns this configuration (null = global default)",
    )

    # Time window settings
    lookback_days = sa.Column(
        sa.Integer(),
        nullable=False,
        default=30,
        server_default=sa.text("30"),
        comment="Maximum age of edge cases to analyze (in days)",
    )

    # Pattern formation settings
    min_pattern_size = sa.Column(
        sa.Integer(),
        nullable=False,
        default=3,
        server_default=sa.text("3"),
        comment="Minimum edge cases required to form a pattern",
    )

    similarity_threshold = sa.Column(
        sa.Float(),
        nullable=False,
        default=0.85,
        server_default=sa.text("0.85"),
        comment="Semantic similarity threshold (0.0-1.0)",
    )

    # Defect auto-creation settings
    defect_auto_creation_threshold = sa.Column(
        sa.Integer(),
        nullable=False,
        default=3,
        server_default=sa.text("3"),
        comment="Number of consecutive auto_fail results before creating defect (minimum: 1)",
    )

    # LLM settings
    enable_llm_analysis = sa.Column(
        sa.Boolean(),
        nullable=False,
        default=True,
        server_default=sa.text("true"),
        comment="Whether to use LLM-powered analysis",
    )

    llm_confidence_threshold = sa.Column(
        sa.Float(),
        nullable=False,
        default=0.70,
        server_default=sa.text("0.70"),
        comment="Minimum LLM confidence for pattern matching (0.0-1.0)",
    )

    # Scheduling settings
    analysis_schedule = sa.Column(
        sa.String(100),
        nullable=False,
        default="0 2 * * *",
        server_default=sa.text("'0 2 * * *'"),
        comment="Cron expression for analysis schedule (default: daily at 2 AM)",
    )

    enable_auto_analysis = sa.Column(
        sa.Boolean(),
        nullable=False,
        default=True,
        server_default=sa.text("true"),
        comment="Whether to run automatic pattern analysis",
    )

    # Notification settings
    notify_on_new_patterns = sa.Column(
        sa.Boolean(),
        nullable=False,
        default=True,
        server_default=sa.text("true"),
        comment="Send notifications when new patterns discovered",
    )

    notify_on_critical_patterns = sa.Column(
        sa.Boolean(),
        nullable=False,
        default=True,
        server_default=sa.text("true"),
        comment="Send alerts for critical severity patterns",
    )

    # Dashboard/SLA settings
    response_time_sla_ms = sa.Column(
        sa.Integer(),
        nullable=False,
        default=2000,
        server_default=sa.text("2000"),
        comment="Response time SLA threshold in milliseconds",
    )

    def __repr__(self) -> str:
        """Readable representation useful for debugging."""
        return f"<PatternAnalysisConfig(tenant_id={self.tenant_id})>"

    def to_dict(self) -> Dict[str, Optional[Any]]:
        """Serialise the configuration into JSON-friendly primitives."""

        def _serialise(value: Optional[Any]) -> Optional[Any]:
            if hasattr(value, '__uuid__'):
                return str(value)
            if isinstance(value, datetime):
                return value.isoformat()
            return value

        return {
            "id": _serialise(self.id),
            "tenant_id": _serialise(self.tenant_id),
            "lookback_days": self.lookback_days,
            "min_pattern_size": self.min_pattern_size,
            "similarity_threshold": self.similarity_threshold,
            "defect_auto_creation_threshold": self.defect_auto_creation_threshold,
            "enable_llm_analysis": self.enable_llm_analysis,
            "llm_confidence_threshold": self.llm_confidence_threshold,
            "analysis_schedule": self.analysis_schedule,
            "enable_auto_analysis": self.enable_auto_analysis,
            "notify_on_new_patterns": self.notify_on_new_patterns,
            "notify_on_critical_patterns": self.notify_on_critical_patterns,
            "response_time_sla_ms": self.response_time_sla_ms,
            "created_at": _serialise(self.created_at),
            "updated_at": _serialise(self.updated_at),
        }
