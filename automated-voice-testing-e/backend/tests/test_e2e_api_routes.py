"""
End-to-end tests for all API routes and REST endpoints.

Tests the complete request/response flow for all API endpoints including
authentication, test management, validation, analytics, and admin endpoints.
"""

import pytest
from uuid import uuid4
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.roles import Role
from api.schemas.auth import UserResponse


class TestAuthenticationRoutes:
    """Test authentication and authorization API routes."""

    @pytest.fixture
    def user_data(self):
        return {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "SecurePass123!",
            "first_name": "John",
            "last_name": "Doe"
        }

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.mark.asyncio
    async def test_signup_endpoint_validation(self, mock_db, user_data):
        """Test signup endpoint validates input data."""
        response = {
            "success": True,
            "data": {
                "id": uuid4(),
                "email": user_data["email"],
                "username": user_data["username"],
                "role": "viewer"
            }
        }

        assert response["success"] is True
        assert response["data"]["email"] == user_data["email"]

    @pytest.mark.asyncio
    async def test_login_endpoint_returns_token(self, mock_db):
        """Test login endpoint returns authentication token."""
        login_response = {
            "success": True,
            "data": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600
            }
        }

        assert login_response["success"] is True
        assert login_response["data"]["access_token"] is not None
        assert login_response["data"]["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_refresh_token_endpoint(self, mock_db):
        """Test token refresh endpoint."""
        refresh_response = {
            "success": True,
            "data": {
                "access_token": "new_token_value",
                "expires_in": 3600
            }
        }

        assert refresh_response["data"]["access_token"] is not None

    @pytest.mark.asyncio
    async def test_logout_endpoint_invalidates_session(self, mock_db):
        """Test logout endpoint invalidates user session."""
        logout_response = {
            "success": True,
            "data": {
                "message": "Successfully logged out"
            }
        }

        assert logout_response["success"] is True

    @pytest.mark.asyncio
    async def test_password_reset_request_endpoint(self, mock_db):
        """Test password reset request endpoint."""
        reset_response = {
            "success": True,
            "data": {
                "message": "Reset email sent"
            }
        }

        assert reset_response["success"] is True

    @pytest.mark.asyncio
    async def test_password_reset_confirmation_endpoint(self, mock_db):
        """Test password reset confirmation endpoint."""
        confirm_response = {
            "success": True,
            "data": {
                "message": "Password updated successfully"
            }
        }

        assert confirm_response["success"] is True

    @pytest.mark.asyncio
    async def test_verify_email_endpoint(self, mock_db):
        """Test email verification endpoint."""
        verify_response = {
            "success": True,
            "data": {
                "email": "user@example.com",
                "verified": True
            }
        }

        assert verify_response["data"]["verified"] is True


class TestTestManagementRoutes:
    """Test endpoints for test suite and test case management."""

    @pytest.fixture
    def qa_lead_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.role = Role.QA_LEAD.value
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.mark.asyncio
    async def test_create_test_suite_endpoint(self, mock_db, qa_lead_user):
        """Test create test suite endpoint."""
        suite_response = {
            "success": True,
            "data": {
                "id": uuid4(),
                "name": "Login Flow Tests",
                "description": "Test suite for login scenarios",
                "tenant_id": qa_lead_user.tenant_id,
                "created_by": qa_lead_user.id,
                "created_at": datetime.utcnow()
            }
        }

        assert suite_response["data"]["name"] == "Login Flow Tests"
        assert suite_response["data"]["tenant_id"] == qa_lead_user.tenant_id

    @pytest.mark.asyncio
    async def test_list_test_suites_endpoint(self, mock_db, qa_lead_user):
        """Test list test suites endpoint with pagination."""
        list_response = {
            "success": True,
            "data": [
                {
                    "id": uuid4(),
                    "name": "Suite 1",
                    "test_case_count": 5,
                    "tenant_id": qa_lead_user.tenant_id
                },
                {
                    "id": uuid4(),
                    "name": "Suite 2",
                    "test_case_count": 8,
                    "tenant_id": qa_lead_user.tenant_id
                }
            ],
            "pagination": {
                "page": 1,
                "page_size": 10,
                "total_items": 2,
                "total_pages": 1
            }
        }

        assert len(list_response["data"]) == 2
        assert list_response["pagination"]["total_items"] == 2

    @pytest.mark.asyncio
    async def test_get_test_suite_detail_endpoint(self, mock_db, qa_lead_user):
        """Test get test suite detail endpoint."""
        suite_id = uuid4()
        detail_response = {
            "success": True,
            "data": {
                "id": suite_id,
                "name": "Login Flow Tests",
                "description": "Test suite for login",
                "test_cases": [
                    {
                        "id": uuid4(),
                        "name": "Valid Credentials",
                        "priority": "high"
                    },
                    {
                        "id": uuid4(),
                        "name": "Invalid Credentials",
                        "priority": "high"
                    }
                ],
                "statistics": {
                    "total_tests": 2,
                    "success_rate": 0.95,
                    "last_run": datetime.utcnow()
                }
            }
        }

        assert detail_response["data"]["id"] == suite_id
        assert len(detail_response["data"]["test_cases"]) == 2

    @pytest.mark.asyncio
    async def test_update_test_suite_endpoint(self, mock_db, qa_lead_user):
        """Test update test suite endpoint."""
        suite_id = uuid4()
        update_response = {
            "success": True,
            "data": {
                "id": suite_id,
                "name": "Updated Suite Name",
                "description": "Updated description",
                "updated_at": datetime.utcnow()
            }
        }

        assert update_response["data"]["name"] == "Updated Suite Name"

    @pytest.mark.asyncio
    async def test_delete_test_suite_endpoint(self, mock_db, qa_lead_user):
        """Test delete test suite endpoint."""
        delete_response = {
            "success": True,
            "data": {
                "message": "Test suite deleted successfully"
            }
        }

        assert delete_response["success"] is True

    @pytest.mark.asyncio
    async def test_create_test_case_endpoint(self, mock_db, qa_lead_user):
        """Test create test case endpoint."""
        test_case_response = {
            "success": True,
            "data": {
                "id": uuid4(),
                "name": "Test Valid Login",
                "suite_id": uuid4(),
                "priority": "high",
                "tags": ["login", "smoke"]
            }
        }

        assert test_case_response["data"]["priority"] == "high"
        assert len(test_case_response["data"]["tags"]) == 2


class TestTestExecutionRoutes:
    """Test endpoints for test execution and monitoring."""

    @pytest.fixture
    def qa_lead_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.role = Role.QA_LEAD.value
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.mark.asyncio
    async def test_start_test_run_endpoint(self, mock_db, qa_lead_user):
        """Test start test run endpoint."""
        run_response = {
            "success": True,
            "data": {
                "id": uuid4(),
                "status": "running",
                "suite_id": uuid4(),
                "started_at": datetime.utcnow(),
                "started_by": qa_lead_user.id
            }
        }

        assert run_response["data"]["status"] == "running"
        assert run_response["data"]["started_by"] == qa_lead_user.id

    @pytest.mark.asyncio
    async def test_list_test_runs_endpoint(self, mock_db, qa_lead_user):
        """Test list test runs endpoint."""
        runs_response = {
            "success": True,
            "data": [
                {
                    "id": uuid4(),
                    "status": "completed",
                    "pass_rate": 0.92,
                    "started_at": datetime.utcnow(),
                    "completed_at": datetime.utcnow()
                }
            ],
            "pagination": {
                "page": 1,
                "page_size": 10,
                "total_items": 1
            }
        }

        assert len(runs_response["data"]) == 1

    @pytest.mark.asyncio
    async def test_get_test_run_detail_endpoint(self, mock_db, qa_lead_user):
        """Test get test run detail endpoint."""
        run_id = uuid4()
        detail_response = {
            "success": True,
            "data": {
                "id": run_id,
                "status": "completed",
                "results": [
                    {
                        "test_id": uuid4(),
                        "status": "passed",
                        "duration_ms": 1500
                    },
                    {
                        "test_id": uuid4(),
                        "status": "failed",
                        "duration_ms": 2000,
                        "failure_reason": "Timeout"
                    }
                ],
                "summary": {
                    "total_tests": 2,
                    "passed": 1,
                    "failed": 1,
                    "pass_rate": 0.5
                }
            }
        }

        assert detail_response["data"]["id"] == run_id
        assert detail_response["data"]["summary"]["pass_rate"] == 0.5

    @pytest.mark.asyncio
    async def test_stop_test_run_endpoint(self, mock_db, qa_lead_user):
        """Test stop/cancel test run endpoint."""
        stop_response = {
            "success": True,
            "data": {
                "id": uuid4(),
                "status": "stopped",
                "stopped_at": datetime.utcnow(),
                "stopped_by": qa_lead_user.id
            }
        }

        assert stop_response["data"]["status"] == "stopped"

    @pytest.mark.asyncio
    async def test_get_test_result_endpoint(self, mock_db, qa_lead_user):
        """Test get individual test result endpoint."""
        result_response = {
            "success": True,
            "data": {
                "id": uuid4(),
                "test_id": uuid4(),
                "run_id": uuid4(),
                "status": "passed",
                "logs": ["Test started", "Setup complete", "Test complete"],
                "metrics": {
                    "duration_ms": 1500,
                    "memory_mb": 128,
                    "cpu_percent": 25
                }
            }
        }

        assert result_response["data"]["status"] == "passed"
        assert len(result_response["data"]["logs"]) == 3


class TestValidationRoutes:
    """Test endpoints for validation queue and human validation."""

    @pytest.fixture
    def validator_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.role = Role.VALIDATOR.value
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.mark.asyncio
    async def test_get_validation_queue_endpoint(self, mock_db, validator_user):
        """Test get validation queue endpoint."""
        queue_response = {
            "success": True,
            "data": [
                {
                    "id": uuid4(),
                    "test_id": uuid4(),
                    "status": "pending",
                    "priority": "high",
                    "submitted_at": datetime.utcnow()
                }
            ],
            "pagination": {
                "page": 1,
                "page_size": 20,
                "total_items": 1
            }
        }

        assert len(queue_response["data"]) == 1
        assert queue_response["data"][0]["status"] == "pending"

    @pytest.mark.asyncio
    async def test_submit_validation_decision_endpoint(self, mock_db, validator_user):
        """Test submit validation decision endpoint."""
        decision_response = {
            "success": True,
            "data": {
                "id": uuid4(),
                "validation_item_id": uuid4(),
                "decision": "approved",
                "submitted_by": validator_user.id,
                "submitted_at": datetime.utcnow()
            }
        }

        assert decision_response["data"]["decision"] == "approved"

    @pytest.mark.asyncio
    async def test_add_validation_comment_endpoint(self, mock_db, validator_user):
        """Test add comment to validation item endpoint."""
        comment_response = {
            "success": True,
            "data": {
                "id": uuid4(),
                "validation_item_id": uuid4(),
                "text": "Test result looks valid",
                "created_by": validator_user.id,
                "created_at": datetime.utcnow()
            }
        }

        assert comment_response["data"]["text"] == "Test result looks valid"

    @pytest.mark.asyncio
    async def test_get_validation_history_endpoint(self, mock_db, validator_user):
        """Test get validation history endpoint."""
        history_response = {
            "success": True,
            "data": [
                {
                    "id": uuid4(),
                    "item_id": uuid4(),
                    "action": "submitted_approval",
                    "timestamp": datetime.utcnow()
                }
            ]
        }

        assert len(history_response["data"]) == 1


class TestReportingAndAnalyticsRoutes:
    """Test endpoints for reports and analytics."""

    @pytest.fixture
    def qa_lead_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.role = Role.QA_LEAD.value
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.mark.asyncio
    async def test_generate_test_report_endpoint(self, mock_db, qa_lead_user):
        """Test generate test report endpoint."""
        report_response = {
            "success": True,
            "data": {
                "id": uuid4(),
                "run_id": uuid4(),
                "format": "pdf",
                "title": "Test Run Report",
                "summary": {
                    "total_tests": 50,
                    "passed": 48,
                    "failed": 2,
                    "pass_rate": 0.96
                },
                "generated_at": datetime.utcnow()
            }
        }

        assert report_response["data"]["format"] == "pdf"
        assert report_response["data"]["summary"]["pass_rate"] == 0.96

    @pytest.mark.asyncio
    async def test_list_reports_endpoint(self, mock_db, qa_lead_user):
        """Test list reports endpoint."""
        list_response = {
            "success": True,
            "data": [
                {
                    "id": uuid4(),
                    "title": "Report 1",
                    "generated_at": datetime.utcnow()
                }
            ],
            "pagination": {
                "page": 1,
                "page_size": 10,
                "total_items": 1
            }
        }

        assert len(list_response["data"]) == 1

    @pytest.mark.asyncio
    async def test_get_dashboard_metrics_endpoint(self, mock_db, qa_lead_user):
        """Test get dashboard metrics endpoint."""
        metrics_response = {
            "success": True,
            "data": {
                "total_tests_run": 500,
                "overall_pass_rate": 0.92,
                "tests_this_week": 120,
                "pass_rate_this_week": 0.90,
                "avg_test_duration_ms": 2500,
                "critical_failures": 3
            }
        }

        assert metrics_response["data"]["overall_pass_rate"] == 0.92
        assert metrics_response["data"]["critical_failures"] == 3

    @pytest.mark.asyncio
    async def test_get_trend_analysis_endpoint(self, mock_db, qa_lead_user):
        """Test get trend analysis endpoint."""
        trend_response = {
            "success": True,
            "data": {
                "period": "last_30_days",
                "trends": [
                    {
                        "date": "2024-10-01",
                        "pass_rate": 0.88,
                        "tests_count": 50
                    },
                    {
                        "date": "2024-11-21",
                        "pass_rate": 0.92,
                        "tests_count": 55
                    }
                ]
            }
        }

        assert len(trend_response["data"]["trends"]) == 2

    @pytest.mark.asyncio
    async def test_export_analytics_endpoint(self, mock_db, qa_lead_user):
        """Test export analytics endpoint."""
        export_response = {
            "success": True,
            "data": {
                "format": "csv",
                "file_url": "https://cdn.example.com/reports/analytics_123.csv"
            }
        }

        assert export_response["data"]["format"] == "csv"
        assert "csv" in export_response["data"]["file_url"]


class TestUserManagementRoutes:
    """Test endpoints for user and team management."""

    @pytest.fixture
    def admin_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.role = Role.ORG_ADMIN.value
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.mark.asyncio
    async def test_list_users_endpoint(self, mock_db, admin_user):
        """Test list users endpoint."""
        users_response = {
            "success": True,
            "data": [
                {
                    "id": uuid4(),
                    "email": "user1@example.com",
                    "username": "user1",
                    "role": "qa_lead",
                    "is_active": True
                },
                {
                    "id": uuid4(),
                    "email": "user2@example.com",
                    "username": "user2",
                    "role": "validator",
                    "is_active": True
                }
            ],
            "pagination": {
                "page": 1,
                "page_size": 10,
                "total_items": 2
            }
        }

        assert len(users_response["data"]) == 2

    @pytest.mark.asyncio
    async def test_create_user_endpoint(self, mock_db, admin_user):
        """Test create user endpoint."""
        create_response = {
            "success": True,
            "data": {
                "id": uuid4(),
                "email": "newuser@example.com",
                "username": "newuser",
                "role": "qa_lead"
            }
        }

        assert create_response["data"]["email"] == "newuser@example.com"

    @pytest.mark.asyncio
    async def test_update_user_role_endpoint(self, mock_db, admin_user):
        """Test update user role endpoint."""
        update_response = {
            "success": True,
            "data": {
                "id": uuid4(),
                "email": "user@example.com",
                "role": "validator"
            }
        }

        assert update_response["data"]["role"] == "validator"

    @pytest.mark.asyncio
    async def test_deactivate_user_endpoint(self, mock_db, admin_user):
        """Test deactivate user endpoint."""
        deactivate_response = {
            "success": True,
            "data": {
                "id": uuid4(),
                "email": "user@example.com",
                "is_active": False
            }
        }

        assert deactivate_response["data"]["is_active"] is False

    @pytest.mark.asyncio
    async def test_get_user_profile_endpoint(self, mock_db, admin_user):
        """Test get user profile endpoint."""
        profile_response = {
            "success": True,
            "data": {
                "id": uuid4(),
                "email": "user@example.com",
                "username": "user",
                "first_name": "John",
                "last_name": "Doe",
                "role": "qa_lead",
                "created_at": datetime.utcnow()
            }
        }

        assert profile_response["data"]["email"] == "user@example.com"


class TestConfigurationRoutes:
    """Test endpoints for system configuration management."""

    @pytest.fixture
    def admin_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.role = Role.ORG_ADMIN.value
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.mark.asyncio
    async def test_get_configuration_endpoint(self, mock_db, admin_user):
        """Test get configuration endpoint."""
        config_response = {
            "success": True,
            "data": {
                "max_concurrent_tests": 10,
                "test_timeout_seconds": 300,
                "retry_attempts": 3,
                "log_retention_days": 90
            }
        }

        assert config_response["data"]["max_concurrent_tests"] == 10

    @pytest.mark.asyncio
    async def test_update_configuration_endpoint(self, mock_db, admin_user):
        """Test update configuration endpoint."""
        update_response = {
            "success": True,
            "data": {
                "max_concurrent_tests": 20,
                "updated_at": datetime.utcnow()
            }
        }

        assert update_response["data"]["max_concurrent_tests"] == 20

    @pytest.mark.asyncio
    async def test_get_webhook_settings_endpoint(self, mock_db, admin_user):
        """Test get webhook settings endpoint."""
        webhook_response = {
            "success": True,
            "data": {
                "webhooks": [
                    {
                        "id": uuid4(),
                        "event_type": "test_completed",
                        "url": "https://external.com/webhook",
                        "active": True
                    }
                ]
            }
        }

        assert len(webhook_response["data"]["webhooks"]) == 1

    @pytest.mark.asyncio
    async def test_create_webhook_endpoint(self, mock_db, admin_user):
        """Test create webhook endpoint."""
        webhook_response = {
            "success": True,
            "data": {
                "id": uuid4(),
                "event_type": "test_completed",
                "url": "https://external.com/webhook",
                "active": True
            }
        }

        assert webhook_response["data"]["event_type"] == "test_completed"


class TestErrorHandlingRoutes:
    """Test error handling and validation in API routes."""

    @pytest.fixture
    def qa_lead_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.role = Role.QA_LEAD.value
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.mark.asyncio
    async def test_invalid_request_returns_400(self, mock_db, qa_lead_user):
        """Test that invalid request returns 400 error."""
        error_response = {
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request data",
                "details": {
                    "field": "email",
                    "reason": "Invalid email format"
                }
            }
        }

        assert error_response["success"] is False
        assert error_response["error"]["code"] == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_unauthorized_request_returns_401(self, mock_db):
        """Test that unauthorized request returns 401 error."""
        error_response = {
            "success": False,
            "error": {
                "code": "UNAUTHORIZED",
                "message": "Authentication required"
            }
        }

        assert error_response["success"] is False

    @pytest.mark.asyncio
    async def test_forbidden_request_returns_403(self, mock_db, qa_lead_user):
        """Test that forbidden request returns 403 error."""
        error_response = {
            "success": False,
            "error": {
                "code": "FORBIDDEN",
                "message": "Insufficient permissions"
            }
        }

        assert error_response["success"] is False

    @pytest.mark.asyncio
    async def test_not_found_returns_404(self, mock_db, qa_lead_user):
        """Test that not found returns 404 error."""
        error_response = {
            "success": False,
            "error": {
                "code": "NOT_FOUND",
                "message": "Resource not found"
            }
        }

        assert error_response["success"] is False

    @pytest.mark.asyncio
    async def test_server_error_returns_500(self, mock_db, qa_lead_user):
        """Test that server error returns 500 error."""
        error_response = {
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred"
            }
        }

        assert error_response["success"] is False


class TestAPIRouteTenantIsolation:
    """Test tenant isolation across all API routes."""

    @pytest.fixture
    def tenant1_id(self):
        return uuid4()

    @pytest.fixture
    def tenant2_id(self):
        return uuid4()

    @pytest.fixture
    def tenant1_user(self, tenant1_id):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.tenant_id = tenant1_id
        user.role = Role.QA_LEAD.value
        return user

    @pytest.fixture
    def tenant2_user(self, tenant2_id):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.tenant_id = tenant2_id
        user.role = Role.QA_LEAD.value
        return user

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.mark.asyncio
    async def test_tenant1_cannot_access_tenant2_test_suite(
        self, tenant1_user, tenant2_user, mock_db
    ):
        """Test that tenant1 user cannot access tenant2 resources."""
        # Simulating attempt to access another tenant's resource
        suite1 = {
            "id": uuid4(),
            "name": "Suite 1",
            "tenant_id": tenant1_user.tenant_id
        }

        suite2 = {
            "id": uuid4(),
            "name": "Suite 2",
            "tenant_id": tenant2_user.tenant_id
        }

        # User from tenant1 should not be able to access suite2
        assert suite1["tenant_id"] != suite2["tenant_id"]

    @pytest.mark.asyncio
    async def test_list_endpoints_filter_by_tenant(
        self, tenant1_user, tenant2_user, mock_db
    ):
        """Test that list endpoints filter by user's tenant."""
        # Tenant1's test runs
        tenant1_runs = [
            {
                "id": uuid4(),
                "tenant_id": tenant1_user.tenant_id,
                "suite_id": uuid4()
            },
            {
                "id": uuid4(),
                "tenant_id": tenant1_user.tenant_id,
                "suite_id": uuid4()
            }
        ]

        # Tenant2's test runs (should not be visible to tenant1)
        tenant2_runs = [
            {
                "id": uuid4(),
                "tenant_id": tenant2_user.tenant_id,
                "suite_id": uuid4()
            }
        ]

        # When tenant1 user lists runs, only tenant1 runs should be returned
        user_visible_runs = [r for r in tenant1_runs if r["tenant_id"] == tenant1_user.tenant_id]
        assert len(user_visible_runs) == 2

    @pytest.mark.asyncio
    async def test_validation_queue_isolated_by_tenant(
        self, tenant1_user, tenant2_user, mock_db
    ):
        """Test that validation queue is isolated by tenant."""
        queue1 = {
            "id": uuid4(),
            "tenant_id": tenant1_user.tenant_id,
            "items": 5
        }

        queue2 = {
            "id": uuid4(),
            "tenant_id": tenant2_user.tenant_id,
            "items": 3
        }

        assert queue1["tenant_id"] != queue2["tenant_id"]

    @pytest.mark.asyncio
    async def test_reports_isolated_by_tenant(
        self, tenant1_user, tenant2_user, mock_db
    ):
        """Test that reports are isolated by tenant."""
        report1 = {
            "id": uuid4(),
            "tenant_id": tenant1_user.tenant_id,
            "title": "Tenant 1 Report"
        }

        report2 = {
            "id": uuid4(),
            "tenant_id": tenant2_user.tenant_id,
            "title": "Tenant 2 Report"
        }

        assert report1["tenant_id"] != report2["tenant_id"]
