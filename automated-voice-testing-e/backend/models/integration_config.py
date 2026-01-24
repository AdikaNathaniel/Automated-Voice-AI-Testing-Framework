"""
IntegrationConfig SQLAlchemy model for external service integrations.

Stores per-tenant configuration for GitHub, Jira, and other service integrations,
with encrypted storage for sensitive credentials like API tokens and secrets.

Security: API tokens, access tokens, and secrets are encrypted using Fernet symmetric encryption.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from sqlalchemy import Column, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import JSON

from models.base import Base, BaseModel, GUID
from models.llm_provider_config import encrypt_value, decrypt_value

logger = logging.getLogger(__name__)

# Use JSONB for PostgreSQL, JSON for SQLite (testing)
JSONB_TYPE = JSONB().with_variant(JSON(), "sqlite")


class IntegrationConfig(Base, BaseModel):
    """
    IntegrationConfig model for storing external service integration settings.

    Stores encrypted credentials and configuration for various integrations
    (GitHub, Jira, etc.), allowing per-tenant configuration.

    Attributes:
        id (UUID): Unique identifier (inherited from BaseModel)
        tenant_id (UUID): Tenant ID for multi-tenant isolation
        integration_type (str): Integration type (github, jira, etc.)
        display_name (str): Human-readable display name
        is_enabled (bool): Whether integration is enabled
        is_connected (bool): Whether the integration is connected/authenticated
        access_token_encrypted (str): Encrypted access/API token
        secret_encrypted (str): Encrypted webhook secret or signing secret
        settings (dict): Additional integration-specific settings as JSONB
        last_sync_at (datetime): Last successful sync/connection timestamp
    """

    __tablename__ = 'integration_configs'

    tenant_id = Column(
        GUID(),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=True,
        index=True,
        comment="Tenant ID for multi-tenant isolation (null = global)"
    )

    integration_type = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Integration type (github, jira, etc.)"
    )

    display_name = Column(
        String(255),
        nullable=True,
        comment="Human-readable display name"
    )

    is_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether integration is enabled"
    )

    is_connected = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether the integration is successfully connected"
    )

    # Encrypted credentials
    access_token_encrypted = Column(
        Text,
        nullable=True,
        comment="Encrypted access token or API token"
    )

    secret_encrypted = Column(
        Text,
        nullable=True,
        comment="Encrypted webhook secret or signing secret"
    )

    # Integration-specific settings stored as JSONB
    settings = Column(
        JSONB_TYPE,
        nullable=True,
        default=dict,
        comment="Integration-specific settings (username, repos, project_key, etc.)"
    )

    last_sync_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last successful sync timestamp"
    )

    def __repr__(self) -> str:
        """String representation of IntegrationConfig."""
        return (
            f"<IntegrationConfig("
            f"type='{self.integration_type}', "
            f"tenant_id='{self.tenant_id}', "
            f"connected={self.is_connected})>"
        )

    # ------------------------------------------------------------------
    # Token/Secret Management (encrypted)
    # ------------------------------------------------------------------

    def set_access_token(self, token: str) -> None:
        """Set and encrypt the access token."""
        self.access_token_encrypted = encrypt_value(token) if token else None

    def get_access_token(self) -> Optional[str]:
        """Get the decrypted access token."""
        if not self.access_token_encrypted:
            return None
        return decrypt_value(self.access_token_encrypted)

    def set_secret(self, secret: str) -> None:
        """Set and encrypt the webhook/signing secret."""
        self.secret_encrypted = encrypt_value(secret) if secret else None

    def get_secret(self) -> Optional[str]:
        """Get the decrypted webhook/signing secret."""
        if not self.secret_encrypted:
            return None
        return decrypt_value(self.secret_encrypted)

    # ------------------------------------------------------------------
    # Settings Helpers
    # ------------------------------------------------------------------

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific setting value."""
        if not self.settings:
            return default
        return self.settings.get(key, default)

    def set_setting(self, key: str, value: Any) -> None:
        """Set a specific setting value.

        Note:
            After using this method, you must call flag_modified() from the
            service layer to ensure SQLAlchemy detects the JSONB change:

            from sqlalchemy.orm.attributes import flag_modified
            config.set_setting("key", "value")
            flag_modified(config, "settings")
        """
        if self.settings is None:
            self.settings = {}
        # Create new dict to help SQLAlchemy detect changes
        new_settings = dict(self.settings)
        new_settings[key] = value
        self.settings = new_settings

    def update_settings(self, updates: Dict[str, Any]) -> None:
        """Update multiple settings at once.

        Note:
            After using this method, you must call flag_modified() from the
            service layer to ensure SQLAlchemy detects the JSONB change:

            from sqlalchemy.orm.attributes import flag_modified
            config.update_settings({"key": "value"})
            flag_modified(config, "settings")
        """
        if self.settings is None:
            self.settings = {}
        # Create new dict to help SQLAlchemy detect changes
        new_settings = dict(self.settings)
        new_settings.update(updates)
        self.settings = new_settings

    # ------------------------------------------------------------------
    # GitHub-specific Helpers
    # ------------------------------------------------------------------

    @property
    def github_username(self) -> Optional[str]:
        """Get GitHub username from settings."""
        return self.get_setting("username")

    @github_username.setter
    def github_username(self, value: str) -> None:
        """Set GitHub username in settings."""
        self.set_setting("username", value)

    @property
    def github_repositories(self) -> List[str]:
        """Get list of GitHub repositories from settings."""
        return self.get_setting("repositories", [])

    @github_repositories.setter
    def github_repositories(self, value: List[str]) -> None:
        """Set GitHub repositories in settings."""
        self.set_setting("repositories", value)

    @property
    def github_auto_create_issues(self) -> bool:
        """Get auto-create issues flag from settings."""
        return self.get_setting("auto_create_issues", False)

    @github_auto_create_issues.setter
    def github_auto_create_issues(self, value: bool) -> None:
        """Set auto-create issues flag in settings."""
        self.set_setting("auto_create_issues", value)

    # ------------------------------------------------------------------
    # Jira-specific Helpers
    # ------------------------------------------------------------------

    @property
    def jira_instance_url(self) -> Optional[str]:
        """Get Jira instance URL from settings."""
        return self.get_setting("instance_url")

    @jira_instance_url.setter
    def jira_instance_url(self, value: str) -> None:
        """Set Jira instance URL in settings."""
        self.set_setting("instance_url", value)

    @property
    def jira_email(self) -> Optional[str]:
        """Get Jira account email from settings."""
        return self.get_setting("email")

    @jira_email.setter
    def jira_email(self, value: str) -> None:
        """Set Jira account email in settings."""
        self.set_setting("email", value)

    @property
    def jira_project_key(self) -> Optional[str]:
        """Get Jira default project key from settings."""
        return self.get_setting("project_key")

    @jira_project_key.setter
    def jira_project_key(self, value: str) -> None:
        """Set Jira default project key in settings."""
        self.set_setting("project_key", value)

    @property
    def jira_issue_type(self) -> str:
        """Get Jira default issue type from settings."""
        return self.get_setting("issue_type", "Bug")

    @jira_issue_type.setter
    def jira_issue_type(self, value: str) -> None:
        """Set Jira default issue type in settings."""
        self.set_setting("issue_type", value)

    @property
    def jira_auto_create_tickets(self) -> bool:
        """Get auto-create tickets flag from settings."""
        return self.get_setting("auto_create_tickets", False)

    @jira_auto_create_tickets.setter
    def jira_auto_create_tickets(self, value: bool) -> None:
        """Set auto-create tickets flag in settings."""
        self.set_setting("auto_create_tickets", value)

    # ------------------------------------------------------------------
    # Sync Tracking
    # ------------------------------------------------------------------

    def mark_synced(self) -> None:
        """Mark the integration as synced now."""
        self.last_sync_at = datetime.now(timezone.utc)

    def to_github_response(self) -> Dict[str, Any]:
        """Convert to GitHub API response format."""
        return {
            "connected": self.is_connected,
            "username": self.github_username,
            "last_sync": self.last_sync_at.isoformat() if self.last_sync_at else None,
            "repositories": self.github_repositories,
            "auto_create_issues": self.github_auto_create_issues,
        }

    def to_jira_response(self) -> Dict[str, Any]:
        """Convert to Jira API response format."""
        return {
            "connected": self.is_connected,
            "instance_url": self.jira_instance_url,
            "project_key": self.jira_project_key,
            "issue_type": self.jira_issue_type,
            "auto_create_tickets": self.jira_auto_create_tickets,
        }
