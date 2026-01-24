"""
Pydantic schemas for validator performance tracking

This module defines Pydantic schemas for validator performance API operations
in the automated testing framework.

The module includes:
    - ValidatorPerformanceSchema: Full performance metrics with all fields
    - ValidatorPerformanceCreate: Schema for creating performance records
    - ValidatorPerformanceUpdate: Schema for updating performance records

Example:
    >>> from api.schemas.validator_performance import ValidatorPerformanceSchema
    >>>
    >>> performance = ValidatorPerformanceSchema(
    ...     id=uuid4(),
    ...     user_id=uuid4(),
    ...     total_validations=100,
    ...     accuracy_rate=0.95
    ... )
"""

from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ValidatorPerformanceBase(BaseModel):
    """
    Base schema for validator performance fields.

    Contains common fields shared across create/update/response schemas.
    """

    user_id: UUID = Field(..., description="User this performance record belongs to")
    total_validations: int = Field(
        0,
        description="Total number of validations completed",
        ge=0
    )
    accuracy_rate: Optional[float] = Field(
        None,
        description="Accuracy rate (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    avg_time_per_validation: Optional[float] = Field(
        None,
        description="Average time per validation in seconds",
        ge=0.0
    )
    validations_today: int = Field(
        0,
        description="Validations completed today",
        ge=0
    )
    validations_this_week: int = Field(
        0,
        description="Validations completed this week",
        ge=0
    )
    validations_this_month: int = Field(
        0,
        description="Validations completed this month",
        ge=0
    )
    agreement_rate: Optional[float] = Field(
        None,
        description="Agreement rate with other validators (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    languages: Optional[Dict[str, int]] = Field(
        None,
        description="Language codes and validation counts"
    )
    performance_metrics: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional performance metrics"
    )


class ValidatorPerformanceCreate(ValidatorPerformanceBase):
    """
    Schema for creating a new validator performance record.

    Example:
        >>> create_data = ValidatorPerformanceCreate(
        ...     user_id=uuid4(),
        ...     total_validations=0
        ... )
    """

    pass


class ValidatorPerformanceUpdate(BaseModel):
    """
    Schema for updating validator performance.

    All fields are optional to allow partial updates.
    """

    total_validations: Optional[int] = Field(None, ge=0)
    accuracy_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    avg_time_per_validation: Optional[float] = Field(None, ge=0.0)
    validations_today: Optional[int] = Field(None, ge=0)
    validations_this_week: Optional[int] = Field(None, ge=0)
    validations_this_month: Optional[int] = Field(None, ge=0)
    agreement_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    languages: Optional[Dict[str, int]] = None
    performance_metrics: Optional[Dict[str, Any]] = None


class ValidatorPerformanceSchema(ValidatorPerformanceBase):
    """
    Full validator performance schema with all fields.

    Used for API responses containing complete performance data.

    Example:
        >>> performance = ValidatorPerformanceSchema(
        ...     id=uuid4(),
        ...     user_id=uuid4(),
        ...     total_validations=100,
        ...     accuracy_rate=0.95,
        ...     avg_time_per_validation=45.5,
        ...     created_at=datetime.now()
        ... )
    """

    id: UUID = Field(..., description="Unique identifier")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)
