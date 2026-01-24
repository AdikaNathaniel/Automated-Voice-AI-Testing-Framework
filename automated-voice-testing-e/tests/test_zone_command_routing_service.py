"""
Test suite for Zone-specific Command Routing Service.

Components:
- Climate commands per zone
- Audio source per zone
- Volume per zone
- Personal preferences per zone
- Privacy mode per zone
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestZoneCommandRoutingServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'zone_command_routing_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'zone_command_routing_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class ZoneCommandRoutingService' in service_file_content


class TestClimateCommands:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'zone_command_routing_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_set_zone_temperature_method(self, service_file_content):
        assert 'def set_zone_temperature(' in service_file_content

    def test_has_set_zone_fan_speed_method(self, service_file_content):
        assert 'def set_zone_fan_speed(' in service_file_content

    def test_has_set_zone_air_direction_method(self, service_file_content):
        assert 'def set_zone_air_direction(' in service_file_content

    def test_has_get_zone_climate_status_method(self, service_file_content):
        assert 'def get_zone_climate_status(' in service_file_content


class TestAudioCommands:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'zone_command_routing_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_set_zone_audio_source_method(self, service_file_content):
        assert 'def set_zone_audio_source(' in service_file_content

    def test_has_set_zone_volume_method(self, service_file_content):
        assert 'def set_zone_volume(' in service_file_content

    def test_has_mute_zone_method(self, service_file_content):
        assert 'def mute_zone(' in service_file_content

    def test_has_get_zone_audio_status_method(self, service_file_content):
        assert 'def get_zone_audio_status(' in service_file_content


class TestPersonalPreferences:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'zone_command_routing_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_set_zone_preferences_method(self, service_file_content):
        assert 'def set_zone_preferences(' in service_file_content

    def test_has_get_zone_preferences_method(self, service_file_content):
        assert 'def get_zone_preferences(' in service_file_content

    def test_has_load_user_profile_method(self, service_file_content):
        assert 'def load_user_profile(' in service_file_content


class TestPrivacyMode:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'zone_command_routing_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_enable_privacy_mode_method(self, service_file_content):
        assert 'def enable_privacy_mode(' in service_file_content

    def test_has_disable_privacy_mode_method(self, service_file_content):
        assert 'def disable_privacy_mode(' in service_file_content

    def test_has_get_privacy_status_method(self, service_file_content):
        assert 'def get_privacy_status(' in service_file_content


class TestCommandRouting:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'zone_command_routing_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_route_command_to_zone_method(self, service_file_content):
        assert 'def route_command_to_zone(' in service_file_content

    def test_has_broadcast_command_method(self, service_file_content):
        assert 'def broadcast_command(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'zone_command_routing_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_zone_command_routing_config_method(self, service_file_content):
        assert 'def get_zone_command_routing_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'zone_command_routing_service.py'
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
            '..', 'backend', 'services', 'zone_command_routing_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class ZoneCommandRoutingService' in service_file_content:
            idx = service_file_content.find('class ZoneCommandRoutingService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
