"""
Unit tests for ValidationService.

Tests the validation orchestration including execution/outcome fetching,
score calculation, and validation result creation.
Uses mocked database sessions and ML components to test service logic
without external dependencies.
"""

import pytest
from uuid import uuid4
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from services.validation_service import ValidationService
from models.multi_turn_execution import MultiTurnExecution
from models.expected_outcome import ExpectedOutcome
from models.validation_result import ValidationResult


class TestValidationServiceInit:
    """Test ValidationService initialization.

    Note: The ValidationService has been refactored to use hybrid validation:
    - Houndify deterministic checks (CommandKind, ASR, response patterns)
    - LLM ensemble behavioral evaluation
    Legacy ML components (semantic_matcher, intent_classifier, entity_extractor)
    have been removed.
    """

    def test_service_initialization_default(self):
        """Test that ValidationService can be instantiated with defaults."""
        service = ValidationService()
        assert service is not None
        assert isinstance(service, ValidationService)
        # New interface only has metrics_recorder and defect_auto_creator
        assert service._metrics_recorder is None
        assert service._defect_auto_creator is None

    def test_service_initialization_with_callbacks(self):
        """Test ValidationService initialization with metrics and defect services."""
        mock_metrics = MagicMock()
        mock_defect = MagicMock()

        service = ValidationService(
            metrics_recorder=mock_metrics,
            defect_auto_creator=mock_defect,
        )

        assert service._metrics_recorder is mock_metrics
        assert service._defect_auto_creator is mock_defect


class TestValidationServiceValidation:
    """Test ValidationService.validate_voice_response method."""

    @pytest.fixture
    def service(self):
        """Provide ValidationService instance."""
        return ValidationService()

    @pytest.fixture
    def mock_db(self):
        """Provide mocked async database session."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def mock_execution(self):
        """Provide mock MultiTurnExecution."""
        execution = MagicMock(spec=MultiTurnExecution)
        execution.id = uuid4()
        execution.suite_run_id = uuid4()
        execution.transcribed_text = "hello world"
        execution.confidence = 0.95
        execution.get_all_response_entities = MagicMock(return_value={
            "transcribed_text": "hello world",
            "confidence": 0.95
        })
        execution.get_all_context = MagicMock(return_value={})
        return execution

    @pytest.fixture
    def mock_expected_outcome(self):
        """Provide mock ExpectedOutcome."""
        outcome = MagicMock(spec=ExpectedOutcome)
        outcome.id = uuid4()
        outcome.expected_transcript = "hello world"
        # Set entities to empty dict so entity validation auto-passes
        # Tests that need specific entity validation should override this
        outcome.entities = {}
        outcome.validation_rules = {"tolerance": 0.85}
        return outcome

    @pytest.mark.asyncio
    async def test_validate_voice_response_success(
        self,
        service,
        mock_db,
        mock_execution,
        mock_expected_outcome
    ):
        """Test successful validation with new hybrid approach.

        The ValidationService now uses:
        - Houndify deterministic checks (CommandKind, ASR, response patterns)
        - LLM ensemble (when enabled)

        Legacy WER/CER/SER/semantic scores are deprecated.
        """
        execution_id = mock_execution.id
        expected_outcome_id = mock_expected_outcome.id

        # Set up expected outcome with Houndify-specific fields
        mock_expected_outcome.expected_command_kind = "WeatherCommand"
        mock_expected_outcome.expected_asr_confidence_min = 0.7
        mock_expected_outcome.expected_response_content = {"contains": ["sunny"]}
        mock_expected_outcome.forbidden_phrases = None

        # Mock Houndify response in execution context
        mock_execution.get_all_context.return_value = {
            "houndify_response": {
                "AllResults": [{
                    "CommandKind": "WeatherCommand",
                    "ASRConfidence": 0.95,
                    "SpokenResponse": "It's sunny and 72 degrees today"
                }]
            }
        }

        with patch.object(service, '_fetch_execution', new_callable=AsyncMock) as mock_fetch_exec:
            with patch.object(service, '_fetch_expected_outcome', new_callable=AsyncMock) as mock_fetch_outcome:
                mock_fetch_exec.return_value = mock_execution
                mock_fetch_outcome.return_value = mock_expected_outcome

                with patch.object(service, '_resolve_transcript', return_value="what's the weather"):
                    result = await service.validate_voice_response(
                        execution_id=execution_id,
                        expected_outcome_id=expected_outcome_id,
                        validation_mode='houndify',
                    )

                    # Verify result
                    assert result is not None
                    assert isinstance(result, ValidationResult)
                    assert result.suite_run_id == mock_execution.suite_run_id
                    # Houndify validation should pass
                    assert result.houndify_passed is True
                    assert result.command_kind_match_score == 1.0
                    # Final decision should be pass
                    assert result.final_decision == 'pass'

    @pytest.mark.asyncio
    async def test_validate_voice_response_execution_not_found(
        self,
        service,
    ):
        """Test that validation raises error when execution not found."""
        execution_id = uuid4()
        expected_outcome_id = uuid4()

        with patch.object(service, '_fetch_execution', new_callable=AsyncMock) as mock_fetch_exec:
            with patch.object(service, '_fetch_expected_outcome', new_callable=AsyncMock) as mock_fetch_outcome:
                mock_fetch_exec.return_value = None
                mock_fetch_outcome.return_value = MagicMock()

                with pytest.raises(ValueError) as exc_info:
                    await service.validate_voice_response(
                        execution_id=execution_id,
                        expected_outcome_id=expected_outcome_id,
                    )

                assert "MultiTurnExecution not found" in str(exc_info.value)
                assert str(execution_id) in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_voice_response_outcome_not_found(
        self,
        service,
        mock_execution,
    ):
        """Test that validation raises error when expected outcome not found."""
        execution_id = mock_execution.id
        expected_outcome_id = uuid4()

        with patch.object(service, '_fetch_execution', new_callable=AsyncMock) as mock_fetch_exec:
            with patch.object(service, '_fetch_expected_outcome', new_callable=AsyncMock) as mock_fetch_outcome:
                mock_fetch_exec.return_value = mock_execution
                mock_fetch_outcome.return_value = None

                with pytest.raises(ValueError) as exc_info:
                    await service.validate_voice_response(
                        execution_id=execution_id,
                        expected_outcome_id=expected_outcome_id,
                    )

                assert "ExpectedOutcome not found" in str(exc_info.value)
                assert str(expected_outcome_id) in str(exc_info.value)


class TestValidationServiceMetricsAndDefects:
    """Test ValidationService integration with metrics and defect services.

    Note: These tests verify callback integration. The actual callback invocation
    is tested when the service passes validation results to metrics/defect services.
    """

    @pytest.fixture
    def service_with_callbacks(self):
        """Provide ValidationService with mock callbacks."""
        mock_metrics = AsyncMock()
        mock_defect = AsyncMock()
        return ValidationService(
            metrics_recorder=mock_metrics,
            defect_auto_creator=mock_defect,
        ), mock_metrics, mock_defect

    def test_service_stores_callbacks(self, service_with_callbacks):
        """Test that ValidationService stores callback references."""
        service, mock_metrics, mock_defect = service_with_callbacks
        assert service._metrics_recorder is mock_metrics
        assert service._defect_auto_creator is mock_defect


class TestValidationServiceIntegration:
    """Integration tests for ValidationService."""

    @pytest.fixture
    def service(self):
        """Provide ValidationService instance."""
        return ValidationService()

    def test_service_has_required_methods(self, service):
        """Test that service has all required public methods."""
        required_methods = [
            'validate_voice_response',
        ]

        for method_name in required_methods:
            assert hasattr(service, method_name), \
                f"ValidationService should have {method_name} method"
            assert callable(getattr(service, method_name)), \
                f"{method_name} should be callable"

    def test_service_inherits_from_mixins(self, service):
        """Test that service inherits from validation mixins.

        The new ValidationService uses:
        - ValidationHoundifyMixin: Houndify-specific validation (CommandKind, ASR, patterns)
        - ValidationLLMMixin: LLM ensemble validation methods
        """
        from services.validation_houndify import ValidationHoundifyMixin
        from services.validation_llm import ValidationLLMMixin

        assert isinstance(service, ValidationHoundifyMixin)
        assert isinstance(service, ValidationLLMMixin)
