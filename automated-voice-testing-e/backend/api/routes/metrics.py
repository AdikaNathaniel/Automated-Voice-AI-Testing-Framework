"""
Metrics API routes (TASK-222).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from api.database import get_db
from api.dependencies import get_current_user_with_db
from api.schemas.auth import UserResponse
from api.schemas.metrics import RealTimeMetricsResponse
from api import metrics
from services import real_time_metrics_service

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get(
    "",
    include_in_schema=False,
    summary="Prometheus metrics scrape target",
)
def scrape_metrics() -> Response:
    payload = generate_latest(metrics.registry)
    response = Response(content=payload)
    response.headers["content-type"] = CONTENT_TYPE_LATEST
    return response


@router.get(
    "/real-time",
    response_model=RealTimeMetricsResponse,
    summary="Get real-time execution metrics",
    description="Return active test runs, queue depth, and throughput snapshots for the dashboard.",
)
async def get_real_time_metrics(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
    window_minutes: int = Query(
        15,
        ge=1,
        le=120,
        description="Rolling window (minutes) for throughput calculations.",
    ),
    max_runs: int = Query(
        5,
        ge=1,
        le=20,
        description="Maximum number of active test runs to include.",
    ),
) -> RealTimeMetricsResponse:
    payload = await real_time_metrics_service.get_real_time_metrics(
        db,
        window_minutes=window_minutes,
        max_runs=max_runs,
    )
    return RealTimeMetricsResponse.model_validate(payload)
