"""
Regression API endpoint tests (TASK-338).

Validates the HTTP contract for listing detected regressions and approving
baselines through the `/api/v1/regressions` routes.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Generator
from uuid import uuid4
import os
import sys

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

# Ensure environment variables required for app import
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


@pytest.fixture(autouse=True)
def ensure_regression_service_module() -> Generator[None, None, None]:
    """
    Provide a stub regression_service module so tests can patch attributes
    before the implementation exists.
    """
    module_name = "services.regression_service"
    if module_name not in sys.modules:
        sys.modules[module_name] = SimpleNamespace()
    yield


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def override_dependencies(monkeypatch: pytest.MonkeyPatch):
    fake_user = SimpleNamespace(id=uuid4(), email="qa@example.com", is_active=True, role="admin", tenant_id=None)
    app.dependency_overrides[get_current_user_with_db] = lambda: fake_user

    async def fake_db():
        yield None

    app.dependency_overrides[get_db] = fake_db

    async def fake_get_redis():
        class _FakeRedis:
            async def close(self) -> None:  # pragma: no cover - simple stub
                return None

        yield _FakeRedis()

    for target in (
        "api.redis_client.get_redis",
        "api.rate_limit.get_redis",
    ):
        monkeypatch.setattr(
            target,
            lambda: fake_get_redis(),
            raising=False,
        )

    async def fake_enforce_rate_limit(_request):
        return None

    monkeypatch.setattr(
        "api.main.enforce_rate_limit",
        fake_enforce_rate_limit,
        raising=False,
    )

    yield

    app.dependency_overrides.clear()


def test_list_regressions_returns_report(client, monkeypatch):
    module = sys.modules["services.regression_service"]

    script_id = uuid4()
    expected_payload = {
        "summary": {
            "total_regressions": 1,
            "status_regressions": 1,
            "metric_regressions": 0,
        },
        "items": [
            {
                "script_id": str(script_id),
                "category": "status",
                "detail": {
                    "baseline_status": "passed",
                    "current_status": "failed",
                },
                "regression_detected_at": "2024-01-20T12:00:00Z",
            }
        ],
    }

    mock_list = AsyncMock(return_value=expected_payload)
    monkeypatch.setattr(module, "list_regressions", mock_list, raising=False)

    suite_id = uuid4()
    response = client.get(
        f"/api/v1/regressions/?suite_id={suite_id}&status=unresolved&skip=5&limit=10"
    )

    assert response.status_code == 200
    assert response.json() == expected_payload

    mock_list.assert_awaited_once()
    kwargs = mock_list.await_args.kwargs
    assert kwargs["filters"] == {
        "suite_id": suite_id,
        "status": "unresolved",
    }
    assert kwargs["pagination"] == {"skip": 5, "limit": 10}


def test_approve_baseline_returns_record(client, monkeypatch):
    module = sys.modules["services.regression_service"]

    current_user = app.dependency_overrides[get_current_user_with_db]()
    script_id = uuid4()
    approved_payload = {
        "script_id": str(script_id),
        "status": "passed",
        "metrics": {"pass_rate": 0.99},
        "version": 1,
        "approved_at": "2024-01-20T12:00:00Z",
        "approved_by": str(current_user.id),
        "note": "Baseline refreshed after investigation",
    }

    mock_approve = AsyncMock(return_value=approved_payload)
    monkeypatch.setattr(module, "approve_baseline", mock_approve, raising=False)
    assert module.approve_baseline is mock_approve

    payload = {
        "status": "passed",
        "metrics": {"pass_rate": 0.99},
        "note": "Baseline refreshed after investigation",
    }

    response = client.post(
        f"/api/v1/regressions/{script_id}/baseline",
        json=payload,
    )

    assert response.status_code == 200
    assert response.json() == approved_payload

    mock_approve.assert_awaited_once()
    kwargs = mock_approve.await_args.kwargs
    assert kwargs["script_id"] == script_id
    assert kwargs["snapshot_data"] == {
        "status": "passed",
        "metrics": {"pass_rate": 0.99},
    }
    assert kwargs["approved_by"] == current_user.id  # Provided via dependency override
    assert kwargs["note"] == "Baseline refreshed after investigation"


def test_get_regression_comparison_returns_snapshots(client, monkeypatch):
    module = sys.modules["services.regression_service"]

    script_id = uuid4()
    comparison_payload = {
        "script_id": str(script_id),
        "baseline": {
            "status": "passed",
            "metrics": {"pass_rate": {"value": 0.95, "threshold": None, "unit": None}},
            "media_uri": None,
        },
        "current": {
            "status": "failed",
            "metrics": {"pass_rate": {"value": 0.82, "threshold": None, "unit": None}},
            "media_uri": None,
        },
        "differences": [
            {
                "metric": "pass_rate",
                "baseline_value": 0.95,
                "current_value": 0.82,
                "delta": -0.13,
                "delta_pct": -13.68,
            }
        ],
    }

    mock_comparison = AsyncMock(return_value=comparison_payload)
    monkeypatch.setattr(module, "get_regression_comparison", mock_comparison, raising=False)

    response = client.get(f"/api/v1/regressions/{script_id}/comparison")

    assert response.status_code == 200
    assert response.json() == comparison_payload
    mock_comparison.assert_awaited_once()
    kwargs = mock_comparison.await_args.kwargs
    assert kwargs["script_id"] == script_id
