"""
Test Suite API routes

Provides endpoints for test suite management including creation, retrieval,
updates, deletion, and scenario management.

Endpoints:
    GET /api/v1/test-suites - List test suites with filters and pagination
    POST /api/v1/test-suites - Create new test suite
    GET /api/v1/test-suites/{id} - Get test suite by ID
    PUT /api/v1/test-suites/{id} - Update test suite
    DELETE /api/v1/test-suites/{id} - Delete test suite
    GET /api/v1/test-suites/{id}/scenarios - Get scenarios in a suite
    POST /api/v1/test-suites/{id}/scenarios - Add scenarios to a suite
    DELETE /api/v1/test-suites/{id}/scenarios - Remove scenarios from a suite
    PUT /api/v1/test-suites/{id}/scenarios/reorder - Reorder scenarios in a suite
    POST /api/v1/test-suites/{id}/run - Run all scenarios in a suite

All endpoints require authentication via JWT token and use Pydantic schemas
for validation and return standard responses.
"""

from datetime import datetime
from typing import Annotated, Optional, List
from uuid import UUID
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.dependencies import get_current_user_with_db
from models.audit_trail import log_audit_trail
from api.schemas.test_suite import (
    TestSuiteCreate,
    TestSuiteUpdate,
    TestSuiteResponse,
    TestSuitesListResponse,
    TestSuiteWithScenariosResponse,
    SuiteScenarioInfo,
    AddScenariosToSuiteRequest,
    RemoveScenariosFromSuiteRequest,
    ReorderSuiteScenariosRequest,
    RunSuiteRequest,
    RunSuiteResponse,
    SuiteExecutionScenarioResult,
)
from api.schemas.auth import UserResponse
from services import test_suite_service
from services.test_suite_service import resolve_suite_languages
from services.multi_turn_execution_service import MultiTurnExecutionService
from models.suite_run import SuiteRun
from api.auth.roles import Role


# Create router
router = APIRouter(prefix="/test-suites", tags=["Test Suites"])

# Security scheme for Bearer token
security = HTTPBearer()
_SUITE_MUTATION_ROLES = {Role.ORG_ADMIN.value, Role.ORG_ADMIN.value, Role.QA_LEAD.value}


# =============================================================================
# Helper Functions
# =============================================================================

# Use centralized get_current_user_with_db from api.dependencies


def _get_effective_tenant_id(user: UserResponse) -> UUID:
    """
    Get effective tenant_id for a user.

    Uses user.tenant_id if set (user belongs to an organization),
    otherwise uses user.id (user is their own tenant).

    This ensures tenant_id is NEVER None for data isolation.
    """
    return user.tenant_id if user.tenant_id else user.id


def _ensure_can_mutate_test_suite(user: UserResponse) -> None:
    """
    Verify user has permission to mutate test suites (create, update, delete).

    Args:
        user: Current authenticated user

    Raises:
        HTTPException: 403 if user lacks required role
    """
    if user.role not in _SUITE_MUTATION_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or QA lead role required to modify test suites.",
        )


# =============================================================================
# List Test Suites Endpoint
# =============================================================================

@router.get(
    "/",
    response_model=TestSuitesListResponse,
    summary="List test suites",
    description="Retrieve a paginated list of test suites with optional filters"
)
async def list_test_suites(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
    category: Optional[str] = Query(None, description="Filter by category"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return")
) -> dict:
    """
    List test suites with filters and pagination.

    Returns a paginated list of test suites matching the specified filters.
    Requires authentication.

    Args:
        db: Database session
        current_user: Current authenticated user
        category: Optional filter by category
        is_active: Optional filter by active status
        skip: Number of records to skip (pagination offset)
        limit: Maximum number of records to return (pagination limit)

    Returns:
        dict: Dictionary containing test_suites list and pagination metadata
    """
    try:
        filters = {}
        if category:
            filters["category"] = category
        if is_active is not None:
            filters["is_active"] = is_active

        pagination = {"skip": skip, "limit": limit}

        tenant_id = _get_effective_tenant_id(current_user)
        test_suites, total = await test_suite_service.list_test_suites(
            db, filters, pagination, tenant_id=tenant_id
        )

        test_suite_responses = [TestSuiteResponse.model_validate(ts) for ts in test_suites]

        return {
            "test_suites": test_suite_responses,
            "total": total,
            "skip": skip,
            "limit": limit
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list test suites: {str(e)}"
        )


# =============================================================================
# Get Categorical Suites Endpoint
# =============================================================================

@router.get(
    "/categorical",
    summary="List categorical suites",
    description="Get scenarios grouped by category as virtual suites"
)
async def list_categorical_suites(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> dict:
    """
    Get scenarios grouped by category/domain as virtual suites.

    These are auto-generated groupings based on scenario metadata,
    not stored in the test_suites table.

    Returns:
        dict: Dictionary containing categorical_suites list
    """
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from models.scenario_script import ScenarioScript

    try:
        # Query all active scenarios with steps eagerly loaded
        query = (
            select(ScenarioScript)
            .where(ScenarioScript.is_active == True)
            .options(selectinload(ScenarioScript.steps))
        )
        result = await db.execute(query)
        scenarios = result.scalars().all()

        # Group scenarios by category
        category_groups: dict = {}

        for scenario in scenarios:
            # Extract category from metadata
            metadata = scenario.script_metadata or {}
            category = (
                metadata.get("category") or
                metadata.get("domain") or
                "Uncategorized"
            )

            # Normalize category name
            category = category.replace("_", " ").title()

            if category not in category_groups:
                category_groups[category] = {
                    "name": category,
                    "scenario_count": 0,
                    "scenario_ids": [],
                    "scenarios": []
                }

            category_groups[category]["scenario_count"] += 1
            category_groups[category]["scenario_ids"].append(str(scenario.id))
            category_groups[category]["scenarios"].append({
                "id": str(scenario.id),
                "name": scenario.name,
                "description": scenario.description,
                "steps_count": len(scenario.steps) if scenario.steps else 0
            })

        # Convert to list and sort by name
        categorical_suites = sorted(
            category_groups.values(),
            key=lambda x: x["name"]
        )

        return {
            "categorical_suites": categorical_suites,
            "total": len(categorical_suites)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get categorical suites: {str(e)}"
        )


# =============================================================================
# Run Categorical Suite Endpoint
# =============================================================================

from pydantic import BaseModel

class RunCategoricalSuiteRequest(BaseModel):
    """Request for running a categorical suite."""
    category_name: str
    scenario_ids: List[str]
    language_code: Optional[str] = "en-US"


@router.post(
    "/categorical/run",
    response_model=RunSuiteResponse,
    summary="Run categorical suite",
    description="Run all scenarios in a category"
)
async def run_categorical_suite(
    data: RunCategoricalSuiteRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> RunSuiteResponse:
    """
    Run all scenarios in a category.

    Creates a new test run and executes all scenarios in the category.

    Args:
        data: Request with category name, scenario IDs, and language code
        db: Database session
        current_user: Current authenticated user

    Returns:
        RunSuiteResponse: Suite execution response with scenario results
    """
    from sqlalchemy import select
    from models.scenario_script import ScenarioScript

    try:
        if not data.scenario_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No scenarios to run"
            )

        # Fetch the scenarios
        scenario_uuids = [UUID(sid) for sid in data.scenario_ids]
        query = select(ScenarioScript).where(
            ScenarioScript.id.in_(scenario_uuids),
            ScenarioScript.is_active == True
        )
        result = await db.execute(query)
        scenarios = result.scalars().all()

        if not scenarios:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active scenarios found for this category"
            )

        # Create a suite run for this categorical suite execution
        tenant_id = _get_effective_tenant_id(current_user)
        suite_run = SuiteRun(
            id=uuid.uuid4(),
            name=f"Category Run: {data.category_name}",
            description=f"Automated execution of category: {data.category_name}",
            status="in_progress",
            category_name=data.category_name,  # Store category for tracing
            created_by=current_user.id,
            tenant_id=tenant_id,
        )
        db.add(suite_run)
        await db.commit()
        await db.refresh(suite_run)

        # Initialize execution service
        execution_service = MultiTurnExecutionService()

        # Execute each scenario
        scenario_results = []
        language_code = data.language_code or "en-US"

        for scenario in scenarios:
            try:
                execution = await execution_service.execute_scenario(
                    db=db,
                    script_id=scenario.id,
                    suite_run_id=suite_run.id,
                    tenant_id=tenant_id,
                    language_codes=[language_code] if language_code else None
                )

                scenario_results.append(SuiteExecutionScenarioResult(
                    scenario_id=scenario.id,
                    scenario_name=scenario.name,
                    execution_id=execution.id,
                    status=execution.status,
                    error_message=execution.error_message
                ))

            except Exception as e:
                scenario_results.append(SuiteExecutionScenarioResult(
                    scenario_id=scenario.id,
                    scenario_name=scenario.name,
                    execution_id=None,
                    status="failed",
                    error_message=str(e)
                ))

        # Update suite run status
        all_completed = all(r.status == "completed" for r in scenario_results)
        any_failed = any(r.status == "failed" for r in scenario_results)

        if all_completed:
            suite_run.status = "completed"
        elif any_failed:
            suite_run.status = "failed"
        else:
            suite_run.status = "completed"

        suite_run.completed_at = datetime.utcnow()
        await db.commit()

        return RunSuiteResponse(
            suite_id=uuid.uuid4(),  # Virtual suite ID
            suite_name=f"Category: {data.category_name}",
            suite_run_id=suite_run.id,
            total_scenarios=len(scenario_results),
            status=suite_run.status,
            scenario_results=scenario_results,
            started_at=suite_run.created_at,
            completed_at=suite_run.completed_at
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run categorical suite: {str(e)}"
        )


# =============================================================================
# Suite Runs (Test Run History) Endpoints
# =============================================================================

@router.get(
    "/runs",
    summary="List suite runs",
    description="Get list of all suite/category runs with their status"
)
async def list_suite_runs(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
    suite_id: Optional[str] = Query(None, description="Filter by suite ID"),
    category_name: Optional[str] = Query(None, description="Filter by category name"),
    run_status: Optional[str] = Query(None, alias="status", description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
) -> dict:
    """
    List all suite runs with pagination.

    Returns both custom suite runs and categorical suite runs.
    """
    from sqlalchemy import select, func, desc
    from sqlalchemy.orm import selectinload

    try:
        # Build query
        tenant_id = _get_effective_tenant_id(current_user)
        query = select(SuiteRun).where(
            SuiteRun.tenant_id == tenant_id
        )

        # Apply filters
        if suite_id:
            query = query.where(SuiteRun.suite_id == UUID(suite_id))
        if category_name:
            query = query.where(SuiteRun.category_name == category_name)
        if run_status:
            query = query.where(SuiteRun.status == run_status)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(desc(SuiteRun.created_at)).offset(skip).limit(limit)

        # Load with relationships
        query = query.options(selectinload(SuiteRun.test_suite))

        result = await db.execute(query)
        runs = result.scalars().all()

        # Format response
        runs_data = []
        for run in runs:
            runs_data.append({
                "id": str(run.id),
                "name": run.name,
                "description": run.description,
                "suite_id": str(run.suite_id) if run.suite_id else None,
                "suite_name": run.test_suite.name if run.test_suite else None,
                "category_name": run.category_name,
                "status": run.status,
                "total_tests": run.total_tests,
                "passed_tests": run.passed_tests,
                "failed_tests": run.failed_tests,
                "skipped_tests": run.skipped_tests,
                "progress_percentage": run.progress_percentage,
                "created_at": run.created_at.isoformat() if run.created_at else None,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
                "is_categorical": run.category_name is not None,
            })

        return {
            "runs": runs_data,
            "total": total,
            "skip": skip,
            "limit": limit
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list suite runs: {str(e)}"
        )


@router.get(
    "/runs/{run_id}",
    summary="Get suite run details",
    description="Get detailed information about a suite run including scenario executions"
)
async def get_suite_run(
    run_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> dict:
    """
    Get details of a specific suite run with all scenario executions.
    """
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from models.multi_turn_execution import MultiTurnExecution

    try:
        # Get the suite run with relationships
        tenant_id = _get_effective_tenant_id(current_user)
        query = (
            select(SuiteRun)
            .where(
                SuiteRun.id == run_id,
                SuiteRun.tenant_id == tenant_id
            )
            .options(
                selectinload(SuiteRun.test_suite),
                selectinload(SuiteRun.scenario_executions).selectinload(MultiTurnExecution.script)
            )
        )

        result = await db.execute(query)
        suite_run = result.scalar_one_or_none()

        if not suite_run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Suite run {run_id} not found"
            )

        # Format scenario executions
        scenario_executions = []
        for execution in suite_run.scenario_executions:
            scenario_executions.append({
                "id": str(execution.id),
                "scenario_id": str(execution.script_id),
                "scenario_name": execution.script.name if execution.script else "Unknown",
                "status": execution.status,
                "current_step": execution.current_step_order,
                "total_steps": execution.total_steps,
                "progress_percentage": execution.progress_percentage,
                "started_at": execution.started_at.isoformat() if execution.started_at else None,
                "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                "error_message": execution.error_message,
            })

        return {
            "id": str(suite_run.id),
            "name": suite_run.name,
            "description": suite_run.description,
            "suite_id": str(suite_run.suite_id) if suite_run.suite_id else None,
            "suite_name": suite_run.test_suite.name if suite_run.test_suite else None,
            "category_name": suite_run.category_name,
            "status": suite_run.status,
            "total_tests": suite_run.total_tests,
            "passed_tests": suite_run.passed_tests,
            "failed_tests": suite_run.failed_tests,
            "skipped_tests": suite_run.skipped_tests,
            "progress_percentage": suite_run.progress_percentage,
            "created_at": suite_run.created_at.isoformat() if suite_run.created_at else None,
            "started_at": suite_run.started_at.isoformat() if suite_run.started_at else None,
            "completed_at": suite_run.completed_at.isoformat() if suite_run.completed_at else None,
            "is_categorical": suite_run.category_name is not None,
            "scenario_executions": scenario_executions,
            "total_scenarios": len(scenario_executions),
            "completed_scenarios": len([e for e in scenario_executions if e["status"] == "completed"]),
            "failed_scenarios": len([e for e in scenario_executions if e["status"] == "failed"]),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get suite run: {str(e)}"
        )


# =============================================================================
# Create Test Suite Endpoint
# =============================================================================

@router.post(
    "/",
    response_model=TestSuiteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create test suite",
    description="Create a new test suite"
)
async def create_test_suite(
    data: TestSuiteCreate,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> TestSuiteResponse:
    """
    Create a new test suite.

    Args:
        data: Test suite creation data
        request: HTTP request for audit logging
        db: Database session
        current_user: Current authenticated user

    Returns:
        TestSuiteResponse: The created test suite

    Raises:
        HTTPException: 403 if user lacks required role
    """
    _ensure_can_mutate_test_suite(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    try:
        test_suite = await test_suite_service.create_test_suite(
            db, data, current_user.id, tenant_id=tenant_id
        )

        # Log audit trail
        await log_audit_trail(
            db=db,
            action_type="create",
            resource_type="test_suite",
            resource_id=str(test_suite.id),
            tenant_id=tenant_id,
            user_id=current_user.id,
            new_values={
                "name": test_suite.name,
                "description": test_suite.description,
                "category": test_suite.category,
                "is_active": test_suite.is_active,
                "language_config": test_suite.language_config,
            },
            changes_summary=f"Test suite '{test_suite.name}' created by {current_user.email}",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=True,
        )

        return TestSuiteResponse.model_validate(test_suite)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create test suite: {str(e)}"
        )


# =============================================================================
# Get Test Suite Endpoint
# =============================================================================

@router.get(
    "/{test_suite_id}",
    response_model=TestSuiteResponse,
    summary="Get test suite",
    description="Retrieve a test suite by ID"
)
async def get_test_suite(
    test_suite_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> TestSuiteResponse:
    """
    Get a test suite by ID.

    Args:
        test_suite_id: UUID of the test suite to retrieve
        db: Database session
        current_user: Current authenticated user

    Returns:
        TestSuiteResponse: The requested test suite
    """
    tenant_id = _get_effective_tenant_id(current_user)
    try:
        test_suite = await test_suite_service.get_test_suite(
            db, test_suite_id, tenant_id=tenant_id
        )

        if not test_suite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test suite {test_suite_id} not found"
            )

        return TestSuiteResponse.model_validate(test_suite)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get test suite: {str(e)}"
        )


# =============================================================================
# Update Test Suite Endpoint
# =============================================================================

@router.put(
    "/{test_suite_id}",
    response_model=TestSuiteResponse,
    summary="Update test suite",
    description="Update a test suite by ID"
)
async def update_test_suite(
    test_suite_id: UUID,
    data: TestSuiteUpdate,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> TestSuiteResponse:
    """
    Update a test suite.

    Args:
        test_suite_id: UUID of the test suite to update
        data: Test suite update data
        request: HTTP request for audit logging
        db: Database session
        current_user: Current authenticated user

    Returns:
        TestSuiteResponse: The updated test suite

    Raises:
        HTTPException: 403 if user lacks required role
    """
    _ensure_can_mutate_test_suite(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    try:
        # Fetch existing test suite for audit logging
        existing = await test_suite_service.get_test_suite(db, test_suite_id, tenant_id=tenant_id)

        # Capture old values
        old_values = {
            "name": existing.name,
            "description": existing.description,
            "category": existing.category,
            "is_active": existing.is_active,
            "language_config": existing.language_config,
        }

        test_suite = await test_suite_service.update_test_suite(
            db, test_suite_id, data, tenant_id=tenant_id
        )

        # Capture new values
        new_values = {
            "name": test_suite.name,
            "description": test_suite.description,
            "category": test_suite.category,
            "is_active": test_suite.is_active,
            "language_config": test_suite.language_config,
        }

        # Build dynamic summary
        changes = []
        if old_values["name"] != new_values["name"]:
            changes.append(f"name changed")
        if old_values["is_active"] != new_values["is_active"]:
            changes.append(f"{'activated' if new_values['is_active'] else 'deactivated'}")
        if old_values["language_config"] != new_values["language_config"]:
            changes.append(f"language config updated")

        summary = f"Test suite '{test_suite.name}' updated by {current_user.email}"
        if changes:
            summary += f" - {', '.join(changes)}"

        # Log audit trail
        await log_audit_trail(
            db=db,
            action_type="update",
            resource_type="test_suite",
            resource_id=str(test_suite_id),
            tenant_id=tenant_id,
            user_id=current_user.id,
            old_values=old_values,
            new_values=new_values,
            changes_summary=summary,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=True,
        )

        return TestSuiteResponse.model_validate(test_suite)

    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test suite {test_suite_id} not found"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update test suite: {str(e)}"
        )


# =============================================================================
# Delete Test Suite Endpoint
# =============================================================================

@router.delete(
    "/{test_suite_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete test suite",
    description="Delete a test suite by ID"
)
async def delete_test_suite(
    test_suite_id: UUID,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
):
    """
    Delete a test suite.

    Args:
        test_suite_id: UUID of the test suite to delete
        request: HTTP request for audit logging
        db: Database session
        current_user: Current authenticated user

    Returns:
        None: 204 No Content on success

    Raises:
        HTTPException: 403 if user lacks required role
    """
    _ensure_can_mutate_test_suite(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    try:
        # Fetch test suite before deletion for audit logging
        existing = await test_suite_service.get_test_suite(db, test_suite_id, tenant_id=tenant_id)

        # Capture old values before deletion
        old_values = {
            "name": existing.name,
            "description": existing.description,
            "category": existing.category,
            "is_active": existing.is_active,
            "language_config": existing.language_config,
        }

        deleted = await test_suite_service.delete_test_suite(
            db, test_suite_id, tenant_id=tenant_id
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test suite {test_suite_id} not found"
            )

        # Log audit trail
        await log_audit_trail(
            db=db,
            action_type="delete",
            resource_type="test_suite",
            resource_id=str(test_suite_id),
            tenant_id=tenant_id,
            user_id=current_user.id,
            old_values=old_values,
            changes_summary=f"Test suite '{existing.name}' deleted by {current_user.email}",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=True,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete test suite: {str(e)}"
        )


# =============================================================================
# Scenario Management Endpoints
# =============================================================================


@router.get(
    "/{test_suite_id}/scenarios",
    response_model=TestSuiteWithScenariosResponse,
    summary="Get suite with scenarios",
    description="Retrieve a test suite with its scenarios"
)
async def get_suite_with_scenarios(
    test_suite_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> TestSuiteWithScenariosResponse:
    """
    Get a test suite with its scenarios.

    Args:
        test_suite_id: UUID of the test suite
        db: Database session
        current_user: Current authenticated user

    Returns:
        TestSuiteWithScenariosResponse: Suite with scenarios list
    """
    tenant_id = _get_effective_tenant_id(current_user)
    try:
        scenarios = await test_suite_service.get_suite_scenarios(
            db, test_suite_id, tenant_id=tenant_id
        )

        suite = await test_suite_service.get_test_suite(
            db, test_suite_id, tenant_id=tenant_id
        )

        if not suite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test suite {test_suite_id} not found"
            )

        scenario_infos = [
            SuiteScenarioInfo(
                scenario_id=s['scenario_id'],
                name=s['name'],
                description=s['description'],
                version=s['version'],
                is_active=s['is_active'],
                order=s['order'],
                languages=s['languages']
            )
            for s in scenarios
        ]

        return TestSuiteWithScenariosResponse(
            id=suite.id,
            name=suite.name,
            description=suite.description,
            category=suite.category,
            is_active=suite.is_active,
            language_config=suite.language_config,
            created_by=suite.created_by,
            scenarios=scenario_infos,
            scenario_count=len(scenario_infos),
            created_at=suite.created_at,
            updated_at=suite.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get suite scenarios: {str(e)}"
        )


@router.post(
    "/{test_suite_id}/scenarios",
    response_model=TestSuiteWithScenariosResponse,
    summary="Add scenarios to suite",
    description="Add scenarios to a test suite"
)
async def add_scenarios_to_suite(
    test_suite_id: UUID,
    data: AddScenariosToSuiteRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> TestSuiteWithScenariosResponse:
    """
    Add scenarios to a test suite.

    Args:
        test_suite_id: UUID of the test suite
        data: Request with scenario IDs to add
        db: Database session
        current_user: Current authenticated user

    Returns:
        TestSuiteWithScenariosResponse: Updated suite with scenarios
    """
    _ensure_can_mutate_test_suite(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    try:
        suite = await test_suite_service.add_scenarios_to_suite(
            db, test_suite_id, data.scenario_ids, tenant_id=tenant_id
        )

        scenarios = await test_suite_service.get_suite_scenarios(
            db, test_suite_id, tenant_id=tenant_id
        )

        scenario_infos = [
            SuiteScenarioInfo(
                scenario_id=s['scenario_id'],
                name=s['name'],
                description=s['description'],
                version=s['version'],
                is_active=s['is_active'],
                order=s['order'],
                languages=s['languages']
            )
            for s in scenarios
        ]

        return TestSuiteWithScenariosResponse(
            id=suite.id,
            name=suite.name,
            description=suite.description,
            category=suite.category,
            is_active=suite.is_active,
            language_config=suite.language_config,
            created_by=suite.created_by,
            scenarios=scenario_infos,
            scenario_count=len(scenario_infos),
            created_at=suite.created_at,
            updated_at=suite.updated_at
        )

    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test suite {test_suite_id} not found"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add scenarios to suite: {str(e)}"
        )


@router.delete(
    "/{test_suite_id}/scenarios",
    response_model=TestSuiteWithScenariosResponse,
    summary="Remove scenarios from suite",
    description="Remove scenarios from a test suite"
)
async def remove_scenarios_from_suite(
    test_suite_id: UUID,
    data: RemoveScenariosFromSuiteRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> TestSuiteWithScenariosResponse:
    """
    Remove scenarios from a test suite.

    Args:
        test_suite_id: UUID of the test suite
        data: Request with scenario IDs to remove
        db: Database session
        current_user: Current authenticated user

    Returns:
        TestSuiteWithScenariosResponse: Updated suite with remaining scenarios
    """
    _ensure_can_mutate_test_suite(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    try:
        suite = await test_suite_service.remove_scenarios_from_suite(
            db, test_suite_id, data.scenario_ids, tenant_id=tenant_id
        )

        scenarios = await test_suite_service.get_suite_scenarios(
            db, test_suite_id, tenant_id=tenant_id
        )

        scenario_infos = [
            SuiteScenarioInfo(
                scenario_id=s['scenario_id'],
                name=s['name'],
                description=s['description'],
                version=s['version'],
                is_active=s['is_active'],
                order=s['order'],
                languages=s['languages']
            )
            for s in scenarios
        ]

        return TestSuiteWithScenariosResponse(
            id=suite.id,
            name=suite.name,
            description=suite.description,
            category=suite.category,
            is_active=suite.is_active,
            language_config=suite.language_config,
            created_by=suite.created_by,
            scenarios=scenario_infos,
            scenario_count=len(scenario_infos),
            created_at=suite.created_at,
            updated_at=suite.updated_at
        )

    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test suite {test_suite_id} not found"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove scenarios from suite: {str(e)}"
        )


@router.put(
    "/{test_suite_id}/scenarios/reorder",
    response_model=TestSuiteWithScenariosResponse,
    summary="Reorder scenarios in suite",
    description="Reorder scenarios in a test suite"
)
async def reorder_suite_scenarios(
    test_suite_id: UUID,
    data: ReorderSuiteScenariosRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> TestSuiteWithScenariosResponse:
    """
    Reorder scenarios in a test suite.

    Args:
        test_suite_id: UUID of the test suite
        data: Request with scenario IDs in desired order
        db: Database session
        current_user: Current authenticated user

    Returns:
        TestSuiteWithScenariosResponse: Updated suite with reordered scenarios
    """
    _ensure_can_mutate_test_suite(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    try:
        suite = await test_suite_service.reorder_suite_scenarios(
            db, test_suite_id, data.scenario_order, tenant_id=tenant_id
        )

        scenarios = await test_suite_service.get_suite_scenarios(
            db, test_suite_id, tenant_id=tenant_id
        )

        scenario_infos = [
            SuiteScenarioInfo(
                scenario_id=s['scenario_id'],
                name=s['name'],
                description=s['description'],
                version=s['version'],
                is_active=s['is_active'],
                order=s['order'],
                languages=s['languages']
            )
            for s in scenarios
        ]

        return TestSuiteWithScenariosResponse(
            id=suite.id,
            name=suite.name,
            description=suite.description,
            category=suite.category,
            is_active=suite.is_active,
            language_config=suite.language_config,
            created_by=suite.created_by,
            scenarios=scenario_infos,
            scenario_count=len(scenario_infos),
            created_at=suite.created_at,
            updated_at=suite.updated_at
        )

    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test suite {test_suite_id} not found"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reorder scenarios in suite: {str(e)}"
        )


# =============================================================================
# Run Suite Endpoint
# =============================================================================


@router.post(
    "/{test_suite_id}/run",
    response_model=RunSuiteResponse,
    summary="Run suite",
    description="Run all scenarios in a test suite"
)
async def run_suite(
    test_suite_id: UUID,
    data: RunSuiteRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> RunSuiteResponse:
    """
    Run all scenarios in a test suite.

    Creates a new test run and executes all scenarios in the suite.

    Args:
        test_suite_id: UUID of the test suite to run
        data: Request with optional language code
        db: Database session
        current_user: Current authenticated user

    Returns:
        RunSuiteResponse: Suite execution response with scenario results
    """
    import logging
    logger = logging.getLogger(__name__)

    tenant_id = _get_effective_tenant_id(current_user)
    try:
        # Get suite with scenarios
        suite = await test_suite_service.get_test_suite_with_scenarios(
            db, test_suite_id, tenant_id=tenant_id
        )

        if not suite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test suite {test_suite_id} not found"
            )

        logger.info(f"[RUN_SUITE] Suite '{suite.name}' found, suite_scenarios count: {len(suite.suite_scenarios) if suite.suite_scenarios else 0}")

        if not suite.suite_scenarios:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Test suite has no scenarios to run"
            )

        # Create a suite run for this suite execution
        suite_run = SuiteRun(
            id=uuid.uuid4(),
            name=f"Suite Run: {suite.name}",
            description=f"Automated execution of test suite: {suite.name}",
            status="in_progress",
            suite_id=suite.id,
            created_by=current_user.id,
            tenant_id=tenant_id,
        )
        db.add(suite_run)
        await db.commit()
        await db.refresh(suite_run)

        # Initialize execution service
        execution_service = MultiTurnExecutionService()

        # Execute each scenario in order
        scenario_results = []

        # Get suite language configuration or use legacy request language_code
        suite_language_config = suite.language_config
        if not suite_language_config and data.language_code:
            # Legacy support: create config from single language_code
            suite_language_config = {
                "mode": "specific",
                "languages": [data.language_code],
                "fallback_behavior": "smart"
            }

        logger.info(f"[RUN_SUITE] Starting execution loop for {len(suite.suite_scenarios)} associations")
        logger.info(f"[RUN_SUITE] Suite language_config: {suite.language_config}")

        for assoc in sorted(suite.suite_scenarios, key=lambda a: a.order):
            scenario = assoc.scenario
            logger.info(f"[RUN_SUITE] Processing association: scenario={scenario.name if scenario else 'None'}, is_active={scenario.is_active if scenario else 'N/A'}, type(is_active)={type(scenario.is_active) if scenario else 'N/A'}")
            if not scenario or not scenario.is_active:
                logger.info(f"[RUN_SUITE] Skipping - scenario is None or inactive")
                continue

            logger.info(f"[RUN_SUITE] ENTERING TRY BLOCK for {scenario.name}")
            try:
                logger.info(f"[RUN_SUITE] Fetching steps for scenario {scenario.id}")
                # Get scenario's available languages
                from sqlalchemy import select
                from models.scenario_script import ScenarioStep
                steps_result = await db.execute(
                    select(ScenarioStep).where(ScenarioStep.script_id == scenario.id)
                )
                logger.info(f"[RUN_SUITE] Steps query executed")
                steps = list(steps_result.scalars().all())
                logger.info(f"[RUN_SUITE] Found {len(steps)} steps")

                # Extract available languages from steps
                available_languages = set()
                for step in steps:
                    if step.step_metadata and 'language_variants' in step.step_metadata:
                        for variant in step.step_metadata['language_variants']:
                            available_languages.add(variant.get('language_code', 'en-US'))

                # Get primary language from script_metadata (primary_language column doesn't exist)
                script_metadata = scenario.script_metadata or {}
                scenario_primary_language = script_metadata.get('language', 'en-US')
                # Handle multi-language scenarios
                if scenario_primary_language == 'multi':
                    supported_langs = script_metadata.get('supported_languages', ['en-US'])
                    scenario_primary_language = supported_langs[0] if supported_langs else 'en-US'

                # If no language variants, use primary language
                if not available_languages:
                    available_languages.add(scenario_primary_language)

                scenario_languages = list(available_languages)

                # Resolve which languages to execute
                logger.info(f"[RUN_SUITE] Resolving languages: config={suite_language_config}, scenario_langs={scenario_languages}, primary={scenario_primary_language}")
                language_resolution = resolve_suite_languages(
                    suite_language_config,
                    scenario_languages,
                    scenario_primary_language
                )
                logger.info(f"[RUN_SUITE] Language resolution result: {language_resolution}")

                # Check if scenario should be skipped or failed
                if language_resolution.get("should_skip"):
                    logger.info(f"[RUN_SUITE] SKIPPING scenario due to language resolution")
                    scenario_results.append(SuiteExecutionScenarioResult(
                        scenario_id=scenario.id,
                        scenario_name=scenario.name,
                        execution_id=None,
                        status="skipped",
                        error_message="; ".join(language_resolution.get("warnings", []))
                    ))
                    continue

                if language_resolution.get("should_fail"):
                    logger.info(f"[RUN_SUITE] FAILING scenario due to language resolution")
                    scenario_results.append(SuiteExecutionScenarioResult(
                        scenario_id=scenario.id,
                        scenario_name=scenario.name,
                        execution_id=None,
                        status="failed",
                        error_message="; ".join(language_resolution.get("warnings", []))
                    ))
                    continue

                # Execute scenario with resolved languages
                languages_to_execute = language_resolution.get("languages", [scenario_primary_language])
                logger.info(f"[RUN_SUITE] CALLING execute_scenario for {scenario.name} with languages={languages_to_execute}")

                execution = await execution_service.execute_scenario(
                    db=db,
                    script_id=scenario.id,
                    suite_run_id=suite_run.id,
                    tenant_id=tenant_id,
                    language_codes=languages_to_execute,
                    suite_id=suite.id
                )

                # Add warnings to error_message if any
                warnings = language_resolution.get("warnings", [])
                error_message = execution.error_message
                if warnings:
                    warning_text = "Language warnings: " + "; ".join(warnings)
                    error_message = f"{error_message}. {warning_text}" if error_message else warning_text

                scenario_results.append(SuiteExecutionScenarioResult(
                    scenario_id=scenario.id,
                    scenario_name=scenario.name,
                    execution_id=execution.id,
                    status=execution.status,
                    error_message=error_message
                ))

            except Exception as e:
                logger.error(f"[RUN_SUITE] ERROR executing scenario {scenario.name}: {str(e)}", exc_info=True)
                scenario_results.append(SuiteExecutionScenarioResult(
                    scenario_id=scenario.id,
                    scenario_name=scenario.name,
                    execution_id=None,
                    status="failed",
                    error_message=str(e)
                ))

        # Update suite run status
        all_completed = all(r.status == "completed" for r in scenario_results)
        any_failed = any(r.status == "failed" for r in scenario_results)

        if all_completed:
            suite_run.status = "completed"
        elif any_failed:
            suite_run.status = "failed"
        else:
            suite_run.status = "completed"

        suite_run.completed_at = datetime.utcnow()
        await db.commit()

        return RunSuiteResponse(
            suite_id=suite.id,
            suite_name=suite.name,
            suite_run_id=suite_run.id,
            total_scenarios=len(scenario_results),
            status=suite_run.status,
            scenario_results=scenario_results,
            started_at=suite_run.created_at,
            completed_at=suite_run.completed_at
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run suite: {str(e)}"
        )
