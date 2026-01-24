"""
NotificationConfig SQLAlchemy model for tenant notification settings.

Stores per-tenant configuration for Slack and other notification channels,
allowing admins to configure notification preferences from the UI.

Security: Webhook URLs and tokens are encrypted using Fernet symmetric encryption.
"""

import logging
from typing import Any, Dict, Optional

from sqlalchemy import Column, String, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects import postgresql
from sqlalchemy import JSON

from models.base import Base, BaseModel, GUID
from models.llm_provider_config import encrypt_value, decrypt_value

logger = logging.getLogger(__name__)

# Use JSONB for PostgreSQL, JSON for SQLite (testing)
JSONB_TYPE = JSONB().with_variant(JSON(), "sqlite")


class NotificationConfig(Base, BaseModel):
    """
    NotificationConfig model for storing tenant notification settings.

    Stores encrypted webhook URLs and notification preferences for various
    channels (Slack, etc.), allowing per-tenant configuration.

    Attributes:
        id (UUID): Unique identifier (inherited from BaseModel)
        tenant_id (UUID): Tenant ID for multi-tenant isolation
        channel_type (str): Notification channel type (slack, email, webhook)
        display_name (str): Human-readable display name
        webhook_url_encrypted (str): Encrypted webhook URL
        is_enabled (bool): Whether notifications are enabled globally
        is_connected (bool): Whether the integration is connected
        workspace_name (str): For Slack - workspace name
        default_channel (str): Default notification channel
        notification_preferences (dict): Per-notification-type settings as JSONB
    """

    __tablename__ = 'notification_configs'

    tenant_id = Column(
        GUID(),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=True,
        index=True,
        comment="Tenant ID for multi-tenant isolation (null = global)"
    )

    channel_type = Column(
        String(50),
        nullable=False,
        default="slack",
        index=True,
        comment="Notification channel type (slack, email, webhook)"
    )

    display_name = Column(
        String(255),
        nullable=True,
        comment="Human-readable display name"
    )

    webhook_url_encrypted = Column(
        Text,
        nullable=True,
        comment="Encrypted webhook URL"
    )

    bot_token_encrypted = Column(
        Text,
        nullable=True,
        comment="Encrypted bot token (for Slack app integrations)"
    )

    signing_secret_encrypted = Column(
        Text,
        nullable=True,
        comment="Encrypted signing secret (for Slack app integrations)"
    )

    is_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether notifications are enabled globally"
    )

    is_connected = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether the integration is successfully connected"
    )

    workspace_name = Column(
        String(255),
        nullable=True,
        comment="For Slack - connected workspace name"
    )

    workspace_icon_url = Column(
        Text,
        nullable=True,
        comment="For Slack - workspace icon URL"
    )

    default_channel = Column(
        String(255),
        nullable=True,
        comment="Default notification channel (e.g., #alerts)"
    )

    notification_preferences = Column(
        JSONB_TYPE,
        nullable=True,
        default=dict,
        comment="Per-notification-type settings (suiteRun, criticalDefect, etc.)"
    )

    def __repr__(self) -> str:
        """String representation of NotificationConfig."""
        return (
            f"<NotificationConfig("
            f"channel_type='{self.channel_type}', "
            f"tenant_id='{self.tenant_id}')>"
        )

    def set_webhook_url(self, url: str) -> None:
        """Set and encrypt the webhook URL."""
        self.webhook_url_encrypted = encrypt_value(url) if url else None

    def get_webhook_url(self) -> Optional[str]:
        """Get the decrypted webhook URL."""
        if not self.webhook_url_encrypted:
            return None
        return decrypt_value(self.webhook_url_encrypted)

    def set_bot_token(self, token: str) -> None:
        """Set and encrypt the bot token."""
        self.bot_token_encrypted = encrypt_value(token) if token else None

    def get_bot_token(self) -> Optional[str]:
        """Get the decrypted bot token."""
        if not self.bot_token_encrypted:
            return None
        return decrypt_value(self.bot_token_encrypted)

    def set_signing_secret(self, secret: str) -> None:
        """Set and encrypt the signing secret."""
        self.signing_secret_encrypted = encrypt_value(secret) if secret else None

    def get_signing_secret(self) -> Optional[str]:
        """Get the decrypted signing secret."""
        if not self.signing_secret_encrypted:
            return None
        return decrypt_value(self.signing_secret_encrypted)

    def get_preference(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get notification preference for a specific type.

        Args:
            key: Preference key (suiteRun, criticalDefect, systemAlert, edgeCase)

        Returns:
            Preference dict with 'enabled' and 'channel' keys, or None
        """
        if not self.notification_preferences:
            return None
        return self.notification_preferences.get(key)

    def is_notification_enabled(self, key: str) -> bool:
        """
        Check if a specific notification type is enabled.

        Args:
            key: Preference key (suiteRun, criticalDefect, systemAlert, edgeCase)

        Returns:
            True if enabled, False otherwise
        """
        if not self.is_enabled:
            return False
        pref = self.get_preference(key)
        if pref is None:
            return True  # Default to enabled if not explicitly set
        return pref.get("enabled", True)

    def get_notification_channel(self, key: str) -> Optional[str]:
        """
        Get the channel for a specific notification type.

        Args:
            key: Preference key (suiteRun, criticalDefect, systemAlert, edgeCase)

        Returns:
            Channel name or None (falls back to default_channel)
        """
        pref = self.get_preference(key)
        if pref and pref.get("channel"):
            return pref["channel"]
        return self.default_channel

    def to_api_response(self) -> Dict[str, Any]:
        """
        Convert config to API response format.

        Returns:
            Dictionary matching SlackIntegrationConfig interface
        """
        # Default preferences structure
        default_pref = {"enabled": True, "channel": ""}
        prefs = self.notification_preferences or {}

        return {
            "isConnected": self.is_connected,
            "workspaceName": self.workspace_name,
            "workspaceIconUrl": self.workspace_icon_url,
            "connectUrl": "",  # OAuth URL would be generated dynamically
            "defaultChannel": self.default_channel or "",
            "notificationPreferences": {
                "suiteRun": prefs.get("suiteRun", default_pref),
                "criticalDefect": prefs.get("criticalDefect", default_pref),
                "systemAlert": prefs.get("systemAlert", default_pref),
                "edgeCase": prefs.get("edgeCase", default_pref),
            },
            "botTokenSet": bool(self.bot_token_encrypted),
            "signingSecretSet": bool(self.signing_secret_encrypted),
        }

    @classmethod
    def get_default_preferences(cls) -> Dict[str, Dict[str, Any]]:
        """Get default notification preferences structure."""
        return {
            "suiteRun": {"enabled": True, "channel": ""},
            "criticalDefect": {"enabled": True, "channel": ""},
            "systemAlert": {"enabled": True, "channel": ""},
            "edgeCase": {"enabled": True, "channel": ""},
        }
