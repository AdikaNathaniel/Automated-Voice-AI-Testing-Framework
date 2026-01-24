"""
Test suite for Report Builder Service.

Components:
- Drag-and-drop report creation
- Custom metric selection
- Flexible grouping/filtering
- Template library
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestReportBuilderServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'report_builder_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'report_builder_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class ReportBuilderService' in service_file_content


class TestReportCreation:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'report_builder_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_create_report_method(self, service_file_content):
        assert 'def create_report(' in service_file_content

    def test_has_add_component_method(self, service_file_content):
        assert 'def add_component(' in service_file_content

    def test_has_reorder_components_method(self, service_file_content):
        assert 'def reorder_components(' in service_file_content


class TestMetricSelection:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'report_builder_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_select_metrics_method(self, service_file_content):
        assert 'def select_metrics(' in service_file_content

    def test_has_get_available_metrics_method(self, service_file_content):
        assert 'def get_available_metrics(' in service_file_content


class TestGroupingFiltering:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'report_builder_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_set_grouping_method(self, service_file_content):
        assert 'def set_grouping(' in service_file_content

    def test_has_set_filters_method(self, service_file_content):
        assert 'def set_filters(' in service_file_content


class TestTemplateLibrary:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'report_builder_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_save_as_template_method(self, service_file_content):
        assert 'def save_as_template(' in service_file_content

    def test_has_get_templates_method(self, service_file_content):
        assert 'def get_templates(' in service_file_content

    def test_has_load_template_method(self, service_file_content):
        assert 'def load_template(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'report_builder_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_builder_config_method(self, service_file_content):
        assert 'def get_builder_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'report_builder_service.py'
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
            '..', 'backend', 'services', 'report_builder_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class ReportBuilderService' in service_file_content:
            idx = service_file_content.find('class ReportBuilderService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
