"""
Custom report builder API tests (TASK-316).
"""

from __future__ import annotations

import base64
import os
from datetime import date
from types import SimpleNamespace
from typing import Optional
from uuid import uuid4

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
from api.database import get_db
from api.routes.reports import get_custom_report_builder_service
from api.dependencies import get_current_user_with_db
from api import rate_limit
from api import redis_client
from services.custom_report_builder import CustomReportRequest, CustomReportResult


@pytest.fixture()
def client(report_builder_stub: "ReportBuilderStub") -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def report_builder_stub() -> "ReportBuilderStub":
    stub = ReportBuilderStub()
    fake_user = SimpleNamespace(id=uuid4(), email="qa@example.com", is_active=True, role="admin", tenant_id=None)

    app.dependency_overrides[get_current_user_with_db] = lambda: fake_user

    async def fake_db():
        yield None

    app.dependency_overrides[get_db] = fake_db
    app.dependency_overrides[get_custom_report_builder_service] = lambda: stub

    async def _noop_rate_limit(request):
        return None

    original_rate_limit = rate_limit.enforce_rate_limit
    rate_limit.enforce_rate_limit = _noop_rate_limit

    class FakeRedisClient:
        async def get(self, *_args, **_kwargs):
            return None

        async def set(self, *_args, **_kwargs):
            return True

        async def delete(self, *_args, **_kwargs):
            return 0

        async def exists(self, *_args, **_kwargs):
            return False

    original_redis_client = redis_client._redis_client
    redis_client._redis_client = FakeRedisClient()

    yield stub

    app.dependency_overrides.clear()
    rate_limit.enforce_rate_limit = original_rate_limit
    redis_client._redis_client = original_redis_client


class ReportBuilderStub:
    def __init__(self) -> None:
        self.calls: list[CustomReportRequest] = []
        self.result: Optional[CustomReportResult] = None

    def create_report(self, request: CustomReportRequest) -> CustomReportResult:
        self.calls.append(request)
        if self.result:
            return self.result
        return CustomReportResult(
            content=b"%PDF",
            data=None,
            content_type="application/pdf",
            filename="custom-report.pdf",
        )


def test_create_custom_report_returns_pdf_payload(client: TestClient, report_builder_stub: ReportBuilderStub) -> None:
    payload = {
        "metrics": ["pass_rate", "defects"],
        "start_date": "2024-01-01",
        "end_date": "2024-01-07",
        "format": "pdf",
        "title": "Weekly Custom Snapshot",
    }

    response = client.post("/api/v1/reports/custom", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["filename"] == "custom-report.pdf"
    assert body["content_type"] == "application/pdf"
    assert base64.b64decode(body["content"]) == b"%PDF"

    request = report_builder_stub.calls[0]
    assert list(request.metrics) == ["pass_rate", "defects"]
    assert request.start_date == date(2024, 1, 1)
    assert request.end_date == date(2024, 1, 7)
    assert request.title == "Weekly Custom Snapshot"


def test_create_custom_report_returns_json_payload(client: TestClient, report_builder_stub: ReportBuilderStub) -> None:
    report_builder_stub.result = CustomReportResult(
        content=None,
        data={"metrics": {"pass_rate": 0.91}},
        content_type="application/json",
        filename="custom.json",
    )

    payload = {
        "metrics": ["pass_rate"],
        "start_date": "2024-02-01",
        "end_date": "2024-02-05",
        "format": "json",
    }

    response = client.post("/api/v1/reports/custom", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert "content" not in body
    assert body["data"] == {"metrics": {"pass_rate": 0.91}}
    assert body["filename"] == "custom.json"
