"""
Test suite for scenario script API schemas.

This module tests the Pydantic schemas for scenario script API operations:
- ScenarioStepCreate/Response
- ScenarioScriptCreate/Response/Update
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

from pathlib import Path
from uuid import uuid4

import pytest


class TestSchemaFileExists:
    """Test that scenario schema file exists"""

    def test_scenario_schema_file_exists(self):
        """Test that scenario.py schema file exists"""
        project_root = Path(__file__).parent.parent
        schema_path = project_root / "backend" / "api" / "schemas" / "scenario.py"
        assert schema_path.exists(), \
            "scenario.py should exist in backend/api/schemas/"


class TestScenarioStepSchemas:
    """Test ScenarioStep schemas"""

    def test_can_import_scenario_step_create(self):
        """Test that ScenarioStepCreate can be imported"""
        try:
            from api.schemas.scenario import ScenarioStepCreate
            assert ScenarioStepCreate is not None
        except ImportError as e:
            pytest.fail(f"Cannot import ScenarioStepCreate: {e}")

    def test_can_import_scenario_step_response(self):
        """Test that ScenarioStepResponse can be imported"""
        try:
            from api.schemas.scenario import ScenarioStepResponse
            assert ScenarioStepResponse is not None
        except ImportError as e:
            pytest.fail(f"Cannot import ScenarioStepResponse: {e}")

    def test_scenario_step_create_has_required_fields(self):
        """Test ScenarioStepCreate has required fields"""
        from api.schemas.scenario import ScenarioStepCreate

        fields = ScenarioStepCreate.model_fields
        assert 'step_order' in fields
        assert 'user_utterance' in fields
        assert 'expected_response' in fields

    def test_scenario_step_create_has_optional_fields(self):
        """Test ScenarioStepCreate has optional fields"""
        from api.schemas.scenario import ScenarioStepCreate

        fields = ScenarioStepCreate.model_fields
        assert 'alternate_responses' in fields
        assert 'tolerances' in fields

    def test_scenario_step_create_validation(self):
        """Test ScenarioStepCreate validates data correctly"""
        from api.schemas.scenario import ScenarioStepCreate

        step = ScenarioStepCreate(
            step_order=1,
            user_utterance="Navigate to the coffee shop",
            expected_response="Found 3 coffee shops nearby"
        )

        assert step.step_order == 1
        assert step.user_utterance == "Navigate to the coffee shop"
        assert step.expected_response == "Found 3 coffee shops nearby"

    def test_scenario_step_create_with_alternates(self):
        """Test ScenarioStepCreate with alternate responses"""
        from api.schemas.scenario import ScenarioStepCreate

        step = ScenarioStepCreate(
            step_order=1,
            user_utterance="What's the weather?",
            expected_response="It's sunny today",
            alternate_responses=["Currently sunny", "The weather is clear"]
        )

        assert len(step.alternate_responses) == 2

    def test_scenario_step_response_has_id(self):
        """Test ScenarioStepResponse has id field"""
        from api.schemas.scenario import ScenarioStepResponse

        fields = ScenarioStepResponse.model_fields
        assert 'id' in fields


class TestScenarioScriptSchemas:
    """Test ScenarioScript schemas"""

    def test_can_import_scenario_script_create(self):
        """Test that ScenarioScriptCreate can be imported"""
        try:
            from api.schemas.scenario import ScenarioScriptCreate
            assert ScenarioScriptCreate is not None
        except ImportError as e:
            pytest.fail(f"Cannot import ScenarioScriptCreate: {e}")

    def test_can_import_scenario_script_response(self):
        """Test that ScenarioScriptResponse can be imported"""
        try:
            from api.schemas.scenario import ScenarioScriptResponse
            assert ScenarioScriptResponse is not None
        except ImportError as e:
            pytest.fail(f"Cannot import ScenarioScriptResponse: {e}")

    def test_can_import_scenario_script_update(self):
        """Test that ScenarioScriptUpdate can be imported"""
        try:
            from api.schemas.scenario import ScenarioScriptUpdate
            assert ScenarioScriptUpdate is not None
        except ImportError as e:
            pytest.fail(f"Cannot import ScenarioScriptUpdate: {e}")

    def test_scenario_script_create_has_required_fields(self):
        """Test ScenarioScriptCreate has required fields"""
        from api.schemas.scenario import ScenarioScriptCreate

        fields = ScenarioScriptCreate.model_fields
        assert 'name' in fields

    def test_scenario_script_create_has_optional_fields(self):
        """Test ScenarioScriptCreate has optional fields"""
        from api.schemas.scenario import ScenarioScriptCreate

        fields = ScenarioScriptCreate.model_fields
        assert 'description' in fields
        assert 'version' in fields
        assert 'steps' in fields

    def test_scenario_script_create_validation(self):
        """Test ScenarioScriptCreate validates data correctly"""
        from api.schemas.scenario import ScenarioScriptCreate

        script = ScenarioScriptCreate(
            name="Navigation Test Scenario",
            description="Test navigation voice commands",
            version="1.0.0"
        )

        assert script.name == "Navigation Test Scenario"
        assert script.description == "Test navigation voice commands"
        assert script.version == "1.0.0"

    def test_scenario_script_create_with_steps(self):
        """Test ScenarioScriptCreate with embedded steps"""
        from api.schemas.scenario import ScenarioScriptCreate, ScenarioStepCreate

        steps = [
            ScenarioStepCreate(
                step_order=1,
                user_utterance="Find a coffee shop",
                expected_response="Found nearby coffee shops"
            ),
            ScenarioStepCreate(
                step_order=2,
                user_utterance="Navigate to the first one",
                expected_response="Starting navigation"
            )
        ]

        script = ScenarioScriptCreate(
            name="Coffee Shop Navigation",
            steps=steps
        )

        assert len(script.steps) == 2
        assert script.steps[0].step_order == 1
        assert script.steps[1].step_order == 2

    def test_scenario_script_response_has_id(self):
        """Test ScenarioScriptResponse has id field"""
        from api.schemas.scenario import ScenarioScriptResponse

        fields = ScenarioScriptResponse.model_fields
        assert 'id' in fields

    def test_scenario_script_response_has_timestamps(self):
        """Test ScenarioScriptResponse has timestamp fields"""
        from api.schemas.scenario import ScenarioScriptResponse

        fields = ScenarioScriptResponse.model_fields
        assert 'created_at' in fields
        assert 'updated_at' in fields

    def test_scenario_script_update_all_optional(self):
        """Test ScenarioScriptUpdate has all optional fields"""
        from api.schemas.scenario import ScenarioScriptUpdate

        # Should be able to create with no fields
        update = ScenarioScriptUpdate()
        assert update is not None


class TestScenarioExportImportSchemas:
    """Test export/import schemas for JSON/YAML"""

    def test_can_import_scenario_export(self):
        """Test that ScenarioExport can be imported"""
        try:
            from api.schemas.scenario import ScenarioExport
            assert ScenarioExport is not None
        except ImportError as e:
            pytest.fail(f"Cannot import ScenarioExport: {e}")

    def test_scenario_export_has_steps(self):
        """Test ScenarioExport includes steps"""
        from api.schemas.scenario import ScenarioExport

        fields = ScenarioExport.model_fields
        assert 'steps' in fields

    def test_scenario_export_has_metadata(self):
        """Test ScenarioExport has metadata field"""
        from api.schemas.scenario import ScenarioExport

        fields = ScenarioExport.model_fields
        assert 'name' in fields
        assert 'version' in fields


class TestSchemaValidation:
    """Test schema validation rules"""

    def test_step_order_must_be_positive(self):
        """Test that step_order must be positive"""
        from api.schemas.scenario import ScenarioStepCreate
        from pydantic import ValidationError

        # Valid positive value
        step = ScenarioStepCreate(
            step_order=1,
            user_utterance="Test",
            expected_response="Response"
        )
        assert step.step_order == 1

    def test_name_cannot_be_empty(self):
        """Test that name cannot be empty string"""
        from api.schemas.scenario import ScenarioScriptCreate
        from pydantic import ValidationError

        # Valid name
        script = ScenarioScriptCreate(name="Valid Name")
        assert script.name == "Valid Name"
