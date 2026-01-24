"""
Tests for dashboard caching and invalidation logic.
"""

from __future__ import annotations

# Minimal configuration so settings can load during tests.
import os

os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/testdb")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("JWT_SECRET_KEY", "supersecretkey1234")
os.environ.setdefault("SOUNDHOUND_API_KEY", "test-key")
os.environ.setdefault("SOUNDHOUND_CLIENT_ID", "test-client")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test-access")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test-secret")

import json
from typing import Dict
from unittest.mock import AsyncMock

import pytest

from services import dashboard_service


class FakeRedis:
    """Minimal async Redis stand-in for caching tests."""

    def __init__(self) -> None:
        self.store: Dict[str, str] = {}
        self.ttl: Dict[str, int | None] = {}

    async def get(self, key: str) -> str | None:
        return self.store.get(key)

    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        self.store[key] = value
        self.ttl[key] = ttl

    async def delete(self, key: str) -> int:
        existed = key in self.store
        self.store.pop(key, None)
        self.ttl.pop(key, None)
        return 1 if existed else 0


def _patch_redis(monkeypatch: pytest.MonkeyPatch, fake_redis: FakeRedis) -> None:
    async def fake_get_redis():
        yield fake_redis

    monkeypatch.setattr("services.dashboard_service.get_redis", fake_get_redis)


@pytest.mark.asyncio
async def test_dashboard_snapshot_uses_cache(monkeypatch: pytest.MonkeyPatch):
    fake_redis = FakeRedis()
    _patch_redis(monkeypatch, fake_redis)

    compute = AsyncMock(return_value={"value": 1})
    monkeypatch.setattr("services.dashboard_service._compute_dashboard_snapshot", compute)

    first = await dashboard_service.get_dashboard_snapshot(db=None, time_range="24h")
    second = await dashboard_service.get_dashboard_snapshot(db=None, time_range="24h")

    assert first == {"value": 1}
    assert second == {"value": 1}
    assert compute.await_count == 1
    cache_key = "dashboard:snapshot:24h"
    assert fake_redis.ttl[cache_key] == 300
    # Ensure serialized payload stored in redis.
    assert json.loads(fake_redis.store[cache_key]) == {"value": 1}


@pytest.mark.asyncio
async def test_invalidate_dashboard_cache(monkeypatch: pytest.MonkeyPatch):
    fake_redis = FakeRedis()
    _patch_redis(monkeypatch, fake_redis)

    compute = AsyncMock(side_effect=[{"value": 1}, {"value": 2}])
    monkeypatch.setattr("services.dashboard_service._compute_dashboard_snapshot", compute)

    first = await dashboard_service.get_dashboard_snapshot(db=None, time_range="24h")
    assert first == {"value": 1}
    assert compute.await_count == 1

    await dashboard_service.invalidate_dashboard_cache("24h")
    second = await dashboard_service.get_dashboard_snapshot(db=None, time_range="24h")

    assert second == {"value": 2}
    assert compute.await_count == 2


@pytest.mark.asyncio
async def test_invalidate_all_time_ranges(monkeypatch: pytest.MonkeyPatch):
    fake_redis = FakeRedis()
    _patch_redis(monkeypatch, fake_redis)

    compute = AsyncMock(
        side_effect=[
            {"value": "24h-first"},
            {"value": "7d-first"},
            {"value": "24h-second"},
            {"value": "7d-second"},
        ]
    )
    monkeypatch.setattr("services.dashboard_service._compute_dashboard_snapshot", compute)

    await dashboard_service.get_dashboard_snapshot(db=None, time_range="24h")
    await dashboard_service.get_dashboard_snapshot(db=None, time_range="7d")
    assert compute.await_count == 2

    await dashboard_service.invalidate_dashboard_cache()

    result_24h = await dashboard_service.get_dashboard_snapshot(db=None, time_range="24h")
    result_7d = await dashboard_service.get_dashboard_snapshot(db=None, time_range="7d")

    assert result_24h == {"value": "24h-second"}
    assert result_7d == {"value": "7d-second"}
    assert compute.await_count == 4
