"""
Async Jira REST API client.

Provides minimal helpers for creating, updating, and retrieving Jira issues.
The client uses HTTP Basic authentication with an Atlassian API token and
wraps networking errors in a dedicated exception.
"""

from __future__ import annotations

import base64
import logging
from copy import deepcopy
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)


class JiraClientError(RuntimeError):
    """Raised when the Jira client encounters an error."""


class JiraClient:
    """Minimal async client for Jira issue APIs."""

    def __init__(
        self,
        *,
        email: str,
        api_token: str,
        base_url: str = "https://example.atlassian.net/rest/api/3",
        timeout: float = 10.0,
    ) -> None:
        if not email:
            raise ValueError("Jira user email is required")
        if not api_token:
            raise ValueError("Jira API token is required")
        if not base_url:
            raise ValueError("Jira base URL is required")

        self._email = email
        self._api_token = api_token
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._auth_header = self._build_auth_header(email, api_token)

    @staticmethod
    def _build_auth_header(email: str, token: str) -> str:
        credentials = f"{email}:{token}".encode("utf-8")
        return f"Basic {base64.b64encode(credentials).decode('utf-8')}"

    def _json_headers(self, *, include_content_type: bool = True) -> Dict[str, str]:
        headers = {
            "Authorization": self._auth_header,
            "Accept": "application/json",
        }
        if include_content_type:
            headers["Content-Type"] = "application/json"
        return headers

    def _build_url(self, *parts: str) -> str:
        suffix = "/".join(part.strip("/") for part in parts if part)
        return f"{self._base_url}/{suffix}" if suffix else self._base_url

    @staticmethod
    def _raise_http_error(message: str, error: Exception) -> None:
        logger.error(message)
        raise JiraClientError(message) from error

    async def create_issue(self, *, project: str, data: Dict[str, Any]) -> str:
        """
        Create an issue inside the given project.

        Args:
            project: Jira project key (e.g., "QA").
            data: Fields payload to merge with the project.

        Returns:
            Created issue key (e.g., "QA-123").
        """
        if not project:
            raise ValueError("Project key is required")
        if not isinstance(data, dict):
            raise ValueError("Issue data must be a dictionary")

        fields = {"project": {"key": project}}
        fields.update(deepcopy(data))

        payload = {"fields": fields}
        url = self._build_url("issue")

        logger.debug("Creating Jira issue at %s with payload: %s", url, payload)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._json_headers(),
                    timeout=self._timeout,
                )
                response.raise_for_status()
                body = response.json()
        except httpx.HTTPStatusError as exc:
            message = f"Jira API returned error while creating issue: {exc}"
            self._raise_http_error(message, exc)
        except httpx.TimeoutException as exc:
            message = f"Timed out creating Jira issue: {exc}"
            self._raise_http_error(message, exc)
        except httpx.RequestError as exc:
            message = f"Failed to communicate with Jira while creating issue: {exc}"
            self._raise_http_error(message, exc)

        issue_key = body.get("key")
        if not issue_key:
            raise JiraClientError("Jira response missing issue key")
        return issue_key

    async def update_issue(self, *, issue_key: str, data: Dict[str, Any]) -> None:
        """
        Update an existing Jira issue.

        Args:
            issue_key: Issue identifier (e.g., "QA-123").
            data: JSON payload to send to Jira (e.g., {"fields": {...}}).
        """
        if not issue_key:
            raise ValueError("Issue key is required")
        if not isinstance(data, dict):
            raise ValueError("Update payload must be a dictionary")

        url = self._build_url("issue", issue_key)

        logger.debug("Updating Jira issue %s with payload: %s", issue_key, data)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    url,
                    json=deepcopy(data),
                    headers=self._json_headers(),
                    timeout=self._timeout,
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            message = f"Jira API returned error while updating issue {issue_key}: {exc}"
            self._raise_http_error(message, exc)
        except httpx.TimeoutException as exc:
            message = f"Timed out updating Jira issue {issue_key}: {exc}"
            self._raise_http_error(message, exc)
        except httpx.RequestError as exc:
            message = f"Failed to communicate with Jira while updating issue {issue_key}: {exc}"
            self._raise_http_error(message, exc)

    async def get_issue(self, *, issue_key: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieve a Jira issue by key.

        Args:
            issue_key: Jira issue key (e.g., "QA-123").
            params: Optional query parameters (e.g., {"fields": "summary,status"}).

        Returns:
            Parsed JSON issue representation.
        """
        if not issue_key:
            raise ValueError("Issue key is required")

        url = self._build_url("issue", issue_key)

        logger.debug("Fetching Jira issue %s with params: %s", issue_key, params)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self._json_headers(include_content_type=False),
                    timeout=self._timeout,
                    params=params,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            message = f"Jira API returned error while fetching issue {issue_key}: {exc}"
            self._raise_http_error(message, exc)
        except httpx.TimeoutException as exc:
            message = f"Timed out fetching Jira issue {issue_key}: {exc}"
            self._raise_http_error(message, exc)
        except httpx.RequestError as exc:
            message = f"Failed to communicate with Jira while fetching issue {issue_key}: {exc}"
            self._raise_http_error(message, exc)
