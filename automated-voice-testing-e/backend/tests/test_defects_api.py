"""
Defects API endpoint tests.

Validates CRUD, assignment, and resolution flows exposed via the HTTP API.
"""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import AsyncMock

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
from services import defect_service


@pytest.fixture()
def client():
    return TestClient(app)


# Shared tenant_id for all tests
TEST_TENANT_ID = uuid4()


@pytest.fixture(autouse=True)
def override_dependencies():
    fake_user = SimpleNamespace(id=uuid4(), email="qa@example.com", is_active=True, role="admin", tenant_id=TEST_TENANT_ID)
    app.dependency_overrides[get_current_user_with_db] = lambda: fake_user

    async def fake_db():
        yield None

    app.dependency_overrides[get_db] = fake_db

    yield

    app.dependency_overrides.clear()


def _defect_payload(**overrides):
    base = {
        "test_case_id": str(uuid4()),
        "test_execution_id": str(uuid4()),
        "severity": "high",
        "category": "semantic",
        "title": "Unexpected response",
        "description": "Assistant returned wrong navigation route.",
        "language_code": "en",
        "detected_at": datetime.now(timezone.utc).isoformat(),
        "status": "open",
    }
    base.update(overrides)
    return base


def _defect_response(**overrides):
    base = {
        "id": str(uuid4()),
        "tenant_id": TEST_TENANT_ID,  # Match the fake_user's tenant_id
        "test_case_id": str(uuid4()),
        "test_execution_id": str(uuid4()),
        "severity": "high",
        "category": "semantic",
        "title": "Unexpected response",
        "description": "Assistant returned wrong navigation route.",
        "language_code": "en",
        "detected_at": datetime.now(timezone.utc).isoformat(),
        "status": "open",
        "assigned_to": None,
        "resolved_at": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    base.update(overrides)
    # Return SimpleNamespace so check_resource_access can use getattr
    return SimpleNamespace(**base)


def test_create_defect_success(client, monkeypatch):
    expected = _defect_response()
    mock_create = AsyncMock(return_value=expected)
    monkeypatch.setattr(defect_service, "create_defect", mock_create)

    payload = _defect_payload()
    response = client.post("/api/v1/defects/", json=payload)

    assert response.status_code == 201
    assert response.json()["id"] == expected.id
    mock_create.assert_awaited_once()


def test_create_defect_validation_error(client, monkeypatch):
    mock_create = AsyncMock(side_effect=ValueError("invalid severity"))
    monkeypatch.setattr(defect_service, "create_defect", mock_create)

    response = client.post("/api/v1/defects/", json=_defect_payload())

    assert response.status_code == 400
    assert response.json()["detail"] == "invalid severity"


def test_get_defect_success(client, monkeypatch):
    expected = _defect_response()
    mock_get = AsyncMock(return_value=expected)
    monkeypatch.setattr(defect_service, "get_defect", mock_get)

    defect_id = expected.id
    response = client.get(f"/api/v1/defects/{defect_id}")

    assert response.status_code == 200
    assert response.json()["id"] == defect_id
    mock_get.assert_awaited_once()
    assert str(mock_get.await_args.args[1]) == defect_id


def test_get_defect_not_found(client, monkeypatch):
    mock_get = AsyncMock(side_effect=NoResultFound("Defect not found"))
    monkeypatch.setattr(defect_service, "get_defect", mock_get)

    missing_id = str(uuid4())
    response = client.get(f"/api/v1/defects/{missing_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Defect not found"


def test_list_defects_supports_filters(client, monkeypatch):
    defects = [_defect_response(status="open"), _defect_response(status="resolved")]
    mock_list = AsyncMock(return_value=(defects[:1], 1))
    monkeypatch.setattr(defect_service, "list_defects", mock_list)

    response = client.get("/api/v1/defects/?status=open&severity=high&skip=5&limit=10")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1
    mock_list.assert_awaited_once()
    kwargs = mock_list.await_args.kwargs
    assert kwargs["filters"] == {"status": "open", "severity": "high"}
    assert kwargs["pagination"] == {"skip": 5, "limit": 10}


def test_update_defect_success(client, monkeypatch):
    original = _defect_response()
    updated = _defect_response(status="in_progress", title="Updated title")
    # Mock get_defect for access check
    mock_get = AsyncMock(return_value=original)
    monkeypatch.setattr(defect_service, "get_defect", mock_get)
    # Mock update_defect for the actual update
    mock_update = AsyncMock(return_value=updated)
    monkeypatch.setattr(defect_service, "update_defect", mock_update)

    defect_id = updated.id
    response = client.patch(
        f"/api/v1/defects/{defect_id}",
        json={"status": "in_progress", "title": "Updated title"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"
    mock_update.assert_awaited_once()
    kwargs = mock_update.await_args.kwargs
    assert str(kwargs["defect_id"]) == defect_id


def test_assign_defect(client, monkeypatch):
    original = _defect_response()
    assigned = _defect_response(status="in_progress", assigned_to=str(uuid4()))
    # Mock get_defect for access check
    mock_get = AsyncMock(return_value=original)
    monkeypatch.setattr(defect_service, "get_defect", mock_get)
    # Mock assign_defect for the actual assignment
    mock_assign = AsyncMock(return_value=assigned)
    monkeypatch.setattr(defect_service, "assign_defect", mock_assign)

    defect_id = assigned.id
    user_id = str(uuid4())
    response = client.post(
        f"/api/v1/defects/{defect_id}/assign",
        json={"assigned_to": user_id},
    )

    assert response.status_code == 200
    assert response.json()["assigned_to"] == assigned.assigned_to
    mock_assign.assert_awaited_once()
    kwargs = mock_assign.await_args.kwargs
    assert str(kwargs["defect_id"]) == defect_id
    assert str(kwargs["user_id"]) == user_id


def test_resolve_defect(client, monkeypatch):
    original = _defect_response()
    resolved = _defect_response(status="resolved", resolved_at=datetime.now(timezone.utc).isoformat())
    # Mock get_defect for access check
    mock_get = AsyncMock(return_value=original)
    monkeypatch.setattr(defect_service, "get_defect", mock_get)
    # Mock resolve_defect for the actual resolution
    mock_resolve = AsyncMock(return_value=resolved)
    monkeypatch.setattr(defect_service, "resolve_defect", mock_resolve)

    defect_id = resolved.id
    response = client.post(
        f"/api/v1/defects/{defect_id}/resolve",
        json={"resolution": "Patched in release"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "resolved"
    mock_resolve.assert_awaited_once()
    kwargs = mock_resolve.await_args.kwargs
    assert str(kwargs["defect_id"]) == defect_id
    assert kwargs["resolution"] == "Patched in release"
