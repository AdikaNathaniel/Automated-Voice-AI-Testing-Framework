"""
SLA Compliance Tracking Service for performance monitoring.

This service provides SLA definition, monitoring, and compliance
reporting for voice AI system testing.

Key features:
- SLA definition and configuration
- Compliance monitoring
- Violation detection
- Compliance reporting

Example:
    >>> service = SLAComplianceService()
    >>> sla = service.define_sla('response_time', target=500, unit='ms')
    >>> service.record_metric('response_time', 450)
    >>> status = service.get_compliance_status()
"""

from typing import List, Dict, Any
from datetime import datetime
import uuid

# Import targets mixin
from services.sla_compliance_targets import SLAComplianceTargetsMixin


class SLAComplianceService(SLAComplianceTargetsMixin):
    """
    Service for SLA compliance tracking and reporting.

    Provides SLA definition, compliance monitoring, violation
    detection, and comprehensive reporting.

    This class inherits from:
    - SLAComplianceTargetsMixin: Targets, alerts, and budget methods

    Example:
        >>> service = SLAComplianceService()
        >>> service.define_sla('uptime', target=99.9, unit='percent')
        >>> rate = service.calculate_compliance_rate()
        >>> print(f"Compliance: {rate:.1f}%")
    """

    def __init__(self):
        """Initialize the SLA compliance service."""
        self._slas: Dict[str, Dict[str, Any]] = {}
        self._metrics: Dict[str, List[Dict[str, Any]]] = {}
        self._violations: List[Dict[str, Any]] = []
        self._alerts: List[Dict[str, Any]] = []
        self._error_budgets: Dict[str, Dict[str, Any]] = {}
        self._compliance_history: List[Dict[str, Any]] = []

    def define_sla(
        self,
        metric_name: str,
        target: float,
        unit: str = "",
        comparison: str = "lte"
    ) -> Dict[str, Any]:
        """
        Define an SLA for a metric.

        Args:
            metric_name: Name of the metric
            target: Target value for the SLA
            unit: Unit of measurement
            comparison: Comparison type (lte, gte, eq)

        Returns:
            Dictionary with SLA definition

        Example:
            >>> sla = service.define_sla('latency', 200, 'ms', 'lte')
        """
        sla_id = str(uuid.uuid4())
        sla = {
            'id': sla_id,
            'metric_name': metric_name,
            'target': target,
            'unit': unit,
            'comparison': comparison,
            'created_at': datetime.utcnow().isoformat()
        }
        self._slas[metric_name] = sla
        self._metrics[metric_name] = []
        return sla

    def update_sla(
        self,
        metric_name: str,
        target: float = None,
        comparison: str = None
    ) -> Dict[str, Any]:
        """
        Update an existing SLA.

        Args:
            metric_name: Name of the metric
            target: New target value
            comparison: New comparison type

        Returns:
            Dictionary with updated SLA

        Example:
            >>> updated = service.update_sla('latency', target=150)
        """
        if metric_name not in self._slas:
            return {'error': 'SLA not found'}

        if target is not None:
            self._slas[metric_name]['target'] = target
        if comparison is not None:
            self._slas[metric_name]['comparison'] = comparison

        self._slas[metric_name]['updated_at'] = datetime.utcnow().isoformat()
        return self._slas[metric_name]

    def get_sla(self, metric_name: str) -> Dict[str, Any]:
        """
        Get an SLA by metric name.

        Args:
            metric_name: Name of the metric

        Returns:
            Dictionary with SLA details

        Example:
            >>> sla = service.get_sla('latency')
        """
        return self._slas.get(metric_name, {'error': 'SLA not found'})

    def record_metric(
        self,
        metric_name: str,
        value: float,
        timestamp: str = None
    ) -> None:
        """
        Record a metric value.

        Args:
            metric_name: Name of the metric
            value: Metric value
            timestamp: Optional timestamp

        Example:
            >>> service.record_metric('latency', 185)
        """
        if metric_name not in self._metrics:
            self._metrics[metric_name] = []

        record = {
            'value': value,
            'timestamp': timestamp or datetime.utcnow().isoformat(),
            'compliant': self._check_value_compliance(metric_name, value)
        }
        self._metrics[metric_name].append(record)

        if not record['compliant']:
            self._violations.append({
                'metric_name': metric_name,
                'value': value,
                'target': self._slas.get(metric_name, {}).get('target'),
                'timestamp': record['timestamp']
            })

    def _check_value_compliance(
        self,
        metric_name: str,
        value: float
    ) -> bool:
        """Check if value complies with SLA."""
        if metric_name not in self._slas:
            return True

        sla = self._slas[metric_name]
        target = sla.get('target', 0)
        comparison = sla.get('comparison', 'lte')

        if comparison == 'lte':
            return value <= target
        elif comparison == 'gte':
            return value >= target
        elif comparison == 'eq':
            return value == target
        return True

    def check_compliance(
        self,
        metric_name: str
    ) -> Dict[str, Any]:
        """
        Check compliance for a metric.

        Args:
            metric_name: Name of the metric

        Returns:
            Dictionary with compliance status

        Example:
            >>> status = service.check_compliance('latency')
        """
        if metric_name not in self._slas:
            return {'error': 'SLA not found'}

        metrics = self._metrics.get(metric_name, [])
        if not metrics:
            return {
                'metric_name': metric_name,
                'compliant': True,
                'total': 0,
                'violations': 0
            }

        compliant_count = sum(1 for m in metrics if m.get('compliant', True))
        total = len(metrics)

        return {
            'metric_name': metric_name,
            'compliant': compliant_count == total,
            'total': total,
            'compliant_count': compliant_count,
            'violation_count': total - compliant_count,
            'compliance_rate': (compliant_count / total * 100) if total > 0 else 100.0
        }

    def get_compliance_status(self) -> Dict[str, Any]:
        """
        Get overall compliance status.

        Returns:
            Dictionary with overall status

        Example:
            >>> status = service.get_compliance_status()
        """
        results = {}
        total_compliant = 0
        total_metrics = 0

        for metric_name in self._slas:
            compliance = self.check_compliance(metric_name)
            results[metric_name] = compliance
            total_metrics += compliance.get('total', 0)
            total_compliant += compliance.get('compliant_count', 0)

        overall_rate = (total_compliant / total_metrics * 100) if total_metrics > 0 else 100.0

        return {
            'overall_compliant': overall_rate >= 99.0,
            'overall_rate': float(overall_rate),
            'total_metrics': total_metrics,
            'total_compliant': total_compliant,
            'by_metric': results
        }

    def detect_violations(self) -> List[Dict[str, Any]]:
        """
        Detect all SLA violations.

        Returns:
            List of violation records

        Example:
            >>> violations = service.detect_violations()
        """
        return self._violations.copy()

    def get_violation_count(
        self,
        metric_name: str = None
    ) -> int:
        """
        Get count of violations.

        Args:
            metric_name: Optional metric to filter by

        Returns:
            Number of violations

        Example:
            >>> count = service.get_violation_count('latency')
        """
        if metric_name:
            return sum(
                1 for v in self._violations
                if v.get('metric_name') == metric_name
            )
        return len(self._violations)

    def get_violation_history(
        self,
        metric_name: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get violation history.

        Args:
            metric_name: Optional metric to filter by
            limit: Maximum number of results

        Returns:
            List of violations

        Example:
            >>> history = service.get_violation_history(limit=50)
        """
        violations = self._violations
        if metric_name:
            violations = [
                v for v in violations
                if v.get('metric_name') == metric_name
            ]
        return violations[-limit:]

    def calculate_compliance_rate(
        self,
        metric_name: str = None
    ) -> float:
        """
        Calculate compliance rate.

        Args:
            metric_name: Optional metric to filter by

        Returns:
            Compliance rate as percentage

        Example:
            >>> rate = service.calculate_compliance_rate()
        """
        if metric_name:
            compliance = self.check_compliance(metric_name)
            return compliance.get('compliance_rate', 100.0)

        status = self.get_compliance_status()
        return status.get('overall_rate', 100.0)

    def get_uptime_percentage(self) -> float:
        """
        Get uptime percentage.

        Returns:
            Uptime as percentage

        Example:
            >>> uptime = service.get_uptime_percentage()
        """
        if 'uptime' in self._slas:
            compliance = self.check_compliance('uptime')
            return compliance.get('compliance_rate', 100.0)
        return 100.0

    def get_error_budget(
        self,
        metric_name: str,
        target_compliance: float = 99.9
    ) -> Dict[str, Any]:
        """
        Get remaining error budget.

        Args:
            metric_name: Name of the metric
            target_compliance: Target compliance percentage

        Returns:
            Dictionary with error budget info

        Example:
            >>> budget = service.get_error_budget('latency', 99.9)
        """
        compliance = self.check_compliance(metric_name)
        total = compliance.get('total', 0)

        allowed_errors = int(total * (100 - target_compliance) / 100)
        actual_errors = compliance.get('violation_count', 0)
        remaining = allowed_errors - actual_errors

        return {
            'metric_name': metric_name,
            'target_compliance': target_compliance,
            'allowed_errors': allowed_errors,
            'actual_errors': actual_errors,
            'remaining_budget': max(0, remaining),
            'budget_exhausted': remaining <= 0
        }

    def generate_compliance_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive compliance report.

        Returns:
            Dictionary with full compliance analysis

        Example:
            >>> report = service.generate_compliance_report()
        """
        status = self.get_compliance_status()

        return {
            'status': status,
            'sla_definitions': self._slas,
            'violation_count': len(self._violations),
            'recent_violations': self.get_violation_history(limit=10),
            'generated_at': datetime.utcnow().isoformat()
        }

    def get_sla_summary(self) -> Dict[str, Any]:
        """
        Get summary of all SLAs.

        Returns:
            Dictionary with SLA summary

        Example:
            >>> summary = service.get_sla_summary()
        """
        summary = []
        for name, sla in self._slas.items():
            compliance = self.check_compliance(name)
            summary.append({
                'metric_name': name,
                'target': sla.get('target'),
                'unit': sla.get('unit'),
                'compliance_rate': compliance.get('compliance_rate', 100.0),
                'violations': compliance.get('violation_count', 0)
            })

        return {
            'sla_count': len(self._slas),
            'slas': summary,
            'total_violations': len(self._violations)
        }
