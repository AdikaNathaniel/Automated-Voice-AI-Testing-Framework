"""
End-to-end authentication API tests (TODO §5.1 JWT & refresh token flows).

Exercises registration, login, refresh, and logout endpoints to ensure refresh
tokens rotate and invalid tokens are rejected (TODO §5.1).
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock

_TEST_ENV_OVERRIDES = {
    "DATABASE_URL": "postgresql://tester:tester@localhost:5432/testdb",
    "REDIS_URL": "redis://localhost:6379/0",
    "JWT_SECRET_KEY": "unit-test-secret",
    "SOUNDHOUND_API_KEY": "fake-soundhound-key",
    "SOUNDHOUND_CLIENT_ID": "fake-client-id",
    "AWS_ACCESS_KEY_ID": "fake-aws-access-key",
    "AWS_SECRET_ACCESS_KEY": "fake-aws-secret",
}

for key, value in _TEST_ENV_OVERRIDES.items():
    os.environ.setdefault(key, value)

from api.database import get_db
from api.dependencies import get_current_user, get_current_user_with_db
from api.routes import auth as auth_routes
from api.schemas.auth import UserResponse
from api.auth.roles import Role
from services import user_service
from services.refresh_token_store import refresh_token_store


def _create_test_app() -> FastAPI:
    application = FastAPI()
    application.include_router(auth_routes.router, prefix="/api/v1")
    return application


app = _create_test_app()


@pytest.fixture(autouse=True)
def override_dependencies():
    async def fake_db():
        yield None

    app.dependency_overrides[get_db] = fake_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest_asyncio.fixture
async def auth_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
    refresh_token_store.clear()


def _make_user():
    return SimpleNamespace(id=uuid4(),
        email="tester@example.com",
        password_hash="hashed-password",
        is_active=True,
        username="tester",
        full_name="Test User",
        role="admin",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def _install_user_mocks(monkeypatch, user):
    get_user_by_email = AsyncMock(return_value=user)
    get_user_by_id = AsyncMock(return_value=user)
    monkeypatch.setattr(user_service, "get_user_by_email", get_user_by_email)
    monkeypatch.setattr(user_service, "get_user_by_id", get_user_by_id)
    return get_user_by_email, get_user_by_id


@pytest.mark.asyncio
async def test_login_refresh_and_logout_flow(auth_client: AsyncClient, monkeypatch: pytest.MonkeyPatch):
    user = _make_user()
    _install_user_mocks(monkeypatch, user)
    monkeypatch.setattr("api.routes.auth.verify_password", lambda plain, hashed: plain == "password123")

    # Login to obtain access + refresh tokens
    login_response = await auth_client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "password123"},
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    refresh_token_1 = tokens["refresh_token"]
    assert tokens["access_token"]

    # Use refresh token to rotate tokens
    refresh_response = await auth_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token_1},
    )
    assert refresh_response.status_code == 200
    refresh_payload = refresh_response.json()
    refresh_token_2 = refresh_payload["refresh_token"]
    assert refresh_token_2 != refresh_token_1
    assert refresh_payload["access_token"]

    # Original refresh token should now be invalid
    stale_response = await auth_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token_1},
    )
    assert stale_response.status_code == 401

    # Logout with the current refresh token
    logout_response = await auth_client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token_2},
    )
    assert logout_response.status_code == 200

    # Token should be revoked after logout
    revoked_response = await auth_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token_2},
    )
    assert revoked_response.status_code == 401


@pytest.mark.asyncio
async def test_registration_requires_admin_role(auth_client: AsyncClient, monkeypatch: pytest.MonkeyPatch):
    non_admin_user = UserResponse(
        id=uuid4(),
        email="qa@example.com",
        username="qa",
        full_name="QA Lead",
        role=Role.QA_LEAD.value,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    async def override_user():
        return non_admin_user

    app.dependency_overrides[get_current_user_with_db] = override_user

    response = await auth_client.post(
        "/api/v1/auth/register",
        json={
            "email": "new.user@example.com",
            "username": "newuser",
            "password": "SecurePass!123",
            "full_name": "New User",
        },
    )

    assert response.status_code == 403
    app.dependency_overrides.pop(get_current_user_with_db, None)


@pytest.mark.asyncio
async def test_admin_can_register_users(auth_client: AsyncClient, monkeypatch: pytest.MonkeyPatch):
    created_user = SimpleNamespace(id=uuid4(),
        email="new.user@example.com",
        username="newuser",
        full_name="New User",
        is_active=True,
        role="qa_lead",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    create_user_mock = AsyncMock(return_value=created_user)
    monkeypatch.setattr(user_service, "create_user", create_user_mock)

    admin_user = UserResponse(
        id=uuid4(),
        email="admin@example.com",
        username="admin",
        full_name="Admin User",
        role=Role.ORG_ADMIN.value,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    async def override_user():
        return admin_user

    app.dependency_overrides[get_current_user_with_db] = override_user

    payload = {
        "email": created_user.email,
        "username": created_user.username,
        "password": "SecurePass!123",
        "full_name": "New User",
    }

    response = await auth_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["email"] == created_user.email
    create_user_mock.assert_awaited_once()

    app.dependency_overrides.pop(get_current_user_with_db, None)
