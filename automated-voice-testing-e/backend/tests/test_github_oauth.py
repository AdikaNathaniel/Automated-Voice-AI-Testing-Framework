"""
Tests for the GitHub OAuth integration.

These tests define the behaviour for creating the authorization URL,
exchanging an OAuth code for an access token, and retrieving the connected
user's profile information. The OAuth client should:
  * Build an authorize URL that includes the client configuration and state.
  * Exchange an authorization code for an access token and handle errors.
  * Fetch the authenticated user's profile and, when necessary, load the
    primary verified email address from the dedicated endpoint.
"""

from __future__ import annotations

from typing import Callable
from unittest.mock import AsyncMock, MagicMock, patch
from urllib.parse import parse_qsl, urlparse

import httpx
import pytest

from integrations.github.oauth import GitHubOAuthClient, GitHubOAuthError, OAuthToken, GitHubUser


def _setup_async_client(mock_post: AsyncMock | None = None, mock_get: AsyncMock | None = None):
    async_client = AsyncMock()
    if mock_post is not None:
        async_client.post = mock_post
    if mock_get is not None:
        async_client.get = mock_get

    async_context = MagicMock()
    async_context.__aenter__ = AsyncMock(return_value=async_client)
    async_context.__aexit__ = AsyncMock(return_value=None)

    async_client_cls = MagicMock(return_value=async_context)
    return async_client_cls, async_client


def create_oauth_client(state_generator: Callable[[], str] = lambda: "static-state") -> GitHubOAuthClient:
    return GitHubOAuthClient(
        client_id="client123",
        client_secret="secret456",
        redirect_uri="https://app.example.com/oauth/github/callback",
        scope=["repo", "user:email"],
        state_generator=state_generator,
    )


def test_build_authorize_url_includes_expected_parameters():
    """Authorize URL should include client id, redirect URI, scopes, and generated state."""
    client = create_oauth_client()

    authorize_url, state = client.build_authorize_url()
    parsed = urlparse(authorize_url)
    query = dict(parse_qsl(parsed.query))

    assert parsed.scheme == "https"
    assert parsed.netloc == "github.com"
    assert parsed.path == "/login/oauth/authorize"

    assert query["client_id"] == "client123"
    assert query["redirect_uri"] == "https://app.example.com/oauth/github/callback"
    # GitHub expects scopes space-separated.
    assert query["scope"] == "repo user:email"
    assert query["state"] == state == "static-state"


@pytest.mark.asyncio
async def test_exchange_code_for_token_succeeds():
    """Exchanging a valid authorization code yields an OAuthToken."""
    client = create_oauth_client()

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "access_token": "access-789",
        "token_type": "bearer",
        "scope": "repo,user:email",
    }

    post_mock = AsyncMock(return_value=mock_response)
    async_client_cls, async_client_instance = _setup_async_client(mock_post=post_mock)

    with patch("integrations.github.oauth.httpx.AsyncClient", async_client_cls):
        token = await client.exchange_code_for_token(code="auth-code-123")

    async_client_cls.assert_called_once()
    post_mock.assert_awaited_once_with(
        "https://github.com/login/oauth/access_token",
        data={
            "client_id": "client123",
            "client_secret": "secret456",
            "code": "auth-code-123",
            "redirect_uri": "https://app.example.com/oauth/github/callback",
        },
        headers={"Accept": "application/json"},
        timeout=10.0,
    )

    assert isinstance(token, OAuthToken)
    assert token.access_token == "access-789"
    assert token.token_type == "bearer"
    assert token.scopes == ["repo", "user:email"]


@pytest.mark.asyncio
async def test_exchange_code_for_token_handles_error_response():
    """HTTP errors during token exchange raise GitHubOAuthError."""
    client = create_oauth_client()

    response = httpx.Response(status_code=400, request=httpx.Request("POST", "https://github.com/login/oauth/access_token"))
    http_error = httpx.HTTPStatusError("Bad Request", request=response.request, response=response)

    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = http_error

    post_mock = AsyncMock(return_value=mock_response)
    async_client_cls, async_client_instance = _setup_async_client(mock_post=post_mock)

    with patch("integrations.github.oauth.httpx.AsyncClient", async_client_cls):
        with pytest.raises(GitHubOAuthError) as exc:
            await client.exchange_code_for_token(code="bad-code")

    assert "Bad Request" in str(exc.value)


@pytest.mark.asyncio
async def test_fetch_user_profile_returns_core_fields():
    """Fetching the user profile returns a GitHubUser dataclass with core fields populated."""
    client = create_oauth_client()

    user_payload = {
        "id": 42,
        "login": "octocat",
        "name": "Mona Lisa",
        "avatar_url": "https://avatars.githubusercontent.com/u/42",
        "html_url": "https://github.com/octocat",
        "email": "octocat@github.com",
    }

    user_response = MagicMock()
    user_response.raise_for_status.return_value = None
    user_response.json.return_value = user_payload

    get_mock = AsyncMock(return_value=user_response)
    async_client_cls, async_client_instance = _setup_async_client(mock_get=get_mock)

    with patch("integrations.github.oauth.httpx.AsyncClient", async_client_cls):
        user = await client.fetch_user_profile(token="access-token")

    get_mock.assert_awaited_once_with(
        "https://api.github.com/user",
        headers={"Authorization": "Bearer access-token", "Accept": "application/vnd.github+json"},
        timeout=10.0,
    )
    assert isinstance(user, GitHubUser)
    assert user.id == 42
    assert user.login == "octocat"
    assert user.name == "Mona Lisa"
    assert user.email == "octocat@github.com"
    assert user.avatar_url == "https://avatars.githubusercontent.com/u/42"
    assert user.profile_url == "https://github.com/octocat"


@pytest.mark.asyncio
async def test_fetch_user_profile_loads_primary_email_when_missing():
    """When the user profile does not include an email, fetch from the emails endpoint."""
    client = create_oauth_client()

    user_payload = {
        "id": 7,
        "login": "no-email",
        "name": None,
        "avatar_url": "https://avatars.githubusercontent.com/u/7",
        "html_url": "https://github.com/no-email",
        "email": None,
    }
    emails_payload = [
        {"email": "secondary@example.com", "primary": False, "verified": True},
        {"email": "primary@example.com", "primary": True, "verified": True},
    ]

    user_response = MagicMock()
    user_response.raise_for_status.return_value = None
    user_response.json.return_value = user_payload

    emails_response = MagicMock()
    emails_response.raise_for_status.return_value = None
    emails_response.json.return_value = emails_payload

    get_mock = AsyncMock(side_effect=[user_response, emails_response])
    async_client_cls, async_client_instance = _setup_async_client(mock_get=get_mock)

    with patch("integrations.github.oauth.httpx.AsyncClient", async_client_cls):
        user = await client.fetch_user_profile(token="token")

    assert get_mock.await_count == 2
    get_mock.assert_any_await(
        "https://api.github.com/user",
        headers={"Authorization": "Bearer token", "Accept": "application/vnd.github+json"},
        timeout=10.0,
    )
    get_mock.assert_any_await(
        "https://api.github.com/user/emails",
        headers={"Authorization": "Bearer token", "Accept": "application/vnd.github+json"},
        timeout=10.0,
    )
    assert user.email == "primary@example.com"


@pytest.mark.asyncio
async def test_fetch_user_profile_raises_on_error():
    """HTTP failures when fetching the user profile raise GitHubOAuthError."""
    client = create_oauth_client()

    response = httpx.Response(status_code=401, request=httpx.Request("GET", "https://api.github.com/user"))
    http_error = httpx.HTTPStatusError("Unauthorized", request=response.request, response=response)

    get_mock = AsyncMock()
    get_mock.side_effect = http_error
    async_client_cls, async_client_instance = _setup_async_client(mock_get=get_mock)

    with patch("integrations.github.oauth.httpx.AsyncClient", async_client_cls):
        with pytest.raises(GitHubOAuthError) as exc:
            await client.fetch_user_profile(token="bad-token")

    assert "Unauthorized" in str(exc.value)
