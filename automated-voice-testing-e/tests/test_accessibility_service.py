"""
Test suite for Accessibility Service.

Components:
- WCAG 2.1 AA compliance
- Screen reader support
- Keyboard navigation
- Color contrast compliance
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestAccessibilityServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'accessibility_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'accessibility_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class AccessibilityService' in service_file_content


class TestWCAGCompliance:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'accessibility_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_audit_compliance_method(self, service_file_content):
        assert 'def audit_compliance(' in service_file_content

    def test_has_get_violations_method(self, service_file_content):
        assert 'def get_violations(' in service_file_content

    def test_has_generate_report_method(self, service_file_content):
        assert 'def generate_report(' in service_file_content


class TestScreenReaderSupport:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'accessibility_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_aria_labels_method(self, service_file_content):
        assert 'def get_aria_labels(' in service_file_content

    def test_has_validate_aria_method(self, service_file_content):
        assert 'def validate_aria(' in service_file_content

    def test_has_get_announcements_method(self, service_file_content):
        assert 'def get_announcements(' in service_file_content


class TestKeyboardNavigation:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'accessibility_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_focus_order_method(self, service_file_content):
        assert 'def get_focus_order(' in service_file_content

    def test_has_validate_tab_navigation_method(self, service_file_content):
        assert 'def validate_tab_navigation(' in service_file_content


class TestColorContrastCompliance:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'accessibility_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_check_contrast_method(self, service_file_content):
        assert 'def check_contrast(' in service_file_content

    def test_has_get_color_issues_method(self, service_file_content):
        assert 'def get_color_issues(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'accessibility_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_accessibility_config_method(self, service_file_content):
        assert 'def get_accessibility_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'accessibility_service.py'
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
            '..', 'backend', 'services', 'accessibility_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class AccessibilityService' in service_file_content:
            idx = service_file_content.find('class AccessibilityService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
