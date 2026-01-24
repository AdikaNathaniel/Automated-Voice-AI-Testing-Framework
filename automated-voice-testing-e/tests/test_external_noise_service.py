"""
Test suite for External Noise Intrusion Service.

Components:
- Traffic noise
- Construction zones
- Emergency vehicles
- Environmental noise
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestExternalNoiseServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'external_noise_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'external_noise_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class ExternalNoiseService' in service_file_content


class TestTrafficNoise:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'external_noise_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_generate_traffic_noise_method(self, service_file_content):
        assert 'def generate_traffic_noise(' in service_file_content

    def test_has_generate_construction_noise_method(self, service_file_content):
        assert 'def generate_construction_noise(' in service_file_content


class TestEmergencyVehicles:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'external_noise_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_generate_siren_noise_method(self, service_file_content):
        assert 'def generate_siren_noise(' in service_file_content


class TestEnvironmentalNoise:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'external_noise_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_generate_train_crossing_noise_method(self, service_file_content):
        assert 'def generate_train_crossing_noise(' in service_file_content

    def test_has_generate_airport_noise_method(self, service_file_content):
        assert 'def generate_airport_noise(' in service_file_content

    def test_has_generate_urban_noise_method(self, service_file_content):
        assert 'def generate_urban_noise(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'external_noise_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_external_noise_config_method(self, service_file_content):
        assert 'def get_external_noise_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'external_noise_service.py'
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
            '..', 'backend', 'services', 'external_noise_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class ExternalNoiseService' in service_file_content:
            idx = service_file_content.find('class ExternalNoiseService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
