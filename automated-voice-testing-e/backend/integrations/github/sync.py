"""
GitHub repository synchronisation utilities.

This module provides helpers for importing and exporting test case files stored
in a GitHub repository directory. Interactions are performed via the GitHub
Contents API using async HTTP requests.
"""

from __future__ import annotations

import base64
import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

import httpx

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class RepoTestCase:
    """Representation of a test case file stored in a GitHub repository."""

    path: str
    sha: Optional[str]
    data: Dict[str, Any]


class GitHubRepoSyncError(RuntimeError):
    """Raised when synchronising test cases with GitHub fails."""


class GitHubRepoSync:
    """Utility for synchronising test cases stored in a GitHub repository."""

    def __init__(
        self,
        *,
        token: str,
        repo_owner: str,
        repo_name: str,
        branch: str = "main",
        test_case_directory: str = "test-cases",
        base_url: str = "https://api.github.com",
        timeout: float = 10.0,
    ) -> None:
        if not token:
            raise ValueError("GitHub API token is required")
        if not repo_owner:
            raise ValueError("Repository owner is required")
        if not repo_name:
            raise ValueError("Repository name is required")
        if not branch:
            raise ValueError("Branch name is required")
        if not test_case_directory:
            raise ValueError("Test case directory is required")

        self._token = token
        self._repo_owner = repo_owner
        self._repo_name = repo_name
        self._branch = branch
        self._test_case_directory = test_case_directory.strip("/")
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    async def fetch_test_cases(self, directory: Optional[str] = None) -> List[RepoTestCase]:
        """
        Fetch test case files from the repository and return decoded payloads.

        Args:
            directory: Optional directory override. Defaults to the configured directory.

        Returns:
            List of RepoTestCase objects representing repository files.

        Raises:
            GitHubRepoSyncError: When the GitHub API request fails or the payload
                cannot be decoded.
        """
        target_directory = (directory or self._test_case_directory).strip("/")
        contents_url = self._build_contents_url(target_directory)

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            try:
                listing_response = await client.get(
                    contents_url,
                    params={"ref": self._branch},
                    headers=self._build_headers(),
                )
                listing_response.raise_for_status()
            except httpx.HTTPError as exc:
                message = f"Failed to fetch GitHub contents for '{target_directory}': {exc}"
                logger.error(message)
                raise GitHubRepoSyncError(message) from exc

            payload = listing_response.json()
            entries: Iterable[Dict[str, Any]]

            if isinstance(payload, dict):
                # The contents API returns a dict when targeting a file instead of a directory.
                entries = [payload]
            elif isinstance(payload, list):
                entries = payload
            else:
                message = f"Unexpected GitHub response when listing contents: {type(payload).__name__}"
                logger.error(message)
                raise GitHubRepoSyncError(message)

            test_cases: List[RepoTestCase] = []

            for entry in entries:
                if entry.get("type") != "file":
                    # Ignore non-file entries (e.g., directories, symlinks).
                    continue

                file_url = entry.get("url")
                path = entry.get("path")
                if not file_url or not path:
                    logger.warning("Skipping GitHub entry missing URL or path: %s", entry)
                    continue

                file_payload = await self._fetch_file_payload(client, file_url, path)
                data = self._decode_test_case(file_payload, path)

                test_cases.append(
                    RepoTestCase(
                        path=path,
                        sha=file_payload.get("sha") or entry.get("sha"),
                        data=data,
                    )
                )

            return test_cases

    async def push_test_cases(
        self,
        cases: Iterable[RepoTestCase],
        commit_message: str,
        *,
        directory: Optional[str] = None,
        committer: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Push local test case payloads to the GitHub repository.

        Args:
            cases: Iterable of RepoTestCase objects to persist.
            commit_message: Commit message to use for each file update.
            directory: Optional directory override for relative paths.
            committer: Optional committer information with ``name`` and ``email``.

        Returns:
            List of GitHub API responses for each successful upload.

        Raises:
            ValueError: If commit_message is empty.
            GitHubRepoSyncError: If a request fails or serialisation fails.
        """
        if not commit_message:
            raise ValueError("Commit message is required when pushing test cases")

        target_directory = (directory or self._test_case_directory).strip("/")
        headers = self._build_headers()
        results: List[Dict[str, Any]] = []

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            for case in cases:
                path = self._normalise_case_path(case.path, target_directory)
                url = self._build_contents_url(path)

                try:
                    raw_content = json.dumps(case.data, indent=2, sort_keys=True)
                except (TypeError, ValueError) as exc:
                    message = f"Failed to serialise test case '{path}' to JSON: {exc}"
                    logger.error(message)
                    raise GitHubRepoSyncError(message) from exc

                encoded_content = base64.b64encode(raw_content.encode("utf-8")).decode("utf-8")

                payload: Dict[str, Any] = {
                    "message": commit_message,
                    "branch": self._branch,
                    "content": encoded_content,
                }

                if committer:
                    payload["committer"] = committer
                if case.sha:
                    payload["sha"] = case.sha

                try:
                    response = await client.put(
                        url,
                        json=payload,
                        headers=headers,
                    )
                    response.raise_for_status()
                except httpx.HTTPError as exc:
                    message = f"Failed to push GitHub test case '{path}': {exc}"
                    logger.error(message)
                    raise GitHubRepoSyncError(message) from exc

                response_payload = response.json()
                if not isinstance(response_payload, dict):
                    message = f"Unexpected payload when pushing '{path}': {type(response_payload).__name__}"
                    logger.error(message)
                    raise GitHubRepoSyncError(message)

                results.append(response_payload)

        return results

    async def _fetch_file_payload(
        self,
        client: httpx.AsyncClient,
        file_url: str,
        path: str,
    ) -> Dict[str, Any]:
        """Fetch an individual file payload from GitHub."""
        try:
            response = await client.get(
                file_url,
                params={"ref": self._branch},
                headers=self._build_headers(),
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            message = f"Failed to fetch GitHub test case '{path}': {exc}"
            logger.error(message)
            raise GitHubRepoSyncError(message) from exc

        payload = response.json()
        if not isinstance(payload, dict):
            message = f"Unexpected payload when fetching '{path}': {type(payload).__name__}"
            logger.error(message)
            raise GitHubRepoSyncError(message)

        return payload

    def _decode_test_case(self, payload: Dict[str, Any], path: str) -> Dict[str, Any]:
        """Decode the GitHub Contents payload into a JSON structure."""
        content = payload.get("content")
        if not content:
            message = f"GitHub payload for '{path}' missing content field"
            logger.error(message)
            raise GitHubRepoSyncError(message)

        encoding = payload.get("encoding", "base64").lower()
        if encoding != "base64":
            message = f"Unsupported encoding '{encoding}' for '{path}'"
            logger.error(message)
            raise GitHubRepoSyncError(message)

        try:
            decoded_bytes = base64.b64decode(content.encode("utf-8"))
        except (TypeError, ValueError) as exc:
            message = f"Failed to decode Base64 content for '{path}': {exc}"
            logger.error(message)
            raise GitHubRepoSyncError(message) from exc

        try:
            return json.loads(decoded_bytes.decode("utf-8"))
        except json.JSONDecodeError as exc:
            message = f"Failed to parse JSON for '{path}': {exc}"
            logger.error(message)
            raise GitHubRepoSyncError(message) from exc

    def _build_contents_url(self, path: str) -> str:
        """Construct a GitHub Contents API URL."""
        normalised_path = path.strip("/")
        return f"{self._base_url}/repos/{self._repo_owner}/{self._repo_name}/contents/{normalised_path}"

    def _build_headers(self) -> Dict[str, str]:
        """Construct HTTP headers for GitHub API requests."""
        return {
            "Authorization": f"token {self._token}",
            "Accept": "application/vnd.github+json",
        }

    @staticmethod
    def _normalise_case_path(case_path: str, directory: str) -> str:
        """Ensure test case path is rooted within the target directory."""
        normalised_case = case_path.strip("/")
        normalised_dir = directory.strip("/")

        if not normalised_dir:
            return normalised_case
        if normalised_case.startswith(f"{normalised_dir}/"):
            return normalised_case
        return f"{normalised_dir}/{normalised_case}"

