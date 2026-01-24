"""
ValidationQueueService for managing human validation task queue

This module provides the ValidationQueueService class which manages the queue
of validation tasks awaiting human review. It handles task enqueueing, assignment,
claiming, releasing, and statistics tracking.

The service provides:
    - Task enqueueing: Add validation results to the queue with priority
    - Task retrieval: Get next validation task for a validator
    - Task claiming: Claim a validation task for a validator
    - Task releasing: Release a claimed task back to the queue
    - Queue statistics: Get current queue metrics

Example:
    >>> from services.validation_queue_service import ValidationQueueService
    >>> from api.dependencies import get_db
    >>>
    >>> service = ValidationQueueService()
    >>> # Enqueue a validation result for human review
    >>> queue_item = await service.enqueue_for_human_review(
    ...     db=db,
    ...     validation_result_id=result_id,
    ...     priority=3,
    ...     confidence_score=65.5,
    ...     language_code='es-MX'
    ... )
    >>>
    >>> # Get next validation task for a validator
    >>> next_task = await service.get_next_validation(
    ...     db=db,
    ...     validator_id=user_id,
    ...     language_code='es'
    ... )
"""

from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from models.validation_queue import ValidationQueue
from models.validation_result import ValidationResult
from models.multi_turn_execution import MultiTurnExecution, StepExecution
from models.scenario_script import ScenarioScript, ScenarioStep
from models.human_validation import HumanValidation
from models.user import User


class ValidationQueueService:
    """
    Service for managing the validation queue.

    Handles all operations related to the validation task queue including
    enqueueing new tasks, retrieving tasks for validators, claiming and
    releasing tasks, and providing queue statistics.

    Methods:
        enqueue_for_human_review: Add a validation result to the queue
        get_next_validation: Get the next validation task for a validator
        claim_validation: Claim a validation task for a validator
        release_validation: Release a claimed task back to the queue
        get_queue_stats: Get current queue statistics
    """

    async def enqueue_for_human_review(
        self,
        db: AsyncSession,
        validation_result_id: UUID,
        priority: int = 5,
        confidence_score: Optional[Decimal] = None,
        language_code: Optional[str] = None,
        requires_native_speaker: bool = False
    ) -> ValidationQueue:
        """
        Add a validation result to the queue for human review.

        Creates a new queue item with the specified priority and configuration.
        Lower priority numbers are processed first (1 = highest priority).

        Args:
            db: Async database session
            validation_result_id: UUID of the validation result to review
            priority: Priority level (1-10, default=5, 1=highest)
            confidence_score: AI confidence score (0.00-100.00)
            language_code: Language code for validator matching (e.g., 'es-MX')
            requires_native_speaker: Whether a native speaker is required

        Returns:
            ValidationQueue: Created queue item

        Example:
            >>> queue_item = await service.enqueue_for_human_review(
            ...     db=db,
            ...     validation_result_id=result_id,
            ...     priority=2,
            ...     confidence_score=Decimal('72.50'),
            ...     language_code='fr-FR',
            ...     requires_native_speaker=True
            ... )
        """
        queue_item = ValidationQueue(
            validation_result_id=validation_result_id,
            priority=priority,
            confidence_score=confidence_score,
            language_code=language_code,
            status='pending',
            requires_native_speaker=requires_native_speaker
        )

        db.add(queue_item)
        await db.commit()
        await db.refresh(queue_item)

        return queue_item

    async def get_next_validation(
        self,
        db: AsyncSession,
        validator_id: UUID,
        language_code: Optional[str] = None,
        tenant_id: Optional[UUID] = None,
    ) -> Optional[ValidationQueue]:
        """
        Get the next validation task for a validator.

        Retrieves the highest priority pending validation task, optionally
        matching the validator's language code. Tasks are ordered by:
        1. Priority (ascending, 1 = highest)
        2. Creation time (oldest first)

        Args:
            db: Async database session
            validator_id: UUID of the validator requesting a task
            language_code: Optional language code for language matching

        Returns:
            Optional[ValidationQueue]: Next validation task, or None if queue is empty

        Example:
            >>> next_task = await service.get_next_validation(
            ...     db=db,
            ...     validator_id=user_id,
            ...     language_code='es'
            ... )
            >>> if next_task:
            ...     print(f"Task priority: {next_task.priority}")
        """
        # Build base query for pending tasks
        query = select(ValidationQueue).where(
            ValidationQueue.status == 'pending'
        )
        if tenant_id:
            query = query.where(
                ValidationQueue.validation_result.has(ValidationResult.tenant_id == tenant_id)
            )

        # If language code provided, prefer matching tasks
        if language_code:
            # Try to find a task matching the language
            language_query = query.where(
                or_(
                    ValidationQueue.language_code == language_code,
                    ValidationQueue.language_code.like(f"{language_code}%")
                )
            ).order_by(
                ValidationQueue.priority.asc(),
                ValidationQueue.created_at.asc()
            ).limit(1)

            result = await db.execute(language_query)
            task = result.scalar_one_or_none()

            if task:
                return task

        # If no language match or no language specified, get any pending task
        general_query = query.order_by(
            ValidationQueue.priority.asc(),
            ValidationQueue.created_at.asc()
        ).limit(1)

        result = await db.execute(general_query)
        return result.scalar_one_or_none()

    async def get_validations_by_user(
        self,
        db: AsyncSession,
        validator_id: UUID,
        status: Optional[str] = None,
        language_code: Optional[str] = None,
        tenant_id: Optional[UUID] = None,
        limit: int = 100,
    ) -> List[ValidationQueue]:
        """
        Get validation queue items for a specific user.

        Retrieves validation queue items claimed by or completed by a specific
        validator, optionally filtered by status and language.

        Args:
            db: Async database session
            validator_id: UUID of the validator
            status: Optional status filter (claimed, completed)
            language_code: Optional language code filter
            tenant_id: Optional tenant ID for filtering
            limit: Maximum number of items to return (default 100)

        Returns:
            List[ValidationQueue]: List of validation queue items

        Example:
            >>> claimed_items = await service.get_validations_by_user(
            ...     db=db,
            ...     validator_id=user_id,
            ...     status='claimed'
            ... )
            >>> print(f"User has {len(claimed_items)} claimed items")
        """
        # Build query for items claimed by this user
        query = select(ValidationQueue).where(
            ValidationQueue.claimed_by == validator_id
        )

        if tenant_id:
            query = query.where(
                ValidationQueue.validation_result.has(ValidationResult.tenant_id == tenant_id)
            )

        # Apply status filter
        if status:
            query = query.where(ValidationQueue.status == status)

        # Apply language filter
        if language_code:
            query = query.where(
                or_(
                    ValidationQueue.language_code == language_code,
                    ValidationQueue.language_code.like(f"{language_code}%")
                )
            )

        # Order by most recently claimed first
        query = query.order_by(
            ValidationQueue.claimed_at.desc()
        ).limit(limit)

        result = await db.execute(query)
        return list(result.scalars().all())

    async def claim_validation(
        self,
        db: AsyncSession,
        queue_id: UUID,
        validator_id: UUID,
        tenant_id: Optional[UUID] = None,
    ) -> bool:
        """
        Claim a validation task for a validator.

        Marks a pending validation task as claimed by the specified validator.
        Only pending tasks can be claimed.

        Args:
            db: Async database session
            queue_id: UUID of the queue item to claim
            validator_id: UUID of the validator claiming the task

        Returns:
            bool: True if task was successfully claimed, False otherwise

        Example:
            >>> success = await service.claim_validation(
            ...     db=db,
            ...     queue_id=task_id,
            ...     validator_id=user_id
            ... )
            >>> if success:
            ...     print("Task claimed successfully")
        """
        # Find the queue item
        query = select(ValidationQueue).where(
            and_(
                ValidationQueue.id == queue_id,
                ValidationQueue.status == 'pending'
            )
        )
        if tenant_id:
            query = query.where(
                ValidationQueue.validation_result.has(ValidationResult.tenant_id == tenant_id)
            )

        result = await db.execute(query)
        queue_item = result.scalar_one_or_none()

        if not queue_item:
            return False

        # Claim the task
        queue_item.status = 'claimed'
        queue_item.claimed_by = validator_id
        queue_item.claimed_at = datetime.utcnow()

        await db.commit()
        return True

    async def get_validation_data(
        self,
        db: AsyncSession,
        queue_id: UUID,
        tenant_id: Optional[UUID] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Get full validation data for a queue item.

        Retrieves all data needed for the validation interface including:
        - Queue item metadata (ID, priority, confidence, language)
        - Test case information (scenario name, step details)
        - Input data (user utterance, audio URL)
        - Expected outcomes (intent, entities, response)
        - Actual results (intent, entities, response)
        - Context information

        Args:
            db: Async database session
            queue_id: UUID of the queue item
            tenant_id: Optional tenant ID for filtering

        Returns:
            Dict with validation data, or None if not found

        Example:
            >>> data = await service.get_validation_data(
            ...     db=db,
            ...     queue_id=queue_id
            ... )
            >>> print(data['test_case_name'])
            'Weather Forecast Query - Step 1'
        """
        # Query with all necessary joins
        query = (
            select(ValidationQueue)
            .options(
                joinedload(ValidationQueue.validation_result)
                .joinedload(ValidationResult.step_execution)
                .joinedload(StepExecution.step)
                .joinedload(ScenarioStep.expected_outcomes),
                joinedload(ValidationQueue.validation_result)
                .joinedload(ValidationResult.step_execution)
                .joinedload(StepExecution.multi_turn_execution)
                .joinedload(MultiTurnExecution.script),
                joinedload(ValidationQueue.validation_result)
                .joinedload(ValidationResult.expected_outcome),
                joinedload(ValidationQueue.validation_result)
                .selectinload(ValidationResult.human_validations)
                .joinedload(HumanValidation.validator),
            )
            .where(ValidationQueue.id == queue_id)
        )

        if tenant_id:
            query = query.where(
                ValidationQueue.validation_result.has(ValidationResult.tenant_id == tenant_id)
            )

        result = await db.execute(query)
        queue_item = result.unique().scalar_one_or_none()

        if not queue_item or not queue_item.validation_result:
            return None

        validation_result = queue_item.validation_result
        step_execution = validation_result.step_execution
        expected_outcome = validation_result.expected_outcome

        # Extract data from relationships
        scenario_name = "Unknown Scenario"
        step_order = 0
        total_steps = 0
        input_text = None
        expected_command_kind = None
        actual_command_kind = None
        expected_entities = None
        actual_entities = None
        expected_response_content = None
        actual_response = None
        context = None
        input_audio_url = None
        response_audio_url = None
        language_code = queue_item.language_code

        if step_execution:
            # Get scenario and step information
            multi_turn_execution = step_execution.multi_turn_execution
            step_order = step_execution.step_order

            if multi_turn_execution:
                total_steps = multi_turn_execution.total_steps

                # Get scenario name from script
                if multi_turn_execution.script:
                    scenario_name = multi_turn_execution.script.name

                    # Get language from script metadata if not already set
                    if not language_code and multi_turn_execution.script.script_metadata:
                        language_code = multi_turn_execution.script.script_metadata.get('language')

            # Get input text (user utterance) from step execution
            input_text = step_execution.user_utterance

            # Get actual results from step execution
            actual_command_kind = step_execution.command_kind
            actual_response = step_execution.ai_response

            # Get entities from validation_details if available
            if step_execution.validation_details:
                actual_entities = step_execution.validation_details.get('actual_entities') or step_execution.validation_details.get('NativeData')

            # Get audio URL if available
            # audio_data_urls is a dict mapping language codes to URLs
            # Use the language_code from queue_item to get the correct audio
            input_audio_url = None
            if step_execution.audio_data_urls:
                # If language_code not set, extract from audio_data_urls keys
                if not language_code:
                    # Get first available language from audio_data_urls
                    available_languages = list(step_execution.audio_data_urls.keys())
                    if available_languages:
                        language_code = available_languages[0]

                # Try to get audio for the specific language
                input_audio_url = step_execution.audio_data_urls.get(language_code)
                # Fallback to first available language if not found
                if not input_audio_url and step_execution.audio_data_urls:
                    input_audio_url = next(iter(step_execution.audio_data_urls.values()), None)

            # Get response audio URL (TTS from Houndify) for the specific language
            response_audio_url = None
            if hasattr(step_execution, 'response_audio_urls') and step_execution.response_audio_urls:
                # Try to get response audio for the specific language
                response_audio_url = step_execution.response_audio_urls.get(language_code)
                # Fallback to first available language if not found
                if not response_audio_url:
                    response_audio_url = next(iter(step_execution.response_audio_urls.values()), None)

            # Build context information
            if step_order > 1:
                context = f"Step {step_order} of {total_steps} in multi-turn conversation"
            else:
                context = f"First step of {total_steps}-step scenario"

        # Get expected outcomes from validation_result.expected_outcome first
        if expected_outcome:
            expected_command_kind = expected_outcome.expected_command_kind
            # expected_response_content is a JSONB field containing patterns
            expected_response_content = expected_outcome.expected_response_content
            # expected_native_data_schema is a JSONB field containing schema/constraints
            expected_entities = expected_outcome.expected_native_data_schema
        elif step_execution and step_execution.step and step_execution.step.expected_outcomes:
            # Fallback: Get expected outcomes from the step's expected_outcomes relationship
            # Use the first expected outcome if multiple exist
            step_expected_outcomes = list(step_execution.step.expected_outcomes)
            if step_expected_outcomes:
                first_outcome = step_expected_outcomes[0]
                expected_command_kind = first_outcome.expected_command_kind
                expected_response_content = first_outcome.expected_response_content
                expected_entities = first_outcome.expected_native_data_schema

        # Build test case name from scenario and step
        test_case_name = f"{scenario_name} - Step {step_order}" if step_order > 0 else scenario_name

        # Build AI validation scores from ValidationResult
        ai_scores = {
            # Core validation scores
            "asr_confidence_score": float(validation_result.asr_confidence_score) if validation_result.asr_confidence_score else None,
            "command_kind_match_score": float(validation_result.command_kind_match_score) if validation_result.command_kind_match_score else None,
            # LLM Ensemble validation fields
            "houndify_passed": validation_result.houndify_passed,
            "houndify_result": validation_result.houndify_result,
            "llm_passed": validation_result.llm_passed,
            "ensemble_result": validation_result.ensemble_result,
            "final_decision": validation_result.final_decision,
            # Review status
            "review_status": validation_result.review_status,
        }

        # Build validation history from all human validations
        validation_history = []
        human_validation_decision = None
        human_validation_feedback = None
        human_validation_submitted_at = None
        human_validation_validator_name = None

        if validation_result.human_validations:
            # Sort by submitted_at descending (most recent first)
            sorted_validations = sorted(
                validation_result.human_validations,
                key=lambda hv: hv.submitted_at or hv.created_at or datetime.min,
                reverse=True
            )

            for hv in sorted_validations:
                validator_name = None
                if hv.validator:
                    validator_name = hv.validator.full_name or hv.validator.username or hv.validator.email

                validation_history.append({
                    "id": str(hv.id),
                    "validator_id": str(hv.validator_id) if hv.validator_id else None,
                    "validator_name": validator_name,
                    "decision": hv.validation_decision,
                    "feedback": hv.feedback,
                    "time_spent_seconds": hv.time_spent_seconds,
                    "is_second_opinion": hv.is_second_opinion,
                    "claimed_at": hv.claimed_at.isoformat() if hv.claimed_at else None,
                    "submitted_at": hv.submitted_at.isoformat() if hv.submitted_at else None,
                    "created_at": hv.created_at.isoformat() if hv.created_at else None,
                })

            # Set primary human validation data from most recent
            if sorted_validations:
                most_recent = sorted_validations[0]
                human_validation_decision = most_recent.validation_decision
                human_validation_feedback = most_recent.feedback
                human_validation_submitted_at = most_recent.submitted_at.isoformat() if most_recent.submitted_at else None
                if most_recent.validator:
                    human_validation_validator_name = most_recent.validator.full_name or most_recent.validator.username or most_recent.validator.email

        # Build response data matching frontend ValidationQueue interface
        # Note: queue_item.confidence_score is stored as 0-100 range,
        # but frontend expects 0-1 range, so we normalize it here
        normalized_confidence = None
        if queue_item.confidence_score is not None:
            confidence_float = float(queue_item.confidence_score)
            # If confidence > 1, it's stored as percentage (0-100), normalize to 0-1
            normalized_confidence = confidence_float / 100.0 if confidence_float > 1 else confidence_float

        return {
            "id": str(queue_item.id),
            "validation_result_id": str(queue_item.validation_result_id),
            "priority": queue_item.priority,
            "confidence_score": normalized_confidence,
            "language_code": language_code,  # Use extracted language_code (from queue, script metadata, or audio_data_urls)
            "status": queue_item.status,
            "claimed_by": str(queue_item.claimed_by) if queue_item.claimed_by else None,
            "claimed_at": queue_item.claimed_at.isoformat() if queue_item.claimed_at else None,
            "created_at": queue_item.created_at.isoformat() if queue_item.created_at else None,
            "updated_at": queue_item.updated_at.isoformat() if queue_item.updated_at else None,
            "test_case_name": test_case_name,
            "input_text": input_text,
            "expected_command_kind": expected_command_kind,
            "actual_command_kind": actual_command_kind,
            "expected_entities": expected_entities,
            "actual_entities": actual_entities,
            "expected_response_content": expected_response_content,
            "actual_response": actual_response,
            "context": context,
            "input_audio_url": input_audio_url,
            "response_audio_url": response_audio_url,
            # AI validation scores
            "ai_scores": ai_scores,
            # Human validation data (most recent, if completed)
            "human_validation_decision": human_validation_decision,
            "human_validation_feedback": human_validation_feedback,
            "human_validation_submitted_at": human_validation_submitted_at,
            "human_validation_validator_name": human_validation_validator_name,
            # Full validation history
            "validation_history": validation_history,
        }

    async def release_validation(
        self,
        db: AsyncSession,
        queue_id: UUID,
        tenant_id: Optional[UUID] = None,
    ) -> bool:
        """
        Release a claimed validation task back to the queue.

        Returns a claimed task to pending status, removing the validator
        assignment. Only claimed tasks can be released.

        Args:
            db: Async database session
            queue_id: UUID of the queue item to release

        Returns:
            bool: True if task was successfully released, False otherwise

        Example:
            >>> success = await service.release_validation(
            ...     db=db,
            ...     queue_id=task_id
            ... )
            >>> if success:
            ...     print("Task released back to queue")
        """
        # Find the claimed queue item
        query = select(ValidationQueue).where(
            and_(
                ValidationQueue.id == queue_id,
                ValidationQueue.status == 'claimed'
            )
        )
        if tenant_id:
            query = query.where(
                ValidationQueue.validation_result.has(ValidationResult.tenant_id == tenant_id)
            )

        result = await db.execute(query)
        queue_item = result.scalar_one_or_none()

        if not queue_item:
            return False

        # Release the task
        queue_item.status = 'pending'
        queue_item.claimed_by = None
        queue_item.claimed_at = None

        await db.commit()
        return True

    async def get_queue_stats(
        self,
        db: AsyncSession,
        tenant_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """
        Get current queue statistics.

        Returns comprehensive statistics about the validation queue including
        counts by status, priority distribution, language breakdown, throughput
        metrics, and SLA metrics.

        Args:
            db: Async database session
            tenant_id: Optional tenant ID to filter statistics

        Returns:
            Dict[str, Any]: Dictionary containing queue statistics with keys:
                - pending_count: Number of pending tasks
                - claimed_count: Number of claimed tasks
                - completed_count: Number of completed tasks
                - total_count: Total tasks across all statuses
                - priority_distribution: Count of tasks by priority level
                - language_distribution: Count of tasks by language (top 10)
                - throughput: Dict with keys:
                    - last_hour: Validations completed in last hour
                    - last_24_hours: Validations completed in last 24 hours
                    - last_7_days: Validations completed in last 7 days
                    - avg_per_hour: Average validations per hour (7-day basis)
                - sla: Dict with keys:
                    - avg_time_to_claim_seconds: Average time from pending to claimed
                    - avg_time_to_complete_seconds: Average time from claimed to completed
                    - avg_total_time_seconds: Average total time from pending to completed

        Example:
            >>> stats = await service.get_queue_stats(db=db)
            >>> print(f"Pending tasks: {stats['pending_count']}")
            >>> print(f"Throughput last hour: {stats['throughput']['last_hour']}")
            >>> print(f"Avg time to claim: {stats['sla']['avg_time_to_claim_seconds']}s")
        """
        # Count by status
        pending_query = select(func.count()).select_from(ValidationQueue).where(
            ValidationQueue.status == 'pending'
        )
        if tenant_id:
            pending_query = pending_query.where(
                ValidationQueue.validation_result.has(ValidationResult.tenant_id == tenant_id)
            )
        claimed_query = select(func.count()).select_from(ValidationQueue).where(
            ValidationQueue.status == 'claimed'
        )
        if tenant_id:
            claimed_query = claimed_query.where(
                ValidationQueue.validation_result.has(ValidationResult.tenant_id == tenant_id)
            )
        completed_query = select(func.count()).select_from(ValidationQueue).where(
            ValidationQueue.status == 'completed'
        )
        if tenant_id:
            completed_query = completed_query.where(
                ValidationQueue.validation_result.has(ValidationResult.tenant_id == tenant_id)
            )

        pending_count = (await db.execute(pending_query)).scalar()
        claimed_count = (await db.execute(claimed_query)).scalar()
        completed_count = (await db.execute(completed_query)).scalar()

        # Get priority distribution for pending tasks
        priority_query = select(
            ValidationQueue.priority,
            func.count().label('count')
        ).where(
            ValidationQueue.status == 'pending'
        ).group_by(
            ValidationQueue.priority
        ).order_by(
            ValidationQueue.priority
        )
        if tenant_id:
            priority_query = priority_query.where(
                ValidationQueue.validation_result.has(ValidationResult.tenant_id == tenant_id)
            )

        priority_result = await db.execute(priority_query)
        priority_distribution = {
            row.priority: row.count
            for row in priority_result
        }

        # Get language distribution for pending tasks
        language_query = select(
            ValidationQueue.language_code,
            func.count().label('count')
        ).where(
            and_(
                ValidationQueue.status == 'pending',
                ValidationQueue.language_code.isnot(None)
            )
        ).group_by(
            ValidationQueue.language_code
        ).order_by(
            func.count().desc()
        ).limit(10)
        if tenant_id:
            language_query = language_query.where(
                ValidationQueue.validation_result.has(ValidationResult.tenant_id == tenant_id)
            )

        language_result = await db.execute(language_query)
        language_distribution = {
            row.language_code: row.count
            for row in language_result
        }

        # Calculate throughput metrics
        from datetime import datetime, timedelta

        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)
        one_day_ago = now - timedelta(hours=24)
        seven_days_ago = now - timedelta(days=7)

        # Count completed validations in different time windows
        # Using updated_at as a proxy for completion time
        throughput_hour_query = select(func.count()).select_from(ValidationQueue).where(
            and_(
                ValidationQueue.status == 'completed',
                ValidationQueue.updated_at >= one_hour_ago
            )
        )
        throughput_24h_query = select(func.count()).select_from(ValidationQueue).where(
            and_(
                ValidationQueue.status == 'completed',
                ValidationQueue.updated_at >= one_day_ago
            )
        )
        throughput_7d_query = select(func.count()).select_from(ValidationQueue).where(
            and_(
                ValidationQueue.status == 'completed',
                ValidationQueue.updated_at >= seven_days_ago
            )
        )

        if tenant_id:
            throughput_hour_query = throughput_hour_query.where(
                ValidationQueue.validation_result.has(ValidationResult.tenant_id == tenant_id)
            )
            throughput_24h_query = throughput_24h_query.where(
                ValidationQueue.validation_result.has(ValidationResult.tenant_id == tenant_id)
            )
            throughput_7d_query = throughput_7d_query.where(
                ValidationQueue.validation_result.has(ValidationResult.tenant_id == tenant_id)
            )

        completed_last_hour = (await db.execute(throughput_hour_query)).scalar() or 0
        completed_last_24h = (await db.execute(throughput_24h_query)).scalar() or 0
        completed_last_7d = (await db.execute(throughput_7d_query)).scalar() or 0

        # Calculate average per hour (based on 7-day data)
        avg_per_hour = round(completed_last_7d / (7 * 24), 2) if completed_last_7d > 0 else 0.0

        # Calculate SLA metrics (time from created to claimed, claimed to completed)
        # Get average time to claim (pending -> claimed)
        sla_claim_query = select(
            func.avg(
                func.extract('epoch', ValidationQueue.claimed_at - ValidationQueue.created_at)
            )
        ).where(
            and_(
                ValidationQueue.claimed_at.isnot(None),
                ValidationQueue.created_at.isnot(None)
            )
        )

        # Get average time to complete (claimed -> completed)
        sla_complete_query = select(
            func.avg(
                func.extract('epoch', ValidationQueue.updated_at - ValidationQueue.claimed_at)
            )
        ).where(
            and_(
                ValidationQueue.status == 'completed',
                ValidationQueue.claimed_at.isnot(None),
                ValidationQueue.updated_at.isnot(None)
            )
        )

        # Get average total time (created -> completed)
        sla_total_query = select(
            func.avg(
                func.extract('epoch', ValidationQueue.updated_at - ValidationQueue.created_at)
            )
        ).where(
            and_(
                ValidationQueue.status == 'completed',
                ValidationQueue.created_at.isnot(None),
                ValidationQueue.updated_at.isnot(None)
            )
        )

        if tenant_id:
            sla_claim_query = sla_claim_query.where(
                ValidationQueue.validation_result.has(ValidationResult.tenant_id == tenant_id)
            )
            sla_complete_query = sla_complete_query.where(
                ValidationQueue.validation_result.has(ValidationResult.tenant_id == tenant_id)
            )
            sla_total_query = sla_total_query.where(
                ValidationQueue.validation_result.has(ValidationResult.tenant_id == tenant_id)
            )

        avg_time_to_claim = (await db.execute(sla_claim_query)).scalar()
        avg_time_to_complete = (await db.execute(sla_complete_query)).scalar()
        avg_total_time = (await db.execute(sla_total_query)).scalar()

        return {
            'pending_count': pending_count or 0,
            'claimed_count': claimed_count or 0,
            'completed_count': completed_count or 0,
            'total_count': (pending_count or 0) + (claimed_count or 0) + (completed_count or 0),
            'priority_distribution': priority_distribution,
            'language_distribution': language_distribution,
            'throughput': {
                'last_hour': completed_last_hour,
                'last_24_hours': completed_last_24h,
                'last_7_days': completed_last_7d,
                'avg_per_hour': avg_per_hour
            },
            'sla': {
                'avg_time_to_claim_seconds': round(avg_time_to_claim, 2) if avg_time_to_claim else None,
                'avg_time_to_complete_seconds': round(avg_time_to_complete, 2) if avg_time_to_complete else None,
                'avg_total_time_seconds': round(avg_total_time, 2) if avg_total_time else None
            }
        }

    async def get_grouped_validation_queue(
        self,
        db: AsyncSession,
        tenant_id: Optional[UUID] = None,
        status: Optional[str] = None,
        language_code: Optional[str] = None,
        validator_id: Optional[UUID] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        Get validation queue items grouped by multi-turn execution with pagination.

        Returns validation queue items grouped by their multi_turn_execution_id,
        with aggregate statistics for each execution (total steps, steps needing
        review, average confidence, etc.).

        Args:
            db: Async database session
            tenant_id: Optional tenant ID for filtering
            status: Optional status filter (pending, claimed, completed)
            language_code: Optional language code filter
            validator_id: Optional validator ID for filtering (used with claimed/completed status)
            page: Page number (1-indexed, default 1)
            page_size: Number of items per page (default 20)

        Returns:
            Dictionary containing:
                - items: List of grouped validation queue items
                - total: Total number of items (before pagination)
                - page: Current page number
                - page_size: Number of items per page
                - total_pages: Total number of pages

        Example:
            >>> result = await service.get_grouped_validation_queue(
            ...     db=db,
            ...     tenant_id=tenant_id,
            ...     status='pending',
            ...     page=1,
            ...     page_size=20
            ... )
            >>> for group in result['items']:
            ...     print(f"Execution {group['execution_id']}: {group['scenario_name']}")
        """
        # Build query to get validation queue items with related data
        query = (
            select(ValidationQueue)
            .join(ValidationResult, ValidationQueue.validation_result_id == ValidationResult.id)
            .join(MultiTurnExecution, ValidationResult.multi_turn_execution_id == MultiTurnExecution.id)
            .join(ScenarioScript, MultiTurnExecution.script_id == ScenarioScript.id)
            .join(StepExecution, ValidationResult.step_execution_id == StepExecution.id)
            .options(
                selectinload(ValidationQueue.validation_result)
                .selectinload(ValidationResult.multi_turn_execution)
                .selectinload(MultiTurnExecution.script),
                selectinload(ValidationQueue.validation_result)
                .selectinload(ValidationResult.step_execution)
            )
            .where(ValidationResult.multi_turn_execution_id.isnot(None))
        )

        # Apply filters
        if tenant_id:
            query = query.where(ScenarioScript.tenant_id == tenant_id)

        if status:
            query = query.where(ValidationQueue.status == status)

        if language_code:
            query = query.where(ValidationQueue.language_code.like(f"{language_code}%"))

        # Filter by validator for claimed/completed items
        if validator_id and status in ['claimed', 'completed']:
            query = query.where(ValidationQueue.claimed_by == validator_id)

        # Order by priority and creation time
        query = query.order_by(
            ValidationQueue.priority.asc(),
            ValidationQueue.created_at.asc()
        )

        result = await db.execute(query)
        queue_items = result.scalars().all()

        # Group by multi_turn_execution_id
        grouped_data: Dict[UUID, Dict[str, Any]] = {}

        for queue_item in queue_items:
            validation_result = queue_item.validation_result
            execution = validation_result.multi_turn_execution
            step_execution = validation_result.step_execution
            script = execution.script

            execution_id = execution.id

            if execution_id not in grouped_data:
                grouped_data[execution_id] = {
                    'execution_id': str(execution_id),
                    'scenario_name': script.name,
                    'scenario_id': str(script.id),
                    'total_steps': execution.total_steps,
                    'steps_needing_review': 0,
                    'confidence_scores': [],
                    'created_at': execution.created_at.isoformat() if execution.created_at else None,
                    'step_validations': []
                }

            # Increment steps needing review
            grouped_data[execution_id]['steps_needing_review'] += 1

            # Collect confidence scores
            if validation_result.asr_confidence_score is not None:
                grouped_data[execution_id]['confidence_scores'].append(
                    float(validation_result.asr_confidence_score)
                )

            # Add step validation details
            grouped_data[execution_id]['step_validations'].append({
                'queue_id': str(queue_item.id),
                'validation_result_id': str(validation_result.id),
                'step_execution_id': str(step_execution.id),
                'step_order': step_execution.step_order,
                'user_utterance': step_execution.user_utterance,
                'confidence_score': float(validation_result.asr_confidence_score) if validation_result.asr_confidence_score else None,
                'review_status': validation_result.review_status,
                'queue_status': queue_item.status,
                'priority': queue_item.priority,
                'language_code': queue_item.language_code,
                'created_at': queue_item.created_at.isoformat() if queue_item.created_at else None
            })

        # Calculate aggregate statistics and determine overall status
        result_list = []
        for execution_id, data in grouped_data.items():
            confidence_scores = data.pop('confidence_scores')

            if confidence_scores:
                data['avg_confidence'] = round(sum(confidence_scores) / len(confidence_scores), 4)
                data['min_confidence'] = round(min(confidence_scores), 4)
                data['max_confidence'] = round(max(confidence_scores), 4)
            else:
                data['avg_confidence'] = None
                data['min_confidence'] = None
                data['max_confidence'] = None

            # Determine overall status
            # Check if all steps are completed
            all_completed = all(sv['queue_status'] == 'completed' for sv in data['step_validations'])
            any_claimed = any(sv['queue_status'] == 'claimed' for sv in data['step_validations'])

            if all_completed:
                data['status'] = 'completed'
            elif any_claimed:
                data['status'] = 'in_progress'
            else:
                data['status'] = 'needs_review'

            # Sort step validations by step_order
            data['step_validations'].sort(key=lambda x: x['step_order'])

            result_list.append(data)

        # Sort by average confidence (lowest first) and creation time
        result_list.sort(key=lambda x: (
            x['avg_confidence'] if x['avg_confidence'] is not None else 999,
            x['created_at'] or ''
        ))

        # Apply pagination
        total = len(result_list)
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 1
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_items = result_list[start_idx:end_idx]

        return {
            'items': paginated_items,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages
        }
