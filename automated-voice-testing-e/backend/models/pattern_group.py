"""
PatternGroup SQLAlchemy model for grouping similar edge cases.

Identifies patterns in edge cases to help with analysis and prioritization.
Part of Phase 2: Pattern Recognition & Grouping.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship

from models.base import Base, GUID


class PatternGroup(Base):
    """
    ORM representation of a pattern group containing similar edge cases.

    A PatternGroup identifies a recurring pattern across multiple edge cases,
    such as:
    - Time zone confusion ("tomorrow" vs "today")
    - Ambiguous numbers ("8" could be time or quantity)
    - Regional dialect issues (UK vs US English)

    Attributes:
        id: Unique identifier for the pattern group
        name: Short descriptive name (e.g., "Time Reference Confusion")
        description: Detailed explanation of the pattern
        pattern_type: Category of pattern (semantic, entity, context, etc.)
        severity: Impact level (critical, high, medium, low)
        first_seen: When this pattern was first detected
        last_seen: When this pattern was last observed
        occurrence_count: Total number of edge cases matching this pattern
        status: active, resolved, monitoring
        suggested_actions: Recommendations for addressing the pattern
        metadata: Additional pattern-specific data
    """

    __test__ = False  # Prevent pytest auto-discovery
    __tablename__ = "pattern_groups"

    id = sa.Column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Primary identifier for the pattern group",
    )

    name = sa.Column(
        sa.String(length=200),
        nullable=False,
        comment="Short descriptive name of the pattern",
    )

    description = sa.Column(
        sa.Text(),
        nullable=True,
        comment="Detailed explanation of what the pattern represents",
    )

    pattern_type = sa.Column(
        sa.String(length=100),
        nullable=True,
        comment="Type of pattern: semantic, entity, context, ambiguity, etc.",
    )

    severity = sa.Column(
        sa.String(length=50),
        nullable=False,
        default="medium",
        server_default=sa.text("'medium'"),
        comment="Impact level: critical, high, medium, low",
    )

    first_seen = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        comment="When this pattern was first detected",
    )

    last_seen = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
        comment="When this pattern was last observed",
    )

    occurrence_count = sa.Column(
        sa.Integer(),
        nullable=False,
        default=0,
        server_default=sa.text("0"),
        comment="Total number of edge cases matching this pattern",
    )

    status = sa.Column(
        sa.String(length=50),
        nullable=False,
        default="active",
        server_default=sa.text("'active'"),
        comment="Lifecycle state: active, resolved, monitoring",
    )

    suggested_actions = sa.Column(
        postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), "sqlite"),
        nullable=True,
        comment="Recommended actions to address this pattern",
    )

    pattern_metadata = sa.Column(
        postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), "sqlite"),
        nullable=True,
        comment="Additional pattern-specific data and metrics",
    )

    created_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        comment="Timestamp when the pattern group was created",
    )

    updated_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
        comment="Timestamp when the pattern group was last updated",
    )

    def __init__(self, **kwargs: Any) -> None:
        """Ensure UUID assignment when instantiating without an id."""
        super().__init__(**kwargs)
        if self.id is None:
            self.id = uuid.uuid4()

    def __repr__(self) -> str:
        """Readable representation useful for debugging."""
        return f"<PatternGroup(id={self.id}, name='{self.name}')>"

    def to_dict(self) -> Dict[str, Optional[Any]]:
        """Serialise the pattern group into JSON-friendly primitives."""

        def _serialise(value: Optional[Any]) -> Optional[Any]:
            if isinstance(value, uuid.UUID):
                return str(value)
            if isinstance(value, datetime):
                return value.isoformat()
            return value

        return {
            "id": _serialise(self.id),
            "name": self.name,
            "description": self.description,
            "pattern_type": self.pattern_type,
            "severity": self.severity,
            "first_seen": _serialise(self.first_seen),
            "last_seen": _serialise(self.last_seen),
            "occurrence_count": self.occurrence_count,
            "status": self.status,
            "suggested_actions": self.suggested_actions or [],
            "pattern_metadata": self.pattern_metadata or {},
            "created_at": _serialise(self.created_at),
            "updated_at": _serialise(self.updated_at),
        }


class EdgeCasePatternLink(Base):
    """
    Association table linking edge cases to pattern groups.

    Allows many-to-many relationship: an edge case can match multiple patterns,
    and a pattern can contain multiple edge cases.

    Attributes:
        id: Unique identifier for the link
        edge_case_id: Reference to edge case
        pattern_group_id: Reference to pattern group
        similarity_score: How closely this edge case matches the pattern (0.0-1.0)
        added_at: When this edge case was added to the pattern group
    """

    __test__ = False
    __tablename__ = "edge_case_pattern_links"

    id = sa.Column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    edge_case_id = sa.Column(
        GUID(),
        sa.ForeignKey("edge_cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Edge case in this pattern group",
    )

    pattern_group_id = sa.Column(
        GUID(),
        sa.ForeignKey("pattern_groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Pattern group this edge case belongs to",
    )

    similarity_score = sa.Column(
        sa.Float(),
        nullable=True,
        comment="Similarity score (0.0-1.0) indicating pattern match strength",
    )

    added_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        comment="When this edge case was added to the pattern group",
    )

    # Ensure unique edge_case + pattern_group combination
    __table_args__ = (
        sa.UniqueConstraint(
            "edge_case_id",
            "pattern_group_id",
            name="uix_edge_case_pattern"
        ),
    )

    def __init__(self, **kwargs: Any) -> None:
        """Ensure UUID assignment when instantiating without an id."""
        super().__init__(**kwargs)
        if self.id is None:
            self.id = uuid.uuid4()

    def __repr__(self) -> str:
        """Readable representation useful for debugging."""
        return (
            f"<EdgeCasePatternLink("
            f"edge_case_id={self.edge_case_id}, "
            f"pattern_group_id={self.pattern_group_id}"
            f")>"
        )

    def to_dict(self) -> Dict[str, Optional[Any]]:
        """Serialise the link into JSON-friendly primitives."""

        def _serialise(value: Optional[Any]) -> Optional[Any]:
            if isinstance(value, uuid.UUID):
                return str(value)
            if isinstance(value, datetime):
                return value.isoformat()
            return value

        return {
            "id": _serialise(self.id),
            "edge_case_id": _serialise(self.edge_case_id),
            "pattern_group_id": _serialise(self.pattern_group_id),
            "similarity_score": self.similarity_score,
            "added_at": _serialise(self.added_at),
        }
