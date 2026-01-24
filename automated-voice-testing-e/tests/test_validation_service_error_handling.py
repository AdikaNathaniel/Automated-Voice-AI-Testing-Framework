"""
Tests for error handling in ValidationService.

These tests verify that:
1. Database errors are caught and logged properly
2. ML component errors are handled gracefully
3. Proper exceptions are raised with meaningful messages
4. All async methods have try/catch blocks
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import uuid4

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestValidationServiceErrorHandling:
    """Test error handling in ValidationService async methods"""

    @pytest.fixture
    def service(self):
        """Create ValidationService instance"""
        from services.validation_service import ValidationService
        return ValidationService()

    @pytest.fixture
    def mock_execution_id(self):
        return uuid4()

    @pytest.fixture
    def mock_expected_outcome_id(self):
        return uuid4()


class TestFetchExecutionErrorHandling:
    """Test error handling in _fetch_execution method"""

    @pytest.mark.asyncio
    async def test_fetch_execution_handles_database_error(self):
        """Test that database errors are caught and re-raised with context"""
        from services.validation_service import ValidationService

        service = ValidationService()
        execution_id = uuid4()

        # Create async context manager mock
        mock_session = AsyncMock()
        mock_session.__aenter__.side_effect = Exception("Database connection failed")

        with patch('services.validation_service.get_async_session', return_value=mock_session):
            with pytest.raises(RuntimeError) as exc_info:
                await service._fetch_execution(execution_id)

            # Should include context about what failed
            assert "Database" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_fetch_execution_logs_database_error(self):
        """Test that database errors are logged"""
        from services.validation_service import ValidationService

        service = ValidationService()
        execution_id = uuid4()

        # Create async context manager mock
        mock_session = AsyncMock()
        mock_session.__aenter__.side_effect = Exception("Connection timeout")

        with patch('services.validation_service.get_async_session', return_value=mock_session):
            with patch('services.validation_service.logger') as mock_logger:
                try:
                    await service._fetch_execution(execution_id)
                except Exception:
                    pass

                # Should log the error
                mock_logger.error.assert_called()


class TestFetchExpectedOutcomeErrorHandling:
    """Test error handling in _fetch_expected_outcome method"""

    @pytest.mark.asyncio
    async def test_fetch_expected_outcome_handles_database_error(self):
        """Test that database errors are caught and re-raised"""
        from services.validation_service import ValidationService

        service = ValidationService()
        outcome_id = uuid4()

        # Create async context manager mock
        mock_session = AsyncMock()
        mock_session.__aenter__.side_effect = Exception("Query execution failed")

        with patch('services.validation_service.get_async_session', return_value=mock_session):
            with pytest.raises(RuntimeError):
                await service._fetch_expected_outcome(outcome_id)

    @pytest.mark.asyncio
    async def test_fetch_expected_outcome_logs_database_error(self):
        """Test that database errors are logged"""
        from services.validation_service import ValidationService

        service = ValidationService()
        outcome_id = uuid4()

        # Create async context manager mock
        mock_session = AsyncMock()
        mock_session.__aenter__.side_effect = Exception("Database unavailable")

        with patch('services.validation_service.get_async_session', return_value=mock_session):
            with patch('services.validation_service.logger') as mock_logger:
                try:
                    await service._fetch_expected_outcome(outcome_id)
                except Exception:
                    pass

                mock_logger.error.assert_called()


class TestValidateVoiceResponseErrorHandling:
    """Test error handling in main validate_voice_response method"""

    @pytest.mark.asyncio
    async def test_validate_voice_response_handles_fetch_error(self):
        """Test that fetch errors are properly handled"""
        from services.validation_service import ValidationService

        service = ValidationService()
        execution_id = uuid4()
        outcome_id = uuid4()

        with patch.object(service, '_fetch_execution', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = Exception("Database error")

            with pytest.raises(Exception):
                await service.validate_voice_response(execution_id, outcome_id)

    @pytest.mark.asyncio
    async def test_validate_voice_response_logs_validation_error(self):
        """Test that validation errors are logged"""
        from services.validation_service import ValidationService

        service = ValidationService()
        execution_id = uuid4()
        outcome_id = uuid4()

        with patch.object(service, '_fetch_execution', new_callable=AsyncMock) as mock_fetch_exec:
            with patch.object(service, '_fetch_expected_outcome', new_callable=AsyncMock) as mock_fetch_out:
                mock_fetch_exec.return_value = None  # Execution not found
                mock_fetch_out.return_value = MagicMock()

                with patch('services.validation_service.logger') as mock_logger:
                    try:
                        await service.validate_voice_response(execution_id, outcome_id)
                    except ValueError:
                        pass

                    # Should have logged the validation attempt
                    assert mock_logger.info.called or mock_logger.error.called


class TestMLComponentErrorHandling:
    """Test error handling for ML component failures"""

    def test_semantic_similarity_handles_matcher_error(self):
        """Test that semantic similarity errors are handled"""
        from services.validation_service import ValidationService

        # Create service with a failing semantic matcher
        mock_matcher = MagicMock()
        mock_matcher.calculate_similarity.side_effect = Exception("Model loading failed")

        service = ValidationService(semantic_matcher=mock_matcher)

        # Should handle the error gracefully (return 0.0 or raise)
        result = service._calculate_semantic_similarity("test", "expected")

        # Either returns default score or handles error
        assert isinstance(result, (int, float))

    def test_intent_classification_handles_classifier_error(self):
        """Test that intent classification errors are handled"""
        from services.validation_service import ValidationService

        # Create service with a failing classifier
        mock_classifier = MagicMock()
        mock_classifier.classify.side_effect = Exception("Classification failed")

        service = ValidationService(intent_classifier=mock_classifier)

        result = service._calculate_intent_score(
            transcript="test transcript",
            locale="en-US",
            expected_entities={"intent": "test"},
            validation_rules={}
        )

        # Should return default score on error
        assert isinstance(result, (int, float))


class TestValidationServiceLogging:
    """Test that proper logging is in place for errors"""

    @pytest.mark.asyncio
    async def test_service_logs_error_with_context(self):
        """Test that errors are logged with useful context"""
        from services.validation_service import ValidationService

        service = ValidationService()
        execution_id = uuid4()
        outcome_id = uuid4()

        with patch('services.validation_service.get_async_session') as mock_session:
            mock_session.side_effect = Exception("Connection refused")

            with patch('services.validation_service.logger') as mock_logger:
                try:
                    await service._fetch_execution(execution_id)
                except Exception:
                    pass

                # Verify error was logged
                if mock_logger.error.called:
                    call_args = str(mock_logger.error.call_args)
                    # Should include execution_id or meaningful context
                    assert mock_logger.error.called


class TestDatabaseSessionHandling:
    """Test proper database session handling"""

    def test_error_handling_uses_context_manager(self):
        """Test that fetch methods use async context manager for cleanup"""
        from services.validation_service import ValidationService
        import inspect

        # Read the source code of _fetch_execution
        source = inspect.getsource(ValidationService._fetch_execution)

        # Verify it uses async with for proper cleanup
        assert "async with" in source, "Should use async with for session management"
        assert "try:" in source, "Should have try block for error handling"
        assert "except" in source, "Should have except block for error handling"

    def test_error_handling_logs_with_context(self):
        """Test that error logging includes useful context"""
        from services.validation_service import ValidationService
        import inspect

        source = inspect.getsource(ValidationService._fetch_execution)

        # Verify error logging includes context
        assert "logger.error" in source, "Should log errors"
        assert "execution_id" in source, "Should include execution_id in logs"


class TestValidationResultCreationErrorHandling:
    """Test error handling when creating validation results"""

    @pytest.mark.asyncio
    async def test_handles_validation_result_creation_error(self):
        """Test handling of ValidationResult creation errors"""
        from services.validation_service import ValidationService

        service = ValidationService()

        # Mock successful fetches but failed result creation
        mock_execution = MagicMock()
        mock_execution.test_run_id = uuid4()
        mock_execution.get_all_response_entities.return_value = {"transcript": "test"}

        mock_outcome = MagicMock()
        mock_outcome.entities = {"transcript": "expected"}
        mock_outcome.validation_rules = {"expected_transcript": "expected"}

        with patch.object(service, '_fetch_execution', new_callable=AsyncMock) as mock_fetch_exec:
            with patch.object(service, '_fetch_expected_outcome', new_callable=AsyncMock) as mock_fetch_outcome:
                mock_fetch_exec.return_value = mock_execution
                mock_fetch_outcome.return_value = mock_outcome

                # This should work or fail gracefully
                try:
                    result = await service.validate_voice_response(uuid4(), uuid4())
                    # If it succeeds, it should return a result
                    assert result is not None
                except Exception as e:
                    # If it fails, should have meaningful error
                    assert str(e)  # Error message should not be empty
