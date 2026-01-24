"""
Test suite for RealTimeMetricsService class-based implementation.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestRealTimeMetricsServiceClassExists:
    """Test that class-based service exists"""

    def test_service_file_exists(self):
        """Test that real_time_metrics_service.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'real_time_metrics_service.py'
        )
        assert os.path.exists(service_file)

    def test_class_exists(self):
        """Test that RealTimeMetricsService class exists"""
        from services.real_time_metrics_service import RealTimeMetricsService
        assert RealTimeMetricsService is not None

    def test_class_is_importable(self):
        """Test class can be instantiated"""
        from services.real_time_metrics_service import RealTimeMetricsService
        service = RealTimeMetricsService()
        assert service is not None


class TestRealTimeMetricsServiceMethods:
    """Test that class has required methods"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        from services.real_time_metrics_service import RealTimeMetricsService
        return RealTimeMetricsService()

    def test_has_get_real_time_metrics_method(self, service):
        """Test get_real_time_metrics method exists"""
        assert hasattr(service, 'get_real_time_metrics')
        assert callable(getattr(service, 'get_real_time_metrics'))


class TestBackwardCompatibility:
    """Test that function-based API still works"""

    def test_get_real_time_metrics_function_exists(self):
        """Test get_real_time_metrics function still exists"""
        from services.real_time_metrics_service import get_real_time_metrics
        assert get_real_time_metrics is not None
        assert callable(get_real_time_metrics)


class TestDocumentation:
    """Test documentation quality"""

    @pytest.fixture
    def service_file_content(self):
        """Read the service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'real_time_metrics_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_class_docstring(self, service_file_content):
        """Test class has docstring"""
        assert 'class RealTimeMetricsService' in service_file_content
        idx = service_file_content.find('class RealTimeMetricsService')
        class_section = service_file_content[idx:idx+500]
        assert '"""' in class_section
