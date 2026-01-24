"""
GitHub Commit Status Client.

Provides a minimal async client for posting commit statuses to GitHub. The
client is intended for CI/CD integrations where test runs report their status
back to GitHub pull requests or commits.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import logging

import httpx

logger = logging.getLogger(__name__)


class GitHubClientError(RuntimeError):
    """Raised when the GitHub client encounters an error."""


class GitHubClient:
    """Client for interacting with the GitHub commit status API."""

    VALID_STATES = {"error", "failure", "pending", "success"}

    def __init__(
        self,
        token: str,
        repo_owner: str,
        repo_name: str,
        *,
        base_url: str = "https://api.github.com",
        timeout: float = 10.0,
    ) -> None:
        if not token:
            raise ValueError("GitHub API token is required")
        if not repo_owner:
            raise ValueError("Repository owner is required")
        if not repo_name:
            raise ValueError("Repository name is required")

        self._token = token
        self._repo_owner = repo_owner
        self._repo_name = repo_name
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    async def set_commit_status(
        self,
        *,
        sha: str,
        state: str,
        target_url: Optional[str] = None,
        description: Optional[str] = None,
        context: str = "continuous-integration/automated-testing",
    ) -> Dict[str, Any]:
        """
        Post a commit status to GitHub.

        Args:
            sha: Commit SHA to update.
            state: Status state. Must be one of: error, failure, pending, success.
            target_url: Optional URL with more details about the status.
            description: Optional description (<= 140 chars as per GitHub docs).
            context: Identifier for the status (defaults to automated testing).

        Returns:
            Parsed JSON response from GitHub.

        Raises:
            ValueError: If parameters are invalid.
            GitHubClientError: If the request fails.
        """
        if not sha:
            raise ValueError("Commit SHA is required")
        if state not in self.VALID_STATES:
            raise ValueError(f"Invalid state '{state}'. Must be one of {sorted(self.VALID_STATES)}")
        if description is not None and len(description) > 140:
            raise ValueError("Description must be 140 characters or fewer")

        payload: Dict[str, Any] = {
            "state": state,
            "context": context,
        }

        if target_url:
            payload["target_url"] = target_url
        if description:
            payload["description"] = description

        headers = {
            "Authorization": f"token {self._token}",
            "Accept": "application/vnd.github+json",
        }

        url = self._build_status_url(sha)

        logger.debug("Posting commit status to %s: %s", url, payload)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=self._timeout,
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as exc:
            message = f"GitHub API error: {str(exc)}"
            logger.error(message)
            raise GitHubClientError(message) from exc
        except httpx.TimeoutException as exc:
            message = f"GitHub API request timed out: {str(exc)}"
            logger.error(message)
            raise GitHubClientError(message) from exc
        except httpx.RequestError as exc:
            message = f"Failed to communicate with GitHub: {str(exc)}"
            logger.error(message)
            raise GitHubClientError(message) from exc

    async def create_issue(
        self,
        *,
        title: str,
        body: Optional[str] = None,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None,
        milestone: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Create a GitHub issue in the configured repository.

        Args:
            title: Title of the issue (required).
            body: Optional Markdown body.
            labels: Optional list of labels to apply.
            assignees: Optional list of assignees.
            milestone: Optional milestone number to associate.

        Returns:
            Parsed JSON response from GitHub.

        Raises:
            ValueError: If the title is empty.
            GitHubClientError: If the request fails.
        """
        if not title or not title.strip():
            raise ValueError("Issue title is required")

        payload: Dict[str, Any] = {"title": title.strip()}

        if body:
            payload["body"] = body
        if labels:
            payload["labels"] = labels
        if assignees:
            payload["assignees"] = assignees
        if milestone is not None:
            payload["milestone"] = milestone

        headers = {
            "Authorization": f"token {self._token}",
            "Accept": "application/vnd.github+json",
        }

        url = f"{self._base_url}/repos/{self._repo_owner}/{self._repo_name}/issues"

        logger.debug("Creating GitHub issue at %s: %s", url, payload)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=self._timeout,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            message = f"GitHub API error while creating issue: {str(exc)}"
            logger.error(message)
            raise GitHubClientError(message) from exc
        except httpx.TimeoutException as exc:
            message = f"GitHub API request timed out while creating issue: {str(exc)}"
            logger.error(message)
            raise GitHubClientError(message) from exc
        except httpx.RequestError as exc:
            message = f"Failed to communicate with GitHub while creating issue: {str(exc)}"
            logger.error(message)
            raise GitHubClientError(message) from exc

    async def post_test_run_status(
        self,
        *,
        sha: str,
        run_status: str,
        passed: int,
        failed: int,
        skipped: int = 0,
        target_url: Optional[str] = None,
        context: Optional[str] = None,
        details: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Convert aggregated test run metrics into a GitHub commit status update.

        Args:
            sha: Commit SHA associated with the run.
            run_status: Internal status keyword (e.g., passed, failed, running).
            passed: Number of passed tests.
            failed: Number of failed tests.
            skipped: Number of skipped tests (defaults to 0).
            target_url: Optional link to the detailed run report.
            context: Optional GitHub status context override.
            details: Optional free-form details appended to the description.

        Returns:
            Parsed JSON payload returned by GitHub.
        """
        state = self._map_run_status(run_status)
        description = self._build_run_description(
            passed=passed,
            failed=failed,
            skipped=skipped,
            details=details,
        )

        return await self.set_commit_status(
            sha=sha,
            state=state,
            target_url=target_url,
            description=description,
            context=context or "continuous-integration/automated-testing",
        )

    @staticmethod
    def _map_run_status(run_status: str) -> str:
        """Map internal run status keywords to GitHub commit status states."""
        if not run_status:
            return "error"

        normalised = run_status.strip().lower()
        mapping = {
            "passed": "success",
            "success": "success",
            "succeeded": "success",
            "failed": "failure",
            "failure": "failure",
            "errored": "error",
            "error": "error",
            "cancelled": "error",
            "canceled": "error",
            "running": "pending",
            "pending": "pending",
            "in_progress": "pending",
            "queued": "pending",
        }
        return mapping.get(normalised, "error")

    @staticmethod
    def _build_run_description(
        *,
        passed: int,
        failed: int,
        skipped: int,
        details: Optional[str] = None,
    ) -> str:
        """Build a GitHub-friendly description summarising run results."""
        summary_parts = [
            f"{passed} passed",
            f"{failed} failed",
        ]

        if skipped:
            summary_parts.append(f"{skipped} skipped")

        summary = ", ".join(summary_parts)

        if details:
            summary = f"{summary} — {details.strip()}"

        return GitHubClient._truncate_description(summary)

    @staticmethod
    def _truncate_description(description: str) -> str:
        """Ensure commit status descriptions comply with GitHub length limits."""
        max_length = 140
        if len(description) <= max_length:
            return description

        ellipsis = "..."
        truncated = description[: max_length - len(ellipsis)].rstrip()
        if not truncated:
            return ellipsis
        return f"{truncated}{ellipsis}"

    def _build_status_url(self, sha: str) -> str:
        """Construct the GitHub statuses API URL for a commit."""
        return f"{self._base_url}/repos/{self._repo_owner}/{self._repo_name}/statuses/{sha}"
