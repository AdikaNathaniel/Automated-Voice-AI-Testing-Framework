"""
KnowledgeBase SQLAlchemy model representing curated documentation articles.

Mirrors the schema introduced in the 025_create_knowledge_base migration and
provides helper methods for serialisation commonly used by services and APIs.

Phase 3 Enhancement: Added pattern_group_id, source_type, and tags fields
to support auto-generation of KB articles from edge case patterns.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import JSON

from sqlalchemy.orm import relationship

from models.base import Base, BaseModel, GUID

# Use ARRAY for PostgreSQL, JSON for SQLite (testing)
# In SQLite, we store arrays as JSON arrays
ARRAY_TYPE = lambda item_type: ARRAY(item_type).with_variant(JSON(), "sqlite")

if TYPE_CHECKING:  # pragma: no cover - type checking only
    from models.pattern_group import PatternGroup


class KnowledgeBase(Base, BaseModel):
    """Persisted knowledge base article authored by a system user."""

    __tablename__ = "knowledge_base"
    __test__ = False  # Prevent pytest from treating this class as a test case

    title = sa.Column(
        sa.String(length=255),
        nullable=False,
        comment="Human-readable article title",
    )

    category = sa.Column(
        sa.String(length=100),
        nullable=True,
        index=True,
        comment="Optional grouping such as troubleshooting or best_practices",
    )

    content = sa.Column(
        sa.Text(),
        nullable=False,
        comment="Rich text or markdown body of the article",
    )

    content_format = sa.Column(
        sa.String(length=50),
        nullable=False,
        server_default=sa.text("'markdown'"),
        comment="Content format descriptor e.g. markdown or html",
    )

    author_id = sa.Column(
        GUID(),
        sa.ForeignKey("users.id"),
        nullable=False,
        index=True,
        comment="Reference to the author in the users table",
    )

    tenant_id = sa.Column(
        GUID(),
        sa.ForeignKey("users.id", ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Tenant (organization or user) that owns this article",
    )

    is_published = sa.Column(
        sa.Boolean(),
        nullable=False,
        default=False,
        server_default=sa.text("false"),
        comment="Whether the article is visible to readers",
    )

    views = sa.Column(
        sa.Integer(),
        nullable=False,
        default=0,
        server_default=sa.text("0"),
        comment="Total number of recorded article views",
    )

    # Phase 3: Pattern Group Integration
    pattern_group_id = sa.Column(
        GUID(),
        sa.ForeignKey("pattern_groups.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Link to pattern group if auto-generated from pattern analysis",
    )

    source_type = sa.Column(
        sa.String(length=50),
        nullable=False,
        default="manual",
        server_default=sa.text("'manual'"),
        comment="Article source: manual, auto_generated, pattern_derived",
    )

    tags = sa.Column(
        ARRAY_TYPE(sa.String(100)),
        nullable=False,
        default=list,
        # Note: server_default only applies to PostgreSQL; SQLite uses default=list
        server_default=None,  # Removed PostgreSQL-specific syntax for SQLite compatibility
        comment="Array of tags for multi-label categorization",
    )

    author = relationship(
        "User",
        backref="knowledge_base_articles",
        foreign_keys=[author_id],
        lazy="joined",
        viewonly=True,
        doc="Relationship to the authoring user",
    )

    pattern_group = relationship(
        "PatternGroup",
        backref="knowledge_base_articles",
        foreign_keys=[pattern_group_id],
        lazy="joined",
        viewonly=True,
        doc="Relationship to the source pattern group if auto-generated",
    )

    def __repr__(self) -> str:
        """Debug-friendly string representation."""
        return f"<KnowledgeBase(id={self.id}, title={self.title!r}, published={self.is_published})>"

    def to_dict(self) -> Dict[str, Optional[Any]]:
        """Serialise the article into JSON-friendly primitives."""

        def _serialise(value: Optional[Any]) -> Optional[Any]:
            if value is None:
                return None
            if isinstance(value, datetime):
                return value.isoformat()
            if hasattr(value, "hex"):  # UUID compatibility
                return str(value)
            return value

        return {
            "id": _serialise(self.id),
            "title": self.title,
            "category": self.category,
            "content": self.content,
            "content_format": self.content_format,
            "author_id": _serialise(self.author_id),
            "tenant_id": _serialise(self.tenant_id),
            "is_published": self.is_published,
            "views": self.views,
            "pattern_group_id": _serialise(self.pattern_group_id),
            "source_type": self.source_type,
            "tags": self.tags or [],
            "created_at": _serialise(self.created_at),
            "updated_at": _serialise(self.updated_at),
        }
