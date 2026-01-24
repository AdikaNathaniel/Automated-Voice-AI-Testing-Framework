"""
Unit tests for the regression suite executor service (TASK-339).
"""

from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

import pytest

from services.regression_suite_executor import RegressionSuiteExecutor


def _settings(enabled: bool = True, suite_ids: list[str] | None = None) -> SimpleNamespace:
    return SimpleNamespace(
        ENABLE_AUTO_REGRESSION=enabled,
        REGRESSION_SUITE_IDS=suite_ids or [],
    )


@pytest.mark.asyncio
async def test_executor_returns_disabled_when_feature_flag_off():
    run_creator = AsyncMock()
    executor = RegressionSuiteExecutor(
        db=AsyncMock(),
        settings=_settings(enabled=False),
        run_creator=run_creator,
    )

    result = await executor.execute(trigger="deployment", metadata={})

    assert result == {"status": "disabled"}
    run_creator.assert_not_awaited()


@pytest.mark.asyncio
async def test_executor_skips_when_no_regression_suites(monkeypatch: pytest.MonkeyPatch):
    run_creator = AsyncMock()
    executor = RegressionSuiteExecutor(
        db=AsyncMock(),
        settings=_settings(),
        run_creator=run_creator,
    )
    monkeypatch.setattr(
        executor,
        "_fetch_regression_suite_ids_from_db",
        AsyncMock(return_value=[]),
    )

    result = await executor.execute(trigger="deployment", metadata=None)

    assert result["status"] == "skipped"
    assert result["reason"] == "no_regression_suites"
    run_creator.assert_not_awaited()


@pytest.mark.asyncio
async def test_executor_creates_test_runs_for_resolved_suites():
    suite_id = uuid4()
    run = SimpleNamespace(id=uuid4(), total_tests=15)
    run_creator = AsyncMock(return_value=run)

    executor = RegressionSuiteExecutor(
        db=AsyncMock(),
        settings=_settings(),
        run_creator=run_creator,
    )

    result = await executor.execute(
        trigger="deployment",
        metadata={
            "provider": "github",
            "regression_suite_ids": [str(suite_id)],
            "additional": {"branch": "main"},
        },
    )

    run_creator.assert_awaited_once()
    kwargs = run_creator.await_args.kwargs
    assert kwargs["suite_id"] == suite_id
    assert kwargs["trigger_type"] == "auto:deployment"
    assert kwargs["trigger_metadata"]["trigger"] == "deployment"
    assert kwargs["trigger_metadata"]["suite_ids"] == [str(suite_id)]
    assert kwargs["trigger_metadata"]["source"]["provider"] == "github"

    assert result["status"] == "scheduled"
    assert result["trigger"] == "deployment"
    assert result["runs"][0]["suite_id"] == str(suite_id)
    assert result["runs"][0]["test_run_id"] == str(run.id)
    assert result["runs"][0]["total_tests"] == 15


@pytest.mark.asyncio
async def test_executor_resolves_suites_from_settings(monkeypatch: pytest.MonkeyPatch):
    suite_id = uuid4()
    run_creator = AsyncMock(return_value=SimpleNamespace(id=uuid4(), total_tests=None))

    executor = RegressionSuiteExecutor(
        db=AsyncMock(),
        settings=_settings(suite_ids=[str(suite_id)]),
        run_creator=run_creator,
    )
    monkeypatch.setattr(
        executor,
        "_fetch_regression_suite_ids_from_db",
        AsyncMock(return_value=[]),
    )

    await executor.execute(trigger="nightly", metadata=None)

    run_creator.assert_awaited_once()
    assert run_creator.await_args.kwargs["suite_id"] == suite_id
    assert run_creator.await_args.kwargs["trigger_type"] == "auto:nightly"


@pytest.mark.asyncio
async def test_fetch_regression_suite_ids_queries_active_regression_suites():
    suite_ids = [uuid4(), uuid4()]

    result = MagicMock()
    result.scalars.return_value.all.return_value = suite_ids

    db = AsyncMock()
    db.execute.return_value = result

    executor = RegressionSuiteExecutor(
        db=db,
        settings=_settings(),
        run_creator=AsyncMock(),
    )

    resolved = await executor._fetch_regression_suite_ids_from_db()

    assert resolved == suite_ids

    db.execute.assert_awaited()
