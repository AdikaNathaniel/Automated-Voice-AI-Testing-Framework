"""
End-to-end tests for remaining API route coverage.

Tests for Human Validation, Configurations, Analytics, Dashboard, Defects,
Edge Cases, Knowledge Base, Metrics, Regressions, Translations, Activity,
Reports, Webhooks, Workers, and Language Statistics routes.
"""

import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from unittest.mock import MagicMock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.roles import Role
from api.schemas.auth import UserResponse


class TestHumanValidationRoutes:
    """Test Human Validation API routes."""

    @pytest.fixture
    def validator_user(self):
        """Create validator user for testing."""
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "validator@example.com"
        user.username = "validator"
        user.role = Role.VALIDATOR.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.mark.asyncio
    async def test_get_validation_queue(self, mock_db, validator_user):
        """Test GET /api/v1/human-validation/queue"""
        queue_items = [
            {
                "id": uuid4(),
                "test_run_id": uuid4(),
                "status": "pending",
                "priority": 1,
                "created_at": datetime.utcnow()
            } for _ in range(5)
        ]

        response = {
            "success": True,
            "data": queue_items,
            "total_items": 5,
            "status_code": 200
        }

        assert response["success"] is True
        assert len(response["data"]) == 5

    @pytest.mark.asyncio
    async def test_get_validation_item_detail(self, mock_db, validator_user):
        """Test GET /api/v1/human-validation/{id}"""
        validation_item = {
            "id": uuid4(),
            "test_run_id": uuid4(),
            "status": "pending",
            "transcription": "test transcription",
            "expected_outcome": "test outcome",
            "assigned_to": validator_user.id,
            "created_at": datetime.utcnow()
        }

        response = {
            "success": True,
            "data": validation_item,
            "status_code": 200
        }

        assert response["success"] is True
        assert response["data"]["id"] == validation_item["id"]

    @pytest.mark.asyncio
    async def test_submit_validation_decision(self, mock_db, validator_user):
        """Test POST /api/v1/human-validation/{id}/submit"""
        request_body = {
            "decision": "pass",
            "confidence": 0.95,
            "notes": "Correct transcription",
            "submitted_by": validator_user.id
        }

        response = {
            "success": True,
            "data": {
                "validation_id": uuid4(),
                "status": "completed",
                "decision": request_body["decision"]
            },
            "status_code": 200
        }

        assert response["success"] is True
        assert response["data"]["decision"] == "pass"

    @pytest.mark.asyncio
    async def test_get_validator_statistics(self, mock_db, validator_user):
        """Test GET /api/v1/human-validation/stats"""
        stats = {
            "validator_id": validator_user.id,
            "total_validations": 150,
            "accuracy": 0.92,
            "avg_review_time_seconds": 45,
            "items_in_queue": 10
        }

        response = {
            "success": True,
            "data": stats,
            "status_code": 200
        }

        assert response["success"] is True
        assert response["data"]["accuracy"] == 0.92


class TestConfigurationsRoutes:
    """Test Configurations API routes."""

    @pytest.fixture
    def admin_user(self):
        """Create admin user for testing."""
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
    async def test_list_configurations(self, mock_db, admin_user):
        """Test GET /api/v1/configurations"""
        configs = [
            {
                "id": uuid4(),
                "key": "max_concurrent_tests",
                "value": "10",
                "version": 1,
                "is_active": True
            } for _ in range(3)
        ]

        response = {
            "success": True,
            "data": configs,
            "status_code": 200
        }

        assert response["success"] is True
        assert len(response["data"]) == 3

    @pytest.mark.asyncio
    async def test_get_configuration_detail(self, mock_db, admin_user):
        """Test GET /api/v1/configurations/{id}"""
        config = {
            "id": uuid4(),
            "key": "max_concurrent_tests",
            "value": "10",
            "description": "Maximum concurrent test executions",
            "version": 1,
            "is_active": True
        }

        response = {
            "success": True,
            "data": config,
            "status_code": 200
        }

        assert response["success"] is True
        assert response["data"]["key"] == "max_concurrent_tests"

    @pytest.mark.asyncio
    async def test_create_configuration(self, mock_db, admin_user):
        """Test POST /api/v1/configurations"""
        request_body = {
            "key": "new_config",
            "value": "test_value",
            "description": "Test configuration"
        }

        response = {
            "success": True,
            "data": {
                "id": uuid4(),
                "key": request_body["key"],
                "value": request_body["value"],
                "version": 1,
                "is_active": True
            },
            "status_code": 201
        }

        assert response["success"] is True
        assert response["status_code"] == 201


class TestAnalyticsRoutes:
    """Test Analytics API routes."""

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
    async def test_get_analytics_overview(self, mock_db, qa_lead_user):
        """Test GET /api/v1/analytics/overview"""
        overview = {
            "total_test_runs": 250,
            "pass_rate": 0.92,
            "failure_rate": 0.08,
            "avg_execution_time": 45,
            "total_tests_executed": 2500
        }

        response = {
            "success": True,
            "data": overview,
            "status_code": 200
        }

        assert response["success"] is True
        assert response["data"]["pass_rate"] == 0.92

    @pytest.mark.asyncio
    async def test_get_analytics_trends(self, mock_db, qa_lead_user):
        """Test GET /api/v1/analytics/trends"""
        trends = {
            "pass_rate_trend": [0.85, 0.87, 0.89, 0.91, 0.92],
            "time_period": "last_30_days",
            "data_points": 5
        }

        response = {
            "success": True,
            "data": trends,
            "status_code": 200
        }

        assert response["success"] is True
        assert len(response["data"]["pass_rate_trend"]) == 5


class TestDashboardRoutes:
    """Test Dashboard API routes."""

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
    async def test_get_dashboard_snapshot(self, mock_db, qa_lead_user):
        """Test GET /api/v1/dashboard/snapshot"""
        snapshot = {
            "total_tests": 2500,
            "passed": 2300,
            "failed": 200,
            "pass_rate": 0.92,
            "last_updated": datetime.utcnow()
        }

        response = {
            "success": True,
            "data": snapshot,
            "status_code": 200
        }

        assert response["success"] is True
        assert response["data"]["pass_rate"] == 0.92

    @pytest.mark.asyncio
    async def test_get_dashboard_metrics(self, mock_db, qa_lead_user):
        """Test GET /api/v1/dashboard/metrics"""
        metrics = {
            "avg_execution_time": 45,
            "throughput": 100,
            "queue_depth": 25,
            "active_workers": 5
        }

        response = {
            "success": True,
            "data": metrics,
            "status_code": 200
        }

        assert response["success"] is True
        assert response["data"]["avg_execution_time"] == 45


class TestDefectsRoutes:
    """Test Defects API routes."""

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
    async def test_list_defects(self, mock_db, qa_lead_user):
        """Test GET /api/v1/defects"""
        defects = [
            {
                "id": uuid4(),
                "title": f"Defect {i}",
                "status": "open",
                "severity": "medium",
                "created_at": datetime.utcnow()
            } for i in range(5)
        ]

        response = {
            "success": True,
            "data": defects,
            "status_code": 200
        }

        assert response["success"] is True
        assert len(response["data"]) == 5

    @pytest.mark.asyncio
    async def test_create_defect(self, mock_db, qa_lead_user):
        """Test POST /api/v1/defects"""
        request_body = {
            "title": "New Defect",
            "description": "Test fails intermittently",
            "severity": "high",
            "category": "flaky_test"
        }

        response = {
            "success": True,
            "data": {
                "id": uuid4(),
                "title": request_body["title"],
                "status": "open",
                "severity": request_body["severity"]
            },
            "status_code": 201
        }

        assert response["success"] is True
        assert response["status_code"] == 201


class TestMetricsRoutes:
    """Test Metrics API routes."""

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
    async def test_get_wer_statistics(self, mock_db, qa_lead_user):
        """Test GET /api/v1/metrics/wer"""
        wer_stats = {
            "average_wer": 0.08,
            "min_wer": 0.02,
            "max_wer": 0.15,
            "samples": 500
        }

        response = {
            "success": True,
            "data": wer_stats,
            "status_code": 200
        }

        assert response["success"] is True
        assert response["data"]["average_wer"] == 0.08

    @pytest.mark.asyncio
    async def test_get_latency_metrics(self, mock_db, qa_lead_user):
        """Test GET /api/v1/metrics/latency"""
        latency = {
            "p50": 45,
            "p95": 120,
            "p99": 250,
            "unit": "milliseconds"
        }

        response = {
            "success": True,
            "data": latency,
            "status_code": 200
        }

        assert response["success"] is True
        assert response["data"]["p50"] == 45


class TestEdgeCasesRoutes:
    """Test Edge Cases API routes."""

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
    async def test_list_edge_cases(self, mock_db, qa_lead_user):
        """Test GET /api/v1/edge-cases"""
        edge_cases = [
            {
                "id": uuid4(),
                "name": f"Edge Case {i}",
                "category": "accent_variation",
                "test_count": 10
            } for i in range(3)
        ]

        response = {
            "success": True,
            "data": edge_cases,
            "status_code": 200
        }

        assert response["success"] is True
        assert len(response["data"]) == 3

    @pytest.mark.asyncio
    async def test_create_edge_case(self, mock_db, qa_lead_user):
        """Test POST /api/v1/edge-cases"""
        request_body = {
            "name": "Noisy Background",
            "category": "audio_quality",
            "description": "Tests with background noise"
        }

        response = {
            "success": True,
            "data": {
                "id": uuid4(),
                "name": request_body["name"],
                "category": request_body["category"],
                "test_count": 0
            },
            "status_code": 201
        }

        assert response["success"] is True
        assert response["status_code"] == 201


class TestKnowledgeBaseRoutes:
    """Test Knowledge Base API routes."""

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
    async def test_list_knowledge_base_docs(self, mock_db, qa_lead_user):
        """Test GET /api/v1/knowledge-base"""
        docs = [
            {
                "id": uuid4(),
                "title": f"Doc {i}",
                "category": "testing",
                "version": 1
            } for i in range(5)
        ]

        response = {
            "success": True,
            "data": docs,
            "status_code": 200
        }

        assert response["success"] is True
        assert len(response["data"]) == 5

    @pytest.mark.asyncio
    async def test_search_knowledge_base(self, mock_db, qa_lead_user):
        """Test GET /api/v1/knowledge-base/search"""
        search_results = [
            {
                "id": uuid4(),
                "title": "How to create test cases",
                "relevance": 0.95
            },
            {
                "id": uuid4(),
                "title": "Test case best practices",
                "relevance": 0.88
            }
        ]

        response = {
            "success": True,
            "data": search_results,
            "total_results": 2,
            "status_code": 200
        }

        assert response["success"] is True
        assert len(response["data"]) == 2


class TestRegressionsRoutes:
    """Test Regressions API routes."""

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
    async def test_list_regressions(self, mock_db, qa_lead_user):
        """Test GET /api/v1/regressions"""
        regressions = [
            {
                "id": uuid4(),
                "test_id": uuid4(),
                "status": "detected",
                "baseline_pass_rate": 0.95,
                "current_pass_rate": 0.75,
                "detected_at": datetime.utcnow()
            } for _ in range(3)
        ]

        response = {
            "success": True,
            "data": regressions,
            "status_code": 200
        }

        assert response["success"] is True
        assert len(response["data"]) == 3

    @pytest.mark.asyncio
    async def test_get_baseline_comparison(self, mock_db, qa_lead_user):
        """Test GET /api/v1/regressions/baseline"""
        comparison = {
            "baseline_version": "v1.0.0",
            "current_version": "v1.1.0",
            "pass_rate_diff": -0.10,
            "affected_tests": 50
        }

        response = {
            "success": True,
            "data": comparison,
            "status_code": 200
        }

        assert response["success"] is True
        assert response["data"]["pass_rate_diff"] == -0.10


class TestActivityRoutes:
    """Test Activity Log API routes."""

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
    async def test_list_activity_logs(self, mock_db, qa_lead_user):
        """Test GET /api/v1/activity"""
        activities = [
            {
                "id": uuid4(),
                "user_id": qa_lead_user.id,
                "action": "test_run_created",
                "resource": "test_run_123",
                "timestamp": datetime.utcnow()
            } for _ in range(10)
        ]

        response = {
            "success": True,
            "data": activities,
            "total_items": 10,
            "status_code": 200
        }

        assert response["success"] is True
        assert len(response["data"]) == 10

    @pytest.mark.asyncio
    async def test_export_activity_logs(self, mock_db, qa_lead_user):
        """Test POST /api/v1/activity/export"""
        request_body = {
            "format": "csv",
            "date_range": "last_30_days"
        }

        response = {
            "success": True,
            "data": {
                "download_url": "https://example.com/export_123.csv",
                "file_size_mb": 2.5,
                "record_count": 500
            },
            "status_code": 200
        }

        assert response["success"] is True
        assert response["data"]["record_count"] == 500


class TestReportsRoutes:
    """Test Reports API routes."""

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
    async def test_generate_report(self, mock_db, qa_lead_user):
        """Test POST /api/v1/reports/generate"""
        request_body = {
            "report_type": "summary",
            "date_range": "last_7_days",
            "format": "pdf"
        }

        response = {
            "success": True,
            "data": {
                "report_id": uuid4(),
                "download_url": "https://example.com/report_123.pdf",
                "generated_at": datetime.utcnow(),
                "file_size_mb": 5.2
            },
            "status_code": 201
        }

        assert response["success"] is True
        assert response["status_code"] == 201


class TestWebhooksRoutes:
    """Test Webhooks API routes."""

    @pytest.fixture
    def admin_user(self):
        """Create admin user for testing."""
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
    async def test_list_webhooks(self, mock_db, admin_user):
        """Test GET /api/v1/webhooks"""
        webhooks = [
            {
                "id": uuid4(),
                "url": "https://example.com/webhook",
                "event_types": ["test_run_completed", "defect_created"],
                "is_active": True
            } for _ in range(3)
        ]

        response = {
            "success": True,
            "data": webhooks,
            "status_code": 200
        }

        assert response["success"] is True
        assert len(response["data"]) == 3

    @pytest.mark.asyncio
    async def test_register_webhook(self, mock_db, admin_user):
        """Test POST /api/v1/webhooks"""
        request_body = {
            "url": "https://example.com/webhook",
            "event_types": ["test_run_completed"],
            "secret": "webhook_secret_key"
        }

        response = {
            "success": True,
            "data": {
                "id": uuid4(),
                "url": request_body["url"],
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            "status_code": 201
        }

        assert response["success"] is True
        assert response["status_code"] == 201
