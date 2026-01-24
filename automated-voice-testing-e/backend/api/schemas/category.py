"""
Pydantic schemas for Category API endpoints.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class CategoryBase(BaseModel):
    """Base schema for category data."""

    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    display_name: Optional[str] = Field(None, max_length=150, description="Human-readable display name")
    description: Optional[str] = Field(None, description="Description of the category")
    color: Optional[str] = Field(None, max_length=7, pattern="^#[0-9A-Fa-f]{6}$", description="Hex color code")
    icon: Optional[str] = Field(None, max_length=50, description="Icon name/identifier")
    is_active: bool = Field(True, description="Whether category is active")


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""

    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    display_name: Optional[str] = Field(None, max_length=150)
    description: Optional[str] = None
    color: Optional[str] = Field(None, max_length=7, pattern="^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None

    @field_validator("name", "display_name", "description", "color", "icon")
    @classmethod
    def empty_string_to_none(cls, v: Optional[str]) -> Optional[str]:
        """Convert empty strings to None."""
        if v == "":
            return None
        return v


class CategoryResponse(CategoryBase):
    """Schema for category response."""

    id: UUID
    is_system: bool
    tenant_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    scenario_count: int = Field(0, description="Number of scenarios using this category")

    model_config = {"from_attributes": True}


class CategoryListResponse(BaseModel):
    """Schema for list of categories."""

    categories: list[CategoryResponse]
    total: int = Field(..., description="Total number of categories")


class CategoryDeleteResponse(BaseModel):
    """Schema for category deletion response."""

    success: bool
    message: str
