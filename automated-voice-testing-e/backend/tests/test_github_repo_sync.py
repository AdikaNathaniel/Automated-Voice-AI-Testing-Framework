"""
Tests for the GitHub repository sync integration.

These tests describe the behaviour for synchronising test cases stored in a
GitHub repository directory. The sync module should:
    * List repository contents and fetch each test case file.
    * Decode the Base64-encoded file content and parse JSON payloads.
    * Wrap lower-level HTTP errors in a dedicated sync error.
"""

from __future__ import annotations

import base64
import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from integrations.github.sync import GitHubRepoSync, GitHubRepoSyncError, RepoTestCase


def _encode_payload(data: dict) -> str:
    """Helper to produce GitHub-style base64 content responses."""
    return base64.b64encode(json.dumps(data).encode("utf-8")).decode("utf-8")


@pytest.mark.asyncio
async def test_fetch_test_cases_decodes_remote_files():
    """Repo sync fetches directory listing and decodes individual test case files."""
    sync = GitHubRepoSync(
        token="ghp_token",
        repo_owner="octocat",
        repo_name="voice-tests",
        branch="main",
        test_case_directory="test-cases",
    )

    listing_response = MagicMock()
    listing_response.raise_for_status.return_value = None
    listing_response.json.return_value = [
        {
            "type": "file",
            "path": "test-cases/wake-word.json",
            "sha": "sha-file-1",
            "url": "https://api.github.com/repos/octocat/voice-tests/contents/test-cases/wake-word.json",
        },
        {
            "type": "file",
            "path": "test-cases/music.json",
            "sha": "sha-file-2",
            "url": "https://api.github.com/repos/octocat/voice-tests/contents/test-cases/music.json",
        },
        {
            "type": "dir",
            "path": "test-cases/archive",
            "sha": "sha-dir",
            "url": "https://api.github.com/repos/octocat/voice-tests/contents/test-cases/archive",
        },
    ]

    wake_word_response = MagicMock()
    wake_word_response.raise_for_status.return_value = None
    wake_word_response.json.return_value = {
        "sha": "sha-file-1",
        "encoding": "base64",
        "content": _encode_payload(
            {
                "id": "wake-word",
                "name": "Wake Word Detection",
                "steps": ["say 'hey car'", "expect wake acknowledgement"],
            }
        ),
    }

    music_response = MagicMock()
    music_response.raise_for_status.return_value = None
    music_response.json.return_value = {
        "sha": "sha-file-2",
        "encoding": "base64",
        "content": _encode_payload(
            {
                "id": "play-music",
                "name": "Play Music",
                "steps": ["say 'play some jazz'", "expect music playback"],
            }
        ),
    }

    mock_async_client = AsyncMock()
    mock_async_client.get = AsyncMock(
        side_effect=[
            listing_response,
            wake_word_response,
            music_response,
        ]
    )

    with patch("integrations.github.sync.httpx.AsyncClient") as async_client_cls:
        async_client_cls.return_value.__aenter__.return_value = mock_async_client

        test_cases = await sync.fetch_test_cases()

    # First call is directory listing, followed by individual file fetches.
    assert mock_async_client.get.await_count == 3
    list_call = mock_async_client.get.await_args_list[0]
    assert list_call.args == (
        "https://api.github.com/repos/octocat/voice-tests/contents/test-cases",
    )
    assert list_call.kwargs["params"] == {"ref": "main"}
    assert list_call.kwargs["headers"]["Authorization"] == "token ghp_token"

    wake_word_call = mock_async_client.get.await_args_list[1]
    assert wake_word_call.args == (
        "https://api.github.com/repos/octocat/voice-tests/contents/test-cases/wake-word.json",
    )
    assert wake_word_call.kwargs["params"] == {"ref": "main"}

    music_call = mock_async_client.get.await_args_list[2]
    assert music_call.args == (
        "https://api.github.com/repos/octocat/voice-tests/contents/test-cases/music.json",
    )

    assert isinstance(test_cases, list)
    assert all(isinstance(case, RepoTestCase) for case in test_cases)
    assert [case.path for case in test_cases] == [
        "test-cases/wake-word.json",
        "test-cases/music.json",
    ]
    assert test_cases[0].data["id"] == "wake-word"
    assert test_cases[1].data["name"] == "Play Music"


@pytest.mark.asyncio
async def test_fetch_test_cases_raises_sync_error_on_http_failure():
    """Repo sync wraps HTTP failures in GitHubRepoSyncError."""
    sync = GitHubRepoSync(
        token="ghp_token",
        repo_owner="octocat",
        repo_name="voice-tests",
    )

    response = httpx.Response(
        status_code=404,
        request=httpx.Request("GET", "https://api.github.com/repos/octocat/voice-tests/contents/test-cases"),
    )
    http_error = httpx.HTTPStatusError("not found", request=response.request, response=response)

    mock_async_client = AsyncMock()
    mock_async_client.get = AsyncMock(side_effect=http_error)

    with patch("integrations.github.sync.httpx.AsyncClient") as async_client_cls:
        async_client_cls.return_value.__aenter__.return_value = mock_async_client

        with pytest.raises(GitHubRepoSyncError) as exc_info:
            await sync.fetch_test_cases()

    assert "failed to fetch" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_push_test_cases_updates_existing_and_new_files():
    """Repo sync PUTs Base64 encoded payloads for each test case."""
    sync = GitHubRepoSync(
        token="ghp_token",
        repo_owner="octocat",
        repo_name="voice-tests",
        branch="feature/cases",
    )

    existing_case = RepoTestCase(
        path="test-cases/wake-word.json",
        sha="sha-existing",
        data={"id": "wake-word", "name": "Wake Word"},
    )
    new_case = RepoTestCase(
        path="test-cases/new-case.json",
        sha=None,
        data={"id": "new-case", "name": "Brand New"},
    )

    put_response = MagicMock()
    put_response.raise_for_status.return_value = None
    put_response.json.return_value = {"content": {"path": "test-cases/wake-word.json"}}

    mock_async_client = AsyncMock()
    mock_async_client.put = AsyncMock(return_value=put_response)

    with patch("integrations.github.sync.httpx.AsyncClient") as async_client_cls:
        async_client_cls.return_value.__aenter__.return_value = mock_async_client

        result = await sync.push_test_cases(
            [existing_case, new_case],
            commit_message="Update test cases",
            committer={"name": "CI Bot", "email": "ci@example.com"},
        )

    assert len(result) == 2
    assert mock_async_client.put.await_count == 2

    first_call = mock_async_client.put.await_args_list[0]
    assert first_call.args == (
        "https://api.github.com/repos/octocat/voice-tests/contents/test-cases/wake-word.json",
    )
    first_payload = first_call.kwargs["json"]
    assert first_payload["message"] == "Update test cases"
    assert first_payload["branch"] == "feature/cases"
    assert first_payload["sha"] == "sha-existing"
    assert first_payload["committer"] == {"name": "CI Bot", "email": "ci@example.com"}
    decoded_first = json.loads(base64.b64decode(first_payload["content"]).decode("utf-8"))
    assert decoded_first["name"] == "Wake Word"

    second_call = mock_async_client.put.await_args_list[1]
    second_payload = second_call.kwargs["json"]
    assert "sha" not in second_payload
    decoded_second = json.loads(base64.b64decode(second_payload["content"]).decode("utf-8"))
    assert decoded_second["id"] == "new-case"


@pytest.mark.asyncio
async def test_push_test_cases_raises_error_on_http_failure():
    """Repo sync wraps HTTP errors raised during push."""
    sync = GitHubRepoSync(
        token="ghp_token",
        repo_owner="octocat",
        repo_name="voice-tests",
    )

    repo_case = RepoTestCase(
        path="test-cases/bad.json",
        sha="sha",
        data={"id": "bad"},
    )

    response = httpx.Response(
        status_code=403,
        request=httpx.Request(
            "PUT", "https://api.github.com/repos/octocat/voice-tests/contents/test-cases/bad.json"
        ),
    )
    http_error = httpx.HTTPStatusError("Forbidden", request=response.request, response=response)

    mock_async_client = AsyncMock()
    mock_async_client.put = AsyncMock(side_effect=http_error)

    with patch("integrations.github.sync.httpx.AsyncClient") as async_client_cls:
        async_client_cls.return_value.__aenter__.return_value = mock_async_client

        with pytest.raises(GitHubRepoSyncError) as exc_info:
            await sync.push_test_cases([repo_case], commit_message="Update test cases")

    assert "failed to push" in str(exc_info.value).lower()
