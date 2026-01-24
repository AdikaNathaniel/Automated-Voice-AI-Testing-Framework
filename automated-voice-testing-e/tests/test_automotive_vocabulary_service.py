"""
Test suite for Automotive Vocabulary Service.

Components:
- Car terminology variations (UK vs US English)
- Measurement units (miles vs kilometers)
- Temperature units (Fahrenheit vs Celsius)
- Address format variations
- Phone number formats
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestAutomotiveVocabularyServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'automotive_vocabulary_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'automotive_vocabulary_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class AutomotiveVocabularyService' in service_file_content


class TestCarTerminologyVariations:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'automotive_vocabulary_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_translate_terminology_method(self, service_file_content):
        assert 'def translate_terminology(' in service_file_content

    def test_has_get_regional_terms_method(self, service_file_content):
        assert 'def get_regional_terms(' in service_file_content

    def test_has_detect_dialect_method(self, service_file_content):
        assert 'def detect_dialect(' in service_file_content


class TestMeasurementUnits:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'automotive_vocabulary_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_convert_distance_method(self, service_file_content):
        assert 'def convert_distance(' in service_file_content

    def test_has_format_distance_method(self, service_file_content):
        assert 'def format_distance(' in service_file_content


class TestTemperatureUnits:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'automotive_vocabulary_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_convert_temperature_method(self, service_file_content):
        assert 'def convert_temperature(' in service_file_content

    def test_has_format_temperature_method(self, service_file_content):
        assert 'def format_temperature(' in service_file_content


class TestAddressFormats:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'automotive_vocabulary_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_format_address_method(self, service_file_content):
        assert 'def format_address(' in service_file_content

    def test_has_parse_address_method(self, service_file_content):
        assert 'def parse_address(' in service_file_content


class TestPhoneNumberFormats:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'automotive_vocabulary_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_format_phone_number_method(self, service_file_content):
        assert 'def format_phone_number(' in service_file_content

    def test_has_validate_phone_number_method(self, service_file_content):
        assert 'def validate_phone_number(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'automotive_vocabulary_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_vocabulary_config_method(self, service_file_content):
        assert 'def get_vocabulary_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'automotive_vocabulary_service.py'
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
            '..', 'backend', 'services', 'automotive_vocabulary_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class AutomotiveVocabularyService' in service_file_content:
            idx = service_file_content.find('class AutomotiveVocabularyService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
