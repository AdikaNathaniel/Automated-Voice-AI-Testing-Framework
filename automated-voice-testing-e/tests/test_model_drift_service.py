"""
Test suite for Model Drift Service.

Components:
- Statistical drift detection (PSI, KL divergence)
- Accuracy trend monitoring
- Confidence distribution shift
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestModelDriftServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'model_drift_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'model_drift_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class ModelDriftService' in service_file_content


class TestStatisticalDriftDetection:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'model_drift_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_psi_method(self, service_file_content):
        assert 'def calculate_psi(' in service_file_content

    def test_has_calculate_kl_divergence_method(self, service_file_content):
        assert 'def calculate_kl_divergence(' in service_file_content

    def test_has_detect_statistical_drift_method(self, service_file_content):
        assert 'def detect_statistical_drift(' in service_file_content


class TestAccuracyTrendMonitoring:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'model_drift_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_track_accuracy_trend_method(self, service_file_content):
        assert 'def track_accuracy_trend(' in service_file_content

    def test_has_get_accuracy_history_method(self, service_file_content):
        assert 'def get_accuracy_history(' in service_file_content


class TestConfidenceDistribution:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'model_drift_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_analyze_confidence_shift_method(self, service_file_content):
        assert 'def analyze_confidence_shift(' in service_file_content

    def test_has_get_confidence_distribution_method(self, service_file_content):
        assert 'def get_confidence_distribution(' in service_file_content


class TestDriftReporting:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'model_drift_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_generate_drift_report_method(self, service_file_content):
        assert 'def generate_drift_report(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'model_drift_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_drift_config_method(self, service_file_content):
        assert 'def get_drift_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'model_drift_service.py'
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
            '..', 'backend', 'services', 'model_drift_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class ModelDriftService' in service_file_content:
            idx = service_file_content.find('class ModelDriftService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
