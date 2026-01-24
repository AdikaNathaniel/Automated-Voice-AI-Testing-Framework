"""
API tests for worker health monitoring endpoint (TASK-285).
"""

from __future__ import annotations

import os
from typing import List
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/testdb")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("JWT_SECRET_KEY", "supersecretkey1234")
os.environ.setdefault("SOUNDHOUND_API_KEY", "test-key")
os.environ.setdefault("SOUNDHOUND_CLIENT_ID", "test-client")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test-access")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test-secret")

from api.main import app
from api.routes import workers
from services.worker_health_service import WorkerHealthReport, WorkerStatus


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def override_service():
    service = MagicMock()
    app.dependency_overrides[workers.get_worker_health_service] = lambda: service
    yield service
    app.dependency_overrides.pop(workers.get_worker_health_service, None)


def _sample_report() -> WorkerHealthReport:
    workers: List[WorkerStatus] = [
        WorkerStatus(
            name="worker-a@example",
            status="online",
            active_tasks=2,
            max_concurrency=4,
            queues=("default",),
        ),
        WorkerStatus(
            name="worker-b@example",
            status="online",
            active_tasks=0,
            max_concurrency=2,
            queues=("priority",),
        ),
    ]

    return WorkerHealthReport(
        status="healthy",
        total_workers=2,
        total_online=2,
        total_offline=0,
        workers=workers,
        alerts=[],
    )


def test_worker_health_endpoint_returns_report(client: TestClient, override_service: MagicMock):
    report = _sample_report()
    override_service.check_health.return_value = report

    response = client.get("/api/v1/workers/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["totals"]["workers"] == 2
    assert payload["totals"]["offline"] == 0
    assert payload["workers"][0]["name"] == "worker-a@example"
    override_service.check_health.assert_called_once()
