"""
Voice AI Testing Framework - Dependency Injection
FastAPI dependencies for database sessions, authentication, and configuration
"""

from typing import Generator, Optional, Dict, Any
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from api.config import Settings, get_settings
from api.schemas.auth import UserResponse
from services import user_service


# ============================================================================
# Security Scheme
# ============================================================================

# HTTP Bearer token security scheme for JWT authentication
security = HTTPBearer(auto_error=False)


# ============================================================================
# Configuration Dependency
# ============================================================================

def get_settings_dependency() -> Settings:
    """
    Dependency to get application settings

    Returns cached Settings instance from the application configuration.
    This dependency can be injected into any FastAPI route to access
    configuration values.

    Returns:
        Settings: Application settings instance

    Example:
        ```python
        from fastapi import APIRouter, Depends
        from api.dependencies import get_settings_dependency
        from api.config import Settings

        router = APIRouter()

        @router.get("/info")
        def get_info(settings: Settings = Depends(get_settings_dependency)):
            return {
                "environment": settings.ENVIRONMENT,
                "version": settings.APP_VERSION
            }
        ```
    """
    return get_settings()


# ============================================================================
# Database Session Dependency
# ============================================================================

async def get_db():
    """
    Dependency to get database session

    Yields a database session and ensures it's properly closed after use.
    Uses FastAPI's dependency injection to manage the session lifecycle.

    Yields:
        AsyncSession: Async database session object

    Example:
        ```python
        from fastapi import APIRouter, Depends
        from api.dependencies import get_db
        from sqlalchemy.ext.asyncio import AsyncSession

        router = APIRouter()

        @router.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            # Use db session here
            result = await db.execute(select(User))
            users = result.scalars().all()
            return users
        ```

    Note:
        This uses the real SQLAlchemy AsyncSession from api.database.
        The mock implementation has been replaced with the actual database connection.
    """
    # Import the real database session factory
    from api.database import get_db as get_real_db

    # Use the real database session
    async for db in get_real_db():
        yield db


# ============================================================================
# Token Verification
# ============================================================================

def verify_token(token: str, settings: Settings) -> Dict[str, Any]:
    """
    Verify and decode JWT token

    Args:
        token: JWT token string
        settings: Application settings containing JWT configuration

    Returns:
        Dict containing decoded token payload with user information

    Raises:
        HTTPException: If token is invalid or expired

    Example:
        ```python
        settings = get_settings()
        payload = verify_token(token, settings)
        user_id = payload.get("sub")
        ```
    """
    # Validate token format before attempting to decode
    if not token or not token.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if token has the basic JWT structure (3 parts separated by dots)
    token_parts = token.split('.')
    if len(token_parts) != 3:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Check if token has expired
        exp = payload.get("exp")
        if exp:
            exp_datetime = datetime.fromtimestamp(exp)
            if exp_datetime < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        return payload

    except HTTPException:
        # Re-raise HTTPException as-is
        raise
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def decode_token(token: str, settings: Settings) -> Dict[str, Any]:
    """
    Decode JWT token without verification (for debugging)

    Args:
        token: JWT token string
        settings: Application settings

    Returns:
        Dict containing decoded token payload

    Warning:
        This function does not verify the token signature.
        Use verify_token() for production code.
    """
    try:
        # Decode without verification
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_signature": False}
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not decode token: {str(e)}",
        )


# ============================================================================
# Current User Dependencies
# ============================================================================

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    settings: Settings = Depends(get_settings_dependency)
) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user (required)

    Validates the JWT token from the Authorization header and returns
    user information. Raises HTTPException if token is missing or invalid.

    Args:
        credentials: HTTP Bearer credentials from Authorization header
        settings: Application settings (injected dependency)

    Returns:
        Dict containing user information from token payload:
            - sub: User ID
            - email: User email (if present)
            - username: Username (if present)
            - roles: User roles (if present)

    Raises:
        HTTPException 401: If token is missing or invalid

    Example:
        ```python
        from fastapi import APIRouter, Depends
        from api.dependencies import get_current_user

        router = APIRouter()

        @router.get("/me")
        async def get_me(current_user: dict = Depends(get_current_user_with_db)):
            return {
                "user_id": current_user.get("sub"),
                "email": current_user.get("email")
            }
        ```
    """
    # Check if credentials are provided
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify and decode token
    token = credentials.credentials
    payload = verify_token(token, settings)

    # Extract user information from payload
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    settings: Settings = Depends(get_settings_dependency)
) -> Optional[Dict[str, Any]]:
    """
    Dependency to get current authenticated user (optional)

    Similar to get_current_user, but returns None instead of raising
    an exception if no token is provided. Still validates token if present.

    Args:
        credentials: HTTP Bearer credentials from Authorization header
        settings: Application settings (injected dependency)

    Returns:
        Dict containing user information if authenticated, None otherwise

    Example:
        ```python
        from fastapi import APIRouter, Depends
        from api.dependencies import get_current_user_optional

        router = APIRouter()

        @router.get("/content")
        async def get_content(
            current_user: Optional[dict] = Depends(get_current_user_optional)
        ):
            if current_user:
                # Return personalized content
                return {"message": f"Hello {current_user.get('email')}"}
            else:
                # Return public content
                return {"message": "Hello guest"}
        ```
    """
    # If no credentials provided, return None (optional authentication)
    if not credentials:
        return None

    try:
        # Verify and decode token
        token = credentials.credentials
        payload = verify_token(token, settings)
        return payload
    except HTTPException:
        # If token is invalid, return None instead of raising exception
        return None


async def get_current_user_with_db(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Dependency to get current authenticated user from database.

    Extracts and validates the JWT token from Authorization header,
    decodes it to get the user ID, and fetches the user from database.
    This is the centralized implementation that replaces duplicates in route files.

    Args:
        credentials: HTTP Bearer credentials from Authorization header
        db: Database session

    Returns:
        UserResponse: Current authenticated user

    Raises:
        HTTPException: 401 if token is invalid, expired, or user not found

    Example:
        ```python
        from fastapi import APIRouter, Depends
        from api.dependencies import get_current_user_with_db
        from api.schemas.auth import UserResponse

        router = APIRouter()

        @router.get("/me")
        async def get_me(current_user: UserResponse = Depends(get_current_user_with_db)):
            return current_user
        ```
    """
    # Validate token format
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # Validate token is not empty
    if not token or not token.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Verify and decode JWT token (with signature validation)
        settings = get_settings()
        payload = verify_token(token, settings)
        user_id_str = payload.get("sub")

        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user from database
        user_id = UUID(user_id_str)

        user = await user_service.get_user_by_id(db, user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Convert to response schema
        user_response = UserResponse.model_validate(user)

        return user_response

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ============================================================================
# User Permission Dependencies
# ============================================================================

def require_admin(
    current_user: UserResponse = Depends(get_current_user_with_db)
) -> UserResponse:
    """
    Dependency to require organization admin role

    Validates that the current user has organization admin or super admin privileges.

    Args:
        current_user: Current user from get_current_user_with_db dependency

    Returns:
        UserResponse: Validated user object

    Raises:
        HTTPException 403: If user is not an org admin or super admin

    Example:
        ```python
        from fastapi import APIRouter, Depends
        from api.dependencies import require_admin
        from api.schemas.auth import UserResponse

        router = APIRouter()

        @router.delete("/users/{user_id}")
        async def delete_user(
            user_id: str,
            admin_user: UserResponse = Depends(require_admin)
        ):
            # Only org admins can delete users in their organization
            return {"message": f"User {user_id} deleted"}
        ```
    """
    if current_user.role not in ("org_admin", "super_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization admin privileges required",
        )

    return current_user


def require_role(allowed_roles: list[str]):
    """
    Dependency factory to require specific roles

    Creates a dependency that validates the user has one of the allowed roles.

    Args:
        allowed_roles: List of allowed roles (e.g., ["org_admin", "super_admin"])

    Returns:
        Dependency function that validates the role

    Example:
        ```python
        from fastapi import APIRouter, Depends
        from api.dependencies import require_role

        router = APIRouter()

        @router.post("/validations")
        async def create_validation(
            current_user: UserResponse = Depends(require_role(["org_admin", "qa_lead"]))
        ):
            # Only org_admin or qa_lead can create validations
            return {"message": "Validation created"}
        ```
    """
    async def role_checker(
        current_user: UserResponse = Depends(get_current_user_with_db)
    ) -> UserResponse:
        # Check if user's role is in the allowed roles list
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of these roles required: {', '.join(allowed_roles)}",
            )

        return current_user

    return role_checker


# ============================================================================
# Export public API
# ============================================================================

__all__ = [
    'get_settings_dependency',
    'get_db',
    'get_current_user',
    'get_current_user_optional',
    'require_admin',
    'require_role',
    'verify_token',
    'decode_token',
]
