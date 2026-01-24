"""
Knowledge base service providing CRUD and search helpers for articles.

This module wraps SQLAlchemy operations for the `KnowledgeBase` model and
exposes asynchronous helpers used by API routes. Responsibilities include:
- Creating new knowledge base articles
- Retrieving individual articles by identifier
- Listing articles with basic filtering and pagination
- Updating article metadata/content
- Deleting articles
- Performing PostgreSQL full-text search across title and content
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from models.knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)

# Pagination defaults
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


class KnowledgeBaseService:
    """
    Service class for knowledge base article management.

    Provides CRUD operations and full-text search for knowledge base articles.
    This class wraps the module-level functions for a consistent OOP interface.

    All operations require tenant_id for multi-tenant data isolation.

    Attributes:
        default_page_size: Default number of items per page
        max_page_size: Maximum allowed page size

    Example:
        >>> service = KnowledgeBaseService()
        >>> article = await service.get_article(db, tenant_id, article_id)
    """

    def __init__(self):
        """Initialize the knowledge base service."""
        self.default_page_size = DEFAULT_PAGE_SIZE
        self.max_page_size = MAX_PAGE_SIZE

    async def create_article(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        data: Any,
        author_id: UUID
    ) -> KnowledgeBase:
        """
        Create and persist a new knowledge base article.

        Args:
            db: Async SQLAlchemy session
            tenant_id: REQUIRED - Tenant UUID for data isolation
            data: Payload containing article properties
            author_id: UUID of the authoring user

        Returns:
            KnowledgeBase: Newly created article
        """
        return await create_article(db, tenant_id, data, author_id)

    async def get_article(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        article_id: UUID
    ) -> Optional[KnowledgeBase]:
        """Retrieve a knowledge base article by identifier, scoped to tenant."""
        return await get_article(db, tenant_id, article_id)

    async def list_articles(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        filters: Optional[Dict[str, Any]] = None,
        pagination: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[KnowledgeBase], Dict[str, Any]]:
        """
        List knowledge base articles with optional filters and pagination.

        Args:
            db: Async SQLAlchemy session
            tenant_id: REQUIRED - Tenant UUID for data isolation
            filters: Optional filters
            pagination: Optional pagination

        Returns a tuple of articles and pagination metadata.
        """
        return await list_articles(db, tenant_id, filters, pagination)

    async def update_article(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        article_id: UUID,
        data: Any
    ) -> Optional[KnowledgeBase]:
        """
        Update an existing article with partial data payload, scoped to tenant.

        Returns the updated article or None if not found within tenant scope.
        """
        return await update_article(db, tenant_id, article_id, data)

    async def delete_article(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        article_id: UUID
    ) -> bool:
        """
        Delete an article by identifier, scoped to tenant.

        Returns True if removed, False if not found within tenant scope.
        """
        return await delete_article(db, tenant_id, article_id)

    async def search_articles(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        search_query: str,
        *,
        filters: Optional[Dict[str, Any]] = None,
        pagination: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[KnowledgeBase], Dict[str, Any]]:
        """
        Perform full-text search across knowledge base articles, scoped to tenant.

        Uses PostgreSQL full-text search for relevancy ranking.
        """
        return await search_articles(db, tenant_id, search_query, filters=filters, pagination=pagination)


def _extract_payload(data: Any, *, exclude_unset: bool = False) -> Dict[str, Any]:
    """
    Normalise incoming data payloads from Pydantic models or dict-like objects.

    Supports .model_dump(), .dict(), and mapping types so the service can be
    reused by API schemas and internal callers.
    """
    if hasattr(data, "model_dump"):
        return data.model_dump(exclude_unset=exclude_unset)
    if hasattr(data, "dict"):
        return data.dict(exclude_unset=exclude_unset)
    if isinstance(data, dict):
        return dict(data)
    raise TypeError("Unsupported payload type for knowledge base service")


def _apply_filters(statement: Select, filters: Optional[Dict[str, Any]]) -> Select:
    """
    Apply filtering to the base statement.

    Supports:
    - category: exact match
    - is_published: boolean match
    - author_id: exact match
    - source_type: exact match (Phase 3)
    - pattern_group_id: exact match (Phase 3)
    - tags: array overlap (Phase 3)
    """
    if not filters:
        return statement

    if "category" in filters and filters["category"]:
        statement = statement.where(KnowledgeBase.category == filters["category"])

    if "is_published" in filters and filters["is_published"] is not None:
        statement = statement.where(KnowledgeBase.is_published == bool(filters["is_published"]))

    if "author_id" in filters and filters["author_id"]:
        statement = statement.where(KnowledgeBase.author_id == filters["author_id"])

    # Phase 3: Pattern group integration filters
    if "source_type" in filters and filters["source_type"]:
        statement = statement.where(KnowledgeBase.source_type == filters["source_type"])

    if "pattern_group_id" in filters and filters["pattern_group_id"]:
        statement = statement.where(
            KnowledgeBase.pattern_group_id == filters["pattern_group_id"]
        )

    # Tags filter: match if article contains ANY of the specified tags
    if "tags" in filters and filters["tags"]:
        tags_list = filters["tags"]
        if isinstance(tags_list, list) and tags_list:
            # PostgreSQL array overlap operator: &&
            statement = statement.where(KnowledgeBase.tags.overlap(tags_list))

    return statement


def _resolve_pagination(pagination: Optional[Dict[str, Any]]) -> Tuple[int, int]:
    """Determine skip/limit values with sane defaults and bounds."""
    pagination = pagination or {}
    skip = max(int(pagination.get("skip", 0)), 0)
    limit = int(pagination.get("limit", DEFAULT_PAGE_SIZE))
    if limit <= 0:
        limit = DEFAULT_PAGE_SIZE
    limit = min(limit, MAX_PAGE_SIZE)
    return skip, limit


async def create_article(
    db: AsyncSession,
    tenant_id: UUID,
    data: Any,
    author_id: UUID,
) -> KnowledgeBase:
    """
    Create and persist a new knowledge base article.

    Args:
        db: Async SQLAlchemy session
        tenant_id: REQUIRED - Tenant UUID for data isolation
        data: Payload containing article properties
        author_id: UUID of the authoring user

    Returns:
        KnowledgeBase: Newly created article
    """
    try:
        payload = _extract_payload(data)
        payload["tenant_id"] = tenant_id
        payload["author_id"] = author_id

        article = KnowledgeBase(**payload)

        db.add(article)
        await db.commit()
        await db.refresh(article)

        logger.debug(f"Created article: {article.id} for tenant: {tenant_id}")
        return article

    except Exception as e:
        logger.error(f"Error creating article: {e}")
        raise


async def get_article(
    db: AsyncSession,
    tenant_id: UUID,
    article_id: UUID,
) -> Optional[KnowledgeBase]:
    """
    Retrieve a knowledge base article by identifier, scoped to tenant.

    Args:
        db: Async SQLAlchemy session
        tenant_id: REQUIRED - Tenant UUID for data isolation
        article_id: Article UUID

    Returns:
        KnowledgeBase if found within tenant scope, None otherwise
    """
    try:
        statement = select(KnowledgeBase).where(
            KnowledgeBase.id == article_id,
            KnowledgeBase.tenant_id == tenant_id,
        )
        result = await db.execute(statement)
        article = result.scalar_one_or_none()
        if article:
            logger.debug(f"Found article: {article_id}")
        return article

    except Exception as e:
        logger.error(f"Error getting article {article_id}: {e}")
        raise


async def list_articles(
    db: AsyncSession,
    tenant_id: UUID,
    filters: Optional[Dict[str, Any]] = None,
    pagination: Optional[Dict[str, Any]] = None,
) -> Tuple[List[KnowledgeBase], Dict[str, Any]]:
    """
    List knowledge base articles with optional filters and pagination, scoped to tenant.

    Args:
        db: Async SQLAlchemy session
        tenant_id: REQUIRED - Tenant UUID for data isolation
        filters: Optional filters
        pagination: Optional pagination

    Returns a tuple of articles and pagination metadata (total, skip, limit).
    """
    try:
        skip, limit = _resolve_pagination(pagination)

        # ALWAYS filter by tenant_id first for data isolation
        base_statement = (
            select(KnowledgeBase)
            .where(KnowledgeBase.tenant_id == tenant_id)
            .order_by(KnowledgeBase.created_at.desc())
        )
        base_statement = _apply_filters(base_statement, filters)

        count_statement = (
            select(func.count(KnowledgeBase.id))
            .where(KnowledgeBase.tenant_id == tenant_id)
        )
        count_statement = _apply_filters(count_statement, filters)

        total_result = await db.execute(count_statement)
        total = int(total_result.scalar_one() or 0)

        statement = base_statement.offset(skip).limit(limit)
        result = await db.execute(statement)
        articles = result.scalars().all()

        logger.debug(f"Listed {len(articles)} articles (total: {total}) for tenant: {tenant_id}")
        return articles, {
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    except Exception as e:
        logger.error(f"Error listing articles: {e}")
        raise


async def update_article(
    db: AsyncSession,
    tenant_id: UUID,
    article_id: UUID,
    data: Any,
) -> KnowledgeBase | None:
    """
    Update an existing article with partial data payload, scoped to tenant.

    Args:
        db: Async SQLAlchemy session
        tenant_id: REQUIRED - Tenant UUID for data isolation
        article_id: Article UUID
        data: Partial update payload

    Returns the updated article or None if not found within tenant scope.
    """
    try:
        payload = _extract_payload(data, exclude_unset=True)

        article = await get_article(db, tenant_id, article_id)
        if article is None:
            return None

        for field, value in payload.items():
            # Prevent changing tenant_id
            if field == "tenant_id":
                continue
            setattr(article, field, value)

        await db.commit()
        await db.refresh(article)

        logger.debug(f"Updated article: {article_id}")
        return article

    except Exception as e:
        logger.error(f"Error updating article {article_id}: {e}")
        raise


async def delete_article(
    db: AsyncSession,
    tenant_id: UUID,
    article_id: UUID,
) -> bool:
    """
    Delete an article by identifier, scoped to tenant.

    Args:
        db: Async SQLAlchemy session
        tenant_id: REQUIRED - Tenant UUID for data isolation
        article_id: Article UUID

    Returns True if the article was removed, False if it was not found within tenant scope.
    """
    try:
        article = await get_article(db, tenant_id, article_id)
        if article is None:
            return False

        await db.delete(article)
        await db.commit()

        logger.debug(f"Deleted article: {article_id}")
        return True

    except Exception as e:
        logger.error(f"Error deleting article {article_id}: {e}")
        raise


async def search_articles(
    db: AsyncSession,
    tenant_id: UUID,
    search_query: str,
    *,
    filters: Optional[Dict[str, Any]] = None,
    pagination: Optional[Dict[str, Any]] = None,
) -> Tuple[List[KnowledgeBase], Dict[str, Any]]:
    """
    Perform full-text search across knowledge base articles, scoped to tenant.

    Uses PostgreSQL `to_tsvector` and `websearch_to_tsquery` for relevancy ranking.

    Args:
        db: Async SQLAlchemy session
        tenant_id: REQUIRED - Tenant UUID for data isolation
        search_query: Search query string
        filters: Optional filters
        pagination: Optional pagination
    """
    if not search_query:
        return await list_articles(db, tenant_id, filters=filters, pagination=pagination)

    skip, limit = _resolve_pagination(pagination)
    ts_vector = func.to_tsvector(
        "english",
        func.coalesce(KnowledgeBase.title, "") + func.coalesce(KnowledgeBase.content, ""),
    )
    ts_query = func.websearch_to_tsquery("english", search_query)

    # ALWAYS filter by tenant_id first for data isolation
    statement = (
        select(KnowledgeBase, func.ts_rank(ts_vector, ts_query).label("rank"))
        .where(KnowledgeBase.tenant_id == tenant_id)
        .where(ts_vector.op("@@")(ts_query))
        .order_by(func.ts_rank(ts_vector, ts_query).desc(), KnowledgeBase.created_at.desc())
    )
    statement = _apply_filters(statement, filters).offset(skip).limit(limit)

    result = await db.execute(statement)
    rows = result.all()
    articles = [row[0] for row in rows]

    # Count total matches within tenant scope
    count_statement = (
        select(func.count(KnowledgeBase.id))
        .where(KnowledgeBase.tenant_id == tenant_id)
        .where(ts_vector.op("@@")(ts_query))
    )
    count_statement = _apply_filters(count_statement, filters)
    count_result = await db.execute(count_statement)
    total = int(count_result.scalar_one() or 0)

    return articles, {
        "total": total,
        "skip": skip,
        "limit": limit,
        "search_query": search_query,
    }
