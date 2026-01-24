"""
Bit Depth and Channel Service for ASR audio testing.

This service provides tools for validating and analyzing audio bit depth
and channel configurations. Bit depth determines dynamic range, while
channel configuration affects how audio is processed for ASR.

Standard bit depths:
- 8-bit: 48 dB dynamic range (legacy)
- 16-bit: 96 dB dynamic range (CD quality)
- 24-bit: 144 dB dynamic range (professional)
- 32-bit float: 1528 dB dynamic range (production)

Channel configurations:
- Mono (1): Standard for ASR
- Stereo (2): Common for music/video
- 5.1 Surround (6): Home theater
- 7.1 Surround (8): Professional theater

Example:
    >>> service = BitDepthChannelService()
    >>> result = service.validate_bit_depth(16)
    >>> print(f"Valid: {result['valid']}")
"""

from typing import List, Dict, Any, Optional
import numpy as np


class BitDepthChannelService:
    """
    Service for validating and analyzing bit depth and channel configurations.

    Provides methods for validating bit depths, analyzing dynamic range,
    handling channel conversions, and recommending optimal settings for ASR.

    Attributes:
        supported_bit_depths: List of supported bit depths
        channel_configs: Information about channel configurations

    Example:
        >>> service = BitDepthChannelService()
        >>> metrics = service.get_bit_depth_metrics(16)
        >>> print(f"Dynamic range: {metrics['dynamic_range']} dB")
    """

    # Standard bit depths
    BIT_DEPTH_8 = 8
    BIT_DEPTH_16 = 16
    BIT_DEPTH_24 = 24
    BIT_DEPTH_32 = 32

    # Channel configurations
    CHANNEL_MONO = 1
    CHANNEL_STEREO = 2
    CHANNEL_SURROUND_5_1 = 6
    CHANNEL_SURROUND_7_1 = 8

    def __init__(self):
        """Initialize the bit depth and channel service."""
        self.supported_bit_depths: List[int] = [
            self.BIT_DEPTH_8,
            self.BIT_DEPTH_16,
            self.BIT_DEPTH_24,
            self.BIT_DEPTH_32
        ]

        self.bit_depth_info: Dict[int, Dict[str, Any]] = {
            self.BIT_DEPTH_8: {
                'name': '8-bit',
                'dynamic_range': 48.0,
                'max_value': 255,
                'dtype': 'uint8',
                'asr_quality': 'poor',
                'use_cases': ['legacy', 'telephony']
            },
            self.BIT_DEPTH_16: {
                'name': '16-bit',
                'dynamic_range': 96.0,
                'max_value': 32767,
                'dtype': 'int16',
                'asr_quality': 'excellent',
                'use_cases': ['cd_quality', 'asr', 'standard']
            },
            self.BIT_DEPTH_24: {
                'name': '24-bit',
                'dynamic_range': 144.0,
                'max_value': 8388607,
                'dtype': 'int32',
                'asr_quality': 'excellent',
                'use_cases': ['professional', 'recording', 'mastering']
            },
            self.BIT_DEPTH_32: {
                'name': '32-bit float',
                'dynamic_range': 1528.0,
                'max_value': 1.0,
                'dtype': 'float32',
                'asr_quality': 'excellent',
                'use_cases': ['production', 'mixing', 'processing']
            }
        }

        self.channel_configs: Dict[int, Dict[str, Any]] = {
            self.CHANNEL_MONO: {
                'name': 'Mono',
                'description': 'Single channel audio',
                'asr_compatible': True,
                'use_cases': ['asr', 'voice', 'telephony']
            },
            self.CHANNEL_STEREO: {
                'name': 'Stereo',
                'description': 'Two channel audio (left/right)',
                'asr_compatible': True,
                'use_cases': ['music', 'video', 'recording']
            },
            self.CHANNEL_SURROUND_5_1: {
                'name': '5.1 Surround',
                'description': 'Six channel surround sound',
                'asr_compatible': False,
                'use_cases': ['home_theater', 'film', 'broadcast']
            },
            self.CHANNEL_SURROUND_7_1: {
                'name': '7.1 Surround',
                'description': 'Eight channel surround sound',
                'asr_compatible': False,
                'use_cases': ['cinema', 'professional_theater']
            }
        }

    def get_supported_bit_depths(self) -> List[int]:
        """
        Get list of supported bit depths.

        Returns:
            List of bit depths in bits

        Example:
            >>> depths = service.get_supported_bit_depths()
            >>> print(depths)
            [8, 16, 24, 32]
        """
        return self.supported_bit_depths.copy()

    def validate_bit_depth(
        self,
        bit_depth: int,
        use_case: str = 'asr'
    ) -> Dict[str, Any]:
        """
        Validate bit depth for a specific use case.

        Args:
            bit_depth: Bit depth to validate
            use_case: Intended use case

        Returns:
            Dictionary with validation results

        Example:
            >>> result = service.validate_bit_depth(16, 'asr')
            >>> print(f"Valid: {result['valid']}")
        """
        is_standard = bit_depth in self.supported_bit_depths
        dynamic_range = self.calculate_dynamic_range(bit_depth)

        # Determine quality for ASR
        if bit_depth >= 16:
            asr_quality = 'excellent'
            valid_for_asr = True
        elif bit_depth >= 8:
            asr_quality = 'fair'
            valid_for_asr = True
        else:
            asr_quality = 'poor'
            valid_for_asr = False

        # Check use case compatibility
        use_case_valid = self._check_use_case_compatibility(bit_depth, use_case)

        # Get bit depth info if available
        depth_info = self.bit_depth_info.get(bit_depth, {
            'name': f'{bit_depth}-bit',
            'dynamic_range': dynamic_range,
            'max_value': 2 ** (bit_depth - 1) - 1,
            'dtype': 'custom',
            'asr_quality': asr_quality,
            'use_cases': []
        })

        return {
            'valid': use_case_valid and valid_for_asr,
            'bit_depth': bit_depth,
            'is_standard': is_standard,
            'dynamic_range': dynamic_range,
            'asr_quality': asr_quality,
            'valid_for_asr': valid_for_asr,
            'use_case_compatible': use_case_valid,
            'depth_info': depth_info,
            'recommendations': self._get_bit_depth_recommendations(bit_depth, use_case)
        }

    def _check_use_case_compatibility(
        self,
        bit_depth: int,
        use_case: str
    ) -> bool:
        """Check if bit depth is compatible with use case."""
        use_case = use_case.lower()

        if use_case in ['asr', 'speech_recognition', 'voice']:
            return bit_depth >= 8
        elif use_case in ['professional', 'mastering', 'recording']:
            return bit_depth >= 24
        elif use_case in ['cd_quality', 'standard']:
            return bit_depth >= 16
        else:
            return bit_depth >= 8

    def _get_bit_depth_recommendations(
        self,
        bit_depth: int,
        use_case: str
    ) -> List[str]:
        """Get recommendations for bit depth optimization."""
        recommendations = []

        if bit_depth < 8:
            recommendations.append('Bit depth too low for any audio use')
            recommendations.append('Minimum 8-bit required')

        if bit_depth == 8 and use_case.lower() == 'asr':
            recommendations.append('Consider 16-bit for better ASR accuracy')

        if bit_depth > 16 and use_case.lower() == 'asr':
            recommendations.append('Higher bit depths provide minimal ASR benefit')
            recommendations.append('16-bit is optimal for ASR')

        if bit_depth not in self.supported_bit_depths:
            closest = min(self.supported_bit_depths, key=lambda x: abs(x - bit_depth))
            recommendations.append(f'Non-standard bit depth; consider {closest}-bit')

        return recommendations

    def calculate_dynamic_range(self, bit_depth: int) -> float:
        """
        Calculate theoretical dynamic range for bit depth.

        Dynamic range = 6.02 * bit_depth dB (for linear PCM)

        Args:
            bit_depth: Bit depth in bits

        Returns:
            Dynamic range in dB

        Example:
            >>> dr = service.calculate_dynamic_range(16)
            >>> print(f"Dynamic range: {dr} dB")
            96.32
        """
        if bit_depth == 32:
            # 32-bit float has much higher theoretical dynamic range
            return 1528.0
        return float(6.02 * bit_depth)

    def validate_channels(
        self,
        num_channels: int,
        use_case: str = 'asr'
    ) -> Dict[str, Any]:
        """
        Validate channel configuration for a specific use case.

        Args:
            num_channels: Number of audio channels
            use_case: Intended use case

        Returns:
            Dictionary with validation results

        Example:
            >>> result = service.validate_channels(1, 'asr')
            >>> print(f"Valid: {result['valid']}")
        """
        # Get channel config info
        channel_info = self.channel_configs.get(num_channels, {
            'name': f'{num_channels}-channel',
            'description': f'{num_channels} channel audio',
            'asr_compatible': num_channels <= 2,
            'use_cases': []
        })

        # ASR typically requires mono
        if use_case.lower() in ['asr', 'speech_recognition']:
            valid = num_channels <= 2
            requires_conversion = num_channels > 1
        else:
            valid = True
            requires_conversion = False

        return {
            'valid': valid,
            'num_channels': num_channels,
            'channel_info': channel_info,
            'asr_compatible': channel_info['asr_compatible'],
            'requires_conversion': requires_conversion,
            'recommendations': self._get_channel_recommendations(num_channels, use_case)
        }

    def _get_channel_recommendations(
        self,
        num_channels: int,
        use_case: str
    ) -> List[str]:
        """Get recommendations for channel configuration."""
        recommendations = []

        if use_case.lower() in ['asr', 'speech_recognition']:
            if num_channels > 1:
                recommendations.append('Convert to mono for ASR processing')
            if num_channels > 2:
                recommendations.append('Multi-channel audio should be downmixed')

        return recommendations

    def convert_to_mono(
        self,
        signal: np.ndarray,
        method: str = 'average'
    ) -> np.ndarray:
        """
        Convert multi-channel audio to mono.

        Args:
            signal: Audio signal (samples x channels or samples)
            method: Conversion method ('average', 'left', 'right')

        Returns:
            Mono audio signal

        Example:
            >>> stereo = np.random.randn(1000, 2)
            >>> mono = service.convert_to_mono(stereo)
            >>> print(mono.shape)
            (1000,)
        """
        if signal.ndim == 1:
            return signal

        if signal.ndim != 2:
            raise ValueError("Signal must be 1D or 2D array")

        if method == 'average':
            return np.mean(signal, axis=1)
        elif method == 'left':
            return signal[:, 0]
        elif method == 'right':
            return signal[:, -1]
        else:
            return np.mean(signal, axis=1)

    def analyze_channel_impact(
        self,
        source_channels: int,
        target_channels: int
    ) -> Dict[str, Any]:
        """
        Analyze impact of channel conversion.

        Args:
            source_channels: Source number of channels
            target_channels: Target number of channels

        Returns:
            Dictionary with channel impact analysis

        Example:
            >>> impact = service.analyze_channel_impact(2, 1)
            >>> print(f"Quality loss: {impact['quality_loss']:.1f}%")
        """
        if source_channels == target_channels:
            return {
                'source_channels': source_channels,
                'target_channels': target_channels,
                'operation': 'none',
                'quality_loss': 0.0,
                'spatial_loss': 0.0,
                'asr_impact': 'none',
                'recommendation': 'acceptable'
            }

        if target_channels < source_channels:
            # Downmixing
            operation = 'downmix'
            quality_loss = (source_channels - target_channels) * 5.0
            spatial_loss = ((source_channels - target_channels) / source_channels) * 100
        else:
            # Upmixing
            operation = 'upmix'
            quality_loss = 0.0
            spatial_loss = 0.0

        # ASR impact
        if target_channels == 1:
            asr_impact = 'optimal'
        elif target_channels == 2:
            asr_impact = 'minimal'
        else:
            asr_impact = 'requires_conversion'

        return {
            'source_channels': source_channels,
            'target_channels': target_channels,
            'operation': operation,
            'quality_loss': float(min(100, quality_loss)),
            'spatial_loss': float(spatial_loss),
            'asr_impact': asr_impact,
            'recommendation': (
                'acceptable' if quality_loss < 10
                else 'caution' if quality_loss < 30
                else 'not_recommended'
            )
        }

    def get_bit_depth_metrics(
        self,
        bit_depth: int,
        signal: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive bit depth metrics.

        Args:
            bit_depth: Bit depth to analyze
            signal: Optional audio signal for analysis

        Returns:
            Dictionary with all bit depth metrics

        Example:
            >>> metrics = service.get_bit_depth_metrics(16)
            >>> print(f"Quality: {metrics['asr_quality']}")
        """
        validation = self.validate_bit_depth(bit_depth, 'asr')
        dynamic_range = self.calculate_dynamic_range(bit_depth)

        # Depth classification
        if bit_depth >= 24:
            classification = 'professional'
        elif bit_depth >= 16:
            classification = 'standard'
        else:
            classification = 'legacy'

        # Signal analysis if provided
        if signal is not None and len(signal) > 0:
            actual_dynamic_range = self._measure_actual_dynamic_range(signal)
            samples = len(signal)
        else:
            actual_dynamic_range = 0.0
            samples = 0

        return {
            'bit_depth': bit_depth,
            'dynamic_range': dynamic_range,
            'classification': classification,
            'is_standard': bit_depth in self.supported_bit_depths,
            'validation': validation,
            'asr_quality': validation['asr_quality'],
            'actual_dynamic_range': float(actual_dynamic_range),
            'total_samples': samples,
            'recommended_for_asr': bit_depth >= 16,
            'optimal_depth': self.BIT_DEPTH_16
        }

    def _measure_actual_dynamic_range(self, signal: np.ndarray) -> float:
        """Measure actual dynamic range from signal."""
        if len(signal) == 0:
            return 0.0

        signal = signal.astype(np.float64)
        signal_max = np.max(np.abs(signal))
        signal_min = np.min(np.abs(signal[signal != 0])) if np.any(signal != 0) else 1e-10

        if signal_max == 0:
            return 0.0

        return float(20 * np.log10(signal_max / signal_min))

