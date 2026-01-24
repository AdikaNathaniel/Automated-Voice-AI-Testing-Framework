"""
Out-of-Scope (OOS) Detection Service for NLU testing.

This service provides metrics for evaluating how well an NLU system
handles out-of-scope utterances that don't match any defined intent.

Key metrics:
- FAR (False Acceptance Rate): OOS utterances incorrectly accepted
- FRR (False Rejection Rate): In-scope utterances incorrectly rejected
- OOS confidence calibration
- EER (Equal Error Rate): Point where FAR = FRR

Example:
    >>> service = OOSDetectionService()
    >>> metrics = service.get_oos_metrics(labels, predictions, confidences)
    >>> print(f"FAR: {metrics['far']:.3f}, FRR: {metrics['frr']:.3f}")
"""

from typing import List, Dict, Any, Tuple
import numpy as np


class OOSDetectionService:
    """
    Service for evaluating out-of-scope detection performance.

    Provides FAR, FRR, threshold optimization, and confidence
    calibration for OOS detection in NLU systems.

    Example:
        >>> service = OOSDetectionService()
        >>> far = service.calculate_far(oos_labels, predictions, 0.5)
        >>> print(f"FAR at 0.5 threshold: {far:.3f}")
    """

    # Label for out-of-scope
    OOS_LABEL = 'OOS'

    def __init__(self):
        """Initialize the OOS detection service."""
        pass

    def calculate_far(
        self,
        true_labels: List[str],
        predictions: List[Tuple[str, float]],
        threshold: float = 0.5
    ) -> float:
        """
        Calculate False Acceptance Rate for OOS utterances.

        FAR = OOS utterances accepted as in-scope / Total OOS utterances

        Args:
            true_labels: Ground truth labels (OOS for out-of-scope)
            predictions: List of (predicted_label, confidence) tuples
            threshold: Confidence threshold for acceptance

        Returns:
            False acceptance rate (0.0 to 1.0)

        Example:
            >>> far = service.calculate_far(
            ...     ['OOS', 'OOS', 'intent_a'],
            ...     [('intent_a', 0.8), ('OOS', 0.3), ('intent_a', 0.9)],
            ...     0.5
            ... )
        """
        oos_count = 0
        false_acceptances = 0

        for true_label, (pred_label, confidence) in zip(true_labels, predictions):
            if true_label == self.OOS_LABEL:
                oos_count += 1
                # False acceptance: OOS accepted as in-scope with high confidence
                if confidence >= threshold and pred_label != self.OOS_LABEL:
                    false_acceptances += 1

        if oos_count == 0:
            return 0.0

        return float(false_acceptances / oos_count)

    def calculate_frr(
        self,
        true_labels: List[str],
        predictions: List[Tuple[str, float]],
        threshold: float = 0.5
    ) -> float:
        """
        Calculate False Rejection Rate for in-scope utterances.

        FRR = In-scope utterances rejected as OOS / Total in-scope utterances

        Args:
            true_labels: Ground truth labels
            predictions: List of (predicted_label, confidence) tuples
            threshold: Confidence threshold for acceptance

        Returns:
            False rejection rate (0.0 to 1.0)

        Example:
            >>> frr = service.calculate_frr(
            ...     ['intent_a', 'intent_b', 'OOS'],
            ...     [('OOS', 0.3), ('intent_b', 0.9), ('OOS', 0.8)],
            ...     0.5
            ... )
        """
        in_scope_count = 0
        false_rejections = 0

        for true_label, (pred_label, confidence) in zip(true_labels, predictions):
            if true_label != self.OOS_LABEL:
                in_scope_count += 1
                # False rejection: In-scope rejected (low confidence or predicted OOS)
                if confidence < threshold or pred_label == self.OOS_LABEL:
                    false_rejections += 1

        if in_scope_count == 0:
            return 0.0

        return float(false_rejections / in_scope_count)

    def calibrate_oos_confidence(
        self,
        true_labels: List[str],
        predictions: List[Tuple[str, float]]
    ) -> Dict[str, Any]:
        """
        Calibrate OOS confidence scores.

        Analyzes the distribution of confidence scores for OOS vs in-scope
        utterances to determine optimal thresholds.

        Args:
            true_labels: Ground truth labels
            predictions: List of (predicted_label, confidence) tuples

        Returns:
            Dictionary with calibration metrics

        Example:
            >>> result = service.calibrate_oos_confidence(labels, predictions)
            >>> print(f"OOS mean confidence: {result['oos_mean_confidence']}")
        """
        oos_confidences = []
        in_scope_confidences = []

        for true_label, (pred_label, confidence) in zip(true_labels, predictions):
            if true_label == self.OOS_LABEL:
                oos_confidences.append(confidence)
            else:
                in_scope_confidences.append(confidence)

        # Calculate statistics
        oos_mean = np.mean(oos_confidences) if oos_confidences else 0.0
        oos_std = np.std(oos_confidences) if oos_confidences else 0.0
        in_scope_mean = np.mean(in_scope_confidences) if in_scope_confidences else 0.0
        in_scope_std = np.std(in_scope_confidences) if in_scope_confidences else 0.0

        # Determine separability
        if oos_confidences and in_scope_confidences:
            # Calculate overlap
            separation = in_scope_mean - oos_mean
            combined_std = (oos_std + in_scope_std) / 2
            separability = separation / combined_std if combined_std > 0 else 0.0
        else:
            separability = 0.0

        # Recommend threshold
        if oos_confidences and in_scope_confidences:
            recommended_threshold = (oos_mean + in_scope_mean) / 2
        else:
            recommended_threshold = 0.5

        return {
            'oos_mean_confidence': float(oos_mean),
            'oos_std_confidence': float(oos_std),
            'in_scope_mean_confidence': float(in_scope_mean),
            'in_scope_std_confidence': float(in_scope_std),
            'separability': float(separability),
            'recommended_threshold': float(recommended_threshold),
            'oos_count': len(oos_confidences),
            'in_scope_count': len(in_scope_confidences),
            'calibration_quality': (
                'excellent' if separability > 2.0
                else 'good' if separability > 1.0
                else 'fair' if separability > 0.5
                else 'poor'
            )
        }

    def optimize_oos_threshold(
        self,
        true_labels: List[str],
        predictions: List[Tuple[str, float]],
        target_far: float = None,
        target_frr: float = None
    ) -> Dict[str, Any]:
        """
        Optimize OOS detection threshold.

        Finds optimal threshold to minimize error or match target FAR/FRR.

        Args:
            true_labels: Ground truth labels
            predictions: List of (predicted_label, confidence) tuples
            target_far: Target false acceptance rate (optional)
            target_frr: Target false rejection rate (optional)

        Returns:
            Dictionary with optimal threshold and metrics

        Example:
            >>> result = service.optimize_oos_threshold(labels, predictions)
            >>> print(f"Optimal threshold: {result['optimal_threshold']}")
        """
        thresholds = [i / 100 for i in range(5, 100, 5)]
        results = []

        for threshold in thresholds:
            far = self.calculate_far(true_labels, predictions, threshold)
            frr = self.calculate_frr(true_labels, predictions, threshold)

            results.append({
                'threshold': threshold,
                'far': far,
                'frr': frr,
                'total_error': far + frr,
                'eer_diff': abs(far - frr)
            })

        # Find optimal based on criteria
        if target_far is not None:
            # Find threshold closest to target FAR
            optimal = min(results, key=lambda x: abs(x['far'] - target_far))
        elif target_frr is not None:
            # Find threshold closest to target FRR
            optimal = min(results, key=lambda x: abs(x['frr'] - target_frr))
        else:
            # Find EER (where FAR ≈ FRR)
            optimal = min(results, key=lambda x: x['eer_diff'])

        # Find EER
        eer_result = min(results, key=lambda x: x['eer_diff'])
        eer = (eer_result['far'] + eer_result['frr']) / 2

        return {
            'optimal_threshold': optimal['threshold'],
            'far_at_optimal': optimal['far'],
            'frr_at_optimal': optimal['frr'],
            'eer': float(eer),
            'eer_threshold': eer_result['threshold'],
            'results_per_threshold': results
        }

    def get_oos_metrics(
        self,
        true_labels: List[str],
        predictions: List[Tuple[str, float]],
        threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        Get comprehensive OOS detection metrics.

        Args:
            true_labels: Ground truth labels
            predictions: List of (predicted_label, confidence) tuples
            threshold: Confidence threshold for metrics

        Returns:
            Dictionary with all OOS metrics

        Example:
            >>> metrics = service.get_oos_metrics(labels, predictions)
            >>> print(f"FAR: {metrics['far']:.3f}, FRR: {metrics['frr']:.3f}")
        """
        far = self.calculate_far(true_labels, predictions, threshold)
        frr = self.calculate_frr(true_labels, predictions, threshold)
        calibration = self.calibrate_oos_confidence(true_labels, predictions)
        optimization = self.optimize_oos_threshold(true_labels, predictions)

        # Count samples
        oos_count = sum(1 for item in true_labels if item == self.OOS_LABEL)
        in_scope_count = len(true_labels) - oos_count

        # Calculate accuracy
        correct = sum(
            1 for true, (pred, conf) in zip(true_labels, predictions)
            if (conf >= threshold and pred == true) or
               (conf < threshold and true == self.OOS_LABEL)
        )
        accuracy = correct / len(true_labels) if true_labels else 0.0

        return {
            'threshold': threshold,
            'far': far,
            'frr': frr,
            'total_error_rate': far + frr,
            'accuracy': float(accuracy),
            'oos_count': oos_count,
            'in_scope_count': in_scope_count,
            'calibration': calibration,
            'threshold_optimization': optimization,
            'eer': optimization['eer'],
            'recommended_threshold': optimization['optimal_threshold']
        }

