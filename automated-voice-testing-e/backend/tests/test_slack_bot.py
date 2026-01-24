"""
Tests for the Slack bot command handler (TASK-330).

Ensures the bot can:
  * Provide a concise system status summary.
  * Trigger a new test run for a suite and report back with identifiers.
  * List recent open defects with severity context.
  * Surface helpful feedback for missing arguments or unknown commands.
"""

from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

import pytest
from unittest.mock import AsyncMock

from integrations.slack.bot import SlackBot


@pytest.mark.asyncio
async def test_status_command_returns_health_snapshot():
    dashboard_snapshot = {
        "kpis": {
            "tests_executed": 128,
            "system_health_pct": 94.5,
            "issues_detected": 3,
            "avg_response_time_ms": 320.4,
        },
        "updated_at": "2025-01-01T12:00:00Z",
    }

    dashboard_service = SimpleNamespace(
        get_dashboard_snapshot=AsyncMock(return_value=dashboard_snapshot)
    )
    orchestration_service = SimpleNamespace()
    defect_service = SimpleNamespace()

    bot = SlackBot(
        dashboard_service=dashboard_service,
        orchestration_service=orchestration_service,
        defect_service=defect_service,
    )

    db = object()
    response = await bot.handle_command(
        db=db,
        text="/voiceai status",
    )

    dashboard_service.get_dashboard_snapshot.assert_awaited_once_with(db, time_range="24h")
    assert response["response_type"] == "ephemeral"
    text = response["text"]
    assert "System health: 94.5%" in text
    assert "Tests executed: 128" in text
    assert "Issues detected: 3" in text
    assert "Avg response: 320.4ms" in text


@pytest.mark.asyncio
async def test_run_command_triggers_test_run(monkeypatch):
    suite_id = uuid4()
    created_run = SimpleNamespace(id=uuid4(), total_tests=42)

    orchestration_service = SimpleNamespace(
        create_test_run=AsyncMock(return_value=created_run),
        schedule_test_executions=AsyncMock(return_value={"scheduled_count": 42}),
    )
    dashboard_service = SimpleNamespace()
    defect_service = SimpleNamespace()

    bot = SlackBot(
        dashboard_service=dashboard_service,
        orchestration_service=orchestration_service,
        defect_service=defect_service,
    )

    db = object()
    response = await bot.handle_command(
        db=db,
        text=f"/voiceai run {suite_id}",
    )

    orchestration_service.create_test_run.assert_awaited_once_with(
        db,
        suite_id=suite_id,
        trigger_type="slack_command",
        trigger_metadata={"channel": None, "user_id": None},
    )
    assert response["response_type"] == "in_channel"
    assert str(created_run.id) in response["text"]
    orchestration_service.schedule_test_executions.assert_awaited_once_with(db, created_run.id)


@pytest.mark.asyncio
async def test_run_command_requires_suite_argument():
    bot = SlackBot(
        dashboard_service=SimpleNamespace(),
        orchestration_service=SimpleNamespace(),
        defect_service=SimpleNamespace(),
    )

    response = await bot.handle_command(db=object(), text="/voiceai run")
    assert response["response_type"] == "ephemeral"
    assert "Provide a suite ID" in response["text"]


@pytest.mark.asyncio
async def test_defects_command_lists_open_defects():
    defects = [
        SimpleNamespace(title="Critical ASR failure", severity="critical", status="open"),
        SimpleNamespace(title="Latency regression", severity="high", status="open"),
    ]

    defect_service = SimpleNamespace(
        list_defects=AsyncMock(return_value=(defects, len(defects)))
    )
    bot = SlackBot(
        dashboard_service=SimpleNamespace(),
        orchestration_service=SimpleNamespace(),
        defect_service=defect_service,
    )

    db = object()
    response = await bot.handle_command(db=db, text="/voiceai defects")

    defect_service.list_defects.assert_awaited_once_with(
        db,
        {"status": "open"},
        {"skip": 0, "limit": 5},
    )
    assert response["response_type"] == "ephemeral"
    text = response["text"]
    assert "Critical ASR failure" in text
    assert "Latency regression" in text
    assert "2 open defects" in text


@pytest.mark.asyncio
async def test_unknown_command_returns_help():
    bot = SlackBot(
        dashboard_service=SimpleNamespace(),
        orchestration_service=SimpleNamespace(),
        defect_service=SimpleNamespace(),
    )

    response = await bot.handle_command(db=object(), text="/voiceai unknown")
    assert "status" in response["text"]
    assert response["response_type"] == "ephemeral"
