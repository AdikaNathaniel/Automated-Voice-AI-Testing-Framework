"""
Test suite for Barge-in and Interruption Handling Service.

This service provides barge-in detection and interruption
handling for voice AI testing.

Components:
- Barge-in detection
- Interruption handling
- Speech timing
- Recovery handling
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestBargeInServiceExists:
    """Test that barge-in handling service exists"""

    @pytest.fixture
    def service_file_content(self):
        """Read the barge-in handling service file"""
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


class TestBargeInDetection:
    """Test barge-in detection"""

    @pytest.fixture
    def service_file_content(self):
        """Read the barge-in handling service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'barge_in_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_detect_barge_in_method(self, service_file_content):
        """Test detect_barge_in method exists"""
        assert 'def detect_barge_in(' in service_file_content

    def test_has_set_detection_threshold_method(self, service_file_content):
        """Test set_detection_threshold method exists"""
        assert 'def set_detection_threshold(' in service_file_content

    def test_has_is_barge_in_active_method(self, service_file_content):
        """Test is_barge_in_active method exists"""
        assert 'def is_barge_in_active(' in service_file_content


class TestInterruptionHandling:
    """Test interruption handling"""

    @pytest.fixture
    def service_file_content(self):
        """Read the barge-in handling service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'barge_in_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_handle_interruption_method(self, service_file_content):
        """Test handle_interruption method exists"""
        assert 'def handle_interruption(' in service_file_content

    def test_has_stop_playback_method(self, service_file_content):
        """Test stop_playback method exists"""
        assert 'def stop_playback(' in service_file_content

    def test_has_get_interruption_point_method(self, service_file_content):
        """Test get_interruption_point method exists"""
        assert 'def get_interruption_point(' in service_file_content


class TestSpeechTiming:
    """Test speech timing management"""

    @pytest.fixture
    def service_file_content(self):
        """Read the barge-in handling service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'barge_in_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_start_utterance_method(self, service_file_content):
        """Test start_utterance method exists"""
        assert 'def start_utterance(' in service_file_content

    def test_has_end_utterance_method(self, service_file_content):
        """Test end_utterance method exists"""
        assert 'def end_utterance(' in service_file_content

    def test_has_get_overlap_duration_method(self, service_file_content):
        """Test get_overlap_duration method exists"""
        assert 'def get_overlap_duration(' in service_file_content


class TestEnergyDetection:
    """Test energy-based detection"""

    @pytest.fixture
    def service_file_content(self):
        """Read the barge-in handling service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'barge_in_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_energy_method(self, service_file_content):
        """Test calculate_energy method exists"""
        assert 'def calculate_energy(' in service_file_content

    def test_has_set_energy_threshold_method(self, service_file_content):
        """Test set_energy_threshold method exists"""
        assert 'def set_energy_threshold(' in service_file_content


class TestRecoveryHandling:
    """Test recovery handling"""

    @pytest.fixture
    def service_file_content(self):
        """Read the barge-in handling service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'barge_in_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_resume_after_barge_in_method(self, service_file_content):
        """Test resume_after_barge_in method exists"""
        assert 'def resume_after_barge_in(' in service_file_content

    def test_has_get_recovery_point_method(self, service_file_content):
        """Test get_recovery_point method exists"""
        assert 'def get_recovery_point(' in service_file_content

    def test_has_get_barge_in_history_method(self, service_file_content):
        """Test get_barge_in_history method exists"""
        assert 'def get_barge_in_history(' in service_file_content


class TestTypeHints:
    """Test type hints for barge-in service"""

    @pytest.fixture
    def service_file_content(self):
        """Read the barge-in handling service file"""
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
        """Read the barge-in handling service file"""
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
