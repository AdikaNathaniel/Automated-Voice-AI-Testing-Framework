"""
Test suite for Error Priority Service.

Components:
- Impact-based prioritization
- User-facing severity scoring
- Frequency-weighted ranking
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestErrorPriorityServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'error_priority_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'error_priority_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class ErrorPriorityService' in service_file_content


class TestImpactPrioritization:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'error_priority_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_impact_score_method(self, service_file_content):
        assert 'def calculate_impact_score(' in service_file_content

    def test_has_get_impact_factors_method(self, service_file_content):
        assert 'def get_impact_factors(' in service_file_content


class TestSeverityScoring:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'error_priority_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_severity_method(self, service_file_content):
        assert 'def calculate_severity(' in service_file_content

    def test_has_get_severity_levels_method(self, service_file_content):
        assert 'def get_severity_levels(' in service_file_content


class TestFrequencyRanking:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'error_priority_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_frequency_weight_method(self, service_file_content):
        assert 'def calculate_frequency_weight(' in service_file_content

    def test_has_get_frequency_distribution_method(self, service_file_content):
        assert 'def get_frequency_distribution(' in service_file_content


class TestPriorityCalculation:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'error_priority_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_prioritize_errors_method(self, service_file_content):
        assert 'def prioritize_errors(' in service_file_content

    def test_has_get_priority_queue_method(self, service_file_content):
        assert 'def get_priority_queue(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'error_priority_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_priority_config_method(self, service_file_content):
        assert 'def get_priority_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'error_priority_service.py'
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
            '..', 'backend', 'services', 'error_priority_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class ErrorPriorityService' in service_file_content:
            idx = service_file_content.find('class ErrorPriorityService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
