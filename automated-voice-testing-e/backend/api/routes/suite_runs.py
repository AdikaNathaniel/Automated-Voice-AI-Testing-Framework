"""
Suite Run API routes

Provides endpoints for suite run management including creation, retrieval,
execution, cancellation, and retry operations.

Endpoints:
    POST /api/v1/suite-runs - Create new suite run
    GET /api/v1/suite-runs - List suite runs with filters and pagination
    GET /api/v1/suite-runs/{id} - Get suite run by ID
    PUT /api/v1/suite-runs/{id}/cancel - Cancel a running suite run
    POST /api/v1/suite-runs/{id}/retry - Retry failed tests from a suite run
    GET /api/v1/suite-runs/{id}/executions - Get test executions for a suite run

All endpoints require authentication via JWT token and use Pydantic schemas
for validation and return standard responses.
"""

from typing import Annotated, Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.dependencies import get_current_user_with_db
from api.schemas.suite_run import (
    SuiteRunCreate,
    SuiteRunResponse,
    TestExecutionResponse,
    SuiteRunsListResponse,
)
from api.schemas.enums import SuiteRunStatus
from api.schemas.auth import UserResponse
from services import orchestration_service
from api.auth.roles import Role


# Create router
router = APIRouter(prefix="/suite-runs", tags=["Suite Runs"])

# Security scheme for Bearer token
security = HTTPBearer()
_RUN_CONTROL_ROLES = {Role.SUPER_ADMIN.value, Role.ORG_ADMIN.value, Role.QA_LEAD.value}


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


def _check_suite_run_tenant_access(user: UserResponse, suite_run) -> None:
    """
    Verify user has access to a suite run based on tenant isolation.

    Args:
        user: Current authenticated user
        suite_run: SuiteRun to check access for

    Raises:
        HTTPException: 403 if user cannot access the suite run
    """
    if suite_run.tenant_id is None:
        # Legacy suite runs without tenant_id are accessible (migration scenario)
        return

    effective_tenant_id = _get_effective_tenant_id(user)
    if suite_run.tenant_id != effective_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Suite run belongs to a different tenant.",
        )


def _ensure_run_controller(user: UserResponse) -> None:
    if user.role not in _RUN_CONTROL_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or QA lead role required for suite run management.",
        )


# =============================================================================
# Create Suite Run Endpoint
# =============================================================================

@router.post(
    "/",
    response_model=SuiteRunResponse,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    summary="Create suite run",
    description="Create a new suite run and schedule test executions"
)
async def create_suite_run(
    data: SuiteRunCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> SuiteRunResponse:
    """
    Create a new suite run.

    Creates a suite run from either a test suite or a list of test case IDs,
    and optionally schedules the test executions.

    Args:
        data: SuiteRunCreate schema with suite run configuration
        db: Database session
        current_user: Current authenticated user

    Returns:
        SuiteRunResponse: Created suite run details

    Raises:
        HTTPException: 400 if validation fails
        HTTPException: 404 if suite or test cases not found
        HTTPException: 500 if creation fails
    """
    _ensure_run_controller(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    import logging
    logger = logging.getLogger(__name__)

    logger.info(
        f"[SUITE_RUN_API] Creating suite run - "
        f"user_id={current_user.id}, suite_id={data.suite_id}, "
        f"scenario_ids={data.scenario_ids}, languages={data.languages}"
    )

    try:
        # Create suite run using orchestration service
        logger.info(f"[SUITE_RUN_API] Calling orchestration service to create suite run")
        suite_run = await orchestration_service.create_suite_run(
            db=db,
            suite_id=data.suite_id,
            scenario_ids=data.scenario_ids,
            languages=data.languages,
            trigger_type=data.trigger_type,
            trigger_metadata=data.trigger_metadata,
            created_by=current_user.id,
            tenant_id=tenant_id,
        )
        logger.info(f"[SUITE_RUN_API] Suite run created - id={suite_run.id}, status={suite_run.status}")

        # Schedule test executions
        logger.info(f"[SUITE_RUN_API] Scheduling test executions for suite_run_id={suite_run.id}")
        schedule_result = await orchestration_service.schedule_test_executions(
            db=db,
            suite_run_id=suite_run.id
        )
        logger.info(
            f"[SUITE_RUN_API] Test executions scheduled - "
            f"suite_run_id={suite_run.id}, "
            f"scheduled_count={schedule_result.get('scheduled_count', 'N/A')}, "
            f"task_ids={len(schedule_result.get('task_ids', []))} tasks"
        )

        # Refresh suite_run to get updated status and attributes
        await db.refresh(suite_run)
        logger.info(
            f"[SUITE_RUN_API] Suite run refreshed - "
            f"id={suite_run.id}, status={suite_run.status}, "
            f"total_tests={suite_run.total_tests}"
        )

        return SuiteRunResponse.model_validate(suite_run)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create suite run: {str(e)}"
        )


# =============================================================================
# List Suite Runs Endpoint
# =============================================================================

@router.get(
    "/",
    response_model=SuiteRunsListResponse,
    response_model_by_alias=True,
    summary="List suite runs",
    description="Retrieve a paginated list of suite runs with optional filters"
)
async def list_suite_runs(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
    suite_id: Optional[UUID] = Query(None, description="Filter by suite ID"),
    status_filter: Optional[SuiteRunStatus] = Query(None, description="Filter by status"),
    created_by: Optional[UUID] = Query(None, description="Filter by creator"),
    start_date: Optional[datetime] = Query(None, description="Filter runs created after this timestamp"),
    end_date: Optional[datetime] = Query(None, description="Filter runs created before this timestamp"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    language_code: Optional[str] = Query(None, description="Filter by language code (planned)"),
) -> dict:
    """
    List suite runs with filters and pagination.

    Returns a paginated list of suite runs matching the specified filters.
    Requires authentication.

    Args:
        db: Database session
        current_user: Current authenticated user
        suite_id: Optional filter by suite ID
        status_filter: Optional filter by status
        skip: Number of records to skip (pagination offset)
        limit: Maximum number of records to return (pagination limit)

    Returns:
        dict: Dictionary containing suite_runs list and pagination metadata
    """
    tenant_id = _get_effective_tenant_id(current_user)
    try:
        # TODO: Implement language filtering when the data model supports it
        runs, total = await orchestration_service.list_suite_runs(
            db=db,
            suite_id=suite_id,
            status_filter=status_filter.value if status_filter else None,
            created_by=created_by,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit,
            language_code=language_code,
            tenant_id=tenant_id,
        )

        return {
            "runs": [_serialize_suite_run_summary(run) for run in runs],
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Failed to list suite runs: {str(e)}"
    )


def _serialize_suite_run_summary(suite_run: Any) -> Dict[str, Any]:
    """
    Convert a SuiteRun ORM object into the summary structure used by the frontend.
    """
    metadata = getattr(suite_run, "trigger_metadata", {}) or {}
    language_code = (
        metadata.get("language_code")
        or metadata.get("languageCode")
        or metadata.get("language")
        or getattr(suite_run, "_derived_language_code", None)
    )

    def _iso(value: Optional[datetime]) -> Optional[str]:
        return value.isoformat() if value else None

    # Determine suite name - try suite run name, then test_suite name, then category
    suite_name = getattr(suite_run, "name", None)
    if not suite_name:
        test_suite = getattr(suite_run, "test_suite", None)
        if test_suite:
            suite_name = getattr(test_suite, "name", None)

    # Determine if this is a categorical run (no real suite_id, has category_name)
    category_name = getattr(suite_run, "category_name", None)
    is_categorical = bool(category_name and not getattr(suite_run, "suite_id", None))

    return {
        "id": str(suite_run.id),
        "testSuiteId": str(suite_run.suite_id) if getattr(suite_run, "suite_id", None) else None,
        "suite_name": suite_name or category_name,
        "is_categorical": is_categorical,
        "category_name": category_name,
        "status": getattr(suite_run, "status", "pending"),
        "startedAt": _iso(getattr(suite_run, "started_at", None)),
        "completedAt": _iso(getattr(suite_run, "completed_at", None)),
        "createdAt": _iso(getattr(suite_run, "created_at", None)),
        "totalTests": getattr(suite_run, "total_tests", 0) or 0,
        "passedTests": getattr(suite_run, "passed_tests", 0) or 0,
        "failedTests": getattr(suite_run, "failed_tests", 0) or 0,
        "skippedTests": getattr(suite_run, "skipped_tests", 0) or 0,
        "languageCode": language_code,
    }


def _extract_response_entities(execution: Any) -> Dict[str, Any]:
    getter = getattr(execution, "get_all_response_entities", None)
    if callable(getter):
        try:
            result = getter()
            if isinstance(result, dict):
                return dict(result)
        except Exception:
            pass

    entities = getattr(execution, "response_entities", None)
    if isinstance(entities, dict):
        return dict(entities)
    return {}


def _extract_execution_context(execution: Any) -> Dict[str, Any]:
    context = getattr(execution, "context", None)
    if isinstance(context, dict):
        return context
    return {}


def _resolve_execution_language(execution: Any, context: Dict[str, Any]) -> Optional[str]:
    if getattr(execution, "language_code", None):
        return execution.language_code
    for key in ("language_code", "languageCode", "language"):
        value = context.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _derive_response_summary(entities: Dict[str, Any], context: Dict[str, Any]) -> Optional[str]:
    for source in (entities, context):
        for key in ("response_summary", "summary", "transcript", "response", "text", "PromptResponse"):
            value = source.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def _derive_confidence_score(entities: Dict[str, Any]) -> Optional[float]:
    for key in ("confidence", "confidence_score", "confidenceScore"):
        value = entities.get(key)
        if value is None:
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def _calculate_response_time_seconds(execution: Any) -> Optional[float]:
    started = getattr(execution, "started_at", None)
    completed = getattr(execution, "completed_at", None)
    if started and completed:
        try:
            return max((completed - started).total_seconds(), 0.0)
        except Exception:
            return None
    return None


def _build_execution_result_payload(
    execution: Any,
    entities: Dict[str, Any],
    context: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    payload: Dict[str, Any] = {}
    if entities:
        payload["response_entities"] = entities
    if context:
        payload["context"] = context
    audio_params = getattr(execution, "audio_params", None)
    if isinstance(audio_params, dict) and audio_params:
        payload["audio_params"] = audio_params
    return payload or None


def _serialize_step_execution(step: Any) -> Dict[str, Any]:
    """Serialize a StepExecution to API response format."""
    # Get input audio URL from audio_data_urls dict
    input_audio = None
    audio_data_urls = getattr(step, "audio_data_urls", None)
    if isinstance(audio_data_urls, dict):
        # Return first available URL
        for url in audio_data_urls.values():
            input_audio = url
            break

    return {
        "id": str(step.id),
        "step_order": getattr(step, "step_order", 0),
        "user_utterance": getattr(step, "user_utterance", ""),
        "ai_response": getattr(step, "ai_response", None),
        "transcription": getattr(step, "transcription", None),
        "command_kind": getattr(step, "command_kind", None),
        "confidence_score": getattr(step, "confidence_score", None),
        "validation_passed": getattr(step, "validation_passed", None),
        "validation_details": getattr(step, "validation_details", None),
        "response_time_ms": getattr(step, "response_time_ms", None),
        "input_audio_url": input_audio,
        "response_audio_url": getattr(step, "response_audio_url", None),
        "executed_at": step.executed_at.isoformat() if getattr(step, "executed_at", None) else None,
        "error_message": getattr(step, "error_message", None),
    }


def _serialize_validation_details(validation_result: Any) -> Optional[Dict[str, Any]]:
    """Serialize validation result details including Houndify and LLM results."""
    if not validation_result:
        return None

    return {
        "houndifyPassed": getattr(validation_result, "houndify_passed", None),
        "houndifyResult": getattr(validation_result, "houndify_result", None),
        "llmPassed": getattr(validation_result, "llm_passed", None),
        "ensembleResult": getattr(validation_result, "ensemble_result", None),
        "finalDecision": getattr(validation_result, "final_decision", None),
        "reviewStatus": getattr(validation_result, "review_status", None),
    }


# =============================================================================
# Get Suite Run by ID Endpoint
# =============================================================================

@router.get(
    "/{suite_run_id}",
    response_model=SuiteRunResponse,
    response_model_by_alias=True,
    summary="Get suite run",
    description="Get a specific suite run by ID"
)
async def get_suite_run(
    suite_run_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> SuiteRunResponse:
    """
    Get a suite run by ID.

    Args:
        suite_run_id: UUID of the suite run
        db: Database session
        current_user: Current authenticated user

    Returns:
        SuiteRunResponse: Suite run details

    Raises:
        HTTPException: 404 if suite run not found
        HTTPException: 500 if retrieval fails
    """
    try:
        # TODO: Implement get_suite_run in orchestration service
        # For now, return placeholder
        from models.suite_run import SuiteRun
        suite_run = await db.get(SuiteRun, suite_run_id)

        if not suite_run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Suite run with ID {suite_run_id} not found"
            )

        # Verify user has access to this suite run (tenant isolation)
        _check_suite_run_tenant_access(current_user, suite_run)

        return SuiteRunResponse.model_validate(suite_run)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get suite run: {str(e)}"
        )


# =============================================================================
# Cancel Suite Run Endpoint
# =============================================================================

@router.put(
    "/{suite_run_id}/cancel",
    response_model=SuiteRunResponse,
    response_model_by_alias=True,
    summary="Cancel suite run",
    description="Cancel a running suite run"
)
async def cancel_suite_run(
    suite_run_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> SuiteRunResponse:
    """
    Cancel a running suite run.

    Stops all pending/running test executions and marks the suite run
    as canceled.

    Args:
        suite_run_id: UUID of the suite run to cancel
        db: Database session
        current_user: Current authenticated user

    Returns:
        SuiteRunResponse: Updated suite run details

    Raises:
        HTTPException: 404 if suite run not found
        HTTPException: 400 if suite run cannot be canceled
        HTTPException: 500 if cancellation fails
    """
    _ensure_run_controller(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    # qa_lead can only cancel their own executions
    if current_user.role == Role.QA_LEAD.value:
        from models.suite_run import SuiteRun as SuiteRunModel
        from sqlalchemy import select
        result = await db.execute(
            select(SuiteRunModel).where(
                SuiteRunModel.id == suite_run_id,
                SuiteRunModel.tenant_id == tenant_id,
            )
        )
        run = result.scalar_one_or_none()
        if not run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Suite run {suite_run_id} not found"
            )
        if run.created_by and str(run.created_by) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only cancel your own executions.",
            )

    try:
        suite_run = await orchestration_service.cancel_suite_run(
            db=db,
            suite_run_id=suite_run_id,
            tenant_id=tenant_id,
        )

        return SuiteRunResponse.model_validate(suite_run)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel suite run: {str(e)}"
        )


# =============================================================================
# Retry Failed Tests Endpoint
# =============================================================================

@router.post(
    "/{suite_run_id}/retry",
    response_model=SuiteRunResponse,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    summary="Retry failed tests",
    description="Create a new suite run with failed tests from the original run"
)
async def retry_failed_tests(
    suite_run_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> SuiteRunResponse:
    """
    Retry failed tests from a suite run.

    Creates a new suite run containing only the tests that failed
    in the original run.

    Args:
        suite_run_id: UUID of the suite run with failed tests
        db: Database session
        current_user: Current authenticated user

    Returns:
        SuiteRunResponse: New suite run for retrying failed tests

    Raises:
        HTTPException: 404 if suite run not found
        HTTPException: 400 if no failed tests to retry
        HTTPException: 500 if retry fails
    """
    _ensure_run_controller(current_user)
    tenant_id = _get_effective_tenant_id(current_user)
    try:
        retry_run = await orchestration_service.retry_failed_tests(
            db=db,
            suite_run_id=suite_run_id,
            tenant_id=tenant_id,
        )

        return SuiteRunResponse.model_validate(retry_run)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except NotImplementedError as e:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retry failed tests: {str(e)}"
        )


# =============================================================================
# Get Test Executions Endpoint
# =============================================================================

@router.get(
    "/{suite_run_id}/executions",
    response_model=List[TestExecutionResponse],
    summary="Get test executions",
    description="Get all test executions for a suite run"
)
async def get_test_executions(
    suite_run_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
    status_filter: Optional[str] = Query(None, description="Filter by execution status")
) -> List[TestExecutionResponse]:
    """
    Get test executions for a suite run.

    Returns all test executions associated with a specific suite run,
    optionally filtered by status.

    Args:
        suite_run_id: UUID of the suite run
        db: Database session
        current_user: Current authenticated user
        status_filter: Optional filter by execution status

    Returns:
        List[TestExecutionResponse]: List of test executions

    Raises:
        HTTPException: 404 if suite run not found
        HTTPException: 500 if retrieval fails
    """
    try:
        # First fetch the suite run to validate tenant access
        from models.suite_run import SuiteRun
        suite_run = await db.get(SuiteRun, suite_run_id)
        if not suite_run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Suite run with ID {suite_run_id} not found"
            )

        # Verify user has access to this suite run (tenant isolation)
        _check_suite_run_tenant_access(current_user, suite_run)

        executions = await orchestration_service.get_suite_run_executions(
            db=db,
            suite_run_id=suite_run_id,
            status_filter=status_filter,
        )

        serialized = []
        for execution in executions:
            entities = _extract_response_entities(execution)
            context = _extract_execution_context(execution)
            duration = _calculate_response_time_seconds(execution)
            result_payload = _build_execution_result_payload(execution, entities, context)

            # Get script name from related script
            script = getattr(execution, "script", None)
            script_name = getattr(script, "name", None) if script else None

            # Serialize step executions
            step_executions = getattr(execution, "step_executions", None) or []
            serialized_steps = [_serialize_step_execution(step) for step in step_executions]

            # Get validation details (use first validation result for display)
            validation_results = getattr(execution, "validation_results", None) or []
            validation_result = validation_results[0] if validation_results else None
            validation_details = _serialize_validation_details(validation_result)

            # Count completed steps
            total_steps = getattr(execution, "total_steps", len(step_executions))
            completed_steps = len([s for s in step_executions if getattr(s, "executed_at", None)])

            serialized.append(
                TestExecutionResponse(
                    id=execution.id,
                    suite_run_id=execution.suite_run_id,
                    script_id=execution.script_id,
                    script_name=script_name,
                    status=getattr(execution, "status", "pending"),
                    created_at=getattr(execution, "created_at"),
                    updated_at=getattr(execution, "updated_at") or getattr(execution, "completed_at") or getattr(execution, "started_at") or getattr(execution, "created_at"),
                    started_at=getattr(execution, "started_at"),
                    completed_at=getattr(execution, "completed_at"),
                    execution_time=duration,
                    response_time_seconds=duration,
                    result=result_payload,
                    error_message=getattr(execution, "error_message", None),
                    language_code=_resolve_execution_language(execution, context),
                    response_summary=_derive_response_summary(entities, context),
                    confidence_score=_derive_confidence_score(entities),
                    validation_result_id=getattr(validation_result, "id", None) if validation_result else None,
                    validation_review_status=getattr(validation_result, "review_status", None) if validation_result else None,
                    validation_details=validation_details,
                    pending_validation_queue_id=getattr(getattr(execution, "pending_validation_queue_item", None), "id", None),
                    latest_human_validation_id=getattr(getattr(execution, "latest_human_validation", None), "id", None),
                    input_audio_url=getattr(execution, "input_audio_url", None),
                    response_audio_url=getattr(execution, "response_audio_url", None),
                    step_executions=serialized_steps if serialized_steps else None,
                    total_steps=total_steps,
                    completed_steps=completed_steps,
                )
            )

        return serialized

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get test executions: {str(e)}"
        )


# =============================================================================
# GET /api/v1/test-runs/validation-results/{id}
# =============================================================================


@router.get(
    "/validation-results/{validation_result_id}",
    response_model=Dict[str, Any],
    summary="Get validation result details",
    description="Retrieve detailed validation result including all AI-calculated scores"
)
async def get_validation_result(
    validation_result_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> Dict[str, Any]:
    """
    Get validation result details by ID.

    Returns all AI-calculated validation scores including semantic similarity,
    intent match, entity match, accuracy, confidence, and error rates (WER, CER, SER).

    Args:
        validation_result_id: UUID of the validation result
        db: Database session
        current_user: Current authenticated user

    Returns:
        Dict containing:
            - id: ValidationResult UUID
            - All score fields (semantic_similarity, intent_match, entity_match, etc.)
            - review_status: auto_pass, needs_review, or auto_fail
            - ensemble_result: Judge consensus details
            - created_at, updated_at timestamps

    Raises:
        404: Validation result not found
        500: Server error
    """
    from models.validation_result import ValidationResult
    from sqlalchemy import select

    try:
        # Fetch validation result
        stmt = select(ValidationResult).where(ValidationResult.id == validation_result_id)
        result = await db.execute(stmt)
        validation_result = result.scalar_one_or_none()

        if not validation_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Validation result {validation_result_id} not found"
            )

        # Check tenant isolation
        effective_tenant_id = _get_effective_tenant_id(current_user)
        if validation_result.tenant_id is not None and validation_result.tenant_id != effective_tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Validation result belongs to a different tenant.",
            )

        # Convert to dict with all scores including LLM/Houndify fields
        return {
            "id": str(validation_result.id),
            "suite_run_id": str(validation_result.suite_run_id) if validation_result.suite_run_id else None,
            "multi_turn_execution_id": str(validation_result.multi_turn_execution_id) if validation_result.multi_turn_execution_id else None,
            "expected_outcome_id": str(validation_result.expected_outcome_id) if validation_result.expected_outcome_id else None,
            # Core ML scores
            "accuracy_score": validation_result.accuracy_score,
            "confidence_score": validation_result.confidence_score,
            "semantic_similarity_score": validation_result.semantic_similarity_score,
            # Error rate scores
            "wer_score": validation_result.wer_score,
            "cer_score": validation_result.cer_score,
            "ser_score": validation_result.ser_score,
            # Houndify-specific scores
            "command_kind_match_score": validation_result.command_kind_match_score,
            "asr_confidence_score": validation_result.asr_confidence_score,
            # LLM Ensemble validation fields
            "houndify_passed": validation_result.houndify_passed,
            "houndify_result": validation_result.houndify_result,
            "llm_passed": validation_result.llm_passed,
            "ensemble_result": validation_result.ensemble_result,
            "final_decision": validation_result.final_decision,
            "review_status": validation_result.review_status,
            "language_code": validation_result.language_code,
            # Timestamps
            "created_at": validation_result.created_at.isoformat() if validation_result.created_at else None,
            "updated_at": validation_result.updated_at.isoformat() if validation_result.updated_at else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get validation result: {str(e)}"
        )
