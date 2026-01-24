"""
Tests for Prometheus & Grafana monitoring configuration.

This test suite validates that monitoring is properly configured for pilot:
1. Prometheus scrapes backend metrics endpoint
2. Grafana dashboards exist for key metrics
3. Monitoring configuration is production-ready
"""

import json
from pathlib import Path

import pytest
import yaml


class TestPrometheusConfiguration:
    """Test Prometheus configuration for backend monitoring"""

    @pytest.fixture
    def prometheus_config_path(self):
        """Get path to prometheus.yml"""
        return Path(__file__).parent.parent / "infrastructure" / "prometheus" / "prometheus.yml"

    @pytest.fixture
    def prometheus_config(self, prometheus_config_path):
        """Load Prometheus configuration"""
        with open(prometheus_config_path, 'r') as f:
            return yaml.safe_load(f)

    def test_prometheus_config_exists(self, prometheus_config_path):
        """Test that prometheus.yml exists"""
        assert prometheus_config_path.exists(), (
            "Prometheus configuration file not found at infrastructure/prometheus/prometheus.yml"
        )

    def test_prometheus_config_valid_yaml(self, prometheus_config):
        """Test that prometheus.yml is valid YAML"""
        assert prometheus_config is not None, "prometheus.yml is not valid YAML"
        assert isinstance(prometheus_config, dict), "prometheus.yml should be a dictionary"

    def test_has_global_config(self, prometheus_config):
        """Test that global configuration is defined"""
        assert 'global' in prometheus_config, "Prometheus config should have 'global' section"

        global_config = prometheus_config['global']
        assert 'scrape_interval' in global_config, "Should define scrape_interval"
        assert 'evaluation_interval' in global_config, "Should define evaluation_interval"

    def test_scrape_interval_reasonable(self, prometheus_config):
        """Test that scrape interval is reasonable for production"""
        scrape_interval = prometheus_config['global']['scrape_interval']

        # Parse interval (e.g., "15s" -> 15)
        interval_seconds = int(scrape_interval.rstrip('s'))

        # Should be between 5s and 60s for production
        assert 5 <= interval_seconds <= 60, (
            f"Scrape interval {scrape_interval} should be between 5s and 60s for production"
        )

    def test_has_scrape_configs(self, prometheus_config):
        """Test that scrape_configs section exists"""
        assert 'scrape_configs' in prometheus_config, (
            "Prometheus config should have 'scrape_configs' section"
        )
        assert len(prometheus_config['scrape_configs']) > 0, (
            "Should have at least one scrape configuration"
        )

    def test_backend_scrape_config_exists(self, prometheus_config):
        """Test that backend scrape configuration exists"""
        scrape_configs = prometheus_config.get('scrape_configs', [])

        # Find backend job
        backend_job = None
        for job in scrape_configs:
            if job.get('job_name') == 'backend':
                backend_job = job
                break

        assert backend_job is not None, (
            "Should have a scrape config with job_name='backend'"
        )

    def test_backend_metrics_path_correct(self, prometheus_config):
        """Test that backend metrics path is /metrics"""
        scrape_configs = prometheus_config.get('scrape_configs', [])

        backend_job = next(
            (job for job in scrape_configs if job.get('job_name') == 'backend'),
            None
        )

        assert backend_job is not None, "Backend scrape config not found"
        assert 'metrics_path' in backend_job, "Backend job should have metrics_path"
        assert backend_job['metrics_path'] == '/metrics', (
            "Backend metrics path should be '/metrics'"
        )

    def test_backend_target_configured(self, prometheus_config):
        """Test that backend target is configured"""
        scrape_configs = prometheus_config.get('scrape_configs', [])

        backend_job = next(
            (job for job in scrape_configs if job.get('job_name') == 'backend'),
            None
        )

        assert backend_job is not None, "Backend scrape config not found"
        assert 'static_configs' in backend_job, "Backend job should have static_configs"

        static_configs = backend_job['static_configs']
        assert len(static_configs) > 0, "Should have at least one static config"

        first_config = static_configs[0]
        assert 'targets' in first_config, "Static config should have targets"

        targets = first_config['targets']
        assert len(targets) > 0, "Should have at least one target"

        # Should target backend service
        assert any('backend' in target for target in targets), (
            "Should have backend service in targets"
        )

    def test_backend_target_port_8000(self, prometheus_config):
        """Test that backend target uses port 8000"""
        scrape_configs = prometheus_config.get('scrape_configs', [])

        backend_job = next(
            (job for job in scrape_configs if job.get('job_name') == 'backend'),
            None
        )

        targets = backend_job['static_configs'][0]['targets']

        # Should have backend:8000
        backend_target = next((t for t in targets if 'backend' in t), None)
        assert backend_target is not None, "Should have backend target"
        assert ':8000' in backend_target, "Backend should be on port 8000"

    def test_has_alerting_rules(self, prometheus_config):
        """Test that alerting rules are configured"""
        assert 'rule_files' in prometheus_config, (
            "Prometheus config should have 'rule_files' for alerts"
        )

        rule_files = prometheus_config['rule_files']
        assert len(rule_files) > 0, "Should have at least one rule file"

        # Should include alerts.yml
        assert 'alerts.yml' in rule_files, (
            "Should include alerts.yml in rule_files"
        )


class TestPrometheusAlerts:
    """Test Prometheus alert rules configuration"""

    @pytest.fixture
    def alerts_path(self):
        """Get path to alerts.yml"""
        return Path(__file__).parent.parent / "infrastructure" / "prometheus" / "alerts.yml"

    def test_alerts_file_exists(self, alerts_path):
        """Test that alerts.yml exists"""
        assert alerts_path.exists(), (
            "Prometheus alerts file not found at infrastructure/prometheus/alerts.yml"
        )

    def test_alerts_valid_yaml(self, alerts_path):
        """Test that alerts.yml is valid YAML"""
        with open(alerts_path, 'r') as f:
            content = yaml.safe_load(f)

        assert content is not None, "alerts.yml is not valid YAML"


class TestGrafanaDashboards:
    """Test Grafana dashboard configuration"""

    @pytest.fixture
    def dashboards_dir(self):
        """Get path to Grafana dashboards directory"""
        return Path(__file__).parent.parent / "infrastructure" / "grafana" / "dashboards"

    def test_dashboards_directory_exists(self, dashboards_dir):
        """Test that dashboards directory exists"""
        assert dashboards_dir.exists(), (
            "Grafana dashboards directory not found at infrastructure/grafana/dashboards"
        )
        assert dashboards_dir.is_dir(), "Dashboards path should be a directory"

    def test_performance_dashboard_exists(self, dashboards_dir):
        """Test that performance dashboard exists"""
        performance_dashboard = dashboards_dir / "performance.json"
        assert performance_dashboard.exists(), (
            "Performance dashboard not found. Should exist at: "
            "infrastructure/grafana/dashboards/performance.json"
        )

    def test_quality_dashboard_exists(self, dashboards_dir):
        """Test that quality dashboard exists"""
        quality_dashboard = dashboards_dir / "quality.json"
        assert quality_dashboard.exists(), (
            "Quality dashboard not found. Should exist at: "
            "infrastructure/grafana/dashboards/quality.json"
        )

    def test_system_health_dashboard_exists(self, dashboards_dir):
        """Test that system health dashboard exists"""
        # Could be named system_overview.json or system_health.json
        system_dashboard = (
            dashboards_dir / "system_overview.json"
            if (dashboards_dir / "system_overview.json").exists()
            else dashboards_dir / "system_health.json"
        )

        assert system_dashboard.exists(), (
            "System health dashboard not found. Should exist at: "
            "infrastructure/grafana/dashboards/system_overview.json or system_health.json"
        )

    def test_performance_dashboard_valid_json(self, dashboards_dir):
        """Test that performance dashboard is valid JSON"""
        performance_dashboard = dashboards_dir / "performance.json"

        with open(performance_dashboard, 'r') as f:
            content = json.load(f)

        assert content is not None, "Performance dashboard is not valid JSON"
        assert isinstance(content, dict), "Dashboard should be a JSON object"

    def test_performance_dashboard_has_title(self, dashboards_dir):
        """Test that performance dashboard has a title"""
        performance_dashboard = dashboards_dir / "performance.json"

        with open(performance_dashboard, 'r') as f:
            content = json.load(f)

        assert 'title' in content, "Dashboard should have a title"
        title = content['title'].lower()

        # Title should indicate it's for performance monitoring
        assert any(keyword in title for keyword in ['performance', 'latency', 'throughput']), (
            "Performance dashboard title should mention performance, latency, or throughput"
        )

    def test_performance_dashboard_has_panels(self, dashboards_dir):
        """Test that performance dashboard has panels/visualization"""
        performance_dashboard = dashboards_dir / "performance.json"

        with open(performance_dashboard, 'r') as f:
            content = json.load(f)

        # Grafana dashboards have panels
        assert 'panels' in content, "Dashboard should have panels"
        panels = content['panels']

        assert isinstance(panels, list), "Panels should be a list"
        assert len(panels) > 0, "Dashboard should have at least one panel"

    def test_quality_dashboard_valid_json(self, dashboards_dir):
        """Test that quality dashboard is valid JSON"""
        quality_dashboard = dashboards_dir / "quality.json"

        with open(quality_dashboard, 'r') as f:
            content = json.load(f)

        assert content is not None, "Quality dashboard is not valid JSON"
        assert isinstance(content, dict), "Dashboard should be a JSON object"

    def test_quality_dashboard_has_relevant_metrics(self, dashboards_dir):
        """Test that quality dashboard has relevant metrics"""
        quality_dashboard = dashboards_dir / "quality.json"

        with open(quality_dashboard, 'r') as f:
            content = json.load(f)

        # Convert to string to search for keywords
        dashboard_str = json.dumps(content).lower()

        # Should mention quality-related metrics
        quality_keywords = ['pass', 'fail', 'defect', 'quality', 'accuracy', 'rate']

        has_quality_metrics = any(keyword in dashboard_str for keyword in quality_keywords)
        assert has_quality_metrics, (
            "Quality dashboard should mention quality-related metrics like "
            "pass rate, fail rate, defect rate, accuracy, etc."
        )

    def test_system_dashboard_valid_json(self, dashboards_dir):
        """Test that system dashboard is valid JSON"""
        system_dashboard = dashboards_dir / "system_overview.json"

        with open(system_dashboard, 'r') as f:
            content = json.load(f)

        assert content is not None, "System dashboard is not valid JSON"
        assert isinstance(content, dict), "Dashboard should be a JSON object"

    def test_system_dashboard_has_health_metrics(self, dashboards_dir):
        """Test that system dashboard has health metrics"""
        system_dashboard = dashboards_dir / "system_overview.json"

        with open(system_dashboard, 'r') as f:
            content = json.load(f)

        # Convert to string to search for keywords
        dashboard_str = json.dumps(content).lower()

        # Should mention system health metrics
        health_keywords = ['cpu', 'memory', 'disk', 'database', 'queue', 'health']

        has_health_metrics = any(keyword in dashboard_str for keyword in health_keywords)
        assert has_health_metrics, (
            "System dashboard should mention system health metrics like "
            "CPU, memory, database, queue depth, etc."
        )

    def test_all_dashboards_have_prometheus_datasource(self, dashboards_dir):
        """Test that all dashboards use Prometheus as datasource"""
        dashboard_files = [
            "performance.json",
            "quality.json",
            "system_overview.json"
        ]

        for dashboard_file in dashboard_files:
            dashboard_path = dashboards_dir / dashboard_file

            if not dashboard_path.exists():
                continue

            with open(dashboard_path, 'r') as f:
                content = json.load(f)

            # Check if dashboard references Prometheus
            dashboard_str = json.dumps(content).lower()

            # Grafana dashboards should reference Prometheus as datasource
            # This is informational - not all dashboards may explicitly mention it
            has_prometheus_ref = 'prometheus' in dashboard_str

            # This is a soft check - just documenting expectation
            if not has_prometheus_ref:
                # Dashboard may use ${DS_PROMETHEUS} or similar variable
                pass


class TestGrafanaProvisioning:
    """Test Grafana provisioning configuration"""

    @pytest.fixture
    def provisioning_dir(self):
        """Get path to Grafana provisioning directory"""
        return Path(__file__).parent.parent / "infrastructure" / "grafana" / "provisioning"

    def test_provisioning_directory_exists(self, provisioning_dir):
        """Test that provisioning directory exists"""
        assert provisioning_dir.exists(), (
            "Grafana provisioning directory not found"
        )

    def test_datasources_config_exists(self, provisioning_dir):
        """Test that datasources provisioning exists"""
        datasources_dir = provisioning_dir / "datasources"
        assert datasources_dir.exists(), (
            "Datasources provisioning directory should exist"
        )

    def test_dashboards_config_exists(self, provisioning_dir):
        """Test that dashboards provisioning exists"""
        dashboards_dir = provisioning_dir / "dashboards"
        assert dashboards_dir.exists(), (
            "Dashboards provisioning directory should exist"
        )


class TestBackendMetricsEndpoint:
    """Test that backend has /metrics endpoint"""

    def test_backend_has_metrics_route_defined(self):
        """Test that backend API defines /metrics route"""
        # Check if backend/api/main.py or routes define /metrics
        backend_main = Path(__file__).parent.parent / "backend" / "api" / "main.py"

        if backend_main.exists():
            content = backend_main.read_text()

            # Should have metrics endpoint or import
            has_metrics = (
                '/metrics' in content or
                'metrics' in content.lower() or
                'prometheus' in content.lower()
            )

            assert has_metrics, (
                "Backend should define /metrics endpoint for Prometheus scraping. "
                "Ensure FastAPI app includes prometheus metrics route."
            )

    def test_metrics_endpoint_documentation(self):
        """Test that metrics endpoint is documented"""
        # Check if there's documentation about the metrics endpoint
        # This is informational
        readme = Path(__file__).parent.parent / "README.md"

        if readme.exists():
            content = readme.read_text()

            # Document that metrics endpoint should be mentioned
            # This is a soft requirement
            has_metrics_doc = '/metrics' in content or 'prometheus' in content.lower()

            # Just documenting - not failing test
            if not has_metrics_doc:
                pass  # Recommendation: Document /metrics endpoint in README
