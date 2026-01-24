"""
Comment service providing CRUD helpers for collaborative discussions (TASK-366).

Supports creating, replying, listing, updating, and deleting comments attached
to core domain entities (test cases, defects, validations). Handles mention
normalisation, permission checks, and eager loading of threaded replies.
"""

from __future__ import annotations

import inspect
from typing import Any, Iterable, Optional
from uuid import UUID, uuid4

from sqlalchemy import asc
from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.comment import Comment

SUPPORTED_ENTITY_TYPES: set[str] = {'test_case', 'defect', 'validation'}
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 200


def _ensure_supported_entity(entity_type: str) -> None:
    """Raise ValueError if the supplied entity type is unsupported."""
    if entity_type not in SUPPORTED_ENTITY_TYPES:
        raise ValueError(
            f"Unsupported entity type '{entity_type}'. "
            f"Expected one of: {', '.join(sorted(SUPPORTED_ENTITY_TYPES))}"
        )


def _normalise_mentions(mentions: Optional[Iterable[Any]]) -> list[dict[str, Any]]:
    """
    Coerce mentions payloads into a normalised list of dictionaries.

    Accepts iterables of UUIDs/strings/dicts with `user_id`. Any additional
    metadata present on dict inputs is preserved.
    """
    if not mentions:
        return []

    normalised: list[dict[str, Any]] = []
    for item in mentions:
        if item is None:
            continue
        if isinstance(item, dict):
            payload = dict(item)
            if "user_id" in payload and isinstance(payload["user_id"], UUID):
                payload["user_id"] = str(payload["user_id"])
            normalised.append(payload)
            continue
        if isinstance(item, UUID):
            normalised.append({"user_id": str(item)})
            continue
        if isinstance(item, (str, bytes)):
            normalised.append({"user_id": item.decode() if isinstance(item, bytes) else item})
            continue
        raise TypeError("mentions entries must be UUID, string, or mapping with user_id")
    return normalised


async def _commit_and_refresh(db: AsyncSession, instance: Comment) -> Comment:
    """Commit transaction (awaiting as needed) and refresh the provided instance."""
    commit_result = db.commit()
    if inspect.isawaitable(commit_result):
        await commit_result

    refresh_result = db.refresh(instance)
    if inspect.isawaitable(refresh_result):
        await refresh_result

    return instance


class CommentService:
    """Service layer encapsulating comment persistence operations."""

    def __init__(self, *, default_limit: int = DEFAULT_PAGE_SIZE) -> None:
        self.default_limit = max(1, min(default_limit, MAX_PAGE_SIZE))

    async def create_comment(self, *, db: AsyncSession, entity_type: str, entity_id: UUID,
                             author_id: UUID, content: str,
                             mentions: Optional[Iterable[Any]] = None,
                             parent_comment_id: Optional[UUID] = None) -> Comment:
        """Create a new comment associated with an entity."""
        _ensure_supported_entity(entity_type)

        comment = Comment(
            id=uuid4(),
            entity_type=entity_type,
            entity_id=entity_id,
            parent_comment_id=parent_comment_id,
            author_id=author_id,
            content=content.strip(),
            mentions=_normalise_mentions(mentions),
        )

        db.add(comment)
        return await _commit_and_refresh(db, comment)

    async def reply_to_comment(
        self,
        *,
        db: AsyncSession,
        parent_comment_id: UUID,
        author_id: UUID,
        content: str,
        mentions: Optional[Iterable[Any]] = None,
    ) -> Comment:
        """Create a reply to an existing comment."""
        statement = select(Comment).where(Comment.id == parent_comment_id)
        execute_result = db.execute(statement)
        if inspect.isawaitable(execute_result):
            execute_result = await execute_result
        parent = execute_result.scalar_one_or_none()
        if parent is None:
            raise ValueError(f"Parent comment {parent_comment_id} was not found")

        return await self.create_comment(
            db=db,
            entity_type=parent.entity_type,
            entity_id=parent.entity_id,
            parent_comment_id=parent_comment_id,
            author_id=author_id,
            content=content,
            mentions=mentions,
        )

    async def list_comments(self, *, db: AsyncSession, entity_type: str, entity_id: UUID,
                            limit: Optional[int] = None, offset: int = 0,
                            include_replies: bool = True) -> list[Comment]:
        """Retrieve comments for the specified entity."""
        _ensure_supported_entity(entity_type)
        effective_limit = max(1, min(limit or self.default_limit, MAX_PAGE_SIZE))
        offset = max(0, offset)

        statement = (
            select(Comment)
            .where(
                Comment.entity_type == entity_type,
                Comment.entity_id == entity_id,
                Comment.parent_comment_id.is_(None),
            )
            .order_by(asc(Comment.created_at))
            .offset(offset)
            .limit(effective_limit)
        )

        if include_replies:
            statement = statement.options(
                selectinload(Comment.replies)
            )

        execute_result = db.execute(statement)
        if inspect.isawaitable(execute_result):
            result = await execute_result
        else:
            result = execute_result

        return result.unique().scalars().all()

    async def update_comment(
        self,
        *,
        db: AsyncSession,
        comment_id: UUID,
        editor_id: UUID,
        content: str,
        mentions: Optional[Iterable[Any]] = None,
    ) -> Comment:
        """Update comment content and mentions payload."""
        statement = select(Comment).where(Comment.id == comment_id)
        execute_result = db.execute(statement)
        if inspect.isawaitable(execute_result):
            execute_result = await execute_result
        comment = execute_result.scalar_one_or_none()
        if comment is None:
            raise ValueError(f"Comment {comment_id} was not found")
        if comment.author_id != editor_id:
            raise PermissionError("Only the original author can edit a comment")

        comment.content = content.strip()
        comment.mentions = _normalise_mentions(mentions)
        comment.is_edited = True

        return await _commit_and_refresh(db, comment)

    async def delete_comment(
        self,
        *,
        db: AsyncSession,
        comment_id: UUID,
        requester_id: UUID,
        force: bool = False,
    ) -> bool:
        """Delete a comment and its replies (cascade) if the requester is permitted."""
        statement = select(Comment).where(Comment.id == comment_id)
        execute_result = db.execute(statement)
        if inspect.isawaitable(execute_result):
            execute_result = await execute_result
        comment = execute_result.scalar_one_or_none()
        if comment is None:
            return False

        if not force and comment.author_id != requester_id:
            raise PermissionError("Cannot delete a comment authored by another user")

        db.delete(comment)
        commit_result = db.commit()
        if inspect.isawaitable(commit_result):
            await commit_result
        return True

    async def delete_comments_for_entity(
        self,
        *,
        db: AsyncSession,
        entity_type: str,
        entity_id: UUID,
    ) -> int:
        """Bulk delete all comments attached to a specific entity."""
        _ensure_supported_entity(entity_type)

        statement = (
            delete(Comment)
            .where(Comment.entity_type == entity_type, Comment.entity_id == entity_id)
            .execution_options(synchronize_session=False)
        )

        execute_result = db.execute(statement)
        if inspect.isawaitable(execute_result):
            execute_result = await execute_result

        commit_result = db.commit()
        if inspect.isawaitable(commit_result):
            await commit_result

        if hasattr(execute_result, "rowcount"):
            return execute_result.rowcount or 0
        return 0


comment_service = CommentService()


async def create_comment(**kwargs: Any) -> Comment:
    """Delegate to CommentService.create_comment."""
    return await comment_service.create_comment(**kwargs)


async def reply_to_comment(**kwargs: Any) -> Comment:
    """Delegate to CommentService.reply_to_comment."""
    return await comment_service.reply_to_comment(**kwargs)


async def list_comments(**kwargs: Any) -> list[Comment]:
    """Delegate to CommentService.list_comments."""
    return await comment_service.list_comments(**kwargs)


async def update_comment(**kwargs: Any) -> Comment:
    """Delegate to CommentService.update_comment."""
    return await comment_service.update_comment(**kwargs)


async def delete_comment(**kwargs: Any) -> bool:
    """Delegate to CommentService.delete_comment."""
    return await comment_service.delete_comment(**kwargs)
