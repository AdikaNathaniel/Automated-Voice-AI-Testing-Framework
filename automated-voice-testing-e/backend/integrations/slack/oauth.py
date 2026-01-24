"""
Slack OAuth integration utilities.

Provides helper classes for initiating the Slack OAuth flow, exchanging the
authorization code for an access token, and retrieving workspace information.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional, Sequence, Tuple
from urllib.parse import urlencode
import logging
import secrets

import httpx

logger = logging.getLogger(__name__)


class SlackOAuthError(RuntimeError):
    """Raised when any step of the Slack OAuth flow fails."""


@dataclass(slots=True)
class SlackOAuthToken:
    """Represents an OAuth access token returned by Slack."""

    access_token: str
    token_type: str
    scopes: List[str]
    bot_user_id: Optional[str] = None
    app_id: Optional[str] = None


@dataclass(slots=True)
class SlackWorkspace:
    """Basic information about a Slack workspace."""

    id: str
    name: str
    domain: Optional[str] = None
    icon_url: Optional[str] = None
    enterprise_id: Optional[str] = None
    enterprise_name: Optional[str] = None


@dataclass(slots=True)
class SlackUser:
    """Basic information about the Slack user who authorized the app."""

    id: str
    name: Optional[str] = None
    email: Optional[str] = None


def _default_state_generator() -> str:
    """Generate a cryptographically random state token."""
    return secrets.token_urlsafe(32)


def _normalize_scopes(scopes: Sequence[str] | None) -> List[str]:
    if not scopes:
        return []
    seen = set()
    normalized: List[str] = []
    for scope in scopes:
        if scope and scope not in seen:
            seen.add(scope)
            normalized.append(scope)
    return normalized


class SlackOAuthClient:
    """Helper for orchestrating Slack OAuth flows."""

    AUTHORIZE_URL = "https://slack.com/oauth/v2/authorize"
    TOKEN_URL = "https://slack.com/api/oauth.v2.access"
    API_BASE_URL = "https://slack.com/api"

    # Default bot scopes for Slack app
    DEFAULT_BOT_SCOPES = [
        "channels:read",
        "chat:write",
        "chat:write.public",
        "commands",
        "incoming-webhook",
        "users:read",
        "users:read.email",
    ]

    # Default user scopes (optional, for user-specific actions)
    DEFAULT_USER_SCOPES = [
        "identity.basic",
        "identity.email",
    ]

    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        bot_scopes: Optional[Sequence[str]] = None,
        user_scopes: Optional[Sequence[str]] = None,
        state_generator: Callable[[], str] = _default_state_generator,
        timeout: float = 10.0,
    ) -> None:
        if not client_id:
            raise ValueError("Slack OAuth client_id is required")
        if not client_secret:
            raise ValueError("Slack OAuth client_secret is required")
        if not redirect_uri:
            raise ValueError("Slack OAuth redirect_uri is required")

        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri
        self._bot_scopes = _normalize_scopes(bot_scopes) or self.DEFAULT_BOT_SCOPES
        self._user_scopes = _normalize_scopes(user_scopes) or []
        self._state_generator = state_generator
        self._timeout = timeout

    def build_authorize_url(
        self,
        *,
        bot_scopes: Optional[Sequence[str]] = None,
        user_scopes: Optional[Sequence[str]] = None,
        state: Optional[str] = None,
    ) -> Tuple[str, str]:
        """
        Construct the Slack authorize URL.

        Returns a tuple of (authorize_url, state) so the caller can persist the
        generated state for later validation.

        Args:
            bot_scopes: Bot token scopes (optional, uses defaults if not provided)
            user_scopes: User token scopes (optional)
            state: OAuth state parameter (optional, auto-generated if not provided)

        Returns:
            Tuple of (authorize_url, state)
        """
        resolved_state = state or self._state_generator()
        resolved_bot_scopes = _normalize_scopes(
            list(bot_scopes) if bot_scopes is not None else self._bot_scopes
        )
        resolved_user_scopes = _normalize_scopes(
            list(user_scopes) if user_scopes is not None else self._user_scopes
        )

        params = {
            "client_id": self._client_id,
            "redirect_uri": self._redirect_uri,
            "state": resolved_state,
            "scope": ",".join(resolved_bot_scopes),
        }

        if resolved_user_scopes:
            params["user_scope"] = ",".join(resolved_user_scopes)

        query = urlencode(params)
        authorize_url = f"{self.AUTHORIZE_URL}?{query}"
        logger.debug("Constructed Slack authorize URL: %s", authorize_url)
        return authorize_url, resolved_state

    async def exchange_code_for_token(
        self,
        *,
        code: str,
        redirect_uri: Optional[str] = None,
    ) -> Tuple[SlackOAuthToken, SlackWorkspace, Optional[SlackUser]]:
        """
        Exchange an OAuth authorization code for an access token.

        Args:
            code: Authorization code from Slack
            redirect_uri: Redirect URI (optional, uses default if not provided)

        Returns:
            Tuple of (token, workspace, user)

        Raises:
            SlackOAuthError: If the exchange fails
        """
        if not code:
            raise ValueError("Authorization code is required")

        data = {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "code": code,
            "redirect_uri": redirect_uri or self._redirect_uri,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.TOKEN_URL,
                    data=data,
                    timeout=self._timeout,
                )
                response.raise_for_status()
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            message = f"Failed to exchange Slack OAuth code: {exc}"
            logger.error(message)
            raise SlackOAuthError(message) from exc

        payload = response.json()

        if not payload.get("ok"):
            error = payload.get("error", "Unknown OAuth error")
            logger.error("Slack OAuth returned error: %s", error)
            raise SlackOAuthError(f"Slack OAuth error: {error}")

        # Extract bot token info
        access_token = payload.get("access_token")
        token_type = payload.get("token_type", "bot")
        raw_scope = payload.get("scope", "")
        scopes = [s for s in raw_scope.split(",") if s]

        if not access_token:
            raise SlackOAuthError("Slack OAuth response missing access_token")

        # Extract bot user ID if available
        bot_user_id = payload.get("bot_user_id")
        app_id = payload.get("app_id")

        token = SlackOAuthToken(
            access_token=access_token,
            token_type=token_type,
            scopes=scopes,
            bot_user_id=bot_user_id,
            app_id=app_id,
        )

        # Extract workspace info
        team_info = payload.get("team", {})
        workspace = SlackWorkspace(
            id=team_info.get("id", ""),
            name=team_info.get("name", ""),
            domain=payload.get("incoming_webhook", {}).get("channel"),
        )

        # Extract user info if available (from user token flow)
        user = None
        authed_user = payload.get("authed_user")
        if authed_user:
            user = SlackUser(
                id=authed_user.get("id", ""),
                name=None,
                email=None,
            )

        logger.info(
            "Successfully exchanged Slack OAuth code for workspace: %s",
            workspace.name,
        )

        return token, workspace, user

    async def fetch_workspace_info(self, *, token: str) -> SlackWorkspace:
        """
        Fetch workspace information using the bot token.

        Args:
            token: Bot access token

        Returns:
            SlackWorkspace with workspace details

        Raises:
            SlackOAuthError: If the API call fails
        """
        if not token:
            raise ValueError("Access token is required to fetch workspace info")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.API_BASE_URL}/team.info",
                    headers=headers,
                    timeout=self._timeout,
                )
                response.raise_for_status()
                payload = response.json()

                if not payload.get("ok"):
                    error = payload.get("error", "Unknown error")
                    raise SlackOAuthError(f"Slack API error: {error}")

                team = payload.get("team", {})
                icon = team.get("icon", {})

                return SlackWorkspace(
                    id=team.get("id", ""),
                    name=team.get("name", ""),
                    domain=team.get("domain"),
                    icon_url=icon.get("image_132") or icon.get("image_88"),
                    enterprise_id=team.get("enterprise_id"),
                    enterprise_name=team.get("enterprise_name"),
                )

        except httpx.HTTPStatusError as exc:
            message = f"Failed to fetch Slack workspace info: HTTP {exc.response.status_code}"
            logger.error(message)
            raise SlackOAuthError(message) from exc
        except httpx.RequestError as exc:
            message = f"Failed to fetch Slack workspace info: {exc}"
            logger.error(message)
            raise SlackOAuthError(message) from exc

    async def fetch_channels(
        self,
        *,
        token: str,
        types: str = "public_channel,private_channel",
        limit: int = 100,
    ) -> List[dict]:
        """
        Fetch list of channels the bot has access to.

        Args:
            token: Bot access token
            types: Channel types to fetch (comma-separated)
            limit: Maximum number of channels to fetch per page

        Returns:
            List of channel dictionaries

        Raises:
            SlackOAuthError: If the API call fails
        """
        if not token:
            raise ValueError("Access token is required to fetch channels")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        channels = []
        cursor = None

        try:
            async with httpx.AsyncClient() as client:
                while True:
                    params = {
                        "types": types,
                        "limit": limit,
                        "exclude_archived": "true",
                    }
                    if cursor:
                        params["cursor"] = cursor

                    response = await client.get(
                        f"{self.API_BASE_URL}/conversations.list",
                        headers=headers,
                        params=params,
                        timeout=self._timeout,
                    )
                    response.raise_for_status()
                    payload = response.json()

                    if not payload.get("ok"):
                        error = payload.get("error", "Unknown error")
                        raise SlackOAuthError(f"Slack API error: {error}")

                    for channel in payload.get("channels", []):
                        channels.append({
                            "id": channel.get("id"),
                            "name": channel.get("name"),
                            "is_private": channel.get("is_private", False),
                            "is_member": channel.get("is_member", False),
                            "num_members": channel.get("num_members", 0),
                        })

                    # Check for pagination
                    response_metadata = payload.get("response_metadata", {})
                    cursor = response_metadata.get("next_cursor")
                    if not cursor:
                        break

                    # Limit to 3 pages to avoid rate limits
                    if len(channels) >= limit * 3:
                        break

                logger.info("Fetched %d Slack channels", len(channels))
                return channels

        except httpx.HTTPStatusError as exc:
            message = f"Failed to fetch Slack channels: HTTP {exc.response.status_code}"
            logger.error(message)
            raise SlackOAuthError(message) from exc
        except httpx.RequestError as exc:
            message = f"Failed to fetch Slack channels: {exc}"
            logger.error(message)
            raise SlackOAuthError(message) from exc

    async def test_auth(self, *, token: str) -> dict:
        """
        Test authentication and get basic info about the token.

        Args:
            token: Access token to test

        Returns:
            Dictionary with auth test results

        Raises:
            SlackOAuthError: If the auth test fails
        """
        if not token:
            raise ValueError("Access token is required")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.API_BASE_URL}/auth.test",
                    headers=headers,
                    timeout=self._timeout,
                )
                response.raise_for_status()
                payload = response.json()

                if not payload.get("ok"):
                    error = payload.get("error", "Unknown error")
                    raise SlackOAuthError(f"Slack auth test failed: {error}")

                return {
                    "ok": True,
                    "url": payload.get("url"),
                    "team": payload.get("team"),
                    "team_id": payload.get("team_id"),
                    "user": payload.get("user"),
                    "user_id": payload.get("user_id"),
                    "bot_id": payload.get("bot_id"),
                    "is_enterprise_install": payload.get("is_enterprise_install", False),
                }

        except httpx.HTTPStatusError as exc:
            message = f"Slack auth test failed: HTTP {exc.response.status_code}"
            logger.error(message)
            raise SlackOAuthError(message) from exc
        except httpx.RequestError as exc:
            message = f"Slack auth test failed: {exc}"
            logger.error(message)
            raise SlackOAuthError(message) from exc
