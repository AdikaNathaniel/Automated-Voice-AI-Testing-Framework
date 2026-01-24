"""
Queue Manager Service

This service handles test execution queue management including:
- Adding tests to the execution queue
- Retrieving tests from the queue with priority ordering
- Updating queue item status
- Getting queue statistics

The queue manager coordinates test execution by managing priority-based
queue entries and tracking execution status.
"""

from uuid import UUID
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime

from models.test_execution_queue import TestExecutionQueue


class QueueManager:
    """
    Service class for test execution queue management.

    Provides methods for adding, retrieving, and managing test execution
    queue entries with priority-based ordering.

    Attributes:
        valid_statuses: List of valid queue entry statuses

    Example:
        >>> manager = QueueManager()
        >>> entry = await manager.enqueue_test(db, test_case_id, suite_run_id)
    """

    def __init__(self):
        """Initialize the queue manager."""
        self.valid_statuses = ["queued", "processing", "completed", "failed"]

    async def enqueue_test(
        self,
        db: AsyncSession,
        test_case_id: UUID,
        suite_run_id: UUID,
        priority: int = 5
    ) -> TestExecutionQueue:
        """Add a test case to the execution queue."""
        return await enqueue_test(db, test_case_id, suite_run_id, priority)

    async def dequeue_test(
        self,
        db: AsyncSession
    ) -> Optional[TestExecutionQueue]:
        """Get the next test from the execution queue."""
        return await dequeue_test(db)

    async def update_queue_status(
        self,
        db: AsyncSession,
        queue_id: UUID,
        status: str
    ) -> TestExecutionQueue:
        """Update the status of a queue entry."""
        return await update_queue_status(db, queue_id, status)

    async def get_queue_stats(
        self,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Get statistics about the execution queue."""
        return await get_queue_stats(db)


async def enqueue_test(
    db: AsyncSession,
    test_case_id: UUID,
    suite_run_id: UUID,
    priority: int = 5
) -> TestExecutionQueue:
    """
    Add a test case to the execution queue.

    Creates a queue entry for a test case execution within a suite run,
    with specified priority for queue ordering.

    Args:
        db: Database session
        test_case_id: UUID of the test case to execute
        suite_run_id: UUID of the suite run this execution belongs to
        priority: Execution priority (1-10, default 5, higher = more urgent)

    Returns:
        TestExecutionQueue: The created queue entry

    Raises:
        ValueError: If priority is out of valid range (1-10)

    Example:
        >>> queue_entry = await enqueue_test(
        ...     db=db,
        ...     test_case_id=UUID("..."),
        ...     suite_run_id=UUID("..."),
        ...     priority=7
        ... )
        >>> print(queue_entry.status)
        'queued'
    """
    # Validate priority range
    if priority < 1 or priority > 10:
        raise ValueError("Priority must be between 1 and 10")

    # Create queue entry
    # Note: The TestExecutionQueue model currently only has suite_run_id
    # In a full implementation, we would add a test_case_id column
    # For now, we'll create the entry with suite_run_id
    queue_entry = TestExecutionQueue(
        suite_run_id=suite_run_id,
        priority=priority,
        status="queued"
    )

    db.add(queue_entry)
    await db.commit()
    await db.refresh(queue_entry)

    return queue_entry


async def dequeue_test(
    db: AsyncSession
) -> Optional[TestExecutionQueue]:
    """
    Get the next test from the execution queue.

    Retrieves the highest priority queued test that is ready for execution.
    Items are ordered by priority (descending) and then by creation time
    (ascending) for FIFO within same priority.

    Args:
        db: Database session

    Returns:
        Optional[TestExecutionQueue]: Next queue entry to process, or None if queue is empty

    Example:
        >>> next_test = await dequeue_test(db=db)
        >>> if next_test:
        ...     print(f"Processing test with priority {next_test.priority}")
        ... else:
        ...     print("Queue is empty")
    """
    # Query for next queued item, ordered by priority (desc) and created_at (asc)
    result = await db.execute(
        select(TestExecutionQueue)
        .filter(TestExecutionQueue.status == "queued")
        .order_by(
            desc(TestExecutionQueue.priority),
            TestExecutionQueue.created_at
        )
        .limit(1)
    )

    queue_entry = result.scalar_one_or_none()

    if queue_entry:
        # Mark as processing
        queue_entry.mark_as_processing()
        await db.commit()
        await db.refresh(queue_entry)

    return queue_entry


async def update_queue_status(
    db: AsyncSession,
    queue_id: UUID,
    status: str
) -> TestExecutionQueue:
    """
    Update the status of a queue entry.

    Updates the status of a specific queue item. Valid statuses are:
    queued, processing, completed, failed.

    Args:
        db: Database session
        queue_id: UUID of the queue entry to update
        status: New status value

    Returns:
        TestExecutionQueue: The updated queue entry

    Raises:
        ValueError: If queue_id is not found
        ValueError: If status is not valid

    Example:
        >>> updated = await update_queue_status(
        ...     db=db,
        ...     queue_id=UUID("..."),
        ...     status="completed"
        ... )
        >>> print(updated.status)
        'completed'
    """
    # Validate status
    valid_statuses = ["queued", "processing", "completed", "failed"]
    if status not in valid_statuses:
        raise ValueError(f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}")

    # Get queue entry
    queue_entry = await db.get(TestExecutionQueue, queue_id)
    if not queue_entry:
        raise ValueError(f"Queue entry with ID {queue_id} not found")

    # Update status using appropriate method
    if status == "queued":
        queue_entry.mark_as_queued()
    elif status == "processing":
        queue_entry.mark_as_processing()
    elif status == "completed":
        queue_entry.mark_as_completed()
    elif status == "failed":
        queue_entry.mark_as_failed()

    await db.commit()
    await db.refresh(queue_entry)

    return queue_entry


async def get_queue_stats(
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Get statistics about the execution queue.

    Returns comprehensive statistics about the queue including counts by
    status, average priority, and queue depth.

    Args:
        db: Database session

    Returns:
        Dict containing:
            - total: Total number of queue entries
            - queued: Number of queued entries
            - processing: Number of processing entries
            - completed: Number of completed entries
            - failed: Number of failed entries
            - average_priority: Average priority of queued items
            - oldest_queued: Age in seconds of oldest queued item (or None)

    Example:
        >>> stats = await get_queue_stats(db=db)
        >>> print(f"Queue depth: {stats['queued']}")
        >>> print(f"Average priority: {stats['average_priority']}")
    """
    # Get counts by status
    total_result = await db.execute(
        select(func.count(TestExecutionQueue.id))
    )
    total = total_result.scalar() or 0

    queued_result = await db.execute(
        select(func.count(TestExecutionQueue.id))
        .filter(TestExecutionQueue.status == "queued")
    )
    queued = queued_result.scalar() or 0

    processing_result = await db.execute(
        select(func.count(TestExecutionQueue.id))
        .filter(TestExecutionQueue.status == "processing")
    )
    processing = processing_result.scalar() or 0

    completed_result = await db.execute(
        select(func.count(TestExecutionQueue.id))
        .filter(TestExecutionQueue.status == "completed")
    )
    completed = completed_result.scalar() or 0

    failed_result = await db.execute(
        select(func.count(TestExecutionQueue.id))
        .filter(TestExecutionQueue.status == "failed")
    )
    failed = failed_result.scalar() or 0

    # Get average priority of queued items
    avg_priority_result = await db.execute(
        select(func.avg(TestExecutionQueue.priority))
        .filter(TestExecutionQueue.status == "queued")
    )
    avg_priority = avg_priority_result.scalar()
    average_priority = float(avg_priority) if avg_priority is not None else 0.0

    # Get oldest queued item
    oldest_result = await db.execute(
        select(TestExecutionQueue.created_at)
        .filter(TestExecutionQueue.status == "queued")
        .order_by(TestExecutionQueue.created_at)
        .limit(1)
    )
    oldest_created_at = oldest_result.scalar_one_or_none()

    oldest_queued_seconds = None
    if oldest_created_at:
        age_delta = datetime.utcnow() - oldest_created_at
        oldest_queued_seconds = age_delta.total_seconds()

    return {
        "total": total,
        "queued": queued,
        "processing": processing,
        "completed": completed,
        "failed": failed,
        "average_priority": round(average_priority, 2),
        "oldest_queued_seconds": oldest_queued_seconds
    }
