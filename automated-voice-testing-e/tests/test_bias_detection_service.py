"""
Test suite for Bias Detection Service.

Components:
- Gender bias in recognition
- Accent bias analysis
- Age group bias detection
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestBiasDetectionServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'bias_detection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'bias_detection_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class BiasDetectionService' in service_file_content


class TestGenderBias:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'bias_detection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_detect_gender_bias_method(self, service_file_content):
        assert 'def detect_gender_bias(' in service_file_content

    def test_has_get_gender_metrics_method(self, service_file_content):
        assert 'def get_gender_metrics(' in service_file_content


class TestAccentBias:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'bias_detection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_detect_accent_bias_method(self, service_file_content):
        assert 'def detect_accent_bias(' in service_file_content

    def test_has_get_accent_metrics_method(self, service_file_content):
        assert 'def get_accent_metrics(' in service_file_content


class TestAgeBias:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'bias_detection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_detect_age_bias_method(self, service_file_content):
        assert 'def detect_age_bias(' in service_file_content

    def test_has_get_age_metrics_method(self, service_file_content):
        assert 'def get_age_metrics(' in service_file_content


class TestBiasReporting:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'bias_detection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_generate_bias_report_method(self, service_file_content):
        assert 'def generate_bias_report(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'bias_detection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_bias_config_method(self, service_file_content):
        assert 'def get_bias_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'bias_detection_service.py'
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
            '..', 'backend', 'services', 'bias_detection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class BiasDetectionService' in service_file_content:
            idx = service_file_content.find('class BiasDetectionService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
