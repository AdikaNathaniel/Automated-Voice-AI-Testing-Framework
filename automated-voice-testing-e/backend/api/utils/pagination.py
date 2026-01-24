"""
Pagination utilities for database queries

This module provides pagination helpers for SQLAlchemy queries including:
- PaginationMetadata: Pydantic model for pagination metadata
- paginate: Function to paginate SQLAlchemy Select queries

The paginate function handles offset calculation, result limiting,
and total record counting for easy pagination in API endpoints.

Example:
    >>> from api.utils.pagination import paginate
    >>> from sqlalchemy import select
    >>> from models.scenario_script import ScenarioScript
    >>>
    >>> # Create query
    >>> query = select(ScenarioScript)
    >>>
    >>> # Paginate query
    >>> results, metadata = await paginate(db, query, page=1, limit=10)
    >>> print(f"Page {metadata.page} of {metadata.pages}")
    Page 1 of 5
    >>> print(f"Total records: {metadata.total}")
    Total records: 42
"""

import math
from typing import List, Tuple, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from pydantic import BaseModel, Field


class PaginationMetadata(BaseModel):
    """
    Pagination metadata model.

    Contains information about the current pagination state including
    total records, current page, records per page, and total pages.

    Attributes:
        total (int): Total number of records across all pages
        page (int): Current page number (1-indexed)
        limit (int): Number of records per page
        pages (int): Total number of pages

    Example:
        >>> metadata = PaginationMetadata(
        ...     total=42,
        ...     page=1,
        ...     limit=10,
        ...     pages=5
        ... )
        >>> print(f"Showing page {metadata.page} of {metadata.pages}")
        Showing page 1 of 5
    """

    total: int = Field(..., description="Total number of records across all pages", ge=0)
    page: int = Field(..., description="Current page number (1-indexed)", ge=1)
    limit: int = Field(..., description="Number of records per page", ge=1)
    pages: int = Field(..., description="Total number of pages", ge=0)

    class Config:
        """Pydantic model configuration"""
        json_schema_extra = {
            "example": {
                "total": 42,
                "page": 1,
                "limit": 10,
                "pages": 5
            }
        }


async def paginate(
    db: AsyncSession,
    query: Select,
    page: int = 1,
    limit: int = 50
) -> Tuple[List[Any], PaginationMetadata]:
    """
    Paginate a SQLAlchemy Select query.

    Takes a SQLAlchemy Select query, applies pagination (offset and limit),
    executes the query, and returns both the results and pagination metadata.

    Args:
        db: Async database session
        query: SQLAlchemy Select query to paginate
        page: Page number to retrieve (1-indexed), defaults to 1
        limit: Number of records per page, defaults to 50

    Returns:
        tuple[list[Any], PaginationMetadata]: Tuple containing:
            - List of query results for the requested page
            - PaginationMetadata with pagination information

    Raises:
        ValueError: If page or limit are less than 1

    Example:
        >>> from sqlalchemy import select
        >>> from models.scenario_script import ScenarioScript
        >>>
        >>> # Create query
        >>> query = select(ScenarioScript).where(ScenarioScript.is_active == True)
        >>>
        >>> # Paginate - get page 2 with 20 records per page
        >>> results, metadata = await paginate(db, query, page=2, limit=20)
        >>>
        >>> # Access results
        >>> for scenario in results:
        ...     print(scenario.name)
        >>>
        >>> # Access metadata
        >>> print(f"Page {metadata.page}/{metadata.pages}")
        >>> print(f"Total: {metadata.total}")

    Note:
        - Page numbers are 1-indexed (first page is page=1)
        - If page exceeds total pages, returns empty results
        - Offset is calculated as: (page - 1) * limit
        - Total pages is calculated as: ceil(total / limit)
    """
    # Validate parameters
    if page < 1:
        raise ValueError("Page must be >= 1")
    if limit < 1:
        raise ValueError("Limit must be >= 1")

    # Calculate offset
    offset = (page - 1) * limit

    # Get total count
    # Create a count query from the original query
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # Calculate total pages
    pages = math.ceil(total / limit) if total > 0 else 0

    # Apply pagination to query
    paginated_query = query.offset(offset).limit(limit)

    # Execute paginated query
    result = await db.execute(paginated_query)
    items = result.scalars().all()

    # Create metadata
    metadata = PaginationMetadata(
        total=total,
        page=page,
        limit=limit,
        pages=pages
    )

    return list(items), metadata
