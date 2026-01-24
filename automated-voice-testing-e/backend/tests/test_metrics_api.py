"""
API tests for the real-time metrics endpoint (TASK-222).
"""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import os
import sys
import types
import pytest
from fastapi.testclient import TestClient
from prometheus_client.exposition import CONTENT_TYPE_LATEST

# Lightweight stub for optional reportlab dependency used by unrelated services.
if "reportlab" not in sys.modules:
    reportlab_module = types.ModuleType("reportlab")
    reportlab_lib = types.ModuleType("reportlab.lib")
    reportlab_pagesizes = types.ModuleType("reportlab.lib.pagesizes")
    reportlab_pagesizes.letter = (612, 792)
    reportlab_pagesizes.A4 = (595.275590551, 841.88976378)
    reportlab_pagesizes.landscape = lambda size: size

    reportlab_units = types.ModuleType("reportlab.lib.units")
    reportlab_units.inch = 72

    reportlab_pdfgen = types.ModuleType("reportlab.pdfgen")
    reportlab_pdfgen_canvas = types.ModuleType("reportlab.pdfgen.canvas")

    class _DummyCanvas:  # pragma: no cover - import shim only
        def __init__(self, *args, **kwargs):
            raise RuntimeError("PDF generation not available in test shim.")

    reportlab_pdfgen_canvas.Canvas = _DummyCanvas

    sys.modules["reportlab"] = reportlab_module
    sys.modules["reportlab.lib"] = reportlab_lib
    sys.modules["reportlab.lib.pagesizes"] = reportlab_pagesizes
    sys.modules["reportlab.lib.units"] = reportlab_units
    sys.modules["reportlab.pdfgen"] = reportlab_pdfgen
    sys.modules["reportlab.pdfgen.canvas"] = reportlab_pdfgen_canvas

    reportlab_module.lib = types.SimpleNamespace(
        pagesizes=reportlab_pagesizes,
        units=reportlab_units,
    )
    reportlab_module.pdfgen = types.SimpleNamespace(canvas=reportlab_pdfgen_canvas)

if "jsonschema" not in sys.modules:
    jsonschema_module = types.ModuleType("jsonschema")

    class _DummyValidationError(Exception):  # pragma: no cover - import shim only
        def __init__(self, message: str = "", path: tuple = ()):
            super().__init__(message)
            self.message = message
            self.path = path

    class _DummyDraft7Validator:  # pragma: no cover - import shim only
        def __init__(self, schema):
            self.schema = schema

        def iter_errors(self, instance):
            return []

    jsonschema_module.Draft7Validator = _DummyDraft7Validator
    jsonschema_module.ValidationError = _DummyValidationError

    sys.modules["jsonschema"] = jsonschema_module

# Minimal configuration for FastAPI app imports.
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
from services import real_time_metrics_service


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


def _sample_payload():
    now = datetime.now(timezone.utc)
    return {
        "current_runs": [
            {
                "id": str(uuid4()),
                "suite_id": str(uuid4()),
                "suite_name": "Smoke Suite",
                "status": "running",
                "progress_pct": 64.3,
                "total_tests": 50,
                "passed_tests": 30,
                "failed_tests": 5,
                "skipped_tests": 3,
                "started_at": now.isoformat().replace("+00:00", "Z"),
                "completed_at": None,
            }
        ],
        "queue_depth": {
            "total": 45,
            "queued": 12,
            "processing": 6,
            "completed": 24,
            "failed": 3,
            "average_priority": 7.2,
            "oldest_queued_seconds": 85.0,
        },
        "throughput": {
            "tests_per_minute": 3.4,
            "sample_size": 51,
            "window_minutes": 15,
            "last_updated": now.isoformat().replace("+00:00", "Z"),
        },
        "run_counts": {
            "pending": 2,
            "running": 3,
            "completed": 5,
            "failed": 1,
            "cancelled": 0,
        },
        "issue_summary": {
            "open_defects": 4,
            "critical_defects": 1,
            "edge_cases_active": 7,
            "edge_cases_new": 2,
        },
    }


def test_real_time_metrics_returns_payload(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    expected = _sample_payload()
    service_mock = AsyncMock(return_value=expected)
    monkeypatch.setattr(
        real_time_metrics_service,
        "get_real_time_metrics",
        service_mock,
    )

    response = client.get("/api/v1/metrics/real-time")

    assert response.status_code == 200
    assert response.json() == expected
    service_mock.assert_awaited_once()
    kwargs = service_mock.await_args.kwargs
    assert kwargs["window_minutes"] == 15
    assert kwargs["max_runs"] == 5


def test_real_time_metrics_accepts_window_override(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    expected = _sample_payload()
    service_mock = AsyncMock(return_value=expected)
    monkeypatch.setattr(
        real_time_metrics_service,
        "get_real_time_metrics",
        service_mock,
    )

    response = client.get("/api/v1/metrics/real-time?window_minutes=30&max_runs=3")

    assert response.status_code == 200
    service_mock.assert_awaited_once()
    kwargs = service_mock.await_args.kwargs
    assert kwargs["window_minutes"] == 30
    assert kwargs["max_runs"] == 3


def test_prometheus_metrics_endpoint_returns_registry(client: TestClient):
    response = client.get("/api/v1/metrics")

    assert response.status_code == 200
    assert response.headers["content-type"] == CONTENT_TYPE_LATEST

    payload = response.text

    assert "# HELP test_executions_total" in payload
    assert "test_executions_total 0.0" in payload
    assert "# TYPE queue_depth gauge" in payload
