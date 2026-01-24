"""
Tests for regression Celery tasks (TASK-339).
"""

from __future__ import annotations

import asyncio
import os
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/testdb")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("JWT_SECRET_KEY", "dummy-secret-key-123456")
os.environ.setdefault("SOUNDHOUND_API_KEY", "test-soundhound-key")
os.environ.setdefault("SOUNDHOUND_CLIENT_ID", "test-soundhound-client")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test-aws-key")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test-aws-secret")

from tasks import regression


def test_run_regression_suite_returns_disabled_when_flag_off(monkeypatch: pytest.MonkeyPatch):
    settings = SimpleNamespace(ENABLE_AUTO_REGRESSION=False)
    monkeypatch.setattr(regression, "get_settings", lambda: settings)

    result = regression.run_regression_suite(trigger="nightly")

    assert result == {"status": "disabled", "reason": "automation disabled"}


def _run_sync(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class _SessionContext:
    def __init__(self, session):
        self._session = session

    async def __aenter__(self):
        return self._session

    async def __aexit__(self, exc_type, exc, tb):
        return False


def test_run_regression_suite_invokes_executor(monkeypatch: pytest.MonkeyPatch):
    settings = SimpleNamespace(ENABLE_AUTO_REGRESSION=True, REGRESSION_SUITE_IDS=[])
    monkeypatch.setattr(regression, "get_settings", lambda: settings)

    session = AsyncMock()
    monkeypatch.setattr(regression, "SessionLocal", lambda: _SessionContext(session))

    executor_instance = SimpleNamespace(
        execute=AsyncMock(return_value={"status": "scheduled", "runs": []})
    )
    executor_cls = MagicMock(return_value=executor_instance)
    monkeypatch.setattr(regression, "RegressionSuiteExecutor", executor_cls)

    monkeypatch.setattr(regression.asyncio, "run", _run_sync)

    result = regression.run_regression_suite(trigger="nightly", metadata={"source": "cron"})

    executor_cls.assert_called_once_with(db=session, settings=settings)
    executor_instance.execute.assert_awaited_once_with(
        trigger="nightly",
        metadata={"source": "cron"},
    )
    assert result["status"] == "scheduled"
    assert result["trigger"] == "nightly"
