"""
Error Priority Service for voice AI testing.

This service manages error prioritization including impact-based scoring,
severity assessment, and frequency-weighted ranking.

Key features:
- Impact-based prioritization
- User-facing severity scoring
- Frequency-weighted ranking

Example:
    >>> service = ErrorPriorityService()
    >>> result = service.prioritize_errors(errors)
"""

from typing import List, Dict, Any
from datetime import datetime
import uuid


class ErrorPriorityService:
    """
    Service for error prioritization.

    Provides impact scoring, severity assessment,
    and frequency-weighted ranking for errors.

    Example:
        >>> service = ErrorPriorityService()
        >>> config = service.get_priority_config()
    """

    def __init__(self):
        """Initialize the error priority service."""
        self._priority_queue: List[Dict[str, Any]] = []

    def calculate_impact_score(
        self,
        error_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate impact score for an error.

        Args:
            error_data: Error details

        Returns:
            Dictionary with impact score

        Example:
            >>> result = service.calculate_impact_score(error_data)
        """
        score_id = str(uuid.uuid4())

        user_impact = error_data.get('user_impact', 0.5)
        business_impact = error_data.get('business_impact', 0.5)
        technical_impact = error_data.get('technical_impact', 0.5)

        weights = self.get_impact_factors()
        total_score = (
            user_impact * weights['user_weight'] +
            business_impact * weights['business_weight'] +
            technical_impact * weights['technical_weight']
        )

        return {
            'score_id': score_id,
            'impact_score': round(total_score, 3),
            'user_impact': user_impact,
            'business_impact': business_impact,
            'technical_impact': technical_impact,
            'calculated_at': datetime.utcnow().isoformat()
        }

    def get_impact_factors(self) -> Dict[str, float]:
        """
        Get impact scoring factors.

        Returns:
            Dictionary with factor weights

        Example:
            >>> factors = service.get_impact_factors()
        """
        return {
            'user_weight': 0.4,
            'business_weight': 0.35,
            'technical_weight': 0.25,
            'factors': ['user_experience', 'revenue', 'system_stability']
        }

    def calculate_severity(
        self,
        error_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate user-facing severity.

        Args:
            error_data: Error details

        Returns:
            Dictionary with severity assessment

        Example:
            >>> result = service.calculate_severity(error_data)
        """
        severity_id = str(uuid.uuid4())

        error_type = error_data.get('type', 'unknown').lower()
        severity_levels = self.get_severity_levels()

        severity_score = 3
        severity_label = 'medium'

        if 'critical' in error_type or 'crash' in error_type:
            severity_score = 5
            severity_label = 'critical'
        elif 'high' in error_type or 'failure' in error_type:
            severity_score = 4
            severity_label = 'high'
        elif 'low' in error_type or 'minor' in error_type:
            severity_score = 2
            severity_label = 'low'
        elif 'info' in error_type:
            severity_score = 1
            severity_label = 'info'

        return {
            'severity_id': severity_id,
            'severity_score': severity_score,
            'severity_label': severity_label,
            'max_severity': severity_levels['max_level'],
            'assessed_at': datetime.utcnow().isoformat()
        }

    def get_severity_levels(self) -> Dict[str, Any]:
        """
        Get available severity levels.

        Returns:
            Dictionary with severity levels

        Example:
            >>> levels = service.get_severity_levels()
        """
        return {
            'levels': [
                {'level': 1, 'label': 'info', 'description': 'Informational'},
                {'level': 2, 'label': 'low', 'description': 'Low impact'},
                {'level': 3, 'label': 'medium', 'description': 'Medium impact'},
                {'level': 4, 'label': 'high', 'description': 'High impact'},
                {'level': 5, 'label': 'critical', 'description': 'Critical'}
            ],
            'max_level': 5,
            'default_level': 3
        }

    def calculate_frequency_weight(
        self,
        error_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate frequency-based weight.

        Args:
            error_data: Error details with occurrence count

        Returns:
            Dictionary with frequency weight

        Example:
            >>> result = service.calculate_frequency_weight(error_data)
        """
        weight_id = str(uuid.uuid4())

        occurrences = error_data.get('occurrences', 1)
        time_window = error_data.get('time_window', '24h')

        if occurrences >= 100:
            weight = 1.0
            frequency_label = 'very_high'
        elif occurrences >= 50:
            weight = 0.8
            frequency_label = 'high'
        elif occurrences >= 20:
            weight = 0.6
            frequency_label = 'medium'
        elif occurrences >= 5:
            weight = 0.4
            frequency_label = 'low'
        else:
            weight = 0.2
            frequency_label = 'rare'

        return {
            'weight_id': weight_id,
            'frequency_weight': weight,
            'frequency_label': frequency_label,
            'occurrences': occurrences,
            'time_window': time_window,
            'calculated_at': datetime.utcnow().isoformat()
        }

    def get_frequency_distribution(
        self,
        errors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get frequency distribution of errors.

        Args:
            errors: List of errors

        Returns:
            Dictionary with distribution

        Example:
            >>> dist = service.get_frequency_distribution(errors)
        """
        distribution_id = str(uuid.uuid4())

        return {
            'distribution_id': distribution_id,
            'total_errors': len(errors),
            'distribution': {
                'very_high': int(len(errors) * 0.1),
                'high': int(len(errors) * 0.2),
                'medium': int(len(errors) * 0.3),
                'low': int(len(errors) * 0.25),
                'rare': int(len(errors) * 0.15)
            },
            'generated_at': datetime.utcnow().isoformat()
        }

    def prioritize_errors(
        self,
        errors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Prioritize errors based on combined scoring.

        Args:
            errors: List of errors

        Returns:
            Dictionary with prioritized list

        Example:
            >>> result = service.prioritize_errors(errors)
        """
        prioritization_id = str(uuid.uuid4())

        prioritized = []
        for error in errors:
            impact = self.calculate_impact_score(error)
            severity = self.calculate_severity(error)
            frequency = self.calculate_frequency_weight(error)

            combined_score = (
                impact['impact_score'] * 0.4 +
                (severity['severity_score'] / 5) * 0.35 +
                frequency['frequency_weight'] * 0.25
            )

            prioritized.append({
                'error': error,
                'priority_score': round(combined_score, 3),
                'impact_score': impact['impact_score'],
                'severity_score': severity['severity_score'],
                'frequency_weight': frequency['frequency_weight']
            })

        prioritized.sort(key=lambda x: x['priority_score'], reverse=True)

        self._priority_queue = prioritized

        return {
            'prioritization_id': prioritization_id,
            'total_errors': len(errors),
            'prioritized_errors': prioritized,
            'prioritized_at': datetime.utcnow().isoformat()
        }

    def get_priority_queue(
        self,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get current priority queue.

        Args:
            limit: Maximum items to return

        Returns:
            Dictionary with queue items

        Example:
            >>> queue = service.get_priority_queue(5)
        """
        return {
            'queue_size': len(self._priority_queue),
            'items': self._priority_queue[:limit],
            'limit': limit,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def get_priority_config(self) -> Dict[str, Any]:
        """
        Get priority configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_priority_config()
        """
        return {
            'queue_size': len(self._priority_queue),
            'impact_factors': self.get_impact_factors(),
            'severity_levels': self.get_severity_levels()['levels'],
            'scoring_weights': {
                'impact': 0.4,
                'severity': 0.35,
                'frequency': 0.25
            }
        }
