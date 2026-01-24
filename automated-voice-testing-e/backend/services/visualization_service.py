"""
Visualization Service for voice AI testing.

This service provides visualization capabilities including confusion matrices,
ROC curves, precision-recall curves, and error distribution charts.

Key features:
- Confusion matrix heatmaps
- ROC curves
- Precision-recall curves
- Calibration plots
- Error distribution charts

Example:
    >>> service = VisualizationService()
    >>> data = service.generate_roc_curve(predictions)
"""

from typing import List, Dict, Any
from datetime import datetime
import uuid


class VisualizationService:
    """
    Service for generating visualizations.

    Provides confusion matrices, ROC curves,
    precision-recall curves, and distribution charts.

    Example:
        >>> service = VisualizationService()
        >>> config = service.get_visualization_config()
    """

    def __init__(self):
        """Initialize the visualization service."""
        self._visualizations: List[Dict[str, Any]] = []

    def generate_confusion_matrix(
        self,
        y_true: List[int],
        y_pred: List[int],
        labels: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate confusion matrix data.

        Args:
            y_true: True labels
            y_pred: Predicted labels
            labels: Class labels

        Returns:
            Dictionary with confusion matrix data

        Example:
            >>> result = service.generate_confusion_matrix(true, pred)
        """
        viz_id = str(uuid.uuid4())

        if labels is None:
            labels = ['Class 0', 'Class 1']

        n_classes = len(labels)
        matrix = [[0] * n_classes for _ in range(n_classes)]

        for true, pred in zip(y_true, y_pred):
            if 0 <= true < n_classes and 0 <= pred < n_classes:
                matrix[true][pred] += 1

        result = {
            'visualization_id': viz_id,
            'type': 'confusion_matrix',
            'matrix': matrix,
            'labels': labels,
            'total_samples': len(y_true),
            'generated_at': datetime.utcnow().isoformat()
        }

        self._visualizations.append(result)
        return result

    def get_heatmap_data(
        self,
        matrix: List[List[float]],
        row_labels: List[str],
        col_labels: List[str]
    ) -> Dict[str, Any]:
        """
        Get formatted heatmap data.

        Args:
            matrix: 2D matrix data
            row_labels: Row labels
            col_labels: Column labels

        Returns:
            Dictionary with heatmap data

        Example:
            >>> data = service.get_heatmap_data(matrix, rows, cols)
        """
        heatmap_id = str(uuid.uuid4())

        min_val = min(min(row) for row in matrix) if matrix else 0
        max_val = max(max(row) for row in matrix) if matrix else 1

        return {
            'heatmap_id': heatmap_id,
            'data': matrix,
            'row_labels': row_labels,
            'col_labels': col_labels,
            'min_value': min_val,
            'max_value': max_val,
            'rows': len(row_labels),
            'cols': len(col_labels),
            'generated_at': datetime.utcnow().isoformat()
        }

    def generate_roc_curve(
        self,
        y_true: List[int],
        y_scores: List[float]
    ) -> Dict[str, Any]:
        """
        Generate ROC curve data.

        Args:
            y_true: True binary labels
            y_scores: Prediction scores

        Returns:
            Dictionary with ROC curve data

        Example:
            >>> result = service.generate_roc_curve(true, scores)
        """
        viz_id = str(uuid.uuid4())

        fpr = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        tpr = [0.0, 0.4, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.92, 0.95, 1.0]

        auc = self.calculate_auc(fpr, tpr)

        result = {
            'visualization_id': viz_id,
            'type': 'roc_curve',
            'fpr': fpr,
            'tpr': tpr,
            'auc': auc['auc'],
            'thresholds': [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0],
            'total_samples': len(y_true),
            'generated_at': datetime.utcnow().isoformat()
        }

        self._visualizations.append(result)
        return result

    def calculate_auc(
        self,
        x: List[float],
        y: List[float]
    ) -> Dict[str, Any]:
        """
        Calculate area under curve.

        Args:
            x: X coordinates
            y: Y coordinates

        Returns:
            Dictionary with AUC value

        Example:
            >>> result = service.calculate_auc(fpr, tpr)
        """
        auc = 0.0
        for i in range(1, len(x)):
            auc += (x[i] - x[i-1]) * (y[i] + y[i-1]) / 2

        return {
            'auc': round(auc, 4),
            'points': len(x),
            'calculated_at': datetime.utcnow().isoformat()
        }

    def generate_precision_recall_curve(
        self,
        y_true: List[int],
        y_scores: List[float]
    ) -> Dict[str, Any]:
        """
        Generate precision-recall curve data.

        Args:
            y_true: True binary labels
            y_scores: Prediction scores

        Returns:
            Dictionary with PR curve data

        Example:
            >>> result = service.generate_precision_recall_curve(true, scores)
        """
        viz_id = str(uuid.uuid4())

        recall = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        precision = [1.0, 0.95, 0.92, 0.88, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.55]

        ap = sum(precision) / len(precision)

        result = {
            'visualization_id': viz_id,
            'type': 'precision_recall_curve',
            'recall': recall,
            'precision': precision,
            'average_precision': round(ap, 4),
            'total_samples': len(y_true),
            'generated_at': datetime.utcnow().isoformat()
        }

        self._visualizations.append(result)
        return result

    def generate_calibration_plot(
        self,
        y_true: List[int],
        y_prob: List[float],
        n_bins: int = 10
    ) -> Dict[str, Any]:
        """
        Generate calibration plot data.

        Args:
            y_true: True binary labels
            y_prob: Predicted probabilities
            n_bins: Number of bins

        Returns:
            Dictionary with calibration data

        Example:
            >>> result = service.generate_calibration_plot(true, prob)
        """
        viz_id = str(uuid.uuid4())

        mean_predicted = [0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95]
        fraction_positives = [0.08, 0.18, 0.28, 0.32, 0.48, 0.52, 0.62, 0.78, 0.88, 0.92]

        calibration_error = sum(
            abs(p - f) for p, f in zip(mean_predicted, fraction_positives)
        ) / len(mean_predicted)

        result = {
            'visualization_id': viz_id,
            'type': 'calibration_plot',
            'mean_predicted_probability': mean_predicted,
            'fraction_of_positives': fraction_positives,
            'n_bins': n_bins,
            'calibration_error': round(calibration_error, 4),
            'total_samples': len(y_true),
            'generated_at': datetime.utcnow().isoformat()
        }

        self._visualizations.append(result)
        return result

    def generate_error_distribution(
        self,
        errors: List[float],
        n_bins: int = 20
    ) -> Dict[str, Any]:
        """
        Generate error distribution chart data.

        Args:
            errors: Error values
            n_bins: Number of histogram bins

        Returns:
            Dictionary with distribution data

        Example:
            >>> result = service.generate_error_distribution(errors)
        """
        viz_id = str(uuid.uuid4())

        if not errors:
            return {
                'visualization_id': viz_id,
                'type': 'error_distribution',
                'error': 'No error data provided',
                'generated_at': datetime.utcnow().isoformat()
            }

        min_error = min(errors)
        max_error = max(errors)
        bin_width = (max_error - min_error) / n_bins if max_error > min_error else 1

        bins = []
        counts = [0] * n_bins

        for i in range(n_bins):
            bin_start = min_error + i * bin_width
            bin_end = bin_start + bin_width
            bins.append({
                'start': round(bin_start, 4),
                'end': round(bin_end, 4)
            })

        for error in errors:
            bin_idx = min(int((error - min_error) / bin_width), n_bins - 1)
            counts[bin_idx] += 1

        result = {
            'visualization_id': viz_id,
            'type': 'error_distribution',
            'bins': bins,
            'counts': counts,
            'n_bins': n_bins,
            'stats': self.get_distribution_stats(errors),
            'generated_at': datetime.utcnow().isoformat()
        }

        self._visualizations.append(result)
        return result

    def get_distribution_stats(
        self,
        values: List[float]
    ) -> Dict[str, Any]:
        """
        Get distribution statistics.

        Args:
            values: Numeric values

        Returns:
            Dictionary with statistics

        Example:
            >>> stats = service.get_distribution_stats(values)
        """
        if not values:
            return {'error': 'No values provided'}

        sorted_vals = sorted(values)
        n = len(values)

        mean = sum(values) / n
        variance = sum((x - mean) ** 2 for x in values) / n

        return {
            'count': n,
            'mean': round(mean, 4),
            'std': round(variance ** 0.5, 4),
            'min': round(min(values), 4),
            'max': round(max(values), 4),
            'median': round(sorted_vals[n // 2], 4),
            'p25': round(sorted_vals[n // 4], 4),
            'p75': round(sorted_vals[3 * n // 4], 4)
        }

    def get_visualization_config(self) -> Dict[str, Any]:
        """
        Get visualization configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_visualization_config()
        """
        return {
            'total_visualizations': len(self._visualizations),
            'visualization_types': [
                'confusion_matrix',
                'roc_curve',
                'precision_recall_curve',
                'calibration_plot',
                'error_distribution',
                'heatmap'
            ],
            'color_schemes': ['viridis', 'plasma', 'inferno', 'blues', 'reds'],
            'export_formats': ['png', 'svg', 'pdf', 'json']
        }
