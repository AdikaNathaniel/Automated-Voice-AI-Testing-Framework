"""
Resource-level access control for tenant isolation and ownership validation.

Provides functions to verify that users can only access resources within their
tenant and optionally validates ownership for write operations.

Functions:
    check_resource_access(user, resource, require_ownership): Validate user's
        access to a specific resource based on tenant_id and ownership.

Usage:
    >>> from api.auth.access_control import check_resource_access
    >>>
    >>> # Basic tenant check (read access)
    >>> check_resource_access(current_user, test_run)
    >>>
    >>> # With ownership validation (write access)
    >>> check_resource_access(current_user, test_run, require_ownership=True)
"""

from __future__ import annotations

from typing import Any
from fastapi import HTTPException, status

from api.auth.roles import Role


# Roles that can bypass ownership checks within their tenant
_OWNERSHIP_BYPASS_ROLES = {Role.ORG_ADMIN.value, Role.QA_LEAD.value}


def check_resource_access(
    user: Any,
    resource: Any,
    require_ownership: bool = False,
) -> None:
    """
    Verify user has access to a specific resource.

    Performs tenant isolation check and optionally validates ownership.
    Admins and QA leads can bypass ownership requirements within their tenant.

    Args:
        user: Current authenticated user (must have id, tenant_id, role attributes)
        resource: Resource to check access for (must have tenant_id attribute,
                  and optionally created_by for ownership checks)
        require_ownership: If True, verify user owns the resource or has
                          elevated role (admin/qa_lead)

    Raises:
        HTTPException: 403 if user cannot access the resource

    Example:
        >>> # Read access - tenant check only
        >>> check_resource_access(current_user, test_run)
        >>>
        >>> # Write access - also check ownership
        >>> check_resource_access(current_user, test_run, require_ownership=True)
        >>>
        >>> # Admin can access any resource in their tenant
        >>> admin_user.role = "admin"
        >>> check_resource_access(admin_user, other_user_resource, require_ownership=True)
    """
    # Get resource tenant_id
    resource_tenant_id = getattr(resource, 'tenant_id', None)

    # Resources with no tenant_id are considered "global" and accessible by all
    # authenticated users. This supports development/testing scenarios where
    # seeded data may not have tenant associations.
    if resource_tenant_id is None:
        return

    # Check tenant isolation - user must be in same tenant as resource
    # Also allow access if user has no tenant (development/admin user)
    if user.tenant_id is not None and user.tenant_id != resource_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Resource belongs to a different tenant.",
        )

    # If ownership not required, we're done
    if not require_ownership:
        return

    # Check if user can bypass ownership (admin or qa_lead)
    if user.role in _OWNERSHIP_BYPASS_ROLES:
        return

    # Check if resource has created_by attribute
    if not hasattr(resource, 'created_by'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot verify ownership - resource has no owner.",
        )

    # Verify ownership
    if resource.created_by != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You do not have ownership of this resource.",
        )


__all__ = ['check_resource_access']
