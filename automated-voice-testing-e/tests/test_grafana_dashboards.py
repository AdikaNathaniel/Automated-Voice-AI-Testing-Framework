"""
Validate Grafana dashboard provisioning for the system overview dashboard.
"""

from __future__ import annotations

import json
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
def dashboards_provisioning_path(project_root: Path) -> Path:
    return project_root / "infrastructure" / "grafana" / "provisioning" / "dashboards" / "system_overview.yml"


@pytest.fixture(scope="module")
def dashboards_provisioning(dashboards_provisioning_path: Path) -> Dict[str, Any]:
    with dashboards_provisioning_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


@pytest.fixture(scope="module")
def system_overview_dashboard_path(project_root: Path) -> Path:
    return project_root / "infrastructure" / "grafana" / "dashboards" / "system_overview.json"


@pytest.fixture(scope="module")
def system_overview_dashboard(system_overview_dashboard_path: Path) -> Dict[str, Any]:
    with system_overview_dashboard_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@pytest.fixture(scope="module")
def performance_dashboard_path(project_root: Path) -> Path:
    return project_root / "infrastructure" / "grafana" / "dashboards" / "performance.json"


@pytest.fixture(scope="module")
def performance_dashboard(performance_dashboard_path: Path) -> Dict[str, Any]:
    with performance_dashboard_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@pytest.fixture(scope="module")
def quality_dashboard_path(project_root: Path) -> Path:
    return project_root / "infrastructure" / "grafana" / "dashboards" / "quality.json"


@pytest.fixture(scope="module")
def quality_dashboard(quality_dashboard_path: Path) -> Dict[str, Any]:
    with quality_dashboard_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_grafana_mounts_dashboards(docker_compose_data: Dict[str, Any]) -> None:
    grafana_service = docker_compose_data["services"]["grafana"]

    volumes: List[str] = grafana_service.get("volumes", [])
    assert any(
        volume.startswith("./infrastructure/grafana/provisioning/dashboards")
        for volume in volumes
    ), "Grafana service must mount dashboards provisioning directory"
    assert any(
        volume.startswith("./infrastructure/grafana/dashboards")
        for volume in volumes
    ), "Grafana service must mount dashboards JSON directory"


def test_dashboards_provisioning_exists(dashboards_provisioning_path: Path) -> None:
    assert dashboards_provisioning_path.exists(), "Grafana dashboards provisioning config must exist"


def test_dashboards_provisioning_targets_system_overview(dashboards_provisioning: Dict[str, Any]) -> None:
    assert dashboards_provisioning.get("apiVersion") == 1, "Dashboards provisioning config must declare apiVersion 1"

    providers = dashboards_provisioning.get("providers", [])
    assert providers, "Dashboards provisioning config must declare providers"

    system_provider = next(
        (provider for provider in providers if provider.get("name") == "system-overview"),
        None,
    )
    assert system_provider is not None, "Dashboards provisioning must include system-overview provider"
    options = system_provider.get("options", {})
    assert options.get("path") == "/var/lib/grafana/dashboards", "system-overview provider must reference dashboards directory"


def test_system_overview_dashboard_exists(system_overview_dashboard_path: Path) -> None:
    assert system_overview_dashboard_path.exists(), "System overview dashboard JSON must exist"


def test_system_overview_dashboard_panels(system_overview_dashboard: Dict[str, Any]) -> None:
    assert system_overview_dashboard.get("title") == "System Overview", "Dashboard title must be 'System Overview'"

    panels = system_overview_dashboard.get("panels", [])
    assert len(panels) >= 4, "System overview dashboard must include at least four panels"

    expected_titles = {
        "Test Throughput",
        "Success Rate",
        "Active Workers",
        "Queue Depth",
    }
    panel_titles = {panel.get("title") for panel in panels}
    missing = expected_titles - panel_titles
    assert not missing, f"System overview dashboard missing panels: {', '.join(sorted(missing))}"


def test_performance_dashboard_exists(performance_dashboard_path: Path) -> None:
    assert performance_dashboard_path.exists(), "Performance dashboard JSON must exist"


def test_performance_dashboard_panels(performance_dashboard: Dict[str, Any]) -> None:
    assert performance_dashboard.get("title") == "Performance Overview", "Performance dashboard title must be 'Performance Overview'"

    panels = performance_dashboard.get("panels", [])
    assert len(panels) >= 3, "Performance dashboard must include at least three panels"

    expected_titles = {
        "Response Time Percentiles",
        "Execution Duration Distribution",
        "API Latency",
    }
    panel_titles = {panel.get("title") for panel in panels}
    missing = expected_titles - panel_titles
    assert not missing, f"Performance dashboard missing panels: {', '.join(sorted(missing))}"


def test_quality_dashboard_exists(quality_dashboard_path: Path) -> None:
    assert quality_dashboard_path.exists(), "Quality dashboard JSON must exist"


def test_quality_dashboard_panels(quality_dashboard: Dict[str, Any]) -> None:
    assert quality_dashboard.get("title") == "Quality Overview", "Quality dashboard title must be 'Quality Overview'"

    panels = quality_dashboard.get("panels", [])
    assert len(panels) >= 3, "Quality dashboard must include at least three panels"

    expected_titles = {
        "Validation Confidence Distribution",
        "Human Validation Rate",
        "Accuracy Metrics",
    }
    panel_titles = {panel.get("title") for panel in panels}
    missing = expected_titles - panel_titles
    assert not missing, f"Quality dashboard missing panels: {', '.join(sorted(missing))}"


@pytest.fixture(scope="module")
def infrastructure_dashboard_path(project_root: Path) -> Path:
    return project_root / "infrastructure" / "grafana" / "dashboards" / "infrastructure.json"


@pytest.fixture(scope="module")
def infrastructure_dashboard(infrastructure_dashboard_path: Path) -> Dict[str, Any]:
    with infrastructure_dashboard_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_infrastructure_dashboard_exists(infrastructure_dashboard_path: Path) -> None:
    assert infrastructure_dashboard_path.exists(), "Infrastructure dashboard JSON must exist"


def test_infrastructure_dashboard_panels(infrastructure_dashboard: Dict[str, Any]) -> None:
    assert infrastructure_dashboard.get("title") == "Infrastructure Overview", \
        "Infrastructure dashboard title must be 'Infrastructure Overview'"

    panels = infrastructure_dashboard.get("panels", [])
    assert len(panels) >= 6, "Infrastructure dashboard must include at least six panels"

    expected_titles = {
        "PostgreSQL Connections",
        "Redis Memory Usage",
        "RabbitMQ Queue Depth",
        "Nginx Request Rate",
        "Database Query Time",
        "Cache Hit Rate",
    }
    panel_titles = {panel.get("title") for panel in panels}
    missing = expected_titles - panel_titles
    assert not missing, f"Infrastructure dashboard missing panels: {', '.join(sorted(missing))}"
