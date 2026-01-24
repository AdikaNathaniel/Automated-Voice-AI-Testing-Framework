"""
GitHub OAuth integration utilities.

Provides helper classes for initiating the GitHub OAuth flow, exchanging the
authorization code for an access token, and retrieving a connected user's
profile information.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, List, Optional, Sequence, Tuple
from urllib.parse import urlencode
import logging
import re
import secrets

import httpx

logger = logging.getLogger(__name__)


class GitHubOAuthError(RuntimeError):
    """Raised when any step of the GitHub OAuth flow fails."""


@dataclass(slots=True)
class OAuthToken:
    """Represents an OAuth access token returned by GitHub."""

    access_token: str
    token_type: str
    scopes: List[str]


@dataclass(slots=True)
class GitHubUser:
    """Basic information about a GitHub user."""

    id: int
    login: str
    name: Optional[str]
    email: Optional[str]
    avatar_url: Optional[str]
    profile_url: Optional[str]


def _default_state_generator() -> str:
    """Generate a cryptographically random state token."""
    return secrets.token_urlsafe(32)


def _normalize_scopes(scopes: Sequence[str] | None) -> List[str]:
    if not scopes:
        return []
    # Preserve order while removing duplicates.
    seen = set()
    normalized: List[str] = []
    for scope in scopes:
        if scope and scope not in seen:
            seen.add(scope)
            normalized.append(scope)
    return normalized


class GitHubOAuthClient:
    """Helper for orchestrating GitHub OAuth flows."""

    AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    API_BASE_URL = "https://api.github.com"

    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        scope: Optional[Sequence[str]] = None,
        state_generator: Callable[[], str] = _default_state_generator,
        timeout: float = 10.0,
    ) -> None:
        if not client_id:
            raise ValueError("GitHub OAuth client_id is required")
        if not client_secret:
            raise ValueError("GitHub OAuth client_secret is required")
        if not redirect_uri:
            raise ValueError("GitHub OAuth redirect_uri is required")

        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri
        self._default_scopes = _normalize_scopes(scope) or ["read:user", "user:email"]
        self._state_generator = state_generator
        self._timeout = timeout

    def build_authorize_url(
        self,
        *,
        scopes: Optional[Iterable[str]] = None,
        state: Optional[str] = None,
    ) -> Tuple[str, str]:
        """
        Construct the GitHub authorize URL.

        Returns a tuple of (authorize_url, state) so the caller can persist the
        generated state for later validation.
        """
        resolved_state = state or self._state_generator()
        resolved_scopes = _normalize_scopes(list(scopes) if scopes is not None else self._default_scopes)

        params = {
            "client_id": self._client_id,
            "redirect_uri": self._redirect_uri,
            "state": resolved_state,
            "scope": " ".join(resolved_scopes),
        }

        query = urlencode(params)
        authorize_url = f"{self.AUTHORIZE_URL}?{query}"
        logger.debug("Constructed GitHub authorize URL: %s", authorize_url)
        return authorize_url, resolved_state

    async def exchange_code_for_token(self, *, code: str, redirect_uri: Optional[str] = None) -> OAuthToken:
        """Exchange an OAuth authorization code for an access token."""
        if not code:
            raise ValueError("Authorization code is required")

        data = {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "code": code,
            "redirect_uri": redirect_uri or self._redirect_uri,
        }

        headers = {"Accept": "application/json"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.TOKEN_URL,
                    data=data,
                    headers=headers,
                    timeout=self._timeout,
                )
                response.raise_for_status()
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            message = f"Failed to exchange GitHub OAuth code: {exc}"
            logger.error(message)
            raise GitHubOAuthError(message) from exc

        payload = response.json()
        if "error" in payload:
            message = payload.get("error_description") or payload.get("error") or "Unknown OAuth error"
            logger.error("GitHub OAuth returned error payload: %s", payload)
            raise GitHubOAuthError(message)

        access_token = payload.get("access_token")
        token_type = payload.get("token_type")
        raw_scope = payload.get("scope", "")

        if not access_token or not token_type:
            raise GitHubOAuthError("GitHub OAuth response missing access_token or token_type")

        scopes = [scope for scope in re.split(r"[,\s]+", raw_scope) if scope]
        return OAuthToken(access_token=access_token, token_type=token_type.lower(), scopes=scopes)

    async def fetch_user_profile(self, *, token: str) -> GitHubUser:
        """Retrieve the GitHub user profile associated with the provided token."""
        if not token:
            raise ValueError("Access token is required to fetch user profile")

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        }

        try:
            async with httpx.AsyncClient() as client:
                user_response = await client.get(
                    f"{self.API_BASE_URL}/user",
                    headers=headers,
                    timeout=self._timeout,
                )
                user_response.raise_for_status()
                user_payload = user_response.json()

                email = user_payload.get("email")
                if not email:
                    email = await self._fetch_primary_email(client, headers=headers)

                return GitHubUser(
                    id=user_payload.get("id"),
                    login=user_payload.get("login"),
                    name=user_payload.get("name"),
                    email=email,
                    avatar_url=user_payload.get("avatar_url"),
                    profile_url=user_payload.get("html_url"),
                )
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            message = f"Failed to fetch GitHub user profile: {exc}"
            logger.error(message)
            raise GitHubOAuthError(message) from exc

    async def _fetch_primary_email(self, client: httpx.AsyncClient, *, headers: dict) -> Optional[str]:
        """Fetch the user's primary email address from the GitHub API."""
        try:
            emails_response = await client.get(
                f"{self.API_BASE_URL}/user/emails",
                headers=headers,
                timeout=self._timeout,
            )
            emails_response.raise_for_status()
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            message = f"Failed to fetch GitHub user emails: {exc}"
            logger.warning(message)
            raise GitHubOAuthError(message) from exc

        emails_payload = emails_response.json() or []
        primary_email = next(
            (email.get("email") for email in emails_payload if email.get("primary") and email.get("verified")),
            None,
        )
        if primary_email:
            return primary_email

        fallback_email = next(
            (email.get("email") for email in emails_payload if email.get("primary") or email.get("verified")),
            None,
        )
        return fallback_email
