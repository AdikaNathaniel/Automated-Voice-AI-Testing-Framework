"""
Test suite for Degradation Alert Service.

Components:
- Automatic alerts on performance drops
- Threshold-based triggers
- Trend-based early warning
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestDegradationAlertServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'degradation_alert_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'degradation_alert_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class DegradationAlertService' in service_file_content


class TestAutomaticAlerts:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'degradation_alert_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_check_performance_drop_method(self, service_file_content):
        assert 'def check_performance_drop(' in service_file_content

    def test_has_send_alert_method(self, service_file_content):
        assert 'def send_alert(' in service_file_content

    def test_has_get_alert_history_method(self, service_file_content):
        assert 'def get_alert_history(' in service_file_content


class TestThresholdTriggers:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'degradation_alert_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_set_threshold_method(self, service_file_content):
        assert 'def set_threshold(' in service_file_content

    def test_has_get_thresholds_method(self, service_file_content):
        assert 'def get_thresholds(' in service_file_content

    def test_has_evaluate_thresholds_method(self, service_file_content):
        assert 'def evaluate_thresholds(' in service_file_content


class TestTrendBasedWarning:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'degradation_alert_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_analyze_trend_method(self, service_file_content):
        assert 'def analyze_trend(' in service_file_content

    def test_has_generate_early_warning_method(self, service_file_content):
        assert 'def generate_early_warning(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'degradation_alert_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_alert_config_method(self, service_file_content):
        assert 'def get_alert_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'degradation_alert_service.py'
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
            '..', 'backend', 'services', 'degradation_alert_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class DegradationAlertService' in service_file_content:
            idx = service_file_content.find('class DegradationAlertService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
