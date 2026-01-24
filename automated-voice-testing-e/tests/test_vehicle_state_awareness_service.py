"""
Test suite for Vehicle State Awareness Service.

Components:
- Parked vs driving responses
- Engine on/off context
- EV charging state
- Towing mode
- Valet mode restrictions
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestVehicleStateAwarenessServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'vehicle_state_awareness_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'vehicle_state_awareness_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class VehicleStateAwarenessService' in service_file_content


class TestDrivingState:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'vehicle_state_awareness_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_driving_state_method(self, service_file_content):
        assert 'def get_driving_state(' in service_file_content

    def test_has_is_parked_method(self, service_file_content):
        assert 'def is_parked(' in service_file_content

    def test_has_get_driving_mode_response_method(self, service_file_content):
        assert 'def get_driving_mode_response(' in service_file_content


class TestEngineState:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'vehicle_state_awareness_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_engine_state_method(self, service_file_content):
        assert 'def get_engine_state(' in service_file_content

    def test_has_is_engine_running_method(self, service_file_content):
        assert 'def is_engine_running(' in service_file_content


class TestEVCharging:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'vehicle_state_awareness_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_charging_state_method(self, service_file_content):
        assert 'def get_charging_state(' in service_file_content

    def test_has_is_charging_method(self, service_file_content):
        assert 'def is_charging(' in service_file_content


class TestSpecialModes:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'vehicle_state_awareness_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_towing_mode_method(self, service_file_content):
        assert 'def get_towing_mode(' in service_file_content

    def test_has_get_valet_mode_method(self, service_file_content):
        assert 'def get_valet_mode(' in service_file_content

    def test_has_get_mode_restrictions_method(self, service_file_content):
        assert 'def get_mode_restrictions(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'vehicle_state_awareness_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_vehicle_state_config_method(self, service_file_content):
        assert 'def get_vehicle_state_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'vehicle_state_awareness_service.py'
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
            '..', 'backend', 'services', 'vehicle_state_awareness_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class VehicleStateAwarenessService' in service_file_content:
            idx = service_file_content.find('class VehicleStateAwarenessService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
