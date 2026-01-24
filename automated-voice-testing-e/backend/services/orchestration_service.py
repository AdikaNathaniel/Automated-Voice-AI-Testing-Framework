"""
Orchestration Service

This service provides a unified interface for test execution orchestration.
It coordinates between TestRunService and ExecutionSchedulerService to handle:
- Creating and managing test runs
- Scheduling test executions via Celery tasks
- Canceling running tests
- Retrying failed tests

The OrchestrationService acts as a facade, delegating to specialized services
while maintaining backward compatibility with existing API consumers.
"""

import logging
from uuid import UUID
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from models.suite_run import SuiteRun
from models.multi_turn_execution import MultiTurnExecution
from models import user  # noqa: F401
from models import scenario_script  # noqa: F401
from models import validation_queue  # noqa: F401
from models import human_validation  # noqa: F401
from models import validation_result  # noqa: F401
from models import validator_performance  # noqa: F401

from services.suite_run_service import SuiteRunService
from services.execution_scheduler_service import ExecutionSchedulerService

logger = logging.getLogger(__name__)


class OrchestrationService:
    """
    Unified service for test execution orchestration.

    Coordinates between SuiteRunService and ExecutionSchedulerService
    to provide a complete test execution workflow.
    """

    def __init__(self) -> None:
        """Initialize orchestration service with dependencies."""
        self._suite_run_service = SuiteRunService()
        self._scheduler_service = ExecutionSchedulerService()

    async def create_suite_run(
        self,
        db: AsyncSession,
        suite_id: Optional[UUID] = None,
        scenario_ids: Optional[List[UUID]] = None,
        languages: Optional[List[str]] = None,
        trigger_type: str = "manual",
        trigger_metadata: Optional[Dict[str, Any]] = None,
        created_by: Optional[UUID] = None,
        tenant_id: Optional[UUID] = None,
    ) -> SuiteRun:
        """
        Create a new suite run.

        Delegates to SuiteRunService for suite run creation.

        Args:
            db: Database session
            suite_id: UUID of the test suite to run (optional)
            scenario_ids: List of scenario script UUIDs to run (optional)
            languages: List of language codes to test (optional)
            trigger_type: Type of trigger
            trigger_metadata: Additional metadata (optional)
            created_by: UUID of the creator (optional)
            tenant_id: UUID of the tenant (optional)

        Returns:
            SuiteRun: The created suite run instance
        """
        try:
            return await self._suite_run_service.create_suite_run(
                db=db,
                suite_id=suite_id,
                scenario_ids=scenario_ids,
                languages=languages,
                trigger_type=trigger_type,
                trigger_metadata=trigger_metadata,
                created_by=created_by,
                tenant_id=tenant_id,
            )
        except Exception as e:
            logger.error(
                "Error creating suite run: %s",
                str(e),
                exc_info=True,
                extra={
                    "suite_id": str(suite_id) if suite_id else None,
                    "trigger_type": trigger_type,
                    "tenant_id": str(tenant_id) if tenant_id else None,
                }
            )
            raise RuntimeError(f"Failed to create suite run: {str(e)}") from e

    async def schedule_test_executions(
        self,
        db: AsyncSession,
        suite_run_id: UUID,
        tenant_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """
        Schedule test executions for a suite run.

        Delegates to ExecutionSchedulerService for scheduling.

        Args:
            db: Database session
            suite_run_id: UUID of the suite run
            tenant_id: UUID of the tenant (optional)

        Returns:
            Dict with suite_run_id, scheduled_count, and task_ids
        """
        try:
            return await self._scheduler_service.schedule_test_executions(
                db=db,
                suite_run_id=suite_run_id,
                tenant_id=tenant_id,
            )
        except Exception as e:
            logger.error(
                "Error scheduling test executions for suite_run_id %s: %s",
                suite_run_id, str(e),
                exc_info=True,
                extra={
                    "suite_run_id": str(suite_run_id),
                    "tenant_id": str(tenant_id) if tenant_id else None,
                }
            )
            raise RuntimeError(
                f"Failed to schedule test executions for suite_run_id {suite_run_id}: {str(e)}"
            ) from e

    async def list_suite_runs(
        self,
        db: AsyncSession,
        *,
        suite_id: Optional[UUID] = None,
        status_filter: Optional[str] = None,
        created_by: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50,
        language_code: Optional[str] = None,
        tenant_id: Optional[UUID] = None,
    ) -> tuple[list[SuiteRun], int]:
        """
        Retrieve paginated suite runs with optional filtering.

        Delegates to SuiteRunService and hydrates with language metadata.

        Args:
            db: Database session
            suite_id: Filter by test suite UUID
            status_filter: Filter by status
            created_by: Filter by creator
            start_date: Filter by start date
            end_date: Filter by end date
            skip: Number of records to skip
            limit: Maximum records to return
            language_code: Filter by language code
            tenant_id: Filter by tenant

        Returns:
            Tuple of (list of suite runs, total count)
        """
        try:
            runs, total = await self._suite_run_service.list_suite_runs(
                db=db,
                suite_id=suite_id,
                status_filter=status_filter,
                created_by=created_by,
                start_date=start_date,
                end_date=end_date,
                skip=skip,
                limit=limit,
                language_code=language_code,
                tenant_id=tenant_id,
            )

            if runs:
                await self._scheduler_service.hydrate_run_language_metadata(db, runs)

            return runs, total
        except Exception as e:
            logger.error(
                "Error listing suite runs: %s",
                str(e),
                exc_info=True,
                extra={
                    "suite_id": str(suite_id) if suite_id else None,
                    "status_filter": status_filter,
                    "skip": skip,
                    "limit": limit,
                }
            )
            raise RuntimeError(f"Failed to list suite runs: {str(e)}") from e

    async def get_suite_run_executions(
        self,
        db: AsyncSession,
        *,
        suite_run_id: UUID,
        status_filter: Optional[str] = None,
    ) -> list[MultiTurnExecution]:
        """
        Retrieve executions for a given suite run.

        Delegates to ExecutionSchedulerService.

        Args:
            db: Database session
            suite_run_id: UUID of the suite run
            status_filter: Optional status to filter by

        Returns:
            List of MultiTurnExecution instances
        """
        try:
            return await self._scheduler_service.get_suite_run_executions(
                db=db,
                suite_run_id=suite_run_id,
                status_filter=status_filter,
            )
        except Exception as e:
            logger.error(
                "Error getting executions for suite_run_id %s: %s",
                suite_run_id, str(e),
                exc_info=True,
                extra={
                    "suite_run_id": str(suite_run_id),
                    "status_filter": status_filter,
                }
            )
            raise RuntimeError(
                f"Failed to get executions for suite_run_id {suite_run_id}: {str(e)}"
            ) from e

    async def cancel_suite_run(
        self,
        db: AsyncSession,
        suite_run_id: UUID,
        tenant_id: Optional[UUID] = None,
    ) -> SuiteRun:
        """
        Cancel a running suite run.

        Delegates to SuiteRunService for cancellation.

        Args:
            db: Database session
            suite_run_id: UUID of the suite run to cancel
            tenant_id: UUID of the tenant (optional)

        Returns:
            SuiteRun: The updated suite run instance
        """
        try:
            return await self._suite_run_service.cancel_suite_run(
                db=db,
                suite_run_id=suite_run_id,
                tenant_id=tenant_id,
            )
        except Exception as e:
            logger.error(
                "Error canceling suite_run_id %s: %s",
                suite_run_id, str(e),
                exc_info=True,
                extra={
                    "suite_run_id": str(suite_run_id),
                    "tenant_id": str(tenant_id) if tenant_id else None,
                }
            )
            raise RuntimeError(
                f"Failed to cancel suite_run_id {suite_run_id}: {str(e)}"
            ) from e

    async def retry_failed_tests(
        self,
        db: AsyncSession,
        suite_run_id: UUID,
        tenant_id: Optional[UUID] = None,
    ) -> SuiteRun:
        """
        Retry failed tests from a suite run.

        Creates a new suite run and schedules executions for failed tests.

        Args:
            db: Database session
            suite_run_id: UUID of the suite run with failed tests
            tenant_id: UUID of the tenant (optional)

        Returns:
            SuiteRun: A new suite run instance for retrying failed tests
        """
        try:
            new_run = await self._suite_run_service.retry_failed_tests(
                db=db,
                suite_run_id=suite_run_id,
                tenant_id=tenant_id,
            )

            await self._scheduler_service.schedule_test_executions(
                db=db,
                suite_run_id=new_run.id,
                tenant_id=tenant_id,
            )

            return new_run
        except Exception as e:
            logger.error(
                "Error retrying failed tests for suite_run_id %s: %s",
                suite_run_id, str(e),
                exc_info=True,
                extra={
                    "suite_run_id": str(suite_run_id),
                    "tenant_id": str(tenant_id) if tenant_id else None,
                }
            )
            raise RuntimeError(
                f"Failed to retry tests for suite_run_id {suite_run_id}: {str(e)}"
            ) from e


# Backward compatibility: module-level functions that delegate to service
_default_service = None


def _get_service() -> OrchestrationService:
    """Get or create default service instance."""
    global _default_service
    if _default_service is None:
        _default_service = OrchestrationService()
    return _default_service


async def create_suite_run(
    db: AsyncSession,
    suite_id: Optional[UUID] = None,
    test_case_ids: Optional[List[UUID]] = None,
    languages: Optional[List[str]] = None,
    trigger_type: str = "manual",
    trigger_metadata: Optional[Dict[str, Any]] = None,
    created_by: Optional[UUID] = None,
    tenant_id: Optional[UUID] = None,
) -> SuiteRun:
    """Create a new suite run (backward compatible function)."""
    return await _get_service().create_suite_run(
        db=db,
        suite_id=suite_id,
        test_case_ids=test_case_ids,
        languages=languages,
        trigger_type=trigger_type,
        trigger_metadata=trigger_metadata,
        created_by=created_by,
        tenant_id=tenant_id,
    )


async def schedule_test_executions(
    db: AsyncSession,
    suite_run_id: UUID,
    tenant_id: Optional[UUID] = None,
) -> Dict[str, Any]:
    """Schedule test executions (backward compatible function)."""
    return await _get_service().schedule_test_executions(
        db=db,
        suite_run_id=suite_run_id,
        tenant_id=tenant_id,
    )


async def list_suite_runs(
    db: AsyncSession,
    *,
    suite_id: Optional[UUID] = None,
    status_filter: Optional[str] = None,
    created_by: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 50,
    language_code: Optional[str] = None,
    tenant_id: Optional[UUID] = None,
) -> tuple[list[SuiteRun], int]:
    """List suite runs (backward compatible function)."""
    return await _get_service().list_suite_runs(
        db=db,
        suite_id=suite_id,
        status_filter=status_filter,
        created_by=created_by,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
        language_code=language_code,
        tenant_id=tenant_id,
    )


async def get_suite_run_executions(
    db: AsyncSession,
    *,
    suite_run_id: UUID,
    status_filter: Optional[str] = None,
) -> list[MultiTurnExecution]:
    """Get suite run executions (backward compatible function)."""
    return await _get_service().get_suite_run_executions(
        db=db,
        suite_run_id=suite_run_id,
        status_filter=status_filter,
    )


async def cancel_suite_run(
    db: AsyncSession,
    suite_run_id: UUID,
    tenant_id: Optional[UUID] = None,
) -> SuiteRun:
    """Cancel suite run (backward compatible function)."""
    return await _get_service().cancel_suite_run(
        db=db,
        suite_run_id=suite_run_id,
        tenant_id=tenant_id,
    )


async def retry_failed_tests(
    db: AsyncSession,
    suite_run_id: UUID,
    tenant_id: Optional[UUID] = None,
) -> SuiteRun:
    """Retry failed tests (backward compatible function)."""
    return await _get_service().retry_failed_tests(
        db=db,
        suite_run_id=suite_run_id,
        tenant_id=tenant_id,
    )
