"""
Pydantic schemas for expected outcomes

This module defines Pydantic schemas for expected outcome API operations
in the automated testing framework.

The module includes:
    - ExpectedOutcomeSchema: Full expected outcome with all fields
    - ExpectedOutcomeCreate: Schema for creating expected outcomes
    - ExpectedOutcomeUpdate: Schema for updating expected outcomes

Example:
    >>> from api.schemas.expected_outcome import ExpectedOutcomeSchema
    >>>
    >>> outcome = ExpectedOutcomeSchema(
    ...     id=uuid4(),
    ...     outcome_code='NAVIGATE_HOME',
    ...     name='Navigate to Home',
    ...     entities={'action': 'navigate', 'destination': 'home'}
    ... )
"""

from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ExpectedOutcomeBase(BaseModel):
    """
    Base schema for expected outcome fields.

    Contains common fields shared across create/update/response schemas.
    """

    outcome_code: str = Field(
        ...,
        description="Unique code identifying this expected outcome",
        max_length=100
    )
    name: str = Field(
        ...,
        description="Human-readable name of the outcome",
        max_length=255
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description of the expected outcome"
    )
    entities: Optional[Dict[str, Any]] = Field(
        None,
        description="Expected entities to be extracted"
    )
    validation_rules: Optional[Dict[str, Any]] = Field(
        None,
        description="Validation rules for verifying outcome"
    )
    language_variations: Optional[Dict[str, Any]] = Field(
        None,
        description="Language-specific variations"
    )
    scenario_step_id: Optional[UUID] = Field(
        None,
        description="Reference to the scenario step"
    )
    acceptable_alternates: Optional[List[str]] = Field(
        None,
        description="List of acceptable alternate responses"
    )
    confirmation_required: bool = Field(
        False,
        description="Whether confirmation is required"
    )
    confirmation_prompt: Optional[str] = Field(
        None,
        description="The expected confirmation prompt"
    )
    allow_partial_success: bool = Field(
        False,
        description="Whether partial success is acceptable"
    )
    tolerance_settings: Optional[Dict[str, Any]] = Field(
        None,
        description="Tolerance settings for validation"
    )
    tolerance_config: Optional[Dict[str, Any]] = Field(
        None,
        description="Complete tolerance configuration"
    )
    required_entities: Optional[List[str]] = Field(
        None,
        description="List of entities that must be present"
    )
    forbidden_phrases: Optional[List[str]] = Field(
        None,
        description="List of phrases that must not appear"
    )
    tone_requirement: Optional[str] = Field(
        None,
        description="Required tone for response",
        max_length=100
    )
    max_response_length: Optional[int] = Field(
        None,
        description="Maximum allowed response length",
        ge=0
    )
    next_step_on_success: Optional[UUID] = Field(
        None,
        description="Next step ID on successful validation"
    )
    next_step_on_failure: Optional[UUID] = Field(
        None,
        description="Next step ID on failed validation"
    )
    recovery_path: Optional[Dict[str, Any]] = Field(
        None,
        description="Recovery path configuration"
    )
    scenario_metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional scenario-specific metadata"
    )
    dynamic_context: Optional[Dict[str, Any]] = Field(
        None,
        description="Dynamic context for resolving references"
    )


class ExpectedOutcomeCreate(ExpectedOutcomeBase):
    """
    Schema for creating a new expected outcome.

    Example:
        >>> create_data = ExpectedOutcomeCreate(
        ...     outcome_code='NAVIGATE_HOME',
        ...     name='Navigate to Home',
        ...     entities={'action': 'navigate', 'destination': 'home'}
        ... )
    """

    pass


class ExpectedOutcomeUpdate(BaseModel):
    """
    Schema for updating an expected outcome.

    All fields are optional to allow partial updates.
    """

    outcome_code: Optional[str] = Field(None, max_length=100)
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    entities: Optional[Dict[str, Any]] = None
    validation_rules: Optional[Dict[str, Any]] = None
    language_variations: Optional[Dict[str, Any]] = None
    scenario_step_id: Optional[UUID] = None
    acceptable_alternates: Optional[List[str]] = None
    confirmation_required: Optional[bool] = None
    confirmation_prompt: Optional[str] = None
    allow_partial_success: Optional[bool] = None
    tolerance_settings: Optional[Dict[str, Any]] = None
    tolerance_config: Optional[Dict[str, Any]] = None
    required_entities: Optional[List[str]] = None
    forbidden_phrases: Optional[List[str]] = None
    tone_requirement: Optional[str] = Field(None, max_length=100)
    max_response_length: Optional[int] = Field(None, ge=0)
    next_step_on_success: Optional[UUID] = None
    next_step_on_failure: Optional[UUID] = None
    recovery_path: Optional[Dict[str, Any]] = None
    scenario_metadata: Optional[Dict[str, Any]] = None
    dynamic_context: Optional[Dict[str, Any]] = None


class ExpectedOutcomeSchema(ExpectedOutcomeBase):
    """
    Full expected outcome schema with all fields.

    Used for API responses containing complete expected outcome data.

    Example:
        >>> outcome = ExpectedOutcomeSchema(
        ...     id=uuid4(),
        ...     outcome_code='NAVIGATE_HOME',
        ...     name='Navigate to Home',
        ...     entities={'action': 'navigate', 'destination': 'home'},
        ...     created_at=datetime.now()
        ... )
    """

    id: UUID = Field(..., description="Unique identifier")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)
