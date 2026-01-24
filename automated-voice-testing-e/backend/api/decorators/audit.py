"""
Audit Logging Decorator

Provides automatic audit trail logging for FastAPI endpoints with minimal boilerplate.

Example usage:

    @router.post("/users")
    @audit_log(
        action_type="create",
        resource_type="user",
        get_resource_id=lambda result: str(result.id),
        get_new_values=lambda result: {
            "email": result.email,
            "role": result.role,
        },
        summary_template="User {email} created with role {role}"
    )
    async def create_user(...):
        ...

    @router.put("/users/{user_id}")
    @audit_log(
        action_type="update",
        resource_type="user",
        get_resource_id=lambda kwargs: str(kwargs["user_id"]),
        get_old_values=lambda context: context.get("old_user_values"),
        get_new_values=lambda result: {
            "email": result.email,
            "role": result.role,
        },
        summary_template="User {email} updated",
        capture_old_values=True  # Will call before_handler to capture old values
    )
    async def update_user(...):
        ...
"""

import inspect
import logging
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, Optional, Union
from uuid import UUID

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from models.audit_trail import log_audit_trail

logger = logging.getLogger(__name__)


def audit_log(
    action_type: str,
    resource_type: str,
    get_resource_id: Optional[Callable] = None,
    get_tenant_id: Optional[Callable] = None,
    get_user_id: Optional[Callable] = None,
    get_old_values: Optional[Callable] = None,
    get_new_values: Optional[Callable] = None,
    summary_template: Optional[str] = None,
    mask_fields: Optional[list] = None,
    capture_old_values: bool = False,
    before_handler: Optional[Callable] = None,
    skip_on_failure: bool = False,
):
    """
    Decorator for automatic audit trail logging.

    Args:
        action_type: Type of action (create, update, delete, execute, login, etc.)
        resource_type: Type of resource affected (user, integration_config, etc.)
        get_resource_id: Function to extract resource ID from result or kwargs
        get_tenant_id: Function to extract tenant ID (defaults to current_user.effective_tenant_id)
        get_user_id: Function to extract user ID (defaults to current_user.id)
        get_old_values: Function to extract old values (for updates/deletes)
        get_new_values: Function to extract new values (for creates/updates)
        summary_template: Template string for changes_summary (e.g., "User {email} created")
        mask_fields: List of field names to mask in audit log (e.g., ["password", "api_key"])
        capture_old_values: If True, captures old values before operation
        before_handler: Optional async function to run before main operation (e.g., fetch old values)
        skip_on_failure: If True, don't log audit trail on operation failure

    Returns:
        Decorated async function with automatic audit logging

    The decorator automatically extracts:
    - db: AsyncSession from function kwargs
    - current_user: UserResponse from function kwargs
    - request: Request from function kwargs
    - result: Return value of the decorated function

    Context passed to callback functions:
    - result: Return value of decorated function
    - kwargs: Function keyword arguments
    - request: FastAPI Request object
    - current_user: Current user object
    - context: Additional context from before_handler
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract standard dependencies
            db: Optional[AsyncSession] = kwargs.get("db")
            current_user = kwargs.get("current_user")
            request: Optional[Request] = kwargs.get("request")

            # Context for callbacks
            context: Dict[str, Any] = {}

            # Run before handler if provided (e.g., to capture old values)
            if before_handler:
                try:
                    context = await before_handler(kwargs, db) if inspect.iscoroutinefunction(before_handler) else before_handler(kwargs, db)
                except Exception as e:
                    logger.warning(f"Before handler failed for audit logging: {e}")

            # Execute the main function
            success = True
            error_message = None
            result = None

            try:
                result = await func(*args, **kwargs)
                success = True
            except Exception as e:
                success = False
                error_message = str(e)
                if not skip_on_failure:
                    # Log audit trail even on failure
                    await _log_audit(
                        db=db,
                        current_user=current_user,
                        request=request,
                        action_type=action_type,
                        resource_type=resource_type,
                        kwargs=kwargs,
                        result=None,
                        context=context,
                        success=False,
                        error_message=error_message,
                        get_resource_id=get_resource_id,
                        get_tenant_id=get_tenant_id,
                        get_user_id=get_user_id,
                        get_old_values=get_old_values,
                        get_new_values=get_new_values,
                        summary_template=summary_template,
                        mask_fields=mask_fields,
                    )
                raise  # Re-raise the exception

            # Log successful audit trail
            if success and db:
                await _log_audit(
                    db=db,
                    current_user=current_user,
                    request=request,
                    action_type=action_type,
                    resource_type=resource_type,
                    kwargs=kwargs,
                    result=result,
                    context=context,
                    success=True,
                    error_message=None,
                    get_resource_id=get_resource_id,
                    get_tenant_id=get_tenant_id,
                    get_user_id=get_user_id,
                    get_old_values=get_old_values,
                    get_new_values=get_new_values,
                    summary_template=summary_template,
                    mask_fields=mask_fields,
                )

            return result

        return wrapper

    return decorator


async def _log_audit(
    db: Optional[AsyncSession],
    current_user: Any,
    request: Optional[Request],
    action_type: str,
    resource_type: str,
    kwargs: Dict[str, Any],
    result: Any,
    context: Dict[str, Any],
    success: bool,
    error_message: Optional[str],
    get_resource_id: Optional[Callable],
    get_tenant_id: Optional[Callable],
    get_user_id: Optional[Callable],
    get_old_values: Optional[Callable],
    get_new_values: Optional[Callable],
    summary_template: Optional[str],
    mask_fields: Optional[list],
):
    """Internal function to create audit trail entry."""
    if not db:
        logger.warning("No database session available for audit logging")
        return

    try:
        # Extract resource ID
        resource_id = None
        if get_resource_id:
            try:
                resource_id = get_resource_id(result=result, kwargs=kwargs, context=context)
                if isinstance(resource_id, UUID):
                    resource_id = str(resource_id)
            except Exception as e:
                logger.warning(f"Failed to extract resource_id: {e}")

        # Extract tenant ID
        tenant_id = None
        if get_tenant_id:
            try:
                tenant_id = get_tenant_id(current_user=current_user, result=result, kwargs=kwargs, context=context)
            except Exception as e:
                logger.warning(f"Failed to extract tenant_id: {e}")
        elif current_user:
            tenant_id = getattr(current_user, "effective_tenant_id", None)

        # Extract user ID
        user_id = None
        if get_user_id:
            try:
                user_id = get_user_id(current_user=current_user, result=result, kwargs=kwargs, context=context)
            except Exception as e:
                logger.warning(f"Failed to extract user_id: {e}")
        elif current_user:
            user_id = getattr(current_user, "id", None)

        # Extract old values
        old_values = None
        if get_old_values:
            try:
                old_values = get_old_values(result=result, kwargs=kwargs, context=context)
                if mask_fields and old_values:
                    old_values = _mask_sensitive_fields(old_values, mask_fields)
            except Exception as e:
                logger.warning(f"Failed to extract old_values: {e}")

        # Extract new values
        new_values = None
        if get_new_values:
            try:
                new_values = get_new_values(result=result, kwargs=kwargs, context=context)
                if mask_fields and new_values:
                    new_values = _mask_sensitive_fields(new_values, mask_fields)
            except Exception as e:
                logger.warning(f"Failed to extract new_values: {e}")

        # Build changes summary
        changes_summary = None
        if summary_template:
            try:
                # Try to format with new_values first, fall back to result attributes
                format_dict = new_values.copy() if new_values else {}
                if result and hasattr(result, "__dict__"):
                    format_dict.update({k: v for k, v in result.__dict__.items() if not k.startswith("_")})
                changes_summary = summary_template.format(**format_dict)
            except Exception as e:
                logger.warning(f"Failed to format summary template: {e}")
                changes_summary = f"{action_type} {resource_type}"

        # Extract request metadata
        ip_address = None
        user_agent = None
        if request:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")

        # Create audit trail entry
        await log_audit_trail(
            db=db,
            action_type=action_type,
            resource_type=resource_type,
            resource_id=resource_id,
            tenant_id=tenant_id,
            user_id=user_id,
            old_values=old_values,
            new_values=new_values,
            changes_summary=changes_summary or f"{action_type} {resource_type}",
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            error_message=error_message,
        )

        # Note: Commit is handled by the endpoint, not here
        logger.debug(f"Audit trail logged: {action_type} {resource_type} (success={success})")

    except Exception as e:
        # Never fail the main operation due to audit logging errors
        logger.error(f"Failed to create audit trail entry: {e}", exc_info=True)


def _mask_sensitive_fields(data: Dict[str, Any], mask_fields: list) -> Dict[str, Any]:
    """
    Mask sensitive fields in audit log data.

    Args:
        data: Dictionary of values
        mask_fields: List of field names to mask

    Returns:
        Dictionary with sensitive fields masked
    """
    if not mask_fields:
        return data

    masked_data = data.copy()

    for field in mask_fields:
        if field in masked_data:
            value = masked_data[field]

            if isinstance(value, str) and value:
                # For strings, show first and last 4 chars (or *** for short strings)
                if len(value) > 8:
                    masked_data[field] = f"{value[:4]}...{value[-4:]}"
                else:
                    masked_data[field] = "***MASKED***"
            else:
                # For non-strings, just indicate it was set
                masked_data[field] = "***MASKED***"

    return masked_data


# Convenience functions for common patterns

def audit_create(
    resource_type: str,
    get_resource_id: Optional[Callable] = None,
    get_new_values: Optional[Callable] = None,
    summary_template: Optional[str] = None,
    **kwargs
):
    """Shorthand for audit_log with action_type="create"."""
    return audit_log(
        action_type="create",
        resource_type=resource_type,
        get_resource_id=get_resource_id,
        get_new_values=get_new_values,
        summary_template=summary_template,
        **kwargs
    )


def audit_update(
    resource_type: str,
    get_resource_id: Optional[Callable] = None,
    get_old_values: Optional[Callable] = None,
    get_new_values: Optional[Callable] = None,
    summary_template: Optional[str] = None,
    before_handler: Optional[Callable] = None,
    **kwargs
):
    """Shorthand for audit_log with action_type="update"."""
    return audit_log(
        action_type="update",
        resource_type=resource_type,
        get_resource_id=get_resource_id,
        get_old_values=get_old_values,
        get_new_values=get_new_values,
        summary_template=summary_template,
        capture_old_values=True,
        before_handler=before_handler,
        **kwargs
    )


def audit_delete(
    resource_type: str,
    get_resource_id: Optional[Callable] = None,
    get_old_values: Optional[Callable] = None,
    summary_template: Optional[str] = None,
    before_handler: Optional[Callable] = None,
    **kwargs
):
    """Shorthand for audit_log with action_type="delete"."""
    return audit_log(
        action_type="delete",
        resource_type=resource_type,
        get_resource_id=get_resource_id,
        get_old_values=get_old_values,
        summary_template=summary_template,
        capture_old_values=True,
        before_handler=before_handler,
        **kwargs
    )
