"""
LLM Provider Configuration Service.

This service manages LLM provider configurations including encrypted API keys,
allowing admins to configure providers from the UI instead of environment variables.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, and_, update as sa_update
from sqlalchemy.orm import Session

from models.llm_provider_config import LLMProviderConfig

logger = logging.getLogger(__name__)


class LLMProviderConfigService:
    """Service for managing LLM provider configurations."""

    def __init__(self, db: Session):
        """
        Initialize the service.

        Args:
            db: SQLAlchemy session
        """
        self.db = db

    def list_configs(
        self,
        tenant_id: Optional[UUID] = None,
        provider: Optional[str] = None,
        is_active: Optional[bool] = None,
        include_global: bool = True,
    ) -> List[LLMProviderConfig]:
        """
        List LLM provider configurations.

        Args:
            tenant_id: Filter by tenant (None = get global configs)
            provider: Filter by provider name
            is_active: Filter by active status
            include_global: Include global configs when tenant_id is set

        Returns:
            List of LLMProviderConfig instances
        """
        conditions = []

        if tenant_id:
            if include_global:
                conditions.append(
                    (LLMProviderConfig.tenant_id == tenant_id) |
                    (LLMProviderConfig.tenant_id.is_(None))
                )
            else:
                conditions.append(LLMProviderConfig.tenant_id == tenant_id)
        else:
            conditions.append(LLMProviderConfig.tenant_id.is_(None))

        if provider:
            conditions.append(LLMProviderConfig.provider == provider.lower())

        if is_active is not None:
            conditions.append(LLMProviderConfig.is_active == is_active)

        stmt = (
            select(LLMProviderConfig)
            .where(and_(*conditions))
            .order_by(LLMProviderConfig.provider, LLMProviderConfig.created_at)
        )

        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def get_config(
        self,
        config_id: UUID,
        tenant_id: Optional[UUID] = None,
    ) -> Optional[LLMProviderConfig]:
        """
        Get a specific configuration by ID.

        Args:
            config_id: Configuration ID
            tenant_id: Optional tenant filter for access control

        Returns:
            LLMProviderConfig or None if not found
        """
        conditions = [LLMProviderConfig.id == config_id]

        if tenant_id:
            # Allow access to own tenant's configs and global configs
            conditions.append(
                (LLMProviderConfig.tenant_id == tenant_id) |
                (LLMProviderConfig.tenant_id.is_(None))
            )

        stmt = select(LLMProviderConfig).where(and_(*conditions))
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def get_default_config(
        self,
        provider: str,
        tenant_id: Optional[UUID] = None,
    ) -> Optional[LLMProviderConfig]:
        """
        Get the default configuration for a provider.

        Args:
            provider: Provider name
            tenant_id: Optional tenant ID (checks tenant then global)

        Returns:
            Default LLMProviderConfig or None
        """
        provider = provider.lower()

        # First try tenant-specific default
        if tenant_id:
            stmt = (
                select(LLMProviderConfig)
                .where(and_(
                    LLMProviderConfig.tenant_id == tenant_id,
                    LLMProviderConfig.provider == provider,
                    LLMProviderConfig.is_default == True,
                    LLMProviderConfig.is_active == True,
                ))
            )
            result = self.db.execute(stmt)
            config = result.scalar_one_or_none()
            if config:
                return config

        # Fall back to global default
        stmt = (
            select(LLMProviderConfig)
            .where(and_(
                LLMProviderConfig.tenant_id.is_(None),
                LLMProviderConfig.provider == provider,
                LLMProviderConfig.is_default == True,
                LLMProviderConfig.is_active == True,
            ))
        )
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def get_active_config(
        self,
        provider: str,
        tenant_id: Optional[UUID] = None,
    ) -> Optional[LLMProviderConfig]:
        """
        Get any active configuration for a provider.

        First tries default, then any active config.

        Args:
            provider: Provider name
            tenant_id: Optional tenant ID

        Returns:
            Active LLMProviderConfig or None
        """
        # Try default first
        config = self.get_default_config(provider, tenant_id)
        if config:
            return config

        provider = provider.lower()

        # Try tenant-specific active
        if tenant_id:
            stmt = (
                select(LLMProviderConfig)
                .where(and_(
                    LLMProviderConfig.tenant_id == tenant_id,
                    LLMProviderConfig.provider == provider,
                    LLMProviderConfig.is_active == True,
                ))
                .limit(1)
            )
            result = self.db.execute(stmt)
            config = result.scalar_one_or_none()
            if config:
                return config

        # Fall back to global active
        stmt = (
            select(LLMProviderConfig)
            .where(and_(
                LLMProviderConfig.tenant_id.is_(None),
                LLMProviderConfig.provider == provider,
                LLMProviderConfig.is_active == True,
            ))
            .limit(1)
        )
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def create_config(
        self,
        provider: str,
        display_name: str,
        api_key: str,
        tenant_id: Optional[UUID] = None,
        default_model: Optional[str] = None,
        is_active: bool = True,
        is_default: bool = False,
        temperature: float = 0.0,
        max_tokens: int = 1024,
        timeout_seconds: int = 30,
        config: Optional[Dict[str, Any]] = None,
    ) -> LLMProviderConfig:
        """
        Create a new LLM provider configuration.

        Args:
            provider: Provider name (openai, anthropic, google)
            display_name: Human-readable name
            api_key: API key (will be encrypted)
            tenant_id: Optional tenant ID (None = global)
            default_model: Default model name
            is_active: Whether active
            is_default: Whether default for provider
            temperature: Default temperature
            max_tokens: Default max tokens
            timeout_seconds: Request timeout
            config: Additional config

        Returns:
            Created LLMProviderConfig
        """
        provider = provider.lower()

        # If setting as default, unset other defaults for this provider
        if is_default:
            self._unset_other_defaults(provider, tenant_id)

        # Set default model if not provided
        if not default_model:
            default_models = LLMProviderConfig.get_default_models()
            default_model = default_models.get(provider)

        # Create the config
        new_config = LLMProviderConfig(
            tenant_id=tenant_id,
            provider=provider,
            display_name=display_name,
            default_model=default_model,
            is_active=is_active,
            is_default=is_default,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout_seconds=timeout_seconds,
            config=config,
        )

        # Set and encrypt the API key
        new_config.set_api_key(api_key)

        self.db.add(new_config)
        self.db.commit()
        self.db.refresh(new_config)

        logger.info(
            f"Created LLM provider config: {provider} - {display_name}"
        )

        return new_config

    def update_config(
        self,
        config_id: UUID,
        tenant_id: Optional[UUID] = None,
        **updates: Any,
    ) -> Optional[LLMProviderConfig]:
        """
        Update an LLM provider configuration.

        Args:
            config_id: Configuration ID
            tenant_id: Optional tenant filter for access control
            **updates: Fields to update

        Returns:
            Updated LLMProviderConfig or None if not found
        """
        config = self.get_config(config_id, tenant_id)
        if not config:
            return None

        # Handle API key separately (needs encryption)
        api_key = updates.pop('api_key', None)
        if api_key:
            config.set_api_key(api_key)

        # Handle is_default (need to unset others)
        is_default = updates.pop('is_default', None)
        if is_default is True:
            self._unset_other_defaults(config.provider, config.tenant_id)
            config.is_default = True
        elif is_default is False:
            config.is_default = False

        # Update other fields
        for field, value in updates.items():
            if value is not None and hasattr(config, field):
                setattr(config, field, value)

        self.db.commit()
        self.db.refresh(config)

        logger.info(f"Updated LLM provider config: {config.id}")

        return config

    def delete_config(
        self,
        config_id: UUID,
        tenant_id: Optional[UUID] = None,
    ) -> bool:
        """
        Delete an LLM provider configuration.

        Args:
            config_id: Configuration ID
            tenant_id: Optional tenant filter for access control

        Returns:
            True if deleted, False if not found
        """
        config = self.get_config(config_id, tenant_id)
        if not config:
            return False

        self.db.delete(config)
        self.db.commit()

        logger.info(f"Deleted LLM provider config: {config_id}")

        return True

    def _unset_other_defaults(
        self,
        provider: str,
        tenant_id: Optional[UUID],
    ) -> None:
        """
        Unset is_default for other configs of same provider.

        Args:
            provider: Provider name
            tenant_id: Tenant ID (None = global)
        """
        conditions = [
            LLMProviderConfig.provider == provider,
            LLMProviderConfig.is_default == True,
        ]

        if tenant_id:
            conditions.append(LLMProviderConfig.tenant_id == tenant_id)
        else:
            conditions.append(LLMProviderConfig.tenant_id.is_(None))

        stmt = (
            sa_update(LLMProviderConfig)
            .where(and_(*conditions))
            .values(is_default=False)
        )

        self.db.execute(stmt)

    def get_providers_summary(
        self,
        tenant_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """
        Get summary of all providers and their configuration status.

        Args:
            tenant_id: Optional tenant ID

        Returns:
            Dictionary with providers summary
        """
        supported = LLMProviderConfig.get_supported_providers()
        default_models = LLMProviderConfig.get_default_models()

        # Get all active configs
        configs = self.list_configs(
            tenant_id=tenant_id,
            is_active=True,
            include_global=True,
        )

        # Build config lookup by provider
        config_by_provider: Dict[str, LLMProviderConfig] = {}
        for config in configs:
            # Prefer tenant-specific over global
            if config.provider not in config_by_provider:
                config_by_provider[config.provider] = config
            elif config.tenant_id and not config_by_provider[config.provider].tenant_id:
                config_by_provider[config.provider] = config

        # Build summary
        providers = []
        for provider in supported:
            config = config_by_provider.get(provider)
            providers.append({
                'provider': provider,
                'display_name': provider.title(),
                'default_model': default_models.get(provider, ''),
                'is_configured': config is not None,
                'is_active': config.is_active if config else False,
            })

        return {
            'providers': providers,
            'total_configured': sum(1 for p in providers if p['is_configured']),
            'total_active': sum(1 for p in providers if p['is_active']),
        }
