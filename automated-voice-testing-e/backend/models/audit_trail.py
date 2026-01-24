"""
Audit Trail Model

Comprehensive audit logging for all configuration changes and critical system operations.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects import postgresql
from sqlalchemy import JSON

from models.base import Base

# Use JSONB for PostgreSQL, JSON for SQLite (testing)
JSONB_TYPE = JSONB().with_variant(JSON(), "sqlite")


class AuditTrail(Base):
    """
    Audit trail for tracking configuration changes and system operations.

    Records all significant system changes including:
    - LLM pricing updates
    - Pattern analysis config changes
    - User role/permission changes
    - Integration config changes
    - CI/CD config changes
    - Notification config changes

    Attributes:
        tenant_id: Organization this audit belongs to
        user_id: User who performed the action
        action_type: Type of action (create, update, delete, execute)
        resource_type: Type of resource affected (llm_pricing, pattern_config, etc.)
        resource_id: ID of the affected resource
        old_values: Previous values (for updates/deletes)
        new_values: New values (for creates/updates)
        changes_summary: Human-readable summary of changes
        ip_address: IP address of the user
        user_agent: User agent string from request
        success: Whether the action succeeded
        error_message: Error message if action failed
    """

    __test__ = False  # Prevent pytest auto-discovery
    __tablename__ = "audit_trail"

    # Primary key
    id = sa.Column(
        sa.UUID(),
        primary_key=True,
        default=uuid4,
        server_default=sa.text("gen_random_uuid()"),
    )

    # Tenant and user association
    tenant_id = sa.Column(
        sa.UUID(),
        nullable=True,  # Nullable for system-wide changes
        index=True,
        comment="Organization this audit belongs to",
    )

    user_id = sa.Column(
        sa.UUID(),
        nullable=True,  # Nullable for system/automated actions
        index=True,
        comment="User who performed the action",
    )

    # Action details
    action_type = sa.Column(
        sa.String(50),
        nullable=False,
        index=True,
        comment="Type of action (create, update, delete, execute, login, etc.)",
    )

    resource_type = sa.Column(
        sa.String(100),
        nullable=False,
        index=True,
        comment="Type of resource affected (llm_pricing, pattern_config, user, etc.)",
    )

    resource_id = sa.Column(
        sa.String(255),
        nullable=True,
        index=True,
        comment="ID of the affected resource",
    )

    # Change tracking
    old_values = sa.Column(
        JSONB_TYPE,
        nullable=True,
        comment="Previous values before change (for updates/deletes)",
    )

    new_values = sa.Column(
        JSONB_TYPE,
        nullable=True,
        comment="New values after change (for creates/updates)",
    )

    changes_summary = sa.Column(
        sa.Text(),
        nullable=True,
        comment="Human-readable summary of changes",
    )

    # Request metadata
    ip_address = sa.Column(
        sa.String(45),  # IPv6 max length
        nullable=True,
        comment="IP address of the user",
    )

    user_agent = sa.Column(
        sa.String(500),
        nullable=True,
        comment="User agent string from request",
    )

    # Success tracking
    success = sa.Column(
        sa.Boolean(),
        nullable=False,
        default=True,
        index=True,
        comment="Whether the action succeeded",
    )

    error_message = sa.Column(
        sa.Text(),
        nullable=True,
        comment="Error message if action failed",
    )

    # Timestamp
    created_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=sa.func.now(),
        index=True,
        comment="When this action occurred",
    )

    # Indexes for common queries
    __table_args__ = (
        sa.Index("ix_audit_tenant_created", "tenant_id", "created_at"),
        sa.Index("ix_audit_user_created", "user_id", "created_at"),
        sa.Index("ix_audit_resource_created", "resource_type", "resource_id", "created_at"),
        sa.Index("ix_audit_action_created", "action_type", "created_at"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "user_id": str(self.user_id) if self.user_id else None,
            "action_type": self.action_type,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "old_values": self.old_values,
            "new_values": self.new_values,
            "changes_summary": self.changes_summary,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "success": self.success,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


async def log_audit_trail(
    db,
    action_type: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    tenant_id: Optional[UUID] = None,
    user_id: Optional[UUID] = None,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    changes_summary: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    success: bool = True,
    error_message: Optional[str] = None,
) -> AuditTrail:
    """
    Create an audit trail entry.

    Args:
        db: Database session (AsyncSession)
        action_type: Type of action (create, update, delete, etc.)
        resource_type: Type of resource affected
        resource_id: ID of the affected resource
        tenant_id: Organization ID
        user_id: User who performed the action
        old_values: Previous values
        new_values: New values
        changes_summary: Human-readable summary
        ip_address: IP address
        user_agent: User agent
        success: Whether action succeeded
        error_message: Error message if failed

    Returns:
        Created AuditTrail entry
    """
    audit = AuditTrail(
        tenant_id=tenant_id,
        user_id=user_id,
        action_type=action_type,
        resource_type=resource_type,
        resource_id=resource_id,
        old_values=old_values,
        new_values=new_values,
        changes_summary=changes_summary,
        ip_address=ip_address,
        user_agent=user_agent,
        success=success,
        error_message=error_message,
    )

    db.add(audit)
    await db.flush()  # Flush to get the ID

    return audit
