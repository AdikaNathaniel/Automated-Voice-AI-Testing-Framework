"""
Test suite for Export Service.

Components:
- PDF report generation
- Excel export with formatting
- CSV bulk export
- Interactive HTML reports
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestExportServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'export_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'export_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class ExportService' in service_file_content


class TestPDFExport:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'export_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_export_to_pdf_method(self, service_file_content):
        assert 'def export_to_pdf(' in service_file_content

    def test_has_configure_pdf_options_method(self, service_file_content):
        assert 'def configure_pdf_options(' in service_file_content


class TestExcelExport:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'export_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_export_to_excel_method(self, service_file_content):
        assert 'def export_to_excel(' in service_file_content

    def test_has_configure_excel_formatting_method(self, service_file_content):
        assert 'def configure_excel_formatting(' in service_file_content


class TestCSVExport:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'export_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_export_to_csv_method(self, service_file_content):
        assert 'def export_to_csv(' in service_file_content

    def test_has_bulk_export_csv_method(self, service_file_content):
        assert 'def bulk_export_csv(' in service_file_content


class TestHTMLExport:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'export_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_export_to_html_method(self, service_file_content):
        assert 'def export_to_html(' in service_file_content

    def test_has_generate_interactive_report_method(self, service_file_content):
        assert 'def generate_interactive_report(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'export_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_export_config_method(self, service_file_content):
        assert 'def get_export_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'export_service.py'
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
            '..', 'backend', 'services', 'export_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class ExportService' in service_file_content:
            idx = service_file_content.find('class ExportService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
