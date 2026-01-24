"""
Test suite for Environment Parity Service.

Components:
- Dev/staging/prod configuration comparison
- Data anonymization for lower environments
- Synthetic data for testing
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestEnvironmentParityServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'environment_parity_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'environment_parity_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class EnvironmentParityService' in service_file_content


class TestConfigurationComparison:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'environment_parity_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_compare_environments_method(self, service_file_content):
        assert 'def compare_environments(' in service_file_content

    def test_has_get_config_diff_method(self, service_file_content):
        assert 'def get_config_diff(' in service_file_content

    def test_has_validate_parity_method(self, service_file_content):
        assert 'def validate_parity(' in service_file_content


class TestDataAnonymization:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'environment_parity_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_anonymize_data_method(self, service_file_content):
        assert 'def anonymize_data(' in service_file_content

    def test_has_configure_anonymization_method(self, service_file_content):
        assert 'def configure_anonymization(' in service_file_content

    def test_has_verify_anonymization_method(self, service_file_content):
        assert 'def verify_anonymization(' in service_file_content


class TestSyntheticData:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'environment_parity_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_generate_synthetic_data_method(self, service_file_content):
        assert 'def generate_synthetic_data(' in service_file_content

    def test_has_configure_data_generator_method(self, service_file_content):
        assert 'def configure_data_generator(' in service_file_content

    def test_has_validate_synthetic_data_method(self, service_file_content):
        assert 'def validate_synthetic_data(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'environment_parity_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_parity_config_method(self, service_file_content):
        assert 'def get_parity_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'environment_parity_service.py'
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
            '..', 'backend', 'services', 'environment_parity_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class EnvironmentParityService' in service_file_content:
            idx = service_file_content.find('class EnvironmentParityService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
