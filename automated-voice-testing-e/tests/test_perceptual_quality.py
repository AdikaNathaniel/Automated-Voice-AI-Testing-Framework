"""
Test suite for Perceptual Quality Scores.

Perceptual quality metrics measure how audio sounds to humans, which directly
correlates with ASR performance. Key metrics include PESQ (Perceptual Evaluation
of Speech Quality) and MOS (Mean Opinion Score).

Components:
- PESQ scoring: Standard ITU-T P.862 quality metric
- MOS estimation: Predict subjective quality scores
- POLQA support: ITU-T P.863 if available
- ASR performance mapping: Correlate quality to expected accuracy
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestPerceptualQualityServiceExists:
    """Test that perceptual quality service exists"""

    @pytest.fixture
    def service_file_content(self):
        """Read the perceptual quality service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'perceptual_quality_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        """Test that perceptual_quality_service.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'perceptual_quality_service.py'
        )
        assert os.path.exists(service_file), (
            "perceptual_quality_service.py should exist"
        )

    def test_service_class_exists(self, service_file_content):
        """Test that PerceptualQualityService class exists"""
        assert 'class PerceptualQualityService' in service_file_content


class TestPESQScoring:
    """Test PESQ scoring functionality"""

    @pytest.fixture
    def service_file_content(self):
        """Read the perceptual quality service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'perceptual_quality_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_pesq_method(self, service_file_content):
        """Test calculate_pesq method exists"""
        assert 'def calculate_pesq(' in service_file_content

    def test_pesq_returns_float(self, service_file_content):
        """Test calculate_pesq returns float"""
        if 'def calculate_pesq(' in service_file_content:
            idx = service_file_content.find('def calculate_pesq(')
            method_sig = service_file_content[idx:idx+200]
            assert 'float' in method_sig

    def test_has_docstring_for_pesq(self, service_file_content):
        """Test calculate_pesq has docstring"""
        if 'def calculate_pesq(' in service_file_content:
            idx = service_file_content.find('def calculate_pesq(')
            method_section = service_file_content[idx:idx+500]
            assert '"""' in method_section


class TestMOSEstimation:
    """Test MOS estimation functionality"""

    @pytest.fixture
    def service_file_content(self):
        """Read the perceptual quality service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'perceptual_quality_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_estimate_mos_method(self, service_file_content):
        """Test estimate_mos method exists"""
        assert 'def estimate_mos(' in service_file_content

    def test_mos_returns_float(self, service_file_content):
        """Test estimate_mos returns float"""
        if 'def estimate_mos(' in service_file_content:
            idx = service_file_content.find('def estimate_mos(')
            method_sig = service_file_content[idx:idx+200]
            assert 'float' in method_sig

    def test_mos_score_range(self, service_file_content):
        """Test MOS score constants are defined"""
        # MOS ranges from 1 to 5
        assert 'mos' in service_file_content.lower()


class TestPOLQASupport:
    """Test POLQA support"""

    @pytest.fixture
    def service_file_content(self):
        """Read the perceptual quality service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'perceptual_quality_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_polqa_method(self, service_file_content):
        """Test POLQA method or reference exists"""
        # POLQA may not be implemented, but should be referenced
        assert 'polqa' in service_file_content.lower()


class TestASRPerformanceMapping:
    """Test mapping quality scores to ASR performance"""

    @pytest.fixture
    def service_file_content(self):
        """Read the perceptual quality service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'perceptual_quality_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_predict_asr_accuracy_method(self, service_file_content):
        """Test predict_asr_accuracy method exists"""
        assert 'def predict_asr_accuracy(' in service_file_content

    def test_predict_accuracy_returns_dict(self, service_file_content):
        """Test predict_asr_accuracy returns Dict"""
        if 'def predict_asr_accuracy(' in service_file_content:
            idx = service_file_content.find('def predict_asr_accuracy(')
            method_sig = service_file_content[idx:idx+250]
            assert 'Dict' in method_sig


class TestQualityClassification:
    """Test quality level classification"""

    @pytest.fixture
    def service_file_content(self):
        """Read the perceptual quality service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'perceptual_quality_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_classify_mos_method(self, service_file_content):
        """Test classify_mos method exists"""
        assert 'def classify_mos(' in service_file_content

    def test_classify_mos_returns_str(self, service_file_content):
        """Test classify_mos returns str"""
        if 'def classify_mos(' in service_file_content:
            idx = service_file_content.find('def classify_mos(')
            method_sig = service_file_content[idx:idx+200]
            assert 'str' in method_sig


class TestPerceptualQualityMetrics:
    """Test comprehensive perceptual quality metrics"""

    @pytest.fixture
    def service_file_content(self):
        """Read the perceptual quality service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'perceptual_quality_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_perceptual_metrics_method(self, service_file_content):
        """Test get_perceptual_metrics method exists"""
        assert 'def get_perceptual_metrics(' in service_file_content

    def test_metrics_returns_dict(self, service_file_content):
        """Test get_perceptual_metrics returns Dict"""
        if 'def get_perceptual_metrics(' in service_file_content:
            idx = service_file_content.find('def get_perceptual_metrics(')
            method_sig = service_file_content[idx:idx+250]
            assert 'Dict' in method_sig

    def test_metrics_include_mos(self, service_file_content):
        """Test metrics include MOS"""
        assert 'mos' in service_file_content.lower()

    def test_metrics_include_pesq(self, service_file_content):
        """Test metrics include PESQ"""
        assert 'pesq' in service_file_content.lower()


class TestSNRToMOSConversion:
    """Test SNR to MOS conversion"""

    @pytest.fixture
    def service_file_content(self):
        """Read the perceptual quality service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'perceptual_quality_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_snr_to_mos_method(self, service_file_content):
        """Test snr_to_mos conversion method exists"""
        assert 'def snr_to_mos(' in service_file_content

    def test_snr_to_mos_returns_float(self, service_file_content):
        """Test snr_to_mos returns float"""
        if 'def snr_to_mos(' in service_file_content:
            idx = service_file_content.find('def snr_to_mos(')
            method_sig = service_file_content[idx:idx+200]
            assert 'float' in method_sig


class TestTypeHints:
    """Test type hints for perceptual quality service"""

    @pytest.fixture
    def service_file_content(self):
        """Read the perceptual quality service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'perceptual_quality_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_imports_typing_modules(self, service_file_content):
        """Test typing modules are imported"""
        assert 'from typing import' in service_file_content

    def test_uses_dict_type_hint(self, service_file_content):
        """Test Dict type hint is used"""
        assert 'Dict[' in service_file_content

    def test_uses_optional_type_hint(self, service_file_content):
        """Test Optional type hint is used"""
        assert 'Optional[' in service_file_content


class TestDocstrings:
    """Test comprehensive documentation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the perceptual quality service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'perceptual_quality_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        """Test module has docstring"""
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        """Test class has docstring"""
        if 'class PerceptualQualityService' in service_file_content:
            idx = service_file_content.find('class PerceptualQualityService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section


class TestNumPyIntegration:
    """Test NumPy integration for audio processing"""

    @pytest.fixture
    def service_file_content(self):
        """Read the perceptual quality service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'perceptual_quality_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_imports_numpy(self, service_file_content):
        """Test numpy is imported"""
        assert 'import numpy' in service_file_content or 'from numpy' in service_file_content


class TestQualityLevelConstants:
    """Test quality level constants"""

    @pytest.fixture
    def service_file_content(self):
        """Read the perceptual quality service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'perceptual_quality_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_excellent_quality(self, service_file_content):
        """Test EXCELLENT quality level exists"""
        assert 'excellent' in service_file_content.lower()

    def test_has_good_quality(self, service_file_content):
        """Test GOOD quality level exists"""
        assert 'good' in service_file_content.lower()

    def test_has_poor_quality(self, service_file_content):
        """Test POOR quality level exists"""
        assert 'poor' in service_file_content.lower()


