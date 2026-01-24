"""
Pattern Group API routes.

Provides endpoints for managing and querying pattern groups from the
LLM-enhanced edge case pattern recognition system.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.dependencies import get_current_user_with_db
from api.schemas.auth import UserResponse
from api.schemas.pattern_group import (
    PatternGroupCreate,
    PatternGroupDetailResponse,
    PatternGroupListResponse,
    PatternGroupResponse,
    PatternGroupUpdate,
)
from models.audit_trail import log_audit_trail
from services.pattern_group_service import PatternGroupService
from api.auth.roles import Role
from celery_app import celery
from celery.result import AsyncResult


router = APIRouter(prefix="/pattern-groups", tags=["Pattern Groups"])

_PATTERN_GROUP_MUTATION_ROLES = {Role.ORG_ADMIN.value, Role.ORG_ADMIN.value, Role.QA_LEAD.value}


def _ensure_can_mutate_pattern_group(user: UserResponse) -> None:
    """
    Verify user has permission to mutate pattern groups.

    Args:
        user: Current authenticated user

    Raises:
        HTTPException: 403 if user lacks required role
    """
    if user.role not in _PATTERN_GROUP_MUTATION_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or QA lead role required to modify pattern groups.",
        )


def _map_not_found(error: Exception) -> HTTPException:
    message = str(error)
    if isinstance(error, NoResultFound) or "not found" in message.lower():
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


async def _run_with_service(
    db: AsyncSession,
    operation,
):
    """Run service operation within sync context."""
    def _execute(sync_session):
        service = PatternGroupService(sync_session)
        return operation(service)

    return await db.run_sync(_execute)


@router.post(
    "/",
    response_model=PatternGroupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new pattern group",
)
async def create_pattern_group_endpoint(
    payload: PatternGroupCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> PatternGroupResponse:
    """
    Create a new pattern group.

    Typically called by the LLM-enhanced pattern recognition system,
    but can also be created manually by admins.
    """
    _ensure_can_mutate_pattern_group(current_user)

    try:
        pattern_group = await _run_with_service(
            db,
            lambda service: service.create_pattern_group(**payload.model_dump()),
        )

        # Log audit trail
        tenant_id = current_user.tenant_id
        await log_audit_trail(
            db=db,
            action_type="create",
            resource_type="pattern_group",
            resource_id=str(pattern_group.id),
            tenant_id=tenant_id,
            user_id=current_user.id,
            new_values={
                "pattern_type": pattern_group.pattern_type,
                "canonical_example": pattern_group.canonical_example,
                "severity": pattern_group.severity,
                "status": pattern_group.status,
                "occurrence_count": pattern_group.occurrence_count,
            },
            changes_summary=f"Pattern group '{pattern_group.pattern_type}' created by {current_user.email}",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=True,
        )

        return PatternGroupResponse.model_validate(pattern_group)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get(
    "/",
    response_model=PatternGroupListResponse,
    summary="List pattern groups with filters and pagination",
)
async def list_pattern_groups_endpoint(
    status_filter: Optional[str] = Query(None, alias="status"),
    severity: Optional[str] = None,
    pattern_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> PatternGroupListResponse:
    """
    List pattern groups with optional filters.

    Returns patterns ordered by most recent activity and occurrence count.
    """
    filters: Dict[str, Any] = {}
    if status_filter:
        filters["status"] = status_filter
    if severity:
        filters["severity"] = severity
    if pattern_type:
        filters["pattern_type"] = pattern_type

    items, total = await _run_with_service(
        db,
        lambda service: service.list_pattern_groups(
            filters=filters,
            pagination={"skip": skip, "limit": limit},
        ),
    )

    responses = [PatternGroupResponse.model_validate(item) for item in items]
    return PatternGroupListResponse(total=total, items=responses)


@router.get(
    "/trending",
    response_model=List[PatternGroupResponse],
    summary="Get trending patterns",
)
async def get_trending_patterns_endpoint(
    days: int = Query(7, ge=1, le=90),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> List[PatternGroupResponse]:
    """
    Get trending patterns (recently active with high occurrence).

    Useful for identifying urgent issues that need attention.
    """
    patterns = await _run_with_service(
        db,
        lambda service: service.get_trending_patterns(days=days, limit=limit),
    )

    return [PatternGroupResponse.model_validate(p) for p in patterns]


@router.get(
    "/{pattern_group_id}",
    response_model=PatternGroupResponse,
    summary="Retrieve a pattern group by ID",
)
async def get_pattern_group_endpoint(
    pattern_group_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> PatternGroupResponse:
    """Get pattern group by ID."""
    try:
        pattern_group = await _run_with_service(
            db,
            lambda service: service.get_pattern_group(pattern_group_id),
        )
        return PatternGroupResponse.model_validate(pattern_group)
    except (NoResultFound, ValueError) as error:
        raise _map_not_found(error) from error


@router.get(
    "/{pattern_group_id}/details",
    response_model=PatternGroupDetailResponse,
    summary="Get pattern group with linked edge cases",
)
async def get_pattern_group_details_endpoint(
    pattern_group_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> PatternGroupDetailResponse:
    """
    Get pattern group with its linked edge cases.

    Returns the pattern group along with up to `limit` edge cases
    that belong to this pattern.
    """
    try:
        pattern, edge_cases, total = await _run_with_service(
            db,
            lambda service: service.get_pattern_with_edge_cases(
                pattern_group_id,
                limit=limit
            ),
        )

        return PatternGroupDetailResponse(
            pattern=PatternGroupResponse.model_validate(pattern),
            edge_cases=[ec.to_dict() for ec in edge_cases],
            total_edge_cases=total,
        )
    except (NoResultFound, ValueError) as error:
        raise _map_not_found(error) from error


@router.patch(
    "/{pattern_group_id}",
    response_model=PatternGroupResponse,
    summary="Update pattern group fields",
)
async def update_pattern_group_endpoint(
    pattern_group_id: UUID,
    payload: PatternGroupUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> PatternGroupResponse:
    """Update pattern group fields."""
    _ensure_can_mutate_pattern_group(current_user)

    values = payload.model_dump(exclude_unset=True)
    if not values:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    # Get old pattern group for audit logging
    try:
        old_pattern_group = await _run_with_service(
            db,
            lambda service: service.get_pattern_group(pattern_group_id),
        )
    except (NoResultFound, ValueError) as error:
        raise _map_not_found(error) from error

    # Capture old values
    old_values = {
        "pattern_type": old_pattern_group.pattern_type,
        "canonical_example": old_pattern_group.canonical_example,
        "severity": old_pattern_group.severity,
        "status": old_pattern_group.status,
        "occurrence_count": old_pattern_group.occurrence_count,
    }

    try:
        pattern_group = await _run_with_service(
            db,
            lambda service: service.update_pattern_group(pattern_group_id, **values),
        )

        # Capture new values
        new_values = {
            "pattern_type": pattern_group.pattern_type,
            "canonical_example": pattern_group.canonical_example,
            "severity": pattern_group.severity,
            "status": pattern_group.status,
            "occurrence_count": pattern_group.occurrence_count,
        }

        # Log audit trail
        tenant_id = current_user.tenant_id
        await log_audit_trail(
            db=db,
            action_type="update",
            resource_type="pattern_group",
            resource_id=str(pattern_group.id),
            tenant_id=tenant_id,
            user_id=current_user.id,
            old_values=old_values,
            new_values=new_values,
            changes_summary=f"Pattern group '{pattern_group.pattern_type}' updated by {current_user.email}",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=True,
        )

        return PatternGroupResponse.model_validate(pattern_group)
    except (NoResultFound, ValueError) as error:
        raise _map_not_found(error) from error


@router.delete(
    "/{pattern_group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a pattern group",
)
async def delete_pattern_group_endpoint(
    pattern_group_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> Response:
    """
    Delete a pattern group.

    This will also delete all links to edge cases (CASCADE).
    """
    _ensure_can_mutate_pattern_group(current_user)

    # Get old pattern group for audit logging
    try:
        old_pattern_group = await _run_with_service(
            db,
            lambda service: service.get_pattern_group(pattern_group_id),
        )
    except (NoResultFound, ValueError) as error:
        raise _map_not_found(error) from error

    # Capture old values
    old_values = {
        "pattern_type": old_pattern_group.pattern_type,
        "canonical_example": old_pattern_group.canonical_example,
        "severity": old_pattern_group.severity,
        "status": old_pattern_group.status,
        "occurrence_count": old_pattern_group.occurrence_count,
    }

    try:
        await _run_with_service(
            db,
            lambda service: service.delete_pattern_group(pattern_group_id),
        )

        # Log audit trail
        tenant_id = current_user.tenant_id
        await log_audit_trail(
            db=db,
            action_type="delete",
            resource_type="pattern_group",
            resource_id=str(pattern_group_id),
            tenant_id=tenant_id,
            user_id=current_user.id,
            old_values=old_values,
            changes_summary=f"Pattern group '{old_pattern_group.pattern_type}' deleted by {current_user.email}",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=True,
        )

    except (NoResultFound, ValueError) as error:
        raise _map_not_found(error) from error

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/analyze/trigger",
    summary="Manually trigger pattern recognition analysis",
)
async def trigger_pattern_analysis_endpoint(
    lookback_days: int = Query(7, ge=1, le=90),
    min_pattern_size: int = Query(3, ge=2, le=20),
    similarity_threshold: float = Query(0.85, ge=0.5, le=1.0),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> Dict[str, Any]:
    """
    Manually trigger the edge case pattern recognition analysis.

    This endpoint allows authorized users to trigger the pattern recognition
    job immediately without waiting for the scheduled 2 AM run.

    Args:
        lookback_days: Number of days to look back for edge cases (1-90)
        min_pattern_size: Minimum edge cases per pattern (2-20)
        similarity_threshold: Semantic similarity threshold (0.5-1.0)

    Returns:
        Dict with task_id and status for tracking the analysis job
    """
    _ensure_can_mutate_pattern_group(current_user)

    # Trigger the Celery task
    task = celery.send_task(
        "analyze_edge_case_patterns",
        kwargs={
            "lookback_days": lookback_days,
            "min_pattern_size": min_pattern_size,
            "similarity_threshold": similarity_threshold,
        },
    )

    return {
        "task_id": task.id,
        "status": "started",
        "message": f"Pattern analysis started with {lookback_days} day lookback",
        "parameters": {
            "lookback_days": lookback_days,
            "min_pattern_size": min_pattern_size,
            "similarity_threshold": similarity_threshold,
        },
    }


@router.get(
    "/analyze/status/{task_id}",
    summary="Check pattern analysis job status",
)
async def check_analysis_status_endpoint(
    task_id: str,
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> Dict[str, Any]:
    """
    Check the status of a pattern recognition analysis job.

    Returns the current status and result (if complete) of the analysis task.

    Args:
        task_id: Celery task ID returned from trigger endpoint

    Returns:
        Dict with task status, state, and result if completed
    """
    # Get task result from Celery
    task_result = AsyncResult(task_id, app=celery)

    response = {
        "task_id": task_id,
        "status": task_result.state,
    }

    if task_result.state == "PENDING":
        response["message"] = "Task is waiting to be processed"
    elif task_result.state == "STARTED":
        response["message"] = "Task is currently running"
    elif task_result.state == "SUCCESS":
        response["message"] = "Analysis completed successfully"
        response["result"] = task_result.result
    elif task_result.state == "FAILURE":
        response["message"] = "Analysis failed"
        response["error"] = str(task_result.info)
    else:
        response["message"] = f"Task state: {task_result.state}"

    return response
