"""
Pydantic schemas for human validation management

This module defines Pydantic schemas for human validation-related API operations
in the automated testing framework's Phase 2 human validation system.

The module includes:
    - ValidationQueueItem: Schema for validation task queue items
    - HumanValidationSubmit: Schema for submitting validation decisions

Example:
    >>> from api.schemas.human_validation import ValidationQueueItem, HumanValidationSubmit
    >>>
    >>> # View validation task from queue
    >>> queue_item = ValidationQueueItem(
    ...     id=task_uuid,
    ...     test_case_name="Voice Navigation Test - Spanish",
    ...     language_code="es-MX",
    ...     confidence_score=65.5,
    ...     input_text="Navegar a casa",
    ...     input_audio_url="https://s3.../audio.wav",
    ...     expected={"intent": "navigate", "location": "home"},
    ...     actual={"intent": "navigate", "location": "house"},
    ...     context={"suite_run_id": "...", "device": "mobile"}
    ... )
    >>>
    >>> # Submit validation decision
    >>> validation_submit = HumanValidationSubmit(
    ...     validation_decision="pass",
    ...     feedback="Translation accurate, intent matches",
    ...     time_spent_seconds=45
    ... )
"""

from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class ValidationQueueItem(BaseModel):
    """
    Schema for a validation task queue item.

    Represents all the data a human validator needs to review a voice AI
    test result and make a validation decision. This schema is used when
    retrieving validation tasks from the queue.

    Attributes:
        id (UUID): Unique identifier for the validation queue item
        test_case_name (str): Name of the test case being validated
        language_code (str): Language code (e.g., en-US, es-MX, fr-FR)
        confidence_score (float): AI confidence score (0.00-100.00)
        input_text (str): Text input that was tested
        input_audio_url (str): S3 URL to the audio file for listening
        expected (Dict[str, Any]): Expected result from test case definition
        actual (Dict[str, Any]): Actual result from voice AI execution
        context (Dict[str, Any]): Additional context (device, suite run, etc.)

    Example:
        >>> queue_item = ValidationQueueItem(
        ...     id=UUID("12345678-1234-1234-1234-123456789abc"),
        ...     test_case_name="Weather Query - French",
        ...     language_code="fr-FR",
        ...     confidence_score=72.3,
        ...     input_text="Quel temps fait-il?",
        ...     input_audio_url="https://s3.amazonaws.com/bucket/audio/123.wav",
        ...     expected={
        ...         "intent": "weather.query",
        ...         "location": "current",
        ...         "time": "now"
        ...     },
        ...     actual={
        ...         "intent": "weather.query",
        ...         "location": "current",
        ...         "time": "today"
        ...     },
        ...     context={
        ...         "suite_run_id": "87654321-4321-4321-4321-210987654321",
        ...         "device_type": "mobile",
        ...         "test_suite": "Weather Commands - French"
        ...     }
        ... )
    """

    id: UUID = Field(..., description="Unique identifier for the validation queue item")
    test_case_name: str = Field(..., description="Name of the test case being validated")
    language_code: str = Field(..., description="Language code (e.g., en-US, es-MX, fr-FR)")
    confidence_score: float = Field(
        ...,
        description="AI confidence score (0.00-100.00)",
        ge=0.0,
        le=100.0
    )
    input_text: str = Field(..., description="Text input that was tested")
    input_audio_url: str = Field(..., description="S3 URL to the audio file for listening")
    expected: Dict[str, Any] = Field(..., description="Expected result from test case definition")
    actual: Dict[str, Any] = Field(..., description="Actual result from voice AI execution")
    context: Dict[str, Any] = Field(
        ...,
        description="Additional context (device, suite run, etc.)"
    )

    model_config = ConfigDict(from_attributes=True)


class HumanValidationSubmit(BaseModel):
    """
    Schema for submitting a human validation decision.

    Represents the data a human validator submits when completing their
    review of a voice AI test result. This schema is used when a validator
    submits their decision via the validation UI.

    Attributes:
        validation_decision (str): Validation decision - must be 'pass', 'fail', or 'edge_case'
        feedback (str | None): Optional feedback explaining the decision
        time_spent_seconds (int): Time spent reviewing this validation in seconds

    Validation Decision Values:
        - 'pass': Voice AI response matches expected result
        - 'fail': Voice AI response does not match expected result
        - 'edge_case': Result is ambiguous or requires special handling

    Example:
        >>> # Pass validation
        >>> submit_pass = HumanValidationSubmit(
        ...     validation_decision="pass",
        ...     feedback="Intent and entities correctly identified",
        ...     time_spent_seconds=30
        ... )
        >>>
        >>> # Fail validation
        >>> submit_fail = HumanValidationSubmit(
        ...     validation_decision="fail",
        ...     feedback="Intent misidentified - should be 'navigate' not 'search'",
        ...     time_spent_seconds=45
        ... )
        >>>
        >>> # Edge case
        >>> submit_edge = HumanValidationSubmit(
        ...     validation_decision="edge_case",
        ...     feedback="Pronunciation ambiguous between two valid interpretations",
        ...     time_spent_seconds=120
        ... )
        >>>
        >>> # Minimal submission (no feedback)
        >>> submit_minimal = HumanValidationSubmit(
        ...     validation_decision="pass",
        ...     feedback=None,
        ...     time_spent_seconds=15
        ... )
    """

    validation_decision: str = Field(
        ...,
        description="Validation decision: 'pass', 'fail', or 'edge_case'"
    )
    feedback: Optional[str] = Field(
        None,
        description="Optional feedback explaining the validation decision"
    )
    time_spent_seconds: int = Field(
        ...,
        description="Time spent reviewing this validation in seconds",
        ge=0
    )

    model_config = ConfigDict(from_attributes=True)
