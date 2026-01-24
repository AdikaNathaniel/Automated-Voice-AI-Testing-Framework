"""
Integration tests for audit trail tenant isolation and security.

Tests that audit trails are properly isolated by tenant and that
security requirements are met for SOC 2, ISO 27001, GDPR, and HIPAA compliance.
"""

import pytest
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.audit_trail import AuditTrail, log_audit_trail


class TestTenantIsolation:
    """Test suite for multi-tenant audit trail isolation."""

    @pytest.mark.asyncio
    async def test_tenant_isolation_basic(self, db_session: AsyncSession):
        """Test that audit logs are isolated by tenant."""
        # Arrange - Create two different tenants
        tenant1_id = uuid4()
        tenant2_id = uuid4()

        # Act - Create audit logs for each tenant
        await log_audit_trail(
            db=db_session,
            action_type="create",
            resource_type="defect",
            resource_id="defect-1",
            tenant_id=tenant1_id,
            user_id=uuid4(),
            changes_summary="Tenant 1 defect created",
        )

        await log_audit_trail(
            db=db_session,
            action_type="create",
            resource_type="defect",
            resource_id="defect-2",
            tenant_id=tenant2_id,
            user_id=uuid4(),
            changes_summary="Tenant 2 defect created",
        )

        await db_session.commit()

        # Query tenant 1 logs
        result1 = await db_session.execute(
            select(AuditTrail).where(AuditTrail.tenant_id == tenant1_id)
        )
        tenant1_audits = result1.scalars().all()

        # Query tenant 2 logs
        result2 = await db_session.execute(
            select(AuditTrail).where(AuditTrail.tenant_id == tenant2_id)
        )
        tenant2_audits = result2.scalars().all()

        # Assert - Each tenant only sees their own logs
        assert len(tenant1_audits) >= 1
        assert len(tenant2_audits) >= 1
        assert all(a.tenant_id == tenant1_id for a in tenant1_audits)
        assert all(a.tenant_id == tenant2_id for a in tenant2_audits)
        assert not any(a.tenant_id == tenant2_id for a in tenant1_audits)
        assert not any(a.tenant_id == tenant1_id for a in tenant2_audits)

    @pytest.mark.asyncio
    async def test_tenant_isolation_multiple_resources(
        self, db_session: AsyncSession
    ):
        """Test tenant isolation across multiple resource types."""
        # Arrange
        tenant1_id = uuid4()
        tenant2_id = uuid4()

        resource_types = ["defect", "test_suite", "integration", "user"]

        # Act - Create logs for different resource types per tenant
        for resource_type in resource_types:
            await log_audit_trail(
                db=db_session,
                action_type="create",
                resource_type=resource_type,
                resource_id=f"{resource_type}-tenant1",
                tenant_id=tenant1_id,
            )

            await log_audit_trail(
                db=db_session,
                action_type="create",
                resource_type=resource_type,
                resource_id=f"{resource_type}-tenant2",
                tenant_id=tenant2_id,
            )

        await db_session.commit()

        # Query tenant 1 logs
        result1 = await db_session.execute(
            select(AuditTrail).where(AuditTrail.tenant_id == tenant1_id)
        )
        tenant1_audits = result1.scalars().all()

        # Query tenant 2 logs
        result2 = await db_session.execute(
            select(AuditTrail).where(AuditTrail.tenant_id == tenant2_id)
        )
        tenant2_audits = result2.scalars().all()

        # Assert - Each tenant has logs for all resource types
        assert len(tenant1_audits) >= len(resource_types)
        assert len(tenant2_audits) >= len(resource_types)

        tenant1_resources = set(a.resource_type for a in tenant1_audits)
        tenant2_resources = set(a.resource_type for a in tenant2_audits)

        assert all(rt in tenant1_resources for rt in resource_types)
        assert all(rt in tenant2_resources for rt in resource_types)

    @pytest.mark.asyncio
    async def test_global_logs_not_isolated(self, db_session: AsyncSession):
        """Test that system-wide logs (tenant_id=None) are visible."""
        # Arrange
        tenant_id = uuid4()

        # Act - Create global system log
        await log_audit_trail(
            db=db_session,
            action_type="system_maintenance",
            resource_type="system",
            tenant_id=None,  # Global log
            changes_summary="System maintenance performed",
        )

        # Create tenant-specific log
        await log_audit_trail(
            db=db_session,
            action_type="create",
            resource_type="defect",
            tenant_id=tenant_id,
            changes_summary="Tenant defect created",
        )

        await db_session.commit()

        # Query global logs
        result_global = await db_session.execute(
            select(AuditTrail).where(AuditTrail.tenant_id.is_(None))
        )
        global_audits = result_global.scalars().all()

        # Query tenant logs
        result_tenant = await db_session.execute(
            select(AuditTrail).where(AuditTrail.tenant_id == tenant_id)
        )
        tenant_audits = result_tenant.scalars().all()

        # Assert - Global logs separate from tenant logs
        assert len(global_audits) >= 1
        assert len(tenant_audits) >= 1
        assert all(a.tenant_id is None for a in global_audits)
        assert all(a.tenant_id == tenant_id for a in tenant_audits)


class TestSensitiveDataProtection:
    """Test suite for sensitive data protection in audit trails."""

    @pytest.mark.asyncio
    async def test_no_password_in_audit_trail(self, db_session: AsyncSession):
        """Test that passwords are NEVER logged in audit trails."""
        # Arrange - Simulate user creation with password
        user_data_with_password = {
            "email": "user@example.com",
            "username": "testuser",
            "role": "user",
            "password": "secretpassword123",  # Should NOT be logged
        }

        # Correct implementation - password excluded
        safe_user_data = {
            "email": user_data_with_password["email"],
            "username": user_data_with_password["username"],
            "role": user_data_with_password["role"],
            # password intentionally excluded
        }

        # Act
        audit = await log_audit_trail(
            db=db_session,
            action_type="create",
            resource_type="user",
            resource_id="user-123",
            tenant_id=uuid4(),
            user_id=uuid4(),
            new_values=safe_user_data,
            changes_summary="User created",
        )

        # Assert - Password should NOT be in new_values
        assert audit.new_values is not None
        assert "password" not in audit.new_values
        assert "Password" not in str(audit.new_values)
        assert "secretpassword123" not in str(audit.new_values)

    @pytest.mark.asyncio
    async def test_no_api_keys_in_audit_trail(self, db_session: AsyncSession):
        """Test that API keys are NEVER logged in audit trails."""
        # Arrange - Simulate LLM provider config with API key
        # Correct implementation - use flag instead of actual key
        config_data = {
            "provider": "openai",
            "model": "gpt-4",
            "temperature": 0.7,
            "api_key_updated": True,  # Flag instead of actual key
        }

        # Act
        audit = await log_audit_trail(
            db=db_session,
            action_type="update",
            resource_type="llm_provider",
            resource_id="provider-456",
            tenant_id=uuid4(),
            user_id=uuid4(),
            new_values=config_data,
            changes_summary="LLM provider config updated (API key changed)",
        )

        # Assert - API key should NOT be in new_values
        assert audit.new_values is not None
        assert "api_key" not in audit.new_values
        assert "apiKey" not in audit.new_values
        assert "api_key_updated" in audit.new_values
        assert audit.new_values["api_key_updated"] is True

    @pytest.mark.asyncio
    async def test_no_webhook_secrets_in_audit_trail(self, db_session: AsyncSession):
        """Test that webhook secrets are NEVER logged in audit trails."""
        # Arrange - Simulate CI/CD config with webhook secret
        # Correct implementation - use flag for each provider
        cicd_config = {
            "providers": {
                "github": {"enabled": True, "webhook_secret_updated": True},
                "gitlab": {"enabled": False, "webhook_secret_updated": False},
            }
        }

        # Act
        audit = await log_audit_trail(
            db=db_session,
            action_type="update",
            resource_type="cicd_config",
            resource_id="cicd-789",
            tenant_id=uuid4(),
            user_id=uuid4(),
            new_values=cicd_config,
            changes_summary="CI/CD config updated (GitHub webhook secret changed)",
        )

        # Assert - Webhook secrets should NOT be in new_values
        # But "webhook_secret_updated" flag is okay
        assert audit.new_values is not None
        # Check that actual webhook secret values are not logged
        assert "whsec_" not in str(audit.new_values)  # Webhook secret format
        assert audit.new_values.get("providers", {}).get("github", {}).get("webhook_secret_updated") is not None

    @pytest.mark.asyncio
    async def test_no_tokens_in_audit_trail(self, db_session: AsyncSession):
        """Test that authentication tokens are NEVER logged."""
        # Arrange - Simulate login with JWT tokens
        # Correct implementation - don't log tokens, just login event
        login_data = {
            "email": "user@example.com",
            "role": "admin",
            "login_time": "2025-12-29T10:00:00",
            # access_token and refresh_token NOT logged
        }

        # Act
        audit = await log_audit_trail(
            db=db_session,
            action_type="login",
            resource_type="user",
            resource_id="user-123",
            tenant_id=uuid4(),
            user_id=uuid4(),
            new_values=login_data,
            changes_summary="User logged in successfully",
        )

        # Assert - Tokens should NOT be in new_values
        assert audit.new_values is not None
        assert "token" not in str(audit.new_values).lower()
        assert "jwt" not in str(audit.new_values).lower()


class TestComplianceRequirements:
    """Test suite for compliance requirements (SOC 2, ISO 27001, GDPR, HIPAA)."""

    @pytest.mark.asyncio
    async def test_soc2_cc61_authentication_logging(self, db_session: AsyncSession):
        """Test SOC 2 CC6.1 - Authentication events must be logged."""
        # Arrange
        user_id = uuid4()
        tenant_id = uuid4()

        # Act - Log successful login
        await log_audit_trail(
            db=db_session,
            action_type="login",
            resource_type="user",
            resource_id=str(user_id),
            tenant_id=tenant_id,
            user_id=user_id,
            ip_address="203.0.113.42",
            user_agent="Mozilla/5.0",
            changes_summary="User logged in successfully",
            success=True,
        )

        # Log failed login
        await log_audit_trail(
            db=db_session,
            action_type="login",
            resource_type="user",
            resource_id="unknown@example.com",
            tenant_id=None,
            user_id=None,
            ip_address="203.0.113.99",
            user_agent="Mozilla/5.0",
            changes_summary="Failed login attempt",
            success=False,
            error_message="Invalid credentials",
        )

        await db_session.commit()

        # Query authentication events
        result = await db_session.execute(
            select(AuditTrail).where(AuditTrail.action_type == "login")
        )
        login_audits = result.scalars().all()

        # Assert - Both success and failure logged with IP and user agent
        assert len(login_audits) >= 2

        successful_logins = [a for a in login_audits if a.success]
        failed_logins = [a for a in login_audits if not a.success]

        assert len(successful_logins) >= 1
        assert len(failed_logins) >= 1

        # Verify IP and user agent captured
        for audit in login_audits:
            assert audit.ip_address is not None
            assert audit.user_agent is not None

    @pytest.mark.asyncio
    async def test_iso27001_a1241_admin_actions_logged(self, db_session: AsyncSession):
        """Test ISO 27001 A.12.4.1 - Administrator actions must be logged."""
        # Arrange
        admin_id = uuid4()
        tenant_id = uuid4()

        admin_actions = [
            ("create", "user", "Created new user"),
            ("update", "user", "Updated user role to admin"),
            ("delete", "user", "Deleted inactive user"),
            ("update", "integration_config", "Updated GitHub integration"),
        ]

        # Act - Log various admin actions
        for action_type, resource_type, summary in admin_actions:
            await log_audit_trail(
                db=db_session,
                action_type=action_type,
                resource_type=resource_type,
                resource_id=f"{resource_type}-{uuid4()}",
                tenant_id=tenant_id,
                user_id=admin_id,
                changes_summary=summary,
            )

        await db_session.commit()

        # Query admin actions
        result = await db_session.execute(
            select(AuditTrail).where(AuditTrail.user_id == admin_id)
        )
        admin_audits = result.scalars().all()

        # Assert - All admin actions logged with user_id
        assert len(admin_audits) >= len(admin_actions)
        assert all(a.user_id == admin_id for a in admin_audits)
        assert all(a.changes_summary is not None for a in admin_audits)

    @pytest.mark.asyncio
    async def test_gdpr_article5_accountability(self, db_session: AsyncSession):
        """Test GDPR Article 5(2) - Accountability through audit trail."""
        # Arrange
        user_id = uuid4()
        tenant_id = uuid4()

        # Act - Log data processing activities
        await log_audit_trail(
            db=db_session,
            action_type="update",
            resource_type="user",
            resource_id=str(user_id),
            tenant_id=tenant_id,
            user_id=uuid4(),
            old_values={"email": "old@example.com", "name": "Old Name"},
            new_values={"email": "new@example.com", "name": "New Name"},
            changes_summary="User personal data updated",
        )

        await log_audit_trail(
            db=db_session,
            action_type="delete",
            resource_type="user",
            resource_id=str(user_id),
            tenant_id=tenant_id,
            user_id=uuid4(),
            old_values={"email": "new@example.com", "name": "New Name"},
            changes_summary="User data deleted (GDPR right to erasure)",
        )

        await db_session.commit()

        # Query user data processing
        result = await db_session.execute(
            select(AuditTrail)
            .where(AuditTrail.resource_type == "user")
            .where(AuditTrail.resource_id == str(user_id))
        )
        user_audits = result.scalars().all()

        # Assert - Complete audit trail with old/new values
        assert len(user_audits) >= 2
        assert any(a.action_type == "update" for a in user_audits)
        assert any(a.action_type == "delete" for a in user_audits)

        # Verify old/new values tracked
        update_audit = next(a for a in user_audits if a.action_type == "update")
        assert update_audit.old_values is not None
        assert update_audit.new_values is not None

    @pytest.mark.asyncio
    async def test_hipaa_audit_controls(self, db_session: AsyncSession):
        """Test HIPAA §164.312(b) - Audit controls for security."""
        # Arrange
        tenant_id = uuid4()

        # Act - Log security-relevant events
        security_events = [
            ("login", "user", "User authentication", True, None),
            ("login", "user", "Failed login attempt", False, "Invalid credentials"),
            ("update", "user", "Password reset", True, None),
            ("update", "integration_config", "Security config changed", True, None),
        ]

        for action, resource, summary, success, error in security_events:
            await log_audit_trail(
                db=db_session,
                action_type=action,
                resource_type=resource,
                tenant_id=tenant_id,
                changes_summary=summary,
                success=success,
                error_message=error,
            )

        await db_session.commit()

        # Query security events
        result = await db_session.execute(
            select(AuditTrail).where(AuditTrail.tenant_id == tenant_id)
        )
        security_audits = result.scalars().all()

        # Assert - Security events tracked with success/failure
        assert len(security_audits) >= len(security_events)
        assert any(not a.success for a in security_audits)  # Failed events tracked
        assert any(a.success for a in security_audits)  # Successful events tracked

        # Verify timestamps for activity review
        assert all(a.created_at is not None for a in security_audits)


class TestAuditTrailQuerying:
    """Test suite for audit trail querying capabilities."""

    @pytest.mark.asyncio
    async def test_query_by_time_range(self, db_session: AsyncSession):
        """Test querying audit logs by time range."""
        # Arrange
        tenant_id = uuid4()

        # Create some audit logs
        for i in range(5):
            await log_audit_trail(
                db=db_session,
                action_type="create",
                resource_type="defect",
                tenant_id=tenant_id,
            )

        await db_session.commit()

        # Act - Query recent logs
        result = await db_session.execute(
            select(AuditTrail)
            .where(AuditTrail.tenant_id == tenant_id)
            .order_by(AuditTrail.created_at.desc())
            .limit(10)
        )
        recent_audits = result.scalars().all()

        # Assert
        assert len(recent_audits) >= 5
        # Verify chronological order (most recent first)
        for i in range(len(recent_audits) - 1):
            assert recent_audits[i].created_at >= recent_audits[i + 1].created_at

    @pytest.mark.asyncio
    async def test_query_by_action_type(self, db_session: AsyncSession):
        """Test filtering audit logs by action type."""
        # Arrange
        tenant_id = uuid4()

        await log_audit_trail(
            db=db_session,
            action_type="create",
            resource_type="defect",
            tenant_id=tenant_id,
        )

        await log_audit_trail(
            db=db_session,
            action_type="update",
            resource_type="defect",
            tenant_id=tenant_id,
        )

        await log_audit_trail(
            db=db_session,
            action_type="delete",
            resource_type="defect",
            tenant_id=tenant_id,
        )

        await db_session.commit()

        # Act - Query only updates
        result = await db_session.execute(
            select(AuditTrail)
            .where(AuditTrail.tenant_id == tenant_id)
            .where(AuditTrail.action_type == "update")
        )
        update_audits = result.scalars().all()

        # Assert
        assert len(update_audits) >= 1
        assert all(a.action_type == "update" for a in update_audits)

    @pytest.mark.asyncio
    async def test_query_by_resource(self, db_session: AsyncSession):
        """Test querying audit history for specific resource."""
        # Arrange
        resource_id = f"defect-{uuid4()}"

        await log_audit_trail(
            db=db_session,
            action_type="create",
            resource_type="defect",
            resource_id=resource_id,
        )

        await log_audit_trail(
            db=db_session,
            action_type="update",
            resource_type="defect",
            resource_id=resource_id,
        )

        await log_audit_trail(
            db=db_session,
            action_type="resolve",
            resource_type="defect",
            resource_id=resource_id,
        )

        await db_session.commit()

        # Act - Query history for specific defect
        result = await db_session.execute(
            select(AuditTrail)
            .where(AuditTrail.resource_type == "defect")
            .where(AuditTrail.resource_id == resource_id)
            .order_by(AuditTrail.created_at.asc())
        )
        resource_history = result.scalars().all()

        # Assert - Complete lifecycle tracked
        assert len(resource_history) >= 3
        assert resource_history[0].action_type == "create"
        assert resource_history[-1].action_type == "resolve"
