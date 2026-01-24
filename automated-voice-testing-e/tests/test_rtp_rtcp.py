"""
Test suite for RTP/RTCP Handling Service.

This service provides RTP (Real-time Transport Protocol) and
RTCP (RTP Control Protocol) handling for voice testing.

Components:
- RTP packet handling
- RTCP statistics
- Jitter buffer management
- Packet loss detection
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


class TestRTPPacketHandling:
    """Test RTP packet handling"""

    @pytest.fixture
    def service_file_content(self):
        """Read the RTP/RTCP service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'rtp_rtcp_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_create_rtp_session_method(self, service_file_content):
        """Test create_rtp_session method exists"""
        assert 'def create_rtp_session(' in service_file_content

    def test_has_send_rtp_packet_method(self, service_file_content):
        """Test send_rtp_packet method exists"""
        assert 'def send_rtp_packet(' in service_file_content

    def test_has_receive_rtp_packet_method(self, service_file_content):
        """Test receive_rtp_packet method exists"""
        assert 'def receive_rtp_packet(' in service_file_content

    def test_has_close_rtp_session_method(self, service_file_content):
        """Test close_rtp_session method exists"""
        assert 'def close_rtp_session(' in service_file_content


class TestRTCPStatistics:
    """Test RTCP statistics handling"""

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

    def test_has_receive_rtcp_report_method(self, service_file_content):
        """Test receive_rtcp_report method exists"""
        assert 'def receive_rtcp_report(' in service_file_content

    def test_has_get_rtcp_statistics_method(self, service_file_content):
        """Test get_rtcp_statistics method exists"""
        assert 'def get_rtcp_statistics(' in service_file_content

    def test_has_calculate_rtt_method(self, service_file_content):
        """Test calculate_rtt method exists"""
        assert 'def calculate_rtt(' in service_file_content


class TestJitterBuffer:
    """Test jitter buffer management"""

    @pytest.fixture
    def service_file_content(self):
        """Read the RTP/RTCP service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'rtp_rtcp_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_configure_jitter_buffer_method(self, service_file_content):
        """Test configure_jitter_buffer method exists"""
        assert 'def configure_jitter_buffer(' in service_file_content

    def test_has_get_jitter_buffer_stats_method(self, service_file_content):
        """Test get_jitter_buffer_stats method exists"""
        assert 'def get_jitter_buffer_stats(' in service_file_content

    def test_has_calculate_jitter_method(self, service_file_content):
        """Test calculate_jitter method exists"""
        assert 'def calculate_jitter(' in service_file_content


class TestPacketLoss:
    """Test packet loss detection"""

    @pytest.fixture
    def service_file_content(self):
        """Read the RTP/RTCP service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'rtp_rtcp_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_detect_packet_loss_method(self, service_file_content):
        """Test detect_packet_loss method exists"""
        assert 'def detect_packet_loss(' in service_file_content

    def test_has_get_packet_loss_rate_method(self, service_file_content):
        """Test get_packet_loss_rate method exists"""
        assert 'def get_packet_loss_rate(' in service_file_content

    def test_has_get_sequence_gaps_method(self, service_file_content):
        """Test get_sequence_gaps method exists"""
        assert 'def get_sequence_gaps(' in service_file_content


class TestSessionManagement:
    """Test session management"""

    @pytest.fixture
    def service_file_content(self):
        """Read the RTP/RTCP service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'rtp_rtcp_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_session_info_method(self, service_file_content):
        """Test get_session_info method exists"""
        assert 'def get_session_info(' in service_file_content

    def test_has_get_all_sessions_method(self, service_file_content):
        """Test get_all_sessions method exists"""
        assert 'def get_all_sessions(' in service_file_content


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
