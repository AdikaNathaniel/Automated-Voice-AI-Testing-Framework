"""
Accent Robustness Metrics Service for voice AI testing.

This service provides accent robustness metrics for evaluating
voice AI system performance across different accents.

Key features:
- WER by accent
- Intent accuracy by accent
- Accent detection accuracy

Example:
    >>> service = AccentRobustnessService()
    >>> wer = service.calculate_wer_by_accent('en-US', results)
    >>> report = service.get_wer_report()
"""

from typing import List, Dict, Any
from datetime import datetime
import uuid


class AccentRobustnessService:
    """
    Service for accent robustness metrics.

    Provides WER calculation by accent, intent accuracy
    analysis, and accent detection accuracy metrics.

    Example:
        >>> service = AccentRobustnessService()
        >>> config = service.get_robustness_config()
        >>> service.set_baseline_threshold(0.15)
    """

    def __init__(self):
        """Initialize the accent robustness service."""
        self._baseline_threshold = 0.15
        self._wer_data: Dict[str, List[Dict[str, Any]]] = {}
        self._intent_data: Dict[str, List[Dict[str, Any]]] = {}
        self._detection_data: List[Dict[str, Any]] = []

    def calculate_wer_by_accent(
        self,
        accent_code: str,
        results: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate WER for specific accent.

        Args:
            accent_code: Accent code (e.g., 'en-US')
            results: Test results to calculate from

        Returns:
            Dictionary with WER calculation

        Example:
            >>> wer = service.calculate_wer_by_accent('en-US', results)
        """
        results = results or []
        
        # Calculate WER from results
        total_words = 0
        total_errors = 0
        
        for result in results:
            total_words += result.get('total_words', 100)
            total_errors += result.get('errors', 10)
        
        wer = total_errors / total_words if total_words > 0 else 0.0
        
        wer_result = {
            'accent_code': accent_code,
            'wer': wer,
            'total_words': total_words,
            'total_errors': total_errors,
            'samples': len(results),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if accent_code not in self._wer_data:
            self._wer_data[accent_code] = []
        self._wer_data[accent_code].append(wer_result)
        
        return wer_result

    def get_wer_report(
        self,
        accent_code: str = None
    ) -> Dict[str, Any]:
        """
        Get WER report for accent(s).

        Args:
            accent_code: Optional specific accent

        Returns:
            Dictionary with WER report

        Example:
            >>> report = service.get_wer_report()
        """
        if accent_code:
            data = self._wer_data.get(accent_code, [])
            avg_wer = sum(d['wer'] for d in data) / len(data) if data else 0
            return {
                'accent_code': accent_code,
                'avg_wer': avg_wer,
                'samples': len(data),
                'history': data
            }
        
        # All accents
        report = {}
        for code, data in self._wer_data.items():
            avg_wer = sum(d['wer'] for d in data) / len(data) if data else 0
            report[code] = {
                'avg_wer': avg_wer,
                'samples': len(data)
            }
        
        return {
            'accents': report,
            'total_accents': len(report)
        }

    def compare_wer_across_accents(
        self,
        accent_codes: List[str] = None
    ) -> Dict[str, Any]:
        """
        Compare WER across multiple accents.

        Args:
            accent_codes: List of accent codes to compare

        Returns:
            Dictionary with comparison results

        Example:
            >>> comparison = service.compare_wer_across_accents(['en-US', 'en-GB'])
        """
        codes = accent_codes or list(self._wer_data.keys())
        
        comparison = []
        for code in codes:
            data = self._wer_data.get(code, [])
            avg_wer = sum(d['wer'] for d in data) / len(data) if data else 0
            comparison.append({
                'accent_code': code,
                'avg_wer': avg_wer,
                'samples': len(data)
            })
        
        # Sort by WER
        comparison.sort(key=lambda x: x['avg_wer'])
        
        best = comparison[0] if comparison else None
        worst = comparison[-1] if comparison else None
        
        return {
            'comparison': comparison,
            'best_accent': best,
            'worst_accent': worst,
            'variance': self._calculate_variance([c['avg_wer'] for c in comparison])
        }

    def calculate_intent_accuracy(
        self,
        accent_code: str,
        results: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate intent accuracy for accent.

        Args:
            accent_code: Accent code
            results: Test results

        Returns:
            Dictionary with intent accuracy

        Example:
            >>> accuracy = service.calculate_intent_accuracy('en-US', results)
        """
        results = results or []
        
        correct = sum(1 for r in results if r.get('correct', True))
        total = len(results) if results else 1
        
        accuracy = correct / total if total > 0 else 0.0
        
        result = {
            'accent_code': accent_code,
            'accuracy': accuracy,
            'correct': correct,
            'total': total,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if accent_code not in self._intent_data:
            self._intent_data[accent_code] = []
        self._intent_data[accent_code].append(result)
        
        return result

    def get_intent_accuracy_report(
        self,
        accent_code: str = None
    ) -> Dict[str, Any]:
        """
        Get intent accuracy report.

        Args:
            accent_code: Optional specific accent

        Returns:
            Dictionary with accuracy report

        Example:
            >>> report = service.get_intent_accuracy_report()
        """
        if accent_code:
            data = self._intent_data.get(accent_code, [])
            avg = sum(d['accuracy'] for d in data) / len(data) if data else 0
            return {
                'accent_code': accent_code,
                'avg_accuracy': avg,
                'samples': len(data),
                'history': data
            }
        
        report = {}
        for code, data in self._intent_data.items():
            avg = sum(d['accuracy'] for d in data) / len(data) if data else 0
            report[code] = {
                'avg_accuracy': avg,
                'samples': len(data)
            }
        
        return {
            'accents': report,
            'total_accents': len(report)
        }

    def compare_intent_accuracy(
        self,
        accent_codes: List[str] = None
    ) -> Dict[str, Any]:
        """
        Compare intent accuracy across accents.

        Args:
            accent_codes: Accent codes to compare

        Returns:
            Dictionary with comparison

        Example:
            >>> comparison = service.compare_intent_accuracy(['en-US', 'en-GB'])
        """
        codes = accent_codes or list(self._intent_data.keys())
        
        comparison = []
        for code in codes:
            data = self._intent_data.get(code, [])
            avg = sum(d['accuracy'] for d in data) / len(data) if data else 0
            comparison.append({
                'accent_code': code,
                'avg_accuracy': avg,
                'samples': len(data)
            })
        
        comparison.sort(key=lambda x: x['avg_accuracy'], reverse=True)
        
        return {
            'comparison': comparison,
            'best_accent': comparison[0] if comparison else None,
            'worst_accent': comparison[-1] if comparison else None
        }

    def detect_accent(
        self,
        audio_data: bytes = None,
        reference_accent: str = None
    ) -> Dict[str, Any]:
        """
        Detect accent from audio.

        Args:
            audio_data: Audio to analyze
            reference_accent: Expected accent

        Returns:
            Dictionary with detection result

        Example:
            >>> result = service.detect_accent(audio, 'en-US')
        """
        # Simulated detection
        detected = reference_accent or 'en-US'
        confidence = 0.85
        correct = detected == reference_accent if reference_accent else True
        
        result = {
            'detection_id': str(uuid.uuid4()),
            'detected_accent': detected,
            'reference_accent': reference_accent,
            'confidence': confidence,
            'correct': correct,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self._detection_data.append(result)
        return result

    def get_detection_accuracy(self) -> Dict[str, Any]:
        """
        Get accent detection accuracy.

        Returns:
            Dictionary with detection accuracy

        Example:
            >>> accuracy = service.get_detection_accuracy()
        """
        if not self._detection_data:
            return {
                'accuracy': 0.0,
                'total_samples': 0,
                'correct': 0
            }
        
        correct = sum(1 for d in self._detection_data if d.get('correct', False))
        total = len(self._detection_data)
        
        return {
            'accuracy': correct / total if total > 0 else 0.0,
            'total_samples': total,
            'correct': correct,
            'avg_confidence': sum(d['confidence'] for d in self._detection_data) / total
        }

    def get_confusion_matrix(self) -> Dict[str, Any]:
        """
        Get accent detection confusion matrix.

        Returns:
            Dictionary with confusion matrix

        Example:
            >>> matrix = service.get_confusion_matrix()
        """
        matrix: Dict[str, Dict[str, int]] = {}
        
        for detection in self._detection_data:
            ref = detection.get('reference_accent', 'unknown')
            det = detection.get('detected_accent', 'unknown')
            
            if ref not in matrix:
                matrix[ref] = {}
            if det not in matrix[ref]:
                matrix[ref][det] = 0
            
            matrix[ref][det] += 1
        
        return {
            'matrix': matrix,
            'accents': list(matrix.keys()),
            'total_samples': len(self._detection_data)
        }

    def get_robustness_config(self) -> Dict[str, Any]:
        """
        Get robustness configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_robustness_config()
        """
        return {
            'baseline_threshold': self._baseline_threshold,
            'wer_accents': len(self._wer_data),
            'intent_accents': len(self._intent_data),
            'detection_samples': len(self._detection_data)
        }

    def set_baseline_threshold(
        self,
        threshold: float
    ) -> Dict[str, Any]:
        """
        Set baseline WER threshold.

        Args:
            threshold: WER threshold

        Returns:
            Dictionary with threshold setting

        Example:
            >>> result = service.set_baseline_threshold(0.15)
        """
        self._baseline_threshold = threshold
        return {
            'threshold': threshold,
            'configured': True
        }

    def get_robustness_summary(self) -> Dict[str, Any]:
        """
        Get overall robustness summary.

        Returns:
            Dictionary with robustness summary

        Example:
            >>> summary = service.get_robustness_summary()
        """
        self.get_wer_report()
        self.get_intent_accuracy_report()
        detection_accuracy = self.get_detection_accuracy()
        
        # Calculate overall scores
        all_wer = []
        for data in self._wer_data.values():
            all_wer.extend([d['wer'] for d in data])
        avg_wer = sum(all_wer) / len(all_wer) if all_wer else 0
        
        all_intent = []
        for data in self._intent_data.values():
            all_intent.extend([d['accuracy'] for d in data])
        avg_intent = sum(all_intent) / len(all_intent) if all_intent else 0
        
        return {
            'overall_wer': avg_wer,
            'overall_intent_accuracy': avg_intent,
            'detection_accuracy': detection_accuracy['accuracy'],
            'wer_below_threshold': avg_wer < self._baseline_threshold,
            'total_wer_samples': len(all_wer),
            'total_intent_samples': len(all_intent),
            'total_detection_samples': len(self._detection_data)
        }

    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of values."""
        if not values:
            return 0.0
        mean = sum(values) / len(values)
        return sum((v - mean) ** 2 for v in values) / len(values)

