"""
Test suite for Interactive API Docs Service.

Components:
- Try-it-out functionality
- Request/response examples
- Authentication setup guide
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestInteractiveApiDocsServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'interactive_api_docs_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'interactive_api_docs_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class InteractiveApiDocsService' in service_file_content


class TestTryItOutFunctionality:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'interactive_api_docs_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_execute_request_method(self, service_file_content):
        assert 'def execute_request(' in service_file_content

    def test_has_validate_request_method(self, service_file_content):
        assert 'def validate_request(' in service_file_content

    def test_has_get_request_history_method(self, service_file_content):
        assert 'def get_request_history(' in service_file_content


class TestRequestResponseExamples:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'interactive_api_docs_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_examples_method(self, service_file_content):
        assert 'def get_examples(' in service_file_content

    def test_has_generate_example_method(self, service_file_content):
        assert 'def generate_example(' in service_file_content

    def test_has_list_endpoints_method(self, service_file_content):
        assert 'def list_endpoints(' in service_file_content


class TestAuthenticationSetup:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'interactive_api_docs_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_auth_guide_method(self, service_file_content):
        assert 'def get_auth_guide(' in service_file_content

    def test_has_test_auth_method(self, service_file_content):
        assert 'def test_auth(' in service_file_content

    def test_has_get_auth_types_method(self, service_file_content):
        assert 'def get_auth_types(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'interactive_api_docs_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_docs_config_method(self, service_file_content):
        assert 'def get_docs_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'interactive_api_docs_service.py'
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
            '..', 'backend', 'services', 'interactive_api_docs_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class InteractiveApiDocsService' in service_file_content:
            idx = service_file_content.find('class InteractiveApiDocsService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
