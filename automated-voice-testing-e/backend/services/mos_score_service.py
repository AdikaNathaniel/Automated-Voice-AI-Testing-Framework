"""
MOS Score Calculation Service for voice quality assessment.

This service provides Mean Opinion Score calculation
using the E-model for voice quality measurement.

Key features:
- R-factor calculation
- MOS score computation
- Quality degradation factors
- Quality classification

Example:
    >>> service = MOSScoreService()
    >>> mos = service.calculate_mos(delay=100, jitter=20, packet_loss=1.0)
    >>> print(f"MOS: {mos['mos']:.2f}")
"""

from typing import List, Dict, Any
from datetime import datetime

# Import analytics mixin
from services.mos_analytics import MOSAnalyticsMixin


class MOSScoreService(MOSAnalyticsMixin):
    """
    Service for MOS (Mean Opinion Score) calculation.

    Provides R-factor calculation, MOS computation,
    quality degradation analysis, and classification.

    Example:
        >>> service = MOSScoreService()
        >>> quality = service.classify_quality(4.2)
        >>> print(f"Quality: {quality['classification']}")
    """

    def __init__(self):
        """Initialize the MOS score service."""
        self._history: List[Dict[str, Any]] = []
        self._codec_impairments = {
            'G.711': 0,
            'G.729': 10,
            'G.723.1': 15,
            'iLBC': 11,
            'opus': 0
        }
        self._thresholds = {
            'excellent': 4.3,
            'good': 4.0,
            'fair': 3.6,
            'poor': 3.1,
            'bad': 0.0
        }
        self._alerts: List[Dict[str, Any]] = []
        self._alert_threshold: float = 3.0

    def calculate_r_factor(
        self,
        delay: float = 0,
        jitter: float = 0,
        packet_loss: float = 0,
        codec: str = "G.711"
    ) -> Dict[str, Any]:
        """
        Calculate R-factor using E-model.

        Args:
            delay: One-way delay in ms
            jitter: Jitter in ms
            packet_loss: Packet loss percentage
            codec: Codec name

        Returns:
            Dictionary with R-factor calculation

        Example:
            >>> r = service.calculate_r_factor(delay=100, packet_loss=1.0)
        """
        # E-model base R-factor
        R0 = 93.2

        # Get impairments
        Id = self.get_delay_impairment(delay)['impairment']
        Ie = self.get_equipment_impairment(codec)['impairment']
        Ipl = self.calculate_packet_loss_impairment(packet_loss)['impairment']
        Ij = self.calculate_jitter_impairment(jitter)['impairment']

        # Calculate R-factor
        R = R0 - Id - Ie - Ipl - Ij

        # Clamp to valid range
        R = max(0, min(100, R))

        return {
            'r_factor': R,
            'base_r': R0,
            'delay_impairment': Id,
            'equipment_impairment': Ie,
            'packet_loss_impairment': Ipl,
            'jitter_impairment': Ij,
            'calculated_at': datetime.utcnow().isoformat()
        }

    def get_delay_impairment(self, delay: float) -> Dict[str, Any]:
        """
        Get delay impairment factor (Id).

        Args:
            delay: One-way delay in ms

        Returns:
            Dictionary with impairment value

        Example:
            >>> id = service.get_delay_impairment(150)
        """
        # Simplified E-model delay impairment
        if delay <= 150:
            impairment = 0.024 * delay
        else:
            impairment = 0.024 * delay + 0.11 * (delay - 150)

        return {
            'delay_ms': delay,
            'impairment': impairment
        }

    def get_equipment_impairment(self, codec: str) -> Dict[str, Any]:
        """
        Get equipment impairment factor (Ie).

        Args:
            codec: Codec name

        Returns:
            Dictionary with impairment value

        Example:
            >>> ie = service.get_equipment_impairment('G.729')
        """
        impairment = self._codec_impairments.get(codec, 0)

        return {
            'codec': codec,
            'impairment': impairment
        }

    def calculate_mos(
        self,
        delay: float = 0,
        jitter: float = 0,
        packet_loss: float = 0,
        codec: str = "G.711"
    ) -> Dict[str, Any]:
        """
        Calculate MOS score.

        Args:
            delay: One-way delay in ms
            jitter: Jitter in ms
            packet_loss: Packet loss percentage
            codec: Codec name

        Returns:
            Dictionary with MOS score

        Example:
            >>> mos = service.calculate_mos(delay=100, packet_loss=0.5)
        """
        r_result = self.calculate_r_factor(delay, jitter, packet_loss, codec)
        R = r_result['r_factor']

        # Convert R to MOS
        mos = self.r_to_mos(R)['mos']

        return {
            'mos': mos,
            'r_factor': R,
            'delay_ms': delay,
            'jitter_ms': jitter,
            'packet_loss': packet_loss,
            'codec': codec,
            'classification': self.classify_quality(mos)['classification'],
            'calculated_at': datetime.utcnow().isoformat()
        }

    def calculate_mos_lq(
        self,
        delay: float = 0,
        jitter: float = 0,
        packet_loss: float = 0,
        codec: str = "G.711"
    ) -> Dict[str, Any]:
        """
        Calculate MOS-LQ (Listening Quality).

        Args:
            delay: One-way delay in ms
            jitter: Jitter in ms
            packet_loss: Packet loss percentage
            codec: Codec name

        Returns:
            Dictionary with MOS-LQ score

        Example:
            >>> mos_lq = service.calculate_mos_lq(delay=100)
        """
        # MOS-LQ focuses on listening quality without conversational factors
        result = self.calculate_mos(delay, jitter, packet_loss, codec)
        result['type'] = 'MOS-LQ'
        return result

    def calculate_mos_cq(
        self,
        delay: float = 0,
        jitter: float = 0,
        packet_loss: float = 0,
        codec: str = "G.711"
    ) -> Dict[str, Any]:
        """
        Calculate MOS-CQ (Conversational Quality).

        Args:
            delay: One-way delay in ms
            jitter: Jitter in ms
            packet_loss: Packet loss percentage
            codec: Codec name

        Returns:
            Dictionary with MOS-CQ score

        Example:
            >>> mos_cq = service.calculate_mos_cq(delay=100)
        """
        # MOS-CQ includes conversational factors (delay more impactful)
        result = self.calculate_mos(delay * 1.2, jitter, packet_loss, codec)
        result['type'] = 'MOS-CQ'
        return result

    def r_to_mos(self, r_factor: float) -> Dict[str, Any]:
        """
        Convert R-factor to MOS.

        Args:
            r_factor: R-factor value (0-100)

        Returns:
            Dictionary with MOS value

        Example:
            >>> mos = service.r_to_mos(80)
        """
        # ITU-T G.107 conversion formula
        if r_factor < 0:
            mos = 1.0
        elif r_factor > 100:
            mos = 4.5
        else:
            mos = 1 + 0.035 * r_factor + r_factor * (r_factor - 60) * (100 - r_factor) * 7e-6

        # Clamp to MOS scale
        mos = max(1.0, min(5.0, mos))

        return {
            'r_factor': r_factor,
            'mos': mos
        }

    def calculate_packet_loss_impairment(
        self,
        packet_loss: float
    ) -> Dict[str, Any]:
        """
        Calculate packet loss impairment.

        Args:
            packet_loss: Packet loss percentage

        Returns:
            Dictionary with impairment value

        Example:
            >>> ipl = service.calculate_packet_loss_impairment(2.0)
        """
        # Simplified packet loss impairment
        impairment = 30 * packet_loss / (packet_loss + 15)

        return {
            'packet_loss': packet_loss,
            'impairment': impairment
        }

    def calculate_jitter_impairment(
        self,
        jitter: float
    ) -> Dict[str, Any]:
        """
        Calculate jitter impairment.

        Args:
            jitter: Jitter in ms

        Returns:
            Dictionary with impairment value

        Example:
            >>> ij = service.calculate_jitter_impairment(30)
        """
        # Simplified jitter impairment
        impairment = 0.1 * jitter

        return {
            'jitter_ms': jitter,
            'impairment': impairment
        }

    def calculate_codec_impairment(self, codec: str) -> Dict[str, Any]:
        """
        Calculate codec-specific impairment.

        Args:
            codec: Codec name

        Returns:
            Dictionary with impairment value

        Example:
            >>> ic = service.calculate_codec_impairment('G.729')
        """
        return self.get_equipment_impairment(codec)


    def calculate_ie(self, codec: str) -> Dict[str, Any]:
        """
        Calculate equipment impairment (Ie).

        Args:
            codec: Codec name

        Returns:
            Dictionary with Ie value

        Example:
            >>> ie = service.calculate_ie('G.729')
        """
        return self.get_equipment_impairment(codec)

    def calculate_id(self, delay: float) -> Dict[str, Any]:
        """
        Calculate delay impairment (Id).

        Args:
            delay: One-way delay in ms

        Returns:
            Dictionary with Id value

        Example:
            >>> id = service.calculate_id(150)
        """
        return self.get_delay_impairment(delay)

    def calculate_mos_from_metrics(
        self,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate MOS from a metrics dictionary.

        Args:
            metrics: Dictionary with delay, jitter, packet_loss, codec

        Returns:
            Dictionary with MOS calculation

        Example:
            >>> mos = service.calculate_mos_from_metrics({'delay': 100, 'jitter': 20})
        """
        return self.calculate_mos(
            delay=metrics.get('delay', 0),
            jitter=metrics.get('jitter', 0),
            packet_loss=metrics.get('packet_loss', 0),
            codec=metrics.get('codec', 'G.711')
        )

    def estimate_mos(
        self,
        delay: float = 0,
        jitter: float = 0,
        packet_loss: float = 0
    ) -> float:
        """
        Estimate MOS score (returns just the value).

        Args:
            delay: One-way delay in ms
            jitter: Jitter in ms
            packet_loss: Packet loss percentage

        Returns:
            MOS score value

        Example:
            >>> mos = service.estimate_mos(delay=100)
        """
        result = self.calculate_mos(delay, jitter, packet_loss)
        return result['mos']
