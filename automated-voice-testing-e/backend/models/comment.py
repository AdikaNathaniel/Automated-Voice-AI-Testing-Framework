"""
Comment SQLAlchemy model (TASK-366).

Represents user-authored comments associated with core entities such as test
cases, defects, and validations. Mirrors the schema introduced in the
027_create_comments migration and exposes helper relationships for threaded
discussions.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, BaseModel, GUID

if TYPE_CHECKING:  # pragma: no cover - type checking only
    from models.user import User


class Comment(Base, BaseModel):
    """Persistent comment entity supporting threaded replies and mentions."""

    __tablename__ = "comments"
    __test__ = False  # Prevent pytest from collecting this class as a test

    entity_type: Mapped[str] = mapped_column(
        sa.String(length=50),
        nullable=False,
        index=True,
        comment="Domain entity type the comment is attached to (test_case, defect, validation)",
    )

    entity_id: Mapped[Any] = mapped_column(
        GUID(),
        nullable=False,
        index=True,
        comment="Identifier of the entity the comment references",
    )

    parent_comment_id: Mapped[Optional[Any]] = mapped_column(
        GUID(),
        sa.ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Optional parent comment to support threaded replies",
    )

    author_id: Mapped[Any] = mapped_column(
        GUID(),
        sa.ForeignKey("users.id"),
        nullable=False,
        index=True,
        comment="Author of the comment referencing users table",
    )

    content: Mapped[str] = mapped_column(
        sa.Text(),
        nullable=False,
        comment="Comment body text (supports markdown)",
    )

    mentions: Mapped[List[Dict[str, Any]]] = mapped_column(
        postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), "sqlite"),
        nullable=False,
        default=list,
        comment="Array of mentioned user identifiers and metadata",
    )

    is_edited: Mapped[bool] = mapped_column(
        sa.Boolean(),
        nullable=False,
        default=False,
        server_default=sa.text("false"),
        comment="Flag indicating whether the comment has been edited",
    )

    author: Mapped["User"] = relationship(
        "User",
        backref="comments",
        foreign_keys=[author_id],
        lazy="joined",
        viewonly=True,
        doc="Relationship to the authoring user",
    )

    parent: Mapped[Optional["Comment"]] = relationship(
        "Comment",
        remote_side="Comment.id",
        foreign_keys=[parent_comment_id],
        primaryjoin="Comment.parent_comment_id == Comment.id",
        backref=sa.orm.backref(
            "replies",
            cascade="all, delete-orphan",
            lazy="selectin",
            order_by="Comment.created_at",
        ),
        doc="Optional parent comment when this entry is a reply",
    )

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the comment into JSON-friendly primitives."""

        def _serialise(value: Any) -> Any:
            if value is None:
                return None
            if isinstance(value, datetime):
                return value.isoformat()
            if hasattr(value, "hex"):  # UUID compatibility
                return str(value)
            return value

        return {
            "id": _serialise(self.id),
            "entity_type": self.entity_type,
            "entity_id": _serialise(self.entity_id),
            "parent_comment_id": _serialise(self.parent_comment_id),
            "author_id": _serialise(self.author_id),
            "content": self.content,
            "mentions": self.mentions,
            "is_edited": self.is_edited,
            "created_at": _serialise(self.created_at),
            "updated_at": _serialise(self.updated_at),
        }

    def __repr__(self) -> str:
        """Debug-friendly representation of the comment."""
        return (
            f"<Comment(id={self.id}, entity_type={self.entity_type!r}, "
            f"entity_id={self.entity_id}, author_id={self.author_id})>"
        )
