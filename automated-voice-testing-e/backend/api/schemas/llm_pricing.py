"""
LLM Pricing API Schemas

Request and response models for LLM pricing management.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class LLMPricingBase(BaseModel):
    """Base schema for LLM pricing."""
    model_name: str = Field(..., min_length=1, max_length=100, description="Name of the LLM model")
    provider: str = Field(..., min_length=1, max_length=50, description="API provider")
    prompt_price_per_1m: float = Field(..., ge=0, description="Price per 1M prompt tokens in USD")
    completion_price_per_1m: float = Field(..., ge=0, description="Price per 1M completion tokens in USD")
    notes: Optional[str] = Field(None, description="Optional notes about this pricing")

    @field_validator("prompt_price_per_1m", "completion_price_per_1m")
    @classmethod
    def validate_price(cls, v):
        """Validate price is reasonable."""
        if v < 0:
            raise ValueError("Price cannot be negative")
        if v > 1000:  # $1000 per 1M tokens seems unreasonable
            raise ValueError("Price seems unreasonably high")
        return v


class LLMPricingCreate(LLMPricingBase):
    """Schema for creating new LLM pricing."""
    effective_date: Optional[datetime] = Field(None, description="When this pricing becomes effective")
    is_active: bool = Field(True, description="Whether this pricing is active")


class LLMPricingUpdate(BaseModel):
    """Schema for updating LLM pricing."""
    prompt_price_per_1m: Optional[float] = Field(None, ge=0)
    completion_price_per_1m: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    effective_date: Optional[datetime] = None


class LLMPricingResponse(LLMPricingBase):
    """Schema for LLM pricing response."""
    id: UUID
    is_active: bool
    effective_date: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LLMPricingListResponse(BaseModel):
    """Schema for list of LLM pricing."""
    pricing: List[LLMPricingResponse]
    total: int


class AuditTrailResponse(BaseModel):
    """Schema for audit trail response."""
    id: UUID
    tenant_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    action_type: str
    resource_type: str
    resource_id: Optional[str] = None
    old_values: Optional[dict] = None
    new_values: Optional[dict] = None
    changes_summary: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AuditTrailListResponse(BaseModel):
    """Schema for list of audit trail entries."""
    audits: List[AuditTrailResponse]
    total: int
