"""
TestExecutionQueue SQLAlchemy model for test execution queue management

This module defines the TestExecutionQueue model which represents items in the
test execution queue for the automated testing framework.

The TestExecutionQueue model includes:
    - Suite run reference: Link to the suite run to be executed
    - Priority management: Priority field for queue ordering (higher = more urgent)
    - Status tracking: Current status of the queue item
    - Queue operations: Methods for managing queue state transitions

Example:
    >>> from models.test_execution_queue import TestExecutionQueue
    >>>
    >>> # Add suite run to queue
    >>> queue_item = TestExecutionQueue(
    ...     suite_run_id=suite_run.id,
    ...     priority=5,
    ...     status="queued"
    ... )
    >>>
    >>> # Start processing
    >>> queue_item.mark_as_processing()
    >>>
    >>> # Complete or fail
    >>> queue_item.mark_as_completed()
"""

from typing import Optional, TYPE_CHECKING

from sqlalchemy import Column, String, Integer, ForeignKey

from sqlalchemy.orm import relationship

from models.base import Base, BaseModel, GUID

# Avoid circular imports for type hints
if TYPE_CHECKING:
    pass


class TestExecutionQueue(Base, BaseModel):
    """
    TestExecutionQueue model for managing test execution queue.

    Represents a queue item for test execution, with priority-based ordering
    and status tracking.

    Attributes:
        id (UUID): Unique identifier (inherited from BaseModel)
        suite_run_id (UUID): Foreign key to suite run, required
        priority (int, optional): Execution priority (higher number = higher priority)
        status (str): Current status (queued, processing, completed, failed), required
        created_at (datetime): Creation timestamp (inherited)
        updated_at (datetime): Last update timestamp (inherited)
        suite_run (SuiteRun): Relationship to the suite run

    Example:
        >>> queue_item = TestExecutionQueue(
        ...     suite_run_id=run_id,
        ...     priority=10,
        ...     status="queued"
        ... )
        >>> queue_item.mark_as_processing()
        >>> print(queue_item.status)
        'processing'
        >>> queue_item.mark_as_completed()
        >>> print(queue_item.is_completed())
        True

    Note:
        - Status must be one of: queued, processing, completed, failed
        - Higher priority numbers are processed first
        - Default priority is None (lowest priority)
    """

    __tablename__ = 'test_execution_queue'

    # Foreign key to suite_runs
    suite_run_id = Column(
        GUID(),
        ForeignKey('suite_runs.id'),
        nullable=False,
        index=True,
        comment="Suite run to be executed"
    )

    # Queue management fields
    priority = Column(
        Integer,
        nullable=True,
        index=True,
        comment="Execution priority (higher number = higher priority)"
    )

    status = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Queue status (queued, processing, completed, failed)"
    )

    # Relationships
    suite_run = relationship(
        'SuiteRun',
        foreign_keys=[suite_run_id],
        primaryjoin="TestExecutionQueue.suite_run_id == SuiteRun.id",
        lazy='joined'
    )

    def __repr__(self) -> str:
        """
        String representation of TestExecutionQueue instance.

        Returns:
            String with status and priority

        Example:
            >>> queue_item = TestExecutionQueue(status="queued", priority=5)
            >>> print(queue_item)
            <TestExecutionQueue(status='queued', priority=5)>
        """
        return f"<TestExecutionQueue(status='{self.status}', priority={self.priority})>"

    def mark_as_queued(self) -> None:
        """
        Mark queue item as queued.

        Example:
            >>> item = TestExecutionQueue(status="processing")
            >>> item.mark_as_queued()
            >>> item.status
            'queued'
        """
        self.status = 'queued'

    def mark_as_processing(self) -> None:
        """
        Mark queue item as processing.

        Example:
            >>> item = TestExecutionQueue(status="queued")
            >>> item.mark_as_processing()
            >>> item.status
            'processing'
        """
        self.status = 'processing'

    def mark_as_completed(self) -> None:
        """
        Mark queue item as completed.

        Example:
            >>> item = TestExecutionQueue(status="processing")
            >>> item.mark_as_completed()
            >>> item.status
            'completed'
        """
        self.status = 'completed'

    def mark_as_failed(self) -> None:
        """
        Mark queue item as failed.

        Example:
            >>> item = TestExecutionQueue(status="processing")
            >>> item.mark_as_failed()
            >>> item.status
            'failed'
        """
        self.status = 'failed'

    def is_queued(self) -> bool:
        """
        Check if queue item is queued.

        Returns:
            bool: True if status is queued

        Example:
            >>> item = TestExecutionQueue(status="queued")
            >>> item.is_queued()
            True
            >>> item = TestExecutionQueue(status="processing")
            >>> item.is_queued()
            False
        """
        return self.status == 'queued'

    def is_processing(self) -> bool:
        """
        Check if queue item is processing.

        Returns:
            bool: True if status is processing

        Example:
            >>> item = TestExecutionQueue(status="processing")
            >>> item.is_processing()
            True
            >>> item = TestExecutionQueue(status="queued")
            >>> item.is_processing()
            False
        """
        return self.status == 'processing'

    def is_completed(self) -> bool:
        """
        Check if queue item has completed (successfully or not).

        Returns:
            bool: True if status is completed or failed

        Example:
            >>> item = TestExecutionQueue(status="completed")
            >>> item.is_completed()
            True
            >>> item = TestExecutionQueue(status="failed")
            >>> item.is_completed()
            True
            >>> item = TestExecutionQueue(status="processing")
            >>> item.is_completed()
            False
        """
        return self.status in ('completed', 'failed')

    def set_priority(self, priority: int) -> None:
        """
        Set the priority for this queue item.

        Args:
            priority: Priority value (higher = more urgent)

        Example:
            >>> item = TestExecutionQueue(priority=5)
            >>> item.set_priority(10)
            >>> item.priority
            10
        """
        self.priority = priority

    def get_priority(self) -> Optional[int]:
        """
        Get the priority for this queue item.

        Returns:
            Optional[int]: Priority value or None if not set

        Example:
            >>> item = TestExecutionQueue(priority=5)
            >>> item.get_priority()
            5
            >>> item = TestExecutionQueue(priority=None)
            >>> item.get_priority()
            None
        """
        return self.priority
