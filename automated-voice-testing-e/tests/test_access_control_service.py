"""
Test suite for Fine-grained Access Control Service.

Components:
- Resource-level permissions
- Project/team isolation
- API key scoping
- IP allowlisting
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestAccessControlServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'access_control_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'access_control_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class AccessControlService' in service_file_content


class TestResourcePermissions:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'access_control_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_set_resource_permission_method(self, service_file_content):
        assert 'def set_resource_permission(' in service_file_content

    def test_has_check_permission_method(self, service_file_content):
        assert 'def check_permission(' in service_file_content

    def test_has_get_resource_permissions_method(self, service_file_content):
        assert 'def get_resource_permissions(' in service_file_content


class TestProjectTeamIsolation:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'access_control_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_create_project_method(self, service_file_content):
        assert 'def create_project(' in service_file_content

    def test_has_add_team_member_method(self, service_file_content):
        assert 'def add_team_member(' in service_file_content

    def test_has_check_project_access_method(self, service_file_content):
        assert 'def check_project_access(' in service_file_content


class TestAPIKeyScoping:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'access_control_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_create_api_key_method(self, service_file_content):
        assert 'def create_api_key(' in service_file_content

    def test_has_set_key_scope_method(self, service_file_content):
        assert 'def set_key_scope(' in service_file_content


class TestIPAllowlisting:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'access_control_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_add_ip_allowlist_method(self, service_file_content):
        assert 'def add_ip_allowlist(' in service_file_content

    def test_has_check_ip_allowed_method(self, service_file_content):
        assert 'def check_ip_allowed(' in service_file_content


class TestAccessControlConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'access_control_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_access_control_config_method(self, service_file_content):
        assert 'def get_access_control_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'access_control_service.py'
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
            '..', 'backend', 'services', 'access_control_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class AccessControlService' in service_file_content:
            idx = service_file_content.find('class AccessControlService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
