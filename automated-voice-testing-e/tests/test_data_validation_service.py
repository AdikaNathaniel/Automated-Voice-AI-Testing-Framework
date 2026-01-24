"""
Test suite for Test Data Validation Service.

Components:
- Schema validation for test cases
- Audio format validation
- Transcript consistency checking
- Duplicate detection
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestDataValidationServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'data_validation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'data_validation_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class DataValidationService' in service_file_content


class TestSchemaValidation:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'data_validation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_validate_schema_method(self, service_file_content):
        assert 'def validate_schema(' in service_file_content

    def test_has_get_schema_method(self, service_file_content):
        assert 'def get_schema(' in service_file_content


class TestAudioValidation:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'data_validation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_validate_audio_format_method(self, service_file_content):
        assert 'def validate_audio_format(' in service_file_content

    def test_has_get_supported_formats_method(self, service_file_content):
        assert 'def get_supported_formats(' in service_file_content


class TestTranscriptValidation:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'data_validation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_validate_transcript_consistency_method(self, service_file_content):
        assert 'def validate_transcript_consistency(' in service_file_content

    def test_has_check_transcript_quality_method(self, service_file_content):
        assert 'def check_transcript_quality(' in service_file_content


class TestDuplicateDetection:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'data_validation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_detect_duplicates_method(self, service_file_content):
        assert 'def detect_duplicates(' in service_file_content

    def test_has_get_duplicate_report_method(self, service_file_content):
        assert 'def get_duplicate_report(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'data_validation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_validation_config_method(self, service_file_content):
        assert 'def get_validation_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'data_validation_service.py'
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
            '..', 'backend', 'services', 'data_validation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class DataValidationService' in service_file_content:
            idx = service_file_content.find('class DataValidationService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
