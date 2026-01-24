"""
Test suite for Resource Utilization Monitoring Service.

This service provides resource monitoring capabilities for
tracking CPU, memory, network, and disk usage.

Components:
- CPU utilization monitoring
- Memory consumption tracking
- Network I/O monitoring
- Disk I/O monitoring
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestResourceUtilizationServiceExists:
    """Test that resource utilization service exists"""

    @pytest.fixture
    def service_file_content(self):
        """Read the resource utilization service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'resource_utilization_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        """Test that resource_utilization_service.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'resource_utilization_service.py'
        )
        assert os.path.exists(service_file), (
            "resource_utilization_service.py should exist"
        )

    def test_service_class_exists(self, service_file_content):
        """Test that ResourceUtilizationService class exists"""
        assert 'class ResourceUtilizationService' in service_file_content


class TestCPUUtilization:
    """Test CPU utilization monitoring"""

    @pytest.fixture
    def service_file_content(self):
        """Read the resource utilization service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'resource_utilization_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_cpu_usage_method(self, service_file_content):
        """Test get_cpu_usage method exists"""
        assert 'def get_cpu_usage(' in service_file_content

    def test_has_get_cpu_per_service_method(self, service_file_content):
        """Test get_cpu_per_service method exists"""
        assert 'def get_cpu_per_service(' in service_file_content

    def test_has_record_cpu_sample_method(self, service_file_content):
        """Test record_cpu_sample method exists"""
        assert 'def record_cpu_sample(' in service_file_content

    def test_has_get_cpu_history_method(self, service_file_content):
        """Test get_cpu_history method exists"""
        assert 'def get_cpu_history(' in service_file_content


class TestMemoryConsumption:
    """Test memory consumption tracking"""

    @pytest.fixture
    def service_file_content(self):
        """Read the resource utilization service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'resource_utilization_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_memory_usage_method(self, service_file_content):
        """Test get_memory_usage method exists"""
        assert 'def get_memory_usage(' in service_file_content

    def test_has_get_memory_per_service_method(self, service_file_content):
        """Test get_memory_per_service method exists"""
        assert 'def get_memory_per_service(' in service_file_content

    def test_has_record_memory_sample_method(self, service_file_content):
        """Test record_memory_sample method exists"""
        assert 'def record_memory_sample(' in service_file_content

    def test_has_get_memory_history_method(self, service_file_content):
        """Test get_memory_history method exists"""
        assert 'def get_memory_history(' in service_file_content


class TestNetworkIO:
    """Test network I/O monitoring"""

    @pytest.fixture
    def service_file_content(self):
        """Read the resource utilization service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'resource_utilization_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_network_io_method(self, service_file_content):
        """Test get_network_io method exists"""
        assert 'def get_network_io(' in service_file_content

    def test_has_record_network_sample_method(self, service_file_content):
        """Test record_network_sample method exists"""
        assert 'def record_network_sample(' in service_file_content

    def test_has_get_network_throughput_method(self, service_file_content):
        """Test get_network_throughput method exists"""
        assert 'def get_network_throughput(' in service_file_content


class TestDiskIO:
    """Test disk I/O monitoring"""

    @pytest.fixture
    def service_file_content(self):
        """Read the resource utilization service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'resource_utilization_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_disk_io_method(self, service_file_content):
        """Test get_disk_io method exists"""
        assert 'def get_disk_io(' in service_file_content

    def test_has_record_disk_sample_method(self, service_file_content):
        """Test record_disk_sample method exists"""
        assert 'def record_disk_sample(' in service_file_content

    def test_has_get_disk_usage_method(self, service_file_content):
        """Test get_disk_usage method exists"""
        assert 'def get_disk_usage(' in service_file_content


class TestResourceReporting:
    """Test resource utilization reporting"""

    @pytest.fixture
    def service_file_content(self):
        """Read the resource utilization service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'resource_utilization_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_generate_report_method(self, service_file_content):
        """Test generate_report method exists"""
        assert 'def generate_report(' in service_file_content

    def test_has_get_resource_summary_method(self, service_file_content):
        """Test get_resource_summary method exists"""
        assert 'def get_resource_summary(' in service_file_content


class TestTypeHints:
    """Test type hints for resource utilization service"""

    @pytest.fixture
    def service_file_content(self):
        """Read the resource utilization service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'resource_utilization_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_imports_typing_modules(self, service_file_content):
        """Test typing modules are imported"""
        assert 'from typing import' in service_file_content

    def test_uses_dict_type_hint(self, service_file_content):
        """Test Dict type hint is used"""
        assert 'Dict[' in service_file_content

    def test_uses_list_type_hint(self, service_file_content):
        """Test List type hint is used"""
        assert 'List[' in service_file_content


class TestDocstrings:
    """Test comprehensive documentation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the resource utilization service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'resource_utilization_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        """Test module has docstring"""
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        """Test class has docstring"""
        if 'class ResourceUtilizationService' in service_file_content:
            idx = service_file_content.find('class ResourceUtilizationService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
