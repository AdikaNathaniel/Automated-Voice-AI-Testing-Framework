"""
Analytics trend endpoints (TASK-310).
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Annotated, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.dependencies import get_current_user_with_db
from api.schemas.analytics import TrendAnalyticsResponse
from api.schemas.auth import UserResponse
from services.trend_analysis_service import TrendAnalysisService

router = APIRouter(prefix="/analytics", tags=["Analytics"])

GranularityLiteral = Literal["raw", "hour", "day"]


async def get_trend_analysis_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TrendAnalysisService:
    return TrendAnalysisService(db)


@router.get(
    "/trends",
    response_model=TrendAnalyticsResponse,
    summary="Retrieve aggregated trend analytics",
    description="Returns pass rate, defect backlog, and performance trends for the requested period.",
)
async def get_trends(
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
    trend_service: Annotated[TrendAnalysisService, Depends(get_trend_analysis_service)],
    start_date: Optional[date] = Query(
        None,
        description="Start date for trend aggregation (defaults to 7 days before end_date).",
    ),
    end_date: Optional[date] = Query(
        None,
        description="End date for trend aggregation (defaults to today).",
    ),
    granularity: GranularityLiteral = Query(
        "day",
        description="Aggregation window size for trend calculations.",
    ),
) -> TrendAnalyticsResponse:
    end = end_date or date.today()
    start = start_date or (end - timedelta(days=7))

    if start > end:
        raise HTTPException(status_code=400, detail="start_date must be on or before end_date")

    try:
        pass_rate = await trend_service.analyze_pass_rate_trend(
            start_date=start,
            end_date=end,
            granularity=granularity,
        )
        defects = await trend_service.analyze_defect_trend(
            start_date=start,
            end_date=end,
            granularity=granularity,
        )
        performance = await trend_service.analyze_performance_trend(
            start_date=start,
            end_date=end,
            granularity=granularity,
        )
        summary = await trend_service.get_summary_statistics(
            start_date=start,
            end_date=end,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return TrendAnalyticsResponse(
        pass_rate=pass_rate,
        defects=defects,
        performance=performance,
        summary=summary,
    )
