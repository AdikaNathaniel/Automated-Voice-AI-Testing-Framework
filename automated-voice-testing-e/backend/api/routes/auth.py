"""
Authentication API routes

Provides endpoints for user authentication including registration, login,
token refresh, logout, and current user retrieval.

Endpoints:
    POST /api/v1/auth/register - Register new user
    POST /api/v1/auth/login - Login and get tokens
    POST /api/v1/auth/refresh - Refresh access token
    POST /api/v1/auth/logout - Revoke a refresh token
    GET /api/v1/auth/me - Get current authenticated user

All endpoints use Pydantic schemas for validation and return standard responses.
"""

from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from api.auth.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from api.auth.password import verify_password
from api.auth.roles import Role
from api.config import get_settings
from api.database import get_db
from api.dependencies import get_current_user_with_db
from api.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    LoginResponse,
    TokenRefreshRequest,
    TokenRefreshResponse,
    UserResponse,
)
from models.audit_trail import log_audit_trail
from services import user_service
from services.refresh_token_store import refresh_token_store
from services.login_attempt_tracker import login_attempt_tracker


# Create router
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Security scheme for Bearer token
security = HTTPBearer()

# Token expiration settings
settings = get_settings()
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_EXPIRATION_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.JWT_REFRESH_EXPIRATION_DAYS


# =============================================================================
# Helper Functions
# =============================================================================


def _ensure_admin_user(user: UserResponse) -> None:
    if user.role != Role.ORG_ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required for this action.",
        )


# Use centralized get_current_user_with_db from api.dependencies


# =============================================================================
# Registration Endpoint
# =============================================================================

@router.post(
    "/register",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with email, username, and password"
)
async def register(
    data: RegisterRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
):
    """
    Register a new user account.

    Creates a new user with the provided email, username, password, and full name.
    Password is automatically hashed before storage.

    Args:
        data: Registration data (email, username, password, full_name)
        request: HTTP request for audit logging
        db: Database session
        current_user: Admin user creating the account

    Returns:
        dict: Created user data (without password)

    Raises:
        HTTPException: 400 if email or username already exists
    """
    _ensure_admin_user(current_user)

    try:
        # Create user
        user = await user_service.create_user(db, data)

        # Log audit trail for user registration
        await log_audit_trail(
            db=db,
            action_type="create",
            resource_type="user",
            resource_id=str(user.id),
            tenant_id=user.effective_tenant_id,
            user_id=current_user.id,
            new_values={
                "email": user.email,
                "username": user.username,
                "role": user.role,
                "is_active": user.is_active,
            },
            changes_summary=f"User {user.email} registered by admin {current_user.email}",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=True,
        )

        # Convert to response schema
        user_response = UserResponse.model_validate(user)

        return {
            "user": user_response.model_dump(),
            "message": "User registered successfully"
        }

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# =============================================================================
# Login Endpoint
# =============================================================================

@router.post(
    "/login",
    response_model=LoginResponse,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Authenticate user and return JWT tokens"
)
async def login(
    data: LoginRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Authenticate user and return JWT tokens.

    Validates email and password, and returns access token, refresh token,
    and user information.

    Includes brute-force protection with:
        - Exponential backoff between failed attempts
        - Account lockout after 5 failed attempts (15 min)

    Args:
        data: Login credentials (email, password)
        db: Database session

    Returns:
        LoginResponse: Access token, refresh token, and user data

    Raises:
        HTTPException: 401 if credentials are invalid
        HTTPException: 429 if account is locked or rate limited
    """
    email = data.email.lower()

    # Check if account is locked out
    if login_attempt_tracker.is_locked_out(email):
        remaining = login_attempt_tracker.get_remaining_lockout_seconds(email)

        # Log account lockout attempt
        await log_audit_trail(
            db=db,
            action_type="login",
            resource_type="user",
            resource_id=None,
            tenant_id=None,
            user_id=None,
            new_values={"email": email, "reason": "account_locked"},
            changes_summary=f"Login attempt blocked - account {email} is locked out",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=False,
            error_message=f"Account locked - {remaining // 60} minutes remaining",
        )

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Account temporarily locked due to too many failed attempts. "
                   f"Try again in {remaining // 60} minutes."
        )

    # Check for rate limiting (exponential backoff)
    wait_time = login_attempt_tracker.get_wait_time(email)
    if wait_time > 0:
        # Log rate limiting
        await log_audit_trail(
            db=db,
            action_type="login",
            resource_type="user",
            resource_id=None,
            tenant_id=None,
            user_id=None,
            new_values={"email": email, "reason": "rate_limited"},
            changes_summary=f"Login attempt rate limited for {email}",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=False,
            error_message=f"Rate limited - wait {int(wait_time)} seconds",
        )

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many login attempts. Please wait {int(wait_time)} seconds."
        )

    # Get user by email
    user = await user_service.get_user_by_email(db, email)

    if user is None:
        # Record failed attempt
        result = login_attempt_tracker.record_failure(email)

        # Log failed login - user not found
        await log_audit_trail(
            db=db,
            action_type="login",
            resource_type="user",
            resource_id=None,
            tenant_id=None,
            user_id=None,
            new_values={"email": email, "reason": "user_not_found"},
            changes_summary=f"Failed login attempt for non-existent user {email}",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=False,
            error_message=f"User not found - {result['attempts_remaining']} attempts remaining",
        )

        if result['locked']:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Account locked due to too many failed attempts. "
                       f"Try again in {result['wait_seconds'] // 60} minutes."
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Incorrect email or password. "
                   f"{result['attempts_remaining']} attempts remaining."
        )

    # Verify password
    if not verify_password(data.password, user.password_hash):
        # Record failed attempt
        result = login_attempt_tracker.record_failure(email)

        # Log failed login - wrong password
        await log_audit_trail(
            db=db,
            action_type="login",
            resource_type="user",
            resource_id=str(user.id),
            tenant_id=user.effective_tenant_id,
            user_id=None,  # Not authenticated yet
            new_values={"email": email, "reason": "wrong_password"},
            changes_summary=f"Failed login attempt for {email} - incorrect password",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=False,
            error_message=f"Wrong password - {result['attempts_remaining']} attempts remaining",
        )

        if result['locked']:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Account locked due to too many failed attempts. "
                       f"Try again in {result['wait_seconds'] // 60} minutes."
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Incorrect email or password. "
                   f"{result['attempts_remaining']} attempts remaining."
        )

    # Check if user is active
    if not user.is_active:
        # Don't record as failed attempt for inactive users

        # Log inactive user login attempt
        await log_audit_trail(
            db=db,
            action_type="login",
            resource_type="user",
            resource_id=str(user.id),
            tenant_id=user.effective_tenant_id,
            user_id=None,  # Not authenticated yet
            new_values={"email": email, "reason": "inactive_user"},
            changes_summary=f"Login attempt for inactive user {email}",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=False,
            error_message="User account is inactive",
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )

    # Successful login - reset attempt counter
    login_attempt_tracker.record_success(email)

    # Create tokens
    access_token = create_access_token(
        user_id=user.id,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(user_id=user.id)
    refresh_token_store.save(
        refresh_token,
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

    # Log successful login
    await log_audit_trail(
        db=db,
        action_type="login",
        resource_type="user",
        resource_id=str(user.id),
        tenant_id=user.effective_tenant_id,
        user_id=user.id,
        new_values={
            "email": user.email,
            "username": user.username,
            "role": user.role,
        },
        changes_summary=f"User {user.email} logged in successfully",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=True,
    )

    # Convert user to response schema
    user_response = UserResponse.model_validate(user)

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
        user=user_response
    )


# =============================================================================
# Token Refresh Endpoint
# =============================================================================

@router.post(
    "/refresh",
    response_model=TokenRefreshResponse,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Get a new access token using a refresh token"
)
async def refresh_token(
    data: TokenRefreshRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Refresh the access token using a refresh token.

    Validates the refresh token and issues a new access token.
    The refresh token remains valid.

    Args:
        data: Refresh token
        db: Database session

    Returns:
        TokenRefreshResponse: New access token

    Raises:
        HTTPException: 401 if refresh token is invalid or expired
    """
    # Validate refresh token is not empty
    if not data.refresh_token or not data.refresh_token.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Validate token has basic JWT structure (3 parts separated by dots)
    token_parts = data.refresh_token.split('.')
    if len(token_parts) != 3:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    try:
        payload = decode_token(data.refresh_token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user_id_str = payload.get("sub")
    token_type = payload.get("type")

    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    if token_type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )

    if not refresh_token_store.verify(data.refresh_token, user_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    refresh_token_store.revoke(data.refresh_token)

    user = await user_service.get_user_by_id(db, user_id)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Create new access token
    access_token = create_access_token(
        user_id=user.id,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    new_refresh_token = create_refresh_token(user_id=user.id)
    refresh_token_store.save(
        new_refresh_token,
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

    # Log successful token refresh
    await log_audit_trail(
        db=db,
        action_type="token_refresh",
        resource_type="user",
        resource_id=str(user.id),
        tenant_id=user.effective_tenant_id,
        user_id=user.id,
        new_values={
            "email": user.email,
        },
        changes_summary=f"Token refreshed for user {user.email}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=True,
    )

    return TokenRefreshResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


# =============================================================================
# Logout Endpoint
# =============================================================================

@router.post(
    "/logout",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Logout user",
    description="Revoke the supplied refresh token to terminate the session"
)
async def logout(
    data: TokenRefreshRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Revoke a refresh token and end the user's session.

    Args:
        data: Refresh token payload

    Returns:
        dict: Confirmation message
    """
    # Validate refresh token is not empty
    if not data.refresh_token or not data.refresh_token.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Validate token has basic JWT structure (3 parts separated by dots)
    token_parts = data.refresh_token.split('.')
    if len(token_parts) != 3:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    try:
        payload = decode_token(data.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        user_id = UUID(user_id_str)
        if not refresh_token_store.verify(data.refresh_token, user_id=user_id):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )

        refresh_token_store.revoke(data.refresh_token)

        # Get user for audit logging
        user = await user_service.get_user_by_id(db, user_id)

        # Log successful logout
        await log_audit_trail(
            db=db,
            action_type="logout",
            resource_type="user",
            resource_id=str(user_id),
            tenant_id=user.effective_tenant_id if user else None,
            user_id=user_id,
            new_values={
                "email": user.email if user else None,
            },
            changes_summary=f"User {user.email if user else user_id_str} logged out",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=True,
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token"
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )

    return {"message": "Logout successful"}


# =============================================================================
# Get Current User Endpoint
# =============================================================================

@router.get(
    "/me",
    response_model=UserResponse,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Get the currently authenticated user's information"
)
async def get_me(
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
):
    """
    Get the currently authenticated user.

    Returns the user information for the currently authenticated user
    based on the JWT token in the Authorization header.

    Args:
        current_user: Current user from JWT token (injected by dependency)

    Returns:
        UserResponse: Current user data

    Raises:
        HTTPException: 401 if not authenticated or token is invalid
    """
    return current_user


# =============================================================================
# Export
# =============================================================================

__all__ = ['router']
