"""
ValidationService for hybrid voice test response validation.

This module provides the ValidationService class which orchestrates
validation of voice AI responses using a hybrid approach:
1. Houndify deterministic checks (CommandKind, ASR, response content patterns)
2. LLM ensemble behavioral evaluation (Gemini + GPT + Claude)

Key Features:
- Houndify CommandKind and ASR confidence validation
- Response content pattern matching (contains, not_contains, regex)
- Three-stage LLM pipeline for behavioral correctness evaluation
- Hybrid mode combining deterministic and LLM validation
- Multi-turn conversation context support

Example:
    >>> from services.validation_service import ValidationService
    >>>
    >>> # Create service
    >>> service = ValidationService()
    >>>
    >>> # Validate a voice test execution (async)
    >>> result = await service.validate_voice_response(
    ...     execution_id=execution_uuid,
    ...     expected_outcome_id=outcome_uuid,
    ...     validation_mode='hybrid'
    ... )
    >>>
    >>> # Inspect results
    >>> print(result.houndify_passed)    # True
    >>> print(result.llm_passed)         # True
    >>> print(result.final_decision)     # 'pass'
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING
from uuid import UUID

try:
    from sqlalchemy import select
except ImportError:  # pragma: no cover
    from sqlalchemy import select  # type: ignore

try:
    from models.multi_turn_execution import MultiTurnExecution, StepExecution
    from models.expected_outcome import ExpectedOutcome
    from models.validation_result import ValidationResult
except ImportError:  # pragma: no cover
    MultiTurnExecution = None  # type: ignore
    StepExecution = None  # type: ignore
    ExpectedOutcome = None  # type: ignore
    ValidationResult = None  # type: ignore

try:
    from api.database import get_async_session
except ImportError:  # pragma: no cover
    async def get_async_session():  # type: ignore
        """Fallback async session factory for tests."""
        raise RuntimeError("Database session factory unavailable")

# Import mixins
from services.validation_houndify import ValidationHoundifyMixin
from services.validation_llm import ValidationLLMMixin

logger = logging.getLogger(__name__)

if TYPE_CHECKING:  # pragma: no cover
    from services.execution_metrics_recorder import ExecutionMetricsRecorder
    from services.defect_auto_creator import DefectAutoCreator


def determine_review_status(confidence_score: Optional[float]) -> str:
    """
    Determine review status based on confidence score thresholds.

    Args:
        confidence_score: Confidence score from validation (0.0 to 1.0)

    Returns:
        One of: 'auto_pass', 'needs_review', 'auto_fail'

    Thresholds:
        - >= 0.75: auto_pass (high confidence, no human review needed)
        - 0.40 to 0.74: needs_review (medium confidence, human review recommended)
        - < 0.40: auto_fail (low confidence, likely failed)
        - None: needs_review (no confidence available)

    Example:
        >>> determine_review_status(0.80)
        'auto_pass'
        >>> determine_review_status(0.50)
        'needs_review'
        >>> determine_review_status(0.20)
        'auto_fail'
    """
    if confidence_score is None:
        return "needs_review"
    if confidence_score >= 0.75:
        return "auto_pass"
    if confidence_score >= 0.40:
        return "needs_review"
    return "auto_fail"


class ValidationService(
    ValidationHoundifyMixin,
    ValidationLLMMixin
):
    """
    Service for hybrid validation of voice test responses.

    The service uses a hybrid approach:
    - Houndify deterministic: CommandKind matching, ASR confidence, response patterns
    - LLM ensemble: Three-stage behavioral evaluation pipeline

    Supports three validation modes (ScenarioScript.validation_mode):
    - houndify: Deterministic Houndify-only validation (CommandKind, ASR, patterns)
    - llm_ensemble: Full LLM ensemble pipeline (Gemini + GPT + Claude)
    - hybrid: Combines Houndify deterministic checks with LLM ensemble (default)

    Note: Legacy semantic similarity, WER, CER, SER calculations have been removed.
    These compared user utterance to expected transcript which doesn't fit
    behavioral testing. Use expected_response_content patterns instead.

    This class inherits from:
    - ValidationHoundifyMixin: Houndify-specific validation (CommandKind, ASR, patterns)
    - ValidationLLMMixin: LLM ensemble validation methods
    """

    def __init__(
        self,
        *,
        metrics_recorder: Optional["ExecutionMetricsRecorder"] = None,
        defect_auto_creator: Optional["DefectAutoCreator"] = None,
    ) -> None:
        """
        Initialize ValidationService.

        Args:
            metrics_recorder: Metrics recording service
            defect_auto_creator: Defect auto-creation service
        """
        self._metrics_recorder = metrics_recorder
        self._defect_auto_creator = defect_auto_creator
        logger.info("ValidationService initialized")

    async def validate_voice_response(
        self,
        execution_id: UUID,
        expected_outcome_id: UUID,
        validation_mode: Optional[str] = None,
        step_order: Optional[int] = None,
        scenario_name: Optional[str] = None,
        language_code: Optional[str] = None,
        tenant_id: Optional[UUID] = None,
    ) -> ValidationResult:
        """
        Validate a voice execution against the expected outcome.

        For multi-turn scenarios, provide step_order to enable conversation
        history context for LLM evaluation. The LLM will see previous turns
        to understand references like "yes", "confirm that", etc.

        Args:
            execution_id: UUID of the voice test execution
            expected_outcome_id: UUID of the expected outcome
            validation_mode: Validation mode ('houndify', 'llm_ensemble', 'hybrid')
                           If not provided, uses DEFAULT_VALIDATION_MODE env var
            step_order: Optional step order for multi-turn scenarios.
                       If provided, LLM will receive conversation history from
                       previous steps for context.
            scenario_name: Optional scenario name for LLM context
            language_code: Optional language code (e.g., 'en-US', 'es-ES', 'fr-FR').
                         If provided, will use language-specific validation patterns
                         from expected_outcome.language_variations.
            tenant_id: Optional tenant UUID for multi-tenant validation.
                      If provided, ensures execution belongs to the specified tenant.

        Returns:
            ValidationResult with all calculated scores

        Raises:
            ValueError: If execution or expected outcome not found
            RuntimeError: If database operations fail
        """
        # Determine validation mode
        if validation_mode is None:
            validation_mode = self._get_default_validation_mode()
        logger.info(
            "Validating voice response execution=%s expected_outcome=%s tenant_id=%s",
            execution_id,
            expected_outcome_id,
            tenant_id,
        )

        execution = await self._fetch_execution(execution_id, tenant_id=tenant_id)
        expected_outcome = await self._fetch_expected_outcome(expected_outcome_id)

        if execution is None:
            raise ValueError(f"MultiTurnExecution not found: {execution_id}")
        if expected_outcome is None:
            raise ValueError(f"ExpectedOutcome not found: {expected_outcome_id}")

        actual_entities = execution.get_all_response_entities()
        expected_entities = expected_outcome.entities or {}
        validation_rules = expected_outcome.validation_rules or {}

        transcript = self._resolve_transcript(actual_entities)

        # Calculate Houndify-specific scores
        execution_context = execution.get_all_context()
        houndify_data = self._extract_houndify_data(execution_context)

        command_kind_match_score = None
        asr_confidence_score = None
        ai_spoken_response = None

        if houndify_data:
            # Extract CommandKind and ASR confidence from Houndify response
            actual_command_kind = self._extract_command_kind(houndify_data)
            asr_confidence = self._extract_asr_confidence(houndify_data)
            ai_spoken_response = self._extract_spoken_response(houndify_data)

            # Get expected values from ExpectedOutcome
            expected_command_kind = expected_outcome.expected_command_kind
            min_asr_confidence = expected_outcome.expected_asr_confidence_min

            # Calculate CommandKind match score
            command_kind_match_score = self._calculate_command_kind_match_score(
                actual_command_kind=actual_command_kind,
                expected_command_kind=expected_command_kind
            )

            # Validate ASR confidence
            asr_confidence_score = self._validate_asr_confidence(
                asr_confidence=asr_confidence,
                min_confidence=min_asr_confidence
            )

        # Validate response content patterns (deterministic check)
        # This validates AI's spoken response against expected patterns

        # Check if language_variations exists and language_code is provided
        language_variations = getattr(expected_outcome, 'language_variations', None)
        if language_code and language_variations and isinstance(language_variations, dict):
            # Extract language-specific expected response patterns
            lang_variation = language_variations.get(language_code, {})
            if lang_variation and 'expected_response_patterns' in lang_variation:
                expected_response_content = lang_variation['expected_response_patterns']
                logger.info(
                    f"Using language-specific validation patterns for {language_code}: "
                    f"{expected_response_content}"
                )
            else:
                # Fall back to default expected_response_content
                expected_response_content = getattr(
                    expected_outcome, 'expected_response_content', None
                )
                logger.debug(
                    f"No language-specific patterns found for {language_code}, "
                    f"using default expected_response_content"
                )
        else:
            # No language variations or language_code, use default
            expected_response_content = getattr(
                expected_outcome, 'expected_response_content', None
            )

        forbidden_phrases = getattr(
            expected_outcome, 'forbidden_phrases', None
        )
        response_content_result = self._validate_response_content(
            ai_response=ai_spoken_response,
            expected_response_content=expected_response_content,
            forbidden_phrases=forbidden_phrases,
        )

        # Validate entities (compare expected vs actual)
        entity_validation_result = self._validate_entities(
            actual_entities=actual_entities,
            expected_entities=expected_entities,
        )

        # Run both Houndify and LLM validation in parallel for better performance
        # Both are independent and can be computed concurrently
        houndify_passed = None
        houndify_result = None
        llm_passed = None
        llm_result = None
        ensemble_result = None
        total_validation_latency_ms = 0

        # Prepare tasks for parallel execution
        tasks = []
        run_houndify = validation_mode in ('houndify', 'hybrid')
        run_llm = validation_mode in ('llm_ensemble', 'hybrid')

        if run_houndify:
            houndify_task = self._run_houndify_validation(
                command_kind_match_score=command_kind_match_score,
                asr_confidence_score=asr_confidence_score,
                response_content_result=response_content_result,
                entity_validation_result=entity_validation_result,
                expected_entities=expected_entities,
                actual_entities=actual_entities,
                expected_outcome_id=str(expected_outcome.id) if expected_outcome else None,
            )
            tasks.append(('houndify', houndify_task))

        if run_llm:
            llm_task = self._run_llm_validation_task(
                execution_id=execution_id,
                expected_outcome=expected_outcome,
                expected_entities=expected_entities,
                houndify_data=houndify_data,
                transcript=transcript,
                ai_spoken_response=ai_spoken_response,
                scenario_name=scenario_name,
                step_order=step_order,
            )
            tasks.append(('llm', llm_task))

        # Execute tasks in parallel and track wall-clock time
        # For parallel execution, total time ≈ max(Houndify, LLM), not sum
        if tasks:
            parallel_start_time = time.time()
            task_coros = [task[1] for task in tasks]
            results = await asyncio.gather(*task_coros, return_exceptions=True)
            total_validation_latency_ms = int((time.time() - parallel_start_time) * 1000)

            # Process results
            for i, (task_name, _) in enumerate(tasks):
                result = results[i]
                if isinstance(result, Exception):
                    logger.error(f"{task_name} validation failed with exception: {result}")
                    continue

                if task_name == 'houndify':
                    houndify_passed, houndify_result = result
                elif task_name == 'llm':
                    llm_passed, llm_result, ensemble_result = result

            logger.info(
                f"Parallel validation completed in {total_validation_latency_ms}ms "
                f"(houndify={houndify_result.get('latency_ms', 0) if houndify_result else 0}ms, "
                f"llm={ensemble_result.get('latency_ms', 0) if ensemble_result else 0}ms)"
            )

            # Add total validation latency to results for frontend access
            if houndify_result:
                houndify_result['total_validation_latency_ms'] = total_validation_latency_ms
            if ensemble_result:
                ensemble_result['total_validation_latency_ms'] = total_validation_latency_ms

        # Compute final combined decision
        final_decision = None
        if validation_mode == 'houndify':
            if houndify_passed is not None:
                final_decision = 'pass' if houndify_passed else 'fail'
        elif validation_mode == 'llm_ensemble':
            if llm_result is not None:
                final_decision = llm_result.final_decision
        elif validation_mode == 'hybrid':
            if llm_result is not None:
                final_decision = self._compute_combined_decision(
                    houndify_passed=houndify_passed,
                    llm_decision=llm_result.final_decision,
                    llm_score=llm_result.final_score,
                    validation_mode=validation_mode,
                )

        # Compute review status
        if llm_result is not None:
            review_status = self._compute_review_status(
                final_decision=final_decision or 'uncertain',
                llm_confidence=llm_result.confidence,
            )
        else:
            # For houndify-only mode, derive review status from pass/fail
            if houndify_passed is True:
                review_status = "auto_pass"
            elif houndify_passed is False:
                review_status = "auto_fail"
            else:
                review_status = "needs_review"

        logger.info(
            "Validation: houndify_passed=%s, llm_passed=%s, final_decision=%s, "
            "command_kind=%s, asr=%s, response_content=%s",
            houndify_passed,
            llm_passed,
            final_decision,
            command_kind_match_score,
            asr_confidence_score,
            response_content_result['passed'],
        )

        validation_result = ValidationResult(
            suite_run_id=execution.suite_run_id,
            tenant_id=execution.tenant_id,
            # Houndify deterministic validation scores
            command_kind_match_score=command_kind_match_score,
            asr_confidence_score=asr_confidence_score,
            # LLM ensemble validation fields
            houndify_passed=houndify_passed,
            houndify_result=houndify_result,
            llm_passed=llm_passed,
            ensemble_result=ensemble_result,
            final_decision=final_decision,
            review_status=review_status,
        )
        validation_result.multi_turn_execution_id = execution_id
        validation_result.expected_outcome_id = expected_outcome_id

        if self._metrics_recorder is not None:
            await self._metrics_recorder.record_execution_metrics(
                execution=execution,
                validation_result=validation_result,
                review_status=review_status,
            )

        if self._defect_auto_creator is not None:
            await self._defect_auto_creator.record_validation_outcome(
                execution=execution,
                validation_result=validation_result,
                review_status=review_status,
            )

        return validation_result

    async def _run_houndify_validation(
        self,
        command_kind_match_score: Optional[float],
        asr_confidence_score: Optional[float],
        response_content_result: Dict[str, Any],
        entity_validation_result: Dict[str, Any],
        expected_entities: Dict[str, Any],
        actual_entities: Dict[str, Any],
        expected_outcome_id: Optional[str],
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Run Houndify deterministic validation with latency tracking.

        This method runs as a coroutine to enable parallel execution with LLM validation.

        Args:
            command_kind_match_score: Score from CommandKind matching
            asr_confidence_score: Score from ASR confidence validation
            response_content_result: Result from response content validation
            entity_validation_result: Result from entity validation
            expected_entities: Expected entities from ExpectedOutcome
            actual_entities: Actual entities from execution
            expected_outcome_id: UUID string of the expected outcome

        Returns:
            Tuple of (houndify_passed, houndify_result dict with latency_ms)
        """
        start_time = time.time()

        # Houndify passes if all deterministic checks pass:
        # 1. CommandKind matches (if expected)
        # 2. ASR confidence is good (if threshold set)
        # 3. Response content patterns pass (if defined)
        # 4. Entity validation passes (if expected entities defined)
        command_matches = (
            command_kind_match_score is None or command_kind_match_score >= 1.0
        )
        asr_ok = (
            asr_confidence_score is None or asr_confidence_score >= 0.5
        )
        response_content_ok = response_content_result['passed']
        entities_ok = entity_validation_result['passed']

        houndify_passed = (
            command_matches and asr_ok and response_content_ok and entities_ok
        )

        # Build complete houndify_result matching frontend interface
        # validation_score: composite score of all deterministic checks
        validation_score = 1.0
        if command_kind_match_score is not None:
            validation_score = min(validation_score, command_kind_match_score)
        if asr_confidence_score is not None:
            validation_score = min(validation_score, asr_confidence_score)
        # Factor in entity validation score
        if entity_validation_result['score'] < 1.0:
            validation_score = min(validation_score, entity_validation_result['score'])

        # Collect all errors
        errors = []
        if not command_matches:
            errors.append('CommandKind mismatch')
        if not asr_ok:
            errors.append('ASR confidence below threshold')
        errors.extend(response_content_result.get('errors', []))
        errors.extend(entity_validation_result.get('errors', []))

        # Calculate latency
        latency_ms = int((time.time() - start_time) * 1000)

        houndify_result = {
            'passed': houndify_passed,
            'errors': errors,
            'method': 'expected_outcome',
            'command_kind_match': command_matches,
            'asr_confidence': asr_confidence_score,
            'validation_score': validation_score,
            'response_content_validation': response_content_result,
            'entity_validation': entity_validation_result,
            'expected_entities': expected_entities,
            'actual_entities': actual_entities,
            'expected_outcome_id': expected_outcome_id,
            'latency_ms': latency_ms,
        }

        logger.info(
            f"Houndify validation: passed={houndify_passed}, "
            f"command_match={command_kind_match_score}, asr={asr_confidence_score}, "
            f"response_content={response_content_result['passed']}, "
            f"entities={entity_validation_result['passed']}, "
            f"latency={latency_ms}ms"
        )

        return houndify_passed, houndify_result

    async def _run_llm_validation_task(
        self,
        execution_id: UUID,
        expected_outcome: ExpectedOutcome,
        expected_entities: Dict[str, Any],
        houndify_data: Optional[Dict[str, Any]],
        transcript: str,
        ai_spoken_response: Optional[str],
        scenario_name: Optional[str],
        step_order: Optional[int],
    ) -> Tuple[bool, Any, Dict[str, Any]]:
        """
        Run LLM ensemble validation as a task for parallel execution.

        This method wraps the LLM pipeline validation to enable concurrent
        execution with Houndify validation using asyncio.gather.

        Args:
            execution_id: UUID of the execution
            expected_outcome: ExpectedOutcome model
            expected_entities: Expected entities dict
            houndify_data: Extracted Houndify response data
            transcript: User's transcript/utterance
            ai_spoken_response: AI's spoken response
            scenario_name: Optional scenario name for context
            step_order: Optional step order for multi-turn context

        Returns:
            Tuple of (llm_passed, llm_result object, ensemble_result dict)
        """
        # Build conversation history for multi-turn scenarios
        # This helps LLM understand context from previous turns
        conversation_history = None
        if step_order is not None and step_order > 1:
            # Fetch previous step executions for context
            step_executions = await self._fetch_step_executions(
                multi_turn_execution_id=execution_id
            )
            if step_executions:
                conversation_history = self._build_conversation_history(
                    step_executions=step_executions,
                    current_step_order=step_order,
                )
                logger.debug(
                    "Built conversation history with %d previous turns "
                    "for step %d",
                    len(conversation_history),
                    step_order
                )

        # Build context for LLM evaluators
        llm_context = self._build_llm_context(
            expected_command_kind=expected_outcome.expected_command_kind,
            expected_entities=expected_entities,
            houndify_data=houndify_data,
            transcript=transcript,
            scenario_name=scenario_name,
            step_order=step_order,
            conversation_history=conversation_history,
        )

        # Run the three-stage LLM pipeline
        # LLMs evaluate behavioral correctness, not exact text matching
        # Note: latency is tracked inside _run_llm_pipeline_validation
        llm_result = await self._run_llm_pipeline_validation(
            user_utterance=transcript,  # What user said (ASR transcription)
            ai_response=ai_spoken_response or transcript,  # What AI said back
            context=llm_context,
        )

        llm_passed = llm_result.final_decision == 'pass'
        ensemble_result = llm_result.to_dict()

        return llm_passed, llm_result, ensemble_result

    async def _fetch_execution(
        self,
        execution_id: UUID,
        tenant_id: Optional[UUID] = None,
    ) -> Optional[MultiTurnExecution]:
        """
        Fetch multi-turn execution from database with optional tenant validation.

        Args:
            execution_id: UUID of the execution
            tenant_id: Optional tenant UUID for validation. If provided,
                      ensures the fetched execution belongs to this tenant.

        Returns:
            MultiTurnExecution or None if not found

        Raises:
            ValueError: If tenant_id provided and execution belongs to different tenant
            RuntimeError: If database operation fails
        """
        logger.debug("Fetching execution %s", execution_id)
        try:
            async with get_async_session() as session:
                stmt = select(MultiTurnExecution).where(
                    MultiTurnExecution.id == execution_id
                )
                result = await session.execute(stmt)
                execution = result.scalar_one_or_none()

            # CRITICAL: Validate tenant isolation if tenant_id provided
            if execution and tenant_id is not None:
                execution_tenant_id = getattr(execution, "tenant_id", None)
                if execution_tenant_id != tenant_id:
                    logger.error(
                        "Tenant validation failed for execution %s: "
                        "expected tenant_id=%s but got tenant_id=%s",
                        execution_id,
                        tenant_id,
                        execution_tenant_id,
                    )
                    raise ValueError(
                        f"Execution {execution_id} does not belong to tenant {tenant_id}"
                    )

            if execution and getattr(execution, "response_entities", None) is None:
                try:
                    execution.response_entities = {}
                except Exception:  # pragma: no cover - defensive
                    logger.debug(
                        "Unable to set default response_entities on %s",
                        execution_id
                    )
            return execution
        except Exception as e:
            logger.error(
                "Database error fetching execution %s: %s",
                execution_id,
                str(e),
                exc_info=True
            )
            raise RuntimeError(
                f"Database error fetching execution {execution_id}: {str(e)}"
            ) from e

    async def _fetch_expected_outcome(
        self,
        expected_outcome_id: UUID,
    ) -> Optional[ExpectedOutcome]:
        """
        Fetch expected outcome from database.

        Args:
            expected_outcome_id: UUID of the expected outcome

        Returns:
            ExpectedOutcome or None if not found

        Raises:
            ValueError: If outcome missing required fields
            RuntimeError: If database operation fails
        """
        logger.debug("Fetching expected outcome %s", expected_outcome_id)
        try:
            async with get_async_session() as session:
                stmt = select(ExpectedOutcome).where(
                    ExpectedOutcome.id == expected_outcome_id
                )
                result = await session.execute(stmt)
                outcome = result.scalar_one_or_none()

            if outcome is None:
                return None

            if not getattr(outcome, "validation_rules", None):
                raise ValueError(
                    f"ExpectedOutcome {expected_outcome_id} missing validation_rules"
                )
            if not getattr(outcome, "entities", None):
                raise ValueError(
                    f"ExpectedOutcome {expected_outcome_id} missing entities"
                )

            return outcome
        except ValueError:
            # Re-raise validation errors as-is
            raise
        except Exception as e:
            logger.error(
                "Database error fetching expected outcome %s: %s",
                expected_outcome_id,
                str(e),
                exc_info=True
            )
            raise RuntimeError(
                f"Database error fetching expected outcome "
                f"{expected_outcome_id}: {str(e)}"
            ) from e

    async def _fetch_step_executions(
        self,
        multi_turn_execution_id: UUID,
    ) -> List[StepExecution]:
        """
        Fetch all step executions for a multi-turn execution.

        Args:
            multi_turn_execution_id: UUID of the multi-turn execution

        Returns:
            List of StepExecution ordered by step_order
        """
        logger.debug(
            "Fetching step executions for multi_turn_execution %s",
            multi_turn_execution_id
        )
        try:
            async with get_async_session() as session:
                stmt = (
                    select(StepExecution)
                    .where(
                        StepExecution.multi_turn_execution_id == multi_turn_execution_id
                    )
                    .order_by(StepExecution.step_order)
                )
                result = await session.execute(stmt)
                return list(result.scalars().all())
        except Exception as e:
            logger.error(
                "Database error fetching step executions for %s: %s",
                multi_turn_execution_id,
                str(e),
                exc_info=True
            )
            return []

    def _build_conversation_history(
        self,
        step_executions: List[StepExecution],
        current_step_order: Optional[int] = None,
    ) -> List[Dict[str, str]]:
        """
        Build conversation history from previous step executions.

        For multi-turn LLM evaluation, the LLM needs context from previous
        turns to understand references like "yes", "confirm that", etc.

        Args:
            step_executions: List of step executions ordered by step_order
            current_step_order: If provided, only include steps BEFORE this order.
                              If None, include all steps (for full execution validation).

        Returns:
            List of conversation turns: [{"user": "...", "ai": "..."}, ...]

        Example:
            >>> history = self._build_conversation_history(
            ...     step_executions=steps,
            ...     current_step_order=3  # Validating step 3
            ... )
            >>> # Returns steps 1 and 2 as history
        """
        history = []

        for step in step_executions:
            # Skip steps at or after the current step being validated
            if current_step_order is not None:
                if step.step_order >= current_step_order:
                    continue

            # Build turn from step execution
            # user = what the user said (or transcription if available)
            # ai = what the AI responded
            user_text = step.transcription or step.user_utterance or ""
            ai_text = step.ai_response or ""

            if user_text or ai_text:
                history.append({
                    "user": user_text,
                    "ai": ai_text,
                })

        return history

    def _resolve_transcript(self, actual_entities: Dict[str, Any]) -> str:
        """
        Resolve transcript from actual entities.

        Args:
            actual_entities: Dictionary of actual response entities

        Returns:
            Resolved transcript string
        """
        candidates = (
            actual_entities.get("transcript"),
            actual_entities.get("formatted_transcription"),
            actual_entities.get("raw_transcription"),
        )
        for value in candidates:
            if isinstance(value, str) and value.strip():
                return value.strip()
        return ""

