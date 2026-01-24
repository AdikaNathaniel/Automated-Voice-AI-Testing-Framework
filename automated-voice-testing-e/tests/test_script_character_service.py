"""
Test suite for Script and Character Testing Service.

This service provides script and character testing for voice AI.

Components:
- Right-to-left languages (Arabic, Hebrew)
- Bidirectional text handling
- Character encoding (UTF-8, UTF-16)
- Diacritics and special characters
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestScriptCharacterServiceExists:
    """Test that service exists"""

    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'script_character_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'script_character_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class ScriptCharacterService' in service_file_content


class TestRTLLanguages:
    """Test RTL language handling"""

    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'script_character_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_detect_rtl_method(self, service_file_content):
        assert 'def detect_rtl(' in service_file_content

    def test_has_get_rtl_languages_method(self, service_file_content):
        assert 'def get_rtl_languages(' in service_file_content


class TestBidirectionalText:
    """Test bidirectional text handling"""

    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'script_character_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_handle_bidi_text_method(self, service_file_content):
        assert 'def handle_bidi_text(' in service_file_content

    def test_has_evaluate_bidi_accuracy_method(self, service_file_content):
        assert 'def evaluate_bidi_accuracy(' in service_file_content


class TestCharacterEncoding:
    """Test character encoding"""

    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'script_character_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_validate_encoding_method(self, service_file_content):
        assert 'def validate_encoding(' in service_file_content

    def test_has_get_supported_encodings_method(self, service_file_content):
        assert 'def get_supported_encodings(' in service_file_content


class TestDiacritics:
    """Test diacritics and special characters"""

    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'script_character_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_handle_diacritics_method(self, service_file_content):
        assert 'def handle_diacritics(' in service_file_content

    def test_has_normalize_characters_method(self, service_file_content):
        assert 'def normalize_characters(' in service_file_content


class TestScriptConfig:
    """Test script configuration"""

    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'script_character_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_script_config_method(self, service_file_content):
        assert 'def get_script_config(' in service_file_content


class TestTypeHints:
    """Test type hints"""

    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'script_character_service.py'
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
    """Test documentation"""

    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'script_character_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class ScriptCharacterService' in service_file_content:
            idx = service_file_content.find('class ScriptCharacterService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section

