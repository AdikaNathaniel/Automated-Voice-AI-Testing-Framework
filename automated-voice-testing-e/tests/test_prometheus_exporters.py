"""
Tests for Prometheus exporters configuration (Phase 4.2 Monitoring & Alerting).
"""

import os
import yaml
import pytest


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


class TestPostgresExporter:
    """Test PostgreSQL exporter configuration."""

    def test_postgres_exporter_service_exists(self, docker_compose_config):
        """Test that postgres-exporter service is defined."""
        services = docker_compose_config.get("services", {})
        assert "postgres-exporter" in services, \
            "postgres-exporter service must be in docker-compose"

    def test_postgres_exporter_image(self, docker_compose_config):
        """Test that postgres-exporter uses correct image."""
        exporter = docker_compose_config["services"]["postgres-exporter"]
        assert "image" in exporter
        assert "postgres-exporter" in exporter["image"] or "postgres_exporter" in exporter["image"]

    def test_postgres_exporter_port_exposed(self, docker_compose_config):
        """Test that postgres-exporter port is exposed."""
        exporter = docker_compose_config["services"]["postgres-exporter"]
        ports = exporter.get("ports", [])
        port_found = any("9187" in str(p) for p in ports)
        assert port_found, "Postgres exporter port 9187 must be exposed"

    def test_postgres_exporter_depends_on_postgres(self, docker_compose_config):
        """Test that postgres-exporter depends on postgres."""
        exporter = docker_compose_config["services"]["postgres-exporter"]
        depends = exporter.get("depends_on", [])
        if isinstance(depends, dict):
            depends = list(depends.keys())
        assert "postgres" in depends, "postgres-exporter must depend on postgres"

    def test_postgres_exporter_in_prometheus_config(self, prometheus_config):
        """Test that Prometheus scrapes postgres-exporter."""
        scrape_configs = prometheus_config.get("scrape_configs", [])
        job_names = [sc.get("job_name") for sc in scrape_configs]
        assert "postgres" in job_names, "Prometheus must scrape postgres exporter"


class TestRedisExporter:
    """Test Redis exporter configuration."""

    def test_redis_exporter_service_exists(self, docker_compose_config):
        """Test that redis-exporter service is defined."""
        services = docker_compose_config.get("services", {})
        assert "redis-exporter" in services, \
            "redis-exporter service must be in docker-compose"

    def test_redis_exporter_image(self, docker_compose_config):
        """Test that redis-exporter uses correct image."""
        exporter = docker_compose_config["services"]["redis-exporter"]
        assert "image" in exporter
        assert "redis-exporter" in exporter["image"] or "redis_exporter" in exporter["image"]

    def test_redis_exporter_port_exposed(self, docker_compose_config):
        """Test that redis-exporter port is exposed."""
        exporter = docker_compose_config["services"]["redis-exporter"]
        ports = exporter.get("ports", [])
        port_found = any("9121" in str(p) for p in ports)
        assert port_found, "Redis exporter port 9121 must be exposed"

    def test_redis_exporter_depends_on_redis(self, docker_compose_config):
        """Test that redis-exporter depends on redis."""
        exporter = docker_compose_config["services"]["redis-exporter"]
        depends = exporter.get("depends_on", [])
        if isinstance(depends, dict):
            depends = list(depends.keys())
        assert "redis" in depends, "redis-exporter must depend on redis"

    def test_redis_exporter_in_prometheus_config(self, prometheus_config):
        """Test that Prometheus scrapes redis-exporter."""
        scrape_configs = prometheus_config.get("scrape_configs", [])
        job_names = [sc.get("job_name") for sc in scrape_configs]
        assert "redis" in job_names, "Prometheus must scrape redis exporter"


class TestRabbitMQExporter:
    """Test RabbitMQ exporter configuration."""

    def test_rabbitmq_exporter_service_exists(self, docker_compose_config):
        """Test that rabbitmq-exporter service is defined."""
        services = docker_compose_config.get("services", {})
        assert "rabbitmq-exporter" in services, \
            "rabbitmq-exporter service must be in docker-compose"

    def test_rabbitmq_exporter_image(self, docker_compose_config):
        """Test that rabbitmq-exporter uses correct image."""
        exporter = docker_compose_config["services"]["rabbitmq-exporter"]
        assert "image" in exporter
        assert "rabbitmq" in exporter["image"].lower()

    def test_rabbitmq_exporter_port_exposed(self, docker_compose_config):
        """Test that rabbitmq-exporter port is exposed."""
        exporter = docker_compose_config["services"]["rabbitmq-exporter"]
        ports = exporter.get("ports", [])
        port_found = any("9419" in str(p) for p in ports)
        assert port_found, "RabbitMQ exporter port 9419 must be exposed"

    def test_rabbitmq_exporter_depends_on_rabbitmq(self, docker_compose_config):
        """Test that rabbitmq-exporter depends on rabbitmq."""
        exporter = docker_compose_config["services"]["rabbitmq-exporter"]
        depends = exporter.get("depends_on", [])
        if isinstance(depends, dict):
            depends = list(depends.keys())
        assert "rabbitmq" in depends, "rabbitmq-exporter must depend on rabbitmq"

    def test_rabbitmq_exporter_in_prometheus_config(self, prometheus_config):
        """Test that Prometheus scrapes rabbitmq-exporter."""
        scrape_configs = prometheus_config.get("scrape_configs", [])
        job_names = [sc.get("job_name") for sc in scrape_configs]
        assert "rabbitmq" in job_names, "Prometheus must scrape rabbitmq exporter"


class TestNginxExporter:
    """Test Nginx exporter configuration."""

    def test_nginx_exporter_service_exists(self, docker_compose_config):
        """Test that nginx-exporter service is defined."""
        services = docker_compose_config.get("services", {})
        assert "nginx-exporter" in services, \
            "nginx-exporter service must be in docker-compose"

    def test_nginx_exporter_image(self, docker_compose_config):
        """Test that nginx-exporter uses correct image."""
        exporter = docker_compose_config["services"]["nginx-exporter"]
        assert "image" in exporter
        assert "nginx" in exporter["image"].lower()

    def test_nginx_exporter_port_exposed(self, docker_compose_config):
        """Test that nginx-exporter port is exposed."""
        exporter = docker_compose_config["services"]["nginx-exporter"]
        ports = exporter.get("ports", [])
        port_found = any("9113" in str(p) for p in ports)
        assert port_found, "Nginx exporter port 9113 must be exposed"

    def test_nginx_exporter_depends_on_nginx(self, docker_compose_config):
        """Test that nginx-exporter depends on nginx."""
        exporter = docker_compose_config["services"]["nginx-exporter"]
        depends = exporter.get("depends_on", [])
        if isinstance(depends, dict):
            depends = list(depends.keys())
        assert "nginx" in depends, "nginx-exporter must depend on nginx"

    def test_nginx_exporter_in_prometheus_config(self, prometheus_config):
        """Test that Prometheus scrapes nginx-exporter."""
        scrape_configs = prometheus_config.get("scrape_configs", [])
        job_names = [sc.get("job_name") for sc in scrape_configs]
        assert "nginx" in job_names, "Prometheus must scrape nginx exporter"


class TestExportersNetwork:
    """Test that all exporters are on the same network."""

    def test_all_exporters_on_voiceai_network(self, docker_compose_config):
        """Test that all exporters are on voiceai-network."""
        exporters = [
            "postgres-exporter",
            "redis-exporter",
            "rabbitmq-exporter",
            "nginx-exporter"
        ]

        for exporter_name in exporters:
            if exporter_name in docker_compose_config.get("services", {}):
                exporter = docker_compose_config["services"][exporter_name]
                networks = exporter.get("networks", [])
                assert "voiceai-network" in networks, \
                    f"{exporter_name} must be on voiceai-network"
