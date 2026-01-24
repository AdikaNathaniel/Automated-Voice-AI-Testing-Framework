"""
LLMProviderConfig SQLAlchemy model for LLM API key storage.

This model stores encrypted API keys for different LLM providers,
allowing admins to configure keys from the UI instead of environment variables.

Security: API keys are encrypted using Fernet symmetric encryption.
The encryption key must be set via ENCRYPTION_KEY environment variable.
"""

import os
import logging
from typing import Any, Dict, Optional

from sqlalchemy import Column, String, Text, Boolean, Float, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects import postgresql
from sqlalchemy import JSON
from sqlalchemy.orm import relationship

from models.base import Base, BaseModel, GUID

logger = logging.getLogger(__name__)


# Use JSONB for PostgreSQL, JSON for SQLite (testing)
JSONB_TYPE = JSONB().with_variant(JSON(), "sqlite")

def get_cipher():
    """
    Get the Fernet cipher for encryption/decryption.

    Returns:
        Fernet cipher instance or None if encryption key not configured

    Raises:
        ValueError: If ENCRYPTION_KEY is set but invalid
    """
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        logger.warning(
            "cryptography package not installed. "
            "Install with: pip install cryptography"
        )
        return None

    encryption_key = os.getenv('ENCRYPTION_KEY')
    if not encryption_key:
        logger.warning(
            "ENCRYPTION_KEY not set. API keys will not be encrypted. "
            "Generate a key with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )
        return None

    try:
        return Fernet(encryption_key.encode())
    except Exception as e:
        raise ValueError(f"Invalid ENCRYPTION_KEY: {e}")


def encrypt_value(value: str) -> str:
    """
    Encrypt a string value.

    Args:
        value: Plain text value to encrypt

    Returns:
        Encrypted value as base64 string, or original if encryption unavailable
    """
    if not value:
        return value

    cipher = get_cipher()
    if cipher is None:
        # Return with marker so we know it's not encrypted
        return f"UNENCRYPTED:{value}"

    encrypted = cipher.encrypt(value.encode())
    return encrypted.decode()


def decrypt_value(value: str) -> str:
    """
    Decrypt an encrypted string value.

    Args:
        value: Encrypted value (base64 string)

    Returns:
        Decrypted plain text value
    """
    if not value:
        return value

    # Handle unencrypted values (for development/migration)
    if value.startswith("UNENCRYPTED:"):
        return value[12:]  # Remove prefix

    cipher = get_cipher()
    if cipher is None:
        logger.error("Cannot decrypt: ENCRYPTION_KEY not configured")
        return ""

    try:
        decrypted = cipher.decrypt(value.encode())
        return decrypted.decode()
    except Exception as e:
        logger.error(f"Failed to decrypt value: {e}")
        return ""


class LLMProviderConfig(Base, BaseModel):
    """
    LLMProviderConfig model for storing LLM provider API keys.

    Stores encrypted API keys and configuration for LLM providers,
    allowing admins to manage keys from the UI.

    Attributes:
        id (UUID): Unique identifier (inherited from BaseModel)
        tenant_id (UUID): Optional tenant ID for multi-tenant isolation
        provider (str): LLM provider name (openai, anthropic, google)
        display_name (str): Human-readable display name
        api_key_encrypted (str): Encrypted API key
        default_model (str): Default model for this provider
        is_active (bool): Whether this config is active
        is_default (bool): Whether this is the default config for the provider
        temperature (float): Default temperature for API calls
        max_tokens (int): Default max tokens for API calls
        timeout_seconds (int): Request timeout in seconds
        config (dict): Additional configuration as JSONB
    """

    __tablename__ = 'llm_provider_configs'

    tenant_id = Column(
        GUID(),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=True,
        index=True,
        comment="Tenant ID for multi-tenant isolation (null = global)"
    )

    provider = Column(
        String(50),
        nullable=False,
        index=True,
        comment="LLM provider name (openai, anthropic, google)"
    )

    display_name = Column(
        String(255),
        nullable=False,
        comment="Human-readable display name"
    )

    api_key_encrypted = Column(
        Text,
        nullable=False,
        comment="Encrypted API key"
    )

    default_model = Column(
        String(100),
        nullable=True,
        comment="Default model name (gpt-4o, claude-sonnet-4-5, etc.)"
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Whether this configuration is active"
    )

    is_default = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether this is the default config for the provider"
    )

    temperature = Column(
        Float,
        nullable=False,
        default=0.0,
        comment="Default temperature for API calls (0.0 = deterministic)"
    )

    max_tokens = Column(
        Float,
        nullable=False,
        default=1024,
        comment="Default max tokens for API calls"
    )

    timeout_seconds = Column(
        Float,
        nullable=False,
        default=30,
        comment="Request timeout in seconds"
    )

    config = Column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        comment="Additional configuration (headers, base_url, etc.)"
    )

    def __repr__(self) -> str:
        """String representation of LLMProviderConfig."""
        return (
            f"<LLMProviderConfig("
            f"provider='{self.provider}', "
            f"display_name='{self.display_name}')>"
        )

    def set_api_key(self, api_key: str) -> None:
        """
        Set and encrypt the API key.

        Args:
            api_key: Plain text API key to store
        """
        self.api_key_encrypted = encrypt_value(api_key)

    def get_api_key(self) -> str:
        """
        Get the decrypted API key.

        Returns:
            Decrypted API key string
        """
        return decrypt_value(self.api_key_encrypted)

    def to_dict(self, include_key: bool = False) -> Dict[str, Any]:
        """
        Convert config to dictionary.

        Args:
            include_key: If True, include masked API key preview

        Returns:
            Dictionary representation of the config
        """
        result = {
            'id': str(self.id),
            'tenant_id': str(self.tenant_id) if self.tenant_id else None,
            'provider': self.provider,
            'display_name': self.display_name,
            'default_model': self.default_model,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'timeout_seconds': self.timeout_seconds,
            'config': self.config or {},
            'created_at': (
                self.created_at.isoformat() if self.created_at else None
            ),
            'updated_at': (
                self.updated_at.isoformat() if self.updated_at else None
            ),
        }

        if include_key:
            # Show masked preview of API key
            api_key = self.get_api_key()
            if api_key:
                # Show first 4 and last 4 characters
                if len(api_key) > 8:
                    result['api_key_preview'] = (
                        f"{api_key[:4]}...{api_key[-4:]}"
                    )
                else:
                    result['api_key_preview'] = "****"
            else:
                result['api_key_preview'] = None

        return result

    @classmethod
    def get_default_models(cls) -> Dict[str, str]:
        """
        Get default model names for each provider.

        Returns:
            Dictionary mapping provider to default model
        """
        return {
            'openai': 'gpt-4o',
            'anthropic': 'claude-sonnet-4-5-20250929',
            'google': 'gemini-1.5-pro',
        }

    @classmethod
    def get_supported_providers(cls) -> list[str]:
        """
        Get list of supported LLM providers.

        Returns:
            List of supported provider names
        """
        return ['openai', 'anthropic', 'google']
