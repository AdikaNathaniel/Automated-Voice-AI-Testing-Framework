"""
Pydantic schemas for edge case library API.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EdgeCaseCreate(BaseModel):
    """Payload for creating a new edge case."""

    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    scenario_definition: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    severity: Optional[str] = Field(default=None, max_length=50)
    category: Optional[str] = Field(default=None, max_length=100)
    status: Optional[str] = Field(default="active", max_length=50)
    script_id: Optional[UUID] = Field(default=None, description="Scenario script that exhibits this edge case")
    discovered_date: Optional[date] = None
    discovered_by: Optional[UUID] = None


class EdgeCaseUpdate(BaseModel):
    """Payload for updating existing edge case fields."""

    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    scenario_definition: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    severity: Optional[str] = Field(default=None, max_length=50)
    category: Optional[str] = Field(default=None, max_length=100)
    status: Optional[str] = Field(default=None, max_length=50)
    script_id: Optional[UUID] = None
    discovered_date: Optional[date] = None
    discovered_by: Optional[UUID] = None


class EdgeCaseCategorizeRequest(BaseModel):
    """Payload for categorisation endpoint."""

    signals: Dict[str, Any] = Field(default_factory=dict)


class EdgeCaseResponse(BaseModel):
    """Response model representing an edge case record."""

    id: UUID
    title: str
    description: Optional[str] = None
    scenario_definition: Dict[str, Any]
    tags: List[str]
    severity: Optional[str] = None
    category: Optional[str] = None
    status: str
    script_id: Optional[UUID] = None
    discovered_date: Optional[date] = None
    discovered_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EdgeCaseListResponse(BaseModel):
    """Response envelope when returning a collection of edge cases."""

    total: int
    items: List[EdgeCaseResponse]


# ---------------------------------------------------------------------
# Analytics schemas (Phase 5)
# ---------------------------------------------------------------------

class DateRangeSchema(BaseModel):
    """Date range for analytics queries."""

    from_date: str = Field(..., alias="from")
    to_date: str = Field(..., alias="to")

    model_config = ConfigDict(populate_by_name=True)


class AnalyticsSummary(BaseModel):
    """Summary metrics for edge cases."""

    total_in_range: int = Field(description="Edge cases created in date range")
    total_all_time: int = Field(description="Total edge cases ever")
    active_count: int = Field(description="Currently active edge cases")
    resolved_in_range: int = Field(description="Edge cases resolved in date range")
    critical_active: int = Field(description="Active critical severity edge cases")


class TimeSeriesPoint(BaseModel):
    """Single data point for time series charts."""

    date: str
    count: int
    cumulative: int


class DistributionItem(BaseModel):
    """Distribution item with count and percentage."""

    category: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    count: int
    percentage: float


class ResolutionMetrics(BaseModel):
    """Edge case resolution metrics."""

    total_created: int
    resolved: int
    active: int
    wont_fix: int
    resolution_rate_percent: float


class TopPattern(BaseModel):
    """Top pattern group with edge case counts."""

    id: str
    name: str
    pattern_type: Optional[str] = None
    severity: str
    occurrence_count: int
    linked_edge_cases: int


class AutoVsManual(BaseModel):
    """Breakdown of auto-created vs manually-created edge cases."""

    auto_created: int
    manually_created: int
    auto_created_percent: float
    manually_created_percent: float


class TrendPeriod(BaseModel):
    """Metrics for a single trend period."""

    from_date: str = Field(..., alias="from")
    to_date: str = Field(..., alias="to")
    count: int

    model_config = ConfigDict(populate_by_name=True)


class TrendComparison(BaseModel):
    """Comparison between current and previous period."""

    current_period: TrendPeriod
    previous_period: TrendPeriod
    change: int
    change_percent: float
    trend: str = Field(description="up, down, or stable")


class EdgeCaseAnalyticsResponse(BaseModel):
    """Complete analytics response for edge cases."""

    date_range: DateRangeSchema
    summary: AnalyticsSummary
    count_over_time: List[TimeSeriesPoint]
    category_distribution: List[DistributionItem]
    severity_distribution: List[DistributionItem]
    status_distribution: List[DistributionItem]
    resolution_metrics: ResolutionMetrics
    top_patterns: List[TopPattern]
    auto_vs_manual: AutoVsManual
    trend_comparison: Optional[TrendComparison] = None
