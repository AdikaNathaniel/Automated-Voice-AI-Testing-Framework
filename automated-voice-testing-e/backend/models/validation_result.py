"""
ValidationResult SQLAlchemy model for validation results.

This module defines the ValidationResult model which stores the results
of Houndify deterministic validation and LLM ensemble validation.

Validation Architecture:
    1. Houndify Deterministic Validation:
       - command_kind_match_score: 1.0 if CommandKind matches, 0.0 otherwise
       - asr_confidence_score: Houndify's ASR confidence (0.0 to 1.0)
       - Response content validation (contains, not_contains, regex patterns)
       - houndify_passed: Overall Houndify validation pass/fail
       - houndify_result: Full Houndify validation details (JSONB)

    2. LLM Ensemble Validation:
       - llm_passed: Whether LLM ensemble passed
       - ensemble_result: Consensus and individual model decisions (JSONB)

    3. Combined Decision:
       - final_decision: pass, fail, or uncertain
       - review_status: auto_pass, auto_fail, or needs_review

Example:
    >>> result = ValidationResult(
    ...     suite_run_id=run.id,
    ...     command_kind_match_score=1.0,
    ...     asr_confidence_score=0.95,
    ...     houndify_passed=True,
    ...     llm_passed=True,
    ...     final_decision='pass',
    ...     review_status='auto_pass'
    ... )
"""

from typing import Optional, Dict, Any, TYPE_CHECKING

from sqlalchemy import Boolean, Column, Float, ForeignKey, String, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects import postgresql
from sqlalchemy import JSON
from sqlalchemy.orm import relationship

from models.base import Base, BaseModel, GUID

if TYPE_CHECKING:
    pass


# Use JSONB for PostgreSQL, JSON for SQLite (testing)
JSONB_TYPE = JSONB().with_variant(JSON(), "sqlite")

class ValidationResult(Base, BaseModel):
    """
    ValidationResult model for storing validation outcomes.

    Stores results from the two-stage validation pipeline:
    1. Houndify deterministic validation (CommandKind, ASR, response content)
    2. LLM ensemble validation (semantic understanding)

    Attributes:
        id (UUID): Unique identifier (inherited from BaseModel)
        tenant_id (UUID, optional): Tenant identifier for multi-tenant scoping
        suite_run_id (UUID): Foreign key to suite run (required)
        multi_turn_execution_id (UUID, optional): Link to multi-turn execution
        step_execution_id (UUID, optional): Link to step execution
        expected_outcome_id (UUID, optional): Link to expected outcome

        Houndify Validation:
            command_kind_match_score (float): 1.0 if matches, 0.0 otherwise
            asr_confidence_score (float): Houndify ASR confidence (0.0 to 1.0)
            houndify_passed (bool): Whether Houndify validation passed
            houndify_result (dict): Full Houndify validation details

        LLM Ensemble Validation:
            llm_passed (bool): Whether LLM ensemble passed
            ensemble_result (dict): Consensus and individual decisions

        Combined Decision:
            final_decision (str): pass, fail, or uncertain
            review_status (str): auto_pass, auto_fail, or needs_review
            language_code (str): Language code (e.g., en-US)
    """

    __tablename__ = 'validation_results'

    tenant_id = Column(
        GUID(),
        nullable=True,
        index=True,
        comment="Tenant identifier for multi-tenant scoping"
    )

    suite_run_id = Column(
        GUID(),
        ForeignKey('suite_runs.id'),
        nullable=True,
        index=True,
        comment="Optional suite run this validation belongs to (None for standalone scenarios)"
    )

    multi_turn_execution_id = Column(
        GUID(),
        ForeignKey('multi_turn_executions.id'),
        nullable=True,
        index=True,
        comment="Multi-turn execution this validation belongs to"
    )

    step_execution_id = Column(
        GUID(),
        ForeignKey('step_executions.id'),
        nullable=True,
        index=True,
        comment="Step execution validated in this result"
    )

    expected_outcome_id = Column(
        GUID(),
        ForeignKey('expected_outcomes.id'),
        nullable=True,
        index=True,
        comment="Expected outcome reference for this validation"
    )

    # Houndify deterministic validation scores
    command_kind_match_score = Column(
        Float,
        nullable=True,
        comment="CommandKind match: 1.0 if matches expected, 0.0 otherwise"
    )

    asr_confidence_score = Column(
        Float,
        nullable=True,
        comment="ASR confidence score from Houndify (0.0 to 1.0)"
    )

    houndify_passed = Column(
        Boolean,
        nullable=True,
        index=True,
        comment="Whether Houndify validation passed"
    )

    houndify_result = Column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        comment="Full Houndify validation result with all details"
    )

    # LLM ensemble validation
    llm_passed = Column(
        Boolean,
        nullable=True,
        index=True,
        comment="Whether LLM ensemble validation passed"
    )

    ensemble_result = Column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        comment="Ensemble judge result with consensus and individual decisions"
    )

    # Combined decision
    final_decision = Column(
        String(32),
        nullable=True,
        index=True,
        comment="Final combined decision: pass, fail, or uncertain"
    )

    review_status = Column(
        String(32),
        nullable=True,
        index=True,
        comment="auto_pass/needs_review/auto_fail status from validation"
    )

    language_code = Column(
        String(16),
        nullable=True,
        index=True,
        comment="Language code validated (e.g., en-US, es-ES, fr-FR)"
    )

    # Relationships
    suite_run = relationship(
        'SuiteRun',
        foreign_keys=[suite_run_id],
        primaryjoin="ValidationResult.suite_run_id == SuiteRun.id",
        lazy='joined'
    )

    multi_turn_execution = relationship(
        'MultiTurnExecution',
        foreign_keys=[multi_turn_execution_id],
        back_populates='validation_results',
        lazy='select'
    )

    step_execution = relationship(
        'StepExecution',
        foreign_keys=[step_execution_id],
        lazy='select'
    )

    expected_outcome = relationship(
        'ExpectedOutcome',
        back_populates='validation_results',
        foreign_keys=[expected_outcome_id],
        lazy='joined'
    )

    queue_items = relationship(
        "ValidationQueue",
        back_populates="validation_result",
        lazy='selectin',
    )

    human_validations = relationship(
        "HumanValidation",
        back_populates="validation_result",
        lazy='selectin',
    )

    def __repr__(self) -> str:
        """String representation of ValidationResult."""
        return (
            f"<ValidationResult(suite_run_id='{self.suite_run_id}', "
            f"final_decision='{self.final_decision}')>"
        )

    def get_houndify_scores(self) -> Dict[str, Any]:
        """
        Get Houndify validation scores.

        Returns:
            Dictionary with command_kind_match_score and asr_confidence_score
        """
        return {
            'command_kind_match_score': self.command_kind_match_score,
            'asr_confidence_score': self.asr_confidence_score,
        }

    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Get summary of all validation results.

        Returns:
            Dictionary with all validation fields
        """
        return {
            'houndify_passed': self.houndify_passed,
            'llm_passed': self.llm_passed,
            'final_decision': self.final_decision,
            'review_status': self.review_status,
            'command_kind_match_score': self.command_kind_match_score,
            'asr_confidence_score': self.asr_confidence_score,
        }
