"""
Test suite for Contextual Help Service.

Components:
- Tooltips and popovers
- Inline documentation
- Video tutorials
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestContextualHelpServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'contextual_help_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'contextual_help_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class ContextualHelpService' in service_file_content


class TestTooltipsAndPopovers:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'contextual_help_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_tooltip_method(self, service_file_content):
        assert 'def get_tooltip(' in service_file_content

    def test_has_get_popover_method(self, service_file_content):
        assert 'def get_popover(' in service_file_content

    def test_has_register_tooltip_method(self, service_file_content):
        assert 'def register_tooltip(' in service_file_content


class TestInlineDocumentation:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'contextual_help_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_inline_doc_method(self, service_file_content):
        assert 'def get_inline_doc(' in service_file_content

    def test_has_search_docs_method(self, service_file_content):
        assert 'def search_docs(' in service_file_content

    def test_has_get_related_docs_method(self, service_file_content):
        assert 'def get_related_docs(' in service_file_content


class TestVideoTutorials:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'contextual_help_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_list_videos_method(self, service_file_content):
        assert 'def list_videos(' in service_file_content

    def test_has_get_video_method(self, service_file_content):
        assert 'def get_video(' in service_file_content

    def test_has_track_video_progress_method(self, service_file_content):
        assert 'def track_video_progress(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'contextual_help_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_help_config_method(self, service_file_content):
        assert 'def get_help_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'contextual_help_service.py'
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
            '..', 'backend', 'services', 'contextual_help_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class ContextualHelpService' in service_file_content:
            idx = service_file_content.find('class ContextualHelpService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
