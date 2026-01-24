"""
Organization Pydantic Schemas

This module defines request and response models for organization management endpoints.
Organizations allow grouping users under a shared tenant for multi-tenant data isolation.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from api.auth.roles import Role


class OrganizationCreate(BaseModel):
    """Request schema for creating a new organization."""

    name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Organization name"
    )
    admin_email: EmailStr = Field(
        ...,
        description="Email for the organization admin account"
    )
    admin_username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Username for the organization admin account"
    )
    admin_password: str = Field(
        ...,
        min_length=12,
        description="Password for the organization admin account (min 12 chars)"
    )
    admin_full_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Full name for the organization admin"
    )
    settings: Optional[Dict[str, Any]] = Field(
        None,
        description="Organization settings (features, limits, etc.)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Acme Corporation",
                    "admin_email": "admin@acme.com",
                    "admin_username": "acme_admin",
                    "admin_password": "SecurePass123!",
                    "admin_full_name": "Acme Administrator",
                    "settings": {
                        "max_users": 100,
                        "features": ["edge_cases", "knowledge_base"]
                    }
                }
            ]
        }
    }


class OrganizationUpdate(BaseModel):
    """Request schema for updating an organization."""

    name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=255,
        description="New organization name"
    )
    settings: Optional[Dict[str, Any]] = Field(
        None,
        description="Settings to merge with existing settings"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Whether the organization is active"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Acme Corp Updated",
                    "settings": {"max_users": 200},
                    "is_active": True
                }
            ]
        }
    }


class OrganizationResponse(BaseModel):
    """Response schema for organization data."""

    id: UUID = Field(..., description="Organization ID (same as owner user ID)")
    name: str = Field(..., description="Organization name")
    admin_email: str = Field(..., description="Organization admin email")
    admin_username: str = Field(..., description="Organization admin username")
    settings: Optional[Dict[str, Any]] = Field(None, description="Organization settings")
    is_active: bool = Field(..., description="Whether organization is active")
    member_count: int = Field(0, description="Number of members in the organization")
    created_at: datetime = Field(..., description="When the organization was created")
    updated_at: Optional[datetime] = Field(None, description="When last updated")

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_user(cls, user, member_count: int = 0) -> "OrganizationResponse":
        """Create response from a User model that is an organization owner."""
        return cls(
            id=user.id,
            name=user.organization_name or user.username,
            admin_email=user.email,
            admin_username=user.username,
            settings=user.organization_settings,
            is_active=user.is_active,
            member_count=member_count,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class OrganizationMemberAdd(BaseModel):
    """Request schema for adding a member to an organization."""

    user_id: UUID = Field(..., description="ID of the user to add")
    role: Role = Field(
        default=Role.VIEWER,
        description="Role to assign to the user in the organization"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "550e8400-e29b-41d4-a716-446655440000",
                    "role": "qa_lead"
                }
            ]
        }
    }


class OrganizationMemberResponse(BaseModel):
    """Response schema for organization member data."""

    id: UUID = Field(..., description="User ID")
    email: str = Field(..., description="User's email")
    username: str = Field(..., description="User's username")
    full_name: Optional[str] = Field(None, description="User's full name")
    role: Optional[str] = Field(None, description="User's role in the organization")
    is_active: bool = Field(..., description="Whether user is active")
    joined_at: datetime = Field(..., description="When user was added to org")

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_user(cls, user) -> "OrganizationMemberResponse":
        """Create response from a User model."""
        return cls(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            joined_at=user.updated_at or user.created_at,
        )


class OrganizationListResponse(BaseModel):
    """Paginated list response for organizations."""

    items: List[OrganizationResponse] = Field(..., description="List of organizations")
    total: int = Field(..., description="Total number of organizations")
    page: int = Field(1, description="Current page")
    page_size: int = Field(20, description="Items per page")


class OrganizationMemberListResponse(BaseModel):
    """Paginated list response for organization members."""

    items: List[OrganizationMemberResponse] = Field(..., description="List of members")
    total: int = Field(..., description="Total number of members")
    organization_id: UUID = Field(..., description="Organization ID")
    organization_name: str = Field(..., description="Organization name")


__all__ = [
    'OrganizationCreate',
    'OrganizationUpdate',
    'OrganizationResponse',
    'OrganizationMemberAdd',
    'OrganizationMemberResponse',
    'OrganizationListResponse',
    'OrganizationMemberListResponse',
]
