"""
Ensure docker-compose integrates Prometheus correctly for metrics scraping.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import pytest
import yaml


@pytest.fixture(scope="module")
def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def docker_compose_path(project_root: Path) -> Path:
    return project_root / "docker-compose.yml"


@pytest.fixture(scope="module")
def docker_compose_data(docker_compose_path: Path) -> Dict[str, Any]:
    with docker_compose_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


@pytest.fixture(scope="module")
def prometheus_config_path(project_root: Path) -> Path:
    return project_root / "infrastructure" / "prometheus" / "prometheus.yml"


@pytest.fixture(scope="module")
def prometheus_config(prometheus_config_path: Path) -> Dict[str, Any]:
    with prometheus_config_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def test_prometheus_service_exists(docker_compose_data: Dict[str, Any]) -> None:
    services = docker_compose_data.get("services", {})
    assert "prometheus" in services, "docker-compose.yml must define a prometheus service"


def test_prometheus_service_configuration(docker_compose_data: Dict[str, Any]) -> None:
    service = docker_compose_data["services"]["prometheus"]

    image = service.get("image", "")
    assert "prom/prometheus" in image, "Prometheus service should use official prom/prometheus image"

    ports: List[str] = service.get("ports", [])
    assert any("9090" in port for port in ports), "Prometheus must expose port 9090"

    volumes: List[str] = service.get("volumes", [])
    assert any(
        volume.startswith("./infrastructure/prometheus/prometheus.yml")
        for volume in volumes
    ), "Prometheus service must mount prometheus.yml configuration file"
    assert any(
        volume.startswith("./infrastructure/prometheus/alerts.yml")
        for volume in volumes
    ), "Prometheus service must mount alerts.yml rules file"
    assert any(
        volume.endswith("/prometheus")
        for volume in volumes
    ), "Prometheus service should persist TSDB data to a volume"

    command = " ".join(service.get("command", []) if isinstance(service.get("command"), list) else [service.get("command", "")]).strip()
    assert "--config.file=/etc/prometheus/prometheus.yml" in command, "Prometheus command must reference custom config file"
    assert "--storage.tsdb.path=/prometheus" in command, "Prometheus command must point storage to mounted volume"

    depends_on = service.get("depends_on", [])
    if isinstance(depends_on, dict):
        depends_on = list(depends_on.keys())
    assert "backend" in depends_on, "Prometheus should depend on backend so metrics endpoint is up"


def test_prometheus_volume_declared(docker_compose_data: Dict[str, Any]) -> None:
    volumes = docker_compose_data.get("volumes", {})
    assert "prometheus_data" in volumes, "docker-compose.yml must declare prometheus_data volume"


def test_prometheus_config_file_exists(prometheus_config_path: Path) -> None:
    assert prometheus_config_path.exists(), "Prometheus configuration file must exist"


def test_prometheus_scrape_backend(prometheus_config: Dict[str, Any]) -> None:
    scrape_configs = prometheus_config.get("scrape_configs", [])
    backend_job = next(
        (job for job in scrape_configs if job.get("job_name") == "backend"), None
    )
    assert backend_job is not None, "Prometheus config must define backend scrape job"
    assert backend_job.get("metrics_path") == "/metrics", "backend job must target /metrics path"

    static_configs = backend_job.get("static_configs", [])
    targets = [target for config in static_configs for target in config.get("targets", [])]
    assert "backend:8000" in targets, "backend job targets must include backend:8000"
