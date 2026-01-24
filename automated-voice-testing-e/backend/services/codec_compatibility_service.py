"""
Codec Compatibility Service for ASR audio testing.

This service provides tools for testing and analyzing how different audio
codecs impact ASR performance. Different codecs have varying characteristics
that can affect transcription accuracy.

Supported codecs:
- G.711: mu-law and A-law telephony codecs (64 kbps)
- G.722: Wideband codec (48-64 kbps)
- Opus: Versatile codec (6-510 kbps)
- AAC: Advanced Audio Coding (32-320 kbps)
- MP3: MPEG Audio Layer III (32-320 kbps)
- Speex: Open source speech codec (2.15-44.2 kbps)

Example:
    >>> service = CodecCompatibilityService()
    >>> info = service.get_codec_info('opus')
    >>> print(f"Bitrate range: {info['min_bitrate']}-{info['max_bitrate']} kbps")
"""

from typing import List, Dict, Any, Optional


class CodecCompatibilityService:
    """
    Service for testing codec compatibility with ASR systems.

    Provides methods for retrieving codec information, measuring
    transcoding impact, and recommending optimal codecs for ASR.

    Attributes:
        codecs: Dictionary of supported codec specifications

    Example:
        >>> service = CodecCompatibilityService()
        >>> recommendation = service.recommend_codec('voip')
        >>> print(f"Recommended: {recommendation}")
    """

    # Codec identifiers
    CODEC_G711_MULAW = 'g711_mulaw'
    CODEC_G711_ALAW = 'g711_alaw'
    CODEC_G722 = 'g722'
    CODEC_OPUS = 'opus'
    CODEC_AAC = 'aac'
    CODEC_MP3 = 'mp3'
    CODEC_SPEEX = 'speex'
    CODEC_PCM = 'pcm'

    def __init__(self):
        """Initialize the codec compatibility service."""
        self.codecs: Dict[str, Dict[str, Any]] = {
            self.CODEC_G711_MULAW: {
                'name': 'G.711 mu-law',
                'type': 'telephony',
                'sample_rate': 8000,
                'bitrate': 64,
                'min_bitrate': 64,
                'max_bitrate': 64,
                'lossy': True,
                'asr_compatibility': 'good',
                'description': 'North American telephony standard'
            },
            self.CODEC_G711_ALAW: {
                'name': 'G.711 A-law',
                'type': 'telephony',
                'sample_rate': 8000,
                'bitrate': 64,
                'min_bitrate': 64,
                'max_bitrate': 64,
                'lossy': True,
                'asr_compatibility': 'good',
                'description': 'European telephony standard'
            },
            self.CODEC_G722: {
                'name': 'G.722',
                'type': 'wideband',
                'sample_rate': 16000,
                'bitrate': 64,
                'min_bitrate': 48,
                'max_bitrate': 64,
                'lossy': True,
                'asr_compatibility': 'excellent',
                'description': 'Wideband telephony codec'
            },
            self.CODEC_OPUS: {
                'name': 'Opus',
                'type': 'versatile',
                'sample_rate': 48000,
                'bitrate': 64,
                'min_bitrate': 6,
                'max_bitrate': 510,
                'lossy': True,
                'asr_compatibility': 'excellent',
                'description': 'Modern versatile codec'
            },
            self.CODEC_AAC: {
                'name': 'AAC',
                'type': 'consumer',
                'sample_rate': 44100,
                'bitrate': 128,
                'min_bitrate': 32,
                'max_bitrate': 320,
                'lossy': True,
                'asr_compatibility': 'good',
                'description': 'Advanced Audio Coding'
            },
            self.CODEC_MP3: {
                'name': 'MP3',
                'type': 'consumer',
                'sample_rate': 44100,
                'bitrate': 128,
                'min_bitrate': 32,
                'max_bitrate': 320,
                'lossy': True,
                'asr_compatibility': 'fair',
                'description': 'MPEG Audio Layer III'
            },
            self.CODEC_SPEEX: {
                'name': 'Speex',
                'type': 'speech',
                'sample_rate': 16000,
                'bitrate': 15,
                'min_bitrate': 2,
                'max_bitrate': 44,
                'lossy': True,
                'asr_compatibility': 'good',
                'description': 'Open source speech codec'
            },
            self.CODEC_PCM: {
                'name': 'PCM',
                'type': 'uncompressed',
                'sample_rate': 44100,
                'bitrate': 1411,
                'min_bitrate': 128,
                'max_bitrate': 4608,
                'lossy': False,
                'asr_compatibility': 'excellent',
                'description': 'Uncompressed audio'
            }
        }

    def get_supported_codecs(self) -> List[str]:
        """
        Get list of supported codec identifiers.

        Returns:
            List of codec identifier strings

        Example:
            >>> codecs = service.get_supported_codecs()
            >>> print(codecs)
            ['g711_mulaw', 'g711_alaw', 'g722', ...]
        """
        return list(self.codecs.keys())

    def get_codec_info(self, codec: str) -> Dict[str, Any]:
        """
        Get detailed information about a codec.

        Args:
            codec: Codec identifier

        Returns:
            Dictionary with codec specifications

        Example:
            >>> info = service.get_codec_info('opus')
            >>> print(f"Max bitrate: {info['max_bitrate']} kbps")
        """
        if codec in self.codecs:
            return self.codecs[codec].copy()

        return {
            'name': 'Unknown',
            'type': 'unknown',
            'sample_rate': 0,
            'bitrate': 0,
            'min_bitrate': 0,
            'max_bitrate': 0,
            'lossy': True,
            'asr_compatibility': 'unknown',
            'description': 'Unknown codec'
        }

    def measure_transcoding_impact(
        self,
        source_codec: str,
        target_codec: str,
        bitrate: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Measure the impact of transcoding between codecs.

        Estimates quality degradation from codec conversion.

        Args:
            source_codec: Source codec identifier
            target_codec: Target codec identifier
            bitrate: Target bitrate (optional)

        Returns:
            Dictionary with transcoding impact metrics

        Example:
            >>> impact = service.measure_transcoding_impact('pcm', 'opus')
            >>> print(f"Quality loss: {impact['quality_loss']:.1f}%")
        """
        source_info = self.get_codec_info(source_codec)
        target_info = self.get_codec_info(target_codec)

        # Estimate quality loss based on codec characteristics
        quality_loss = 0.0

        # Lossy to lossy transcoding adds more artifacts
        if source_info['lossy'] and target_info['lossy']:
            quality_loss += 5.0

        # Sample rate downsampling causes loss
        if target_info['sample_rate'] < source_info['sample_rate']:
            ratio = source_info['sample_rate'] / target_info['sample_rate']
            quality_loss += (ratio - 1) * 10

        # Lower bitrate causes loss
        target_bitrate = bitrate or target_info['bitrate']
        if target_bitrate < source_info['bitrate']:
            ratio = source_info['bitrate'] / target_bitrate
            quality_loss += (ratio - 1) * 5

        # ASR compatibility impact
        compat_scores = {
            'excellent': 0,
            'good': 2,
            'fair': 5,
            'poor': 10,
            'unknown': 5
        }

        source_compat = compat_scores.get(source_info['asr_compatibility'], 5)
        target_compat = compat_scores.get(target_info['asr_compatibility'], 5)
        quality_loss += max(0, target_compat - source_compat)

        # Estimate WER increase
        wer_increase = quality_loss * 0.5

        return {
            'source_codec': source_codec,
            'target_codec': target_codec,
            'quality_loss': min(100.0, float(quality_loss)),
            'estimated_wer_increase': float(wer_increase),
            'sample_rate_change': (
                source_info['sample_rate'],
                target_info['sample_rate']
            ),
            'bitrate_change': (
                source_info['bitrate'],
                target_bitrate
            ),
            'recommendation': (
                'acceptable' if quality_loss < 10
                else 'caution' if quality_loss < 20
                else 'not_recommended'
            )
        }

    def recommend_codec(self, use_case: str) -> str:
        """
        Recommend optimal codec for a use case.

        Args:
            use_case: Use case type ('voip', 'broadcast', 'storage', 'asr')

        Returns:
            Recommended codec identifier

        Example:
            >>> codec = service.recommend_codec('voip')
            >>> print(f"Recommended: {codec}")
        """
        recommendations = {
            'voip': self.CODEC_OPUS,
            'telephony': self.CODEC_G711_MULAW,
            'wideband_telephony': self.CODEC_G722,
            'broadcast': self.CODEC_AAC,
            'storage': self.CODEC_PCM,
            'asr': self.CODEC_OPUS,
            'low_bandwidth': self.CODEC_SPEEX,
            'streaming': self.CODEC_OPUS
        }

        return recommendations.get(use_case.lower(), self.CODEC_OPUS)

    def analyze_bitrate_impact(
        self,
        codec: str,
        bitrates: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Analyze impact of different bitrates on codec quality.

        Args:
            codec: Codec identifier
            bitrates: List of bitrates to analyze (optional)

        Returns:
            Dictionary with bitrate impact analysis

        Example:
            >>> analysis = service.analyze_bitrate_impact('opus')
            >>> for br in analysis['bitrate_analysis']:
            ...     print(f"{br['bitrate']} kbps: {br['quality']}")
        """
        codec_info = self.get_codec_info(codec)

        if bitrates is None:
            # Default bitrate range
            min_br = codec_info['min_bitrate']
            max_br = codec_info['max_bitrate']

            if max_br > min_br:
                step = (max_br - min_br) // 4
                bitrates = [
                    min_br,
                    min_br + step,
                    min_br + 2 * step,
                    min_br + 3 * step,
                    max_br
                ]
            else:
                bitrates = [min_br]

        analysis = []
        for bitrate in bitrates:
            # Quality estimation based on bitrate
            if codec_info['max_bitrate'] > codec_info['min_bitrate']:
                quality_pct = (
                    (bitrate - codec_info['min_bitrate']) /
                    (codec_info['max_bitrate'] - codec_info['min_bitrate'])
                ) * 100
            else:
                quality_pct = 100.0

            # Classify quality level
            if quality_pct >= 80:
                quality_level = 'excellent'
            elif quality_pct >= 60:
                quality_level = 'good'
            elif quality_pct >= 40:
                quality_level = 'fair'
            else:
                quality_level = 'poor'

            # Estimate WER based on quality
            base_wer = 5.0  # Base WER for excellent quality
            wer_multiplier = 1 + (100 - quality_pct) / 50
            estimated_wer = base_wer * wer_multiplier

            analysis.append({
                'bitrate': bitrate,
                'quality_percentage': float(quality_pct),
                'quality': quality_level,
                'estimated_wer': float(estimated_wer),
                'recommended_for_asr': quality_pct >= 50
            })

        return {
            'codec': codec,
            'codec_name': codec_info['name'],
            'bitrate_range': (codec_info['min_bitrate'], codec_info['max_bitrate']),
            'bitrate_analysis': analysis,
            'optimal_bitrate': codec_info['max_bitrate'],
            'minimum_asr_bitrate': self._get_minimum_asr_bitrate(codec)
        }

    def _get_minimum_asr_bitrate(self, codec: str) -> int:
        """Get minimum bitrate recommended for ASR."""
        minimum_bitrates = {
            self.CODEC_OPUS: 16,
            self.CODEC_AAC: 64,
            self.CODEC_MP3: 96,
            self.CODEC_SPEEX: 8,
            self.CODEC_G711_MULAW: 64,
            self.CODEC_G711_ALAW: 64,
            self.CODEC_G722: 48,
            self.CODEC_PCM: 128
        }
        return minimum_bitrates.get(codec, 32)

    def get_compatibility_metrics(
        self,
        codec: str,
        bitrate: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive codec compatibility metrics.

        Args:
            codec: Codec identifier
            bitrate: Specific bitrate to analyze (optional)

        Returns:
            Dictionary with all compatibility metrics

        Example:
            >>> metrics = service.get_compatibility_metrics('opus', 64)
            >>> print(f"ASR compatibility: {metrics['asr_compatibility']}")
        """
        codec_info = self.get_codec_info(codec)
        bitrate_analysis = self.analyze_bitrate_impact(codec, [bitrate] if bitrate else None)

        # Calculate overall score
        compat_scores = {
            'excellent': 95,
            'good': 80,
            'fair': 60,
            'poor': 40,
            'unknown': 50
        }

        base_score = compat_scores.get(codec_info['asr_compatibility'], 50)

        # Adjust for bitrate
        if bitrate:
            if bitrate < self._get_minimum_asr_bitrate(codec):
                base_score -= 20
            elif bitrate >= codec_info['max_bitrate'] * 0.8:
                base_score += 5

        return {
            'codec': codec,
            'codec_info': codec_info,
            'asr_compatibility': codec_info['asr_compatibility'],
            'overall_score': min(100, max(0, base_score)),
            'bitrate_analysis': bitrate_analysis,
            'recommended_settings': {
                'sample_rate': codec_info['sample_rate'],
                'bitrate': codec_info['max_bitrate'],
                'min_asr_bitrate': self._get_minimum_asr_bitrate(codec)
            },
            'potential_issues': self._identify_potential_issues(codec, bitrate)
        }

    def _identify_potential_issues(
        self,
        codec: str,
        bitrate: Optional[int] = None
    ) -> List[str]:
        """Identify potential issues with codec/bitrate combination."""
        issues = []
        codec_info = self.get_codec_info(codec)

        # Sample rate issues
        if codec_info['sample_rate'] < 16000:
            issues.append('Low sample rate may limit frequency response')

        # Bitrate issues
        if bitrate:
            if bitrate < self._get_minimum_asr_bitrate(codec):
                issues.append('Bitrate below recommended minimum for ASR')

        # Codec-specific issues
        if codec == self.CODEC_MP3:
            issues.append('MP3 not optimized for speech')

        if codec_info['asr_compatibility'] in ['fair', 'poor']:
            issues.append('Codec not optimized for ASR use')

        return issues
