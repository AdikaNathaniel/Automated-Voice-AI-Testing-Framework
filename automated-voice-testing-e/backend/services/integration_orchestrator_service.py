"""
Integration Orchestrator Service

Automatically triggers integrations after test suite completion:
- GitHub: Auto-creates issues for failed tests
- Jira: Auto-creates tickets for defects
- Slack: Sends completion notifications

This service is the bridge between test execution and external integrations,
making the "auto-create" functionality work as advertised in the UI.
"""

from __future__ import annotations

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from integrations.github.client import GitHubClient, GitHubClientError
from integrations.jira.client import JiraClient, JiraClientError
from models.integration_config import IntegrationConfig
from models.multi_turn_execution import MultiTurnExecution
from models.suite_run import SuiteRun
from models.defect import Defect
from services.defect_service import create_defect, SEVERITY_PRIORITY_MAP
from services.notification_service import get_tenant_notification_service, should_send_notification

logger = logging.getLogger(__name__)


class IntegrationOrchestratorError(RuntimeError):
    """Raised when integration orchestration fails."""


async def trigger_integrations_after_suite_run(
    db: AsyncSession,
    suite_run_id: UUID,
    tenant_id: UUID,
) -> dict[str, any]:
    """
    Trigger all enabled integrations after a suite run completes.

    This is the main entry point that orchestrates all integration actions:
    1. Fetches failed executions from the suite run
    2. Loads tenant's integration configs
    3. Creates GitHub issues for failures (if enabled)
    4. Creates Jira tickets for defects (if enabled)
    5. Sends Slack notifications (if enabled)

    Args:
        db: Database session
        suite_run_id: UUID of the completed suite run
        tenant_id: UUID of the tenant (for multi-tenant isolation)

    Returns:
        Dict with integration results:
        {
            "github_issues_created": 3,
            "jira_tickets_created": 2,
            "slack_notification_sent": True,
            "errors": ["error1", "error2"]
        }

    Example:
        >>> await trigger_integrations_after_suite_run(db, suite_run_id, tenant_id)
        {"github_issues_created": 3, "jira_tickets_created": 0, "slack_notification_sent": True}
    """
    logger.info(f"Triggering integrations for suite run {suite_run_id} (tenant: {tenant_id})")

    results = {
        "github_issues_created": 0,
        "jira_tickets_created": 0,
        "slack_notification_sent": False,
        "errors": [],
    }

    try:
        # Fetch suite run with eager loading for relationships
        result = await db.execute(
            select(SuiteRun)
            .options(selectinload(SuiteRun.suite))
            .where(SuiteRun.id == suite_run_id)
        )
        suite_run = result.scalar_one_or_none()
        if not suite_run:
            logger.warning(f"Suite run {suite_run_id} not found, skipping integrations")
            return results

        # Fetch failed executions
        failed_executions = await _get_failed_executions(db, suite_run_id)
        logger.info(f"Found {len(failed_executions)} failed executions for suite run {suite_run_id}")

        # Fetch integration configs for this tenant
        github_config = await _get_integration_config(db, tenant_id, "github")
        jira_config = await _get_integration_config(db, tenant_id, "jira")

        # GitHub: Auto-create issues for failed tests
        if github_config and github_config.is_enabled and github_config.is_connected:
            if github_config.github_auto_create_issues and failed_executions:
                try:
                    issues_created = await _create_github_issues_for_failures(
                        db=db,
                        tenant_id=tenant_id,
                        suite_run=suite_run,
                        failed_executions=failed_executions,
                        github_config=github_config,
                    )
                    results["github_issues_created"] = issues_created
                    logger.info(f"Created {issues_created} GitHub issues for suite run {suite_run_id}")
                except Exception as exc:
                    error_msg = f"GitHub issue creation failed: {exc}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)

        # Jira: Auto-create tickets for defects
        if jira_config and jira_config.is_enabled and jira_config.is_connected:
            if jira_config.jira_auto_create_tickets and failed_executions:
                try:
                    tickets_created = await _create_jira_tickets_for_failures(
                        db=db,
                        tenant_id=tenant_id,
                        suite_run=suite_run,
                        failed_executions=failed_executions,
                        jira_config=jira_config,
                    )
                    results["jira_tickets_created"] = tickets_created
                    logger.info(f"Created {tickets_created} Jira tickets for suite run {suite_run_id}")
                except Exception as exc:
                    error_msg = f"Jira ticket creation failed: {exc}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)

        # Slack: Send suite completion notification
        try:
            notification_sent = await _send_slack_notification(
                db=db,
                tenant_id=tenant_id,
                suite_run=suite_run,
            )
            results["slack_notification_sent"] = notification_sent
        except Exception as exc:
            error_msg = f"Slack notification failed: {exc}"
            logger.error(error_msg)
            results["errors"].append(error_msg)

    except Exception as exc:
        error_msg = f"Integration orchestration failed: {exc}"
        logger.error(error_msg)
        results["errors"].append(error_msg)

    return results


async def _get_integration_config(
    db: AsyncSession,
    tenant_id: UUID,
    integration_type: str,
) -> Optional[IntegrationConfig]:
    """
    Fetch integration config for a specific tenant and integration type.

    Args:
        db: Database session
        tenant_id: Tenant UUID
        integration_type: Integration type (github, jira, slack)

    Returns:
        IntegrationConfig or None if not found
    """
    result = await db.execute(
        select(IntegrationConfig).where(
            IntegrationConfig.tenant_id == tenant_id,
            IntegrationConfig.integration_type == integration_type,
        )
    )
    return result.scalar_one_or_none()


async def _get_failed_executions(
    db: AsyncSession,
    suite_run_id: UUID,
) -> list[MultiTurnExecution]:
    """
    Fetch all failed executions for a suite run with eager loading.

    Eager loads script and validation_results relationships to avoid N+1 queries
    when building GitHub issues and Jira tickets.

    Args:
        db: Database session
        suite_run_id: Suite run UUID

    Returns:
        List of failed MultiTurnExecution objects with relationships loaded
    """
    result = await db.execute(
        select(MultiTurnExecution)
        .options(
            selectinload(MultiTurnExecution.script),
            selectinload(MultiTurnExecution.validation_results),
        )
        .where(
            MultiTurnExecution.suite_run_id == suite_run_id,
            MultiTurnExecution.status.in_(["failed", "error"]),
        )
    )
    return list(result.scalars().all())


async def _create_github_issues_for_failures(
    db: AsyncSession,
    tenant_id: UUID,
    suite_run: SuiteRun,
    failed_executions: list[MultiTurnExecution],
    github_config: IntegrationConfig,
) -> int:
    """
    Create GitHub issues for all failed test executions.

    Args:
        db: Database session
        tenant_id: Tenant UUID
        suite_run: Suite run object
        failed_executions: List of failed executions
        github_config: GitHub integration config

    Returns:
        Number of issues created

    Raises:
        GitHubClientError: If GitHub API calls fail
    """
    # Get GitHub access token
    access_token = github_config.get_access_token()
    if not access_token:
        logger.warning("GitHub access token not set, skipping issue creation")
        return 0

    # Get repository from settings
    repositories = github_config.github_repositories
    if not repositories:
        logger.warning("No GitHub repositories configured, skipping issue creation")
        return 0

    # Use first repository as default (format: "owner/repo")
    repository = repositories[0]

    # Parse repository into owner and name
    if "/" not in repository:
        logger.error(f"Invalid repository format: {repository}, expected 'owner/repo'")
        return 0

    repo_owner, repo_name = repository.split("/", 1)

    # Create GitHub client
    github_client = GitHubClient(
        token=access_token,
        repo_owner=repo_owner,
        repo_name=repo_name,
    )

    issues_created = 0

    for execution in failed_executions:
        try:
            # Build issue payload
            issue_data = _build_github_issue_payload(execution, suite_run)

            # Create issue (returns full GitHub API response dict)
            response = await github_client.create_issue(
                title=issue_data["title"],
                body=issue_data["body"],
                labels=issue_data.get("labels", []),
            )

            # Extract issue URL from response
            issue_url = response.get("html_url", "Unknown URL")

            logger.info(f"Created GitHub issue for execution {execution.id}: {issue_url}")
            issues_created += 1

        except GitHubClientError as exc:
            logger.error(f"Failed to create GitHub issue for execution {execution.id}: {exc}")
            # Continue creating other issues even if one fails

    return issues_created


async def _create_jira_tickets_for_failures(
    db: AsyncSession,
    tenant_id: UUID,
    suite_run: SuiteRun,
    failed_executions: list[MultiTurnExecution],
    jira_config: IntegrationConfig,
) -> int:
    """
    Create Jira tickets for all failed test executions.

    For each failed execution, creates a Defect record and then
    creates a corresponding Jira ticket.

    Args:
        db: Database session
        tenant_id: Tenant UUID
        suite_run: Suite run object
        failed_executions: List of failed executions
        jira_config: Jira integration config

    Returns:
        Number of tickets created

    Raises:
        JiraClientError: If Jira API calls fail
    """
    # Get Jira credentials
    api_token = jira_config.get_access_token()
    if not api_token:
        logger.warning("Jira API token not set, skipping ticket creation")
        return 0

    instance_url = jira_config.jira_instance_url
    email = jira_config.jira_email
    project_key = jira_config.jira_project_key
    issue_type = jira_config.jira_issue_type

    if not all([instance_url, email, project_key]):
        logger.warning("Jira configuration incomplete, skipping ticket creation")
        return 0

    # Normalize Jira base URL to include /rest/api/3
    normalized_url = instance_url.rstrip('/')
    if not normalized_url.endswith('/rest/api/3'):
        if '/rest/api' not in normalized_url:
            normalized_url = f"{normalized_url}/rest/api/3"
            logger.debug(f"Normalized Jira URL from '{instance_url}' to '{normalized_url}'")

    # Create Jira client
    jira_client = JiraClient(
        base_url=normalized_url,
        email=email,
        api_token=api_token,
    )

    tickets_created = 0

    for execution in failed_executions:
        try:
            # Create defect record with Jira ticket
            defect_data = _build_defect_data_from_execution(
                execution=execution,
                suite_run=suite_run,
                tenant_id=tenant_id,
            )

            # Create defect with Jira integration
            defect = await create_defect(
                db=db,
                data=defect_data,
                jira_client=jira_client,
                jira_project_key=project_key,
                jira_issue_type=issue_type,
                jira_browse_base_url=instance_url,
            )

            logger.info(f"Created Jira ticket for execution {execution.id}: {defect.jira_issue_key}")
            tickets_created += 1

        except JiraClientError as exc:
            logger.error(f"Failed to create Jira ticket for execution {execution.id}: {exc}")
            # Continue creating other tickets even if one fails

    return tickets_created


async def _send_slack_notification(
    db: AsyncSession,
    tenant_id: UUID,
    suite_run: SuiteRun,
) -> bool:
    """
    Send Slack notification for suite run completion.

    Uses the existing notification service infrastructure.

    Args:
        db: Database session
        tenant_id: Tenant UUID
        suite_run: Suite run object

    Returns:
        True if notification was sent, False otherwise
    """
    try:
        # Get tenant-specific notification service
        notification_service, preferences = await get_tenant_notification_service(db, tenant_id)

        # Check if suite run notifications are enabled
        should_send, channel = should_send_notification(
            preferences=preferences,
            notification_type="suiteRun",
        )

        if not should_send:
            logger.debug(f"Suite run notifications disabled for tenant {tenant_id}")
            return False

        # Build notification data
        status = "success" if suite_run.status == "completed" else "failure"
        passed = suite_run.passed_tests or 0
        failed = suite_run.failed_tests or 0
        duration = suite_run.duration_seconds or 0.0

        # Build absolute suite run URL for clickable link in Slack
        from api.config import get_settings
        settings = get_settings()
        frontend_url = settings.FRONTEND_URL.rstrip('/')
        run_url = f"{frontend_url}/suite-runs/{suite_run.id}"

        # Send notification
        await notification_service.notify_test_run_result(
            status=status,
            passed=passed,
            failed=failed,
            duration_seconds=duration,
            run_url=run_url,
        )

        logger.info(f"Sent Slack notification for suite run {suite_run.id}")
        return True

    except Exception as exc:
        logger.error(f"Failed to send Slack notification for suite run {suite_run.id}: {exc}")
        return False


def _build_github_issue_payload(
    execution: MultiTurnExecution,
    suite_run: SuiteRun,
) -> dict[str, any]:
    """
    Build GitHub issue payload from failed execution.

    Args:
        execution: Failed execution object
        suite_run: Suite run object

    Returns:
        Dict with title, body, and labels for GitHub issue
    """
    # Get scenario name from execution
    scenario_name = getattr(execution.script, "name", "Unknown Scenario") if execution.script else "Unknown Scenario"

    # Get language code from validation results if available
    language_code = None
    if execution.validation_results:
        # Get language from first validation result
        first_validation = execution.validation_results[0]
        language_code = getattr(first_validation, "language_code", None)

    # Build title
    title = f"Test Failure: {scenario_name}"
    if language_code:
        title += f" ({language_code})"

    # Calculate duration
    duration_str = "N/A"
    if execution.started_at and execution.completed_at:
        duration = (execution.completed_at - execution.started_at).total_seconds()
        duration_str = f"{duration:.2f}s"

    # Build body
    body_parts = [
        f"## Test Failure Report",
        f"",
        f"**Suite Run**: {suite_run.suite.name if suite_run.suite else 'Unknown Suite'}",
        f"**Scenario**: {scenario_name}",
        f"**Language**: {language_code or 'N/A'}",
        f"**Status**: {execution.status}",
        f"**Duration**: {duration_str}",
        f"**Started**: {execution.started_at.isoformat() if execution.started_at else 'N/A'}",
        f"**Completed**: {execution.completed_at.isoformat() if execution.completed_at else 'N/A'}",
        f"",
        f"### Error Details",
        f"```",
        execution.error_message or "No error details available",
        f"```",
        f"",
        f"### Steps Completed",
        f"{execution.current_step_order}/{execution.total_steps}",
    ]

    body = "\n".join(body_parts)

    # Build labels
    labels = ["automated-test", "test-failure"]
    if language_code:
        labels.append(f"lang:{language_code}")
    if execution.status == "error":
        labels.append("error")

    return {
        "title": title,
        "body": body,
        "labels": labels,
    }


def _build_defect_data_from_execution(
    execution: MultiTurnExecution,
    suite_run: SuiteRun,
    tenant_id: UUID,
) -> dict[str, any]:
    """
    Build defect data from failed execution for Jira ticket creation.

    Args:
        execution: Failed execution object
        suite_run: Suite run object
        tenant_id: Tenant UUID

    Returns:
        Dict with defect data
    """
    # Get scenario name
    scenario_name = getattr(execution.script, "name", "Unknown Scenario") if execution.script else "Unknown Scenario"

    # Get language code from validation results if available
    language_code = None
    if execution.validation_results:
        # Get language from first validation result
        first_validation = execution.validation_results[0]
        language_code = getattr(first_validation, "language_code", None)

    # Build title
    title = f"Test Failure: {scenario_name}"
    if language_code:
        title += f" ({language_code})"

    # Build description
    description_parts = [
        f"Test execution failed in suite run: {suite_run.suite.name if suite_run.suite else 'Unknown Suite'}",
        f"",
        f"Scenario: {scenario_name}",
        f"Language: {language_code or 'N/A'}",
        f"Status: {execution.status}",
        f"Steps completed: {execution.current_step_order}/{execution.total_steps}",
        f"",
        f"Error details:",
        execution.error_message or "No error details available",
    ]

    description = "\n".join(description_parts)

    # Determine severity based on execution status
    severity = "high" if execution.status == "error" else "medium"

    return {
        "tenant_id": tenant_id,
        "title": title,
        "description": description,
        "severity": severity,
        "status": "open",
        "category": "test_failure",
        "execution_id": execution.id,
        "suite_run_id": suite_run.id,
        "script_id": execution.script_id,
        "language_code": language_code,
        "detected_at": execution.completed_at or execution.started_at,
    }
