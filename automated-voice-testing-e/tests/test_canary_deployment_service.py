"""
Test suite for Canary Deployment Service.

Components:
- Percentage traffic routing
- Canary metrics comparison
- Automatic rollback triggers
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestCanaryDeploymentServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'canary_deployment_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'canary_deployment_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class CanaryDeploymentService' in service_file_content


class TestPercentageTrafficRouting:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'canary_deployment_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_set_traffic_percentage_method(self, service_file_content):
        assert 'def set_traffic_percentage(' in service_file_content

    def test_has_get_traffic_distribution_method(self, service_file_content):
        assert 'def get_traffic_distribution(' in service_file_content

    def test_has_gradual_rollout_method(self, service_file_content):
        assert 'def gradual_rollout(' in service_file_content


class TestCanaryMetricsComparison:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'canary_deployment_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_compare_metrics_method(self, service_file_content):
        assert 'def compare_metrics(' in service_file_content

    def test_has_get_canary_metrics_method(self, service_file_content):
        assert 'def get_canary_metrics(' in service_file_content

    def test_has_analyze_performance_method(self, service_file_content):
        assert 'def analyze_performance(' in service_file_content


class TestAutomaticRollbackTriggers:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'canary_deployment_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_set_rollback_triggers_method(self, service_file_content):
        assert 'def set_rollback_triggers(' in service_file_content

    def test_has_check_triggers_method(self, service_file_content):
        assert 'def check_triggers(' in service_file_content

    def test_has_auto_rollback_method(self, service_file_content):
        assert 'def auto_rollback(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'canary_deployment_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_canary_config_method(self, service_file_content):
        assert 'def get_canary_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'canary_deployment_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_imports_typing_modules(self, service_file_content):
        assert 'from typing import' in service_file_content

    def test_uses_dict_type_hint(self, service_file_content):
        assert 'Dict[' in service_file_content

    def test_uses_list_type_hint(self, service_file_content):
        assert 'List[' in service_file_content


class TestDocstrings:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'canary_deployment_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class CanaryDeploymentService' in service_file_content:
            idx = service_file_content.find('class CanaryDeploymentService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
