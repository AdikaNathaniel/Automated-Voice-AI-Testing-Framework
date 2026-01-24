"""
Audio Quality Service for SNR measurement and analysis.

This service provides methods for measuring Signal-to-Noise Ratio (SNR)
and other audio quality metrics. SNR is critical for understanding audio
quality and its impact on ASR performance.

Supported algorithms:
- WADA-SNR: Waveform Amplitude Distribution Analysis
- NIST-SNR: NIST standard SNR estimation

Quality classifications:
- EXCELLENT: SNR > 30 dB
- GOOD: 20 dB < SNR <= 30 dB
- FAIR: 10 dB < SNR <= 20 dB
- POOR: SNR <= 10 dB

Example:
    >>> service = AudioQualityService()
    >>> snr = service.measure_snr(audio_signal, sample_rate=16000)
    >>> print(f"SNR: {snr:.2f} dB")
"""

from typing import List, Dict, Any, Optional
import numpy as np


class AudioQualityService:
    """
    Service for audio quality measurement and analysis.

    Provides methods for measuring SNR, classifying audio quality,
    and analyzing the impact of noise on ASR performance.

    Attributes:
        quality_thresholds: SNR thresholds for quality classification

    Example:
        >>> service = AudioQualityService()
        >>> metrics = service.get_quality_metrics(audio_signal)
        >>> print(f"Quality: {metrics['quality_class']}")
    """

    # Quality classification thresholds (in dB)
    EXCELLENT_THRESHOLD = 30.0
    GOOD_THRESHOLD = 20.0
    FAIR_THRESHOLD = 10.0

    # Quality level constants
    EXCELLENT = 'EXCELLENT'
    GOOD = 'GOOD'
    FAIR = 'FAIR'
    POOR = 'POOR'

    def __init__(self):
        """Initialize the audio quality service."""
        self.quality_thresholds = {
            self.EXCELLENT: self.EXCELLENT_THRESHOLD,
            self.GOOD: self.GOOD_THRESHOLD,
            self.FAIR: self.FAIR_THRESHOLD
        }

    def measure_snr(
        self,
        signal: Optional[np.ndarray],
        sample_rate: int = 16000,
        algorithm: str = 'wada'
    ) -> float:
        """
        Measure Signal-to-Noise Ratio of audio signal.

        Args:
            signal: Audio signal as numpy array
            sample_rate: Sample rate in Hz
            algorithm: Algorithm to use ('wada' or 'nist')

        Returns:
            SNR value in decibels (dB)

        Example:
            >>> snr = service.measure_snr(audio_signal)
            >>> print(f"SNR: {snr:.2f} dB")
        """
        if signal is None or len(signal) == 0:
            return 0.0

        # Normalize signal to float
        if signal.dtype != np.float32 and signal.dtype != np.float64:
            signal = signal.astype(np.float64) / np.iinfo(signal.dtype).max

        if algorithm.lower() == 'nist':
            return self.calculate_nist_snr(signal, sample_rate)
        else:
            return self.calculate_wada_snr(signal, sample_rate)

    def calculate_wada_snr(
        self,
        signal: np.ndarray,
        sample_rate: int = 16000
    ) -> float:
        """
        Calculate SNR using WADA (Waveform Amplitude Distribution Analysis).

        WADA-SNR uses the distribution of waveform amplitudes to estimate
        SNR without requiring a separate noise estimate.

        Args:
            signal: Audio signal as numpy array
            sample_rate: Sample rate in Hz

        Returns:
            SNR value in decibels (dB)

        Example:
            >>> snr = service.calculate_wada_snr(audio_signal)
            >>> print(f"WADA SNR: {snr:.2f} dB")
        """
        if signal is None or len(signal) == 0:
            return 0.0

        # Calculate signal statistics
        abs_signal = np.abs(signal)
        mean_abs = np.mean(abs_signal)

        if mean_abs == 0:
            return 0.0

        # WADA SNR estimation based on amplitude distribution
        # Using the ratio of RMS to mean absolute value
        rms = np.sqrt(np.mean(signal ** 2))

        if rms == 0:
            return 0.0

        # Estimate SNR based on kurtosis and distribution
        np.mean((signal - np.mean(signal)) ** 4) / (
            np.var(signal) ** 2 + 1e-10
        )

        # WADA formula approximation
        # Higher kurtosis indicates more speech-like (peaky) signal
        snr_estimate = 10 * np.log10(
            rms ** 2 / (self._estimate_noise_power(signal) + 1e-10)
        )

        return max(0.0, snr_estimate)

    def calculate_nist_snr(
        self,
        signal: np.ndarray,
        sample_rate: int = 16000
    ) -> float:
        """
        Calculate SNR using NIST standard method.

        NIST-SNR uses Voice Activity Detection to separate speech
        and noise segments for more accurate estimation.

        Args:
            signal: Audio signal as numpy array
            sample_rate: Sample rate in Hz

        Returns:
            SNR value in decibels (dB)

        Example:
            >>> snr = service.calculate_nist_snr(audio_signal)
            >>> print(f"NIST SNR: {snr:.2f} dB")
        """
        if signal is None or len(signal) == 0:
            return 0.0

        # Frame-based analysis
        frame_length = int(0.025 * sample_rate)  # 25ms frames
        hop_length = int(0.010 * sample_rate)    # 10ms hop

        frames = self._frame_signal(signal, frame_length, hop_length)

        if len(frames) == 0:
            return 0.0

        # Calculate energy per frame
        frame_energies = np.array([np.sum(f ** 2) for f in frames])

        # Simple VAD based on energy threshold
        energy_threshold = np.percentile(frame_energies, 20)

        speech_frames = frame_energies > energy_threshold
        noise_frames = ~speech_frames

        if not np.any(speech_frames) or not np.any(noise_frames):
            # Cannot separate speech and noise
            return self.calculate_wada_snr(signal, sample_rate)

        # Calculate signal and noise power
        signal_power = np.mean(frame_energies[speech_frames])
        noise_power = np.mean(frame_energies[noise_frames])

        if noise_power == 0:
            return 60.0  # Very high SNR

        snr = 10 * np.log10(signal_power / noise_power)

        return max(0.0, snr)

    def _frame_signal(
        self,
        signal: np.ndarray,
        frame_length: int,
        hop_length: int
    ) -> List[np.ndarray]:
        """Split signal into overlapping frames."""
        frames = []
        for i in range(0, len(signal) - frame_length + 1, hop_length):
            frames.append(signal[i:i + frame_length])
        return frames

    def _estimate_noise_power(self, signal: np.ndarray) -> float:
        """Estimate noise power from signal."""
        # Use minimum statistics approach
        # Sort absolute values and use lower percentile as noise estimate
        sorted_abs = np.sort(np.abs(signal))
        noise_portion = sorted_abs[:int(len(sorted_abs) * 0.1)]
        return np.mean(noise_portion ** 2)

    def classify_quality(self, snr: float) -> str:
        """
        Classify audio quality based on SNR value.

        Args:
            snr: SNR value in decibels

        Returns:
            Quality classification string

        Example:
            >>> quality = service.classify_quality(25.0)
            >>> print(quality)
            'GOOD'
        """
        if snr > self.EXCELLENT_THRESHOLD:
            return self.EXCELLENT
        elif snr > self.GOOD_THRESHOLD:
            return self.GOOD
        elif snr > self.FAIR_THRESHOLD:
            return self.FAIR
        else:
            return self.POOR

    def calculate_signal_power(self, signal: np.ndarray) -> float:
        """
        Calculate signal power (RMS squared).

        Args:
            signal: Audio signal as numpy array

        Returns:
            Signal power value

        Example:
            >>> power = service.calculate_signal_power(audio_signal)
            >>> print(f"Power: {power:.6f}")
        """
        if signal is None or len(signal) == 0:
            return 0.0

        return float(np.mean(signal ** 2))

    def estimate_noise_floor(
        self,
        signal: np.ndarray,
        percentile: float = 10.0
    ) -> float:
        """
        Estimate noise floor from audio signal.

        Uses minimum statistics to estimate the noise floor
        without requiring explicit noise segments.

        Args:
            signal: Audio signal as numpy array
            percentile: Percentile to use for noise estimate

        Returns:
            Noise floor estimate in linear scale

        Example:
            >>> noise = service.estimate_noise_floor(audio_signal)
            >>> print(f"Noise floor: {noise:.6f}")
        """
        if signal is None or len(signal) == 0:
            return 0.0

        # Calculate frame energies
        frame_length = 256
        hop_length = 128

        frames = self._frame_signal(signal, frame_length, hop_length)

        if len(frames) == 0:
            return self._estimate_noise_power(signal)

        frame_energies = np.array([np.mean(f ** 2) for f in frames])

        # Use percentile as noise floor estimate
        noise_floor = np.percentile(frame_energies, percentile)

        return float(noise_floor)

    def calculate_snr_impact(
        self,
        snr_values: List[float],
        accuracy_values: List[float]
    ) -> Dict[str, Any]:
        """
        Calculate SNR impact on ASR accuracy.

        Analyzes correlation between SNR and transcription accuracy
        to understand how audio quality affects ASR performance.

        Args:
            snr_values: List of SNR measurements
            accuracy_values: Corresponding accuracy values

        Returns:
            Dictionary with impact analysis

        Example:
            >>> impact = service.calculate_snr_impact(snr_list, acc_list)
            >>> print(f"Correlation: {impact['correlation']:.2f}")
        """
        if not snr_values or not accuracy_values:
            return {
                'correlation': 0.0,
                'slope': 0.0,
                'intercept': 0.0,
                'samples': 0
            }

        if len(snr_values) != len(accuracy_values):
            min_len = min(len(snr_values), len(accuracy_values))
            snr_values = snr_values[:min_len]
            accuracy_values = accuracy_values[:min_len]

        snr_array = np.array(snr_values)
        acc_array = np.array(accuracy_values)

        # Calculate correlation
        if np.std(snr_array) == 0 or np.std(acc_array) == 0:
            correlation = 0.0
        else:
            correlation = float(np.corrcoef(snr_array, acc_array)[0, 1])

        # Linear regression
        if len(snr_values) >= 2:
            slope, intercept = np.polyfit(snr_array, acc_array, 1)
        else:
            slope = 0.0
            intercept = acc_array[0] if len(acc_array) > 0 else 0.0

        # Group by quality class
        quality_breakdown = {}
        for snr, acc in zip(snr_values, accuracy_values):
            quality = self.classify_quality(snr)
            if quality not in quality_breakdown:
                quality_breakdown[quality] = {
                    'count': 0,
                    'total_accuracy': 0.0
                }
            quality_breakdown[quality]['count'] += 1
            quality_breakdown[quality]['total_accuracy'] += acc

        # Calculate average accuracy per quality class
        for quality in quality_breakdown:
            count = quality_breakdown[quality]['count']
            total = quality_breakdown[quality]['total_accuracy']
            quality_breakdown[quality]['avg_accuracy'] = total / count if count > 0 else 0.0

        return {
            'correlation': correlation,
            'slope': float(slope),
            'intercept': float(intercept),
            'samples': len(snr_values),
            'quality_breakdown': quality_breakdown
        }

    def to_decibels(self, power: float) -> float:
        """
        Convert power ratio to decibels.

        Args:
            power: Power value (linear scale)

        Returns:
            Value in decibels (dB)

        Example:
            >>> db = service.to_decibels(100.0)
            >>> print(f"{db:.2f} dB")
        """
        if power <= 0:
            return -np.inf
        return 10 * np.log10(power)

    def get_quality_metrics(
        self,
        signal: np.ndarray,
        sample_rate: int = 16000
    ) -> Dict[str, Any]:
        """
        Get comprehensive audio quality metrics.

        Args:
            signal: Audio signal as numpy array
            sample_rate: Sample rate in Hz

        Returns:
            Dictionary with all quality metrics

        Example:
            >>> metrics = service.get_quality_metrics(audio_signal)
            >>> print(f"SNR: {metrics['snr']:.2f} dB")
            >>> print(f"Quality: {metrics['quality_class']}")
        """
        # Calculate SNR using both algorithms
        wada_snr = self.calculate_wada_snr(signal, sample_rate)
        nist_snr = self.calculate_nist_snr(signal, sample_rate)

        # Use average as primary SNR
        snr = (wada_snr + nist_snr) / 2

        # Other metrics
        signal_power = self.calculate_signal_power(signal)
        noise_floor = self.estimate_noise_floor(signal)
        quality_class = self.classify_quality(snr)

        # Calculate dynamic range
        if signal is not None and len(signal) > 0:
            peak = np.max(np.abs(signal))
            rms = np.sqrt(signal_power)
            crest_factor = peak / rms if rms > 0 else 0.0
        else:
            peak = 0.0
            rms = 0.0
            crest_factor = 0.0

        return {
            'snr': snr,
            'wada_snr': wada_snr,
            'nist_snr': nist_snr,
            'signal_power': signal_power,
            'signal_power_db': self.to_decibels(signal_power),
            'noise_floor': noise_floor,
            'noise_floor_db': self.to_decibels(noise_floor),
            'quality_class': quality_class,
            'peak': float(peak),
            'rms': float(rms),
            'crest_factor': float(crest_factor)
        }
