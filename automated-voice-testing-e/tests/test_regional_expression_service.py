"""
Test suite for Regional Expression Testing Service.

Components:
- Colloquialisms and slang
- Regional terminology
- Cultural references
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestRegionalExpressionServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'regional_expression_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'regional_expression_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class RegionalExpressionService' in service_file_content


class TestColloquialisms:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'regional_expression_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_detect_colloquialism_method(self, service_file_content):
        assert 'def detect_colloquialism(' in service_file_content

    def test_has_get_slang_dictionary_method(self, service_file_content):
        assert 'def get_slang_dictionary(' in service_file_content


class TestRegionalTerminology:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'regional_expression_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_identify_regional_term_method(self, service_file_content):
        assert 'def identify_regional_term(' in service_file_content

    def test_has_get_regional_vocabulary_method(self, service_file_content):
        assert 'def get_regional_vocabulary(' in service_file_content


class TestCulturalReferences:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'regional_expression_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_detect_cultural_reference_method(self, service_file_content):
        assert 'def detect_cultural_reference(' in service_file_content

    def test_has_get_cultural_database_method(self, service_file_content):
        assert 'def get_cultural_database(' in service_file_content


class TestRegionalConfig:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'regional_expression_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_regional_config_method(self, service_file_content):
        assert 'def get_regional_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'regional_expression_service.py'
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
            '..', 'backend', 'services', 'regional_expression_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class RegionalExpressionService' in service_file_content:
            idx = service_file_content.find('class RegionalExpressionService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section

