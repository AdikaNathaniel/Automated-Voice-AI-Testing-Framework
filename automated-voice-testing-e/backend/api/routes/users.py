"""
User Management API endpoints for Super Admin.

Provides endpoints for managing users across all organizations.
Only super_admin users can access these endpoints.

Endpoints:
    GET /api/v1/users - List all users with filtering/pagination
    GET /api/v1/users/stats - Get user statistics
    POST /api/v1/users - Create a new user
    GET /api/v1/users/{user_id} - Get user details
    PUT /api/v1/users/{user_id} - Update user
    DELETE /api/v1/users/{user_id} - Delete user
    POST /api/v1/users/{user_id}/reset-password - Reset user password
    POST /api/v1/users/{user_id}/deactivate - Deactivate user
    POST /api/v1/users/{user_id}/activate - Activate user
"""

from __future__ import annotations

import logging
from typing import Annotated, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from api.database import get_db
from api.dependencies import get_current_user_with_db
from api.schemas.auth import UserResponse
from api.schemas.user import (
    UserCreate,
    UserUpdate,
    UserPasswordReset,
    UserDetailResponse,
    UserListResponse,
    UserStats,
)
from api.auth.roles import Role
from api.auth.password import hash_password
from models.audit_trail import log_audit_trail
from models.user import User


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["User Management"])

_SUPER_ADMIN_ROLES = {Role.SUPER_ADMIN.value}


def _ensure_super_admin(user: UserResponse) -> None:
    """Verify user is a super admin."""
    if user.role not in _SUPER_ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin role required for user management.",
        )


# =============================================================================
# List and Statistics Endpoints
# =============================================================================


@router.get(
    "/stats",
    response_model=UserStats,
    summary="Get user statistics",
    description="Get statistics about users across the platform.",
)
async def get_user_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> UserStats:
    """Get user statistics for admin dashboard."""
    _ensure_super_admin(current_user)

    # Total users (including organization owners since they can log in)
    total_result = await db.execute(
        select(func.count(User.id))
    )
    total_users = total_result.scalar() or 0

    # Active users
    active_result = await db.execute(
        select(func.count(User.id)).where(
            User.is_active == True,  # noqa: E712
        )
    )
    active_users = active_result.scalar() or 0

    # Inactive users
    inactive_users = total_users - active_users

    # Users by role
    role_result = await db.execute(
        select(User.role, func.count(User.id))
        .group_by(User.role)
    )
    users_by_role = {row[0] or "none": row[1] for row in role_result.all()}

    # Users in organizations (has tenant_id)
    org_users_result = await db.execute(
        select(func.count(User.id)).where(
            User.tenant_id.isnot(None),
        )
    )
    users_by_organization = org_users_result.scalar() or 0

    # Individual users (not in organizations)
    individual_users = total_users - users_by_organization

    return UserStats(
        total_users=total_users,
        active_users=active_users,
        inactive_users=inactive_users,
        users_by_role=users_by_role,
        users_by_organization=users_by_organization,
        individual_users=individual_users,
    )


@router.get(
    "/",
    response_model=UserListResponse,
    summary="List all users",
    description="List all users with filtering and pagination. Super admin only.",
)
async def list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by email/username/name"),
    role: Optional[str] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    organization_id: Optional[UUID] = Query(
        None, description="Filter by organization"
    ),
    include_org_owners: bool = Query(
        False, description="Include organization owner records"
    ),
) -> UserListResponse:
    """List all users with filtering and pagination."""
    _ensure_super_admin(current_user)

    # Build base query
    query = select(User)
    count_query = select(func.count())

    # Exclude org owners by default
    if not include_org_owners:
        query = query.where(User.is_organization_owner == False)  # noqa: E712
        count_query = count_query.where(
            User.is_organization_owner == False  # noqa: E712
        )

    # Apply filters
    if search:
        search_filter = f"%{search}%"
        query = query.where(
            (User.email.ilike(search_filter))
            | (User.username.ilike(search_filter))
            | (User.full_name.ilike(search_filter))
        )
        count_query = count_query.where(
            (User.email.ilike(search_filter))
            | (User.username.ilike(search_filter))
            | (User.full_name.ilike(search_filter))
        )

    if role:
        query = query.where(User.role == role)
        count_query = count_query.where(User.role == role)

    if is_active is not None:
        query = query.where(User.is_active == is_active)
        count_query = count_query.where(User.is_active == is_active)

    if organization_id:
        query = query.where(User.tenant_id == organization_id)
        count_query = count_query.where(User.tenant_id == organization_id)

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination and ordering
    skip = (page - 1) * page_size
    query = query.order_by(User.created_at.desc()).offset(skip).limit(page_size)

    # Execute query
    result = await db.execute(query)
    users = list(result.scalars().all())

    items = [UserDetailResponse.model_validate(u) for u in users]

    return UserListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


# =============================================================================
# CRUD Endpoints
# =============================================================================


@router.post(
    "/",
    response_model=UserDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Create a new user. Super admin only.",
)
async def create_user(
    data: UserCreate,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> UserDetailResponse:
    """Create a new user."""
    _ensure_super_admin(current_user)

    # Validate organization exists if tenant_id provided
    if data.tenant_id:
        org_result = await db.execute(
            select(User).where(
                User.id == data.tenant_id,
                User.is_organization_owner == True,  # noqa: E712
            )
        )
        org = org_result.scalar_one_or_none()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Organization {data.tenant_id} not found.",
            )

    # Hash password
    hashed_password = hash_password(data.password)

    # Create user
    user = User(
        id=uuid4(),
        email=data.email,
        username=data.username,
        password_hash=hashed_password,
        full_name=data.full_name,
        role=data.role.value if isinstance(data.role, Role) else data.role,
        is_active=data.is_active,
        tenant_id=data.tenant_id,
        language_proficiencies=data.language_proficiencies,
        is_organization_owner=False,
    )

    try:
        db.add(user)
        await db.commit()
        await db.refresh(user)

        # Log user creation
        await log_audit_trail(
            db=db,
            action_type="create",
            resource_type="user",
            resource_id=str(user.id),
            tenant_id=user.effective_tenant_id,
            user_id=current_user.id,
            new_values={
                "email": user.email,
                "username": user.username,
                "role": user.role,
                "is_active": user.is_active,
                "tenant_id": str(user.tenant_id) if user.tenant_id else None,
            },
            changes_summary=f"User {user.email} created by super admin {current_user.email}",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=True,
        )

        logger.info(f"Super admin created user {user.email} (ID: {user.id})")
        return UserDetailResponse.model_validate(user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username already exists.",
        )


@router.get(
    "/{user_id}",
    response_model=UserDetailResponse,
    summary="Get user details",
    description="Get detailed information about a specific user.",
)
async def get_user(
    user_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> UserDetailResponse:
    """Get user details by ID."""
    _ensure_super_admin(current_user)

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found.",
        )

    return UserDetailResponse.model_validate(user)


@router.put(
    "/{user_id}",
    response_model=UserDetailResponse,
    summary="Update user",
    description="Update user details. Super admin only.",
)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> UserDetailResponse:
    """Update user details."""
    _ensure_super_admin(current_user)

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found.",
        )

    # Prevent modifying super admin's own critical fields
    if user_id == current_user.id:
        if data.role is not None and data.role != Role.SUPER_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change your own role.",
            )
        if data.is_active is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate yourself.",
            )

    # Validate organization if tenant_id is being set
    if data.tenant_id is not None:
        org_result = await db.execute(
            select(User).where(
                User.id == data.tenant_id,
                User.is_organization_owner == True,  # noqa: E712
            )
        )
        org = org_result.scalar_one_or_none()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Organization {data.tenant_id} not found.",
            )

    # Capture old values for audit trail
    old_values = {
        "email": user.email,
        "username": user.username,
        "role": user.role,
        "is_active": user.is_active,
        "tenant_id": str(user.tenant_id) if user.tenant_id else None,
    }

    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == 'role' and value is not None:
            value = value.value if isinstance(value, Role) else value
        setattr(user, key, value)

    try:
        await db.commit()
        await db.refresh(user)

        # Log user update
        await log_audit_trail(
            db=db,
            action_type="update",
            resource_type="user",
            resource_id=str(user_id),
            tenant_id=user.effective_tenant_id,
            user_id=current_user.id,
            old_values=old_values,
            new_values={
                "email": user.email,
                "username": user.username,
                "role": user.role,
                "is_active": user.is_active,
                "tenant_id": str(user.tenant_id) if user.tenant_id else None,
            },
            changes_summary=f"User {user.email} updated by super admin {current_user.email}",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=True,
        )

        logger.info(f"Super admin updated user {user.email} (ID: {user_id})")
        return UserDetailResponse.model_validate(user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username already exists.",
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Permanently delete a user. Super admin only.",
)
async def delete_user(
    user_id: UUID,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> Response:
    """Delete a user permanently."""
    _ensure_super_admin(current_user)

    # Prevent self-deletion
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself.",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found.",
        )

    # Prevent deleting organization owners
    if user.is_organization_owner:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete organization owner. Delete the organization first.",
        )

    # Capture old values for audit trail before deletion
    old_values = {
        "email": user.email,
        "username": user.username,
        "role": user.role,
        "is_active": user.is_active,
        "tenant_id": str(user.tenant_id) if user.tenant_id else None,
    }

    # Log user deletion
    await log_audit_trail(
        db=db,
        action_type="delete",
        resource_type="user",
        resource_id=str(user_id),
        tenant_id=user.effective_tenant_id,
        user_id=current_user.id,
        old_values=old_values,
        changes_summary=f"User {user.email} deleted by super admin {current_user.email}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=True,
    )

    await db.delete(user)
    await db.commit()
    logger.info(f"Super admin deleted user {user.email} (ID: {user_id})")

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# =============================================================================
# Password and Status Management
# =============================================================================


@router.post(
    "/{user_id}/reset-password",
    response_model=dict,
    summary="Reset user password",
    description="Reset a user's password. Super admin only.",
)
async def reset_user_password(
    user_id: UUID,
    data: UserPasswordReset,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> dict:
    """Reset a user's password."""
    _ensure_super_admin(current_user)

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found.",
        )

    # Hash and set new password
    user.password_hash = hash_password(data.new_password)

    await db.commit()

    # Log password reset (CRITICAL security operation)
    await log_audit_trail(
        db=db,
        action_type="password_reset",
        resource_type="user",
        resource_id=str(user_id),
        tenant_id=user.effective_tenant_id,
        user_id=current_user.id,
        new_values={
            "email": user.email,
            "password_reset_by": current_user.email,
        },
        changes_summary=f"Password reset for user {user.email} by super admin {current_user.email}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=True,
    )

    logger.info(f"Super admin reset password for user {user.email} (ID: {user_id})")

    return {"message": "Password reset successfully."}


@router.post(
    "/{user_id}/deactivate",
    response_model=UserDetailResponse,
    summary="Deactivate user",
    description="Deactivate a user account. Super admin only.",
)
async def deactivate_user(
    user_id: UUID,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> UserDetailResponse:
    """Deactivate a user account."""
    _ensure_super_admin(current_user)

    # Prevent self-deactivation
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate yourself.",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already inactive.",
        )

    user.is_active = False
    await db.commit()
    await db.refresh(user)

    # Log user deactivation
    await log_audit_trail(
        db=db,
        action_type="deactivate",
        resource_type="user",
        resource_id=str(user_id),
        tenant_id=user.effective_tenant_id,
        user_id=current_user.id,
        old_values={"is_active": True},
        new_values={"is_active": False, "email": user.email},
        changes_summary=f"User {user.email} deactivated by super admin {current_user.email}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=True,
    )

    logger.info(f"Super admin deactivated user {user.email} (ID: {user_id})")

    return UserDetailResponse.model_validate(user)


@router.post(
    "/{user_id}/activate",
    response_model=UserDetailResponse,
    summary="Activate user",
    description="Activate a user account. Super admin only.",
)
async def activate_user(
    user_id: UUID,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> UserDetailResponse:
    """Activate a user account."""
    _ensure_super_admin(current_user)

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found.",
        )

    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already active.",
        )

    user.is_active = True
    await db.commit()
    await db.refresh(user)

    # Log user activation
    await log_audit_trail(
        db=db,
        action_type="activate",
        resource_type="user",
        resource_id=str(user_id),
        tenant_id=user.effective_tenant_id,
        user_id=current_user.id,
        old_values={"is_active": False},
        new_values={"is_active": True, "email": user.email},
        changes_summary=f"User {user.email} activated by super admin {current_user.email}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=True,
    )

    logger.info(f"Super admin activated user {user.email} (ID: {user_id})")

    return UserDetailResponse.model_validate(user)


# =============================================================================
# Export
# =============================================================================

__all__ = ['router']
