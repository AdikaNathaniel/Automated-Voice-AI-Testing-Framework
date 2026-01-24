"""
MOS Analytics Mixin for quality classification, history, and thresholds.

This mixin provides analytics methods for MOSScoreService:
- Quality classification
- History recording and retrieval
- Statistics calculation
- Threshold monitoring and alerts

Extracted from mos_score_service.py to maintain 500-line limit per file.

Example:
    >>> class MOSScoreService(MOSAnalyticsMixin):
    ...     pass
"""

from typing import List, Dict, Any
from datetime import datetime
import uuid


class MOSAnalyticsMixin:
    """
    Mixin providing analytics methods for MOSScoreService.

    This mixin contains:
    - Quality classification methods
    - History tracking methods
    - Statistics methods
    - Threshold and alert methods
    """

    def classify_quality(self, mos: float) -> Dict[str, Any]:
        """
        Classify voice quality based on MOS.

        Args:
            mos: MOS score

        Returns:
            Dictionary with quality classification

        Example:
            >>> quality = service.classify_quality(4.2)
        """
        if mos >= self._thresholds['excellent']:
            classification = 'excellent'
        elif mos >= self._thresholds['good']:
            classification = 'good'
        elif mos >= self._thresholds['fair']:
            classification = 'fair'
        elif mos >= self._thresholds['poor']:
            classification = 'poor'
        else:
            classification = 'bad'

        return {
            'mos': mos,
            'classification': classification,
            'acceptable': mos >= self._thresholds['fair']
        }

    def get_quality_thresholds(self) -> Dict[str, float]:
        """
        Get quality classification thresholds.

        Returns:
            Dictionary with threshold values

        Example:
            >>> thresholds = service.get_quality_thresholds()
        """
        return self._thresholds.copy()

    def is_acceptable_quality(self, mos: float) -> bool:
        """
        Check if MOS indicates acceptable quality.

        Args:
            mos: MOS score

        Returns:
            True if quality is acceptable

        Example:
            >>> acceptable = service.is_acceptable_quality(3.8)
        """
        return mos >= self._thresholds['fair']

    def get_mos_rating(self, mos: float) -> Dict[str, Any]:
        """
        Get quality rating for a MOS score.

        Args:
            mos: MOS score

        Returns:
            Dictionary with rating info

        Example:
            >>> rating = service.get_mos_rating(4.2)
        """
        classification = self.classify_quality(mos)

        ratings = {
            'excellent': 5,
            'good': 4,
            'fair': 3,
            'poor': 2,
            'bad': 1
        }

        return {
            'mos': mos,
            'classification': classification['classification'],
            'rating': ratings.get(classification['classification'], 1),
            'acceptable': classification['acceptable']
        }

    def record_call_metrics(
        self,
        call_id: str,
        delay: float,
        jitter: float,
        packet_loss: float,
        codec: str = "G.711"
    ) -> Dict[str, Any]:
        """
        Record call metrics and calculate MOS.

        Args:
            call_id: Call identifier
            delay: One-way delay in ms
            jitter: Jitter in ms
            packet_loss: Packet loss percentage
            codec: Codec name

        Returns:
            Dictionary with recorded metrics and MOS

        Example:
            >>> result = service.record_call_metrics('call-1', 100, 20, 0.5)
        """
        mos_result = self.calculate_mos(delay, jitter, packet_loss, codec)

        record = {
            'id': str(uuid.uuid4()),
            'call_id': call_id,
            'mos': mos_result['mos'],
            'r_factor': mos_result['r_factor'],
            'delay_ms': delay,
            'jitter_ms': jitter,
            'packet_loss': packet_loss,
            'codec': codec,
            'classification': mos_result['classification'],
            'recorded_at': datetime.utcnow().isoformat()
        }
        self._history.append(record)

        return record

    def get_mos_history(
        self,
        call_id: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get MOS calculation history.

        Args:
            call_id: Optional call ID filter
            limit: Maximum records to return

        Returns:
            List of MOS records

        Example:
            >>> history = service.get_mos_history(limit=50)
        """
        history = self._history
        if call_id:
            history = [h for h in history if h.get('call_id') == call_id]

        return history[-limit:]

    def get_average_mos(self, call_id: str = None) -> Dict[str, Any]:
        """
        Get average MOS score.

        Args:
            call_id: Optional call ID filter

        Returns:
            Dictionary with average MOS

        Example:
            >>> avg = service.get_average_mos()
        """
        history = self._history
        if call_id:
            history = [h for h in history if h.get('call_id') == call_id]

        if not history:
            return {
                'average_mos': 0.0,
                'sample_count': 0
            }

        total_mos = sum(h.get('mos', 0) for h in history)
        avg_mos = total_mos / len(history)

        return {
            'average_mos': avg_mos,
            'sample_count': len(history),
            'classification': self.classify_quality(avg_mos)['classification']
        }

    def record_mos(
        self,
        mos: float,
        call_id: str = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Record a MOS score.

        Args:
            mos: MOS score to record
            call_id: Optional call identifier
            metadata: Optional metadata

        Returns:
            Dictionary with recorded info

        Example:
            >>> result = service.record_mos(4.2, call_id='call-1')
        """
        record = {
            'id': str(uuid.uuid4()),
            'mos': mos,
            'call_id': call_id,
            'classification': self.classify_quality(mos)['classification'],
            'metadata': metadata or {},
            'recorded_at': datetime.utcnow().isoformat()
        }
        self._history.append(record)

        # Check threshold
        self.check_threshold(mos)

        return record

    def get_mos_statistics(
        self,
        call_id: str = None
    ) -> Dict[str, Any]:
        """
        Get MOS statistics.

        Args:
            call_id: Optional call ID filter

        Returns:
            Dictionary with statistics

        Example:
            >>> stats = service.get_mos_statistics()
        """
        history = self._history
        if call_id:
            history = [h for h in history if h.get('call_id') == call_id]

        if not history:
            return {
                'count': 0,
                'average': 0.0,
                'min': 0.0,
                'max': 0.0,
                'std_dev': 0.0
            }

        mos_values = [h.get('mos', 0) for h in history]
        count = len(mos_values)
        avg = sum(mos_values) / count
        min_mos = min(mos_values)
        max_mos = max(mos_values)

        # Calculate standard deviation
        variance = sum((x - avg) ** 2 for x in mos_values) / count
        std_dev = variance ** 0.5

        return {
            'count': count,
            'average': avg,
            'min': min_mos,
            'max': max_mos,
            'std_dev': std_dev,
            'classification': self.classify_quality(avg)['classification']
        }

    def set_threshold(self, threshold: float) -> Dict[str, Any]:
        """
        Set alert threshold for MOS score.

        Args:
            threshold: MOS threshold for alerts

        Returns:
            Dictionary with threshold config

        Example:
            >>> service.set_threshold(3.5)
        """
        self._alert_threshold = threshold
        return {
            'threshold': threshold,
            'set_at': datetime.utcnow().isoformat()
        }

    def check_threshold(self, mos: float) -> Dict[str, Any]:
        """
        Check if MOS meets threshold.

        Args:
            mos: MOS score to check

        Returns:
            Dictionary with check result

        Example:
            >>> result = service.check_threshold(3.8)
        """
        meets_threshold = mos >= self._alert_threshold

        if not meets_threshold:
            alert = {
                'id': str(uuid.uuid4()),
                'mos': mos,
                'threshold': self._alert_threshold,
                'created_at': datetime.utcnow().isoformat()
            }
            self._alerts.append(alert)

        return {
            'mos': mos,
            'threshold': self._alert_threshold,
            'meets_threshold': meets_threshold,
            'alert_generated': not meets_threshold
        }

    def get_alerts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get MOS alerts.

        Args:
            limit: Maximum alerts to return

        Returns:
            List of alerts

        Example:
            >>> alerts = service.get_alerts()
        """
        return self._alerts[-limit:]

    def clear_alerts(self) -> Dict[str, Any]:
        """
        Clear all alerts.

        Returns:
            Dictionary with clear result

        Example:
            >>> result = service.clear_alerts()
        """
        count = len(self._alerts)
        self._alerts = []
        return {
            'cleared': True,
            'count': count
        }
