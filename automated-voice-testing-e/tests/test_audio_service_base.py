"""
Test suite for Audio Service Base class.

This base class extracts common patterns from audio services including
signal validation, sample rate handling, frame analysis, and calculations.

Components:
- Signal validation and normalization
- Sample rate handling
- Frame-based analysis utilities
- Power and dB calculations
- Severity classification helpers
"""

import pytest
import sys
import os
import numpy as np

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestAudioServiceBaseExists:
    """Test that audio service base exists"""

    def test_service_file_exists(self):
        """Test that audio_service_base.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'audio_service_base.py'
        )
        assert os.path.exists(service_file), (
            "audio_service_base.py should exist"
        )

    def test_base_class_exists(self):
        """Test that AudioServiceBase class exists"""
        from services.audio_service_base import AudioServiceBase
        assert AudioServiceBase is not None


class TestAudioServiceBaseBasic:
    """Test basic base class functionality"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        from services.audio_service_base import AudioServiceBase
        return AudioServiceBase()

    def test_service_initialization(self, service):
        """Test service initializes correctly"""
        assert service is not None

    def test_has_default_sample_rate(self, service):
        """Test service has default sample rate"""
        assert hasattr(service, 'default_sample_rate')
        assert service.default_sample_rate == 16000


class TestSignalValidation:
    """Test signal validation functionality"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        from services.audio_service_base import AudioServiceBase
        return AudioServiceBase()

    def test_validate_signal_method(self, service):
        """Test validate_signal method exists"""
        assert hasattr(service, 'validate_signal')
        assert callable(getattr(service, 'validate_signal'))

    def test_validate_signal_with_none(self, service):
        """Test validate_signal returns False for None"""
        result = service.validate_signal(None)
        assert result is False

    def test_validate_signal_with_empty(self, service):
        """Test validate_signal returns False for empty array"""
        result = service.validate_signal(np.array([]))
        assert result is False

    def test_validate_signal_with_valid(self, service):
        """Test validate_signal returns True for valid signal"""
        signal = np.array([0.1, 0.2, 0.3])
        result = service.validate_signal(signal)
        assert result is True


class TestSignalNormalization:
    """Test signal normalization functionality"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        from services.audio_service_base import AudioServiceBase
        return AudioServiceBase()

    def test_normalize_signal_method(self, service):
        """Test normalize_signal method exists"""
        assert hasattr(service, 'normalize_signal')
        assert callable(getattr(service, 'normalize_signal'))

    def test_normalize_signal_returns_float(self, service):
        """Test normalize_signal converts to float"""
        signal = np.array([1, 2, 3], dtype=np.int16)
        result = service.normalize_signal(signal)
        assert result.dtype in [np.float32, np.float64]


class TestFrameAnalysis:
    """Test frame-based analysis utilities"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        from services.audio_service_base import AudioServiceBase
        return AudioServiceBase()

    def test_frame_signal_method(self, service):
        """Test frame_signal method exists"""
        assert hasattr(service, 'frame_signal')
        assert callable(getattr(service, 'frame_signal'))

    def test_frame_signal_returns_list(self, service):
        """Test frame_signal returns list of frames"""
        signal = np.random.randn(1600)
        frames = service.frame_signal(signal, 400, 160)
        assert isinstance(frames, list)
        assert len(frames) > 0


class TestPowerCalculations:
    """Test power and dB calculations"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        from services.audio_service_base import AudioServiceBase
        return AudioServiceBase()

    def test_calculate_rms_method(self, service):
        """Test calculate_rms method exists"""
        assert hasattr(service, 'calculate_rms')
        assert callable(getattr(service, 'calculate_rms'))

    def test_calculate_rms_returns_float(self, service):
        """Test calculate_rms returns float"""
        signal = np.array([0.1, 0.2, 0.3])
        result = service.calculate_rms(signal)
        assert isinstance(result, float)

    def test_to_decibels_method(self, service):
        """Test to_decibels method exists"""
        assert hasattr(service, 'to_decibels')
        assert callable(getattr(service, 'to_decibels'))

    def test_to_decibels_returns_float(self, service):
        """Test to_decibels returns float"""
        result = service.to_decibels(100.0)
        assert isinstance(result, float)


class TestSeverityClassification:
    """Test severity classification helpers"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        from services.audio_service_base import AudioServiceBase
        return AudioServiceBase()

    def test_has_severity_constants(self, service):
        """Test service has severity constants"""
        assert hasattr(service, 'SEVERITY_NONE')
        assert hasattr(service, 'SEVERITY_LOW')
        assert hasattr(service, 'SEVERITY_MEDIUM')
        assert hasattr(service, 'SEVERITY_HIGH')

    def test_classify_by_thresholds_method(self, service):
        """Test classify_by_thresholds method exists"""
        assert hasattr(service, 'classify_by_thresholds')
        assert callable(getattr(service, 'classify_by_thresholds'))


class TestConfiguration:
    """Test configuration functionality"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        from services.audio_service_base import AudioServiceBase
        return AudioServiceBase()

    def test_get_config_method(self, service):
        """Test get_config method exists"""
        assert hasattr(service, 'get_config')

    def test_config_returns_dict(self, service):
        """Test config returns dictionary"""
        config = service.get_config()
        assert isinstance(config, dict)

    def test_config_has_sample_rate(self, service):
        """Test config has sample_rate"""
        config = service.get_config()
        assert 'default_sample_rate' in config


class TestTypeHints:
    """Test type hints for audio service base"""

    @pytest.fixture
    def service_file_content(self):
        """Read the audio service base file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'audio_service_base.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_imports_typing_modules(self, service_file_content):
        """Test typing modules are imported"""
        assert 'from typing import' in service_file_content

    def test_imports_numpy(self, service_file_content):
        """Test numpy is imported"""
        assert 'import numpy' in service_file_content


class TestDocstrings:
    """Test comprehensive documentation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the audio service base file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'audio_service_base.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        """Test module has docstring"""
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        """Test class has docstring"""
        if 'class AudioServiceBase' in service_file_content:
            idx = service_file_content.find('class AudioServiceBase')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
