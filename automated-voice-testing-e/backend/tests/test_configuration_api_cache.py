"""
Tests ensuring configuration API responses are cached and invalidated.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any, AsyncGenerator, Dict, List
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

# Ensure environment variables for app startup.
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
from api.config import get_settings


class FakeRedis:
    def __init__(self) -> None:
        self.store: Dict[str, str] = {}
        self.ttl: Dict[str, int | None] = {}
        self.client = self

    async def get(self, key: str) -> str | None:
        return self.store.get(key)

    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        self.store[key] = value
        self.ttl[key] = ttl

    async def delete(self, *keys: str) -> int:
        deleted = 0
        for key in keys:
            if key in self.store:
                deleted += 1
            self.store.pop(key, None)
            self.ttl.pop(key, None)
        return deleted

    async def keys(self, pattern: str) -> List[str]:
        from fnmatch import fnmatch

        return [key for key in self.store if fnmatch(key, pattern)]


@pytest.fixture()
def client() -> TestClient:
    async def override_get_db() -> AsyncGenerator[None, None]:
        yield None

    fake_user = SimpleNamespace(id=uuid4(), is_active=True, role="admin", tenant_id=None)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user_with_db] = lambda: fake_user

    test_client = TestClient(app)

    try:
        yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_current_user_with_db, None)


def _patch_redis(monkeypatch: pytest.MonkeyPatch, fake_redis: FakeRedis) -> None:
    async def fake_get_redis():
        yield fake_redis

    for target in [
        "api.routes.configurations.get_redis",
        "api.rate_limit.get_redis",
        "api.redis_client.get_redis",
    ]:
        try:
            monkeypatch.setattr(target, fake_get_redis)
        except AttributeError:
            continue


def _sample_configuration(key: str = "feature.flag", description: str = "Initial") -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    return {
        "id": uuid4(),
        "config_key": key,
        "config_data": {"enabled": True},
        "description": description,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }


def _create_payload(key: str = "feature.flag") -> Dict[str, Any]:
    return {
        "config_key": key,
        "config_data": {"enabled": True},
        "description": "Created via API",
        "is_active": True,
    }


def test_configuration_list_uses_cache(monkeypatch: pytest.MonkeyPatch, client: TestClient) -> None:
    fake_redis = FakeRedis()
    _patch_redis(monkeypatch, fake_redis)
    settings = get_settings()

    list_calls = {"count": 0}

    async def fake_run_in_sync(db, func, *args, **kwargs):
        assert func.__name__ == "list_configurations"
        list_calls["count"] += 1
        limit = kwargs.get("limit", 50)
        return (
            [_sample_configuration()],
            {"next_cursor": "cursor-conf", "limit": limit, "total": 1},
        )

    monkeypatch.setattr("api.routes.configurations._run_in_sync", fake_run_in_sync)

    first = client.get("/api/v1/configurations")
    second = client.get("/api/v1/configurations")

    assert first.status_code == 200
    assert second.status_code == 200
    assert list_calls["count"] == 1
    assert first.json()["next_cursor"] == "cursor-conf"

    cached_keys = [key for key in fake_redis.store if key.startswith("api:configurations:list:")]
    assert len(cached_keys) == 1
    cache_key = cached_keys[0]
    assert cache_key.startswith("api:configurations:list:")
    assert fake_redis.ttl[cache_key] == settings.CACHE_TTL


def test_configuration_mutation_invalidates_cache(monkeypatch: pytest.MonkeyPatch, client: TestClient) -> None:
    fake_redis = FakeRedis()
    _patch_redis(monkeypatch, fake_redis)

    list_responses = [
        (
            [_sample_configuration(description="Listed-1")],
            {"next_cursor": "cursor-1", "limit": 50, "total": 2},
        ),
        (
            [_sample_configuration(description="Listed-2")],
            {"next_cursor": "cursor-2", "limit": 50, "total": 2},
        ),
    ]
    list_calls = {"count": 0}

    async def fake_run_in_sync(db, func, *args, **kwargs):
        name = func.__name__
        if name == "list_configurations":
            list_calls["count"] += 1
            return list_responses.pop(0)
        if name == "create_configuration":
            return _sample_configuration(description="Created")
        raise AssertionError(f"Unexpected call to {name}")

    monkeypatch.setattr("api.routes.configurations._run_in_sync", fake_run_in_sync)

    first = client.get("/api/v1/configurations")
    assert first.status_code == 200

    second = client.get("/api/v1/configurations")
    assert second.status_code == 200
    assert list_calls["count"] == 1
    cached_keys = [key for key in fake_redis.store if key.startswith("api:configurations:list:")]
    assert len(cached_keys) == 1

    create_payload = _create_payload("another.flag")
    created = client.post("/api/v1/configurations", json=create_payload)
    assert created.status_code == 201
    assert not any(key.startswith("api:configurations:list:") for key in fake_redis.store)

    third = client.get("/api/v1/configurations")
    assert third.status_code == 200
    assert list_calls["count"] == 2
    cached_keys = [key for key in fake_redis.store if key.startswith("api:configurations:list:")]
    assert len(cached_keys) == 1


def test_configuration_field_selection(monkeypatch: pytest.MonkeyPatch, client: TestClient) -> None:
    fake_redis = FakeRedis()
    _patch_redis(monkeypatch, fake_redis)

    sample = _sample_configuration()
    list_calls = {"count": 0}

    async def fake_run_in_sync(db, func, *args, **kwargs):
        name = func.__name__
        if name == "list_configurations":
            list_calls["count"] += 1
            limit = kwargs.get("limit", 50)
            return [sample], {"next_cursor": None, "limit": limit, "total": 1}
        raise AssertionError(name)

    monkeypatch.setattr("api.routes.configurations._run_in_sync", fake_run_in_sync)

    response = client.get("/api/v1/configurations?fields=id,config_key")

    assert response.status_code == 200
    payload = response.json()
    assert payload["items"] == [{"id": str(sample["id"]), "config_key": sample["config_key"]}]
    assert list_calls["count"] == 1
