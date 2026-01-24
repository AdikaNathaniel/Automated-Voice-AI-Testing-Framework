"""
Test suite for Data Retention Service.

Components:
- Configurable retention periods
- Automatic data deletion jobs
- Legal hold support
- Data export for deletion requests
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestDataRetentionServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'data_retention_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'data_retention_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class DataRetentionService' in service_file_content


class TestRetentionPeriods:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'data_retention_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_set_retention_period_method(self, service_file_content):
        assert 'def set_retention_period(' in service_file_content

    def test_has_get_retention_periods_method(self, service_file_content):
        assert 'def get_retention_periods(' in service_file_content


class TestDataDeletion:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'data_retention_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_schedule_deletion_method(self, service_file_content):
        assert 'def schedule_deletion(' in service_file_content

    def test_has_get_deletion_jobs_method(self, service_file_content):
        assert 'def get_deletion_jobs(' in service_file_content

    def test_has_execute_deletion_method(self, service_file_content):
        assert 'def execute_deletion(' in service_file_content


class TestLegalHold:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'data_retention_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_set_legal_hold_method(self, service_file_content):
        assert 'def set_legal_hold(' in service_file_content

    def test_has_get_legal_holds_method(self, service_file_content):
        assert 'def get_legal_holds(' in service_file_content

    def test_has_release_legal_hold_method(self, service_file_content):
        assert 'def release_legal_hold(' in service_file_content


class TestDataExport:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'data_retention_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_export_user_data_method(self, service_file_content):
        assert 'def export_user_data(' in service_file_content

    def test_has_get_export_status_method(self, service_file_content):
        assert 'def get_export_status(' in service_file_content


class TestRetentionConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'data_retention_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_retention_config_method(self, service_file_content):
        assert 'def get_retention_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'data_retention_service.py'
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
            '..', 'backend', 'services', 'data_retention_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class DataRetentionService' in service_file_content:
            idx = service_file_content.find('class DataRetentionService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
