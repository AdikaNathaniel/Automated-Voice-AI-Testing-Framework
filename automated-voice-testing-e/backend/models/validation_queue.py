"""
ValidationQueue SQLAlchemy model for managing human validation task queue

This module defines the ValidationQueue model which manages the queue of
validation tasks awaiting human review, enabling efficient task assignment
and prioritization for the voice AI testing framework.

The ValidationQueue model includes:
    - Task queuing: Tracks validation results requiring human review
    - Priority management: Supports configurable priority levels (1-10)
    - Validator assignment: Tracks which validator claimed the task
    - Language routing: Matches tasks to validators by language proficiency
    - Status tracking: Manages queue item lifecycle (pending, claimed, completed)
    - Native speaker requirements: Flags tasks requiring native speaker review

Example:
    >>> from models.validation_queue import ValidationQueue
    >>> from uuid import uuid4
    >>> from decimal import Decimal
    >>>
    >>> # Create new queue item
    >>> queue_item = ValidationQueue(
    ...     id=uuid4(),
    ...     validation_result_id=result_id,
    ...     priority=3,
    ...     confidence_score=Decimal('65.50'),
    ...     language_code='es-MX',
    ...     status='pending',
    ...     requires_native_speaker=True
    ... )
    >>>
    >>> # Claim task for validation
    >>> queue_item.claimed_by = validator_id
    >>> queue_item.claimed_at = datetime.utcnow()
    >>> queue_item.status = 'claimed'
    >>>
    >>> # Check queue item status
    >>> if queue_item.is_pending():
    ...     print("Task available for claim")
"""

from typing import Optional

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Numeric, Index

from sqlalchemy.orm import relationship

from models.base import Base, BaseModel, GUID


class ValidationQueue(Base, BaseModel):
    """
    ValidationQueue model for managing human validation task queue.

    Represents a validation task in the queue awaiting human review,
    including priority, language requirements, validator assignment, and status.

    Attributes:
        id (UUID): Unique identifier (inherited from BaseModel)
        validation_result_id (UUID): Reference to the validation result to be reviewed
        priority (int): Priority level for queue ordering (1=highest, 10=lowest, default=5)
        confidence_score (Decimal, optional): AI confidence score (0.00-100.00)
        language_code (str, optional): Language code for validator matching (e.g., 'en-US', 'es-MX')
        claimed_by (UUID, optional): Reference to the user who claimed this task
        claimed_at (datetime, optional): When the task was claimed by a validator
        status (str): Queue status - 'pending', 'claimed', or 'completed' (default='pending')
        requires_native_speaker (bool): Whether this task requires a native speaker (default=False)
        created_at (datetime): When this queue item was created (inherited)
        updated_at (datetime): Last update timestamp (inherited)

    Relationships:
        validation_result: The ValidationResult to be reviewed (many-to-one)
        claimed_by_user: The User who claimed this task (many-to-one)

    Example:
        >>> queue_item = ValidationQueue(
        ...     validation_result_id=result_uuid,
        ...     priority=2,
        ...     confidence_score=Decimal('72.35'),
        ...     language_code='fr-FR',
        ...     status='pending',
        ...     requires_native_speaker=False
        ... )
        >>> print(queue_item.is_pending())
        True
        >>> print(queue_item.get_priority_label())
        'high'

    Note:
        - Priority levels: 1-3=high, 4-6=normal, 7-10=low
        - Status values: 'pending' (unclaimed), 'claimed' (in progress), 'completed' (finished)
        - confidence_score typically represents AI uncertainty (lower = needs review)
        - language_code should match ISO 639-1 with optional region (e.g., 'en', 'en-US')
    """

    __tablename__ = 'validation_queue'

    __table_args__ = (
        Index('ix_validation_queue_validation_result_id_status', 'validation_result_id', 'status'),
    )

    # Foreign key to validation result
    validation_result_id = Column(
        GUID(),
        ForeignKey('validation_results.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Reference to the validation result to be reviewed"
    )

    # Priority for queue ordering
    priority = Column(
        Integer,
        default=5,
        nullable=False,
        index=True,
        comment="Priority level for queue ordering (1=highest, 10=lowest, default=5)"
    )

    # AI confidence score
    confidence_score = Column(
        Numeric(precision=5, scale=2),
        nullable=True,
        comment="AI confidence score (0.00-100.00) indicating uncertainty"
    )

    # Language code for validator matching
    language_code = Column(
        String(10),
        nullable=True,
        index=True,
        comment="Language code for matching to validators with language proficiency"
    )

    # Validator claim information
    claimed_by = Column(
        GUID(),
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
        comment="User who claimed this validation task"
    )

    claimed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When the validation task was claimed"
    )

    # Queue status
    status = Column(
        String(50),
        default='pending',
        nullable=False,
        index=True,
        comment="Queue status: 'pending', 'claimed', 'completed'"
    )

    # Native speaker requirement flag
    requires_native_speaker = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether this validation requires a native speaker"
    )

    # Relationships to other models
    validation_result = relationship(
        "ValidationResult",
        back_populates="queue_items",
        foreign_keys=[validation_result_id]
    )

    claimed_by_user = relationship(
        "User",
        foreign_keys=[claimed_by],
        primaryjoin="ValidationQueue.claimed_by == remote(User.id)",
        viewonly=True
    )

    def __repr__(self) -> str:
        """String representation of ValidationQueue."""
        return (
            f"<ValidationQueue(id={self.id}, "
            f"priority={self.priority}, "
            f"status={self.status}, "
            f"language_code={self.language_code})>"
        )

    def is_pending(self) -> bool:
        """
        Check if queue item is pending (unclaimed).

        Returns:
            bool: True if status is 'pending'

        Example:
            >>> queue_item.status = 'pending'
            >>> print(queue_item.is_pending())
            True
        """
        return self.status == 'pending'

    def is_claimed(self) -> bool:
        """
        Check if queue item is claimed (in progress).

        Returns:
            bool: True if status is 'claimed'

        Example:
            >>> queue_item.status = 'claimed'
            >>> queue_item.claimed_by = user_id
            >>> print(queue_item.is_claimed())
            True
        """
        return self.status == 'claimed'

    def is_completed(self) -> bool:
        """
        Check if queue item is completed.

        Returns:
            bool: True if status is 'completed'

        Example:
            >>> queue_item.status = 'completed'
            >>> print(queue_item.is_completed())
            True
        """
        return self.status == 'completed'

    def get_priority_label(self) -> str:
        """
        Get human-readable priority label.

        Returns:
            str: Priority label - 'high' (1-3), 'normal' (4-6), or 'low' (7-10)

        Example:
            >>> queue_item.priority = 2
            >>> print(queue_item.get_priority_label())
            'high'
            >>> queue_item.priority = 5
            >>> print(queue_item.get_priority_label())
            'normal'
        """
        if self.priority <= 3:
            return 'high'
        elif self.priority <= 6:
            return 'normal'
        else:
            return 'low'

    def get_confidence_percentage(self) -> Optional[float]:
        """
        Get confidence score as a percentage.

        Returns:
            Optional[float]: Confidence score as percentage (0.0-100.0), or None if not set

        Example:
            >>> queue_item.confidence_score = Decimal('85.50')
            >>> print(queue_item.get_confidence_percentage())
            85.5
        """
        if self.confidence_score is None:
            return None
        return float(self.confidence_score)
