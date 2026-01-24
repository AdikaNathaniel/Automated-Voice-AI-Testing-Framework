"""
Ensure docker-compose integrates Grafana with Prometheus datasource provisioning.
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
def grafana_datasource_path(project_root: Path) -> Path:
    return project_root / "infrastructure" / "grafana" / "provisioning" / "datasources" / "prometheus.yml"


@pytest.fixture(scope="module")
def grafana_datasource_config(grafana_datasource_path: Path) -> Dict[str, Any]:
    with grafana_datasource_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def test_grafana_service_exists(docker_compose_data: Dict[str, Any]) -> None:
    services = docker_compose_data.get("services", {})
    assert "grafana" in services, "docker-compose.yml must define a grafana service"


def test_grafana_service_configuration(docker_compose_data: Dict[str, Any]) -> None:
    service = docker_compose_data["services"]["grafana"]

    image = service.get("image", "")
    assert "grafana/grafana" in image, "Grafana service should use official grafana/grafana image"

    ports: List[str] = service.get("ports", [])
    assert any("3000" in port for port in ports), "Grafana must expose port 3000"

    volumes: List[str] = service.get("volumes", [])
    assert any(
        volume.startswith("./infrastructure/grafana/provisioning/datasources")
        for volume in volumes
    ), "Grafana service must mount provisioned datasources directory"
    assert any(
        volume.endswith("/var/lib/grafana")
        for volume in volumes
    ), "Grafana service should persist state to grafana data directory"

    depends_on = service.get("depends_on", [])
    if isinstance(depends_on, dict):
        depends_on = list(depends_on.keys())
    assert "prometheus" in depends_on, "Grafana should depend on Prometheus so datasource is reachable"


def test_grafana_volume_declared(docker_compose_data: Dict[str, Any]) -> None:
    volumes = docker_compose_data.get("volumes", {})
    assert "grafana_data" in volumes, "docker-compose.yml must declare grafana_data volume for persistence"


def test_grafana_datasource_file_exists(grafana_datasource_path: Path) -> None:
    assert grafana_datasource_path.exists(), "Grafana Prometheus datasource config must exist"


def test_grafana_datasource_configuration(grafana_datasource_config: Dict[str, Any]) -> None:
    assert grafana_datasource_config.get("apiVersion") == 1, "Grafana datasource config must set apiVersion to 1"

    datasources = grafana_datasource_config.get("datasources", [])
    assert datasources, "Grafana datasource config must define at least one datasource"

    prometheus_ds = next(
        (item for item in datasources if item.get("name") == "Prometheus"),
        None,
    )
    assert prometheus_ds is not None, "Grafana datasource config must include Prometheus datasource named 'Prometheus'"

    assert prometheus_ds.get("type") == "prometheus", "Prometheus datasource must be of type 'prometheus'"
    assert prometheus_ds.get("url") == "http://prometheus:9090", "Prometheus datasource must target prometheus service URL"
    assert prometheus_ds.get("access") == "proxy", "Prometheus datasource should use proxy access"
    assert prometheus_ds.get("isDefault") is True, "Prometheus datasource should be default"
