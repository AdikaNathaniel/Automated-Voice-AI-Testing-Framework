"""
LLM Analytics API Schemas

Response models for LLM cost analytics and usage tracking endpoints.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class DailyCostSummary(BaseModel):
    """Daily cost summary for a specific date."""

    date: str = Field(description="Date in YYYY-MM-DD format")
    total_calls: int = Field(description="Total API calls made")
    total_tokens: int = Field(description="Total tokens used")
    prompt_tokens: int = Field(description="Total prompt tokens")
    completion_tokens: int = Field(description="Total completion tokens")
    total_cost_usd: float = Field(description="Total cost in USD")
    successful_calls: int = Field(description="Number of successful calls")
    failed_calls: int = Field(description="Number of failed calls")


class OperationCostBreakdown(BaseModel):
    """Cost breakdown by operation type."""

    operation: str = Field(description="Operation name")
    total_calls: int = Field(description="Number of calls")
    total_tokens: int = Field(description="Total tokens used")
    total_cost_usd: float = Field(description="Total cost in USD")
    avg_tokens_per_call: float = Field(description="Average tokens per call")
    avg_cost_per_call: float = Field(description="Average cost per call in USD")
    avg_duration_ms: float = Field(description="Average duration in milliseconds")


class ModelCostBreakdown(BaseModel):
    """Cost breakdown by model."""

    model: str = Field(description="Model name")
    provider: str = Field(description="Provider name")
    total_calls: int = Field(description="Number of calls")
    total_tokens: int = Field(description="Total tokens used")
    total_cost_usd: float = Field(description="Total cost in USD")
    avg_tokens_per_call: float = Field(description="Average tokens per call")
    avg_cost_per_call: float = Field(description="Average cost per call in USD")


class LLMCostSummary(BaseModel):
    """Overall LLM cost summary."""

    total_calls: int = Field(description="Total API calls")
    total_tokens: int = Field(description="Total tokens used")
    total_cost_usd: float = Field(description="Total cost in USD")
    successful_calls: int = Field(description="Successful calls")
    failed_calls: int = Field(description="Failed calls")
    success_rate: float = Field(description="Success rate percentage")
    avg_cost_per_call: float = Field(description="Average cost per call in USD")
    avg_tokens_per_call: float = Field(description="Average tokens per call")
    period_start: str = Field(description="Start of analysis period")
    period_end: str = Field(description="End of analysis period")


class DailyCostsResponse(BaseModel):
    """Response for daily costs endpoint."""

    summary: LLMCostSummary
    daily_costs: List[DailyCostSummary]


class OperationBreakdownResponse(BaseModel):
    """Response for operation breakdown endpoint."""

    summary: LLMCostSummary
    operations: List[OperationCostBreakdown]


class ModelBreakdownResponse(BaseModel):
    """Response for model breakdown endpoint."""

    summary: LLMCostSummary
    models: List[ModelCostBreakdown]


class RecentCallLog(BaseModel):
    """Recent LLM call log entry."""

    id: str
    created_at: str
    operation: str
    model: str
    total_tokens: int
    estimated_cost_usd: float
    duration_ms: Optional[int]
    success: bool
    error_message: Optional[str]


class RecentCallsResponse(BaseModel):
    """Response for recent calls endpoint."""

    calls: List[RecentCallLog]
    total_count: int
