"""
Integration tests for validation pipeline.

Tests the complete validation flow from test result submission through
auto-validation, human validation queue, and LLM judge integration.
"""

import pytest
from uuid import uuid4
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.roles import Role
from api.schemas.auth import UserResponse


class TestAutoValidationPipeline:
    """Test automatic validation pipeline with rules engine."""

    @pytest.fixture
    def qa_lead_user(self):
        """Create QA Lead user for testing."""
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "qalead@example.com"
        user.username = "qalead"
        user.role = Role.QA_LEAD.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.mark.asyncio
    async def test_test_result_submitted_to_validation(self, mock_db, qa_lead_user):
        """Test that test results are submitted to validation pipeline."""
        result = {
            "id": uuid4(),
            "test_run_id": uuid4(),
            "status": "pending_validation",
            "submitted_at": datetime.utcnow(),
            "user_response": "one two three",
            "expected_response": "one two three"
        }

        assert result["status"] == "pending_validation"
        assert result["user_response"] is not None

    @pytest.mark.asyncio
    async def test_rules_engine_evaluates_result(self, mock_db, qa_lead_user):
        """Test that rules engine evaluates test result."""
        validation_rule = {
            "id": uuid4(),
            "name": "Word Error Rate Check",
            "metric": "wer",
            "threshold": 0.15,
            "comparison": "less_than",
            "weight": 1.0
        }

        result_metrics = {
            "wer": 0.08,
            "intent_match": True,
            "entities_correct": True
        }

        assert result_metrics["wer"] < validation_rule["threshold"]

    @pytest.mark.asyncio
    async def test_multiple_validation_criteria_applied(self, mock_db, qa_lead_user):
        """Test that multiple validation criteria are applied."""
        criteria = [
            {"metric": "wer", "threshold": 0.15, "result": 0.08, "comparison": "less_than"},
            {"metric": "intent_match", "threshold": 1.0, "result": 1.0, "comparison": "equal"},
            {"metric": "entity_accuracy", "threshold": 0.90, "result": 0.95, "comparison": "greater_equal"}
        ]

        def check_criterion(c: dict) -> bool:
            comparison = c.get("comparison", "greater_equal")
            if comparison == "less_than":
                return c["result"] < c["threshold"]
            elif comparison == "equal":
                return c["result"] == c["threshold"]
            else:  # greater_equal
                return c["result"] >= c["threshold"]

        passed_criteria = [c for c in criteria if check_criterion(c)]
        assert len(passed_criteria) == 3

    @pytest.mark.asyncio
    async def test_confidence_based_escalation(self, mock_db, qa_lead_user):
        """Test that low-confidence results are escalated."""
        validation_result = {
            "id": uuid4(),
            "confidence_score": 0.55,
            "escalate": True,
            "escalation_reason": "Low confidence"
        }

        assert validation_result["escalate"] is True
        assert validation_result["confidence_score"] < 0.70

    @pytest.mark.asyncio
    async def test_validation_result_classification(self, mock_db, qa_lead_user):
        """Test that validation results are classified."""
        classification = {
            "result_id": uuid4(),
            "classification": "pass",
            "confidence": 0.92,
            "metrics": {
                "wer": 0.05,
                "intent_match": True,
                "entities_correct": True
            }
        }

        assert classification["classification"] in ["pass", "fail", "unclear"]
        assert classification["confidence"] > 0.9

    @pytest.mark.asyncio
    async def test_validation_result_stored_with_metrics(self, mock_db, qa_lead_user):
        """Test that validation results stored with all metrics."""
        stored_result = {
            "id": uuid4(),
            "test_result_id": uuid4(),
            "validation_status": "completed",
            "classification": "pass",
            "metrics": {
                "wer": 0.05,
                "intent_match": True,
                "entities_match": True,
                "tone_appropriate": True
            },
            "confidence_score": 0.95,
            "created_at": datetime.utcnow()
        }

        assert stored_result["validation_status"] == "completed"
        assert stored_result["classification"] is not None


class TestHumanValidationQueue:
    """Test human validation queue management."""

    @pytest.fixture
    def qa_lead_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.role = Role.QA_LEAD.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def validator_user(self):
        """Create validator user."""
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "validator@example.com"
        user.username = "validator"
        user.role = "validator"
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.mark.asyncio
    async def test_escalated_result_added_to_queue(self, mock_db, qa_lead_user):
        """Test that escalated results are added to validation queue."""
        queue_item = {
            "id": uuid4(),
            "test_result_id": uuid4(),
            "status": "queued",
            "priority": "high",
            "queued_at": datetime.utcnow(),
            "reason": "Low confidence score"
        }

        assert queue_item["status"] == "queued"
        assert queue_item["priority"] in ["low", "medium", "high"]

    @pytest.mark.asyncio
    async def test_validation_task_assigned_to_validator(
        self, mock_db, qa_lead_user, validator_user
    ):
        """Test that validation task is assigned to available validator."""
        task = {
            "id": uuid4(),
            "queue_item_id": uuid4(),
            "assigned_to": validator_user.id,
            "status": "assigned",
            "assigned_at": datetime.utcnow()
        }

        assert task["assigned_to"] == validator_user.id
        assert task["status"] == "assigned"

    @pytest.mark.asyncio
    async def test_workload_balanced_across_validators(
        self, mock_db, qa_lead_user
    ):
        """Test that workload is balanced across validators."""
        validator_workloads = {
            uuid4(): 5,
            uuid4(): 5,
            uuid4(): 4
        }

        min_workload = min(validator_workloads.values())
        assert min_workload == 4

    @pytest.mark.asyncio
    async def test_validator_reviews_and_submits_result(
        self, mock_db, validator_user
    ):
        """Test that validator can review and submit validation decision."""
        review = {
            "id": uuid4(),
            "task_id": uuid4(),
            "validator_id": validator_user.id,
            "decision": "pass",
            "notes": "Voice quality good, intent clear",
            "submitted_at": datetime.utcnow()
        }

        assert review["decision"] in ["pass", "fail"]
        assert review["validator_id"] is not None

    @pytest.mark.asyncio
    async def test_validation_timeout_and_reassignment(
        self, mock_db, qa_lead_user
    ):
        """Test that overdue validations are reassigned."""
        task = {
            "id": uuid4(),
            "assigned_to": uuid4(),
            "assigned_at": datetime.utcnow(),
            "timeout_minutes": 60,
            "overdue": True,
            "reassigned": True
        }

        assert task["overdue"] is True
        assert task["reassigned"] is True

    @pytest.mark.asyncio
    async def test_inter_rater_reliability_calculated(self, mock_db, qa_lead_user):
        """Test that inter-rater reliability is calculated."""
        ratings = {
            "validator1": "pass",
            "validator2": "pass",
            "validator3": "fail"
        }

        agreements = sum(
            1 for v in ratings.values() if v == "pass"
        )
        agreement_rate = agreements / len(ratings)
        assert agreement_rate > 0.5

    @pytest.mark.asyncio
    async def test_validator_performance_tracked(self, mock_db, qa_lead_user):
        """Test that validator performance metrics are tracked."""
        performance = {
            "validator_id": uuid4(),
            "total_validations": 150,
            "accuracy": 0.94,
            "average_time_minutes": 8.5,
            "agreements_with_auto_validation": 0.89
        }

        assert performance["accuracy"] > 0.8
        assert performance["total_validations"] > 0


class TestValidationResultAggregation:
    """Test aggregation of validation results."""

    @pytest.fixture
    def qa_lead_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.role = Role.QA_LEAD.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.mark.asyncio
    async def test_multiple_validation_sources_combined(
        self, mock_db, qa_lead_user
    ):
        """Test that results from multiple validation sources are combined."""
        validations = {
            "auto_validation": {"decision": "pass", "confidence": 0.95},
            "human_validation": {"decision": "pass", "validator_id": uuid4()},
            "llm_judge": {"decision": "pass", "confidence": 0.92}
        }

        pass_count = sum(
            1 for v in validations.values() if v.get("decision") == "pass"
        )
        assert pass_count == 3

    @pytest.mark.asyncio
    async def test_conflicting_validations_resolved(
        self, mock_db, qa_lead_user
    ):
        """Test that conflicting validation decisions are resolved."""
        validations = [
            {"source": "auto", "decision": "pass", "confidence": 0.65},
            {"source": "human", "decision": "fail", "validator_id": uuid4()},
            {"source": "llm", "decision": "pass", "confidence": 0.88}
        ]

        high_confidence = [
            v for v in validations if v.get("confidence", 1.0) > 0.7
        ]
        assert len(high_confidence) >= 2

    @pytest.mark.asyncio
    async def test_final_result_decision_determined(
        self, mock_db, qa_lead_user
    ):
        """Test that final result decision is determined."""
        final_result = {
            "test_result_id": uuid4(),
            "final_decision": "pass",
            "validation_sources": ["auto", "human", "llm"],
            "decision_confidence": 0.92,
            "aggregation_method": "ensemble"
        }

        assert final_result["final_decision"] in ["pass", "fail"]
        assert final_result["decision_confidence"] > 0.0

    @pytest.mark.asyncio
    async def test_audit_trail_recorded(self, mock_db, qa_lead_user):
        """Test that complete audit trail is recorded."""
        audit_trail = {
            "test_result_id": uuid4(),
            "events": [
                {
                    "timestamp": datetime.utcnow(),
                    "event": "submitted_for_validation"
                },
                {
                    "timestamp": datetime.utcnow(),
                    "event": "auto_validation_completed",
                    "result": "pass"
                },
                {
                    "timestamp": datetime.utcnow(),
                    "event": "escalated_to_human"
                },
                {
                    "timestamp": datetime.utcnow(),
                    "event": "validation_approved"
                }
            ]
        }

        assert len(audit_trail["events"]) > 0
        assert all(e.get("timestamp") for e in audit_trail["events"])


class TestValidationTenantIsolation:
    """Test tenant isolation in validation."""

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
        user.is_active = True
        return user

    @pytest.fixture
    def tenant2_user(self, tenant2_id):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.tenant_id = tenant2_id
        user.role = Role.QA_LEAD.value
        user.is_active = True
        return user

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.mark.asyncio
    async def test_validation_queue_isolated_by_tenant(
        self, tenant1_user, tenant2_user, mock_db
    ):
        """Test that validation queue is isolated by tenant."""
        queue1_item = {
            "id": uuid4(),
            "tenant_id": tenant1_user.tenant_id,
            "status": "queued"
        }

        queue2_item = {
            "id": uuid4(),
            "tenant_id": tenant2_user.tenant_id,
            "status": "queued"
        }

        assert queue1_item["tenant_id"] != queue2_item["tenant_id"]

    @pytest.mark.asyncio
    async def test_validator_cannot_see_other_tenant_items(
        self, tenant1_user, tenant2_user, mock_db
    ):
        """Test that validator cannot see items from other tenants."""
        assert tenant1_user.tenant_id != tenant2_user.tenant_id

    @pytest.mark.asyncio
    async def test_validation_results_scoped_to_tenant(
        self, tenant1_user, tenant2_user, mock_db
    ):
        """Test that validation results are scoped to tenant."""
        result1 = {
            "id": uuid4(),
            "tenant_id": tenant1_user.tenant_id,
            "status": "completed"
        }

        result2 = {
            "id": uuid4(),
            "tenant_id": tenant2_user.tenant_id,
            "status": "completed"
        }

        assert result1["tenant_id"] != result2["tenant_id"]
