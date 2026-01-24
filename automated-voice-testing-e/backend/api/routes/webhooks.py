"""
Webhook receiver endpoints (TASK-262).
"""

from __future__ import annotations

import json
from typing import Any, Dict, Tuple

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from services import webhook_service

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


def _identify_provider(headers: Dict[str, str]) -> Tuple[str, str]:
    """
    Determine webhook provider and associated event type from headers.

    Args:
        headers: Mapping of incoming request headers.

    Returns:
        Tuple of provider slug and event type string.

    Raises:
        ValueError: When the provider cannot be determined.
    """

    github_event = headers.get("x-github-event")
    if github_event:
        return "github", github_event

    gitlab_event = headers.get("x-gitlab-event")
    if gitlab_event:
        return "gitlab", gitlab_event

    jenkins_event = headers.get("x-jenkins-event")
    if jenkins_event:
        return "jenkins", jenkins_event

    raise ValueError("Unsupported webhook provider")


@router.post(
    "/ci-cd/{webhook_token}",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Receive CI/CD webhook events",
    response_description="Acknowledgement that the webhook was accepted for processing.",
)
async def receive_ci_cd_webhook(
    webhook_token: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, str]:
    """
    Accept webhook payloads from CI/CD providers (GitHub, GitLab, Jenkins).

    Args:
        webhook_token: Unique webhook token (avtwh_*) identifying the tenant
    """
    raw_body = await request.body()
    if not raw_body:
        raw_body = b"{}"

    try:
        payload: Dict[str, Any] = json.loads(raw_body.decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Payload must be a JSON object.")
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON payload: {exc}",
        ) from exc

    # Validate webhook token format
    if not webhook_token.startswith("avtwh_"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook token format",
        )

    try:
        provider, event_type = _identify_provider(request.headers)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    # Load integration config for this specific webhook token
    integration_config, tenant_id = await webhook_service.load_integration_config_by_token(
        db, webhook_token
    )

    if not integration_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook token not found or configuration not active",
        )

    try:
        webhook_service.verify_signature(
            provider, request.headers, raw_body, integration_config
        )
    except webhook_service.SignatureVerificationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    try:
        await webhook_service.dispatch_ci_cd_event(
            provider=provider,
            event_type=event_type,
            payload=payload,
            headers=dict(request.headers.items()),
            integration_config=integration_config,
            tenant_id=tenant_id,
            db=db,
        )
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process webhook",
        ) from exc

    return {"status": "accepted", "provider": provider}
