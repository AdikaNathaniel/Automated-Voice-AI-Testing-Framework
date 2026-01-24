"""
Unit tests for AuditTrail model and log_audit_trail helper function.

Tests core audit trail functionality including:
- Model creation and validation
- Helper function behavior
- Field constraints and indexing
- to_dict serialization
"""

import pytest
from uuid import uuid4
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.audit_trail import AuditTrail, log_audit_trail


class TestAuditTrailModel:
    """Test suite for AuditTrail model."""

    @pytest.mark.asyncio
    async def test_create_basic_audit_entry(self, db_session: AsyncSession):
        """Test creating basic audit trail entry."""
        # Arrange
        tenant_id = uuid4()
        user_id = uuid4()

        # Act
        audit = AuditTrail(
            tenant_id=tenant_id,
            user_id=user_id,
            action_type="create",
            resource_type="test_resource",
            resource_id="resource-123",
            changes_summary="Test audit entry created",
            success=True,
        )

        db_session.add(audit)
        await db_session.flush()

        # Assert
        assert audit.id is not None
        assert audit.tenant_id == tenant_id
        assert audit.user_id == user_id
        assert audit.action_type == "create"
        assert audit.resource_type == "test_resource"
        assert audit.resource_id == "resource-123"
        assert audit.success is True
        assert audit.created_at is not None

    @pytest.mark.asyncio
    async def test_audit_with_old_new_values(self, db_session: AsyncSession):
        """Test audit entry with old and new values tracking."""
        # Arrange
        old_values = {"status": "pending", "severity": "low"}
        new_values = {"status": "resolved", "severity": "high"}

        # Act
        audit = AuditTrail(
            tenant_id=uuid4(),
            user_id=uuid4(),
            action_type="update",
            resource_type="defect",
            resource_id="defect-456",
            old_values=old_values,
            new_values=new_values,
            changes_summary="Defect status updated",
            success=True,
        )

        db_session.add(audit)
        await db_session.flush()

        # Assert
        assert audit.old_values == old_values
        assert audit.new_values == new_values
        assert audit.old_values["status"] == "pending"
        assert audit.new_values["status"] == "resolved"

    @pytest.mark.asyncio
    async def test_audit_with_request_metadata(self, db_session: AsyncSession):
        """Test audit entry with IP address and user agent."""
        # Arrange
        ip_address = "192.168.1.100"
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

        # Act
        audit = AuditTrail(
            tenant_id=uuid4(),
            user_id=uuid4(),
            action_type="login",
            resource_type="user",
            resource_id="user-789",
            ip_address=ip_address,
            user_agent=user_agent,
            changes_summary="User logged in successfully",
            success=True,
        )

        db_session.add(audit)
        await db_session.flush()

        # Assert
        assert audit.ip_address == ip_address
        assert audit.user_agent == user_agent

    @pytest.mark.asyncio
    async def test_audit_failed_action(self, db_session: AsyncSession):
        """Test audit entry for failed action."""
        # Arrange
        error_msg = "Invalid credentials"

        # Act
        audit = AuditTrail(
            tenant_id=None,  # No tenant for failed login
            user_id=None,  # No user for failed login
            action_type="login",
            resource_type="user",
            resource_id="unknown@example.com",
            success=False,
            error_message=error_msg,
            changes_summary="Failed login attempt",
        )

        db_session.add(audit)
        await db_session.flush()

        # Assert
        assert audit.success is False
        assert audit.error_message == error_msg
        assert audit.tenant_id is None
        assert audit.user_id is None

    @pytest.mark.asyncio
    async def test_to_dict_serialization(self, db_session: AsyncSession):
        """Test to_dict serialization method."""
        # Arrange
        tenant_id = uuid4()
        user_id = uuid4()
        old_values = {"key": "old_value"}
        new_values = {"key": "new_value"}

        audit = AuditTrail(
            tenant_id=tenant_id,
            user_id=user_id,
            action_type="update",
            resource_type="config",
            resource_id="config-123",
            old_values=old_values,
            new_values=new_values,
            changes_summary="Config updated",
            ip_address="10.0.0.1",
            user_agent="Test Agent",
            success=True,
        )

        db_session.add(audit)
        await db_session.flush()

        # Act
        result = audit.to_dict()

        # Assert
        assert result["id"] == str(audit.id)
        assert result["tenant_id"] == str(tenant_id)
        assert result["user_id"] == str(user_id)
        assert result["action_type"] == "update"
        assert result["resource_type"] == "config"
        assert result["resource_id"] == "config-123"
        assert result["old_values"] == old_values
        assert result["new_values"] == new_values
        assert result["changes_summary"] == "Config updated"
        assert result["ip_address"] == "10.0.0.1"
        assert result["user_agent"] == "Test Agent"
        assert result["success"] is True
        assert result["error_message"] is None
        assert result["created_at"] is not None

    @pytest.mark.asyncio
    async def test_nullable_fields(self, db_session: AsyncSession):
        """Test that optional fields can be null."""
        # Act
        audit = AuditTrail(
            action_type="system_action",
            resource_type="system",
            success=True,
            # All optional fields omitted
        )

        db_session.add(audit)
        await db_session.flush()

        # Assert
        assert audit.tenant_id is None
        assert audit.user_id is None
        assert audit.resource_id is None
        assert audit.old_values is None
        assert audit.new_values is None
        assert audit.changes_summary is None
        assert audit.ip_address is None
        assert audit.user_agent is None
        assert audit.error_message is None


class TestLogAuditTrailHelper:
    """Test suite for log_audit_trail helper function."""

    @pytest.mark.asyncio
    async def test_log_audit_trail_basic(self, db_session: AsyncSession):
        """Test basic audit trail logging."""
        # Arrange
        tenant_id = uuid4()
        user_id = uuid4()

        # Act
        audit = await log_audit_trail(
            db=db_session,
            action_type="create",
            resource_type="test_suite",
            resource_id="suite-123",
            tenant_id=tenant_id,
            user_id=user_id,
            changes_summary="Test suite created",
        )

        # Assert
        assert audit is not None
        assert audit.id is not None
        assert audit.tenant_id == tenant_id
        assert audit.user_id == user_id
        assert audit.action_type == "create"
        assert audit.resource_type == "test_suite"
        assert audit.resource_id == "suite-123"
        assert audit.changes_summary == "Test suite created"
        assert audit.success is True

    @pytest.mark.asyncio
    async def test_log_audit_trail_with_values(self, db_session: AsyncSession):
        """Test audit logging with old and new values."""
        # Arrange
        old_vals = {"name": "Old Name", "status": "active"}
        new_vals = {"name": "New Name", "status": "inactive"}

        # Act
        audit = await log_audit_trail(
            db=db_session,
            action_type="update",
            resource_type="user",
            resource_id="user-456",
            tenant_id=uuid4(),
            user_id=uuid4(),
            old_values=old_vals,
            new_values=new_vals,
            changes_summary="User updated: name changed, deactivated",
        )

        # Assert
        assert audit.old_values == old_vals
        assert audit.new_values == new_vals

    @pytest.mark.asyncio
    async def test_log_audit_trail_with_metadata(self, db_session: AsyncSession):
        """Test audit logging with request metadata."""
        # Act
        audit = await log_audit_trail(
            db=db_session,
            action_type="login",
            resource_type="user",
            resource_id="user-789",
            tenant_id=uuid4(),
            user_id=uuid4(),
            ip_address="203.0.113.42",
            user_agent="Chrome/120.0.0.0",
            changes_summary="Successful login",
        )

        # Assert
        assert audit.ip_address == "203.0.113.42"
        assert audit.user_agent == "Chrome/120.0.0.0"

    @pytest.mark.asyncio
    async def test_log_audit_trail_failure(self, db_session: AsyncSession):
        """Test audit logging for failed operations."""
        # Act
        audit = await log_audit_trail(
            db=db_session,
            action_type="delete",
            resource_type="defect",
            resource_id="defect-999",
            tenant_id=uuid4(),
            user_id=uuid4(),
            success=False,
            error_message="Defect not found",
            changes_summary="Failed to delete defect",
        )

        # Assert
        assert audit.success is False
        assert audit.error_message == "Defect not found"

    @pytest.mark.asyncio
    async def test_log_audit_trail_persisted(self, db_session: AsyncSession):
        """Test that logged audit trail is persisted to database."""
        # Arrange
        resource_id = f"test-{uuid4()}"

        # Act
        audit = await log_audit_trail(
            db=db_session,
            action_type="create",
            resource_type="integration",
            resource_id=resource_id,
            tenant_id=uuid4(),
            user_id=uuid4(),
            changes_summary="Integration configured",
        )

        audit_id = audit.id
        await db_session.commit()

        # Query from database
        result = await db_session.execute(
            select(AuditTrail).where(AuditTrail.id == audit_id)
        )
        retrieved_audit = result.scalar_one()

        # Assert
        assert retrieved_audit is not None
        assert retrieved_audit.id == audit_id
        assert retrieved_audit.resource_id == resource_id
        assert retrieved_audit.action_type == "create"

    @pytest.mark.asyncio
    async def test_log_audit_trail_default_success(self, db_session: AsyncSession):
        """Test that success defaults to True."""
        # Act
        audit = await log_audit_trail(
            db=db_session,
            action_type="update",
            resource_type="config",
            tenant_id=uuid4(),
            user_id=uuid4(),
        )

        # Assert
        assert audit.success is True
        assert audit.error_message is None

    @pytest.mark.asyncio
    async def test_log_audit_trail_optional_params(self, db_session: AsyncSession):
        """Test that optional parameters can be omitted."""
        # Act - minimal required params
        audit = await log_audit_trail(
            db=db_session,
            action_type="execute",
            resource_type="scenario",
        )

        # Assert
        assert audit.action_type == "execute"
        assert audit.resource_type == "scenario"
        assert audit.tenant_id is None
        assert audit.user_id is None
        assert audit.resource_id is None


class TestAuditTrailIndexing:
    """Test suite for audit trail database indexing."""

    @pytest.mark.asyncio
    async def test_tenant_created_index(self, db_session: AsyncSession):
        """Test querying by tenant_id and created_at uses index."""
        # Arrange
        tenant_id = uuid4()

        for i in range(5):
            await log_audit_trail(
                db=db_session,
                action_type="test",
                resource_type="test",
                tenant_id=tenant_id,
            )

        await db_session.commit()

        # Act - Query should use ix_audit_tenant_created index
        result = await db_session.execute(
            select(AuditTrail)
            .where(AuditTrail.tenant_id == tenant_id)
            .order_by(AuditTrail.created_at.desc())
        )
        audits = result.scalars().all()

        # Assert
        assert len(audits) == 5
        assert all(a.tenant_id == tenant_id for a in audits)

    @pytest.mark.asyncio
    async def test_user_created_index(self, db_session: AsyncSession):
        """Test querying by user_id and created_at uses index."""
        # Arrange
        user_id = uuid4()

        for i in range(3):
            await log_audit_trail(
                db=db_session,
                action_type="test",
                resource_type="test",
                user_id=user_id,
            )

        await db_session.commit()

        # Act - Query should use ix_audit_user_created index
        result = await db_session.execute(
            select(AuditTrail)
            .where(AuditTrail.user_id == user_id)
            .order_by(AuditTrail.created_at.desc())
        )
        audits = result.scalars().all()

        # Assert
        assert len(audits) == 3
        assert all(a.user_id == user_id for a in audits)

    @pytest.mark.asyncio
    async def test_resource_created_index(self, db_session: AsyncSession):
        """Test querying by resource_type, resource_id, created_at."""
        # Arrange
        resource_id = "resource-123"

        for i in range(4):
            await log_audit_trail(
                db=db_session,
                action_type="update",
                resource_type="defect",
                resource_id=resource_id,
            )

        await db_session.commit()

        # Act - Query should use ix_audit_resource_created index
        result = await db_session.execute(
            select(AuditTrail)
            .where(AuditTrail.resource_type == "defect")
            .where(AuditTrail.resource_id == resource_id)
            .order_by(AuditTrail.created_at.desc())
        )
        audits = result.scalars().all()

        # Assert
        assert len(audits) == 4
        assert all(a.resource_type == "defect" for a in audits)
        assert all(a.resource_id == resource_id for a in audits)

    @pytest.mark.asyncio
    async def test_action_created_index(self, db_session: AsyncSession):
        """Test querying by action_type and created_at."""
        # Arrange
        for i in range(6):
            await log_audit_trail(
                db=db_session,
                action_type="login",
                resource_type="user",
            )

        await db_session.commit()

        # Act - Query should use ix_audit_action_created index
        result = await db_session.execute(
            select(AuditTrail)
            .where(AuditTrail.action_type == "login")
            .order_by(AuditTrail.created_at.desc())
        )
        audits = result.scalars().all()

        # Assert
        assert len(audits) >= 6  # May have others from previous tests
        login_audits = [a for a in audits if a.action_type == "login"]
        assert len(login_audits) >= 6
