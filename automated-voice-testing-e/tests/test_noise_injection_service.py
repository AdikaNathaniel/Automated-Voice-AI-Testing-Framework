"""
Test suite for Noise Injection Service.

Components:
- Additive noise at configurable SNR
- Convolutive noise (room response)
- Real-world noise samples library
- Noise scheduling during utterance
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestNoiseInjectionServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'noise_injection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'noise_injection_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class NoiseInjectionService' in service_file_content


class TestAdditiveNoise:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'noise_injection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_add_noise_method(self, service_file_content):
        assert 'def add_noise(' in service_file_content

    def test_has_set_snr_level_method(self, service_file_content):
        assert 'def set_snr_level(' in service_file_content

    def test_has_get_snr_range_method(self, service_file_content):
        assert 'def get_snr_range(' in service_file_content


class TestConvolutiveNoise:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'noise_injection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_apply_room_response_method(self, service_file_content):
        assert 'def apply_room_response(' in service_file_content

    def test_has_get_room_impulse_responses_method(self, service_file_content):
        assert 'def get_room_impulse_responses(' in service_file_content


class TestNoiseSamplesLibrary:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'noise_injection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_add_noise_sample_method(self, service_file_content):
        assert 'def add_noise_sample(' in service_file_content

    def test_has_get_noise_samples_method(self, service_file_content):
        assert 'def get_noise_samples(' in service_file_content

    def test_has_get_noise_categories_method(self, service_file_content):
        assert 'def get_noise_categories(' in service_file_content


class TestNoiseScheduling:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'noise_injection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_create_noise_schedule_method(self, service_file_content):
        assert 'def create_noise_schedule(' in service_file_content

    def test_has_apply_scheduled_noise_method(self, service_file_content):
        assert 'def apply_scheduled_noise(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'noise_injection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_noise_config_method(self, service_file_content):
        assert 'def get_noise_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'noise_injection_service.py'
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
            '..', 'backend', 'services', 'noise_injection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class NoiseInjectionService' in service_file_content:
            idx = service_file_content.find('class NoiseInjectionService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
