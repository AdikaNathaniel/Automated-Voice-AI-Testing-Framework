"""
Regression SQLAlchemy model for tracking detected regressions.

Unlike the ephemeral regression detection that compares current runs to baselines,
this model provides persistent tracking of regressions over time, allowing:
- Historical tracking of when regressions first appeared
- Linking regressions to defects for workflow management
- Tracking resolution of regressions
- Metrics on regression trends and frequency
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
import uuid

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from models.base import Base, GUID


class Regression(Base):
    """ORM model representing a detected and tracked regression."""

    __test__ = False  # Prevent pytest from treating this as a test case
    __tablename__ = "regressions"

    id = sa.Column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Primary identifier for the regression record",
    )

    tenant_id = sa.Column(
        GUID(),
        nullable=True,
        index=True,
        comment="Tenant identifier for multi-tenant scoping",
    )

    script_id = sa.Column(
        GUID(),
        sa.ForeignKey("scenario_scripts.id", ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Scenario script where regression was detected",
    )

    category = sa.Column(
        sa.String(length=50),
        nullable=False,
        comment="Regression category: status, metric, or llm",
    )

    severity = sa.Column(
        sa.String(length=50),
        nullable=False,
        default="medium",
        server_default=sa.text("'medium'"),
        comment="Severity: low, medium, high, critical",
    )

    status = sa.Column(
        sa.String(length=50),
        nullable=False,
        default="active",
        server_default=sa.text("'active'"),
        comment="Regression status: active, resolved, ignored, investigating",
    )

    baseline_version = sa.Column(
        sa.Integer(),
        nullable=True,
        comment="Version of baseline used for detection",
    )

    detection_date = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        comment="When the regression was first detected",
    )

    resolution_date = sa.Column(
        sa.DateTime(timezone=True),
        nullable=True,
        comment="When the regression was resolved",
    )

    last_seen_date = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        comment="Most recent occurrence of this regression",
    )

    occurrence_count = sa.Column(
        sa.Integer(),
        nullable=False,
        default=1,
        server_default=sa.text("1"),
        comment="Number of times this regression has been detected",
    )

    details = sa.Column(
        sa.JSON,
        nullable=False,
        default=dict,
        server_default=sa.text("'{}'"),
        comment="Regression details: baseline values, current values, deltas, etc.",
    )

    linked_defect_id = sa.Column(
        GUID(),
        sa.ForeignKey("defects.id", ondelete='SET NULL'),
        nullable=True,
        index=True,
        comment="Defect created to track this regression",
    )

    resolved_by = sa.Column(
        GUID(),
        sa.ForeignKey("users.id", ondelete='SET NULL'),
        nullable=True,
        comment="User who resolved this regression",
    )

    resolution_note = sa.Column(
        sa.Text(),
        nullable=True,
        comment="Note explaining how regression was resolved",
    )

    created_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        comment="Record creation timestamp",
    )

    updated_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
        comment="Record last update timestamp",
    )

    # Relationships
    script = relationship("ScenarioScript", foreign_keys=[script_id])
    linked_defect = relationship("Defect", foreign_keys=[linked_defect_id])
    resolver = relationship("User", foreign_keys=[resolved_by])

    def __init__(self, **kwargs: Any) -> None:
        """Ensure UUID assignment on instantiation if not provided."""
        super().__init__(**kwargs)
        if self.id is None:
            self.id = uuid.uuid4()

    def __repr__(self) -> str:
        """Human-readable representation of the regression."""
        return f"<Regression(id={self.id}, script_id={self.script_id}, status={self.status})>"

    def to_dict(self) -> Dict[str, Optional[Any]]:
        """Serialize the regression into primitives for API responses."""
        def _serialise(value: Optional[Any]) -> Optional[Any]:
            if isinstance(value, uuid.UUID):
                return str(value)
            if isinstance(value, datetime):
                return value.isoformat()
            return value

        return {
            "id": _serialise(self.id),
            "tenant_id": _serialise(self.tenant_id),
            "script_id": _serialise(self.script_id),
            "category": self.category,
            "severity": self.severity,
            "status": self.status,
            "baseline_version": self.baseline_version,
            "detection_date": _serialise(self.detection_date),
            "resolution_date": _serialise(self.resolution_date),
            "last_seen_date": _serialise(self.last_seen_date),
            "occurrence_count": self.occurrence_count,
            "details": self.details or {},
            "linked_defect_id": _serialise(self.linked_defect_id),
            "resolved_by": _serialise(self.resolved_by),
            "resolution_note": self.resolution_note,
            "created_at": _serialise(self.created_at),
            "updated_at": _serialise(self.updated_at),
        }

    def update_occurrence(self, new_details: Dict[str, Any]) -> None:
        """Update regression with new occurrence."""
        self.last_seen_date = datetime.now(datetime.timezone.utc) if hasattr(datetime, 'timezone') else datetime.utcnow()
        self.occurrence_count += 1
        # Merge new details with existing
        if isinstance(self.details, dict):
            self.details = {**self.details, **new_details}
        else:
            self.details = new_details

    def resolve(self, resolved_by: Optional[uuid.UUID], note: Optional[str] = None) -> None:
        """Mark regression as resolved."""
        self.status = "resolved"
        self.resolution_date = datetime.now(datetime.timezone.utc) if hasattr(datetime, 'timezone') else datetime.utcnow()
        self.resolved_by = resolved_by
        if note:
            self.resolution_note = note

    def link_defect(self, defect_id: uuid.UUID) -> None:
        """Link a defect to this regression."""
        self.linked_defect_id = defect_id
        self.status = "investigating"
