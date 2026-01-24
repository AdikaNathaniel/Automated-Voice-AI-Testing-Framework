"""
Audio Artifact Detection Service for ASR quality analysis.

This service provides methods for detecting audio artifacts that can
impact ASR performance, including clipping, echo, background noise,
and reverb.

Artifact types:
- Clipping: Signal amplitude saturation
- Echo: Delayed signal reflections
- Background noise: Ambient sounds (babble, traffic, music)
- Reverb: Room acoustic reflections

Severity levels:
- NONE: No artifact detected
- LOW: Minor artifact, minimal ASR impact
- MEDIUM: Moderate artifact, noticeable ASR impact
- HIGH: Severe artifact, significant ASR degradation

Example:
    >>> service = AudioArtifactDetectionService()
    >>> metrics = service.get_artifact_metrics(audio_signal)
    >>> print(f"Clipping: {metrics['clipping']['severity']}")
"""

from typing import List, Dict, Any
import numpy as np


class AudioArtifactDetectionService:
    """
    Service for detecting audio artifacts.

    Provides methods for detecting clipping, echo, background noise,
    and reverb, along with severity assessment for each artifact type.

    Attributes:
        thresholds: Detection thresholds for different artifacts

    Example:
        >>> service = AudioArtifactDetectionService()
        >>> clipping = service.detect_clipping(audio_signal)
        >>> print(f"Clipping detected: {clipping['detected']}")
    """

    # Severity level constants
    SEVERITY_NONE = 'NONE'
    SEVERITY_LOW = 'LOW'
    SEVERITY_MEDIUM = 'MEDIUM'
    SEVERITY_HIGH = 'HIGH'

    # Noise type constants
    NOISE_BABBLE = 'babble'
    NOISE_TRAFFIC = 'traffic'
    NOISE_MUSIC = 'music'
    NOISE_WHITE = 'white'
    NOISE_PINK = 'pink'
    NOISE_UNKNOWN = 'unknown'

    # All supported noise types
    NOISE_TYPES: List[str] = [
        NOISE_BABBLE, NOISE_TRAFFIC, NOISE_MUSIC,
        NOISE_WHITE, NOISE_PINK, NOISE_UNKNOWN
    ]

    def __init__(self):
        """Initialize the audio artifact detection service."""
        # Clipping threshold (proportion of samples at max)
        self.clipping_threshold_low = 0.001
        self.clipping_threshold_medium = 0.01
        self.clipping_threshold_high = 0.05

        # Echo detection thresholds
        self.echo_threshold = 0.3

        # Reverb RT60 thresholds (in seconds)
        self.rt60_threshold_low = 0.3
        self.rt60_threshold_medium = 0.6
        self.rt60_threshold_high = 1.0

    def detect_clipping(
        self,
        signal: np.ndarray,
        threshold: float = 0.99
    ) -> Dict[str, Any]:
        """
        Detect audio clipping (amplitude saturation).

        Clipping occurs when signal amplitude exceeds the maximum
        representable value, causing waveform distortion.

        Args:
            signal: Audio signal as numpy array
            threshold: Threshold for considering sample as clipped

        Returns:
            Dictionary with clipping metrics

        Example:
            >>> result = service.detect_clipping(audio_signal)
            >>> print(f"Clipping: {result['severity']}")
        """
        if signal is None or len(signal) == 0:
            return {
                'detected': False,
                'severity': self.SEVERITY_NONE,
                'clipped_samples': 0,
                'clipping_ratio': 0.0
            }

        # Normalize signal
        max_val = np.max(np.abs(signal))
        if max_val > 0:
            normalized = signal / max_val
        else:
            normalized = signal

        # Count clipped samples
        clipped = np.sum(np.abs(normalized) >= threshold)
        clipping_ratio = clipped / len(signal)

        # Determine severity
        if clipping_ratio >= self.clipping_threshold_high:
            severity = self.SEVERITY_HIGH
        elif clipping_ratio >= self.clipping_threshold_medium:
            severity = self.SEVERITY_MEDIUM
        elif clipping_ratio >= self.clipping_threshold_low:
            severity = self.SEVERITY_LOW
        else:
            severity = self.SEVERITY_NONE

        return {
            'detected': clipping_ratio >= self.clipping_threshold_low,
            'severity': severity,
            'clipped_samples': int(clipped),
            'clipping_ratio': float(clipping_ratio)
        }

    def detect_echo(
        self,
        signal: np.ndarray,
        sample_rate: int = 16000
    ) -> Dict[str, Any]:
        """
        Detect echo in audio signal.

        Uses autocorrelation to identify delayed signal reflections.

        Args:
            signal: Audio signal as numpy array
            sample_rate: Sample rate in Hz

        Returns:
            Dictionary with echo detection results

        Example:
            >>> result = service.detect_echo(audio_signal)
            >>> if result['detected']:
            ...     print(f"Echo delay: {result['delay_ms']:.1f} ms")
        """
        if signal is None or len(signal) == 0:
            return {
                'detected': False,
                'severity': self.SEVERITY_NONE,
                'delay_ms': 0.0,
                'echo_strength': 0.0
            }

        # Calculate autocorrelation
        signal = signal.astype(np.float64)
        signal = signal - np.mean(signal)

        # Normalize
        norm = np.sum(signal ** 2)
        if norm == 0:
            return {
                'detected': False,
                'severity': self.SEVERITY_NONE,
                'delay_ms': 0.0,
                'echo_strength': 0.0
            }

        # Look for peaks in autocorrelation after initial decay
        # Minimum delay of 20ms to skip immediate correlation
        min_lag = int(0.02 * sample_rate)
        max_lag = min(int(0.5 * sample_rate), len(signal) // 2)

        autocorr = np.correlate(signal, signal, mode='full')
        autocorr = autocorr[len(signal) - 1:]  # Keep positive lags only
        autocorr = autocorr / autocorr[0]  # Normalize

        # Find peaks after min_lag
        if max_lag > min_lag and min_lag < len(autocorr):
            search_region = autocorr[min_lag:max_lag]
            if len(search_region) > 0:
                peak_idx = np.argmax(search_region)
                peak_value = search_region[peak_idx]
                delay_samples = min_lag + peak_idx
            else:
                peak_value = 0.0
                delay_samples = 0
        else:
            peak_value = 0.0
            delay_samples = 0

        # Calculate delay in milliseconds
        delay_ms = (delay_samples / sample_rate) * 1000

        # Determine severity
        if peak_value >= 0.5:
            severity = self.SEVERITY_HIGH
        elif peak_value >= 0.3:
            severity = self.SEVERITY_MEDIUM
        elif peak_value >= self.echo_threshold:
            severity = self.SEVERITY_LOW
        else:
            severity = self.SEVERITY_NONE

        return {
            'detected': peak_value >= self.echo_threshold,
            'severity': severity,
            'delay_ms': float(delay_ms),
            'echo_strength': float(peak_value)
        }

    def classify_noise(
        self,
        signal: np.ndarray,
        sample_rate: int = 16000
    ) -> Dict[str, Any]:
        """
        Classify background noise type.

        Analyzes spectral characteristics to identify noise type
        (babble, traffic, music, white, pink, etc.).

        Args:
            signal: Audio signal as numpy array
            sample_rate: Sample rate in Hz

        Returns:
            Dictionary with noise classification

        Example:
            >>> result = service.classify_noise(audio_signal)
            >>> print(f"Noise type: {result['noise_type']}")
        """
        if signal is None or len(signal) == 0:
            return {
                'noise_type': self.NOISE_UNKNOWN,
                'confidence': 0.0,
                'spectral_slope': 0.0
            }

        # Calculate spectrum
        signal = signal.astype(np.float64)

        # Use FFT to get power spectrum
        n_fft = min(2048, len(signal))
        spectrum = np.abs(np.fft.rfft(signal, n_fft)) ** 2

        if len(spectrum) < 2 or np.sum(spectrum) == 0:
            return {
                'noise_type': self.NOISE_UNKNOWN,
                'confidence': 0.0,
                'spectral_slope': 0.0
            }

        # Calculate spectral slope
        freqs = np.fft.rfftfreq(n_fft, 1 / sample_rate)

        # Log-log regression for spectral slope
        valid = (spectrum > 0) & (freqs > 0)
        if np.sum(valid) < 2:
            spectral_slope = 0.0
        else:
            log_freqs = np.log10(freqs[valid])
            log_spectrum = np.log10(spectrum[valid])
            slope, _ = np.polyfit(log_freqs, log_spectrum, 1)
            spectral_slope = float(slope)

        # Classify based on spectral characteristics
        # White noise: flat spectrum (slope ~0)
        # Pink noise: slope ~ -1
        # Traffic: low frequency dominant (slope < -1)
        # Babble/music: more complex

        confidence = 0.7  # Base confidence

        if -0.3 <= spectral_slope <= 0.3:
            noise_type = self.NOISE_WHITE
        elif -1.3 <= spectral_slope < -0.3:
            noise_type = self.NOISE_PINK
        elif spectral_slope < -1.3:
            noise_type = self.NOISE_TRAFFIC
            confidence = 0.5  # Lower confidence for traffic
        else:
            noise_type = self.NOISE_UNKNOWN
            confidence = 0.3

        return {
            'noise_type': noise_type,
            'confidence': confidence,
            'spectral_slope': spectral_slope
        }

    def detect_reverb(
        self,
        signal: np.ndarray,
        sample_rate: int = 16000
    ) -> Dict[str, Any]:
        """
        Detect reverb and estimate RT60.

        RT60 is the time for sound to decay by 60dB.

        Args:
            signal: Audio signal as numpy array
            sample_rate: Sample rate in Hz

        Returns:
            Dictionary with reverb detection results

        Example:
            >>> result = service.detect_reverb(audio_signal)
            >>> print(f"RT60: {result['rt60']:.2f} seconds")
        """
        if signal is None or len(signal) == 0:
            return {
                'detected': False,
                'severity': self.SEVERITY_NONE,
                'rt60': 0.0,
                'decay_rate': 0.0
            }

        # Estimate RT60 using energy decay
        rt60 = self.estimate_rt60(signal, sample_rate)

        # Determine severity
        if rt60 >= self.rt60_threshold_high:
            severity = self.SEVERITY_HIGH
        elif rt60 >= self.rt60_threshold_medium:
            severity = self.SEVERITY_MEDIUM
        elif rt60 >= self.rt60_threshold_low:
            severity = self.SEVERITY_LOW
        else:
            severity = self.SEVERITY_NONE

        # Calculate decay rate (dB/second)
        decay_rate = 60 / rt60 if rt60 > 0 else 0.0

        return {
            'detected': rt60 >= self.rt60_threshold_low,
            'severity': severity,
            'rt60': float(rt60),
            'decay_rate': float(decay_rate)
        }

    def estimate_rt60(
        self,
        signal: np.ndarray,
        sample_rate: int = 16000
    ) -> float:
        """
        Estimate RT60 (reverberation time).

        Uses Schroeder integration method for RT60 estimation.

        Args:
            signal: Audio signal as numpy array
            sample_rate: Sample rate in Hz

        Returns:
            Estimated RT60 in seconds

        Example:
            >>> rt60 = service.estimate_rt60(audio_signal)
            >>> print(f"RT60: {rt60:.2f} seconds")
        """
        if signal is None or len(signal) == 0:
            return 0.0

        # Square the signal
        signal_sq = signal.astype(np.float64) ** 2

        # Schroeder integration (backward integration)
        schroeder = np.cumsum(signal_sq[::-1])[::-1]

        if schroeder[0] == 0:
            return 0.0

        # Convert to dB
        schroeder_db = 10 * np.log10(schroeder / schroeder[0] + 1e-10)

        # Find T60 (time to decay by 60 dB)
        # Use linear regression on -5 to -35 dB range for T30 estimation
        valid_range = (schroeder_db >= -35) & (schroeder_db <= -5)

        if np.sum(valid_range) < 2:
            return 0.1  # Default to minimal reverb

        indices = np.where(valid_range)[0]
        times = indices / sample_rate
        db_values = schroeder_db[valid_range]

        if len(times) >= 2:
            slope, _ = np.polyfit(times, db_values, 1)
            if slope < 0:
                rt60 = -60 / slope
            else:
                rt60 = 0.1
        else:
            rt60 = 0.1

        return max(0.0, min(rt60, 5.0))  # Clamp to reasonable range

    def get_artifact_metrics(
        self,
        signal: np.ndarray,
        sample_rate: int = 16000
    ) -> Dict[str, Any]:
        """
        Get comprehensive artifact detection metrics.

        Args:
            signal: Audio signal as numpy array
            sample_rate: Sample rate in Hz

        Returns:
            Dictionary with all artifact metrics

        Example:
            >>> metrics = service.get_artifact_metrics(audio)
            >>> print(f"Clipping: {metrics['clipping']['severity']}")
            >>> print(f"Echo: {metrics['echo']['severity']}")
        """
        clipping = self.detect_clipping(signal)
        echo = self.detect_echo(signal, sample_rate)
        noise = self.classify_noise(signal, sample_rate)
        reverb = self.detect_reverb(signal, sample_rate)

        # Calculate overall quality impact
        severity_scores = {
            self.SEVERITY_NONE: 0,
            self.SEVERITY_LOW: 1,
            self.SEVERITY_MEDIUM: 2,
            self.SEVERITY_HIGH: 3
        }

        total_severity = (
            severity_scores.get(clipping['severity'], 0) +
            severity_scores.get(echo['severity'], 0) +
            severity_scores.get(reverb['severity'], 0)
        )

        if total_severity >= 6:
            overall_impact = 'SEVERE'
        elif total_severity >= 4:
            overall_impact = 'HIGH'
        elif total_severity >= 2:
            overall_impact = 'MEDIUM'
        elif total_severity >= 1:
            overall_impact = 'LOW'
        else:
            overall_impact = 'NONE'

        return {
            'clipping': clipping,
            'echo': echo,
            'noise': noise,
            'reverb': reverb,
            'overall_impact': overall_impact,
            'total_severity_score': total_severity
        }
