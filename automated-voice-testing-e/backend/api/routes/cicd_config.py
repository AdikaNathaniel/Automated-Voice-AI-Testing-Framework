"""
CI/CD Configuration routes for managing webhook-to-test-suite mappings.

Provides a user-friendly way to configure:
- Which test suites to run when webhooks are received
- Provider-specific settings (GitHub, GitLab, Jenkins)
- Branch filters and event type filters
- Webhook secrets management
"""

import logging
import secrets
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Body, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.dependencies import get_db, get_current_user_with_db
from api.schemas.responses import SuccessResponse
from api.schemas.auth import UserResponse
from models.audit_trail import log_audit_trail
from models.configuration import Configuration

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cicd-config", tags=["cicd-config"])


# =============================================================================
# Configuration Key Constants
# =============================================================================

CICD_CONFIG_KEY = "integration.cicd"


def _get_effective_tenant_id(user: UserResponse) -> UUID:
    """Get effective tenant_id for a user."""
    return user.tenant_id if user.tenant_id else user.id


# =============================================================================
# Request/Response Models
# =============================================================================

class ProviderBranchFilter(BaseModel):
    """Branch filter configuration."""
    enabled: bool = Field(False, description="Whether branch filtering is enabled")
    branches: List[str] = Field(
        default_factory=list,
        description="List of branch patterns to match (e.g., 'main', 'release/*')"
    )
    exclude_branches: List[str] = Field(
        default_factory=list,
        description="Branches to exclude"
    )


class ProviderEventFilter(BaseModel):
    """Event type filter configuration."""
    push: bool = Field(True, description="Trigger on push events")
    pull_request: bool = Field(False, description="Trigger on pull request events")
    workflow_run: bool = Field(True, description="Trigger on workflow run events")
    deployment: bool = Field(True, description="Trigger on deployment events")


class ProviderConfig(BaseModel):
    """Configuration for a single CI/CD provider."""
    enabled: bool = Field(True, description="Whether this provider is enabled")
    webhook_secret: Optional[str] = Field(
        None,
        description="Webhook secret for signature verification (write-only)"
    )
    webhook_secret_set: bool = Field(
        False,
        description="Whether a webhook secret is configured (read-only)"
    )
    suite_id: Optional[str] = Field(
        None,
        description="Test suite to run when webhook is received"
    )
    suite_name: Optional[str] = Field(
        None,
        description="Name of the selected test suite (read-only)"
    )
    scenario_ids: List[str] = Field(
        default_factory=list,
        description="Specific scenarios to run (if empty, runs all in suite)"
    )
    branch_filter: ProviderBranchFilter = Field(
        default_factory=ProviderBranchFilter,
        description="Branch filtering configuration"
    )
    event_filter: ProviderEventFilter = Field(
        default_factory=ProviderEventFilter,
        description="Event type filtering configuration"
    )
    run_regression_tests: bool = Field(
        False,
        description="Also run regression tests on deployment events"
    )
    regression_suite_ids: List[str] = Field(
        default_factory=list,
        description="Regression suite IDs to run on deployment"
    )


class CICDConfigResponse(BaseModel):
    """Response model for CI/CD configuration."""
    is_configured: bool = Field(False, description="Whether any CI/CD is configured")
    webhook_url: str = Field("", description="Webhook URL to configure in providers")
    default_suite_id: Optional[str] = Field(None, description="Default test suite")
    default_suite_name: Optional[str] = Field(None, description="Default suite name")
    providers: Dict[str, ProviderConfig] = Field(
        default_factory=dict,
        description="Provider-specific configurations"
    )
    last_updated: Optional[str] = Field(None, description="Last update timestamp")


class CICDConfigUpdatePayload(BaseModel):
    """Payload for updating CI/CD configuration."""
    default_suite_id: Optional[str] = Field(None, description="Default test suite ID")
    providers: Dict[str, ProviderConfig] = Field(
        default_factory=dict,
        description="Provider configurations to update"
    )


class WebhookTestResult(BaseModel):
    """Result of webhook configuration test."""
    success: bool
    message: str
    provider: str
    details: Optional[Dict[str, Any]] = None


# =============================================================================
# Helper Functions
# =============================================================================

def _generate_webhook_token() -> str:
    """Generate a unique webhook token with avtwh_ prefix.

    Format: avtwh_ + 32 random hex characters
    Example: avtwh_a7f8e3c9d2b1f4e6a8c7d9e1f3b5a2c4d6e8f1a3b5c7d9e2f4a6b8c1d3e5f7a9
    """
    random_part = secrets.token_hex(32)  # 32 bytes = 64 hex chars
    return f"avtwh_{random_part}"


async def _get_or_create_cicd_config(
    db: AsyncSession,
    tenant_id: UUID,
) -> Configuration:
    """Get or create CI/CD integration configuration for tenant."""
    from sqlalchemy.orm.attributes import flag_modified

    result = await db.execute(
        select(Configuration).where(
            Configuration.tenant_id == tenant_id,
            Configuration.config_key == CICD_CONFIG_KEY,
        )
    )
    config = result.scalar_one_or_none()

    if not config:
        # Generate unique webhook token for this tenant
        webhook_token = _generate_webhook_token()

        config = Configuration(
            tenant_id=tenant_id,
            config_key=CICD_CONFIG_KEY,
            description="Webhook-to-test-suite mappings for CI/CD pipelines",
            is_active=True,
            config_data={
                "webhook_token": webhook_token,
                "default_suite_id": None,
                "providers": {
                    "github": _default_provider_config(),
                    "gitlab": _default_provider_config(),
                    "jenkins": _default_provider_config(),
                },
            },
        )
        db.add(config)
        await db.commit()
        await db.refresh(config)
    else:
        # Ensure existing configs have a webhook token (migration support)
        config_data = config.config_data or {}
        if "webhook_token" not in config_data:
            config_data["webhook_token"] = _generate_webhook_token()
            config.config_data = config_data
            # Mark the JSONB field as modified so SQLAlchemy detects the change
            flag_modified(config, "config_data")
            await db.commit()
            await db.refresh(config)

    return config


def _default_provider_config() -> Dict[str, Any]:
    """Return default provider configuration."""
    return {
        "enabled": False,
        "webhook_secret_hash": None,
        "suite_id": None,
        "scenario_ids": [],
        "branch_filter": {
            "enabled": False,
            "branches": [],
            "exclude_branches": [],
        },
        "event_filter": {
            "push": True,
            "pull_request": False,
            "workflow_run": True,
            "deployment": True,
        },
        "run_regression_tests": False,
        "regression_suite_ids": [],
    }


async def _get_suite_name(db: AsyncSession, suite_id: Optional[str]) -> Optional[str]:
    """Get test suite name by ID."""
    if not suite_id:
        return None

    try:
        from models.test_suite import TestSuite
        result = await db.execute(
            select(TestSuite.name).where(TestSuite.id == UUID(suite_id))
        )
        name = result.scalar_one_or_none()
        return name
    except Exception:
        return None


def _build_provider_response(
    provider_data: Dict[str, Any],
    suite_name: Optional[str] = None,
) -> ProviderConfig:
    """Build ProviderConfig response from stored data."""
    branch_data = provider_data.get("branch_filter", {})
    event_data = provider_data.get("event_filter", {})

    return ProviderConfig(
        enabled=provider_data.get("enabled", False),
        webhook_secret=None,  # Never return the secret
        webhook_secret_set=bool(provider_data.get("webhook_secret_hash")),
        suite_id=provider_data.get("suite_id"),
        suite_name=suite_name,
        scenario_ids=provider_data.get("scenario_ids", []),
        branch_filter=ProviderBranchFilter(
            enabled=branch_data.get("enabled", False),
            branches=branch_data.get("branches", []),
            exclude_branches=branch_data.get("exclude_branches", []),
        ),
        event_filter=ProviderEventFilter(
            push=event_data.get("push", True),
            pull_request=event_data.get("pull_request", False),
            workflow_run=event_data.get("workflow_run", True),
            deployment=event_data.get("deployment", True),
        ),
        run_regression_tests=provider_data.get("run_regression_tests", False),
        regression_suite_ids=provider_data.get("regression_suite_ids", []),
    )


# =============================================================================
# Endpoints
# =============================================================================

@router.get("")
async def get_cicd_config(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> SuccessResponse:
    """Get CI/CD webhook configuration for the current tenant."""
    tenant_id = _get_effective_tenant_id(current_user)
    logger.info(f"[CICD-CONFIG] Getting config for tenant {tenant_id}")

    config = await _get_or_create_cicd_config(db, tenant_id)
    config_data = config.config_data or {}

    # Build provider responses with suite names
    providers_data = config_data.get("providers", {})
    providers_response = {}

    for provider_name in ["github", "gitlab", "jenkins"]:
        provider_data = providers_data.get(provider_name, _default_provider_config())
        suite_name = await _get_suite_name(db, provider_data.get("suite_id"))
        providers_response[provider_name] = _build_provider_response(
            provider_data, suite_name
        )

    # Get default suite name
    default_suite_id = config_data.get("default_suite_id")
    default_suite_name = await _get_suite_name(db, default_suite_id)

    # Determine if configured
    is_configured = any(
        p.enabled and p.suite_id for p in providers_response.values()
    )

    # Build webhook URL with unique token
    from api.config import get_settings
    settings = get_settings()
    base_url = getattr(settings, "BASE_URL", "http://localhost:8000")
    webhook_token = config_data.get("webhook_token", "")
    webhook_url = f"{base_url}/api/v1/webhooks/ci-cd/{webhook_token}"

    return SuccessResponse(
        data={
            "is_configured": is_configured,
            "webhook_url": webhook_url,
            "webhook_token": webhook_token,  # Also return token separately for reference
            "default_suite_id": default_suite_id,
            "default_suite_name": default_suite_name,
            "providers": {
                k: v.model_dump() for k, v in providers_response.items()
            },
            "last_updated": config.updated_at.isoformat() if config.updated_at else None,
        }
    )


@router.put("")
async def update_cicd_config(
    payload: CICDConfigUpdatePayload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> SuccessResponse:
    """Update CI/CD webhook configuration."""
    tenant_id = _get_effective_tenant_id(current_user)
    logger.info(f"[CICD-CONFIG] Updating config for tenant {tenant_id}")

    config = await _get_or_create_cicd_config(db, tenant_id)
    config_data = config.config_data or {}

    # Capture old values for audit logging (NEVER log webhook secrets)
    old_providers = config_data.get("providers", {})
    old_values = {
        "default_suite_id": config_data.get("default_suite_id"),
        "providers_enabled": {
            name: prov.get("enabled", False)
            for name, prov in old_providers.items()
        },
    }

    # Track changes for summary
    changes = []
    webhook_secrets_changed = []

    # Update default suite
    if payload.default_suite_id is not None:
        if config_data.get("default_suite_id") != payload.default_suite_id:
            changes.append("default suite changed")
        config_data["default_suite_id"] = payload.default_suite_id

    # Update providers
    existing_providers = config_data.get("providers", {})

    for provider_name, provider_config in payload.providers.items():
        if provider_name not in ["github", "gitlab", "jenkins"]:
            continue

        existing = existing_providers.get(provider_name, _default_provider_config())

        # Track if enabled state changed
        if existing.get("enabled") != provider_config.enabled:
            changes.append(f"{provider_name} {'enabled' if provider_config.enabled else 'disabled'}")

        # Update fields
        existing["enabled"] = provider_config.enabled
        existing["suite_id"] = provider_config.suite_id
        existing["scenario_ids"] = provider_config.scenario_ids
        existing["run_regression_tests"] = provider_config.run_regression_tests
        existing["regression_suite_ids"] = provider_config.regression_suite_ids

        # Update webhook secret only if provided (non-None and non-empty)
        if provider_config.webhook_secret:
            # Store hashed for security
            import hashlib
            existing["webhook_secret_hash"] = hashlib.sha256(
                provider_config.webhook_secret.encode()
            ).hexdigest()
            # Also store the actual secret for webhook verification
            existing["secret"] = provider_config.webhook_secret
            webhook_secrets_changed.append(provider_name)

        # Update filters
        existing["branch_filter"] = provider_config.branch_filter.model_dump()
        existing["event_filter"] = provider_config.event_filter.model_dump()

        existing_providers[provider_name] = existing

    config_data["providers"] = existing_providers
    config.config_data = config_data
    config.updated_at = datetime.now(timezone.utc)

    # Mark the JSONB field as modified so SQLAlchemy detects the change
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(config, "config_data")

    await db.commit()
    await db.refresh(config)

    logger.info(f"[CICD-CONFIG] Config updated for tenant {tenant_id}")

    # Capture new values for audit logging (NEVER log webhook secrets)
    new_values = {
        "default_suite_id": config_data.get("default_suite_id"),
        "providers_enabled": {
            name: prov.get("enabled", False)
            for name, prov in existing_providers.items()
        },
    }

    # Add indicator if webhook secrets changed
    if webhook_secrets_changed:
        new_values["webhook_secrets_updated"] = webhook_secrets_changed
        changes.append(f"webhook secrets updated for: {', '.join(webhook_secrets_changed)}")

    # Build summary
    summary = f"CI/CD configuration updated by {current_user.email}"
    if changes:
        summary += " - " + ", ".join(changes)

    # Log audit trail
    await log_audit_trail(
        db=db,
        action_type="update",
        resource_type="cicd_config",
        resource_id=str(config.id),
        tenant_id=tenant_id,
        user_id=current_user.id,
        old_values=old_values,
        new_values=new_values,
        changes_summary=summary,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=True,
    )

    # Return updated config
    return await get_cicd_config(db, current_user)


@router.post("/test-webhook/{provider}")
async def test_webhook_config(
    provider: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> SuccessResponse:
    """Test webhook configuration for a provider."""
    tenant_id = _get_effective_tenant_id(current_user)
    logger.info(f"[CICD-CONFIG] Testing {provider} webhook for tenant {tenant_id}")

    if provider not in ["github", "gitlab", "jenkins"]:
        raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}")

    config = await _get_or_create_cicd_config(db, tenant_id)
    config_data = config.config_data or {}
    provider_data = config_data.get("providers", {}).get(provider, {})

    # Check configuration
    issues = []
    if not provider_data.get("enabled"):
        issues.append(f"{provider.title()} integration is not enabled")
    if not provider_data.get("suite_id"):
        issues.append("No test suite selected")
    if not provider_data.get("secret"):
        issues.append("No webhook secret configured")

    if issues:
        return SuccessResponse(
            data={
                "success": False,
                "message": "Configuration incomplete",
                "provider": provider,
                "details": {"issues": issues},
            }
        )

    return SuccessResponse(
        data={
            "success": True,
            "message": f"{provider.title()} webhook is configured correctly",
            "provider": provider,
            "details": {
                "suite_id": provider_data.get("suite_id"),
                "webhook_secret_set": True,
                "branch_filter_enabled": provider_data.get("branch_filter", {}).get("enabled", False),
            },
        }
    )


@router.get("/webhook-instructions/{provider}")
async def get_webhook_instructions(
    provider: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> SuccessResponse:
    """Get setup instructions for a specific provider's webhook."""
    if provider not in ["github", "gitlab", "jenkins"]:
        raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}")

    # Get tenant's webhook URL with their unique token
    tenant_id = _get_effective_tenant_id(current_user)
    config = await _get_or_create_cicd_config(db, tenant_id)
    config_data = config.config_data or {}
    webhook_token = config_data.get("webhook_token", "")

    from api.config import get_settings
    settings = get_settings()
    base_url = getattr(settings, "BASE_URL", "https://your-domain.com")
    webhook_url = f"{base_url}/api/v1/webhooks/ci-cd/{webhook_token}"

    instructions = {
        "github": {
            "title": "GitHub Webhook Setup",
            "steps": [
                "Go to your GitHub repository settings",
                "Navigate to 'Webhooks' in the left sidebar",
                "Click 'Add webhook'",
                f"Set Payload URL to: {webhook_url}",
                "Set Content type to: application/json",
                "Enter your webhook secret (same as configured above)",
                "Select events: 'Push', 'Workflow runs', 'Deployments'",
                "Click 'Add webhook'",
            ],
            "webhook_url": webhook_url,
            "content_type": "application/json",
            "events": ["push", "workflow_run", "deployment"],
            "docs_url": "https://docs.github.com/en/webhooks",
        },
        "gitlab": {
            "title": "GitLab Webhook Setup",
            "steps": [
                "Go to your GitLab project settings",
                "Navigate to 'Webhooks' under 'Settings'",
                f"Set URL to: {webhook_url}",
                "Enter your secret token (same as configured above)",
                "Select triggers: 'Push events', 'Pipeline events', 'Deployment events'",
                "Click 'Add webhook'",
            ],
            "webhook_url": webhook_url,
            "content_type": "application/json",
            "events": ["push", "pipeline", "deployment"],
            "docs_url": "https://docs.gitlab.com/ee/user/project/integrations/webhooks.html",
        },
        "jenkins": {
            "title": "Jenkins Webhook Setup",
            "steps": [
                "Install the 'Generic Webhook Trigger' plugin",
                "Go to your Jenkins job configuration",
                "Under 'Build Triggers', enable 'Generic Webhook Trigger'",
                f"Set the webhook URL: {webhook_url}",
                "Configure the secret token in Post content parameters",
                "Add the X-Jenkins-Signature header with HMAC signature",
                "Save the job configuration",
            ],
            "webhook_url": webhook_url,
            "content_type": "application/json",
            "events": ["build_started", "build_completed"],
            "docs_url": "https://plugins.jenkins.io/generic-webhook-trigger/",
        },
    }

    return SuccessResponse(data=instructions[provider])
