"""
Test suite for Capacity Monitoring Service.

Components:
- Growth forecasting
- Capacity alerts
- Cost monitoring
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestCapacityMonitoringServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'capacity_monitoring_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'capacity_monitoring_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class CapacityMonitoringService' in service_file_content


class TestGrowthForecasting:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'capacity_monitoring_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_forecast_growth_method(self, service_file_content):
        assert 'def forecast_growth(' in service_file_content

    def test_has_analyze_trends_method(self, service_file_content):
        assert 'def analyze_trends(' in service_file_content

    def test_has_get_growth_metrics_method(self, service_file_content):
        assert 'def get_growth_metrics(' in service_file_content


class TestCapacityAlerts:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'capacity_monitoring_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_configure_capacity_alert_method(self, service_file_content):
        assert 'def configure_capacity_alert(' in service_file_content

    def test_has_check_capacity_method(self, service_file_content):
        assert 'def check_capacity(' in service_file_content

    def test_has_get_capacity_status_method(self, service_file_content):
        assert 'def get_capacity_status(' in service_file_content


class TestCostMonitoring:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'capacity_monitoring_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_track_costs_method(self, service_file_content):
        assert 'def track_costs(' in service_file_content

    def test_has_set_budget_alert_method(self, service_file_content):
        assert 'def set_budget_alert(' in service_file_content

    def test_has_get_cost_report_method(self, service_file_content):
        assert 'def get_cost_report(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'capacity_monitoring_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_capacity_monitoring_config_method(self, service_file_content):
        assert 'def get_capacity_monitoring_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'capacity_monitoring_service.py'
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
            '..', 'backend', 'services', 'capacity_monitoring_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class CapacityMonitoringService' in service_file_content:
            idx = service_file_content.find('class CapacityMonitoringService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
