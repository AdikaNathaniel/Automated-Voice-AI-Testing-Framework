"""
Category management API routes.

Provides CRUD operations for managing test scenario categories.
Admin users can create, update, and delete categories.
All authenticated users can list and view categories.
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, or_, and_

from api.database import get_db
from api.schemas.auth import UserResponse
from api.dependencies import get_current_user_with_db
from api.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListResponse,
    CategoryDeleteResponse,
)
from models.category import Category
from models.scenario_script import ScenarioScript

router = APIRouter(prefix="/categories", tags=["Categories"])


def _get_effective_tenant_id(user: UserResponse) -> UUID:
    """
    Get effective tenant_id for a user.

    Uses user.tenant_id if set (user belongs to an organization),
    otherwise uses user.id (user is their own tenant).
    """
    return user.tenant_id if user.tenant_id else user.id


def _ensure_admin(user: UserResponse) -> None:
    """Ensure user has admin role.

    Both ORG_ADMIN and SUPER_ADMIN can manage categories:
    - ORG_ADMIN: Manages their organization's categories (tenant-specific)
    - SUPER_ADMIN: Manages system categories (tenant_id=NULL) available to all
    """
    if user.role not in ("org_admin", "super_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required for this operation.",
        )


async def _get_category_scenario_count(db: AsyncSession, category_name: str, tenant_id: UUID) -> int:
    """Get count of scenarios using this category."""
    result = await db.execute(
        select(func.count(ScenarioScript.id)).where(
            ScenarioScript.script_metadata['category'].astext == category_name,
            ScenarioScript.tenant_id == tenant_id
        )
    )
    count = result.scalar()
    return count or 0


@router.get("", response_model=CategoryListResponse)
async def list_categories(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    include_system: bool = Query(True, description="Include system categories"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> CategoryListResponse:
    """
    List all categories for the current user's tenant.

    Includes both:
    - System categories (tenant_id=None) - available to all tenants
    - Tenant-specific categories (tenant_id=current_tenant_id)

    Args:
        is_active: Optional filter for active/inactive categories
        include_system: Whether to include system-defined categories
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of categories with counts
    """
    tenant_id = _get_effective_tenant_id(current_user)

    # Build query to fetch both system and tenant-specific categories
    if include_system:
        # Include both system categories (tenant_id=None) and tenant-specific categories
        query = select(Category).where(
            or_(Category.tenant_id == tenant_id, Category.tenant_id == None)  # noqa: E711
        )
    else:
        # Only tenant-specific categories (exclude system)
        query = select(Category).where(
            and_(Category.tenant_id == tenant_id, Category.is_system == False)  # noqa: E712
        )

    if is_active is not None:
        query = query.where(Category.is_active == is_active)

    query = query.order_by(Category.name)
    result = await db.execute(query)
    categories = result.scalars().all()

    # Add scenario counts
    category_responses = []
    for cat in categories:
        cat_dict = cat.to_dict()
        cat_dict['scenario_count'] = await _get_category_scenario_count(db, cat.name, tenant_id)
        category_responses.append(CategoryResponse(**cat_dict))

    return CategoryListResponse(
        categories=category_responses,
        total=len(category_responses)
    )


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> CategoryResponse:
    """
    Get a specific category by ID.

    Args:
        category_id: Category UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Category details with scenario count

    Raises:
        404: Category not found
    """
    tenant_id = _get_effective_tenant_id(current_user)

    result = await db.execute(
        select(Category).where(
            Category.id == category_id,
            Category.tenant_id == tenant_id
        )
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {category_id} not found"
        )

    cat_dict = category.to_dict()
    cat_dict['scenario_count'] = await _get_category_scenario_count(db, category.name, tenant_id)

    return CategoryResponse(**cat_dict)


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> CategoryResponse:
    """
    Create a new category.

    Requires admin role.

    Args:
        category_data: Category creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created category

    Raises:
        403: User is not admin
        409: Category with this name already exists
    """
    _ensure_admin(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    # Check if category with this name already exists
    result = await db.execute(
        select(Category).where(
            Category.name == category_data.name,
            Category.tenant_id == tenant_id
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category with name '{category_data.name}' already exists"
        )

    # Create new category
    category = Category(
        name=category_data.name,
        display_name=category_data.display_name or category_data.name,
        description=category_data.description,
        color=category_data.color,
        icon=category_data.icon,
        is_active=category_data.is_active,
        is_system=False,  # User-created categories are never system categories
        tenant_id=tenant_id
    )

    db.add(category)
    await db.commit()
    await db.refresh(category)

    cat_dict = category.to_dict()
    cat_dict['scenario_count'] = 0  # New category has no scenarios

    return CategoryResponse(**cat_dict)


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    category_data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> CategoryResponse:
    """
    Update an existing category.

    Requires admin role.
    System categories cannot be modified.

    Args:
        category_id: Category UUID
        category_data: Category update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated category

    Raises:
        403: User is not admin or trying to modify system category
        404: Category not found
        409: Name already exists
    """
    _ensure_admin(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    result = await db.execute(
        select(Category).where(
            Category.id == category_id,
            Category.tenant_id == tenant_id
        )
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {category_id} not found"
        )

    if category.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System categories cannot be modified"
        )

    # Check for name conflicts if name is being changed
    if category_data.name and category_data.name != category.name:
        result = await db.execute(
            select(Category).where(
                Category.name == category_data.name,
                Category.tenant_id == tenant_id,
                Category.id != category_id
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Category with name '{category_data.name}' already exists"
            )

    # Update fields
    update_data = category_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    await db.commit()
    await db.refresh(category)

    cat_dict = category.to_dict()
    cat_dict['scenario_count'] = await _get_category_scenario_count(db, category.name, tenant_id)

    return CategoryResponse(**cat_dict)


@router.delete("/{category_id}", response_model=CategoryDeleteResponse)
async def delete_category(
    category_id: UUID,
    force: bool = Query(False, description="Force delete even if scenarios exist"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> CategoryDeleteResponse:
    """
    Delete a category.

    Requires admin role.
    System categories cannot be deleted.
    Categories with associated scenarios cannot be deleted unless force=true.

    Args:
        category_id: Category UUID
        force: Force delete even if scenarios use this category
        db: Database session
        current_user: Current authenticated user

    Returns:
        Deletion success message

    Raises:
        403: User is not admin or trying to delete system category
        404: Category not found
        409: Category has associated scenarios and force=false
    """
    _ensure_admin(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    result = await db.execute(
        select(Category).where(
            Category.id == category_id,
            Category.tenant_id == tenant_id
        )
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {category_id} not found"
        )

    if category.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System categories cannot be deleted"
        )

    # Check for associated scenarios
    scenario_count = await _get_category_scenario_count(db, category.name, tenant_id)
    if scenario_count > 0 and not force:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category has {scenario_count} associated scenario(s). Use force=true to delete anyway."
        )

    category_name = category.name
    await db.delete(category)
    await db.commit()

    return CategoryDeleteResponse(
        success=True,
        message=f"Category '{category_name}' deleted successfully"
    )
