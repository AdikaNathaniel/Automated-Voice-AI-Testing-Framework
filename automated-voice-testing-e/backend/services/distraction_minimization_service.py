"""
Distraction Minimization Testing Service for voice AI testing.

This service provides distraction minimization validation for
automotive voice AI testing with safety-focused metrics.

Key features:
- Task completion time measurement
- Number of turns required
- Cognitive load assessment
- Distraction scoring
- Minimization reporting

Example:
    >>> service = DistractionMinimizationService()
    >>> result = service.measure_task_completion_time('navigation', 2500)
"""

from typing import List, Dict, Any
from datetime import datetime
import uuid


class DistractionMinimizationService:
    """
    Service for distraction minimization testing.

    Provides automotive voice AI testing for measuring
    and minimizing driver distraction during interactions.

    Example:
        >>> service = DistractionMinimizationService()
        >>> config = service.get_distraction_minimization_config()
    """

    def __init__(self):
        """Initialize the distraction minimization service."""
        self._time_thresholds = {
            'simple': 3000,
            'moderate': 6000,
            'complex': 10000
        }
        self._turn_limits = {
            'simple': 2,
            'moderate': 4,
            'complex': 6
        }
        self._load_thresholds = {
            'low': 30,
            'medium': 60,
            'high': 100
        }
        self._task_history: List[Dict[str, Any]] = []

    def measure_task_completion_time(
        self,
        task_type: str,
        completion_time_ms: float
    ) -> Dict[str, Any]:
        """
        Measure task completion time.

        Args:
            task_type: Type of task
            completion_time_ms: Time to complete in milliseconds

        Returns:
            Dictionary with measurement result

        Example:
            >>> result = service.measure_task_completion_time('navigation', 2500)
        """
        measurement_id = str(uuid.uuid4())

        threshold = self._time_thresholds.get(task_type, 6000)
        within_threshold = completion_time_ms <= threshold

        return {
            'measurement_id': measurement_id,
            'task_type': task_type,
            'completion_time_ms': completion_time_ms,
            'threshold_ms': threshold,
            'within_threshold': within_threshold,
            'efficiency': min(100, (threshold / completion_time_ms) * 100) if completion_time_ms > 0 else 100,
            'measured_at': datetime.utcnow().isoformat()
        }

    def get_task_time_thresholds(self) -> Dict[str, Any]:
        """
        Get task time thresholds.

        Returns:
            Dictionary with thresholds

        Example:
            >>> thresholds = service.get_task_time_thresholds()
        """
        return {
            'thresholds': self._time_thresholds,
            'units': 'milliseconds',
            'source': 'automotive_safety_standards',
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def validate_completion_time(
        self,
        task_type: str,
        completion_time_ms: float
    ) -> Dict[str, Any]:
        """
        Validate task completion time against thresholds.

        Args:
            task_type: Type of task
            completion_time_ms: Completion time in milliseconds

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_completion_time('simple', 2000)
        """
        validation_id = str(uuid.uuid4())

        threshold = self._time_thresholds.get(task_type, 6000)
        passed = completion_time_ms <= threshold

        return {
            'validation_id': validation_id,
            'task_type': task_type,
            'completion_time_ms': completion_time_ms,
            'threshold_ms': threshold,
            'passed': passed,
            'margin_ms': threshold - completion_time_ms,
            'validated_at': datetime.utcnow().isoformat()
        }

    def track_task_duration(
        self,
        task_id: str,
        task_type: str,
        duration_ms: float
    ) -> Dict[str, Any]:
        """
        Track task duration for analysis.

        Args:
            task_id: Task identifier
            task_type: Type of task
            duration_ms: Duration in milliseconds

        Returns:
            Dictionary with tracking result

        Example:
            >>> result = service.track_task_duration('task_1', 'navigation', 3000)
        """
        tracking_id = str(uuid.uuid4())

        task_record = {
            'task_id': task_id,
            'task_type': task_type,
            'duration_ms': duration_ms,
            'tracked_at': datetime.utcnow().isoformat()
        }
        self._task_history.append(task_record)

        return {
            'tracking_id': tracking_id,
            'task_id': task_id,
            'task_type': task_type,
            'duration_ms': duration_ms,
            'total_tracked': len(self._task_history),
            'tracked_at': datetime.utcnow().isoformat()
        }

    def count_interaction_turns(
        self,
        session_id: str,
        interactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Count interaction turns in session.

        Args:
            session_id: Session identifier
            interactions: List of interactions

        Returns:
            Dictionary with turn count result

        Example:
            >>> result = service.count_interaction_turns('session_1', [{'type': 'user'}, {'type': 'system'}])
        """
        count_id = str(uuid.uuid4())

        user_turns = len([i for i in interactions if i.get('type') == 'user'])
        system_turns = len([i for i in interactions if i.get('type') == 'system'])
        total_turns = user_turns + system_turns

        return {
            'count_id': count_id,
            'session_id': session_id,
            'user_turns': user_turns,
            'system_turns': system_turns,
            'total_turns': total_turns,
            'counted_at': datetime.utcnow().isoformat()
        }

    def validate_turn_count(
        self,
        task_type: str,
        turn_count: int
    ) -> Dict[str, Any]:
        """
        Validate turn count against limits.

        Args:
            task_type: Type of task
            turn_count: Number of turns

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_turn_count('simple', 2)
        """
        validation_id = str(uuid.uuid4())

        limit = self._turn_limits.get(task_type, 4)
        passed = turn_count <= limit

        return {
            'validation_id': validation_id,
            'task_type': task_type,
            'turn_count': turn_count,
            'turn_limit': limit,
            'passed': passed,
            'excess_turns': max(0, turn_count - limit),
            'validated_at': datetime.utcnow().isoformat()
        }

    def get_optimal_turns(
        self,
        task_type: str
    ) -> Dict[str, Any]:
        """
        Get optimal turn count for task type.

        Args:
            task_type: Type of task

        Returns:
            Dictionary with optimal turns

        Example:
            >>> optimal = service.get_optimal_turns('simple')
        """
        optimal = self._turn_limits.get(task_type, 4)

        return {
            'task_type': task_type,
            'optimal_turns': optimal,
            'all_limits': self._turn_limits,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def analyze_turn_efficiency(
        self,
        task_type: str,
        actual_turns: int
    ) -> Dict[str, Any]:
        """
        Analyze turn efficiency.

        Args:
            task_type: Type of task
            actual_turns: Actual turn count

        Returns:
            Dictionary with efficiency analysis

        Example:
            >>> result = service.analyze_turn_efficiency('simple', 3)
        """
        analysis_id = str(uuid.uuid4())

        optimal = self._turn_limits.get(task_type, 4)
        efficiency = min(100, (optimal / actual_turns) * 100) if actual_turns > 0 else 100

        rating = 'excellent' if efficiency >= 90 else 'good' if efficiency >= 70 else 'needs_improvement'

        return {
            'analysis_id': analysis_id,
            'task_type': task_type,
            'actual_turns': actual_turns,
            'optimal_turns': optimal,
            'efficiency_percent': round(efficiency, 2),
            'rating': rating,
            'analyzed_at': datetime.utcnow().isoformat()
        }

    def assess_cognitive_load(
        self,
        task_complexity: str,
        turn_count: int,
        completion_time_ms: float
    ) -> Dict[str, Any]:
        """
        Assess cognitive load of interaction.

        Args:
            task_complexity: Complexity level
            turn_count: Number of turns
            completion_time_ms: Completion time

        Returns:
            Dictionary with cognitive load assessment

        Example:
            >>> result = service.assess_cognitive_load('moderate', 3, 4000)
        """
        assessment_id = str(uuid.uuid4())

        complexity_weights = {'simple': 1, 'moderate': 2, 'complex': 3}
        complexity_weight = complexity_weights.get(task_complexity, 2)

        turn_factor = turn_count * 10
        time_factor = (completion_time_ms / 1000) * 5
        load_score = (complexity_weight * 20) + turn_factor + time_factor

        if load_score <= 30:
            load_level = 'low'
        elif load_score <= 60:
            load_level = 'medium'
        else:
            load_level = 'high'

        return {
            'assessment_id': assessment_id,
            'task_complexity': task_complexity,
            'turn_count': turn_count,
            'completion_time_ms': completion_time_ms,
            'load_score': round(load_score, 2),
            'load_level': load_level,
            'safe_for_driving': load_level != 'high',
            'assessed_at': datetime.utcnow().isoformat()
        }

    def calculate_load_score(
        self,
        factors: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Calculate cognitive load score from factors.

        Args:
            factors: Dictionary of load factors

        Returns:
            Dictionary with load score

        Example:
            >>> result = service.calculate_load_score({'turns': 3, 'time': 5})
        """
        calculation_id = str(uuid.uuid4())

        total_score = sum(factors.values())
        normalized_score = min(100, total_score)

        return {
            'calculation_id': calculation_id,
            'factors': factors,
            'total_score': total_score,
            'normalized_score': normalized_score,
            'calculated_at': datetime.utcnow().isoformat()
        }

    def get_load_thresholds(self) -> Dict[str, Any]:
        """
        Get cognitive load thresholds.

        Returns:
            Dictionary with thresholds

        Example:
            >>> thresholds = service.get_load_thresholds()
        """
        return {
            'thresholds': self._load_thresholds,
            'description': {
                'low': 'Minimal distraction, safe for driving',
                'medium': 'Moderate attention required',
                'high': 'High distraction, not recommended while driving'
            },
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def validate_cognitive_load(
        self,
        load_score: float,
        context: str = 'driving'
    ) -> Dict[str, Any]:
        """
        Validate cognitive load for context.

        Args:
            load_score: Calculated load score
            context: Usage context

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_cognitive_load(45, 'driving')
        """
        validation_id = str(uuid.uuid4())

        if context == 'driving':
            threshold = self._load_thresholds['low']
        else:
            threshold = self._load_thresholds['medium']

        passed = load_score <= threshold

        return {
            'validation_id': validation_id,
            'load_score': load_score,
            'context': context,
            'threshold': threshold,
            'passed': passed,
            'recommendation': 'Safe to use' if passed else 'Reduce complexity',
            'validated_at': datetime.utcnow().isoformat()
        }

    def calculate_distraction_score(
        self,
        completion_time_ms: float,
        turn_count: int,
        error_count: int = 0
    ) -> Dict[str, Any]:
        """
        Calculate overall distraction score.

        Args:
            completion_time_ms: Task completion time
            turn_count: Number of turns
            error_count: Number of errors

        Returns:
            Dictionary with distraction score

        Example:
            >>> result = service.calculate_distraction_score(3000, 2, 0)
        """
        calculation_id = str(uuid.uuid4())

        time_score = min(40, (completion_time_ms / 250))
        turn_score = turn_count * 15
        error_score = error_count * 20

        total_score = time_score + turn_score + error_score
        normalized = min(100, total_score)

        if normalized <= 30:
            level = 'low'
        elif normalized <= 60:
            level = 'medium'
        else:
            level = 'high'

        return {
            'calculation_id': calculation_id,
            'completion_time_ms': completion_time_ms,
            'turn_count': turn_count,
            'error_count': error_count,
            'time_component': round(time_score, 2),
            'turn_component': turn_score,
            'error_component': error_score,
            'distraction_score': round(normalized, 2),
            'distraction_level': level,
            'calculated_at': datetime.utcnow().isoformat()
        }

    def get_distraction_factors(self) -> List[Dict[str, Any]]:
        """
        Get list of distraction factors.

        Returns:
            List of distraction factors

        Example:
            >>> factors = service.get_distraction_factors()
        """
        return [
            {
                'factor': 'completion_time',
                'weight': 0.4,
                'description': 'Time spent on task'
            },
            {
                'factor': 'turn_count',
                'weight': 0.35,
                'description': 'Number of interaction turns'
            },
            {
                'factor': 'error_rate',
                'weight': 0.25,
                'description': 'Recognition and understanding errors'
            }
        ]

    def generate_minimization_report(
        self,
        session_id: str,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate distraction minimization report.

        Args:
            session_id: Session identifier
            metrics: Collected metrics

        Returns:
            Dictionary with minimization report

        Example:
            >>> report = service.generate_minimization_report('session_1', {'time': 3000})
        """
        report_id = str(uuid.uuid4())

        recommendations = []
        if metrics.get('completion_time_ms', 0) > 5000:
            recommendations.append('Reduce task completion time')
        if metrics.get('turn_count', 0) > 4:
            recommendations.append('Simplify interaction flow')
        if metrics.get('error_count', 0) > 0:
            recommendations.append('Improve recognition accuracy')

        return {
            'report_id': report_id,
            'session_id': session_id,
            'metrics': metrics,
            'recommendations': recommendations,
            'overall_assessment': 'passed' if len(recommendations) == 0 else 'needs_improvement',
            'generated_at': datetime.utcnow().isoformat()
        }

    def get_distraction_minimization_config(self) -> Dict[str, Any]:
        """
        Get distraction minimization service configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_distraction_minimization_config()
        """
        return {
            'time_thresholds': self._time_thresholds,
            'turn_limits': self._turn_limits,
            'load_thresholds': self._load_thresholds,
            'task_history_count': len(self._task_history),
            'features': [
                'task_completion_time', 'turn_counting',
                'cognitive_load', 'distraction_scoring',
                'minimization_reporting'
            ]
        }
