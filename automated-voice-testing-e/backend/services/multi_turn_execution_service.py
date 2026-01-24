"""
Multi-Turn Execution Service

This service orchestrates multi-turn conversation scenario execution with:
- Conversation state tracking across multiple steps
- Step-by-step execution with validation
- Houndify API integration with ConversationState management
- Real-time progress updates via Socket.IO

Example:
    >>> from services.multi_turn_execution_service import MultiTurnExecutionService
    >>>
    >>> service = MultiTurnExecutionService()
    >>> result = await service.execute_scenario(
    ...     db=db,
    ...     script_id=script.id,
    ...     suite_run_id=suite_run.id,
    ...     tenant_id=user.id
    ... )
"""

import logging
import asyncio
import os
import random
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models.scenario_script import ScenarioScript, ScenarioStep
from models.expected_outcome import ExpectedOutcome
from models.multi_turn_execution import MultiTurnExecution, StepExecution
from models.suite_run import SuiteRun
from models.validation_result import ValidationResult
from services.tts_service import TTSService
from services.storage_service import StorageService
from services.validation_queue_service import ValidationQueueService
from services.validation_service import determine_review_status
from services.llm_pipeline_service import LLMPipelineService
from services.validation_houndify import ValidationHoundifyMixin
from services.defect_auto_creator import DefectAutoCreator, get_defect_threshold
from integrations.houndify import create_houndify_client
from api.config import get_settings
from api.events import emit_to_room
from services.audio_utils import convert_to_pcm
from services.noise_profile_library_service import NoiseProfileLibraryService

logger = logging.getLogger(__name__)


class MultiTurnExecutionService(ValidationHoundifyMixin):
    """
    Service for executing multi-turn conversation scenarios.

    This service manages the complete lifecycle of multi-turn scenario execution:
    1. Load scenario script with all steps
    2. Initialize conversation tracking
    3. Execute each step in sequence
    4. Track conversation state between steps
    5. Validate each step's response
    6. Emit real-time progress updates
    7. Store execution results
    """
    
    def __init__(self):
        """Initialize the multi-turn execution service."""
        self.settings = get_settings()
        self.tts_service = TTSService()

        # Initialize StorageService with proper MinIO/S3 credentials
        self.storage_service = StorageService(
            aws_access_key_id=self.settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=self.settings.MINIO_SECRET_KEY,
            endpoint_url=self.settings.MINIO_ENDPOINT_URL if self.settings.STORAGE_BACKEND == "minio" else None,
            region_name=self.settings.MINIO_REGION,
            default_bucket=self.settings.MINIO_AUDIO_BUCKET
        )

        # Initialize Houndify client using centralized factory
        self.houndify_client = create_houndify_client(
            client_id=self.settings.SOUNDHOUND_CLIENT_ID,
            client_key=self.settings.SOUNDHOUND_API_KEY,
        )

        # Initialize noise profile library
        self.noise_profile_library = NoiseProfileLibraryService()

    def _apply_noise_to_pcm(
        self,
        pcm_bytes: bytes,
        noise_config: Dict[str, Any],
        sample_rate: int = 16000
    ) -> bytes:
        """
        Apply noise injection to PCM audio bytes.

        Converts PCM bytes to numpy array, applies noise profile from
        NoiseProfileLibraryService, and converts back to PCM bytes.

        Args:
            pcm_bytes: Raw PCM audio (16-bit signed, mono, little-endian)
            noise_config: Noise configuration dictionary with:
                - enabled: bool - Whether noise is enabled
                - profile: str - Noise profile name from library
                - snr_db: float (optional) - SNR override
                - randomize_snr: bool - Whether to randomize SNR
                - snr_variance: float - Variance for randomization
            sample_rate: Audio sample rate (default 16000)

        Returns:
            PCM bytes with noise applied
        """
        import numpy as np

        if not noise_config.get('enabled', False):
            return pcm_bytes

        profile_name = noise_config.get('profile', 'car_cabin_city')
        snr_db = noise_config.get('snr_db')
        randomize_snr = noise_config.get('randomize_snr', False)
        snr_variance = noise_config.get('snr_variance', 3.0)

        # If no SNR specified, use profile's typical SNR
        if snr_db is None:
            profile = self.noise_profile_library.get_profile(profile_name)
            snr_db = profile.get('typical_snr', 15)

        # Apply SNR randomization if enabled
        if randomize_snr:
            snr_db = snr_db + random.uniform(-snr_variance, snr_variance)

        logger.info(f"    🔊 Applying noise: profile={profile_name}, SNR={snr_db:.1f}dB")

        # Convert PCM bytes to numpy array (16-bit signed integers)
        signal = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32)

        # Normalize to [-1, 1] range for noise processing
        signal = signal / 32768.0

        # Apply noise using the profile library
        noisy_signal = self.noise_profile_library.apply_noise(
            signal=signal,
            profile_name=profile_name,
            snr_db=snr_db,
            sample_rate=sample_rate
        )

        # Clip to prevent overflow and convert back to 16-bit PCM
        noisy_signal = np.clip(noisy_signal, -1.0, 1.0)
        noisy_pcm = (noisy_signal * 32767.0).astype(np.int16)

        logger.info(f"    ✓ Noise applied: {len(pcm_bytes)} → {len(noisy_pcm.tobytes())} bytes")

        return noisy_pcm.tobytes()

    def _get_room_name(self, execution: MultiTurnExecution) -> str:
        """Get WebSocket room name for this execution."""
        if execution.suite_run_id:
            return f"suite_run_{execution.suite_run_id}"
        return f"execution_{execution.id}"

    async def execute_scenario(
        self,
        db: AsyncSession,
        script_id: UUID,
        suite_run_id: Optional[UUID],
        tenant_id: UUID,
        socketio=None,
        language_codes: Optional[List[str]] = None,
        suite_id: Optional[UUID] = None
    ) -> MultiTurnExecution:
        """
        Execute a complete multi-turn scenario.

        Args:
            db: Database session
            script_id: ID of the scenario script to execute
            suite_run_id: ID of the suite run
            tenant_id: ID of the tenant (organization or user) executing the scenario
            socketio: Optional Socket.IO instance for real-time updates
            language_codes: Optional list of language codes to execute (e.g., ["en-US", "fr-FR"])
                          If None, executes all language variants
                          If ["en-US"], executes only English variants
                          If ["en-US", "fr-FR"], executes both
            suite_id: Optional test suite ID if executing as part of a suite

        Returns:
            MultiTurnExecution: The execution record

        Example:
            >>> # Execute only English variants
            >>> execution = await service.execute_scenario(
            ...     db=db,
            ...     script_id=script.id,
            ...     suite_run_id=suite_run.id,
            ...     tenant_id=user.id,
            ...     language_codes=["en-US"]
            ... )
            >>> # Execute all language variants
            >>> execution = await service.execute_scenario(
            ...     db=db,
            ...     script_id=script.id,
            ...     suite_run_id=suite_run.id,
            ...     tenant_id=user.id,
            ...     language_codes=None  # or omit parameter
            ... )
        """
        logger.info(f"===== STARTING MULTI-TURN SCENARIO EXECUTION =====")
        logger.info(f"Script ID: {script_id}")
        logger.info(f"Suite Run ID: {suite_run_id}")
        if suite_id:
            logger.info(f"Suite ID: {suite_id}")
        
        # 1. Load scenario script with steps
        script = await self._load_script(db, script_id)
        if not script:
            raise ValueError(f"Scenario script {script_id} not found")
        
        if not script.steps:
            raise ValueError(f"Scenario script {script_id} has no steps")
        
        logger.info(f"✓ Loaded scenario: {script.name} ({len(script.steps)} steps)")

        # 2. Create multi-turn execution record
        execution = await self._create_execution(db, script, suite_run_id, tenant_id, suite_id)
        logger.info(f"✓ Created execution record: {execution.id}")

        # Emit execution started event
        await self._emit_execution_started(execution, script)

        # 3. Execute each step in sequence
        try:
            await self._execute_steps(db, execution, script, socketio, language_codes)

            # Mark execution as completed
            execution.status = 'completed'
            execution.completed_at = datetime.utcnow()

            # Update suite run status (if part of a suite)
            if suite_run_id:
                await self._update_suite_run_status(db, suite_run_id, 'completed')

            await db.commit()

            logger.info(f"===== MULTI-TURN SCENARIO COMPLETED SUCCESSFULLY =====")

            # Reload execution with step_executions eagerly loaded
            stmt = (
                select(MultiTurnExecution)
                .where(MultiTurnExecution.id == execution.id)
                .options(selectinload(MultiTurnExecution.step_executions))
            )
            result = await db.execute(stmt)
            execution = result.scalar_one()

            # Emit execution completed event
            await self._emit_execution_completed(execution)

            return execution

        except Exception as e:
            logger.error(f"❌ Multi-turn execution failed: {str(e)}", exc_info=True)
            execution.status = 'failed'

            # Update suite run status to failed (if part of a suite)
            if suite_run_id:
                await self._update_suite_run_status(db, suite_run_id, 'failed')
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            await db.commit()

            # Emit execution failed event
            await self._emit_execution_failed(execution, str(e))

            raise

    async def _load_script(self, db: AsyncSession, script_id: UUID) -> Optional[ScenarioScript]:
        """Load scenario script with all steps."""
        stmt = (
            select(ScenarioScript)
            .where(ScenarioScript.id == script_id)
            .options(selectinload(ScenarioScript.steps))
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def _create_execution(
        self,
        db: AsyncSession,
        script: ScenarioScript,
        suite_run_id: UUID,
        tenant_id: UUID,
        suite_id: Optional[UUID] = None
    ) -> MultiTurnExecution:
        """Create multi-turn execution record."""
        execution = MultiTurnExecution(
            tenant_id=tenant_id,
            suite_run_id=suite_run_id,
            script_id=script.id,
            suite_id=suite_id,
            user_id=f"test_user_{suite_run_id}",  # Unique user_id per suite run
            total_steps=len(script.steps),
            status='in_progress',
            started_at=datetime.utcnow()
        )
        db.add(execution)
        await db.commit()
        await db.refresh(execution)
        return execution

    def _filter_steps_by_language(
        self,
        steps: List[ScenarioStep],
        language_codes: Optional[List[str]] = None
    ) -> List[ScenarioStep]:
        """
        Return all steps sorted by step_order.

        IMPORTANT: Language filtering happens at the variant level inside
        _get_language_variants, NOT at the step level. Each step_order should
        have exactly ONE ScenarioStep record, with language variants stored
        in step_metadata['language_variants'].

        Args:
            steps: List of all scenario steps
            language_codes: Passed through but not used here (filtering happens later)

        Returns:
            All steps sorted by step_order
        """
        if not steps:
            return []

        # Simply return all steps sorted by step_order
        # Language filtering happens in _get_language_variants
        return sorted(steps, key=lambda s: s.step_order)

    async def _execute_steps(
        self,
        db: AsyncSession,
        execution: MultiTurnExecution,
        script: ScenarioScript,
        socketio=None,
        language_codes: Optional[List[str]] = None
    ) -> None:
        """
        Execute all steps in the scenario sequentially.

        This method maintains conversation state across steps by:
        1. Extracting ConversationState from each response
        2. Passing it to the next request
        3. Using the same user_id for all steps
        4. Filtering steps by language preference if specified

        Args:
            db: Database session
            execution: Multi-turn execution record
            script: Scenario script with steps
            socketio: Optional Socket.IO instance for real-time updates
            language_codes: Optional list of language codes to filter steps
                          None = execute all language variants
                          ["en-US"] = execute only English variants
                          ["en-US", "fr-FR"] = execute both English and French variants
        """
        conversation_state = None  # No state for first turn

        # Get all steps sorted by step_order
        sorted_steps = self._filter_steps_by_language(script.steps, language_codes)

        logger.info(f"Executing {len(sorted_steps)} steps")
        if language_codes:
            logger.info(f"Language filter (applied to variants): {language_codes}")

        for step in sorted_steps:
            logger.info(f"\n===== STEP {step.step_order}/{execution.total_steps}: {step.user_utterance} =====")

            # Update current step
            execution.current_step_order = step.step_order
            await db.commit()

            # Emit step started event
            await self._emit_step_started(execution, step)

            # Emit progress update (legacy)
            if socketio:
                await self._emit_progress(socketio, execution, step)

            # Execute the step
            step_result = await self._execute_step(
                db=db,
                execution=execution,
                step=step,
                conversation_state=conversation_state,
                script=script,
                language_codes=language_codes
            )

            # Get the step execution record
            step_execution = step_result.get('step_execution')

            # Emit step completed event
            if step_execution:
                await self._emit_step_completed(execution, step_execution)

            # Update conversation state for next step
            conversation_state = step_result.get('conversation_state_after')

            # Update execution's conversation state
            execution.conversation_state = conversation_state
            if conversation_state and 'ConversationStateId' in conversation_state:
                execution.conversation_state_id = conversation_state['ConversationStateId']
            await db.commit()

            # If step failed validation, stop execution
            if not step_result.get('validation_passed', False):
                logger.warning(f"⚠️ Step {step.step_order} validation failed - stopping execution")
                break

            logger.info(f"✓ Step {step.step_order} completed successfully")

    async def _execute_step(
        self,
        db: AsyncSession,
        execution: MultiTurnExecution,
        step: ScenarioStep,
        conversation_state: Optional[Dict[str, Any]],
        script: ScenarioScript,
        language_codes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Execute a single step in the scenario.

        Args:
            db: Database session
            execution: Multi-turn execution record
            step: Scenario step to execute
            conversation_state: Conversation state from previous step (or None for first step)
            script: Scenario script (for accessing metadata like language_code)
            language_codes: Optional list of language codes to filter variants

        Returns:
            Dictionary with step execution results
        """
        start_time = datetime.utcnow()
        request_id = f"req_{execution.id}_{step.step_order}"

        try:
            # 1. Generate TTS audio for language variants (filtered by language_codes)
            logger.info(f"STEP {step.step_order}.1: Generating TTS audio for language variants")

            # Get language variants from step metadata (filtered by language_codes)
            language_variants = self._get_language_variants(script, step, language_codes)
            logger.info(f"  - Found {len(language_variants)} language variant(s): {list(language_variants.keys())}")

            # Generate and upload audio for each language
            audio_urls = {}
            audio_data_by_lang = {}

            for lang_code, utterance in language_variants.items():
                # Convert language code to TTS format (e.g., "en-US" -> "en")
                tts_lang = lang_code.split('-')[0] if lang_code else "en"

                logger.info(f"  - Generating audio for {lang_code}: '{utterance}'")
                audio_data = self.tts_service.text_to_speech(
                    text=utterance,
                    lang=tts_lang
                )
                logger.info(f"    ✓ Generated {len(audio_data)} bytes")

                # Upload to storage
                audio_url = await self._upload_audio_to_storage(
                    audio_data,
                    execution.id,
                    step.step_order,
                    lang_code
                )

                if audio_url:
                    audio_urls[lang_code] = audio_url
                    audio_data_by_lang[lang_code] = audio_data
                    logger.info(f"    ✓ Uploaded to: {audio_url}")

            logger.info(f"✓ Generated and uploaded audio for {len(audio_urls)} language(s)")

            # 1b. Validate ALL language variants
            if not audio_data_by_lang:
                error_msg = "Failed to generate audio for any language variant. Check storage service configuration."
                logger.error(f"❌ {error_msg}")
                raise RuntimeError(error_msg)

            # ═══════════════════════════════════════════════════════════════════
            # 🌍 MULTI-LANGUAGE VALIDATION: Process each language variant
            # ═══════════════════════════════════════════════════════════════════
            logger.info(f"STEP {step.step_order}.2: Validating {len(audio_data_by_lang)} language variant(s)")

            # Track validation results per language
            language_validation_results = {}
            primary_lang = self._get_language_code(script, step)
            new_conversation_state = None
            primary_ai_response = None
            primary_transcription = None
            primary_command_kind = None
            primary_confidence = None
            primary_response_audio_base64 = None  # TTS response audio from Houndify
            any_validation_passed = False

            for lang_code, audio_data in audio_data_by_lang.items():
                logger.info(f"\n  ─── Language: {lang_code} {'(PRIMARY)' if lang_code == primary_lang else ''} ───")

                # Convert audio to raw PCM format for Houndify
                try:
                    pcm_audio = convert_to_pcm(audio_data, target_rate=16000, raw=True)
                    logger.info(f"    ✓ Converted to raw PCM: {len(pcm_audio)} bytes")
                except Exception as e:
                    logger.warning(f"    ⚠ PCM conversion failed, using original: {e}")
                    pcm_audio = audio_data

                # Apply noise injection if configured at scenario level
                noise_config = (script.script_metadata or {}).get('noise_config', {})
                if noise_config.get('enabled', False):
                    try:
                        pcm_audio = self._apply_noise_to_pcm(
                            pcm_bytes=pcm_audio,
                            noise_config=noise_config,
                            sample_rate=16000
                        )
                    except Exception as e:
                        logger.warning(f"    ⚠ Noise injection failed, using original: {e}")

                # Get utterance for this language
                utterance = language_variants.get(lang_code, step.user_utterance)

                # Build request_info for this language
                # LanguageCode is passed to enable language-specific responses
                lang_request_info = {
                    "Prompt": utterance,
                    "LanguageCode": lang_code,  # Pass language to Houndify client
                    "Latitude": 37.7749,
                    "Longitude": -122.4194,
                    "TimeZone": "America/Los_Angeles",
                    "ConversationState": conversation_state
                }

                lang_request_id = f"{request_id}_{lang_code}"

                # Send to Houndify
                try:
                    response = await self.houndify_client.voice_query(
                        audio_data=pcm_audio,
                        user_id=execution.user_id,
                        request_id=lang_request_id,
                        request_info=lang_request_info
                    )

                    # Extract response data
                    ai_response = None
                    transcription = None
                    command_kind = None
                    confidence_score = None
                    lang_conversation_state = None
                    response_audio_base64 = None

                    native_data = None
                    if response.get("AllResults") and len(response["AllResults"]) > 0:
                        result = response["AllResults"][0]
                        ai_response = result.get("SpokenResponse")
                        transcription = result.get("FormattedTranscription")
                        command_kind = result.get("CommandKind")
                        confidence_score = result.get("ASRConfidence")
                        lang_conversation_state = result.get("ConversationState")
                        # Extract TTS response audio (base64-encoded)
                        response_audio_base64 = result.get("ResponseAudioBytes")
                        # Extract NativeData for entity validation
                        native_data = result.get("NativeData")

                    logger.info(f"    - Transcription: {transcription}")
                    logger.info(f"    - Command Kind: {command_kind}")
                    logger.info(f"    - Confidence: {confidence_score}")
                    if response_audio_base64:
                        logger.info(f"    - Response Audio: {len(response_audio_base64)} chars (base64)")

                    # Store primary language results for step execution record
                    if lang_code == primary_lang:
                        new_conversation_state = lang_conversation_state
                        primary_ai_response = ai_response
                        primary_transcription = transcription
                        primary_command_kind = command_kind
                        primary_confidence = confidence_score
                        # Store response audio for primary language
                        primary_response_audio_base64 = response_audio_base64

                    # Validate response
                    validation_result = await self._validate_step(
                        db=db,
                        step=step,
                        ai_response=ai_response,
                        transcription=transcription,
                        command_kind=command_kind,
                        confidence_score=confidence_score,
                        language_code=lang_code,  # Pass language code for language-specific validation
                        actual_entities=native_data  # Pass NativeData for entity validation
                    )

                    if validation_result['passed']:
                        any_validation_passed = True

                    logger.info(f"    - Validation: {'✓ PASSED' if validation_result['passed'] else '✗ FAILED'}")

                    # Store results for this language
                    language_validation_results[lang_code] = {
                        'ai_response': ai_response,
                        'transcription': transcription,
                        'command_kind': command_kind,
                        'confidence_score': confidence_score,
                        'validation_result': validation_result,
                        'request_id': lang_request_id,
                        'response_audio_base64': response_audio_base64  # Store response audio for each language
                    }

                except Exception as e:
                    logger.error(f"    ✗ Houndify call failed for {lang_code}: {e}")
                    language_validation_results[lang_code] = {
                        'error': str(e),
                        'validation_result': {'passed': False, 'errors': [str(e)]}
                    }

            end_time = datetime.utcnow()
            response_time_ms = int((end_time - start_time).total_seconds() * 1000)

            logger.info(f"\n✓ All {len(language_validation_results)} language(s) processed ({response_time_ms}ms)")

            # Upload response audio (TTS from Houndify) for ALL language variants
            response_audio_urls = {}
            logger.info("Uploading Houndify response audio (TTS) for all languages...")
            for lang_code, lang_result in language_validation_results.items():
                if 'error' in lang_result:
                    continue

                response_audio_base64 = lang_result.get('response_audio_base64')
                if response_audio_base64:
                    logger.info(f"  - Uploading {lang_code} response audio...")
                    response_audio_url = await self._upload_response_audio_to_storage(
                        response_audio_base64=response_audio_base64,
                        execution_id=execution.id,
                        step_order=step.step_order,
                        language_code=lang_code
                    )
                    response_audio_urls[lang_code] = response_audio_url
                    logger.info(f"    ✓ {lang_code}: {response_audio_url}")
                else:
                    logger.warning(f"    - No response audio for {lang_code}")

            logger.info(f"✓ Uploaded response audio for {len(response_audio_urls)} language(s)")

            # Create step execution record (using primary language data)
            step_execution = StepExecution(
                multi_turn_execution_id=execution.id,
                step_id=step.id,
                step_order=step.step_order,
                user_utterance=step.user_utterance,
                audio_data_urls=audio_urls,
                response_audio_urls=response_audio_urls,  # TTS response audio from Houndify for all languages
                request_id=request_id,
                ai_response=primary_ai_response,
                transcription=primary_transcription,
                command_kind=primary_command_kind,
                confidence_score=primary_confidence,
                conversation_state_before=conversation_state,
                conversation_state_after=new_conversation_state,
                validation_passed=any_validation_passed,
                validation_details={
                    'languages_validated': list(language_validation_results.keys()),
                    'primary_language': primary_lang,
                    'per_language_results': {
                        lang: {
                            'user_utterance': language_variants.get(lang, step.user_utterance),
                            'ai_response': r.get('ai_response'),
                            'transcription': r.get('transcription'),
                            'command_kind': r.get('command_kind'),
                            'confidence_score': r.get('confidence_score'),
                            'passed': r.get('validation_result', {}).get('passed', False),
                            'errors': r.get('validation_result', {}).get('errors', [])
                        }
                        for lang, r in language_validation_results.items()
                        if 'error' not in r  # Only include successful executions
                    }
                },
                response_time_ms=response_time_ms,
                executed_at=start_time
            )
            db.add(step_execution)
            await db.commit()
            await db.refresh(step_execution)

            logger.info(f"✓ Step execution record created: {step_execution.id}")

            # ═══════════════════════════════════════════════════════════════════
            # 🌍 Create ValidationResult for EACH language variant
            # ═══════════════════════════════════════════════════════════════════
            logger.info(f"\nSTEP {step.step_order}.3: Creating ValidationResults for each language")

            for lang_code, lang_result in language_validation_results.items():
                if 'error' in lang_result:
                    logger.warning(f"  - Skipping {lang_code} due to error: {lang_result['error']}")
                    continue

                # Track total validation latency (Houndify + LLM combined)
                validation_start_time = time.time()

                validation_result = lang_result['validation_result']
                expected_outcome = validation_result.pop('expected_outcome', None)
                confidence_score = lang_result.get('confidence_score')

                # Calculate validation score for this language (composite of deterministic checks)
                validation_score = self._calculate_validation_score(
                    validation_result=validation_result,
                    asr_confidence=confidence_score,
                    expected_outcome=expected_outcome
                )

                # Calculate command_kind_match_score
                command_kind_match_score = 0.0
                if expected_outcome and expected_outcome.expected_command_kind:
                    errors = validation_result.get('errors', [])
                    has_command_kind_error = any('CommandKind mismatch' in err for err in errors)
                    command_kind_match_score = 0.0 if has_command_kind_error else 1.0
                else:
                    command_kind_match_score = 1.0

                # Get actual command kind from language result
                actual_command_kind = lang_result.get('command_kind')

                # Build comprehensive Houndify result dict for storage
                # Includes all expected vs actual values for transparent validation display
                response_content_result = validation_result.get('response_content_result')
                entity_validation_result = validation_result.get('entity_validation')
                houndify_result_dict = {
                    'passed': validation_result.get('passed', False),
                    'errors': validation_result.get('errors', []),
                    'method': validation_result.get('method', 'expected_outcome'),
                    # Command Kind validation
                    'command_kind_match': command_kind_match_score == 1.0,
                    'expected_command_kind': expected_outcome.expected_command_kind if expected_outcome else None,
                    'actual_command_kind': actual_command_kind,
                    # ASR Confidence validation
                    'asr_confidence': confidence_score,
                    'expected_asr_confidence_min': expected_outcome.expected_asr_confidence_min if expected_outcome else None,
                    # Composite validation score (deterministic checks only)
                    'validation_score': validation_score,
                    'expected_outcome_id': str(expected_outcome.id) if expected_outcome else None,
                    # Response content validation (frontend checks both field names)
                    'response_content_validation': response_content_result,
                    'response_content_result': response_content_result,
                    # Entity validation
                    'entity_validation': entity_validation_result,
                    'expected_entities': validation_result.get('expected_entities'),
                    'actual_entities': validation_result.get('actual_entities'),
                    # Houndify validation latency in milliseconds
                    'latency_ms': validation_result.get('latency_ms', 0),
                }

                # Create ValidationResult for this language
                validation_result_obj = ValidationResult(
                    suite_run_id=execution.suite_run_id,
                    tenant_id=execution.tenant_id,
                    multi_turn_execution_id=execution.id,
                    step_execution_id=step_execution.id,
                    expected_outcome_id=expected_outcome.id if expected_outcome else None,
                    language_code=lang_code,  # 🌍 Language being validated
                    asr_confidence_score=confidence_score,
                    command_kind_match_score=command_kind_match_score,
                    # Store Houndify-specific results
                    houndify_passed=validation_result.get('passed', False),
                    houndify_result=houndify_result_dict,
                )

                db.add(validation_result_obj)
                await db.commit()
                await db.refresh(validation_result_obj)

                logger.info(f"  - {lang_code}: ValidationResult {validation_result_obj.id} created")

                # ═══════════════════════════════════════════════════════════════════
                # 🤖 LLM Pipeline Validation (if enabled)
                # ═══════════════════════════════════════════════════════════════════
                validation_mode = getattr(script, 'validation_mode', 'houndify')
                llm_passed = True  # Default to True if LLM not enabled
                llm_decision = 'pass'  # Default decision
                llm_confidence = 'high'  # Default confidence

                if validation_mode in ('llm_ensemble', 'hybrid'):
                    # Get the AI response and user utterance for this language
                    lang_ai_response = lang_result.get('ai_response', primary_ai_response)
                    lang_utterance = language_variants.get(lang_code, step.user_utterance)

                    # Build context for LLM evaluation (only step_order needed)
                    eval_context = {
                        'step_order': step.step_order,
                    }

                    # Run LLM validation - LLMs evaluate behavioral correctness
                    llm_passed, llm_decision, llm_confidence = await self._run_llm_pipeline_validation(
                        db=db,
                        validation_result=validation_result_obj,
                        user_utterance=lang_utterance,
                        ai_response=lang_ai_response or "",
                        context=eval_context
                    )

                # ═══════════════════════════════════════════════════════════════════
                # 🔀 Compute COMBINED decision (deterministic + LLM)
                # ═══════════════════════════════════════════════════════════════════
                houndify_passed = validation_result.get('passed', False)
                final_decision = self._compute_combined_decision(
                    houndify_passed=houndify_passed,
                    llm_decision=llm_decision,
                    validation_mode=validation_mode
                )
                review_status = self._compute_review_status(
                    final_decision=final_decision,
                    llm_confidence=llm_confidence
                )

                # Store combined decision on validation result
                validation_result_obj.final_decision = final_decision
                validation_result_obj.review_status = review_status

                # Calculate total validation latency (Houndify + LLM combined wall-clock time)
                total_validation_latency_ms = int((time.time() - validation_start_time) * 1000)

                # Add total_validation_latency_ms to both houndify_result and ensemble_result
                if validation_result_obj.houndify_result:
                    validation_result_obj.houndify_result['total_validation_latency_ms'] = total_validation_latency_ms
                if validation_result_obj.ensemble_result:
                    validation_result_obj.ensemble_result['total_validation_latency_ms'] = total_validation_latency_ms

                await db.commit()

                logger.info(
                    f"  - {lang_code}: Combined decision: houndify={houndify_passed}, "
                    f"llm={llm_decision}, final={final_decision}, status={review_status}, "
                    f"latency={total_validation_latency_ms}ms"
                )

                # ═══════════════════════════════════════════════════════════════════
                # 🔴 Track validation outcome for defect auto-creation
                # ═══════════════════════════════════════════════════════════════════
                # Call for ALL review statuses - auto_fail increments streak,
                # other statuses reset it (prevents false positives from intermittent failures)
                try:
                    await self._check_defect_auto_creation(
                        db=db,
                        execution=execution,
                        validation_result=validation_result_obj,
                        review_status=review_status,
                    )
                except Exception as defect_err:
                    logger.warning(f"Defect auto-creation check failed: {defect_err}")

                # ═══════════════════════════════════════════════════════════════════
                # 📋 Enqueue for human review based on COMBINED decision
                # ═══════════════════════════════════════════════════════════════════
                # Queue if the combined decision is not auto_pass
                needs_human_review = review_status != "auto_pass"

                # 5% random sampling of auto_pass items for calibration
                # This allows us to measure agreement on pass decisions too
                is_sampled = False
                if review_status == "auto_pass" and random.random() < 0.05:
                    needs_human_review = True
                    is_sampled = True
                    logger.info(f"    🎲 Random sample: auto_pass selected for human review")

                if needs_human_review:
                    from decimal import Decimal

                    queue_service = ValidationQueueService()

                    # Priority based on combined decision:
                    # - Priority 1: Combined decision is 'fail' (highest urgency)
                    # - Priority 2: Combined decision is 'uncertain' (systems disagreed)
                    # - Priority 5: Needs review for other reasons
                    # - Priority 10: Random sample (lowest urgency, for calibration)
                    if is_sampled:
                        priority = 10  # Random sample - lowest priority
                    elif final_decision == 'fail':
                        priority = 1  # Confirmed failure
                    elif final_decision == 'uncertain':
                        priority = 2  # Systems disagreed or LLM uncertain
                    else:
                        priority = 5  # Needs review

                    confidence_percentage = Decimal(str(validation_score * 100)).quantize(
                        Decimal('0.01')
                    )

                    queue_item = await queue_service.enqueue_for_human_review(
                        db=db,
                        validation_result_id=validation_result_obj.id,
                        priority=priority,
                        confidence_score=confidence_percentage,
                        language_code=lang_code,  # 🌍 Pass language code to queue
                        requires_native_speaker=False
                    )

                    sample_tag = " [SAMPLE]" if is_sampled else ""
                    logger.info(
                        f"    → Queued for review: {queue_item.id}{sample_tag} "
                        f"(final={final_decision}, houndify={houndify_passed}, llm={llm_decision})"
                    )

            # ═══════════════════════════════════════════════════════════════════
            # 📝 Update step_execution.validation_details with full results
            # ═══════════════════════════════════════════════════════════════════
            # Fetch ValidationResults for this step to include in validation_details
            stmt = select(ValidationResult).where(
                ValidationResult.step_execution_id == step_execution.id
            )
            validation_results = await db.execute(stmt)
            validation_results = validation_results.scalars().all()

            # Build enhanced per-language results with houndify and LLM data
            # Start with the execution data we already stored
            enhanced_per_language = dict(step_execution.validation_details.get('per_language_results', {}))
            # Track if all languages passed the combined decision
            # Start with False if no results exist (all failed with errors)
            all_passed = len(validation_results) > 0
            for vr in validation_results:
                # Use combined final_decision, not just houndify_passed
                lang_passed = vr.final_decision == 'pass'
                if not lang_passed:
                    all_passed = False
                # Get existing data for this language (if any)
                existing_data = enhanced_per_language.get(vr.language_code, {})
                # Merge validation results with execution data
                enhanced_per_language[vr.language_code] = {
                    **existing_data,  # Keep user_utterance, ai_response, transcription, etc.
                    'passed': lang_passed,  # Combined decision, not just houndify
                    'errors': vr.houndify_result.get('errors', []) if vr.houndify_result else [],
                    'houndify_result': vr.houndify_result,
                    'ensemble_result': vr.ensemble_result,
                    'final_decision': vr.final_decision,
                    'review_status': vr.review_status,
                }

            # Update step_execution validation_details and validation_passed
            # Use combined decision from LLM + Houndify, not just houndify-only result
            step_execution.validation_passed = all_passed
            step_execution.validation_details = {
                'languages_validated': list(language_validation_results.keys()),
                'primary_language': primary_lang,
                'per_language_results': enhanced_per_language,
                # Include primary language's results at top level for convenience
                'houndify_result': enhanced_per_language.get(primary_lang, {}).get('houndify_result'),
                'ensemble_result': enhanced_per_language.get(primary_lang, {}).get('ensemble_result'),
                'final_decision': enhanced_per_language.get(primary_lang, {}).get('final_decision'),
            }
            await db.commit()

            return {
                "step_execution_id": str(step_execution.id),
                "step_execution": step_execution,
                "validation_passed": all_passed,  # Combined decision from LLM + Houndify
                "conversation_state_after": new_conversation_state,
                "ai_response": primary_ai_response,
                "languages_validated": list(language_validation_results.keys())
            }

        except Exception as e:
            logger.error(f"❌ Step {step.step_order} execution failed: {str(e)}", exc_info=True)

            # Create failed step execution record
            step_execution = StepExecution(
                multi_turn_execution_id=execution.id,
                step_id=step.id,
                step_order=step.step_order,
                user_utterance=step.user_utterance,
                request_id=request_id,
                conversation_state_before=conversation_state,
                validation_passed=False,
                error_message=str(e),
                executed_at=start_time
            )
            db.add(step_execution)
            await db.commit()

            raise

    async def _validate_step(
        self,
        db: AsyncSession,
        step: ScenarioStep,
        ai_response: Optional[str],
        transcription: Optional[str],
        command_kind: Optional[str],
        confidence_score: Optional[float],
        language_code: Optional[str] = None,
        actual_entities: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate step execution against expected outcome.

        Args:
            db: Database session
            step: Scenario step
            ai_response: AI's response
            transcription: Transcription of user utterance
            command_kind: Houndify CommandKind
            confidence_score: Recognition confidence
            language_code: Language code for language-specific validation
            actual_entities: NativeData/entities from Houndify response

        Returns:
            Dictionary with validation results including latency_ms
        """
        # Track validation latency
        validation_start_time = time.time()

        # Get expected outcome for this step
        stmt = select(ExpectedOutcome).where(ExpectedOutcome.scenario_step_id == step.id)
        result = await db.execute(stmt)
        expected_outcome = result.scalar_one_or_none()

        if not expected_outcome:
            # No ExpectedOutcome configured - auto-pass with warning
            logger.warning("  - No ExpectedOutcome configured for step, auto-passing")
            latency_ms = int((time.time() - validation_start_time) * 1000)
            return {
                "passed": True,
                "errors": [],
                "method": "no_validation",
                "warning": "No ExpectedOutcome configured for this step",
                "latency_ms": latency_ms,
            }

        # Validate against ExpectedOutcome
        logger.info(f"  - Validating against ExpectedOutcome: {expected_outcome.outcome_code}")

        errors = []

        # Check expected CommandKind (Houndify's native classification)
        if expected_outcome.expected_command_kind and command_kind:
            if command_kind != expected_outcome.expected_command_kind:
                errors.append(f"CommandKind mismatch: expected {expected_outcome.expected_command_kind}, got {command_kind}")

        # Check confidence threshold
        validation_rules = expected_outcome.validation_rules or {}
        min_confidence = validation_rules.get('min_confidence', 0.0)
        if confidence_score is not None and confidence_score < min_confidence:
            errors.append(f"Confidence too low: {confidence_score} < {min_confidence}")

        # Check response content patterns if defined
        # Uses ValidationHoundifyMixin._validate_response_content for deterministic checks

        # Check if language_variations exists and language_code is provided
        language_variations = getattr(expected_outcome, 'language_variations', None)
        if language_code and language_variations and isinstance(language_variations, dict):
            # Extract language-specific expected response patterns
            lang_variation = language_variations.get(language_code, {})
            if lang_variation and 'expected_response_patterns' in lang_variation:
                expected_response_content = lang_variation['expected_response_patterns']
                logger.info(
                    f"    Using language-specific validation patterns for {language_code}: "
                    f"{expected_response_content}"
                )
            else:
                # Fall back to default expected_response_content
                expected_response_content = expected_outcome.expected_response_content or {}
                logger.debug(
                    f"    No language-specific patterns found for {language_code}, "
                    f"using default expected_response_content"
                )
        else:
            # No language variations or language_code, use default
            expected_response_content = expected_outcome.expected_response_content or {}

        forbidden_phrases = expected_outcome.forbidden_phrases
        response_content_result = self._validate_response_content(
            ai_response=ai_response,
            expected_response_content=expected_response_content,
            forbidden_phrases=forbidden_phrases,
        )

        # Add response content errors to overall errors
        if not response_content_result['passed']:
            errors.extend(response_content_result.get('errors', []))

        # Validate entities if expected entities are defined
        expected_entities = expected_outcome.entities
        entity_validation_result = self._validate_entities(
            actual_entities=actual_entities,
            expected_entities=expected_entities,
        )

        # Add entity validation errors to overall errors
        if not entity_validation_result['passed']:
            errors.extend(entity_validation_result.get('errors', []))

        passed = len(errors) == 0

        # Calculate Houndify validation latency
        latency_ms = int((time.time() - validation_start_time) * 1000)

        return {
            "passed": passed,
            "errors": errors,
            "expected_outcome_id": str(expected_outcome.id),
            "expected_outcome": expected_outcome,  # Return the object for confidence calculation
            "confidence_score": confidence_score,
            "command_kind": command_kind,
            "response_content_result": response_content_result,  # Include detailed result
            "entity_validation": entity_validation_result,  # Include entity validation result
            "expected_entities": expected_entities,
            "actual_entities": actual_entities,
            "latency_ms": latency_ms,  # Houndify validation latency in milliseconds
        }

    def _calculate_validation_score(
        self,
        validation_result: Dict[str, Any],
        asr_confidence: Optional[float],
        expected_outcome: Optional[ExpectedOutcome]
    ) -> float:
        """
        Calculate composite validation score for Houndify deterministic checks.

        This score represents the overall quality of the deterministic validation,
        combining multiple check results into a single 0.0-1.0 score.

        Components:
        1. Validation passed/failed (50% weight)
        2. ASR confidence from Houndify (30% weight)
        3. CommandKind match (20% weight)

        Args:
            validation_result: Validation result dict with 'passed' and 'errors'
            asr_confidence: ASR confidence from Houndify (0.0 to 1.0)
            expected_outcome: Expected outcome for this step

        Returns:
            Validation score (0.0 to 1.0)
        """
        # Base score from validation pass/fail
        pass_score = 1.0 if validation_result.get('passed', False) else 0.0

        # ASR confidence from Houndify
        asr_score = asr_confidence if asr_confidence is not None else 0.5

        # CommandKind match score
        command_kind_score = 0.0
        if expected_outcome and expected_outcome.expected_command_kind:
            errors = validation_result.get('errors', [])
            has_command_kind_error = any('CommandKind mismatch' in err for err in errors)
            command_kind_score = 0.0 if has_command_kind_error else 1.0
        else:
            command_kind_score = 1.0  # No CommandKind requirement = pass

        # Weighted average
        score = (
            pass_score * 0.5 +
            asr_score * 0.3 +
            command_kind_score * 0.2
        )

        return round(score, 4)


    async def _emit_execution_started(
        self,
        execution: MultiTurnExecution,
        script: ScenarioScript
    ) -> None:
        """Emit event when multi-turn execution starts."""
        try:
            room_name = self._get_room_name(execution)
            await emit_to_room(
                room=room_name,
                event='multi_turn_execution_started',
                data={
                    'execution_id': str(execution.id),
                    'suite_run_id': str(execution.suite_run_id),
                    'script_id': str(execution.script_id),
                    'script_name': script.name,
                    'total_steps': execution.total_steps,
                    'status': execution.status,
                    'started_at': execution.started_at.isoformat() if execution.started_at else None
                }
            )
            logger.debug(f"[SOCKET.IO] Emitted multi_turn_execution_started for execution {execution.id}")
        except Exception as e:
            logger.warning(f"[SOCKET.IO] Failed to emit execution_started: {str(e)}")

    async def _emit_step_started(
        self,
        execution: MultiTurnExecution,
        step: ScenarioStep
    ) -> None:
        """Emit event when a step starts executing."""
        try:
            room_name = self._get_room_name(execution)
            await emit_to_room(
                room=room_name,
                event='multi_turn_step_started',
                data={
                    'execution_id': str(execution.id),
                    'suite_run_id': str(execution.suite_run_id),
                    'step_id': str(step.id),
                    'step_order': step.step_order,
                    'total_steps': execution.total_steps,
                    'user_utterance': step.user_utterance,
                    'progress_percentage': ((step.step_order - 1) / execution.total_steps) * 100
                }
            )
            logger.debug(f"[SOCKET.IO] Emitted multi_turn_step_started for step {step.step_order}")
        except Exception as e:
            logger.warning(f"[SOCKET.IO] Failed to emit step_started: {str(e)}")

    async def _emit_step_completed(
        self,
        execution: MultiTurnExecution,
        step_execution: StepExecution
    ) -> None:
        """Emit event when a step completes."""
        try:
            room_name = self._get_room_name(execution)
            await emit_to_room(
                room=room_name,
                event='multi_turn_step_completed',
                data={
                    'execution_id': str(execution.id),
                    'suite_run_id': str(execution.suite_run_id),
                    'step_execution_id': str(step_execution.id),
                    'step_order': step_execution.step_order,
                    'total_steps': execution.total_steps,
                    'user_utterance': step_execution.user_utterance,
                    'audio_data_urls': step_execution.audio_data_urls,  # Map of language codes to audio URLs
                    'request_id': step_execution.request_id,
                    'ai_response': step_execution.ai_response,
                    'transcription': step_execution.transcription,
                    'command_kind': step_execution.command_kind,
                    'confidence_score': step_execution.confidence_score,
                    'validation_passed': step_execution.validation_passed,
                    'validation_details': step_execution.validation_details,
                    'response_time_ms': step_execution.response_time_ms,
                    'progress_percentage': (step_execution.step_order / execution.total_steps) * 100,
                    'executed_at': step_execution.executed_at.isoformat() if step_execution.executed_at else None
                }
            )
            logger.debug(f"[SOCKET.IO] Emitted multi_turn_step_completed for step {step_execution.step_order}")
        except Exception as e:
            logger.warning(f"[SOCKET.IO] Failed to emit step_completed: {str(e)}")

    async def _emit_execution_completed(
        self,
        execution: MultiTurnExecution
    ) -> None:
        """Emit event when multi-turn execution completes."""
        try:
            room_name = self._get_room_name(execution)
            await emit_to_room(
                room=room_name,
                event='multi_turn_execution_completed',
                data={
                    'execution_id': str(execution.id),
                    'suite_run_id': str(execution.suite_run_id),
                    'script_id': str(execution.script_id),
                    'status': execution.status,
                    'total_steps': execution.total_steps,
                    'current_step_order': execution.current_step_order,
                    'all_steps_passed': execution.all_steps_passed,
                    'started_at': execution.started_at.isoformat() if execution.started_at else None,
                    'completed_at': execution.completed_at.isoformat() if execution.completed_at else None
                }
            )
            logger.debug(f"[SOCKET.IO] Emitted multi_turn_execution_completed for execution {execution.id}")
        except Exception as e:
            logger.warning(f"[SOCKET.IO] Failed to emit execution_completed: {str(e)}")

    async def _emit_execution_failed(
        self,
        execution: MultiTurnExecution,
        error_message: str
    ) -> None:
        """Emit event when multi-turn execution fails."""
        try:
            room_name = self._get_room_name(execution)
            await emit_to_room(
                room=room_name,
                event='multi_turn_execution_failed',
                data={
                    'execution_id': str(execution.id),
                    'suite_run_id': str(execution.suite_run_id),
                    'script_id': str(execution.script_id),
                    'status': execution.status,
                    'error_message': error_message,
                    'current_step_order': execution.current_step_order,
                    'total_steps': execution.total_steps,
                    'failed_at': datetime.utcnow().isoformat()
                }
            )
            logger.debug(f"[SOCKET.IO] Emitted multi_turn_execution_failed for execution {execution.id}")
        except Exception as e:
            logger.warning(f"[SOCKET.IO] Failed to emit execution_failed: {str(e)}")

    async def _emit_progress(
        self,
        socketio,
        execution: MultiTurnExecution,
        step: ScenarioStep
    ) -> None:
        """Emit real-time progress update via Socket.IO (legacy method for backward compatibility)."""
        try:
            await socketio.emit(
                'multi_turn_progress',
                {
                    'execution_id': str(execution.id),
                    'suite_run_id': str(execution.suite_run_id),
                    'current_step': step.step_order,
                    'total_steps': execution.total_steps,
                    'progress_percentage': (step.step_order / execution.total_steps) * 100,
                    'step_utterance': step.user_utterance
                },
                room=f"suite_run_{execution.suite_run_id}"
            )
        except Exception as e:
            logger.warning(f"Failed to emit progress update: {str(e)}")

    async def _update_suite_run_status(
        self,
        db: AsyncSession,
        suite_run_id: UUID,
        status: str
    ) -> None:
        """
        Update suite run status and completion timestamp.

        Args:
            db: Database session
            suite_run_id: Suite run ID to update
            status: New status (completed, failed, etc.)
        """
        try:
            # Load suite run
            result = await db.execute(
                select(SuiteRun).where(SuiteRun.id == suite_run_id)
            )
            suite_run = result.scalar_one_or_none()

            if not suite_run:
                logger.warning(f"Suite run {suite_run_id} not found, cannot update status")
                return

            # Update status using model methods to ensure timestamps are set
            if status == 'completed':
                suite_run.mark_as_completed()
            elif status == 'failed':
                suite_run.mark_as_failed()
            elif status == 'running':
                suite_run.mark_as_running()
            elif status == 'cancelled':
                suite_run.mark_as_cancelled()
            else:
                suite_run.status = status

            # Calculate test metrics from executions with validation results
            executions_result = await db.execute(
                select(MultiTurnExecution)
                .options(selectinload(MultiTurnExecution.validation_results))
                .where(MultiTurnExecution.suite_run_id == suite_run_id)
            )
            executions = executions_result.scalars().all()

            # Count tests considering both execution status AND validation result
            total_tests = len(executions)
            passed_tests = 0
            failed_tests = 0

            for ex in executions:
                # Get the validation review status (if any)
                validation_status = None
                if ex.validation_results:
                    # Check all validation results - if any is auto_fail, consider failed
                    for vr in ex.validation_results:
                        if vr.review_status == 'auto_fail':
                            validation_status = 'auto_fail'
                            break
                        elif vr.review_status == 'auto_pass':
                            validation_status = 'auto_pass'
                        elif vr.review_status == 'needs_review' and validation_status != 'auto_pass':
                            validation_status = 'needs_review'

                # Determine pass/fail based on execution status and validation
                if ex.status == 'failed':
                    # Execution itself failed
                    failed_tests += 1
                elif validation_status == 'auto_fail':
                    # Execution completed but validation failed
                    failed_tests += 1
                elif ex.status == 'completed':
                    # Completed and either auto_pass or no validation yet
                    if validation_status == 'auto_pass':
                        passed_tests += 1
                    elif validation_status == 'needs_review':
                        # Don't count as passed or failed until reviewed
                        pass
                    else:
                        # No validation result yet, count as passed for now
                        passed_tests += 1

            suite_run.total_tests = total_tests
            suite_run.passed_tests = passed_tests
            suite_run.failed_tests = failed_tests

            logger.info(
                f"Updated suite run {suite_run_id}: status={status}, "
                f"total={total_tests}, passed={passed_tests}, failed={failed_tests}"
            )

        except Exception as e:
            logger.error(f"Failed to update suite run status: {str(e)}", exc_info=True)

    def _get_language_code(
        self,
        script: ScenarioScript,
        step: ScenarioStep
    ) -> str:
        """
        Extract primary language code from script or step metadata.

        Priority:
        1. step.step_metadata['language'] (for single-turn converted scenarios)
        2. step.step_metadata['primary_language'] (for multi-language steps)
        3. script.script_metadata['language'] (for whole script)
        4. First language from script.script_metadata['supported_languages'] if language is "multi"
        5. Default to "en-US"

        Args:
            script: Scenario script
            step: Scenario step

        Returns:
            Language code (e.g., "en-US", "es-ES", "fr-FR")
        """
        # Check step metadata first
        step_metadata = step.step_metadata or {}
        if 'language' in step_metadata and step_metadata['language'] != 'multi':
            return step_metadata['language']
        if 'primary_language' in step_metadata:
            return step_metadata['primary_language']

        # Check script metadata
        script_metadata = script.script_metadata or {}
        if 'language' in script_metadata:
            language = script_metadata['language']
            # Handle "multi" language - use first supported language
            if language == 'multi' and 'supported_languages' in script_metadata:
                supported = script_metadata['supported_languages']
                if isinstance(supported, list) and len(supported) > 0:
                    return supported[0]
            elif language != 'multi':
                return language

        # Default to English
        return "en-US"

    def _get_language_variants(
        self,
        script: ScenarioScript,
        step: ScenarioStep,
        language_codes: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Extract language variants from step metadata, optionally filtering by language_codes.

        Returns a dictionary mapping language codes to user utterances.

        Priority:
        1. step.step_metadata['language_variants'] (for multi-language steps)
        2. Single language from step.step_metadata['language'] or primary_language
        3. Single language from script.script_metadata['language']
        4. Default to English with step.user_utterance

        Args:
            script: Scenario script
            step: Scenario step
            language_codes: Optional list of language codes to include.
                           None = include all variants
                           ["en-US"] = include only English
                           ["en-US", "fr-FR"] = include both

        Returns:
            Dictionary mapping language codes to utterances
            Example: {
                "en-US": "What's the weather?",
                "fr-FR": "Quel temps fait-il?"
            }
        """
        step_metadata = step.step_metadata or {}

        # Check for language_variants array
        if 'language_variants' in step_metadata:
            variants = step_metadata['language_variants']
            if isinstance(variants, list) and len(variants) > 0:
                # Convert array to dict, filtering by language_codes if specified
                result = {}
                for variant in variants:
                    if isinstance(variant, dict):
                        lang_code = variant.get('language_code')
                        utterance = variant.get('user_utterance')
                        if lang_code and utterance:
                            # Apply language filter if specified
                            if language_codes is None or lang_code in language_codes:
                                result[lang_code] = utterance

                if result:
                    return result

        # Fallback: single language
        primary_lang = self._get_language_code(script, step)

        # Apply filter even to fallback
        if language_codes is not None and primary_lang not in language_codes:
            # If primary language not in filter, use the first language from the filter
            # This ensures steps without language_variants still work when filtering
            if len(language_codes) > 0:
                primary_lang = language_codes[0]
                logger.warning(
                    f"Step {step.step_order} doesn't have language_variants for filtered languages. "
                    f"Using first filtered language ({primary_lang}) with default utterance."
                )

        return {primary_lang: step.user_utterance}

    async def _upload_audio_to_storage(
        self,
        audio_bytes: bytes,
        execution_id: UUID,
        step_order: int,
        language_code: str
    ) -> Optional[str]:
        """
        Upload audio to S3/MinIO storage and return the HTTP URL.

        Args:
            audio_bytes: Raw audio data
            execution_id: MultiTurnExecution ID
            step_order: Step order number
            language_code: Language code (e.g., en-US, es-ES, fr-FR)

        Returns:
            HTTP URL or None if upload fails
        """
        try:
            # Generate unique filename
            filename = f"multi-turn/{execution_id}/step_{step_order}_{language_code}.mp3"

            # Upload to S3/MinIO
            s3_url = await self.storage_service.upload_audio(
                audio_bytes,
                filename,
                bucket="voice-ai-testing-audio"
            )

            logger.info(f"Uploaded {len(audio_bytes)} bytes to {s3_url}")
            return s3_url

        except Exception as e:
            logger.error(f"Failed to upload audio to storage: {e}", exc_info=True)
            return None

    async def _upload_response_audio_to_storage(
        self,
        response_audio_base64: str,
        execution_id: UUID,
        step_order: int,
        language_code: str
    ) -> Optional[str]:
        """
        Upload Houndify response audio (TTS) to S3/MinIO storage.

        Args:
            response_audio_base64: Base64-encoded audio from Houndify ResponseAudioBytes
            execution_id: MultiTurnExecution ID
            step_order: Step order number
            language_code: Language code (e.g., en-US, es-ES, fr-FR)

        Returns:
            HTTP URL or None if upload fails
        """
        import base64

        try:
            # Decode base64 audio
            audio_bytes = base64.b64decode(response_audio_base64)

            # Generate unique filename for response audio
            filename = f"multi-turn/{execution_id}/step_{step_order}_{language_code}_response.wav"

            # Upload to S3/MinIO
            s3_url = await self.storage_service.upload_audio(
                audio_bytes,
                filename,
                bucket="voice-ai-testing-audio"
            )

            logger.info(f"Uploaded response audio ({len(audio_bytes)} bytes) to {s3_url}")
            return s3_url

        except Exception as e:
            logger.error(f"Failed to upload response audio: {e}", exc_info=True)
            return None

    async def _run_llm_pipeline_validation(
        self,
        db: AsyncSession,
        validation_result: ValidationResult,
        user_utterance: str,
        ai_response: str,
        context: Dict[str, Any]
    ) -> tuple:
        """
        Run LLM pipeline validation for a validation result.

        This method uses the 3-stage LLM pipeline (2 evaluators + 1 curator)
        to evaluate the voice AI response behaviorally (not text matching)
        and updates the ValidationResult.

        Args:
            db: Database session
            validation_result: ValidationResult to update
            user_utterance: What the user said
            ai_response: What the voice AI responded
            context: Additional context for evaluation (step_order, etc.)

        Returns:
            tuple: (llm_passed, llm_decision, llm_confidence)
                - llm_passed: True if LLM validation passed
                - llm_decision: 'pass', 'fail', or 'needs_review'
                - llm_confidence: 'high', 'medium', or 'low'
        """
        try:
            logger.info(f"  [LLM Pipeline] Starting 3-stage evaluation...")

            # Create pipeline service
            pipeline_service = LLMPipelineService()

            # Run evaluation - LLMs evaluate behavioral correctness
            pipeline_result = await pipeline_service.evaluate(
                user_utterance=user_utterance,
                ai_response=ai_response,
                context=context,
            )

            # Determine if LLM passed (pass decision with high/medium confidence)
            llm_passed = (
                pipeline_result.final_decision == 'pass' and
                pipeline_result.confidence in ('high', 'medium')
            )

            # Update validation result with pipeline results (using correct field names)
            validation_result.ensemble_result = pipeline_result.to_dict()
            validation_result.llm_passed = llm_passed

            await db.commit()

            logger.info(
                f"  [LLM Pipeline] Completed: decision={pipeline_result.final_decision}, "
                f"score={pipeline_result.final_score:.2f}, confidence={pipeline_result.confidence}, "
                f"llm_passed={llm_passed}"
            )

            return llm_passed, pipeline_result.final_decision, pipeline_result.confidence

        except Exception as e:
            logger.error(f"  [LLM Pipeline] Failed: {str(e)}", exc_info=True)
            # Don't fail the whole validation - just log the error
            # Return needs_review so it goes to human review (safe default)
            return False, 'needs_review', 'low'

    def _compute_combined_decision(
        self,
        houndify_passed: bool,
        llm_decision: str,
        validation_mode: str,
    ) -> str:
        """
        Compute the final combined decision from Houndify and LLM results.

        Decision logic varies by validation mode:
        - houndify: Use Houndify result only
        - llm_ensemble: Use LLM result only
        - hybrid: Combine both (agreement required for confident decision)

        Args:
            houndify_passed: Whether Houndify validation passed
            llm_decision: LLM's decision (pass/fail/needs_review)
            validation_mode: 'houndify', 'llm_ensemble', or 'hybrid'

        Returns:
            Final decision: 'pass', 'fail', or 'uncertain'
        """
        if validation_mode == 'houndify':
            # Houndify only
            return 'pass' if houndify_passed else 'fail'

        if validation_mode == 'llm_ensemble':
            # LLM only
            if llm_decision == 'needs_review':
                return 'uncertain'
            return llm_decision

        # Hybrid mode - combine both
        llm_passed = llm_decision == 'pass'

        # If LLM is uncertain, needs human review
        if llm_decision == 'needs_review':
            return 'uncertain'

        # Both ran - check agreement
        if houndify_passed and llm_passed:
            return 'pass'
        elif not houndify_passed and not llm_passed:
            return 'fail'
        else:
            # Disagreement - needs human review
            logger.info(
                f"Houndify/LLM disagreement: houndify={houndify_passed}, "
                f"llm={llm_decision}, flagging for review"
            )
            return 'uncertain'

    def _compute_review_status(
        self,
        final_decision: str,
        llm_confidence: str,
    ) -> str:
        """
        Compute the review status from final decision and LLM confidence.

        Args:
            final_decision: 'pass', 'fail', or 'uncertain'
            llm_confidence: 'high', 'medium', or 'low'

        Returns:
            Review status: 'auto_pass', 'auto_fail', or 'needs_review'
        """
        if final_decision == 'uncertain':
            return 'needs_review'

        # Low confidence always needs review
        if llm_confidence == 'low':
            return 'needs_review'

        if final_decision == 'pass':
            return 'auto_pass'
        elif final_decision == 'fail':
            return 'auto_fail'
        else:
            return 'needs_review'

    async def _check_defect_auto_creation(
        self,
        db: AsyncSession,
        execution: MultiTurnExecution,
        validation_result: ValidationResult,
        review_status: str,
    ) -> None:
        """
        Check if defect should be auto-created based on consecutive failures.

        Uses Redis for persistent streak tracking across server restarts.
        """
        from api.redis_client import get_redis
        from services.defect_service import DefectService

        # Ensure relationships are loaded for defect payload
        # - script: for scenario name in defect title
        # - step_executions: for language code extraction from audio_data_urls
        try:
            if not execution.script:
                await db.refresh(execution, ['script'])
            if not execution.step_executions:
                await db.refresh(execution, ['step_executions'])
        except Exception as e:
            logger.debug(f"Could not load execution relationships: {e}")

        # Get Redis client for persistent streak storage
        try:
            redis_gen = get_redis()
            redis_client = await redis_gen.__anext__()
        except Exception as e:
            logger.warning(f"Could not get Redis client for defect tracking: {e}")
            redis_client = None

        # Get threshold from settings
        tenant_id = execution.tenant_id
        threshold = await get_defect_threshold(db, tenant_id)

        # Create defect creation function
        async def create_defect(data: dict) -> None:
            defect_service = DefectService()
            defect_data = {
                "title": data.get("title", "Auto-detected defect"),
                "description": data.get("description", ""),
                "severity": data.get("severity", "high"),
                "category": data.get("category", "validation_failure"),
                "script_id": data.get("script_id"),
                "execution_id": data.get("execution_id"),
                "tenant_id": data.get("tenant_id"),
                "status": data.get("status", "open"),
                "detected_at": data.get("detected_at"),
                "language_code": data.get("language_code"),
            }
            await defect_service.create_defect(db=db, data=defect_data)
            logger.info(f"Auto-created defect for script {data.get('script_id')}")

        # Create and use DefectAutoCreator
        defect_creator = DefectAutoCreator(
            create_defect=create_defect,
            failure_threshold=threshold,
            redis_client=redis_client,
        )

        await defect_creator.record_validation_outcome(
            execution=execution,
            validation_result=validation_result,
            review_status=review_status,
        )


