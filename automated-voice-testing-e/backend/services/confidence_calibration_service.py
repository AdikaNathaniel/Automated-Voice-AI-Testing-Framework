"""
Confidence Calibration Service for ASR performance analysis.

This service provides methods for analyzing the calibration of confidence scores
from ASR systems. A well-calibrated model's confidence scores match its actual
accuracy - when it says it's 80% confident, it should be correct 80% of the time.

Key metrics:
- Expected Calibration Error (ECE): Weighted average of bin-wise calibration errors
- Maximum Calibration Error (MCE): Worst-case calibration error across bins
- Reliability diagrams: Visual representation of calibration

Example:
    >>> service = ConfidenceCalibrationService()
    >>> predictions = [
    ...     {'confidence': 0.9, 'correct': True},
    ...     {'confidence': 0.8, 'correct': True},
    ...     {'confidence': 0.7, 'correct': False},
    ... ]
    >>> ece = service.calculate_ece(predictions)
    >>> metrics = service.get_calibration_metrics(predictions)
"""

from typing import List, Dict, Any, Optional
import math


class ConfidenceCalibrationService:
    """
    Service for confidence score calibration analysis.

    Provides methods for calculating calibration metrics, generating
    reliability diagram data, and analyzing confidence-accuracy correlation.

    Attributes:
        default_num_bins: Default number of bins for calibration analysis

    Example:
        >>> service = ConfidenceCalibrationService()
        >>> predictions = [{'confidence': 0.9, 'correct': True}]
        >>> ece = service.calculate_ece(predictions)
    """

    def __init__(self, default_num_bins: int = 10):
        """
        Initialize the calibration service.

        Args:
            default_num_bins: Default number of bins for calibration
        """
        self.default_num_bins = default_num_bins

    def bin_predictions(
        self,
        predictions: List[Dict[str, Any]],
        num_bins: int = 10
    ) -> Dict[int, List[Dict[str, Any]]]:
        """
        Bin predictions by confidence score.

        Args:
            predictions: List of prediction dicts with 'confidence' and 'correct' keys
            num_bins: Number of bins to divide confidence range [0, 1]

        Returns:
            Dictionary mapping bin index to list of predictions in that bin

        Example:
            >>> predictions = [
            ...     {'confidence': 0.95, 'correct': True},
            ...     {'confidence': 0.85, 'correct': True},
            ... ]
            >>> bins = service.bin_predictions(predictions, num_bins=10)
            >>> len(bins[9])  # Bin for [0.9, 1.0]
            1
        """
        bins: Dict[int, List[Dict[str, Any]]] = {i: [] for i in range(num_bins)}

        for pred in predictions:
            confidence = pred.get('confidence', 0.0)
            # Calculate bin index (0 to num_bins-1)
            bin_idx = min(int(confidence * num_bins), num_bins - 1)
            bins[bin_idx].append(pred)

        return bins

    def generate_reliability_diagram_data(
        self,
        predictions: List[Dict[str, Any]],
        num_bins: int = 10
    ) -> Dict[str, Any]:
        """
        Generate data for reliability diagram visualization.

        A reliability diagram plots mean confidence vs accuracy for each bin.
        Perfect calibration shows points along the diagonal.

        Args:
            predictions: List of prediction dicts with 'confidence' and 'correct' keys
            num_bins: Number of bins for the diagram

        Returns:
            Dictionary with:
                - bins: List of bin data (mean_confidence, accuracy, count)
                - perfect_calibration: Points for diagonal reference line
                - gap: Average gap between confidence and accuracy

        Example:
            >>> data = service.generate_reliability_diagram_data(predictions)
            >>> for bin_data in data['bins']:
            ...     print(f"Confidence: {bin_data['mean_confidence']:.2f}, "
            ...           f"Accuracy: {bin_data['accuracy']:.2f}")
        """
        if not predictions:
            return {
                'bins': [],
                'perfect_calibration': [(i/num_bins, i/num_bins) for i in range(num_bins + 1)],
                'gap': 0.0
            }

        bins = self.bin_predictions(predictions, num_bins)
        bin_data = []
        total_gap = 0.0
        total_samples = 0

        for bin_idx in range(num_bins):
            bin_preds = bins[bin_idx]
            if not bin_preds:
                continue

            confidences = [p['confidence'] for p in bin_preds]
            accuracies = [1.0 if p.get('correct', False) else 0.0 for p in bin_preds]

            mean_confidence = sum(confidences) / len(confidences)
            accuracy = sum(accuracies) / len(accuracies)
            count = len(bin_preds)

            bin_data.append({
                'bin_index': bin_idx,
                'mean_confidence': mean_confidence,
                'accuracy': accuracy,
                'count': count,
                'bin_lower': bin_idx / num_bins,
                'bin_upper': (bin_idx + 1) / num_bins
            })

            gap = abs(accuracy - mean_confidence)
            total_gap += gap * count
            total_samples += count

        avg_gap = total_gap / total_samples if total_samples > 0 else 0.0

        return {
            'bins': bin_data,
            'perfect_calibration': [(i/num_bins, i/num_bins) for i in range(num_bins + 1)],
            'gap': avg_gap
        }

    def calculate_ece(
        self,
        predictions: List[Dict[str, Any]],
        num_bins: int = 10
    ) -> float:
        """
        Calculate Expected Calibration Error (ECE).

        ECE is the weighted average of absolute differences between
        confidence and accuracy in each bin:
        ECE = sum(|accuracy_bin - confidence_bin| * fraction_in_bin)

        Lower ECE indicates better calibration (0 = perfect calibration).

        Args:
            predictions: List of prediction dicts with 'confidence' and 'correct' keys
            num_bins: Number of bins for calculation

        Returns:
            ECE value between 0 and 1

        Example:
            >>> predictions = [
            ...     {'confidence': 0.9, 'correct': True},
            ...     {'confidence': 0.8, 'correct': False},
            ... ]
            >>> ece = service.calculate_ece(predictions)
            >>> print(f"ECE: {ece:.4f}")
        """
        if not predictions:
            return 0.0

        bins = self.bin_predictions(predictions, num_bins)
        total_samples = len(predictions)
        ece = 0.0

        for bin_idx in range(num_bins):
            bin_preds = bins[bin_idx]
            if not bin_preds:
                continue

            confidences = [p['confidence'] for p in bin_preds]
            accuracies = [1.0 if p.get('correct', False) else 0.0 for p in bin_preds]

            mean_confidence = sum(confidences) / len(confidences)
            accuracy = sum(accuracies) / len(accuracies)
            bin_fraction = len(bin_preds) / total_samples

            ece += abs(accuracy - mean_confidence) * bin_fraction

        return ece

    def calculate_mce(
        self,
        predictions: List[Dict[str, Any]],
        num_bins: int = 10
    ) -> float:
        """
        Calculate Maximum Calibration Error (MCE).

        MCE is the maximum absolute difference between confidence and
        accuracy across all bins. It represents the worst-case calibration.

        Args:
            predictions: List of prediction dicts with 'confidence' and 'correct' keys
            num_bins: Number of bins for calculation

        Returns:
            MCE value between 0 and 1

        Example:
            >>> mce = service.calculate_mce(predictions)
            >>> print(f"MCE: {mce:.4f}")
        """
        if not predictions:
            return 0.0

        bins = self.bin_predictions(predictions, num_bins)
        mce = 0.0

        for bin_idx in range(num_bins):
            bin_preds = bins[bin_idx]
            if not bin_preds:
                continue

            confidences = [p['confidence'] for p in bin_preds]
            accuracies = [1.0 if p.get('correct', False) else 0.0 for p in bin_preds]

            mean_confidence = sum(confidences) / len(confidences)
            accuracy = sum(accuracies) / len(accuracies)

            calibration_error = abs(accuracy - mean_confidence)
            mce = max(mce, calibration_error)

        return mce

    def calculate_confidence_accuracy_correlation(
        self,
        predictions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate correlation between confidence scores and accuracy.

        Computes Pearson correlation coefficient and other statistics
        to analyze the relationship between confidence and correctness.

        Args:
            predictions: List of prediction dicts with 'confidence' and 'correct' keys

        Returns:
            Dictionary with:
                - pearson_r: Pearson correlation coefficient
                - mean_confidence: Average confidence score
                - accuracy: Overall accuracy
                - overconfidence: Mean(confidence) - accuracy (positive = overconfident)

        Example:
            >>> corr = service.calculate_confidence_accuracy_correlation(predictions)
            >>> print(f"Correlation: {corr['pearson_r']:.4f}")
        """
        if not predictions:
            return {
                'pearson_r': 0.0,
                'mean_confidence': 0.0,
                'accuracy': 0.0,
                'overconfidence': 0.0
            }

        confidences = [p['confidence'] for p in predictions]
        accuracies = [1.0 if p.get('correct', False) else 0.0 for p in predictions]

        n = len(predictions)
        mean_conf = sum(confidences) / n
        mean_acc = sum(accuracies) / n

        # Calculate Pearson correlation
        numerator = sum(
            (c - mean_conf) * (a - mean_acc)
            for c, a in zip(confidences, accuracies)
        )

        sum_sq_conf = sum((c - mean_conf) ** 2 for c in confidences)
        sum_sq_acc = sum((a - mean_acc) ** 2 for a in accuracies)

        denominator = math.sqrt(sum_sq_conf * sum_sq_acc)

        if denominator == 0:
            pearson_r = 0.0
        else:
            pearson_r = numerator / denominator

        return {
            'pearson_r': pearson_r,
            'mean_confidence': mean_conf,
            'accuracy': mean_acc,
            'overconfidence': mean_conf - mean_acc
        }

    def aggregate_word_confidences(
        self,
        word_confidences: List[float],
        method: str = 'mean'
    ) -> Optional[float]:
        """
        Aggregate per-word confidence scores into a single utterance confidence.

        Different aggregation methods have different properties:
        - mean: Average confidence (simple but may miss weak words)
        - min: Minimum confidence (conservative, sensitive to weak words)
        - geometric: Geometric mean (balanced, penalizes low values)

        Args:
            word_confidences: List of per-word confidence scores
            method: Aggregation method ('mean', 'min', 'geometric')

        Returns:
            Aggregated confidence score, or None if no confidences provided

        Example:
            >>> confidences = [0.9, 0.95, 0.85, 0.7]
            >>> mean_conf = service.aggregate_word_confidences(confidences, 'mean')
            >>> min_conf = service.aggregate_word_confidences(confidences, 'min')
            >>> geo_conf = service.aggregate_word_confidences(confidences, 'geometric')
        """
        if not word_confidences:
            return None

        if method == 'mean':
            return sum(word_confidences) / len(word_confidences)

        elif method == 'min':
            return min(word_confidences)

        elif method == 'geometric':
            # Geometric mean = (product of all values) ^ (1/n)
            # Use log sum to avoid overflow
            log_sum = sum(
                math.log(c) if c > 0 else float('-inf')
                for c in word_confidences
            )
            if log_sum == float('-inf'):
                return 0.0
            return math.exp(log_sum / len(word_confidences))

        else:
            raise ValueError(f"Unknown aggregation method: {method}")

    def get_calibration_metrics(
        self,
        predictions: List[Dict[str, Any]],
        num_bins: int = 10
    ) -> Dict[str, Any]:
        """
        Get comprehensive calibration metrics.

        Combines ECE, MCE, correlation, and other metrics into a single
        report for calibration analysis.

        Args:
            predictions: List of prediction dicts with 'confidence' and 'correct' keys
            num_bins: Number of bins for calculations

        Returns:
            Dictionary with:
                - ece: Expected Calibration Error
                - mce: Maximum Calibration Error
                - correlation: Confidence-accuracy correlation metrics
                - num_predictions: Total number of predictions
                - num_correct: Number of correct predictions
                - accuracy: Overall accuracy

        Example:
            >>> metrics = service.get_calibration_metrics(predictions)
            >>> print(f"ECE: {metrics['ece']:.4f}, MCE: {metrics['mce']:.4f}")
        """
        ece = self.calculate_ece(predictions, num_bins)
        mce = self.calculate_mce(predictions, num_bins)
        correlation = self.calculate_confidence_accuracy_correlation(predictions)

        num_correct = sum(
            1 for p in predictions if p.get('correct', False)
        )
        accuracy = num_correct / len(predictions) if predictions else 0.0

        return {
            'ece': ece,
            'mce': mce,
            'correlation': correlation,
            'num_predictions': len(predictions),
            'num_correct': num_correct,
            'accuracy': accuracy
        }
