"""
Test suite for WebRTC Integration Service.

This service provides WebRTC integration for browser-based
voice AI testing.

Components:
- Peer connection management
- STUN/TURN server integration
- Codec negotiation
- Media stream handling
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestWebRTCIntegrationServiceExists:
    """Test that WebRTC integration service exists"""

    @pytest.fixture
    def service_file_content(self):
        """Read the WebRTC integration service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'webrtc_integration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        """Test that webrtc_integration_service.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'webrtc_integration_service.py'
        )
        assert os.path.exists(service_file), (
            "webrtc_integration_service.py should exist"
        )

    def test_service_class_exists(self, service_file_content):
        """Test that WebRTCIntegrationService class exists"""
        assert 'class WebRTCIntegrationService' in service_file_content


class TestPeerConnection:
    """Test peer connection management"""

    @pytest.fixture
    def service_file_content(self):
        """Read the WebRTC integration service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'webrtc_integration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_create_peer_connection_method(self, service_file_content):
        """Test create_peer_connection method exists"""
        assert 'def create_peer_connection(' in service_file_content

    def test_has_close_peer_connection_method(self, service_file_content):
        """Test close_peer_connection method exists"""
        assert 'def close_peer_connection(' in service_file_content

    def test_has_get_connection_state_method(self, service_file_content):
        """Test get_connection_state method exists"""
        assert 'def get_connection_state(' in service_file_content


class TestSTUNTURN:
    """Test STUN/TURN server integration"""

    @pytest.fixture
    def service_file_content(self):
        """Read the WebRTC integration service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'webrtc_integration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_configure_ice_servers_method(self, service_file_content):
        """Test configure_ice_servers method exists"""
        assert 'def configure_ice_servers(' in service_file_content

    def test_has_add_stun_server_method(self, service_file_content):
        """Test add_stun_server method exists"""
        assert 'def add_stun_server(' in service_file_content

    def test_has_add_turn_server_method(self, service_file_content):
        """Test add_turn_server method exists"""
        assert 'def add_turn_server(' in service_file_content

    def test_has_test_ice_connectivity_method(self, service_file_content):
        """Test test_ice_connectivity method exists"""
        assert 'def test_ice_connectivity(' in service_file_content


class TestCodecNegotiation:
    """Test codec negotiation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the WebRTC integration service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'webrtc_integration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_supported_codecs_method(self, service_file_content):
        """Test get_supported_codecs method exists"""
        assert 'def get_supported_codecs(' in service_file_content

    def test_has_set_preferred_codecs_method(self, service_file_content):
        """Test set_preferred_codecs method exists"""
        assert 'def set_preferred_codecs(' in service_file_content

    def test_has_test_codec_compatibility_method(self, service_file_content):
        """Test test_codec_compatibility method exists"""
        assert 'def test_codec_compatibility(' in service_file_content


class TestMediaStreams:
    """Test media stream handling"""

    @pytest.fixture
    def service_file_content(self):
        """Read the WebRTC integration service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'webrtc_integration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_add_audio_track_method(self, service_file_content):
        """Test add_audio_track method exists"""
        assert 'def add_audio_track(' in service_file_content

    def test_has_get_remote_streams_method(self, service_file_content):
        """Test get_remote_streams method exists"""
        assert 'def get_remote_streams(' in service_file_content

    def test_has_get_connection_stats_method(self, service_file_content):
        """Test get_connection_stats method exists"""
        assert 'def get_connection_stats(' in service_file_content


class TestSignaling:
    """Test signaling functionality"""

    @pytest.fixture
    def service_file_content(self):
        """Read the WebRTC integration service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'webrtc_integration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_create_offer_method(self, service_file_content):
        """Test create_offer method exists"""
        assert 'def create_offer(' in service_file_content

    def test_has_create_answer_method(self, service_file_content):
        """Test create_answer method exists"""
        assert 'def create_answer(' in service_file_content


class TestTypeHints:
    """Test type hints for WebRTC integration service"""

    @pytest.fixture
    def service_file_content(self):
        """Read the WebRTC integration service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'webrtc_integration_service.py'
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
        """Read the WebRTC integration service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'webrtc_integration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        """Test module has docstring"""
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        """Test class has docstring"""
        if 'class WebRTCIntegrationService' in service_file_content:
            idx = service_file_content.find('class WebRTCIntegrationService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section

