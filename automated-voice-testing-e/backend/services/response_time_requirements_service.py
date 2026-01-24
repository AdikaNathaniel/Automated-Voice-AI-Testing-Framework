"""
Response Time Requirements Service for voice AI testing.

This service provides response time validation for
automotive voice AI testing with industry benchmarks.

Key features:
- End-to-end latency validation
- Wake word detection timing
- Speech processing timing
- NLP/Intent processing timing
- TTS generation timing
- Perception threshold validation
- Latency percentile tracking

Example:
    >>> service = ResponseTimeRequirementsService()
    >>> result = service.validate_end_to_end_latency(450)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class ResponseTimeRequirementsService:
    """
    Service for response time requirements validation.

    Provides automotive voice AI testing for latency
    validation against industry benchmarks.

    Example:
        >>> service = ResponseTimeRequirementsService()
        >>> config = service.get_response_time_config()
    """

    def __init__(self):
        """Initialize the response time requirements service."""
        self._latency_history: List[float] = []
        self._thresholds = {
            'end_to_end_ideal': 500,
            'end_to_end_acceptable': 800,
            'wake_word': 200,
            'stt': 200,
            'nlp': 200,
            'tts': 100,
            'perception': 120,
            'total_simple': 1000
        }

    def validate_end_to_end_latency(
        self,
        latency_ms: float
    ) -> Dict[str, Any]:
        """
        Validate end-to-end latency against thresholds.

        Args:
            latency_ms: Measured latency in milliseconds

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_end_to_end_latency(450)
        """
        validation_id = str(uuid.uuid4())

        is_ideal = latency_ms <= self._thresholds['end_to_end_ideal']
        is_acceptable = latency_ms <= self._thresholds['end_to_end_acceptable']

        return {
            'validation_id': validation_id,
            'latency_ms': latency_ms,
            'is_ideal': is_ideal,
            'is_acceptable': is_acceptable,
            'ideal_threshold_ms': self._thresholds['end_to_end_ideal'],
            'acceptable_threshold_ms': self._thresholds['end_to_end_acceptable'],
            'rating': 'ideal' if is_ideal else 'acceptable' if is_acceptable else 'unacceptable',
            'validated_at': datetime.utcnow().isoformat()
        }

    def get_latency_thresholds(self) -> Dict[str, Any]:
        """
        Get all latency thresholds.

        Returns:
            Dictionary with thresholds

        Example:
            >>> thresholds = service.get_latency_thresholds()
        """
        return {
            'thresholds': self._thresholds,
            'units': 'milliseconds',
            'source': 'industry_research',
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def validate_wake_word_detection(
        self,
        latency_ms: float
    ) -> Dict[str, Any]:
        """
        Validate wake word detection time.

        Args:
            latency_ms: Detection latency in milliseconds

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_wake_word_detection(150)
        """
        validation_id = str(uuid.uuid4())

        threshold = self._thresholds['wake_word']
        passed = latency_ms <= threshold

        return {
            'validation_id': validation_id,
            'latency_ms': latency_ms,
            'threshold_ms': threshold,
            'passed': passed,
            'margin_ms': threshold - latency_ms,
            'component': 'wake_word_detection',
            'validated_at': datetime.utcnow().isoformat()
        }

    def validate_stt_processing(
        self,
        latency_ms: float
    ) -> Dict[str, Any]:
        """
        Validate speech-to-text processing time.

        Args:
            latency_ms: STT latency in milliseconds

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_stt_processing(180)
        """
        validation_id = str(uuid.uuid4())

        threshold = self._thresholds['stt']
        passed = latency_ms <= threshold

        return {
            'validation_id': validation_id,
            'latency_ms': latency_ms,
            'threshold_ms': threshold,
            'passed': passed,
            'margin_ms': threshold - latency_ms,
            'component': 'speech_to_text',
            'validated_at': datetime.utcnow().isoformat()
        }

    def validate_nlp_processing(
        self,
        latency_ms: float
    ) -> Dict[str, Any]:
        """
        Validate NLP/Intent processing time.

        Args:
            latency_ms: NLP latency in milliseconds

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_nlp_processing(150)
        """
        validation_id = str(uuid.uuid4())

        threshold = self._thresholds['nlp']
        passed = latency_ms <= threshold

        return {
            'validation_id': validation_id,
            'latency_ms': latency_ms,
            'threshold_ms': threshold,
            'passed': passed,
            'margin_ms': threshold - latency_ms,
            'component': 'nlp_intent',
            'validated_at': datetime.utcnow().isoformat()
        }

    def validate_tts_generation(
        self,
        latency_ms: float
    ) -> Dict[str, Any]:
        """
        Validate text-to-speech generation time.

        Args:
            latency_ms: TTS latency in milliseconds

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_tts_generation(80)
        """
        validation_id = str(uuid.uuid4())

        threshold = self._thresholds['tts']
        passed = latency_ms <= threshold

        return {
            'validation_id': validation_id,
            'latency_ms': latency_ms,
            'threshold_ms': threshold,
            'passed': passed,
            'margin_ms': threshold - latency_ms,
            'component': 'text_to_speech',
            'validated_at': datetime.utcnow().isoformat()
        }

    def check_perception_threshold(
        self,
        latency_ms: float
    ) -> Dict[str, Any]:
        """
        Check if latency is within human perception threshold.

        Args:
            latency_ms: Latency in milliseconds

        Returns:
            Dictionary with perception check result

        Example:
            >>> result = service.check_perception_threshold(100)
        """
        check_id = str(uuid.uuid4())

        threshold = self._thresholds['perception']
        noticeable = latency_ms > threshold

        return {
            'check_id': check_id,
            'latency_ms': latency_ms,
            'perception_threshold_ms': threshold,
            'delay_noticeable': noticeable,
            'user_experience': 'seamless' if not noticeable else 'noticeable_delay',
            'checked_at': datetime.utcnow().isoformat()
        }

    def validate_total_interaction_time(
        self,
        total_ms: float,
        command_type: str = 'simple'
    ) -> Dict[str, Any]:
        """
        Validate total interaction time.

        Args:
            total_ms: Total interaction time in milliseconds
            command_type: Type of command (simple, complex)

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_total_interaction_time(800, 'simple')
        """
        validation_id = str(uuid.uuid4())

        threshold = self._thresholds['total_simple'] if command_type == 'simple' else 2000
        passed = total_ms <= threshold

        return {
            'validation_id': validation_id,
            'total_ms': total_ms,
            'command_type': command_type,
            'threshold_ms': threshold,
            'passed': passed,
            'meets_user_expectation': passed,
            'user_expectation_source': 'MoldStud_study_70_percent',
            'validated_at': datetime.utcnow().isoformat()
        }

    def calculate_latency_percentiles(
        self,
        latencies: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        Calculate latency percentiles (p50, p90, p99).

        Args:
            latencies: List of latency measurements

        Returns:
            Dictionary with percentile calculations

        Example:
            >>> result = service.calculate_latency_percentiles([100, 200, 300, 400, 500])
        """
        calculation_id = str(uuid.uuid4())

        data = latencies or self._latency_history
        if not data:
            data = [0]

        sorted_data = sorted(data)
        n = len(sorted_data)

        p50_idx = int(n * 0.50)
        p90_idx = int(n * 0.90)
        p99_idx = int(n * 0.99)

        return {
            'calculation_id': calculation_id,
            'sample_count': n,
            'p50_ms': sorted_data[min(p50_idx, n-1)],
            'p90_ms': sorted_data[min(p90_idx, n-1)],
            'p99_ms': sorted_data[min(p99_idx, n-1)],
            'min_ms': sorted_data[0],
            'max_ms': sorted_data[-1],
            'calculated_at': datetime.utcnow().isoformat()
        }

    def track_latency(
        self,
        latency_ms: float,
        component: str = 'end_to_end'
    ) -> Dict[str, Any]:
        """
        Track latency measurement.

        Args:
            latency_ms: Latency to track
            component: Component name

        Returns:
            Dictionary with tracking result

        Example:
            >>> result = service.track_latency(450, 'end_to_end')
        """
        tracking_id = str(uuid.uuid4())

        self._latency_history.append(latency_ms)

        return {
            'tracking_id': tracking_id,
            'latency_ms': latency_ms,
            'component': component,
            'total_tracked': len(self._latency_history),
            'tracked_at': datetime.utcnow().isoformat()
        }

    def get_response_time_config(self) -> Dict[str, Any]:
        """
        Get response time requirements service configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_response_time_config()
        """
        return {
            'thresholds': self._thresholds,
            'latency_history_count': len(self._latency_history),
            'features': [
                'end_to_end_validation', 'wake_word_timing',
                'stt_timing', 'nlp_timing', 'tts_timing',
                'perception_threshold', 'percentile_tracking'
            ]
        }
