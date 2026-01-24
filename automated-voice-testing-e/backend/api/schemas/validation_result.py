"""
Pydantic schemas for validation results.

This module defines Pydantic schemas for validation result API operations.

Validation Architecture:
    1. Houndify Deterministic Validation:
       - command_kind_match_score: 1.0 if CommandKind matches, 0.0 otherwise
       - asr_confidence_score: Houndify's ASR confidence (0.0 to 1.0)
       - houndify_passed: Overall pass/fail
       - houndify_result: Full validation details (JSONB)

    2. LLM Ensemble Validation:
       - llm_passed: Whether LLM ensemble passed
       - ensemble_result: Consensus and individual decisions

    3. Combined Decision:
       - final_decision: pass, fail, or uncertain
       - review_status: auto_pass, auto_fail, or needs_review

Example:
    >>> result = ValidationResultSchema(
    ...     id=uuid4(),
    ...     suite_run_id=uuid4(),
    ...     command_kind_match_score=1.0,
    ...     asr_confidence_score=0.95,
    ...     houndify_passed=True,
    ...     final_decision='pass',
    ...     review_status='auto_pass'
    ... )
"""

from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ValidationResultBase(BaseModel):
    """
    Base schema for validation result fields.

    Contains fields for Houndify and LLM ensemble validation.
    """

    suite_run_id: UUID = Field(..., description="Suite run this validation belongs to")

    multi_turn_execution_id: Optional[UUID] = Field(
        None,
        description="Multi-turn execution validated"
    )
    expected_outcome_id: Optional[UUID] = Field(
        None,
        description="Expected outcome reference"
    )

    # Houndify deterministic validation
    command_kind_match_score: Optional[float] = Field(
        None,
        description="CommandKind match: 1.0 = match, 0.0 = mismatch",
        ge=0.0,
        le=1.0
    )
    asr_confidence_score: Optional[float] = Field(
        None,
        description="ASR confidence score from Houndify (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    houndify_passed: Optional[bool] = Field(
        None,
        description="Whether Houndify validation passed"
    )
    houndify_result: Optional[Dict[str, Any]] = Field(
        None,
        description="Full Houndify validation result with details"
    )

    # LLM ensemble validation
    llm_passed: Optional[bool] = Field(
        None,
        description="Whether LLM ensemble validation passed"
    )
    ensemble_result: Optional[Dict[str, Any]] = Field(
        None,
        description="LLM ensemble result with consensus and individual decisions"
    )

    # Combined decision
    final_decision: Optional[str] = Field(
        None,
        description="Final combined decision: pass, fail, or uncertain"
    )
    review_status: Optional[str] = Field(
        None,
        description="Review status: auto_pass, needs_review, auto_fail"
    )
    language_code: Optional[str] = Field(
        None,
        description="Language code for the validation (e.g., en-US, es-ES)"
    )


class ValidationResultCreate(ValidationResultBase):
    """
    Schema for creating a new validation result.

    Example:
        >>> create_data = ValidationResultCreate(
        ...     suite_run_id=uuid4(),
        ...     command_kind_match_score=1.0,
        ...     houndify_passed=True
        ... )
    """
    pass


class ValidationResultUpdate(BaseModel):
    """
    Schema for updating a validation result.

    All fields are optional to allow partial updates.
    """

    # Houndify validation
    command_kind_match_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    asr_confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    houndify_passed: Optional[bool] = None
    houndify_result: Optional[Dict[str, Any]] = None

    # LLM ensemble validation
    llm_passed: Optional[bool] = None
    ensemble_result: Optional[Dict[str, Any]] = None

    # Combined decision
    final_decision: Optional[str] = None
    review_status: Optional[str] = None
    language_code: Optional[str] = None


class ValidationResultSchema(ValidationResultBase):
    """
    Full validation result schema with all fields.

    Used for API responses containing complete validation result data.

    Example:
        >>> result = ValidationResultSchema(
        ...     id=uuid4(),
        ...     suite_run_id=uuid4(),
        ...     command_kind_match_score=1.0,
        ...     houndify_passed=True,
        ...     final_decision='pass',
        ...     review_status='auto_pass'
        ... )
    """

    id: UUID = Field(..., description="Unique identifier")
    tenant_id: Optional[UUID] = Field(None, description="Tenant identifier")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)
