"""
Dashboard API endpoint tests.

Validates the aggregated dashboard snapshot endpoint and query parameter handling.
"""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import os
import pytest
from fastapi.testclient import TestClient

# Minimal configuration so FastAPI app imports succeed during tests
os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/testdb")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("JWT_SECRET_KEY", "supersecretkey1234")
os.environ.setdefault("SOUNDHOUND_API_KEY", "test-key")
os.environ.setdefault("SOUNDHOUND_CLIENT_ID", "test-client")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test-access")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test-secret")

from api.main import app
from api.database import get_db
from api.dependencies import get_current_user_with_db
from services import dashboard_service


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def override_dependencies():
    fake_user = SimpleNamespace(id=uuid4(), email="user@example.com", is_active=True, role="admin", tenant_id=None)

    app.dependency_overrides[get_current_user_with_db] = lambda: fake_user

    async def fake_db():
        yield None

    app.dependency_overrides[get_db] = fake_db

    yield

    app.dependency_overrides.clear()


def _dashboard_snapshot():
    return {
        "kpis": {
            "tests_executed": 1280,
            "system_health_pct": 98.7,
            "issues_detected": 12,
            "avg_response_time_ms": 1180.5,
        },
        "real_time_execution": {
            "current_run_id": str(uuid4()),
            "progress_pct": 72.4,
            "tests_passed": 820,
            "tests_failed": 37,
            "under_review": 48,
            "queued": 212,
        },
        "validation_accuracy": {
            "overall_accuracy_pct": 99.6,
            "total_validations": 9340,
            "human_reviews": 384,
            "time_saved_hours": 812.5,
        },
        "language_coverage": [
            {"language_code": "en-US", "test_cases": 420, "pass_rate_pct": 99.1},
            {"language_code": "es-ES", "test_cases": 310, "pass_rate_pct": 97.8},
        ],
        "defects": {
            "open": 14,
            "critical": 2,
            "high": 5,
            "medium": 4,
            "low": 3,
        },
        "defects_trend": [
            {"date": "2025-11-19T00:00:00Z", "open": 15},
            {"date": "2025-11-20T00:00:00Z", "open": 14},
        ],
        "test_coverage": [
            {"area": "intents", "coverage_pct": 95.0, "automated_pct": 90.0},
            {"area": "entities", "coverage_pct": 88.0, "automated_pct": 85.0},
        ],
        "cicd_status": {
            "pipelines": [
                {"id": "pipeline-1", "name": "Main Pipeline", "status": "success", "last_run_at": "2025-11-20T05:00:00Z"},
            ],
            "incidents": 0,
        },
        "edge_cases": {
            "total": 150,
            "resolved": 120,
            "categories": [
                {"category": "ambiguous_input", "count": 45},
                {"category": "noise_handling", "count": 35},
            ],
        },
        "pass_rate_trend": [],
        "regressions": {
            "total": 0,
            "recent": [],
        },
        "validation_accuracy_trend": [],
        "updated_at": datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def test_dashboard_endpoint_returns_snapshot(client: TestClient, monkeypatch):
    expected = _dashboard_snapshot()
    mock_snapshot = AsyncMock(return_value=expected)
    monkeypatch.setattr(
        dashboard_service,
        "get_dashboard_snapshot",
        mock_snapshot,
    )

    response = client.get("/api/v1/reports/dashboard?time_range=7d")

    assert response.status_code == 200
    assert response.json() == expected
    mock_snapshot.assert_awaited_once()
    kwargs = mock_snapshot.await_args.kwargs
    assert kwargs["time_range"] == "7d"


def test_dashboard_endpoint_defaults_to_24h(client: TestClient, monkeypatch):
    expected = _dashboard_snapshot()
    mock_snapshot = AsyncMock(return_value=expected)
    monkeypatch.setattr(
        dashboard_service,
        "get_dashboard_snapshot",
        mock_snapshot,
    )

    response = client.get("/api/v1/reports/dashboard")

    assert response.status_code == 200
    mock_snapshot.assert_awaited_once()
    assert mock_snapshot.await_args.kwargs["time_range"] == "24h"


def test_dashboard_endpoint_rejects_invalid_range(client: TestClient):
    response = client.get("/api/v1/reports/dashboard?time_range=12h")

    assert response.status_code == 422
