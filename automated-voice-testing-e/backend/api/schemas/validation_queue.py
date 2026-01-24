"""
Pydantic schemas for validation queue management

This module defines Pydantic schemas for validation queue API operations
in the automated testing framework.

The module includes:
    - ValidationQueueSchema: Full queue item with all fields
    - ValidationQueueCreate: Schema for creating queue items
    - ValidationQueueUpdate: Schema for updating queue items

Example:
    >>> from api.schemas.validation_queue import ValidationQueueSchema
    >>>
    >>> queue_item = ValidationQueueSchema(
    ...     id=uuid4(),
    ...     validation_result_id=uuid4(),
    ...     priority=3,
    ...     status='pending'
    ... )
"""

from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class ValidationQueueBase(BaseModel):
    """
    Base schema for validation queue fields.

    Contains common fields shared across create/update/response schemas.
    """

    validation_result_id: UUID = Field(
        ...,
        description="Reference to the validation result to be reviewed"
    )
    priority: int = Field(
        5,
        description="Priority level (1=highest, 10=lowest)",
        ge=1,
        le=10
    )
    confidence_score: Optional[Decimal] = Field(
        None,
        description="AI confidence score (0.00-100.00)",
        ge=0,
        le=100
    )
    language_code: Optional[str] = Field(
        None,
        description="Language code for validator matching",
        max_length=10
    )
    status: str = Field(
        'pending',
        description="Queue status: pending, claimed, completed"
    )
    requires_native_speaker: bool = Field(
        False,
        description="Whether this task requires a native speaker"
    )


class ValidationQueueCreate(ValidationQueueBase):
    """
    Schema for creating a new validation queue item.

    Example:
        >>> create_data = ValidationQueueCreate(
        ...     validation_result_id=uuid4(),
        ...     priority=3,
        ...     language_code='es-MX'
        ... )
    """

    pass


class ValidationQueueUpdate(BaseModel):
    """
    Schema for updating a validation queue item.

    All fields are optional to allow partial updates.
    """

    priority: Optional[int] = Field(None, ge=1, le=10)
    confidence_score: Optional[Decimal] = Field(None, ge=0, le=100)
    language_code: Optional[str] = Field(None, max_length=10)
    claimed_by: Optional[UUID] = None
    claimed_at: Optional[datetime] = None
    status: Optional[str] = None
    requires_native_speaker: Optional[bool] = None


class ValidationQueueSchema(ValidationQueueBase):
    """
    Full validation queue schema with all fields.

    Used for API responses containing complete queue item data.

    Example:
        >>> queue_item = ValidationQueueSchema(
        ...     id=uuid4(),
        ...     validation_result_id=uuid4(),
        ...     priority=3,
        ...     status='pending',
        ...     language_code='en-US',
        ...     created_at=datetime.now()
        ... )
    """

    id: UUID = Field(..., description="Unique identifier")
    claimed_by: Optional[UUID] = Field(
        None,
        description="User who claimed this task"
    )
    claimed_at: Optional[datetime] = Field(
        None,
        description="When the task was claimed"
    )
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)
