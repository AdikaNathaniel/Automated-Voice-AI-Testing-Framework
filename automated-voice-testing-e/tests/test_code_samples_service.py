"""
Test suite for Code Samples Service.

Components:
- Python examples
- JavaScript examples
- cURL examples
- Postman collection
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestCodeSamplesServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'code_samples_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'code_samples_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class CodeSamplesService' in service_file_content


class TestLanguageExamples:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'code_samples_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_python_example_method(self, service_file_content):
        assert 'def get_python_example(' in service_file_content

    def test_has_get_javascript_example_method(self, service_file_content):
        assert 'def get_javascript_example(' in service_file_content

    def test_has_get_curl_example_method(self, service_file_content):
        assert 'def get_curl_example(' in service_file_content

    def test_has_list_languages_method(self, service_file_content):
        assert 'def list_languages(' in service_file_content


class TestPostmanCollection:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'code_samples_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_generate_postman_collection_method(self, service_file_content):
        assert 'def generate_postman_collection(' in service_file_content

    def test_has_export_collection_method(self, service_file_content):
        assert 'def export_collection(' in service_file_content


class TestSampleManagement:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'code_samples_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_list_samples_method(self, service_file_content):
        assert 'def list_samples(' in service_file_content

    def test_has_get_sample_method(self, service_file_content):
        assert 'def get_sample(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'code_samples_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_samples_config_method(self, service_file_content):
        assert 'def get_samples_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'code_samples_service.py'
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
            '..', 'backend', 'services', 'code_samples_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class CodeSamplesService' in service_file_content:
            idx = service_file_content.find('class CodeSamplesService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
