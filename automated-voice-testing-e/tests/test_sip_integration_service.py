"""
Test suite for SIP Integration Service.

This service provides SIP protocol support for voice AI testing
including client/server implementation and authentication.

Components:
- SIP client for test calls
- SIP server for inbound calls
- SIP trunk integration
- SIP authentication
- SRTP encryption
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestSIPIntegrationServiceExists:
    """Test that SIP integration service exists"""

    @pytest.fixture
    def service_file_content(self):
        """Read the SIP integration service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'sip_integration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        """Test that sip_integration_service.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'sip_integration_service.py'
        )
        assert os.path.exists(service_file), (
            "sip_integration_service.py should exist"
        )

    def test_service_class_exists(self, service_file_content):
        """Test that SIPIntegrationService class exists"""
        assert 'class SIPIntegrationService' in service_file_content


class TestSIPClient:
    """Test SIP client implementation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the SIP integration service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'sip_integration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_create_client_method(self, service_file_content):
        """Test create_client method exists"""
        assert 'def create_client(' in service_file_content

    def test_has_make_call_method(self, service_file_content):
        """Test make_call method exists"""
        assert 'def make_call(' in service_file_content

    def test_has_end_call_method(self, service_file_content):
        """Test end_call method exists"""
        assert 'def end_call(' in service_file_content

    def test_has_get_call_status_method(self, service_file_content):
        """Test get_call_status method exists"""
        assert 'def get_call_status(' in service_file_content


class TestSIPServer:
    """Test SIP server for inbound calls"""

    @pytest.fixture
    def service_file_content(self):
        """Read the SIP integration service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'sip_integration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_start_server_method(self, service_file_content):
        """Test start_server method exists"""
        assert 'def start_server(' in service_file_content

    def test_has_stop_server_method(self, service_file_content):
        """Test stop_server method exists"""
        assert 'def stop_server(' in service_file_content

    def test_has_handle_inbound_call_method(self, service_file_content):
        """Test handle_inbound_call method exists"""
        assert 'def handle_inbound_call(' in service_file_content


class TestSIPTrunk:
    """Test SIP trunk integration"""

    @pytest.fixture
    def service_file_content(self):
        """Read the SIP integration service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'sip_integration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_configure_trunk_method(self, service_file_content):
        """Test configure_trunk method exists"""
        assert 'def configure_trunk(' in service_file_content

    def test_has_test_trunk_method(self, service_file_content):
        """Test test_trunk method exists"""
        assert 'def test_trunk(' in service_file_content

    def test_has_get_trunk_status_method(self, service_file_content):
        """Test get_trunk_status method exists"""
        assert 'def get_trunk_status(' in service_file_content


class TestSIPAuthentication:
    """Test SIP authentication"""

    @pytest.fixture
    def service_file_content(self):
        """Read the SIP integration service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'sip_integration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_set_credentials_method(self, service_file_content):
        """Test set_credentials method exists"""
        assert 'def set_credentials(' in service_file_content

    def test_has_authenticate_digest_method(self, service_file_content):
        """Test authenticate_digest method exists"""
        assert 'def authenticate_digest(' in service_file_content

    def test_has_configure_tls_method(self, service_file_content):
        """Test configure_tls method exists"""
        assert 'def configure_tls(' in service_file_content


class TestSRTPEncryption:
    """Test SRTP encryption"""

    @pytest.fixture
    def service_file_content(self):
        """Read the SIP integration service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'sip_integration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_enable_srtp_method(self, service_file_content):
        """Test enable_srtp method exists"""
        assert 'def enable_srtp(' in service_file_content

    def test_has_set_srtp_keys_method(self, service_file_content):
        """Test set_srtp_keys method exists"""
        assert 'def set_srtp_keys(' in service_file_content

    def test_has_get_encryption_status_method(self, service_file_content):
        """Test get_encryption_status method exists"""
        assert 'def get_encryption_status(' in service_file_content


class TestTypeHints:
    """Test type hints for SIP integration service"""

    @pytest.fixture
    def service_file_content(self):
        """Read the SIP integration service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'sip_integration_service.py'
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
        """Read the SIP integration service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'sip_integration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        """Test module has docstring"""
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        """Test class has docstring"""
        if 'class SIPIntegrationService' in service_file_content:
            idx = service_file_content.find('class SIPIntegrationService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
