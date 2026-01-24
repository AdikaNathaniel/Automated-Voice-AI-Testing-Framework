"""
SLAComplianceTargetsMixin - Targets, alerts, and budget methods for SLA compliance service.

This mixin provides target management, alerting, and budget tracking methods:
- SLA target definition (latency, availability, throughput)
- Violation alerting
- Compliance reporting and export
- Error budget tracking

Extracted from sla_compliance_service.py to reduce file size per coding conventions.
"""

from typing import List, Dict, Any
from datetime import datetime
import uuid


class SLAComplianceTargetsMixin:
    """
    Mixin providing targets, alerts, and budget methods for SLAComplianceService.

    This mixin contains:
    - SLA target definition methods
    - Violation alerting methods
    - Compliance reporting methods
    - Error budget tracking methods
    """

    def set_latency_target(
        self,
        target_ms: float,
        percentile: float = 95.0
    ) -> Dict[str, Any]:
        """Set latency SLA target."""
        return self.define_sla(
            f'latency_p{int(percentile)}',
            target=target_ms,
            unit='ms',
            comparison='lte'
        )

    def set_availability_target(
        self,
        target_percent: float = 99.9
    ) -> Dict[str, Any]:
        """Set availability SLA target."""
        return self.define_sla(
            'availability',
            target=target_percent,
            unit='percent',
            comparison='gte'
        )

    def set_throughput_target(
        self,
        target_rps: float
    ) -> Dict[str, Any]:
        """Set throughput SLA target."""
        return self.define_sla(
            'throughput',
            target=target_rps,
            unit='rps',
            comparison='gte'
        )

    def get_targets(self) -> Dict[str, Any]:
        """Get all SLA targets."""
        return {
            'targets': list(self._slas.values()),
            'count': len(self._slas)
        }

    def check_violation(
        self,
        metric_name: str,
        value: float
    ) -> Dict[str, Any]:
        """Check if a value violates the SLA."""
        if metric_name not in self._slas:
            return {'error': 'SLA not found', 'violated': False}

        compliant = self._check_value_compliance(metric_name, value)
        sla = self._slas[metric_name]

        return {
            'metric_name': metric_name,
            'value': value,
            'target': sla.get('target'),
            'violated': not compliant,
            'severity': 'critical' if not compliant else 'none'
        }

    def get_violations(
        self,
        metric_name: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get violations list."""
        violations = self._violations
        if metric_name:
            violations = [
                v for v in violations
                if v.get('metric_name') == metric_name
            ]
        return violations[-limit:]

    def create_alert(
        self,
        metric_name: str,
        severity: str = 'warning',
        message: str = None
    ) -> Dict[str, Any]:
        """Create an SLA violation alert."""
        alert_id = str(uuid.uuid4())
        alert = {
            'id': alert_id,
            'metric_name': metric_name,
            'severity': severity,
            'message': message or f'SLA violation for {metric_name}',
            'status': 'active',
            'created_at': datetime.utcnow().isoformat()
        }
        self._alerts.append(alert)
        return alert

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts."""
        return [a for a in self._alerts if a.get('status') == 'active']

    def calculate_compliance(
        self,
        metric_name: str = None
    ) -> Dict[str, Any]:
        """Calculate compliance metrics."""
        if metric_name:
            compliance = self.check_compliance(metric_name)
            return {
                'metric_name': metric_name,
                'compliance_rate': compliance.get('compliance_rate', 100.0),
                'total_checks': compliance.get('total', 0),
                'violations': compliance.get('violation_count', 0)
            }

        status = self.get_compliance_status()
        return {
            'overall_compliance_rate': status.get('overall_rate', 100.0),
            'total_metrics': status.get('total_metrics', 0),
            'compliant_count': status.get('total_compliant', 0),
            'by_metric': status.get('by_metric', {})
        }

    def generate_report(
        self,
        include_history: bool = True
    ) -> Dict[str, Any]:
        """Generate SLA compliance report."""
        report = self.generate_compliance_report()
        if include_history:
            report['compliance_history'] = self._compliance_history[-50:]
        return report

    def get_compliance_history(
        self,
        metric_name: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get compliance history."""
        history = self._compliance_history
        if metric_name:
            history = [
                h for h in history
                if h.get('metric_name') == metric_name
            ]
        return history[-limit:]

    def export_compliance_data(
        self,
        format: str = 'json'
    ) -> Dict[str, Any]:
        """Export compliance data."""
        data = {
            'slas': list(self._slas.values()),
            'violations': self._violations,
            'compliance_history': self._compliance_history,
            'alerts': self._alerts
        }

        return {
            'format': format,
            'data': data,
            'exported_at': datetime.utcnow().isoformat(),
            'record_count': len(self._violations) + len(self._compliance_history)
        }

    def set_error_budget(
        self,
        metric_name: str,
        budget_percent: float = 0.1,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Set error budget for a metric."""
        budget = {
            'metric_name': metric_name,
            'budget_percent': budget_percent,
            'period_days': period_days,
            'consumed': 0.0,
            'remaining': budget_percent,
            'started_at': datetime.utcnow().isoformat()
        }
        self._error_budgets[metric_name] = budget
        return budget

    def consume_error_budget(
        self,
        metric_name: str,
        amount: float
    ) -> Dict[str, Any]:
        """Consume error budget."""
        if metric_name not in self._error_budgets:
            return {'error': 'Error budget not found'}

        budget = self._error_budgets[metric_name]
        budget['consumed'] += amount
        budget['remaining'] = max(0, budget['budget_percent'] - budget['consumed'])

        return {
            'metric_name': metric_name,
            'consumed': budget['consumed'],
            'remaining': budget['remaining'],
            'exhausted': budget['remaining'] <= 0
        }

    def get_remaining_budget(
        self,
        metric_name: str
    ) -> Dict[str, Any]:
        """Get remaining error budget."""
        if metric_name not in self._error_budgets:
            return {'error': 'Error budget not found', 'remaining': 0}

        budget = self._error_budgets[metric_name]
        return {
            'metric_name': metric_name,
            'budget_percent': budget['budget_percent'],
            'consumed': budget['consumed'],
            'remaining': budget['remaining'],
            'remaining_percent': (budget['remaining'] / budget['budget_percent'] * 100) if budget['budget_percent'] > 0 else 0
        }

    def reset_error_budget(
        self,
        metric_name: str
    ) -> Dict[str, Any]:
        """Reset error budget."""
        if metric_name not in self._error_budgets:
            return {'error': 'Error budget not found'}

        budget = self._error_budgets[metric_name]
        budget['consumed'] = 0.0
        budget['remaining'] = budget['budget_percent']
        budget['reset_at'] = datetime.utcnow().isoformat()

        return {
            'metric_name': metric_name,
            'reset': True,
            'remaining': budget['remaining']
        }

    def get_budget_burn_rate(
        self,
        metric_name: str
    ) -> Dict[str, Any]:
        """Get error budget burn rate."""
        if metric_name not in self._error_budgets:
            return {'error': 'Error budget not found', 'burn_rate': 0}

        budget = self._error_budgets[metric_name]
        consumed = budget['consumed']
        budget_percent = budget['budget_percent']

        if budget_percent > 0:
            burn_rate = consumed / budget_percent * 100
        else:
            burn_rate = 0

        return {
            'metric_name': metric_name,
            'burn_rate_percent': float(burn_rate),
            'consumed': consumed,
            'budget': budget_percent,
            'status': 'critical' if burn_rate > 100 else 'warning' if burn_rate > 80 else 'healthy'
        }
