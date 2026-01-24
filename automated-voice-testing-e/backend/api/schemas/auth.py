"""
Authentication Pydantic Schemas

This module defines request and response models for authentication endpoints
including login, registration, token refresh, and password management.

All schemas use Pydantic for validation and serialization.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

import re
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict

from api.auth.roles import Role, ALL_ROLES


# =============================================================================
# Password Validation Helper
# =============================================================================

def validate_password_complexity(password: str) -> str:
    """
    Validate password meets security requirements.

    Requirements:
        - Minimum 12 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character

    Args:
        password: Password to validate

    Returns:
        str: Validated password

    Raises:
        ValueError: If password doesn't meet requirements
    """
    if len(password) < 12:
        raise ValueError('Password must be at least 12 characters long')

    if not re.search(r'[A-Z]', password):
        raise ValueError('Password must contain at least one uppercase letter')

    if not re.search(r'[a-z]', password):
        raise ValueError('Password must contain at least one lowercase letter')

    if not re.search(r'\d', password):
        raise ValueError('Password must contain at least one digit')

    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;\'`~]', password):
        raise ValueError('Password must contain at least one special character')

    return password


# =============================================================================
# User Response Schema
# =============================================================================

class UserResponse(BaseModel):
    """
    User response schema for API responses.

    This schema represents user data returned in API responses.
    It excludes sensitive fields like password hashes.

    Attributes:
        id: Unique user identifier (UUID)
        email: User's email address
        username: User's username
        full_name: User's full name
        role: User's role for authorization (admin, user, etc.) - optional
        is_active: Whether the user account is active
        is_organization_owner: Whether user represents an organization
        organization_name: Organization name (if is_organization_owner)
        created_at: Timestamp when the user was created
        updated_at: Timestamp when the user was last updated (optional)

    Example:
        ```json
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "user@example.com",
            "username": "johndoe",
            "full_name": "John Doe",
            "is_active": true,
            "is_organization_owner": false,
            "created_at": "2024-01-01T00:00:00Z"
        }
        ```
    """

    id: UUID = Field(..., description="Unique user identifier")
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., description="User's username")
    full_name: str = Field(..., description="User's full name")
    tenant_id: Optional[UUID] = Field(None, description="Tenant identifier for multi-tenant deployments")
    role: Optional[Role] = Field(None, description="User's role for authorization")
    is_active: bool = Field(default=True, description="Whether the user account is active")
    is_organization_owner: bool = Field(default=False, description="Whether user represents an organization")
    organization_name: Optional[str] = Field(None, description="Organization name (if is_organization_owner)")
    created_at: datetime = Field(..., description="Timestamp when the user was created")
    updated_at: Optional[datetime] = Field(None, description="Timestamp when the user was last updated")

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Login Schemas
# =============================================================================

class LoginRequest(BaseModel):
    """
    Login request schema.

    Used to authenticate users with email and password.

    Attributes:
        email: User's email address (validated format)
        password: User's password (plain text, will be verified against hash)

    Example:
        ```json
        {
            "email": "user@example.com",
            "password": "SecurePassword123!"
        }
        ```
    """

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=1, description="User's password")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "SecurePassword123!"
                }
            ]
        }
    }


class LoginResponse(BaseModel):
    """
    Login response schema.

    Returned after successful authentication, containing tokens and user info.

    Attributes:
        access_token: JWT access token for API authentication
        refresh_token: JWT refresh token for obtaining new access tokens
        token_type: Token type (always "bearer")
        expires_in: Access token expiration time in seconds
        user: User information

    Example:
        ```json
        {
            "access_token": "eyJhbGci...",
            "refresh_token": "eyJhbGci...",
            "token_type": "bearer",
            "expires_in": 900,
            "user": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "is_active": true,
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
        ```
    """

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration time in seconds")
    user: UserResponse = Field(..., description="User information")


# =============================================================================
# Registration Schemas
# =============================================================================

class RegisterRequest(BaseModel):
    """
    User registration request schema.

    Used to create new user accounts.

    Attributes:
        email: User's email address (validated format, must be unique)
        username: Desired username (must be unique)
        password: User's password (will be hashed before storage)
        full_name: User's full name

    Validation:
        - Email must be valid format
        - Username must be at least 3 characters
        - Password must be at least 8 characters (additional rules recommended)
        - All fields are required

    Example:
        ```json
        {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "SecurePassword123!",
            "full_name": "New User"
        }
        ```
    """

    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., min_length=3, max_length=50, description="Desired username")
    password: str = Field(..., min_length=12, description="User's password (12+ chars, mixed case, digits, special)")
    full_name: str = Field(..., min_length=1, max_length=100, description="User's full name")
    role: Role = Field(default=Role.VIEWER, description="Role assigned to the user (admin only)")

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        """Validate that username contains only alphanumeric characters and underscores"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must contain only alphanumeric characters, hyphens, and underscores')
        return v

    @field_validator('password')
    @classmethod
    def password_complexity(cls, v: str) -> str:
        """Validate password meets security complexity requirements"""
        return validate_password_complexity(v)

    @field_validator("role", mode="before")
    @classmethod
    def validate_role(cls, value):
        """Ensure provided role is one of the supported pilot roles."""
        if value is None:
            return Role.VIEWER
        if isinstance(value, Role):
            return value
        if value not in ALL_ROLES:
            raise ValueError("Invalid role specified")
        return Role(value)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "newuser@example.com",
                    "username": "newuser",
                    "password": "SecurePassword123!",
                    "full_name": "New User"
                }
            ]
        }
    }


# =============================================================================
# Token Refresh Schemas
# =============================================================================

class TokenRefreshRequest(BaseModel):
    """
    Token refresh request schema.

    Used to obtain a new access token using a refresh token.

    Attributes:
        refresh_token: The refresh token obtained during login

    Example:
        ```json
        {
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        }
        ```
    """

    refresh_token: str = Field(..., description="Refresh token")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                }
            ]
        }
    }


class TokenRefreshResponse(BaseModel):
    """
    Token refresh response schema.

    Returned after successfully refreshing an access token.

    Attributes:
        access_token: New JWT access token
        token_type: Token type (always "bearer")
        expires_in: Access token expiration time in seconds

    Example:
        ```json
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "expires_in": 900
        }
        ```
    """

    access_token: str = Field(..., description="New JWT access token")
    refresh_token: str = Field(..., description="Rotated refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration time in seconds")


# =============================================================================
# Password Management Schemas
# =============================================================================

class PasswordChangeRequest(BaseModel):
    """
    Password change request schema.

    Used when an authenticated user wants to change their password.

    Attributes:
        old_password: Current password for verification
        new_password: New password to set

    Validation:
        - Old password must be provided for verification
        - New password must be at least 8 characters
        - New password should be different from old password (recommended)

    Example:
        ```json
        {
            "old_password": "OldPassword123!",
            "new_password": "NewSecurePassword456!"
        }
        ```
    """

    old_password: str = Field(..., min_length=1, description="Current password")
    new_password: str = Field(..., min_length=12, description="New password (12+ chars, mixed case, digits, special)")

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str, info) -> str:
        """Validate password complexity and ensure different from old password"""
        # Check complexity
        v = validate_password_complexity(v)
        # Check different from old
        if info.data.get('old_password') and v == info.data['old_password']:
            raise ValueError('New password must be different from old password')
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "old_password": "OldPassword123!",
                    "new_password": "NewSecurePassword456!"
                }
            ]
        }
    }


class PasswordResetRequest(BaseModel):
    """
    Password reset request schema.

    Used to initiate a password reset flow (typically sends reset email).

    Attributes:
        email: Email address of the account to reset

    Example:
        ```json
        {
            "email": "user@example.com"
        }
        ```
    """

    email: EmailStr = Field(..., description="Email address for password reset")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@example.com"
                }
            ]
        }
    }


class PasswordResetConfirm(BaseModel):
    """
    Password reset confirmation schema.

    Used to complete password reset with a reset token.

    Attributes:
        token: Password reset token from email
        new_password: New password to set

    Example:
        ```json
        {
            "token": "reset-token-from-email",
            "new_password": "NewSecurePassword123!"
        }
        ```
    """

    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=12, description="New password (12+ chars, mixed case, digits, special)")

    @field_validator('new_password')
    @classmethod
    def password_complexity(cls, v: str) -> str:
        """Validate password meets security complexity requirements"""
        return validate_password_complexity(v)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "token": "abcdef123456",
                    "new_password": "NewSecurePassword123!"
                }
            ]
        }
    }


# =============================================================================
# Export public API
# =============================================================================

__all__ = [
    'UserResponse',
    'LoginRequest',
    'LoginResponse',
    'RegisterRequest',
    'TokenRefreshRequest',
    'TokenRefreshResponse',
    'PasswordChangeRequest',
    'PasswordResetRequest',
    'PasswordResetConfirm',
]
