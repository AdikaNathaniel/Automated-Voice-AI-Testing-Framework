"""
Test suite for Architecture Decision Records (ADR) Service.

Components:
- Document key decisions
- Trade-off analysis
- Decision rationale
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestADRServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'adr_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'adr_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class ADRService' in service_file_content


class TestDocumentKeyDecisions:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'adr_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_create_adr_method(self, service_file_content):
        assert 'def create_adr(' in service_file_content

    def test_has_get_adr_method(self, service_file_content):
        assert 'def get_adr(' in service_file_content

    def test_has_list_adrs_method(self, service_file_content):
        assert 'def list_adrs(' in service_file_content

    def test_has_update_adr_status_method(self, service_file_content):
        assert 'def update_adr_status(' in service_file_content

    def test_has_search_adrs_method(self, service_file_content):
        assert 'def search_adrs(' in service_file_content


class TestTradeoffAnalysis:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'adr_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_add_tradeoff_method(self, service_file_content):
        assert 'def add_tradeoff(' in service_file_content

    def test_has_list_tradeoffs_method(self, service_file_content):
        assert 'def list_tradeoffs(' in service_file_content

    def test_has_compare_options_method(self, service_file_content):
        assert 'def compare_options(' in service_file_content

    def test_has_get_pros_cons_method(self, service_file_content):
        assert 'def get_pros_cons(' in service_file_content


class TestDecisionRationale:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'adr_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_add_rationale_method(self, service_file_content):
        assert 'def add_rationale(' in service_file_content

    def test_has_get_rationale_method(self, service_file_content):
        assert 'def get_rationale(' in service_file_content

    def test_has_add_context_method(self, service_file_content):
        assert 'def add_context(' in service_file_content

    def test_has_get_consequences_method(self, service_file_content):
        assert 'def get_consequences(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'adr_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_adr_config_method(self, service_file_content):
        assert 'def get_adr_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'adr_service.py'
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
            '..', 'backend', 'services', 'adr_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class ADRService' in service_file_content:
            idx = service_file_content.find('class ADRService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
