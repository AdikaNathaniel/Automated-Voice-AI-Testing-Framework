"""
Test suite for Automated Insights Service.

Components:
- Anomaly summary in reports
- Week-over-week comparison
- Key metrics highlighting
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestAutomatedInsightsServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'automated_insights_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'automated_insights_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class AutomatedInsightsService' in service_file_content


class TestAnomalySummary:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'automated_insights_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_generate_anomaly_summary_method(self, service_file_content):
        assert 'def generate_anomaly_summary(' in service_file_content

    def test_has_detect_anomalies_method(self, service_file_content):
        assert 'def detect_anomalies(' in service_file_content

    def test_has_get_anomaly_details_method(self, service_file_content):
        assert 'def get_anomaly_details(' in service_file_content


class TestWeekOverWeekComparison:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'automated_insights_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_compare_week_over_week_method(self, service_file_content):
        assert 'def compare_week_over_week(' in service_file_content

    def test_has_calculate_trends_method(self, service_file_content):
        assert 'def calculate_trends(' in service_file_content


class TestKeyMetricsHighlighting:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'automated_insights_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_highlight_key_metrics_method(self, service_file_content):
        assert 'def highlight_key_metrics(' in service_file_content

    def test_has_identify_significant_changes_method(self, service_file_content):
        assert 'def identify_significant_changes(' in service_file_content

    def test_has_generate_insights_report_method(self, service_file_content):
        assert 'def generate_insights_report(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'automated_insights_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_insights_config_method(self, service_file_content):
        assert 'def get_insights_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'automated_insights_service.py'
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
            '..', 'backend', 'services', 'automated_insights_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class AutomatedInsightsService' in service_file_content:
            idx = service_file_content.find('class AutomatedInsightsService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
