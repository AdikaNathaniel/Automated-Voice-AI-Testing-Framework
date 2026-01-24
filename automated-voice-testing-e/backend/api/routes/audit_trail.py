"""
Audit Trail API endpoints for querying and viewing audit logs.

Provides endpoints for administrators to view, filter, and export audit trail logs.
Includes comprehensive filtering, pagination, and tenant isolation.

Endpoints:
    GET /api/v1/audit-trail - Query audit logs with filters
    GET /api/v1/audit-trail/{audit_id} - Get specific audit log entry
    GET /api/v1/audit-trail/export - Export audit logs to CSV/JSON

Access: Super Admin only
"""

from datetime import datetime, timezone
from typing import Annotated, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.dependencies import get_current_user_with_db
from api.schemas.auth import UserResponse
from api.auth.roles import Role
from models.audit_trail import AuditTrail

import csv
import io
import json


router = APIRouter(prefix="/audit-trail", tags=["Audit Trail"])

_SUPER_ADMIN_ROLES = {Role.SUPER_ADMIN.value}


def _ensure_super_admin(user: UserResponse) -> None:
    """Verify user is a super admin."""
    if user.role not in _SUPER_ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin role required for audit trail access.",
        )


# =============================================================================
# Response Models
# =============================================================================


class AuditTrailResponse(BaseModel):
    """Response model for a single audit trail entry."""
    id: str
    tenant_id: Optional[str] = None
    user_id: Optional[str] = None
    action_type: str
    resource_type: str
    resource_id: Optional[str] = None
    old_values: Optional[dict] = None
    new_values: Optional[dict] = None
    changes_summary: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AuditTrailListResponse(BaseModel):
    """Paginated list of audit trail entries."""
    items: List[AuditTrailResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AuditTrailStatsResponse(BaseModel):
    """Statistics about audit trail entries."""
    total_entries: int
    successful_actions: int
    failed_actions: int
    unique_users: int
    unique_tenants: int
    actions_by_type: dict
    resources_by_type: dict


# =============================================================================
# Query Endpoints
# =============================================================================


@router.get(
    "/",
    response_model=AuditTrailListResponse,
    summary="Query audit trail logs",
    description="Retrieve audit trail entries with comprehensive filtering and pagination.",
)
async def query_audit_trail(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page"),
    tenant_id: Optional[UUID] = Query(None, description="Filter by tenant ID"),
    user_id: Optional[UUID] = Query(None, description="Filter by user ID"),
    action_type: Optional[str] = Query(None, description="Filter by action type"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    resource_id: Optional[str] = Query(None, description="Filter by resource ID"),
    success: Optional[bool] = Query(None, description="Filter by success status"),
    start_date: Optional[datetime] = Query(None, description="Start date (ISO 8601)"),
    end_date: Optional[datetime] = Query(None, description="End date (ISO 8601)"),
    search: Optional[str] = Query(None, description="Search in changes_summary"),
) -> AuditTrailListResponse:
    """
    Query audit trail logs with comprehensive filtering.

    Allows super admins to view and filter audit logs for security monitoring,
    compliance reporting, and incident investigation.

    Args:
        db: Database session
        current_user: Current authenticated user (must be super admin)
        page: Page number for pagination
        page_size: Number of items per page
        tenant_id: Filter by specific tenant
        user_id: Filter by specific user
        action_type: Filter by action type (create, update, delete, etc.)
        resource_type: Filter by resource type (user, integration_config, etc.)
        resource_id: Filter by specific resource ID
        success: Filter by success/failure status
        start_date: Filter entries after this date
        end_date: Filter entries before this date
        search: Search text in changes_summary

    Returns:
        Paginated list of audit trail entries

    Raises:
        HTTPException: 403 if user is not super admin
    """
    _ensure_super_admin(current_user)

    # Build base query
    query = select(AuditTrail)
    count_query = select(func.count()).select_from(AuditTrail)

    # Apply filters
    filters = []

    if tenant_id:
        filters.append(AuditTrail.tenant_id == tenant_id)

    if user_id:
        filters.append(AuditTrail.user_id == user_id)

    if action_type:
        filters.append(AuditTrail.action_type == action_type)

    if resource_type:
        filters.append(AuditTrail.resource_type == resource_type)

    if resource_id:
        filters.append(AuditTrail.resource_id == resource_id)

    if success is not None:
        filters.append(AuditTrail.success == success)

    if start_date:
        filters.append(AuditTrail.created_at >= start_date)

    if end_date:
        filters.append(AuditTrail.created_at <= end_date)

    if search:
        search_filter = f"%{search}%"
        filters.append(AuditTrail.changes_summary.ilike(search_filter))

    # Apply all filters
    if filters:
        query = query.where(and_(*filters))
        count_query = count_query.where(and_(*filters))

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination and ordering
    skip = (page - 1) * page_size
    query = query.order_by(AuditTrail.created_at.desc()).offset(skip).limit(page_size)

    # Execute query
    result = await db.execute(query)
    audit_entries = list(result.scalars().all())

    # Convert to response models
    items = [
        AuditTrailResponse(
            id=str(entry.id),
            tenant_id=str(entry.tenant_id) if entry.tenant_id else None,
            user_id=str(entry.user_id) if entry.user_id else None,
            action_type=entry.action_type,
            resource_type=entry.resource_type,
            resource_id=entry.resource_id,
            old_values=entry.old_values,
            new_values=entry.new_values,
            changes_summary=entry.changes_summary,
            ip_address=entry.ip_address,
            user_agent=entry.user_agent,
            success=entry.success,
            error_message=entry.error_message,
            created_at=entry.created_at,
        )
        for entry in audit_entries
    ]

    total_pages = (total + page_size - 1) // page_size

    return AuditTrailListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/stats",
    response_model=AuditTrailStatsResponse,
    summary="Get audit trail statistics",
    description="Get aggregated statistics about audit trail entries.",
)
async def get_audit_trail_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
    tenant_id: Optional[UUID] = Query(None, description="Filter by tenant ID"),
    start_date: Optional[datetime] = Query(None, description="Start date (ISO 8601)"),
    end_date: Optional[datetime] = Query(None, description="End date (ISO 8601)"),
) -> AuditTrailStatsResponse:
    """
    Get aggregated statistics about audit trail entries.

    Provides insights into audit log activity for monitoring and reporting.

    Args:
        db: Database session
        current_user: Current authenticated user (must be super admin)
        tenant_id: Optional filter by specific tenant
        start_date: Optional filter entries after this date
        end_date: Optional filter entries before this date

    Returns:
        Aggregated statistics

    Raises:
        HTTPException: 403 if user is not super admin
    """
    _ensure_super_admin(current_user)

    # Build filters
    filters = []
    if tenant_id:
        filters.append(AuditTrail.tenant_id == tenant_id)
    if start_date:
        filters.append(AuditTrail.created_at >= start_date)
    if end_date:
        filters.append(AuditTrail.created_at <= end_date)

    base_filter = and_(*filters) if filters else True

    # Total entries
    total_result = await db.execute(
        select(func.count()).select_from(AuditTrail).where(base_filter)
    )
    total_entries = total_result.scalar() or 0

    # Successful actions
    success_result = await db.execute(
        select(func.count())
        .select_from(AuditTrail)
        .where(and_(base_filter, AuditTrail.success == True))
    )
    successful_actions = success_result.scalar() or 0

    # Failed actions
    failed_actions = total_entries - successful_actions

    # Unique users
    users_result = await db.execute(
        select(func.count(func.distinct(AuditTrail.user_id)))
        .where(and_(base_filter, AuditTrail.user_id.isnot(None)))
    )
    unique_users = users_result.scalar() or 0

    # Unique tenants
    tenants_result = await db.execute(
        select(func.count(func.distinct(AuditTrail.tenant_id)))
        .where(and_(base_filter, AuditTrail.tenant_id.isnot(None)))
    )
    unique_tenants = tenants_result.scalar() or 0

    # Actions by type
    actions_result = await db.execute(
        select(AuditTrail.action_type, func.count())
        .where(base_filter)
        .group_by(AuditTrail.action_type)
    )
    actions_by_type = {row[0]: row[1] for row in actions_result.all()}

    # Resources by type
    resources_result = await db.execute(
        select(AuditTrail.resource_type, func.count())
        .where(base_filter)
        .group_by(AuditTrail.resource_type)
    )
    resources_by_type = {row[0]: row[1] for row in resources_result.all()}

    return AuditTrailStatsResponse(
        total_entries=total_entries,
        successful_actions=successful_actions,
        failed_actions=failed_actions,
        unique_users=unique_users,
        unique_tenants=unique_tenants,
        actions_by_type=actions_by_type,
        resources_by_type=resources_by_type,
    )


@router.get(
    "/{audit_id}",
    response_model=AuditTrailResponse,
    summary="Get specific audit trail entry",
    description="Retrieve a single audit trail entry by ID.",
)
async def get_audit_trail_entry(
    audit_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> AuditTrailResponse:
    """
    Get a specific audit trail entry by ID.

    Args:
        audit_id: UUID of the audit trail entry
        db: Database session
        current_user: Current authenticated user (must be super admin)

    Returns:
        Audit trail entry

    Raises:
        HTTPException: 403 if user is not super admin
        HTTPException: 404 if audit entry not found
    """
    _ensure_super_admin(current_user)

    result = await db.execute(
        select(AuditTrail).where(AuditTrail.id == audit_id)
    )
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit trail entry {audit_id} not found.",
        )

    return AuditTrailResponse(
        id=str(entry.id),
        tenant_id=str(entry.tenant_id) if entry.tenant_id else None,
        user_id=str(entry.user_id) if entry.user_id else None,
        action_type=entry.action_type,
        resource_type=entry.resource_type,
        resource_id=entry.resource_id,
        old_values=entry.old_values,
        new_values=entry.new_values,
        changes_summary=entry.changes_summary,
        ip_address=entry.ip_address,
        user_agent=entry.user_agent,
        success=entry.success,
        error_message=entry.error_message,
        created_at=entry.created_at,
    )


@router.get(
    "/export/csv",
    summary="Export audit trail to CSV",
    description="Export filtered audit trail entries to CSV format.",
)
async def export_audit_trail_csv(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
    tenant_id: Optional[UUID] = Query(None, description="Filter by tenant ID"),
    user_id: Optional[UUID] = Query(None, description="Filter by user ID"),
    action_type: Optional[str] = Query(None, description="Filter by action type"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    start_date: Optional[datetime] = Query(None, description="Start date (ISO 8601)"),
    end_date: Optional[datetime] = Query(None, description="End date (ISO 8601)"),
    limit: int = Query(1000, le=10000, description="Maximum entries to export"),
) -> StreamingResponse:
    """
    Export audit trail entries to CSV format.

    Args:
        db: Database session
        current_user: Current authenticated user (must be super admin)
        tenant_id: Optional filter by tenant
        user_id: Optional filter by user
        action_type: Optional filter by action type
        resource_type: Optional filter by resource type
        start_date: Optional start date filter
        end_date: Optional end date filter
        limit: Maximum number of entries to export

    Returns:
        CSV file as streaming response

    Raises:
        HTTPException: 403 if user is not super admin
    """
    _ensure_super_admin(current_user)

    # Build query with same filters as main endpoint
    query = select(AuditTrail)
    filters = []

    if tenant_id:
        filters.append(AuditTrail.tenant_id == tenant_id)
    if user_id:
        filters.append(AuditTrail.user_id == user_id)
    if action_type:
        filters.append(AuditTrail.action_type == action_type)
    if resource_type:
        filters.append(AuditTrail.resource_type == resource_type)
    if start_date:
        filters.append(AuditTrail.created_at >= start_date)
    if end_date:
        filters.append(AuditTrail.created_at <= end_date)

    if filters:
        query = query.where(and_(*filters))

    query = query.order_by(AuditTrail.created_at.desc()).limit(limit)

    # Execute query
    result = await db.execute(query)
    entries = list(result.scalars().all())

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "id",
            "created_at",
            "tenant_id",
            "user_id",
            "action_type",
            "resource_type",
            "resource_id",
            "changes_summary",
            "ip_address",
            "success",
            "error_message",
        ],
    )

    writer.writeheader()
    for entry in entries:
        writer.writerow(
            {
                "id": str(entry.id),
                "created_at": entry.created_at.isoformat() if entry.created_at else "",
                "tenant_id": str(entry.tenant_id) if entry.tenant_id else "",
                "user_id": str(entry.user_id) if entry.user_id else "",
                "action_type": entry.action_type or "",
                "resource_type": entry.resource_type or "",
                "resource_id": entry.resource_id or "",
                "changes_summary": entry.changes_summary or "",
                "ip_address": entry.ip_address or "",
                "success": "success" if entry.success else "failure",
                "error_message": entry.error_message or "",
            }
        )

    # Return as streaming response
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=audit_trail_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
        },
    )


# =============================================================================
# Export
# =============================================================================

__all__ = ["router"]
