"""
LLM Analytics API Routes

Endpoints for LLM usage and cost analytics.
Provides cost breakdowns, usage trends, and budget monitoring.
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.dependencies import get_current_user_with_db
from api.schemas.auth import UserResponse
from api.schemas.llm_analytics import (
    DailyCostsResponse,
    DailyCostSummary,
    OperationBreakdownResponse,
    OperationCostBreakdown,
    ModelBreakdownResponse,
    ModelCostBreakdown,
    LLMCostSummary,
    RecentCallsResponse,
    RecentCallLog,
)
from models.llm_usage_log import LLMUsageLog


router = APIRouter(
    prefix="/analytics/llm-costs",
    tags=["LLM Analytics"],
)


def _calculate_summary(
    total_calls: int,
    total_tokens: int,
    total_cost: float,
    successful_calls: int,
    failed_calls: int,
    period_start: datetime,
    period_end: datetime,
) -> LLMCostSummary:
    """Calculate summary statistics."""
    success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0
    avg_cost = total_cost / total_calls if total_calls > 0 else 0
    avg_tokens = total_tokens / total_calls if total_calls > 0 else 0

    return LLMCostSummary(
        total_calls=total_calls,
        total_tokens=total_tokens,
        total_cost_usd=round(total_cost, 6),
        successful_calls=successful_calls,
        failed_calls=failed_calls,
        success_rate=round(success_rate, 2),
        avg_cost_per_call=round(avg_cost, 6),
        avg_tokens_per_call=round(avg_tokens, 2),
        period_start=period_start.strftime("%Y-%m-%d"),
        period_end=period_end.strftime("%Y-%m-%d"),
    )


@router.get("/daily", response_model=DailyCostsResponse)
async def get_daily_costs(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> DailyCostsResponse:
    """
    Get daily LLM costs for current tenant.

    Returns cost breakdown by day for the specified time period.
    """
    period_end = datetime.utcnow()
    period_start = period_end - timedelta(days=days)

    # Get daily aggregates
    daily_query = (
        select(
            func.date(LLMUsageLog.created_at).label("date"),
            func.count().label("total_calls"),
            func.sum(LLMUsageLog.total_tokens).label("total_tokens"),
            func.sum(LLMUsageLog.prompt_tokens).label("prompt_tokens"),
            func.sum(LLMUsageLog.completion_tokens).label("completion_tokens"),
            func.sum(LLMUsageLog.estimated_cost_usd).label("total_cost"),
            func.sum(func.cast(LLMUsageLog.success, func.INTEGER)).label("successful_calls"),
            func.sum(func.cast(~LLMUsageLog.success, func.INTEGER)).label("failed_calls"),
        )
        .where(
            and_(
                LLMUsageLog.tenant_id == current_user.tenant_id,
                LLMUsageLog.created_at >= period_start,
                LLMUsageLog.created_at <= period_end,
            )
        )
        .group_by(func.date(LLMUsageLog.created_at))
        .order_by(func.date(LLMUsageLog.created_at).desc())
    )

    result = await db.execute(daily_query)
    daily_rows = result.all()

    # Get overall summary
    summary_query = (
        select(
            func.count().label("total_calls"),
            func.sum(LLMUsageLog.total_tokens).label("total_tokens"),
            func.sum(LLMUsageLog.estimated_cost_usd).label("total_cost"),
            func.sum(func.cast(LLMUsageLog.success, func.INTEGER)).label("successful_calls"),
            func.sum(func.cast(~LLMUsageLog.success, func.INTEGER)).label("failed_calls"),
        )
        .where(
            and_(
                LLMUsageLog.tenant_id == current_user.tenant_id,
                LLMUsageLog.created_at >= period_start,
                LLMUsageLog.created_at <= period_end,
            )
        )
    )

    summary_result = await db.execute(summary_query)
    summary_row = summary_result.one()

    # Build response
    daily_costs = [
        DailyCostSummary(
            date=str(row.date),
            total_calls=row.total_calls or 0,
            total_tokens=row.total_tokens or 0,
            prompt_tokens=row.prompt_tokens or 0,
            completion_tokens=row.completion_tokens or 0,
            total_cost_usd=round(float(row.total_cost or 0), 6),
            successful_calls=row.successful_calls or 0,
            failed_calls=row.failed_calls or 0,
        )
        for row in daily_rows
    ]

    summary = _calculate_summary(
        total_calls=summary_row.total_calls or 0,
        total_tokens=summary_row.total_tokens or 0,
        total_cost=float(summary_row.total_cost or 0),
        successful_calls=summary_row.successful_calls or 0,
        failed_calls=summary_row.failed_calls or 0,
        period_start=period_start,
        period_end=period_end,
    )

    return DailyCostsResponse(summary=summary, daily_costs=daily_costs)


@router.get("/by-operation", response_model=OperationBreakdownResponse)
async def get_costs_by_operation(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> OperationBreakdownResponse:
    """
    Get LLM costs broken down by operation type.

    Shows which operations (analyze_edge_case, match_pattern, etc.) are most expensive.
    """
    period_end = datetime.utcnow()
    period_start = period_end - timedelta(days=days)

    # Get operation breakdown
    operation_query = (
        select(
            LLMUsageLog.operation,
            func.count().label("total_calls"),
            func.sum(LLMUsageLog.total_tokens).label("total_tokens"),
            func.sum(LLMUsageLog.estimated_cost_usd).label("total_cost"),
            func.avg(LLMUsageLog.total_tokens).label("avg_tokens"),
            func.avg(LLMUsageLog.estimated_cost_usd).label("avg_cost"),
            func.avg(LLMUsageLog.duration_ms).label("avg_duration"),
        )
        .where(
            and_(
                LLMUsageLog.tenant_id == current_user.tenant_id,
                LLMUsageLog.created_at >= period_start,
                LLMUsageLog.created_at <= period_end,
            )
        )
        .group_by(LLMUsageLog.operation)
        .order_by(func.sum(LLMUsageLog.estimated_cost_usd).desc())
    )

    result = await db.execute(operation_query)
    operation_rows = result.all()

    # Get overall summary
    summary_query = (
        select(
            func.count().label("total_calls"),
            func.sum(LLMUsageLog.total_tokens).label("total_tokens"),
            func.sum(LLMUsageLog.estimated_cost_usd).label("total_cost"),
            func.sum(func.cast(LLMUsageLog.success, func.INTEGER)).label("successful_calls"),
            func.sum(func.cast(~LLMUsageLog.success, func.INTEGER)).label("failed_calls"),
        )
        .where(
            and_(
                LLMUsageLog.tenant_id == current_user.tenant_id,
                LLMUsageLog.created_at >= period_start,
                LLMUsageLog.created_at <= period_end,
            )
        )
    )

    summary_result = await db.execute(summary_query)
    summary_row = summary_result.one()

    # Build response
    operations = [
        OperationCostBreakdown(
            operation=row.operation,
            total_calls=row.total_calls or 0,
            total_tokens=row.total_tokens or 0,
            total_cost_usd=round(float(row.total_cost or 0), 6),
            avg_tokens_per_call=round(float(row.avg_tokens or 0), 2),
            avg_cost_per_call=round(float(row.avg_cost or 0), 6),
            avg_duration_ms=round(float(row.avg_duration or 0), 2),
        )
        for row in operation_rows
    ]

    summary = _calculate_summary(
        total_calls=summary_row.total_calls or 0,
        total_tokens=summary_row.total_tokens or 0,
        total_cost=float(summary_row.total_cost or 0),
        successful_calls=summary_row.successful_calls or 0,
        failed_calls=summary_row.failed_calls or 0,
        period_start=period_start,
        period_end=period_end,
    )

    return OperationBreakdownResponse(summary=summary, operations=operations)


@router.get("/by-model", response_model=ModelBreakdownResponse)
async def get_costs_by_model(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> ModelBreakdownResponse:
    """
    Get LLM costs broken down by model.

    Shows which models (Claude Sonnet, GPT-4, etc.) are most expensive.
    """
    period_end = datetime.utcnow()
    period_start = period_end - timedelta(days=days)

    # Get model breakdown
    model_query = (
        select(
            LLMUsageLog.model,
            LLMUsageLog.provider,
            func.count().label("total_calls"),
            func.sum(LLMUsageLog.total_tokens).label("total_tokens"),
            func.sum(LLMUsageLog.estimated_cost_usd).label("total_cost"),
            func.avg(LLMUsageLog.total_tokens).label("avg_tokens"),
            func.avg(LLMUsageLog.estimated_cost_usd).label("avg_cost"),
        )
        .where(
            and_(
                LLMUsageLog.tenant_id == current_user.tenant_id,
                LLMUsageLog.created_at >= period_start,
                LLMUsageLog.created_at <= period_end,
            )
        )
        .group_by(LLMUsageLog.model, LLMUsageLog.provider)
        .order_by(func.sum(LLMUsageLog.estimated_cost_usd).desc())
    )

    result = await db.execute(model_query)
    model_rows = result.all()

    # Get overall summary
    summary_query = (
        select(
            func.count().label("total_calls"),
            func.sum(LLMUsageLog.total_tokens).label("total_tokens"),
            func.sum(LLMUsageLog.estimated_cost_usd).label("total_cost"),
            func.sum(func.cast(LLMUsageLog.success, func.INTEGER)).label("successful_calls"),
            func.sum(func.cast(~LLMUsageLog.success, func.INTEGER)).label("failed_calls"),
        )
        .where(
            and_(
                LLMUsageLog.tenant_id == current_user.tenant_id,
                LLMUsageLog.created_at >= period_start,
                LLMUsageLog.created_at <= period_end,
            )
        )
    )

    summary_result = await db.execute(summary_query)
    summary_row = summary_result.one()

    # Build response
    models = [
        ModelCostBreakdown(
            model=row.model,
            provider=row.provider,
            total_calls=row.total_calls or 0,
            total_tokens=row.total_tokens or 0,
            total_cost_usd=round(float(row.total_cost or 0), 6),
            avg_tokens_per_call=round(float(row.avg_tokens or 0), 2),
            avg_cost_per_call=round(float(row.avg_cost or 0), 6),
        )
        for row in model_rows
    ]

    summary = _calculate_summary(
        total_calls=summary_row.total_calls or 0,
        total_tokens=summary_row.total_tokens or 0,
        total_cost=float(summary_row.total_cost or 0),
        successful_calls=summary_row.successful_calls or 0,
        failed_calls=summary_row.failed_calls or 0,
        period_start=period_start,
        period_end=period_end,
    )

    return ModelBreakdownResponse(summary=summary, models=models)


@router.get("/recent-calls", response_model=RecentCallsResponse)
async def get_recent_calls(
    limit: int = Query(default=50, ge=1, le=500, description="Number of recent calls to return"),
    include_failed: bool = Query(default=True, description="Include failed calls"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> RecentCallsResponse:
    """
    Get recent LLM API calls.

    Returns the most recent LLM calls with details for debugging and monitoring.
    """
    query = (
        select(LLMUsageLog)
        .where(LLMUsageLog.tenant_id == current_user.tenant_id)
        .order_by(LLMUsageLog.created_at.desc())
        .limit(limit)
    )

    if not include_failed:
        query = query.where(LLMUsageLog.success == True)  # noqa: E712

    result = await db.execute(query)
    logs = result.scalars().all()

    # Get total count
    count_query = select(func.count()).where(
        LLMUsageLog.tenant_id == current_user.tenant_id
    )
    if not include_failed:
        count_query = count_query.where(LLMUsageLog.success == True)  # noqa: E712

    count_result = await db.execute(count_query)
    total_count = count_result.scalar()

    # Build response
    calls = [
        RecentCallLog(
            id=str(log.id),
            created_at=log.created_at.isoformat(),
            operation=log.operation,
            model=log.model,
            total_tokens=log.total_tokens or 0,
            estimated_cost_usd=round(float(log.estimated_cost_usd or 0), 6),
            duration_ms=log.duration_ms,
            success=log.success,
            error_message=log.error_message,
        )
        for log in logs
    ]

    return RecentCallsResponse(calls=calls, total_count=total_count or 0)
