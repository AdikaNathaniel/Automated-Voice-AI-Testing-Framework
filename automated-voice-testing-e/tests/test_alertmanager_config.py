"""
Tests for Alertmanager configuration (Phase 4.2 Monitoring & Alerting).
"""

import os
import yaml
import pytest


@pytest.fixture
def alertmanager_config_path():
    """Get path to Alertmanager configuration file."""
    project_root = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(project_root, "infrastructure", "alertmanager", "alertmanager.yml")


@pytest.fixture
def alertmanager_config(alertmanager_config_path):
    """Load and parse Alertmanager configuration."""
    with open(alertmanager_config_path) as f:
        return yaml.safe_load(f)


@pytest.fixture
def docker_compose_path():
    """Get path to docker-compose.yml."""
    project_root = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(project_root, "docker-compose.yml")


@pytest.fixture
def docker_compose_config(docker_compose_path):
    """Load and parse docker-compose.yml."""
    with open(docker_compose_path) as f:
        return yaml.safe_load(f)


@pytest.fixture
def prometheus_config_path():
    """Get path to Prometheus configuration file."""
    project_root = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(project_root, "infrastructure", "prometheus", "prometheus.yml")


@pytest.fixture
def prometheus_config(prometheus_config_path):
    """Load and parse Prometheus configuration."""
    with open(prometheus_config_path) as f:
        return yaml.safe_load(f)


class TestAlertmanagerConfigExists:
    """Test that Alertmanager configuration file exists."""

    def test_alertmanager_config_file_exists(self, alertmanager_config_path):
        """Test that alertmanager.yml exists."""
        assert os.path.exists(alertmanager_config_path), \
            f"Alertmanager config not found at {alertmanager_config_path}"

    def test_alertmanager_config_is_valid_yaml(self, alertmanager_config):
        """Test that alertmanager.yml is valid YAML."""
        assert alertmanager_config is not None
        assert isinstance(alertmanager_config, dict)


class TestAlertmanagerGlobalConfig:
    """Test Alertmanager global configuration."""

    def test_global_section_exists(self, alertmanager_config):
        """Test that global section exists."""
        assert "global" in alertmanager_config

    def test_smtp_config_exists(self, alertmanager_config):
        """Test that SMTP configuration exists for email notifications."""
        global_config = alertmanager_config.get("global", {})
        # SMTP should be configured (can use env vars)
        assert "smtp_smarthost" in global_config or "smtp_from" in global_config

    def test_resolve_timeout_configured(self, alertmanager_config):
        """Test that resolve timeout is configured."""
        global_config = alertmanager_config.get("global", {})
        assert "resolve_timeout" in global_config


class TestAlertmanagerRouting:
    """Test Alertmanager routing configuration."""

    def test_route_section_exists(self, alertmanager_config):
        """Test that route section exists."""
        assert "route" in alertmanager_config

    def test_default_receiver_configured(self, alertmanager_config):
        """Test that default receiver is configured."""
        route = alertmanager_config.get("route", {})
        assert "receiver" in route, "Default receiver must be configured"

    def test_group_by_configured(self, alertmanager_config):
        """Test that group_by is configured for alert grouping."""
        route = alertmanager_config.get("route", {})
        assert "group_by" in route

    def test_group_wait_configured(self, alertmanager_config):
        """Test that group_wait is configured."""
        route = alertmanager_config.get("route", {})
        assert "group_wait" in route

    def test_repeat_interval_configured(self, alertmanager_config):
        """Test that repeat_interval is configured."""
        route = alertmanager_config.get("route", {})
        assert "repeat_interval" in route

    def test_critical_alerts_route_exists(self, alertmanager_config):
        """Test that critical alerts have specific routing."""
        route = alertmanager_config.get("route", {})
        routes = route.get("routes", [])

        # Check for critical severity route
        critical_route = None
        for r in routes:
            match = r.get("match", {}) or r.get("match_re", {})
            if "severity" in match:
                if match.get("severity") == "critical":
                    critical_route = r
                    break

        assert critical_route is not None, "Critical alerts should have specific routing"


class TestAlertmanagerReceivers:
    """Test Alertmanager receiver configuration."""

    def test_receivers_section_exists(self, alertmanager_config):
        """Test that receivers section exists."""
        assert "receivers" in alertmanager_config

    def test_at_least_one_receiver_configured(self, alertmanager_config):
        """Test that at least one receiver is configured."""
        receivers = alertmanager_config.get("receivers", [])
        assert len(receivers) > 0, "At least one receiver must be configured"

    def test_default_receiver_exists(self, alertmanager_config):
        """Test that the default receiver exists in receivers list."""
        route = alertmanager_config.get("route", {})
        default_receiver = route.get("receiver")
        receivers = alertmanager_config.get("receivers", [])

        receiver_names = [r.get("name") for r in receivers]
        assert default_receiver in receiver_names, \
            f"Default receiver '{default_receiver}' must exist in receivers"

    def test_slack_receiver_configured(self, alertmanager_config):
        """Test that Slack receiver is configured."""
        receivers = alertmanager_config.get("receivers", [])

        slack_configured = False
        for receiver in receivers:
            if "slack_configs" in receiver:
                slack_configured = True
                break

        assert slack_configured, "Slack notification channel should be configured"

    def test_email_receiver_configured(self, alertmanager_config):
        """Test that email receiver is configured."""
        receivers = alertmanager_config.get("receivers", [])

        email_configured = False
        for receiver in receivers:
            if "email_configs" in receiver:
                email_configured = True
                break

        assert email_configured, "Email notification channel should be configured"


class TestAlertmanagerInhibitRules:
    """Test Alertmanager inhibit rules configuration."""

    def test_inhibit_rules_section_exists(self, alertmanager_config):
        """Test that inhibit_rules section exists."""
        assert "inhibit_rules" in alertmanager_config

    def test_critical_inhibits_warning(self, alertmanager_config):
        """Test that critical alerts inhibit warnings for same alertname."""
        inhibit_rules = alertmanager_config.get("inhibit_rules", [])

        critical_inhibit = False
        for rule in inhibit_rules:
            source = rule.get("source_match", {}) or rule.get("source_matchers", [])
            target = rule.get("target_match", {}) or rule.get("target_matchers", [])

            # Check for critical->warning inhibition
            if isinstance(source, dict) and source.get("severity") == "critical":
                if isinstance(target, dict) and target.get("severity") == "warning":
                    critical_inhibit = True
                    break
            elif isinstance(source, list) and any("critical" in str(s) for s in source):
                if isinstance(target, list) and any("warning" in str(t) for t in target):
                    critical_inhibit = True
                    break

        assert critical_inhibit, "Critical alerts should inhibit warnings"


class TestDockerComposeAlertmanager:
    """Test Alertmanager service in docker-compose."""

    def test_alertmanager_service_exists(self, docker_compose_config):
        """Test that alertmanager service is defined."""
        services = docker_compose_config.get("services", {})
        assert "alertmanager" in services, "Alertmanager service must be in docker-compose"

    def test_alertmanager_image_configured(self, docker_compose_config):
        """Test that alertmanager uses official image."""
        alertmanager = docker_compose_config["services"]["alertmanager"]
        assert "image" in alertmanager
        assert "prom/alertmanager" in alertmanager["image"]

    def test_alertmanager_config_volume_mounted(self, docker_compose_config):
        """Test that alertmanager config is mounted as volume."""
        alertmanager = docker_compose_config["services"]["alertmanager"]
        volumes = alertmanager.get("volumes", [])

        config_mounted = False
        for vol in volumes:
            if "alertmanager.yml" in vol:
                config_mounted = True
                break

        assert config_mounted, "Alertmanager config must be mounted"

    def test_alertmanager_port_exposed(self, docker_compose_config):
        """Test that alertmanager port is exposed."""
        alertmanager = docker_compose_config["services"]["alertmanager"]
        ports = alertmanager.get("ports", [])

        port_exposed = False
        for port in ports:
            if "9093" in str(port):
                port_exposed = True
                break

        assert port_exposed, "Alertmanager port 9093 must be exposed"

    def test_alertmanager_network_configured(self, docker_compose_config):
        """Test that alertmanager is on the same network."""
        alertmanager = docker_compose_config["services"]["alertmanager"]
        networks = alertmanager.get("networks", [])
        assert "voiceai-network" in networks

    def test_alertmanager_healthcheck_configured(self, docker_compose_config):
        """Test that alertmanager has healthcheck."""
        alertmanager = docker_compose_config["services"]["alertmanager"]
        assert "healthcheck" in alertmanager


class TestPrometheusAlertmanagerIntegration:
    """Test Prometheus integration with Alertmanager."""

    def test_alerting_section_exists(self, prometheus_config):
        """Test that alerting section exists in Prometheus config."""
        assert "alerting" in prometheus_config, \
            "Prometheus must have alerting section for Alertmanager integration"

    def test_alertmanagers_configured(self, prometheus_config):
        """Test that alertmanagers are configured."""
        alerting = prometheus_config.get("alerting", {})
        assert "alertmanagers" in alerting

    def test_alertmanager_target_configured(self, prometheus_config):
        """Test that Alertmanager target is configured."""
        alerting = prometheus_config.get("alerting", {})
        alertmanagers = alerting.get("alertmanagers", [])

        assert len(alertmanagers) > 0, "At least one alertmanager must be configured"

        targets_found = False
        for am in alertmanagers:
            static_configs = am.get("static_configs", [])
            for config in static_configs:
                targets = config.get("targets", [])
                if any("alertmanager" in t or "9093" in t for t in targets):
                    targets_found = True
                    break

        assert targets_found, "Alertmanager target must be configured in Prometheus"


class TestAlertmanagerTemplates:
    """Test Alertmanager template configuration."""

    def test_templates_directory_exists(self):
        """Test that templates directory exists."""
        project_root = os.path.dirname(os.path.dirname(__file__))
        templates_dir = os.path.join(project_root, "infrastructure", "alertmanager", "templates")

        # Templates are optional but recommended
        if os.path.exists(templates_dir):
            assert os.path.isdir(templates_dir)
