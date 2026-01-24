"""
Far-Field Testing Service for voice AI testing.

This service provides far-field voice recognition testing
including distance-based accuracy and echo cancellation.

Key features:
- Distance-based accuracy testing
- Echo cancellation testing
- Background noise handling
- Signal-to-noise ratio calculation

Example:
    >>> service = FarFieldTestingService()
    >>> result = service.test_at_distance(command='hello', distance_meters=3.0)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import math


class FarFieldTestingService:
    """
    Service for far-field voice recognition testing.

    Provides tools for testing voice recognition at various
    distances and with different acoustic conditions.

    Example:
        >>> service = FarFieldTestingService()
        >>> config = service.get_far_field_config()
    """

    def __init__(self):
        """Initialize the far-field testing service."""
        self._test_results: Dict[str, Dict[str, Any]] = {}
        self._echo_tests: Dict[str, Dict[str, Any]] = {}

    def test_at_distance(
        self,
        command: str,
        distance_meters: float,
        ambient_noise_db: float = 30.0
    ) -> Dict[str, Any]:
        """
        Test voice recognition at a specific distance.

        Args:
            command: Command to test
            distance_meters: Distance from microphone
            ambient_noise_db: Ambient noise level

        Returns:
            Dictionary with test result

        Example:
            >>> result = service.test_at_distance('turn on lights', 3.0)
        """
        test_id = str(uuid.uuid4())

        # Simulate accuracy degradation with distance
        base_accuracy = 0.98
        distance_factor = math.exp(-0.1 * distance_meters)
        noise_factor = max(0.5, 1 - (ambient_noise_db - 30) / 100)
        accuracy = base_accuracy * distance_factor * noise_factor

        result = {
            'test_id': test_id,
            'command': command,
            'distance_meters': distance_meters,
            'ambient_noise_db': ambient_noise_db,
            'accuracy': round(accuracy, 3),
            'recognized': accuracy > 0.7,
            'tested_at': datetime.utcnow().isoformat()
        }

        self._test_results[test_id] = result

        return {
            'test_id': test_id,
            'command': command,
            'distance_meters': distance_meters,
            'accuracy': result['accuracy'],
            'recognized': result['recognized'],
            'success': True,
            'tested_at': result['tested_at']
        }

    def measure_accuracy(
        self,
        test_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Measure overall accuracy from tests.

        Args:
            test_ids: Optional specific test IDs

        Returns:
            Dictionary with accuracy metrics

        Example:
            >>> metrics = service.measure_accuracy()
        """
        measurement_id = str(uuid.uuid4())

        if test_ids:
            tests = [self._test_results[tid] for tid in test_ids if tid in self._test_results]
        else:
            tests = list(self._test_results.values())

        if not tests:
            return {
                'measurement_id': measurement_id,
                'total_tests': 0,
                'average_accuracy': 0.0,
                'measured_at': datetime.utcnow().isoformat()
            }

        accuracies = [t['accuracy'] for t in tests]
        avg_accuracy = sum(accuracies) / len(accuracies)
        recognized_count = sum(1 for t in tests if t['recognized'])

        return {
            'measurement_id': measurement_id,
            'total_tests': len(tests),
            'average_accuracy': round(avg_accuracy, 3),
            'recognition_rate': round(recognized_count / len(tests), 3),
            'min_accuracy': round(min(accuracies), 3),
            'max_accuracy': round(max(accuracies), 3),
            'measured_at': datetime.utcnow().isoformat()
        }

    def get_distance_report(
        self,
        group_by_distance: bool = True
    ) -> Dict[str, Any]:
        """
        Get report of distance-based tests.

        Args:
            group_by_distance: Group results by distance

        Returns:
            Dictionary with distance report

        Example:
            >>> report = service.get_distance_report()
        """
        report_id = str(uuid.uuid4())

        tests = list(self._test_results.values())

        if group_by_distance and tests:
            by_distance: Dict[float, List[Dict[str, Any]]] = {}
            for test in tests:
                dist = test['distance_meters']
                if dist not in by_distance:
                    by_distance[dist] = []
                by_distance[dist].append(test)

            grouped = {
                str(dist): {
                    'count': len(t_list),
                    'avg_accuracy': round(sum(t['accuracy'] for t in t_list) / len(t_list), 3)
                }
                for dist, t_list in by_distance.items()
            }
        else:
            grouped = {}

        return {
            'report_id': report_id,
            'total_tests': len(tests),
            'by_distance': grouped,
            'grouped': group_by_distance,
            'generated_at': datetime.utcnow().isoformat()
        }

    def test_echo_cancellation(
        self,
        command: str,
        echo_delay_ms: float = 50.0,
        echo_level_db: float = -10.0
    ) -> Dict[str, Any]:
        """
        Test echo cancellation capability.

        Args:
            command: Command to test
            echo_delay_ms: Echo delay in milliseconds
            echo_level_db: Echo level in dB

        Returns:
            Dictionary with echo test result

        Example:
            >>> result = service.test_echo_cancellation('play music', 100.0, -6.0)
        """
        test_id = str(uuid.uuid4())

        # Simulate echo cancellation effectiveness
        # Better cancellation with lower echo levels and shorter delays
        delay_factor = max(0.5, 1 - echo_delay_ms / 500)
        level_factor = max(0.5, 1 + echo_level_db / 30)
        cancellation_effectiveness = delay_factor * level_factor

        result = {
            'test_id': test_id,
            'command': command,
            'echo_delay_ms': echo_delay_ms,
            'echo_level_db': echo_level_db,
            'cancellation_effectiveness': round(cancellation_effectiveness, 3),
            'passed': cancellation_effectiveness > 0.6,
            'tested_at': datetime.utcnow().isoformat()
        }

        self._echo_tests[test_id] = result

        return {
            'test_id': test_id,
            'command': command,
            'echo_delay_ms': echo_delay_ms,
            'echo_level_db': echo_level_db,
            'effectiveness': result['cancellation_effectiveness'],
            'passed': result['passed'],
            'success': True,
            'tested_at': result['tested_at']
        }

    def measure_echo_reduction(
        self,
        test_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Measure echo reduction across tests.

        Args:
            test_ids: Optional specific test IDs

        Returns:
            Dictionary with echo reduction metrics

        Example:
            >>> metrics = service.measure_echo_reduction()
        """
        measurement_id = str(uuid.uuid4())

        if test_ids:
            tests = [self._echo_tests[tid] for tid in test_ids if tid in self._echo_tests]
        else:
            tests = list(self._echo_tests.values())

        if not tests:
            return {
                'measurement_id': measurement_id,
                'total_tests': 0,
                'average_effectiveness': 0.0,
                'measured_at': datetime.utcnow().isoformat()
            }

        effectiveness = [t['cancellation_effectiveness'] for t in tests]
        avg_effectiveness = sum(effectiveness) / len(effectiveness)
        passed_count = sum(1 for t in tests if t['passed'])

        return {
            'measurement_id': measurement_id,
            'total_tests': len(tests),
            'average_effectiveness': round(avg_effectiveness, 3),
            'pass_rate': round(passed_count / len(tests), 3),
            'min_effectiveness': round(min(effectiveness), 3),
            'max_effectiveness': round(max(effectiveness), 3),
            'measured_at': datetime.utcnow().isoformat()
        }

    def get_echo_report(self) -> Dict[str, Any]:
        """
        Get report of echo cancellation tests.

        Returns:
            Dictionary with echo report

        Example:
            >>> report = service.get_echo_report()
        """
        report_id = str(uuid.uuid4())

        tests = list(self._echo_tests.values())
        passed = [t for t in tests if t['passed']]
        failed = [t for t in tests if not t['passed']]

        return {
            'report_id': report_id,
            'total_tests': len(tests),
            'passed_count': len(passed),
            'failed_count': len(failed),
            'pass_rate': round(len(passed) / len(tests), 3) if tests else 0.0,
            'tests': tests,
            'generated_at': datetime.utcnow().isoformat()
        }

    def test_with_background_noise(
        self,
        command: str,
        noise_type: str,
        noise_level_db: float
    ) -> Dict[str, Any]:
        """
        Test voice recognition with background noise.

        Args:
            command: Command to test
            noise_type: Type of noise (white, pink, babble, traffic)
            noise_level_db: Noise level in dB

        Returns:
            Dictionary with noise test result

        Example:
            >>> result = service.test_with_background_noise('set timer', 'babble', 60.0)
        """
        test_id = str(uuid.uuid4())

        # Different noise types have different impacts
        noise_penalties = {
            'white': 0.1,
            'pink': 0.15,
            'babble': 0.25,
            'traffic': 0.2,
            'music': 0.18
        }

        penalty = noise_penalties.get(noise_type, 0.15)
        noise_impact = max(0.3, 1 - penalty * (noise_level_db / 50))
        accuracy = round(0.95 * noise_impact, 3)

        return {
            'test_id': test_id,
            'command': command,
            'noise_type': noise_type,
            'noise_level_db': noise_level_db,
            'accuracy': accuracy,
            'recognized': accuracy > 0.6,
            'success': True,
            'tested_at': datetime.utcnow().isoformat()
        }

    def calculate_snr(
        self,
        signal_level_db: float,
        noise_level_db: float
    ) -> Dict[str, Any]:
        """
        Calculate signal-to-noise ratio.

        Args:
            signal_level_db: Signal level in dB
            noise_level_db: Noise level in dB

        Returns:
            Dictionary with SNR calculation

        Example:
            >>> snr = service.calculate_snr(70.0, 40.0)
        """
        calculation_id = str(uuid.uuid4())

        snr = signal_level_db - noise_level_db

        # Quality assessment based on SNR
        if snr >= 30:
            quality = 'excellent'
        elif snr >= 20:
            quality = 'good'
        elif snr >= 10:
            quality = 'acceptable'
        elif snr >= 0:
            quality = 'poor'
        else:
            quality = 'unusable'

        return {
            'calculation_id': calculation_id,
            'signal_level_db': signal_level_db,
            'noise_level_db': noise_level_db,
            'snr_db': snr,
            'quality': quality,
            'calculated_at': datetime.utcnow().isoformat()
        }

    def test_wake_word(
        self,
        wake_word: str,
        audio_samples: int = 100,
        distance_meters: float = 2.0
    ) -> Dict[str, Any]:
        """
        Test wake word detection sensitivity.

        Args:
            wake_word: Wake word to test
            audio_samples: Number of test samples
            distance_meters: Test distance

        Returns:
            Dictionary with wake word test result

        Example:
            >>> result = service.test_wake_word('hey assistant', 100, 3.0)
        """
        test_id = str(uuid.uuid4())

        # Simulate wake word detection
        distance_factor = math.exp(-0.05 * distance_meters)
        base_detection_rate = 0.95
        detection_rate = base_detection_rate * distance_factor

        detections = int(audio_samples * detection_rate)
        misses = audio_samples - detections

        return {
            'test_id': test_id,
            'wake_word': wake_word,
            'samples_tested': audio_samples,
            'distance_meters': distance_meters,
            'detections': detections,
            'misses': misses,
            'detection_rate': round(detection_rate, 3),
            'success': detection_rate > 0.8,
            'tested_at': datetime.utcnow().isoformat()
        }

    def measure_false_acceptance(
        self,
        wake_word: str,
        negative_samples: int = 1000
    ) -> Dict[str, Any]:
        """
        Measure false acceptance rate for wake word.

        Args:
            wake_word: Wake word to test
            negative_samples: Number of negative samples

        Returns:
            Dictionary with false acceptance metrics

        Example:
            >>> result = service.measure_false_acceptance('hey assistant', 1000)
        """
        measurement_id = str(uuid.uuid4())

        # Simulate false acceptance rate (should be very low)
        import random
        random.seed(hash(wake_word))
        false_accepts = random.randint(0, max(1, negative_samples // 100))
        far = false_accepts / negative_samples

        return {
            'measurement_id': measurement_id,
            'wake_word': wake_word,
            'negative_samples': negative_samples,
            'false_accepts': false_accepts,
            'false_acceptance_rate': round(far, 4),
            'passed': far < 0.01,
            'measured_at': datetime.utcnow().isoformat()
        }

    def get_far_field_config(self) -> Dict[str, Any]:
        """
        Get far-field testing configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_far_field_config()
        """
        return {
            'total_distance_tests': len(self._test_results),
            'total_echo_tests': len(self._echo_tests),
            'supported_distances': [0.5, 1.0, 2.0, 3.0, 5.0, 10.0],
            'supported_noise_types': ['white', 'pink', 'babble', 'traffic', 'music'],
            'echo_delay_range_ms': [10, 500],
            'features': [
                'distance_testing', 'echo_cancellation',
                'background_noise', 'snr_calculation',
                'accuracy_measurement'
            ]
        }
