"""
Organization management API endpoints.

Provides endpoints for managing organizations and their members.
Only super_admin users can create organizations.
Organization admins can manage members within their organization.

Multi-tenancy model:
- Users with is_organization_owner=True represent organizations
- Their user.id becomes the tenant_id for all organization members
- Regular users can be assigned to an org by setting their tenant_id
"""

from __future__ import annotations

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.dependencies import get_current_user_with_db
from api.schemas.auth import UserResponse
from api.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationMemberAdd,
    OrganizationMemberResponse,
    OrganizationListResponse,
    OrganizationMemberListResponse,
)
from api.auth.roles import Role
from services.organization_service import OrganizationService


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/organizations", tags=["Organizations"])

# Roles that can create organizations
_SUPER_ADMIN_ROLES = {Role.SUPER_ADMIN.value}

# Roles that can manage org members (within their own org)
_ORG_ADMIN_ROLES = {Role.SUPER_ADMIN.value, Role.ORG_ADMIN.value}


def _ensure_super_admin(user: UserResponse) -> None:
    """Verify user is a super admin."""
    if user.role not in _SUPER_ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin role required for this operation.",
        )


def _ensure_org_admin(user: UserResponse) -> None:
    """Verify user can manage organization members."""
    if user.role not in _ORG_ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization admin role required for this operation.",
        )


def _get_user_org_id(user: UserResponse) -> UUID:
    """Get the organization ID the user belongs to or owns."""
    return user.tenant_id if user.tenant_id else user.id


@router.post(
    "/",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new organization",
    description="Create a new organization. Only super_admin users can perform this action.",
)
async def create_organization(
    data: OrganizationCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> OrganizationResponse:
    """Create a new organization."""
    _ensure_super_admin(current_user)

    service = OrganizationService(db)

    # Check if org already exists
    existing = await service.get_organization_by_name(data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Organization '{data.name}' already exists.",
        )

    try:
        org = await service.create_organization(
            name=data.name,
            admin_email=data.admin_email,
            admin_username=data.admin_username,
            admin_password=data.admin_password,
            admin_full_name=data.admin_full_name,
            settings=data.settings,
        )
        await db.commit()

        member_count = await service.get_member_count(org.id)
        logger.info(f"Created organization '{data.name}' (ID: {org.id})")

        return OrganizationResponse.from_user(org, member_count)

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create organization: {str(e)}",
        )


@router.get(
    "/",
    response_model=OrganizationListResponse,
    summary="List all organizations",
    description="List all organizations. Only super_admin users can see all organizations.",
)
async def list_organizations(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> OrganizationListResponse:
    """List organizations."""
    _ensure_super_admin(current_user)

    service = OrganizationService(db)
    skip = (page - 1) * page_size

    orgs, total = await service.list_organizations(skip=skip, limit=page_size)

    items = []
    for org in orgs:
        member_count = await service.get_member_count(org.id)
        items.append(OrganizationResponse.from_user(org, member_count))

    return OrganizationListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{org_id}",
    response_model=OrganizationResponse,
    summary="Get organization details",
    description="Get details of a specific organization.",
)
async def get_organization(
    org_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> OrganizationResponse:
    """Get organization by ID."""
    # Super admins can view any org, others can only view their own
    user_org_id = _get_user_org_id(current_user)
    if current_user.role not in _SUPER_ADMIN_ROLES and org_id != user_org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own organization.",
        )

    service = OrganizationService(db)
    org = await service.get_organization(org_id)

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization {org_id} not found.",
        )

    member_count = await service.get_member_count(org_id)
    return OrganizationResponse.from_user(org, member_count)


@router.put(
    "/{org_id}",
    response_model=OrganizationResponse,
    summary="Update organization",
    description="Update organization details.",
)
async def update_organization(
    org_id: UUID,
    data: OrganizationUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> OrganizationResponse:
    """Update organization."""
    # Super admins can update any org, org_admins can only update their own
    user_org_id = _get_user_org_id(current_user)
    if current_user.role not in _SUPER_ADMIN_ROLES and org_id != user_org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own organization.",
        )

    _ensure_org_admin(current_user)

    service = OrganizationService(db)

    org = await service.update_organization(
        org_id=org_id,
        name=data.name,
        settings=data.settings,
        is_active=data.is_active,
    )

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization {org_id} not found.",
        )

    await db.commit()

    member_count = await service.get_member_count(org_id)
    return OrganizationResponse.from_user(org, member_count)


@router.delete(
    "/{org_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete organization",
    description="Delete an organization. Only super_admin can perform this.",
)
async def delete_organization(
    org_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> Response:
    """Delete organization."""
    _ensure_super_admin(current_user)

    service = OrganizationService(db)
    deleted = await service.delete_organization(org_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization {org_id} not found.",
        )

    await db.commit()
    logger.info(f"Deleted organization {org_id}")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# =============================================================================
# Member Management
# =============================================================================


@router.get(
    "/{org_id}/members",
    response_model=OrganizationMemberListResponse,
    summary="List organization members",
    description="List all members of an organization.",
)
async def list_organization_members(
    org_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> OrganizationMemberListResponse:
    """List organization members."""
    # Super admins can view any org's members, others can only view their own
    user_org_id = _get_user_org_id(current_user)
    if current_user.role not in _SUPER_ADMIN_ROLES and org_id != user_org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view members of your own organization.",
        )

    service = OrganizationService(db)

    # Get org to check it exists and get name
    org = await service.get_organization(org_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization {org_id} not found.",
        )

    skip = (page - 1) * page_size
    members, total = await service.list_members(org_id, skip=skip, limit=page_size)

    items = [OrganizationMemberResponse.from_user(m) for m in members]

    return OrganizationMemberListResponse(
        items=items,
        total=total,
        organization_id=org_id,
        organization_name=org.organization_name or org.username,
    )


@router.post(
    "/{org_id}/members",
    response_model=OrganizationMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add member to organization",
    description="Add a user to an organization.",
)
async def add_organization_member(
    org_id: UUID,
    data: OrganizationMemberAdd,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> OrganizationMemberResponse:
    """Add member to organization."""
    # Super admins can add to any org, org_admins can only add to their own
    user_org_id = _get_user_org_id(current_user)
    if current_user.role not in _SUPER_ADMIN_ROLES and org_id != user_org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only add members to your own organization.",
        )

    _ensure_org_admin(current_user)

    service = OrganizationService(db)

    member = await service.add_member(
        org_id=org_id,
        user_id=data.user_id,
        role=data.role.value if data.role else "viewer",
    )

    if not member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to add member. User or organization not found, or user is already an org owner.",
        )

    await db.commit()
    logger.info(f"Added user {data.user_id} to organization {org_id}")

    return OrganizationMemberResponse.from_user(member)


@router.delete(
    "/{org_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove member from organization",
    description="Remove a user from an organization.",
)
async def remove_organization_member(
    org_id: UUID,
    user_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> Response:
    """Remove member from organization."""
    # Super admins can remove from any org, org_admins can only remove from their own
    user_org_id = _get_user_org_id(current_user)
    if current_user.role not in _SUPER_ADMIN_ROLES and org_id != user_org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only remove members from your own organization.",
        )

    _ensure_org_admin(current_user)

    # Prevent removing yourself
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot remove yourself from the organization.",
        )

    service = OrganizationService(db)
    removed = await service.remove_member(org_id, user_id)

    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found in this organization.",
        )

    await db.commit()
    logger.info(f"Removed user {user_id} from organization {org_id}")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
