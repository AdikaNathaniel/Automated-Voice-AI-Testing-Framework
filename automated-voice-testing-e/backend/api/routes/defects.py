"""
Defect management API routes.
"""

from __future__ import annotations

from typing import Annotated, Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.dependencies import get_current_user_with_db
from api.schemas.auth import UserResponse
from sqlalchemy import select

from api.schemas.defect import (
    DefectAssign,
    DefectComment,
    DefectCreate,
    DefectCreateFromValidation,
    DefectDetailResponse,
    DefectListResponse,
    DefectRelatedExecution,
    DefectResolve,
    DefectResponse,
    DefectUpdate,
)
from services import defect_service
from api.auth.roles import Role
from api.schemas.enums import DefectStatus
from models.comment import Comment
from models.multi_turn_execution import MultiTurnExecution
from models.audit_trail import log_audit_trail
from models.integration_config import IntegrationConfig
from integrations.jira.client import JiraClient, JiraClientError
import logging

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/defects", tags=["Defects"])

_DEFECT_MUTATION_ROLES = {Role.ORG_ADMIN.value, Role.ORG_ADMIN.value, Role.QA_LEAD.value}


def _get_effective_tenant_id(user: UserResponse) -> UUID:
    """
    Get effective tenant_id for a user.

    Uses user.tenant_id if set (user belongs to an organization),
    otherwise uses user.id (user is their own tenant).

    This ensures tenant_id is NEVER None for data isolation.
    """
    return user.tenant_id if user.tenant_id else user.id


def _check_defect_tenant_access(user: UserResponse, defect) -> None:
    """
    Verify user has access to a defect based on tenant isolation.

    Args:
        user: Current authenticated user
        defect: Defect to check access for

    Raises:
        HTTPException: 403 if user cannot access the defect
    """
    if defect.tenant_id is None:
        # Legacy defects without tenant_id are accessible (migration scenario)
        return

    effective_tenant_id = _get_effective_tenant_id(user)
    if defect.tenant_id != effective_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Defect belongs to a different tenant.",
        )


def _ensure_can_mutate_defect(user: UserResponse) -> None:
    """
    Verify user has permission to mutate defects (create, update, assign, resolve).

    Args:
        user: Current authenticated user

    Raises:
        HTTPException: 403 if user lacks required role
    """
    if user.role not in _DEFECT_MUTATION_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or QA lead role required to modify defects.",
        )


def _map_exception(error: Exception) -> HTTPException:
    message = str(error)
    if isinstance(error, NoResultFound) or "not found" in message.lower():
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


@router.post(
    "/",
    response_model=DefectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new defect record",
)
async def create_defect_endpoint(
    payload: DefectCreate,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> DefectResponse:
    _ensure_can_mutate_defect(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    try:
        data = payload.model_dump()
        data["tenant_id"] = tenant_id
        defect = await defect_service.create_defect(db, data=data)

        # Log audit trail
        await log_audit_trail(
            db=db,
            action_type="create",
            resource_type="defect",
            resource_id=str(defect.id),
            tenant_id=tenant_id,
            user_id=current_user.id,
            new_values={
                "script_id": str(defect.script_id) if defect.script_id else None,
                "execution_id": str(defect.execution_id) if defect.execution_id else None,
                "suite_run_id": str(defect.suite_run_id) if defect.suite_run_id else None,
                "severity": defect.severity,
                "category": defect.category,
                "title": defect.title,
                "description": defect.description,
                "language_code": defect.language_code,
                "status": defect.status,
            },
            changes_summary=f"Defect '{defect.title}' ({defect.severity}) created by {current_user.email}",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=True,
        )

        return DefectResponse.model_validate(defect)
    except ValueError as error:
        raise _map_exception(error)


@router.post(
    "/from-validation",
    response_model=DefectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create defect from validation result during human review",
)
async def create_defect_from_validation_endpoint(
    payload: DefectCreateFromValidation,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> DefectResponse:
    """
    Create a defect manually during human validation review.

    This endpoint is called when a QA validator reviews a test execution
    and decides to create a defect for unexpected behavior. It automatically
    extracts context from the validation result (execution_id, script_id, etc.)
    and creates a defect record.

    Args:
        payload: Defect creation payload with validation_result_id
        db: Database session
        current_user: Currently authenticated user

    Returns:
        Created defect record

    Raises:
        403: If user lacks permission to create defects
        404: If validation result not found
        400: If validation result data is invalid
    """
    from models.validation_result import ValidationResult
    from datetime import datetime, timezone

    _ensure_can_mutate_defect(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    try:
        # Fetch validation result to extract execution context
        result = await db.execute(
            select(ValidationResult).where(
                ValidationResult.id == payload.validation_result_id
            )
        )
        validation_result = result.scalar_one_or_none()

        if not validation_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Validation result {payload.validation_result_id} not found"
            )

        # Extract execution details from validation result
        execution_id = validation_result.execution_id

        # Fetch execution to get script_id, suite_run_id, and language_code
        exec_result = await db.execute(
            select(MultiTurnExecution).where(
                MultiTurnExecution.id == execution_id
            )
        )
        execution = exec_result.scalar_one_or_none()

        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Execution {execution_id} not found"
            )

        # Generate title if not provided
        title = payload.title
        if not title:
            script_name = getattr(execution, 'script_name', None) or 'Unknown Script'
            title = f"Manual defect: {script_name}"

        # Build defect data
        defect_data = {
            "tenant_id": tenant_id,
            "script_id": execution.script_id,
            "execution_id": execution_id,
            "suite_run_id": execution.suite_run_id,
            "severity": payload.severity,
            "category": payload.category,
            "title": title,
            "description": payload.description or f"Defect created during validation review.\n\nValidation Result ID: {payload.validation_result_id}",
            "language_code": execution.language_code,
            "detected_at": datetime.now(timezone.utc),
            "status": "open",
        }

        # Create defect
        defect = await defect_service.create_defect(db, data=defect_data)

        # Log audit trail
        await log_audit_trail(
            db=db,
            action_type="create",
            resource_type="defect",
            resource_id=str(defect.id),
            tenant_id=tenant_id,
            user_id=current_user.id,
            new_values={
                "script_id": str(defect.script_id) if defect.script_id else None,
                "execution_id": str(defect.execution_id) if defect.execution_id else None,
                "suite_run_id": str(defect.suite_run_id) if defect.suite_run_id else None,
                "validation_result_id": str(payload.validation_result_id),
                "severity": defect.severity,
                "category": defect.category,
                "title": defect.title,
                "description": defect.description,
                "language_code": defect.language_code,
                "status": defect.status,
            },
            changes_summary=f"Defect '{defect.title}' ({defect.severity}) created from validation review by {current_user.email}",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=True,
        )

        return DefectResponse.model_validate(defect)

    except HTTPException:
        raise
    except Exception as error:
        raise _map_exception(error)


@router.get(
    "/{defect_id}",
    response_model=DefectDetailResponse,
    summary="Retrieve a defect by ID with related data",
)
async def get_defect_endpoint(
    defect_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> DefectDetailResponse:
    try:
        defect = await defect_service.get_defect(db, defect_id)
        # Verify user has access to this defect (tenant isolation)
        _check_defect_tenant_access(current_user, defect)

        # Fetch related executions
        related_executions = []
        if defect.execution_id:
            exec_result = await db.execute(
                select(MultiTurnExecution).where(
                    MultiTurnExecution.id == defect.execution_id
                )
            )
            execution = exec_result.scalar_one_or_none()
            if execution:
                related_executions.append(
                    DefectRelatedExecution(
                        id=execution.id,
                        status=execution.status or "unknown",
                        suite_run_id=execution.suite_run_id,
                        executed_at=execution.started_at,
                    )
                )

        # Fetch comments for this defect
        comments_result = await db.execute(
            select(Comment).where(
                Comment.entity_type == "defect",
                Comment.entity_id == defect_id,
            ).order_by(Comment.created_at.asc())
        )
        comment_rows = comments_result.scalars().all()
        comments = [
            DefectComment(
                id=c.id,
                author=c.author.email if c.author else "Unknown",
                message=c.content,
                created_at=c.created_at,
            )
            for c in comment_rows
        ]

        return DefectDetailResponse(
            **DefectResponse.model_validate(defect).model_dump(),
            related_executions=related_executions,
            comments=comments,
        )
    except (NoResultFound, ValueError) as error:
        raise _map_exception(error)


@router.get(
    "/",
    response_model=DefectListResponse,
    summary="List defects with filters and pagination",
)
async def list_defects_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
    status_filter: Optional[DefectStatus] = Query(None, alias="status"),
    severity: Optional[str] = None,
    category: Optional[str] = None,
    assigned_to: Optional[UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> DefectListResponse:
    tenant_id = _get_effective_tenant_id(current_user)

    filters: Dict[str, object] = {}
    if status_filter:
        filters["status"] = status_filter.value
    if severity:
        filters["severity"] = severity
    if category:
        filters["category"] = category
    if assigned_to:
        filters["assigned_to"] = assigned_to

    items, total = await defect_service.list_defects(
        db,
        filters=filters,
        pagination={"skip": skip, "limit": limit},
        tenant_id=tenant_id,
    )

    responses = [DefectResponse.model_validate(item) for item in items]
    return DefectListResponse(total=total, items=responses)


@router.patch(
    "/{defect_id}",
    response_model=DefectResponse,
    summary="Update defect fields",
)
async def update_defect_endpoint(
    defect_id: UUID,
    payload: DefectUpdate,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> DefectResponse:
    _ensure_can_mutate_defect(current_user)

    values = payload.model_dump(exclude_unset=True)
    if not values:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    try:
        # First fetch to validate access
        existing = await defect_service.get_defect(db, defect_id)
        _check_defect_tenant_access(current_user, existing)

        # Capture old values for audit logging
        old_values = {
            "status": existing.status,
            "severity": existing.severity,
            "category": existing.category,
            "title": existing.title,
            "description": existing.description,
            "assigned_to": str(existing.assigned_to) if existing.assigned_to else None,
        }

        defect = await defect_service.update_defect(
            db,
            defect_id=defect_id,
            data=values,
        )

        # Capture new values
        new_values = {
            "status": defect.status,
            "severity": defect.severity,
            "category": defect.category,
            "title": defect.title,
            "description": defect.description,
            "assigned_to": str(defect.assigned_to) if defect.assigned_to else None,
        }

        # Build dynamic summary noting what changed
        changes = []
        if old_values["status"] != new_values["status"]:
            changes.append(f"status: {old_values['status']} → {new_values['status']}")
        if old_values["severity"] != new_values["severity"]:
            changes.append(f"severity: {old_values['severity']} → {new_values['severity']}")
        if old_values["category"] != new_values["category"]:
            changes.append(f"category: {old_values['category']} → {new_values['category']}")
        if old_values["assigned_to"] != new_values["assigned_to"]:
            changes.append(f"assignment changed")

        summary = f"Defect '{defect.title}' updated by {current_user.email}"
        if changes:
            summary += f" - {', '.join(changes)}"

        # Log audit trail
        tenant_id = _get_effective_tenant_id(current_user)
        await log_audit_trail(
            db=db,
            action_type="update",
            resource_type="defect",
            resource_id=str(defect_id),
            tenant_id=tenant_id,
            user_id=current_user.id,
            old_values=old_values,
            new_values=new_values,
            changes_summary=summary,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=True,
        )

        return DefectResponse.model_validate(defect)
    except (NoResultFound, ValueError) as error:
        raise _map_exception(error)


@router.post(
    "/{defect_id}/assign",
    response_model=DefectResponse,
    summary="Assign a defect to a user",
)
async def assign_defect_endpoint(
    defect_id: UUID,
    payload: DefectAssign,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> DefectResponse:
    _ensure_can_mutate_defect(current_user)

    try:
        # First fetch to validate access
        existing = await defect_service.get_defect(db, defect_id)
        _check_defect_tenant_access(current_user, existing)

        # Capture old assignment for audit logging
        old_assigned_to = str(existing.assigned_to) if existing.assigned_to else None

        defect = await defect_service.assign_defect(
            db,
            defect_id=defect_id,
            user_id=payload.assigned_to,
        )

        # Log audit trail
        tenant_id = _get_effective_tenant_id(current_user)
        await log_audit_trail(
            db=db,
            action_type="assign",
            resource_type="defect",
            resource_id=str(defect_id),
            tenant_id=tenant_id,
            user_id=current_user.id,
            old_values={
                "assigned_to": old_assigned_to,
            },
            new_values={
                "assigned_to": str(payload.assigned_to) if payload.assigned_to else None,
            },
            changes_summary=f"Defect '{defect.title}' assigned to user {payload.assigned_to} by {current_user.email}",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=True,
        )

        return DefectResponse.model_validate(defect)
    except (NoResultFound, ValueError) as error:
        raise _map_exception(error)


@router.post(
    "/{defect_id}/resolve",
    response_model=DefectResponse,
    summary="Resolve a defect with resolution summary",
)
async def resolve_defect_endpoint(
    defect_id: UUID,
    payload: DefectResolve,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> DefectResponse:
    _ensure_can_mutate_defect(current_user)

    try:
        # First fetch to validate access
        existing = await defect_service.get_defect(db, defect_id)
        _check_defect_tenant_access(current_user, existing)

        # Capture old status for audit logging
        old_status = existing.status

        defect = await defect_service.resolve_defect(
            db,
            defect_id=defect_id,
            resolution=payload.resolution,
        )

        # Log audit trail
        tenant_id = _get_effective_tenant_id(current_user)
        await log_audit_trail(
            db=db,
            action_type="resolve",
            resource_type="defect",
            resource_id=str(defect_id),
            tenant_id=tenant_id,
            user_id=current_user.id,
            old_values={
                "status": old_status,
                "resolved_at": None,
            },
            new_values={
                "status": defect.status,
                "resolution": payload.resolution,
                "resolved_at": defect.resolved_at.isoformat() if defect.resolved_at else None,
            },
            changes_summary=f"Defect '{defect.title}' resolved by {current_user.email}",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=True,
        )

        return DefectResponse.model_validate(defect)
    except (NoResultFound, ValueError) as error:
        raise _map_exception(error)


async def _get_jira_client_for_tenant(
    db: AsyncSession,
    tenant_id: UUID,
) -> tuple[JiraClient | None, IntegrationConfig | None]:
    """
    Get Jira client configured for a tenant.

    Returns:
        Tuple of (JiraClient or None, IntegrationConfig or None)
    """
    result = await db.execute(
        select(IntegrationConfig).where(
            IntegrationConfig.tenant_id == tenant_id,
            IntegrationConfig.integration_type == "jira",
            IntegrationConfig.is_enabled == True,  # noqa: E712
            IntegrationConfig.is_connected == True,  # noqa: E712
        )
    )
    config = result.scalar_one_or_none()

    if not config:
        return None, None

    # Get decrypted credentials
    api_token = config.get_access_token()
    email = config.jira_email
    instance_url = config.jira_instance_url

    if not all([api_token, email, instance_url]):
        logger.warning(f"Jira config incomplete for tenant {tenant_id}")
        return None, config

    # Build API base URL
    base_url = instance_url.rstrip("/")
    if not base_url.endswith("/rest/api/3"):
        base_url = f"{base_url}/rest/api/3"

    try:
        client = JiraClient(
            email=email,
            api_token=api_token,
            base_url=base_url,
        )
        return client, config
    except ValueError as e:
        logger.error(f"Failed to create JiraClient for tenant {tenant_id}: {e}")
        return None, config


@router.post(
    "/{defect_id}/jira",
    response_model=DefectResponse,
    summary="Create a Jira ticket for an existing defect",
)
async def create_jira_ticket_endpoint(
    defect_id: UUID,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> DefectResponse:
    """
    Create a Jira ticket for an existing defect.

    This endpoint creates a Jira issue linked to the defect and updates
    the defect record with the Jira issue key and URL.

    Args:
        defect_id: UUID of the defect
        db: Database session
        current_user: Currently authenticated user

    Returns:
        Updated defect record with Jira fields populated

    Raises:
        403: If user lacks permission
        404: If defect not found
        400: If Jira not configured or defect already has Jira ticket
    """
    _ensure_can_mutate_defect(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    try:
        # Fetch defect
        defect = await defect_service.get_defect(db, defect_id)
        _check_defect_tenant_access(current_user, defect)

        # Check if already has Jira ticket
        if defect.jira_issue_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Defect already has Jira ticket: {defect.jira_issue_key}",
            )

        # Get Jira client for tenant
        jira_client, jira_config = await _get_jira_client_for_tenant(db, tenant_id)

        if not jira_client:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Jira integration not configured or not connected. Please configure Jira in Settings > Integrations.",
            )

        if not jira_config.jira_project_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Jira project key not configured. Please set a default project in Jira integration settings.",
            )

        # Build Jira browse URL base
        jira_browse_base_url = jira_config.jira_instance_url
        if jira_browse_base_url:
            jira_browse_base_url = jira_browse_base_url.rstrip("/") + "/browse"

        # Create Jira ticket using defect_service helper
        issue_payload = defect_service._build_jira_issue_payload(
            defect,
            issue_type=jira_config.jira_issue_type or "Bug",
        )

        try:
            issue_key = await jira_client.create_issue(
                project=jira_config.jira_project_key,
                data=issue_payload,
            )
        except JiraClientError as e:
            logger.error(f"Failed to create Jira issue for defect {defect_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to create Jira ticket: {str(e)}",
            )

        # Update defect with Jira info
        jira_issue_url = defect_service._build_jira_issue_url(jira_browse_base_url, issue_key)
        updated_defect = await defect_service.update_defect(
            db,
            defect_id=defect_id,
            data={
                "jira_issue_key": issue_key,
                "jira_issue_url": jira_issue_url,
                "jira_status": "To Do",
            },
        )

        # Log audit trail
        await log_audit_trail(
            db=db,
            action_type="jira_create",
            resource_type="defect",
            resource_id=str(defect_id),
            tenant_id=tenant_id,
            user_id=current_user.id,
            old_values={
                "jira_issue_key": None,
                "jira_issue_url": None,
            },
            new_values={
                "jira_issue_key": issue_key,
                "jira_issue_url": jira_issue_url,
            },
            changes_summary=f"Jira ticket {issue_key} created for defect '{defect.title}' by {current_user.email}",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=True,
        )

        logger.info(f"Created Jira ticket {issue_key} for defect {defect_id}")
        return DefectResponse.model_validate(updated_defect)

    except HTTPException:
        raise
    except (NoResultFound, ValueError) as error:
        raise _map_exception(error)
    except Exception as e:
        logger.error(f"Unexpected error creating Jira ticket for defect {defect_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create Jira ticket: {str(e)}",
        )
