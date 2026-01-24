"""
Audio Service Base - Common patterns for audio services.

This base class extracts common functionality shared across audio services
including signal validation, frame analysis, power calculations, and
severity classification.

Key features:
- Signal validation and normalization
- Sample rate handling
- Frame-based analysis utilities
- Power and dB calculations
- Severity classification helpers

Example:
    >>> from services.audio_service_base import AudioServiceBase
    >>> service = AudioServiceBase()
    >>> if service.validate_signal(audio):
    ...     rms = service.calculate_rms(audio)
    ...     print(f"RMS: {rms:.4f}")
"""

from typing import List, Dict, Any, Optional
import numpy as np


class AudioServiceBase:
    """
    Base class for audio analysis services.

    Provides common functionality for signal processing, validation,
    and metric calculations used across audio services.

    Attributes:
        default_sample_rate: Default audio sample rate in Hz
        SEVERITY_NONE: No severity constant
        SEVERITY_LOW: Low severity constant
        SEVERITY_MEDIUM: Medium severity constant
        SEVERITY_HIGH: High severity constant

    Example:
        >>> service = AudioServiceBase()
        >>> frames = service.frame_signal(audio, 400, 160)
        >>> for frame in frames:
        ...     rms = service.calculate_rms(frame)
    """

    # Severity level constants
    SEVERITY_NONE = 'NONE'
    SEVERITY_LOW = 'LOW'
    SEVERITY_MEDIUM = 'MEDIUM'
    SEVERITY_HIGH = 'HIGH'

    def __init__(self):
        """Initialize the audio service base."""
        self.default_sample_rate = 16000

    # =========================================================================
    # Signal Validation
    # =========================================================================

    def validate_signal(
        self,
        signal: Optional[np.ndarray]
    ) -> bool:
        """
        Validate that signal is usable for analysis.

        Args:
            signal: Audio signal as numpy array

        Returns:
            True if signal is valid, False otherwise

        Example:
            >>> if service.validate_signal(audio):
            ...     process(audio)
        """
        if signal is None:
            return False
        if not isinstance(signal, np.ndarray):
            return False
        if len(signal) == 0:
            return False
        return True

    def normalize_signal(
        self,
        signal: np.ndarray
    ) -> np.ndarray:
        """
        Normalize signal to float format.

        Converts integer signals to floating point range [-1, 1].

        Args:
            signal: Audio signal as numpy array

        Returns:
            Normalized signal as float array

        Example:
            >>> normalized = service.normalize_signal(int16_audio)
        """
        if signal.dtype in [np.float32, np.float64]:
            return signal.astype(np.float64)

        # Convert integer types to float
        if signal.dtype == np.int16:
            return signal.astype(np.float64) / 32768.0
        elif signal.dtype == np.int32:
            return signal.astype(np.float64) / 2147483648.0
        elif signal.dtype == np.uint8:
            return (signal.astype(np.float64) - 128) / 128.0
        else:
            # Try to normalize using dtype max
            try:
                max_val = np.iinfo(signal.dtype).max
                return signal.astype(np.float64) / max_val
            except (ValueError, TypeError):
                return signal.astype(np.float64)

    # =========================================================================
    # Frame-Based Analysis
    # =========================================================================

    def frame_signal(
        self,
        signal: np.ndarray,
        frame_length: int,
        hop_length: int
    ) -> List[np.ndarray]:
        """
        Split signal into overlapping frames.

        Args:
            signal: Audio signal as numpy array
            frame_length: Length of each frame in samples
            hop_length: Hop size between frames in samples

        Returns:
            List of signal frames

        Example:
            >>> frames = service.frame_signal(audio, 400, 160)
            >>> print(f"Number of frames: {len(frames)}")
        """
        frames = []
        for i in range(0, len(signal) - frame_length + 1, hop_length):
            frames.append(signal[i:i + frame_length])
        return frames

    def get_frame_parameters(
        self,
        sample_rate: int,
        frame_ms: float = 25.0,
        hop_ms: float = 10.0
    ) -> Dict[str, int]:
        """
        Calculate frame parameters from milliseconds.

        Args:
            sample_rate: Sample rate in Hz
            frame_ms: Frame length in milliseconds
            hop_ms: Hop length in milliseconds

        Returns:
            Dictionary with frame_length and hop_length

        Example:
            >>> params = service.get_frame_parameters(16000)
            >>> frames = service.frame_signal(audio, **params)
        """
        frame_length = int((frame_ms / 1000.0) * sample_rate)
        hop_length = int((hop_ms / 1000.0) * sample_rate)

        return {
            'frame_length': frame_length,
            'hop_length': hop_length
        }

    # =========================================================================
    # Power and dB Calculations
    # =========================================================================

    def calculate_rms(
        self,
        signal: np.ndarray
    ) -> float:
        """
        Calculate Root Mean Square of signal.

        Args:
            signal: Audio signal as numpy array

        Returns:
            RMS value

        Example:
            >>> rms = service.calculate_rms(audio)
            >>> print(f"RMS: {rms:.4f}")
        """
        if signal is None or len(signal) == 0:
            return 0.0

        return float(np.sqrt(np.mean(signal.astype(np.float64) ** 2)))

    def calculate_power(
        self,
        signal: np.ndarray
    ) -> float:
        """
        Calculate signal power (mean squared).

        Args:
            signal: Audio signal as numpy array

        Returns:
            Signal power value

        Example:
            >>> power = service.calculate_power(audio)
        """
        if signal is None or len(signal) == 0:
            return 0.0

        return float(np.mean(signal.astype(np.float64) ** 2))

    def to_decibels(
        self,
        value: float,
        reference: float = 1.0
    ) -> float:
        """
        Convert value to decibels.

        Args:
            value: Value to convert (power ratio)
            reference: Reference value for dB calculation

        Returns:
            Value in decibels

        Example:
            >>> db = service.to_decibels(0.001)
            >>> print(f"{db:.2f} dB")
        """
        if value <= 0:
            return float('-inf')

        return float(10 * np.log10(value / reference))

    def from_decibels(
        self,
        db: float,
        reference: float = 1.0
    ) -> float:
        """
        Convert decibels to linear value.

        Args:
            db: Value in decibels
            reference: Reference value

        Returns:
            Linear value

        Example:
            >>> linear = service.from_decibels(-20.0)
        """
        return float(reference * (10 ** (db / 10)))

    # =========================================================================
    # Severity Classification
    # =========================================================================

    def classify_by_thresholds(
        self,
        value: float,
        thresholds: Dict[str, float],
        ascending: bool = True
    ) -> str:
        """
        Classify value by thresholds.

        Args:
            value: Value to classify
            thresholds: Dictionary with LOW, MEDIUM, HIGH thresholds
            ascending: If True, higher values = higher severity

        Returns:
            Severity level string

        Example:
            >>> thresholds = {'LOW': 0.01, 'MEDIUM': 0.05, 'HIGH': 0.1}
            >>> severity = service.classify_by_thresholds(0.07, thresholds)
        """
        low = thresholds.get('LOW', 0.0)
        medium = thresholds.get('MEDIUM', 0.0)
        high = thresholds.get('HIGH', 0.0)

        if ascending:
            if value >= high:
                return self.SEVERITY_HIGH
            elif value >= medium:
                return self.SEVERITY_MEDIUM
            elif value >= low:
                return self.SEVERITY_LOW
            else:
                return self.SEVERITY_NONE
        else:
            # Descending: lower values = higher severity
            if value <= high:
                return self.SEVERITY_HIGH
            elif value <= medium:
                return self.SEVERITY_MEDIUM
            elif value <= low:
                return self.SEVERITY_LOW
            else:
                return self.SEVERITY_NONE

    def get_severity_score(
        self,
        severity: str
    ) -> int:
        """
        Get numeric score for severity level.

        Args:
            severity: Severity level string

        Returns:
            Numeric severity score (0-3)

        Example:
            >>> score = service.get_severity_score('MEDIUM')
            >>> print(f"Score: {score}")
        """
        scores = {
            self.SEVERITY_NONE: 0,
            self.SEVERITY_LOW: 1,
            self.SEVERITY_MEDIUM: 2,
            self.SEVERITY_HIGH: 3
        }
        return scores.get(severity, 0)

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def calculate_peak(
        self,
        signal: np.ndarray
    ) -> float:
        """
        Calculate peak amplitude of signal.

        Args:
            signal: Audio signal as numpy array

        Returns:
            Peak amplitude value

        Example:
            >>> peak = service.calculate_peak(audio)
        """
        if signal is None or len(signal) == 0:
            return 0.0

        return float(np.max(np.abs(signal)))

    def calculate_crest_factor(
        self,
        signal: np.ndarray
    ) -> float:
        """
        Calculate crest factor (peak to RMS ratio).

        Args:
            signal: Audio signal as numpy array

        Returns:
            Crest factor value

        Example:
            >>> crest = service.calculate_crest_factor(audio)
        """
        if signal is None or len(signal) == 0:
            return 0.0

        rms = self.calculate_rms(signal)
        peak = self.calculate_peak(signal)

        if rms == 0:
            return 0.0

        return float(peak / rms)

    def estimate_noise_floor(
        self,
        signal: np.ndarray,
        percentile: float = 10.0
    ) -> float:
        """
        Estimate noise floor from signal.

        Uses minimum statistics approach.

        Args:
            signal: Audio signal as numpy array
            percentile: Percentile for noise estimate

        Returns:
            Noise floor estimate

        Example:
            >>> noise = service.estimate_noise_floor(audio)
        """
        if signal is None or len(signal) == 0:
            return 0.0

        sorted_abs = np.sort(np.abs(signal))
        cutoff = int(len(sorted_abs) * percentile / 100)
        if cutoff == 0:
            cutoff = 1

        noise_samples = sorted_abs[:cutoff]
        return float(np.sqrt(np.mean(noise_samples ** 2)))

    # =========================================================================
    # Configuration
    # =========================================================================

    def get_config(self) -> Dict[str, Any]:
        """
        Get audio service base configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_config()
            >>> print(f"Sample rate: {config['default_sample_rate']}")
        """
        return {
            'default_sample_rate': self.default_sample_rate,
            'severity_levels': [
                self.SEVERITY_NONE,
                self.SEVERITY_LOW,
                self.SEVERITY_MEDIUM,
                self.SEVERITY_HIGH
            ],
            'supported_operations': [
                'validate_signal',
                'normalize_signal',
                'frame_signal',
                'calculate_rms',
                'calculate_power',
                'to_decibels',
                'classify_by_thresholds'
            ],
            'default_frame_ms': 25.0,
            'default_hop_ms': 10.0
        }
