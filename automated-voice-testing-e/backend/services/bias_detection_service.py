"""
Bias Detection Service for voice AI testing.

This service detects various types of bias in voice AI systems including
gender bias, accent bias, and age group bias.

Key features:
- Gender bias in recognition
- Accent bias analysis
- Age group bias detection

Example:
    >>> service = BiasDetectionService()
    >>> result = service.detect_gender_bias(data)
"""

from typing import List, Dict, Any
from datetime import datetime
import uuid


class BiasDetectionService:
    """
    Service for bias detection.

    Provides gender, accent, and age bias detection
    and analysis capabilities.

    Example:
        >>> service = BiasDetectionService()
        >>> config = service.get_bias_config()
    """

    def __init__(self):
        """Initialize the bias detection service."""
        self._bias_reports: List[Dict[str, Any]] = []

    def detect_gender_bias(
        self,
        data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Detect gender bias in recognition results.

        Args:
            data: Test results with gender info

        Returns:
            Dictionary with gender bias detection result

        Example:
            >>> result = service.detect_gender_bias(data)
        """
        detection_id = str(uuid.uuid4())

        male_metrics = {'correct': 0, 'total': 0}
        female_metrics = {'correct': 0, 'total': 0}

        for item in data:
            gender = item.get('gender', '').lower()
            if gender == 'male':
                male_metrics['total'] += 1
                if item.get('correct', False):
                    male_metrics['correct'] += 1
            elif gender == 'female':
                female_metrics['total'] += 1
                if item.get('correct', False):
                    female_metrics['correct'] += 1

        male_accuracy = male_metrics['correct'] / male_metrics['total'] if male_metrics['total'] > 0 else 0
        female_accuracy = female_metrics['correct'] / female_metrics['total'] if female_metrics['total'] > 0 else 0

        bias_score = abs(male_accuracy - female_accuracy)

        return {
            'detection_id': detection_id,
            'male_accuracy': round(male_accuracy, 4),
            'female_accuracy': round(female_accuracy, 4),
            'bias_score': round(bias_score, 4),
            'bias_detected': bias_score > 0.05,
            'bias_direction': 'male' if male_accuracy > female_accuracy else 'female' if female_accuracy > male_accuracy else 'none',
            'detected_at': datetime.utcnow().isoformat()
        }

    def get_gender_metrics(self) -> Dict[str, Any]:
        """
        Get gender-related metrics definitions.

        Returns:
            Dictionary with gender metrics

        Example:
            >>> metrics = service.get_gender_metrics()
        """
        return {
            'metrics': [
                {'name': 'accuracy_gap', 'description': 'Difference in accuracy between genders'},
                {'name': 'error_rate_ratio', 'description': 'Ratio of error rates'},
                {'name': 'false_positive_disparity', 'description': 'FP rate difference'}
            ],
            'threshold': 0.05,
            'categories': ['male', 'female', 'other'],
            'generated_at': datetime.utcnow().isoformat()
        }

    def detect_accent_bias(
        self,
        data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Detect accent bias in recognition results.

        Args:
            data: Test results with accent info

        Returns:
            Dictionary with accent bias detection result

        Example:
            >>> result = service.detect_accent_bias(data)
        """
        detection_id = str(uuid.uuid4())

        accent_metrics = {}

        for item in data:
            accent = item.get('accent', 'unknown')
            if accent not in accent_metrics:
                accent_metrics[accent] = {'correct': 0, 'total': 0}
            accent_metrics[accent]['total'] += 1
            if item.get('correct', False):
                accent_metrics[accent]['correct'] += 1

        accent_accuracies = {}
        for accent, metrics in accent_metrics.items():
            accuracy = metrics['correct'] / metrics['total'] if metrics['total'] > 0 else 0
            accent_accuracies[accent] = round(accuracy, 4)

        if accent_accuracies:
            max_acc = max(accent_accuracies.values())
            min_acc = min(accent_accuracies.values())
            bias_score = max_acc - min_acc
        else:
            bias_score = 0

        return {
            'detection_id': detection_id,
            'accent_accuracies': accent_accuracies,
            'bias_score': round(bias_score, 4),
            'bias_detected': bias_score > 0.1,
            'highest_accuracy_accent': max(accent_accuracies, key=accent_accuracies.get) if accent_accuracies else None,
            'lowest_accuracy_accent': min(accent_accuracies, key=accent_accuracies.get) if accent_accuracies else None,
            'detected_at': datetime.utcnow().isoformat()
        }

    def get_accent_metrics(self) -> Dict[str, Any]:
        """
        Get accent-related metrics definitions.

        Returns:
            Dictionary with accent metrics

        Example:
            >>> metrics = service.get_accent_metrics()
        """
        return {
            'metrics': [
                {'name': 'accuracy_variance', 'description': 'Variance in accuracy across accents'},
                {'name': 'max_min_gap', 'description': 'Gap between best and worst performing'},
                {'name': 'native_non_native_ratio', 'description': 'Native vs non-native performance'}
            ],
            'threshold': 0.1,
            'accents': ['US', 'UK', 'Australian', 'Indian', 'Chinese', 'Spanish'],
            'generated_at': datetime.utcnow().isoformat()
        }

    def detect_age_bias(
        self,
        data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Detect age group bias in recognition results.

        Args:
            data: Test results with age info

        Returns:
            Dictionary with age bias detection result

        Example:
            >>> result = service.detect_age_bias(data)
        """
        detection_id = str(uuid.uuid4())

        age_groups = {
            '18-30': {'correct': 0, 'total': 0},
            '31-50': {'correct': 0, 'total': 0},
            '51+': {'correct': 0, 'total': 0}
        }

        for item in data:
            age = item.get('age', 0)
            if 18 <= age <= 30:
                group = '18-30'
            elif 31 <= age <= 50:
                group = '31-50'
            else:
                group = '51+'

            age_groups[group]['total'] += 1
            if item.get('correct', False):
                age_groups[group]['correct'] += 1

        age_accuracies = {}
        for group, metrics in age_groups.items():
            accuracy = metrics['correct'] / metrics['total'] if metrics['total'] > 0 else 0
            age_accuracies[group] = round(accuracy, 4)

        accuracies = [v for v in age_accuracies.values() if v > 0]
        if accuracies:
            bias_score = max(accuracies) - min(accuracies)
        else:
            bias_score = 0

        return {
            'detection_id': detection_id,
            'age_accuracies': age_accuracies,
            'bias_score': round(bias_score, 4),
            'bias_detected': bias_score > 0.08,
            'detected_at': datetime.utcnow().isoformat()
        }

    def get_age_metrics(self) -> Dict[str, Any]:
        """
        Get age-related metrics definitions.

        Returns:
            Dictionary with age metrics

        Example:
            >>> metrics = service.get_age_metrics()
        """
        return {
            'metrics': [
                {'name': 'group_accuracy_variance', 'description': 'Variance across age groups'},
                {'name': 'elderly_gap', 'description': 'Gap for elderly users'},
                {'name': 'youth_performance', 'description': 'Young user performance ratio'}
            ],
            'threshold': 0.08,
            'age_groups': ['18-30', '31-50', '51+'],
            'generated_at': datetime.utcnow().isoformat()
        }

    def generate_bias_report(
        self,
        data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive bias detection report.

        Args:
            data: Test results

        Returns:
            Dictionary with bias report

        Example:
            >>> report = service.generate_bias_report(data)
        """
        report_id = str(uuid.uuid4())

        gender_result = self.detect_gender_bias(data)
        accent_result = self.detect_accent_bias(data)
        age_result = self.detect_age_bias(data)

        biases_detected = []
        if gender_result['bias_detected']:
            biases_detected.append('gender')
        if accent_result['bias_detected']:
            biases_detected.append('accent')
        if age_result['bias_detected']:
            biases_detected.append('age')

        report = {
            'report_id': report_id,
            'gender_bias': gender_result,
            'accent_bias': accent_result,
            'age_bias': age_result,
            'biases_detected': biases_detected,
            'overall_bias_score': round(
                (gender_result['bias_score'] + accent_result['bias_score'] + age_result['bias_score']) / 3,
                4
            ),
            'recommendations': [],
            'generated_at': datetime.utcnow().isoformat()
        }

        if 'gender' in biases_detected:
            report['recommendations'].append('Review training data gender balance')
        if 'accent' in biases_detected:
            report['recommendations'].append('Augment training with diverse accents')
        if 'age' in biases_detected:
            report['recommendations'].append('Include more elderly voice samples')

        self._bias_reports.append(report)
        return report

    def get_bias_config(self) -> Dict[str, Any]:
        """
        Get bias detection configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_bias_config()
        """
        return {
            'total_reports': len(self._bias_reports),
            'bias_types': ['gender', 'accent', 'age', 'region'],
            'thresholds': {
                'gender': 0.05,
                'accent': 0.1,
                'age': 0.08
            },
            'metrics': {
                'gender': self.get_gender_metrics()['metrics'],
                'accent': self.get_accent_metrics()['metrics'],
                'age': self.get_age_metrics()['metrics']
            }
        }
