"""
Test suite for Accent Robustness Metrics Service.

This service provides accent robustness metrics for voice AI testing.

Components:
- WER by accent
- Intent accuracy by accent
- Accent detection accuracy
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestAccentRobustnessServiceExists:
    """Test that accent robustness service exists"""

    @pytest.fixture
    def service_file_content(self):
        """Read the accent robustness service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'accent_robustness_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        """Test that accent_robustness_service.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'accent_robustness_service.py'
        )
        assert os.path.exists(service_file), (
            "accent_robustness_service.py should exist"
        )

    def test_service_class_exists(self, service_file_content):
        """Test that AccentRobustnessService class exists"""
        assert 'class AccentRobustnessService' in service_file_content


class TestWERByAccent:
    """Test WER by accent metrics"""

    @pytest.fixture
    def service_file_content(self):
        """Read the accent robustness service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'accent_robustness_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_wer_by_accent_method(self, service_file_content):
        """Test calculate_wer_by_accent method exists"""
        assert 'def calculate_wer_by_accent(' in service_file_content

    def test_has_get_wer_report_method(self, service_file_content):
        """Test get_wer_report method exists"""
        assert 'def get_wer_report(' in service_file_content

    def test_has_compare_wer_across_accents_method(self, service_file_content):
        """Test compare_wer_across_accents method exists"""
        assert 'def compare_wer_across_accents(' in service_file_content


class TestIntentAccuracyByAccent:
    """Test intent accuracy by accent metrics"""

    @pytest.fixture
    def service_file_content(self):
        """Read the accent robustness service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'accent_robustness_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_intent_accuracy_method(self, service_file_content):
        """Test calculate_intent_accuracy method exists"""
        assert 'def calculate_intent_accuracy(' in service_file_content

    def test_has_get_intent_accuracy_report_method(self, service_file_content):
        """Test get_intent_accuracy_report method exists"""
        assert 'def get_intent_accuracy_report(' in service_file_content

    def test_has_compare_intent_accuracy_method(self, service_file_content):
        """Test compare_intent_accuracy method exists"""
        assert 'def compare_intent_accuracy(' in service_file_content


class TestAccentDetectionAccuracy:
    """Test accent detection accuracy metrics"""

    @pytest.fixture
    def service_file_content(self):
        """Read the accent robustness service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'accent_robustness_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_detect_accent_method(self, service_file_content):
        """Test detect_accent method exists"""
        assert 'def detect_accent(' in service_file_content

    def test_has_get_detection_accuracy_method(self, service_file_content):
        """Test get_detection_accuracy method exists"""
        assert 'def get_detection_accuracy(' in service_file_content

    def test_has_get_confusion_matrix_method(self, service_file_content):
        """Test get_confusion_matrix method exists"""
        assert 'def get_confusion_matrix(' in service_file_content


class TestRobustnessConfiguration:
    """Test robustness configuration"""

    @pytest.fixture
    def service_file_content(self):
        """Read the accent robustness service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'accent_robustness_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_robustness_config_method(self, service_file_content):
        """Test get_robustness_config method exists"""
        assert 'def get_robustness_config(' in service_file_content

    def test_has_set_baseline_threshold_method(self, service_file_content):
        """Test set_baseline_threshold method exists"""
        assert 'def set_baseline_threshold(' in service_file_content

    def test_has_get_robustness_summary_method(self, service_file_content):
        """Test get_robustness_summary method exists"""
        assert 'def get_robustness_summary(' in service_file_content


class TestTypeHints:
    """Test type hints for accent robustness service"""

    @pytest.fixture
    def service_file_content(self):
        """Read the accent robustness service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'accent_robustness_service.py'
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
        """Read the accent robustness service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'accent_robustness_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        """Test module has docstring"""
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        """Test class has docstring"""
        if 'class AccentRobustnessService' in service_file_content:
            idx = service_file_content.find('class AccentRobustnessService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section

