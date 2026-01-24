"""
Test suite for Barge-in and Interruption Service.

This service handles barge-in detection and interruption
for testing voice AI systems.

Components:
- User interruption during TTS
- Early endpoint detection
- Barge-in latency measurement
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestBargeInServiceExists:
    """Test that barge-in service exists"""

    @pytest.fixture
    def service_file_content(self):
        """Read the barge-in service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'barge_in_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        """Test that barge_in_service.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'barge_in_service.py'
        )
        assert os.path.exists(service_file), (
            "barge_in_service.py should exist"
        )

    def test_service_class_exists(self, service_file_content):
        """Test that BargeInService class exists"""
        assert 'class BargeInService' in service_file_content


class TestUserInterruption:
    """Test user interruption during TTS"""

    @pytest.fixture
    def service_file_content(self):
        """Read the barge-in service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'barge_in_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_detect_interruption_method(self, service_file_content):
        """Test detect_interruption method exists"""
        assert 'def detect_interruption(' in service_file_content

    def test_has_handle_interruption_method(self, service_file_content):
        """Test handle_interruption method exists"""
        assert 'def handle_interruption(' in service_file_content

    def test_has_stop_tts_method(self, service_file_content):
        """Test stop_tts method exists"""
        assert 'def stop_tts(' in service_file_content


class TestEarlyEndpointDetection:
    """Test early endpoint detection"""

    @pytest.fixture
    def service_file_content(self):
        """Read the barge-in service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'barge_in_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_detect_endpoint_method(self, service_file_content):
        """Test detect_endpoint method exists"""
        assert 'def detect_endpoint(' in service_file_content

    def test_has_set_endpoint_sensitivity_method(self, service_file_content):
        """Test set_endpoint_sensitivity method exists"""
        assert 'def set_endpoint_sensitivity(' in service_file_content

    def test_has_get_endpoint_config_method(self, service_file_content):
        """Test get_endpoint_config method exists"""
        assert 'def get_endpoint_config(' in service_file_content


class TestBargeInLatency:
    """Test barge-in latency measurement"""

    @pytest.fixture
    def service_file_content(self):
        """Read the barge-in service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'barge_in_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_measure_barge_in_latency_method(self, service_file_content):
        """Test measure_barge_in_latency method exists"""
        assert 'def measure_barge_in_latency(' in service_file_content

    def test_has_get_latency_stats_method(self, service_file_content):
        """Test get_latency_stats method exists"""
        assert 'def get_latency_stats(' in service_file_content

    def test_has_set_latency_threshold_method(self, service_file_content):
        """Test set_latency_threshold method exists"""
        assert 'def set_latency_threshold(' in service_file_content


class TestBargeInConfiguration:
    """Test barge-in configuration"""

    @pytest.fixture
    def service_file_content(self):
        """Read the barge-in service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'barge_in_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_enable_barge_in_method(self, service_file_content):
        """Test enable_barge_in method exists"""
        assert 'def enable_barge_in(' in service_file_content

    def test_has_disable_barge_in_method(self, service_file_content):
        """Test disable_barge_in method exists"""
        assert 'def disable_barge_in(' in service_file_content

    def test_has_get_barge_in_history_method(self, service_file_content):
        """Test get_barge_in_history method exists"""
        assert 'def get_barge_in_history(' in service_file_content


class TestTypeHints:
    """Test type hints for barge-in service"""

    @pytest.fixture
    def service_file_content(self):
        """Read the barge-in service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'barge_in_service.py'
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
        """Read the barge-in service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'barge_in_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        """Test module has docstring"""
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        """Test class has docstring"""
        if 'class BargeInService' in service_file_content:
            idx = service_file_content.find('class BargeInService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
