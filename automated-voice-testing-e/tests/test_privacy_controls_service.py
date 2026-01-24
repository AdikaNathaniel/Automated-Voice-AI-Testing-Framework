"""
Test suite for Privacy Controls Service.

Components:
- Data collection consent
- Profile data deletion
- Anonymization options
- Data portability
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestPrivacyControlsServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'privacy_controls_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'privacy_controls_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class PrivacyControlsService' in service_file_content


class TestDataCollectionConsent:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'privacy_controls_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_set_consent_method(self, service_file_content):
        assert 'def set_consent(' in service_file_content

    def test_has_get_consent_status_method(self, service_file_content):
        assert 'def get_consent_status(' in service_file_content

    def test_has_revoke_consent_method(self, service_file_content):
        assert 'def revoke_consent(' in service_file_content


class TestProfileDataDeletion:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'privacy_controls_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_delete_profile_data_method(self, service_file_content):
        assert 'def delete_profile_data(' in service_file_content

    def test_has_schedule_deletion_method(self, service_file_content):
        assert 'def schedule_deletion(' in service_file_content

    def test_has_get_deletion_status_method(self, service_file_content):
        assert 'def get_deletion_status(' in service_file_content


class TestAnonymizationOptions:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'privacy_controls_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_anonymize_data_method(self, service_file_content):
        assert 'def anonymize_data(' in service_file_content

    def test_has_set_anonymization_level_method(self, service_file_content):
        assert 'def set_anonymization_level(' in service_file_content


class TestDataPortability:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'privacy_controls_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_export_data_method(self, service_file_content):
        assert 'def export_data(' in service_file_content

    def test_has_import_data_method(self, service_file_content):
        assert 'def import_data(' in service_file_content

    def test_has_get_export_formats_method(self, service_file_content):
        assert 'def get_export_formats(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'privacy_controls_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_privacy_config_method(self, service_file_content):
        assert 'def get_privacy_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'privacy_controls_service.py'
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
            '..', 'backend', 'services', 'privacy_controls_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class PrivacyControlsService' in service_file_content:
            idx = service_file_content.find('class PrivacyControlsService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
