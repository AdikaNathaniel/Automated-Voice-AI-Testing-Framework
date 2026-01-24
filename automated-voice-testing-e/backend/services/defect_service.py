"""
Service layer for managing defects.

Provides CRUD operations, assignment workflows, and resolution helpers
backed by the Defect ORM model.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from models.defect import Defect
from services.notification_service import (
    get_notification_service,
    NotificationServiceError,
    ALERT_SEVERITIES,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:  # pragma: no cover - import guarded for typing only
    from integrations.jira.client import JiraClient

SEVERITY_PRIORITY_MAP = {
    "critical": "Highest",
    "high": "High",
    "medium": "Medium",
    "low": "Low",
}

STATUS_TO_JIRA_STATUS = {
    "open": "To Do",
    "in_progress": "In Progress",
    "resolved": "Done",
}

JIRA_STATUS_TO_LOCAL = {value.lower(): key for key, value in STATUS_TO_JIRA_STATUS.items()}


class DefectService:
    """
    Service class for defect management operations.

    Provides CRUD operations, assignment workflows, and resolution helpers.

    Example:
        >>> service = DefectService()
        >>> defect = await service.create_defect(db, data)
    """

    def __init__(self):
        """Initialize the defect service."""
        pass

    async def create_defect(self, db: AsyncSession, data: Dict[str, Any], **kwargs) -> Defect:
        """Persist a new defect record."""
        return await create_defect(db, data, **kwargs)

    async def get_defect(self, db: AsyncSession, defect_id: UUID) -> Defect:
        """Retrieve a defect by ID."""
        return await get_defect(db, defect_id)

    async def list_defects(self, db: AsyncSession, filters: Dict[str, Any], pagination: Dict[str, Any], tenant_id: Optional[UUID] = None) -> Tuple[List[Defect], int]:
        """List defects with filters and pagination."""
        return await list_defects(db, filters, pagination, tenant_id=tenant_id)

    async def update_defect(self, db: AsyncSession, defect_id: UUID, data: Dict[str, Any]) -> Defect:
        """Update defect fields."""
        return await update_defect(db, defect_id, data)

    async def assign_defect(self, db: AsyncSession, defect_id: UUID, assignee_id: UUID) -> Defect:
        """Assign defect to user."""
        return await assign_defect(db, defect_id, assignee_id)

    async def resolve_defect(self, db: AsyncSession, defect_id: UUID, resolution: str, **kwargs) -> Defect:
        """Resolve a defect."""
        return await resolve_defect(db, defect_id, resolution, **kwargs)


def _ensure_timezone(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("datetime values must be timezone aware")
    return value.astimezone(timezone.utc)


async def create_defect(
    db: AsyncSession,
    data: Dict[str, Any],
    *,
    jira_client: Optional["JiraClient"] = None,
    jira_project_key: Optional[str] = None,
    jira_issue_type: str = "Bug",
    jira_browse_base_url: Optional[str] = None,
) -> Defect:
    """Persist a new defect record."""
    try:
        payload = data.copy()
        if "detected_at" in payload and payload["detected_at"] is not None:
            payload["detected_at"] = _ensure_timezone(payload["detected_at"])

        defect = Defect(**payload)
        db.add(defect)
        await db.commit()
        await db.refresh(defect)

        if jira_client and jira_project_key:
            issue_payload = _build_jira_issue_payload(defect, issue_type=jira_issue_type)
            issue_key = await jira_client.create_issue(project=jira_project_key, data=issue_payload)
            defect.jira_issue_key = issue_key
            defect.jira_issue_url = _build_jira_issue_url(jira_browse_base_url, issue_key)
            defect.jira_status = STATUS_TO_JIRA_STATUS.get(defect.status)
            await db.commit()
            await db.refresh(defect)

        logger.debug(f"Created defect: {defect.id}")

        # Send notification for critical/high severity defects
        if (defect.severity or "").lower() in ALERT_SEVERITIES:
            try:
                notification_service = get_notification_service()
                defect_url = f"/defects/{defect.id}"  # Relative URL for frontend
                await notification_service.notify_critical_defect(
                    defect_id=str(defect.id),
                    title=defect.title or "Untitled Defect",
                    severity=defect.severity or "high",
                    defect_url=defect_url,
                    description=defect.description,
                )
                logger.info(f"Sent notification for critical defect {defect.id}")
            except NotificationServiceError as e:
                # Log but don't fail - notifications shouldn't break core functionality
                logger.warning(f"Failed to send defect notification: {e}")
            except Exception as e:
                logger.warning(f"Unexpected error sending defect notification: {e}")

        return defect

    except Exception as e:
        logger.error(f"Error creating defect: {e}")
        raise


async def get_defect(db: AsyncSession, defect_id: UUID) -> Defect:
    """Fetch a defect by its identifier or raise if not found."""
    try:
        result = await db.execute(select(Defect).where(Defect.id == defect_id))
        defect = result.scalar_one_or_none()
        if defect is None:
            raise NoResultFound(f"Defect {defect_id} not found")
        logger.debug(f"Found defect: {defect_id}")
        return defect

    except NoResultFound:
        raise
    except Exception as e:
        logger.error(f"Error getting defect {defect_id}: {e}")
        raise


async def list_defects(
    db: AsyncSession,
    filters: Dict[str, Any],
    pagination: Dict[str, int],
    tenant_id: Optional[UUID] = None,
) -> Tuple[List[Defect], int]:
    """List defects matching provided filters with pagination."""
    try:
        conditions = []

        # Filter by tenant_id if provided
        if tenant_id:
            conditions.append(Defect.tenant_id == tenant_id)

        if status := filters.get("status"):
            conditions.append(Defect.status == status)
        if severity := filters.get("severity"):
            conditions.append(Defect.severity == severity)
        if category := filters.get("category"):
            conditions.append(Defect.category == category)
        if assigned_to := filters.get("assigned_to"):
            conditions.append(Defect.assigned_to == assigned_to)
        if script_id := filters.get("script_id"):
            conditions.append(Defect.script_id == script_id)
        if execution_id := filters.get("execution_id"):
            conditions.append(Defect.execution_id == execution_id)

        query = select(Defect)
        if conditions:
            query = query.where(*conditions)

        count_query = select(func.count()).select_from(Defect)
        if conditions:
            count_query = count_query.where(*conditions)

        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        skip = pagination.get("skip", 0)
        limit = pagination.get("limit", 50)
        result = await db.execute(query.offset(skip).limit(limit))
        defects = result.scalars().all()

        logger.debug(f"Listed {len(defects)} defects (total: {total})")
        return defects, total

    except Exception as e:
        logger.error(f"Error listing defects: {e}")
        raise


async def update_defect(
    db: AsyncSession,
    defect_id: UUID,
    data: Dict[str, Any],
    *,
    jira_client: Optional["JiraClient"] = None,
) -> Defect:
    """Update mutable fields on a defect."""
    try:
        if "detected_at" in data and data["detected_at"] is not None:
            data["detected_at"] = _ensure_timezone(data["detected_at"])

        await db.execute(
            update(Defect)
                .where(Defect.id == defect_id)
                .values(**data)
        )
        await db.commit()
        updated = await get_defect(db, defect_id)

        if jira_client and updated.jira_issue_key and "status" in data:
            jira_status = STATUS_TO_JIRA_STATUS.get(updated.status, updated.status.title())
            await jira_client.update_issue(
                issue_key=updated.jira_issue_key,
                data={"fields": {"status": {"name": jira_status}}},
            )
            await db.execute(
                update(Defect)
                    .where(Defect.id == defect_id)
                    .values(jira_status=jira_status)
            )
            await db.commit()
            updated = await get_defect(db, defect_id)

        logger.debug(f"Updated defect: {defect_id}")
        return updated

    except NoResultFound:
        raise
    except Exception as e:
        logger.error(f"Error updating defect {defect_id}: {e}")
        raise


async def assign_defect(
    db: AsyncSession,
    defect_id: UUID,
    user_id: UUID,
) -> Defect:
    """Assign a defect to a user and mark it in progress."""
    values: Dict[str, Any] = {"assigned_to": user_id}
    defect = await get_defect(db, defect_id)
    if defect.status == "open":
        values["status"] = "in_progress"

    await db.execute(
        update(Defect)
            .where(Defect.id == defect_id)
            .values(**values)
    )
    await db.commit()
    return await get_defect(db, defect_id)


async def resolve_defect(
    db: AsyncSession,
    defect_id: UUID,
    resolution: str,
    *,
    jira_client: Optional["JiraClient"] = None,
) -> Defect:
    """Resolve a defect, append resolution details, and mark resolved timestamp."""
    now = datetime.now(timezone.utc)
    defect = await get_defect(db, defect_id)

    description = defect.description or ""
    if description:
        description = f"{description}\n\nResolution: {resolution}"
    else:
        description = resolution

    await db.execute(
        update(Defect)
            .where(Defect.id == defect_id)
            .values(
                status="resolved",
                resolved_at=now,
                description=description,
            )
    )
    await db.commit()
    resolved = await get_defect(db, defect_id)

    if jira_client and resolved.jira_issue_key:
        jira_status = STATUS_TO_JIRA_STATUS.get("resolved", "Done")
        await jira_client.update_issue(
            issue_key=resolved.jira_issue_key,
            data={"fields": {"status": {"name": jira_status}}},
        )
        await db.execute(
            update(Defect)
                .where(Defect.id == defect_id)
                .values(jira_status=jira_status)
        )
        await db.commit()
        resolved = await get_defect(db, defect_id)

    return resolved


async def sync_defect_status_from_jira(
    db: AsyncSession,
    defect_id: UUID,
    *,
    jira_client: "JiraClient",
) -> Defect:
    """
    Refresh local defect status from Jira and reconcile differences.
    """
    defect = await get_defect(db, defect_id)
    if not defect.jira_issue_key:
        return defect

    issue = await jira_client.get_issue(issue_key=defect.jira_issue_key, params={"fields": "status"})
    remote_status = (
        issue.get("fields", {})
        .get("status", {})
        .get("name")
    )
    if not remote_status:
        return defect

    updates: Dict[str, Any] = {}
    if remote_status != defect.jira_status:
        updates["jira_status"] = remote_status

    mapped_status = JIRA_STATUS_TO_LOCAL.get(remote_status.lower())
    if mapped_status and mapped_status != defect.status:
        updates["status"] = mapped_status
        if mapped_status == "resolved" and defect.resolved_at is None:
            updates["resolved_at"] = datetime.now(timezone.utc)

    if not updates:
        return defect

    await db.execute(
        update(Defect)
            .where(Defect.id == defect_id)
            .values(**updates)
    )
    await db.commit()
    return await get_defect(db, defect_id)


def _build_jira_issue_payload(defect: Defect, *, issue_type: str) -> Dict[str, Any]:
    description_parts = []
    if defect.description:
        description_parts.append(defect.description.strip())
    description_parts.append("")
    description_parts.append(f"*Severity*: {defect.severity}")
    if defect.detected_at:
        description_parts.append(f"*Detected at*: {defect.detected_at.isoformat()}")
    if defect.language_code:
        description_parts.append(f"*Language*: {defect.language_code}")
    description = "\n".join(description_parts).strip()

    priority_name = SEVERITY_PRIORITY_MAP.get((defect.severity or "").lower(), "Medium")

    payload: Dict[str, Any] = {
        "summary": defect.title,
        "description": description or "Automatically created from validation defect.",
        "issuetype": {"name": issue_type},
        "priority": {"name": priority_name},
    }

    labels: List[str] = []
    if defect.category:
        labels.append(defect.category.replace(" ", "-").lower())
    if defect.language_code:
        labels.append(defect.language_code.lower())
    if labels:
        payload["labels"] = labels

    return payload


def _build_jira_issue_url(base_url: Optional[str], issue_key: str) -> Optional[str]:
    if not base_url:
        return None
    base = base_url.rstrip("/")
    if base.lower().endswith("/browse"):
        return f"{base}/{issue_key}"
    return f"{base}/browse/{issue_key}"
