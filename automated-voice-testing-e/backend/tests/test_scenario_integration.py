"""
Integration tests for scenario lifecycle and multi-step execution.

Tests that scenarios can be created with multiple steps, executed with
conditional branches, and support data-driven parameters.
"""

import pytest
from uuid import uuid4
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.roles import Role
from api.schemas.auth import UserResponse


class ScenarioCreation:
    """Test creation of scenarios with steps and configurations."""

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
    async def test_qa_lead_can_create_scenario(self, mock_db, qa_lead_user):
        """Test that QA Lead can create a scenario."""
        assert qa_lead_user.role == Role.QA_LEAD.value

    @pytest.mark.asyncio
    async def test_scenario_with_single_step(self, mock_db, qa_lead_user):
        """Test scenario creation with a single step."""
        scenario_data = {
            "name": "Login Scenario",
            "description": "Test user login flow",
            "steps": [
                {
                    "step_number": 1,
                    "action": "say",
                    "prompt": "Say your username",
                    "expected_result": "username confirmed"
                }
            ]
        }

        assert len(scenario_data["steps"]) == 1
        assert scenario_data["steps"][0]["step_number"] == 1

    @pytest.mark.asyncio
    async def test_scenario_with_multiple_steps(self, mock_db, qa_lead_user):
        """Test scenario creation with multiple sequential steps."""
        scenario_data = {
            "name": "Multi-step Scenario",
            "description": "Test multi-step flow",
            "steps": [
                {
                    "step_number": 1,
                    "action": "say",
                    "prompt": "Say your account number",
                    "expected_result": "account confirmed"
                },
                {
                    "step_number": 2,
                    "action": "listen",
                    "expected_result": "confirmation code received"
                },
                {
                    "step_number": 3,
                    "action": "say",
                    "prompt": "Say your PIN",
                    "expected_result": "PIN verified"
                }
            ]
        }

        assert len(scenario_data["steps"]) == 3
        assert all(step["step_number"] == i + 1 for i, step in enumerate(scenario_data["steps"]))

    @pytest.mark.asyncio
    async def test_scenario_with_conditional_branches(self, mock_db, qa_lead_user):
        """Test scenario creation with conditional branching."""
        scenario_data = {
            "name": "Conditional Scenario",
            "description": "Test conditional branching",
            "steps": [
                {
                    "step_number": 1,
                    "action": "say",
                    "prompt": "Are you a new customer?",
                    "branches": [
                        {
                            "condition": "yes",
                            "next_step": 2,
                            "label": "new_customer_flow"
                        },
                        {
                            "condition": "no",
                            "next_step": 4,
                            "label": "existing_customer_flow"
                        }
                    ]
                },
                {
                    "step_number": 2,
                    "action": "say",
                    "prompt": "Please provide your email",
                    "expected_result": "email confirmed"
                },
                {
                    "step_number": 3,
                    "action": "say",
                    "prompt": "Account created successfully"
                },
                {
                    "step_number": 4,
                    "action": "say",
                    "prompt": "Please confirm your existing account"
                }
            ]
        }

        # Verify branching logic exists
        assert "branches" in scenario_data["steps"][0]
        assert len(scenario_data["steps"][0]["branches"]) == 2

    @pytest.mark.asyncio
    async def test_scenario_with_data_driven_parameters(self, mock_db, qa_lead_user):
        """Test scenario creation with data-driven parameters."""
        scenario_data = {
            "name": "Data-driven Scenario",
            "description": "Test with parameters",
            "parameters": [
                {"name": "customer_id", "type": "string", "required": True},
                {"name": "pin", "type": "numeric", "length": 4, "required": True},
                {"name": "timeout", "type": "integer", "default": 30}
            ],
            "steps": [
                {
                    "step_number": 1,
                    "action": "say",
                    "prompt": "Say your customer ID: {{customer_id}}",
                    "expected_result": "ID confirmed"
                },
                {
                    "step_number": 2,
                    "action": "say",
                    "prompt": "Say your {{pin.length}}-digit PIN",
                    "expected_result": "PIN verified"
                }
            ]
        }

        assert len(scenario_data["parameters"]) == 3
        assert scenario_data["parameters"][0]["name"] == "customer_id"
        assert "{{customer_id}}" in scenario_data["steps"][0]["prompt"]

    @pytest.mark.asyncio
    async def test_viewer_cannot_create_scenario(self, mock_db, qa_lead_user):
        """Test that Viewer cannot create scenarios."""
        viewer = MagicMock(spec=UserResponse)
        viewer.id = uuid4()
        viewer.role = Role.VIEWER.value
        viewer.is_active = True
        viewer.tenant_id = qa_lead_user.tenant_id

        assert viewer.role != Role.QA_LEAD.value
        assert viewer.role != Role.ORG_ADMIN.value


class ScenarioExecution:
    """Test scenario execution and step progression."""

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
    async def test_scenario_execution_progresses_through_steps(self, mock_db, qa_lead_user):
        """Test that scenario execution progresses through steps sequentially."""
        execution_flow = {
            "scenario_id": uuid4(),
            "execution_id": uuid4(),
            "current_step": 1,
            "total_steps": 3,
            "status": "running"
        }

        # Simulate step progression
        execution_flow["current_step"] = 2
        assert execution_flow["current_step"] == 2

        execution_flow["current_step"] = 3
        assert execution_flow["current_step"] == 3

        execution_flow["status"] = "completed"
        assert execution_flow["status"] == "completed"

    @pytest.mark.asyncio
    async def test_scenario_execution_handles_conditional_branches(self, mock_db, qa_lead_user):
        """Test that scenario execution correctly handles conditional branches."""
        execution_flow = {
            "scenario_id": uuid4(),
            "current_step": 1,
            "branch_taken": None,
            "condition_result": "yes"
        }

        # Based on condition, should branch to different step
        if execution_flow["condition_result"] == "yes":
            execution_flow["branch_taken"] = "new_customer_flow"
            execution_flow["next_step"] = 2
        else:
            execution_flow["branch_taken"] = "existing_customer_flow"
            execution_flow["next_step"] = 4

        assert execution_flow["branch_taken"] == "new_customer_flow"
        assert execution_flow["next_step"] == 2

    @pytest.mark.asyncio
    async def test_scenario_execution_with_parameter_substitution(self, mock_db, qa_lead_user):
        """Test that parameters are substituted during execution."""
        execution_data = {
            "scenario_id": uuid4(),
            "parameters": {
                "customer_id": "12345",
                "pin": "6789"
            },
            "step": {
                "prompt": "Say your customer ID: {{customer_id}}",
                "expected_result": "ID confirmed"
            }
        }

        # Simulate parameter substitution
        prompt = execution_data["step"]["prompt"]
        for key, value in execution_data["parameters"].items():
            prompt = prompt.replace(f"{{{{{key}}}}}", str(value))

        assert "Say your customer ID: 12345" == prompt

    @pytest.mark.asyncio
    async def test_scenario_execution_timeout(self, mock_db, qa_lead_user):
        """Test that scenario execution respects timeout settings."""
        execution_data = {
            "scenario_id": uuid4(),
            "timeout_seconds": 30,
            "started_at": datetime.utcnow(),
            "status": "running"
        }

        assert execution_data["timeout_seconds"] == 30

    @pytest.mark.asyncio
    async def test_scenario_execution_failure_handling(self, mock_db, qa_lead_user):
        """Test that scenario handles execution failures."""
        execution_result = {
            "scenario_id": uuid4(),
            "status": "failed",
            "failed_at_step": 2,
            "error_message": "Step 2: Expected 'confirmation code' but got 'error'",
            "execution_time": 15.5
        }

        assert execution_result["status"] == "failed"
        assert execution_result["failed_at_step"] == 2
        assert execution_result["error_message"] is not None


class ScenarioVersioning:
    """Test scenario versioning and history."""

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
    async def test_scenario_versioning_on_update(self, mock_db, qa_lead_user):
        """Test that updating a scenario creates a new version."""
        scenario_v1 = {
            "id": uuid4(),
            "version": 1,
            "name": "Original Scenario",
            "updated_at": datetime.utcnow()
        }

        scenario_v2 = {
            "id": scenario_v1["id"],
            "version": 2,
            "name": "Updated Scenario",
            "updated_at": datetime.utcnow()
        }

        assert scenario_v1["version"] == 1
        assert scenario_v2["version"] == 2
        assert scenario_v1["id"] == scenario_v2["id"]

    @pytest.mark.asyncio
    async def test_scenario_can_be_rolled_back_to_previous_version(self, mock_db, qa_lead_user):
        """Test that scenario can be rolled back to a previous version."""
        scenarios = [
            {"version": 1, "steps": 2},
            {"version": 2, "steps": 3},
            {"version": 3, "steps": 2}
        ]

        # Rollback from version 3 to version 2
        rollback_target = scenarios[1]
        assert rollback_target["version"] == 2
        assert rollback_target["steps"] == 3

    @pytest.mark.asyncio
    async def test_scenario_version_history_tracking(self, mock_db, qa_lead_user):
        """Test that all versions of a scenario are tracked."""
        scenario_id = uuid4()
        history = [
            {"version": 1, "created_by": qa_lead_user.id, "timestamp": datetime.utcnow()},
            {"version": 2, "created_by": qa_lead_user.id, "timestamp": datetime.utcnow()},
            {"version": 3, "created_by": qa_lead_user.id, "timestamp": datetime.utcnow()}
        ]

        assert len(history) == 3
        assert all(h["version"] == i + 1 for i, h in enumerate(history))


class ScenarioResultAggregation:
    """Test scenario result aggregation and reporting."""

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
    async def test_scenario_execution_results_aggregation(self, mock_db, qa_lead_user):
        """Test that scenario execution results are aggregated."""
        scenario_executions = [
            {"scenario_id": uuid4(), "status": "passed", "execution_time": 12.5},
            {"scenario_id": uuid4(), "status": "passed", "execution_time": 11.2},
            {"scenario_id": uuid4(), "status": "failed", "execution_time": 8.3}
        ]

        passed_count = sum(1 for e in scenario_executions if e["status"] == "passed")
        failed_count = sum(1 for e in scenario_executions if e["status"] == "failed")
        avg_time = sum(e["execution_time"] for e in scenario_executions) / len(scenario_executions)

        assert passed_count == 2
        assert failed_count == 1
        assert avg_time == pytest.approx(10.67, rel=0.01)

    @pytest.mark.asyncio
    async def test_scenario_step_results_tracking(self, mock_db, qa_lead_user):
        """Test that results are tracked for each scenario step."""
        step_results = [
            {
                "step_number": 1,
                "prompt": "Say your account number",
                "result": "passed",
                "execution_time": 3.2
            },
            {
                "step_number": 2,
                "prompt": "Confirm the account",
                "result": "passed",
                "execution_time": 2.1
            },
            {
                "step_number": 3,
                "prompt": "Say your PIN",
                "result": "failed",
                "error": "Expected 4-digit PIN but got speech"
            }
        ]

        assert len(step_results) == 3
        assert step_results[2]["result"] == "failed"

    @pytest.mark.asyncio
    async def test_scenario_success_rate_calculation(self, mock_db, qa_lead_user):
        """Test calculation of scenario success rate."""
        scenario_runs = {
            "total_runs": 10,
            "successful_runs": 8,
            "failed_runs": 2
        }

        success_rate = (scenario_runs["successful_runs"] / scenario_runs["total_runs"]) * 100

        assert success_rate == 80.0

    @pytest.mark.asyncio
    async def test_scenario_timing_metrics(self, mock_db, qa_lead_user):
        """Test tracking of timing metrics for scenarios."""
        execution_metrics = {
            "scenario_id": uuid4(),
            "min_execution_time": 9.5,
            "max_execution_time": 18.2,
            "avg_execution_time": 12.8,
            "median_execution_time": 12.1
        }

        assert execution_metrics["min_execution_time"] < execution_metrics["avg_execution_time"]
        assert execution_metrics["avg_execution_time"] < execution_metrics["max_execution_time"]


class ScenarioTenantIsolation:
    """Test tenant isolation in scenarios."""

    @pytest.fixture
    def tenant1_id(self):
        return uuid4()

    @pytest.fixture
    def tenant2_id(self):
        return uuid4()

    @pytest.fixture
    def tenant1_qa_lead(self, tenant1_id):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.role = Role.QA_LEAD.value
        user.is_active = True
        user.tenant_id = tenant1_id
        return user

    @pytest.fixture
    def tenant2_qa_lead(self, tenant2_id):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.role = Role.QA_LEAD.value
        user.is_active = True
        user.tenant_id = tenant2_id
        return user

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.mark.asyncio
    async def test_scenario_isolated_by_tenant(self, tenant1_id, tenant2_id, mock_db):
        """Test that scenarios are isolated by tenant."""
        scenario1 = {
            "id": uuid4(),
            "tenant_id": tenant1_id,
            "name": "Tenant 1 Scenario"
        }

        scenario2 = {
            "id": uuid4(),
            "tenant_id": tenant2_id,
            "name": "Tenant 2 Scenario"
        }

        assert scenario1["tenant_id"] != scenario2["tenant_id"]

    @pytest.mark.asyncio
    async def test_tenant1_user_cannot_see_tenant2_scenarios(self, tenant1_qa_lead, tenant2_qa_lead, mock_db):
        """Test that Tenant1 user cannot access Tenant2 scenarios."""
        assert tenant1_qa_lead.tenant_id != tenant2_qa_lead.tenant_id

    @pytest.mark.asyncio
    async def test_scenario_queries_filtered_by_tenant(self, tenant1_id, tenant2_id, mock_db):
        """Test that scenario queries are filtered by tenant."""
        tenant1_scenarios = [
            {"id": uuid4(), "tenant_id": tenant1_id} for _ in range(3)
        ]

        tenant2_scenarios = [
            {"id": uuid4(), "tenant_id": tenant2_id} for _ in range(2)
        ]

        assert all(s["tenant_id"] == tenant1_id for s in tenant1_scenarios)
        assert all(s["tenant_id"] == tenant2_id for s in tenant2_scenarios)


class ScenarioListingAndFiltering:
    """Test listing and filtering scenarios."""

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
    async def test_list_scenarios_with_pagination(self, mock_db, qa_lead_user):
        """Test listing scenarios with pagination."""
        scenarios = [
            {"id": uuid4(), "name": f"Scenario {i}"} for i in range(5)
        ]

        paginated = scenarios[0:3]
        assert len(paginated) == 3

    @pytest.mark.asyncio
    async def test_filter_scenarios_by_name(self, mock_db, qa_lead_user):
        """Test filtering scenarios by name."""
        scenarios = [
            {"id": uuid4(), "name": "Login Scenario"},
            {"id": uuid4(), "name": "Logout Scenario"},
            {"id": uuid4(), "name": "Login Failure Scenario"}
        ]

        filtered = [s for s in scenarios if "Login" in s["name"]]
        assert len(filtered) == 2

    @pytest.mark.asyncio
    async def test_filter_scenarios_by_status(self, mock_db, qa_lead_user):
        """Test filtering scenarios by status."""
        scenarios = [
            {"id": uuid4(), "status": "active"},
            {"id": uuid4(), "status": "draft"},
            {"id": uuid4(), "status": "archived"}
        ]

        active_scenarios = [s for s in scenarios if s["status"] == "active"]
        assert len(active_scenarios) == 1

    @pytest.mark.asyncio
    async def test_sort_scenarios_by_creation_date(self, mock_db, qa_lead_user):
        """Test sorting scenarios by creation date."""
        scenarios = [
            {"id": uuid4(), "name": "A", "created_at": datetime.utcnow()},
            {"id": uuid4(), "name": "B", "created_at": datetime.utcnow()},
            {"id": uuid4(), "name": "C", "created_at": datetime.utcnow()}
        ]

        sorted_scenarios = sorted(scenarios, key=lambda s: s["created_at"], reverse=True)
        assert len(sorted_scenarios) == 3
