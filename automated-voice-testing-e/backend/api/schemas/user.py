"""
User Management Pydantic Schemas

Schemas for super admin user management operations including:
- Listing users with filtering and pagination
- Creating users (by admin)
- Updating users
- User detail responses
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict

from api.auth.roles import Role, ALL_ROLES
from api.schemas.auth import validate_password_complexity


# =============================================================================
# User Admin Schemas
# =============================================================================


class UserCreate(BaseModel):
    """
    Schema for admin-created users.

    Allows admins to create users with specific roles and organization assignment.
    """

    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=12, description="Password (12+ chars)")
    full_name: str = Field(..., min_length=1, max_length=100, description="Full name")
    role: Role = Field(default=Role.VIEWER, description="Role to assign")
    is_active: bool = Field(default=True, description="Whether user is active")
    tenant_id: Optional[UUID] = Field(
        None, description="Organization ID to assign user to"
    )
    language_proficiencies: Optional[List[str]] = Field(
        None, description="Language codes user is proficient in"
    )

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        """Validate username format."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError(
                'Username must contain only alphanumeric characters, '
                'hyphens, and underscores'
            )
        return v

    @field_validator('password')
    @classmethod
    def password_complexity(cls, v: str) -> str:
        """Validate password complexity."""
        return validate_password_complexity(v)

    @field_validator("role", mode="before")
    @classmethod
    def validate_role(cls, value):
        """Ensure provided role is valid."""
        if value is None:
            return Role.VIEWER
        if isinstance(value, Role):
            return value
        if value not in ALL_ROLES:
            raise ValueError("Invalid role specified")
        return Role(value)

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "email": "newuser@example.com",
                    "username": "newuser",
                    "password": "SecurePassword123!",
                    "full_name": "New User",
                    "role": "viewer",
                    "is_active": True,
                }
            ]
        }
    )


class UserUpdate(BaseModel):
    """
    Schema for updating user details.

    All fields are optional - only provided fields will be updated.
    """

    email: Optional[EmailStr] = Field(None, description="User's email address")
    username: Optional[str] = Field(
        None, min_length=3, max_length=50, description="Username"
    )
    full_name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Full name"
    )
    role: Optional[Role] = Field(None, description="Role to assign")
    is_active: Optional[bool] = Field(None, description="Whether user is active")
    tenant_id: Optional[UUID] = Field(
        None, description="Organization ID (null to remove)"
    )
    language_proficiencies: Optional[List[str]] = Field(
        None, description="Language codes user is proficient in"
    )

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: Optional[str]) -> Optional[str]:
        """Validate username format if provided."""
        if v is None:
            return v
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError(
                'Username must contain only alphanumeric characters, '
                'hyphens, and underscores'
            )
        return v

    @field_validator("role", mode="before")
    @classmethod
    def validate_role(cls, value):
        """Ensure provided role is valid."""
        if value is None:
            return None
        if isinstance(value, Role):
            return value
        if value not in ALL_ROLES:
            raise ValueError("Invalid role specified")
        return Role(value)

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "full_name": "Updated Name",
                    "role": "qa_lead",
                    "is_active": True,
                }
            ]
        }
    )


class UserPasswordReset(BaseModel):
    """Schema for admin-initiated password reset."""

    new_password: str = Field(..., min_length=12, description="New password")

    @field_validator('new_password')
    @classmethod
    def password_complexity(cls, v: str) -> str:
        """Validate password complexity."""
        return validate_password_complexity(v)


class UserDetailResponse(BaseModel):
    """
    Detailed user response for admin views.

    Includes additional fields not shown in regular UserResponse.
    """

    id: UUID = Field(..., description="User ID")
    email: EmailStr = Field(..., description="Email address")
    username: str = Field(..., description="Username")
    full_name: str = Field(..., description="Full name")
    role: Optional[Role] = Field(None, description="User role")
    is_active: bool = Field(default=True, description="Whether user is active")
    tenant_id: Optional[UUID] = Field(None, description="Organization ID")
    is_organization_owner: bool = Field(
        default=False, description="Whether user owns an organization"
    )
    organization_name: Optional[str] = Field(
        None, description="Organization name (if owner)"
    )
    language_proficiencies: Optional[List[str]] = Field(
        None, description="Language proficiencies"
    )
    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """Paginated list of users for admin view."""

    items: List[UserDetailResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")


class UserStats(BaseModel):
    """User statistics for admin dashboard."""

    total_users: int = Field(..., description="Total number of users")
    active_users: int = Field(..., description="Number of active users")
    inactive_users: int = Field(..., description="Number of inactive users")
    users_by_role: dict = Field(..., description="User count by role")
    users_by_organization: int = Field(
        ..., description="Users belonging to organizations"
    )
    individual_users: int = Field(..., description="Users not in organizations")


# =============================================================================
# Export
# =============================================================================

__all__ = [
    'UserCreate',
    'UserUpdate',
    'UserPasswordReset',
    'UserDetailResponse',
    'UserListResponse',
    'UserStats',
]
