"""
Notification service coordinating outbound alerts across channels.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Optional

from integrations.github.client import GitHubClient, GitHubClientError
from integrations.slack.client import SlackClient, SlackClientError

logger = logging.getLogger(__name__)

# Severity levels that should trigger immediate alerts
ALERT_SEVERITIES = {"critical", "high"}


class NotificationServiceError(RuntimeError):
    """Raised when the notification service fails to deliver a message."""


class NotificationService:
    """
    Provides a unified interface for dispatching notifications to multiple channels.
    """

    def __init__(
        self,
        *,
        slack_client: Optional[SlackClient] = None,
        github_client: Optional[GitHubClient] = None,
        github_default_context: str = "continuous-integration/automated-testing",
    ) -> None:
        self._slack_client = slack_client
        self._github_client = github_client
        self._github_default_context = github_default_context

    async def notify_test_run_result(
        self,
        *,
        status: str,
        passed: int,
        failed: int,
        duration_seconds: float,
        run_url: str,
        commit_sha: Optional[str] = None,
        github_context: Optional[str] = None,
    ) -> None:
        """
        Notify configured channels about the outcome of a test run.

        Args:
            status: Overall status of the run (success, failure, warning).
            passed: Number of passed tests.
            failed: Number of failed tests.
            duration_seconds: Execution duration.
            run_url: URL with detailed run results.
            commit_sha: Optional commit SHA to update on GitHub.
            github_context: Optional GitHub status context override.

        Raises:
            NotificationServiceError: If one or more channels fail.
        """
        errors: list[str] = []

        # Send Slack notification if configured
        if self._slack_client:
            try:
                await self._slack_client.send_test_run_notification(
                    status=status,
                    passed=passed,
                    failed=failed,
                    duration_seconds=duration_seconds,
                    run_url=run_url,
                )
            except SlackClientError as exc:
                message = f"Slack notification failed: {exc}"
                logger.error(message)
                errors.append(message)

        # Update GitHub commit status if configured
        if self._github_client and commit_sha:
            github_state = self._map_status_to_github(status)
            try:
                await self._github_client.set_commit_status(
                    sha=commit_sha,
                    state=github_state,
                    target_url=run_url,
                    description=self._build_commit_description(passed, failed),
                    context=github_context or self._github_default_context,
                )
            except GitHubClientError as exc:
                message = f"GitHub status update failed: {exc}"
                logger.error(message)
                errors.append(message)

        if errors:
            raise NotificationServiceError("; ".join(errors))

    async def notify_critical_defect(
        self,
        *,
        defect_id: str,
        title: str,
        severity: str,
        defect_url: str,
        description: Optional[str] = None,
    ) -> None:
        """
        Notify configured channels about a newly discovered critical defect.
        """
        errors: list[str] = []

        if self._slack_client:
            try:
                await self._slack_client.send_critical_defect_alert(
                    defect_id=defect_id,
                    title=title,
                    severity=severity,
                    defect_url=defect_url,
                    description=description,
                )
            except SlackClientError as exc:
                message = f"Slack notification failed: {exc}"
                logger.error(message)
                errors.append(message)

        if errors:
            raise NotificationServiceError("; ".join(errors))

    async def notify_system_alert(
        self,
        *,
        severity: str,
        title: str,
        message: str,
        alert_url: Optional[str] = None,
    ) -> None:
        """
        Notify configured channels about a system alert.
        """
        errors: list[str] = []

        if self._slack_client:
            try:
                await self._slack_client.send_system_alert(
                    severity=severity,
                    title=title,
                    message=message,
                    alert_url=alert_url,
                )
            except SlackClientError as exc:
                message = f"Slack notification failed: {exc}"
                logger.error(message)
                errors.append(message)

        if errors:
            raise NotificationServiceError("; ".join(errors))

    async def notify_edge_case_created(
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
        force: bool = False,
    ) -> None:
        """
        Notify configured channels about a newly created edge case.

        By default, only alerts for critical/high severity edge cases.
        Use force=True to send notification regardless of severity.

        Args:
            edge_case_id: Unique identifier of the edge case
            title: Edge case title
            category: Edge case category
            severity: Severity level (critical, high, medium, low)
            edge_case_url: URL to view edge case details
            scenario_name: Optional scenario name that triggered this
            description: Optional description or validator feedback
            channel: Optional channel override for Slack
            force: Send notification regardless of severity threshold

        Raises:
            NotificationServiceError: If notification delivery fails
        """
        # Only alert on critical/high severity unless forced
        if not force and severity.lower() not in ALERT_SEVERITIES:
            logger.debug(
                "Skipping edge case notification for %s severity edge case %s",
                severity,
                edge_case_id,
            )
            return

        errors: list[str] = []

        if self._slack_client:
            try:
                await self._slack_client.send_edge_case_alert(
                    edge_case_id=edge_case_id,
                    title=title,
                    category=category,
                    severity=severity,
                    edge_case_url=edge_case_url,
                    scenario_name=scenario_name,
                    description=description,
                    channel=channel,
                )
                logger.info(
                    "Sent Slack notification for edge case %s (severity: %s)",
                    edge_case_id,
                    severity,
                )
            except SlackClientError as exc:
                message = f"Slack notification failed: {exc}"
                logger.error(message)
                errors.append(message)

        if errors:
            raise NotificationServiceError("; ".join(errors))

    @staticmethod
    def _build_commit_description(passed: int, failed: int) -> str:
        """Create a short description summarising run results for GitHub."""
        return f"{passed} passed, {failed} failed"

    @staticmethod
    def _map_status_to_github(status: str) -> str:
        """Map internal status keywords to GitHub commit status states."""
        mapping = {
            "success": "success",
            "failure": "failure",
            "warning": "failure",
            "pending": "pending",
        }
        return mapping.get(status, "error")


@lru_cache()
def get_notification_service() -> NotificationService:
    """
    Get a configured NotificationService instance (singleton).

    Creates a NotificationService with Slack client configured from settings.
    If Slack is not configured, returns a service with no active channels.

    Note: This uses global settings. For tenant-specific notifications,
    use get_tenant_notification_service() instead.

    Returns:
        NotificationService: Configured notification service instance
    """
    from api.config import get_settings

    settings = get_settings()

    slack_client = None
    if (
        settings.SLACK_NOTIFICATIONS_ENABLED
        and settings.SLACK_WEBHOOK_URL
    ):
        slack_client = SlackClient(
            webhook_url=settings.SLACK_WEBHOOK_URL,
            default_channel=settings.SLACK_ALERT_CHANNEL,
        )
        logger.info("Slack notifications enabled (global config)")
    else:
        logger.debug("Slack notifications disabled or not configured (global config)")

    return NotificationService(slack_client=slack_client)


async def get_tenant_notification_service(
    db,
    tenant_id,
) -> tuple[NotificationService, Optional[dict]]:
    """
    Get a NotificationService configured for a specific tenant.

    Looks up the tenant's notification config from the database
    and returns a service configured with their settings.

    Args:
        db: AsyncSession database connection
        tenant_id: UUID of the tenant (user)

    Returns:
        Tuple of (NotificationService, notification_preferences dict or None)
        notification_preferences contains per-event-type settings like:
        {"edgeCase": {"enabled": True, "channel": "#alerts"}, ...}
    """
    from sqlalchemy import select
    from models.notification_config import NotificationConfig

    # Look up tenant's Slack config
    result = await db.execute(
        select(NotificationConfig).where(
            NotificationConfig.tenant_id == tenant_id,
            NotificationConfig.channel_type == "slack",
        )
    )
    config = result.scalar_one_or_none()

    if not config or not config.is_enabled or not config.is_connected:
        logger.debug(
            "Slack notifications not configured for tenant %s",
            tenant_id,
        )
        return NotificationService(slack_client=None), None

    # Get decrypted webhook URL
    webhook_url = config.get_webhook_url()
    if not webhook_url:
        logger.debug(
            "Slack webhook URL not set for tenant %s",
            tenant_id,
        )
        return NotificationService(slack_client=None), None

    slack_client = SlackClient(
        webhook_url=webhook_url,
        default_channel=config.default_channel,
    )

    logger.debug(
        "Created tenant-specific Slack notification service for %s",
        tenant_id,
    )

    return NotificationService(slack_client=slack_client), config.notification_preferences


def should_send_notification(
    preferences: Optional[dict],
    notification_type: str,
    severity: Optional[str] = None,
) -> tuple[bool, Optional[str]]:
    """
    Check if a notification should be sent based on tenant preferences.

    Args:
        preferences: Notification preferences dict from NotificationConfig
        notification_type: Type of notification (suiteRun, criticalDefect, systemAlert, edgeCase)
        severity: Optional severity level for edge case filtering

    Returns:
        Tuple of (should_send: bool, channel: str or None)
    """
    # Default to enabled if no preferences set
    if not preferences:
        return True, None

    pref = preferences.get(notification_type, {})
    enabled = pref.get("enabled", True)
    channel = pref.get("channel", "") or None

    if not enabled:
        return False, None

    # For edge cases, also check severity threshold
    if notification_type == "edgeCase" and severity:
        if severity.lower() not in ALERT_SEVERITIES:
            return False, None

    return True, channel
