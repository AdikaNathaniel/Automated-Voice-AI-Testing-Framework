"""
Degradation Alert Service for voice AI testing.

This service manages alerts for performance degradation including
automatic alerts, threshold triggers, and trend-based early warnings.

Key features:
- Automatic alerts on performance drops
- Threshold-based triggers
- Trend-based early warning

Example:
    >>> service = DegradationAlertService()
    >>> result = service.check_performance_drop(metrics)
"""

from typing import List, Dict, Any
from datetime import datetime
import uuid


class DegradationAlertService:
    """
    Service for degradation alerting.

    Provides performance drop detection, threshold evaluation,
    and early warning system.

    Example:
        >>> service = DegradationAlertService()
        >>> config = service.get_alert_config()
    """

    def __init__(self):
        """Initialize the degradation alert service."""
        self._alerts: List[Dict[str, Any]] = []
        self._thresholds: Dict[str, float] = {
            'accuracy': 0.85,
            'latency': 500,
            'error_rate': 0.1
        }

    def check_performance_drop(
        self,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check for performance drops in metrics.

        Args:
            metrics: Current performance metrics

        Returns:
            Dictionary with check result

        Example:
            >>> result = service.check_performance_drop(metrics)
        """
        check_id = str(uuid.uuid4())

        drops_detected = []

        accuracy = metrics.get('accuracy', 1.0)
        if accuracy < self._thresholds['accuracy']:
            drops_detected.append({
                'metric': 'accuracy',
                'current': accuracy,
                'threshold': self._thresholds['accuracy'],
                'severity': 'high' if accuracy < 0.7 else 'medium'
            })

        latency = metrics.get('latency', 0)
        if latency > self._thresholds['latency']:
            drops_detected.append({
                'metric': 'latency',
                'current': latency,
                'threshold': self._thresholds['latency'],
                'severity': 'high' if latency > 1000 else 'medium'
            })

        error_rate = metrics.get('error_rate', 0)
        if error_rate > self._thresholds['error_rate']:
            drops_detected.append({
                'metric': 'error_rate',
                'current': error_rate,
                'threshold': self._thresholds['error_rate'],
                'severity': 'high' if error_rate > 0.2 else 'medium'
            })

        return {
            'check_id': check_id,
            'drops_detected': len(drops_detected) > 0,
            'drops': drops_detected,
            'metrics_checked': list(metrics.keys()),
            'checked_at': datetime.utcnow().isoformat()
        }

    def send_alert(
        self,
        alert_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send a degradation alert.

        Args:
            alert_data: Alert details

        Returns:
            Dictionary with send result

        Example:
            >>> result = service.send_alert(alert_data)
        """
        alert_id = str(uuid.uuid4())

        alert = {
            'alert_id': alert_id,
            'type': alert_data.get('type', 'performance_drop'),
            'severity': alert_data.get('severity', 'medium'),
            'message': alert_data.get('message', 'Performance degradation detected'),
            'metrics': alert_data.get('metrics', {}),
            'sent_at': datetime.utcnow().isoformat(),
            'status': 'sent'
        }

        self._alerts.append(alert)

        return {
            'alert_id': alert_id,
            'status': 'sent',
            'channels': ['email', 'slack'],
            'sent_at': alert['sent_at']
        }

    def get_alert_history(
        self,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get alert history.

        Args:
            limit: Maximum alerts to return

        Returns:
            Dictionary with history

        Example:
            >>> history = service.get_alert_history(50)
        """
        history = self._alerts[-limit:] if limit else self._alerts

        return {
            'total_alerts': len(self._alerts),
            'returned_alerts': len(history),
            'alerts': history,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def set_threshold(
        self,
        metric: str,
        value: float
    ) -> Dict[str, Any]:
        """
        Set threshold for a metric.

        Args:
            metric: Metric name
            value: Threshold value

        Returns:
            Dictionary with result

        Example:
            >>> result = service.set_threshold('accuracy', 0.9)
        """
        old_value = self._thresholds.get(metric)
        self._thresholds[metric] = value

        return {
            'metric': metric,
            'old_value': old_value,
            'new_value': value,
            'updated_at': datetime.utcnow().isoformat()
        }

    def get_thresholds(self) -> Dict[str, Any]:
        """
        Get all configured thresholds.

        Returns:
            Dictionary with thresholds

        Example:
            >>> thresholds = service.get_thresholds()
        """
        return {
            'thresholds': self._thresholds.copy(),
            'count': len(self._thresholds),
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def evaluate_thresholds(
        self,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate metrics against thresholds.

        Args:
            metrics: Metrics to evaluate

        Returns:
            Dictionary with evaluation result

        Example:
            >>> result = service.evaluate_thresholds(metrics)
        """
        evaluation_id = str(uuid.uuid4())

        results = []
        violations = 0

        for metric, value in metrics.items():
            if metric in self._thresholds:
                threshold = self._thresholds[metric]
                if metric == 'latency':
                    violated = value > threshold
                else:
                    violated = value < threshold if metric == 'accuracy' else value > threshold

                if violated:
                    violations += 1

                results.append({
                    'metric': metric,
                    'value': value,
                    'threshold': threshold,
                    'violated': violated
                })

        return {
            'evaluation_id': evaluation_id,
            'results': results,
            'violations': violations,
            'all_passed': violations == 0,
            'evaluated_at': datetime.utcnow().isoformat()
        }

    def analyze_trend(
        self,
        metric_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze metric trend over time.

        Args:
            metric_history: Historical metric values

        Returns:
            Dictionary with trend analysis

        Example:
            >>> result = service.analyze_trend(history)
        """
        analysis_id = str(uuid.uuid4())

        if len(metric_history) < 2:
            trend = 'insufficient_data'
            slope = 0
        else:
            values = [h.get('value', 0) for h in metric_history]
            slope = (values[-1] - values[0]) / len(values)

            if abs(slope) < 0.01:
                trend = 'stable'
            elif slope > 0:
                trend = 'increasing'
            else:
                trend = 'decreasing'

        return {
            'analysis_id': analysis_id,
            'trend': trend,
            'slope': round(slope, 4),
            'data_points': len(metric_history),
            'analyzed_at': datetime.utcnow().isoformat()
        }

    def generate_early_warning(
        self,
        metrics: Dict[str, Any],
        trends: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Generate early warning based on trends.

        Args:
            metrics: Current metrics
            trends: Trend analysis results

        Returns:
            Dictionary with early warning

        Example:
            >>> result = service.generate_early_warning(metrics, trends)
        """
        warning_id = str(uuid.uuid4())

        warnings = []

        for metric, trend in trends.items():
            if trend == 'decreasing' and metric in ['accuracy']:
                warnings.append({
                    'metric': metric,
                    'warning': 'Performance declining',
                    'severity': 'warning',
                    'action': 'Monitor closely'
                })
            elif trend == 'increasing' and metric in ['latency', 'error_rate']:
                warnings.append({
                    'metric': metric,
                    'warning': 'Metric increasing',
                    'severity': 'warning',
                    'action': 'Investigate cause'
                })

        return {
            'warning_id': warning_id,
            'warnings_generated': len(warnings),
            'warnings': warnings,
            'generated_at': datetime.utcnow().isoformat()
        }

    def get_alert_config(self) -> Dict[str, Any]:
        """
        Get alert configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_alert_config()
        """
        return {
            'total_alerts': len(self._alerts),
            'thresholds': self._thresholds,
            'channels': ['email', 'slack', 'pagerduty'],
            'severity_levels': ['low', 'medium', 'high', 'critical']
        }
