"""
HumanValidation SQLAlchemy model for human validation of voice AI test results

This module defines the HumanValidation model which tracks human validation
reviews of voice AI test results, enabling quality assurance and validation
workflows for the voice AI testing framework.

The HumanValidation model includes:
    - Validation tracking: Links to validation results requiring human review
    - Validator assignment: Tracks which validator claimed and reviewed the test
    - Decision recording: Stores pass/fail/edge_case decisions
    - Feedback collection: Optional validator feedback and notes
    - Time tracking: Measures validation time for performance metrics
    - QA support: Flags second-opinion validations for quality assurance

Example:
    >>> from models.human_validation import HumanValidation
    >>> from uuid import uuid4
    >>>
    >>> # Create new human validation record
    >>> validation = HumanValidation(
    ...     id=uuid4(),
    ...     validation_result_id=result_id,
    ...     validator_id=user_id,
    ...     claimed_at=datetime.utcnow()
    ... )
    >>>
    >>> # Submit validation decision
    >>> validation.validation_decision = 'pass'
    >>> validation.feedback = 'Output matches expected result'
    >>> validation.time_spent_seconds = 45
    >>> validation.submitted_at = datetime.utcnow()
    >>>
    >>> # Mark as second opinion for QA
    >>> validation.is_second_opinion = True
"""

from typing import Optional

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text

from sqlalchemy.orm import relationship

from models.base import Base, BaseModel, GUID


class HumanValidation(Base, BaseModel):
    """
    HumanValidation model for tracking human review of voice AI test results.

    Represents a human validation review of a voice AI test validation result,
    including the validator assignment, decision, feedback, and timing information.

    Attributes:
        id (UUID): Unique identifier (inherited from BaseModel)
        validation_result_id (UUID): Reference to the validation result being reviewed
        validator_id (UUID): Reference to the user performing the validation
        claimed_at (datetime, optional): When the validator claimed this validation task
        submitted_at (datetime, optional): When the validation decision was submitted
        validation_decision (str, optional): Decision: 'pass', 'fail', or 'edge_case'
        feedback (str, optional): Optional validator feedback and notes
        time_spent_seconds (int, optional): Time spent on validation in seconds
        is_second_opinion (bool): Whether this is a QA second opinion, defaults to False
        created_at (datetime): Record creation timestamp (inherited)
        updated_at (datetime): Last update timestamp (inherited)

    Relationships:
        validation_result: The ValidationResult being reviewed (many-to-one)
        validator: The User who performed the validation (many-to-one)

    Example:
        >>> validation = HumanValidation(
        ...     validation_result_id=result_uuid,
        ...     validator_id=user_uuid,
        ...     claimed_at=datetime.utcnow(),
        ...     validation_decision='pass',
        ...     feedback='Audio quality is excellent',
        ...     time_spent_seconds=30,
        ...     is_second_opinion=False
        ... )
        >>> print(validation.validation_decision)
        'pass'

    Note:
        - validation_decision should be one of: 'pass', 'fail', 'edge_case'
        - claimed_at is set when validator claims the task from queue
        - submitted_at is set when validator submits their decision
        - time_spent_seconds helps track validator performance
        - is_second_opinion=True indicates QA second review
    """

    __tablename__ = 'human_validations'

    tenant_id = Column(
        GUID(),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Tenant (organization or user) that owns this validation"
    )

    # Foreign key to validation result
    validation_result_id = Column(
        GUID(),
        ForeignKey('validation_results.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Reference to the validation result being reviewed"
    )

    # Foreign key to validator (user)
    validator_id = Column(
        GUID(),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="User performing the validation"
    )

    # Timestamp tracking
    claimed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When the validator claimed this validation task"
    )

    submitted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When the validation decision was submitted"
    )

    # Validation decision
    validation_decision = Column(
        String(50),
        nullable=True,
        index=True,
        comment="Validation decision: 'pass', 'fail', or 'edge_case'"
    )

    # Validator feedback
    feedback = Column(
        Text,
        nullable=True,
        comment="Optional feedback and notes from the validator"
    )

    # Time tracking
    time_spent_seconds = Column(
        Integer,
        nullable=True,
        comment="Time spent on validation in seconds"
    )

    # QA second opinion flag
    is_second_opinion = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether this is a second validation for quality assurance"
    )

    # Relationships to other models
    validation_result = relationship(
        "ValidationResult",
        back_populates="human_validations",
        foreign_keys=[validation_result_id]
    )

    validator = relationship(
        "User",
        foreign_keys=[validator_id],
        primaryjoin="HumanValidation.validator_id == remote(User.id)",
        viewonly=True
    )

    def __repr__(self) -> str:
        """String representation of HumanValidation."""
        return (
            f"<HumanValidation(id={self.id}, "
            f"validator_id={self.validator_id}, "
            f"decision={self.validation_decision}, "
            f"is_second_opinion={self.is_second_opinion})>"
        )

    def is_completed(self) -> bool:
        """
        Check if validation is completed.

        Returns:
            bool: True if validation has been submitted with a decision

        Example:
            >>> validation.validation_decision = 'pass'
            >>> validation.submitted_at = datetime.utcnow()
            >>> print(validation.is_completed())
            True
        """
        return (
            self.validation_decision is not None and
            self.submitted_at is not None
        )

    def is_pending(self) -> bool:
        """
        Check if validation is pending (claimed but not submitted).

        Returns:
            bool: True if claimed but not yet submitted

        Example:
            >>> validation.claimed_at = datetime.utcnow()
            >>> print(validation.is_pending())
            True
        """
        return (
            self.claimed_at is not None and
            self.submitted_at is None
        )

    def get_time_spent_minutes(self) -> Optional[float]:
        """
        Get time spent in minutes.

        Returns:
            Optional[float]: Time spent in minutes, or None if not recorded

        Example:
            >>> validation.time_spent_seconds = 150
            >>> print(validation.get_time_spent_minutes())
            2.5
        """
        if self.time_spent_seconds is None:
            return None
        return self.time_spent_seconds / 60.0
