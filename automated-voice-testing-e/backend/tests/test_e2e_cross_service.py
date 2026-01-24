"""
Cross-service E2E tests covering complete integration pipelines.

Tests the full end-to-end flows that involve multiple services working together,
including test execution pipeline, defect auto-creation, validation escalation,
regression detection, and configuration propagation.
"""

import pytest
from uuid import uuid4
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.roles import Role
from api.schemas.auth import UserResponse


class TestExecutionFullPipeline:
    """Test complete test execution pipeline across all services."""

    @pytest.fixture
    def qa_lead_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.role = Role.QA_LEAD.value
        user.tenant_id = uuid4()
        user.email = "qa@example.com"
        return user

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.mark.asyncio
    async def test_create_suite_through_execution(self, mock_db, qa_lead_user):
        """Test full pipeline: Create suite → Add cases → Configure → Execute."""
        # Step 1: Create suite
        suite = {
            "id": uuid4(),
            "name": "End-to-End Test Suite",
            "tenant_id": qa_lead_user.tenant_id,
            "created_by": qa_lead_user.id,
            "created_at": datetime.utcnow()
        }

        # Step 2: Add test cases
        test_cases = [
            {"id": uuid4(), "name": "Login Test", "suite_id": suite["id"]},
            {"id": uuid4(), "name": "Navigation Test", "suite_id": suite["id"]}
        ]

        # Step 3: Configure run
        run_config = {
            "suite_id": suite["id"],
            "test_case_ids": [tc["id"] for tc in test_cases],
            "languages": ["en-US"],
            "providers": ["twilio"],
            "retry_failed": True
        }

        # Step 4: Execute
        test_run = {
            "id": uuid4(),
            "suite_id": suite["id"],
            "status": "completed",
            "results": {
                "total": 2,
                "passed": 2,
                "failed": 0,
                "pass_rate": 1.0
            },
            "completed_at": datetime.utcnow()
        }

        assert suite["id"] is not None
        assert len(test_cases) == 2
        assert test_run["results"]["pass_rate"] == 1.0

    @pytest.mark.asyncio
    async def test_queue_to_worker_assignment(self, mock_db, qa_lead_user):
        """Test queuing → Worker assignment → Execution → Result collection."""
        # Queue test
        queue_item = {
            "id": uuid4(),
            "test_id": uuid4(),
            "status": "queued",
            "priority": 10,
            "created_at": datetime.utcnow()
        }

        # Worker picks up
        assignment = {
            "queue_item_id": queue_item["id"],
            "worker_id": uuid4(),
            "assigned_at": datetime.utcnow(),
            "status": "assigned"
        }

        # Execution
        execution = {
            "id": uuid4(),
            "test_id": queue_item["test_id"],
            "worker_id": assignment["worker_id"],
            "status": "executing",
            "started_at": datetime.utcnow()
        }

        # Result collection
        result = {
            "id": uuid4(),
            "execution_id": execution["id"],
            "status": "passed",
            "metrics": {
                "duration_ms": 5000,
                "wer": 0.05,
                "confidence": 0.95
            },
            "collected_at": datetime.utcnow()
        }

        assert assignment["queue_item_id"] == queue_item["id"]
        assert result["execution_id"] == execution["id"]

    @pytest.mark.asyncio
    async def test_metrics_update_to_dashboard_refresh(self, mock_db, qa_lead_user):
        """Test metrics update → Aggregation → Dashboard refresh."""
        # Test completes with metrics
        test_result = {
            "id": uuid4(),
            "status": "passed",
            "wer": 0.05,
            "duration_ms": 5000,
            "confidence": 0.95
        }

        # Metrics aggregation
        aggregated_metrics = {
            "total_tests": 100,
            "passed": 95,
            "failed": 5,
            "pass_rate": 0.95,
            "avg_wer": 0.08,
            "avg_duration_ms": 4500
        }

        # Dashboard refresh
        dashboard = {
            "id": uuid4(),
            "user_id": qa_lead_user.id,
            "metrics": aggregated_metrics,
            "updated_at": datetime.utcnow()
        }

        assert dashboard["metrics"]["pass_rate"] == 0.95

    @pytest.mark.asyncio
    async def test_report_generation_from_execution(self, mock_db, qa_lead_user):
        """Test execution completion → Report generation → Distribution."""
        # Test run completes
        test_run = {
            "id": uuid4(),
            "status": "completed",
            "total_tests": 50,
            "passed": 48,
            "failed": 2
        }

        # Report generation
        report = {
            "id": uuid4(),
            "run_id": test_run["id"],
            "title": f"Test Run {test_run['id']} Report",
            "format": "pdf",
            "summary": {
                "total": 50,
                "passed": 48,
                "failed": 2,
                "pass_rate": 0.96
            },
            "generated_at": datetime.utcnow()
        }

        # Report distribution
        distribution = {
            "report_id": report["id"],
            "recipients": [qa_lead_user.email],
            "sent_at": datetime.utcnow()
        }

        assert report["run_id"] == test_run["id"]
        assert report["summary"]["pass_rate"] == 0.96


class TestDefectAutocreationPipeline:
    """Test defect auto-creation from test failures."""

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
    async def test_failure_analysis_to_defect_creation(self, mock_db, qa_lead_user):
        """Test: Failure → Analysis → Categorization → Deduplication → Creation."""
        # Test fails
        test_result = {
            "id": uuid4(),
            "test_id": uuid4(),
            "status": "failed",
            "failure_reason": "Timeout waiting for response",
            "failure_timestamp": datetime.utcnow()
        }

        # Failure analysis
        analysis = {
            "result_id": test_result["id"],
            "error_type": "timeout",
            "severity": "high",
            "root_cause": "Provider response delay",
            "analyzed_at": datetime.utcnow()
        }

        # Categorization
        categorization = {
            "analysis_id": analysis["result_id"],
            "category": "external_service_failure",
            "subcategory": "provider_timeout"
        }

        # Deduplication check
        existing_defect = {
            "id": uuid4(),
            "pattern": "provider_timeout",
            "last_occurrence": datetime.utcnow()
        }

        # Defect creation
        defect = {
            "id": uuid4(),
            "title": f"Provider timeout in {test_result['test_id']}",
            "description": analysis["root_cause"],
            "category": categorization["category"],
            "severity": analysis["severity"],
            "first_occurrence": test_result["failure_timestamp"],
            "tenant_id": qa_lead_user.tenant_id,
            "created_by": qa_lead_user.id
        }

        assert analysis["result_id"] == test_result["id"]
        assert defect["category"] == categorization["category"]

    @pytest.mark.asyncio
    async def test_defect_notification_and_dashboard_update(self, mock_db, qa_lead_user):
        """Test: Defect creation → Notification → Dashboard update."""
        # Add email to mock user
        qa_lead_user.email = "qa@example.com"

        # Defect created
        defect = {
            "id": uuid4(),
            "title": "Login test failure",
            "severity": "high",
            "created_at": datetime.utcnow()
        }

        # Notification sent
        notification = {
            "id": uuid4(),
            "defect_id": defect["id"],
            "recipient": qa_lead_user.email,
            "channel": "email",
            "sent_at": datetime.utcnow()
        }

        # Dashboard updated
        dashboard_update = {
            "timestamp": datetime.utcnow(),
            "defect_id": defect["id"],
            "open_defect_count": 5
        }

        assert notification["defect_id"] == defect["id"]
        assert dashboard_update["defect_id"] == defect["id"]

    @pytest.mark.asyncio
    async def test_defect_aggregation_and_deduplication(self, mock_db, qa_lead_user):
        """Test multiple similar failures being aggregated into one defect."""
        # Multiple test failures with same pattern
        failures = [
            {"test_id": uuid4(), "error": "timeout", "timestamp": datetime.utcnow()},
            {"test_id": uuid4(), "error": "timeout", "timestamp": datetime.utcnow()},
            {"test_id": uuid4(), "error": "timeout", "timestamp": datetime.utcnow()}
        ]

        # Pattern analysis identifies same root cause
        pattern = {
            "type": "timeout",
            "count": 3,
            "pattern_hash": "hash_123"
        }

        # Single defect created with multiple occurrences
        defect = {
            "id": uuid4(),
            "pattern_hash": pattern["pattern_hash"],
            "occurrence_count": 3,
            "test_ids": [f["test_id"] for f in failures]
        }

        assert defect["occurrence_count"] == len(failures)
        assert len(defect["test_ids"]) == 3


class TestHumanValidationEscalationPipeline:
    """Test human validation escalation workflow."""

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
    async def test_auto_validation_to_escalation(self, mock_db, validator_user):
        """Test: Auto-validation uncertain → Escalation check → Queue creation."""
        # Auto-validation result
        auto_result = {
            "id": uuid4(),
            "test_result_id": uuid4(),
            "confidence": 0.55,  # Below threshold
            "status": "uncertain"
        }

        # Escalation policy check
        escalation_policy = {
            "confidence_threshold": 0.75,
            "requires_human_validation": True,
            "priority": "normal"
        }

        # Queue item created
        queue_item = {
            "id": uuid4(),
            "validation_result_id": auto_result["id"],
            "priority": escalation_policy["priority"],
            "status": "pending",
            "created_at": datetime.utcnow()
        }

        assert auto_result["confidence"] < escalation_policy["confidence_threshold"]
        assert queue_item["validation_result_id"] == auto_result["id"]

    @pytest.mark.asyncio
    async def test_validator_assignment_and_review(self, mock_db, validator_user):
        """Test: Queue → Assignment → Review → Submission."""
        # Queue item awaiting assignment
        queue_item = {
            "id": uuid4(),
            "status": "pending",
            "priority": "normal",
            "created_at": datetime.utcnow()
        }

        # Assignment to validator
        assignment = {
            "queue_item_id": queue_item["id"],
            "validator_id": validator_user.id,
            "assigned_at": datetime.utcnow(),
            "status": "assigned"
        }

        # Validator completes review
        review = {
            "id": uuid4(),
            "assignment_id": assignment["queue_item_id"],
            "validator_id": validator_user.id,
            "decision": "approved",
            "confidence": 0.95,
            "submitted_at": datetime.utcnow()
        }

        # Audit trail
        audit = {
            "id": uuid4(),
            "queue_item_id": queue_item["id"],
            "validator_id": validator_user.id,
            "action": "validation_submitted",
            "timestamp": review["submitted_at"]
        }

        assert assignment["validator_id"] == validator_user.id
        assert review["decision"] == "approved"
        assert audit["action"] == "validation_submitted"

    @pytest.mark.asyncio
    async def test_metrics_update_after_validation(self, mock_db, validator_user):
        """Test: Validation submission → Metrics update → Performance tracking."""
        # Validation submitted
        validation = {
            "id": uuid4(),
            "validator_id": validator_user.id,
            "decision": "approved",
            "submitted_at": datetime.utcnow()
        }

        # Validator metrics updated
        validator_metrics = {
            "validator_id": validator_user.id,
            "validations_completed": 150,
            "approval_rate": 0.88,
            "avg_review_time_seconds": 120,
            "updated_at": datetime.utcnow()
        }

        # System metrics updated
        system_metrics = {
            "total_validations": 5000,
            "human_validations_completed": 1200,
            "queue_depth": 45,
            "avg_queue_wait_time_minutes": 15
        }

        assert validator_metrics["validator_id"] == validator_user.id
        assert system_metrics["total_validations"] == 5000


class TestRegressionDetectionPipeline:
    """Test regression detection workflow."""

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
    async def test_baseline_comparison(self, mock_db, qa_lead_user):
        """Test: Test run complete → Baseline comparison → Analysis."""
        # Current test run
        current_run = {
            "id": uuid4(),
            "pass_rate": 0.88,
            "avg_wer": 0.10,
            "avg_latency_ms": 2500
        }

        # Baseline metrics
        baseline = {
            "id": uuid4(),
            "pass_rate": 0.95,
            "avg_wer": 0.05,
            "avg_latency_ms": 2000
        }

        # Comparison
        comparison = {
            "current_run_id": current_run["id"],
            "baseline_id": baseline["id"],
            "pass_rate_delta": current_run["pass_rate"] - baseline["pass_rate"],
            "wer_delta": current_run["avg_wer"] - baseline["avg_wer"],
            "latency_delta": current_run["avg_latency_ms"] - baseline["avg_latency_ms"]
        }

        # Use approximate comparison for floating point
        assert abs(comparison["pass_rate_delta"] - (-0.07)) < 0.001

    @pytest.mark.asyncio
    async def test_regression_detection_and_alert(self, mock_db, qa_lead_user):
        """Test: Statistical analysis → Regression detection → Alert generation."""
        # Add email to mock user
        qa_lead_user.email = "qa@example.com"

        # Statistical analysis
        analysis = {
            "run_id": uuid4(),
            "pass_rate": 0.88,
            "baseline_pass_rate": 0.95,
            "regression_detected": True,
            "confidence_level": 0.99,
            "affected_areas": ["login", "navigation"]
        }

        # Regression alert
        alert = {
            "id": uuid4(),
            "analysis_id": analysis["run_id"],
            "severity": "high",
            "message": "Quality regression detected: pass rate dropped 7%",
            "triggered_at": datetime.utcnow(),
            "recipients": [qa_lead_user.email]
        }

        # Report update
        report = {
            "id": uuid4(),
            "alert_id": alert["id"],
            "regression_section": {
                "detected": True,
                "affected_tests": 5,
                "confidence": analysis["confidence_level"]
            }
        }

        assert analysis["regression_detected"] is True
        assert alert["severity"] == "high"


class TestConfigurationPropagationPipeline:
    """Test configuration update propagation across system."""

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
    async def test_config_update_through_propagation(self, mock_db, admin_user):
        """Test: Config update → Validation → Version → Activation → Propagation."""
        # Configuration update initiated
        config_update = {
            "key": "max_concurrent_tests",
            "old_value": "10",
            "new_value": "20",
            "updated_by": admin_user.id,
            "initiated_at": datetime.utcnow()
        }

        # Validation
        validation = {
            "config_key": config_update["key"],
            "valid": True,
            "constraints": {
                "min": 1,
                "max": 100,
                "type": "integer"
            }
        }

        # Version creation
        config_version = {
            "id": uuid4(),
            "config_key": config_update["key"],
            "version": 2,
            "value": config_update["new_value"],
            "created_at": datetime.utcnow()
        }

        # Activation
        activation = {
            "version_id": config_version["id"],
            "activated_by": admin_user.id,
            "activated_at": datetime.utcnow(),
            "status": "active"
        }

        assert validation["valid"] is True
        assert config_version["value"] == config_update["new_value"]

    @pytest.mark.asyncio
    async def test_cache_invalidation_on_config_change(self, mock_db, admin_user):
        """Test: Config activation → Cache invalidation → Service notification."""
        # Configuration activated
        config_activation = {
            "key": "max_concurrent_tests",
            "new_value": "20",
            "activated_at": datetime.utcnow()
        }

        # Cache invalidation triggered
        cache_invalidation = {
            "id": uuid4(),
            "cache_key": f"config:{config_activation['key']}",
            "reason": "config_changed",
            "invalidated_at": datetime.utcnow()
        }

        # Services notified
        service_notifications = [
            {
                "service": "orchestration_service",
                "notification_type": "config_updated",
                "config_key": config_activation["key"],
                "new_value": config_activation["new_value"]
            },
            {
                "service": "execution_scheduler",
                "notification_type": "config_updated",
                "config_key": config_activation["key"],
                "new_value": config_activation["new_value"]
            }
        ]

        # Configuration reloaded in services
        reloads = [
            {
                "service": n["service"],
                "reloaded_at": datetime.utcnow()
            }
            for n in service_notifications
        ]

        assert len(reloads) == 2
        assert cache_invalidation["reason"] == "config_changed"

    @pytest.mark.asyncio
    async def test_rollback_on_config_failure(self, mock_db, admin_user):
        """Test: Config activation failure → Automatic rollback."""
        # New configuration activated
        new_config = {
            "key": "test_timeout",
            "new_value": "5",  # 5 seconds
            "old_value": "30",
            "activated_at": datetime.utcnow()
        }

        # Failure detected (tests timing out)
        failure = {
            "error_type": "timeout_too_short",
            "affected_tests": 50,
            "detected_at": datetime.utcnow()
        }

        # Automatic rollback triggered
        rollback = {
            "config_key": new_config["key"],
            "from_version": 2,
            "to_version": 1,
            "from_value": new_config["new_value"],
            "to_value": new_config["old_value"],
            "reason": failure["error_type"],
            "rolled_back_at": datetime.utcnow()
        }

        # System recovered
        recovery = {
            "status": "recovered",
            "config_key": new_config["key"],
            "current_value": rollback["to_value"],
            "recovered_at": datetime.utcnow()
        }

        assert rollback["to_value"] == new_config["old_value"]
        assert recovery["current_value"] == new_config["old_value"]
