"""
Service layer for managing PatternAnalysisConfig records.

Provides CRUD operations and utilities for tenant-specific pattern analysis settings.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.pattern_analysis_config import PatternAnalysisConfig
from services.settings_manager import SettingsManager


class PatternAnalysisConfigService:
    """Encapsulates PatternAnalysisConfig persistence and business logic."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_or_create(
        self,
        tenant_id: UUID
    ) -> PatternAnalysisConfig:
        """
        Get configuration for tenant, creating default if doesn't exist.

        Args:
            tenant_id: Tenant UUID

        Returns:
            PatternAnalysisConfig instance
        """
        stmt = select(PatternAnalysisConfig).where(
            PatternAnalysisConfig.tenant_id == tenant_id
        )
        result = await self.session.execute(stmt)
        config = result.scalar_one_or_none()

        if config is None:
            # Create with defaults
            config = PatternAnalysisConfig(
                tenant_id=tenant_id,
                # Column defaults will be used
            )
            self.session.add(config)
            await self.session.commit()
            await self.session.refresh(config)

        return config

    async def get_by_id(
        self,
        config_id: UUID
    ) -> Optional[PatternAnalysisConfig]:
        """
        Get configuration by ID.

        Args:
            config_id: Configuration UUID

        Returns:
            PatternAnalysisConfig if found, None otherwise
        """
        stmt = select(PatternAnalysisConfig).where(
            PatternAnalysisConfig.id == config_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_tenant(
        self,
        tenant_id: UUID
    ) -> Optional[PatternAnalysisConfig]:
        """
        Get configuration for specific tenant.

        Args:
            tenant_id: Tenant UUID

        Returns:
            PatternAnalysisConfig if exists, None otherwise
        """
        stmt = select(PatternAnalysisConfig).where(
            PatternAnalysisConfig.tenant_id == tenant_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_active(self) -> List[PatternAnalysisConfig]:
        """
        Get all configurations with auto-analysis enabled.

        Returns:
            List of PatternAnalysisConfig instances
        """
        stmt = select(PatternAnalysisConfig).where(
            PatternAnalysisConfig.enable_auto_analysis == True  # noqa: E712
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self,
        config_id: UUID,
        **updates: Any
    ) -> PatternAnalysisConfig:
        """
        Update configuration fields.

        Args:
            config_id: Configuration UUID
            **updates: Fields to update

        Returns:
            Updated PatternAnalysisConfig

        Raises:
            ValueError: If config not found
        """
        config = await self.get_by_id(config_id)

        if config is None:
            raise ValueError(f"PatternAnalysisConfig {config_id} not found")

        # Update fields
        for field, value in updates.items():
            if hasattr(config, field) and value is not None:
                setattr(config, field, value)

        await self.session.commit()
        await self.session.refresh(config)

        return config

    async def delete(self, config_id: UUID) -> bool:
        """
        Delete configuration.

        Args:
            config_id: Configuration UUID

        Returns:
            True if deleted, False if not found
        """
        config = await self.get_by_id(config_id)

        if config is None:
            return False

        await self.session.delete(config)
        await self.session.commit()

        return True

    async def get_analysis_params(
        self,
        tenant_id: UUID
    ) -> Dict[str, Any]:
        """
        Get analysis parameters for tenant in dict format.

        Uses SettingsManager to apply proper 3-tier hierarchy:
        1. Organization-specific config (tenant_id)
        2. Global defaults (tenant_id = NULL)
        3. .env defaults

        Useful for passing to Celery tasks.

        Args:
            tenant_id: Tenant UUID

        Returns:
            Dict with analysis parameters following settings hierarchy
        """
        manager = SettingsManager(self.session)

        return {
            'lookback_days': await manager.get_pattern_analysis_setting(
                'lookback_days', tenant_id, default=30
            ),
            'min_pattern_size': await manager.get_pattern_analysis_setting(
                'min_pattern_size', tenant_id, default=3
            ),
            'similarity_threshold': await manager.get_pattern_analysis_setting(
                'similarity_threshold', tenant_id, default=0.85
            ),
            'defect_auto_creation_threshold': await manager.get_pattern_analysis_setting(
                'defect_auto_creation_threshold', tenant_id, default=3
            ),
            'enable_llm_analysis': await manager.get_pattern_analysis_setting(
                'enable_llm_analysis', tenant_id, default=True
            ),
            'llm_confidence_threshold': await manager.get_pattern_analysis_setting(
                'llm_confidence_threshold', tenant_id, default=0.70
            ),
        }
