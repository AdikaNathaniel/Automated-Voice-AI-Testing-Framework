"""
Beamforming Performance Service for voice AI testing.

This service provides beamforming performance testing and validation
for automotive voice AI microphone arrays.

Key features:
- Beam steering accuracy
- Noise rejection ratio
- Speaker isolation
- Performance metrics

Example:
    >>> service = BeamformingPerformanceService()
    >>> result = service.measure_steering_accuracy(30.0, 32.0)
"""

from typing import List, Dict, Any
from datetime import datetime
import uuid


class BeamformingPerformanceService:
    """
    Service for beamforming performance testing.

    Provides automotive voice AI testing for beamforming
    accuracy, noise rejection, and speaker isolation.

    Example:
        >>> service = BeamformingPerformanceService()
        >>> config = service.get_beamforming_performance_config()
    """

    def __init__(self):
        """Initialize the beamforming performance service."""
        self._steering_range = {'min': -90, 'max': 90}
        self._accuracy_threshold_degrees = 5.0
        self._noise_rejection_threshold_db = 15.0
        self._isolation_threshold_db = 20.0
        self._measurements: List[Dict[str, Any]] = []

    def measure_steering_accuracy(
        self,
        target_angle: float,
        actual_angle: float
    ) -> Dict[str, Any]:
        """
        Measure beam steering accuracy.

        Args:
            target_angle: Target beam angle in degrees
            actual_angle: Actual beam angle in degrees

        Returns:
            Dictionary with accuracy measurement

        Example:
            >>> result = service.measure_steering_accuracy(30.0, 32.0)
        """
        measurement_id = str(uuid.uuid4())

        error = abs(actual_angle - target_angle)
        passed = error <= self._accuracy_threshold_degrees

        measurement = {
            'type': 'steering_accuracy',
            'target': target_angle,
            'actual': actual_angle,
            'error': error
        }
        self._measurements.append(measurement)

        return {
            'measurement_id': measurement_id,
            'target_angle_degrees': target_angle,
            'actual_angle_degrees': actual_angle,
            'error_degrees': error,
            'threshold_degrees': self._accuracy_threshold_degrees,
            'passed': passed,
            'measured_at': datetime.utcnow().isoformat()
        }

    def set_beam_angle(
        self,
        array_id: str,
        angle_degrees: float
    ) -> Dict[str, Any]:
        """
        Set beam angle for array.

        Args:
            array_id: Array identifier
            angle_degrees: Target angle in degrees

        Returns:
            Dictionary with setting result

        Example:
            >>> result = service.set_beam_angle('array_1', 45.0)
        """
        setting_id = str(uuid.uuid4())

        valid = (self._steering_range['min'] <= angle_degrees <=
                 self._steering_range['max'])

        return {
            'setting_id': setting_id,
            'array_id': array_id,
            'angle_degrees': angle_degrees,
            'valid_range': valid,
            'steering_range': self._steering_range,
            'set_at': datetime.utcnow().isoformat()
        }

    def get_steering_range(self) -> Dict[str, Any]:
        """
        Get beam steering range.

        Returns:
            Dictionary with steering range

        Example:
            >>> range_info = service.get_steering_range()
        """
        return {
            'min_angle_degrees': self._steering_range['min'],
            'max_angle_degrees': self._steering_range['max'],
            'total_range_degrees': (self._steering_range['max'] -
                                    self._steering_range['min']),
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def validate_steering_accuracy(
        self,
        error_degrees: float
    ) -> Dict[str, Any]:
        """
        Validate steering accuracy.

        Args:
            error_degrees: Steering error in degrees

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_steering_accuracy(3.0)
        """
        validation_id = str(uuid.uuid4())

        passed = error_degrees <= self._accuracy_threshold_degrees

        return {
            'validation_id': validation_id,
            'error_degrees': error_degrees,
            'threshold_degrees': self._accuracy_threshold_degrees,
            'passed': passed,
            'rating': 'excellent' if error_degrees <= 2 else 'good' if passed else 'poor',
            'validated_at': datetime.utcnow().isoformat()
        }

    def measure_noise_rejection(
        self,
        signal_level_db: float,
        noise_level_db: float
    ) -> Dict[str, Any]:
        """
        Measure noise rejection ratio.

        Args:
            signal_level_db: Signal level in dB
            noise_level_db: Noise level in dB

        Returns:
            Dictionary with rejection measurement

        Example:
            >>> result = service.measure_noise_rejection(-20.0, -40.0)
        """
        measurement_id = str(uuid.uuid4())

        rejection_db = signal_level_db - noise_level_db
        passed = rejection_db >= self._noise_rejection_threshold_db

        measurement = {
            'type': 'noise_rejection',
            'signal': signal_level_db,
            'noise': noise_level_db,
            'rejection': rejection_db
        }
        self._measurements.append(measurement)

        return {
            'measurement_id': measurement_id,
            'signal_level_db': signal_level_db,
            'noise_level_db': noise_level_db,
            'rejection_ratio_db': rejection_db,
            'threshold_db': self._noise_rejection_threshold_db,
            'passed': passed,
            'measured_at': datetime.utcnow().isoformat()
        }

    def calculate_rejection_ratio(
        self,
        on_axis_level_db: float,
        off_axis_level_db: float
    ) -> Dict[str, Any]:
        """
        Calculate rejection ratio.

        Args:
            on_axis_level_db: On-axis signal level
            off_axis_level_db: Off-axis signal level

        Returns:
            Dictionary with rejection ratio

        Example:
            >>> result = service.calculate_rejection_ratio(-10.0, -30.0)
        """
        calculation_id = str(uuid.uuid4())

        ratio_db = on_axis_level_db - off_axis_level_db

        return {
            'calculation_id': calculation_id,
            'on_axis_level_db': on_axis_level_db,
            'off_axis_level_db': off_axis_level_db,
            'rejection_ratio_db': ratio_db,
            'calculated_at': datetime.utcnow().isoformat()
        }

    def get_rejection_thresholds(self) -> Dict[str, Any]:
        """
        Get noise rejection thresholds.

        Returns:
            Dictionary with thresholds

        Example:
            >>> thresholds = service.get_rejection_thresholds()
        """
        return {
            'minimum_rejection_db': self._noise_rejection_threshold_db,
            'recommended_rejection_db': 20.0,
            'excellent_rejection_db': 25.0,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def measure_speaker_isolation(
        self,
        target_speaker_level_db: float,
        interfering_speaker_level_db: float
    ) -> Dict[str, Any]:
        """
        Measure speaker isolation.

        Args:
            target_speaker_level_db: Target speaker level
            interfering_speaker_level_db: Interfering speaker level

        Returns:
            Dictionary with isolation measurement

        Example:
            >>> result = service.measure_speaker_isolation(-15.0, -35.0)
        """
        measurement_id = str(uuid.uuid4())

        isolation_db = target_speaker_level_db - interfering_speaker_level_db
        passed = isolation_db >= self._isolation_threshold_db

        measurement = {
            'type': 'speaker_isolation',
            'target': target_speaker_level_db,
            'interfering': interfering_speaker_level_db,
            'isolation': isolation_db
        }
        self._measurements.append(measurement)

        return {
            'measurement_id': measurement_id,
            'target_speaker_level_db': target_speaker_level_db,
            'interfering_speaker_level_db': interfering_speaker_level_db,
            'isolation_db': isolation_db,
            'threshold_db': self._isolation_threshold_db,
            'passed': passed,
            'measured_at': datetime.utcnow().isoformat()
        }

    def calculate_isolation_ratio(
        self,
        primary_level_db: float,
        secondary_level_db: float
    ) -> Dict[str, Any]:
        """
        Calculate speaker isolation ratio.

        Args:
            primary_level_db: Primary speaker level
            secondary_level_db: Secondary speaker level

        Returns:
            Dictionary with isolation ratio

        Example:
            >>> result = service.calculate_isolation_ratio(-10.0, -32.0)
        """
        calculation_id = str(uuid.uuid4())

        ratio_db = primary_level_db - secondary_level_db

        return {
            'calculation_id': calculation_id,
            'primary_level_db': primary_level_db,
            'secondary_level_db': secondary_level_db,
            'isolation_ratio_db': ratio_db,
            'calculated_at': datetime.utcnow().isoformat()
        }

    def validate_isolation(
        self,
        isolation_db: float
    ) -> Dict[str, Any]:
        """
        Validate speaker isolation.

        Args:
            isolation_db: Isolation in dB

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_isolation(22.0)
        """
        validation_id = str(uuid.uuid4())

        passed = isolation_db >= self._isolation_threshold_db

        return {
            'validation_id': validation_id,
            'isolation_db': isolation_db,
            'threshold_db': self._isolation_threshold_db,
            'passed': passed,
            'rating': 'excellent' if isolation_db >= 25 else 'good' if passed else 'poor',
            'validated_at': datetime.utcnow().isoformat()
        }

    def get_beam_pattern(
        self,
        array_id: str
    ) -> Dict[str, Any]:
        """
        Get beam pattern for array.

        Args:
            array_id: Array identifier

        Returns:
            Dictionary with beam pattern

        Example:
            >>> pattern = service.get_beam_pattern('array_1')
        """
        return {
            'array_id': array_id,
            'pattern_type': 'cardioid',
            'main_lobe_width_degrees': 60,
            'side_lobe_level_db': -20,
            'null_depth_db': -40,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def optimize_beam_width(
        self,
        target_width_degrees: float,
        environment: str = 'car_cabin'
    ) -> Dict[str, Any]:
        """
        Optimize beam width for environment.

        Args:
            target_width_degrees: Target beam width
            environment: Target environment

        Returns:
            Dictionary with optimization result

        Example:
            >>> result = service.optimize_beam_width(60.0, 'car_cabin')
        """
        optimization_id = str(uuid.uuid4())

        recommended_widths = {
            'car_cabin': 60,
            'conference': 90,
            'far_field': 45
        }

        recommended = recommended_widths.get(environment, 60)
        optimal = abs(target_width_degrees - recommended) <= 15

        return {
            'optimization_id': optimization_id,
            'target_width_degrees': target_width_degrees,
            'environment': environment,
            'recommended_width_degrees': recommended,
            'is_optimal': optimal,
            'optimized_at': datetime.utcnow().isoformat()
        }

    def calculate_directivity_index(
        self,
        on_axis_sensitivity_db: float,
        average_sensitivity_db: float
    ) -> Dict[str, Any]:
        """
        Calculate directivity index.

        Args:
            on_axis_sensitivity_db: On-axis sensitivity
            average_sensitivity_db: Average sensitivity

        Returns:
            Dictionary with directivity index

        Example:
            >>> result = service.calculate_directivity_index(-26.0, -32.0)
        """
        calculation_id = str(uuid.uuid4())

        di = on_axis_sensitivity_db - average_sensitivity_db

        return {
            'calculation_id': calculation_id,
            'on_axis_sensitivity_db': on_axis_sensitivity_db,
            'average_sensitivity_db': average_sensitivity_db,
            'directivity_index_db': di,
            'calculated_at': datetime.utcnow().isoformat()
        }

    def generate_performance_report(
        self,
        array_id: str
    ) -> Dict[str, Any]:
        """
        Generate beamforming performance report.

        Args:
            array_id: Array identifier

        Returns:
            Dictionary with performance report

        Example:
            >>> report = service.generate_performance_report('array_1')
        """
        report_id = str(uuid.uuid4())

        steering_measurements = [m for m in self._measurements
                                 if m.get('type') == 'steering_accuracy']
        noise_measurements = [m for m in self._measurements
                              if m.get('type') == 'noise_rejection']
        isolation_measurements = [m for m in self._measurements
                                  if m.get('type') == 'speaker_isolation']

        return {
            'report_id': report_id,
            'array_id': array_id,
            'steering_tests': len(steering_measurements),
            'noise_tests': len(noise_measurements),
            'isolation_tests': len(isolation_measurements),
            'total_measurements': len(self._measurements),
            'generated_at': datetime.utcnow().isoformat()
        }

    def get_beamforming_performance_config(self) -> Dict[str, Any]:
        """
        Get beamforming performance service configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_beamforming_performance_config()
        """
        return {
            'steering_range': self._steering_range,
            'accuracy_threshold_degrees': self._accuracy_threshold_degrees,
            'noise_rejection_threshold_db': self._noise_rejection_threshold_db,
            'isolation_threshold_db': self._isolation_threshold_db,
            'total_measurements': len(self._measurements),
            'features': [
                'beam_steering', 'noise_rejection',
                'speaker_isolation', 'performance_metrics'
            ]
        }
