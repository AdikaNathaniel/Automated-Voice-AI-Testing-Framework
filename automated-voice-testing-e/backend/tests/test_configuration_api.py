"""
API tests for configuration management endpoints (TASK-250).
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Generator
from uuid import uuid4

import pytest
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from unittest.mock import patch


class _DummySettings:
    # Database
    DATABASE_URL = "postgresql+asyncpg://user:pass@localhost:5432/testdb"
    READ_REPLICA_URL = None
    DB_HOST = "localhost"
    DB_PORT = 5432
    DB_NAME = "testdb"
    DB_USER = "user"
    DB_PASSWORD = "pass"
    DB_POOL_SIZE = 20
    DB_MAX_OVERFLOW = 10
    DB_POOL_TIMEOUT = 30
    DB_POOL_RECYCLE = 3600

    # Redis
    REDIS_URL = "redis://localhost:6379/0"
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = 0
    REDIS_PASSWORD = None
    REDIS_MAX_CONNECTIONS = 10
    CACHE_TTL = 300

    # JWT/Auth
    JWT_SECRET_KEY = "super-secret-key-123"
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_MINUTES = 30
    JWT_REFRESH_EXPIRATION_DAYS = 7
    PASSWORD_HASH_ROUNDS = 12

    # Rate Limiting
    RATE_LIMIT_DEFAULT_REQUESTS = 100
    RATE_LIMIT_DEFAULT_WINDOW = 60
    RATE_LIMIT_AUTH_REQUESTS = 5
    RATE_LIMIT_AUTH_WINDOW = 300
    RATE_LIMIT_TRUSTED_PROXIES = []

    # External Services
    SOUNDHOUND_API_KEY = "test-key"
    SOUNDHOUND_CLIENT_ID = "test-client"
    SOUNDHOUND_ENDPOINT = "https://api.soundhound.com"
    SOUNDHOUND_TIMEOUT = 30
    SOUNDHOUND_MAX_RETRIES = 3
    AWS_ACCESS_KEY_ID = "test"
    AWS_SECRET_ACCESS_KEY = "test"
    AWS_REGION = "us-east-1"

    # Application
    DEBUG = False
    ENVIRONMENT = "test"
    API_V1_PREFIX = "/api/v1"
    SENTRY_DSN = None
    SENTRY_SAMPLE_RATE = 1.0

    # Optional fields
    REPORT_EMAIL_RECIPIENTS = []
    REPORT_EMAIL_SENDER = "test@example.com"
    REPORT_EMAIL_SMTP_HOST = None
    REPORT_EMAIL_SMTP_PORT = None

    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.ENVIRONMENT == "production"

    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.ENVIRONMENT == "development"


with patch("api.config.get_settings", return_value=_DummySettings()):
    from api.database import get_db

import api.config as config_module
config_module.get_settings = lambda: _DummySettings()

# Mock rate limiting to avoid httpx.AsyncClient header format incompatibility
async def _mock_enforce_rate_limit(request):
    """No-op rate limiter for tests"""
    pass

# Patch rate limit before importing app
import api.rate_limit
api.rate_limit.enforce_rate_limit = _mock_enforce_rate_limit

from api.main import app
from api.dependencies import get_current_user_with_db
from api.schemas.auth import UserResponse
from models.base import Base
from models.configuration import Configuration
from models.configuration_history import ConfigurationHistory
import models.test_suite  # noqa: F401
import models.test_run  # noqa: F401

# Ensure required environment variables exist for FastAPI app startup.
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["JWT_SECRET_KEY"] = "super-secret-key-123"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["SOUNDHOUND_API_KEY"] = "test-key"
os.environ["SOUNDHOUND_CLIENT_ID"] = "test-client"
os.environ["AWS_ACCESS_KEY_ID"] = "test"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test"


class SyncSessionWrapper:
    """Wrapper that adds run_sync method to sync sessions for route compatibility."""

    def __init__(self, session: Session):
        self._session = session

    async def run_sync(self, fn):
        """Execute function synchronously with session (awaitable for compatibility)."""
        return fn(self._session)

    async def commit(self):
        """Commit the underlying session."""
        self._session.commit()

    async def rollback(self):
        """Rollback the underlying session."""
        self._session.rollback()

    async def close(self):
        """Close the underlying session."""
        self._session.close()

    def __getattr__(self, name):
        """Delegate attribute access to underlying session."""
        return getattr(self._session, name)


@pytest.fixture(scope="function")
def test_client() -> Generator[TestClient, None, None]:
    """
    Provide a TestClient with dependency overrides and in-memory database.
    Using sync client to avoid async event loop complications.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        poolclass=sa.pool.StaticPool,  # Required for in-memory SQLite
        connect_args={"check_same_thread": False},  # Allow multi-threading
    )

    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    # Create tables
    with engine.begin() as conn:
        conn.execute(
            sa.text("CREATE TABLE IF NOT EXISTS users (id CHAR(36) PRIMARY KEY, email VARCHAR(255))")
        )
        Base.metadata.create_all(
            bind=conn,
            tables=[Configuration.__table__, ConfigurationHistory.__table__],
        )

    # Create test user
    user_id = uuid4()
    with SessionLocal() as session:
        session.execute(
            sa.text("INSERT INTO users (id, email) VALUES (:id, :email)"),
            {"id": str(user_id), "email": "qa@example.com"},
        )
        session.commit()

    async def override_get_db():
        """Async generator that yields wrapped sync session."""
        session = SessionLocal()
        wrapped = SyncSessionWrapper(session)
        try:
            yield wrapped
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    user_response = UserResponse(
        id=user_id,
        email="qa@example.com",
        username="qa-user",
        full_name="QA User",
        is_active=True,
        role="admin",
        created_at=datetime.now(tz=timezone.utc),
    )

    def override_current_user():
        return user_response

    app.dependency_overrides[get_current_user_with_db] = override_current_user

    with TestClient(app) as client:
        yield client

    # Cleanup
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_current_user_with_db, None)

    with engine.begin() as conn:
        Base.metadata.drop_all(
            bind=conn,
            tables=[ConfigurationHistory.__table__, Configuration.__table__],
        )
        conn.execute(sa.text("DROP TABLE IF EXISTS users"))

    engine.dispose()


def _create_payload(key: str = "feature.flag") -> dict:
    if key == "queue.config":
        config_data = {"size": 10}
        description = "Queue size controls"
    elif key == "smtp.settings":
        config_data = {"host": "smtp.example.com", "port": 587}
        description = "SMTP delivery configuration"
    else:
        config_data = {"enabled": False}
        description = "Feature flag controls"

    return {
        "config_key": key,
        "config_data": config_data,
        "description": description,
    }


def test_create_configuration_endpoint(test_client: TestClient) -> None:
    response = test_client.post("/api/v1/configurations", json=_create_payload())
    assert response.status_code == 201
    body = response.json()
    assert body["config_key"] == "feature.flag"
    assert body["config_data"]["enabled"] is False
    assert body["description"] == "Feature flag controls"
    assert body["is_active"] is True
    assert "id" in body

    list_response = test_client.get("/api/v1/configurations")
    assert list_response.status_code == 200
    listing = list_response.json()
    assert listing["total"] == 1
    assert listing["items"][0]["config_key"] == "feature.flag"
    assert "next_cursor" in listing


def test_update_configuration_and_history(test_client: TestClient) -> None:
    create_resp = test_client.post("/api/v1/configurations", json=_create_payload("queue.config"))
    config_id = create_resp.json()["id"]

    update_payload = {
        "config_data": {"size": 25},
        "description": "Queue size tuning",
        "change_reason": "Increase capacity",
    }
    update_resp = test_client.patch(f"/api/v1/configurations/{config_id}", json=update_payload)
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["config_data"]["size"] == 25
    assert updated["description"] == "Queue size tuning"

    history_resp = test_client.get(f"/api/v1/configurations/{config_id}/history")
    assert history_resp.status_code == 200
    history = history_resp.json()
    assert history["total"] == 2
    assert history["items"][-1]["new_value"]["config_data"]["size"] == 25
    assert history["items"][-1]["change_reason"] == "Increase capacity"


def test_delete_configuration_soft_delete(test_client: TestClient) -> None:
    create_resp = test_client.post("/api/v1/configurations", json=_create_payload("legacy.setting"))
    config_id = create_resp.json()["id"]

    delete_resp = test_client.delete(
        f"/api/v1/configurations/{config_id}",
        params={"reason": "Sunset legacy pathway"},
    )
    assert delete_resp.status_code == 200
    deleted = delete_resp.json()
    assert deleted["is_active"] is False


def test_create_configuration_rejects_invalid_payload(test_client: TestClient) -> None:
    response = test_client.post(
        "/api/v1/configurations",
        json={
            "config_key": "smtp.settings",
            "config_data": {"port": 2525},
            "description": "Missing SMTP host",
        },
    )
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "smtp.settings" in detail
    assert "host" in detail

    active_list = test_client.get("/api/v1/configurations", params={"is_active": True})
    assert active_list.status_code == 200
    assert active_list.json()["total"] == 0

    all_list = test_client.get("/api/v1/configurations", params={"include_inactive": True})
    assert all_list.status_code == 200
    assert all_list.json()["total"] == 0
