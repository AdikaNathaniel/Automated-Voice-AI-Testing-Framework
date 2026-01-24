"""
Tests for the GitHub commit status client.

These tests describe the expected behaviour for posting commit statuses to
GitHub and the associated error handling. The client should:
    * Send a POST request with the correct URL, headers, and payload.
    * Validate the provided status state before performing the request.
    * Raise a dedicated error when the GitHub API responds with an error.
    * Surface timeout errors as the same dedicated error type.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from integrations.github.client import GitHubClient, GitHubClientError


@pytest.mark.asyncio
async def test_set_commit_status_success():
    """Client posts commit status with proper payload and headers."""
    client = GitHubClient(
        token="ghp_testtoken",
        repo_owner="octocat",
        repo_name="hello-world",
    )

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"state": "success"}

    mock_async_client = AsyncMock()
    mock_async_client.post.return_value = mock_response

    with patch("integrations.github.client.httpx.AsyncClient") as async_client_cls:
        async_client_cls.return_value.__aenter__.return_value = mock_async_client

        result = await client.set_commit_status(
            sha="abc123",
            state="success",
            target_url="https://ci.example.com/run/1",
            description="All checks passed",
            context="ci/tests",
        )

    async_client_cls.assert_called_once()
    mock_async_client.post.assert_awaited_once_with(
        "https://api.github.com/repos/octocat/hello-world/statuses/abc123",
        json={
            "state": "success",
            "target_url": "https://ci.example.com/run/1",
            "description": "All checks passed",
            "context": "ci/tests",
        },
        headers={
            "Authorization": "token ghp_testtoken",
            "Accept": "application/vnd.github+json",
        },
        timeout=10.0,
    )
    assert result == {"state": "success"}


@pytest.mark.asyncio
async def test_set_commit_status_rejects_invalid_state():
    """Client validates the provided state before contacting GitHub."""
    client = GitHubClient(token="t", repo_owner="o", repo_name="r")

    with pytest.raises(ValueError):
        await client.set_commit_status(sha="abc", state="not-a-valid-state")


@pytest.mark.asyncio
async def test_set_commit_status_raises_on_http_error():
    """Client wraps HTTP status errors in GitHubClientError."""
    client = GitHubClient(token="t", repo_owner="o", repo_name="r")

    response = httpx.Response(status_code=401, request=httpx.Request("POST", "https://api.github.com"))
    http_error = httpx.HTTPStatusError("Unauthorized", request=response.request, response=response)

    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = http_error

    mock_async_client = AsyncMock()
    mock_async_client.post.return_value = mock_response

    with patch("integrations.github.client.httpx.AsyncClient") as async_client_cls:
        async_client_cls.return_value.__aenter__.return_value = mock_async_client

        with pytest.raises(GitHubClientError) as exc:
            await client.set_commit_status(sha="abc", state="success")

    assert "Unauthorized" in str(exc.value)


@pytest.mark.asyncio
async def test_set_commit_status_raises_on_timeout():
    """Client raises GitHubClientError when the request times out."""
    client = GitHubClient(token="t", repo_owner="o", repo_name="r")

    mock_async_client = AsyncMock()
    mock_async_client.post.side_effect = httpx.TimeoutException("timeout")

    with patch("integrations.github.client.httpx.AsyncClient") as async_client_cls:
        async_client_cls.return_value.__aenter__.return_value = mock_async_client

        with pytest.raises(GitHubClientError) as exc:
            await client.set_commit_status(sha="abc", state="success")

    assert "timeout" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_post_test_run_status_maps_success_state_and_description():
    """post_test_run_status builds commit payload from run metrics."""
    client = GitHubClient(token="tok", repo_owner="owner", repo_name="repo")
    client.set_commit_status = AsyncMock(return_value={"state": "success"})

    result = await client.post_test_run_status(
        sha="abc123",
        run_status="passed",
        passed=12,
        failed=0,
        skipped=3,
        target_url="https://ci.example.com/runs/42",
        context="ci/tests",
    )

    client.set_commit_status.assert_awaited_once()
    kwargs = client.set_commit_status.await_args.kwargs
    assert kwargs == {
        "sha": "abc123",
        "state": "success",
        "target_url": "https://ci.example.com/runs/42",
        "description": "12 passed, 0 failed, 3 skipped",
        "context": "ci/tests",
    }
    assert result == {"state": "success"}


@pytest.mark.asyncio
async def test_post_test_run_status_truncates_long_details():
    """Commit description is truncated to GitHub limits when details are long."""
    client = GitHubClient(token="tok", repo_owner="owner", repo_name="repo")
    client.set_commit_status = AsyncMock(return_value={"state": "failure"})

    long_details = " ".join(["failure"] * 50)

    await client.post_test_run_status(
        sha="deadbeef",
        run_status="failed",
        passed=5,
        failed=7,
        skipped=1,
        details=long_details,
        target_url=None,
        context=None,
    )

    kwargs = client.set_commit_status.await_args.kwargs
    assert kwargs["state"] == "failure"
    assert len(kwargs["description"]) <= 140
    assert kwargs["description"].endswith("...")


@pytest.mark.asyncio
async def test_create_issue_posts_payload_to_github():
    """create_issue sends title/body/labels/assignees to GitHub issues API."""
    client = GitHubClient(token="ghp_testtoken", repo_owner="octocat", repo_name="hello-world")

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"number": 101, "html_url": "https://github.com/octocat/hello-world/issues/101"}

    mock_async_client = AsyncMock()
    mock_async_client.post.return_value = mock_response

    with patch("integrations.github.client.httpx.AsyncClient") as async_client_cls:
        async_client_cls.return_value.__aenter__.return_value = mock_async_client

        issue = await client.create_issue(
            title="Critical defect in voice pipeline",
            body="Detected failure when validating wake word accuracy.",
            labels=["bug", "high-priority"],
            assignees=["qa-lead"],
        )

    mock_async_client.post.assert_awaited_once_with(
        "https://api.github.com/repos/octocat/hello-world/issues",
        json={
            "title": "Critical defect in voice pipeline",
            "body": "Detected failure when validating wake word accuracy.",
            "labels": ["bug", "high-priority"],
            "assignees": ["qa-lead"],
        },
        headers={
            "Authorization": "token ghp_testtoken",
            "Accept": "application/vnd.github+json",
        },
        timeout=10.0,
    )
    assert issue["number"] == 101


@pytest.mark.asyncio
async def test_create_issue_requires_title():
    """create_issue validates title before contacting GitHub."""
    client = GitHubClient(token="tok", repo_owner="owner", repo_name="repo")

    with pytest.raises(ValueError):
        await client.create_issue(title="")


@pytest.mark.asyncio
async def test_create_issue_wraps_http_errors():
    """GitHubClientError is raised when GitHub returns an error."""
    client = GitHubClient(token="tok", repo_owner="owner", repo_name="repo")

    response = httpx.Response(
        status_code=422,
        request=httpx.Request("POST", "https://api.github.com/repos/owner/repo/issues"),
    )
    http_error = httpx.HTTPStatusError("Validation Failed", request=response.request, response=response)

    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = http_error

    mock_async_client = AsyncMock()
    mock_async_client.post.return_value = mock_response

    with patch("integrations.github.client.httpx.AsyncClient") as async_client_cls:
        async_client_cls.return_value.__aenter__.return_value = mock_async_client

        with pytest.raises(GitHubClientError) as exc:
            await client.create_issue(title="Bad payload")

    assert "Validation Failed" in str(exc.value)
