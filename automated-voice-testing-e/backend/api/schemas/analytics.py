"""
Analytics trend response schemas.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

TrendDirection = Literal["up", "down", "flat"]


class PassRateTrendPoint(BaseModel):
    period_start: datetime = Field(..., description="Beginning of the aggregation window.")
    pass_rate_pct: float = Field(..., description="Average validation pass rate expressed as a percentage.")
    change_pct: Optional[float] = Field(
        None,
        description="Change in pass rate percentage compared to the previous period.",
    )
    direction: TrendDirection = Field(
        "flat",
        description="Direction of change compared to the previous period.",
    )
    total_executions: int = Field(..., ge=0, description="Total executions measured during the period.")


class DefectTrendPoint(BaseModel):
    period_start: datetime
    detected: int = Field(..., ge=0, description="Number of defects detected in this period.")
    resolved: int = Field(..., ge=0, description="Number of defects resolved in this period.")
    net_open: int = Field(..., ge=0, description="Running total of unresolved defects after this period.")
    change_open: Optional[int] = Field(
        None,
        description="Net change in open defects compared to the previous period.",
    )
    direction: TrendDirection


class PerformanceTrendPoint(BaseModel):
    period_start: datetime
    avg_response_time_ms: float = Field(..., ge=0, description="Average response time in milliseconds.")
    change_ms: Optional[float] = Field(
        None,
        description="Change in response time (ms) compared to the previous period.",
    )
    direction: TrendDirection
    sample_size: int = Field(..., ge=0, description="Number of samples included in the aggregation.")


class TrendSummary(BaseModel):
    """Summary metrics for the trend period."""
    total_executions: int = Field(..., ge=0, description="Total scenario executions in the period.")
    total_validations: int = Field(..., ge=0, description="Total validation results in the period.")
    avg_pass_rate_pct: float = Field(..., ge=0, le=100, description="Average pass rate across the period.")
    avg_response_time_ms: float = Field(..., ge=0, description="Average response time in milliseconds across the period.")
    response_time_samples: int = Field(..., ge=0, description="Number of response time samples.")


class TrendAnalyticsResponse(BaseModel):
    pass_rate: List[PassRateTrendPoint]
    defects: List[DefectTrendPoint]
    performance: List[PerformanceTrendPoint]
    summary: Optional[TrendSummary] = Field(None, description="Summary metrics for the time period.")
