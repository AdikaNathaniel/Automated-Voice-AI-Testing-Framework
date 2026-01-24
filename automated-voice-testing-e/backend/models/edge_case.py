"""
EdgeCase SQLAlchemy model for documenting tricky test scenarios.

Mirrors the schema introduced in the `023_create_edge_cases` migration and
provides helpers to serialise instances for API responses or service logic.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, Optional
import uuid

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from models.base import Base, GUID

SCENARIO_DEFINITION_TYPE = postgresql.JSONB(astext_type=sa.Text()).with_variant(
    sa.JSON(), "sqlite"
)
TAGS_TYPE = postgresql.ARRAY(sa.Text()).with_variant(sa.JSON(), "sqlite")


class EdgeCase(Base):
    """ORM representation of curated edge cases discovered during testing."""

    __test__ = False  # Prevent pytest from auto-discovering this as a test
    __tablename__ = "edge_cases"

    id = sa.Column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Primary identifier for the edge case record",
    )

    title = sa.Column(
        sa.String(length=255),
        nullable=False,
        comment="Human-readable summary of the edge case",
    )

    description = sa.Column(
        sa.Text(),
        nullable=True,
        comment="Detailed narrative describing the unexpected behaviour",
    )

    category = sa.Column(
        sa.String(length=100),
        nullable=True,
        comment="Category such as audio_quality, ambiguity, or context_loss",
    )

    severity = sa.Column(
        sa.String(length=50),
        nullable=True,
        comment="Impact level of the edge case (critical, high, medium, low)",
    )

    scenario_definition = sa.Column(
        SCENARIO_DEFINITION_TYPE,
        nullable=False,
        server_default=sa.text("'{}'"),
        comment="Structured definition detailing steps, utterances, expectations",
    )

    script_id = sa.Column(
        GUID(),
        sa.ForeignKey("scenario_scripts.id", ondelete='SET NULL'),
        nullable=True,
        index=True,
        comment="Scenario script that exhibits this edge case",
    )

    discovered_date = sa.Column(
        sa.Date(),
        nullable=True,
        comment="Date when the edge case was first reported",
    )

    discovered_by = sa.Column(
        GUID(),
        sa.ForeignKey("users.id", ondelete='SET NULL'),
        nullable=True,
        index=True,
        comment="User who reported or confirmed the edge case",
    )

    tenant_id = sa.Column(
        GUID(),
        sa.ForeignKey("users.id", ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Tenant (organization or user) that owns this edge case",
    )

    status = sa.Column(
        sa.String(length=50),
        nullable=False,
        default="active",
        server_default=sa.text("'active'"),
        comment="Lifecycle state: active, resolved, or wont_fix",
    )

    tags = sa.Column(
        TAGS_TYPE,
        nullable=False,
        default=list,
        comment="Custom tags used for searching and grouping edge cases",
    )

    human_validation_id = sa.Column(
        GUID(),
        sa.ForeignKey("human_validations.id", ondelete='SET NULL'),
        nullable=True,
        index=True,
        comment="Link to the human validation that created this edge case",
    )

    validation_result_id = sa.Column(
        GUID(),
        sa.ForeignKey("validation_results.id", ondelete='SET NULL'),
        nullable=True,
        index=True,
        comment="Link to the validation result being reviewed",
    )

    auto_created = sa.Column(
        sa.Boolean(),
        nullable=False,
        default=False,
        server_default=sa.text("false"),
        comment="Whether this edge case was auto-created from validation or manually created",
    )

    created_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        comment="Timestamp when the edge case was created",
    )

    updated_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
        comment="Timestamp when the edge case was last updated",
    )

    def __init__(self, **kwargs: Any) -> None:
        """Ensure UUID assignment when instantiating without an id."""
        super().__init__(**kwargs)
        if self.id is None:
            self.id = uuid.uuid4()

    def __repr__(self) -> str:
        """Readable representation useful for debugging."""
        return f"<EdgeCase(id={self.id})>"

    def to_dict(self) -> Dict[str, Optional[Any]]:
        """Serialise the edge case into JSON-friendly primitives."""

        def _serialise(value: Optional[Any]) -> Optional[Any]:
            if isinstance(value, uuid.UUID):
                return str(value)
            if isinstance(value, datetime):
                return value.isoformat()
            if isinstance(value, date):
                return value.isoformat()
            return value

        return {
            "id": _serialise(self.id),
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "severity": self.severity,
            "scenario_definition": self.scenario_definition or {},
            "script_id": _serialise(self.script_id),
            "discovered_date": _serialise(self.discovered_date),
            "discovered_by": _serialise(self.discovered_by),
            "tenant_id": _serialise(self.tenant_id),
            "status": self.status,
            "tags": list(self.tags or []),
            "human_validation_id": _serialise(self.human_validation_id),
            "validation_result_id": _serialise(self.validation_result_id),
            "auto_created": self.auto_created,
            "created_at": _serialise(self.created_at),
            "updated_at": _serialise(self.updated_at),
        }
