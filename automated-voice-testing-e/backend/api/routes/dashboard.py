"""
Dashboard analytics API routes.
"""

from __future__ import annotations

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.schemas.auth import UserResponse
from api.schemas.dashboard import DashboardResponse
from api.dependencies import get_current_user_with_db
from services import dashboard_service
from services.settings_manager import SettingsManager

router = APIRouter(prefix="/reports", tags=["Reports"])


class DashboardSettingsResponse(BaseModel):
    """Response model for dashboard settings."""
    response_time_sla_ms: int

TimeRangeLiteral = Literal["1h", "24h", "7d", "30d"]


@router.get(
    "/dashboard",
    response_model=DashboardResponse,
    summary="Get dashboard snapshot",
    description="Return aggregated dashboard metrics for the requested time range.",
)
async def get_dashboard_snapshot(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
    time_range: TimeRangeLiteral = Query("24h", description="Time range window"),
) -> DashboardResponse:
    snapshot = await dashboard_service.get_dashboard_snapshot(
        db,
        time_range=time_range,
    )
    return DashboardResponse.model_validate(snapshot)


@router.get(
    "/dashboard/settings",
    response_model=DashboardSettingsResponse,
    summary="Get dashboard settings",
    description="Return dashboard-specific settings like SLA thresholds.",
)
async def get_dashboard_settings(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> DashboardSettingsResponse:
    """Get dashboard settings including SLA thresholds."""
    settings_manager = SettingsManager(db)

    # Get tenant ID from current user if available
    tenant_id = getattr(current_user, 'tenant_id', None)

    response_time_sla = await settings_manager.get_pattern_analysis_setting(
        "response_time_sla_ms",
        tenant_id=tenant_id,
        default=2000
    )

    return DashboardSettingsResponse(
        response_time_sla_ms=response_time_sla
    )
