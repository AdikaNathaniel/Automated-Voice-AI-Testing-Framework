"""
Test suite for GDPR Compliance Service.

Components:
- Consent management integration
- Right to erasure implementation
- Data portability export
- Processing records
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestGDPRServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'gdpr_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'gdpr_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class GDPRService' in service_file_content


class TestConsentManagement:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'gdpr_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_record_consent_method(self, service_file_content):
        assert 'def record_consent(' in service_file_content

    def test_has_get_consent_status_method(self, service_file_content):
        assert 'def get_consent_status(' in service_file_content

    def test_has_revoke_consent_method(self, service_file_content):
        assert 'def revoke_consent(' in service_file_content


class TestRightToErasure:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'gdpr_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_request_erasure_method(self, service_file_content):
        assert 'def request_erasure(' in service_file_content

    def test_has_execute_erasure_method(self, service_file_content):
        assert 'def execute_erasure(' in service_file_content

    def test_has_get_erasure_status_method(self, service_file_content):
        assert 'def get_erasure_status(' in service_file_content


class TestDataPortability:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'gdpr_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_export_portable_data_method(self, service_file_content):
        assert 'def export_portable_data(' in service_file_content

    def test_has_get_export_formats_method(self, service_file_content):
        assert 'def get_export_formats(' in service_file_content


class TestProcessingRecords:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'gdpr_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_log_processing_method(self, service_file_content):
        assert 'def log_processing(' in service_file_content

    def test_has_get_processing_records_method(self, service_file_content):
        assert 'def get_processing_records(' in service_file_content


class TestGDPRConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'gdpr_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_gdpr_config_method(self, service_file_content):
        assert 'def get_gdpr_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'gdpr_service.py'
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
            '..', 'backend', 'services', 'gdpr_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class GDPRService' in service_file_content:
            idx = service_file_content.find('class GDPRService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
