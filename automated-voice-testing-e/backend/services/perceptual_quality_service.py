"""
Perceptual Quality Service for audio quality assessment.

This service provides methods for measuring perceptual quality of audio
signals using metrics like PESQ (ITU-T P.862), MOS estimation, and
mapping quality scores to expected ASR performance.

Quality metrics:
- PESQ: Perceptual Evaluation of Speech Quality (-0.5 to 4.5)
- MOS: Mean Opinion Score (1 to 5)
- POLQA: P.863 perceptual quality (reference only)

MOS Classifications:
- EXCELLENT: 4.3-5.0
- GOOD: 3.6-4.3
- FAIR: 2.6-3.6
- POOR: 1.6-2.6
- BAD: 1.0-1.6

Example:
    >>> service = PerceptualQualityService()
    >>> mos = service.estimate_mos(audio_signal)
    >>> print(f"MOS: {mos:.2f}")
"""

from typing import Dict, Any, Optional
import numpy as np


class PerceptualQualityService:
    """
    Service for perceptual audio quality assessment.

    Provides methods for calculating PESQ scores, estimating MOS,
    and predicting ASR performance based on audio quality.

    Attributes:
        mos_thresholds: Thresholds for MOS classification

    Example:
        >>> service = PerceptualQualityService()
        >>> metrics = service.get_perceptual_metrics(audio_signal)
        >>> print(f"Quality: {metrics['classification']}")
    """

    # MOS classification thresholds
    EXCELLENT_THRESHOLD = 4.3
    GOOD_THRESHOLD = 3.6
    FAIR_THRESHOLD = 2.6
    POOR_THRESHOLD = 1.6

    # Quality level constants
    EXCELLENT = 'EXCELLENT'
    GOOD = 'GOOD'
    FAIR = 'FAIR'
    POOR = 'POOR'
    BAD = 'BAD'

    # PESQ range
    PESQ_MIN = -0.5
    PESQ_MAX = 4.5

    # MOS range
    MOS_MIN = 1.0
    MOS_MAX = 5.0

    def __init__(self):
        """Initialize the perceptual quality service."""
        self.mos_thresholds = {
            self.EXCELLENT: self.EXCELLENT_THRESHOLD,
            self.GOOD: self.GOOD_THRESHOLD,
            self.FAIR: self.FAIR_THRESHOLD,
            self.POOR: self.POOR_THRESHOLD
        }

    def calculate_pesq(
        self,
        reference: Optional[np.ndarray],
        degraded: np.ndarray,
        sample_rate: int = 16000,
        mode: str = 'wb'
    ) -> float:
        """
        Calculate PESQ (Perceptual Evaluation of Speech Quality) score.

        PESQ is defined in ITU-T P.862 and measures the perceived quality
        difference between reference and degraded audio signals.

        Note: This is a simplified estimation. For production use,
        integrate the pypesq or pesq library.

        Args:
            reference: Reference audio signal (or None for blind estimation)
            degraded: Degraded audio signal to evaluate
            sample_rate: Sample rate in Hz (16000 for wb, 8000 for nb)
            mode: 'wb' for wideband or 'nb' for narrowband

        Returns:
            PESQ score (-0.5 to 4.5)

        Example:
            >>> pesq = service.calculate_pesq(ref_audio, deg_audio)
            >>> print(f"PESQ: {pesq:.2f}")
        """
        if degraded is None or len(degraded) == 0:
            return self.PESQ_MIN

        # If no reference, estimate based on signal characteristics
        if reference is None:
            return self._estimate_pesq_blind(degraded, sample_rate)

        # Ensure same length
        min_len = min(len(reference), len(degraded))
        ref = reference[:min_len].astype(np.float64)
        deg = degraded[:min_len].astype(np.float64)

        # Normalize
        if np.max(np.abs(ref)) > 0:
            ref = ref / np.max(np.abs(ref))
        if np.max(np.abs(deg)) > 0:
            deg = deg / np.max(np.abs(deg))

        # Simplified PESQ estimation based on correlation and distortion
        correlation = np.corrcoef(ref, deg)[0, 1] if len(ref) > 0 else 0

        # Mean squared error
        mse = np.mean((ref - deg) ** 2)

        # Map to PESQ scale
        # High correlation + low MSE = high PESQ
        quality_score = correlation * (1 - mse)

        # Scale to PESQ range (-0.5 to 4.5)
        pesq = self.PESQ_MIN + (self.PESQ_MAX - self.PESQ_MIN) * (
            (quality_score + 1) / 2
        )

        return float(np.clip(pesq, self.PESQ_MIN, self.PESQ_MAX))

    def _estimate_pesq_blind(
        self,
        signal: np.ndarray,
        sample_rate: int
    ) -> float:
        """Estimate PESQ without reference signal."""
        if signal is None or len(signal) == 0:
            return self.PESQ_MIN

        # Normalize
        signal = signal.astype(np.float64)
        if np.max(np.abs(signal)) > 0:
            signal = signal / np.max(np.abs(signal))

        # Calculate signal quality indicators
        rms = np.sqrt(np.mean(signal ** 2))

        # Estimate SNR
        sorted_abs = np.sort(np.abs(signal))
        noise_estimate = np.mean(sorted_abs[:int(len(sorted_abs) * 0.1)] ** 2)
        signal_estimate = rms ** 2

        if noise_estimate > 0:
            snr = 10 * np.log10(signal_estimate / noise_estimate)
        else:
            snr = 60.0

        # Convert SNR to PESQ estimate
        pesq = self.snr_to_pesq(snr)

        return pesq

    def snr_to_pesq(self, snr: float) -> float:
        """
        Convert SNR to estimated PESQ score.

        Args:
            snr: Signal-to-noise ratio in dB

        Returns:
            Estimated PESQ score

        Example:
            >>> pesq = service.snr_to_pesq(30.0)
        """
        # Sigmoid mapping from SNR to PESQ
        # SNR of 30+ dB -> PESQ ~4.5
        # SNR of 0 dB -> PESQ ~1.5
        # SNR of -10 dB -> PESQ ~0
        pesq = self.PESQ_MIN + (self.PESQ_MAX - self.PESQ_MIN) / (
            1 + np.exp(-0.1 * (snr - 15))
        )

        return float(np.clip(pesq, self.PESQ_MIN, self.PESQ_MAX))

    def estimate_mos(
        self,
        signal: Optional[np.ndarray],
        sample_rate: int = 16000,
        reference: Optional[np.ndarray] = None
    ) -> float:
        """
        Estimate Mean Opinion Score (MOS) for audio quality.

        MOS represents average subjective quality rating on 1-5 scale.

        Args:
            signal: Audio signal to evaluate
            sample_rate: Sample rate in Hz
            reference: Optional reference signal for comparison

        Returns:
            MOS score (1.0 to 5.0)

        Example:
            >>> mos = service.estimate_mos(audio_signal)
            >>> print(f"MOS: {mos:.2f}")
        """
        if signal is None or len(signal) == 0:
            return self.MOS_MIN

        # Calculate PESQ first
        pesq = self.calculate_pesq(reference, signal, sample_rate)

        # Convert PESQ to MOS using ITU-T P.862.1 mapping
        mos = self.pesq_to_mos(pesq)

        return mos

    def pesq_to_mos(self, pesq: float) -> float:
        """
        Convert PESQ score to MOS using ITU-T P.862.1 mapping.

        Args:
            pesq: PESQ score (-0.5 to 4.5)

        Returns:
            MOS score (1.0 to 5.0)

        Example:
            >>> mos = service.pesq_to_mos(3.5)
        """
        # Linear mapping from PESQ range to MOS range
        mos = self.MOS_MIN + (pesq - self.PESQ_MIN) * (
            (self.MOS_MAX - self.MOS_MIN) / (self.PESQ_MAX - self.PESQ_MIN)
        )

        return float(np.clip(mos, self.MOS_MIN, self.MOS_MAX))

    def snr_to_mos(self, snr: float) -> float:
        """
        Convert SNR to estimated MOS score.

        Args:
            snr: Signal-to-noise ratio in dB

        Returns:
            Estimated MOS score (1.0 to 5.0)

        Example:
            >>> mos = service.snr_to_mos(25.0)
            >>> print(f"MOS: {mos:.2f}")
        """
        pesq = self.snr_to_pesq(snr)
        return self.pesq_to_mos(pesq)

    def classify_mos(self, mos: float) -> str:
        """
        Classify audio quality based on MOS score.

        Args:
            mos: MOS score (1.0 to 5.0)

        Returns:
            Quality classification string

        Example:
            >>> quality = service.classify_mos(3.8)
            >>> print(quality)
            'GOOD'
        """
        if mos >= self.EXCELLENT_THRESHOLD:
            return self.EXCELLENT
        elif mos >= self.GOOD_THRESHOLD:
            return self.GOOD
        elif mos >= self.FAIR_THRESHOLD:
            return self.FAIR
        elif mos >= self.POOR_THRESHOLD:
            return self.POOR
        else:
            return self.BAD

    def predict_asr_accuracy(
        self,
        mos: float
    ) -> Dict[str, Any]:
        """
        Predict ASR accuracy based on MOS score.

        Maps perceptual quality to expected transcription accuracy.

        Args:
            mos: MOS score (1.0 to 5.0)

        Returns:
            Dictionary with predicted accuracy ranges

        Example:
            >>> prediction = service.predict_asr_accuracy(4.0)
            >>> print(f"Expected WER: {prediction['expected_wer']:.1f}%")
        """
        # Map MOS to expected WER (Word Error Rate)
        # Higher MOS = Lower WER
        # MOS 5.0 -> WER ~2%
        # MOS 4.0 -> WER ~5%
        # MOS 3.0 -> WER ~15%
        # MOS 2.0 -> WER ~35%
        # MOS 1.0 -> WER ~60%

        # Exponential relationship
        normalized_mos = (mos - self.MOS_MIN) / (self.MOS_MAX - self.MOS_MIN)
        expected_wer = 60 * np.exp(-3 * normalized_mos)

        # Confidence range
        confidence_margin = 5 + 10 * (1 - normalized_mos)

        return {
            'expected_wer': float(expected_wer),
            'wer_range': (
                max(0, float(expected_wer - confidence_margin)),
                float(expected_wer + confidence_margin)
            ),
            'expected_accuracy': float(100 - expected_wer),
            'confidence': 'high' if mos >= 3.5 else 'medium' if mos >= 2.5 else 'low',
            'quality_class': self.classify_mos(mos)
        }

    def calculate_polqa(
        self,
        reference: Optional[np.ndarray],
        degraded: np.ndarray,
        sample_rate: int = 48000
    ) -> float:
        """
        Calculate POLQA (ITU-T P.863) score.

        Note: POLQA requires licensed software. This method provides
        a placeholder that falls back to PESQ estimation.

        Args:
            reference: Reference audio signal
            degraded: Degraded audio signal
            sample_rate: Sample rate in Hz (typically 48000 for POLQA)

        Returns:
            Estimated quality score

        Example:
            >>> polqa = service.calculate_polqa(ref, deg)
        """
        # POLQA requires commercial license - fall back to PESQ estimation
        # In production, integrate actual POLQA library
        return self.calculate_pesq(reference, degraded, sample_rate)

    def get_perceptual_metrics(
        self,
        signal: Optional[np.ndarray],
        sample_rate: int = 16000,
        reference: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive perceptual quality metrics.

        Args:
            signal: Audio signal to evaluate
            sample_rate: Sample rate in Hz
            reference: Optional reference signal for comparison

        Returns:
            Dictionary with all perceptual quality metrics

        Example:
            >>> metrics = service.get_perceptual_metrics(audio)
            >>> print(f"MOS: {metrics['mos']:.2f}")
            >>> print(f"Classification: {metrics['classification']}")
        """
        if signal is None or len(signal) == 0:
            return {
                'pesq': self.PESQ_MIN,
                'mos': self.MOS_MIN,
                'classification': self.BAD,
                'asr_prediction': self.predict_asr_accuracy(self.MOS_MIN)
            }

        # Calculate PESQ
        pesq = self.calculate_pesq(reference, signal, sample_rate)

        # Estimate MOS
        mos = self.pesq_to_mos(pesq)

        # Classify quality
        classification = self.classify_mos(mos)

        # Predict ASR performance
        asr_prediction = self.predict_asr_accuracy(mos)

        return {
            'pesq': pesq,
            'mos': mos,
            'classification': classification,
            'asr_prediction': asr_prediction,
            'mos_min': self.MOS_MIN,
            'mos_max': self.MOS_MAX,
            'pesq_min': self.PESQ_MIN,
            'pesq_max': self.PESQ_MAX
        }
