"""
Test suite for Regression Gating Service.

Components:
- Automatic regression detection in CI
- PR blocking on regression
- Configurable thresholds
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestRegressionGatingServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'regression_gating_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'regression_gating_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class RegressionGatingService' in service_file_content


class TestAutomaticRegressionDetection:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'regression_gating_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_detect_regressions_method(self, service_file_content):
        assert 'def detect_regressions(' in service_file_content

    def test_has_compare_baselines_method(self, service_file_content):
        assert 'def compare_baselines(' in service_file_content

    def test_has_analyze_metrics_method(self, service_file_content):
        assert 'def analyze_metrics(' in service_file_content


class TestPRBlocking:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'regression_gating_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_evaluate_pr_method(self, service_file_content):
        assert 'def evaluate_pr(' in service_file_content

    def test_has_block_pr_method(self, service_file_content):
        assert 'def block_pr(' in service_file_content

    def test_has_approve_pr_method(self, service_file_content):
        assert 'def approve_pr(' in service_file_content


class TestConfigurableThresholds:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'regression_gating_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_set_thresholds_method(self, service_file_content):
        assert 'def set_thresholds(' in service_file_content

    def test_has_get_thresholds_method(self, service_file_content):
        assert 'def get_thresholds(' in service_file_content

    def test_has_validate_against_thresholds_method(self, service_file_content):
        assert 'def validate_against_thresholds(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'regression_gating_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_gating_config_method(self, service_file_content):
        assert 'def get_gating_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'regression_gating_service.py'
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
            '..', 'backend', 'services', 'regression_gating_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class RegressionGatingService' in service_file_content:
            idx = service_file_content.find('class RegressionGatingService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
