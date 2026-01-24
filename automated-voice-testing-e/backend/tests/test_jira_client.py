"""
Tests for the Jira API client.

The Jira client should provide helpers for:
  * Creating issues in a project with properly merged fields and headers.
  * Updating existing issues by key.
  * Fetching issues by key and returning JSON payloads.
  * Raising a dedicated error type when HTTP errors, timeouts, or network
    issues occur.
"""

from __future__ import annotations

import base64
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from integrations.jira.client import JiraClient, JiraClientError


def _expected_auth_header(email: str, token: str) -> str:
    creds = f"{email}:{token}".encode("utf-8")
    return f"Basic {base64.b64encode(creds).decode('utf-8')}"


@pytest.mark.asyncio
async def test_create_issue_posts_payload_and_returns_issue_key():
    client = JiraClient(
        email="qa@example.com",
        api_token="atlassian-api-token",
        base_url="https://example.atlassian.net/rest/api/3",
    )

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"key": "QA-123"}

    mock_async_client = AsyncMock()
    mock_async_client.post.return_value = mock_response

    with patch("integrations.jira.client.httpx.AsyncClient") as async_client_cls:
        async_client_cls.return_value.__aenter__.return_value = mock_async_client

        issue_key = await client.create_issue(
            project="QA",
            data={
                "summary": "Voice transcription regression",
                "description": "Transcription accuracy dropped below threshold.",
                "issuetype": {"name": "Bug"},
            },
        )

    mock_async_client.post.assert_awaited_once_with(
        "https://example.atlassian.net/rest/api/3/issue",
        json={
            "fields": {
                "project": {"key": "QA"},
                "summary": "Voice transcription regression",
                "description": "Transcription accuracy dropped below threshold.",
                "issuetype": {"name": "Bug"},
            }
        },
        headers={
            "Authorization": _expected_auth_header("qa@example.com", "atlassian-api-token"),
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        timeout=10.0,
    )

    assert issue_key == "QA-123"


@pytest.mark.asyncio
async def test_create_issue_wraps_http_errors():
    client = JiraClient(email="qa@example.com", api_token="token", base_url="https://example.atlassian.net/rest/api/3")

    response = httpx.Response(status_code=400, request=httpx.Request("POST", "https://example.atlassian.net"))
    http_error = httpx.HTTPStatusError("Bad Request", request=response.request, response=response)

    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = http_error

    mock_async_client = AsyncMock()
    mock_async_client.post.return_value = mock_response

    with patch("integrations.jira.client.httpx.AsyncClient") as async_client_cls:
        async_client_cls.return_value.__aenter__.return_value = mock_async_client

        with pytest.raises(JiraClientError) as exc:
            await client.create_issue(project="QA", data={"summary": "Broken"})

    assert "Bad Request" in str(exc.value)


@pytest.mark.asyncio
async def test_update_issue_puts_payload():
    client = JiraClient(email="qa@example.com", api_token="token", base_url="https://example.atlassian.net/rest/api/3")

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None

    mock_async_client = AsyncMock()
    mock_async_client.put.return_value = mock_response

    with patch("integrations.jira.client.httpx.AsyncClient") as async_client_cls:
        async_client_cls.return_value.__aenter__.return_value = mock_async_client

        await client.update_issue(issue_key="QA-123", data={"fields": {"summary": "Updated"}})

    mock_async_client.put.assert_awaited_once_with(
        "https://example.atlassian.net/rest/api/3/issue/QA-123",
        json={"fields": {"summary": "Updated"}},
        headers={
            "Authorization": _expected_auth_header("qa@example.com", "token"),
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        timeout=10.0,
    )


@pytest.mark.asyncio
async def test_get_issue_returns_json_payload():
    client = JiraClient(email="qa@example.com", api_token="token", base_url="https://example.atlassian.net/rest/api/3")

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"key": "QA-123", "fields": {"summary": "Investigate"}}

    mock_async_client = AsyncMock()
    mock_async_client.get.return_value = mock_response

    with patch("integrations.jira.client.httpx.AsyncClient") as async_client_cls:
        async_client_cls.return_value.__aenter__.return_value = mock_async_client

        issue = await client.get_issue(issue_key="QA-123")

    mock_async_client.get.assert_awaited_once_with(
        "https://example.atlassian.net/rest/api/3/issue/QA-123",
        headers={
            "Authorization": _expected_auth_header("qa@example.com", "token"),
            "Accept": "application/json",
        },
        timeout=10.0,
        params=None,
    )

    assert issue == {"key": "QA-123", "fields": {"summary": "Investigate"}}


@pytest.mark.asyncio
async def test_timeout_errors_raise_dedicated_exception():
    client = JiraClient(email="qa@example.com", api_token="token", base_url="https://example.atlassian.net/rest/api/3")

    mock_async_client = AsyncMock()
    mock_async_client.get.side_effect = httpx.TimeoutException("timeout")

    with patch("integrations.jira.client.httpx.AsyncClient") as async_client_cls:
        async_client_cls.return_value.__aenter__.return_value = mock_async_client

        with pytest.raises(JiraClientError) as exc:
            await client.get_issue(issue_key="QA-123")

    assert "timeout" in str(exc.value).lower()
