"""
Tests for Houndify/SoundHound Integration

This module contains comprehensive tests for the Houndify (SoundHound) integration,
focusing on the MockHoundifyClient for testing purposes.

Test Coverage:
- HoundifyResponse model validation
- HoundifyRequestInfo model validation
- HoundifyError exception handling
- MockHoundifyClient initialization
- text_query method (success, errors, latency, patterns)
- voice_query method (success, errors, latency)
- Pattern matching logic
- Call history tracking
- Conversation state management

All tests use the mock client to avoid real API calls.
"""

import pytest

# Import Houndify components
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from integrations.houndify.models import (
    HoundifyResponse,
    HoundifyRequestInfo,
    HoundifyError
)
from integrations.houndify.mock_client import MockHoundifyClient


# ========== HoundifyResponse Model Tests ==========

class TestHoundifyResponseModel:
    """Test suite for HoundifyResponse Pydantic model"""

    def test_create_valid_response(self):
        """Test creating a valid HoundifyResponse"""
        # Arrange & Act
        response = HoundifyResponse(
            raw_transcription="what's the weather",
            formatted_transcription="What's the weather?",
            command_kind="WeatherQuery",
            command_results=[{"Temperature": 22, "Condition": "Sunny"}],
            entities={"Location": "Paris"},
            confidence=0.95,
            spoken_response="It's sunny and 22 degrees",
            request_id="req123",
            all_results={"AllResults": []}
        )

        # Assert
        assert response.raw_transcription == "what's the weather"
        assert response.formatted_transcription == "What's the weather?"
        assert response.command_kind == "WeatherQuery"
        assert response.confidence == 0.95
        assert response.request_id == "req123"

    def test_response_with_optional_fields(self):
        """Test response with all optional fields populated"""
        # Arrange & Act
        response = HoundifyResponse(
            raw_transcription="test",
            formatted_transcription="Test",
            command_kind="TestCommand",
            command_results=[],
            entities={},
            confidence=1.0,
            spoken_response="Test response",
            spoken_response_long="This is a longer test response",
            conversation_state={"state": "active"},
            response_audio_bytes=b"audio_data",
            response_time_ms=150,
            request_id="req456",
            all_results={}
        )

        # Assert
        assert response.spoken_response_long == "This is a longer test response"
        assert response.conversation_state == {"state": "active"}
        assert response.response_audio_bytes == b"audio_data"
        assert response.response_time_ms == 150

    def test_response_without_optional_fields(self):
        """Test response with optional fields as None"""
        # Arrange & Act
        response = HoundifyResponse(
            raw_transcription="test",
            formatted_transcription="Test",
            command_kind="TestCommand",
            command_results=[],
            entities={},
            confidence=1.0,
            spoken_response="Test",
            request_id="req789",
            all_results={}
        )

        # Assert
        assert response.spoken_response_long is None
        assert response.conversation_state is None
        assert response.response_audio_bytes is None
        assert response.response_time_ms is None


# ========== HoundifyRequestInfo Model Tests ==========

class TestHoundifyRequestInfoModel:
    """Test suite for HoundifyRequestInfo Pydantic model"""

    def test_create_valid_request_info(self):
        """Test creating valid request info with all fields"""
        # Arrange & Act
        request_info = HoundifyRequestInfo(
            user_id="user123",
            request_id="req456",
            latitude=37.7749,
            longitude=-122.4194,
            partial_transcripts_desired=True
        )

        # Assert
        assert request_info.user_id == "user123"
        assert request_info.request_id == "req456"
        assert request_info.latitude == 37.7749
        assert request_info.longitude == -122.4194
        assert request_info.partial_transcripts_desired is True

    def test_request_info_without_location(self):
        """Test request info without optional location fields"""
        # Arrange & Act
        request_info = HoundifyRequestInfo(
            user_id="user789",
            request_id="req123"
        )

        # Assert
        assert request_info.user_id == "user789"
        assert request_info.request_id == "req123"
        assert request_info.latitude is None
        assert request_info.longitude is None
        assert request_info.partial_transcripts_desired is False

    def test_request_info_partial_transcripts_default(self):
        """Test that partial_transcripts_desired defaults to False"""
        # Arrange & Act
        request_info = HoundifyRequestInfo(
            user_id="user111",
            request_id="req222"
        )

        # Assert
        assert request_info.partial_transcripts_desired is False


# ========== HoundifyError Exception Tests ==========

class TestHoundifyError:
    """Test suite for HoundifyError exception"""

    def test_create_error_with_message_only(self):
        """Test creating HoundifyError with just a message"""
        # Arrange & Act
        error = HoundifyError("Test error message")

        # Assert
        assert error.message == "Test error message"
        assert error.status_code is None
        assert error.response is None
        assert str(error) == "Test error message"

    def test_create_error_with_status_code(self):
        """Test creating HoundifyError with status code"""
        # Arrange & Act
        error = HoundifyError(
            "Rate limit exceeded",
            status_code=429
        )

        # Assert
        assert error.message == "Rate limit exceeded"
        assert error.status_code == 429
        assert error.response is None

    def test_create_error_with_response(self):
        """Test creating HoundifyError with full response"""
        # Arrange
        response_data = {
            "error": "Invalid request",
            "details": "Missing required parameter"
        }

        # Act
        error = HoundifyError(
            "API request failed",
            status_code=400,
            response=response_data
        )

        # Assert
        assert error.message == "API request failed"
        assert error.status_code == 400
        assert error.response == response_data
        assert error.response["error"] == "Invalid request"

    def test_error_can_be_raised(self):
        """Test that HoundifyError can be raised and caught"""
        # Arrange & Act & Assert
        with pytest.raises(HoundifyError) as exc_info:
            raise HoundifyError("Test exception")

        assert exc_info.value.message == "Test exception"


# ========== MockHoundifyClient Initialization Tests ==========

class TestMockHoundifyClientInit:
    """Test suite for MockHoundifyClient initialization"""

    def test_init_with_defaults(self):
        """Test initialization with default parameters"""
        # Arrange & Act
        client = MockHoundifyClient()

        # Assert
        assert client.response_patterns == {}
        assert client.error_rate == 0.0
        assert client.latency_ms == 0
        # client_id and client_key are optional (None by default)
        assert client.client_id is None
        assert client.client_key is None

    def test_init_with_response_patterns(self):
        """Test initialization with custom response patterns"""
        # Arrange
        patterns = {
            "weather": {
                "command_kind": "WeatherQuery",
                "spoken_response": "It's sunny"
            },
            "time": {
                "command_kind": "TimeQuery",
                "spoken_response": "It's 3 PM"
            }
        }

        # Act
        client = MockHoundifyClient(response_patterns=patterns)

        # Assert
        assert client.response_patterns == patterns
        assert "weather" in client.response_patterns
        assert "time" in client.response_patterns

    def test_init_with_error_rate(self):
        """Test initialization with custom error rate"""
        # Arrange & Act
        client = MockHoundifyClient(error_rate=0.25)

        # Assert
        assert client.error_rate == 0.25

    def test_init_error_rate_invalid_negative_raises(self):
        """Test that negative error rate raises ValueError"""
        # Arrange & Act & Assert
        with pytest.raises(ValueError) as exc_info:
            MockHoundifyClient(error_rate=-0.5)
        assert "error_rate must be between 0.0 and 1.0" in str(exc_info.value)

    def test_init_error_rate_invalid_above_one_raises(self):
        """Test that error rate > 1.0 raises ValueError"""
        # Arrange & Act & Assert
        with pytest.raises(ValueError) as exc_info:
            MockHoundifyClient(error_rate=1.5)
        assert "error_rate must be between 0.0 and 1.0" in str(exc_info.value)

    def test_init_with_latency(self):
        """Test initialization with custom latency"""
        # Arrange & Act
        client = MockHoundifyClient(latency_ms=100)

        # Assert
        assert client.latency_ms == 100

    def test_init_latency_invalid_negative_raises(self):
        """Test that negative latency raises ValueError"""
        # Arrange & Act & Assert
        with pytest.raises(ValueError) as exc_info:
            MockHoundifyClient(latency_ms=-50)
        assert "latency_ms must be non-negative" in str(exc_info.value)


# ========== MockHoundifyClient text_query Tests ==========

class TestMockHoundifyClientTextQuery:
    """Test suite for MockHoundifyClient.text_query method"""

    @pytest.mark.asyncio
    async def test_text_query_success(self):
        """Test successful text query"""
        # Arrange
        client = MockHoundifyClient()
        query = "what's the weather?"
        user_id = "user123"
        request_id = "req456"

        # Act
        result = await client.text_query(
            query, user_id, request_id,
            request_info={"LanguageCode": "en-US"}
        )

        # Assert
        assert result["Status"] == "OK"
        assert result["NumToReturn"] == 1
        assert len(result["AllResults"]) == 1
        # RawTranscription is lowercased in implementation
        assert result["AllResults"][0]["RawTranscription"] == query.lower()
        assert result["AllResults"][0]["FormattedTranscription"] == query

    @pytest.mark.asyncio
    async def test_text_query_with_pattern_match(self):
        """Test text query with pattern matching returns custom response"""
        # Arrange - pattern response is returned directly when matched
        patterns = {
            "weather": {
                "Status": "OK",
                "NumToReturn": 1,
                "AllResults": [{
                    "CommandKind": "WeatherQuery",
                    "SpokenResponse": "It's sunny and 72 degrees",
                    "Entities": {"Location": "New York"}
                }]
            }
        }
        client = MockHoundifyClient(response_patterns=patterns)

        # Act
        result = await client.text_query(
            "what's the weather in New York?",
            "user123",
            "req456"
        )

        # Assert - pattern response returned directly
        assert result["AllResults"][0]["CommandKind"] == "WeatherQuery"
        assert result["AllResults"][0]["SpokenResponse"] == "It's sunny and 72 degrees"
        assert result["AllResults"][0]["Entities"] == {"Location": "New York"}

    @pytest.mark.asyncio
    async def test_text_query_no_pattern_match(self):
        """Test text query with no pattern match returns default response"""
        # Arrange
        patterns = {"weather": {"command_kind": "WeatherQuery"}}
        client = MockHoundifyClient(response_patterns=patterns)
        query = "play some music"

        # Act
        result = await client.text_query(
            query, "user123", "req456",
            request_info={"LanguageCode": "en-US"}
        )

        # Assert - music query infers MusicCommand
        assert result["AllResults"][0]["CommandKind"] == "MusicCommand"
        assert "music" in result["AllResults"][0]["SpokenResponse"].lower()

    @pytest.mark.asyncio
    async def test_text_query_returns_valid_structure(self):
        """Test that text_query returns valid response structure"""
        # Arrange
        client = MockHoundifyClient()
        query = "test query"
        user_id = "user789"
        request_id = "req123"

        # Act
        result = await client.text_query(
            query, user_id, request_id,
            request_info={"LanguageCode": "en-US"}
        )

        # Assert - verify standard response structure
        assert "Status" in result
        assert "AllResults" in result
        assert result["userId"] == user_id
        assert result["requestId"] == request_id

    @pytest.mark.asyncio
    async def test_text_query_with_request_info(self):
        """Test text query with additional request info"""
        # Arrange
        client = MockHoundifyClient()
        request_info = {"Latitude": 37.7749, "Longitude": -122.4194, "LanguageCode": "en-US"}

        # Act
        result = await client.text_query(
            "test",
            "user123",
            "req456",
            request_info=request_info
        )

        # Assert - request info doesn't change response structure
        assert result["Status"] == "OK"

    @pytest.mark.asyncio
    async def test_text_query_simulates_latency(self):
        """Test that text_query simulates configured latency"""
        # Arrange
        client = MockHoundifyClient(latency_ms=100)

        # Act
        import time
        start = time.time()
        await client.text_query(
            "test", "user123", "req456",
            request_info={"LanguageCode": "en-US"}
        )
        duration_ms = (time.time() - start) * 1000

        # Assert
        assert duration_ms >= 100  # Should take at least 100ms

    @pytest.mark.asyncio
    async def test_text_query_error_simulation(self):
        """Test that text_query raises errors based on error_rate"""
        # Arrange
        from integrations.houndify.mock_client import MockHoundifyError
        client = MockHoundifyClient(error_rate=1.0)  # 100% error rate

        # Act & Assert
        with pytest.raises(MockHoundifyError) as exc_info:
            await client.text_query("test", "user123", "req456")

        assert "Simulated Houndify API error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_text_query_error_message_content(self):
        """Test that simulated errors have expected message"""
        # Arrange
        from integrations.houndify.mock_client import MockHoundifyError
        client = MockHoundifyClient(error_rate=1.0)

        # Act & Assert
        with pytest.raises(MockHoundifyError) as exc_info:
            await client.text_query("test query", "user123", "req456")

        assert "Simulated" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_text_query_multiple_calls_work(self):
        """Test that multiple calls work correctly"""
        # Arrange
        client = MockHoundifyClient()
        request_info = {"LanguageCode": "en-US"}

        # Act
        result1 = await client.text_query("query 1", "user1", "req1", request_info=request_info)
        result2 = await client.text_query("query 2", "user2", "req2", request_info=request_info)
        result3 = await client.text_query("query 3", "user3", "req3", request_info=request_info)

        # Assert - all return valid responses
        assert result1["Status"] == "OK"
        assert result2["Status"] == "OK"
        assert result3["Status"] == "OK"


# ========== MockHoundifyClient voice_query Tests ==========

class TestMockHoundifyClientVoiceQuery:
    """Test suite for MockHoundifyClient.voice_query method"""

    @pytest.mark.asyncio
    async def test_voice_query_success(self):
        """Test successful voice query"""
        # Arrange
        client = MockHoundifyClient()
        audio_data = b"fake_audio_data"
        user_id = "user123"
        request_id = "req456"

        # Act - voice query uses Prompt from request_info for response
        result = await client.voice_query(
            audio_data, user_id, request_id,
            request_info={"LanguageCode": "en-US"}
        )

        # Assert
        assert result["Status"] == "OK"
        assert result["NumToReturn"] == 1
        assert len(result["AllResults"]) == 1
        # Without Prompt in request_info, RawTranscription is empty string lowercased
        assert "RawTranscription" in result["AllResults"][0]

    @pytest.mark.asyncio
    async def test_voice_query_returns_valid_structure(self):
        """Test that voice_query returns valid response structure"""
        # Arrange
        client = MockHoundifyClient()
        audio_data = b"audio_bytes"
        user_id = "user789"
        request_id = "req123"

        # Act
        result = await client.voice_query(
            audio_data, user_id, request_id,
            request_info={"LanguageCode": "en-US"}
        )

        # Assert
        assert "Status" in result
        assert "AllResults" in result
        assert result["userId"] == user_id
        assert result["requestId"] == request_id

    @pytest.mark.asyncio
    async def test_voice_query_with_request_info(self):
        """Test voice query with additional request info"""
        # Arrange
        client = MockHoundifyClient()
        request_info = {"Latitude": 40.7128, "Longitude": -74.0060, "Prompt": "hello", "LanguageCode": "en-US"}

        # Act
        result = await client.voice_query(
            b"audio",
            "user123",
            "req456",
            request_info=request_info
        )

        # Assert
        assert result["Status"] == "OK"

    @pytest.mark.asyncio
    async def test_voice_query_uses_prompt_from_request_info(self):
        """Test voice query uses Prompt from request_info"""
        # Arrange
        client = MockHoundifyClient()
        request_info = {"Prompt": "what's the weather?", "LanguageCode": "en-US"}

        # Act
        result = await client.voice_query(
            b"audio",
            "user123",
            "req456",
            request_info=request_info
        )

        # Assert - prompt is used for transcription
        assert result["AllResults"][0]["FormattedTranscription"] == "what's the weather?"

    @pytest.mark.asyncio
    async def test_voice_query_no_minimum_latency(self):
        """Test that voice_query uses configured latency"""
        # Arrange
        client = MockHoundifyClient(latency_ms=0)  # No configured latency

        # Act
        import time
        start = time.time()
        await client.voice_query(
            b"audio", "user123", "req456",
            request_info={"LanguageCode": "en-US"}
        )
        duration_ms = (time.time() - start) * 1000

        # Assert - no minimum latency required, should be fast
        assert duration_ms < 1000  # Just verify it doesn't hang

    @pytest.mark.asyncio
    async def test_voice_query_uses_max_latency(self):
        """Test that voice_query uses max(configured, 50ms) latency"""
        # Arrange
        client = MockHoundifyClient(latency_ms=100)

        # Act
        import time
        start = time.time()
        await client.voice_query(
            b"audio", "user123", "req456",
            request_info={"LanguageCode": "en-US"}
        )
        duration_ms = (time.time() - start) * 1000

        # Assert
        assert duration_ms >= 100  # Should use configured 100ms

    @pytest.mark.asyncio
    async def test_voice_query_error_simulation(self):
        """Test that voice_query raises errors based on error_rate"""
        # Arrange
        from integrations.houndify.mock_client import MockHoundifyError
        client = MockHoundifyClient(error_rate=1.0)  # 100% error rate

        # Act & Assert
        with pytest.raises(MockHoundifyError) as exc_info:
            await client.voice_query(b"audio", "user123", "req456")

        assert "Simulated Houndify API error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_voice_query_error_message(self):
        """Test that simulated voice errors have expected message"""
        # Arrange
        from integrations.houndify.mock_client import MockHoundifyError
        client = MockHoundifyClient(error_rate=1.0)
        audio_data = b"test_audio_data_bytes"

        # Act & Assert
        with pytest.raises(MockHoundifyError) as exc_info:
            await client.voice_query(audio_data, "user123", "req456")

        assert "Simulated" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_voice_query_with_pattern_match(self):
        """Test voice query with pattern matching from Prompt"""
        # Arrange - pattern matched against Prompt in request_info
        patterns = {
            "hello": {
                "Status": "OK",
                "NumToReturn": 1,
                "AllResults": [{
                    "CommandKind": "VoiceTestCommand",
                    "SpokenResponse": "Voice test response"
                }]
            }
        }
        client = MockHoundifyClient(response_patterns=patterns)

        # Act - provide Prompt that matches pattern
        result = await client.voice_query(
            b"audio", "user123", "req456",
            request_info={"Prompt": "hello world"}
        )

        # Assert
        assert result["AllResults"][0]["CommandKind"] == "VoiceTestCommand"
        assert result["AllResults"][0]["SpokenResponse"] == "Voice test response"

    @pytest.mark.asyncio
    async def test_voice_query_command_kind_inferred(self):
        """Test that voice query infers CommandKind from Prompt"""
        # Arrange
        client = MockHoundifyClient()

        # Act - weather query
        result = await client.voice_query(
            b"audio", "user123", "req456",
            request_info={"Prompt": "what's the weather?", "LanguageCode": "en-US"}
        )

        # Assert - infers WeatherCommand
        assert result["AllResults"][0]["CommandKind"] == "WeatherCommand"


# ========== MockHoundifyClient _match_pattern Tests ==========

class TestMockHoundifyClientMatchPattern:
    """Test suite for MockHoundifyClient._match_pattern method"""

    def test_match_pattern_exact_match(self):
        """Test pattern matching with exact keyword"""
        # Arrange
        patterns = {"weather": {"temp": 72}}
        client = MockHoundifyClient(response_patterns=patterns)

        # Act
        result = client._match_pattern("weather")

        # Assert
        assert result == {"temp": 72}

    def test_match_pattern_case_insensitive(self):
        """Test that pattern matching is case-insensitive"""
        # Arrange
        patterns = {"WEATHER": {"temp": 72}}
        client = MockHoundifyClient(response_patterns=patterns)

        # Act
        result = client._match_pattern("what's the weather?")

        # Assert
        assert result == {"temp": 72}

    def test_match_pattern_substring(self):
        """Test pattern matching finds keywords in query substring"""
        # Arrange
        patterns = {"time": {"hour": 15}}
        client = MockHoundifyClient(response_patterns=patterns)

        # Act
        result = client._match_pattern("what time is it in Paris?")

        # Assert
        assert result == {"hour": 15}

    def test_match_pattern_no_match(self):
        """Test that no pattern match returns None"""
        # Arrange
        patterns = {"weather": {"temp": 72}}
        client = MockHoundifyClient(response_patterns=patterns)

        # Act
        result = client._match_pattern("unrelated query")

        # Assert
        assert result is None

    def test_match_pattern_multiple_patterns_first_match(self):
        """Test that multiple patterns return first match"""
        # Arrange
        patterns = {
            "weather": {"type": "weather"},
            "temperature": {"type": "temp"}
        }
        client = MockHoundifyClient(response_patterns=patterns)

        # Act - "weather" appears first in patterns dict
        result = client._match_pattern("what's the weather and temperature?")

        # Assert - Should match first pattern found
        assert "type" in result

    def test_match_pattern_empty_query(self):
        """Test pattern matching with empty query returns None"""
        # Arrange
        patterns = {"weather": {"temp": 72}}
        client = MockHoundifyClient(response_patterns=patterns)

        # Act
        result = client._match_pattern("")

        # Assert
        assert result is None

    def test_match_pattern_empty_patterns(self):
        """Test pattern matching with no patterns configured returns None"""
        # Arrange
        client = MockHoundifyClient(response_patterns={})

        # Act
        result = client._match_pattern("any query")

        # Assert
        assert result is None


# ========== Conversation State Tests ==========

class TestMockHoundifyClientConversationState:
    """Test suite for conversation state management"""

    @pytest.mark.asyncio
    async def test_text_query_includes_conversation_state(self):
        """Test that text query includes conversation state in response"""
        # Arrange
        client = MockHoundifyClient()

        # Act
        result = await client.text_query(
            "test", "user123", "req456",
            request_info={"LanguageCode": "en-US"}
        )

        # Assert - conversation state always included per user
        assert result["AllResults"][0]["ConversationState"] is not None
        assert "TurnCount" in result["AllResults"][0]["ConversationState"]

    @pytest.mark.asyncio
    async def test_text_query_conversation_state_tracks_turns(self):
        """Test that conversation state tracks turn count"""
        # Arrange
        client = MockHoundifyClient()
        request_info = {"LanguageCode": "en-US"}

        # Act - make multiple calls
        await client.text_query("test 1", "user123", "req1", request_info=request_info)
        result = await client.text_query("test 2", "user123", "req2", request_info=request_info)

        # Assert - turn count incremented
        assert result["AllResults"][0]["ConversationState"]["TurnCount"] == 2

    @pytest.mark.asyncio
    async def test_voice_query_includes_conversation_state(self):
        """Test that voice query includes conversation state in response"""
        # Arrange
        client = MockHoundifyClient()

        # Act
        result = await client.voice_query(
            b"audio", "user123", "req456",
            request_info={"LanguageCode": "en-US"}
        )

        # Assert
        assert result["AllResults"][0]["ConversationState"] is not None

    @pytest.mark.asyncio
    async def test_voice_query_with_incoming_conversation_state(self):
        """Test voice query with incoming conversation state from request"""
        # Arrange
        client = MockHoundifyClient()
        request_info = {
            "Prompt": "hello",
            "LanguageCode": "en-US",
            "ConversationState": {"previous": "state", "CollectedSlots": {"slot1": "value1"}}
        }

        # Act
        result = await client.voice_query(
            b"audio", "user123", "req456",
            request_info=request_info
        )

        # Assert - conversation state preserved and updated
        assert result["AllResults"][0]["ConversationState"] is not None


# ========== Integration Tests ==========

class TestMockHoundifyClientIntegration:
    """Integration tests for MockHoundifyClient"""

    @pytest.mark.asyncio
    async def test_mixed_text_and_voice_queries(self):
        """Test that text and voice queries can be mixed"""
        # Arrange
        client = MockHoundifyClient()
        request_info = {"LanguageCode": "en-US"}

        # Act
        result1 = await client.text_query("test text", "user1", "req1", request_info=request_info)
        result2 = await client.voice_query(b"audio", "user1", "req2", request_info=request_info)

        # Assert - both return valid responses
        assert result1["Status"] == "OK"
        assert result2["Status"] == "OK"

    @pytest.mark.asyncio
    async def test_error_rate_statistical_behavior(self):
        """Test that error_rate produces expected error frequency (statistical)"""
        # Arrange
        from integrations.houndify.mock_client import MockHoundifyError
        client = MockHoundifyClient(error_rate=0.5)  # 50% error rate
        num_calls = 100
        errors = 0
        request_info = {"LanguageCode": "en-US"}

        # Act
        for i in range(num_calls):
            try:
                await client.text_query(f"query{i}", f"user{i}", f"req{i}", request_info=request_info)
            except MockHoundifyError:
                errors += 1

        # Assert
        # With 50% error rate and 100 calls, expect 30-70 errors (statistical range)
        assert 30 <= errors <= 70

    @pytest.mark.asyncio
    async def test_client_with_all_features(self):
        """Test client with all features enabled (patterns, latency)"""
        # Arrange - use fully structured pattern response
        patterns = {
            "weather": {
                "Status": "OK",
                "NumToReturn": 1,
                "AllResults": [{
                    "CommandKind": "WeatherQuery",
                    "SpokenResponse": "Sunny",
                    "Entities": {"Location": "NYC"}
                }]
            }
        }
        client = MockHoundifyClient(
            response_patterns=patterns,
            error_rate=0.0,  # No errors for this test
            latency_ms=50
        )

        # Act
        import time
        start = time.time()
        result = await client.text_query(
            "what's the weather in NYC?",
            "user123",
            "req456",
            request_info={"Latitude": 40.7128}
        )
        duration_ms = (time.time() - start) * 1000

        # Assert
        # Response structure
        assert result["AllResults"][0]["CommandKind"] == "WeatherQuery"
        assert result["AllResults"][0]["SpokenResponse"] == "Sunny"
        assert result["AllResults"][0]["Entities"] == {"Location": "NYC"}

        # Latency
        assert duration_ms >= 50
