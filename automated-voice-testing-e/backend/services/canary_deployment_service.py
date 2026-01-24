"""
Canary Deployment Service for voice AI testing.

This service provides canary deployment capabilities including
percentage traffic routing, metrics comparison, and auto rollback.

Key features:
- Percentage traffic routing
- Canary metrics comparison
- Automatic rollback triggers

Example:
    >>> service = CanaryDeploymentService()
    >>> result = service.set_traffic_percentage(10)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class CanaryDeploymentService:
    """
    Service for canary deployment management.

    Provides traffic routing, metrics comparison,
    and automatic rollback capabilities.

    Example:
        >>> service = CanaryDeploymentService()
        >>> config = service.get_canary_config()
    """

    def __init__(self):
        """Initialize the canary deployment service."""
        self._canary_percentage: int = 0
        self._triggers: Dict[str, Dict[str, Any]] = {}
        self._metrics: List[Dict[str, Any]] = []
        self._rollback_history: List[Dict[str, Any]] = []

    def set_traffic_percentage(
        self,
        percentage: int,
        canary_version: str = 'canary'
    ) -> Dict[str, Any]:
        """
        Set canary traffic percentage.

        Args:
            percentage: Traffic percentage (0-100)
            canary_version: Canary version identifier

        Returns:
            Dictionary with configuration result

        Example:
            >>> result = service.set_traffic_percentage(10)
        """
        config_id = str(uuid.uuid4())

        if percentage < 0 or percentage > 100:
            return {
                'config_id': config_id,
                'success': False,
                'error': f'Invalid percentage: {percentage}',
                'configured_at': datetime.utcnow().isoformat()
            }

        previous = self._canary_percentage
        self._canary_percentage = percentage

        return {
            'config_id': config_id,
            'canary_version': canary_version,
            'previous_percentage': previous,
            'new_percentage': percentage,
            'stable_percentage': 100 - percentage,
            'success': True,
            'configured_at': datetime.utcnow().isoformat()
        }

    def get_traffic_distribution(self) -> Dict[str, Any]:
        """
        Get current traffic distribution.

        Returns:
            Dictionary with distribution details

        Example:
            >>> result = service.get_traffic_distribution()
        """
        return {
            'canary_percentage': self._canary_percentage,
            'stable_percentage': 100 - self._canary_percentage,
            'total': 100,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def gradual_rollout(
        self,
        start_percentage: int,
        end_percentage: int,
        steps: int = 5
    ) -> Dict[str, Any]:
        """
        Plan gradual traffic rollout.

        Args:
            start_percentage: Starting percentage
            end_percentage: Target percentage
            steps: Number of steps

        Returns:
            Dictionary with rollout plan

        Example:
            >>> result = service.gradual_rollout(0, 100, 5)
        """
        rollout_id = str(uuid.uuid4())

        step_size = (end_percentage - start_percentage) / steps
        stages = [
            {
                'stage': i + 1,
                'percentage': int(start_percentage + step_size * (i + 1))
            }
            for i in range(steps)
        ]

        return {
            'rollout_id': rollout_id,
            'start_percentage': start_percentage,
            'end_percentage': end_percentage,
            'steps': steps,
            'stages': stages,
            'created_at': datetime.utcnow().isoformat()
        }

    def compare_metrics(
        self,
        canary_metrics: Dict[str, float],
        stable_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Compare canary vs stable metrics.

        Args:
            canary_metrics: Canary version metrics
            stable_metrics: Stable version metrics

        Returns:
            Dictionary with comparison result

        Example:
            >>> result = service.compare_metrics(canary, stable)
        """
        comparison_id = str(uuid.uuid4())

        comparisons = {}
        for metric in canary_metrics:
            if metric in stable_metrics:
                canary_val = canary_metrics[metric]
                stable_val = stable_metrics[metric]
                diff = canary_val - stable_val
                pct_diff = (
                    (diff / stable_val * 100) if stable_val != 0 else 0
                )

                comparisons[metric] = {
                    'canary': canary_val,
                    'stable': stable_val,
                    'diff': diff,
                    'pct_diff': pct_diff,
                    'status': (
                        'degraded' if pct_diff < -10
                        else 'improved' if pct_diff > 10
                        else 'similar'
                    )
                }

        return {
            'comparison_id': comparison_id,
            'comparisons': comparisons,
            'metrics_compared': len(comparisons),
            'compared_at': datetime.utcnow().isoformat()
        }

    def get_canary_metrics(
        self,
        metric_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get canary metrics.

        Args:
            metric_types: Specific metric types

        Returns:
            Dictionary with metrics

        Example:
            >>> result = service.get_canary_metrics()
        """
        metrics = self._metrics

        if metric_types:
            metrics = [
                m for m in metrics
                if m.get('type') in metric_types
            ]

        return {
            'metrics': metrics,
            'count': len(metrics),
            'canary_percentage': self._canary_percentage,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def analyze_performance(
        self,
        canary_data: List[Dict[str, Any]],
        baseline_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze canary performance.

        Args:
            canary_data: Canary performance data
            baseline_data: Baseline performance data

        Returns:
            Dictionary with analysis result

        Example:
            >>> result = service.analyze_performance(canary, baseline)
        """
        analysis_id = str(uuid.uuid4())

        # Aggregate metrics
        canary_avg = {}
        baseline_avg = {}

        for item in canary_data:
            for k, v in item.items():
                if isinstance(v, (int, float)):
                    canary_avg[k] = canary_avg.get(k, 0) + v

        for item in baseline_data:
            for k, v in item.items():
                if isinstance(v, (int, float)):
                    baseline_avg[k] = baseline_avg.get(k, 0) + v

        # Calculate averages
        if canary_data:
            canary_avg = {k: v / len(canary_data) for k, v in canary_avg.items()}
        if baseline_data:
            baseline_avg = {k: v / len(baseline_data) for k, v in baseline_avg.items()}

        return {
            'analysis_id': analysis_id,
            'canary_summary': canary_avg,
            'baseline_summary': baseline_avg,
            'canary_samples': len(canary_data),
            'baseline_samples': len(baseline_data),
            'analyzed_at': datetime.utcnow().isoformat()
        }

    def set_rollback_triggers(
        self,
        trigger_id: str,
        conditions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Set automatic rollback triggers.

        Args:
            trigger_id: Trigger identifier
            conditions: Trigger conditions

        Returns:
            Dictionary with trigger configuration

        Example:
            >>> result = service.set_rollback_triggers('t1', conditions)
        """
        self._triggers[trigger_id] = {
            'id': trigger_id,
            'conditions': conditions,
            'created_at': datetime.utcnow().isoformat()
        }

        return {
            'trigger_id': trigger_id,
            'conditions': conditions,
            'status': 'active',
            'created_at': datetime.utcnow().isoformat()
        }

    def check_triggers(
        self,
        current_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Check if rollback triggers are met.

        Args:
            current_metrics: Current metrics

        Returns:
            Dictionary with trigger check result

        Example:
            >>> result = service.check_triggers(metrics)
        """
        check_id = str(uuid.uuid4())

        triggered = []
        for trigger_id, trigger in self._triggers.items():
            conditions = trigger['conditions']
            for metric, threshold in conditions.items():
                if metric in current_metrics:
                    if current_metrics[metric] > threshold:
                        triggered.append({
                            'trigger_id': trigger_id,
                            'metric': metric,
                            'value': current_metrics[metric],
                            'threshold': threshold
                        })

        return {
            'check_id': check_id,
            'triggered': triggered,
            'should_rollback': len(triggered) > 0,
            'checked_at': datetime.utcnow().isoformat()
        }

    def auto_rollback(
        self,
        reason: str,
        triggered_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform automatic rollback.

        Args:
            reason: Rollback reason
            triggered_by: Trigger identifier

        Returns:
            Dictionary with rollback result

        Example:
            >>> result = service.auto_rollback('Error threshold exceeded')
        """
        rollback_id = str(uuid.uuid4())

        previous_percentage = self._canary_percentage
        self._canary_percentage = 0

        record = {
            'rollback_id': rollback_id,
            'reason': reason,
            'triggered_by': triggered_by,
            'previous_percentage': previous_percentage,
            'status': 'completed',
            'rolled_back_at': datetime.utcnow().isoformat()
        }

        self._rollback_history.append(record)

        return record

    def get_canary_config(self) -> Dict[str, Any]:
        """
        Get canary configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_canary_config()
        """
        return {
            'canary_percentage': self._canary_percentage,
            'total_triggers': len(self._triggers),
            'total_rollbacks': len(self._rollback_history),
            'features': [
                'traffic_routing', 'metrics_comparison',
                'auto_rollback', 'gradual_rollout'
            ]
        }
