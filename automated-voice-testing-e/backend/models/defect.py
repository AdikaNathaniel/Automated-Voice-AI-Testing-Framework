"""
Defect SQLAlchemy model for defect tracking workflows.

Mirrors the schema from the `defects` table migration and provides helpers for
serialising records to dictionaries used by higher-level services.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
import uuid

import sqlalchemy as sa

from models.base import Base, GUID


class Defect(Base):
    """ORM model representing a tracked defect discovered during test runs."""

    __test__ = False  # Prevent pytest from treating this as a test case
    __tablename__ = "defects"

    id = sa.Column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Primary identifier for the defect record",
    )

    tenant_id = sa.Column(
        GUID(),
        nullable=True,
        index=True,
        comment="Tenant identifier for multi-tenant scoping",
    )

    script_id = sa.Column(
        GUID(),
        sa.ForeignKey("scenario_scripts.id", ondelete='SET NULL'),
        nullable=True,
        index=True,
        comment="Scenario script that produced the defect",
    )

    execution_id = sa.Column(
        GUID(),
        sa.ForeignKey("multi_turn_executions.id", ondelete='SET NULL'),
        nullable=True,
        index=True,
        comment="Multi-turn execution where the defect was detected",
    )

    suite_run_id = sa.Column(
        GUID(),
        sa.ForeignKey("suite_runs.id", ondelete='SET NULL'),
        nullable=True,
        comment="Suite run in which the defect was detected",
    )

    severity = sa.Column(
        sa.String(length=50),
        nullable=False,
        comment="Severity classification (critical, high, medium, low)",
    )

    category = sa.Column(
        sa.String(length=100),
        nullable=False,
        comment="Defect category such as semantic, timing, or audio",
    )

    title = sa.Column(
        sa.String(length=255),
        nullable=False,
        comment="Short summary describing the defect",
    )

    description = sa.Column(
        sa.Text(),
        nullable=True,
        comment="Detailed narrative describing the defect",
    )

    language_code = sa.Column(
        sa.String(length=10),
        nullable=True,
        comment="Language code associated with the defect",
    )

    detected_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        comment="Timestamp when the defect was identified",
    )

    status = sa.Column(
        sa.String(length=50),
        nullable=False,
        default="open",
        server_default=sa.text("'open'"),
        comment="Lifecycle status (open, in_progress, resolved)",
    )

    assigned_to = sa.Column(
        GUID(),
        sa.ForeignKey("users.id", ondelete='SET NULL'),
        nullable=True,
        index=True,
        comment="User currently assigned to resolve the defect",
    )

    resolved_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when the defect was resolved",
    )

    created_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        comment="Insert timestamp for the defect record",
    )

    jira_issue_key = sa.Column(
        sa.String(length=100),
        nullable=True,
        comment="Associated Jira issue key (e.g., QA-123)",
    )

    jira_issue_url = sa.Column(
        sa.String(length=2048),
        nullable=True,
        comment="Link to the Jira issue for quick navigation",
    )

    jira_status = sa.Column(
        sa.String(length=100),
        nullable=True,
        comment="Last known Jira workflow status for the linked issue",
    )

    def __init__(self, **kwargs: Any) -> None:
        """Ensure UUID assignment on instantiation if not provided."""
        super().__init__(**kwargs)
        if self.id is None:
            self.id = uuid.uuid4()

    def __repr__(self) -> str:
        """Human-readable representation of the defect."""
        return f"<Defect(id={self.id})>"

    def to_dict(self) -> Dict[str, Optional[Any]]:
        """Serialise the defect into primitives for API responses."""
        def _serialise(value: Optional[Any]) -> Optional[Any]:
            if isinstance(value, uuid.UUID):
                return str(value)
            if isinstance(value, datetime):
                return value.isoformat()
            return value

        return {
            "id": _serialise(self.id),
            "script_id": _serialise(self.script_id),
            "execution_id": _serialise(self.execution_id),
            "suite_run_id": _serialise(self.suite_run_id),
            "severity": self.severity,
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "language_code": self.language_code,
            "detected_at": _serialise(self.detected_at),
            "status": self.status,
            "assigned_to": _serialise(self.assigned_to),
            "resolved_at": _serialise(self.resolved_at),
            "created_at": _serialise(self.created_at),
            "jira_issue_key": self.jira_issue_key,
            "jira_issue_url": self.jira_issue_url,
            "jira_status": self.jira_status,
        }
