"""
Unit tests for webhook service deployment-triggered regression execution (TASK-339).
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from services import webhook_service


def _settings(enabled: bool) -> SimpleNamespace:
    return SimpleNamespace(
        ENABLE_AUTO_REGRESSION=enabled,
        REGRESSION_SUITE_IDS=[],
    )


@pytest.mark.asyncio
async def test_dispatch_event_triggers_regression_executor_on_deployment(monkeypatch: pytest.MonkeyPatch):
    settings = _settings(enabled=True)
    monkeypatch.setattr(webhook_service, "get_settings", lambda: settings)

    orchestrator = AsyncMock()
    monkeypatch.setattr(
        webhook_service.orchestration_service,
        "create_test_run",
        orchestrator,
    )

    executor_instance = SimpleNamespace(execute=AsyncMock(return_value={"status": "scheduled"}))
    executor_cls = MagicMock(return_value=executor_instance)
    monkeypatch.setattr(webhook_service, "RegressionSuiteExecutor", executor_cls)

    db = AsyncMock()
    payload = {"status": "success"}

    await webhook_service.dispatch_ci_cd_event(
        provider="github",
        event_type="deployment",
        payload=payload,
        db=db,
    )

    executor_cls.assert_called_once_with(db=db, settings=settings)
    executor_instance.execute.assert_awaited_once()
    kwargs = executor_instance.execute.await_args.kwargs
    assert kwargs["trigger"] == "deployment"
    assert kwargs["metadata"]["provider"] == "github"
    assert kwargs["metadata"]["event_type"] == "deployment"


@pytest.mark.asyncio
async def test_dispatch_event_skips_regression_when_disabled(monkeypatch: pytest.MonkeyPatch):
    settings = _settings(enabled=False)
    monkeypatch.setattr(webhook_service, "get_settings", lambda: settings)

    orchestrator = AsyncMock()
    monkeypatch.setattr(
        webhook_service.orchestration_service,
        "create_test_run",
        orchestrator,
    )

    executor_cls = MagicMock()
    monkeypatch.setattr(webhook_service, "RegressionSuiteExecutor", executor_cls)

    db = AsyncMock()

    await webhook_service.dispatch_ci_cd_event(
        provider="github",
        event_type="deployment",
        payload={"status": "success"},
        db=db,
    )

    executor_cls.assert_not_called()


@pytest.mark.asyncio
async def test_dispatch_event_skips_regression_for_non_deployment(monkeypatch: pytest.MonkeyPatch):
    settings = _settings(enabled=True)
    monkeypatch.setattr(webhook_service, "get_settings", lambda: settings)

    orchestrator = AsyncMock()
    monkeypatch.setattr(
        webhook_service.orchestration_service,
        "create_test_run",
        orchestrator,
    )

    executor_cls = MagicMock()
    monkeypatch.setattr(webhook_service, "RegressionSuiteExecutor", executor_cls)

    db = AsyncMock()

    await webhook_service.dispatch_ci_cd_event(
        provider="github",
        event_type="push",
        payload={"status": "success"},
        db=db,
    )

    executor_cls.assert_not_called()
