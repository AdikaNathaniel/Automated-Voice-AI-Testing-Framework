"""
Test suite for CLI Service.

Components:
- Command-line interface for common operations
- Shell completion
- Configuration management
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestCLIServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'cli_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'cli_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class CLIService' in service_file_content


class TestCommandInterface:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'cli_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_register_command_method(self, service_file_content):
        assert 'def register_command(' in service_file_content

    def test_has_execute_command_method(self, service_file_content):
        assert 'def execute_command(' in service_file_content

    def test_has_get_available_commands_method(self, service_file_content):
        assert 'def get_available_commands(' in service_file_content


class TestShellCompletion:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'cli_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_generate_completion_method(self, service_file_content):
        assert 'def generate_completion(' in service_file_content

    def test_has_get_completions_method(self, service_file_content):
        assert 'def get_completions(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'cli_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_cli_config_method(self, service_file_content):
        assert 'def get_cli_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'cli_service.py'
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
            '..', 'backend', 'services', 'cli_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class CLIService' in service_file_content:
            idx = service_file_content.find('class CLIService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
