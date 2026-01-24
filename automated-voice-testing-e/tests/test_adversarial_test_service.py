"""
Test suite for Adversarial Test Generation Service.

Components:
- Edge case generation
- Boundary condition tests
- Typo/mispronunciation injection
- Grammar error injection
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestAdversarialTestServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'adversarial_test_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'adversarial_test_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class AdversarialTestService' in service_file_content


class TestEdgeCaseGeneration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'adversarial_test_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_generate_edge_cases_method(self, service_file_content):
        assert 'def generate_edge_cases(' in service_file_content

    def test_has_get_edge_case_categories_method(self, service_file_content):
        assert 'def get_edge_case_categories(' in service_file_content


class TestBoundaryConditions:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'adversarial_test_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_generate_boundary_tests_method(self, service_file_content):
        assert 'def generate_boundary_tests(' in service_file_content

    def test_has_get_boundary_types_method(self, service_file_content):
        assert 'def get_boundary_types(' in service_file_content


class TestTypoInjection:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'adversarial_test_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_inject_typos_method(self, service_file_content):
        assert 'def inject_typos(' in service_file_content

    def test_has_inject_mispronunciations_method(self, service_file_content):
        assert 'def inject_mispronunciations(' in service_file_content


class TestGrammarErrors:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'adversarial_test_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_inject_grammar_errors_method(self, service_file_content):
        assert 'def inject_grammar_errors(' in service_file_content

    def test_has_get_grammar_error_types_method(self, service_file_content):
        assert 'def get_grammar_error_types(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'adversarial_test_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_adversarial_config_method(self, service_file_content):
        assert 'def get_adversarial_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'adversarial_test_service.py'
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
            '..', 'backend', 'services', 'adversarial_test_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class AdversarialTestService' in service_file_content:
            idx = service_file_content.find('class AdversarialTestService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
