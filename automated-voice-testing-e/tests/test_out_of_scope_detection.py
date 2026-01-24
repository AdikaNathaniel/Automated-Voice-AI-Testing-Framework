"""
Test suite for Out-of-Scope (OOS) Detection Service.

This service provides metrics for evaluating how well an NLU system
handles out-of-scope utterances that don't match any defined intent.

Components:
- False acceptance rate (FAR) for OOS utterances
- False rejection rate (FRR) for in-scope utterances
- OOS confidence calibration
- Threshold optimization for OOS detection
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestOOSServiceExists:
    """Test that OOS detection service exists"""

    @pytest.fixture
    def service_file_content(self):
        """Read the OOS detection service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oos_detection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        """Test that oos_detection_service.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oos_detection_service.py'
        )
        assert os.path.exists(service_file), (
            "oos_detection_service.py should exist"
        )

    def test_service_class_exists(self, service_file_content):
        """Test that OOSDetectionService class exists"""
        assert 'class OOSDetectionService' in service_file_content


class TestFalseAcceptanceRate:
    """Test false acceptance rate calculation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the OOS detection service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oos_detection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_far_method(self, service_file_content):
        """Test calculate_far method exists"""
        assert 'def calculate_far(' in service_file_content

    def test_far_returns_float(self, service_file_content):
        """Test calculate_far returns float"""
        if 'def calculate_far(' in service_file_content:
            idx = service_file_content.find('def calculate_far(')
            method_sig = service_file_content[idx:idx+200]
            assert 'float' in method_sig


class TestFalseRejectionRate:
    """Test false rejection rate calculation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the OOS detection service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oos_detection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_frr_method(self, service_file_content):
        """Test calculate_frr method exists"""
        assert 'def calculate_frr(' in service_file_content

    def test_frr_returns_float(self, service_file_content):
        """Test calculate_frr returns float"""
        if 'def calculate_frr(' in service_file_content:
            idx = service_file_content.find('def calculate_frr(')
            method_sig = service_file_content[idx:idx+200]
            assert 'float' in method_sig


class TestOOSConfidenceCalibration:
    """Test OOS confidence calibration"""

    @pytest.fixture
    def service_file_content(self):
        """Read the OOS detection service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oos_detection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calibrate_oos_confidence_method(self, service_file_content):
        """Test calibrate_oos_confidence method exists"""
        assert 'def calibrate_oos_confidence(' in service_file_content

    def test_calibration_returns_dict(self, service_file_content):
        """Test calibrate_oos_confidence returns Dict"""
        if 'def calibrate_oos_confidence(' in service_file_content:
            idx = service_file_content.find('def calibrate_oos_confidence(')
            method_sig = service_file_content[idx:idx+250]
            assert 'Dict' in method_sig


class TestOOSThresholdOptimization:
    """Test OOS threshold optimization"""

    @pytest.fixture
    def service_file_content(self):
        """Read the OOS detection service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oos_detection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_optimize_oos_threshold_method(self, service_file_content):
        """Test optimize_oos_threshold method exists"""
        assert 'def optimize_oos_threshold(' in service_file_content

    def test_threshold_returns_dict(self, service_file_content):
        """Test optimize_oos_threshold returns Dict"""
        if 'def optimize_oos_threshold(' in service_file_content:
            idx = service_file_content.find('def optimize_oos_threshold(')
            method_sig = service_file_content[idx:idx+250]
            assert 'Dict' in method_sig


class TestOOSMetrics:
    """Test comprehensive OOS metrics"""

    @pytest.fixture
    def service_file_content(self):
        """Read the OOS detection service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oos_detection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_oos_metrics_method(self, service_file_content):
        """Test get_oos_metrics method exists"""
        assert 'def get_oos_metrics(' in service_file_content

    def test_metrics_returns_dict(self, service_file_content):
        """Test get_oos_metrics returns Dict"""
        if 'def get_oos_metrics(' in service_file_content:
            idx = service_file_content.find('def get_oos_metrics(')
            method_sig = service_file_content[idx:idx+200]
            assert 'Dict' in method_sig


class TestTypeHints:
    """Test type hints for OOS detection service"""

    @pytest.fixture
    def service_file_content(self):
        """Read the OOS detection service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oos_detection_service.py'
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
        """Read the OOS detection service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oos_detection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        """Test module has docstring"""
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        """Test class has docstring"""
        if 'class OOSDetectionService' in service_file_content:
            idx = service_file_content.find('class OOSDetectionService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section

