"""
Category SQLAlchemy model for organizing test scenarios.

This model allows administrators to create and manage custom categories
for organizing test scenarios. Categories can be assigned to scenarios
and help with filtering, grouping, and reporting.
"""

from __future__ import annotations

from typing import Any, Dict
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import UniqueConstraint

from models.base import Base, GUID, BaseModel


class Category(Base, BaseModel):
    """ORM representation of scenario categories."""

    __test__ = False  # Prevent pytest from auto-discovering this as a test
    __tablename__ = "categories"

    # Ensure category names are unique within a tenant
    __table_args__ = (
        UniqueConstraint('name', 'tenant_id', name='uq_category_name_tenant'),
    )

    name = sa.Column(
        sa.String(length=100),
        nullable=False,
        index=True,
        comment="Category name (unique within tenant)",
    )

    display_name = sa.Column(
        sa.String(length=150),
        nullable=True,
        comment="Human-readable display name for the category",
    )

    description = sa.Column(
        sa.Text(),
        nullable=True,
        comment="Description of what scenarios belong to this category",
    )

    color = sa.Column(
        sa.String(length=7),
        nullable=True,
        comment="Hex color code for UI display (e.g., #FF5733)",
    )

    icon = sa.Column(
        sa.String(length=50),
        nullable=True,
        comment="Icon name/identifier for UI display",
    )

    is_active = sa.Column(
        sa.Boolean(),
        default=True,
        nullable=False,
        comment="Whether this category is active and available for use",
    )

    is_system = sa.Column(
        sa.Boolean(),
        default=False,
        nullable=False,
        comment="Whether this is a system-defined category (cannot be deleted)",
    )

    tenant_id = sa.Column(
        GUID(),
        nullable=True,
        index=True,
        comment="Tenant identifier for multi-tenant scoping",
    )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert category to dictionary for API responses.

        Returns:
            Dictionary with all category fields
        """
        return {
            "id": str(self.id),
            "name": self.name,
            "display_name": self.display_name or self.name,
            "description": self.description,
            "color": self.color,
            "icon": self.icon,
            "is_active": self.is_active,
            "is_system": self.is_system,
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        """String representation of the category."""
        return f"<Category(id={self.id}, name='{self.name}')>"
