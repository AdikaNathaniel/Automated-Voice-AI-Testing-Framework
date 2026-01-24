"""
Unit tests for audio normalization feature.

Tests the peak normalization function in audio_utils.py.
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock
import io


class TestNormalizeAudioPeak:
    """Tests for normalize_audio_peak function."""

    def test_normalize_audio_peak_empty_bytes_raises(self):
        """Empty audio bytes should raise ValueError."""
        from services.audio_utils import normalize_audio_peak

        with pytest.raises(ValueError) as exc_info:
            normalize_audio_peak(b'')

        assert "empty" in str(exc_info.value).lower()

    def test_normalize_audio_peak_scales_correctly(self):
        """Verify audio is scaled to target peak level."""
        from services.audio_utils import normalize_audio_peak

        # Create a simple test audio signal
        sample_rate = 16000
        duration = 0.5  # 0.5 seconds
        t = np.linspace(0, duration, int(sample_rate * duration))
        # Create a quiet sine wave (peak at 0.3)
        audio_data = (0.3 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)

        # Convert to WAV bytes
        import soundfile as sf
        buffer = io.BytesIO()
        sf.write(buffer, audio_data, sample_rate, format='WAV', subtype='PCM_16')
        buffer.seek(0)
        audio_bytes = buffer.read()

        # Normalize to -3 dB (peak amplitude ~0.708)
        result = normalize_audio_peak(audio_bytes, target_db=-3.0)

        # Read the normalized audio
        result_buffer = io.BytesIO(result)
        normalized_data, _ = sf.read(result_buffer, dtype='float32')

        # Check peak is approximately at target level
        actual_peak = np.max(np.abs(normalized_data))
        expected_peak = 10 ** (-3.0 / 20)  # ~0.708

        assert abs(actual_peak - expected_peak) < 0.05, \
            f"Expected peak ~{expected_peak:.3f}, got {actual_peak:.3f}"

    def test_normalize_audio_peak_silent_audio(self):
        """Silent audio (all zeros) should return original bytes."""
        from services.audio_utils import normalize_audio_peak

        # Create silent audio
        sample_rate = 16000
        silence = np.zeros(sample_rate, dtype=np.float32)

        import soundfile as sf
        buffer = io.BytesIO()
        sf.write(buffer, silence, sample_rate, format='WAV', subtype='PCM_16')
        buffer.seek(0)
        audio_bytes = buffer.read()

        # Should return original (can't normalize silence)
        result = normalize_audio_peak(audio_bytes, target_db=-3.0)

        # Result should be the original audio bytes
        assert result == audio_bytes

    def test_normalize_audio_peak_to_zero_db(self):
        """Normalize to 0 dB (full scale)."""
        from services.audio_utils import normalize_audio_peak

        # Create a quiet test audio
        sample_rate = 16000
        duration = 0.5
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)

        import soundfile as sf
        buffer = io.BytesIO()
        sf.write(buffer, audio_data, sample_rate, format='WAV', subtype='PCM_16')
        buffer.seek(0)
        audio_bytes = buffer.read()

        # Normalize to 0 dB (peak amplitude = 1.0)
        result = normalize_audio_peak(audio_bytes, target_db=0.0)

        # Read normalized audio
        result_buffer = io.BytesIO(result)
        normalized_data, _ = sf.read(result_buffer, dtype='float32')

        # Peak should be at 1.0
        actual_peak = np.max(np.abs(normalized_data))
        assert abs(actual_peak - 1.0) < 0.05, \
            f"Expected peak ~1.0, got {actual_peak:.3f}"

    def test_normalize_audio_peak_negative_target(self):
        """Normalize to negative dB level."""
        from services.audio_utils import normalize_audio_peak

        # Create a loud test audio (peak at 0.9)
        sample_rate = 16000
        duration = 0.5
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = (0.9 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)

        import soundfile as sf
        buffer = io.BytesIO()
        sf.write(buffer, audio_data, sample_rate, format='WAV', subtype='PCM_16')
        buffer.seek(0)
        audio_bytes = buffer.read()

        # Normalize to -6 dB (peak amplitude ~0.5)
        result = normalize_audio_peak(audio_bytes, target_db=-6.0)

        # Read normalized audio
        result_buffer = io.BytesIO(result)
        normalized_data, _ = sf.read(result_buffer, dtype='float32')

        # Peak should be at ~0.5
        actual_peak = np.max(np.abs(normalized_data))
        expected_peak = 10 ** (-6.0 / 20)  # ~0.501

        assert abs(actual_peak - expected_peak) < 0.05, \
            f"Expected peak ~{expected_peak:.3f}, got {actual_peak:.3f}"

    def test_audio_utils_class_method(self):
        """Verify AudioUtils class exposes normalize method."""
        from services.audio_utils import AudioUtils

        utils = AudioUtils()
        assert hasattr(utils, 'normalize_audio_peak')
        assert callable(utils.normalize_audio_peak)