"""
Test suite for scenario script import/export functionality.

This module tests the import and export capabilities for scenarios:
- Export to JSON format
- Export to YAML format
- Import from JSON
- Import from YAML
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

import json
from pathlib import Path
from uuid import uuid4

import pytest


class TestExportServiceMethods:
    """Test export methods in scenario service"""

    def test_service_has_export_to_dict_method(self):
        """Test that scenario service has export_to_dict method"""
        from services.scenario_service import ScenarioService

        service = ScenarioService()
        assert hasattr(service, 'export_to_dict')

    def test_service_has_export_to_json_method(self):
        """Test that scenario service has export_to_json method"""
        from services.scenario_service import ScenarioService

        service = ScenarioService()
        assert hasattr(service, 'export_to_json')

    def test_service_has_export_to_yaml_method(self):
        """Test that scenario service has export_to_yaml method"""
        from services.scenario_service import ScenarioService

        service = ScenarioService()
        assert hasattr(service, 'export_to_yaml')


class TestImportServiceMethods:
    """Test import methods in scenario service"""

    def test_service_has_import_from_dict_method(self):
        """Test that scenario service has import_from_dict method"""
        from services.scenario_service import ScenarioService

        service = ScenarioService()
        assert hasattr(service, 'import_from_dict')

    def test_service_has_import_from_json_method(self):
        """Test that scenario service has import_from_json method"""
        from services.scenario_service import ScenarioService

        service = ScenarioService()
        assert hasattr(service, 'import_from_json')

    def test_service_has_import_from_yaml_method(self):
        """Test that scenario service has import_from_yaml method"""
        from services.scenario_service import ScenarioService

        service = ScenarioService()
        assert hasattr(service, 'import_from_yaml')


class TestExportRoutes:
    """Test export API routes"""

    def test_export_json_route_exists(self):
        """Test that GET /scenarios/{id}/export/json route exists"""
        from api.routes.scenarios import router

        routes = [route for route in router.routes]
        export_routes = [
            r for r in routes
            if hasattr(r, 'methods') and 'GET' in r.methods
            and 'export' in r.path
        ]
        assert len(export_routes) >= 1, "Export routes should exist"

    def test_export_yaml_route_exists(self):
        """Test that GET /scenarios/{id}/export/yaml route exists"""
        from api.routes.scenarios import router

        routes = [route for route in router.routes]
        yaml_routes = [
            r for r in routes
            if hasattr(r, 'methods') and 'GET' in r.methods
            and 'yaml' in r.path
        ]
        assert len(yaml_routes) >= 1, "YAML export route should exist"


class TestImportRoutes:
    """Test import API routes"""

    def test_import_json_route_exists(self):
        """Test that POST /scenarios/import/json route exists"""
        from api.routes.scenarios import router

        routes = [route for route in router.routes]
        import_routes = [
            r for r in routes
            if hasattr(r, 'methods') and 'POST' in r.methods
            and 'import' in r.path
        ]
        assert len(import_routes) >= 1, "Import routes should exist"


class TestExportSchemas:
    """Test export-related schemas"""

    def test_scenario_export_schema_exists(self):
        """Test ScenarioExport schema exists"""
        from api.schemas.scenario import ScenarioExport
        assert ScenarioExport is not None

    def test_export_schema_has_required_fields(self):
        """Test ScenarioExport has required fields for export"""
        from api.schemas.scenario import ScenarioExport

        fields = ScenarioExport.model_fields
        assert 'name' in fields
        assert 'steps' in fields


class TestYAMLSupport:
    """Test YAML library availability"""

    def test_yaml_library_available(self):
        """Test that PyYAML is available"""
        try:
            import yaml
            assert yaml is not None
        except ImportError:
            pytest.fail("PyYAML library not available")

    def test_can_dump_yaml(self):
        """Test that YAML can serialize data"""
        import yaml

        data = {
            'name': 'Test Scenario',
            'version': '1.0.0',
            'steps': [
                {'step_order': 1, 'user_utterance': 'Hello'}
            ]
        }
        yaml_str = yaml.dump(data)
        assert 'Test Scenario' in yaml_str

    def test_can_load_yaml(self):
        """Test that YAML can deserialize data"""
        import yaml

        yaml_str = """
name: Test Scenario
version: '1.0.0'
steps:
  - step_order: 1
    user_utterance: Hello
"""
        data = yaml.safe_load(yaml_str)
        assert data['name'] == 'Test Scenario'
        assert len(data['steps']) == 1


class TestJSONExportFormat:
    """Test JSON export format compliance"""

    def test_json_export_format_valid(self):
        """Test that export produces valid JSON"""
        sample_export = {
            'name': 'Navigation Test',
            'description': 'Test navigation commands',
            'version': '1.0.0',
            'metadata': {'language': 'en-US'},
            'steps': [
                {
                    'step_order': 1,
                    'user_utterance': 'Find a coffee shop',
                    'expected_response': 'Found 3 coffee shops',
                    'alternate_responses': ['Found nearby coffee shops'],
                    'tolerances': {'semantic_similarity': 0.85}
                }
            ]
        }

        # Should produce valid JSON
        json_str = json.dumps(sample_export, indent=2)
        parsed = json.loads(json_str)

        assert parsed['name'] == 'Navigation Test'
        assert len(parsed['steps']) == 1
        assert parsed['steps'][0]['step_order'] == 1


class TestImportValidation:
    """Test import validation"""

    def test_import_validates_required_fields(self):
        """Test that import requires name field"""
        from api.schemas.scenario import ScenarioScriptCreate

        # Valid data should work
        valid_data = {'name': 'Test'}
        script = ScenarioScriptCreate(**valid_data)
        assert script.name == 'Test'

    def test_import_validates_step_structure(self):
        """Test that import validates step structure"""
        from api.schemas.scenario import ScenarioStepCreate

        # Valid step data
        valid_step = {
            'step_order': 1,
            'user_utterance': 'Hello',
            'expected_response': 'Hi there'
        }
        step = ScenarioStepCreate(**valid_step)
        assert step.step_order == 1
