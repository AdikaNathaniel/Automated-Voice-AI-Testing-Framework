"""
ActivityLog SQLAlchemy model representing auditable user actions.

Mirrors the schema introduced in the 026_create_activity_log migration and
provides helpers for serialising entries for API responses or background jobs.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional, TYPE_CHECKING
import uuid

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship

from models.base import Base, GUID

if TYPE_CHECKING:  # pragma: no cover - import guard for type checkers
    pass


class ActivityLog(Base):
    """ORM mapping for persisted activity log entries."""

    __tablename__ = "activity_log"
    __test__ = False  # Prevent pytest from collecting as a test case

    id = sa.Column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Primary identifier for the activity event",
    )

    user_id = sa.Column(
        GUID(),
        sa.ForeignKey("users.id"),
        nullable=False,
        index=True,
        comment="Reference to the user who performed the action",
    )

    action_type = sa.Column(
        sa.String(length=100),
        nullable=False,
        index=True,
        comment="Short descriptor for the type of action performed",
    )

    resource_type = sa.Column(
        sa.String(length=100),
        nullable=True,
        index=True,
        comment="Domain entity affected by the action, e.g. test_case",
    )

    resource_id = sa.Column(
        GUID(),
        nullable=True,
        comment="Identifier of the affected resource when applicable",
    )

    action_description = sa.Column(
        sa.Text(),
        nullable=True,
        comment="Human-readable description of the action for activity feeds",
    )

    metadata_payload = sa.Column(
        "metadata",
        postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), "sqlite"),
        nullable=True,
        comment="Structured metadata payload describing the event",
    )

    ip_address = sa.Column(
        postgresql.INET().with_variant(sa.String(45), "sqlite"),
        nullable=True,
        comment="IP address associated with the action, if available",
    )

    created_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("(CURRENT_TIMESTAMP)"),
        comment="Timestamp when the activity was recorded",
    )

    user = relationship(
        "User",
        backref="activity_log_entries",
        foreign_keys=[user_id],
        lazy="joined",
        viewonly=True,
        doc="Relationship to the user who triggered the event",
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialise the activity log entry ensuring UUID presence."""
        super().__init__(**kwargs)
        if self.id is None:
            self.id = uuid.uuid4()

    def __repr__(self) -> str:
        """Return a concise representation useful during debugging."""
        return f"<ActivityLog(id={self.id}, action_type={self.action_type!r})>"

    def to_dict(self) -> Dict[str, Optional[Any]]:
        """Serialise the activity entry into JSON-friendly primitives."""

        def _serialise(value: Optional[Any]) -> Optional[Any]:
            if value is None:
                return None
            if isinstance(value, uuid.UUID):
                return str(value)
            if isinstance(value, datetime):
                return value.isoformat()
            return value

        payload: Dict[str, Optional[Any]] = {
            "id": _serialise(self.id),
            "user_id": _serialise(self.user_id),
            "action_type": self.action_type,
            "resource_type": self.resource_type,
            "resource_id": _serialise(self.resource_id),
            "action_description": self.action_description,
            "metadata": self.metadata_payload or {},
            "ip_address": _serialise(self.ip_address),
            "created_at": _serialise(self.created_at),
        }

        return payload
