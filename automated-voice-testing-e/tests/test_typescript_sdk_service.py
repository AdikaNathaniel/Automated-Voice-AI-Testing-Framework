"""
Test suite for TypeScript SDK Service.

Components:
- Browser and Node.js support
- TypeScript types
- Promise-based API
- npm package
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestTypeScriptSDKServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'typescript_sdk_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'typescript_sdk_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class TypeScriptSDKService' in service_file_content


class TestClientGeneration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'typescript_sdk_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_generate_client_method(self, service_file_content):
        assert 'def generate_client(' in service_file_content

    def test_has_generate_types_method(self, service_file_content):
        assert 'def generate_types(' in service_file_content


class TestPlatformSupport:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'typescript_sdk_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_create_browser_bundle_method(self, service_file_content):
        assert 'def create_browser_bundle(' in service_file_content

    def test_has_create_node_package_method(self, service_file_content):
        assert 'def create_node_package(' in service_file_content


class TestPackageManagement:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'typescript_sdk_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_generate_npm_package_method(self, service_file_content):
        assert 'def generate_npm_package(' in service_file_content

    def test_has_get_installation_command_method(self, service_file_content):
        assert 'def get_installation_command(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'typescript_sdk_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_sdk_config_method(self, service_file_content):
        assert 'def get_sdk_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'typescript_sdk_service.py'
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
            '..', 'backend', 'services', 'typescript_sdk_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class TypeScriptSDKService' in service_file_content:
            idx = service_file_content.find('class TypeScriptSDKService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
