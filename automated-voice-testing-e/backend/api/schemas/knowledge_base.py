"""
Pydantic schemas for knowledge base API (TASK-355).

Defines request/response models used by the knowledge base routes, ensuring
consistent payload validation and documentation coverage across CRUD
operations and list responses.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class KnowledgeBaseBase(BaseModel):
    """Common fields shared by create and update schema variants."""

    title: Optional[str] = Field(
        default=None,
        description="Human-readable article title",
        max_length=255,
    )
    category: Optional[str] = Field(
        default=None,
        description="Optional article category (e.g. troubleshooting, best_practices)",
        max_length=100,
    )
    content: Optional[str] = Field(
        default=None,
        description="Rich text or markdown body for the knowledge base article",
    )
    content_format: Optional[str] = Field(
        default="markdown",
        description="Content format identifier (e.g. markdown, html)",
        max_length=50,
    )
    is_published: Optional[bool] = Field(
        default=None,
        description="Whether the article is visible to readers",
    )
    tags: Optional[List[str]] = Field(
        default=None,
        description="List of tags for multi-label categorization",
    )


class KnowledgeBaseCreateRequest(KnowledgeBaseBase):
    """Payload required to create a new knowledge base article."""

    title: str = Field(..., max_length=255, description="Article title")
    content: str = Field(..., description="Primary article content")
    content_format: str = Field(default="markdown", description="Format of the content body")
    is_published: bool = Field(default=False, description="Whether the article is published upon creation")
    pattern_group_id: Optional[UUID] = Field(
        default=None,
        description="Link to pattern group if generated from pattern analysis"
    )
    source_type: str = Field(
        default="manual",
        description="Article source: manual, auto_generated, pattern_derived"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="List of tags for multi-label categorization"
    )


class KnowledgeBaseUpdateRequest(KnowledgeBaseBase):
    """Payload for partial updates to an existing article."""

    pass


class KnowledgeBaseResponse(BaseModel):
    """Response model representing a knowledge base article."""

    id: UUID
    title: str
    category: Optional[str]
    content: str
    content_format: str
    author_id: UUID
    is_published: bool
    views: int
    created_at: datetime
    updated_at: datetime
    # Phase 3: Pattern group integration fields
    pattern_group_id: Optional[UUID] = Field(
        default=None,
        description="Link to pattern group if auto-generated from pattern analysis",
    )
    source_type: str = Field(
        default="manual",
        description="Article source: manual, auto_generated, pattern_derived",
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Tags for multi-label categorization",
    )


class KnowledgeBasePagination(BaseModel):
    """Pagination metadata returned alongside list responses."""

    total: int
    skip: int
    limit: int
    search_query: Optional[str] = None


class KnowledgeBaseListResponse(BaseModel):
    """Wrapper structure for paginated knowledge base results."""

    items: List[KnowledgeBaseResponse]
    pagination: KnowledgeBasePagination

    def model_dump(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Override model_dump to ensure consistent return type (dict).

        FastAPI uses this when serialising the response; the default behaviour
        is sufficient but the override keeps mypy happy when routes return dict.
        """
        return super().model_dump(*args, **kwargs)
