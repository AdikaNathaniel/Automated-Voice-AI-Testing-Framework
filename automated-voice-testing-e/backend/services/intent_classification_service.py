"""
Intent Classification Service for NLU testing.

This service provides comprehensive metrics for evaluating intent
classification performance in voice AI and NLU systems.

Key metrics:
- Precision, Recall, F1 score per intent class
- Confusion matrix generation
- Top-N accuracy (top-1, top-3, top-5)
- Confidence threshold optimization

Example:
    >>> service = IntentClassificationService()
    >>> metrics = service.get_classification_metrics(true_labels, predictions)
    >>> print(f"Overall F1: {metrics['macro_f1']:.3f}")
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np


class IntentClassificationService:
    """
    Service for calculating intent classification metrics.

    Provides precision, recall, F1 scores, confusion matrices,
    top-N accuracy, and threshold optimization for intent classifiers.

    Example:
        >>> service = IntentClassificationService()
        >>> precision = service.calculate_precision(tp=80, fp=20)
        >>> print(f"Precision: {precision:.3f}")
    """

    def __init__(self):
        """Initialize the intent classification service."""
        pass

    def calculate_precision(
        self,
        tp: int,
        fp: int
    ) -> float:
        """
        Calculate precision from true positives and false positives.

        Precision = TP / (TP + FP)

        Args:
            tp: True positives count
            fp: False positives count

        Returns:
            Precision score (0.0 to 1.0)

        Example:
            >>> precision = service.calculate_precision(80, 20)
            >>> print(f"Precision: {precision:.3f}")
            0.800
        """
        if tp + fp == 0:
            return 0.0
        return float(tp / (tp + fp))

    def calculate_recall(
        self,
        tp: int,
        fn: int
    ) -> float:
        """
        Calculate recall from true positives and false negatives.

        Recall = TP / (TP + FN)

        Args:
            tp: True positives count
            fn: False negatives count

        Returns:
            Recall score (0.0 to 1.0)

        Example:
            >>> recall = service.calculate_recall(80, 10)
            >>> print(f"Recall: {recall:.3f}")
            0.889
        """
        if tp + fn == 0:
            return 0.0
        return float(tp / (tp + fn))

    def calculate_f1(
        self,
        precision: float,
        recall: float
    ) -> float:
        """
        Calculate F1 score from precision and recall.

        F1 = 2 * (precision * recall) / (precision + recall)

        Args:
            precision: Precision score
            recall: Recall score

        Returns:
            F1 score (0.0 to 1.0)

        Example:
            >>> f1 = service.calculate_f1(0.8, 0.9)
            >>> print(f"F1: {f1:.3f}")
            0.847
        """
        if precision + recall == 0:
            return 0.0
        return float(2 * (precision * recall) / (precision + recall))

    def generate_confusion_matrix(
        self,
        true_labels: List[str],
        predicted_labels: List[str],
        labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate confusion matrix from true and predicted labels.

        Args:
            true_labels: Ground truth labels
            predicted_labels: Predicted labels
            labels: Optional list of label names (auto-detected if None)

        Returns:
            Dictionary with confusion matrix and related metrics

        Example:
            >>> result = service.generate_confusion_matrix(
            ...     ['A', 'A', 'B', 'B'],
            ...     ['A', 'B', 'B', 'A']
            ... )
            >>> print(result['accuracy'])
        """
        if len(true_labels) != len(predicted_labels):
            raise ValueError("Label lists must have same length")

        # Get unique labels
        if labels is None:
            labels = sorted(set(true_labels) | set(predicted_labels))

        n_classes = len(labels)
        label_to_idx = {label: i for i, label in enumerate(labels)}

        # Build confusion matrix
        matrix = [[0] * n_classes for _ in range(n_classes)]

        for true, pred in zip(true_labels, predicted_labels):
            true_idx = label_to_idx.get(true, 0)
            pred_idx = label_to_idx.get(pred, 0)
            matrix[true_idx][pred_idx] += 1

        # Calculate accuracy
        correct = sum(matrix[i][i] for i in range(n_classes))
        total = len(true_labels)
        accuracy = correct / total if total > 0 else 0.0

        return {
            'matrix': matrix,
            'labels': labels,
            'accuracy': float(accuracy),
            'total_samples': total,
            'correct_predictions': correct
        }

    def calculate_top_n_accuracy(
        self,
        true_labels: List[str],
        predictions: List[List[Tuple[str, float]]],
        n_values: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Calculate top-N accuracy for intent classification.

        Args:
            true_labels: Ground truth labels
            predictions: List of (label, confidence) tuples for each sample,
                        sorted by confidence descending
            n_values: List of N values to calculate (default [1, 3, 5])

        Returns:
            Dictionary with top-N accuracy values

        Example:
            >>> result = service.calculate_top_n_accuracy(
            ...     ['A', 'B'],
            ...     [[('A', 0.8), ('B', 0.2)], [('A', 0.6), ('B', 0.4)]]
            ... )
            >>> print(f"Top-1: {result['top_1']:.3f}")
        """
        if n_values is None:
            n_values = [1, 3, 5]

        total = len(true_labels)
        if total == 0:
            return {f'top_{n}': 0.0 for n in n_values}

        results = {}
        for n in n_values:
            correct = 0
            for true_label, preds in zip(true_labels, predictions):
                # Get top-N predicted labels
                top_n_labels = [p[0] for p in preds[:n]]
                if true_label in top_n_labels:
                    correct += 1

            results[f'top_{n}'] = float(correct / total)

        results['total_samples'] = total
        return results

    def optimize_threshold(
        self,
        true_labels: List[str],
        predictions: List[Tuple[str, float]],
        metric: str = 'f1'
    ) -> Dict[str, Any]:
        """
        Optimize confidence threshold for intent classification.

        Args:
            true_labels: Ground truth labels
            predictions: List of (predicted_label, confidence) tuples
            metric: Metric to optimize ('f1', 'precision', 'recall')

        Returns:
            Dictionary with optimal threshold and metrics

        Example:
            >>> result = service.optimize_threshold(
            ...     ['A', 'A', 'B'],
            ...     [('A', 0.9), ('A', 0.6), ('B', 0.8)]
            ... )
            >>> print(f"Optimal threshold: {result['optimal_threshold']:.2f}")
        """
        # Test different thresholds
        thresholds = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        best_threshold = 0.5
        best_score = 0.0
        results_per_threshold = []

        for threshold in thresholds:
            # Apply threshold - predictions below threshold are rejected
            tp, fp, fn = 0, 0, 0

            for true_label, (pred_label, confidence) in zip(true_labels, predictions):
                if confidence >= threshold:
                    if pred_label == true_label:
                        tp += 1
                    else:
                        fp += 1
                else:
                    fn += 1

            precision = self.calculate_precision(tp, fp)
            recall = self.calculate_recall(tp, fn)
            f1 = self.calculate_f1(precision, recall)

            if metric == 'f1':
                score = f1
            elif metric == 'precision':
                score = precision
            else:
                score = recall

            results_per_threshold.append({
                'threshold': threshold,
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'score': score
            })

            if score > best_score:
                best_score = score
                best_threshold = threshold

        return {
            'optimal_threshold': best_threshold,
            'best_score': best_score,
            'metric': metric,
            'results_per_threshold': results_per_threshold
        }

    def calculate_per_class_metrics(
        self,
        true_labels: List[str],
        predicted_labels: List[str]
    ) -> Dict[str, Any]:
        """
        Calculate precision, recall, F1 for each intent class.

        Args:
            true_labels: Ground truth labels
            predicted_labels: Predicted labels

        Returns:
            Dictionary with per-class metrics

        Example:
            >>> result = service.calculate_per_class_metrics(
            ...     ['A', 'A', 'B', 'B'],
            ...     ['A', 'B', 'B', 'B']
            ... )
            >>> print(result['per_class']['A']['f1'])
        """
        # Get unique classes
        classes = sorted(set(true_labels) | set(predicted_labels))

        per_class = {}
        for cls in classes:
            tp = sum(1 for t, p in zip(true_labels, predicted_labels)
                    if t == cls and p == cls)
            fp = sum(1 for t, p in zip(true_labels, predicted_labels)
                    if t != cls and p == cls)
            fn = sum(1 for t, p in zip(true_labels, predicted_labels)
                    if t == cls and p != cls)

            precision = self.calculate_precision(tp, fp)
            recall = self.calculate_recall(tp, fn)
            f1 = self.calculate_f1(precision, recall)

            per_class[cls] = {
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'support': sum(1 for t in true_labels if t == cls),
                'tp': tp,
                'fp': fp,
                'fn': fn
            }

        return {
            'per_class': per_class,
            'classes': classes,
            'num_classes': len(classes)
        }

    def get_classification_metrics(
        self,
        true_labels: List[str],
        predicted_labels: List[str],
        predictions_with_confidence: Optional[List[Tuple[str, float]]] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive classification metrics.

        Args:
            true_labels: Ground truth labels
            predicted_labels: Predicted labels
            predictions_with_confidence: Optional (label, confidence) tuples

        Returns:
            Dictionary with all classification metrics

        Example:
            >>> metrics = service.get_classification_metrics(
            ...     ['A', 'A', 'B', 'B'],
            ...     ['A', 'B', 'B', 'A']
            ... )
            >>> print(f"Macro F1: {metrics['macro_f1']:.3f}")
        """
        # Get per-class metrics
        per_class_result = self.calculate_per_class_metrics(
            true_labels, predicted_labels
        )
        per_class = per_class_result['per_class']

        # Calculate macro averages
        precisions = [m['precision'] for m in per_class.values()]
        recalls = [m['recall'] for m in per_class.values()]
        f1s = [m['f1'] for m in per_class.values()]

        macro_precision = np.mean(precisions) if precisions else 0.0
        macro_recall = np.mean(recalls) if recalls else 0.0
        macro_f1 = np.mean(f1s) if f1s else 0.0

        # Calculate weighted averages
        supports = [m['support'] for m in per_class.values()]
        total_support = sum(supports)

        if total_support > 0:
            weighted_precision = sum(
                m['precision'] * m['support']
                for m in per_class.values()
            ) / total_support
            weighted_recall = sum(
                m['recall'] * m['support']
                for m in per_class.values()
            ) / total_support
            weighted_f1 = sum(
                m['f1'] * m['support']
                for m in per_class.values()
            ) / total_support
        else:
            weighted_precision = 0.0
            weighted_recall = 0.0
            weighted_f1 = 0.0

        # Generate confusion matrix
        confusion = self.generate_confusion_matrix(true_labels, predicted_labels)

        result = {
            'accuracy': confusion['accuracy'],
            'macro_precision': float(macro_precision),
            'macro_recall': float(macro_recall),
            'macro_f1': float(macro_f1),
            'weighted_precision': float(weighted_precision),
            'weighted_recall': float(weighted_recall),
            'weighted_f1': float(weighted_f1),
            'per_class_metrics': per_class,
            'confusion_matrix': confusion,
            'num_classes': len(per_class),
            'total_samples': len(true_labels)
        }

        # Add threshold optimization if confidence provided
        if predictions_with_confidence:
            threshold_result = self.optimize_threshold(
                true_labels, predictions_with_confidence
            )
            result['threshold_optimization'] = threshold_result

        return result

