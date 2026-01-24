"""
Test suite for Unified Report Service.

This service consolidates the 4 report generation services into
a coherent interface for report creation, generation, and export.

Components:
- Report creation and building
- Executive report generation
- Component and metric management
- Template library
- PDF/JSON export
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestUnifiedReportServiceExists:
    """Test that unified report service exists"""

    def test_service_file_exists(self):
        """Test that unified_report_service.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'unified_report_service.py'
        )
        assert os.path.exists(service_file), (
            "unified_report_service.py should exist"
        )

    def test_service_class_exists(self):
        """Test that UnifiedReportService class exists"""
        from services.unified_report_service import UnifiedReportService
        assert UnifiedReportService is not None


class TestUnifiedReportServiceBasic:
    """Test basic service functionality"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        from services.unified_report_service import UnifiedReportService
        return UnifiedReportService()

    def test_service_initialization(self, service):
        """Test service initializes correctly"""
        assert service is not None

    def test_has_builder_component(self, service):
        """Test service has builder component"""
        assert hasattr(service, 'builder')

    def test_has_generator_component(self, service):
        """Test service has generator component"""
        assert hasattr(service, 'generator')


class TestReportCreation:
    """Test report creation functionality"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        from services.unified_report_service import UnifiedReportService
        return UnifiedReportService()

    def test_create_report_method(self, service):
        """Test create_report method exists"""
        assert hasattr(service, 'create_report')
        assert callable(getattr(service, 'create_report'))

    def test_create_report_returns_dict(self, service):
        """Test create_report returns dictionary"""
        result = service.create_report('Test Report')
        assert isinstance(result, dict)

    def test_create_report_has_report_id(self, service):
        """Test result has report_id"""
        result = service.create_report('Test Report')
        assert 'report_id' in result

    def test_create_report_has_name(self, service):
        """Test result has name"""
        result = service.create_report('My Report')
        assert result.get('name') == 'My Report'


class TestComponentManagement:
    """Test component management functionality"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        from services.unified_report_service import UnifiedReportService
        return UnifiedReportService()

    def test_add_component_method(self, service):
        """Test add_component method exists"""
        assert hasattr(service, 'add_component')
        assert callable(getattr(service, 'add_component'))

    def test_add_component_returns_dict(self, service):
        """Test add_component returns dictionary"""
        report = service.create_report('Test Report')
        result = service.add_component(
            report['report_id'], 'chart', {'title': 'Test'}
        )
        assert isinstance(result, dict)

    def test_reorder_components_method(self, service):
        """Test reorder_components method exists"""
        assert hasattr(service, 'reorder_components')
        assert callable(getattr(service, 'reorder_components'))


class TestMetricSelection:
    """Test metric selection functionality"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        from services.unified_report_service import UnifiedReportService
        return UnifiedReportService()

    def test_select_metrics_method(self, service):
        """Test select_metrics method exists"""
        assert hasattr(service, 'select_metrics')
        assert callable(getattr(service, 'select_metrics'))

    def test_get_available_metrics_method(self, service):
        """Test get_available_metrics method exists"""
        assert hasattr(service, 'get_available_metrics')
        result = service.get_available_metrics()
        assert isinstance(result, dict)
        assert 'metrics' in result


class TestExecutiveReports:
    """Test executive report generation"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        from services.unified_report_service import UnifiedReportService
        return UnifiedReportService()

    def test_generate_weekly_report_method(self, service):
        """Test generate_weekly_report method exists"""
        assert hasattr(service, 'generate_weekly_report')
        assert callable(getattr(service, 'generate_weekly_report'))

    def test_generate_monthly_report_method(self, service):
        """Test generate_monthly_report method exists"""
        assert hasattr(service, 'generate_monthly_report')
        assert callable(getattr(service, 'generate_monthly_report'))

    def test_generate_executive_summary_method(self, service):
        """Test generate_executive_summary method exists"""
        assert hasattr(service, 'generate_executive_summary')
        assert callable(getattr(service, 'generate_executive_summary'))


class TestTemplateManagement:
    """Test template library functionality"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        from services.unified_report_service import UnifiedReportService
        return UnifiedReportService()

    def test_save_as_template_method(self, service):
        """Test save_as_template method exists"""
        assert hasattr(service, 'save_as_template')
        assert callable(getattr(service, 'save_as_template'))

    def test_get_templates_method(self, service):
        """Test get_templates method exists"""
        assert hasattr(service, 'get_templates')
        result = service.get_templates()
        assert isinstance(result, dict)

    def test_load_template_method(self, service):
        """Test load_template method exists"""
        assert hasattr(service, 'load_template')
        assert callable(getattr(service, 'load_template'))


class TestExportFormats:
    """Test export format functionality"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        from services.unified_report_service import UnifiedReportService
        return UnifiedReportService()

    def test_export_to_json_method(self, service):
        """Test export_to_json method exists"""
        assert hasattr(service, 'export_to_json')
        assert callable(getattr(service, 'export_to_json'))

    def test_get_supported_formats_method(self, service):
        """Test get_supported_formats method exists"""
        assert hasattr(service, 'get_supported_formats')
        formats = service.get_supported_formats()
        assert isinstance(formats, list)
        assert 'json' in formats


class TestFilteringAndGrouping:
    """Test filtering and grouping functionality"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        from services.unified_report_service import UnifiedReportService
        return UnifiedReportService()

    def test_set_grouping_method(self, service):
        """Test set_grouping method exists"""
        assert hasattr(service, 'set_grouping')
        assert callable(getattr(service, 'set_grouping'))

    def test_set_filters_method(self, service):
        """Test set_filters method exists"""
        assert hasattr(service, 'set_filters')
        assert callable(getattr(service, 'set_filters'))


class TestServiceConfiguration:
    """Test service configuration"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        from services.unified_report_service import UnifiedReportService
        return UnifiedReportService()

    def test_get_service_config_method(self, service):
        """Test get_service_config method exists"""
        assert hasattr(service, 'get_service_config')

    def test_config_returns_dict(self, service):
        """Test config returns dictionary"""
        config = service.get_service_config()
        assert isinstance(config, dict)

    def test_config_has_components(self, service):
        """Test config has components"""
        config = service.get_service_config()
        assert 'component_types' in config

    def test_config_has_formats(self, service):
        """Test config has supported formats"""
        config = service.get_service_config()
        assert 'supported_formats' in config


class TestTypeHints:
    """Test type hints for unified report service"""

    @pytest.fixture
    def service_file_content(self):
        """Read the unified report service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'unified_report_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_imports_typing_modules(self, service_file_content):
        """Test typing modules are imported"""
        assert 'from typing import' in service_file_content

    def test_uses_dict_type_hint(self, service_file_content):
        """Test Dict type hint is used"""
        assert 'Dict[' in service_file_content


class TestDocstrings:
    """Test comprehensive documentation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the unified report service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'unified_report_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        """Test module has docstring"""
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        """Test class has docstring"""
        if 'class UnifiedReportService' in service_file_content:
            idx = service_file_content.find('class UnifiedReportService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
