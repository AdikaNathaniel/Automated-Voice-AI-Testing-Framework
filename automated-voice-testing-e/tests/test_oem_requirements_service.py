"""
Test suite for OEM-specific Requirements Service.

Components:
- Configurable OEM testing profiles
- Brand-specific terminology
- Response style guidelines
- Feature availability by market/trim
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestOEMRequirementsServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oem_requirements_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oem_requirements_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class OEMRequirementsService' in service_file_content


class TestOEMProfiles:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oem_requirements_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_oem_profile_method(self, service_file_content):
        assert 'def get_oem_profile(' in service_file_content

    def test_has_configure_oem_profile_method(self, service_file_content):
        assert 'def configure_oem_profile(' in service_file_content


class TestBrandTerminology:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oem_requirements_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_brand_terminology_method(self, service_file_content):
        assert 'def get_brand_terminology(' in service_file_content

    def test_has_validate_terminology_method(self, service_file_content):
        assert 'def validate_terminology(' in service_file_content


class TestResponseStyle:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oem_requirements_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_response_style_method(self, service_file_content):
        assert 'def get_response_style(' in service_file_content

    def test_has_validate_response_style_method(self, service_file_content):
        assert 'def validate_response_style(' in service_file_content


class TestFeatureAvailability:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oem_requirements_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_check_feature_availability_method(self, service_file_content):
        assert 'def check_feature_availability(' in service_file_content

    def test_has_get_market_features_method(self, service_file_content):
        assert 'def get_market_features(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oem_requirements_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_oem_requirements_config_method(self, service_file_content):
        assert 'def get_oem_requirements_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oem_requirements_service.py'
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
            '..', 'backend', 'services', 'oem_requirements_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class OEMRequirementsService' in service_file_content:
            idx = service_file_content.find('class OEMRequirementsService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
