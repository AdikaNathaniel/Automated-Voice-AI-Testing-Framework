"""
Regression management API routes (TASK-338).
"""

from __future__ import annotations

from typing import Annotated, Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.dependencies import get_current_user_with_db
from api.schemas.auth import UserResponse
from api.schemas.regression import (
    BaselineApprovalRequest,
    RegressionsListResponse,
    BaselineApprovalResponse,
    RegressionComparisonResponse,
    BaselineHistoryResponse,
    RegressionListResponse,
    RegressionRecordResponse,
    RegressionResolveRequest,
    RegressionCreateDefectRequest,
    RegressionCreateDefectResponse,
)
from models.audit_trail import log_audit_trail
from services import regression_service
from services.regression_tracking_service import RegressionTrackingService
from api.auth.roles import Role

router = APIRouter(prefix="/regressions", tags=["Regressions"])

_REGRESSION_MUTATION_ROLES = {Role.ORG_ADMIN.value, Role.ORG_ADMIN.value, Role.QA_LEAD.value}


def _ensure_can_mutate_regression(user: UserResponse) -> None:
    """
    Verify user has permission to approve regression baselines.

    Args:
        user: Current authenticated user

    Raises:
        HTTPException: 403 if user lacks required role
    """
    if user.role not in _REGRESSION_MUTATION_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or QA lead role required to approve regression baselines.",
        )


@router.get(
    "/",
    response_model=RegressionsListResponse,
    summary="List detected regressions",
    description="Retrieve detected regressions with optional filtering.",
)
async def list_regressions_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
    suite_id: Optional[UUID] = Query(None, description="Filter by suite ID"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by regression status"),
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum records to return"),
) -> dict:
    filters: Dict[str, object] = {}
    if suite_id is not None:
        filters["suite_id"] = suite_id
    if status_filter:
        filters["status"] = status_filter

    try:
        return await regression_service.list_regressions(
            db,
            filters=filters,
            pagination={"skip": skip, "limit": limit},
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.post(
    "/{script_id}/baseline",
    response_model=BaselineApprovalResponse,
    summary="Approve regression baseline",
    description="Approve a regression baseline snapshot for a scenario script.",
)
async def approve_baseline_endpoint(
    script_id: UUID,
    payload: BaselineApprovalRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> dict:
    _ensure_can_mutate_regression(current_user)

    snapshot_data = {
        "status": payload.status,
        "metrics": payload.metrics or {},
    }

    try:
        result = await regression_service.approve_baseline(
            db,
            script_id=script_id,
            snapshot_data=snapshot_data,
            approved_by=current_user.id,
            note=payload.note,
        )

        # Log audit trail
        tenant_id = current_user.tenant_id
        await log_audit_trail(
            db=db,
            action_type="approve_baseline",
            resource_type="regression_baseline",
            resource_id=str(script_id),
            tenant_id=tenant_id,
            user_id=current_user.id,
            new_values={
                "script_id": str(script_id),
                "status": payload.status,
                "approved_by": str(current_user.id),
                "note": payload.note,
            },
            changes_summary=f"Regression baseline approved for script {script_id} by {current_user.email}",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=True,
        )

        return result
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get(
    "/{script_id}/comparison",
    response_model=RegressionComparisonResponse,
    summary="Compare baseline against latest execution",
    description="Return current vs baseline snapshots with metric deltas.",
)
async def get_regression_comparison_endpoint(
    script_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> dict:
    try:
        return await regression_service.get_regression_comparison(
            db,
            script_id=script_id,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.get(
    "/{script_id}/baselines",
    response_model=BaselineHistoryResponse,
    summary="Get baseline history",
    description="Retrieve the baseline version history for a scenario script.",
)
async def get_baseline_history_endpoint(
    script_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> dict:
    try:
        return await regression_service.get_baseline_history(
            db,
            script_id=script_id,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


# ============================================================================
# Persistent Regression Tracking Endpoints
# ============================================================================


@router.get(
    "/records",
    response_model=RegressionListResponse,
    summary="List persistent regression records",
    description="Retrieve tracked regression records with filters and pagination.",
)
async def list_regression_records(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    script_id: Optional[UUID] = Query(None, description="Filter by script ID"),
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum records to return"),
) -> dict:
    service = RegressionTrackingService(db)
    return await service.list_regressions(
        tenant_id=current_user.tenant_id,
        status_filter=status_filter,
        category_filter=category,
        script_id=script_id,
        skip=skip,
        limit=limit,
    )


@router.post(
    "/records/{regression_id}/resolve",
    response_model=RegressionRecordResponse,
    summary="Resolve a regression",
    description="Manually mark a regression as resolved.",
)
async def resolve_regression_endpoint(
    regression_id: UUID,
    payload: RegressionResolveRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> dict:
    _ensure_can_mutate_regression(current_user)

    service = RegressionTrackingService(db)
    try:
        regression = await service.resolve_regression(
            regression_id=regression_id,
            resolved_by=current_user.id,
            note=payload.note,
        )

        # Log audit trail
        tenant_id = current_user.tenant_id
        await log_audit_trail(
            db=db,
            action_type="resolve",
            resource_type="regression",
            resource_id=str(regression_id),
            tenant_id=tenant_id,
            user_id=current_user.id,
            new_values={
                "regression_id": str(regression_id),
                "resolved_by": str(current_user.id),
                "note": payload.note,
                "status": "resolved",
            },
            changes_summary=f"Regression {regression_id} resolved by {current_user.email}",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=True,
        )

        return service._serialize_regression(regression)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.post(
    "/records/{regression_id}/create-defect",
    response_model=RegressionCreateDefectResponse,
    summary="Create defect from regression",
    description="Create a defect to track and resolve a regression.",
)
async def create_defect_from_regression_endpoint(
    regression_id: UUID,
    payload: RegressionCreateDefectRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> dict:
    _ensure_can_mutate_regression(current_user)

    service = RegressionTrackingService(db)
    try:
        defect = await service.create_defect_from_regression(
            regression_id=regression_id,
            created_by=current_user.id,
            severity_override=payload.severity,
            additional_notes=payload.additional_notes,
        )

        # Log audit trail
        tenant_id = current_user.tenant_id
        await log_audit_trail(
            db=db,
            action_type="create_defect_from_regression",
            resource_type="defect",
            resource_id=str(defect.id),
            tenant_id=tenant_id,
            user_id=current_user.id,
            new_values={
                "defect_id": str(defect.id),
                "regression_id": str(regression_id),
                "severity": payload.severity if payload.severity else "from_regression",
                "created_by": str(current_user.id),
            },
            changes_summary=f"Defect {defect.id} created from regression {regression_id} by {current_user.email}",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=True,
        )

        return {
            "defect_id": str(defect.id),
            "regression_id": str(regression_id),
            "message": "Defect created successfully from regression",
        }
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
