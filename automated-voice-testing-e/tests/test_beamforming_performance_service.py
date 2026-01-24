"""
Test suite for Beamforming Performance Service.

Components:
- Beam steering accuracy
- Noise rejection ratio
- Speaker isolation
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestBeamformingPerformanceServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'beamforming_performance_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'beamforming_performance_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class BeamformingPerformanceService' in service_file_content


class TestBeamSteering:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'beamforming_performance_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_measure_steering_accuracy_method(self, service_file_content):
        assert 'def measure_steering_accuracy(' in service_file_content

    def test_has_set_beam_angle_method(self, service_file_content):
        assert 'def set_beam_angle(' in service_file_content

    def test_has_get_steering_range_method(self, service_file_content):
        assert 'def get_steering_range(' in service_file_content

    def test_has_validate_steering_accuracy_method(self, service_file_content):
        assert 'def validate_steering_accuracy(' in service_file_content


class TestNoiseRejection:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'beamforming_performance_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_measure_noise_rejection_method(self, service_file_content):
        assert 'def measure_noise_rejection(' in service_file_content

    def test_has_calculate_rejection_ratio_method(self, service_file_content):
        assert 'def calculate_rejection_ratio(' in service_file_content

    def test_has_get_rejection_thresholds_method(self, service_file_content):
        assert 'def get_rejection_thresholds(' in service_file_content


class TestSpeakerIsolation:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'beamforming_performance_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_measure_speaker_isolation_method(self, service_file_content):
        assert 'def measure_speaker_isolation(' in service_file_content

    def test_has_calculate_isolation_ratio_method(self, service_file_content):
        assert 'def calculate_isolation_ratio(' in service_file_content

    def test_has_validate_isolation_method(self, service_file_content):
        assert 'def validate_isolation(' in service_file_content


class TestBeamformingMetrics:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'beamforming_performance_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_beam_pattern_method(self, service_file_content):
        assert 'def get_beam_pattern(' in service_file_content

    def test_has_optimize_beam_width_method(self, service_file_content):
        assert 'def optimize_beam_width(' in service_file_content

    def test_has_calculate_directivity_index_method(self, service_file_content):
        assert 'def calculate_directivity_index(' in service_file_content

    def test_has_generate_performance_report_method(self, service_file_content):
        assert 'def generate_performance_report(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'beamforming_performance_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_beamforming_performance_config_method(self, service_file_content):
        assert 'def get_beamforming_performance_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'beamforming_performance_service.py'
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
            '..', 'backend', 'services', 'beamforming_performance_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class BeamformingPerformanceService' in service_file_content:
            idx = service_file_content.find('class BeamformingPerformanceService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
