"""
MultiTurnExecution and StepExecution SQLAlchemy models for multi-turn conversation tracking.

This module defines models for tracking multi-turn scenario execution with:
- Conversation state management across multiple steps
- Step-by-step execution tracking
- Houndify conversation state persistence
- Validation results for each step

Example:
    >>> from models.multi_turn_execution import MultiTurnExecution, StepExecution
    >>>
    >>> # Create a multi-turn execution
    >>> execution = MultiTurnExecution(
    ...     suite_run_id=suite_run.id,
    ...     script_id=script.id,
    ...     user_id="test_user_123",
    ...     status="in_progress"
    ... )
    >>>
    >>> # Add step execution
    >>> step = StepExecution(
    ...     multi_turn_execution_id=execution.id,
    ...     step_id=scenario_step.id,
    ...     step_order=1,
    ...     user_utterance="I want to make a reservation"
    ... )
"""

from datetime import datetime
from typing import Optional, Dict, Any, TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Column, String, Text, Integer, ForeignKey, Float, Boolean, DateTime
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSON

from sqlalchemy.orm import relationship

from models.base import Base, BaseModel, GUID

if TYPE_CHECKING:
    pass


class MultiTurnExecution(Base, BaseModel):
    """
    MultiTurnExecution model for tracking multi-turn scenario execution.

    Represents a complete multi-turn conversation execution with conversation
    state tracking and step-by-step results.

    Attributes:
        id (UUID): Unique identifier (inherited from BaseModel)
        suite_run_id (UUID): Foreign key to suite run
        script_id (UUID): Foreign key to scenario script
        user_id (str): Houndify user_id for conversation tracking
        conversation_state_id (str, optional): ConversationStateId from Houndify
        current_step_order (int): Current step being executed
        total_steps (int): Total number of steps in scenario
        status (str): Execution status (in_progress, completed, failed, cancelled)
        conversation_state (dict): Full conversation state from Houndify (JSONB)
        started_at (datetime): When execution started
        completed_at (datetime, optional): When execution completed
        error_message (str, optional): Error message if execution failed
        step_executions (List[StepExecution]): Relationship to step executions
        created_at (datetime): Creation timestamp (inherited)
        updated_at (datetime): Last update timestamp (inherited)

    Example:
        >>> execution = MultiTurnExecution(
        ...     suite_run_id=suite_run.id,
        ...     script_id=script.id,
        ...     user_id="test_user_123",
        ...     total_steps=5,
        ...     status="in_progress"
        ... )
    """

    __tablename__ = 'multi_turn_executions'

    tenant_id = Column(
        GUID(),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Tenant (organization or user) that owns this execution"
    )

    suite_run_id = Column(
        GUID(),
        ForeignKey('suite_runs.id'),
        nullable=True,
        index=True,
        comment="Optional suite run this execution belongs to (None for standalone scenarios)"
    )

    script_id = Column(
        GUID(),
        ForeignKey('scenario_scripts.id'),
        nullable=False,
        index=True,
        comment="Scenario script being executed"
    )

    suite_id = Column(
        GUID(),
        ForeignKey('test_suites.id'),
        nullable=True,
        index=True,
        comment="Test suite this execution belongs to (nullable - not all executions are from suites)"
    )

    user_id = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Houndify user_id for conversation tracking"
    )

    conversation_state_id = Column(
        String(255),
        nullable=True,
        index=True,
        comment="ConversationStateId from Houndify"
    )

    current_step_order = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Current step being executed (0 = not started)"
    )

    total_steps = Column(
        Integer,
        nullable=False,
        comment="Total number of steps in scenario"
    )

    status = Column(
        String(50),
        nullable=False,
        default='pending',
        index=True,
        comment="Execution status: pending, in_progress, completed, failed, cancelled"
    )

    conversation_state = Column(
        postgresql.JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        comment="Full conversation state from Houndify (JSONB)"
    )

    started_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When execution started"
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When execution completed"
    )

    error_message = Column(
        Text,
        nullable=True,
        comment="Error message if execution failed"
    )

    # Relationships
    suite_run = relationship(
        'SuiteRun',
        foreign_keys=[suite_run_id],
        back_populates='scenario_executions',
        lazy='select'
    )

    script = relationship(
        'ScenarioScript',
        foreign_keys=[script_id],
        lazy='select'
    )

    suite = relationship(
        'TestSuite',
        foreign_keys=[suite_id],
        back_populates='multi_turn_executions',
        lazy='select'
    )

    step_executions = relationship(
        'StepExecution',
        back_populates='multi_turn_execution',
        cascade='all, delete-orphan',
        order_by='StepExecution.step_order',
        lazy='select'
    )

    # Validation results for this execution (one-to-many: one per language variant)
    validation_results = relationship(
        'ValidationResult',
        foreign_keys='ValidationResult.multi_turn_execution_id',
        back_populates='multi_turn_execution',
        lazy='selectin'
    )

    @property
    def pending_validation_queue_item(self):
        """Get pending validation queue item from any validation result.

        Checks both the validation_results relationship and any manually
        attached validation_result attribute (set by attach_validation_metadata).
        """
        # Build list of validation results to check
        results_to_check = list(self.validation_results) if self.validation_results else []

        # Also check manually attached validation_result (singular)
        # This is set by attach_validation_metadata in execution_scheduler_service
        manual_result = getattr(self, 'validation_result', None)
        if manual_result and manual_result not in results_to_check:
            results_to_check.append(manual_result)

        if not results_to_check:
            return None

        # Check all validation results for pending queue items
        for validation_result in results_to_check:
            queue_items = getattr(validation_result, 'queue_items', [])
            for item in queue_items:
                if getattr(item, 'status', None) == 'pending':
                    return item
        return None

    @property
    def input_audio_url(self) -> Optional[str]:
        """Get input audio URL from the first step execution."""
        if not self.step_executions:
            return None
        first_step = self.step_executions[0] if self.step_executions else None
        if first_step and first_step.audio_data_urls:
            # audio_data_urls is a dict like {'en-US': 'http://...'}
            # Return the first URL found
            for url in first_step.audio_data_urls.values():
                return url
        return None

    @property
    def response_audio_url(self) -> Optional[str]:
        """
        Get response audio URL from the last step execution.

        For backward compatibility, returns the first URL found in response_audio_urls dict.
        Prefer using get_response_audio_url(language_code) for multi-language scenarios.
        """
        if not self.step_executions:
            return None
        last_step = self.step_executions[-1] if self.step_executions else None
        if last_step and hasattr(last_step, 'response_audio_urls') and last_step.response_audio_urls:
            # Return the first URL found in the dict
            for url in last_step.response_audio_urls.values():
                return url
        return None

    def get_response_audio_url(self, language_code: str) -> Optional[str]:
        """
        Get response audio URL for a specific language from the last step execution.

        Args:
            language_code: Language code (e.g., 'en-US', 'es-ES')

        Returns:
            Response audio URL for the specified language, or None if not found
        """
        if not self.step_executions:
            return None
        last_step = self.step_executions[-1] if self.step_executions else None
        if last_step and hasattr(last_step, 'response_audio_urls') and last_step.response_audio_urls:
            return last_step.response_audio_urls.get(language_code)
        return None

    @property
    def latest_human_validation(self):
        """Get the latest human validation from all validation results.

        Checks both the validation_results relationship and any manually
        attached validation_result attribute (set by attach_validation_metadata).
        """
        # Build list of validation results to check
        results_to_check = list(self.validation_results) if self.validation_results else []

        # Also check manually attached validation_result (singular)
        manual_result = getattr(self, 'validation_result', None)
        if manual_result and manual_result not in results_to_check:
            results_to_check.append(manual_result)

        if not results_to_check:
            return None

        # Collect all human validations from all validation results
        all_human_validations = []
        for validation_result in results_to_check:
            human_validations = getattr(validation_result, 'human_validations', [])
            all_human_validations.extend(human_validations)
        if not all_human_validations:
            return None
        # Return the most recent one (by submitted_at or created_at)
        return max(all_human_validations, key=lambda hv: hv.submitted_at or hv.created_at, default=None)

    @property
    def is_completed(self) -> bool:
        """Check if execution is completed."""
        return self.status == 'completed'

    @property
    def is_failed(self) -> bool:
        """Check if execution failed."""
        return self.status == 'failed'

    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        if self.total_steps == 0:
            return 0.0
        return (self.current_step_order / self.total_steps) * 100.0

    @property
    def all_steps_passed(self) -> bool:
        """Check if all steps in the execution passed validation."""
        if not self.step_executions:
            return False
        return all(
            step.validation_passed is True
            for step in self.step_executions
        )


class StepExecution(Base, BaseModel):
    """
    StepExecution model for tracking individual step execution within multi-turn scenario.

    Represents a single conversation turn with request/response data,
    conversation state, and validation results.

    Attributes:
        id (UUID): Unique identifier (inherited from BaseModel)
        multi_turn_execution_id (UUID): Foreign key to multi-turn execution
        step_id (UUID): Foreign key to scenario step
        step_order (int): Order of this step in the scenario
        user_utterance (str): What the user said
        audio_data_urls (dict, optional): Map of language codes to S3 input audio URLs
            Example: {"en-US": "http://.../step_1_en-US.mp3", "es-ES": "http://.../step_1_es-ES.mp3"}
        response_audio_urls (dict, optional): Map of language codes to S3 response audio URLs
            Example: {"en-US": "http://.../response_1_en-US.wav", "es-ES": "http://.../response_1_es-ES.wav"}
        request_id (str): Houndify request ID
        ai_response (str, optional): AI's spoken response
        transcription (str, optional): Transcription of user utterance
        command_kind (str, optional): Houndify CommandKind
        confidence_score (float, optional): Recognition confidence
        conversation_state_before (dict): Conversation state before this step
        conversation_state_after (dict): Conversation state after this step
        validation_passed (bool, optional): Whether validation passed
        validation_details (dict, optional): Detailed validation results
        response_time_ms (int, optional): API response time in milliseconds
        executed_at (datetime): When step was executed
        error_message (str, optional): Error message if step failed
        multi_turn_execution (MultiTurnExecution): Relationship to parent execution
        step (ScenarioStep): Relationship to scenario step
        created_at (datetime): Creation timestamp (inherited)
        updated_at (datetime): Last update timestamp (inherited)

    Example:
        >>> step_exec = StepExecution(
        ...     multi_turn_execution_id=execution.id,
        ...     step_id=step.id,
        ...     step_order=1,
        ...     user_utterance="I want to make a reservation",
        ...     request_id="req_001"
        ... )
    """

    __tablename__ = 'step_executions'

    multi_turn_execution_id = Column(
        GUID(),
        ForeignKey('multi_turn_executions.id'),
        nullable=False,
        index=True,
        comment="Parent multi-turn execution"
    )

    step_id = Column(
        GUID(),
        ForeignKey('scenario_steps.id'),
        nullable=False,
        index=True,
        comment="Scenario step being executed"
    )

    step_order = Column(
        Integer,
        nullable=False,
        comment="Order of this step in the scenario"
    )

    user_utterance = Column(
        Text,
        nullable=False,
        comment="What the user said"
    )

    audio_data_urls = Column(
        postgresql.JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        comment="Map of language codes to S3 audio URLs (e.g., {'en-US': 'http://...', 'es-ES': 'http://...'})"
    )

    response_audio_urls = Column(
        postgresql.JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        comment="Map of language codes to S3 response audio URLs (e.g., {'en-US': 'http://...', 'es-ES': 'http://...'})"
    )

    request_id = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Houndify request ID"
    )

    ai_response = Column(
        Text,
        nullable=True,
        comment="AI's spoken response"
    )

    transcription = Column(
        Text,
        nullable=True,
        comment="Transcription of user utterance"
    )

    command_kind = Column(
        String(100),
        nullable=True,
        comment="Houndify CommandKind"
    )

    confidence_score = Column(
        Float,
        nullable=True,
        comment="Recognition confidence score (0.0 to 1.0)"
    )

    conversation_state_before = Column(
        postgresql.JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        comment="Conversation state before this step (JSONB)"
    )

    conversation_state_after = Column(
        postgresql.JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        comment="Conversation state after this step (JSONB)"
    )

    validation_passed = Column(
        Boolean,
        nullable=True,
        comment="Whether validation passed for this step"
    )

    validation_details = Column(
        postgresql.JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        comment="Detailed validation results (JSONB)"
    )

    response_time_ms = Column(
        Integer,
        nullable=True,
        comment="API response time in milliseconds"
    )

    executed_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        comment="When step was executed"
    )

    error_message = Column(
        Text,
        nullable=True,
        comment="Error message if step failed"
    )

    # Relationships
    multi_turn_execution = relationship(
        'MultiTurnExecution',
        back_populates='step_executions',
        lazy='select'
    )

    step = relationship(
        'ScenarioStep',
        foreign_keys=[step_id],
        lazy='select'
    )

    @property
    def is_successful(self) -> bool:
        """Check if step execution was successful."""
        return self.validation_passed is True and self.error_message is None

    @property
    def has_error(self) -> bool:
        """Check if step has an error."""
        return self.error_message is not None

