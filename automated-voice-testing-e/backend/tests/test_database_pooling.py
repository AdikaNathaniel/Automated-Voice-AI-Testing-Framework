"""
Tests for database engine connection pooling configuration.
"""

from __future__ import annotations

import importlib
import sys
from types import SimpleNamespace
from typing import Any, Dict

import pytest


@pytest.fixture()
def minimal_env(monkeypatch):
    """Provide required environment variables for Settings."""
    env_values = {
        "DATABASE_URL": "postgresql://user:pass@localhost:5432/test_db",
        "REDIS_URL": "redis://localhost:6379/0",
        "JWT_SECRET_KEY": "super-secret-key-123",
        "SOUNDHOUND_API_KEY": "api-key",
        "SOUNDHOUND_CLIENT_ID": "client-id",
        "AWS_ACCESS_KEY_ID": "access-key",
        "AWS_SECRET_ACCESS_KEY": "secret",
        "DB_POOL_SIZE": "8",
        "DB_MAX_OVERFLOW": "12",
        "DB_POOL_TIMEOUT": "45",
        "DB_POOL_RECYCLE": "7200",
    }
    for key, value in env_values.items():
        monkeypatch.setenv(key, value)


def _reload_database(monkeypatch, create_engine_stub) -> Any:
    """Reload the api.database module with patched create_async_engine."""
    from sqlalchemy.ext import asyncio as sa_asyncio

    monkeypatch.setattr(sa_asyncio, "create_async_engine", create_engine_stub)

    if "api.database" in sys.modules:
        del sys.modules["api.database"]

    return importlib.import_module("api.database")


@pytest.mark.asyncio
async def test_engine_uses_configured_pool_parameters(monkeypatch, minimal_env):
    captured: Dict[str, Any] = {}

    async def fake_dispose() -> None:  # pragma: no cover - exercised in tests
        captured["disposed"] = True

    def fake_create_async_engine(url: str, **kwargs: Any):
        captured["url"] = url
        captured["kwargs"] = kwargs
        return SimpleNamespace(dispose=fake_dispose)

    module = _reload_database(monkeypatch, fake_create_async_engine)

    assert captured["url"] == "postgresql+asyncpg://user:pass@localhost:5432/test_db"

    expected = {
        "echo": module.settings.DEBUG,
        "future": True,
        "pool_size": module.settings.DB_POOL_SIZE,
        "max_overflow": module.settings.DB_MAX_OVERFLOW,
        "pool_timeout": module.settings.DB_POOL_TIMEOUT,
        "pool_recycle": module.settings.DB_POOL_RECYCLE,
        "pool_pre_ping": True,
    }
    assert captured["kwargs"] == expected

    # Ensure dispose wraps underlying engine
    await module.dispose_engine()
    assert captured.get("disposed") is True
