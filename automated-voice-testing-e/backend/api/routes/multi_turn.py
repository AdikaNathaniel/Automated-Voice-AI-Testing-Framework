"""
Multi-Turn Execution API routes.

Provides endpoints for multi-turn conversation scenario execution including:
- Execute multi-turn scenarios
- Get execution status and results
- Get step-by-step execution details

Endpoints:
    POST /api/v1/multi-turn/execute/{script_id} - Execute a multi-turn scenario
    GET /api/v1/multi-turn/executions/{execution_id} - Get execution status
    GET /api/v1/multi-turn/executions/{execution_id}/steps - Get step-by-step results
    GET /api/v1/multi-turn/executions - List all executions with filters

All endpoints require authentication via JWT token.
"""

from typing import Annotated, Optional, List, Dict, Any
from uuid import UUID
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks, Body
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel, Field

from api.database import get_db
from api.dependencies import get_current_user_with_db
from api.schemas.auth import UserResponse
from api.schemas.responses import SuccessResponse, PaginatedResponse
from models.multi_turn_execution import MultiTurnExecution, StepExecution
from models.scenario_script import ScenarioScript
from models.suite_run import SuiteRun
from services.multi_turn_execution_service import MultiTurnExecutionService
from api.websocket import sio
from api.auth.roles import Role

# Create router
router = APIRouter(prefix="/multi-turn", tags=["Multi-Turn Execution"])

# Security scheme for Bearer token
security = HTTPBearer()

# Logger
logger = logging.getLogger(__name__)

# Roles that can approve/reject scenarios
_APPROVAL_ROLES = {Role.SUPER_ADMIN.value, Role.ORG_ADMIN.value, Role.QA_LEAD.value}


def _get_effective_tenant_id(user: UserResponse) -> UUID:
    """
    Get effective tenant_id for a user.

    Uses user.tenant_id if set (user belongs to an organization),
    otherwise uses user.id (user is their own tenant).

    This ensures tenant_id is NEVER None for data isolation.
    """
    return user.tenant_id if user.tenant_id else user.id


# =============================================================================
# Request/Response Schemas
# =============================================================================

class ExecuteScenarioRequest(BaseModel):
    """Request model for executing a scenario."""
    language_codes: Optional[List[str]] = Field(
        None,
        description="Optional list of language codes to execute. If omitted, executes all language variants. "
                    "Examples: ['en-US'], ['fr-FR'], ['en-US', 'fr-FR']"
    )
    suite_run_id: Optional[UUID] = Field(
        None,
        description="Optional suite run ID to associate execution with. If omitted, scenario runs standalone."
    )


def _ensure_can_review_scenario(
    user: UserResponse,
    scenario: ScenarioScript
) -> None:
    """
    Verify user has permission to review (approve/reject) a scenario.

    Rules:
    - User must have ADMIN or QA_LEAD role
    - User cannot approve their own scenario UNLESS they are ADMIN

    Args:
        user: Current authenticated user
        scenario: The scenario being reviewed

    Raises:
        HTTPException: 403 if user lacks permission
    """
    # Check role first
    if user.role not in _APPROVAL_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or QA Lead role required to approve/reject scenarios."
        )

    # Prevent self-approval unless user is ADMIN
    if user.role not in {Role.SUPER_ADMIN.value, Role.ORG_ADMIN.value}:
        if scenario.created_by and str(scenario.created_by) == str(user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot approve/reject your own scenario. Only admins can self-approve."
            )


# =============================================================================
# Scenario Management Endpoints
# =============================================================================

@router.get(
    "/scenarios",
    response_model=SuccessResponse,
    summary="List scenarios",
    description="List all scenario scripts with optional filters"
)
async def list_scenarios(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    approval_status: Optional[str] = Query(None, description="Filter by approval status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> SuccessResponse:
    """
    List scenario scripts with pagination and filters.

    Args:
        is_active: Optional filter by active status
        approval_status: Optional filter by approval status
        page: Page number (1-based)
        page_size: Items per page
        db: Database session
        current_user: Authenticated user

    Returns:
        List of scenarios with pagination info
    """
    from sqlalchemy import select, func
    from sqlalchemy.orm import selectinload
    from models.scenario_script import ScenarioScript

    # Build query with tenant filtering
    tenant_id = _get_effective_tenant_id(current_user)
    query = select(ScenarioScript).options(selectinload(ScenarioScript.steps)).where(
        ScenarioScript.tenant_id == tenant_id
    )

    if is_active is not None:
        query = query.where(ScenarioScript.is_active == is_active)
    if approval_status:
        query = query.where(ScenarioScript.approval_status == approval_status)

    # Order by most recent first
    query = query.order_by(desc(ScenarioScript.created_at))

    # Get total count (with tenant filtering)
    count_query = select(func.count()).select_from(ScenarioScript).where(
        ScenarioScript.tenant_id == tenant_id
    )
    if is_active is not None:
        count_query = count_query.where(ScenarioScript.is_active == is_active)
    if approval_status:
        count_query = count_query.where(ScenarioScript.approval_status == approval_status)

    count_result = await db.execute(count_query)
    total_items = count_result.scalar()

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    # Execute query
    result = await db.execute(query)
    scenarios = result.scalars().all()

    def extract_languages(scenario: ScenarioScript) -> List[str]:
        """Extract unique language codes from scenario steps."""
        languages_set = set()
        for step in scenario.steps:
            if step.step_metadata:
                # Check for language_variants array
                variants = step.step_metadata.get('language_variants', [])
                for variant in variants:
                    if isinstance(variant, dict) and 'language_code' in variant:
                        languages_set.add(variant['language_code'])
                # Check for primary_language
                primary = step.step_metadata.get('primary_language')
                if primary:
                    languages_set.add(primary)
        return sorted(list(languages_set)) if languages_set else []

    scenarios_data = [
        {
            "id": str(scenario.id),
            "name": scenario.name,
            "description": scenario.description,
            "version": scenario.version,
            "is_active": scenario.is_active,
            "validation_mode": scenario.validation_mode,
            "approval_status": scenario.approval_status,
            "script_metadata": scenario.script_metadata,
            "created_by": str(scenario.created_by) if scenario.created_by else None,
            "owner_id": str(scenario.owner_id) if scenario.owner_id else None,
            "reviewed_by": str(scenario.reviewed_by) if scenario.reviewed_by else None,
            "reviewed_at": scenario.reviewed_at.isoformat() if scenario.reviewed_at else None,
            "review_notes": scenario.review_notes,
            "steps_count": len(scenario.steps),
            "languages": extract_languages(scenario),
            "created_at": scenario.created_at.isoformat() if scenario.created_at else None,
            "updated_at": scenario.updated_at.isoformat() if scenario.updated_at else None
        }
        for scenario in scenarios
    ]

    return SuccessResponse(
        data={
            "scenarios": scenarios_data,
            "total": total_items,
            "page": page,
            "page_size": page_size
        }
    )


@router.get(
    "/scenarios/{script_id}",
    response_model=SuccessResponse,
    summary="Get scenario details",
    description="Get detailed information about a specific scenario including all steps"
)
async def get_scenario(
    script_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> SuccessResponse:
    """
    Get detailed scenario information including all steps and expected outcomes.

    Args:
        script_id: Scenario script ID
        db: Database session
        current_user: Authenticated user

    Returns:
        Detailed scenario information
    """
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from models.scenario_script import ScenarioScript, ScenarioStep

    # Query scenario with steps and expected outcomes (with tenant filtering)
    tenant_id = _get_effective_tenant_id(current_user)
    query = select(ScenarioScript).where(
        ScenarioScript.id == script_id,
        ScenarioScript.tenant_id == tenant_id
    ).options(
        selectinload(ScenarioScript.steps).selectinload(ScenarioStep.expected_outcomes)
    )

    result = await db.execute(query)
    scenario = result.scalar_one_or_none()

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario {script_id} not found"
        )

    # Build steps data with expected outcomes
    steps_data = []
    for step in scenario.steps:
        expected_outcomes_data = [
            {
                "id": str(outcome.id),
                "outcome_code": outcome.outcome_code,
                "name": outcome.name,
                "description": outcome.description,
                "expected_command_kind": outcome.expected_command_kind,
                "expected_asr_confidence_min": outcome.expected_asr_confidence_min,
                "expected_response_content": outcome.expected_response_content,
                "entities": outcome.entities,
                "validation_rules": outcome.validation_rules
            }
            for outcome in step.expected_outcomes
        ]

        steps_data.append({
            "id": str(step.id),
            "step_order": step.step_order,
            "user_utterance": step.user_utterance,
            "step_metadata": step.step_metadata,
            "follow_up_action": step.follow_up_action,
            "expected_outcomes": expected_outcomes_data
        })

    return SuccessResponse(
        data={
            "id": str(scenario.id),
            "name": scenario.name,
            "description": scenario.description,
            "version": scenario.version,
            "is_active": scenario.is_active,
            "validation_mode": scenario.validation_mode,
            "approval_status": scenario.approval_status,
            "script_metadata": scenario.script_metadata,
            "created_by": str(scenario.created_by) if scenario.created_by else None,
            "owner_id": str(scenario.owner_id) if scenario.owner_id else None,
            "reviewed_by": str(scenario.reviewed_by) if scenario.reviewed_by else None,
            "reviewed_at": scenario.reviewed_at.isoformat() if scenario.reviewed_at else None,
            "review_notes": scenario.review_notes,
            "steps": steps_data,
            "created_at": scenario.created_at.isoformat() if scenario.created_at else None,
            "updated_at": scenario.updated_at.isoformat() if scenario.updated_at else None
        }
    )


@router.post(
    "/scenarios",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create scenario",
    description="Create a new scenario script with steps and expected outcomes"
)
async def create_scenario(
    scenario_data: Dict[str, Any],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> SuccessResponse:
    """
    Create a new scenario script with steps and expected outcomes.

    Args:
        scenario_data: Scenario data including name, description, steps, etc.
        db: Database session
        current_user: Authenticated user

    Returns:
        Created scenario with ID
    """
    from models.scenario_script import ScenarioScript, ScenarioStep
    from models.expected_outcome import ExpectedOutcome

    try:
        # Validate required fields
        if not scenario_data.get("name", "").strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Scenario name is required"
            )

        if not scenario_data.get("version", "").strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Scenario version is required"
            )

        # Validate steps
        steps_data = scenario_data.get("steps", [])
        if not steps_data or len(steps_data) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one step is required"
            )

        # Validate each step has required fields
        for i, step_data in enumerate(steps_data):
            if not step_data.get("user_utterance", "").strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Step {i + 1}: User utterance is required"
                )
        # Create scenario with tenant_id
        tenant_id = _get_effective_tenant_id(current_user)
        logger.info(f"[SCENARIO] Creating scenario with user_id type: {type(current_user.id)}, value: {current_user.id}")
        scenario = ScenarioScript(
            name=scenario_data.get("name"),
            description=scenario_data.get("description"),
            version=scenario_data.get("version", "1.0.0"),
            is_active=scenario_data.get("is_active", True),
            validation_mode=scenario_data.get("validation_mode", "hybrid"),
            script_metadata=scenario_data.get("script_metadata", {}),
            created_by=current_user.id,
            owner_id=current_user.id,
            tenant_id=tenant_id,
            approval_status=scenario_data.get("approval_status", "draft")
        )
        logger.info(f"[SCENARIO] Scenario object created successfully")

        db.add(scenario)
        logger.info(f"[SCENARIO] Scenario added to session")
        await db.flush()  # Get scenario ID
        logger.info(f"[SCENARIO] Scenario flushed, ID: {scenario.id}")
        for step_data in steps_data:
            step = ScenarioStep(
                script_id=scenario.id,
                step_order=step_data.get("step_order"),
                user_utterance=step_data.get("user_utterance"),
                step_metadata=step_data.get("step_metadata", {}),
                follow_up_action=step_data.get("follow_up_action")
            )
            db.add(step)
            await db.flush()  # Get step ID

            # Create expected outcomes for this step
            outcomes_data = step_data.get("expected_outcomes", [])
            for outcome_data in outcomes_data:
                outcome = ExpectedOutcome(
                    tenant_id=tenant_id,
                    scenario_step_id=step.id,
                    outcome_code=outcome_data.get("outcome_code", f"outcome_{step.id}_{len(outcomes_data)}"),
                    name=outcome_data.get("name", "Expected Outcome"),
                    description=outcome_data.get("description"),
                    expected_command_kind=outcome_data.get("expected_command_kind"),
                    expected_asr_confidence_min=outcome_data.get("expected_asr_confidence_min", 0.7),
                    expected_response_content=outcome_data.get("expected_response_content"),
                    entities=outcome_data.get("entities", {}),
                    validation_rules=outcome_data.get("validation_rules", {})
                )
                db.add(outcome)

        await db.commit()
        await db.refresh(scenario)

        logger.info(f"[SCENARIO] Created scenario {scenario.id}: {scenario.name}")

        return SuccessResponse(
            data={
                "id": str(scenario.id),
                "name": scenario.name,
                "description": scenario.description,
                "version": scenario.version,
                "approval_status": scenario.approval_status,
                "created_at": scenario.created_at.isoformat() if scenario.created_at else None
            }
        )

    except Exception as e:
        await db.rollback()
        import traceback
        logger.error(f"[SCENARIO] Failed to create scenario: {str(e)}")
        logger.error(f"[SCENARIO] Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create scenario: {str(e)}"
        )


@router.put(
    "/scenarios/{script_id}",
    response_model=SuccessResponse,
    summary="Update scenario",
    description="Update an existing scenario script"
)
async def update_scenario(
    script_id: UUID,
    scenario_data: Dict[str, Any],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> SuccessResponse:
    """
    Update an existing scenario script.

    Args:
        script_id: Scenario script ID
        scenario_data: Updated scenario data
        db: Database session
        current_user: Authenticated user

    Returns:
        Updated scenario information
    """
    from sqlalchemy import select
    from models.scenario_script import ScenarioScript

    # Get existing scenario (with tenant filtering)
    tenant_id = _get_effective_tenant_id(current_user)
    query = select(ScenarioScript).where(
        ScenarioScript.id == script_id,
        ScenarioScript.tenant_id == tenant_id
    )
    result = await db.execute(query)
    scenario = result.scalar_one_or_none()

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario {script_id} not found"
        )

    try:
        # Update metadata fields
        if "name" in scenario_data:
            scenario.name = scenario_data["name"]
        if "description" in scenario_data:
            scenario.description = scenario_data["description"]
        if "version" in scenario_data:
            scenario.version = scenario_data["version"]
        if "is_active" in scenario_data:
            scenario.is_active = scenario_data["is_active"]
        if "validation_mode" in scenario_data:
            scenario.validation_mode = scenario_data["validation_mode"]
        if "script_metadata" in scenario_data:
            scenario.script_metadata = scenario_data["script_metadata"]
        if "approval_status" in scenario_data:
            scenario.approval_status = scenario_data["approval_status"]

        # Handle steps update if provided
        if "steps" in scenario_data:
            from sqlalchemy.orm import selectinload
            from models.scenario_script import ScenarioStep
            from models.expected_outcome import ExpectedOutcome

            # Reload scenario with steps and expected outcomes
            query = select(ScenarioScript).where(ScenarioScript.id == script_id).options(
                selectinload(ScenarioScript.steps).selectinload(ScenarioStep.expected_outcomes)
            )
            result = await db.execute(query)
            scenario = result.scalar_one()

            # Get existing step IDs
            existing_step_ids = {str(step.id) for step in scenario.steps}
            incoming_step_ids = {
                step_data.get("id") for step_data in scenario_data["steps"]
                if step_data.get("id")
            }

            # Delete steps that are no longer in the payload
            for step in list(scenario.steps):
                if str(step.id) not in incoming_step_ids:
                    for outcome in list(step.expected_outcomes):
                        await db.delete(outcome)
                    await db.delete(step)

            # Update or create steps
            for step_data in scenario_data["steps"]:
                step_id = step_data.get("id")

                if step_id and step_id in existing_step_ids:
                    # Update existing step
                    existing_step = next(
                        (s for s in scenario.steps if str(s.id) == step_id), None
                    )
                    if existing_step:
                        existing_step.step_order = step_data.get(
                            "step_order", existing_step.step_order
                        )
                        existing_step.user_utterance = step_data.get(
                            "user_utterance", existing_step.user_utterance
                        )
                        existing_step.step_metadata = step_data.get(
                            "step_metadata", existing_step.step_metadata
                        )
                        existing_step.follow_up_action = step_data.get(
                            "follow_up_action", existing_step.follow_up_action
                        )

                        # Handle expected outcomes for this step
                        if "expected_outcomes" in step_data:
                            existing_outcome_ids = {
                                str(o.id) for o in existing_step.expected_outcomes
                            }
                            incoming_outcome_ids = {
                                o.get("id") for o in step_data["expected_outcomes"]
                                if o.get("id")
                            }

                            # Delete outcomes no longer in payload
                            for outcome in list(existing_step.expected_outcomes):
                                if str(outcome.id) not in incoming_outcome_ids:
                                    await db.delete(outcome)

                            # Update or create outcomes
                            for outcome_data in step_data["expected_outcomes"]:
                                outcome_id = outcome_data.get("id")
                                if outcome_id and outcome_id in existing_outcome_ids:
                                    existing_outcome = next(
                                        (o for o in existing_step.expected_outcomes
                                         if str(o.id) == outcome_id), None
                                    )
                                    if existing_outcome:
                                        existing_outcome.outcome_code = outcome_data.get(
                                            "outcome_code", existing_outcome.outcome_code
                                        )
                                        existing_outcome.name = outcome_data.get(
                                            "name", existing_outcome.name
                                        )
                                        existing_outcome.description = outcome_data.get(
                                            "description", existing_outcome.description
                                        )
                                        existing_outcome.expected_command_kind = outcome_data.get(
                                            "expected_command_kind",
                                            existing_outcome.expected_command_kind
                                        )
                                        existing_outcome.expected_asr_confidence_min = outcome_data.get(
                                            "expected_asr_confidence_min",
                                            existing_outcome.expected_asr_confidence_min
                                        )
                                        existing_outcome.expected_response_content = outcome_data.get(
                                            "expected_response_content",
                                            existing_outcome.expected_response_content
                                        )
                                        existing_outcome.entities = outcome_data.get(
                                            "entities",
                                            existing_outcome.entities
                                        )
                                        existing_outcome.validation_rules = outcome_data.get(
                                            "validation_rules",
                                            existing_outcome.validation_rules
                                        )
                                else:
                                    # Create new outcome
                                    new_outcome = ExpectedOutcome(
                                        tenant_id=tenant_id,
                                        scenario_step_id=existing_step.id,
                                        outcome_code=outcome_data.get(
                                            "outcome_code",
                                            f"outcome_{existing_step.step_order}"
                                        ),
                                        name=outcome_data.get("name"),
                                        description=outcome_data.get("description"),
                                        expected_command_kind=outcome_data.get(
                                            "expected_command_kind"
                                        ),
                                        expected_asr_confidence_min=outcome_data.get(
                                            "expected_asr_confidence_min"
                                        ),
                                        expected_response_content=outcome_data.get(
                                            "expected_response_content"
                                        ),
                                        entities=outcome_data.get(
                                            "entities", {}
                                        ),
                                        validation_rules=outcome_data.get(
                                            "validation_rules", {}
                                        ),
                                    )
                                    db.add(new_outcome)
                else:
                    # Create new step
                    new_step = ScenarioStep(
                        script_id=scenario.id,
                        step_order=step_data.get("step_order", 1),
                        user_utterance=step_data.get("user_utterance", ""),
                        step_metadata=step_data.get("step_metadata", {}),
                        follow_up_action=step_data.get("follow_up_action"),
                    )
                    db.add(new_step)
                    await db.flush()  # Get the new step ID

                    # Create expected outcomes for new step
                    for outcome_data in step_data.get("expected_outcomes", []):
                        new_outcome = ExpectedOutcome(
                            tenant_id=tenant_id,
                            scenario_step_id=new_step.id,
                            outcome_code=outcome_data.get(
                                "outcome_code", f"outcome_{new_step.step_order}"
                            ),
                            name=outcome_data.get("name"),
                            description=outcome_data.get("description"),
                            expected_command_kind=outcome_data.get("expected_command_kind"),
                            expected_asr_confidence_min=outcome_data.get(
                                "expected_asr_confidence_min"
                            ),
                            expected_response_content=outcome_data.get(
                                "expected_response_content"
                            ),
                            entities=outcome_data.get("entities", {}),
                            validation_rules=outcome_data.get("validation_rules", {}),
                        )
                        db.add(new_outcome)

        await db.commit()
        await db.refresh(scenario)

        logger.info(f"[SCENARIO] Updated scenario {scenario.id}: {scenario.name}")

        return SuccessResponse(
            data={
                "id": str(scenario.id),
                "name": scenario.name,
                "description": scenario.description,
                "version": scenario.version,
                "is_active": scenario.is_active,
                "approval_status": scenario.approval_status,
                "updated_at": scenario.updated_at.isoformat() if scenario.updated_at else None
            }
        )

    except Exception as e:
        await db.rollback()
        logger.error(f"[SCENARIO] Failed to update scenario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update scenario: {str(e)}"
        )


@router.delete(
    "/scenarios/{script_id}",
    response_model=SuccessResponse,
    summary="Delete scenario",
    description="Delete a scenario script and all its steps"
)
async def delete_scenario(
    script_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> SuccessResponse:
    """
    Delete a scenario script and all its steps.

    Properly handles cascade deletion of related records:
    1. Delete step_executions referencing scenario steps
    2. Delete expected_outcomes referencing scenario steps
    3. Delete the scenario (cascades to steps)

    Args:
        script_id: Scenario script ID
        db: Database session
        current_user: Authenticated user

    Returns:
        Success confirmation
    """
    from sqlalchemy import select, delete
    from models.scenario_script import ScenarioScript, ScenarioStep
    from models.multi_turn_execution import StepExecution
    from models.expected_outcome import ExpectedOutcome

    # Get existing scenario (with tenant filtering)
    tenant_id = _get_effective_tenant_id(current_user)
    query = select(ScenarioScript).where(
        ScenarioScript.id == script_id,
        ScenarioScript.tenant_id == tenant_id
    )
    result = await db.execute(query)
    scenario = result.scalar_one_or_none()

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario {script_id} not found"
        )

    try:
        scenario_name = scenario.name

        # Get all step IDs for this scenario
        step_query = select(ScenarioStep.id).where(
            ScenarioStep.script_id == script_id
        )
        step_result = await db.execute(step_query)
        step_ids = [row[0] for row in step_result.fetchall()]

        if step_ids:
            # 1. Delete step_executions referencing these steps
            await db.execute(
                delete(StepExecution).where(
                    StepExecution.step_id.in_(step_ids)
                )
            )
            logger.debug(f"[SCENARIO] Deleted step_executions for {len(step_ids)} steps")

            # 2. Delete expected_outcomes referencing these steps
            await db.execute(
                delete(ExpectedOutcome).where(
                    ExpectedOutcome.scenario_step_id.in_(step_ids)
                )
            )
            logger.debug(f"[SCENARIO] Deleted expected_outcomes for {len(step_ids)} steps")

        # 3. Delete the scenario (cascades to steps)
        await db.delete(scenario)
        await db.commit()

        logger.info(f"[SCENARIO] Deleted scenario {script_id}: {scenario_name}")

        return SuccessResponse(
            data={
                "id": str(script_id),
                "name": scenario_name,
                "deleted": True
            }
        )

    except Exception as e:
        await db.rollback()
        logger.error(f"[SCENARIO] Failed to delete scenario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete scenario: {str(e)}"
        )


@router.post(
    "/scenarios/{script_id}/submit-for-review",
    response_model=SuccessResponse,
    summary="Submit scenario for review",
    description="Submit a scenario for approval review"
)
async def submit_scenario_for_review(
    script_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> SuccessResponse:
    """
    Submit a scenario for approval review.

    Args:
        script_id: Scenario script ID
        db: Database session
        current_user: Authenticated user

    Returns:
        Updated scenario status
    """
    from sqlalchemy import select
    from models.scenario_script import ScenarioScript

    # Get scenario with tenant filtering
    tenant_id = _get_effective_tenant_id(current_user)
    query = select(ScenarioScript).where(
        ScenarioScript.id == script_id,
        ScenarioScript.tenant_id == tenant_id
    )
    result = await db.execute(query)
    scenario = result.scalar_one_or_none()

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario {script_id} not found"
        )

    try:
        scenario.submit_for_review()
        await db.commit()

        logger.info(f"[SCENARIO] Submitted scenario {script_id} for review")

        return SuccessResponse(
            data={
                "id": str(scenario.id),
                "name": scenario.name,
                "approval_status": scenario.approval_status
            }
        )

    except Exception as e:
        await db.rollback()
        logger.error(f"[SCENARIO] Failed to submit scenario for review: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit scenario for review: {str(e)}"
        )


@router.post(
    "/scenarios/{script_id}/approve",
    response_model=SuccessResponse,
    summary="Approve scenario",
    description="Approve a scenario for use in testing"
)
async def approve_scenario(
    script_id: UUID,
    approval_data: Dict[str, Any],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> SuccessResponse:
    """
    Approve a scenario for use in testing.

    Requires ADMIN or QA_LEAD role. QA_LEAD cannot approve their own scenarios.

    Args:
        script_id: Scenario script ID
        approval_data: Approval notes
        db: Database session
        current_user: Authenticated user

    Returns:
        Updated scenario status

    Raises:
        HTTPException: 403 if user lacks permission or tries to self-approve
        HTTPException: 404 if scenario not found
    """
    from sqlalchemy import select
    from models.scenario_script import ScenarioScript

    # Get scenario with tenant filtering
    tenant_id = _get_effective_tenant_id(current_user)
    query = select(ScenarioScript).where(
        ScenarioScript.id == script_id,
        ScenarioScript.tenant_id == tenant_id
    )
    result = await db.execute(query)
    scenario = result.scalar_one_or_none()

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario {script_id} not found"
        )

    # Check permission to review
    _ensure_can_review_scenario(current_user, scenario)

    try:
        notes = approval_data.get("notes") or approval_data.get("review_notes")
        scenario.approve(reviewer_id=current_user.id, notes=notes)
        await db.commit()

        logger.info(f"[SCENARIO] Approved scenario {script_id} by user {current_user.id}")

        return SuccessResponse(
            data={
                "id": str(scenario.id),
                "name": scenario.name,
                "approval_status": scenario.approval_status,
                "reviewed_by": str(scenario.reviewed_by) if scenario.reviewed_by else None,
                "reviewed_at": scenario.reviewed_at.isoformat() if scenario.reviewed_at else None,
                "review_notes": scenario.review_notes
            }
        )

    except Exception as e:
        await db.rollback()
        logger.error(f"[SCENARIO] Failed to approve scenario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve scenario: {str(e)}"
        )


@router.post(
    "/scenarios/{script_id}/reject",
    response_model=SuccessResponse,
    summary="Reject scenario",
    description="Reject a scenario with feedback"
)
async def reject_scenario(
    script_id: UUID,
    rejection_data: Dict[str, Any],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> SuccessResponse:
    """
    Reject a scenario with feedback.

    Requires ADMIN or QA_LEAD role. QA_LEAD cannot reject their own scenarios.

    Args:
        script_id: Scenario script ID
        rejection_data: Rejection notes (required)
        db: Database session
        current_user: Authenticated user

    Returns:
        Updated scenario status

    Raises:
        HTTPException: 403 if user lacks permission or tries to self-reject
        HTTPException: 404 if scenario not found
    """
    from sqlalchemy import select
    from models.scenario_script import ScenarioScript

    # Get scenario with tenant filtering
    tenant_id = _get_effective_tenant_id(current_user)
    query = select(ScenarioScript).where(
        ScenarioScript.id == script_id,
        ScenarioScript.tenant_id == tenant_id
    )
    result = await db.execute(query)
    scenario = result.scalar_one_or_none()

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario {script_id} not found"
        )

    # Check permission to review
    _ensure_can_review_scenario(current_user, scenario)

    notes = rejection_data.get("notes") or rejection_data.get("review_notes")
    if not notes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rejection notes are required"
        )

    try:
        scenario.reject(reviewer_id=current_user.id, notes=notes)
        await db.commit()

        logger.info(f"[SCENARIO] Rejected scenario {script_id} by user {current_user.id}")

        return SuccessResponse(
            data={
                "id": str(scenario.id),
                "name": scenario.name,
                "approval_status": scenario.approval_status,
                "reviewed_by": str(scenario.reviewed_by) if scenario.reviewed_by else None,
                "reviewed_at": scenario.reviewed_at.isoformat() if scenario.reviewed_at else None,
                "review_notes": scenario.review_notes
            }
        )

    except Exception as e:
        await db.rollback()
        logger.error(f"[SCENARIO] Failed to reject scenario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject scenario: {str(e)}"
        )


# =============================================================================
# Multi-Turn Execution Endpoints
# =============================================================================

@router.post(
    "/execute/{script_id}",
    response_model=SuccessResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Execute multi-turn scenario",
    description="Execute a multi-turn conversation scenario with optional language filtering"
)
async def execute_multi_turn_scenario(
    script_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
    background_tasks: BackgroundTasks,
    request_body: ExecuteScenarioRequest = Body(default=ExecuteScenarioRequest()),
) -> SuccessResponse:
    """
    Execute a multi-turn conversation scenario.

    Args:
        script_id: ID of the scenario script to execute
        request_body: Request body with language_codes and suite_run_id
        db: Database session
        current_user: Authenticated user
        background_tasks: FastAPI background tasks

    Returns:
        Execution ID and initial status

    Raises:
        HTTPException: 404 if scenario not found
    """
    suite_run_id = request_body.suite_run_id
    language_codes = request_body.language_codes
    tenant_id = _get_effective_tenant_id(current_user)

    # Verify scenario exists (with tenant filtering)
    result = await db.execute(select(ScenarioScript).where(
        ScenarioScript.id == script_id,
        ScenarioScript.tenant_id == tenant_id
    ))
    script = result.scalar_one_or_none()

    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario script {script_id} not found"
        )

    # suite_run_id is optional for standalone scenario execution

    # Execute scenario synchronously for now (can be moved to Celery later)
    service = MultiTurnExecutionService()

    try:
        execution = await service.execute_scenario(
            db=db,
            script_id=script_id,
            suite_run_id=suite_run_id,
            tenant_id=tenant_id,
            socketio=sio,
            language_codes=language_codes
        )

        # execution is a MultiTurnExecution object, access attributes directly
        return SuccessResponse(
            data={
                "script_id": str(script_id),
                "suite_run_id": str(suite_run_id),
                "execution_id": str(execution.id),
                "status": execution.status,
                "total_steps": execution.total_steps,
                "completed_steps": execution.current_step_order,
                "all_passed": execution.status == "completed"
            },
            message="Multi-turn scenario execution completed"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Execution failed: {str(e)}"
        )


@router.get(
    "/executions/{execution_id}",
    response_model=SuccessResponse,
    summary="Get execution status",
    description="Get the status and results of a multi-turn execution"
)
async def get_execution_status(
    execution_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> SuccessResponse:
    """
    Get multi-turn execution status and results.

    Args:
        execution_id: ID of the execution
        db: Database session
        current_user: Authenticated user

    Returns:
        Execution details including status, steps, and results

    Raises:
        HTTPException: 404 if execution not found
    """
    # Filter by tenant
    tenant_id = _get_effective_tenant_id(current_user)
    result = await db.execute(
        select(MultiTurnExecution).where(
            MultiTurnExecution.id == execution_id,
            MultiTurnExecution.tenant_id == tenant_id
        )
    )
    execution = result.scalar_one_or_none()

    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution {execution_id} not found"
        )

    return SuccessResponse(
        data={
            "id": str(execution.id),
            "suite_run_id": str(execution.suite_run_id),
            "script_id": str(execution.script_id),
            "user_id": execution.user_id,
            "conversation_state_id": execution.conversation_state_id,
            "current_step_order": execution.current_step_order,
            "total_steps": execution.total_steps,
            "status": execution.status,
            "started_at": execution.started_at.isoformat() if execution.started_at else None,
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "error_message": execution.error_message,
            "conversation_state": execution.conversation_state
        }
    )


@router.get(
    "/executions/{execution_id}/steps",
    response_model=SuccessResponse,
    summary="Get execution steps",
    description="Get step-by-step execution details for a multi-turn execution"
)
async def get_execution_steps(
    execution_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> SuccessResponse:
    """
    Get step-by-step execution details.

    Args:
        execution_id: ID of the execution
        db: Database session
        current_user: Authenticated user

    Returns:
        List of step executions with validation results

    Raises:
        HTTPException: 404 if execution not found
    """
    # Verify execution exists (with tenant filtering)
    tenant_id = _get_effective_tenant_id(current_user)
    result = await db.execute(
        select(MultiTurnExecution).where(
            MultiTurnExecution.id == execution_id,
            MultiTurnExecution.tenant_id == tenant_id
        )
    )
    execution = result.scalar_one_or_none()

    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution {execution_id} not found"
        )

    # Get all steps for this execution
    result = await db.execute(
        select(StepExecution)
        .where(StepExecution.multi_turn_execution_id == execution_id)
        .order_by(StepExecution.step_order)
    )
    steps = result.scalars().all()

    steps_data = [
        {
            "id": str(step.id),
            "step_id": str(step.step_id),
            "step_order": step.step_order,
            "user_utterance": step.user_utterance,
            "audio_data_urls": step.audio_data_urls,  # JSONB map of language codes to input audio URLs
            "response_audio_urls": step.response_audio_urls,  # JSONB map of language codes to response audio URLs
            "request_id": step.request_id,
            "ai_response": step.ai_response,
            "transcription": step.transcription,
            "command_kind": step.command_kind,
            "confidence_score": step.confidence_score,
            "conversation_state_before": step.conversation_state_before,
            "conversation_state_after": step.conversation_state_after,
            "validation_passed": step.validation_passed,
            "validation_details": step.validation_details,
            "response_time_ms": step.response_time_ms,
            "executed_at": step.executed_at.isoformat() if step.executed_at else None,
            "error_message": step.error_message
        }
        for step in steps
    ]

    return SuccessResponse(
        data={
            "execution_id": str(execution_id),
            "total_steps": len(steps_data),
            "steps": steps_data
        }
    )


@router.get(
    "/executions",
    response_model=PaginatedResponse,
    summary="List executions",
    description="List all multi-turn executions with optional filters"
)
async def list_executions(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
    suite_run_id: Optional[UUID] = Query(None, description="Filter by suite run ID"),
    script_id: Optional[UUID] = Query(None, description="Filter by script ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> PaginatedResponse:
    """
    List multi-turn executions with pagination and filters.

    Args:
        suite_run_id: Optional filter by suite run ID
        script_id: Optional filter by script ID
        status: Optional filter by status
        page: Page number (1-based)
        page_size: Items per page
        db: Database session
        current_user: Authenticated user

    Returns:
        Paginated list of executions
    """
    from sqlalchemy.orm import selectinload

    # Build query with script relationship (with tenant filtering)
    tenant_id = _get_effective_tenant_id(current_user)
    query = select(MultiTurnExecution).options(selectinload(MultiTurnExecution.script)).where(
        MultiTurnExecution.tenant_id == tenant_id
    )

    if suite_run_id:
        query = query.where(MultiTurnExecution.suite_run_id == suite_run_id)
    if script_id:
        query = query.where(MultiTurnExecution.script_id == script_id)
    if status:
        query = query.where(MultiTurnExecution.status == status)

    # Order by most recent first
    query = query.order_by(desc(MultiTurnExecution.created_at))

    # Get total count
    count_result = await db.execute(query)
    total_items = len(count_result.scalars().all())

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    # Execute query
    result = await db.execute(query)
    executions = result.scalars().all()

    executions_data = [
        {
            "id": str(execution.id),
            "suite_run_id": str(execution.suite_run_id),
            "script_id": str(execution.script_id),
            "scenario_name": execution.script.name if execution.script else None,
            "status": execution.status,
            "current_step_order": execution.current_step_order,
            "total_steps": execution.total_steps,
            "started_at": execution.started_at.isoformat() if execution.started_at else None,
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "created_at": execution.created_at.isoformat() if execution.created_at else None
        }
        for execution in executions
    ]

    return PaginatedResponse(
        data=executions_data,
        pagination={
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": (total_items + page_size - 1) // page_size
        }
    )

