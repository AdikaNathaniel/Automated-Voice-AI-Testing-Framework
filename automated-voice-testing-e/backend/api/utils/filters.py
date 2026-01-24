"""
Filtering utilities for database queries

This module provides filtering helpers for SQLAlchemy queries including:
- apply_filters: Function to apply multiple filters to a Select query

The apply_filters function supports filtering by:
- suite_id: Filter by test suite UUID
- category: Filter by category string
- validation_mode: Filter by validation mode string
- tags: Filter by tags array (checks if any tag matches)
- search: Full-text search across name, description, tags
- is_active: Filter by active status boolean

Example:
    >>> from api.utils.filters import apply_filters
    >>> from sqlalchemy import select
    >>> from models.scenario_script import ScenarioScript
    >>>
    >>> # Create base query
    >>> query = select(ScenarioScript)
    >>>
    >>> # Apply filters
    >>> filters = {
    ...     "category": "API",
    ...     "is_active": True,
    ...     "search": "authentication"
    ... }
    >>> filtered_query = apply_filters(query, filters)
"""

from typing import Dict, Any
from uuid import UUID
from sqlalchemy.sql import Select
from sqlalchemy import or_

from models.scenario_script import ScenarioScript


def apply_filters(
    query: Select,
    filters: Dict[str, Any]
) -> Select:
    """
    Apply filters to a SQLAlchemy Select query.

    Takes a SQLAlchemy Select query and a dictionary of filters,
    applies each filter to the query, and returns the modified query.

    Supports the following filters:
    - category: Category string (exact match)
    - validation_mode: Validation mode string (exact match)
    - tags: List of tags to search for (matches if any tag is present)
    - search: Text search across name, description, and tags (case-insensitive)
    - is_active: Boolean for active status (exact match)

    Args:
        query: SQLAlchemy Select query to filter
        filters: Dictionary of filter key-value pairs

    Returns:
        Select: Modified query with filters applied

    Example:
        >>> from sqlalchemy import select
        >>> from models.scenario_script import ScenarioScript
        >>>
        >>> # Create base query
        >>> query = select(ScenarioScript)
        >>>
        >>> # Apply category filter
        >>> filters = {"category": "API"}
        >>> filtered_query = apply_filters(query, filters)
        >>>
        >>> # Apply search filter
        >>> filters = {"search": "authentication"}
        >>> filtered_query = apply_filters(query, filters)
        >>>
        >>> # Apply multiple filters
        >>> filters = {
        ...     "category": "API",
        ...     "is_active": True,
        ...     "search": "login"
        ... }
        >>> filtered_query = apply_filters(query, filters)

    Note:
        - All filters are optional - empty filters dict returns original query
        - Filters are combined with AND logic (all must match)
        - Search uses case-insensitive matching (ILIKE)
        - Tags filter checks if ScenarioScript.tags contains any of the specified tags
        - None or empty filter values are safely ignored
    """
    # Return original query if no filters provided
    if not filters:
        return query

    # Apply category filter
    if "category" in filters and filters["category"]:
        query = query.where(ScenarioScript.category == filters["category"])

    # Apply validation_mode filter
    if "validation_mode" in filters and filters["validation_mode"]:
        query = query.where(ScenarioScript.validation_mode == filters["validation_mode"])

    # Apply is_active filter
    if "is_active" in filters and filters["is_active"] is not None:
        query = query.where(ScenarioScript.is_active == filters["is_active"])

    # Apply tags filter (check if any tag matches)
    if "tags" in filters and filters["tags"]:
        tags = filters["tags"]
        if isinstance(tags, str):
            # Single tag as string
            query = query.where(ScenarioScript.tags.contains([tags]))
        elif isinstance(tags, list) and len(tags) > 0:
            # Multiple tags - match if any tag is present
            # Use OR to match any of the tags
            tag_conditions = [ScenarioScript.tags.contains([tag]) for tag in tags]
            if tag_conditions:
                query = query.where(or_(*tag_conditions))

    # Apply search filter (full-text search)
    if "search" in filters and filters["search"]:
        search_term = f"%{filters['search']}%"
        query = query.where(
            or_(
                ScenarioScript.name.ilike(search_term),
                ScenarioScript.description.ilike(search_term),
                # For tags array, convert to string and search
                ScenarioScript.tags.cast(str).ilike(search_term)
            )
        )

    return query
