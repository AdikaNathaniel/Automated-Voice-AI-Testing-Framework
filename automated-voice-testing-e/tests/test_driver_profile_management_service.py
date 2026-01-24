"""
Test suite for Driver Profile Management Service.

Components:
- Profile creation and switching
- Preference synchronization
- Multi-vehicle profiles
- Guest mode
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestDriverProfileManagementServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'driver_profile_management_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'driver_profile_management_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class DriverProfileManagementService' in service_file_content


class TestProfileCreationSwitching:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'driver_profile_management_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_create_profile_method(self, service_file_content):
        assert 'def create_profile(' in service_file_content

    def test_has_switch_profile_method(self, service_file_content):
        assert 'def switch_profile(' in service_file_content

    def test_has_get_active_profile_method(self, service_file_content):
        assert 'def get_active_profile(' in service_file_content

    def test_has_delete_profile_method(self, service_file_content):
        assert 'def delete_profile(' in service_file_content


class TestPreferenceSynchronization:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'driver_profile_management_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_sync_preferences_method(self, service_file_content):
        assert 'def sync_preferences(' in service_file_content

    def test_has_get_sync_status_method(self, service_file_content):
        assert 'def get_sync_status(' in service_file_content

    def test_has_resolve_conflicts_method(self, service_file_content):
        assert 'def resolve_conflicts(' in service_file_content


class TestMultiVehicleProfiles:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'driver_profile_management_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_link_vehicle_method(self, service_file_content):
        assert 'def link_vehicle(' in service_file_content

    def test_has_get_linked_vehicles_method(self, service_file_content):
        assert 'def get_linked_vehicles(' in service_file_content

    def test_has_transfer_profile_method(self, service_file_content):
        assert 'def transfer_profile(' in service_file_content


class TestGuestMode:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'driver_profile_management_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_enable_guest_mode_method(self, service_file_content):
        assert 'def enable_guest_mode(' in service_file_content

    def test_has_disable_guest_mode_method(self, service_file_content):
        assert 'def disable_guest_mode(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'driver_profile_management_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_profile_config_method(self, service_file_content):
        assert 'def get_profile_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'driver_profile_management_service.py'
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
            '..', 'backend', 'services', 'driver_profile_management_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class DriverProfileManagementService' in service_file_content:
            idx = service_file_content.find('class DriverProfileManagementService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
