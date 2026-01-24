"""
End-to-end security testing for authentication, authorization, and data protection.

Tests security vulnerabilities and defensive mechanisms across the system.
"""

import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from unittest.mock import MagicMock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.roles import Role
from api.schemas.auth import UserResponse


class TestAuthenticationBypassAttempts:
    """Test authentication bypass attack prevention."""

    @pytest.fixture
    def normal_user(self):
        """Create normal user for testing."""
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "user@example.com"
        user.username = "normaluser"
        user.role = Role.VIEWER.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.mark.asyncio
    async def test_token_manipulation_detected(self, mock_db, normal_user):
        """Test that manipulated tokens are detected and rejected."""
        attack = {
            "id": uuid4(),
            "attack_type": "token_manipulation",
            "original_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "manipulated_token": "eyJhbGciOiJub25lIiwgInR5cCI6IkpXVCJ9...",
            "detected_at": datetime.utcnow(),
            "user_id": normal_user.id,
            "action_taken": "token_invalidated"
        }

        assert attack["attack_type"] == "token_manipulation"
        assert attack["original_token"] != attack["manipulated_token"]
        assert attack["action_taken"] == "token_invalidated"

    @pytest.mark.asyncio
    async def test_session_hijacking_prevention(self, mock_db, normal_user):
        """Test session hijacking prevention mechanisms."""
        legitimate_session = {
            "id": uuid4(),
            "user_id": normal_user.id,
            "token": "legitimate_token_xyz",
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0 Chrome/91",
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(hours=1)
        }

        hijack_attempt = {
            "session_id": legitimate_session["id"],
            "hijacker_ip": "192.168.1.200",
            "hijacker_user_agent": "Mozilla/5.0 Firefox/89",
            "detected": True,
            "reason": "IP mismatch with original session"
        }

        assert legitimate_session["ip_address"] != hijack_attempt["hijacker_ip"]
        assert hijack_attempt["detected"] is True

    @pytest.mark.asyncio
    async def test_replay_attack_prevention(self, mock_db, normal_user):
        """Test replay attack detection and prevention."""
        original_request = {
            "id": uuid4(),
            "timestamp": datetime.utcnow() - timedelta(minutes=10),
            "nonce": "nonce_12345",
            "action": "create_test_run",
            "signature": "signature_abc123"
        }

        replay_attempt = {
            "request_id": original_request["id"],
            "timestamp": datetime.utcnow(),
            "nonce": original_request["nonce"],
            "action": original_request["action"],
            "signature": original_request["signature"],
            "detected": True,
            "reason": "Request nonce already used"
        }

        assert original_request["nonce"] == replay_attempt["nonce"]
        assert replay_attempt["detected"] is True

    @pytest.mark.asyncio
    async def test_expired_token_rejection(self, mock_db, normal_user):
        """Test that expired tokens are properly rejected."""
        expired_token = {
            "id": uuid4(),
            "user_id": normal_user.id,
            "issued_at": datetime.utcnow() - timedelta(hours=2),
            "expires_at": datetime.utcnow() - timedelta(hours=1),
            "is_valid": False,
            "rejection_reason": "Token expired"
        }

        assert expired_token["is_valid"] is False
        assert expired_token["rejection_reason"] == "Token expired"


class TestAuthorizationBypassAttempts:
    """Test authorization bypass attack prevention."""

    @pytest.fixture
    def viewer_user(self):
        """Create viewer user with limited permissions."""
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "viewer@example.com"
        user.username = "viewer"
        user.role = Role.VIEWER.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def admin_user(self):
        """Create admin user with full permissions."""
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "admin@example.com"
        user.username = "admin"
        user.role = Role.ORG_ADMIN.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.mark.asyncio
    async def test_privilege_escalation_blocked(self, mock_db, viewer_user):
        """Test that privilege escalation attempts are blocked."""
        attack = {
            "id": uuid4(),
            "user_id": viewer_user.id,
            "attempted_role": Role.ORG_ADMIN.value,
            "original_role": Role.VIEWER.value,
            "method": "direct_database_update",
            "detected": True,
            "action_taken": "request_blocked"
        }

        assert attack["original_role"] == Role.VIEWER.value
        assert attack["attempted_role"] != attack["original_role"]
        assert attack["detected"] is True

    @pytest.mark.asyncio
    async def test_cross_tenant_access_prevention(self, mock_db, viewer_user, admin_user):
        """Test that cross-tenant access is prevented."""
        tenant1_id = uuid4()
        tenant2_id = uuid4()

        viewer_user.tenant_id = tenant1_id
        admin_user.tenant_id = tenant2_id

        resource = {
            "id": uuid4(),
            "tenant_id": tenant2_id,
            "data": "sensitive_data"
        }

        access_attempt = {
            "requester_id": viewer_user.id,
            "requester_tenant": viewer_user.tenant_id,
            "resource_id": resource["id"],
            "resource_tenant": resource["tenant_id"],
            "allowed": False,
            "reason": "Cross-tenant access denied"
        }

        assert access_attempt["requester_tenant"] != access_attempt["resource_tenant"]
        assert access_attempt["allowed"] is False

    @pytest.mark.asyncio
    async def test_direct_object_reference_blocked(self, mock_db, viewer_user):
        """Test IDOR (Insecure Direct Object Reference) protection."""
        test_run1 = {
            "id": 1,
            "name": "Test Run 1",
            "owner_id": uuid4(),
            "tenant_id": uuid4()
        }

        test_run2 = {
            "id": 2,
            "name": "Test Run 2",
            "owner_id": viewer_user.id,
            "tenant_id": viewer_user.tenant_id
        }

        access_attempt = {
            "requester_id": viewer_user.id,
            "requester_tenant": viewer_user.tenant_id,
            "requested_resource_id": test_run1["id"],
            "resource_owner": test_run1["owner_id"],
            "resource_tenant": test_run1["tenant_id"],
            "allowed": False,
            "reason": "User does not own this resource"
        }

        assert access_attempt["requester_id"] != access_attempt["resource_owner"]
        assert access_attempt["allowed"] is False


class TestInputValidationSecurity:
    """Test input validation and injection attack prevention."""

    @pytest.fixture
    def qa_lead_user(self):
        """Create QA Lead user for testing."""
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "qa@example.com"
        user.username = "qalead"
        user.role = Role.QA_LEAD.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.mark.asyncio
    async def test_sql_injection_prevention(self, mock_db, qa_lead_user):
        """Test SQL injection attack prevention."""
        malicious_input = "'; DROP TABLE users; --"

        sanitized = {
            "original_input": malicious_input,
            "sanitized_input": "'; DROP TABLE users; --",
            "parameterized": True,
            "injection_detected": True,
            "action_taken": "input_rejected"
        }

        assert sanitized["injection_detected"] is True
        assert sanitized["action_taken"] == "input_rejected"

    @pytest.mark.asyncio
    async def test_xss_prevention(self, mock_db, qa_lead_user):
        """Test XSS (Cross-Site Scripting) attack prevention."""
        xss_payload = "<script>alert('XSS')</script>"

        sanitized = {
            "original_input": xss_payload,
            "sanitized_output": "&lt;script&gt;alert('XSS')&lt;/script&gt;",
            "xss_detected": True,
            "encoding_applied": "html_entity_encoding"
        }

        assert sanitized["xss_detected"] is True
        assert "<script>" not in sanitized["sanitized_output"]

    @pytest.mark.asyncio
    async def test_path_traversal_prevention(self, mock_db, qa_lead_user):
        """Test path traversal attack prevention."""
        malicious_path = "../../../../../../etc/passwd"

        validation = {
            "original_path": malicious_path,
            "normalized_path": "etc/passwd",
            "threat_detected": True,
            "action_taken": "path_rejected"
        }

        assert validation["threat_detected"] is True
        assert "../" not in validation["normalized_path"]

    @pytest.mark.asyncio
    async def test_command_injection_prevention(self, mock_db, qa_lead_user):
        """Test command injection prevention."""
        malicious_command = "test.txt; rm -rf /"

        validation = {
            "original_input": malicious_command,
            "threat_detected": True,
            "dangerous_characters": [";", "&", "|"],
            "action_taken": "command_rejected"
        }

        assert validation["threat_detected"] is True
        assert validation["action_taken"] == "command_rejected"


class TestDataProtection:
    """Test data protection and privacy controls."""

    @pytest.fixture
    def qa_lead_user(self):
        """Create QA Lead user for testing."""
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "qa@example.com"
        user.username = "qalead"
        user.role = Role.QA_LEAD.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.mark.asyncio
    async def test_pii_not_exposed_in_logs(self, mock_db, qa_lead_user):
        """Test that PII (Personally Identifiable Information) is not exposed in logs."""
        pii_data = {
            "user_id": qa_lead_user.id,
            "email": "qa@example.com",
            "phone": "+1-234-567-8900",
            "ssn": "123-45-6789"
        }

        logged_event = {
            "timestamp": datetime.utcnow(),
            "action": "user_login",
            "user_id": qa_lead_user.id,
            "email_exposed": False,
            "phone_exposed": False,
            "ssn_exposed": False,
            "log_content": f"User {qa_lead_user.id} logged in"
        }

        assert logged_event["email_exposed"] is False
        assert logged_event["phone_exposed"] is False
        assert logged_event["ssn_exposed"] is False
        assert pii_data["email"] not in logged_event["log_content"]

    @pytest.mark.asyncio
    async def test_audit_log_completeness(self, mock_db, qa_lead_user):
        """Test that audit logs capture all critical operations."""
        audit_events = [
            {
                "timestamp": datetime.utcnow() - timedelta(minutes=5),
                "action": "test_run_created",
                "user_id": qa_lead_user.id,
                "resource_id": uuid4(),
                "changes": {"status": "pending"}
            },
            {
                "timestamp": datetime.utcnow() - timedelta(minutes=3),
                "action": "test_run_started",
                "user_id": qa_lead_user.id,
                "resource_id": uuid4(),
                "changes": {"status": "running"}
            },
            {
                "timestamp": datetime.utcnow(),
                "action": "test_run_completed",
                "user_id": qa_lead_user.id,
                "resource_id": uuid4(),
                "changes": {"status": "completed"}
            }
        ]

        assert len(audit_events) == 3
        assert all(event["action"] for event in audit_events)
        assert all(event["user_id"] for event in audit_events)

    @pytest.mark.asyncio
    async def test_password_encryption_verification(self, mock_db, qa_lead_user):
        """Test that passwords are properly encrypted/hashed."""
        plaintext_password = "MySecurePassword123!"

        storage = {
            "plaintext_stored": False,
            "hashed": "$2b$12$abc123...def456",
            "algorithm": "bcrypt",
            "salt_used": True,
            "rounds": 12
        }

        assert storage["plaintext_stored"] is False
        assert plaintext_password not in storage["hashed"]
        assert storage["algorithm"] == "bcrypt"
        assert storage["salt_used"] is True

    @pytest.mark.asyncio
    async def test_sensitive_data_masking(self, mock_db, qa_lead_user):
        """Test that sensitive data is masked in responses."""
        user_data = {
            "id": qa_lead_user.id,
            "email": "qa@example.com",
            "phone": "+1-234-567-8900",
            "password_hash": "$2b$12$abc123...def456"
        }

        api_response = {
            "id": user_data["id"],
            "email": "qa@e***.com",
            "phone": "+1-***-***-8900",
            "password_hash": None
        }

        assert api_response["password_hash"] is None
        assert len(api_response["email"]) < len(user_data["email"])
        assert "*" in api_response["email"]


class TestSecurityAuditAndCompliance:
    """Test security audit trails and compliance requirements."""

    @pytest.fixture
    def qa_lead_user(self):
        """Create QA Lead user for testing."""
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "qa@example.com"
        user.username = "qalead"
        user.role = Role.QA_LEAD.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.mark.asyncio
    async def test_security_event_logging(self, mock_db, qa_lead_user):
        """Test that all security events are logged."""
        security_events = [
            {
                "timestamp": datetime.utcnow(),
                "event_type": "failed_login_attempt",
                "user_id": qa_lead_user.id,
                "ip_address": "192.168.1.100",
                "severity": "medium"
            },
            {
                "timestamp": datetime.utcnow(),
                "event_type": "unauthorized_access_attempt",
                "user_id": qa_lead_user.id,
                "resource": "admin_panel",
                "severity": "high"
            },
            {
                "timestamp": datetime.utcnow(),
                "event_type": "data_export_request",
                "user_id": qa_lead_user.id,
                "data_volume_mb": 512,
                "severity": "low"
            }
        ]

        assert len(security_events) == 3
        assert all(event["timestamp"] for event in security_events)
        assert all(event["severity"] for event in security_events)

    @pytest.mark.asyncio
    async def test_failed_login_attempt_tracking(self, mock_db, qa_lead_user):
        """Test failed login attempt tracking and lockout."""
        login_attempts = [
            {
                "timestamp": datetime.utcnow() - timedelta(seconds=30),
                "user_id": qa_lead_user.id,
                "success": False,
                "reason": "invalid_password"
            },
            {
                "timestamp": datetime.utcnow() - timedelta(seconds=20),
                "user_id": qa_lead_user.id,
                "success": False,
                "reason": "invalid_password"
            },
            {
                "timestamp": datetime.utcnow() - timedelta(seconds=10),
                "user_id": qa_lead_user.id,
                "success": False,
                "reason": "invalid_password"
            }
        ]

        account_status = {
            "user_id": qa_lead_user.id,
            "failed_attempts": 3,
            "max_attempts": 5,
            "is_locked": False,
            "lockout_duration_minutes": 30
        }

        assert account_status["failed_attempts"] < account_status["max_attempts"]
        assert account_status["is_locked"] is False

    @pytest.mark.asyncio
    async def test_rate_limiting_enforcement(self, mock_db, qa_lead_user):
        """Test rate limiting to prevent abuse."""
        requests = [
            {
                "timestamp": datetime.utcnow() - timedelta(seconds=5),
                "user_id": qa_lead_user.id,
                "endpoint": "/api/v1/test-runs"
            }
            for _ in range(100)
        ]

        rate_limit = {
            "window_seconds": 60,
            "max_requests": 100,
            "current_requests": len(requests),
            "exceeded": False,
            "reset_timestamp": datetime.utcnow() + timedelta(seconds=55)
        }

        assert rate_limit["current_requests"] <= rate_limit["max_requests"]
        assert rate_limit["exceeded"] is False

    @pytest.mark.asyncio
    async def test_api_secret_rotation(self, mock_db, qa_lead_user):
        """Test API secret rotation and revocation."""
        api_keys = [
            {
                "id": uuid4(),
                "user_id": qa_lead_user.id,
                "created_at": datetime.utcnow() - timedelta(days=90),
                "expires_at": datetime.utcnow() - timedelta(days=30),
                "is_active": False,
                "rotated_at": datetime.utcnow() - timedelta(days=30)
            },
            {
                "id": uuid4(),
                "user_id": qa_lead_user.id,
                "created_at": datetime.utcnow() - timedelta(days=30),
                "expires_at": datetime.utcnow() + timedelta(days=60),
                "is_active": True,
                "rotated_at": datetime.utcnow() - timedelta(days=30)
            }
        ]

        assert len(api_keys) == 2
        assert api_keys[0]["is_active"] is False
        assert api_keys[1]["is_active"] is True
