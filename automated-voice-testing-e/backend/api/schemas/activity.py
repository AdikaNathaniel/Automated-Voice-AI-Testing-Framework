"""
Pydantic schemas for activity feed API (TASK-363).

Defines serialisable representations of activity log entries and
response wrappers used by the activity feed route.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ActivityLogResponse(BaseModel):
    """Serialised representation of an ActivityLog entry."""

    id: UUID
    user_id: UUID
    action_type: str
    resource_type: Optional[str] = Field(
        default=None,
        description="Domain entity affected by the action (e.g. test_case)",
    )
    resource_id: Optional[UUID] = Field(
        default=None,
        description="Identifier of the affected resource, when applicable",
    )
    action_description: Optional[str] = Field(
        default=None,
        description="Human-readable description of the activity",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Structured metadata payload describing the activity event",
    )
    ip_address: Optional[str] = Field(
        default=None,
        description="IP address associated with the action, if available",
    )
    created_at: datetime


class ActivityFeedPagination(BaseModel):
    """Pagination metadata for activity feed responses."""

    limit: int = Field(description="Maximum number of events requested")
    offset: int = Field(description="Number of events skipped before this page")
    returned: int = Field(description="Number of events included in this response")
    user_id: Optional[UUID] = Field(default=None, description="User filter applied to the query")
    action_type: Optional[str] = Field(default=None, description="Action type filter applied to the query")
    resource_type: Optional[str] = Field(default=None, description="Resource type filter applied to the query")
    since: Optional[datetime] = Field(default=None, description="Lower bound timestamp filter applied to the query")


class ActivityFeedResponse(BaseModel):
    """Wrapper containing activity log entries and pagination metadata."""

    items: List[ActivityLogResponse]
    pagination: ActivityFeedPagination

    def model_dump(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Ensure consistent dict output for FastAPI responses."""
        return super().model_dump(*args, **kwargs)
