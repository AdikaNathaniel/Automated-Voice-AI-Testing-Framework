"""
Sample Rate Validation Service for ASR audio testing.

This service provides tools for validating and analyzing audio sample rates
and their impact on ASR performance. Sample rate determines the frequency
range that can be captured.

Standard sample rates:
- 8000 Hz: Telephony (narrowband)
- 16000 Hz: Wideband speech
- 22050 Hz: Half CD quality
- 44100 Hz: CD quality
- 48000 Hz: Professional audio/video

Example:
    >>> service = SampleRateValidationService()
    >>> result = service.validate_sample_rate(16000, 'asr')
    >>> print(f"Valid: {result['valid']}")
"""

from typing import List, Dict, Any, Optional
import numpy as np


class SampleRateValidationService:
    """
    Service for validating and analyzing audio sample rates.

    Provides methods for validating sample rates, detecting resampling
    artifacts, and recommending optimal rates for ASR systems.

    Attributes:
        standard_rates: List of standard sample rates
        rate_info: Information about each sample rate

    Example:
        >>> service = SampleRateValidationService()
        >>> rate = service.recommend_sample_rate('voip')
        >>> print(f"Recommended: {rate} Hz")
    """

    # Standard sample rates
    RATE_8000 = 8000    # Telephony
    RATE_11025 = 11025  # Quarter CD
    RATE_16000 = 16000  # Wideband speech
    RATE_22050 = 22050  # Half CD
    RATE_32000 = 32000  # Digital radio
    RATE_44100 = 44100  # CD quality
    RATE_48000 = 48000  # Professional

    def __init__(self):
        """Initialize the sample rate validation service."""
        self.standard_rates: List[int] = [
            self.RATE_8000,
            self.RATE_11025,
            self.RATE_16000,
            self.RATE_22050,
            self.RATE_32000,
            self.RATE_44100,
            self.RATE_48000
        ]

        self.rate_info: Dict[int, Dict[str, Any]] = {
            self.RATE_8000: {
                'name': 'Telephony',
                'type': 'narrowband',
                'nyquist': 4000,
                'frequency_range': '0-4 kHz',
                'asr_quality': 'fair',
                'use_cases': ['voip', 'telephony', 'low_bandwidth']
            },
            self.RATE_16000: {
                'name': 'Wideband Speech',
                'type': 'wideband',
                'nyquist': 8000,
                'frequency_range': '0-8 kHz',
                'asr_quality': 'excellent',
                'use_cases': ['asr', 'voip_hd', 'speech_recognition']
            },
            self.RATE_22050: {
                'name': 'Half CD',
                'type': 'wideband',
                'nyquist': 11025,
                'frequency_range': '0-11 kHz',
                'asr_quality': 'excellent',
                'use_cases': ['speech', 'podcasts']
            },
            self.RATE_44100: {
                'name': 'CD Quality',
                'type': 'fullband',
                'nyquist': 22050,
                'frequency_range': '0-22 kHz',
                'asr_quality': 'excellent',
                'use_cases': ['music', 'broadcast', 'high_quality']
            },
            self.RATE_48000: {
                'name': 'Professional',
                'type': 'fullband',
                'nyquist': 24000,
                'frequency_range': '0-24 kHz',
                'asr_quality': 'excellent',
                'use_cases': ['video', 'professional', 'broadcast']
            }
        }

    def get_supported_rates(self) -> List[int]:
        """
        Get list of supported sample rates.

        Returns:
            List of sample rates in Hz

        Example:
            >>> rates = service.get_supported_rates()
            >>> print(rates)
            [8000, 11025, 16000, 22050, 32000, 44100, 48000]
        """
        return self.standard_rates.copy()

    def get_nyquist_frequency(self, sample_rate: int) -> float:
        """
        Get Nyquist frequency for a sample rate.

        The Nyquist frequency is half the sample rate and represents
        the highest frequency that can be accurately captured.

        Args:
            sample_rate: Sample rate in Hz

        Returns:
            Nyquist frequency in Hz

        Example:
            >>> nyquist = service.get_nyquist_frequency(16000)
            >>> print(f"Nyquist: {nyquist} Hz")
            8000.0
        """
        return float(sample_rate / 2)

    def validate_sample_rate(
        self,
        sample_rate: int,
        use_case: str = 'asr'
    ) -> Dict[str, Any]:
        """
        Validate sample rate for a specific use case.

        Args:
            sample_rate: Sample rate to validate
            use_case: Intended use case

        Returns:
            Dictionary with validation results

        Example:
            >>> result = service.validate_sample_rate(16000, 'asr')
            >>> print(f"Valid: {result['valid']}")
        """
        is_standard = sample_rate in self.standard_rates
        nyquist = self.get_nyquist_frequency(sample_rate)

        # Determine quality for ASR
        if sample_rate >= 16000:
            asr_quality = 'excellent'
            valid_for_asr = True
        elif sample_rate >= 8000:
            asr_quality = 'fair'
            valid_for_asr = True
        else:
            asr_quality = 'poor'
            valid_for_asr = False

        # Check use case compatibility
        use_case_valid = self._check_use_case_compatibility(sample_rate, use_case)

        # Get rate info if available
        rate_info = self.rate_info.get(sample_rate, {
            'name': 'Custom',
            'type': 'custom',
            'nyquist': nyquist,
            'frequency_range': f'0-{nyquist/1000:.1f} kHz',
            'asr_quality': asr_quality,
            'use_cases': []
        })

        return {
            'valid': use_case_valid and valid_for_asr,
            'sample_rate': sample_rate,
            'is_standard': is_standard,
            'nyquist_frequency': nyquist,
            'asr_quality': asr_quality,
            'valid_for_asr': valid_for_asr,
            'use_case_compatible': use_case_valid,
            'rate_info': rate_info,
            'recommendations': self._get_recommendations(sample_rate, use_case)
        }

    def _check_use_case_compatibility(
        self,
        sample_rate: int,
        use_case: str
    ) -> bool:
        """Check if sample rate is compatible with use case."""
        use_case = use_case.lower()

        if use_case in ['asr', 'speech_recognition']:
            return sample_rate >= 8000
        elif use_case in ['voip', 'telephony']:
            return sample_rate >= 8000
        elif use_case in ['music', 'broadcast', 'high_quality']:
            return sample_rate >= 44100
        elif use_case in ['professional', 'video']:
            return sample_rate >= 48000
        else:
            return sample_rate >= 8000

    def _get_recommendations(
        self,
        sample_rate: int,
        use_case: str
    ) -> List[str]:
        """Get recommendations for sample rate optimization."""
        recommendations = []

        if sample_rate < 8000:
            recommendations.append('Sample rate too low for speech recognition')
            recommendations.append('Consider upsampling to at least 8000 Hz')

        if sample_rate == 8000 and use_case.lower() == 'asr':
            recommendations.append('Consider 16000 Hz for better ASR accuracy')

        if sample_rate > 16000 and use_case.lower() == 'asr':
            recommendations.append('Higher rates provide no ASR benefit')
            recommendations.append('Consider downsampling to 16000 Hz')

        if sample_rate not in self.standard_rates:
            closest = min(self.standard_rates, key=lambda x: abs(x - sample_rate))
            recommendations.append(f'Non-standard rate; consider {closest} Hz')

        return recommendations

    def detect_resampling_artifacts(
        self,
        signal: np.ndarray,
        original_rate: int,
        current_rate: int
    ) -> Dict[str, Any]:
        """
        Detect artifacts from resampling.

        Resampling can introduce aliasing, phase distortion, and
        frequency response changes.

        Args:
            signal: Audio signal
            original_rate: Original sample rate
            current_rate: Current sample rate

        Returns:
            Dictionary with artifact detection results

        Example:
            >>> result = service.detect_resampling_artifacts(signal, 44100, 16000)
            >>> print(f"Aliasing risk: {result['aliasing_risk']}")
        """
        if signal is None or len(signal) == 0:
            return {
                'artifacts_detected': False,
                'aliasing_risk': 'none',
                'quality_impact': 0.0
            }

        # Calculate resampling ratio
        ratio = current_rate / original_rate

        # Detect aliasing risk
        if ratio < 1:
            # Downsampling - check for aliasing
            original_rate / 2
            current_rate / 2

            # High frequency content above new Nyquist causes aliasing
            aliasing_risk = 'high' if ratio < 0.5 else 'medium' if ratio < 0.75 else 'low'
        else:
            aliasing_risk = 'none'

        # Estimate quality impact
        if ratio == 1:
            quality_impact = 0.0
        elif ratio < 1:
            # Downsampling quality loss
            quality_impact = (1 - ratio) * 50
        else:
            # Upsampling (no real quality gain)
            quality_impact = 5.0

        # Spectral analysis for artifact detection
        signal = signal.astype(np.float64)
        spectrum = np.abs(np.fft.rfft(signal))

        # Check for energy near Nyquist (potential aliasing)
        if len(spectrum) > 10:
            high_freq_energy = np.mean(spectrum[-len(spectrum)//10:])
            total_energy = np.mean(spectrum)
            high_freq_ratio = high_freq_energy / (total_energy + 1e-10)
            potential_aliasing = high_freq_ratio > 0.1
        else:
            potential_aliasing = False

        return {
            'artifacts_detected': aliasing_risk != 'none' or potential_aliasing,
            'aliasing_risk': aliasing_risk,
            'quality_impact': float(min(100, quality_impact)),
            'resampling_ratio': float(ratio),
            'potential_aliasing': potential_aliasing,
            'original_nyquist': original_rate / 2,
            'current_nyquist': current_rate / 2
        }

    def analyze_quality_impact(
        self,
        source_rate: int,
        target_rate: int
    ) -> Dict[str, Any]:
        """
        Analyze quality impact of sample rate conversion.

        Args:
            source_rate: Source sample rate
            target_rate: Target sample rate

        Returns:
            Dictionary with quality impact analysis

        Example:
            >>> impact = service.analyze_quality_impact(44100, 16000)
            >>> print(f"Quality loss: {impact['quality_loss']:.1f}%")
        """
        ratio = target_rate / source_rate

        # Calculate frequency loss
        source_nyquist = source_rate / 2
        target_nyquist = target_rate / 2
        freq_loss = max(0, (source_nyquist - target_nyquist) / source_nyquist * 100)

        # Estimate quality loss
        if ratio >= 1:
            quality_loss = 0.0
            operation = 'upsampling'
        else:
            quality_loss = freq_loss * 0.5
            operation = 'downsampling'

        # ASR impact estimation
        if target_rate >= 16000:
            asr_impact = 'minimal'
            wer_increase = 0.0
        elif target_rate >= 8000:
            asr_impact = 'moderate'
            wer_increase = 5.0
        else:
            asr_impact = 'severe'
            wer_increase = 20.0

        return {
            'source_rate': source_rate,
            'target_rate': target_rate,
            'operation': operation,
            'ratio': float(ratio),
            'frequency_loss': float(freq_loss),
            'quality_loss': float(quality_loss),
            'asr_impact': asr_impact,
            'estimated_wer_increase': float(wer_increase),
            'recommendation': (
                'acceptable' if quality_loss < 10
                else 'caution' if quality_loss < 30
                else 'not_recommended'
            )
        }

    def recommend_sample_rate(self, use_case: str) -> int:
        """
        Recommend optimal sample rate for use case.

        Args:
            use_case: Use case type

        Returns:
            Recommended sample rate in Hz

        Example:
            >>> rate = service.recommend_sample_rate('asr')
            >>> print(f"Recommended: {rate} Hz")
        """
        use_case = use_case.lower()

        recommendations = {
            'asr': self.RATE_16000,
            'speech_recognition': self.RATE_16000,
            'voip': self.RATE_16000,
            'voip_hd': self.RATE_16000,
            'telephony': self.RATE_8000,
            'music': self.RATE_44100,
            'broadcast': self.RATE_48000,
            'video': self.RATE_48000,
            'professional': self.RATE_48000,
            'podcast': self.RATE_44100,
            'low_bandwidth': self.RATE_8000
        }

        return recommendations.get(use_case, self.RATE_16000)

    def get_sample_rate_metrics(
        self,
        sample_rate: int,
        signal: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive sample rate metrics.

        Args:
            sample_rate: Sample rate to analyze
            signal: Optional audio signal for analysis

        Returns:
            Dictionary with all sample rate metrics

        Example:
            >>> metrics = service.get_sample_rate_metrics(16000)
            >>> print(f"Quality: {metrics['asr_quality']}")
        """
        validation = self.validate_sample_rate(sample_rate, 'asr')
        nyquist = self.get_nyquist_frequency(sample_rate)

        # Rate classification
        if sample_rate >= 44100:
            classification = 'fullband'
        elif sample_rate >= 16000:
            classification = 'wideband'
        else:
            classification = 'narrowband'

        # Signal analysis if provided
        if signal is not None and len(signal) > 0:
            duration = len(signal) / sample_rate
            samples = len(signal)
        else:
            duration = 0.0
            samples = 0

        return {
            'sample_rate': sample_rate,
            'nyquist_frequency': nyquist,
            'classification': classification,
            'is_standard': sample_rate in self.standard_rates,
            'validation': validation,
            'asr_quality': validation['asr_quality'],
            'signal_duration': float(duration),
            'total_samples': samples,
            'recommended_for_asr': sample_rate >= 16000,
            'frequency_range': f'0-{nyquist/1000:.1f} kHz',
            'optimal_rate': self.recommend_sample_rate('asr')
        }
