"""
Test suite for scenario builder tooling.

This module tests the scenario builder system:
- Creating and managing scripted test scenarios
- Multi-step conversation trees with tolerances
- Import/export in JSON and YAML formats
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

from uuid import uuid4

import pytest


class TestScenarioBuilderService:
    """Test ScenarioBuilderService for scenario authoring"""

    def test_service_exists(self):
        """Test that ScenarioBuilderService can be imported"""
        from services.scenario_builder_service import ScenarioBuilderService
        assert ScenarioBuilderService is not None

    def test_has_create_scenario_method(self):
        """Test service has create_scenario method"""
        from services.scenario_builder_service import ScenarioBuilderService

        assert hasattr(ScenarioBuilderService, 'create_scenario')

    def test_has_add_step_method(self):
        """Test service has add_step method"""
        from services.scenario_builder_service import ScenarioBuilderService

        assert hasattr(ScenarioBuilderService, 'add_step')

    def test_has_export_scenario_method(self):
        """Test service has export_scenario method"""
        from services.scenario_builder_service import ScenarioBuilderService

        assert hasattr(ScenarioBuilderService, 'export_scenario')

    def test_has_import_scenario_method(self):
        """Test service has import_scenario method"""
        from services.scenario_builder_service import ScenarioBuilderService

        assert hasattr(ScenarioBuilderService, 'import_scenario')


class TestScenarioCreation:
    """Test scenario creation functionality"""

    def test_create_basic_scenario(self):
        """Test creating a basic scenario"""
        from services.scenario_builder_service import ScenarioBuilderService

        service = ScenarioBuilderService()
        scenario = service.create_scenario(
            name='Weather Query',
            description='Test weather queries'
        )

        assert scenario['name'] == 'Weather Query'
        assert 'id' in scenario
        assert 'steps' in scenario

    def test_create_scenario_with_metadata(self):
        """Test creating scenario with metadata"""
        from services.scenario_builder_service import ScenarioBuilderService

        service = ScenarioBuilderService()
        scenario = service.create_scenario(
            name='Navigation Test',
            description='Test navigation commands',
            metadata={'language': 'en-US', 'domain': 'automotive'}
        )

        assert scenario['metadata']['language'] == 'en-US'

    def test_create_scenario_with_version(self):
        """Test creating scenario with version"""
        from services.scenario_builder_service import ScenarioBuilderService

        service = ScenarioBuilderService()
        scenario = service.create_scenario(
            name='Test',
            version='1.0.0'
        )

        assert scenario['version'] == '1.0.0'


class TestStepManagement:
    """Test step management in scenarios"""

    def test_add_step_to_scenario(self):
        """Test adding a step to a scenario"""
        from services.scenario_builder_service import ScenarioBuilderService

        service = ScenarioBuilderService()
        scenario = service.create_scenario(name='Test')

        step = service.add_step(
            scenario,
            user_utterance='What is the weather?',
            expected_response='The weather is sunny'
        )

        assert step['user_utterance'] == 'What is the weather?'
        assert step['expected_response'] == 'The weather is sunny'
        assert len(scenario['steps']) == 1

    def test_add_step_with_alternates(self):
        """Test adding step with alternate responses"""
        from services.scenario_builder_service import ScenarioBuilderService

        service = ScenarioBuilderService()
        scenario = service.create_scenario(name='Test')

        step = service.add_step(
            scenario,
            user_utterance='What is the weather?',
            expected_response='The weather is sunny',
            alternate_responses=['It is sunny today', 'Sunny weather expected']
        )

        assert len(step['alternate_responses']) == 2

    def test_add_step_with_tolerances(self):
        """Test adding step with tolerance settings"""
        from services.scenario_builder_service import ScenarioBuilderService

        service = ScenarioBuilderService()
        scenario = service.create_scenario(name='Test')

        step = service.add_step(
            scenario,
            user_utterance='Navigate to work',
            expected_response='Starting navigation',
            tolerances={'semantic_similarity': 0.8, 'tone': 'helpful'}
        )

        assert step['tolerances']['semantic_similarity'] == 0.8

    def test_add_multiple_steps(self):
        """Test adding multiple steps preserves order"""
        from services.scenario_builder_service import ScenarioBuilderService

        service = ScenarioBuilderService()
        scenario = service.create_scenario(name='Multi-step')

        service.add_step(scenario, 'Step 1', 'Response 1')
        service.add_step(scenario, 'Step 2', 'Response 2')
        service.add_step(scenario, 'Step 3', 'Response 3')

        assert len(scenario['steps']) == 3
        assert scenario['steps'][0]['step_order'] == 1
        assert scenario['steps'][2]['step_order'] == 3


class TestConversationTrees:
    """Test multi-step conversation tree support"""

    def test_add_step_with_follow_up(self):
        """Test adding step with follow-up action"""
        from services.scenario_builder_service import ScenarioBuilderService

        service = ScenarioBuilderService()
        scenario = service.create_scenario(name='Confirmation Flow')

        step = service.add_step(
            scenario,
            user_utterance='Book the appointment',
            expected_response='Confirm booking?',
            follow_up_action='await_confirmation'
        )

        assert step['follow_up_action'] == 'await_confirmation'

    def test_create_branching_scenario(self):
        """Test creating scenario with branching paths"""
        from services.scenario_builder_service import ScenarioBuilderService

        service = ScenarioBuilderService()
        scenario = service.create_scenario(name='Branching')

        # Main path
        step1 = service.add_step(scenario, 'Find restaurant', 'Found 3 options')

        # Branch for first selection
        service.add_branch(
            scenario,
            parent_step=step1,
            condition='first one',
            user_utterance='The first one',
            expected_response='Selected restaurant A'
        )

        assert 'branches' in scenario or len(scenario['steps']) >= 2

    def test_has_add_branch_method(self):
        """Test service has add_branch method"""
        from services.scenario_builder_service import ScenarioBuilderService

        assert hasattr(ScenarioBuilderService, 'add_branch')


class TestJSONExport:
    """Test JSON export functionality"""

    def test_export_to_json(self):
        """Test exporting scenario to JSON"""
        from services.scenario_builder_service import ScenarioBuilderService

        service = ScenarioBuilderService()
        scenario = service.create_scenario(
            name='Export Test',
            description='Test export'
        )
        service.add_step(scenario, 'Hello', 'Hi there')

        json_str = service.export_scenario(scenario, format='json')

        assert isinstance(json_str, str)
        assert 'Export Test' in json_str

    def test_export_json_is_valid(self):
        """Test exported JSON is valid"""
        import json
        from services.scenario_builder_service import ScenarioBuilderService

        service = ScenarioBuilderService()
        scenario = service.create_scenario(name='Valid JSON')
        service.add_step(scenario, 'Test', 'Response')

        json_str = service.export_scenario(scenario, format='json')
        parsed = json.loads(json_str)

        assert parsed['name'] == 'Valid JSON'
        assert len(parsed['steps']) == 1


class TestYAMLExport:
    """Test YAML export functionality"""

    def test_export_to_yaml(self):
        """Test exporting scenario to YAML"""
        from services.scenario_builder_service import ScenarioBuilderService

        service = ScenarioBuilderService()
        scenario = service.create_scenario(name='YAML Test')
        service.add_step(scenario, 'Hello', 'World')

        yaml_str = service.export_scenario(scenario, format='yaml')

        assert isinstance(yaml_str, str)
        assert 'YAML Test' in yaml_str

    def test_export_yaml_is_valid(self):
        """Test exported YAML is valid"""
        import yaml
        from services.scenario_builder_service import ScenarioBuilderService

        service = ScenarioBuilderService()
        scenario = service.create_scenario(name='Valid YAML')
        service.add_step(scenario, 'Test', 'Response')

        yaml_str = service.export_scenario(scenario, format='yaml')
        parsed = yaml.safe_load(yaml_str)

        assert parsed['name'] == 'Valid YAML'


class TestJSONImport:
    """Test JSON import functionality"""

    def test_import_from_json(self):
        """Test importing scenario from JSON"""
        import json
        from services.scenario_builder_service import ScenarioBuilderService

        service = ScenarioBuilderService()
        json_data = json.dumps({
            'name': 'Imported Scenario',
            'description': 'From JSON',
            'steps': [
                {
                    'user_utterance': 'Hello',
                    'expected_response': 'Hi',
                    'step_order': 1
                }
            ]
        })

        scenario = service.import_scenario(json_data, format='json')

        assert scenario['name'] == 'Imported Scenario'
        assert len(scenario['steps']) == 1

    def test_import_validates_required_fields(self):
        """Test import validates required fields"""
        import json
        from services.scenario_builder_service import ScenarioBuilderService

        service = ScenarioBuilderService()
        json_data = json.dumps({
            'description': 'Missing name'
        })

        result = service.import_scenario(json_data, format='json')
        assert result.get('valid') is False or 'error' in result


class TestYAMLImport:
    """Test YAML import functionality"""

    def test_import_from_yaml(self):
        """Test importing scenario from YAML"""
        from services.scenario_builder_service import ScenarioBuilderService

        service = ScenarioBuilderService()
        yaml_data = """
name: YAML Import
description: From YAML file
steps:
  - user_utterance: What time is it?
    expected_response: It is 3 PM
    step_order: 1
"""

        scenario = service.import_scenario(yaml_data, format='yaml')

        assert scenario['name'] == 'YAML Import'
        assert len(scenario['steps']) == 1


class TestScenarioValidation:
    """Test scenario validation"""

    def test_validate_scenario_structure(self):
        """Test validating scenario structure"""
        from services.scenario_builder_service import ScenarioBuilderService

        service = ScenarioBuilderService()
        scenario = service.create_scenario(name='Valid')
        service.add_step(scenario, 'Test', 'Response')

        result = service.validate_scenario(scenario)
        assert result['valid'] is True

    def test_validate_empty_steps_fails(self):
        """Test validation fails for empty steps"""
        from services.scenario_builder_service import ScenarioBuilderService

        service = ScenarioBuilderService()
        scenario = service.create_scenario(name='No Steps')

        result = service.validate_scenario(scenario)
        assert result['valid'] is False

    def test_has_validate_scenario_method(self):
        """Test service has validate_scenario method"""
        from services.scenario_builder_service import ScenarioBuilderService

        assert hasattr(ScenarioBuilderService, 'validate_scenario')


class TestScenarioCloning:
    """Test scenario cloning for templates"""

    def test_clone_scenario(self):
        """Test cloning a scenario"""
        from services.scenario_builder_service import ScenarioBuilderService

        service = ScenarioBuilderService()
        original = service.create_scenario(name='Original')
        service.add_step(original, 'Step 1', 'Response 1')

        clone = service.clone_scenario(original, new_name='Clone')

        assert clone['name'] == 'Clone'
        assert clone['id'] != original['id']
        assert len(clone['steps']) == 1

    def test_has_clone_scenario_method(self):
        """Test service has clone_scenario method"""
        from services.scenario_builder_service import ScenarioBuilderService

        assert hasattr(ScenarioBuilderService, 'clone_scenario')


class TestVersionControl:
    """Test version control support"""

    def test_scenario_has_version(self):
        """Test scenario includes version"""
        from services.scenario_builder_service import ScenarioBuilderService

        service = ScenarioBuilderService()
        scenario = service.create_scenario(
            name='Versioned',
            version='1.0.0'
        )

        assert scenario['version'] == '1.0.0'

    def test_bump_version(self):
        """Test bumping scenario version"""
        from services.scenario_builder_service import ScenarioBuilderService

        service = ScenarioBuilderService()
        scenario = service.create_scenario(
            name='Test',
            version='1.0.0'
        )

        service.bump_version(scenario, 'minor')
        assert scenario['version'] == '1.1.0'

    def test_has_bump_version_method(self):
        """Test service has bump_version method"""
        from services.scenario_builder_service import ScenarioBuilderService

        assert hasattr(ScenarioBuilderService, 'bump_version')


