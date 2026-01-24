"""
Test suite for RTP/RTCP Handling Service.

This service provides RTP/RTCP protocol handling for voice quality
testing including stream quality monitoring and packet simulation.

Components:
- RTP stream quality monitoring
- RTCP feedback processing
- Jitter buffer simulation
- Packet loss injection
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestRTPRTCPServiceExists:
    """Test that RTP/RTCP service exists"""

    @pytest.fixture
    def service_file_content(self):
        """Read the RTP/RTCP service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'rtp_rtcp_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        """Test that rtp_rtcp_service.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'rtp_rtcp_service.py'
        )
        assert os.path.exists(service_file), (
            "rtp_rtcp_service.py should exist"
        )

    def test_service_class_exists(self, service_file_content):
        """Test that RTPRTCPService class exists"""
        assert 'class RTPRTCPService' in service_file_content


class TestRTPStreamQuality:
    """Test RTP stream quality monitoring"""

    @pytest.fixture
    def service_class(self):
        """Get the RTPRTCPService class"""
        from services.rtp_rtcp_service import RTPRTCPService
        return RTPRTCPService

    def test_has_create_stream_method(self, service_class):
        """Test create_stream method exists"""
        assert hasattr(service_class, 'create_stream')
        assert callable(getattr(service_class, 'create_stream'))

    def test_has_get_stream_stats_method(self, service_class):
        """Test get_stream_stats method exists"""
        assert hasattr(service_class, 'get_stream_stats')
        assert callable(getattr(service_class, 'get_stream_stats'))

    def test_has_measure_jitter_method(self, service_class):
        """Test measure_jitter method exists"""
        assert hasattr(service_class, 'measure_jitter')
        assert callable(getattr(service_class, 'measure_jitter'))

    def test_has_calculate_packet_loss_method(self, service_class):
        """Test calculate_packet_loss method exists"""
        assert hasattr(service_class, 'calculate_packet_loss')
        assert callable(getattr(service_class, 'calculate_packet_loss'))

    def test_has_get_stream_quality_method(self, service_class):
        """Test get_stream_quality method exists"""
        assert hasattr(service_class, 'get_stream_quality')
        assert callable(getattr(service_class, 'get_stream_quality'))


class TestRTCPFeedback:
    """Test RTCP feedback processing"""

    @pytest.fixture
    def service_class(self):
        """Get the RTPRTCPService class"""
        from services.rtp_rtcp_service import RTPRTCPService
        return RTPRTCPService

    @pytest.fixture
    def service_file_content(self):
        """Read the RTP/RTCP service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'rtp_rtcp_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_send_rtcp_report_method(self, service_file_content):
        """Test send_rtcp_report method exists"""
        assert 'def send_rtcp_report(' in service_file_content

    def test_has_process_rtcp_report_method(self, service_class):
        """Test process_rtcp_report method exists"""
        assert hasattr(service_class, 'process_rtcp_report')
        assert callable(getattr(service_class, 'process_rtcp_report'))

    def test_has_get_rtcp_stats_method(self, service_class):
        """Test get_rtcp_stats method exists"""
        assert hasattr(service_class, 'get_rtcp_stats')
        assert callable(getattr(service_class, 'get_rtcp_stats'))

    def test_has_calculate_rtt_method(self, service_file_content):
        """Test calculate_rtt method exists"""
        assert 'def calculate_rtt(' in service_file_content


class TestJitterBuffer:
    """Test jitter buffer simulation"""

    @pytest.fixture
    def service_class(self):
        """Get the RTPRTCPService class"""
        from services.rtp_rtcp_service import RTPRTCPService
        return RTPRTCPService

    def test_has_configure_jitter_buffer_method(self, service_class):
        """Test configure_jitter_buffer method exists"""
        assert hasattr(service_class, 'configure_jitter_buffer')
        assert callable(getattr(service_class, 'configure_jitter_buffer'))

    def test_has_get_buffer_status_method(self, service_class):
        """Test get_buffer_status method exists"""
        assert hasattr(service_class, 'get_buffer_status')
        assert callable(getattr(service_class, 'get_buffer_status'))

    def test_has_simulate_jitter_method(self, service_class):
        """Test simulate_jitter method exists"""
        assert hasattr(service_class, 'simulate_jitter')
        assert callable(getattr(service_class, 'simulate_jitter'))

    def test_has_get_buffer_stats_method(self, service_class):
        """Test get_buffer_stats method exists"""
        assert hasattr(service_class, 'get_buffer_stats')
        assert callable(getattr(service_class, 'get_buffer_stats'))


class TestPacketSimulation:
    """Test packet loss injection"""

    @pytest.fixture
    def service_class(self):
        """Get the RTPRTCPService class"""
        from services.rtp_rtcp_service import RTPRTCPService
        return RTPRTCPService

    def test_has_inject_packet_loss_method(self, service_class):
        """Test inject_packet_loss method exists"""
        assert hasattr(service_class, 'inject_packet_loss')
        assert callable(getattr(service_class, 'inject_packet_loss'))

    def test_has_inject_latency_method(self, service_class):
        """Test inject_latency method exists"""
        assert hasattr(service_class, 'inject_latency')
        assert callable(getattr(service_class, 'inject_latency'))

    def test_has_inject_burst_loss_method(self, service_class):
        """Test inject_burst_loss method exists"""
        assert hasattr(service_class, 'inject_burst_loss')
        assert callable(getattr(service_class, 'inject_burst_loss'))

    def test_has_get_injection_stats_method(self, service_class):
        """Test get_injection_stats method exists"""
        assert hasattr(service_class, 'get_injection_stats')
        assert callable(getattr(service_class, 'get_injection_stats'))


class TestTypeHints:
    """Test type hints for RTP/RTCP service"""

    @pytest.fixture
    def service_file_content(self):
        """Read the RTP/RTCP service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'rtp_rtcp_service.py'
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
        """Read the RTP/RTCP service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'rtp_rtcp_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        """Test module has docstring"""
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        """Test class has docstring"""
        if 'class RTPRTCPService' in service_file_content:
            idx = service_file_content.find('class RTPRTCPService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
