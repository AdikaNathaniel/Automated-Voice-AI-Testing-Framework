"""
Test suite for Fairness Analysis Service.

Components:
- Accuracy by demographic group
- Error rate disparity analysis
- Fairness metric calculation (equalized odds, etc.)
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestFairnessAnalysisServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'fairness_analysis_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'fairness_analysis_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class FairnessAnalysisService' in service_file_content


class TestDemographicAccuracy:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'fairness_analysis_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_group_accuracy_method(self, service_file_content):
        assert 'def calculate_group_accuracy(' in service_file_content

    def test_has_get_demographic_groups_method(self, service_file_content):
        assert 'def get_demographic_groups(' in service_file_content


class TestErrorRateDisparity:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'fairness_analysis_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_analyze_error_disparity_method(self, service_file_content):
        assert 'def analyze_error_disparity(' in service_file_content

    def test_has_get_disparity_ratio_method(self, service_file_content):
        assert 'def get_disparity_ratio(' in service_file_content


class TestFairnessMetrics:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'fairness_analysis_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_equalized_odds_method(self, service_file_content):
        assert 'def calculate_equalized_odds(' in service_file_content

    def test_has_calculate_demographic_parity_method(self, service_file_content):
        assert 'def calculate_demographic_parity(' in service_file_content

    def test_has_get_fairness_report_method(self, service_file_content):
        assert 'def get_fairness_report(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'fairness_analysis_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_fairness_config_method(self, service_file_content):
        assert 'def get_fairness_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'fairness_analysis_service.py'
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
            '..', 'backend', 'services', 'fairness_analysis_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class FairnessAnalysisService' in service_file_content:
            idx = service_file_content.find('class FairnessAnalysisService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
