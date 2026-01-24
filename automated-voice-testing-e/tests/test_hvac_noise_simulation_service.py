"""
Test suite for HVAC Noise Simulation Service.

Components:
- Fan speed noise levels
- AC compressor cycling
- Defrost and ventilation
- Air quality systems
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestHVACNoiseSimulationServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'hvac_noise_simulation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'hvac_noise_simulation_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class HVACNoiseSimulationService' in service_file_content


class TestFanSpeedNoise:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'hvac_noise_simulation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_generate_fan_noise_method(self, service_file_content):
        assert 'def generate_fan_noise(' in service_file_content

    def test_has_get_fan_speed_profiles_method(self, service_file_content):
        assert 'def get_fan_speed_profiles(' in service_file_content


class TestACCompressor:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'hvac_noise_simulation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_generate_ac_compressor_noise_method(self, service_file_content):
        assert 'def generate_ac_compressor_noise(' in service_file_content

    def test_has_simulate_compressor_cycling_method(self, service_file_content):
        assert 'def simulate_compressor_cycling(' in service_file_content


class TestDefrostAndVentilation:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'hvac_noise_simulation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_generate_defrost_noise_method(self, service_file_content):
        assert 'def generate_defrost_noise(' in service_file_content

    def test_has_generate_seat_ventilation_noise_method(self, service_file_content):
        assert 'def generate_seat_ventilation_noise(' in service_file_content


class TestAirQuality:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'hvac_noise_simulation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_generate_air_filter_noise_method(self, service_file_content):
        assert 'def generate_air_filter_noise(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'hvac_noise_simulation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_hvac_noise_config_method(self, service_file_content):
        assert 'def get_hvac_noise_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'hvac_noise_simulation_service.py'
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
            '..', 'backend', 'services', 'hvac_noise_simulation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class HVACNoiseSimulationService' in service_file_content:
            idx = service_file_content.find('class HVACNoiseSimulationService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
