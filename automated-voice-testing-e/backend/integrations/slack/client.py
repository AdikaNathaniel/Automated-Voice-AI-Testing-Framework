"""
Slack notification client.

Provides a minimal async wrapper around Slack incoming webhooks to broadcast
test run summaries to team channels.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class SlackClientError(RuntimeError):
    """Raised when the Slack client fails to deliver a message."""


class SlackClient:
    """Client for posting notifications to Slack via incoming webhooks."""

    VALID_STATUSES = {"success", "failure", "warning"}
    STATUS_EMOJI = {
        "success": ":white_check_mark:",
        "failure": ":x:",
        "warning": ":warning:",
    }
    STATUS_LABEL = {
        "success": "passed",
        "failure": "failed",
        "warning": "completed",
    }
    SYSTEM_SEVERITY_EMOJI = {
        "critical": ":fire:",
        "warning": ":warning:",
        "info": ":information_source:",
    }

    def __init__(
        self,
        *,
        webhook_url: str,
        default_channel: Optional[str] = None,
        username: Optional[str] = None,
        icon_emoji: Optional[str] = None,
        timeout: float = 10.0,
    ) -> None:
        if not webhook_url:
            raise ValueError("Slack webhook URL is required")

        self._webhook_url = webhook_url
        self._default_channel = default_channel
        self._username = username
        self._icon_emoji = icon_emoji
        self._timeout = timeout

    async def send_test_run_notification(
        self,
        *,
        status: str,
        passed: int,
        failed: int,
        duration_seconds: float,
        run_url: str,
        channel: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Post a summary of a test run to Slack.

        Args:
            status: One of success, failure, warning.
            passed: Count of passed tests.
            failed: Count of failed tests.
            duration_seconds: Total run duration in seconds.
            run_url: Link to the detailed run report.
            channel: Optional Slack channel override (e.g., "#qa-alerts").

        Returns:
            Parsed JSON response from Slack.

        Raises:
            ValueError: If supplied parameters are invalid.
            SlackClientError: If the request fails or Slack returns an error.
        """
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status '{status}'. Must be one of {sorted(self.VALID_STATUSES)}")

        summary_text = self._build_summary_text(status, passed, failed, duration_seconds, run_url)
        payload: Dict[str, Any] = {
            "text": summary_text,
            "blocks": self._build_blocks(status, passed, failed, duration_seconds, run_url),
        }

        return await self._dispatch(payload, channel=channel)

    async def send_critical_defect_alert(
        self,
        *,
        defect_id: str,
        title: str,
        severity: str,
        defect_url: str,
        description: Optional[str] = None,
        channel: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Post an alert highlighting a newly discovered critical defect.
        """
        if not defect_id:
            raise ValueError("defect_id is required for critical defect alerts")
        if not title:
            raise ValueError("title is required for critical defect alerts")
        if not severity:
            raise ValueError("severity is required for critical defect alerts")
        if not defect_url:
            raise ValueError("defect_url is required for critical defect alerts")

        severity_display = severity.upper()
        summary = (
            f":rotating_light: Critical defect detected – "
            f"[{severity_display}] {title}. <{defect_url}|View details>"
        )
        blocks: List[Dict[str, Any]] = [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": summary},
            }
        ]

        if description:
            blocks.append(
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": description},
                }
            )

        blocks.append(
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": f"*Defect ID:* `{defect_id}`"},
                    {"type": "mrkdwn", "text": f"*Severity:* {severity_display}"},
                ],
            }
        )

        payload: Dict[str, Any] = {
            "text": summary,
            "blocks": blocks,
        }

        return await self._dispatch(payload, channel=channel)

    async def send_system_alert(
        self,
        *,
        severity: str,
        title: str,
        message: str,
        alert_url: Optional[str] = None,
        channel: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Post a system alert notification to Slack.
        """
        if not severity:
            raise ValueError("severity is required for system alerts")
        if not title:
            raise ValueError("title is required for system alerts")
        if not message:
            raise ValueError("message is required for system alerts")

        severity_key = severity.lower()
        severity_display = severity.upper()
        emoji = self.SYSTEM_SEVERITY_EMOJI.get(severity_key, ":speech_balloon:")

        summary = f"{emoji} System alert – [{severity_display}] {title}"
        if alert_url:
            summary = f"{summary}. <{alert_url}|View details>"

        blocks: List[Dict[str, Any]] = [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": summary},
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": message},
            },
        ]

        context_elements: List[Dict[str, Any]] = [{"type": "mrkdwn", "text": f"*Severity:* {severity_display}"}]
        if alert_url:
            context_elements.append({"type": "mrkdwn", "text": f"<{alert_url}|Investigate>"})

        blocks.append(
            {
                "type": "context",
                "elements": context_elements,
            }
        )

        payload: Dict[str, Any] = {
            "text": summary,
            "blocks": blocks,
        }

        return await self._dispatch(payload, channel=channel)

    async def send_edge_case_alert(
        self,
        *,
        edge_case_id: str,
        title: str,
        category: str,
        severity: str,
        edge_case_url: str,
        scenario_name: Optional[str] = None,
        description: Optional[str] = None,
        channel: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Post an alert about a newly discovered edge case.

        Args:
            edge_case_id: Unique identifier of the edge case
            title: Edge case title
            category: Edge case category (e.g., ambiguous_intent, boundary_condition)
            severity: Severity level (critical, high, medium, low)
            edge_case_url: Link to view the edge case details
            scenario_name: Optional name of the scenario that triggered this
            description: Optional description or validator feedback
            channel: Optional Slack channel override

        Returns:
            Parsed response from Slack

        Raises:
            ValueError: If required parameters are missing
            SlackClientError: If the request fails
        """
        if not edge_case_id:
            raise ValueError("edge_case_id is required for edge case alerts")
        if not title:
            raise ValueError("title is required for edge case alerts")
        if not category:
            raise ValueError("category is required for edge case alerts")
        if not severity:
            raise ValueError("severity is required for edge case alerts")
        if not edge_case_url:
            raise ValueError("edge_case_url is required for edge case alerts")

        severity_lower = severity.lower()
        severity_display = severity.upper()
        category_display = category.replace("_", " ").title()

        # Use appropriate emoji based on severity
        severity_emoji = {
            "critical": ":rotating_light:",
            "high": ":warning:",
            "medium": ":large_yellow_circle:",
            "low": ":information_source:",
        }
        emoji = severity_emoji.get(severity_lower, ":speech_balloon:")

        summary = f"{emoji} New Edge Case – [{severity_display}] {title}. <{edge_case_url}|View details>"

        blocks: List[Dict[str, Any]] = [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": summary},
            }
        ]

        if description:
            blocks.append(
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"_{description}_"},
                }
            )

        context_elements: List[Dict[str, Any]] = [
            {"type": "mrkdwn", "text": f"*ID:* `{edge_case_id}`"},
            {"type": "mrkdwn", "text": f"*Category:* {category_display}"},
            {"type": "mrkdwn", "text": f"*Severity:* {severity_display}"},
        ]

        if scenario_name:
            context_elements.append(
                {"type": "mrkdwn", "text": f"*Scenario:* {scenario_name}"}
            )

        blocks.append(
            {
                "type": "context",
                "elements": context_elements,
            }
        )

        payload: Dict[str, Any] = {
            "text": summary,
            "blocks": blocks,
        }

        return await self._dispatch(payload, channel=channel)

    def _build_summary_text(
        self,
        status: str,
        passed: int,
        failed: int,
        duration_seconds: float,
        run_url: str,
    ) -> str:
        emoji = self.STATUS_EMOJI.get(status, ":information_source:")
        label = self.STATUS_LABEL.get(status, "completed")
        total = passed + failed
        duration_str = self._format_duration(duration_seconds)
        return (
            f"{emoji} Test run {label} – {passed} passed, {failed} failed "
            f"({total} total) in {duration_str}. <{run_url}|View results>"
        )

    def _build_blocks(
        self,
        status: str,
        passed: int,
        failed: int,
        duration_seconds: float,
        run_url: str,
    ) -> List[Dict[str, Any]]:
        summary = self._build_summary_text(status, passed, failed, duration_seconds, run_url)
        detail_lines = [
            f"*Passed:* {passed}",
            f"*Failed:* {failed}",
            f"*Duration:* {self._format_duration(duration_seconds)}",
        ]
        return [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": summary},
            },
            {
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": " • ".join(detail_lines)}],
            },
        ]

    @staticmethod
    def _format_duration(duration_seconds: float) -> str:
        """Format a duration (in seconds) into a human friendly string."""
        if duration_seconds < 0:
            return "0s"

        total_seconds = int(round(duration_seconds))
        minutes, seconds = divmod(total_seconds, 60)
        hours, minutes = divmod(minutes, 60)

        parts = []
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")
        return " ".join(parts)

    async def _dispatch(self, payload: Dict[str, Any], *, channel: Optional[str]) -> Dict[str, Any]:
        """
        Apply default envelope settings and deliver the payload to Slack.
        """
        enriched_payload = dict(payload)

        target_channel = channel or self._default_channel
        if target_channel:
            enriched_payload["channel"] = target_channel
        if self._username:
            enriched_payload["username"] = self._username
        if self._icon_emoji:
            enriched_payload["icon_emoji"] = self._icon_emoji

        logger.debug("Sending Slack notification to %s: %s", self._webhook_url, enriched_payload)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self._webhook_url,
                    json=enriched_payload,
                    timeout=self._timeout,
                )
                response.raise_for_status()
                # Slack incoming webhooks return plain text "ok" on success, not JSON
                # Handle both cases for compatibility
                text = response.text.strip()
                if text == "ok":
                    return {"ok": True}
                try:
                    return response.json()
                except Exception:
                    return {"ok": True, "response": text}

        except httpx.HTTPStatusError as exc:
            message = f"Slack API error: {str(exc)}"
            logger.error(message)
            raise SlackClientError(message) from exc
        except httpx.TimeoutException as exc:
            message = f"Slack request timed out: {str(exc)}"
            logger.error(message)
            raise SlackClientError(message) from exc
        except httpx.RequestError as exc:
            message = f"Failed to communicate with Slack: {str(exc)}"
            logger.error(message)
            raise SlackClientError(message) from exc
