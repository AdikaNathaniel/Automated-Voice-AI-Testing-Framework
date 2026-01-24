"""
Test suite for Recovery Procedures Service.

Components:
- RTO/RPO definitions
- Recovery runbooks
- DR testing schedule
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestRecoveryProceduresServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'recovery_procedures_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'recovery_procedures_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class RecoveryProceduresService' in service_file_content


class TestRtoRpoDefinitions:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'recovery_procedures_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_define_rto_method(self, service_file_content):
        assert 'def define_rto(' in service_file_content

    def test_has_define_rpo_method(self, service_file_content):
        assert 'def define_rpo(' in service_file_content

    def test_has_get_sla_metrics_method(self, service_file_content):
        assert 'def get_sla_metrics(' in service_file_content


class TestRecoveryRunbooks:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'recovery_procedures_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_create_runbook_method(self, service_file_content):
        assert 'def create_runbook(' in service_file_content

    def test_has_execute_runbook_method(self, service_file_content):
        assert 'def execute_runbook(' in service_file_content

    def test_has_get_runbook_status_method(self, service_file_content):
        assert 'def get_runbook_status(' in service_file_content


class TestDrTestingSchedule:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'recovery_procedures_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_schedule_dr_test_method(self, service_file_content):
        assert 'def schedule_dr_test(' in service_file_content

    def test_has_run_dr_test_method(self, service_file_content):
        assert 'def run_dr_test(' in service_file_content

    def test_has_get_dr_test_results_method(self, service_file_content):
        assert 'def get_dr_test_results(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'recovery_procedures_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_recovery_procedures_config_method(self, service_file_content):
        assert 'def get_recovery_procedures_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'recovery_procedures_service.py'
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
            '..', 'backend', 'services', 'recovery_procedures_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class RecoveryProceduresService' in service_file_content:
            idx = service_file_content.find('class RecoveryProceduresService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
