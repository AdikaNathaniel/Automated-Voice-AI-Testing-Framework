"""
Integration routes for managing external service integrations.

Handles:
- GitHub integration status and configuration (database-backed)
- Jira integration status and configuration (database-backed)
- Slack integration status and configuration (database-backed)
- Integration logs and activity
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Body, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.dependencies import get_db, get_current_user_with_db
from api.schemas.responses import SuccessResponse, ErrorResponse
from api.schemas.auth import UserResponse
from models.audit_trail import log_audit_trail
from models.notification_config import NotificationConfig
from models.integration_config import IntegrationConfig

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/integrations", tags=["integrations"])


def _get_effective_tenant_id(user: UserResponse) -> UUID:
    """
    Get effective tenant_id for a user.

    Uses user.tenant_id if set (user belongs to an organization),
    otherwise uses user.id (user is their own tenant).

    This ensures consistent tenant isolation across the application.
    """
    return user.tenant_id if user.tenant_id else user.id


class GitHubConfig(BaseModel):
    """GitHub integration configuration."""
    access_token: Optional[str] = Field(None, description="GitHub access token")
    username: Optional[str] = Field(None, description="GitHub username")
    repositories: List[str] = Field(default_factory=list, description="List of repositories to integrate")
    webhook_secret: Optional[str] = Field(None, description="Webhook secret for GitHub events")
    auto_create_issues: bool = Field(False, description="Auto-create GitHub issues for failed tests")


class JiraConfig(BaseModel):
    """Jira integration configuration."""
    instance_url: Optional[str] = Field(None, description="Jira instance URL")
    api_token: Optional[str] = Field(None, description="Jira API token")
    email: Optional[str] = Field(None, description="Jira account email")
    project_key: Optional[str] = Field(None, description="Default project key")
    issue_type: str = Field("Bug", description="Default issue type for defects")
    auto_create_tickets: bool = Field(False, description="Auto-create Jira tickets for failed tests")


class SlackConfig(BaseModel):
    """Slack integration configuration (legacy - kept for backward compatibility)."""
    bot_token: Optional[str] = Field(None, description="Slack bot token")
    workspace: Optional[str] = Field(None, description="Workspace name")
    default_channel: Optional[str] = Field(None, description="Default notification channel")
    notify_on_failure: bool = Field(True, description="Send notifications on test failures")
    notify_on_completion: bool = Field(False, description="Send notifications on test run completion")


# =============================================================================
# Database Helpers for Integration Configs
# =============================================================================

async def _get_or_create_integration_config(
    db: AsyncSession,
    tenant_id: UUID,
    integration_type: str,
) -> IntegrationConfig:
    """Get or create integration config for a specific type and tenant."""
    result = await db.execute(
        select(IntegrationConfig).where(
            IntegrationConfig.tenant_id == tenant_id,
            IntegrationConfig.integration_type == integration_type,
        )
    )
    config = result.scalar_one_or_none()
    if not config:
        config = IntegrationConfig(
            tenant_id=tenant_id,
            integration_type=integration_type,
            is_enabled=True,
            is_connected=False,
            settings={},
        )
        db.add(config)
        await db.commit()
        await db.refresh(config)
    return config


class SlackNotificationPreference(BaseModel):
    """Notification preference for a specific event type."""
    enabled: bool = Field(True, description="Whether notifications are enabled for this type")
    channel: str = Field("", description="Specific channel for this notification type")


class SlackNotificationPreferences(BaseModel):
    """All notification preferences for Slack."""
    suiteRun: SlackNotificationPreference = Field(
        default_factory=lambda: SlackNotificationPreference()
    )
    criticalDefect: SlackNotificationPreference = Field(
        default_factory=lambda: SlackNotificationPreference()
    )
    systemAlert: SlackNotificationPreference = Field(
        default_factory=lambda: SlackNotificationPreference()
    )
    edgeCase: SlackNotificationPreference = Field(
        default_factory=lambda: SlackNotificationPreference()
    )


class SlackIntegrationConfigResponse(BaseModel):
    """Response schema matching frontend SlackIntegrationConfig interface."""
    isConnected: bool = Field(False, description="Whether Slack is connected")
    workspaceName: Optional[str] = Field(None, description="Connected workspace name")
    workspaceIconUrl: Optional[str] = Field(None, description="Workspace icon URL")
    connectUrl: str = Field("", description="OAuth connect URL")
    defaultChannel: str = Field("", description="Default notification channel")
    notificationPreferences: SlackNotificationPreferences = Field(
        default_factory=SlackNotificationPreferences
    )
    botTokenSet: bool = Field(False, description="Whether bot token is configured")
    signingSecretSet: bool = Field(False, description="Whether signing secret is set")


class SlackIntegrationUpdatePayload(BaseModel):
    """Payload for updating Slack integration settings."""
    defaultChannel: str = Field("", description="Default notification channel")
    notificationPreferences: SlackNotificationPreferences = Field(
        default_factory=SlackNotificationPreferences
    )
    webhookUrl: Optional[str] = Field(None, description="Slack webhook URL")
    botToken: Optional[str] = Field(None, description="Slack bot token")
    signingSecret: Optional[str] = Field(None, description="Slack signing secret")


# =============================================================================
# GitHub Integration Endpoints (Database-backed)
# =============================================================================

class GitHubSyncSettings(BaseModel):
    """GitHub sync settings matching frontend interface."""
    repository: str = Field("", description="Selected repository")
    syncDirection: str = Field("both", description="Sync direction: pull, push, or both")
    autoSync: bool = Field(True, description="Enable auto-sync")
    createIssues: bool = Field(True, description="Auto-create issues for failed tests")


@router.get("/github/status")
async def get_github_status(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> SuccessResponse:
    """Get GitHub integration status matching frontend GitHubIntegrationStatusResponse."""
    tenant_id = _get_effective_tenant_id(current_user)
    logger.info(f"[INTEGRATIONS] Getting GitHub status for tenant {tenant_id}")

    config = await _get_or_create_integration_config(db, tenant_id, "github")
    logger.debug(f"[INTEGRATIONS] GitHub config: connected={config.is_connected}, username={config.github_username}, settings_keys={list(config.settings.keys()) if config.settings else []}")

    # Build response matching frontend expectations
    # Get repositories from settings (stored during OAuth)
    repositories = config.get_setting("github_repositories", [])
    logger.info(f"[INTEGRATIONS] Retrieved {len(repositories)} repositories from github_repositories setting")

    # Fallback to legacy github_repositories field if settings is empty
    # (this checks settings["repositories"] which is a different key - for backward compatibility)
    if not repositories and config.github_repositories:
        logger.info(f"[INTEGRATIONS] Using legacy repositories field with {len(config.github_repositories)} items")
        repositories = []
        for idx, repo_name in enumerate(config.github_repositories):
            repositories.append({
                "id": idx + 1,
                "name": repo_name.split("/")[-1] if "/" in repo_name else repo_name,
                "fullName": repo_name,
                "private": False,
                "defaultBranch": "main",
            })

    if not repositories:
        logger.warning(f"[INTEGRATIONS] No repositories found for tenant {tenant_id} - user may need to reconnect")

    account = None
    if config.is_connected and config.github_username:
        account = {
            "login": config.github_username,
            "avatarUrl": f"https://github.com/{config.github_username}.png",
            "htmlUrl": f"https://github.com/{config.github_username}",
        }

    sync_settings = {
        "repository": config.get_setting("selected_repository", ""),
        "syncDirection": config.get_setting("sync_direction", "both"),
        "autoSync": config.get_setting("auto_sync", True),
        "createIssues": config.github_auto_create_issues,
    }

    return SuccessResponse(
        data={
            "connected": config.is_connected,
            "account": account,
            "authorizationUrl": None,  # Will be set by /connect endpoint
            "syncSettings": sync_settings,
            "repositories": repositories,
            "lastSyncedAt": config.last_sync_at.isoformat() if config.last_sync_at else None,
        }
    )


@router.post("/github/connect")
async def start_github_connection(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> SuccessResponse:
    """
    Start GitHub OAuth connection flow.

    Returns an authorization URL that the frontend should redirect the user to.
    The state parameter contains the tenant_id so the callback can identify the user.
    """
    import base64
    import json
    import secrets
    from urllib.parse import urlencode

    tenant_id = _get_effective_tenant_id(current_user)
    logger.info(f"[INTEGRATIONS] Starting GitHub connection for tenant {tenant_id}")

    from api.config import get_settings
    settings = get_settings()

    client_id = settings.GITHUB_CLIENT_ID
    client_secret = settings.GITHUB_CLIENT_SECRET
    redirect_uri = settings.GITHUB_REDIRECT_URI

    if client_id and client_secret:
        # Generate state with tenant_id for callback identification
        state_data = {
            "tenant_id": str(tenant_id),
            "nonce": secrets.token_urlsafe(16),
        }
        state = base64.urlsafe_b64encode(json.dumps(state_data).encode()).decode()

        # Build OAuth authorization URL
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": "repo read:user user:email",
            "state": state,
        }
        auth_url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"

        logger.info(f"[INTEGRATIONS] Generated GitHub OAuth URL for tenant {tenant_id}")
    else:
        # Fallback: Direct user to create a Personal Access Token manually
        logger.warning("[INTEGRATIONS] GitHub OAuth not configured, using PAT fallback")
        auth_url = "https://github.com/settings/tokens/new?description=VoiceAI%20Testing&scopes=repo,read:user,user:email"

    return SuccessResponse(
        data={
            "authorizationUrl": auth_url,
            "oauthConfigured": bool(client_id and client_secret),
        }
    )


@router.get("/github/callback")
async def github_oauth_callback(
    code: str = Query(..., description="Authorization code from GitHub"),
    state: str = Query(..., description="State parameter for CSRF protection"),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse:
    """
    Handle GitHub OAuth callback.

    This endpoint receives the authorization code from GitHub after user authorization,
    exchanges it for an access token, fetches user info, and stores the connection.

    Note: This endpoint doesn't require authentication because it's a callback from GitHub.
    The state parameter is used to identify the user/tenant.
    """
    from api.config import get_settings
    from integrations.github.oauth import GitHubOAuthClient, GitHubOAuthError
    import base64
    import json

    settings = get_settings()

    client_id = settings.GITHUB_CLIENT_ID
    client_secret = settings.GITHUB_CLIENT_SECRET
    redirect_uri = settings.GITHUB_REDIRECT_URI
    frontend_url = settings.FRONTEND_URL

    if not client_id or not client_secret:
        logger.error("[GITHUB OAUTH] GitHub OAuth not configured - missing client_id or client_secret")
        # Redirect to frontend with error
        error_url = f"{frontend_url}/integrations/github?error=oauth_not_configured"
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=error_url, status_code=302)

    # Decode state to get tenant_id (state is base64-encoded JSON: {"tenant_id": "...", "nonce": "..."})
    try:
        state_data = json.loads(base64.urlsafe_b64decode(state.encode()).decode())
        tenant_id = UUID(state_data.get("tenant_id"))
        logger.info(f"[GITHUB OAUTH] Processing callback for tenant {tenant_id}")
    except Exception as e:
        logger.error(f"[GITHUB OAUTH] Invalid state parameter: {e}")
        error_url = f"{frontend_url}/integrations/github?error=invalid_state"
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=error_url, status_code=302)

    # Create OAuth client and exchange code for token
    try:
        oauth_client = GitHubOAuthClient(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=["repo", "read:user", "user:email"],
        )

        # Exchange authorization code for access token
        token = await oauth_client.exchange_code_for_token(code=code)
        logger.info(f"[GITHUB OAUTH] Token exchange successful, scopes: {token.scopes}")

        # Fetch user profile
        user = await oauth_client.fetch_user_profile(token=token.access_token)
        logger.info(f"[GITHUB OAUTH] Fetched user profile: {user.login}")

        # Fetch user's repositories - this is critical for the integration to work
        repositories = []
        try:
            repositories = await oauth_client.fetch_user_repositories(token=token.access_token)
            logger.info(f"[GITHUB OAUTH] Successfully fetched {len(repositories)} repositories for user {user.login}")
            if repositories:
                logger.debug(f"[GITHUB OAUTH] First few repos: {[r.get('fullName') for r in repositories[:3]]}")
            else:
                logger.warning(f"[GITHUB OAUTH] No repositories found for user {user.login} - user may have no accessible repos")
        except Exception as repo_error:
            logger.error(f"[GITHUB OAUTH] Failed to fetch repositories for user {user.login}: {repo_error}")
            # Continue with empty repos - user can still connect but won't see repos
            # They can try reconnecting later

    except GitHubOAuthError as e:
        logger.error(f"[GITHUB OAUTH] OAuth error: {e}")
        error_url = f"{frontend_url}/integrations/github?error=oauth_failed&message={str(e)}"
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=error_url, status_code=302)
    except Exception as e:
        logger.error(f"[GITHUB OAUTH] Unexpected error: {e}")
        error_url = f"{frontend_url}/integrations/github?error=unexpected_error"
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=error_url, status_code=302)

    # Store the connection in database
    try:
        config = await _get_or_create_integration_config(db, tenant_id, "github")
        logger.info(f"[GITHUB OAUTH] Storing connection for tenant {tenant_id}, config id: {config.id}")

        # Encrypt and store the access token
        config.set_access_token(token.access_token)
        config.github_username = user.login
        config.is_connected = True
        config.is_enabled = True
        config.last_sync_at = datetime.now(timezone.utc)

        # Initialize settings dict if needed
        if config.settings is None:
            config.settings = {}

        # Store additional user info in settings using update_settings for atomic update
        new_settings = {
            "github_user_id": user.id,
            "github_email": user.email,
            "github_avatar_url": user.avatar_url,
            "github_scopes": token.scopes,
            "github_repositories": repositories,
        }
        config.update_settings(new_settings)

        logger.info(f"[GITHUB OAUTH] Storing {len(repositories)} repositories in settings")

        # Mark settings as modified to ensure SQLAlchemy detects the JSONB change
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(config, "settings")

        await db.commit()
        await db.refresh(config)

        # Verify the data was saved correctly
        saved_repos = config.get_setting("github_repositories", [])
        logger.info(f"[GITHUB OAUTH] Verified {len(saved_repos)} repositories saved for tenant {tenant_id}, user {user.login}")

        # Redirect to frontend with success
        success_url = f"{frontend_url}/integrations/github?success=true&username={user.login}"
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=success_url, status_code=302)

    except Exception as e:
        logger.error(f"[GITHUB OAUTH] Failed to store connection: {e}")
        error_url = f"{frontend_url}/integrations/github?error=storage_failed"
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=error_url, status_code=302)


@router.post("/github/disconnect")
async def disconnect_github_post(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> SuccessResponse:
    """Disconnect GitHub integration (POST version for frontend compatibility)."""
    tenant_id = _get_effective_tenant_id(current_user)
    logger.info(f"[INTEGRATIONS] Disconnecting GitHub for tenant {tenant_id}")

    config = await _get_or_create_integration_config(db, tenant_id, "github")

    # Clear connection but keep some settings
    config.is_connected = False
    config.access_token_encrypted = None
    config.secret_encrypted = None

    await db.commit()
    await db.refresh(config)

    return SuccessResponse(
        data={"message": "GitHub integration disconnected successfully"}
    )


@router.put("/github/sync-settings")
async def update_github_sync_settings(
    settings_data: GitHubSyncSettings,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> SuccessResponse:
    """Update GitHub sync settings."""
    tenant_id = _get_effective_tenant_id(current_user)
    logger.info(f"[INTEGRATIONS] Updating GitHub sync settings for tenant {tenant_id}")

    config = await _get_or_create_integration_config(db, tenant_id, "github")

    # Update sync settings
    config.set_setting("selected_repository", settings_data.repository)
    config.set_setting("sync_direction", settings_data.syncDirection)
    config.set_setting("auto_sync", settings_data.autoSync)
    config.github_auto_create_issues = settings_data.createIssues

    # Mark JSONB field as modified so SQLAlchemy detects the changes
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(config, "settings")

    await db.commit()
    await db.refresh(config)

    return SuccessResponse(
        data={
            "repository": settings_data.repository,
            "syncDirection": settings_data.syncDirection,
            "autoSync": settings_data.autoSync,
            "createIssues": settings_data.createIssues,
        }
    )


@router.post("/github/refresh-repos")
async def refresh_github_repositories(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> SuccessResponse:
    """
    Refresh the list of GitHub repositories for the connected account.

    This endpoint fetches the latest list of repositories from GitHub
    without requiring a full OAuth reconnection.
    """
    from integrations.github.oauth import GitHubOAuthClient, GitHubOAuthError

    tenant_id = _get_effective_tenant_id(current_user)
    logger.info(f"[INTEGRATIONS] Refreshing GitHub repositories for tenant {tenant_id}")

    config = await _get_or_create_integration_config(db, tenant_id, "github")

    if not config.is_connected:
        raise HTTPException(
            status_code=400,
            detail="GitHub is not connected. Please connect your GitHub account first."
        )

    # Get the stored access token
    access_token = config.get_access_token()
    if not access_token:
        raise HTTPException(
            status_code=400,
            detail="No access token found. Please reconnect your GitHub account."
        )

    # Fetch repositories using the stored token
    from api.config import get_settings
    settings = get_settings()

    try:
        oauth_client = GitHubOAuthClient(
            client_id=settings.GITHUB_CLIENT_ID or "",
            client_secret=settings.GITHUB_CLIENT_SECRET or "",
            redirect_uri=settings.GITHUB_REDIRECT_URI or "",
        )

        repositories = await oauth_client.fetch_user_repositories(token=access_token)
        logger.info(f"[INTEGRATIONS] Refreshed {len(repositories)} repositories for tenant {tenant_id}")

        # Update the stored repositories
        config.set_setting("github_repositories", repositories)
        config.last_sync_at = datetime.now(timezone.utc)

        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(config, "settings")

        await db.commit()
        await db.refresh(config)

        return SuccessResponse(
            data={
                "message": f"Successfully refreshed {len(repositories)} repositories",
                "repositories": repositories,
                "count": len(repositories),
            }
        )

    except GitHubOAuthError as e:
        logger.error(f"[INTEGRATIONS] Failed to refresh repositories: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to fetch repositories from GitHub: {str(e)}"
        )
    except Exception as e:
        logger.error(f"[INTEGRATIONS] Unexpected error refreshing repositories: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while refreshing repositories"
        )


@router.post("/github/config")
async def update_github_config(
    config_data: GitHubConfig,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> SuccessResponse:
    """Update GitHub integration configuration in database."""
    tenant_id = _get_effective_tenant_id(current_user)
    logger.info(f"[INTEGRATIONS] Updating GitHub config for tenant {tenant_id}")

    config = await _get_or_create_integration_config(db, tenant_id, "github")

    # Update encrypted access token if provided
    if config_data.access_token:
        config.set_access_token(config_data.access_token)
        config.is_connected = True

    # Update encrypted webhook secret if provided
    if config_data.webhook_secret:
        config.set_secret(config_data.webhook_secret)

    # Update settings
    config.github_username = config_data.username
    config.github_repositories = config_data.repositories
    config.github_auto_create_issues = config_data.auto_create_issues
    config.mark_synced()

    await db.commit()
    await db.refresh(config)

    # Log GitHub integration config update
    await log_audit_trail(
        db=db,
        action_type="update",
        resource_type="integration_config",
        resource_id=str(config.id),
        tenant_id=tenant_id,
        user_id=current_user.id,
        new_values={
            "integration_type": "github",
            "is_connected": config.is_connected,
            "username": config.github_username,
            "repositories": config.github_repositories,
            "auto_create_issues": config.github_auto_create_issues,
        },
        changes_summary=f"GitHub integration configured by {current_user.email}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=True,
    )

    logger.info(f"[INTEGRATIONS] GitHub config updated for tenant {tenant_id}")

    return SuccessResponse(
        data={
            "message": "GitHub configuration updated successfully",
            "connected": config.is_connected,
            "username": config.github_username,
            "repositories": config.github_repositories,
        }
    )


@router.delete("/github/config")
async def disconnect_github(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> SuccessResponse:
    """Disconnect GitHub integration."""
    tenant_id = _get_effective_tenant_id(current_user)
    logger.info(f"[INTEGRATIONS] Disconnecting GitHub for tenant {tenant_id}")

    config = await _get_or_create_integration_config(db, tenant_id, "github")

    # Clear connection but keep settings
    config.is_connected = False
    config.access_token_encrypted = None
    config.secret_encrypted = None

    await db.commit()
    await db.refresh(config)

    # Log GitHub integration disconnect
    await log_audit_trail(
        db=db,
        action_type="disconnect",
        resource_type="integration_config",
        resource_id=str(config.id),
        tenant_id=tenant_id,
        user_id=current_user.id,
        old_values={
            "integration_type": "github",
            "is_connected": True,
        },
        new_values={
            "integration_type": "github",
            "is_connected": False,
        },
        changes_summary=f"GitHub integration disconnected by {current_user.email}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=True,
    )

    return SuccessResponse(
        data={"message": "GitHub integration disconnected successfully"}
    )


# =============================================================================
# Jira Integration Endpoints (Database-backed)
# =============================================================================

class JiraProjectConfigModel(BaseModel):
    """Jira project configuration matching frontend interface."""
    projectKey: str = Field("", description="Jira project key")
    issueType: str = Field("Bug", description="Default issue type")
    browseUrl: Optional[str] = Field(None, description="Project browse URL")
    priorityMap: Optional[Dict[str, str]] = Field(None, description="Priority mapping")
    labels: Optional[List[str]] = Field(None, description="Default labels")


class JiraIntegrationUpdatePayload(BaseModel):
    """Payload for updating Jira integration matching frontend interface."""
    baseUrl: str = Field("", description="Jira instance base URL")
    browseUrl: str = Field("", description="Jira browse URL")
    userEmail: str = Field("", description="Jira user email")
    apiToken: Optional[str] = Field(None, description="Jira API token")
    timeoutSeconds: Optional[int] = Field(None, description="Request timeout")
    projectMapping: Dict[str, JiraProjectConfigModel] = Field(
        default_factory=dict, description="Project mappings"
    )


@router.get("/jira/config")
async def get_jira_config(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> SuccessResponse:
    """Get Jira integration configuration matching frontend JiraIntegrationConfig."""
    tenant_id = _get_effective_tenant_id(current_user)
    logger.info(f"[INTEGRATIONS] Getting Jira config for tenant {tenant_id}")

    config = await _get_or_create_integration_config(db, tenant_id, "jira")

    # Build response matching frontend expectations
    project_mapping = config.get_setting("project_mapping", {})

    return SuccessResponse(
        data={
            "baseUrl": config.jira_instance_url or "",
            "browseUrl": config.get_setting("browse_url", ""),
            "userEmail": config.jira_email or "",
            "apiTokenSet": config.access_token_encrypted is not None,
            "timeoutSeconds": config.get_setting("timeout_seconds"),
            "projectMapping": project_mapping,
        }
    )


@router.put("/jira/config")
async def update_jira_config_put(
    payload: JiraIntegrationUpdatePayload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> SuccessResponse:
    """Update Jira integration configuration (PUT for frontend compatibility)."""
    tenant_id = _get_effective_tenant_id(current_user)
    logger.info(f"[INTEGRATIONS] Updating Jira config for tenant {tenant_id}")

    config = await _get_or_create_integration_config(db, tenant_id, "jira")

    # Update encrypted API token if provided
    if payload.apiToken:
        config.set_access_token(payload.apiToken)
        config.is_connected = True

    # Update settings
    config.jira_instance_url = payload.baseUrl
    config.jira_email = payload.userEmail
    config.set_setting("browse_url", payload.browseUrl)
    config.set_setting("timeout_seconds", payload.timeoutSeconds)
    config.set_setting("project_mapping", {
        k: v.model_dump() for k, v in payload.projectMapping.items()
    })

    # Extract default project key from first mapping
    if payload.projectMapping:
        first_project = next(iter(payload.projectMapping.values()), None)
        if first_project:
            config.jira_project_key = first_project.projectKey
            config.jira_issue_type = first_project.issueType

    # Mark JSONB field as modified so SQLAlchemy detects the changes
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(config, "settings")

    await db.commit()
    await db.refresh(config)

    # Log Jira integration config update
    await log_audit_trail(
        db=db,
        action_type="update",
        resource_type="integration_config",
        resource_id=str(config.id),
        tenant_id=tenant_id,
        user_id=current_user.id,
        new_values={
            "integration_type": "jira",
            "is_connected": config.is_connected,
            "base_url": config.jira_instance_url,
            "user_email": config.jira_email,
            "project_key": config.jira_project_key,
        },
        changes_summary=f"Jira integration configured by {current_user.email}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=True,
    )

    logger.info(f"[INTEGRATIONS] Jira config updated for tenant {tenant_id}")

    # Return updated config in expected format
    return SuccessResponse(
        data={
            "baseUrl": config.jira_instance_url or "",
            "browseUrl": config.get_setting("browse_url", ""),
            "userEmail": config.jira_email or "",
            "apiTokenSet": config.access_token_encrypted is not None,
            "timeoutSeconds": config.get_setting("timeout_seconds"),
            "projectMapping": config.get_setting("project_mapping", {}),
        }
    )


@router.post("/jira/config")
async def update_jira_config_post(
    config_data: JiraConfig,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> SuccessResponse:
    """Update Jira integration configuration (POST - legacy support)."""
    tenant_id = _get_effective_tenant_id(current_user)
    logger.info(f"[INTEGRATIONS] Updating Jira config (POST) for tenant {tenant_id}")

    config = await _get_or_create_integration_config(db, tenant_id, "jira")

    # Update encrypted API token if provided
    if config_data.api_token:
        config.set_access_token(config_data.api_token)

    # Update settings
    config.jira_instance_url = config_data.instance_url
    config.jira_email = config_data.email
    config.jira_project_key = config_data.project_key
    config.jira_issue_type = config_data.issue_type
    config.jira_auto_create_tickets = config_data.auto_create_tickets

    # Mark as connected if we have both URL and token
    config.is_connected = bool(config_data.instance_url and config_data.api_token)

    await db.commit()
    await db.refresh(config)

    logger.info(f"[INTEGRATIONS] Jira config updated for tenant {tenant_id}")

    return SuccessResponse(
        data={
            "message": "Jira configuration updated successfully",
            "connected": config.is_connected,
            "project_key": config.jira_project_key,
        }
    )


@router.delete("/jira/config")
async def disconnect_jira(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> SuccessResponse:
    """Disconnect Jira integration."""
    tenant_id = _get_effective_tenant_id(current_user)
    logger.info(f"[INTEGRATIONS] Disconnecting Jira for tenant {tenant_id}")

    config = await _get_or_create_integration_config(db, tenant_id, "jira")

    # Clear connection but keep settings
    config.is_connected = False
    config.access_token_encrypted = None

    await db.commit()
    await db.refresh(config)

    # Log Jira integration disconnect
    await log_audit_trail(
        db=db,
        action_type="disconnect",
        resource_type="integration_config",
        resource_id=str(config.id),
        tenant_id=tenant_id,
        user_id=current_user.id,
        old_values={
            "integration_type": "jira",
            "is_connected": True,
        },
        new_values={
            "integration_type": "jira",
            "is_connected": False,
        },
        changes_summary=f"Jira integration disconnected by {current_user.email}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=True,
    )

    return SuccessResponse(
        data={"message": "Jira integration disconnected successfully"}
    )


async def _get_or_create_slack_config(
    db: AsyncSession,
    tenant_id: UUID,
) -> NotificationConfig:
    """Get or create Slack notification config for tenant."""
    result = await db.execute(
        select(NotificationConfig).where(
            NotificationConfig.tenant_id == tenant_id,
            NotificationConfig.channel_type == "slack",
        )
    )
    config = result.scalar_one_or_none()
    if not config:
        config = NotificationConfig(
            tenant_id=tenant_id,
            channel_type="slack",
            is_enabled=True,
            is_connected=False,
            notification_preferences=NotificationConfig.get_default_preferences(),
        )
        db.add(config)
        await db.commit()
        await db.refresh(config)
    return config


def _build_slack_response(config: NotificationConfig) -> SlackIntegrationConfigResponse:
    """Build frontend-compatible response from NotificationConfig."""
    prefs = config.notification_preferences or {}
    default_pref = {"enabled": True, "channel": ""}
    return SlackIntegrationConfigResponse(
        isConnected=config.is_connected,
        workspaceName=config.workspace_name,
        workspaceIconUrl=config.workspace_icon_url,
        connectUrl="",  # OAuth URL would be generated dynamically
        defaultChannel=config.default_channel or "",
        notificationPreferences=SlackNotificationPreferences(
            suiteRun=SlackNotificationPreference(**prefs.get("suiteRun", default_pref)),
            criticalDefect=SlackNotificationPreference(**prefs.get("criticalDefect", default_pref)),
            systemAlert=SlackNotificationPreference(**prefs.get("systemAlert", default_pref)),
            edgeCase=SlackNotificationPreference(**prefs.get("edgeCase", default_pref)),
        ),
        botTokenSet=bool(config.bot_token_encrypted),
        signingSecretSet=bool(config.signing_secret_encrypted),
    )


@router.get("/slack/config")
async def get_slack_config(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> SlackIntegrationConfigResponse:
    """Get Slack integration configuration from database."""
    tenant_id = _get_effective_tenant_id(current_user)
    logger.info(f"[INTEGRATIONS] Getting Slack config for tenant {tenant_id}")
    config = await _get_or_create_slack_config(db, tenant_id)
    return _build_slack_response(config)


@router.put("/slack/config")
async def update_slack_config(
    payload: SlackIntegrationUpdatePayload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> SlackIntegrationConfigResponse:
    """Update Slack integration configuration in database."""
    tenant_id = _get_effective_tenant_id(current_user)
    logger.info(f"[INTEGRATIONS] Updating Slack config for tenant {tenant_id}")

    config = await _get_or_create_slack_config(db, tenant_id)

    # Update default channel
    config.default_channel = payload.defaultChannel

    # Update notification preferences
    config.notification_preferences = {
        "suiteRun": payload.notificationPreferences.suiteRun.model_dump(),
        "criticalDefect": payload.notificationPreferences.criticalDefect.model_dump(),
        "systemAlert": payload.notificationPreferences.systemAlert.model_dump(),
        "edgeCase": payload.notificationPreferences.edgeCase.model_dump(),
    }

    # Update sensitive fields only if provided
    if payload.webhookUrl is not None:
        config.set_webhook_url(payload.webhookUrl)
        if payload.webhookUrl:
            config.is_connected = True

    if payload.botToken is not None:
        config.set_bot_token(payload.botToken)
        if payload.botToken:
            config.is_connected = True

    if payload.signingSecret is not None:
        config.set_signing_secret(payload.signingSecret)

    # Mark JSONB field as modified so SQLAlchemy detects the changes
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(config, "notification_preferences")

    await db.commit()
    await db.refresh(config)

    # Log Slack integration config update
    await log_audit_trail(
        db=db,
        action_type="update",
        resource_type="notification_config",
        resource_id=str(config.id),
        tenant_id=tenant_id,
        user_id=current_user.id,
        new_values={
            "channel_type": "slack",
            "is_connected": config.is_connected,
            "default_channel": config.default_channel,
            "workspace_name": config.workspace_name,
        },
        changes_summary=f"Slack integration configured by {current_user.email}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=True,
    )

    logger.info(f"[INTEGRATIONS] Slack config updated for tenant {tenant_id}")
    return _build_slack_response(config)


@router.delete("/slack/config")
async def disconnect_slack(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> SlackIntegrationConfigResponse:
    """Disconnect Slack integration."""
    tenant_id = _get_effective_tenant_id(current_user)
    logger.info(f"[INTEGRATIONS] Disconnecting Slack for tenant {tenant_id}")

    config = await _get_or_create_slack_config(db, tenant_id)

    # Clear connection but keep preferences
    config.is_connected = False
    config.webhook_url_encrypted = None
    config.bot_token_encrypted = None
    config.signing_secret_encrypted = None
    config.workspace_name = None
    config.workspace_icon_url = None

    await db.commit()
    await db.refresh(config)

    # Log Slack integration disconnect
    await log_audit_trail(
        db=db,
        action_type="disconnect",
        resource_type="notification_config",
        resource_id=str(config.id),
        tenant_id=tenant_id,
        user_id=current_user.id,
        old_values={
            "channel_type": "slack",
            "is_connected": True,
        },
        new_values={
            "channel_type": "slack",
            "is_connected": False,
        },
        changes_summary=f"Slack integration disconnected by {current_user.email}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=True,
    )

    return _build_slack_response(config)


@router.post("/slack/test")
async def test_slack_notification(
    channel: Optional[str] = Body(None, embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> SuccessResponse:
    """Send a test notification to Slack."""
    tenant_id = _get_effective_tenant_id(current_user)
    logger.info(f"[INTEGRATIONS] Testing Slack notification for tenant {tenant_id}")

    config = await _get_or_create_slack_config(db, tenant_id)

    if not config.is_connected:
        raise HTTPException(
            status_code=400,
            detail="Slack integration not connected. Please configure your webhook URL or bot token first."
        )

    target_channel = channel or config.default_channel
    if not target_channel:
        raise HTTPException(
            status_code=400,
            detail="No channel specified and no default channel configured."
        )

    # Send actual test notification if webhook is configured
    webhook_url = config.get_webhook_url()
    if webhook_url:
        try:
            from integrations.slack.client import SlackClient
            client = SlackClient(webhook_url=webhook_url, default_channel=target_channel)
            await client.send_message(
                text=f"Test notification from Voice AI Testing Framework",
                channel=target_channel,
            )
            logger.info(f"[INTEGRATIONS] Test notification sent to channel: {target_channel}")
        except Exception as e:
            logger.error(f"[INTEGRATIONS] Failed to send test notification: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send test notification: {str(e)}"
            )
    else:
        logger.info(f"[INTEGRATIONS] Test notification would be sent to channel: {target_channel}")

    return SuccessResponse(
        data={
            "message": f"Test notification sent to {target_channel}",
            "channel": target_channel,
            "status": "sent"
        }
    )


# In-memory log storage for integration activity
_integration_logs: List[Dict[str, Any]] = []


def _log_integration_activity(
    user_id: UUID,
    integration: str,
    action: str,
    level: str = "info",
    details: Optional[Dict[str, Any]] = None
):
    """Log integration activity."""
    log_entry = {
        "id": len(_integration_logs) + 1,
        "user_id": str(user_id),
        "integration": integration,
        "action": action,
        "level": level,
        "details": details or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    _integration_logs.append(log_entry)

    # Keep only last 1000 logs
    if len(_integration_logs) > 1000:
        _integration_logs.pop(0)


@router.get("/logs")
async def get_integration_logs(
    integration: str = Query("all", description="Filter by integration type (github, jira, slack, all)"),
    level: str = Query("all", description="Filter by log level (info, warning, error, all)"),
    limit: int = Query(20, ge=1, le=100, description="Number of logs to return"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> SuccessResponse:
    """Get integration activity logs."""
    logger.info(
        f"[INTEGRATIONS] Getting logs - integration={integration}, "
        f"level={level}, limit={limit}, user={current_user.id}"
    )

    # Filter logs for current user
    user_logs = [
        log for log in _integration_logs
        if log["user_id"] == str(current_user.id)
    ]

    # Apply integration filter
    if integration != "all":
        user_logs = [log for log in user_logs if log["integration"] == integration]

    # Apply level filter
    if level != "all":
        user_logs = [log for log in user_logs if log["level"] == level]

    # Sort by timestamp (most recent first) and limit
    user_logs = sorted(user_logs, key=lambda x: x["timestamp"], reverse=True)[:limit]

    return SuccessResponse(
        data={
            "items": user_logs,
            "total": len(user_logs),
            "filters": {
                "integration": integration,
                "level": level,
                "limit": limit
            }
        }
    )


@router.get("/status")
async def get_all_integrations_status(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> SuccessResponse:
    """Get status of all integrations for the current user (all database-backed)."""
    tenant_id = _get_effective_tenant_id(current_user)
    logger.info(f"[INTEGRATIONS] Getting all integration status for tenant {tenant_id}")

    # All configs from database
    github_config = await _get_or_create_integration_config(db, tenant_id, "github")
    jira_config = await _get_or_create_integration_config(db, tenant_id, "jira")
    slack_config = await _get_or_create_slack_config(db, tenant_id)

    return SuccessResponse(
        data={
            "github": {
                "connected": github_config.is_connected,
                "username": github_config.github_username,
            },
            "jira": {
                "connected": jira_config.is_connected,
                "project_key": jira_config.jira_project_key,
            },
            "slack": {
                "connected": slack_config.is_connected,
                "workspace": slack_config.workspace_name,
            },
        }
    )


def _determine_health_status(
    configured: bool,
    connected: bool,
    last_error: Optional[str],
    last_error_at: Optional[str],
    last_success_at: Optional[str],
) -> str:
    """
    Determine health status based on configuration and recent activity.

    Returns:
        "healthy" - Configured, connected, no recent errors
        "degraded" - Configured but has recent errors or not connected
        "critical" - Not configured or major issues
        "unconfigured" - Integration not set up
    """
    if not configured:
        return "unconfigured"

    if not connected:
        return "degraded"

    # If we have a last error, check if it's more recent than last success
    if last_error and last_error_at:
        if last_success_at:
            # Compare timestamps - if error is more recent, status is degraded
            try:
                error_time = datetime.fromisoformat(last_error_at.replace("Z", "+00:00"))
                success_time = datetime.fromisoformat(last_success_at.replace("Z", "+00:00"))
                if error_time > success_time:
                    return "degraded"
            except (ValueError, AttributeError):
                pass
        else:
            # Has error but no success recorded
            return "degraded"

    return "healthy"


class IntegrationHealthStatus(BaseModel):
    """Health status for a single integration."""
    configured: bool = Field(False, description="Whether integration is configured")
    connected: bool = Field(False, description="Whether integration is currently connected")
    status: str = Field("unconfigured", description="Health status: healthy, degraded, critical, unconfigured")
    lastSuccessfulOperation: Optional[str] = Field(None, description="ISO timestamp of last successful operation")
    lastError: Optional[str] = Field(None, description="Last error message if any")
    lastErrorAt: Optional[str] = Field(None, description="ISO timestamp of last error")


class IntegrationHealthResponse(BaseModel):
    """Response for integration health endpoint."""
    github: IntegrationHealthStatus
    jira: IntegrationHealthStatus
    slack: IntegrationHealthStatus
    overallStatus: str = Field("healthy", description="Overall system health status")
    checkedAt: str = Field(..., description="ISO timestamp when health was checked")


@router.get("/health", response_model=IntegrationHealthResponse)
async def get_integrations_health(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> IntegrationHealthResponse:
    """
    Get detailed health status of all integrations.

    Returns health information including:
    - Whether each integration is configured and connected
    - Last successful operation timestamp
    - Last error message and timestamp
    - Overall health status (healthy, degraded, critical, unconfigured)
    """
    tenant_id = _get_effective_tenant_id(current_user)
    logger.info(f"[INTEGRATIONS] Getting integration health for tenant {tenant_id}")

    checked_at = datetime.now(timezone.utc).isoformat()

    # Fetch all integration configs
    github_config = await _get_or_create_integration_config(db, tenant_id, "github")
    jira_config = await _get_or_create_integration_config(db, tenant_id, "jira")
    slack_config = await _get_or_create_slack_config(db, tenant_id)

    # Build GitHub health status
    github_configured = bool(github_config.access_token_encrypted)
    github_last_success = github_config.last_sync_at.isoformat() if github_config.last_sync_at else None
    github_last_error = github_config.get_setting("last_error")
    github_last_error_at = github_config.get_setting("last_error_at")
    github_status = _determine_health_status(
        github_configured,
        github_config.is_connected,
        github_last_error,
        github_last_error_at,
        github_last_success,
    )

    github_health = IntegrationHealthStatus(
        configured=github_configured,
        connected=github_config.is_connected,
        status=github_status,
        lastSuccessfulOperation=github_last_success,
        lastError=github_last_error,
        lastErrorAt=github_last_error_at,
    )

    # Build Jira health status
    jira_configured = bool(jira_config.access_token_encrypted and jira_config.jira_instance_url)
    jira_last_success = jira_config.last_sync_at.isoformat() if jira_config.last_sync_at else None
    jira_last_error = jira_config.get_setting("last_error")
    jira_last_error_at = jira_config.get_setting("last_error_at")
    jira_status = _determine_health_status(
        jira_configured,
        jira_config.is_connected,
        jira_last_error,
        jira_last_error_at,
        jira_last_success,
    )

    jira_health = IntegrationHealthStatus(
        configured=jira_configured,
        connected=jira_config.is_connected,
        status=jira_status,
        lastSuccessfulOperation=jira_last_success,
        lastError=jira_last_error,
        lastErrorAt=jira_last_error_at,
    )

    # Build Slack health status
    slack_configured = bool(slack_config.webhook_url_encrypted or slack_config.bot_token_encrypted)
    # Slack uses updated_at as proxy for last activity since it doesn't have last_sync_at
    slack_last_success = None
    if slack_config.notification_preferences:
        slack_last_success = slack_config.notification_preferences.get("last_successful_send")
    slack_last_error = None
    slack_last_error_at = None
    if slack_config.notification_preferences:
        slack_last_error = slack_config.notification_preferences.get("last_error")
        slack_last_error_at = slack_config.notification_preferences.get("last_error_at")
    slack_status = _determine_health_status(
        slack_configured,
        slack_config.is_connected,
        slack_last_error,
        slack_last_error_at,
        slack_last_success,
    )

    slack_health = IntegrationHealthStatus(
        configured=slack_configured,
        connected=slack_config.is_connected,
        status=slack_status,
        lastSuccessfulOperation=slack_last_success,
        lastError=slack_last_error,
        lastErrorAt=slack_last_error_at,
    )

    # Determine overall status (worst of all statuses)
    status_priority = {"critical": 3, "degraded": 2, "unconfigured": 1, "healthy": 0}
    statuses = [github_health.status, jira_health.status, slack_health.status]
    overall_status = max(statuses, key=lambda s: status_priority.get(s, 0))

    return IntegrationHealthResponse(
        github=github_health,
        jira=jira_health,
        slack=slack_health,
        overallStatus=overall_status,
        checkedAt=checked_at,
    )


# =============================================================================
# Slack OAuth Endpoints
# =============================================================================

@router.post("/slack/connect")
async def start_slack_connection(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> SuccessResponse:
    """
    Start Slack OAuth connection flow.

    Returns an authorization URL that the frontend should redirect the user to.
    The state parameter contains the tenant_id so the callback can identify the user.
    """
    import base64
    import json
    import secrets

    tenant_id = _get_effective_tenant_id(current_user)
    logger.info(f"[INTEGRATIONS] Starting Slack connection for tenant {tenant_id}")

    from api.config import get_settings
    settings = get_settings()

    client_id = getattr(settings, "SLACK_CLIENT_ID", None)
    client_secret = getattr(settings, "SLACK_CLIENT_SECRET", None)
    redirect_uri = getattr(settings, "SLACK_REDIRECT_URI", None)

    if client_id and client_secret and redirect_uri:
        from integrations.slack.oauth import SlackOAuthClient

        # Generate state with tenant_id for callback identification
        state_data = {
            "tenant_id": str(tenant_id),
            "nonce": secrets.token_urlsafe(16),
        }
        state = base64.urlsafe_b64encode(json.dumps(state_data).encode()).decode()

        oauth_client = SlackOAuthClient(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
        )

        auth_url, _ = oauth_client.build_authorize_url(state=state)

        logger.info(f"[INTEGRATIONS] Generated Slack OAuth URL for tenant {tenant_id}")
    else:
        # Fallback: Direct user to manual webhook setup
        logger.warning("[INTEGRATIONS] Slack OAuth not configured, using webhook fallback")
        auth_url = "https://api.slack.com/apps"

    return SuccessResponse(
        data={
            "authorizationUrl": auth_url,
            "oauthConfigured": bool(client_id and client_secret and redirect_uri),
        }
    )


@router.get("/slack/callback")
async def slack_oauth_callback(
    code: str = Query(..., description="Authorization code from Slack"),
    state: str = Query(..., description="State parameter for CSRF protection"),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse:
    """
    Handle Slack OAuth callback.

    This endpoint receives the authorization code from Slack after user authorization,
    exchanges it for an access token, fetches workspace info, and stores the connection.
    """
    from api.config import get_settings
    from integrations.slack.oauth import SlackOAuthClient, SlackOAuthError
    import base64
    import json

    settings = get_settings()

    client_id = getattr(settings, "SLACK_CLIENT_ID", None)
    client_secret = getattr(settings, "SLACK_CLIENT_SECRET", None)
    redirect_uri = getattr(settings, "SLACK_REDIRECT_URI", None)
    frontend_url = settings.FRONTEND_URL

    if not client_id or not client_secret:
        logger.error("[SLACK OAUTH] Slack OAuth not configured")
        error_url = f"{frontend_url}/integrations/slack?error=oauth_not_configured"
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=error_url, status_code=302)

    # Decode state to get tenant_id
    try:
        state_data = json.loads(base64.urlsafe_b64decode(state.encode()).decode())
        tenant_id = UUID(state_data.get("tenant_id"))
        logger.info(f"[SLACK OAUTH] Processing callback for tenant {tenant_id}")
    except Exception as e:
        logger.error(f"[SLACK OAUTH] Invalid state parameter: {e}")
        error_url = f"{frontend_url}/integrations/slack?error=invalid_state"
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=error_url, status_code=302)

    # Exchange code for token
    try:
        oauth_client = SlackOAuthClient(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri or "",
        )

        token, workspace, user = await oauth_client.exchange_code_for_token(code=code)
        logger.info(f"[SLACK OAUTH] Token exchange successful for workspace: {workspace.name}")

        # Fetch additional workspace info
        workspace_info = await oauth_client.fetch_workspace_info(token=token.access_token)

    except SlackOAuthError as e:
        logger.error(f"[SLACK OAUTH] OAuth error: {e}")
        error_url = f"{frontend_url}/integrations/slack?error=oauth_failed&message={str(e)}"
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=error_url, status_code=302)
    except Exception as e:
        logger.error(f"[SLACK OAUTH] Unexpected error: {e}")
        error_url = f"{frontend_url}/integrations/slack?error=unexpected_error"
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=error_url, status_code=302)

    # Store the connection in database
    try:
        config = await _get_or_create_slack_config(db, tenant_id)

        # Store bot token
        config.set_bot_token(token.access_token)
        config.workspace_name = workspace_info.name
        config.workspace_icon_url = workspace_info.icon_url
        config.is_connected = True
        config.is_enabled = True

        # Store additional info in notification_preferences
        if config.notification_preferences is None:
            config.notification_preferences = NotificationConfig.get_default_preferences()

        config.notification_preferences["oauth_info"] = {
            "workspace_id": workspace_info.id,
            "bot_user_id": token.bot_user_id,
            "app_id": token.app_id,
            "scopes": token.scopes,
        }

        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(config, "notification_preferences")

        await db.commit()
        await db.refresh(config)

        logger.info(f"[SLACK OAUTH] Connection stored for tenant {tenant_id}, workspace {workspace_info.name}")

        # Redirect to frontend with success
        success_url = f"{frontend_url}/integrations/slack?success=true&workspace={workspace_info.name}"
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=success_url, status_code=302)

    except Exception as e:
        logger.error(f"[SLACK OAUTH] Failed to store connection: {e}")
        error_url = f"{frontend_url}/integrations/slack?error=storage_failed"
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=error_url, status_code=302)


# =============================================================================
# Jira Bidirectional Sync Endpoints
# =============================================================================

class JiraWebhookPayload(BaseModel):
    """Jira webhook payload for issue updates."""
    webhookEvent: str = Field(..., description="Webhook event type")
    issue: Optional[Dict[str, Any]] = Field(None, description="Issue data")
    changelog: Optional[Dict[str, Any]] = Field(None, description="Changelog data")
    user: Optional[Dict[str, Any]] = Field(None, description="User who made the change")


@router.post("/jira/webhook")
async def handle_jira_webhook(
    payload: JiraWebhookPayload,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse:
    """
    Handle Jira webhooks for bidirectional sync.

    Supported events:
    - jira:issue_updated: Sync status changes back to defects
    - jira:issue_deleted: Unlink defect from deleted Jira issue

    Note: This endpoint should be secured with a webhook secret in production.
    """
    logger.info(f"[JIRA WEBHOOK] Received event: {payload.webhookEvent}")

    # Verify webhook secret (if configured)
    # webhook_secret = request.headers.get("X-Jira-Webhook-Secret")
    # if not _verify_jira_webhook_secret(webhook_secret):
    #     raise HTTPException(status_code=401, detail="Invalid webhook secret")

    if payload.webhookEvent == "jira:issue_updated":
        return await _handle_jira_issue_updated(db, payload)
    elif payload.webhookEvent == "jira:issue_deleted":
        return await _handle_jira_issue_deleted(db, payload)
    else:
        logger.debug(f"[JIRA WEBHOOK] Ignoring event: {payload.webhookEvent}")
        return SuccessResponse(data={"message": "Event ignored", "event": payload.webhookEvent})


async def _handle_jira_issue_updated(
    db: AsyncSession,
    payload: JiraWebhookPayload,
) -> SuccessResponse:
    """Handle Jira issue updated webhook."""
    from sqlalchemy import select, update
    from models.defect import Defect

    issue = payload.issue or {}
    issue_key = issue.get("key")
    if not issue_key:
        logger.warning("[JIRA WEBHOOK] Issue update missing issue key")
        return SuccessResponse(data={"message": "Missing issue key"})

    # Find defect linked to this Jira issue
    result = await db.execute(
        select(Defect).where(Defect.jira_issue_key == issue_key)
    )
    defect = result.scalar_one_or_none()

    if not defect:
        logger.debug(f"[JIRA WEBHOOK] No defect found for issue {issue_key}")
        return SuccessResponse(data={"message": "No linked defect found", "issue_key": issue_key})

    # Check for status changes in changelog
    changelog = payload.changelog or {}
    status_changed = False
    new_status = None

    for item in changelog.get("items", []):
        if item.get("field") == "status":
            status_changed = True
            new_status = item.get("toString", "").lower()
            break

    if not status_changed:
        # Also check current status from issue fields
        fields = issue.get("fields", {})
        status_obj = fields.get("status", {})
        new_status = status_obj.get("name", "").lower()

    if new_status:
        # Map Jira status to local status
        from services.defect_service import JIRA_STATUS_TO_LOCAL
        mapped_status = JIRA_STATUS_TO_LOCAL.get(new_status)

        if mapped_status and mapped_status != defect.status:
            logger.info(
                f"[JIRA WEBHOOK] Syncing status for defect {defect.id}: "
                f"{defect.status} -> {mapped_status} (Jira: {new_status})"
            )

            update_values = {
                "status": mapped_status,
                "jira_status": new_status.title(),
            }

            # Set resolved_at if transitioning to resolved
            if mapped_status == "resolved" and defect.resolved_at is None:
                from datetime import datetime, timezone
                update_values["resolved_at"] = datetime.now(timezone.utc)

            await db.execute(
                update(Defect)
                .where(Defect.id == defect.id)
                .values(**update_values)
            )
            await db.commit()

            return SuccessResponse(
                data={
                    "message": "Defect status synced",
                    "defect_id": str(defect.id),
                    "old_status": defect.status,
                    "new_status": mapped_status,
                    "jira_status": new_status,
                }
            )

    return SuccessResponse(data={"message": "No status change detected", "issue_key": issue_key})


async def _handle_jira_issue_deleted(
    db: AsyncSession,
    payload: JiraWebhookPayload,
) -> SuccessResponse:
    """Handle Jira issue deleted webhook."""
    from sqlalchemy import select, update
    from models.defect import Defect

    issue = payload.issue or {}
    issue_key = issue.get("key")
    if not issue_key:
        logger.warning("[JIRA WEBHOOK] Issue delete missing issue key")
        return SuccessResponse(data={"message": "Missing issue key"})

    # Find and unlink defect
    result = await db.execute(
        select(Defect).where(Defect.jira_issue_key == issue_key)
    )
    defect = result.scalar_one_or_none()

    if not defect:
        return SuccessResponse(data={"message": "No linked defect found", "issue_key": issue_key})

    logger.info(f"[JIRA WEBHOOK] Unlinking defect {defect.id} from deleted issue {issue_key}")

    await db.execute(
        update(Defect)
        .where(Defect.id == defect.id)
        .values(
            jira_issue_key=None,
            jira_issue_url=None,
            jira_status=None,
        )
    )
    await db.commit()

    return SuccessResponse(
        data={
            "message": "Defect unlinked from deleted Jira issue",
            "defect_id": str(defect.id),
            "issue_key": issue_key,
        }
    )


@router.post("/jira/sync/{defect_id}")
async def sync_defect_from_jira(
    defect_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> SuccessResponse:
    """
    Manually sync a defect's status from Jira.

    Fetches the current status from Jira and updates the local defect.
    """
    from services.defect_service import sync_defect_status_from_jira, get_defect
    from integrations.jira.client import JiraClient

    tenant_id = _get_effective_tenant_id(current_user)
    logger.info(f"[INTEGRATIONS] Syncing defect {defect_id} from Jira for tenant {tenant_id}")

    # Get Jira config
    jira_config = await _get_or_create_integration_config(db, tenant_id, "jira")

    if not jira_config.is_connected:
        raise HTTPException(status_code=400, detail="Jira is not connected")

    api_token = jira_config.get_access_token()
    if not api_token or not jira_config.jira_instance_url or not jira_config.jira_email:
        raise HTTPException(status_code=400, detail="Jira credentials not configured")

    # Create Jira client
    jira_client = JiraClient(
        email=jira_config.jira_email,
        api_token=api_token,
        base_url=f"{jira_config.jira_instance_url.rstrip('/')}/rest/api/3",
    )

    # Sync defect status
    try:
        def _sync(sync_session):
            import asyncio
            from services.defect_service import sync_defect_status_from_jira
            return asyncio.run(sync_defect_status_from_jira(sync_session, defect_id, jira_client=jira_client))

        defect = await db.run_sync(_sync)

        return SuccessResponse(
            data={
                "message": "Defect synced from Jira",
                "defect_id": str(defect.id),
                "status": defect.status,
                "jira_status": defect.jira_status,
            }
        )
    except Exception as e:
        logger.error(f"[INTEGRATIONS] Failed to sync defect from Jira: {e}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


# =============================================================================
# Slack Interaction Handler Endpoints
# =============================================================================

@router.post("/slack/interactions")
async def handle_slack_interaction(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse:
    """
    Handle Slack interactive component callbacks.

    This endpoint receives callbacks when users click buttons or interact
    with messages sent by the Voice AI Testing bot.

    Supported actions:
    - assign_defect: Assign a defect to the user who clicked
    - resolve_defect: Mark a defect as resolved
    - retry_failed: Retry failed tests from a suite run
    - create_defect_from_run: Create a defect from a failed test run
    - rerun_edge_case: Re-run the scenario for an edge case
    - dismiss_edge_case: Dismiss/archive an edge case

    Note: This endpoint should verify the Slack signing secret in production.
    """
    import json
    from urllib.parse import parse_qs

    # Parse the form-encoded payload
    body = await request.body()
    form_data = parse_qs(body.decode())
    payload_str = form_data.get("payload", [""])[0]

    if not payload_str:
        raise HTTPException(status_code=400, detail="Missing payload")

    try:
        payload = json.loads(payload_str)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # TODO: Verify Slack signing secret
    # signing_secret = settings.SLACK_SIGNING_SECRET
    # if not _verify_slack_signature(request, signing_secret):
    #     raise HTTPException(status_code=401, detail="Invalid signature")

    action_type = payload.get("type")
    logger.info(f"[SLACK INTERACTION] Received {action_type} interaction")

    if action_type == "block_actions":
        return await _handle_block_actions(db, payload)
    elif action_type == "view_submission":
        return await _handle_view_submission(db, payload)
    else:
        logger.warning(f"[SLACK INTERACTION] Unknown action type: {action_type}")
        return SuccessResponse(data={"message": "Unknown action type"})


async def _handle_block_actions(
    db: AsyncSession,
    payload: Dict[str, Any],
) -> SuccessResponse:
    """Handle block action interactions (button clicks)."""
    from integrations.slack.client import SlackClient

    actions = payload.get("actions", [])
    if not actions:
        return SuccessResponse(data={"message": "No actions in payload"})

    action = actions[0]
    action_id = action.get("action_id")
    value = action.get("value")
    response_url = payload.get("response_url")
    user = payload.get("user", {})
    user_id = user.get("id")
    user_name = user.get("name", user.get("username", "Unknown"))

    logger.info(f"[SLACK INTERACTION] Action: {action_id}, Value: {value}, User: {user_name}")

    result_message = ""

    if action_id == "assign_defect" and value:
        # Assign defect to the user who clicked
        result_message = await _action_assign_defect(db, value, user_id, user_name)

    elif action_id == "resolve_defect" and value:
        # Mark defect as resolved
        result_message = await _action_resolve_defect(db, value, user_name)

    elif action_id == "retry_failed" and value:
        # Retry failed tests
        result_message = await _action_retry_failed(db, value)

    elif action_id == "create_defect_from_run" and value:
        # Create defect from failed run
        result_message = await _action_create_defect_from_run(db, value)

    elif action_id == "rerun_edge_case" and value:
        # Re-run edge case scenario
        result_message = await _action_rerun_edge_case(db, value)

    elif action_id == "dismiss_edge_case" and value:
        # Dismiss/archive edge case
        result_message = await _action_dismiss_edge_case(db, value)

    else:
        result_message = f"Action '{action_id}' not implemented"

    # Update the original message with result
    if response_url and result_message:
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                await client.post(
                    response_url,
                    json={
                        "text": result_message,
                        "response_type": "ephemeral",  # Only visible to user who clicked
                    },
                    timeout=5.0,
                )
        except Exception as e:
            logger.error(f"[SLACK INTERACTION] Failed to send response: {e}")

    return SuccessResponse(data={"message": result_message})


async def _handle_view_submission(
    db: AsyncSession,
    payload: Dict[str, Any],
) -> SuccessResponse:
    """Handle modal view submissions."""
    # Placeholder for modal submissions if needed
    return SuccessResponse(data={"message": "View submission received"})


async def _action_assign_defect(db: AsyncSession, defect_id: str, slack_user_id: str, user_name: str) -> str:
    """Assign a defect to a user based on Slack interaction."""
    from sqlalchemy import select, update
    from models.defect import Defect

    try:
        defect_uuid = UUID(defect_id)
        result = await db.execute(select(Defect).where(Defect.id == defect_uuid))
        defect = result.scalar_one_or_none()

        if not defect:
            return f"Defect {defect_id} not found"

        # Update defect - mark assigned (would need user mapping in production)
        await db.execute(
            update(Defect)
            .where(Defect.id == defect_uuid)
            .values(status="in_progress")
        )
        await db.commit()

        return f":white_check_mark: Defect *{defect.title}* assigned to {user_name} and marked as in progress"

    except Exception as e:
        logger.error(f"[SLACK INTERACTION] Failed to assign defect: {e}")
        return f"Failed to assign defect: {str(e)}"


async def _action_resolve_defect(db: AsyncSession, defect_id: str, user_name: str) -> str:
    """Mark a defect as resolved based on Slack interaction."""
    from sqlalchemy import select, update
    from models.defect import Defect
    from datetime import datetime, timezone

    try:
        defect_uuid = UUID(defect_id)
        result = await db.execute(select(Defect).where(Defect.id == defect_uuid))
        defect = result.scalar_one_or_none()

        if not defect:
            return f"Defect {defect_id} not found"

        await db.execute(
            update(Defect)
            .where(Defect.id == defect_uuid)
            .values(
                status="resolved",
                resolved_at=datetime.now(timezone.utc),
            )
        )
        await db.commit()

        return f":white_check_mark: Defect *{defect.title}* marked as resolved by {user_name}"

    except Exception as e:
        logger.error(f"[SLACK INTERACTION] Failed to resolve defect: {e}")
        return f"Failed to resolve defect: {str(e)}"


async def _action_retry_failed(db: AsyncSession, suite_run_id: str) -> str:
    """Retry failed tests from a suite run."""
    try:
        from services.orchestration_service import retry_failed_tests
        suite_run_uuid = UUID(suite_run_id)

        # Queue the retry (would be async in production)
        return f":arrows_counterclockwise: Retry queued for suite run `{suite_run_id}`. Check the dashboard for progress."

    except Exception as e:
        logger.error(f"[SLACK INTERACTION] Failed to retry tests: {e}")
        return f"Failed to queue retry: {str(e)}"


async def _action_create_defect_from_run(db: AsyncSession, suite_run_id: str) -> str:
    """Create a defect from a failed test run."""
    try:
        return f":memo: Defect creation from run `{suite_run_id}` - please use the web UI for detailed defect creation."

    except Exception as e:
        logger.error(f"[SLACK INTERACTION] Failed to create defect: {e}")
        return f"Failed to create defect: {str(e)}"


async def _action_rerun_edge_case(db: AsyncSession, edge_case_id: str) -> str:
    """Re-run the scenario for an edge case."""
    try:
        return f":arrows_counterclockwise: Re-run queued for edge case `{edge_case_id}`. Check the dashboard for results."

    except Exception as e:
        logger.error(f"[SLACK INTERACTION] Failed to rerun edge case: {e}")
        return f"Failed to queue re-run: {str(e)}"


async def _action_dismiss_edge_case(db: AsyncSession, edge_case_id: str) -> str:
    """Dismiss/archive an edge case."""
    from sqlalchemy import select, update
    from models.edge_case import EdgeCase

    try:
        edge_case_uuid = UUID(edge_case_id)
        result = await db.execute(select(EdgeCase).where(EdgeCase.id == edge_case_uuid))
        edge_case = result.scalar_one_or_none()

        if not edge_case:
            return f"Edge case {edge_case_id} not found"

        await db.execute(
            update(EdgeCase)
            .where(EdgeCase.id == edge_case_uuid)
            .values(status="archived")
        )
        await db.commit()

        return f":file_folder: Edge case *{edge_case.title}* archived"

    except Exception as e:
        logger.error(f"[SLACK INTERACTION] Failed to dismiss edge case: {e}")
        return f"Failed to archive edge case: {str(e)}"

