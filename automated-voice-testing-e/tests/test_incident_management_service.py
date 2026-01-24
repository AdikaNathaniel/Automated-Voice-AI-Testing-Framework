"""
Test suite for Incident Management Service.

Components:
- PagerDuty/OpsGenie integration
- Escalation policies
- Incident retrospectives
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestIncidentManagementServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'incident_management_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'incident_management_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class IncidentManagementService' in service_file_content


class TestPagerDutyIntegration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'incident_management_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_configure_pagerduty_method(self, service_file_content):
        assert 'def configure_pagerduty(' in service_file_content

    def test_has_create_incident_method(self, service_file_content):
        assert 'def create_incident(' in service_file_content

    def test_has_get_incident_status_method(self, service_file_content):
        assert 'def get_incident_status(' in service_file_content


class TestEscalationPolicies:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'incident_management_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_create_escalation_policy_method(self, service_file_content):
        assert 'def create_escalation_policy(' in service_file_content

    def test_has_trigger_escalation_method(self, service_file_content):
        assert 'def trigger_escalation(' in service_file_content

    def test_has_get_escalation_status_method(self, service_file_content):
        assert 'def get_escalation_status(' in service_file_content


class TestIncidentRetrospectives:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'incident_management_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_create_retrospective_method(self, service_file_content):
        assert 'def create_retrospective(' in service_file_content

    def test_has_add_action_item_method(self, service_file_content):
        assert 'def add_action_item(' in service_file_content

    def test_has_get_retrospective_summary_method(self, service_file_content):
        assert 'def get_retrospective_summary(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'incident_management_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_incident_management_config_method(self, service_file_content):
        assert 'def get_incident_management_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'incident_management_service.py'
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
            '..', 'backend', 'services', 'incident_management_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class IncidentManagementService' in service_file_content:
            idx = service_file_content.find('class IncidentManagementService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
