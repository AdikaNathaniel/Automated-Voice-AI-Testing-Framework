"""
Edge case library API routes.
"""

from __future__ import annotations

from datetime import date
from typing import Dict, List, Optional, TypeVar, Callable
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.dependencies import get_current_user_with_db
from api.schemas.auth import UserResponse
from api.schemas.edge_case import (
    EdgeCaseAnalyticsResponse,
    EdgeCaseCategorizeRequest,
    EdgeCaseCreate,
    EdgeCaseListResponse,
    EdgeCaseResponse,
    EdgeCaseUpdate,
)
from services.edge_case_service import EdgeCaseService
from services.edge_case_analytics_service import EdgeCaseAnalyticsService
from api.auth.roles import Role


router = APIRouter(prefix="/edge-cases", tags=["Edge Cases"])

_EDGE_CASE_MUTATION_ROLES = {Role.ORG_ADMIN.value, Role.ORG_ADMIN.value, Role.QA_LEAD.value}


def _get_effective_tenant_id(user: UserResponse) -> UUID:
    """
    Get effective tenant_id for a user.

    Uses user.tenant_id if set (user belongs to an organization),
    otherwise uses user.id (user is their own tenant).

    This ensures tenant_id is NEVER None for data isolation.
    """
    return user.tenant_id if user.tenant_id else user.id


def _ensure_can_mutate_edge_case(user: UserResponse) -> None:
    """
    Verify user has permission to mutate edge cases (create, update, delete, etc).

    Args:
        user: Current authenticated user

    Raises:
        HTTPException: 403 if user lacks required role
    """
    if user.role not in _EDGE_CASE_MUTATION_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or QA lead role required to modify edge cases.",
        )

T = TypeVar("T")


def _map_not_found(error: Exception) -> HTTPException:
    message = str(error)
    if isinstance(error, NoResultFound) or "not found" in message.lower():
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


async def _run_with_service(
    db: AsyncSession,
    operation: Callable[[EdgeCaseService], T],
) -> T:
    def _execute(sync_session):
        service = EdgeCaseService(sync_session)
        return operation(service)

    return await db.run_sync(_execute)


@router.post(
    "/",
    response_model=EdgeCaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new edge case record",
)
async def create_edge_case_endpoint(
    payload: EdgeCaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> EdgeCaseResponse:
    _ensure_can_mutate_edge_case(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    try:
        edge_case = await _run_with_service(
            db,
            lambda service: service.create_edge_case(
                tenant_id=tenant_id,
                **payload.model_dump(),
            ),
        )
        return EdgeCaseResponse.model_validate(edge_case)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get(
    "/analytics",
    response_model=EdgeCaseAnalyticsResponse,
    summary="Get edge case analytics and metrics",
)
async def get_edge_case_analytics_endpoint(
    date_from: Optional[date] = Query(
        None,
        description="Start date for analytics (YYYY-MM-DD). Defaults to 30 days ago.",
    ),
    date_to: Optional[date] = Query(
        None,
        description="End date for analytics (YYYY-MM-DD). Defaults to today.",
    ),
    include_trend: bool = Query(
        True,
        description="Include trend comparison with previous period",
    ),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> EdgeCaseAnalyticsResponse:
    """
    Retrieve comprehensive analytics for edge cases.

    Returns:
    - Summary metrics (totals, active, resolved)
    - Time series data for trend charts
    - Category and severity distributions
    - Resolution rate metrics
    - Top patterns by occurrence
    - Auto-created vs manual breakdown
    - Optional trend comparison with previous period

    Date range defaults to last 30 days if not specified.
    """
    from datetime import date as date_type

    def _get_analytics(sync_session):
        service = EdgeCaseAnalyticsService(sync_session)

        # Get main analytics
        analytics = service.get_analytics(
            date_from=date_from,
            date_to=date_to,
        )

        # Add trend comparison if requested
        if include_trend:
            trend = service.get_trend_comparison(
                date_to=date_to,
                period_days=30,
            )
            analytics["trend_comparison"] = trend

        return analytics

    result = await db.run_sync(_get_analytics)

    # Transform to match schema expectations
    return EdgeCaseAnalyticsResponse(
        date_range={
            "from": result["date_range"]["from"],
            "to": result["date_range"]["to"],
        },
        summary=result["summary"],
        count_over_time=result["count_over_time"],
        category_distribution=[
            {"category": item["category"], "count": item["count"], "percentage": item["percentage"]}
            for item in result["category_distribution"]
        ],
        severity_distribution=[
            {"severity": item["severity"], "count": item["count"], "percentage": item["percentage"]}
            for item in result["severity_distribution"]
        ],
        status_distribution=[
            {"status": item["status"], "count": item["count"], "percentage": item["percentage"]}
            for item in result["status_distribution"]
        ],
        resolution_metrics=result["resolution_metrics"],
        top_patterns=result["top_patterns"],
        auto_vs_manual=result["auto_vs_manual"],
        trend_comparison=result.get("trend_comparison"),
    )


@router.get(
    "/search",
    response_model=EdgeCaseListResponse,
    summary="Search edge cases by keyword",
)
async def search_edge_cases_endpoint(
    query: str = Query(..., min_length=1),
    status_filter: Optional[str] = Query(None, alias="status"),
    category: Optional[str] = None,
    severity: Optional[str] = None,
    tags: Optional[List[str]] = Query(default=None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> EdgeCaseListResponse:
    tenant_id = _get_effective_tenant_id(current_user)

    filters: Dict[str, object] = {}
    if status_filter:
        filters["status"] = status_filter
    if category:
        filters["category"] = category
    if severity:
        filters["severity"] = severity
    if tags:
        filters["tags"] = list(tags)

    items, total = await _run_with_service(
        db,
        lambda service: service.search_edge_cases(
            tenant_id=tenant_id,
            query=query,
            filters=filters,
            pagination={"skip": skip, "limit": limit},
        ),
    )

    responses = [EdgeCaseResponse.model_validate(item) for item in items]
    return EdgeCaseListResponse(total=total, items=responses)


@router.get(
    "/",
    response_model=EdgeCaseListResponse,
    summary="List edge cases with filters and pagination",
)
async def list_edge_cases_endpoint(
    status_filter: Optional[str] = Query(None, alias="status"),
    category: Optional[str] = None,
    severity: Optional[str] = None,
    tags: Optional[List[str]] = Query(default=None),
    script_id: Optional[UUID] = None,
    discovered_by: Optional[UUID] = None,
    pattern_group_id: Optional[UUID] = Query(
        None,
        description="Filter by pattern group ID to show only edge cases in this pattern"
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> EdgeCaseListResponse:
    tenant_id = _get_effective_tenant_id(current_user)

    filters: Dict[str, object] = {}
    if status_filter:
        filters["status"] = status_filter
    if category:
        filters["category"] = category
    if severity:
        filters["severity"] = severity
    if tags:
        filters["tags"] = list(tags)
    if script_id:
        filters["script_id"] = script_id
    if discovered_by:
        filters["discovered_by"] = discovered_by
    if pattern_group_id:
        filters["pattern_group_id"] = pattern_group_id

    items, total = await _run_with_service(
        db,
        lambda service: service.list_edge_cases(
            tenant_id=tenant_id,
            filters=filters,
            pagination={"skip": skip, "limit": limit},
        ),
    )

    responses = [EdgeCaseResponse.model_validate(item) for item in items]
    return EdgeCaseListResponse(total=total, items=responses)


@router.get(
    "/{edge_case_id}",
    response_model=EdgeCaseResponse,
    summary="Retrieve an edge case by ID",
)
async def get_edge_case_endpoint(
    edge_case_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> EdgeCaseResponse:
    tenant_id = _get_effective_tenant_id(current_user)

    try:
        edge_case = await _run_with_service(
            db,
            lambda service: service.get_edge_case(edge_case_id, tenant_id=tenant_id),
        )
        return EdgeCaseResponse.model_validate(edge_case)
    except (NoResultFound, ValueError) as error:
        raise _map_not_found(error) from error


@router.patch(
    "/{edge_case_id}",
    response_model=EdgeCaseResponse,
    summary="Update edge case fields",
)
async def update_edge_case_endpoint(
    edge_case_id: UUID,
    payload: EdgeCaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> EdgeCaseResponse:
    _ensure_can_mutate_edge_case(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    values = payload.model_dump(exclude_unset=True)
    if not values:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    try:
        edge_case = await _run_with_service(
            db,
            lambda service: service.update_edge_case(
                edge_case_id,
                tenant_id=tenant_id,
                **values,
            ),
        )
        return EdgeCaseResponse.model_validate(edge_case)
    except (NoResultFound, ValueError) as error:
        raise _map_not_found(error) from error


@router.post(
    "/{edge_case_id}/categorize",
    response_model=EdgeCaseResponse,
    summary="Categorize an edge case using heuristic signals",
)
async def categorize_edge_case_endpoint(
    edge_case_id: UUID,
    payload: EdgeCaseCategorizeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> EdgeCaseResponse:
    _ensure_can_mutate_edge_case(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    try:
        edge_case = await _run_with_service(
            db,
            lambda service: service.categorize_edge_case(
                edge_case_id,
                tenant_id=tenant_id,
                signals=payload.signals,
            ),
        )
        return EdgeCaseResponse.model_validate(edge_case)
    except (NoResultFound, ValueError) as error:
        raise _map_not_found(error) from error


@router.delete(
    "/{edge_case_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an edge case record",
)
async def delete_edge_case_endpoint(
    edge_case_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> Response:
    _ensure_can_mutate_edge_case(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    try:
        await _run_with_service(
            db,
            lambda service: service.delete_edge_case(edge_case_id, tenant_id=tenant_id),
        )
    except (NoResultFound, ValueError) as error:
        raise _map_not_found(error) from error

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{edge_case_id}/rerun",
    response_model=Dict,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Re-run the scenario that caused this edge case",
)
async def rerun_edge_case_scenario(
    edge_case_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> Dict:
    """
    Re-execute the scenario linked to this edge case.

    This allows verification of whether the edge case issue still exists.
    If the scenario passes, the edge case can be marked as resolved.

    Args:
        edge_case_id: ID of the edge case to rerun
        db: Database session
        current_user: Authenticated user

    Returns:
        Execution result with pass/fail status

    Raises:
        HTTPException: 404 if edge case not found or has no linked script
    """
    from sqlalchemy import select
    from models.edge_case import EdgeCase
    from models.scenario_script import ScenarioScript
    from services.multi_turn_execution_service import MultiTurnExecutionService

    tenant_id = _get_effective_tenant_id(current_user)

    # Get edge case - scoped to tenant
    result = await db.execute(
        select(EdgeCase).where(
            EdgeCase.id == edge_case_id,
            EdgeCase.tenant_id == tenant_id,
        )
    )
    edge_case = result.scalar_one_or_none()

    if not edge_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Edge case {edge_case_id} not found"
        )

    if not edge_case.script_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Edge case has no linked scenario script to re-run"
        )

    # Verify script exists
    script_result = await db.execute(
        select(ScenarioScript).where(ScenarioScript.id == edge_case.script_id)
    )
    script = script_result.scalar_one_or_none()

    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Linked scenario script {edge_case.script_id} not found"
        )

    # Create a suite run for this edge case execution
    from models.suite_run import SuiteRun
    import uuid
    suite_run = SuiteRun(
        id=uuid.uuid4(),
        name=f"Edge Case Execution: {edge_case.title}",
        description=f"Re-run of edge case: {edge_case.title}",
        status="running",
        created_by=current_user.id,
        tenant_id=tenant_id,
    )
    db.add(suite_run)
    await db.commit()
    await db.refresh(suite_run)

    # Execute the scenario
    service = MultiTurnExecutionService()

    try:
        execution = await service.execute_scenario(
            db=db,
            script_id=edge_case.script_id,
            suite_run_id=suite_run.id,
            tenant_id=tenant_id,
        )
        await db.commit()

        # Determine if the execution passed
        passed = execution.status == "completed" and all(
            step.validation_passed for step in execution.step_executions
        )

        return {
            "edge_case_id": str(edge_case_id),
            "execution_id": str(execution.id),
            "script_id": str(edge_case.script_id),
            "script_name": script.name,
            "status": execution.status,
            "result": execution.overall_result,
            "passed": passed,
            "message": (
                "Scenario passed! Consider marking edge case as resolved."
                if passed
                else "Scenario still failing. Edge case issue persists."
            ),
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scenario execution failed: {str(e)}"
        )
