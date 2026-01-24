"""
Tests for NotificationService orchestrating multiple notification channels.
"""

import pytest
from unittest.mock import AsyncMock

from integrations.slack.client import SlackClientError
from services.notification_service import (
    NotificationService,
    NotificationServiceError,
)


@pytest.mark.asyncio
async def test_notify_test_run_notifies_slack_and_github():
    """NotificationService sends run status to both Slack and GitHub when available."""
    slack_client = AsyncMock()
    github_client = AsyncMock()

    service = NotificationService(
        slack_client=slack_client,
        github_client=github_client,
    )

    await service.notify_test_run_result(
        status="success",
        passed=10,
        failed=0,
        duration_seconds=65.5,
        run_url="https://ci.example.com/runs/123",
        commit_sha="abc123",
        github_context="ci/tests",
    )

    slack_client.send_test_run_notification.assert_awaited_once_with(
        status="success",
        passed=10,
        failed=0,
        duration_seconds=65.5,
        run_url="https://ci.example.com/runs/123",
    )
    github_client.set_commit_status.assert_awaited_once_with(
        sha="abc123",
        state="success",
        target_url="https://ci.example.com/runs/123",
        description="10 passed, 0 failed",
        context="ci/tests",
    )


@pytest.mark.asyncio
async def test_notify_test_run_handles_optional_channels():
    """NotificationService skips channels that are not configured."""
    slack_client = AsyncMock()
    service = NotificationService(slack_client=slack_client)

    await service.notify_test_run_result(
        status="failure",
        passed=5,
        failed=2,
        duration_seconds=90.0,
        run_url="https://ci.example.com/runs/456",
    )

    slack_client.send_test_run_notification.assert_awaited_once()


@pytest.mark.asyncio
async def test_notify_test_run_raises_notification_error_on_failure():
    """Errors from underlying clients are surfaced as NotificationServiceError."""
    slack_client = AsyncMock()
    slack_client.send_test_run_notification.side_effect = SlackClientError("Slack failure")

    service = NotificationService(slack_client=slack_client)

    with pytest.raises(NotificationServiceError) as exc:
        await service.notify_test_run_result(
            status="success",
            passed=1,
            failed=1,
            duration_seconds=30.0,
            run_url="https://ci.example.com/runs/789",
        )

    assert "Slack failure" in str(exc.value)


@pytest.mark.asyncio
async def test_notify_critical_defect_notifies_slack():
    """Critical defect notifications are forwarded to Slack client."""
    slack_client = AsyncMock()
    service = NotificationService(slack_client=slack_client)

    await service.notify_critical_defect(
        defect_id="def-123",
        title="Wake word misdetection",
        severity="critical",
        defect_url="https://app.example.com/defects/def-123",
        description="System fails to wake up in noisy café.",
    )

    slack_client.send_critical_defect_alert.assert_awaited_once_with(
        defect_id="def-123",
        title="Wake word misdetection",
        severity="critical",
        defect_url="https://app.example.com/defects/def-123",
        description="System fails to wake up in noisy café.",
    )


@pytest.mark.asyncio
async def test_notify_system_alert_notifies_slack():
    """System alerts are forwarded to Slack client."""
    slack_client = AsyncMock()
    service = NotificationService(slack_client=slack_client)

    await service.notify_system_alert(
        severity="critical",
        title="Database outage",
        message="Primary database unreachable for 5 minutes.",
        alert_url="https://status.example.com/incidents/db",
    )

    slack_client.send_system_alert.assert_awaited_once_with(
        severity="critical",
        title="Database outage",
        message="Primary database unreachable for 5 minutes.",
        alert_url="https://status.example.com/incidents/db",
    )


@pytest.mark.asyncio
async def test_notify_system_alert_raises_on_slack_failure():
    """System alert errors surface as NotificationServiceError."""
    slack_client = AsyncMock()
    slack_client.send_system_alert.side_effect = SlackClientError("Slack not reachable")
    service = NotificationService(slack_client=slack_client)

    with pytest.raises(NotificationServiceError) as exc:
        await service.notify_system_alert(
            severity="critical",
            title="Database outage",
            message="Primary database unreachable for 5 minutes.",
            alert_url="https://status.example.com/incidents/db",
        )

    assert "Slack not reachable" in str(exc.value)


@pytest.mark.asyncio
async def test_notify_edge_case_created_sends_to_slack():
    """Edge case creation notifies Slack for high severity."""
    slack_client = AsyncMock()
    service = NotificationService(slack_client=slack_client)

    await service.notify_edge_case_created(
        edge_case_id="ec-123",
        title="Ambiguous intent detected",
        category="ambiguous_intent",
        severity="high",
        edge_case_url="https://app.example.com/edge-cases/ec-123",
        scenario_name="Morning Routine",
        description="User request was unclear",
    )

    slack_client.send_edge_case_alert.assert_awaited_once_with(
        edge_case_id="ec-123",
        title="Ambiguous intent detected",
        category="ambiguous_intent",
        severity="high",
        edge_case_url="https://app.example.com/edge-cases/ec-123",
        scenario_name="Morning Routine",
        description="User request was unclear",
        channel=None,
    )


@pytest.mark.asyncio
async def test_notify_edge_case_created_sends_for_critical_severity():
    """Critical severity edge cases trigger notification."""
    slack_client = AsyncMock()
    service = NotificationService(slack_client=slack_client)

    await service.notify_edge_case_created(
        edge_case_id="ec-456",
        title="System crash on input",
        category="system_error",
        severity="critical",
        edge_case_url="https://app.example.com/edge-cases/ec-456",
    )

    slack_client.send_edge_case_alert.assert_awaited_once()


@pytest.mark.asyncio
async def test_notify_edge_case_created_skips_low_severity():
    """Low severity edge cases do not trigger notification by default."""
    slack_client = AsyncMock()
    service = NotificationService(slack_client=slack_client)

    await service.notify_edge_case_created(
        edge_case_id="ec-789",
        title="Minor edge case",
        category="boundary_condition",
        severity="low",
        edge_case_url="https://app.example.com/edge-cases/ec-789",
    )

    slack_client.send_edge_case_alert.assert_not_awaited()


@pytest.mark.asyncio
async def test_notify_edge_case_created_skips_medium_severity():
    """Medium severity edge cases do not trigger notification by default."""
    slack_client = AsyncMock()
    service = NotificationService(slack_client=slack_client)

    await service.notify_edge_case_created(
        edge_case_id="ec-101",
        title="Moderate edge case",
        category="unusual_input",
        severity="medium",
        edge_case_url="https://app.example.com/edge-cases/ec-101",
    )

    slack_client.send_edge_case_alert.assert_not_awaited()


@pytest.mark.asyncio
async def test_notify_edge_case_created_force_sends_for_any_severity():
    """Force flag sends notification regardless of severity."""
    slack_client = AsyncMock()
    service = NotificationService(slack_client=slack_client)

    await service.notify_edge_case_created(
        edge_case_id="ec-102",
        title="Low priority but forced",
        category="boundary_condition",
        severity="low",
        edge_case_url="https://app.example.com/edge-cases/ec-102",
        force=True,
    )

    slack_client.send_edge_case_alert.assert_awaited_once()


@pytest.mark.asyncio
async def test_notify_edge_case_created_uses_custom_channel():
    """Custom channel is forwarded to Slack client."""
    slack_client = AsyncMock()
    service = NotificationService(slack_client=slack_client)

    await service.notify_edge_case_created(
        edge_case_id="ec-103",
        title="Edge case with custom channel",
        category="test",
        severity="high",
        edge_case_url="https://app.example.com/edge-cases/ec-103",
        channel="#custom-alerts",
    )

    slack_client.send_edge_case_alert.assert_awaited_once()
    call_kwargs = slack_client.send_edge_case_alert.call_args.kwargs
    assert call_kwargs["channel"] == "#custom-alerts"


@pytest.mark.asyncio
async def test_notify_edge_case_created_raises_on_slack_failure():
    """Slack failures surface as NotificationServiceError."""
    slack_client = AsyncMock()
    slack_client.send_edge_case_alert.side_effect = SlackClientError("Webhook failed")
    service = NotificationService(slack_client=slack_client)

    with pytest.raises(NotificationServiceError) as exc:
        await service.notify_edge_case_created(
            edge_case_id="ec-104",
            title="Edge case notification failure",
            category="test",
            severity="critical",
            edge_case_url="https://app.example.com/edge-cases/ec-104",
        )

    assert "Webhook failed" in str(exc.value)


@pytest.mark.asyncio
async def test_notify_edge_case_created_no_op_without_slack_client():
    """Notification is no-op when Slack client is not configured."""
    service = NotificationService()  # No slack_client

    # Should not raise, just skip
    await service.notify_edge_case_created(
        edge_case_id="ec-105",
        title="No slack client",
        category="test",
        severity="critical",
        edge_case_url="https://app.example.com/edge-cases/ec-105",
    )
