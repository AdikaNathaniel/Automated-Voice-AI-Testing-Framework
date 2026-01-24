"""
Role-based authorization for API endpoints

Provides role-checking functionality to protect endpoints based on user roles.
Uses FastAPI's dependency injection system to verify that authenticated users
have the required role(s) to access specific endpoints.

Functions:
    require_role(*roles: str) -> Callable:
        Returns a dependency function that checks if the current user has
        one of the required roles. Raises 403 Forbidden if not authorized.

Usage:
    >>> from fastapi import APIRouter, Depends
    >>> from api.auth.permissions import require_role
    >>> from api.schemas.auth import UserResponse
    >>>
    >>> router = APIRouter()
    >>>
    >>> @router.get("/admin/dashboard")
    >>> async def admin_dashboard(user: UserResponse = Depends(require_role("admin"))):
    ...     return {"message": "Admin dashboard"}
    >>>
    >>> @router.get("/admin/settings")
    >>> async def admin_settings(user: UserResponse = Depends(require_role("admin", "moderator"))):
    ...     return {"message": "Settings - accessible by admin or moderator"}

Example:
    Protect an endpoint that requires admin role:

    ```python
    @router.delete("/users/{user_id}")
    async def delete_user(
        user_id: UUID,
        current_user: UserResponse = Depends(require_role("admin"))
    ):
        # Only admins can delete users
        await user_service.delete_user(db, user_id)
        return {"message": "User deleted"}
    ```

Security Notes:
    - Always use with authentication (get_current_user dependency)
    - Returns 403 Forbidden if user lacks required role
    - Returns 401 Unauthorized if user is not authenticated
    - Role checking is case-sensitive
    - Users without a role field are denied access
"""

from typing import Callable
from fastapi import Depends, HTTPException, status
from api.schemas.auth import UserResponse
from api.dependencies import get_current_user_with_db


def require_role(*roles: str) -> Callable:
    """
    Create a dependency that requires the current user to have one of the specified roles.

    This is a dependency factory that returns a FastAPI dependency function.
    The returned function checks if the authenticated user has at least one
    of the required roles. If not, it raises a 403 Forbidden error.

    Args:
        *roles: One or more role names that are allowed to access the endpoint.
               User must have at least one of these roles.

    Returns:
        Callable: A dependency function that can be used with FastAPI's Depends().
                 The function takes the current_user and returns the user if authorized.

    Raises:
        ValueError: If no roles are provided (at function definition time)
        HTTPException: 403 if user doesn't have required role
        HTTPException: 401 if user is not authenticated (from get_current_user)

    Example:
        >>> # Single role
        >>> @router.get("/admin")
        >>> async def admin_only(user = Depends(require_role("admin"))):
        ...     return {"message": "Admin area"}
        >>>
        >>> # Multiple roles - user needs one of them
        >>> @router.get("/moderation")
        >>> async def moderation(user = Depends(require_role("admin", "moderator"))):
        ...     return {"message": "Moderation tools"}

    Note:
        - Role checking is case-sensitive ("Admin" != "admin")
        - Users without a role field (role=None) are denied access
        - The dependency returns the UserResponse object for further use
        - Combine with other dependencies as needed
    """
    # Validate that at least one role is provided
    if not roles:
        raise ValueError("At least one role must be specified for require_role()")

    # Create and return the dependency function
    async def role_checker(current_user: UserResponse = Depends(get_current_user_with_db)) -> UserResponse:
        """
        Dependency function that checks if current user has required role.

        This function is returned by require_role() and is used as a FastAPI dependency.
        It receives the current authenticated user and verifies they have the required role.

        Args:
            current_user: The authenticated user from get_current_user dependency

        Returns:
            UserResponse: The current user if they have the required role

        Raises:
            HTTPException: 403 Forbidden if user doesn't have required role
        """
        # Check if user has a role field
        if current_user.role is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: User has no assigned role. Required role(s): {', '.join(roles)}"
            )

        # Check if user's role matches any of the required roles
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: Required role(s): {', '.join(roles)}. Your role: {current_user.role}"
            )

        # User has required role - return user for further use in endpoint
        return current_user

    return role_checker


# =============================================================================
# Export
# =============================================================================

__all__ = ['require_role']
