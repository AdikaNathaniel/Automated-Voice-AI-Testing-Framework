"""
Activity logging service for recording and retrieving user actions.

Provides helpers to:
- Persist ActivityLog entries with optional contextual metadata
- Fetch recent activity with lightweight filtering and pagination support
"""

from __future__ import annotations

from datetime import datetime
import inspect
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import and_
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from models.activity_log import ActivityLog

# Reasonable default limit for recent activity views
DEFAULT_ACTIVITY_LIMIT = 50
MAX_ACTIVITY_LIMIT = 200


def _coerce_metadata(metadata: Optional[dict[str, Any]]) -> dict[str, Any] | None:
    """Normalise metadata payloads ensuring serialisable dictionaries."""
    if metadata is None:
        return None
    if isinstance(metadata, dict):
        return metadata
    if hasattr(metadata, "model_dump"):
        return metadata.model_dump()
    if hasattr(metadata, "dict"):
        return metadata.dict()
    raise TypeError("metadata must be a mapping or dataclass-like object")


def _apply_activity_filters(statement: Select, *, user_id: Optional[UUID] = None,
                            action_type: Optional[str] = None,
                            resource_type: Optional[str] = None,
                            since: Optional[datetime] = None) -> Select:
    """Attach optional WHERE clauses to the base select statement."""
    conditions: list[Any] = []

    if user_id is not None:
        conditions.append(ActivityLog.user_id == user_id)
    if action_type:
        conditions.append(ActivityLog.action_type == action_type)
    if resource_type:
        conditions.append(ActivityLog.resource_type == resource_type)
    if since:
        conditions.append(ActivityLog.created_at >= since)

    if conditions:
        statement = statement.where(and_(*conditions))

    return statement


class ActivityService:
    """Facade exposing activity logging helpers."""

    def __init__(self, *, default_limit: int = DEFAULT_ACTIVITY_LIMIT) -> None:
        self.default_limit = max(1, min(default_limit, MAX_ACTIVITY_LIMIT))

    async def log_event(
        self,
        *,
        db: AsyncSession,
        user_id: UUID,
        action_type: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[UUID] = None,
        description: Optional[str] = None,
        metadata: Optional[dict[str, Any] | Any] = None,
        ip_address: Optional[str] = None,
    ) -> ActivityLog:
        """
        Persist a new activity log entry.

        Args:
            db: Async SQLAlchemy session.
            user_id: Identifier of the acting user.
            action_type: Short descriptor for the action.
            resource_type: Optional domain resource touched by the action.
            resource_id: Optional identifier of the resource.
            description: Free-form human-readable description.
            metadata: Optional structured payload with extra context.
            ip_address: Optional IP address associated with the event.

        Returns:
            ActivityLog: Newly persisted log entry.
        """
        entry = ActivityLog(
            id=uuid4(),
            user_id=user_id,
            action_type=action_type,
            resource_type=resource_type,
            resource_id=resource_id,
            action_description=description,
            metadata_payload=_coerce_metadata(metadata),
            ip_address=ip_address,
        )

        db.add(entry)

        commit_result = db.commit()
        if inspect.isawaitable(commit_result):
            await commit_result

        refresh_result = db.refresh(entry)
        if inspect.isawaitable(refresh_result):
            await refresh_result

        return entry

    async def list_recent(
        self,
        *,
        db: AsyncSession,
        limit: Optional[int] = None,
        offset: int = 0,
        user_id: Optional[UUID] = None,
        action_type: Optional[str] = None,
        resource_type: Optional[str] = None,
        since: Optional[datetime] = None,
    ) -> list[ActivityLog]:
        """
        Retrieve recent activity sorted by most recent first.

        Args:
            db: Async SQLAlchemy session.
            limit: Optional max number of rows to return.
            offset: Number of rows to skip.
            user_id: Filter to a specific user identifier.
            action_type: Filter by action type.
            resource_type: Filter by domain resource type.
            since: Filter to events occurring on/after the supplied timestamp.

        Returns:
            List of ActivityLog instances matching the criteria.
        """
        effective_limit = limit or self.default_limit
        effective_limit = max(1, min(effective_limit, MAX_ACTIVITY_LIMIT))
        offset = max(0, offset)

        statement = select(ActivityLog).order_by(ActivityLog.created_at.desc())
        statement = _apply_activity_filters(
            statement,
            user_id=user_id,
            action_type=action_type,
            resource_type=resource_type,
            since=since,
        ).offset(offset).limit(effective_limit)

        execute_result = db.execute(statement)
        if inspect.isawaitable(execute_result):
            result = await execute_result
        else:
            result = execute_result
        return result.scalars().all()


# Provide a shared singleton instance for convenience
activity_service = ActivityService()


async def log_event(**kwargs: Any) -> ActivityLog:
    """Convenience wrapper delegating to the ActivityService singleton."""
    return await activity_service.log_event(**kwargs)


async def list_recent(**kwargs: Any) -> list[ActivityLog]:
    """Convenience wrapper delegating to the ActivityService singleton."""
    return await activity_service.list_recent(**kwargs)
