"""
ITU Standards Speech Quality Service for voice AI testing.

This service provides ITU standards compliance testing for
automotive voice AI speech quality.

Key standards:
- ITU-T P.862 (PESQ) - Perceptual Evaluation of Speech Quality
- ITU-T P.863 (POLQA) - Perceptual Objective Listening Quality
- ITU-T G.168 - Digital network echo cancellers

Example:
    >>> service = ITUSpeechQualityService()
    >>> result = service.evaluate_pesq(audio_data)
"""

from typing import List, Dict, Any
from datetime import datetime
import uuid


class ITUSpeechQualityService:
    """
    Service for ITU speech quality standards compliance testing.

    Provides automotive voice AI testing against ITU standards
    for speech quality evaluation and echo cancellation.

    Example:
        >>> service = ITUSpeechQualityService()
        >>> config = service.get_itu_speech_quality_config()
    """

    def __init__(self):
        """Initialize the ITU speech quality service."""
        self._standards = {
            'P.862': 'PESQ - Perceptual Evaluation of Speech Quality',
            'P.863': 'POLQA - Perceptual Objective Listening Quality',
            'G.168': 'Digital network echo cancellers'
        }
        self._test_results: List[Dict[str, Any]] = []

    def evaluate_pesq(
        self,
        audio_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate speech quality using PESQ (P.862).

        Args:
            audio_data: Audio data for evaluation

        Returns:
            Dictionary with PESQ evaluation result

        Example:
            >>> result = service.evaluate_pesq({'snr': 20})
        """
        evaluation_id = str(uuid.uuid4())

        # PESQ scoring (1.0 to 4.5 MOS scale)
        snr = audio_data.get('snr_db', 20)
        distortion = audio_data.get('distortion', 0)

        # Simulated PESQ calculation
        base_score = min(4.5, 1.0 + (snr / 10))
        score = max(1.0, base_score - distortion * 0.5)
        mos_score = round(score, 2)

        quality_rating = 'poor'
        if mos_score >= 4.0:
            quality_rating = 'excellent'
        elif mos_score >= 3.5:
            quality_rating = 'good'
        elif mos_score >= 3.0:
            quality_rating = 'fair'
        elif mos_score >= 2.5:
            quality_rating = 'poor'
        else:
            quality_rating = 'bad'

        return {
            'evaluation_id': evaluation_id,
            'standard': 'ITU-T P.862',
            'mos_score': mos_score,
            'quality_rating': quality_rating,
            'min_score': 1.0,
            'max_score': 4.5,
            'evaluated_at': datetime.utcnow().isoformat()
        }

    def check_p862_compliance(
        self,
        test_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check ITU-T P.862 (PESQ) compliance.

        Args:
            test_data: Test data with PESQ metrics

        Returns:
            Dictionary with compliance result

        Example:
            >>> result = service.check_p862_compliance({'mos_score': 3.5})
        """
        check_id = str(uuid.uuid4())

        violations: List[Dict[str, str]] = []

        # P.862 requirements
        mos_score = test_data.get('mos_score', 0)
        if mos_score < 3.0:
            violations.append({
                'requirement': 'minimum_mos',
                'message': f'MOS score {mos_score} below 3.0 minimum'
            })

        sample_rate = test_data.get('sample_rate', 0)
        if sample_rate not in [8000, 16000]:
            violations.append({
                'requirement': 'sample_rate',
                'message': 'Sample rate must be 8kHz or 16kHz'
            })

        compliant = len(violations) == 0

        result = {
            'standard': 'P.862',
            'compliant': compliant,
            'violations': violations
        }
        self._test_results.append(result)

        return {
            'check_id': check_id,
            'standard': 'ITU-T P.862',
            'compliant': compliant,
            'mos_score': mos_score,
            'violations': violations,
            'checked_at': datetime.utcnow().isoformat()
        }

    def evaluate_polqa(
        self,
        audio_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate speech quality using POLQA (P.863).

        Args:
            audio_data: Audio data for evaluation

        Returns:
            Dictionary with POLQA evaluation result

        Example:
            >>> result = service.evaluate_polqa({'snr': 25})
        """
        evaluation_id = str(uuid.uuid4())

        # POLQA scoring (1.0 to 5.0 MOS-LQO scale)
        snr = audio_data.get('snr_db', 25)
        codec_quality = audio_data.get('codec_quality', 1.0)

        # Simulated POLQA calculation
        base_score = min(5.0, 1.0 + (snr / 8))
        score = max(1.0, base_score * codec_quality)
        mos_lqo = round(score, 2)

        return {
            'evaluation_id': evaluation_id,
            'standard': 'ITU-T P.863',
            'mos_lqo_score': mos_lqo,
            'min_score': 1.0,
            'max_score': 5.0,
            'mode': audio_data.get('mode', 'super_wideband'),
            'evaluated_at': datetime.utcnow().isoformat()
        }

    def check_p863_compliance(
        self,
        test_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check ITU-T P.863 (POLQA) compliance.

        Args:
            test_data: Test data with POLQA metrics

        Returns:
            Dictionary with compliance result

        Example:
            >>> result = service.check_p863_compliance({'mos_lqo': 4.0})
        """
        check_id = str(uuid.uuid4())

        violations: List[Dict[str, str]] = []

        # P.863 requirements
        mos_lqo = test_data.get('mos_lqo_score', 0)
        if mos_lqo < 3.5:
            violations.append({
                'requirement': 'minimum_mos_lqo',
                'message': f'MOS-LQO score {mos_lqo} below 3.5 minimum'
            })

        bandwidth = test_data.get('bandwidth', '')
        valid_bandwidths = ['narrowband', 'wideband', 'super_wideband', 'fullband']
        if bandwidth and bandwidth not in valid_bandwidths:
            violations.append({
                'requirement': 'bandwidth',
                'message': f'Invalid bandwidth mode: {bandwidth}'
            })

        compliant = len(violations) == 0

        result = {
            'standard': 'P.863',
            'compliant': compliant,
            'violations': violations
        }
        self._test_results.append(result)

        return {
            'check_id': check_id,
            'standard': 'ITU-T P.863',
            'compliant': compliant,
            'mos_lqo_score': mos_lqo,
            'violations': violations,
            'checked_at': datetime.utcnow().isoformat()
        }

    def check_g168_compliance(
        self,
        echo_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check ITU-T G.168 echo cancellation compliance.

        Args:
            echo_data: Echo cancellation test data

        Returns:
            Dictionary with compliance result

        Example:
            >>> result = service.check_g168_compliance({'erle_db': 30})
        """
        check_id = str(uuid.uuid4())

        violations: List[Dict[str, str]] = []

        # G.168 requirements (25 dB ERLE minimum)
        erle_db = echo_data.get('erle_db', 0)
        if erle_db < 25:
            violations.append({
                'requirement': 'minimum_erle',
                'message': f'ERLE {erle_db} dB below 25 dB minimum'
            })

        convergence_time = echo_data.get('convergence_time_ms', 0)
        if convergence_time > 500:
            violations.append({
                'requirement': 'convergence_time',
                'message': 'Convergence time exceeds 500ms'
            })

        double_talk = echo_data.get('double_talk_performance', True)
        if not double_talk:
            violations.append({
                'requirement': 'double_talk',
                'message': 'Poor double-talk performance'
            })

        compliant = len(violations) == 0

        result = {
            'standard': 'G.168',
            'compliant': compliant,
            'violations': violations
        }
        self._test_results.append(result)

        return {
            'check_id': check_id,
            'standard': 'ITU-T G.168',
            'compliant': compliant,
            'erle_db': erle_db,
            'minimum_erle_db': 25,
            'violations': violations,
            'checked_at': datetime.utcnow().isoformat()
        }

    def measure_erle(
        self,
        measurement_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Measure Echo Return Loss Enhancement (ERLE).

        Args:
            measurement_params: Measurement parameters

        Returns:
            Dictionary with ERLE measurement

        Example:
            >>> result = service.measure_erle({'echo_level': -30})
        """
        measurement_id = str(uuid.uuid4())

        reference_level = measurement_params.get('reference_level_db', 0)
        echo_level = measurement_params.get('echo_level_db', -30)

        # Calculate ERLE
        erle_db = abs(reference_level - echo_level)

        return {
            'measurement_id': measurement_id,
            'reference_level_db': reference_level,
            'echo_level_db': echo_level,
            'erle_db': round(erle_db, 1),
            'meets_g168': erle_db >= 25,
            'measurement_standard': 'ITU-T G.168',
            'measured_at': datetime.utcnow().isoformat()
        }

    def get_itu_speech_quality_config(self) -> Dict[str, Any]:
        """
        Get ITU speech quality service configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_itu_speech_quality_config()
        """
        return {
            'supported_standards': self._standards,
            'total_tests': len(self._test_results),
            'features': [
                'pesq_evaluation', 'polqa_evaluation',
                'g168_echo_cancellation', 'erle_measurement'
            ]
        }
