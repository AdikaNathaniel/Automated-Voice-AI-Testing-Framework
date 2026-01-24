"""
SuiteRun SQLAlchemy model for suite execution tracking

This module defines the SuiteRun model which represents a suite execution run
in the automated testing framework.

The SuiteRun model includes:
    - Test suite reference: Link to the test suite being executed
    - Status tracking: Current status of the suite run
    - Test metrics: Counters for passed, failed, and skipped tests
    - Timestamps: Track when the run was created, started, and completed
    - Relationships: Links to test suite, user, and executions
    - Calculated properties: Progress percentage based on completed tests

Example:
    >>> from models.suite_run import SuiteRun
    >>>
    >>> # Create a new suite run
    >>> suite_run = SuiteRun(
    ...     suite_id=suite.id,
    ...     created_by=user.id,
    ...     status="pending"
    ... )
    >>>
    >>> # Start the run
    >>> suite_run.mark_as_running()
    >>>
    >>> # Update test counts
    >>> suite_run.update_test_counts(total=10, passed=8, failed=2, skipped=0)
    >>>
    >>> # Complete the run
    >>> suite_run.mark_as_completed()
    >>>
    >>> # Check progress
    >>> print(suite_run.progress_percentage)
    100.0
"""

from typing import Optional, TYPE_CHECKING, Any, Dict
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects import postgresql
from sqlalchemy import JSON

from sqlalchemy.orm import relationship

from models.base import Base, BaseModel, GUID

# Avoid circular imports for type hints
if TYPE_CHECKING:
    pass


# Use JSONB for PostgreSQL, JSON for SQLite (testing)
JSONB_TYPE = JSONB().with_variant(JSON(), "sqlite")

class SuiteRun(Base, BaseModel):
    """
    SuiteRun model for tracking suite execution runs.

    Represents a single execution of a test suite, including status tracking,
    test metrics, and timing information.

    Attributes:
        id (UUID): Unique identifier (inherited from BaseModel)
        suite_id (UUID): Foreign key to test suite, optional for categorical runs
        created_by (UUID, optional): Foreign key to user who created the run
        status (str): Current status (pending, running, completed, failed, cancelled), required
        created_at (datetime): Creation timestamp (inherited)
        updated_at (datetime): Last update timestamp (inherited)
        started_at (datetime, optional): When suite run execution started
        completed_at (datetime, optional): When suite run execution completed
        total_tests (int, optional): Total number of tests in the run
        passed_tests (int, optional): Number of tests that passed
        failed_tests (int, optional): Number of tests that failed
        skipped_tests (int, optional): Number of tests that were skipped
        test_suite (TestSuite): Relationship to the test suite
        creator (User): Relationship to the user who created the run

    Example:
        >>> run = SuiteRun(
        ...     suite_id=suite_id,
        ...     created_by=user_id,
        ...     status="pending",
        ...     total_tests=10
        ... )
        >>> run.mark_as_running()
        >>> print(run.status)
        'running'
        >>> run.update_test_counts(passed=5, failed=1)
        >>> print(run.progress_percentage)
        60.0

    Note:
        - Status must be one of: pending, running, completed, failed, cancelled
        - Test counts should add up to total_tests
        - started_at is set when status changes to running
        - completed_at is set when status changes to completed/failed/cancelled
    """

    __tablename__ = 'suite_runs'

    tenant_id = Column(
        GUID(),
        nullable=True,
        index=True,
        comment="Tenant identifier for multi-tenant scoping"
    )

    # Identifying info
    name = Column(
        String(255),
        nullable=True,
        comment="Name of the suite run (e.g., 'Suite Run: Login Tests' or 'Category Run: Booking')"
    )

    description = Column(
        Text,
        nullable=True,
        comment="Description of what this run covers"
    )

    # Foreign keys
    suite_id = Column(
        GUID(),
        ForeignKey('test_suites.id'),
        nullable=True,  # Nullable for categorical suite runs (virtual suites)
        index=True,
        comment="Test suite being run (null for categorical/ad-hoc runs)"
    )

    # For categorical runs, store the category name
    category_name = Column(
        String(255),
        nullable=True,
        index=True,
        comment="Category name for categorical suite runs (null for real suite runs)"
    )

    created_by = Column(
        GUID(),
        ForeignKey('users.id'),
        nullable=True,
        index=True,
        comment="User who initiated the suite run"
    )

    # Status and timestamps
    status = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Suite run status (pending, running, completed, failed, cancelled)"
    )

    started_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When suite run execution started"
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When suite run execution completed"
    )

    # Test metrics
    total_tests = Column(
        Integer,
        nullable=True,
        comment="Total number of tests in the run"
    )

    passed_tests = Column(
        Integer,
        nullable=True,
        comment="Number of tests that passed"
    )

    failed_tests = Column(
        Integer,
        nullable=True,
        comment="Number of tests that failed"
    )

    skipped_tests = Column(
        Integer,
        nullable=True,
        comment="Number of tests that were skipped"
    )

    # Trigger information
    trigger_type = Column(
        String(50),
        nullable=True,
        comment="Type of trigger (manual, scheduled, api, webhook)"
    )

    trigger_metadata = Column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        comment="Additional trigger metadata including languages"
    )

    # Relationships
    test_suite = relationship(
        'TestSuite',
        back_populates='suite_runs',
        foreign_keys=[suite_id],
        lazy='joined'
    )

    creator = relationship(
        'User',
        foreign_keys=[created_by],
        lazy='select'
    )

    # Scenario executions within this run
    scenario_executions = relationship(
        'MultiTurnExecution',
        foreign_keys='MultiTurnExecution.suite_run_id',
        primaryjoin="SuiteRun.id == foreign(MultiTurnExecution.suite_run_id)",
        back_populates='suite_run',
        lazy='selectin',
        order_by='MultiTurnExecution.created_at'
    )

    def __repr__(self) -> str:
        """
        String representation of SuiteRun instance.

        Returns:
            String with status and suite ID

        Example:
            >>> run = SuiteRun(status="running", suite_id=suite_id)
            >>> print(run)
            <SuiteRun(status='running')>
        """
        return f"<SuiteRun(status='{self.status}')>"

    @property
    def progress_percentage(self) -> float:
        """
        Calculate progress percentage based on completed tests.

        Returns:
            float: Percentage of tests completed (0.0 to 100.0)

        Example:
            >>> run = SuiteRun(total_tests=10, passed_tests=5, failed_tests=2, skipped_tests=1)
            >>> run.progress_percentage
            80.0
            >>> run = SuiteRun(total_tests=0)
            >>> run.progress_percentage
            0.0
        """
        if not self.total_tests or self.total_tests == 0:
            return 0.0

        completed = (self.passed_tests or 0) + (self.failed_tests or 0) + (self.skipped_tests or 0)
        return (completed / self.total_tests) * 100.0

    def mark_as_running(self) -> None:
        """
        Mark suite run as running and set started_at timestamp.

        Example:
            >>> run = SuiteRun(status="pending")
            >>> run.mark_as_running()
            >>> run.status
            'running'
            >>> run.started_at is not None
            True
        """
        self.status = 'running'
        if self.started_at is None:
            self.started_at = datetime.utcnow()

    def mark_as_completed(self) -> None:
        """
        Mark suite run as completed and set timestamps.

        Sets started_at to created_at if not already set (fallback for race conditions).
        Sets completed_at to current time if not already set.

        Example:
            >>> run = SuiteRun(status="running")
            >>> run.mark_as_completed()
            >>> run.status
            'completed'
            >>> run.completed_at is not None
            True
        """
        self.status = 'completed'
        now = datetime.utcnow()
        if self.started_at is None:
            # Fallback to created_at for meaningful duration calculation
            self.started_at = self.created_at or now
        if self.completed_at is None:
            self.completed_at = now

    def mark_as_failed(self) -> None:
        """
        Mark suite run as failed and set timestamps.

        Sets started_at to created_at if not already set (fallback for race conditions).
        Sets completed_at to current time if not already set.

        Example:
            >>> run = SuiteRun(status="running")
            >>> run.mark_as_failed()
            >>> run.status
            'failed'
            >>> run.completed_at is not None
            True
        """
        self.status = 'failed'
        now = datetime.utcnow()
        if self.started_at is None:
            # Fallback to created_at for meaningful duration calculation
            self.started_at = self.created_at or now
        if self.completed_at is None:
            self.completed_at = now

    def mark_as_cancelled(self) -> None:
        """
        Mark suite run as cancelled and set timestamps.

        Sets started_at to created_at if not already set (fallback for race conditions).
        Sets completed_at to current time if not already set.

        Example:
            >>> run = SuiteRun(status="running")
            >>> run.mark_as_cancelled()
            >>> run.status
            'cancelled'
            >>> run.completed_at is not None
            True
        """
        self.status = 'cancelled'
        now = datetime.utcnow()
        if self.started_at is None:
            # Fallback to created_at for meaningful duration calculation
            self.started_at = self.created_at or now
        if self.completed_at is None:
            self.completed_at = now

    def update_test_counts(
        self,
        total: Optional[int] = None,
        passed: Optional[int] = None,
        failed: Optional[int] = None,
        skipped: Optional[int] = None
    ) -> None:
        """
        Update test count metrics.

        Args:
            total: Total number of tests
            passed: Number of passed tests
            failed: Number of failed tests
            skipped: Number of skipped tests

        Example:
            >>> run = SuiteRun(status="running")
            >>> run.update_test_counts(total=10, passed=5, failed=2, skipped=1)
            >>> run.total_tests
            10
            >>> run.passed_tests
            5
        """
        if total is not None:
            self.total_tests = total
        if passed is not None:
            self.passed_tests = passed
        if failed is not None:
            self.failed_tests = failed
        if skipped is not None:
            self.skipped_tests = skipped

    def increment_passed(self) -> None:
        """
        Increment the passed tests counter.

        Example:
            >>> run = SuiteRun(passed_tests=5)
            >>> run.increment_passed()
            >>> run.passed_tests
            6
        """
        if self.passed_tests is None:
            self.passed_tests = 0
        self.passed_tests += 1

    def increment_failed(self) -> None:
        """
        Increment the failed tests counter.

        Example:
            >>> run = SuiteRun(failed_tests=2)
            >>> run.increment_failed()
            >>> run.failed_tests
            3
        """
        if self.failed_tests is None:
            self.failed_tests = 0
        self.failed_tests += 1

    def increment_skipped(self) -> None:
        """
        Increment the skipped tests counter.

        Example:
            >>> run = SuiteRun(skipped_tests=1)
            >>> run.increment_skipped()
            >>> run.skipped_tests
            2
        """
        if self.skipped_tests is None:
            self.skipped_tests = 0
        self.skipped_tests += 1

    def is_completed(self) -> bool:
        """
        Check if suite run has completed (successfully or not).

        Returns:
            bool: True if status is completed, failed, or cancelled

        Example:
            >>> run = SuiteRun(status="completed")
            >>> run.is_completed()
            True
            >>> run = SuiteRun(status="running")
            >>> run.is_completed()
            False
        """
        return self.status in ('completed', 'failed', 'cancelled')

    def is_running(self) -> bool:
        """
        Check if suite run is currently running.

        Returns:
            bool: True if status is running

        Example:
            >>> run = SuiteRun(status="running")
            >>> run.is_running()
            True
            >>> run = SuiteRun(status="pending")
            >>> run.is_running()
            False
        """
        return self.status == 'running'

    def get_duration(self) -> Optional[float]:
        """
        Get suite run duration in seconds.

        Returns:
            Optional[float]: Duration in seconds, or None if not started/completed

        Example:
            >>> from datetime import datetime, timedelta
            >>> run = SuiteRun(
            ...     started_at=datetime.utcnow() - timedelta(seconds=60),
            ...     completed_at=datetime.utcnow()
            ... )
            >>> duration = run.get_duration()
            >>> duration >= 59.0 and duration <= 61.0
            True
        """
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            return delta.total_seconds()
        return None


# Backward compatibility alias - DEPRECATED, use SuiteRun instead
TestRun = SuiteRun
