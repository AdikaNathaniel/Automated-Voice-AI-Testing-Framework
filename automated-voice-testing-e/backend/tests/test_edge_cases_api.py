"""
Edge cases API endpoint tests.

Validates CRUD, search, and categorisation flows exposed via the HTTP API.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from types import SimpleNamespace
from uuid import UUID, uuid4
from typing import Any, Dict, List, Tuple

import os

import pytest
from fastapi.testclient import TestClient

from sqlalchemy.exc import NoResultFound

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
from services import edge_case_service


class FakeAsyncSession:
    """Minimal async session stub exposing run_sync used by the routes."""

    def __init__(self) -> None:
        self.sync_session = object()

    async def run_sync(self, func, *args, **kwargs):
        return func(self.sync_session, *args, **kwargs)


class FakeEdgeCaseService:
    """Test double capturing method calls and returning configured payloads."""

    last_call: Tuple[str, Dict[str, Any]] | None = None
    create_return_value: Dict[str, Any] | None = None
    get_return_value: Dict[str, Any] | None = None
    list_return_value: Tuple[List[Dict[str, Any]], int] = ([], 0)
    search_return_value: Tuple[List[Dict[str, Any]], int] = ([], 0)
    update_return_value: Dict[str, Any] | None = None
    categorize_return_value: Dict[str, Any] | None = None
    delete_return_value: bool = True
    raise_error: Exception | None = None

    def __init__(self, session) -> None:
        self.session = session

    def create_edge_case(self, **kwargs):
        FakeEdgeCaseService.last_call = ("create_edge_case", kwargs)
        if FakeEdgeCaseService.raise_error:
            raise FakeEdgeCaseService.raise_error
        return FakeEdgeCaseService.create_return_value

    def get_edge_case(self, edge_case_id: UUID):
        FakeEdgeCaseService.last_call = ("get_edge_case", {"edge_case_id": edge_case_id})
        if FakeEdgeCaseService.raise_error:
            raise FakeEdgeCaseService.raise_error
        return FakeEdgeCaseService.get_return_value

    def list_edge_cases(self, filters: Dict[str, Any], pagination: Dict[str, int]):
        FakeEdgeCaseService.last_call = (
            "list_edge_cases",
            {"filters": filters, "pagination": pagination},
        )
        if FakeEdgeCaseService.raise_error:
            raise FakeEdgeCaseService.raise_error
        return FakeEdgeCaseService.list_return_value

    def search_edge_cases(self, query: str, filters: Dict[str, Any], pagination: Dict[str, int]):
        FakeEdgeCaseService.last_call = (
            "search_edge_cases",
            {"query": query, "filters": filters, "pagination": pagination},
        )
        if FakeEdgeCaseService.raise_error:
            raise FakeEdgeCaseService.raise_error
        return FakeEdgeCaseService.search_return_value

    def update_edge_case(self, edge_case_id: UUID, **data):
        FakeEdgeCaseService.last_call = (
            "update_edge_case",
            {"edge_case_id": edge_case_id, "data": data},
        )
        if FakeEdgeCaseService.raise_error:
            raise FakeEdgeCaseService.raise_error
        return FakeEdgeCaseService.update_return_value

    def categorize_edge_case(self, edge_case_id: UUID, signals: Dict[str, Any]):
        FakeEdgeCaseService.last_call = (
            "categorize_edge_case",
            {"edge_case_id": edge_case_id, "signals": signals},
        )
        if FakeEdgeCaseService.raise_error:
            raise FakeEdgeCaseService.raise_error
        return FakeEdgeCaseService.categorize_return_value

    def delete_edge_case(self, edge_case_id: UUID):
        FakeEdgeCaseService.last_call = ("delete_edge_case", {"edge_case_id": edge_case_id})
        if FakeEdgeCaseService.raise_error:
            raise FakeEdgeCaseService.raise_error
        return FakeEdgeCaseService.delete_return_value


@pytest.fixture(autouse=True)
def reset_fake_service():
    FakeEdgeCaseService.last_call = None
    FakeEdgeCaseService.create_return_value = None
    FakeEdgeCaseService.get_return_value = None
    FakeEdgeCaseService.list_return_value = ([], 0)
    FakeEdgeCaseService.search_return_value = ([], 0)
    FakeEdgeCaseService.update_return_value = None
    FakeEdgeCaseService.categorize_return_value = None
    FakeEdgeCaseService.delete_return_value = True
    FakeEdgeCaseService.raise_error = None
    yield
    FakeEdgeCaseService.last_call = None


@pytest.fixture()
def client(monkeypatch):
    # Override dependencies
    fake_user = SimpleNamespace(id=uuid4(), email="qa@example.com", is_active=True, role="admin", tenant_id=None)
    app.dependency_overrides[get_current_user_with_db] = lambda: fake_user

    async def fake_db():
        yield FakeAsyncSession()

    app.dependency_overrides[get_db] = fake_db
    monkeypatch.setattr(edge_case_service, "EdgeCaseService", FakeEdgeCaseService)
    monkeypatch.setattr("api.routes.edge_cases.EdgeCaseService", FakeEdgeCaseService)

    class DummyRedisClient:
        def __init__(self, *args, **kwargs):
            self.connected = False

        async def connect(self):
            self.connected = True

        async def disconnect(self):
            self.connected = False

        async def get(self, *args, **kwargs):
            return None

        async def set(self, *args, **kwargs):
            return True

        async def delete(self, *args, **kwargs):
            return True

        async def exists(self, *args, **kwargs):
            return False

    monkeypatch.setattr("api.redis_client.RedisClient", DummyRedisClient)
    # Ensure global client resets between tests
    monkeypatch.setattr("api.redis_client._redis_client", None, raising=False)

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def _edge_case_payload(**overrides):
    base = {
        "title": "Ambiguous navigation near mall",
        "description": "Assistant chooses incorrect store when multiple match.",
        "scenario_definition": {"steps": ["ask for mall", "expect correct store"]},
        "tags": ["navigation", "ambiguity"],
        "severity": "high",
        "category": "ambiguity",
        "test_case_id": str(uuid4()),
        "discovered_date": date.today().isoformat(),
        "discovered_by": str(uuid4()),
        "status": "active",
    }
    base.update(overrides)
    return base


def _edge_case_response(**overrides):
    base = {
        "id": str(uuid4()),
        "title": "Ambiguous navigation near mall",
        "description": "Assistant chooses incorrect store when multiple match.",
        "scenario_definition": {"steps": ["ask for mall", "expect correct store"]},
        "tags": ["navigation", "ambiguity"],
        "severity": "high",
        "category": "ambiguity",
        "test_case_id": str(uuid4()),
        "discovered_date": date.today().isoformat(),
        "discovered_by": str(uuid4()),
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    base.update(overrides)
    return base


def test_create_edge_case_success(client):
    expected = _edge_case_response()
    FakeEdgeCaseService.create_return_value = expected

    response = client.post("/api/v1/edge-cases/", json=_edge_case_payload())

    assert response.status_code == 201
    assert response.json()["id"] == expected["id"]
    assert FakeEdgeCaseService.last_call and FakeEdgeCaseService.last_call[0] == "create_edge_case"


def test_create_edge_case_validation_error(client):
    FakeEdgeCaseService.raise_error = ValueError("invalid severity")

    response = client.post("/api/v1/edge-cases/", json=_edge_case_payload())

    assert response.status_code == 400
    assert response.json()["detail"] == "invalid severity"


def test_get_edge_case_success(client):
    expected = _edge_case_response()
    FakeEdgeCaseService.get_return_value = expected

    response = client.get(f"/api/v1/edge-cases/{expected['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == expected["id"]
    assert FakeEdgeCaseService.last_call == (
        "get_edge_case",
        {"edge_case_id": UUID(expected["id"])},
    )


def test_get_edge_case_not_found(client):
    FakeEdgeCaseService.raise_error = NoResultFound("Edge case not found")
    missing_id = str(uuid4())

    response = client.get(f"/api/v1/edge-cases/{missing_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Edge case not found"


def test_list_edge_cases_with_filters(client):
    edge_case = _edge_case_response()
    FakeEdgeCaseService.list_return_value = ([edge_case], 1)

    response = client.get(
        "/api/v1/edge-cases/?status=active&severity=high&category=audio_quality&"
        "tags=audio&tags=regression&skip=5&limit=10"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert FakeEdgeCaseService.last_call == (
        "list_edge_cases",
        {
            "filters": {
                "status": "active",
                "severity": "high",
                "category": "audio_quality",
                "tags": ["audio", "regression"],
            },
            "pagination": {"skip": 5, "limit": 10},
        },
    )


def test_search_edge_cases(client):
    match = _edge_case_response(title="Media playback stutter")
    FakeEdgeCaseService.search_return_value = ([match], 1)

    response = client.get(
        "/api/v1/edge-cases/search?query=media&status=active&limit=5"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Media playback stutter"
    assert FakeEdgeCaseService.last_call == (
        "search_edge_cases",
        {
            "query": "media",
            "filters": {"status": "active"},
            "pagination": {"skip": 0, "limit": 5},
        },
    )


def test_update_edge_case(client):
    updated = _edge_case_response(status="resolved", tags=["audio", "noise"])
    FakeEdgeCaseService.update_return_value = updated

    response = client.patch(
        f"/api/v1/edge-cases/{updated['id']}",
        json={"status": "resolved", "tags": ["audio", "noise"]},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "resolved"
    assert FakeEdgeCaseService.last_call == (
        "update_edge_case",
        {
            "edge_case_id": UUID(updated["id"]),
            "data": {"status": "resolved", "tags": ["audio", "noise"]},
        },
    )


def test_categorize_edge_case(client):
    categorized = _edge_case_response(category="audio_quality", severity="high")
    FakeEdgeCaseService.categorize_return_value = categorized

    response = client.post(
        f"/api/v1/edge-cases/{categorized['id']}/categorize",
        json={"signals": {"impact_score": 0.82}},
    )

    assert response.status_code == 200
    assert response.json()["category"] == "audio_quality"
    assert FakeEdgeCaseService.last_call == (
        "categorize_edge_case",
        {
            "edge_case_id": UUID(categorized["id"]),
            "signals": {"impact_score": 0.82},
        },
    )


def test_delete_edge_case(client):
    edge_case_id = str(uuid4())
    FakeEdgeCaseService.delete_return_value = True

    response = client.delete(f"/api/v1/edge-cases/{edge_case_id}")

    assert response.status_code == 204, response.text
    assert response.content == b""
    assert FakeEdgeCaseService.last_call == (
        "delete_edge_case",
        {"edge_case_id": UUID(edge_case_id)},
    )


def test_delete_edge_case_not_found(client):
    missing_id = str(uuid4())
    FakeEdgeCaseService.raise_error = NoResultFound("Edge case not found")

    response = client.delete(f"/api/v1/edge-cases/{missing_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Edge case not found"
