"""
Test suite for Edge Case Manager.

This manager consolidates the 3 edge case services into
a coherent module with unified interface.

Components:
- Edge case persistence (CRUD)
- Edge case detection (auto-detection from failures)
- Edge case testing (boundary values, invalid inputs)
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestEdgeCaseManagerExists:
    """Test that edge case manager exists"""

    def test_service_file_exists(self):
        """Test that edge_case_manager.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'edge_case_manager.py'
        )
        assert os.path.exists(service_file), (
            "edge_case_manager.py should exist"
        )

    def test_manager_class_exists(self):
        """Test that EdgeCaseManager class exists"""
        from services.edge_case_manager import EdgeCaseManager
        assert EdgeCaseManager is not None


class TestEdgeCaseManagerBasic:
    """Test basic manager functionality"""

    @pytest.fixture
    def manager(self):
        """Create manager instance"""
        from services.edge_case_manager import EdgeCaseManager
        return EdgeCaseManager()

    def test_manager_initialization(self, manager):
        """Test manager initializes correctly"""
        assert manager is not None

    def test_has_testing_component(self, manager):
        """Test manager has testing component"""
        assert hasattr(manager, 'testing')

    def test_has_detection_component(self, manager):
        """Test manager has detection component"""
        assert hasattr(manager, 'detection')


class TestBoundaryValueTesting:
    """Test boundary value testing functionality"""

    @pytest.fixture
    def manager(self):
        """Create manager instance"""
        from services.edge_case_manager import EdgeCaseManager
        return EdgeCaseManager()

    def test_test_boundary_values_method(self, manager):
        """Test test_boundary_values method exists"""
        assert hasattr(manager, 'test_boundary_values')
        assert callable(getattr(manager, 'test_boundary_values'))

    def test_boundary_values_returns_dict(self, manager):
        """Test boundary value testing returns dictionary"""
        result = manager.test_boundary_values('volume', 0, 100)
        assert isinstance(result, dict)

    def test_boundary_values_has_test_id(self, manager):
        """Test result has test_id"""
        result = manager.test_boundary_values('volume', 0, 100)
        assert 'test_id' in result

    def test_boundary_values_has_parameter(self, manager):
        """Test result has parameter"""
        result = manager.test_boundary_values('volume', 0, 100)
        assert result['parameter'] == 'volume'

    def test_boundary_values_has_test_cases(self, manager):
        """Test result has test cases"""
        result = manager.test_boundary_values('volume', 0, 100)
        assert 'test_cases' in result
        assert len(result['test_cases']) >= 5

    def test_generate_boundary_cases(self, manager):
        """Test generate_boundary_cases method"""
        assert hasattr(manager, 'generate_boundary_cases')
        cases = manager.generate_boundary_cases('speed', 0, 200)
        assert isinstance(cases, list)


class TestInvalidInputTesting:
    """Test invalid input handling functionality"""

    @pytest.fixture
    def manager(self):
        """Create manager instance"""
        from services.edge_case_manager import EdgeCaseManager
        return EdgeCaseManager()

    def test_test_invalid_inputs_method(self, manager):
        """Test test_invalid_inputs method exists"""
        assert hasattr(manager, 'test_invalid_inputs')
        assert callable(getattr(manager, 'test_invalid_inputs'))

    def test_invalid_inputs_returns_dict(self, manager):
        """Test invalid input testing returns dictionary"""
        result = manager.test_invalid_inputs('temperature')
        assert isinstance(result, dict)

    def test_invalid_inputs_has_parameter(self, manager):
        """Test result has parameter"""
        result = manager.test_invalid_inputs('temperature')
        assert result['parameter'] == 'temperature'

    def test_get_invalid_input_types(self, manager):
        """Test get_invalid_input_types method"""
        assert hasattr(manager, 'get_invalid_input_types')
        types = manager.get_invalid_input_types()
        assert isinstance(types, list)
        assert 'null' in types
        assert 'empty_string' in types


class TestTimeoutTesting:
    """Test timeout scenario functionality"""

    @pytest.fixture
    def manager(self):
        """Create manager instance"""
        from services.edge_case_manager import EdgeCaseManager
        return EdgeCaseManager()

    def test_test_timeout_scenarios_method(self, manager):
        """Test test_timeout_scenarios method exists"""
        assert hasattr(manager, 'test_timeout_scenarios')
        assert callable(getattr(manager, 'test_timeout_scenarios'))

    def test_timeout_scenarios_returns_dict(self, manager):
        """Test timeout testing returns dictionary"""
        result = manager.test_timeout_scenarios('api_call', timeout_ms=5000)
        assert isinstance(result, dict)

    def test_timeout_scenarios_has_operation(self, manager):
        """Test result has operation"""
        result = manager.test_timeout_scenarios('api_call', timeout_ms=5000)
        assert result['operation'] == 'api_call'


class TestEdgeCaseDetection:
    """Test edge case detection functionality"""

    @pytest.fixture
    def manager(self):
        """Create manager instance"""
        from services.edge_case_manager import EdgeCaseManager
        return EdgeCaseManager()

    def test_detect_from_failures_method(self, manager):
        """Test detect_from_failures method exists"""
        assert hasattr(manager, 'detect_from_failures')
        assert callable(getattr(manager, 'detect_from_failures'))

    def test_detect_timeout_pattern(self, manager):
        """Test detecting timeout patterns"""
        failures = [
            {'failure_reason': 'Operation timed out', 'error_type': 'TimeoutError'}
        ]
        result = manager.detect_from_failures(failures)
        assert isinstance(result, list)

    def test_detect_empty_failures(self, manager):
        """Test detecting from empty failures list"""
        result = manager.detect_from_failures([])
        assert result == []

    def test_classify_failure_method(self, manager):
        """Test classify_failure method"""
        assert hasattr(manager, 'classify_failure')


class TestEdgeCaseResults:
    """Test edge case result management"""

    @pytest.fixture
    def manager(self):
        """Create manager instance"""
        from services.edge_case_manager import EdgeCaseManager
        return EdgeCaseManager()

    def test_get_test_results_method(self, manager):
        """Test get_test_results method exists"""
        assert hasattr(manager, 'get_test_results')

    def test_get_test_results_returns_list(self, manager):
        """Test get_test_results returns list"""
        results = manager.get_test_results()
        assert isinstance(results, list)

    def test_clear_test_results_method(self, manager):
        """Test clear_test_results method exists"""
        assert hasattr(manager, 'clear_test_results')

    def test_clear_removes_results(self, manager):
        """Test clearing removes results"""
        manager.test_boundary_values('volume', 0, 100)
        manager.clear_test_results()
        results = manager.get_test_results()
        assert len(results) == 0


class TestEdgeCaseConfig:
    """Test edge case configuration"""

    @pytest.fixture
    def manager(self):
        """Create manager instance"""
        from services.edge_case_manager import EdgeCaseManager
        return EdgeCaseManager()

    def test_get_edge_case_config_method(self, manager):
        """Test get_edge_case_config method exists"""
        assert hasattr(manager, 'get_edge_case_config')

    def test_config_returns_dict(self, manager):
        """Test config returns dictionary"""
        config = manager.get_edge_case_config()
        assert isinstance(config, dict)

    def test_config_has_boundary_settings(self, manager):
        """Test config has boundary settings"""
        config = manager.get_edge_case_config()
        assert 'boundary_test_points' in config

    def test_config_has_timeout_settings(self, manager):
        """Test config has timeout settings"""
        config = manager.get_edge_case_config()
        assert 'timeout_multipliers' in config


class TestSeverityDerivation:
    """Test severity derivation from signals"""

    @pytest.fixture
    def manager(self):
        """Create manager instance"""
        from services.edge_case_manager import EdgeCaseManager
        return EdgeCaseManager()

    def test_derive_severity_method(self, manager):
        """Test derive_severity method exists"""
        assert hasattr(manager, 'derive_severity')

    def test_critical_severity(self, manager):
        """Test critical severity derivation"""
        severity = manager.derive_severity({'impact_score': 0.9})
        assert severity == 'critical'

    def test_high_severity(self, manager):
        """Test high severity derivation"""
        severity = manager.derive_severity({'impact_score': 0.7})
        assert severity == 'high'

    def test_medium_severity(self, manager):
        """Test medium severity derivation"""
        severity = manager.derive_severity({'impact_score': 0.5})
        assert severity == 'medium'

    def test_low_severity(self, manager):
        """Test low severity derivation"""
        severity = manager.derive_severity({'impact_score': 0.2})
        assert severity == 'low'


class TestTypeHints:
    """Test type hints for edge case manager"""

    @pytest.fixture
    def service_file_content(self):
        """Read the edge case manager file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'edge_case_manager.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_imports_typing_modules(self, service_file_content):
        """Test typing modules are imported"""
        assert 'from typing import' in service_file_content

    def test_uses_dict_type_hint(self, service_file_content):
        """Test Dict type hint is used"""
        assert 'Dict[' in service_file_content


class TestDocstrings:
    """Test comprehensive documentation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the edge case manager file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'edge_case_manager.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        """Test module has docstring"""
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        """Test class has docstring"""
        if 'class EdgeCaseManager' in service_file_content:
            idx = service_file_content.find('class EdgeCaseManager')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
