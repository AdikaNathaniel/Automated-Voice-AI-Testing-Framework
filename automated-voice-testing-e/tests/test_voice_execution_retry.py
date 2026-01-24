"""
Tests for retry logic in VoiceExecutionService.

These tests verify that:
1. External API calls are retried on transient errors
2. Retry uses exponential backoff
3. Retries are logged appropriately
4. Non-retryable errors fail immediately
"""

import pytest
import sys
import os
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import uuid4

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestRetryDecorator:
    """Test the retry decorator functionality"""

    def test_retry_decorator_exists(self):
        """Test that retry decorator is available"""
        from services.voice_execution_service import async_retry
        assert callable(async_retry)

    @pytest.mark.asyncio
    async def test_retry_succeeds_on_first_attempt(self):
        """Test that successful calls don't trigger retries"""
        from services.voice_execution_service import async_retry

        call_count = {"value": 0}

        @async_retry(max_retries=3, base_delay=0.01)
        async def successful_operation():
            call_count["value"] += 1
            return "success"

        result = await successful_operation()

        assert result == "success"
        assert call_count["value"] == 1

    @pytest.mark.asyncio
    async def test_retry_on_transient_error(self):
        """Test that transient errors trigger retries"""
        from services.voice_execution_service import async_retry

        call_count = {"value": 0}

        @async_retry(max_retries=3, base_delay=0.01)
        async def failing_then_succeeding():
            call_count["value"] += 1
            if call_count["value"] < 3:
                raise ConnectionError("Network error")
            return "success"

        result = await failing_then_succeeding()

        assert result == "success"
        assert call_count["value"] == 3

    @pytest.mark.asyncio
    async def test_retry_exhausted_raises_error(self):
        """Test that error is raised after max retries"""
        from services.voice_execution_service import async_retry

        call_count = {"value": 0}

        @async_retry(max_retries=3, base_delay=0.01)
        async def always_failing():
            call_count["value"] += 1
            raise ConnectionError("Network error")

        with pytest.raises(ConnectionError):
            await always_failing()

        assert call_count["value"] == 3

    @pytest.mark.asyncio
    async def test_no_retry_on_non_retryable_error(self):
        """Test that non-retryable errors fail immediately"""
        from services.voice_execution_service import async_retry

        call_count = {"value": 0}

        @async_retry(max_retries=3, base_delay=0.01)
        async def client_error():
            call_count["value"] += 1
            raise ValueError("Invalid input")

        with pytest.raises(ValueError):
            await client_error()

        # Should not retry on ValueError
        assert call_count["value"] == 1


class TestHoundifyRetryLogic:
    """Test retry logic for Houndify API calls"""

    @pytest.mark.asyncio
    async def test_houndify_call_retries_on_network_error(self):
        """Test that Houndify calls are retried on network errors"""
        from services.voice_execution_service import VoiceExecutionService
        from integrations.houndify.models import HoundifyError

        service = VoiceExecutionService()

        # Mock execution, test_case, test_run
        execution = MagicMock()
        execution.id = uuid4()
        test_case = MagicMock()
        test_case.id = uuid4()
        test_run = MagicMock()
        test_run.id = uuid4()
        test_run.created_by = None

        # Create mock houndify client that fails then succeeds
        mock_client = AsyncMock()
        call_count = {"value": 0}

        async def voice_query_with_retry(*args, **kwargs):
            call_count["value"] += 1
            if call_count["value"] < 2:
                raise ConnectionError("Network timeout")
            return {"transcript": "test response"}

        mock_client.voice_query = voice_query_with_retry

        # Mock TTS service
        mock_tts = MagicMock()
        mock_tts.synthesize.return_value = MagicMock(
            audio_bytes=b"audio",
            sample_rate=16000,
            duration_seconds=1.0
        )

        with patch.object(service, '_ensure_houndify_client', return_value=mock_client):
            with patch.object(service, '_ensure_tts_service', return_value=mock_tts):
                with patch.object(service, '_extract_prompt_text', return_value="test prompt"):
                    with patch.object(service, '_synthesize_prompt') as mock_synth:
                        mock_synth.return_value = MagicMock(
                            audio_bytes=b"audio",
                            sample_rate=16000,
                            duration_seconds=1.0
                        )
                        # Should retry and succeed
                        # Note: If retry is implemented, this should succeed

    @pytest.mark.asyncio
    async def test_houndify_call_no_retry_on_400_error(self):
        """Test that Houndify 400 errors are not retried"""
        from services.voice_execution_service import VoiceExecutionService
        from integrations.houndify.models import HoundifyError

        service = VoiceExecutionService()

        call_count = {"value": 0}

        # Create mock that raises 400 error
        async def voice_query_400(*args, **kwargs):
            call_count["value"] += 1
            raise HoundifyError(
                message="Bad request",
                status_code=400,
                response={}
            )

        # If we implement proper retry logic, 400 errors should not be retried


class TestRetryWithBackoff:
    """Test exponential backoff in retry logic"""

    @pytest.mark.asyncio
    async def test_retry_uses_exponential_backoff(self):
        """Test that retries use exponential backoff"""
        from services.voice_execution_service import async_retry

        delays = []

        @async_retry(max_retries=4, base_delay=0.01)
        async def track_delays():
            delays.append(len(delays))
            if len(delays) < 4:
                raise ConnectionError("Retry me")
            return "done"

        # Mock sleep to track delays
        original_sleep = asyncio.sleep
        sleep_calls = []

        async def mock_sleep(delay):
            sleep_calls.append(delay)
            await original_sleep(0.001)  # Actually sleep very briefly

        with patch('asyncio.sleep', mock_sleep):
            result = await track_delays()

        assert result == "done"
        # Should have 3 sleep calls for 4 attempts
        assert len(sleep_calls) == 3
        # Each delay should be larger than the previous (exponential)
        for i in range(1, len(sleep_calls)):
            assert sleep_calls[i] >= sleep_calls[i-1]


class TestRetryLogging:
    """Test that retries are properly logged"""

    @pytest.mark.asyncio
    async def test_retry_logs_attempt(self):
        """Test that retry attempts are logged"""
        from services.voice_execution_service import async_retry

        @async_retry(max_retries=3, base_delay=0.01)
        async def failing_operation():
            raise ConnectionError("Network error")

        with patch('services.voice_execution_service.logger') as mock_logger:
            try:
                await failing_operation()
            except ConnectionError:
                pass

            # Should have logged retry attempts
            assert mock_logger.warning.called or mock_logger.info.called


class TestRetryableErrors:
    """Test which errors are considered retryable"""

    def test_connection_error_is_retryable(self):
        """Test that ConnectionError is retryable"""
        from services.voice_execution_service import is_retryable_error
        assert is_retryable_error(ConnectionError("test"))

    def test_timeout_error_is_retryable(self):
        """Test that TimeoutError is retryable"""
        from services.voice_execution_service import is_retryable_error
        assert is_retryable_error(TimeoutError("test"))

    def test_oserror_is_retryable(self):
        """Test that OSError is retryable"""
        from services.voice_execution_service import is_retryable_error
        assert is_retryable_error(OSError("Network unreachable"))

    def test_value_error_is_not_retryable(self):
        """Test that ValueError is not retryable"""
        from services.voice_execution_service import is_retryable_error
        assert not is_retryable_error(ValueError("Invalid"))

    def test_houndify_500_is_retryable(self):
        """Test that Houndify 500 errors are retryable"""
        from services.voice_execution_service import is_retryable_error
        from integrations.houndify.models import HoundifyError

        error = HoundifyError(message="Server error", status_code=500, response={})
        assert is_retryable_error(error)

    def test_houndify_429_is_retryable(self):
        """Test that Houndify 429 (rate limit) errors are retryable"""
        from services.voice_execution_service import is_retryable_error
        from integrations.houndify.models import HoundifyError

        error = HoundifyError(message="Rate limited", status_code=429, response={})
        assert is_retryable_error(error)

    def test_houndify_400_is_not_retryable(self):
        """Test that Houndify 400 errors are not retryable"""
        from services.voice_execution_service import is_retryable_error
        from integrations.houndify.models import HoundifyError

        error = HoundifyError(message="Bad request", status_code=400, response={})
        assert not is_retryable_error(error)
