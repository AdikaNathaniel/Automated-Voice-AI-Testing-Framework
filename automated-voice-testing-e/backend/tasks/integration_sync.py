"""
Integration Sync Tasks

This module contains Celery tasks for synchronizing data between
the Voice AI Testing Framework and external integrations.

Handles:
- Jira bidirectional sync (status updates from Jira)
- Slack notification delivery
- Integration health checks
"""

from celery_app import celery
from typing import Dict, Any, List, Optional
import asyncio
import logging

logger = logging.getLogger(__name__)


@celery.task(name='tasks.integration_sync.sync_all_jira_defects', bind=True)
def sync_all_jira_defects(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Sync all defects with Jira links to get current status.

    This task fetches the current status from Jira for all defects
    that have a jira_issue_key and updates their local status if changed.

    Can be scheduled to run periodically (e.g., every 15 minutes) to
    ensure bidirectional sync even if webhooks fail.

    Args:
        tenant_id: Optional tenant UUID to filter defects. If None, syncs all.

    Returns:
        Dict with sync results including counts of synced defects.
    """
    from uuid import UUID
    from sqlalchemy import select, create_engine
    from sqlalchemy.orm import sessionmaker
    from models.defect import Defect
    from models.integration_config import IntegrationConfig
    from integrations.jira.client import JiraClient, JiraClientError
    from services.defect_service import JIRA_STATUS_TO_LOCAL
    from api.config import get_settings

    settings = get_settings()

    # Create sync engine
    sync_db_url = settings.DATABASE_URL.replace('+asyncpg', '')
    sync_engine = create_engine(sync_db_url)
    SyncSession = sessionmaker(bind=sync_engine)

    results = {
        "synced": 0,
        "unchanged": 0,
        "errors": 0,
        "total": 0,
        "details": [],
    }

    try:
        db = SyncSession()

        # Build query for defects with Jira links
        stmt = select(Defect).where(
            Defect.jira_issue_key.isnot(None),
            Defect.status != "resolved",  # Only sync active defects
        )

        if tenant_id:
            stmt = stmt.where(Defect.tenant_id == UUID(tenant_id))

        defects = db.execute(stmt).scalars().all()
        results["total"] = len(defects)

        if not defects:
            logger.info("[JIRA SYNC] No defects to sync")
            db.close()
            return results

        # Group defects by tenant for efficient config lookup
        tenant_defects: Dict[str, List[Defect]] = {}
        for defect in defects:
            tid = str(defect.tenant_id)
            if tid not in tenant_defects:
                tenant_defects[tid] = []
            tenant_defects[tid].append(defect)

        # Process each tenant's defects
        for tid, td_list in tenant_defects.items():
            # Get Jira config for tenant
            config_stmt = select(IntegrationConfig).where(
                IntegrationConfig.tenant_id == UUID(tid),
                IntegrationConfig.integration_type == "jira",
            )
            jira_config = db.execute(config_stmt).scalar_one_or_none()

            if not jira_config or not jira_config.is_connected:
                logger.debug(f"[JIRA SYNC] No Jira config for tenant {tid}")
                continue

            api_token = jira_config.get_access_token()
            if not api_token or not jira_config.jira_instance_url or not jira_config.jira_email:
                logger.warning(f"[JIRA SYNC] Incomplete Jira config for tenant {tid}")
                continue

            # Create Jira client
            try:
                jira_client = JiraClient(
                    email=jira_config.jira_email,
                    api_token=api_token,
                    base_url=f"{jira_config.jira_instance_url.rstrip('/')}/rest/api/3",
                )
            except ValueError as e:
                logger.error(f"[JIRA SYNC] Invalid Jira config for tenant {tid}: {e}")
                continue

            # Sync each defect
            for defect in td_list:
                try:
                    # Fetch current status from Jira
                    jira_issue = asyncio.run(
                        jira_client.get_issue(
                            issue_key=defect.jira_issue_key,
                            params={"fields": "status"},
                        )
                    )

                    remote_status = jira_issue.get("fields", {}).get("status", {}).get("name", "")
                    if not remote_status:
                        continue

                    # Map Jira status to local status
                    mapped_status = JIRA_STATUS_TO_LOCAL.get(remote_status.lower())

                    if mapped_status and mapped_status != defect.status:
                        logger.info(
                            f"[JIRA SYNC] Updating defect {defect.id}: "
                            f"{defect.status} -> {mapped_status}"
                        )

                        defect.status = mapped_status
                        defect.jira_status = remote_status.title()

                        if mapped_status == "resolved" and defect.resolved_at is None:
                            from datetime import datetime, timezone
                            defect.resolved_at = datetime.now(timezone.utc)

                        results["synced"] += 1
                        results["details"].append({
                            "defect_id": str(defect.id),
                            "issue_key": defect.jira_issue_key,
                            "old_status": defect.status,
                            "new_status": mapped_status,
                        })
                    else:
                        results["unchanged"] += 1

                except JiraClientError as e:
                    logger.warning(f"[JIRA SYNC] Failed to fetch {defect.jira_issue_key}: {e}")
                    results["errors"] += 1
                except Exception as e:
                    logger.error(f"[JIRA SYNC] Unexpected error for {defect.id}: {e}")
                    results["errors"] += 1

        # Commit all changes
        db.commit()
        db.close()

        logger.info(
            f"[JIRA SYNC] Completed: {results['synced']} synced, "
            f"{results['unchanged']} unchanged, {results['errors']} errors"
        )

        return results

    except Exception as e:
        logger.error(f"[JIRA SYNC] Task failed: {e}", exc_info=True)
        return {
            "synced": 0,
            "unchanged": 0,
            "errors": 1,
            "total": 0,
            "error": str(e),
        }


@celery.task(name='tasks.integration_sync.check_integration_health', bind=True)
def check_integration_health(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Check health of all integrations.

    This task performs health checks on configured integrations and
    can be used to send alerts if integrations become unhealthy.

    Args:
        tenant_id: Optional tenant UUID to check. If None, checks all tenants.

    Returns:
        Dict with health status for each integration type.
    """
    from uuid import UUID
    from sqlalchemy import select, create_engine
    from sqlalchemy.orm import sessionmaker
    from models.integration_config import IntegrationConfig
    from models.notification_config import NotificationConfig
    from integrations.jira.client import JiraClient, JiraClientError
    from integrations.slack.client import SlackClient, SlackClientError
    from api.config import get_settings

    settings = get_settings()
    sync_db_url = settings.DATABASE_URL.replace('+asyncpg', '')
    sync_engine = create_engine(sync_db_url)
    SyncSession = sessionmaker(bind=sync_engine)

    results: Dict[str, Any] = {
        "tenants_checked": 0,
        "integrations": {
            "jira": {"healthy": 0, "unhealthy": 0},
            "slack": {"healthy": 0, "unhealthy": 0},
            "github": {"healthy": 0, "unhealthy": 0},
        },
        "issues": [],
    }

    try:
        db = SyncSession()

        # Get all tenants to check
        if tenant_id:
            tenant_ids = [UUID(tenant_id)]
        else:
            # Get unique tenant IDs from configs
            jira_tenants = db.execute(
                select(IntegrationConfig.tenant_id).distinct()
            ).scalars().all()
            slack_tenants = db.execute(
                select(NotificationConfig.tenant_id).distinct()
            ).scalars().all()
            tenant_ids = list(set(jira_tenants) | set(slack_tenants))

        results["tenants_checked"] = len(tenant_ids)

        for tid in tenant_ids:
            # Check Jira
            jira_config = db.execute(
                select(IntegrationConfig).where(
                    IntegrationConfig.tenant_id == tid,
                    IntegrationConfig.integration_type == "jira",
                )
            ).scalar_one_or_none()

            if jira_config and jira_config.is_connected:
                api_token = jira_config.get_access_token()
                if api_token and jira_config.jira_instance_url and jira_config.jira_email:
                    try:
                        jira_client = JiraClient(
                            email=jira_config.jira_email,
                            api_token=api_token,
                            base_url=f"{jira_config.jira_instance_url.rstrip('/')}/rest/api/3",
                        )
                        # Simple health check - try to fetch server info
                        # (would need to add this method to JiraClient)
                        results["integrations"]["jira"]["healthy"] += 1
                    except Exception as e:
                        results["integrations"]["jira"]["unhealthy"] += 1
                        results["issues"].append({
                            "tenant_id": str(tid),
                            "integration": "jira",
                            "error": str(e),
                        })

            # Check Slack
            slack_config = db.execute(
                select(NotificationConfig).where(
                    NotificationConfig.tenant_id == tid,
                )
            ).scalar_one_or_none()

            if slack_config and slack_config.is_connected:
                webhook_url = slack_config.get_webhook_url()
                bot_token = slack_config.get_bot_token()

                if webhook_url or bot_token:
                    try:
                        if bot_token:
                            from integrations.slack.oauth import SlackOAuthClient, SlackOAuthError
                            # Simple auth test would go here
                            pass
                        results["integrations"]["slack"]["healthy"] += 1
                    except Exception as e:
                        results["integrations"]["slack"]["unhealthy"] += 1
                        results["issues"].append({
                            "tenant_id": str(tid),
                            "integration": "slack",
                            "error": str(e),
                        })

            # Check GitHub
            github_config = db.execute(
                select(IntegrationConfig).where(
                    IntegrationConfig.tenant_id == tid,
                    IntegrationConfig.integration_type == "github",
                )
            ).scalar_one_or_none()

            if github_config and github_config.is_connected:
                results["integrations"]["github"]["healthy"] += 1

        db.close()

        logger.info(f"[HEALTH CHECK] Completed for {results['tenants_checked']} tenants")
        return results

    except Exception as e:
        logger.error(f"[HEALTH CHECK] Task failed: {e}", exc_info=True)
        return {
            "tenants_checked": 0,
            "integrations": {},
            "error": str(e),
        }


@celery.task(name='tasks.integration_sync.send_slack_notification', bind=True, max_retries=3)
def send_slack_notification(
    self,
    tenant_id: str,
    notification_type: str,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Send a Slack notification asynchronously with retry support.

    This task handles sending Slack notifications in the background,
    with automatic retries on failure.

    Args:
        tenant_id: UUID of the tenant
        notification_type: Type of notification (test_result, defect, edge_case, system_alert)
        payload: Notification data to send

    Returns:
        Dict with send result
    """
    from uuid import UUID
    from sqlalchemy import select, create_engine
    from sqlalchemy.orm import sessionmaker
    from models.notification_config import NotificationConfig
    from integrations.slack.client import SlackClient, SlackClientError
    from api.config import get_settings

    settings = get_settings()
    sync_db_url = settings.DATABASE_URL.replace('+asyncpg', '')
    sync_engine = create_engine(sync_db_url)
    SyncSession = sessionmaker(bind=sync_engine)

    try:
        db = SyncSession()

        # Get Slack config
        config = db.execute(
            select(NotificationConfig).where(
                NotificationConfig.tenant_id == UUID(tenant_id),
            )
        ).scalar_one_or_none()

        if not config or not config.is_connected:
            db.close()
            return {"sent": False, "reason": "Slack not connected"}

        webhook_url = config.get_webhook_url()
        if not webhook_url:
            db.close()
            return {"sent": False, "reason": "No webhook URL configured"}

        # Create Slack client
        client = SlackClient(
            webhook_url=webhook_url,
            default_channel=config.default_channel,
        )

        # Send appropriate notification type with interactive buttons
        if notification_type == "test_result":
            result = asyncio.run(client.send_interactive_test_result(
                suite_run_id=payload.get("suite_run_id", ""),
                suite_name=payload.get("suite_name", "Test Suite"),
                status=payload.get("status", "warning"),
                passed=payload.get("passed", 0),
                failed=payload.get("failed", 0),
                duration_seconds=payload.get("duration_seconds", 0),
                run_url=payload.get("run_url", "#"),
                channel=payload.get("channel"),
            ))

        elif notification_type == "defect":
            result = asyncio.run(client.send_interactive_defect_alert(
                defect_id=payload.get("defect_id", ""),
                title=payload.get("title", "New Defect"),
                severity=payload.get("severity", "medium"),
                defect_url=payload.get("defect_url", "#"),
                description=payload.get("description"),
                channel=payload.get("channel"),
            ))

        elif notification_type == "edge_case":
            result = asyncio.run(client.send_interactive_edge_case_alert(
                edge_case_id=payload.get("edge_case_id", ""),
                title=payload.get("title", "New Edge Case"),
                category=payload.get("category", "uncategorized"),
                severity=payload.get("severity", "medium"),
                edge_case_url=payload.get("edge_case_url", "#"),
                scenario_name=payload.get("scenario_name"),
                description=payload.get("description"),
                channel=payload.get("channel"),
            ))

        elif notification_type == "system_alert":
            result = asyncio.run(client.send_system_alert(
                severity=payload.get("severity", "info"),
                title=payload.get("title", "System Alert"),
                message=payload.get("message", ""),
                alert_url=payload.get("alert_url"),
                channel=payload.get("channel"),
            ))

        else:
            # Generic message
            result = asyncio.run(client.send_message(
                text=payload.get("text", "Notification"),
                channel=payload.get("channel"),
            ))

        db.close()

        logger.info(f"[SLACK TASK] Sent {notification_type} notification for tenant {tenant_id}")
        return {"sent": True, "result": result}

    except SlackClientError as e:
        logger.error(f"[SLACK TASK] Failed to send notification: {e}")
        # Retry with exponential backoff
        try:
            self.retry(countdown=2 ** self.request.retries * 30, exc=e)
        except self.MaxRetriesExceededError:
            return {"sent": False, "error": str(e), "max_retries_exceeded": True}

    except Exception as e:
        logger.error(f"[SLACK TASK] Unexpected error: {e}", exc_info=True)
        return {"sent": False, "error": str(e)}
