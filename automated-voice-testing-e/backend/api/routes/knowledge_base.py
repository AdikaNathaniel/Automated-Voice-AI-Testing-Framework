"""
Knowledge base API endpoints (TASK-355).

Provides CRUD and search capabilities for knowledge base articles, delegating
business logic to the `knowledge_base_service`. Authentication is required for
all interactions to ensure only authorised users can manage documentation.

Phase 3 additions:
- Generate KB articles from Pattern Groups using LLM
- Filter articles by pattern group and source type
- Support for pattern-linked article navigation
- LLM-powered content generation via KB_GENERATION_LLM_PROVIDER
"""

from __future__ import annotations

import logging
from typing import Annotated, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.config import get_settings
from api.dependencies import get_current_user_with_db
from api.schemas.auth import UserResponse
from api.schemas.knowledge_base import (
    KnowledgeBaseCreateRequest,
    KnowledgeBaseListResponse,
    KnowledgeBasePagination,
    KnowledgeBaseResponse,
    KnowledgeBaseUpdateRequest,
)
from services import knowledge_base_service
from services.kb_generation_service import KBGenerationService
from services.llm_providers import get_adapter
from api.auth.roles import Role

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/knowledge-base", tags=["Knowledge Base"])

_KB_MUTATION_ROLES = {Role.ORG_ADMIN.value, Role.ORG_ADMIN.value, Role.QA_LEAD.value}


def _get_effective_tenant_id(user: UserResponse) -> UUID:
    """
    Get effective tenant_id for a user.

    Uses user.tenant_id if set (user belongs to an organization),
    otherwise uses user.id (user is their own tenant).

    This ensures tenant_id is NEVER None for data isolation.
    """
    return user.tenant_id if user.tenant_id else user.id


def _ensure_can_mutate_kb(user: UserResponse) -> None:
    """
    Verify user has permission to mutate knowledge base articles.

    Args:
        user: Current authenticated user

    Raises:
        HTTPException: 403 if user lacks required role
    """
    if user.role not in _KB_MUTATION_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or QA lead role required to modify knowledge base articles.",
        )


def _serialise_article(article) -> KnowledgeBaseResponse:
    """Convert ORM article instance into API response schema."""
    return KnowledgeBaseResponse.model_validate(article.to_dict())


@router.get(
    "/",
    response_model=KnowledgeBaseListResponse,
    summary="List knowledge base articles",
    description="Retrieve knowledge base articles with optional filters, pagination, and full-text search.",
)
async def list_knowledge_base_articles(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
    category: Optional[str] = Query(default=None, description="Filter by category name"),
    is_published: Optional[bool] = Query(
        default=None,
        description="Filter to published/unpublished articles",
    ),
    author_id: Optional[UUID] = Query(default=None, description="Filter articles authored by a specific user"),
    source_type: Optional[str] = Query(
        default=None,
        description="Filter by source type: manual, auto_generated, pattern_derived",
    ),
    pattern_group_id: Optional[UUID] = Query(
        default=None,
        description="Filter articles linked to a specific pattern group",
    ),
    tags: Optional[List[str]] = Query(
        default=None,
        description="Filter articles containing any of these tags",
    ),
    search_query: Optional[str] = Query(default=None, alias="q", description="Full-text search query"),
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of records to return"),
) -> KnowledgeBaseListResponse:
    """List articles with optional filtering and pagination support."""
    tenant_id = _get_effective_tenant_id(current_user)

    filters: Dict[str, object] = {}
    if category:
        filters["category"] = category
    if is_published is not None:
        filters["is_published"] = is_published
    if author_id:
        filters["author_id"] = author_id
    if source_type:
        filters["source_type"] = source_type
    if pattern_group_id:
        filters["pattern_group_id"] = pattern_group_id
    if tags:
        filters["tags"] = tags

    pagination = {"skip": skip, "limit": limit}

    if search_query:
        articles, metadata = await knowledge_base_service.search_articles(
            db,
            tenant_id=tenant_id,
            search_query=search_query,
            filters=filters,
            pagination=pagination,
        )
    else:
        articles, metadata = await knowledge_base_service.list_articles(
            db,
            tenant_id=tenant_id,
            filters=filters,
            pagination=pagination,
        )

    pagination_metadata = KnowledgeBasePagination.model_validate(metadata)

    return KnowledgeBaseListResponse(
        items=[_serialise_article(article) for article in articles],
        pagination=pagination_metadata,
    )


@router.get(
    "/{article_id}",
    response_model=KnowledgeBaseResponse,
    summary="Retrieve a knowledge base article",
    description="Fetch a single knowledge base article by its identifier.",
)
async def get_knowledge_base_article(
    article_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> dict:
    """Retrieve a specific knowledge base article."""
    tenant_id = _get_effective_tenant_id(current_user)

    article = await knowledge_base_service.get_article(db, tenant_id, article_id)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base article not found",
        )
    return _serialise_article(article)


@router.post(
    "/",
    response_model=KnowledgeBaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a knowledge base article",
    description="Create a new knowledge base article authored by the current user.",
)
async def create_knowledge_base_article(
    payload: KnowledgeBaseCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> KnowledgeBaseResponse:
    """Create a new knowledge base article."""
    _ensure_can_mutate_kb(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    article = await knowledge_base_service.create_article(
        db,
        tenant_id=tenant_id,
        data=payload,
        author_id=current_user.id,
    )
    return _serialise_article(article)


@router.patch(
    "/{article_id}",
    response_model=KnowledgeBaseResponse,
    summary="Update a knowledge base article",
    description="Apply partial updates to an existing knowledge base article.",
)
async def update_knowledge_base_article(
    article_id: UUID,
    payload: KnowledgeBaseUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> KnowledgeBaseResponse:
    """Update an existing knowledge base article."""
    _ensure_can_mutate_kb(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    article = await knowledge_base_service.update_article(
        db,
        tenant_id,
        article_id,
        data=payload,
    )
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base article not found",
        )
    return _serialise_article(article)


@router.delete(
    "/{article_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a knowledge base article",
    description="Remove a knowledge base article permanently.",
)
async def delete_knowledge_base_article(
    article_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> Response:
    """Delete a knowledge base article."""
    _ensure_can_mutate_kb(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    deleted = await knowledge_base_service.delete_article(db, tenant_id, article_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base article not found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# -----------------------------------------------------------------------------
# Phase 3: Pattern Group Integration Endpoints
# -----------------------------------------------------------------------------


@router.post(
    "/generate-from-pattern/{pattern_group_id}",
    response_model=KnowledgeBaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate KB article from pattern group",
    description=(
        "Auto-generate a knowledge base article from a pattern group. "
        "Uses LLM to create structured content documenting the pattern, "
        "its edge cases, and recommended actions."
    ),
)
async def generate_article_from_pattern(
    pattern_group_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
    auto_publish: bool = Query(
        default=False,
        description="Whether to publish the article immediately",
    ),
) -> KnowledgeBaseResponse:
    """
    Generate a KB article from a pattern group.

    Creates a comprehensive article documenting the pattern, including:
    - Pattern overview and description
    - Impact assessment and severity
    - Example edge cases
    - Root cause analysis
    - Recommended actions and prevention strategies

    The article is linked to the pattern group for bidirectional navigation.

    Uses the LLM provider configured via KB_GENERATION_LLM_PROVIDER env var.
    Falls back to template-based generation if no provider is configured.
    """
    _ensure_can_mutate_kb(current_user)

    try:
        # Get LLM adapter if configured
        settings = get_settings()
        llm_adapter = None
        provider = settings.KB_GENERATION_LLM_PROVIDER
        model = settings.KB_GENERATION_LLM_MODEL

        if provider:
            try:
                adapter_kwargs = {}
                if model:
                    adapter_kwargs["model"] = model
                llm_adapter = get_adapter(provider, **adapter_kwargs)
                model_name = model or llm_adapter.model
                logger.info(f"Using {provider}/{model_name} for KB generation")
            except Exception as e:
                logger.warning(
                    f"Failed to initialize {provider} adapter: {e}. "
                    "Falling back to template-based generation."
                )

        kb_service = KBGenerationService(llm_adapter=llm_adapter)
        article = await kb_service.generate_from_pattern_group(
            db=db,
            pattern_group_id=pattern_group_id,
            author_id=current_user.id,
            tenant_id=current_user.id,  # User ID acts as tenant ID
            auto_publish=auto_publish,
        )

        generation_method = "LLM" if llm_adapter else "template"
        logger.info(
            f"Generated KB article '{article.title}' from pattern {pattern_group_id} "
            f"using {generation_method} by user {current_user.id}"
        )
        return _serialise_article(article)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to generate KB article from pattern: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate knowledge base article",
        )


@router.get(
    "/by-pattern/{pattern_group_id}",
    response_model=KnowledgeBaseListResponse,
    summary="Get articles by pattern group",
    description="Retrieve all knowledge base articles linked to a specific pattern group.",
)
async def get_articles_by_pattern(
    pattern_group_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum records to return"),
) -> KnowledgeBaseListResponse:
    """Get all articles linked to a pattern group."""
    tenant_id = _get_effective_tenant_id(current_user)

    filters = {"pattern_group_id": pattern_group_id}
    pagination = {"skip": skip, "limit": limit}

    articles, metadata = await knowledge_base_service.list_articles(
        db,
        tenant_id=tenant_id,
        filters=filters,
        pagination=pagination,
    )

    pagination_metadata = KnowledgeBasePagination.model_validate(metadata)

    return KnowledgeBaseListResponse(
        items=[_serialise_article(article) for article in articles],
        pagination=pagination_metadata,
    )
