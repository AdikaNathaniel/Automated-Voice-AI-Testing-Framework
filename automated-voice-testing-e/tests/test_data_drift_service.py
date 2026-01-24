"""
Test suite for Data Drift Service.

Components:
- Input distribution monitoring
- Feature drift detection
- Concept drift identification
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestDataDriftServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'data_drift_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'data_drift_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class DataDriftService' in service_file_content


class TestInputDistributionMonitoring:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'data_drift_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_monitor_input_distribution_method(self, service_file_content):
        assert 'def monitor_input_distribution(' in service_file_content

    def test_has_get_distribution_stats_method(self, service_file_content):
        assert 'def get_distribution_stats(' in service_file_content


class TestFeatureDriftDetection:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'data_drift_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_detect_feature_drift_method(self, service_file_content):
        assert 'def detect_feature_drift(' in service_file_content

    def test_has_get_feature_importance_method(self, service_file_content):
        assert 'def get_feature_importance(' in service_file_content


class TestConceptDriftIdentification:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'data_drift_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_identify_concept_drift_method(self, service_file_content):
        assert 'def identify_concept_drift(' in service_file_content

    def test_has_get_concept_drift_indicators_method(self, service_file_content):
        assert 'def get_concept_drift_indicators(' in service_file_content


class TestDriftAnalysis:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'data_drift_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_analyze_drift_method(self, service_file_content):
        assert 'def analyze_drift(' in service_file_content

    def test_has_get_drift_summary_method(self, service_file_content):
        assert 'def get_drift_summary(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'data_drift_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_data_drift_config_method(self, service_file_content):
        assert 'def get_data_drift_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'data_drift_service.py'
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
            '..', 'backend', 'services', 'data_drift_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class DataDriftService' in service_file_content:
            idx = service_file_content.find('class DataDriftService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
