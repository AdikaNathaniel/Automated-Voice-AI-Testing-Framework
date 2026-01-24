"""
Tests for the Slack notification client.

The client should format a summary message describing the outcome of a test run
and deliver it to a Slack incoming webhook. Behaviour covered here:
    * Successful requests include summary counts and target URL.
    * Failure notifications use the appropriate emoji and messaging.
    * HTTP errors and timeouts are surfaced via SlackClientError.
    * Invalid status values are rejected before performing the request.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from integrations.slack.client import SlackClient, SlackClientError


@pytest.mark.asyncio
async def test_send_test_run_notification_success():
    """Posting a successful run summary sends the correct payload."""
    client = SlackClient(
        webhook_url="https://slack.test/webhook",
        default_channel="#alerts",
    )

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"ok": True}

    mock_async_client = AsyncMock()
    mock_async_client.post.return_value = mock_response

    with patch("integrations.slack.client.httpx.AsyncClient") as async_client_cls:
        async_client_cls.return_value.__aenter__.return_value = mock_async_client

        result = await client.send_test_run_notification(
            status="success",
            passed=42,
            failed=0,
            duration_seconds=123.4,
            run_url="https://ci.example.com/runs/42",
        )

    mock_async_client.post.assert_awaited_once()
    args, kwargs = mock_async_client.post.call_args
    assert args[0] == "https://slack.test/webhook"
    assert kwargs["json"]["channel"] == "#alerts"
    assert ":white_check_mark:" in kwargs["json"]["text"]
    assert "42 passed" in kwargs["json"]["text"]
    assert "https://ci.example.com/runs/42" in kwargs["json"]["text"]
    assert result == {"ok": True}


@pytest.mark.asyncio
async def test_send_test_run_notification_failure_message():
    """Failure notifications include failure emoji and counts."""
    client = SlackClient(
        webhook_url="https://slack.test/webhook",
        default_channel="#alerts",
    )

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"ok": True}

    mock_async_client = AsyncMock()
    mock_async_client.post.return_value = mock_response

    with patch("integrations.slack.client.httpx.AsyncClient") as async_client_cls:
        async_client_cls.return_value.__aenter__.return_value = mock_async_client

        await client.send_test_run_notification(
            status="failure",
            passed=30,
            failed=5,
            duration_seconds=200.0,
            run_url="https://ci.example.com/runs/99",
        )

    args, kwargs = mock_async_client.post.call_args
    payload = kwargs["json"]
    assert ":x:" in payload["text"]
    assert "5 failed" in payload["text"]
    # Ensure the blocks summary mirrors the high-level message
    blocks = payload["blocks"]
    assert any("5 failed" in block.get("text", {}).get("text", "") for block in blocks if block["type"] == "section")


@pytest.mark.asyncio
async def test_send_test_run_notification_raises_on_http_error():
    """HTTP errors are wrapped in SlackClientError."""
    client = SlackClient(webhook_url="https://slack.test/webhook")

    response = httpx.Response(
        status_code=500,
        request=httpx.Request("POST", "https://slack.test/webhook"),
        json={"error": "internal_error"},
    )
    http_error = httpx.HTTPStatusError("Internal error", request=response.request, response=response)

    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = http_error

    mock_async_client = AsyncMock()
    mock_async_client.post.return_value = mock_response

    with patch("integrations.slack.client.httpx.AsyncClient") as async_client_cls:
        async_client_cls.return_value.__aenter__.return_value = mock_async_client

        with pytest.raises(SlackClientError):
            await client.send_test_run_notification(
                status="success",
                passed=1,
                failed=0,
                duration_seconds=10,
                run_url="https://ci.example.com",
            )


@pytest.mark.asyncio
async def test_send_test_run_notification_rejects_invalid_status():
    """Invalid status values are rejected early."""
    client = SlackClient(webhook_url="https://slack.test/webhook")

    with pytest.raises(ValueError):
        await client.send_test_run_notification(
            status="unknown",
            passed=0,
            failed=0,
            duration_seconds=0,
            run_url="https://ci.example.com",
        )


@pytest.mark.asyncio
async def test_send_critical_defect_alert_posts_alert():
    """Critical defect alerts include severity, title, and deep link."""
    client = SlackClient(
        webhook_url="https://slack.test/webhook",
        default_channel="#critical-defects",
    )

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"ok": True}

    mock_async_client = AsyncMock()
    mock_async_client.post.return_value = mock_response

    with patch("integrations.slack.client.httpx.AsyncClient") as async_client_cls:
        async_client_cls.return_value.__aenter__.return_value = mock_async_client

        result = await client.send_critical_defect_alert(
            defect_id="def-123",
            title="ASR misrecognizes wake word",
            severity="critical",
            defect_url="https://app.example.com/defects/def-123",
            description="Wake word fails in noisy environments.",
        )

    mock_async_client.post.assert_awaited_once()
    args, kwargs = mock_async_client.post.call_args
    assert args[0] == "https://slack.test/webhook"
    payload = kwargs["json"]
    assert payload["channel"] == "#critical-defects"
    assert ":rotating_light:" in payload["text"]
    assert "CRITICAL" in payload["text"]
    assert "ASR misrecognizes wake word" in payload["text"]
    assert "https://app.example.com/defects/def-123" in payload["text"]
    blocks = payload["blocks"]
    assert any("Wake word fails" in block.get("text", {}).get("text", "") for block in blocks if block["type"] == "section")
    assert result == {"ok": True}


@pytest.mark.asyncio
async def test_send_system_alert_posts_payload():
    """System alerts include severity badge, summary, and details."""
    client = SlackClient(
        webhook_url="https://slack.test/webhook",
        default_channel="#system-alerts",
    )

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"ok": True}

    mock_async_client = AsyncMock()
    mock_async_client.post.return_value = mock_response

    with patch("integrations.slack.client.httpx.AsyncClient") as async_client_cls:
        async_client_cls.return_value.__aenter__.return_value = mock_async_client

        result = await client.send_system_alert(
            severity="critical",
            title="Database outage",
            message="Primary database unreachable for 5 minutes.",
            alert_url="https://status.example.com/incidents/db",
        )

    mock_async_client.post.assert_awaited_once()
    args, kwargs = mock_async_client.post.call_args
    assert args[0] == "https://slack.test/webhook"
    payload = kwargs["json"]
    assert payload["channel"] == "#system-alerts"
    assert ":fire:" in payload["text"]
    assert "CRITICAL" in payload["text"]
    assert "Database outage" in payload["text"]
    assert "status.example.com" in payload["text"]
    blocks = payload["blocks"]
    assert any("Primary database unreachable" in block.get("text", {}).get("text", "") for block in blocks if block["type"] == "section")
    assert result == {"ok": True}


@pytest.mark.asyncio
async def test_send_edge_case_alert_posts_payload():
    """Edge case alerts include severity, category, and deep link."""
    client = SlackClient(
        webhook_url="https://slack.test/webhook",
        default_channel="#edge-cases",
    )

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.text = "ok"

    mock_async_client = AsyncMock()
    mock_async_client.post.return_value = mock_response

    with patch("integrations.slack.client.httpx.AsyncClient") as async_client_cls:
        async_client_cls.return_value.__aenter__.return_value = mock_async_client

        result = await client.send_edge_case_alert(
            edge_case_id="ec-456",
            title="Ambiguous intent: play music vs set alarm",
            category="ambiguous_intent",
            severity="high",
            edge_case_url="https://app.example.com/edge-cases/ec-456",
            scenario_name="Morning Routine",
            description="User said 'wake me up with music' - unclear if alarm or playback",
        )

    mock_async_client.post.assert_awaited_once()
    args, kwargs = mock_async_client.post.call_args
    assert args[0] == "https://slack.test/webhook"
    payload = kwargs["json"]
    assert payload["channel"] == "#edge-cases"
    assert ":warning:" in payload["text"]  # high severity emoji
    assert "HIGH" in payload["text"]
    assert "Ambiguous intent" in payload["text"]
    assert "https://app.example.com/edge-cases/ec-456" in payload["text"]
    blocks = payload["blocks"]
    # Check context elements include ID, category, severity, scenario
    context_block = next(b for b in blocks if b["type"] == "context")
    context_text = " ".join(e.get("text", "") for e in context_block["elements"])
    assert "ec-456" in context_text
    assert "Ambiguous Intent" in context_text
    assert "HIGH" in context_text
    assert "Morning Routine" in context_text
    assert result == {"ok": True}


@pytest.mark.asyncio
async def test_send_edge_case_alert_critical_severity_emoji():
    """Critical severity edge cases use rotating light emoji."""
    client = SlackClient(webhook_url="https://slack.test/webhook")

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.text = "ok"

    mock_async_client = AsyncMock()
    mock_async_client.post.return_value = mock_response

    with patch("integrations.slack.client.httpx.AsyncClient") as async_client_cls:
        async_client_cls.return_value.__aenter__.return_value = mock_async_client

        await client.send_edge_case_alert(
            edge_case_id="ec-789",
            title="System crash on voice input",
            category="system_error",
            severity="critical",
            edge_case_url="https://app.example.com/edge-cases/ec-789",
        )

    args, kwargs = mock_async_client.post.call_args
    assert ":rotating_light:" in kwargs["json"]["text"]


@pytest.mark.asyncio
async def test_send_edge_case_alert_validates_required_params():
    """Edge case alerts validate required parameters."""
    client = SlackClient(webhook_url="https://slack.test/webhook")

    with pytest.raises(ValueError, match="edge_case_id is required"):
        await client.send_edge_case_alert(
            edge_case_id="",
            title="Test",
            category="test",
            severity="low",
            edge_case_url="https://example.com",
        )

    with pytest.raises(ValueError, match="title is required"):
        await client.send_edge_case_alert(
            edge_case_id="ec-123",
            title="",
            category="test",
            severity="low",
            edge_case_url="https://example.com",
        )


@pytest.mark.asyncio
async def test_dispatch_handles_plain_text_ok_response():
    """Slack webhooks return plain text 'ok' - handle this correctly."""
    client = SlackClient(webhook_url="https://slack.test/webhook")

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.text = "ok"  # Plain text, not JSON

    mock_async_client = AsyncMock()
    mock_async_client.post.return_value = mock_response

    with patch("integrations.slack.client.httpx.AsyncClient") as async_client_cls:
        async_client_cls.return_value.__aenter__.return_value = mock_async_client

        result = await client.send_test_run_notification(
            status="success",
            passed=5,
            failed=0,
            duration_seconds=30.0,
            run_url="https://example.com/runs/1",
        )

    # Should return {"ok": True} even for plain text response
    assert result == {"ok": True}
