"""
Human Validation API routes

Provides endpoints for human validation workflow including queue management,
task claiming, validation submission, and performance tracking.

Endpoints:
    GET /api/v1/validation/queue - Get next validation task from queue
    POST /api/v1/validation/{queue_id}/claim - Claim a validation task
    POST /api/v1/validation/{queue_id}/submit - Submit validation decision
    POST /api/v1/validation/{queue_id}/release - Release a claimed task back to queue
    GET /api/v1/validation/stats - Get validation queue statistics

All endpoints require authentication via JWT token and use Pydantic schemas
for validation and return standard responses.
"""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.dependencies import get_current_user_with_db
from api.schemas.human_validation import (
    HumanValidationSubmit,
)
from api.schemas.responses import SuccessResponse
from api.schemas.auth import UserResponse
from services import validation_queue_service
from services.human_validation_service import HumanValidationService
from services.validator_statistics_service import ValidatorStatisticsService
from api.auth.roles import Role


def _get_effective_tenant_id(user: UserResponse) -> UUID:
    """
    Get effective tenant_id for a user.

    Uses user.tenant_id if set (user belongs to an organization),
    otherwise uses user.id (user is their own tenant).
    """
    return user.tenant_id if user.tenant_id else user.id


# Create router
router = APIRouter(prefix="/validation", tags=["Human Validation"])

# Security scheme for Bearer token
security = HTTPBearer()

_VALIDATION_ROLES = {Role.SUPER_ADMIN.value, Role.ORG_ADMIN.value, Role.QA_LEAD.value, Role.VALIDATOR.value}


def _ensure_can_validate(user: UserResponse) -> None:
    """
    Verify user has permission to perform validation operations.

    Args:
        user: Current authenticated user

    Raises:
        HTTPException: 403 if user lacks required role
    """
    if user.role not in _VALIDATION_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin, org admin, admin, QA lead, or validator role required for validation operations.",
        )


# =============================================================================
# Helper Functions
# =============================================================================

# Use centralized get_current_user_with_db from api.dependencies


# =============================================================================
# Get Next Validation Task Endpoint
# =============================================================================

@router.get(
    "/queue",
    response_model=SuccessResponse,
    summary="Get validation queue",
    description="Retrieve validation tasks from the queue (returns array for frontend compatibility)"
)
async def get_validation_queue(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
    language_code: Optional[str] = Query(
        None,
        description="Optional language code to filter tasks (e.g., 'es-MX', 'fr-FR')"
    ),
    status: Optional[str] = Query(
        None,
        description="Optional status filter (pending, claimed, completed). If 'claimed' or 'completed', returns items for current user."
    ),
    my_items: Optional[bool] = Query(
        None,
        description="If true, return only items claimed by current user (regardless of status)"
    )
) -> SuccessResponse:
    """
    Get validation queue tasks.

    Behavior depends on parameters:
    - No status/my_items: Returns next pending task (single item or empty array)
    - status='pending': Returns next pending task
    - status='claimed' or 'completed': Returns current user's items with that status
    - my_items=true: Returns all items claimed by current user

    Tasks are ordered by:
    - Pending: Priority (ascending, 1 = highest), then creation time (oldest first)
    - Claimed/Completed: Most recently claimed first

    Args:
        db: Database session
        current_user: Current authenticated user (validator)
        language_code: Optional language code for language-specific task routing
        status: Optional status filter
        my_items: If true, return only current user's items

    Returns:
        SuccessResponse: Contains array of ValidationQueueItems

    Raises:
        HTTPException: 401 if authentication fails
    """
    _ensure_can_validate(current_user)

    service = validation_queue_service.ValidationQueueService()

    # If requesting user's own items (claimed or completed)
    if my_items or status in ['claimed', 'completed']:
        tasks = await service.get_validations_by_user(
            db=db,
            validator_id=current_user.id,
            status=status if status in ['claimed', 'completed'] else None,
            language_code=language_code,
            tenant_id=current_user.tenant_id
        )

        # Convert to response schema
        tasks_data = [
            {
                "id": str(task.id),
                "validation_result_id": str(task.validation_result_id),
                "priority": task.priority,
                "confidence_score": float(task.confidence_score) if task.confidence_score else None,
                "language_code": task.language_code,
                "status": task.status,
                "requires_native_speaker": task.requires_native_speaker,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "claimed_by": str(task.claimed_by) if task.claimed_by else None,
                "claimed_at": task.claimed_at.isoformat() if task.claimed_at else None
            }
            for task in tasks
        ]

        return SuccessResponse(
            data=tasks_data,
            message=f"Retrieved {len(tasks_data)} validation items for current user"
        )

    # Otherwise, get next pending task
    task = await service.get_next_validation(
        db=db,
        validator_id=current_user.id,
        language_code=language_code,
        tenant_id=current_user.tenant_id
    )

    if not task:
        return SuccessResponse(
            data=[],
            message="No validation tasks available in queue"
        )

    # Convert to response schema and return as array
    task_data = {
        "id": str(task.id),
        "validation_result_id": str(task.validation_result_id),
        "priority": task.priority,
        "confidence_score": float(task.confidence_score) if task.confidence_score else None,
        "language_code": task.language_code,
        "status": task.status,
        "requires_native_speaker": task.requires_native_speaker,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "claimed_by": str(task.claimed_by) if task.claimed_by else None,
        "claimed_at": task.claimed_at.isoformat() if task.claimed_at else None
    }

    return SuccessResponse(
        data=[task_data],  # Return as array for frontend compatibility
        message="Validation queue retrieved successfully"
    )


# =============================================================================
# Get Queue Statistics Endpoint
# =============================================================================
# NOTE: This must come BEFORE /{queue_id} route to avoid path matching conflicts

@router.get(
    "/stats",
    response_model=SuccessResponse,
    summary="Get validation queue statistics",
    description="Retrieve comprehensive statistics about the validation queue"
)
async def get_queue_statistics(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> SuccessResponse:
    """
    Get comprehensive validation queue statistics.

    Returns statistics including counts by status, priority distribution,
    and language breakdown.

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        SuccessResponse: Dictionary containing queue statistics

    Statistics Include:
        - pending_count: Number of pending tasks
        - claimed_count: Number of claimed tasks
        - completed_count: Number of completed tasks
        - total_count: Total tasks across all statuses
        - priority_distribution: Count of tasks by priority level
        - language_distribution: Count of tasks by language (top 10)
        - throughput: Validation throughput metrics
        - sla: Service level agreement metrics

    Raises:
        HTTPException: 401 if authentication fails
    """
    _ensure_can_validate(current_user)

    # Get queue statistics from service
    service = validation_queue_service.ValidationQueueService()
    stats = await service.get_queue_stats(
        db=db,
        tenant_id=current_user.tenant_id
    )

    # Convert to frontend-expected format (camelCase)
    response_stats = {
        'pendingCount': stats['pending_count'],
        'claimedCount': stats['claimed_count'],
        'completedCount': stats['completed_count'],
        'totalCount': stats['total_count'],
        'priorityDistribution': stats['priority_distribution'],
        'languageDistribution': stats['language_distribution'],
        'throughput': stats['throughput'],
        'sla': stats['sla']
    }

    return SuccessResponse(
        data=response_stats,
        message="Queue statistics retrieved successfully"
    )


# =============================================================================
# Get Specific Validation Item Endpoint
# =============================================================================

@router.get(
    "/{queue_id}",
    response_model=SuccessResponse,
    summary="Get validation item by ID",
    description="Retrieve full validation data for a specific queue item"
)
async def get_validation_item(
    queue_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> SuccessResponse:
    """
    Get full validation data for a specific queue item.

    Retrieves all data needed for the validation interface including test case
    information, expected/actual values, context, and audio URLs.

    Args:
        queue_id: UUID of the queue item
        db: Database session
        current_user: Current authenticated user (validator)

    Returns:
        SuccessResponse: Full validation data

    Raises:
        HTTPException:
            - 401 if authentication fails
            - 403 if user lacks required role
            - 404 if queue item not found
    """
    _ensure_can_validate(current_user)

    service = validation_queue_service.ValidationQueueService()
    validation_data = await service.get_validation_data(
        db=db,
        queue_id=queue_id,
        tenant_id=current_user.tenant_id
    )

    if not validation_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Validation item {queue_id} not found"
        )

    return SuccessResponse(
        data=validation_data,
        message="Validation item retrieved successfully"
    )


# =============================================================================
# Claim Validation Task Endpoint
# =============================================================================

@router.post(
    "/{queue_id}/claim",
    response_model=SuccessResponse,
    summary="Claim validation task",
    description="Claim a validation task to work on it"
)
async def claim_validation_task(
    queue_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> SuccessResponse:
    """
    Claim a validation task for the current validator.

    Marks a pending validation task as claimed by the current validator.
    Only pending tasks can be claimed. Returns full validation data including
    test case information, expected/actual values, and audio URLs.

    Args:
        queue_id: UUID of the queue item to claim
        db: Database session
        current_user: Current authenticated user (validator)

    Returns:
        SuccessResponse: Full validation data for the claimed task

    Raises:
        HTTPException:
            - 401 if authentication fails
            - 403 if user lacks required role
            - 404 if queue item not found
            - 409 if task is not in pending status
    """
    _ensure_can_validate(current_user)

    # Claim the validation task
    service = validation_queue_service.ValidationQueueService()
    success = await service.claim_validation(
        db=db,
        queue_id=queue_id,
        validator_id=current_user.id,
        tenant_id=current_user.tenant_id,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validation task not found or already claimed"
        )

    # Fetch the full validation data
    validation_data = await service.get_validation_data(
        db=db,
        queue_id=queue_id,
        tenant_id=current_user.tenant_id
    )

    if not validation_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validation data not found after claiming"
        )

    return SuccessResponse(
        data=validation_data,
        message=f"Validation task {queue_id} claimed successfully"
    )


# =============================================================================
# Submit Validation Decision Endpoint
# =============================================================================

@router.post(
    "/{queue_id}/submit",
    response_model=SuccessResponse,
    summary="Submit validation decision",
    description="Submit a validation decision for a claimed task"
)
async def submit_validation_decision(
    queue_id: UUID,
    validation_data: HumanValidationSubmit,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> SuccessResponse:
    """
    Submit validation decision for a claimed task.

    Submits the validator's decision (pass/fail/edge_case) along with
    optional feedback and time spent. This completes the validation task.

    Args:
        queue_id: UUID of the queue item being validated
        validation_data: Validation decision and feedback
        db: Database session
        current_user: Current authenticated user (validator)

    Returns:
        SuccessResponse: Confirmation of successful submission

    Raises:
        HTTPException:
            - 401 if authentication fails
            - 403 if user lacks required role or task not claimed by current user
            - 404 if queue item not found
            - 400 if invalid validation decision value
    """
    _ensure_can_validate(current_user)

    # Validate decision value
    valid_decisions = ['pass', 'fail', 'edge_case', 'create_defect']
    if validation_data.validation_decision not in valid_decisions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid validation decision. Must be one of: {', '.join(valid_decisions)}"
        )

    service = HumanValidationService()
    tenant_id = _get_effective_tenant_id(current_user)
    payload = await service.submit_decision(
        db=db,
        queue_id=queue_id,
        validator_id=current_user.id,
        validation_data=validation_data,
        tenant_id=tenant_id,
    )

    return SuccessResponse(
        data=payload,
        message="Validation decision submitted successfully"
    )


# =============================================================================
# Release Validation Task Endpoint
# =============================================================================

@router.post(
    "/{queue_id}/release",
    response_model=SuccessResponse,
    summary="Release validation task",
    description="Release a claimed validation task back to the queue"
)
async def release_validation_task(
    queue_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> SuccessResponse:
    """
    Release a claimed validation task back to the queue.

    Returns a claimed task to pending status, removing the validator
    assignment. Only claimed tasks can be released.

    Args:
        queue_id: UUID of the queue item to release
        db: Database session
        current_user: Current authenticated user (validator)

    Returns:
        SuccessResponse: Confirmation of successful release

    Raises:
        HTTPException:
            - 401 if authentication fails
            - 403 if user lacks required role
            - 404 if queue item not found
            - 409 if task is not in claimed status
    """
    _ensure_can_validate(current_user)

    # Release the validation task
    service = validation_queue_service.ValidationQueueService()
    success = await service.release_validation(
        db=db,
        queue_id=queue_id,
        tenant_id=current_user.tenant_id,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validation task not found or not currently claimed"
        )

    return SuccessResponse(
        data={"queue_id": str(queue_id)},
        message=f"Validation task {queue_id} released back to queue"
    )


# =============================================================================
# Get Grouped Validation Queue Endpoint
# =============================================================================

@router.get(
    "/queue/grouped",
    response_model=SuccessResponse,
    summary="Get grouped validation queue",
    description="Retrieve validation queue items grouped by multi-turn execution"
)
async def get_grouped_validation_queue(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
    status: Optional[str] = Query(
        None,
        description="Optional status filter (pending, claimed, completed)"
    ),
    language_code: Optional[str] = Query(
        None,
        description="Optional language code filter (e.g., 'es', 'fr')"
    ),
    page: int = Query(
        1,
        ge=1,
        description="Page number (1-indexed)"
    ),
    page_size: int = Query(
        20,
        ge=1,
        le=100,
        description="Number of items per page (max 100)"
    )
) -> SuccessResponse:
    """
    Get validation queue items grouped by multi-turn execution.

    Returns validation queue items grouped by their multi_turn_execution_id,
    with aggregate statistics for each execution. This allows validators to
    see all steps from a single execution together, making it easier to
    understand context and review related steps.

    Args:
        db: Database session
        current_user: Current authenticated user
        status: Optional status filter (pending, claimed, completed)
        language_code: Optional language code filter

    Returns:
        SuccessResponse: List of grouped validation queue items

    Response Structure:
        Each group contains:
        - execution_id: UUID of the multi-turn execution
        - scenario_name: Name of the scenario script
        - scenario_id: UUID of the scenario script
        - total_steps: Total number of steps in execution
        - steps_needing_review: Number of steps in validation queue
        - avg_confidence: Average confidence score across all steps
        - min_confidence: Lowest confidence score
        - max_confidence: Highest confidence score
        - status: Overall status (needs_review, in_progress, completed)
        - created_at: When the execution was created
        - step_validations: List of step validation details

    Raises:
        HTTPException: 401 if authentication fails, 403 if user lacks permission
    """
    _ensure_can_validate(current_user)

    # Get grouped validation queue from service
    service = validation_queue_service.ValidationQueueService()

    # If status is claimed or completed, filter by current user
    validator_id = current_user.id if status in ['claimed', 'completed'] else None

    result = await service.get_grouped_validation_queue(
        db=db,
        tenant_id=current_user.tenant_id,
        status=status,
        language_code=language_code,
        validator_id=validator_id,
        page=page,
        page_size=page_size
    )

    return SuccessResponse(
        data=result,
        message=f"Retrieved {len(result['items'])} of {result['total']} grouped validation queue items"
    )


# =============================================================================
# Validator Performance Endpoint
# =============================================================================

@router.get(
    "/validators/stats",
    response_model=SuccessResponse,
    summary="Get validator performance metrics",
    description="Return per-validator performance metrics, leaderboard placeholder, and accuracy trend data"
)
async def get_validator_statistics(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> SuccessResponse:
    """
    Retrieve validator performance metrics for the authenticated user.

    Aggregates total validations, approvals, rejections, average time spent,
    lightweight leaderboard information, and accuracy trends over the past
    30 days to power the validator statistics dashboard.
    """
    display_name = current_user.full_name or current_user.username or current_user.email or "Current Validator"
    service = ValidatorStatisticsService()
    payload = await service.build_validator_statistics(
        db=db,
        validator_id=current_user.id,
        display_name=display_name,
    )

    return SuccessResponse(
        data=payload,
        message="Validator statistics retrieved successfully"
    )
