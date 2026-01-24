"""
Tests for the integration health monitoring service (TASK-335).

These tests describe the desired behaviour before the implementation exists:
  * Aggregating per-integration check results into a unified report.
  * Triggering system alerts when any integration reports a failure.
  * Capturing uncaught exceptions as critical failures with helpful metadata.
"""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Dict, List
from unittest.mock import AsyncMock

import pytest

from services.integration_health_service import (
    IntegrationCheckResult,
    IntegrationHealthReport,
    IntegrationHealthResult,
    IntegrationHealthService,
)


@pytest.mark.asyncio
async def test_run_checks_returns_detailed_report() -> None:
    """Each configured checker contributes a result and the overall status reflects the worst outcome."""

    async def slack_check() -> IntegrationCheckResult:
        return IntegrationCheckResult(
            integration="slack",
            status="healthy",
            detail="Webhook accepted payload",
            metadata={"latency_ms": 120},
        )

    async def jira_check() -> IntegrationCheckResult:
        return IntegrationCheckResult(
            integration="jira",
            status="degraded",
            detail="API responded with elevated latency",
            metadata={"latency_ms": 820},
        )

    fixed_now = datetime(2024, 2, 1, 12, 0, tzinfo=timezone.utc)

    service = IntegrationHealthService(
        checkers={
            "slack": slack_check,
            "jira": jira_check,
        },
        notification_service=None,
        clock=lambda: fixed_now,
    )

    report = await service.run_checks()

    assert isinstance(report, IntegrationHealthReport)
    assert report.status == "degraded"
    assert report.checked_at == fixed_now

    results: List[IntegrationHealthResult] = report.results
    assert {result.integration for result in results} == {"slack", "jira"}

    slack_result = _result_by_integration(results, "slack")
    assert slack_result.status == "healthy"
    assert slack_result.detail == "Webhook accepted payload"
    assert slack_result.metadata == {"latency_ms": 120}
    assert slack_result.checked_at == fixed_now

    jira_result = _result_by_integration(results, "jira")
    assert jira_result.status == "degraded"
    assert "elevated latency" in jira_result.detail
    assert jira_result.metadata["latency_ms"] == 820
    assert jira_result.checked_at == fixed_now


@pytest.mark.asyncio
async def test_run_checks_triggers_alert_on_failure() -> None:
    """Non-healthy results should trigger a system alert with context."""

    async def slack_check() -> IntegrationCheckResult:
        return IntegrationCheckResult(
            integration="slack",
            status="healthy",
            detail="Webhook operational",
        )

    async def github_check() -> IntegrationCheckResult:
        return IntegrationCheckResult(
            integration="github",
            status="critical",
            detail="Commit status endpoint returned 500",
            metadata={"status_code": 500},
        )

    notifier = SimpleNamespace(
        notify_system_alert=AsyncMock()
    )
    fixed_now = datetime(2024, 2, 1, 13, 0, tzinfo=timezone.utc)

    service = IntegrationHealthService(
        checkers={"slack": slack_check, "github": github_check},
        notification_service=notifier,
        clock=lambda: fixed_now,
    )

    report = await service.run_checks()

    assert report.status == "critical"
    notifier.notify_system_alert.assert_awaited_once()
    kwargs = notifier.notify_system_alert.await_args.kwargs
    assert kwargs["severity"] == "critical"
    assert "Integration health check" in kwargs["title"]
    assert "github" in kwargs["message"].lower()
    assert "500" in kwargs["message"]


@pytest.mark.asyncio
async def test_run_checks_marks_critical_on_exception() -> None:
    """Unhandled checker exceptions are converted into critical failures."""

    async def jira_check() -> IntegrationCheckResult:
        raise RuntimeError("Authentication failed")

    fixed_now = datetime(2024, 2, 1, 14, 0, tzinfo=timezone.utc)

    service = IntegrationHealthService(
        checkers={"jira": jira_check},
        notification_service=None,
        clock=lambda: fixed_now,
    )

    report = await service.run_checks()

    assert report.status == "critical"
    jira_result = _result_by_integration(report.results, "jira")
    assert jira_result.status == "critical"
    assert "Authentication failed" in jira_result.detail
    assert jira_result.metadata["exception_type"] == "RuntimeError"
    assert jira_result.checked_at == fixed_now


def _result_by_integration(
    results: List[IntegrationHealthResult],
    integration: str,
) -> IntegrationHealthResult:
    lookup: Dict[str, IntegrationHealthResult] = {result.integration: result for result in results}
    return lookup[integration]

