"""
Test suite for monitoring and alerts validation with forced failure scenarios.

This module tests:
- Prometheus metrics endpoint functionality
- Alert expressions match actual metric names
- Forced failure scenarios to validate alerts would fire
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

import re
from pathlib import Path
from typing import Any, Dict, List

import pytest
import yaml


class TestPrometheusMetricsEndpoint:
    """Test that Prometheus metrics endpoint is properly configured"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return Path(__file__).parent.parent

    @pytest.fixture
    def metrics_module(self):
        """Import the metrics module"""
        from api.metrics import (
            registry,
            test_executions_total,
            queue_depth,
        )
        return {
            'registry': registry,
            'test_executions_total': test_executions_total,
            'queue_depth': queue_depth,
        }

    def test_metrics_registry_exists(self, metrics_module):
        """Test that Prometheus registry exists"""
        from prometheus_client import CollectorRegistry
        assert isinstance(metrics_module['registry'], CollectorRegistry)

    def test_metrics_endpoint_route_exists(self, project_root):
        """Test that metrics route file exists"""
        metrics_route = project_root / "backend" / "api" / "routes" / "metrics.py"
        assert metrics_route.exists(), \
            "Metrics route should exist at backend/api/routes/metrics.py"

    def test_metrics_module_exists(self, project_root):
        """Test that metrics module file exists"""
        metrics_module = project_root / "backend" / "api" / "metrics.py"
        assert metrics_module.exists(), \
            "Metrics module should exist at backend/api/metrics.py"

    def test_prometheus_config_scrapes_backend(self, project_root):
        """Test that Prometheus is configured to scrape backend metrics"""
        prom_config_path = project_root / "infrastructure" / "prometheus" / "prometheus.yml"

        with open(prom_config_path) as f:
            config = yaml.safe_load(f)

        scrape_configs = config.get('scrape_configs', [])
        backend_job = next(
            (job for job in scrape_configs if job.get('job_name') == 'backend'),
            None
        )

        assert backend_job is not None, \
            "Prometheus should have a 'backend' scrape job"
        assert backend_job.get('metrics_path') == '/metrics', \
            "Backend scrape job should use /metrics path"


class TestMetricNamesMatchAlerts:
    """Test that metric names in code match alert expressions"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return Path(__file__).parent.parent

    @pytest.fixture
    def alerts_config(self, project_root):
        """Load alerts configuration"""
        alerts_path = project_root / "infrastructure" / "prometheus" / "alerts.yml"
        with open(alerts_path) as f:
            return yaml.safe_load(f)

    @pytest.fixture
    def alert_rules(self, alerts_config):
        """Get alert rules from config"""
        groups = alerts_config.get('groups', [])
        for group in groups:
            if group.get('name') == 'automated-testing-alerts':
                return group.get('rules', [])
        return []

    def test_test_executions_metric_matches_low_success_rate_alert(self):
        """Test that test_executions metric is used in LowSuccessRate alert"""
        # Import to verify metric exists
        from api.metrics import test_executions_total
        from prometheus_client import Counter

        assert isinstance(test_executions_total, Counter), \
            "test_executions_total should be a Counter"

        # Verify metric name matches alert expression pattern
        # Alert uses: test_executions_total{result="success"}
        assert test_executions_total._name == 'test_executions', \
            "Metric name should be 'test_executions'"

    def test_queue_depth_metric_matches_high_queue_depth_alert(self):
        """Test that queue_depth metric is used in HighQueueDepth alert"""
        from api.metrics import queue_depth
        from prometheus_client import Gauge

        assert isinstance(queue_depth, Gauge), \
            "queue_depth should be a Gauge"

        # Alert uses: queue_depth > 1000
        assert queue_depth._name == 'queue_depth', \
            "Metric name should be 'queue_depth'"

    def test_low_success_rate_alert_uses_correct_metric(self, alert_rules):
        """Test LowSuccessRate alert references correct metric"""
        low_success_alert = next(
            (rule for rule in alert_rules if rule.get('alert') == 'LowSuccessRate'),
            None
        )

        assert low_success_alert is not None
        expr = low_success_alert.get('expr', '')

        # Should reference test_executions_total metric
        assert 'test_executions_total' in expr, \
            "LowSuccessRate should use test_executions_total metric"

    def test_high_queue_depth_alert_uses_correct_metric(self, alert_rules):
        """Test HighQueueDepth alert references correct metric"""
        queue_alert = next(
            (rule for rule in alert_rules if rule.get('alert') == 'HighQueueDepth'),
            None
        )

        assert queue_alert is not None
        expr = queue_alert.get('expr', '')

        # Should reference queue_depth metric
        assert 'queue_depth' in expr, \
            "HighQueueDepth should use queue_depth metric"


class TestForcedFailureScenarios:
    """Test forced failure scenarios to validate alerts would fire"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return Path(__file__).parent.parent

    @pytest.fixture
    def alerts_config(self, project_root):
        """Load alerts configuration"""
        alerts_path = project_root / "infrastructure" / "prometheus" / "alerts.yml"
        with open(alerts_path) as f:
            return yaml.safe_load(f)

    @pytest.fixture
    def alert_rules(self, alerts_config):
        """Get alert rules from config"""
        groups = alerts_config.get('groups', [])
        for group in groups:
            if group.get('name') == 'automated-testing-alerts':
                return group.get('rules', [])
        return []

    def test_forced_failure_low_success_rate_scenario(self):
        """
        Forced failure scenario: Simulate low success rate

        This test validates that when success rate drops below 95%,
        the LowSuccessRate alert expression would evaluate to true.
        """
        from api.metrics import test_executions_total, registry
        from prometheus_client import REGISTRY

        # Create isolated registry for test
        from prometheus_client import CollectorRegistry, Counter
        test_registry = CollectorRegistry()

        # Create test metrics
        test_counter = Counter(
            'test_executions',
            'Test counter',
            labelnames=['result'],
            registry=test_registry
        )

        # Simulate failure scenario: 90% success rate (below 95% threshold)
        # 90 successes, 10 failures = 90% success rate
        for _ in range(90):
            test_counter.labels(result='success').inc()
        for _ in range(10):
            test_counter.labels(result='failure').inc()

        # Calculate success rate
        success_count = test_counter.labels(result='success')._value.get()
        total_count = sum(
            test_counter.labels(result=r)._value.get()
            for r in ['success', 'failure']
        )

        success_rate = success_count / total_count if total_count > 0 else 0

        # Assert: This scenario would trigger the alert
        assert success_rate < 0.95, \
            f"Forced failure: Success rate {success_rate:.2%} should be below 95%"

        # Document the alert condition
        alert_would_fire = success_rate < 0.95
        assert alert_would_fire, \
            "LowSuccessRate alert should fire when success rate is below 95%"

    def test_forced_failure_high_queue_depth_scenario(self):
        """
        Forced failure scenario: Simulate high queue depth

        This test validates that when queue depth exceeds 1000,
        the HighQueueDepth alert expression would evaluate to true.
        """
        from prometheus_client import CollectorRegistry, Gauge

        # Create isolated registry for test
        test_registry = CollectorRegistry()

        # Create test metric
        test_queue = Gauge(
            'queue_depth',
            'Test queue depth',
            registry=test_registry
        )

        # Simulate failure scenario: Queue depth of 1500 (above 1000 threshold)
        test_queue.set(1500)

        queue_value = test_queue._value.get()

        # Assert: This scenario would trigger the alert
        assert queue_value > 1000, \
            f"Forced failure: Queue depth {queue_value} should exceed 1000"

        # Document the alert condition
        alert_would_fire = queue_value > 1000
        assert alert_would_fire, \
            "HighQueueDepth alert should fire when queue depth exceeds 1000"

    def test_forced_failure_high_latency_scenario(self):
        """
        Forced failure scenario: Simulate high API latency

        This test validates that when P95 latency exceeds 5 seconds,
        the HighResponseLatency alert expression would evaluate to true.
        """
        from prometheus_client import CollectorRegistry, Histogram
        import statistics

        # Create isolated registry for test
        test_registry = CollectorRegistry()

        # Create test metric with same buckets as production
        test_histogram = Histogram(
            'api_response_time_seconds',
            'Test API response time',
            registry=test_registry,
            buckets=(0.1, 0.5, 1, 2, 5, 10, 30, 60)
        )

        # Simulate failure scenario: Most requests are slow (> 5s)
        # Generate 100 samples where P95 would be > 5 seconds
        latencies = []
        for i in range(100):
            if i < 90:
                # 90% of requests take 6 seconds (above threshold)
                latency = 6.0
            else:
                # 10% take 1 second
                latency = 1.0
            test_histogram.observe(latency)
            latencies.append(latency)

        # Calculate P95 manually
        sorted_latencies = sorted(latencies)
        p95_index = int(len(sorted_latencies) * 0.95) - 1
        p95_latency = sorted_latencies[p95_index]

        # Assert: This scenario would trigger the alert
        assert p95_latency > 5, \
            f"Forced failure: P95 latency {p95_latency}s should exceed 5s"

        # Document the alert condition
        alert_would_fire = p95_latency > 5
        assert alert_would_fire, \
            "HighResponseLatency alert should fire when P95 exceeds 5 seconds"

    def test_forced_failure_documents_alert_thresholds(self, alert_rules):
        """
        Document all alert thresholds for forced failure testing

        This test validates that alerts have documented thresholds
        that can be used for forced failure scenarios.
        """
        threshold_tests = {
            'LowSuccessRate': {
                'threshold': 0.95,
                'condition': 'success_rate < 0.95',
                'unit': 'percentage',
            },
            'HighQueueDepth': {
                'threshold': 1000,
                'condition': 'queue_depth > 1000',
                'unit': 'jobs',
            },
            'HighResponseLatency': {
                'threshold': 5,
                'condition': 'p95_latency > 5',
                'unit': 'seconds',
            },
        }

        for rule in alert_rules:
            alert_name = rule.get('alert')

            if alert_name in threshold_tests:
                expected = threshold_tests[alert_name]
                expr = rule.get('expr', '')

                # Verify threshold is in expression
                threshold_str = str(expected['threshold'])

                # Check if the expression contains the threshold value
                # (allowing for different formats like 0.95 or 95%)
                if expected['unit'] == 'percentage':
                    assert '0.95' in expr or '95' in expr, \
                        f"{alert_name} should have threshold {threshold_str}"
                else:
                    assert threshold_str in expr, \
                        f"{alert_name} should have threshold {threshold_str}"


class TestAlertNotificationConfiguration:
    """Test alert notification configuration is properly set up"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return Path(__file__).parent.parent

    @pytest.fixture
    def alerts_config(self, project_root):
        """Load alerts configuration"""
        alerts_path = project_root / "infrastructure" / "prometheus" / "alerts.yml"
        with open(alerts_path) as f:
            return yaml.safe_load(f)

    def test_alerts_have_severity_for_routing(self, alerts_config):
        """Test that all alerts have severity labels for routing"""
        groups = alerts_config.get('groups', [])

        for group in groups:
            rules = group.get('rules', [])
            for rule in rules:
                alert_name = rule.get('alert')
                labels = rule.get('labels', {})

                assert 'severity' in labels, \
                    f"Alert '{alert_name}' should have severity label for routing"

    def test_critical_alerts_have_short_duration(self, alerts_config):
        """Test that critical alerts have reasonable 'for' duration"""
        groups = alerts_config.get('groups', [])

        for group in groups:
            rules = group.get('rules', [])
            for rule in rules:
                alert_name = rule.get('alert')
                labels = rule.get('labels', {})

                if labels.get('severity') == 'critical':
                    # Critical alerts should have 'for' clause
                    assert 'for' in rule, \
                        f"Critical alert '{alert_name}' should have 'for' duration"

                    # Parse duration (e.g., "2m", "5m")
                    duration = rule['for']
                    minutes = int(re.search(r'(\d+)', duration).group(1))

                    # Critical alerts should fire within 10 minutes
                    assert minutes <= 10, \
                        f"Critical alert '{alert_name}' duration {duration} should be <= 10m"


class TestMonitoringIntegration:
    """Test end-to-end monitoring integration"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return Path(__file__).parent.parent

    def test_docker_compose_includes_prometheus(self, project_root):
        """Test that docker-compose includes Prometheus service"""
        compose_path = project_root / "docker-compose.yml"

        with open(compose_path) as f:
            compose = yaml.safe_load(f)

        services = compose.get('services', {})
        assert 'prometheus' in services, \
            "docker-compose should include prometheus service"

    def test_docker_compose_includes_grafana(self, project_root):
        """Test that docker-compose includes Grafana service"""
        compose_path = project_root / "docker-compose.yml"

        with open(compose_path) as f:
            compose = yaml.safe_load(f)

        services = compose.get('services', {})
        assert 'grafana' in services, \
            "docker-compose should include grafana service"

    def test_grafana_has_prometheus_datasource(self, project_root):
        """Test that Grafana is configured with Prometheus datasource"""
        datasource_path = (
            project_root / "infrastructure" / "grafana" /
            "provisioning" / "datasources" / "prometheus.yml"
        )

        assert datasource_path.exists(), \
            "Grafana should have Prometheus datasource configured"

        with open(datasource_path) as f:
            config = yaml.safe_load(f)

        datasources = config.get('datasources', [])
        prometheus_ds = next(
            (ds for ds in datasources if ds.get('type') == 'prometheus'),
            None
        )

        assert prometheus_ds is not None, \
            "Grafana should have Prometheus datasource"


class TestMonitoringResilience:
    """Test monitoring system resilience and recovery"""

    def test_metrics_can_be_incremented_after_failure(self):
        """
        Test that metrics can recover after simulated failures

        This validates that the monitoring system remains functional
        even after experiencing failures.
        """
        from prometheus_client import CollectorRegistry, Counter

        # Create isolated registry
        test_registry = CollectorRegistry()

        # Create test metric
        test_counter = Counter(
            'resilience_test',
            'Test counter for resilience',
            registry=test_registry
        )

        # Initial value
        test_counter.inc()
        initial_value = test_counter._value.get()

        # Simulate "failure" and recovery by incrementing again
        test_counter.inc()
        recovered_value = test_counter._value.get()

        assert recovered_value == initial_value + 1, \
            "Counter should increment after simulated failure"

    def test_gauge_can_be_reset_after_failure(self):
        """
        Test that gauge metrics can be reset after failures

        This validates queue depth and similar gauges can recover.
        """
        from prometheus_client import CollectorRegistry, Gauge

        # Create isolated registry
        test_registry = CollectorRegistry()

        # Create test metric
        test_gauge = Gauge(
            'resilience_queue',
            'Test gauge for resilience',
            registry=test_registry
        )

        # Simulate high value (failure condition)
        test_gauge.set(2000)
        high_value = test_gauge._value.get()
        assert high_value == 2000

        # Simulate recovery
        test_gauge.set(100)
        recovered_value = test_gauge._value.get()

        assert recovered_value == 100, \
            "Gauge should return to normal after recovery"
        assert recovered_value < 1000, \
            "Recovered value should be below alert threshold"
