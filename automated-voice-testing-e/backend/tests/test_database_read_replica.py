"""
Tests ensuring database read replica routing is configured correctly.
"""

from __future__ import annotations

import importlib
import sys
from types import SimpleNamespace
from typing import Any, List

import pytest
from sqlalchemy import Column, Integer, MetaData, Table, insert, select


@pytest.fixture()
def base_env(monkeypatch):
    """Provide minimum environment for settings."""
    env_values = {
        "DATABASE_URL": "postgresql://user:pass@primary:5432/test_db",
        "REDIS_URL": "redis://localhost:6379/0",
        "JWT_SECRET_KEY": "super-secret-key-123",
        "SOUNDHOUND_API_KEY": "api-key",
        "SOUNDHOUND_CLIENT_ID": "client-id",
        "AWS_ACCESS_KEY_ID": "access-key",
        "AWS_SECRET_ACCESS_KEY": "secret",
    }
    for key, value in env_values.items():
        monkeypatch.setenv(key, value)


@pytest.fixture()
def env_with_replica(monkeypatch, base_env):
    """Add read replica URL to base environment."""
    monkeypatch.setenv(
        "READ_REPLICA_URL",
        "postgresql://user:pass@replica:5432/test_db_read",
    )


def _reload_database(monkeypatch, engines: List[Any]):
    """Reload api.database with patched create_async_engine."""
    from sqlalchemy.ext import asyncio as sa_asyncio

    def fake_create_async_engine(url: str, **kwargs: Any):
        engine = SimpleNamespace(
            url=url,
            kwargs=kwargs,
            sync_engine=SimpleNamespace(name=url),
        )

        async def dispose() -> None:  # pragma: no cover - exercised by callers
            engine.disposed = True  # type: ignore[attr-defined]

        engine.dispose = dispose  # type: ignore[attr-defined]
        engines.append(engine)
        return engine

    monkeypatch.setattr(sa_asyncio, "create_async_engine", fake_create_async_engine)

    # Ensure fresh settings for each reload
    import api.config as config_module

    if hasattr(config_module.get_settings, "cache_clear"):
        config_module.get_settings.cache_clear()

    for module_name in ["api.database"]:
        sys.modules.pop(module_name, None)

    return importlib.import_module("api.database")


@pytest.mark.asyncio
async def test_select_queries_use_replica_when_configured(monkeypatch, env_with_replica):
    engines: List[Any] = []
    module = _reload_database(monkeypatch, engines)

    assert len(engines) == 2, "Expected primary and replica engines to be created"
    primary_engine, replica_engine = engines

    # Ensure replica engine is exposed
    assert module.replica_engine is not None

    # Use session to inspect routing decisions
    async with module.SessionLocal() as session:
        # SELECT should be routed to replica engine
        bind = session.sync_session.get_bind(clause=select(1))
        assert bind is replica_engine.sync_engine

        # INSERT should continue to use primary engine
        metadata = MetaData()
        example = Table("example", metadata, Column("id", Integer, primary_key=True))
        bind = session.sync_session.get_bind(clause=insert(example))
        assert bind is primary_engine.sync_engine


@pytest.mark.asyncio
async def test_reads_fall_back_to_primary_without_replica(monkeypatch, base_env):
    engines: List[Any] = []
    # Ensure replica env var is not set
    monkeypatch.delenv("READ_REPLICA_URL", raising=False)

    module = _reload_database(monkeypatch, engines)

    assert len(engines) == 1, "Only primary engine should be created without replica"
    primary_engine = engines[0]
    assert module.replica_engine is None

    async with module.SessionLocal() as session:
        bind = session.sync_session.get_bind(clause=select(1))
        assert bind is primary_engine.sync_engine
