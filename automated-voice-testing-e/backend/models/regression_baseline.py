"""
Regression baseline models.

Stores the approved baseline result for each scenario script so regression
detection has a canonical reference point. Includes history tracking for
audit trail.

Models:
- RegressionBaseline: Current approved baseline per script (one per script)
- BaselineHistory: Historical record of all baseline versions (audit trail)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional, TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from models.base import Base, BaseModel, GUID

if TYPE_CHECKING:
    pass


class RegressionBaseline(Base, BaseModel):
    """
    Current approved baseline for a scenario script.

    Each script has at most one baseline record. When a new baseline is
    approved, the current record is updated and the previous version is
    archived to BaselineHistory.
    """

    __tablename__ = "regression_baselines"

    # Note: Uses String(36) to match existing migration structure
    script_id = sa.Column(
        sa.String(36),
        nullable=False,
        unique=True,
        index=True,
        comment="Scenario script whose baseline is stored",
    )

    result_status = sa.Column(
        sa.String(32),
        nullable=False,
        comment="Status associated with the approved baseline (e.g., passed)",
    )

    metrics = sa.Column(
        sa.JSON,
        nullable=False,
        default=dict,
        comment="Numeric metrics captured for the baseline run",
    )

    version = sa.Column(
        sa.Integer,
        nullable=False,
        default=1,
        comment="Monotonic version number incremented on each approval",
    )

    # Note: Uses String(36) to match existing migration structure
    approved_by = sa.Column(
        sa.String(36),
        nullable=True,
        comment="User who approved the baseline",
    )

    approved_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when the baseline was approved",
    )

    note = sa.Column(
        sa.Text,
        nullable=True,
        comment="Optional justification or note associated with the approval",
    )

    # Relationships
    history = relationship(
        "BaselineHistory",
        back_populates="baseline",
        order_by="desc(BaselineHistory.version)",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<RegressionBaseline(script_id={self.script_id}, "
            f"status={self.result_status}, version={self.version})>"
        )

    def archive_current(self) -> "BaselineHistory":
        """
        Create a history record from the current state before updating.

        Returns:
            BaselineHistory record with current values
        """
        return BaselineHistory(
            baseline_id=self.id,
            script_id=self.script_id,
            version=self.version,
            result_status=self.result_status,
            metrics=dict(self.metrics or {}),
            approved_by=self.approved_by,
            approved_at=self.approved_at,
            note=self.note,
        )

    def update_from_snapshot(
        self,
        *,
        status: str,
        metrics: Dict[str, Any],
        approved_by: Optional[str],
        approved_at: datetime,
        note: Optional[str],
    ) -> None:
        """Replace the stored baseline details and audit metadata."""
        self.result_status = status
        self.metrics = dict(metrics or {})
        self.approved_by = approved_by
        self.approved_at = approved_at
        self.note = note


class BaselineHistory(Base, BaseModel):
    """
    Historical record of baseline versions.

    Each time a baseline is updated, the previous version is archived here.
    This provides an audit trail and allows viewing baseline changes over time.
    """

    __tablename__ = "baseline_history"

    baseline_id = sa.Column(
        GUID(),
        sa.ForeignKey("regression_baselines.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to the parent baseline record",
    )

    # Note: Uses String(36) to match parent table structure
    script_id = sa.Column(
        sa.String(36),
        nullable=False,
        index=True,
        comment="Scenario script ID (denormalized for query efficiency)",
    )

    version = sa.Column(
        sa.Integer,
        nullable=False,
        comment="Version number at time of archival",
    )

    result_status = sa.Column(
        sa.String(32),
        nullable=False,
        comment="Status at this version",
    )

    metrics = sa.Column(
        sa.JSON,
        nullable=False,
        default=dict,
        comment="Metrics at this version",
    )

    # Note: Uses String(36) to match parent table structure
    approved_by = sa.Column(
        sa.String(36),
        nullable=True,
        comment="User who approved this version",
    )

    approved_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=True,
        comment="When this version was approved",
    )

    note = sa.Column(
        sa.Text,
        nullable=True,
        comment="Note for this version",
    )

    # Relationships
    baseline = relationship(
        "RegressionBaseline",
        back_populates="history",
    )

    # Unique constraint on baseline_id + version
    __table_args__ = (
        sa.UniqueConstraint("baseline_id", "version", name="uq_baseline_history_version"),
    )

    def __repr__(self) -> str:
        return (
            f"<BaselineHistory(script_id={self.script_id}, "
            f"version={self.version}, status={self.result_status})>"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "version": self.version,
            "status": self.result_status,
            "metrics": self.metrics or {},
            "approved_by": str(self.approved_by) if self.approved_by else None,
            "approved_at": (
                self.approved_at.isoformat() if self.approved_at else None
            ),
            "note": self.note,
        }
