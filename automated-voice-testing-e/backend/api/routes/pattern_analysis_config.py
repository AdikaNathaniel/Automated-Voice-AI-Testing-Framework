"""
Pattern Analysis Configuration API routes.

Provides endpoints for managing tenant-specific pattern analysis settings.
"""

from typing import Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.dependencies import get_current_user_with_db
from api.schemas.auth import UserResponse
from api.schemas.pattern_analysis_config import (
    PatternAnalysisConfigResponse,
    PatternAnalysisConfigUpdate,
    ManualAnalysisRequest,
    ManualAnalysisResponse,
)
from services.pattern_analysis_config_service import PatternAnalysisConfigService
from services.settings_manager import SettingsManager
from tasks.edge_case_analysis import analyze_edge_case_patterns


router = APIRouter(
    prefix="/pattern-analysis/config",
    tags=["Pattern Analysis Configuration"],
)


def _ensure_org_admin(user: UserResponse) -> None:
    """Ensure user has organization admin privileges.

    Both ORG_ADMIN and SUPER_ADMIN can access pattern analysis configs:
    - ORG_ADMIN: Manages their organization's specific configuration
    - SUPER_ADMIN: Manages global default configuration (tenant_id=NULL)
    """
    if user.role not in ("org_admin", "super_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization admin privileges required"
        )


@router.get(
    "",
    response_model=PatternAnalysisConfigResponse,
    summary="Get pattern analysis configuration",
)
async def get_pattern_analysis_config(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> PatternAnalysisConfigResponse:
    """
    Get pattern analysis configuration for current tenant.

    Creates default configuration if it doesn't exist.

    TODO: Connect analysis_schedule to Celery Beat
    Currently, the schedule is stored but not actively used by Celery Beat.
    To implement:
    1. Create dynamic Celery Beat schedule loader
    2. Read all active configs on Beat startup
    3. Update Beat schedule when configs change
    4. Use django-celery-beat or similar for dynamic scheduling

    Example implementation:
        from celery.schedules import crontab
        from celery import current_app

        # On config update:
        schedule_entry = {
            f'pattern-analysis-{tenant_id}': {
                'task': 'analyze_edge_case_patterns',
                'schedule': crontab(**parse_cron(config.analysis_schedule)),
                'args': (str(tenant_id),),
            }
        }
        current_app.conf.beat_schedule.update(schedule_entry)
    """
    service = PatternAnalysisConfigService(db)
    # tenant_id can be None for super_admin (manages global defaults)
    config = await service.get_or_create(current_user.tenant_id)

    return PatternAnalysisConfigResponse.model_validate(config)


@router.put(
    "",
    response_model=PatternAnalysisConfigResponse,
    summary="Update pattern analysis configuration",
)
async def update_pattern_analysis_config(
    updates: PatternAnalysisConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> PatternAnalysisConfigResponse:
    """
    Update pattern analysis configuration.

    Requires organization admin privileges.
    """
    _ensure_org_admin(current_user)

    service = PatternAnalysisConfigService(db)

    # Get or create config
    config = await service.get_or_create(current_user.tenant_id)

    # Prepare update dict (only non-None values)
    update_data = updates.dict(exclude_unset=True, exclude_none=True)

    if not update_data:
        # No updates provided
        return PatternAnalysisConfigResponse.model_validate(config)

    # Update
    updated_config = await service.update(config.id, **update_data)

    return PatternAnalysisConfigResponse.model_validate(updated_config)


@router.post(
    "/analyze/manual",
    response_model=ManualAnalysisResponse,
    summary="Trigger manual pattern analysis",
    status_code=status.HTTP_202_ACCEPTED,
)
async def trigger_manual_analysis(
    request: ManualAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> ManualAnalysisResponse:
    """
    Trigger manual pattern analysis with optional parameter overrides.

    Useful for:
    - Testing different analysis parameters
    - Running analysis on-demand outside of schedule
    - Analyzing specific time windows

    Requires organization admin privileges.

    Example overrides:
    ```json
    {
      "overrides": {
        "lookback_days": 14,
        "min_pattern_size": 2,
        "similarity_threshold": 0.80
      }
    }
    ```
    """
    _ensure_org_admin(current_user)

    # Queue Celery task
    task = analyze_edge_case_patterns.delay(
        tenant_id=str(current_user.tenant_id),
        override_params=request.overrides
    )

    return ManualAnalysisResponse(
        status="queued",
        task_id=task.id,
        message=f"Pattern analysis queued for tenant {current_user.tenant_id}"
    )


@router.get(
    "/defaults",
    response_model=Dict[str, Any],
    summary="Get effective configuration values with hierarchy",
)
async def get_default_config(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> Dict[str, Any]:
    """
    Get effective configuration values for current tenant with hierarchy.

    Returns values following 3-tier hierarchy:
    1. Organization-specific settings
    2. Global defaults (set by super admin)
    3. .env defaults (application fallback)

    Useful for:
    - Seeing what values would be used if no org config exists
    - Understanding baseline settings
    - Comparing org overrides with global defaults
    """
    manager = SettingsManager(db)

    # Get all settings with hierarchy applied for this tenant
    settings = await manager.get_all_settings(
        setting_type="pattern_analysis",
        tenant_id=current_user.tenant_id,
        include_source=True
    )

    return settings
