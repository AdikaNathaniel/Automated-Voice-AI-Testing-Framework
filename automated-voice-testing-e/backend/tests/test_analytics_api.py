"""
Analytics trends API endpoint tests.

Ensures the analytics router aggregates trend data and validates parameters.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from types import SimpleNamespace
from typing import Any, Dict, List, Tuple
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
from api.routes.analytics import get_trend_analysis_service
from api import rate_limit
from api import redis_client


@pytest.fixture()
def client(trend_stub: "StubTrendService") -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def trend_stub() -> "StubTrendService":
    stub = StubTrendService()
    fake_user = SimpleNamespace(id=uuid4(), email="user@example.com", is_active=True, role="admin", tenant_id=None)

    app.dependency_overrides[get_current_user_with_db] = lambda: fake_user

    async def fake_db():
        yield None

    app.dependency_overrides[get_db] = fake_db
    app.dependency_overrides[get_trend_analysis_service] = lambda: stub

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


class StubTrendService:
    """Collects calls and returns predefined payloads for trend analyses."""

    def __init__(self) -> None:
        now = datetime(2024, 1, 1, tzinfo=timezone.utc)
        iso = now.isoformat().replace("+00:00", "Z")
        self.pass_rate_result = [
            {
                "period_start": iso,
                "pass_rate_pct": 80.0,
                "change_pct": None,
                "direction": "flat",
                "total_executions": 10,
            }
        ]
        self.defect_result = [
            {
                "period_start": iso,
                "detected": 3,
                "resolved": 1,
                "net_open": 5,
                "change_open": None,
                "direction": "flat",
            }
        ]
        self.performance_result = [
            {
                "period_start": iso,
                "avg_response_time_ms": 1200.0,
                "change_ms": None,
                "direction": "flat",
                "sample_size": 4,
            }
        ]
        self.calls: List[Tuple[str, Dict[str, Any]]] = []

    async def analyze_pass_rate_trend(self, **kwargs: Any):
        self.calls.append(("pass_rate", kwargs))
        return self.pass_rate_result

    async def analyze_defect_trend(self, **kwargs: Any):
        self.calls.append(("defect", kwargs))
        return self.defect_result

    async def analyze_performance_trend(self, **kwargs: Any):
        self.calls.append(("performance", kwargs))
        return self.performance_result


def test_trends_endpoint_returns_combined_payload(
    client: TestClient, trend_stub: StubTrendService
) -> None:
    start = "2024-01-01"
    end = "2024-01-03"

    response = client.get(
        f"/api/v1/analytics/trends?start_date={start}&end_date={end}&granularity=day"
    )

    assert response.status_code == 200
    assert response.json() == {
        "pass_rate": trend_stub.pass_rate_result,
        "defects": trend_stub.defect_result,
        "performance": trend_stub.performance_result,
    }

    assert [call[0] for call in trend_stub.calls] == [
        "pass_rate",
        "defect",
        "performance",
    ]

    for _, kwargs in trend_stub.calls:
        assert kwargs["granularity"] == "day"
        assert kwargs["start_date"] == date(2024, 1, 1)
        assert kwargs["end_date"] == date(2024, 1, 3)


def test_trends_endpoint_accepts_default_dates(client: TestClient, trend_stub: StubTrendService):
    response = client.get("/api/v1/analytics/trends")

    assert response.status_code == 200
    # Ensure at least one call was made and dates are populated.
    assert trend_stub.calls
    for _, kwargs in trend_stub.calls:
        assert isinstance(kwargs["start_date"], date)
        assert isinstance(kwargs["end_date"], date)
        assert kwargs["start_date"] <= kwargs["end_date"]


def test_trends_endpoint_rejects_invalid_granularity(
    client: TestClient, trend_stub: StubTrendService
) -> None:
    response = client.get("/api/v1/analytics/trends?granularity=week")

    assert response.status_code == 422
    assert not trend_stub.calls


def test_trends_endpoint_rejects_inverted_dates(
    client: TestClient, trend_stub: StubTrendService
) -> None:
    response = client.get("/api/v1/analytics/trends?start_date=2024-01-04&end_date=2024-01-02")

    assert response.status_code == 400
    assert response.json()["detail"] == "start_date must be on or before end_date"
    assert not trend_stub.calls
