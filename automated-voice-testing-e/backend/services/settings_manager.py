"""
Settings Manager Service

Centralized settings management with 3-tier hierarchy:
1. Organization setting (tenant-specific override)
2. Global default (system-wide default)
3. .env default (application fallback)

This ensures consistent settings resolution across the application.
"""

from typing import Any, Optional, Dict
from uuid import UUID
import os

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.pattern_analysis_config import PatternAnalysisConfig
from api.config import get_settings


class SettingsManager:
    """
    Centralized settings manager implementing 3-tier hierarchy.

    Resolution order:
    1. Organization-specific setting (if tenant_id provided)
    2. Global system default (tenant_id = NULL)
    3. .env / application default

    Example:
        ```python
        settings_mgr = SettingsManager(db)

        # Get pattern analysis lookback days
        lookback_days = await settings_mgr.get_setting(
            key="lookback_days",
            tenant_id=org_uuid,
            setting_type="pattern_analysis",
            default=30  # Application default
        )
        ```
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.app_settings = get_settings()

    async def get_pattern_analysis_setting(
        self,
        key: str,
        tenant_id: Optional[UUID] = None,
        default: Any = None
    ) -> Any:
        """
        Get pattern analysis configuration setting with proper hierarchy.

        Args:
            key: Setting key (e.g., "lookback_days")
            tenant_id: Organization ID (optional)
            default: Fallback value if not found anywhere

        Returns:
            Setting value following the hierarchy
        """
        # 1. Try organization-specific setting
        if tenant_id:
            org_value = await self._get_org_pattern_analysis_setting(tenant_id, key)
            if org_value is not None:
                return org_value

        # 2. Try global default
        global_value = await self._get_global_pattern_analysis_setting(key)
        if global_value is not None:
            return global_value

        # 3. Fall back to .env or provided default
        return self._get_env_pattern_analysis_default(key, default)

    async def _get_org_pattern_analysis_setting(
        self,
        tenant_id: UUID,
        key: str
    ) -> Optional[Any]:
        """Get organization-specific pattern analysis setting."""
        query = select(PatternAnalysisConfig).where(
            PatternAnalysisConfig.tenant_id == tenant_id
        )
        result = await self.db.execute(query)
        config = result.scalar_one_or_none()

        if config and hasattr(config, key):
            value = getattr(config, key)
            # Return None if the value is not explicitly set
            # This allows fallback to global defaults
            if value is not None:
                return value

        return None

    async def _get_global_pattern_analysis_setting(
        self,
        key: str
    ) -> Optional[Any]:
        """
        Get global default pattern analysis setting.

        Queries pattern_analysis_configs table with tenant_id = NULL
        to get system-wide global defaults set by super admin.
        """
        query = select(PatternAnalysisConfig).where(
            PatternAnalysisConfig.tenant_id == None
        )
        result = await self.db.execute(query)
        config = result.scalar_one_or_none()

        if config and hasattr(config, key):
            value = getattr(config, key)
            # Return None if the value is not explicitly set
            # This allows fallback to .env defaults
            if value is not None:
                return value

        return None

    def _get_env_pattern_analysis_default(
        self,
        key: str,
        fallback: Any = None
    ) -> Any:
        """
        Get .env or hardcoded application default.

        Maps pattern analysis setting keys to .env variables or defaults.
        """
        defaults = {
            "lookback_days": int(os.getenv("PATTERN_ANALYSIS_LOOKBACK_DAYS", "30")),
            "min_pattern_size": int(os.getenv("PATTERN_ANALYSIS_MIN_SIZE", "3")),
            "similarity_threshold": float(os.getenv("PATTERN_ANALYSIS_SIMILARITY", "0.85")),
            "defect_auto_creation_threshold": int(os.getenv("DEFECT_AUTO_CREATION_THRESHOLD", "3")),
            "enable_llm_analysis": os.getenv("PATTERN_ANALYSIS_ENABLE_LLM", "true").lower() == "true",
            "llm_confidence_threshold": float(os.getenv("PATTERN_ANALYSIS_LLM_CONFIDENCE", "0.70")),
            "analysis_schedule": os.getenv("PATTERN_ANALYSIS_SCHEDULE", "0 2 * * *"),
            "enable_auto_analysis": os.getenv("PATTERN_ANALYSIS_AUTO", "true").lower() == "true",
            "notify_on_new_patterns": os.getenv("PATTERN_ANALYSIS_NOTIFY_NEW", "true").lower() == "true",
            "notify_on_critical_patterns": os.getenv("PATTERN_ANALYSIS_NOTIFY_CRITICAL", "true").lower() == "true",
            "response_time_sla_ms": int(os.getenv("RESPONSE_TIME_SLA_MS", "2000")),
        }

        return defaults.get(key, fallback)

    # =========================================================================
    # Generic Settings Methods (for extensibility)
    # =========================================================================

    async def get_setting(
        self,
        key: str,
        setting_type: str = "pattern_analysis",
        tenant_id: Optional[UUID] = None,
        default: Any = None
    ) -> Any:
        """
        Generic setting getter with hierarchy support.

        Args:
            key: Setting key
            setting_type: Type of setting ("pattern_analysis", "notification", etc.)
            tenant_id: Organization ID
            default: Fallback value

        Returns:
            Setting value following the hierarchy
        """
        if setting_type == "pattern_analysis":
            return await self.get_pattern_analysis_setting(key, tenant_id, default)

        # TODO: Add support for other setting types
        # elif setting_type == "notification":
        #     return await self.get_notification_setting(key, tenant_id, default)
        # elif setting_type == "cicd":
        #     return await self.get_cicd_setting(key, tenant_id, default)

        # Fallback to default
        return default

    async def get_all_settings(
        self,
        setting_type: str = "pattern_analysis",
        tenant_id: Optional[UUID] = None,
        include_source: bool = False
    ) -> Dict[str, Any]:
        """
        Get all settings of a specific type with hierarchy applied.

        Args:
            setting_type: Type of settings to retrieve
            tenant_id: Organization ID
            include_source: If True, includes metadata about where each value came from

        Returns:
            Dictionary of all settings with hierarchy applied
        """
        if setting_type == "pattern_analysis":
            return await self._get_all_pattern_analysis_settings(tenant_id, include_source)

        return {}

    async def _get_all_pattern_analysis_settings(
        self,
        tenant_id: Optional[UUID] = None,
        include_source: bool = False
    ) -> Dict[str, Any]:
        """Get all pattern analysis settings with hierarchy applied."""
        keys = [
            "lookback_days",
            "min_pattern_size",
            "similarity_threshold",
            "defect_auto_creation_threshold",
            "enable_llm_analysis",
            "llm_confidence_threshold",
            "analysis_schedule",
            "enable_auto_analysis",
            "notify_on_new_patterns",
            "notify_on_critical_patterns",
            "response_time_sla_ms",
        ]

        result = {}
        for key in keys:
            value = await self.get_pattern_analysis_setting(key, tenant_id)

            if include_source:
                # Determine source for transparency
                source = "env_default"
                if tenant_id:
                    org_value = await self._get_org_pattern_analysis_setting(tenant_id, key)
                    if org_value is not None:
                        source = "org_override"
                    else:
                        global_value = await self._get_global_pattern_analysis_setting(key)
                        if global_value is not None:
                            source = "global_default"

                result[key] = {
                    "value": value,
                    "source": source
                }
            else:
                result[key] = value

        return result


# Convenience function for quick access
async def get_setting(
    db: AsyncSession,
    key: str,
    setting_type: str = "pattern_analysis",
    tenant_id: Optional[UUID] = None,
    default: Any = None
) -> Any:
    """
    Convenience function to get a single setting value.

    Example:
        ```python
        lookback_days = await get_setting(
            db=db,
            key="lookback_days",
            setting_type="pattern_analysis",
            tenant_id=current_user.tenant_id,
            default=30
        )
        ```
    """
    manager = SettingsManager(db)
    return await manager.get_setting(key, setting_type, tenant_id, default)
