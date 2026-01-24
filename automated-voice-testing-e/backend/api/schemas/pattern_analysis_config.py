"""
Pydantic schemas for pattern analysis configuration API.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class PatternAnalysisConfigBase(BaseModel):
    """Base schema with shared configuration fields."""

    lookback_days: int = Field(
        default=30,
        ge=1,
        le=365,
        description="Maximum age of edge cases to analyze (in days)"
    )
    min_pattern_size: int = Field(
        default=3,
        ge=2,
        le=50,
        description="Minimum edge cases required to form a pattern"
    )
    similarity_threshold: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0,
        description="Semantic similarity threshold"
    )
    defect_auto_creation_threshold: int = Field(
        default=3,
        ge=1,
        le=100,
        description="Number of consecutive auto_fail results before creating defect"
    )
    enable_llm_analysis: bool = Field(
        default=True,
        description="Whether to use LLM-powered analysis"
    )
    llm_confidence_threshold: float = Field(
        default=0.70,
        ge=0.0,
        le=1.0,
        description="Minimum LLM confidence for pattern matching"
    )
    analysis_schedule: str = Field(
        default="0 2 * * *",
        description="Cron expression for analysis schedule"
    )
    enable_auto_analysis: bool = Field(
        default=True,
        description="Whether to run automatic pattern analysis"
    )
    notify_on_new_patterns: bool = Field(
        default=True,
        description="Send notifications when new patterns discovered"
    )
    notify_on_critical_patterns: bool = Field(
        default=True,
        description="Send alerts for critical severity patterns"
    )
    response_time_sla_ms: int = Field(
        default=2000,
        ge=100,
        le=30000,
        description="Response time SLA threshold in milliseconds for performance monitoring"
    )

class PatternAnalysisConfigCreate(PatternAnalysisConfigBase):
    """Schema for creating a new pattern analysis configuration."""

    tenant_id: UUID = Field(description="Organization/tenant ID")


class PatternAnalysisConfigUpdate(BaseModel):
    """Schema for updating pattern analysis configuration (all fields optional)."""

    lookback_days: Optional[int] = Field(default=None, ge=1, le=365)
    min_pattern_size: Optional[int] = Field(default=None, ge=2, le=50)
    similarity_threshold: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    defect_auto_creation_threshold: Optional[int] = Field(default=None, ge=1, le=100)
    enable_llm_analysis: Optional[bool] = None
    llm_confidence_threshold: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    analysis_schedule: Optional[str] = None
    enable_auto_analysis: Optional[bool] = None
    notify_on_new_patterns: Optional[bool] = None
    notify_on_critical_patterns: Optional[bool] = None
    response_time_sla_ms: Optional[int] = Field(default=None, ge=100, le=30000)


class PatternAnalysisConfigResponse(PatternAnalysisConfigBase):
    """Schema for pattern analysis configuration responses."""

    id: UUID
    tenant_id: Optional[UUID] = Field(
        default=None,
        description="Organization/tenant ID (null for global defaults)"
    )
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ManualAnalysisRequest(BaseModel):
    """Schema for triggering manual pattern analysis with optional overrides."""

    overrides: Optional[dict] = Field(
        default=None,
        description="Optional parameter overrides for this run"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "overrides": {
                    "lookback_days": 14,
                    "min_pattern_size": 2,
                    "similarity_threshold": 0.80
                }
            }
        }


class ManualAnalysisResponse(BaseModel):
    """Schema for manual analysis trigger response."""

    status: str = Field(description="Status of the request (queued, running, etc.)")
    task_id: str = Field(description="Celery task ID for tracking")
    message: str = Field(description="Human-readable status message")
