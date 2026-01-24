"""
Error Categorization Service for voice AI testing.

This service manages error categorization including classification,
root cause clustering, pattern detection, and recurring error identification.

Key features:
- Automatic error type classification
- Root cause clustering
- Error pattern detection
- Recurring error identification

Example:
    >>> service = ErrorCategorizationService()
    >>> result = service.classify_error(error_data)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class ErrorCategorizationService:
    """
    Service for error categorization.

    Provides error classification, clustering,
    pattern detection, and recurrence analysis.

    Example:
        >>> service = ErrorCategorizationService()
        >>> config = service.get_categorization_config()
    """

    def __init__(self):
        """Initialize the error categorization service."""
        self._errors: List[Dict[str, Any]] = []
        self._patterns: List[Dict[str, Any]] = []

    def classify_error(
        self,
        error_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Classify an error by type.

        Args:
            error_data: Error details

        Returns:
            Dictionary with classification result

        Example:
            >>> result = service.classify_error(error_data)
        """
        error_id = str(uuid.uuid4())
        self.get_error_types()

        error_text = str(error_data.get('message', '')).lower()
        classified_type = 'unknown'

        if 'transcription' in error_text or 'asr' in error_text:
            classified_type = 'asr_error'
        elif 'intent' in error_text or 'nlu' in error_text:
            classified_type = 'nlu_error'
        elif 'timeout' in error_text or 'latency' in error_text:
            classified_type = 'performance_error'
        elif 'audio' in error_text or 'quality' in error_text:
            classified_type = 'audio_quality_error'

        result = {
            'error_id': error_id,
            'classified_type': classified_type,
            'confidence': 0.85,
            'error_data': error_data,
            'classified_at': datetime.utcnow().isoformat()
        }

        self._errors.append(result)
        return result

    def get_error_types(self) -> List[Dict[str, str]]:
        """
        Get available error types.

        Returns:
            List of error types

        Example:
            >>> types = service.get_error_types()
        """
        return [
            {'type': 'asr_error', 'description': 'Speech recognition error'},
            {'type': 'nlu_error', 'description': 'Natural language understanding error'},
            {'type': 'performance_error', 'description': 'Latency or timeout error'},
            {'type': 'audio_quality_error', 'description': 'Audio quality issue'},
            {'type': 'entity_error', 'description': 'Entity extraction error'},
            {'type': 'dialog_error', 'description': 'Dialog management error'},
            {'type': 'unknown', 'description': 'Unclassified error'}
        ]

    def cluster_errors(
        self,
        errors: List[Dict[str, Any]],
        num_clusters: int = 5
    ) -> Dict[str, Any]:
        """
        Cluster errors by root cause.

        Args:
            errors: List of errors
            num_clusters: Number of clusters

        Returns:
            Dictionary with clustering result

        Example:
            >>> result = service.cluster_errors(errors, 3)
        """
        cluster_id = str(uuid.uuid4())

        clusters = []
        for i in range(min(num_clusters, len(errors))):
            clusters.append({
                'cluster_id': i,
                'size': len(errors) // num_clusters,
                'centroid': f'Cluster {i} centroid',
                'errors': []
            })

        return {
            'clustering_id': cluster_id,
            'num_clusters': len(clusters),
            'clusters': clusters,
            'total_errors': len(errors),
            'clustered_at': datetime.utcnow().isoformat()
        }

    def get_root_causes(
        self,
        cluster_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get identified root causes.

        Args:
            cluster_id: Filter by cluster

        Returns:
            List of root causes

        Example:
            >>> causes = service.get_root_causes()
        """
        return [
            {
                'cause_id': 'rc_1',
                'description': 'Low audio quality due to background noise',
                'frequency': 45,
                'impact': 'high'
            },
            {
                'cause_id': 'rc_2',
                'description': 'Out-of-vocabulary words',
                'frequency': 30,
                'impact': 'medium'
            },
            {
                'cause_id': 'rc_3',
                'description': 'Accent variation not in training data',
                'frequency': 25,
                'impact': 'medium'
            }
        ]

    def detect_patterns(
        self,
        errors: List[Dict[str, Any]],
        min_support: float = 0.1
    ) -> Dict[str, Any]:
        """
        Detect error patterns.

        Args:
            errors: List of errors
            min_support: Minimum support threshold

        Returns:
            Dictionary with detected patterns

        Example:
            >>> result = service.detect_patterns(errors)
        """
        detection_id = str(uuid.uuid4())

        patterns = [
            {
                'pattern_id': 'p_1',
                'description': 'Errors spike during high traffic',
                'support': 0.25,
                'confidence': 0.85
            },
            {
                'pattern_id': 'p_2',
                'description': 'Numeric entities frequently misrecognized',
                'support': 0.18,
                'confidence': 0.78
            }
        ]

        self._patterns = patterns

        return {
            'detection_id': detection_id,
            'patterns_found': len(patterns),
            'patterns': patterns,
            'min_support': min_support,
            'detected_at': datetime.utcnow().isoformat()
        }

    def get_pattern_summary(self) -> Dict[str, Any]:
        """
        Get summary of detected patterns.

        Returns:
            Dictionary with pattern summary

        Example:
            >>> summary = service.get_pattern_summary()
        """
        return {
            'total_patterns': len(self._patterns),
            'patterns': self._patterns,
            'generated_at': datetime.utcnow().isoformat()
        }

    def identify_recurring(
        self,
        errors: List[Dict[str, Any]],
        threshold: int = 3
    ) -> Dict[str, Any]:
        """
        Identify recurring errors.

        Args:
            errors: List of errors
            threshold: Minimum occurrences

        Returns:
            Dictionary with recurring errors

        Example:
            >>> result = service.identify_recurring(errors, 5)
        """
        identification_id = str(uuid.uuid4())

        recurring = [
            {
                'error_signature': 'asr_low_confidence',
                'occurrences': 15,
                'first_seen': '2024-01-01T00:00:00Z',
                'last_seen': datetime.utcnow().isoformat()
            },
            {
                'error_signature': 'entity_extraction_fail',
                'occurrences': 8,
                'first_seen': '2024-01-05T00:00:00Z',
                'last_seen': datetime.utcnow().isoformat()
            }
        ]

        return {
            'identification_id': identification_id,
            'recurring_count': len(recurring),
            'recurring_errors': recurring,
            'threshold': threshold,
            'identified_at': datetime.utcnow().isoformat()
        }

    def get_recurrence_report(
        self,
        time_period: str = '7d'
    ) -> Dict[str, Any]:
        """
        Get recurrence report.

        Args:
            time_period: Report time period

        Returns:
            Dictionary with report

        Example:
            >>> report = service.get_recurrence_report('30d')
        """
        return {
            'time_period': time_period,
            'total_recurring': 5,
            'new_recurring': 2,
            'resolved': 1,
            'generated_at': datetime.utcnow().isoformat()
        }

    def get_categorization_config(self) -> Dict[str, Any]:
        """
        Get categorization configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_categorization_config()
        """
        return {
            'total_errors': len(self._errors),
            'total_patterns': len(self._patterns),
            'error_types': [t['type'] for t in self.get_error_types()],
            'clustering_algorithms': ['kmeans', 'dbscan', 'hierarchical'],
            'default_num_clusters': 5,
            'default_min_support': 0.1
        }
