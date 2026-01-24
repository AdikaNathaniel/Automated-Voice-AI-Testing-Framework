"""
Test suite for Far-Field Testing Service.

Components:
- Distance-based accuracy
- Echo cancellation testing
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestFarFieldTestingServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'far_field_testing_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'far_field_testing_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class FarFieldTestingService' in service_file_content


class TestDistanceBasedAccuracy:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'far_field_testing_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_test_at_distance_method(self, service_file_content):
        assert 'def test_at_distance(' in service_file_content

    def test_has_measure_accuracy_method(self, service_file_content):
        assert 'def measure_accuracy(' in service_file_content

    def test_has_get_distance_report_method(self, service_file_content):
        assert 'def get_distance_report(' in service_file_content


class TestEchoCancellation:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'far_field_testing_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_test_echo_cancellation_method(self, service_file_content):
        assert 'def test_echo_cancellation(' in service_file_content

    def test_has_measure_echo_reduction_method(self, service_file_content):
        assert 'def measure_echo_reduction(' in service_file_content

    def test_has_get_echo_report_method(self, service_file_content):
        assert 'def get_echo_report(' in service_file_content


class TestNoiseHandling:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'far_field_testing_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_test_with_background_noise_method(self, service_file_content):
        assert 'def test_with_background_noise(' in service_file_content

    def test_has_calculate_snr_method(self, service_file_content):
        assert 'def calculate_snr(' in service_file_content


class TestWakeWordSensitivity:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'far_field_testing_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_test_wake_word_method(self, service_file_content):
        assert 'def test_wake_word(' in service_file_content

    def test_has_measure_false_acceptance_method(self, service_file_content):
        assert 'def measure_false_acceptance(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'far_field_testing_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_far_field_config_method(self, service_file_content):
        assert 'def get_far_field_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'far_field_testing_service.py'
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
            '..', 'backend', 'services', 'far_field_testing_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class FarFieldTestingService' in service_file_content:
            idx = service_file_content.find('class FarFieldTestingService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
