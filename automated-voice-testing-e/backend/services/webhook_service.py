"""
Webhook service utilities (TASK-262/TASK-263).

Includes helper functions for verifying webhook signatures and dispatching
events for downstream processing. Event processing logic will be implemented in
subsequent tasks.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
from typing import Any, Dict, Mapping, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from services import orchestration_service
from services.configuration_service import ConfigurationService
from services.regression_suite_executor import RegressionSuiteExecutor
from api.config import get_settings


class SignatureVerificationError(Exception):
    """Raised when a webhook signature or token fails verification."""


def _get_lower_headers(headers: Mapping[str, str]) -> Dict[str, str]:
    """Normalise header keys to lowercase for case-insensitive lookups."""
    return {key.lower(): value for key, value in headers.items()}


def _provider_config(
    provider: str, integration_config: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    if not integration_config:
        return {}
    providers = integration_config.get("providers")
    if not isinstance(providers, Mapping):
        return {}
    entry = providers.get(provider)
    if isinstance(entry, Mapping):
        return dict(entry)
    return {}


def verify_signature(
    provider: str,
    headers: Mapping[str, str],
    body: bytes,
    integration_config: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Validate webhook signatures/tokens for supported providers.

    Args:
        provider: Normalised provider identifier (github, gitlab, jenkins).
        headers: Incoming request headers.
        body: Raw request body bytes.

    Raises:
        SignatureVerificationError: If verification fails or is misconfigured.
    """

    normalised_headers = _get_lower_headers(headers)
    config = get_settings()
    provider_config = _provider_config(provider, integration_config)

    if provider == "github":
        secret = provider_config.get("secret") or config.GITHUB_WEBHOOK_SECRET
        previous_secret = (
            provider_config.get("previous_secret")
            or getattr(config, "GITHUB_WEBHOOK_SECRET_PREVIOUS", None)
        )
        signature_header = normalised_headers.get("x-hub-signature-256")

        if not secret:
            raise SignatureVerificationError("GitHub webhook secret not configured.")
        if not signature_header:
            raise SignatureVerificationError("Missing GitHub signature header.")
        if not signature_header.startswith("sha256="):
            raise SignatureVerificationError("Invalid GitHub signature format.")

        provided_signature = signature_header.split("=", 1)[1]

        # Try current secret
        expected_signature = hmac.new(
            secret.encode("utf-8"),
            body,
            hashlib.sha256,
        ).hexdigest()

        if hmac.compare_digest(provided_signature, expected_signature):
            return  # Valid with current secret

        # Try previous secret for rotation support
        if previous_secret:
            expected_previous = hmac.new(
                previous_secret.encode("utf-8"),
                body,
                hashlib.sha256,
            ).hexdigest()
            if hmac.compare_digest(provided_signature, expected_previous):
                return  # Valid with previous secret

        raise SignatureVerificationError("Invalid GitHub webhook signature.")

    elif provider == "gitlab":
        secret = provider_config.get("secret") or config.GITLAB_WEBHOOK_SECRET
        previous_secret = (
            provider_config.get("previous_secret")
            or getattr(config, "GITLAB_WEBHOOK_SECRET_PREVIOUS", None)
        )
        token_header = normalised_headers.get("x-gitlab-token")

        if not secret:
            raise SignatureVerificationError("GitLab webhook token not configured.")
        if not token_header:
            raise SignatureVerificationError("Missing GitLab token header.")

        # Try current secret
        if hmac.compare_digest(token_header, secret):
            return  # Valid with current secret

        # Try previous secret for rotation support
        if previous_secret and hmac.compare_digest(token_header, previous_secret):
            return  # Valid with previous secret

        raise SignatureVerificationError("Invalid GitLab webhook token.")

    elif provider == "jenkins":
        secret = provider_config.get("secret") or config.JENKINS_WEBHOOK_SECRET
        previous_secret = (
            provider_config.get("previous_secret")
            or getattr(config, "JENKINS_WEBHOOK_SECRET_PREVIOUS", None)
        )
        signature_header = normalised_headers.get("x-jenkins-signature")

        if not secret:
            raise SignatureVerificationError("Jenkins webhook secret not configured.")
        if not signature_header:
            raise SignatureVerificationError("Missing Jenkins signature header.")

        # Try current secret
        expected_signature = hmac.new(
            secret.encode("utf-8"),
            body,
            hashlib.sha256,
        ).hexdigest()

        if hmac.compare_digest(signature_header, expected_signature):
            return  # Valid with current secret

        # Try previous secret for rotation support
        if previous_secret:
            expected_previous = hmac.new(
                previous_secret.encode("utf-8"),
                body,
                hashlib.sha256,
            ).hexdigest()
            if hmac.compare_digest(signature_header, expected_previous):
                return  # Valid with previous secret

        raise SignatureVerificationError("Invalid Jenkins webhook signature.")

    else:
        raise SignatureVerificationError(f"Signature verification unsupported for provider {provider!r}.")


logger = logging.getLogger(__name__)


def _normalise_branch(ref: Optional[str]) -> Optional[str]:
    if not ref:
        return None
    if ref.startswith("refs/heads/"):
        return ref.split("/", 2)[-1]
    return ref


def _extract_github_metadata(payload: Dict[str, Any]) -> Dict[str, Any]:
    repository = payload.get("repository") or {}
    head_commit = payload.get("head_commit") or {}
    branch = _normalise_branch(payload.get("ref"))

    return {
        "repository": repository.get("name"),
        "branch": branch,
        "commit_sha": payload.get("after") or head_commit.get("id"),
        "author": (head_commit.get("author") or {}).get("name"),
        "author_email": (head_commit.get("author") or {}).get("email"),
        "source_url": repository.get("url") or repository.get("html_url"),
    }


def _extract_gitlab_metadata(payload: Dict[str, Any]) -> Dict[str, Any]:
    project = payload.get("project") or {}
    branch = _normalise_branch(payload.get("ref"))

    return {
        "repository": project.get("name"),
        "branch": branch,
        "commit_sha": payload.get("checkout_sha"),
        "author": payload.get("user_name") or payload.get("user_username"),
        "author_email": payload.get("user_email"),
        "source_url": project.get("web_url"),
    }


def _extract_jenkins_metadata(payload: Dict[str, Any]) -> Dict[str, Any]:
    build = payload.get("build") or {}
    parameters = build.get("parameters") or {}
    scm = build.get("scm") or {}

    branch = parameters.get("GIT_BRANCH") or scm.get("branch")
    commit = parameters.get("GIT_COMMIT") or scm.get("commit")

    return {
        "repository": payload.get("name"),
        "branch": branch,
        "commit_sha": commit,
        "author": build.get("builtBy"),
        "author_email": None,
        "source_url": build.get("full_url"),
    }


def _build_metadata(provider: str, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if provider == "github":
        extracted = _extract_github_metadata(payload)
    elif provider == "gitlab":
        extracted = _extract_gitlab_metadata(payload)
    elif provider == "jenkins":
        extracted = _extract_jenkins_metadata(payload)
    else:
        extracted = {}

    metadata = {
        "provider": provider,
        "event_type": event_type,
        "repository": extracted.get("repository"),
        "branch": extracted.get("branch"),
        "commit_sha": extracted.get("commit_sha"),
        "author": extracted.get("author"),
        "author_email": extracted.get("author_email"),
        "source_url": extracted.get("source_url"),
        "raw_payload": payload,
    }

    # Ensure branch/commit fields fall back to safe defaults
    metadata["branch"] = metadata["branch"] or _normalise_branch(payload.get("branch"))
    metadata["commit_sha"] = metadata["commit_sha"] or payload.get("after") or payload.get("sha")

    return metadata


def _extract_regression_suite_ids(
    provider_cfg: Mapping[str, Any],
    integration_config: Optional[Dict[str, Any]],
) -> list[UUID]:
    """
    Collect regression suite identifiers from provider or integration config.

    Returns:
        List of UUID objects representing regression test suite IDs.
        Invalid UUIDs are logged and skipped.
    """
    raw = provider_cfg.get("regression_suite_ids")
    if raw is None and integration_config:
        raw = integration_config.get("regression_suite_ids")

    if raw is None:
        return []

    if isinstance(raw, (list, tuple, set)):
        items = raw
    else:
        items = str(raw).split(",")

    suite_ids: list[UUID] = []
    for item in items:
        if item is None:
            continue
        text = str(item).strip()
        if not text:
            continue

        # Convert to UUID with validation
        try:
            suite_id = UUID(text)
            suite_ids.append(suite_id)
        except (ValueError, AttributeError) as exc:
            logger.warning(
                f"Invalid regression_suite_id '{text}': {exc}. Skipping."
            )
            continue

    return suite_ids


def _is_deployment_event(event_type: str) -> bool:
    """
    Return True when the incoming event type represents a deployment.

    Recognizes deployment events from GitHub, GitLab, and Jenkins.

    Args:
        event_type: Event type from webhook header (e.g., "deployment", "Deployment Hook")

    Returns:
        True if this is a deployment event, False otherwise
    """
    if not event_type:
        return False

    event = event_type.lower().strip()

    # Specific deployment event types from different providers
    deployment_events = {
        'deployment',           # GitHub: deployment event
        'deployment_status',    # GitHub: deployment status update
        'deployment hook',      # GitLab: deployment webhook
        'deploy',              # Generic deployment event
    }

    # Check exact matches first
    if event in deployment_events:
        return True

    # Check if it starts with "deployment" (covers "deployment_created", etc.)
    # But exclude events like "pre_deployment" or "undeployment"
    if event.startswith('deployment'):
        return True

    return False


def _normalise_trigger(event_type: str) -> str:
    """Collate event type into a trigger label for regression automation."""
    event = (event_type or "").lower()
    if not event:
        return "deployment"
    return "deployment" if "deploy" in event else event


def _matches_branch_pattern(branch: Optional[str], pattern: str) -> bool:
    """
    Check if a branch name matches a filter pattern.

    Supports:
    - Exact match: "main" matches "main"
    - Wildcards: "release/*" matches "release/v1.0"
    - Multiple segments: "feature/*/backend" matches "feature/auth/backend"

    Args:
        branch: Branch name to check (e.g., "main", "feature/auth")
        pattern: Pattern to match against (e.g., "main", "feature/*")

    Returns:
        True if branch matches pattern, False otherwise
    """
    import fnmatch

    if not branch or not pattern:
        return False

    # Normalize: remove leading/trailing slashes and refs/heads/ prefix
    branch = branch.strip('/').replace('refs/heads/', '')
    pattern = pattern.strip('/')

    # fnmatch supports * and ? wildcards
    return fnmatch.fnmatch(branch, pattern)


def _should_process_branch(branch: Optional[str], branch_filter: Dict[str, Any]) -> bool:
    """
    Check if a branch should trigger tests based on branch filters.

    Args:
        branch: Branch name from webhook (e.g., "main", "feature/auth")
        branch_filter: Branch filter configuration with 'enabled', 'branches', 'exclude_branches'

    Returns:
        True if tests should run for this branch, False if filtered out
    """
    # If branch filtering is disabled, allow all branches
    if not branch_filter.get("enabled"):
        return True

    # No branch info means we can't filter - allow by default
    if not branch:
        logger.warning("No branch information in webhook, cannot apply branch filter")
        return True

    # Check exclude patterns first (takes precedence)
    exclude_patterns = branch_filter.get("exclude_branches") or []
    for pattern in exclude_patterns:
        if _matches_branch_pattern(branch, pattern):
            logger.info(f"Branch '{branch}' excluded by pattern '{pattern}'")
            return False

    # Check include patterns
    include_patterns = branch_filter.get("branches") or []

    # If no include patterns specified, allow all (that weren't excluded)
    if not include_patterns:
        return True

    # Check if branch matches any include pattern
    for pattern in include_patterns:
        if _matches_branch_pattern(branch, pattern):
            logger.info(f"Branch '{branch}' matched include pattern '{pattern}'")
            return True

    # Branch didn't match any include pattern
    logger.info(f"Branch '{branch}' did not match any include patterns: {include_patterns}")
    return False


def _should_process_event(event_type: Optional[str], event_filter: Dict[str, Any]) -> bool:
    """
    Check if an event type should trigger tests based on event filters.

    Maps provider-specific event types to filter keys:
    - push events → 'push' filter
    - pull_request/merge_request events → 'pull_request' filter
    - workflow/pipeline events → 'workflow_run' filter
    - deployment events → 'deployment' filter

    Args:
        event_type: Event type from webhook header (e.g., "push", "pull_request")
        event_filter: Event filter configuration with boolean flags

    Returns:
        True if tests should run for this event type, False if filtered out
    """
    # If no event type, allow by default (defensive)
    if not event_type:
        logger.warning("No event type in webhook, cannot apply event filter")
        return True

    event_lower = event_type.lower()

    # Map event types to filter keys
    # GitHub: push, pull_request, workflow_run, deployment
    # GitLab: Push Hook, Merge Request Hook, Pipeline Hook, Deployment Hook
    # Jenkins: varies by plugin

    if "push" in event_lower:
        return event_filter.get("push", True)

    elif "pull" in event_lower or "merge" in event_lower:
        return event_filter.get("pull_request", False)

    elif "workflow" in event_lower or "pipeline" in event_lower:
        return event_filter.get("workflow_run", True)

    elif "deploy" in event_lower:
        return event_filter.get("deployment", True)

    # Unknown event type - allow by default to avoid blocking legitimate events
    logger.warning(f"Unknown event type '{event_type}', allowing by default")
    return True


def _should_process_webhook(
    provider_config: Dict[str, Any],
    branch: Optional[str],
    event_type: Optional[str]
) -> tuple[bool, str]:
    """
    Determine if a webhook should trigger test execution based on all filters.

    Args:
        provider_config: Provider-specific configuration including filters
        branch: Branch name from webhook
        event_type: Event type from webhook

    Returns:
        Tuple of (should_process: bool, reason: str)
        - should_process: True if tests should run, False if filtered out
        - reason: Human-readable explanation of the decision
    """
    # Check if provider is enabled
    if not provider_config.get("enabled", True):
        return False, "Provider is disabled in configuration"

    # Check branch filter
    branch_filter = provider_config.get("branch_filter", {})
    if not _should_process_branch(branch, branch_filter):
        return False, f"Branch '{branch}' filtered out by branch filter"

    # Check event filter
    event_filter = provider_config.get("event_filter", {})
    if not _should_process_event(event_type, event_filter):
        return False, f"Event type '{event_type}' filtered out by event filter"

    return True, f"Passed all filters (branch='{branch}', event='{event_type}')"


async def dispatch_ci_cd_event(
    *,
    provider: str,
    event_type: str,
    payload: Dict[str, Any],
    headers: Dict[str, str] | None = None,
    integration_config: Optional[Dict[str, Any]] = None,
    tenant_id: Optional[UUID] = None,
    db: Optional[AsyncSession] = None,
) -> None:
    """
    Dispatch a CI/CD webhook event for asynchronous processing.

    Args:
        provider: Normalised provider name (github, gitlab, jenkins)
        event_type: Provider-specific event type string/header
        payload: Raw webhook JSON payload
        headers: Optional HTTP headers associated with the request
        integration_config: Integration configuration dictionary
        tenant_id: Tenant ID that owns this webhook configuration
        db: Database session

    Returns:
        None. The implementation will be filled in by later tasks.
    """

    if db is None:
        logger.warning("No database session provided; cannot persist CI/CD run.")
        return

    if integration_config is None:
        logger.warning("No integration config provided; cannot process webhook.")
        return

    if tenant_id is None:
        logger.error("No tenant_id provided; cannot process webhook (multi-tenancy required).")
        return

    settings = get_settings()
    metadata = _build_metadata(provider, event_type, payload)

    provider_cfg = _provider_config(provider, integration_config)
    default_suite_id = (integration_config or {}).get("default_suite_id")
    suite_identifier = provider_cfg.get("suite_id") or default_suite_id

    suite_uuid: Optional[UUID] = None
    if suite_identifier:
        try:
            suite_uuid = UUID(str(suite_identifier))
        except (TypeError, ValueError):
            error_msg = f"Invalid suite_id configured for provider {provider}: {suite_identifier}"
            logger.error(error_msg)

            # Create failed CICD run record
            if db is not None:
                try:
                    from models.cicd_run import CICDRun
                    import json

                    cicd_run = CICDRun(
                        tenant_id=tenant_id,
                        provider=provider,
                        pipeline_name=metadata.get("repository") or "Unknown Pipeline",
                        status="failed",
                        branch=metadata.get("branch"),
                        commit_sha=metadata.get("commit_sha"),
                        commit_url=metadata.get("source_url"),
                        triggered_by=metadata.get("author") or "webhook",
                        event_type=event_type,
                        error_message=error_msg,
                        raw_payload=json.dumps(payload) if payload else None,
                    )
                    db.add(cicd_run)
                    await db.commit()
                    logger.info(f"Created failed CICDRun record for invalid suite_id: {cicd_run.id}")
                except Exception as exc:
                    logger.warning(f"Failed to create CICDRun record: {exc}")

            # Exit early - don't attempt to create suite run with invalid suite
            return

    raw_scenario_ids = provider_cfg.get("scenario_ids") or provider_cfg.get("test_case_ids")
    scenario_ids: Optional[list[UUID]] = None
    if isinstance(raw_scenario_ids, (list, tuple)):
        parsed: list[UUID] = []
        for item in raw_scenario_ids:
            try:
                parsed.append(UUID(str(item)))
            except (TypeError, ValueError):
                logger.warning("Invalid scenario_id configured for provider %s", provider)
        if parsed:
            scenario_ids = parsed

    regression_suite_ids = _extract_regression_suite_ids(provider_cfg, integration_config)
    if regression_suite_ids:
        # Convert UUIDs to strings for JSON serialization in metadata
        metadata["regression_suite_ids"] = [str(sid) for sid in regression_suite_ids]

    metadata["suite_id"] = str(suite_uuid) if suite_uuid else None
    metadata["scenario_ids"] = [str(item) for item in (scenario_ids or [])]
    metadata["config_version"] = (integration_config or {}).get("version")

    if headers:
        metadata["headers"] = headers

    logger.info(
        "Dispatching CI/CD webhook event",
        extra={
            "provider": provider,
            "event_type": event_type,
            "branch": metadata.get("branch"),
            "commit": metadata.get("commit_sha"),
        },
    )

    # Check if webhook should be processed based on filters
    should_process, reason = _should_process_webhook(
        provider_config=provider_cfg,
        branch=metadata.get("branch"),
        event_type=event_type
    )

    if not should_process:
        logger.info(
            f"[CICD-FILTER] Skipping webhook: {reason}",
            extra={
                "provider": provider,
                "event_type": event_type,
                "branch": metadata.get("branch"),
                "reason": reason,
            },
        )
        return  # Exit early - do not create run or trigger tests

    logger.info(
        f"[CICD-FILTER] Processing webhook: {reason}",
        extra={
            "provider": provider,
            "event_type": event_type,
            "branch": metadata.get("branch"),
        },
    )

    # Create CI/CD run record for tracking
    if db is not None:
        try:
            from models.cicd_run import CICDRun
            import json

            cicd_run = CICDRun(
                tenant_id=tenant_id,  # Multi-tenant scoping
                provider=provider,
                pipeline_name=metadata.get("repository") or "Unknown Pipeline",
                status="pending",
                branch=metadata.get("branch"),
                commit_sha=metadata.get("commit_sha"),
                commit_url=metadata.get("source_url"),
                triggered_by=metadata.get("author") or "webhook",
                event_type=event_type,
                raw_payload=json.dumps(payload) if payload else None,
            )
            db.add(cicd_run)
            await db.commit()
            logger.info(f"Created CICDRun record for tenant {tenant_id}: {cicd_run.id}")
        except Exception as exc:
            logger.warning(f"Failed to create CICDRun record: {exc}")

    await orchestration_service.create_suite_run(
        db=db,
        suite_id=suite_uuid,
        test_case_ids=scenario_ids,  # Fixed: was undefined test_case_ids
        trigger_type="webhook",
        trigger_metadata=metadata,
        tenant_id=tenant_id,  # FIXED: Add tenant_id for multi-tenant scoping
    )

    # FIXED: Use per-provider regression test setting instead of global setting
    if (
        db is not None
        and provider_cfg.get("run_regression_tests", False)  # Per-provider check
        and _is_deployment_event(event_type)
        and regression_suite_ids  # Only run if suite IDs are configured
    ):
        try:
            logger.info(
                f"[CICD-REGRESSION] Triggering regression tests for deployment event",
                extra={
                    "provider": provider,
                    "event_type": event_type,
                    "regression_suite_ids": regression_suite_ids,
                    "tenant_id": str(tenant_id),
                },
            )
            executor = RegressionSuiteExecutor(db=db, settings=settings)
            await executor.execute(
                trigger=_normalise_trigger(event_type),
                metadata=metadata,
            )
        except Exception as exc:  # pragma: no cover - defensive log
            logger.warning(
                f"Automatic regression execution failed: {exc}",
                extra={"provider": provider, "tenant_id": str(tenant_id)},
            )


async def load_integration_config_by_token(
    db: AsyncSession,
    webhook_token: str,
) -> tuple[Optional[Dict[str, Any]], Optional[UUID]]:
    """
    Fetch CI/CD integration configuration by webhook token.

    Args:
        db: Database session
        webhook_token: Unique webhook token (avtwh_*)

    Returns:
        Tuple of (config_data dict, tenant_id UUID) or (None, None) if not found
    """
    from models.configuration import Configuration
    from sqlalchemy import select

    try:
        # Query for configuration with matching webhook_token
        stmt = select(Configuration).where(
            Configuration.config_key == "integration.cicd",
            Configuration.is_active.is_(True),
        )
        result = await db.execute(stmt)
        configs = result.scalars().all()

        # Find config with matching webhook token
        for config in configs:
            if config.config_data and isinstance(config.config_data, dict):
                if config.config_data.get("webhook_token") == webhook_token:
                    return dict(config.config_data), config.tenant_id

        logger.warning(f"No active CI/CD config found for webhook token: {webhook_token[:15]}...")
        return None, None

    except Exception as exc:  # pragma: no cover - defensive
        logger.error(f"Error loading CI/CD config by token: {exc}")
        return None, None


async def load_integration_config(db: Optional[AsyncSession]) -> Dict[str, Any]:
    """
    Fetch the CI/CD integration configuration from the database when available.

    DEPRECATED: Use load_integration_config_by_token instead for multi-tenant support.
    This function is kept for backward compatibility but should not be used.
    """

    if db is None:
        return {}

    try:
        return await db.run_sync(_fetch_integration_config)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Unable to load CI/CD integration configuration: %s", exc)
        return {}


def _fetch_integration_config(sync_session) -> Dict[str, Any]:
    """
    DEPRECATED: This function doesn't support multi-tenancy properly.
    Use load_integration_config_by_token instead.
    """
    service = ConfigurationService(sync_session)
    # This is broken - needs tenant_id but we don't have it here
    # Keeping for backward compatibility only
    return {}
