"""
Test suite for Climate Commands Service.

Components:
- Temperature control
- Fan speed control
- Airflow direction
- Climate modes
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestClimateCommandsServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'climate_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'climate_commands_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class ClimateCommandsService' in service_file_content


class TestTemperatureControl:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'climate_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_set_temperature_method(self, service_file_content):
        assert 'def set_temperature(' in service_file_content

    def test_has_adjust_temperature_method(self, service_file_content):
        assert 'def adjust_temperature(' in service_file_content

    def test_has_set_zone_temperature_method(self, service_file_content):
        assert 'def set_zone_temperature(' in service_file_content


class TestFanAndAirflow:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'climate_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_control_fan_speed_method(self, service_file_content):
        assert 'def control_fan_speed(' in service_file_content

    def test_has_set_airflow_direction_method(self, service_file_content):
        assert 'def set_airflow_direction(' in service_file_content

    def test_has_toggle_ac_method(self, service_file_content):
        assert 'def toggle_ac(' in service_file_content


class TestClimateModes:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'climate_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_set_climate_mode_method(self, service_file_content):
        assert 'def set_climate_mode(' in service_file_content

    def test_has_control_defrost_method(self, service_file_content):
        assert 'def control_defrost(' in service_file_content

    def test_has_get_climate_status_method(self, service_file_content):
        assert 'def get_climate_status(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'climate_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_climate_commands_config_method(self, service_file_content):
        assert 'def get_climate_commands_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'climate_commands_service.py'
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
            '..', 'backend', 'services', 'climate_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class ClimateCommandsService' in service_file_content:
            idx = service_file_content.find('class ClimateCommandsService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
