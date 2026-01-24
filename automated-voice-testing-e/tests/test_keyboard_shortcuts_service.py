"""
Test suite for Keyboard Shortcuts Service.

Components:
- Comprehensive shortcut system
- Customizable shortcuts
- Shortcut cheat sheet
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestKeyboardShortcutsServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'keyboard_shortcuts_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'keyboard_shortcuts_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class KeyboardShortcutsService' in service_file_content


class TestComprehensiveShortcutSystem:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'keyboard_shortcuts_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_register_shortcut_method(self, service_file_content):
        assert 'def register_shortcut(' in service_file_content

    def test_has_get_shortcut_method(self, service_file_content):
        assert 'def get_shortcut(' in service_file_content

    def test_has_list_shortcuts_method(self, service_file_content):
        assert 'def list_shortcuts(' in service_file_content

    def test_has_execute_shortcut_method(self, service_file_content):
        assert 'def execute_shortcut(' in service_file_content


class TestCustomizableShortcuts:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'keyboard_shortcuts_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_customize_shortcut_method(self, service_file_content):
        assert 'def customize_shortcut(' in service_file_content

    def test_has_reset_shortcut_method(self, service_file_content):
        assert 'def reset_shortcut(' in service_file_content

    def test_has_get_user_shortcuts_method(self, service_file_content):
        assert 'def get_user_shortcuts(' in service_file_content


class TestShortcutCheatSheet:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'keyboard_shortcuts_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_cheat_sheet_method(self, service_file_content):
        assert 'def get_cheat_sheet(' in service_file_content

    def test_has_search_shortcuts_method(self, service_file_content):
        assert 'def search_shortcuts(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'keyboard_shortcuts_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_shortcuts_config_method(self, service_file_content):
        assert 'def get_shortcuts_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'keyboard_shortcuts_service.py'
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
            '..', 'backend', 'services', 'keyboard_shortcuts_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class KeyboardShortcutsService' in service_file_content:
            idx = service_file_content.find('class KeyboardShortcutsService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
