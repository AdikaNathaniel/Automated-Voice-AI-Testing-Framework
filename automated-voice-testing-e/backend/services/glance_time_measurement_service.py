"""
Glance Time Measurement Service for voice AI testing.

This service provides glance time measurement and validation for
automotive voice AI testing with display interactions.

Key features:
- Glance time measurement (if display used)
- Visual attention tracking
- AAM guidelines compliance
- Display interaction analysis

Example:
    >>> service = GlanceTimeMeasurementService()
    >>> result = service.measure_glance_time('task_1', 1500)
"""

from typing import List, Dict, Any
from datetime import datetime
import uuid


class GlanceTimeMeasurementService:
    """
    Service for glance time measurement.

    Provides automotive voice AI testing for measuring
    driver visual attention and AAM compliance.

    Example:
        >>> service = GlanceTimeMeasurementService()
        >>> config = service.get_glance_time_config()
    """

    def __init__(self):
        """Initialize the glance time measurement service."""
        self._glance_thresholds = {
            'single_glance_max_ms': 2000,
            'total_glance_time_max_ms': 12000,
            'aam_single_max_ms': 2000,
            'aam_total_max_ms': 12000
        }
        self._glance_history: List[Dict[str, Any]] = []

    def measure_glance_time(
        self,
        task_id: str,
        glance_duration_ms: float
    ) -> Dict[str, Any]:
        """
        Measure single glance time.

        Args:
            task_id: Task identifier
            glance_duration_ms: Glance duration in milliseconds

        Returns:
            Dictionary with measurement result

        Example:
            >>> result = service.measure_glance_time('task_1', 1500)
        """
        measurement_id = str(uuid.uuid4())

        threshold = self._glance_thresholds['single_glance_max_ms']
        within_limit = glance_duration_ms <= threshold

        glance_record = {
            'task_id': task_id,
            'duration_ms': glance_duration_ms,
            'measured_at': datetime.utcnow().isoformat()
        }
        self._glance_history.append(glance_record)

        return {
            'measurement_id': measurement_id,
            'task_id': task_id,
            'glance_duration_ms': glance_duration_ms,
            'threshold_ms': threshold,
            'within_limit': within_limit,
            'measured_at': datetime.utcnow().isoformat()
        }

    def validate_single_glance(
        self,
        glance_duration_ms: float
    ) -> Dict[str, Any]:
        """
        Validate single glance against AAM threshold.

        Args:
            glance_duration_ms: Glance duration in milliseconds

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_single_glance(1500)
        """
        validation_id = str(uuid.uuid4())

        threshold = self._glance_thresholds['aam_single_max_ms']
        passed = glance_duration_ms <= threshold

        return {
            'validation_id': validation_id,
            'glance_duration_ms': glance_duration_ms,
            'threshold_ms': threshold,
            'passed': passed,
            'margin_ms': threshold - glance_duration_ms,
            'validated_at': datetime.utcnow().isoformat()
        }

    def calculate_total_glance_time(
        self,
        glances: List[float]
    ) -> Dict[str, Any]:
        """
        Calculate total glance time from list of glances.

        Args:
            glances: List of glance durations in milliseconds

        Returns:
            Dictionary with total glance time

        Example:
            >>> result = service.calculate_total_glance_time([1000, 1500, 800])
        """
        calculation_id = str(uuid.uuid4())

        total_ms = sum(glances)
        threshold = self._glance_thresholds['total_glance_time_max_ms']
        within_limit = total_ms <= threshold

        return {
            'calculation_id': calculation_id,
            'glance_count': len(glances),
            'total_glance_time_ms': total_ms,
            'threshold_ms': threshold,
            'within_limit': within_limit,
            'average_glance_ms': total_ms / len(glances) if glances else 0,
            'calculated_at': datetime.utcnow().isoformat()
        }

    def get_glance_thresholds(self) -> Dict[str, Any]:
        """
        Get glance time thresholds.

        Returns:
            Dictionary with thresholds

        Example:
            >>> thresholds = service.get_glance_thresholds()
        """
        return {
            'thresholds': self._glance_thresholds,
            'source': 'AAM_Driver_Focus_Guidelines',
            'units': 'milliseconds',
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def track_visual_attention(
        self,
        session_id: str,
        attention_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Track visual attention during interaction.

        Args:
            session_id: Session identifier
            attention_data: Attention tracking data

        Returns:
            Dictionary with tracking result

        Example:
            >>> result = service.track_visual_attention('session_1', {'display': True})
        """
        tracking_id = str(uuid.uuid4())

        return {
            'tracking_id': tracking_id,
            'session_id': session_id,
            'attention_data': attention_data,
            'eyes_on_road_percent': attention_data.get('eyes_on_road', 100),
            'display_usage': attention_data.get('display', False),
            'tracked_at': datetime.utcnow().isoformat()
        }

    def count_glances(
        self,
        task_id: str
    ) -> Dict[str, Any]:
        """
        Count glances for a task.

        Args:
            task_id: Task identifier

        Returns:
            Dictionary with glance count

        Example:
            >>> count = service.count_glances('task_1')
        """
        count_id = str(uuid.uuid4())

        task_glances = [g for g in self._glance_history if g.get('task_id') == task_id]
        glance_count = len(task_glances)

        return {
            'count_id': count_id,
            'task_id': task_id,
            'glance_count': glance_count,
            'counted_at': datetime.utcnow().isoformat()
        }

    def analyze_glance_pattern(
        self,
        glances: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze glance pattern.

        Args:
            glances: List of glance data

        Returns:
            Dictionary with pattern analysis

        Example:
            >>> result = service.analyze_glance_pattern([{'duration_ms': 1000}])
        """
        analysis_id = str(uuid.uuid4())

        if not glances:
            return {
                'analysis_id': analysis_id,
                'glance_count': 0,
                'pattern': 'none',
                'analyzed_at': datetime.utcnow().isoformat()
            }

        durations = [g.get('duration_ms', 0) for g in glances]
        avg_duration = sum(durations) / len(durations)

        if avg_duration <= 1000:
            pattern = 'short_frequent'
        elif avg_duration <= 1500:
            pattern = 'moderate'
        else:
            pattern = 'long_infrequent'

        return {
            'analysis_id': analysis_id,
            'glance_count': len(glances),
            'average_duration_ms': avg_duration,
            'max_duration_ms': max(durations),
            'min_duration_ms': min(durations),
            'pattern': pattern,
            'analyzed_at': datetime.utcnow().isoformat()
        }

    def validate_aam_compliance(
        self,
        total_glance_time_ms: float,
        max_single_glance_ms: float
    ) -> Dict[str, Any]:
        """
        Validate AAM (Alliance of Automobile Manufacturers) compliance.

        Args:
            total_glance_time_ms: Total glance time
            max_single_glance_ms: Maximum single glance duration

        Returns:
            Dictionary with AAM compliance result

        Example:
            >>> result = service.validate_aam_compliance(10000, 1800)
        """
        validation_id = str(uuid.uuid4())

        total_threshold = self._glance_thresholds['aam_total_max_ms']
        single_threshold = self._glance_thresholds['aam_single_max_ms']

        total_compliant = total_glance_time_ms <= total_threshold
        single_compliant = max_single_glance_ms <= single_threshold
        fully_compliant = total_compliant and single_compliant

        return {
            'validation_id': validation_id,
            'total_glance_time_ms': total_glance_time_ms,
            'max_single_glance_ms': max_single_glance_ms,
            'total_threshold_ms': total_threshold,
            'single_threshold_ms': single_threshold,
            'total_compliant': total_compliant,
            'single_compliant': single_compliant,
            'aam_compliant': fully_compliant,
            'validated_at': datetime.utcnow().isoformat()
        }

    def get_aam_guidelines(self) -> Dict[str, Any]:
        """
        Get AAM Driver Focus Guidelines.

        Returns:
            Dictionary with AAM guidelines

        Example:
            >>> guidelines = service.get_aam_guidelines()
        """
        return {
            'name': 'AAM Driver Focus Guidelines',
            'version': '2.0',
            'requirements': {
                'single_glance_max_seconds': 2.0,
                'total_glance_time_max_seconds': 12.0,
                'task_time_max_seconds': 15.0
            },
            'description': 'Alliance of Automobile Manufacturers guidelines for driver distraction',
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def check_task_acceptance(
        self,
        total_glance_time_ms: float,
        max_single_glance_ms: float,
        task_time_ms: float
    ) -> Dict[str, Any]:
        """
        Check if task is acceptable per AAM guidelines.

        Args:
            total_glance_time_ms: Total glance time
            max_single_glance_ms: Maximum single glance
            task_time_ms: Total task time

        Returns:
            Dictionary with acceptance result

        Example:
            >>> result = service.check_task_acceptance(10000, 1800, 12000)
        """
        check_id = str(uuid.uuid4())

        total_ok = total_glance_time_ms <= 12000
        single_ok = max_single_glance_ms <= 2000
        task_ok = task_time_ms <= 15000

        accepted = total_ok and single_ok and task_ok

        return {
            'check_id': check_id,
            'total_glance_time_ms': total_glance_time_ms,
            'max_single_glance_ms': max_single_glance_ms,
            'task_time_ms': task_time_ms,
            'total_glance_ok': total_ok,
            'single_glance_ok': single_ok,
            'task_time_ok': task_ok,
            'task_accepted': accepted,
            'checked_at': datetime.utcnow().isoformat()
        }

    def measure_display_interaction(
        self,
        interaction_id: str,
        display_time_ms: float,
        interaction_type: str = 'visual'
    ) -> Dict[str, Any]:
        """
        Measure display interaction.

        Args:
            interaction_id: Interaction identifier
            display_time_ms: Time spent on display
            interaction_type: Type of interaction

        Returns:
            Dictionary with measurement result

        Example:
            >>> result = service.measure_display_interaction('int_1', 1500, 'visual')
        """
        measurement_id = str(uuid.uuid4())

        return {
            'measurement_id': measurement_id,
            'interaction_id': interaction_id,
            'display_time_ms': display_time_ms,
            'interaction_type': interaction_type,
            'requires_visual_attention': interaction_type == 'visual',
            'measured_at': datetime.utcnow().isoformat()
        }

    def validate_eyes_off_road(
        self,
        eyes_off_road_ms: float
    ) -> Dict[str, Any]:
        """
        Validate eyes-off-road time.

        Args:
            eyes_off_road_ms: Time with eyes off road

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_eyes_off_road(1500)
        """
        validation_id = str(uuid.uuid4())

        threshold = self._glance_thresholds['aam_single_max_ms']
        safe = eyes_off_road_ms <= threshold

        return {
            'validation_id': validation_id,
            'eyes_off_road_ms': eyes_off_road_ms,
            'threshold_ms': threshold,
            'safe': safe,
            'risk_level': 'low' if safe else 'high',
            'validated_at': datetime.utcnow().isoformat()
        }

    def generate_glance_report(
        self,
        session_id: str,
        glance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate glance time report.

        Args:
            session_id: Session identifier
            glance_data: Collected glance data

        Returns:
            Dictionary with glance report

        Example:
            >>> report = service.generate_glance_report('session_1', {'glances': []})
        """
        report_id = str(uuid.uuid4())

        total_glance = glance_data.get('total_glance_time_ms', 0)
        max_single = glance_data.get('max_single_glance_ms', 0)

        aam_compliant = total_glance <= 12000 and max_single <= 2000

        recommendations = []
        if not aam_compliant:
            if total_glance > 12000:
                recommendations.append('Reduce total visual attention time')
            if max_single > 2000:
                recommendations.append('Break up long glances into shorter ones')

        return {
            'report_id': report_id,
            'session_id': session_id,
            'glance_data': glance_data,
            'aam_compliant': aam_compliant,
            'recommendations': recommendations,
            'generated_at': datetime.utcnow().isoformat()
        }

    def get_glance_time_config(self) -> Dict[str, Any]:
        """
        Get glance time measurement service configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_glance_time_config()
        """
        return {
            'glance_thresholds': self._glance_thresholds,
            'glance_history_count': len(self._glance_history),
            'features': [
                'glance_measurement', 'visual_attention_tracking',
                'aam_compliance', 'display_interaction',
                'glance_reporting'
            ]
        }
