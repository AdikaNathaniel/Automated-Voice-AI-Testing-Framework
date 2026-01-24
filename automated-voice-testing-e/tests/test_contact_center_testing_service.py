"""
Test suite for Contact Center Testing Service.

Components:
- IVR flow testing
- Agent assist testing
- Sentiment detection
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestContactCenterTestingServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'contact_center_testing_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'contact_center_testing_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class ContactCenterTestingService' in service_file_content


class TestIVRFlowTesting:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'contact_center_testing_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_test_ivr_flow_method(self, service_file_content):
        assert 'def test_ivr_flow(' in service_file_content

    def test_has_validate_ivr_path_method(self, service_file_content):
        assert 'def validate_ivr_path(' in service_file_content

    def test_has_get_ivr_report_method(self, service_file_content):
        assert 'def get_ivr_report(' in service_file_content


class TestAgentAssist:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'contact_center_testing_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_test_agent_assist_method(self, service_file_content):
        assert 'def test_agent_assist(' in service_file_content

    def test_has_measure_assist_accuracy_method(self, service_file_content):
        assert 'def measure_assist_accuracy(' in service_file_content


class TestSentimentDetection:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'contact_center_testing_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_analyze_sentiment_method(self, service_file_content):
        assert 'def analyze_sentiment(' in service_file_content

    def test_has_track_sentiment_trend_method(self, service_file_content):
        assert 'def track_sentiment_trend(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'contact_center_testing_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_contact_center_config_method(self, service_file_content):
        assert 'def get_contact_center_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'contact_center_testing_service.py'
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
            '..', 'backend', 'services', 'contact_center_testing_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class ContactCenterTestingService' in service_file_content:
            idx = service_file_content.find('class ContactCenterTestingService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
