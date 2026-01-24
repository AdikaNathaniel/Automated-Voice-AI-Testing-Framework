"""
Capacity Planning Service for infrastructure sizing.

This service provides capacity planning capabilities for
resource projection, cost estimation, and infrastructure sizing.

Key features:
- Resource projection based on growth
- Cost estimation per test volume
- Infrastructure right-sizing recommendations

Example:
    >>> service = CapacityPlanningService()
    >>> service.set_growth_rate(0.1)  # 10% growth
    >>> projection = service.project_resources(months=12)
    >>> print(f"Projected: {projection['projected_resources']}")
"""

from typing import List, Dict, Any
from datetime import datetime


class CapacityPlanningService:
    """
    Service for capacity planning and infrastructure sizing.

    Provides resource projection, cost estimation, and
    optimization recommendations.

    Example:
        >>> service = CapacityPlanningService()
        >>> cost = service.estimate_cost(test_volume=1000)
        >>> print(f"Estimated cost: ${cost['total_cost']}")
    """

    def __init__(self):
        """Initialize the capacity planning service."""
        self._growth_rate: float = 0.0
        self._current_resources: Dict[str, Any] = {}
        self._cost_model: Dict[str, float] = {
            'cpu_per_hour': 0.05,
            'memory_per_gb_hour': 0.01,
            'storage_per_gb_month': 0.10,
            'network_per_gb': 0.05
        }
        self._utilization_data: List[Dict[str, Any]] = []

    # Resource Projection Methods

    def project_resources(
        self,
        months: int = 12,
        base_usage: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Project resource needs based on growth.

        Args:
            months: Number of months to project
            base_usage: Base resource usage

        Returns:
            Dictionary with projected resources

        Example:
            >>> projection = service.project_resources(months=6)
        """
        base = base_usage or {
            'cpu_cores': 4,
            'memory_gb': 16,
            'storage_gb': 100
        }

        projections = []
        for month in range(1, months + 1):
            factor = (1 + self._growth_rate) ** month
            projections.append({
                'month': month,
                'cpu_cores': int(base.get('cpu_cores', 4) * factor),
                'memory_gb': int(base.get('memory_gb', 16) * factor),
                'storage_gb': int(base.get('storage_gb', 100) * factor)
            })

        return {
            'base_usage': base,
            'growth_rate': self._growth_rate,
            'projections': projections,
            'final_projection': projections[-1] if projections else base
        }

    def set_growth_rate(
        self,
        rate: float
    ) -> Dict[str, Any]:
        """
        Set expected growth rate.

        Args:
            rate: Monthly growth rate (e.g., 0.1 for 10%)

        Returns:
            Dictionary with growth configuration

        Example:
            >>> service.set_growth_rate(0.15)  # 15% monthly growth
        """
        self._growth_rate = rate
        return {
            'growth_rate': rate,
            'annual_growth': (1 + rate) ** 12 - 1,
            'updated_at': datetime.utcnow().isoformat()
        }

    def get_projection(
        self,
        resource_type: str,
        months: int = 12
    ) -> Dict[str, Any]:
        """
        Get projection for specific resource.

        Args:
            resource_type: Type of resource (cpu, memory, storage)
            months: Number of months

        Returns:
            Dictionary with resource projection

        Example:
            >>> proj = service.get_projection('cpu', months=6)
        """
        base_values = {
            'cpu': 4,
            'memory': 16,
            'storage': 100
        }

        base = base_values.get(resource_type, 10)
        values = []
        for month in range(1, months + 1):
            value = base * ((1 + self._growth_rate) ** month)
            values.append({
                'month': month,
                'value': float(value)
            })

        return {
            'resource_type': resource_type,
            'base_value': base,
            'projections': values,
            'final_value': values[-1]['value'] if values else base
        }

    def forecast_capacity(
        self,
        target_utilization: float = 0.8
    ) -> Dict[str, Any]:
        """
        Forecast when capacity will be reached.

        Args:
            target_utilization: Target utilization threshold

        Returns:
            Dictionary with capacity forecast

        Example:
            >>> forecast = service.forecast_capacity(0.75)
        """
        if self._growth_rate <= 0:
            return {
                'months_until_capacity': None,
                'message': 'No growth rate set'
            }

        # Simple calculation: when does utilization hit target?
        current_util = 0.5  # Assume 50% current
        months = 0
        util = current_util

        while util < target_utilization and months < 120:
            util = current_util * ((1 + self._growth_rate) ** months)
            months += 1

        return {
            'current_utilization': current_util,
            'target_utilization': target_utilization,
            'months_until_capacity': months,
            'growth_rate': self._growth_rate
        }

    # Cost Estimation Methods

    def estimate_cost(
        self,
        test_volume: int,
        duration_hours: int = 1
    ) -> Dict[str, Any]:
        """
        Estimate cost for test volume.

        Args:
            test_volume: Number of tests
            duration_hours: Test duration in hours

        Returns:
            Dictionary with cost estimate

        Example:
            >>> cost = service.estimate_cost(1000, duration_hours=2)
        """
        # Estimate resources needed
        cpu_hours = (test_volume / 100) * duration_hours
        memory_gb_hours = (test_volume / 50) * duration_hours
        storage_gb = test_volume * 0.01
        network_gb = test_volume * 0.005

        cpu_cost = cpu_hours * self._cost_model['cpu_per_hour']
        memory_cost = memory_gb_hours * self._cost_model['memory_per_gb_hour']
        storage_cost = storage_gb * self._cost_model['storage_per_gb_month']
        network_cost = network_gb * self._cost_model['network_per_gb']

        total = cpu_cost + memory_cost + storage_cost + network_cost

        return {
            'test_volume': test_volume,
            'duration_hours': duration_hours,
            'cpu_cost': float(cpu_cost),
            'memory_cost': float(memory_cost),
            'storage_cost': float(storage_cost),
            'network_cost': float(network_cost),
            'total_cost': float(total),
            'cost_per_test': float(total / test_volume) if test_volume > 0 else 0
        }

    def set_cost_model(
        self,
        cost_model: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Set cost model parameters.

        Args:
            cost_model: Dictionary with cost parameters

        Returns:
            Dictionary with updated cost model

        Example:
            >>> service.set_cost_model({'cpu_per_hour': 0.10})
        """
        self._cost_model.update(cost_model)
        return {
            'cost_model': self._cost_model,
            'updated_at': datetime.utcnow().isoformat()
        }

    def get_cost_breakdown(
        self,
        test_volume: int
    ) -> Dict[str, Any]:
        """
        Get detailed cost breakdown.

        Args:
            test_volume: Number of tests

        Returns:
            Dictionary with cost breakdown

        Example:
            >>> breakdown = service.get_cost_breakdown(1000)
        """
        estimate = self.estimate_cost(test_volume)

        breakdown = {
            'compute': {
                'cpu': estimate['cpu_cost'],
                'memory': estimate['memory_cost']
            },
            'storage': estimate['storage_cost'],
            'network': estimate['network_cost']
        }

        total = estimate['total_cost']
        percentages = {}
        if total > 0:
            percentages = {
                'compute': (estimate['cpu_cost'] + estimate['memory_cost']) / total * 100,
                'storage': estimate['storage_cost'] / total * 100,
                'network': estimate['network_cost'] / total * 100
            }

        return {
            'breakdown': breakdown,
            'percentages': percentages,
            'total_cost': total
        }

    def calculate_roi(
        self,
        test_volume: int,
        manual_cost_per_test: float = 10.0
    ) -> Dict[str, Any]:
        """
        Calculate ROI of automated testing.

        Args:
            test_volume: Number of tests
            manual_cost_per_test: Cost of manual testing

        Returns:
            Dictionary with ROI calculation

        Example:
            >>> roi = service.calculate_roi(1000, manual_cost_per_test=15)
        """
        automated_cost = self.estimate_cost(test_volume)['total_cost']
        manual_cost = test_volume * manual_cost_per_test

        savings = manual_cost - automated_cost
        roi_percent = (savings / automated_cost * 100) if automated_cost > 0 else 0

        return {
            'test_volume': test_volume,
            'automated_cost': float(automated_cost),
            'manual_cost': float(manual_cost),
            'savings': float(savings),
            'roi_percent': float(roi_percent),
            'recommendation': 'Automate' if roi_percent > 100 else 'Evaluate further'
        }

    # Infrastructure Sizing Methods

    def recommend_sizing(
        self,
        expected_load: int,
        growth_months: int = 12
    ) -> Dict[str, Any]:
        """
        Recommend infrastructure sizing.

        Args:
            expected_load: Expected test load
            growth_months: Months to plan for

        Returns:
            Dictionary with sizing recommendations

        Example:
            >>> sizing = service.recommend_sizing(1000, growth_months=6)
        """
        # Base sizing
        base_cpu = max(2, expected_load // 100)
        base_memory = max(4, expected_load // 50)
        base_storage = max(50, expected_load // 10)

        # Apply growth factor
        growth_factor = (1 + self._growth_rate) ** growth_months

        return {
            'expected_load': expected_load,
            'growth_months': growth_months,
            'current_sizing': {
                'cpu_cores': base_cpu,
                'memory_gb': base_memory,
                'storage_gb': base_storage
            },
            'recommended_sizing': {
                'cpu_cores': int(base_cpu * growth_factor),
                'memory_gb': int(base_memory * growth_factor),
                'storage_gb': int(base_storage * growth_factor)
            },
            'headroom_percent': 20
        }

    def analyze_utilization(
        self,
        utilization_samples: List[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Analyze resource utilization.

        Args:
            utilization_samples: List of utilization samples

        Returns:
            Dictionary with utilization analysis

        Example:
            >>> analysis = service.analyze_utilization()
        """
        samples = utilization_samples or self._utilization_data

        if not samples:
            return {
                'average_utilization': 0.0,
                'peak_utilization': 0.0,
                'recommendation': 'Insufficient data'
            }

        cpu_utils = [s.get('cpu', 0) for s in samples]
        memory_utils = [s.get('memory', 0) for s in samples]

        avg_cpu = sum(cpu_utils) / len(cpu_utils)
        avg_memory = sum(memory_utils) / len(memory_utils)
        peak_cpu = max(cpu_utils)
        peak_memory = max(memory_utils)

        # Determine recommendation
        if avg_cpu < 30 and avg_memory < 30:
            recommendation = 'Consider downsizing resources'
        elif peak_cpu > 80 or peak_memory > 80:
            recommendation = 'Consider scaling up resources'
        else:
            recommendation = 'Current sizing is appropriate'

        return {
            'cpu': {
                'average': float(avg_cpu),
                'peak': float(peak_cpu)
            },
            'memory': {
                'average': float(avg_memory),
                'peak': float(peak_memory)
            },
            'recommendation': recommendation,
            'sample_count': len(samples)
        }

    def get_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """
        Get optimization suggestions.

        Returns:
            List of optimization suggestions

        Example:
            >>> suggestions = service.get_optimization_suggestions()
        """
        suggestions = []

        # Analyze current state
        analysis = self.analyze_utilization()

        if analysis.get('cpu', {}).get('average', 0) < 30:
            suggestions.append({
                'category': 'compute',
                'suggestion': 'Reduce CPU allocation',
                'potential_savings': '20-30%',
                'priority': 'medium'
            })

        if analysis.get('memory', {}).get('peak', 0) > 80:
            suggestions.append({
                'category': 'memory',
                'suggestion': 'Increase memory allocation',
                'impact': 'Prevent OOM errors',
                'priority': 'high'
            })

        # Always suggest reserved instances for cost savings
        suggestions.append({
            'category': 'cost',
            'suggestion': 'Consider reserved instances for predictable workloads',
            'potential_savings': '30-50%',
            'priority': 'medium'
        })

        return suggestions

    # Reporting Methods

    def generate_plan(
        self,
        months: int = 12
    ) -> Dict[str, Any]:
        """
        Generate comprehensive capacity plan.

        Args:
            months: Planning horizon

        Returns:
            Dictionary with capacity plan

        Example:
            >>> plan = service.generate_plan(months=12)
        """
        projection = self.project_resources(months)
        cost = self.estimate_cost(1000 * (1 + self._growth_rate) ** months)
        suggestions = self.get_optimization_suggestions()

        return {
            'planning_horizon_months': months,
            'resource_projection': projection,
            'cost_projection': cost,
            'optimization_suggestions': suggestions,
            'growth_rate': self._growth_rate,
            'generated_at': datetime.utcnow().isoformat()
        }

    def get_planning_summary(self) -> Dict[str, Any]:
        """
        Get capacity planning summary.

        Returns:
            Dictionary with planning summary

        Example:
            >>> summary = service.get_planning_summary()
        """
        projection = self.project_resources(12)
        analysis = self.analyze_utilization()

        return {
            'current_state': {
                'growth_rate': self._growth_rate,
                'utilization': analysis
            },
            'future_state': {
                'months_ahead': 12,
                'projected_resources': projection['final_projection']
            },
            'cost_model': self._cost_model,
            'recommendations': self.get_optimization_suggestions()[:3]
        }
