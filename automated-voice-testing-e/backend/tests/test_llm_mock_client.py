"""
Tests for the LLM-powered mock Houndify client.

These tests verify:
- Client initialization and configuration
- Response structure matches Houndify format
- CommandKind validation
- Conversation state tracking
- Error simulation
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

from integrations.houndify.llm_mock_client import (
    LLMMockClient,
    ALLOWED_COMMAND_KINDS,
    LLM_RESPONSE_SCHEMA,
    _build_user_prompt,
)
from integrations.houndify.mock_client import MockHoundifyError


class TestLLMMockClientInit:
    """Test LLMMockClient initialization."""

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test-key'}):
            client = LLMMockClient()

        assert client.model == "openai/gpt-4o-mini"
        assert client.temperature == 0.0
        assert client.max_tokens == 256
        assert client.timeout == 30
        assert client.error_rate == 0.0
        assert client.latency_ms == 0
        assert client.base_url == "https://openrouter.ai/api/v1"

    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        client = LLMMockClient(
            api_key="custom-key",
            model="openai/gpt-4o",
            temperature=0.5,
            max_tokens=512,
            timeout=60,
            error_rate=0.1,
            latency_ms=100,
            base_url="https://custom.api/v1",
        )

        assert client.api_key == "custom-key"
        assert client.model == "openai/gpt-4o"
        assert client.temperature == 0.5
        assert client.max_tokens == 512
        assert client.timeout == 60
        assert client.error_rate == 0.1
        assert client.latency_ms == 100
        assert client.base_url == "https://custom.api/v1"

    def test_init_invalid_error_rate(self):
        """Test that invalid error_rate raises ValueError."""
        with pytest.raises(ValueError, match="error_rate must be between"):
            LLMMockClient(api_key="test", error_rate=1.5)

        with pytest.raises(ValueError, match="error_rate must be between"):
            LLMMockClient(api_key="test", error_rate=-0.1)

    def test_init_invalid_latency(self):
        """Test that negative latency raises ValueError."""
        with pytest.raises(ValueError, match="latency_ms must be non-negative"):
            LLMMockClient(api_key="test", latency_ms=-100)


class TestAllowedCommandKinds:
    """Test CommandKind validation."""

    def test_all_command_kinds_present(self):
        """Test that all expected command kinds are defined."""
        expected = [
            "WeatherCommand",
            "MusicCommand",
            "NavigationCommand",
            "PhoneCommand",
            "ClientMatchCommand",
            "NoResultCommand",
            "UnknownCommand",
        ]
        assert ALLOWED_COMMAND_KINDS == expected

    def test_schema_enforces_command_kinds(self):
        """Test that JSON schema enforces CommandKind enum."""
        schema_enum = LLM_RESPONSE_SCHEMA["properties"]["CommandKind"]["enum"]
        assert schema_enum == ALLOWED_COMMAND_KINDS


class TestBuildUserPrompt:
    """Test user prompt building."""

    def test_build_prompt_simple(self):
        """Test building a simple prompt without history."""
        prompt = _build_user_prompt(
            utterance="What's the weather?",
            language="en",
        )

        assert "LANGUAGE: en" in prompt
        assert "USER UTTERANCE: What's the weather?" in prompt
        assert "CONVERSATION HISTORY:" not in prompt

    def test_build_prompt_with_history(self):
        """Test building a prompt with conversation history."""
        history = [
            {"user": "Hello", "ai": "Hi there!"},
            {"user": "How are you?", "ai": "I'm doing well!"},
        ]

        prompt = _build_user_prompt(
            utterance="What's next?",
            language="es",
            conversation_history=history,
        )

        assert "CONVERSATION HISTORY:" in prompt
        assert "Turn 1:" in prompt
        assert "User: Hello" in prompt
        assert "AI: Hi there!" in prompt
        assert "Turn 2:" in prompt
        assert "LANGUAGE: es" in prompt
        assert "USER UTTERANCE: What's next?" in prompt


class TestConversationState:
    """Test conversation state management."""

    def test_get_or_create_conversation_new(self):
        """Test creating a new conversation state."""
        client = LLMMockClient(api_key="test")
        conversation = client._get_or_create_conversation("user123")

        assert "ConversationStateId" in conversation
        assert conversation["ConversationStateId"].startswith("conv_user123_")
        assert conversation["History"] == []
        assert conversation["CollectedSlots"] == {}
        assert conversation["TurnCount"] == 0

    def test_get_or_create_conversation_existing(self):
        """Test retrieving an existing conversation state."""
        client = LLMMockClient(api_key="test")

        # Create first
        conv1 = client._get_or_create_conversation("user123")
        conv1["TurnCount"] = 5

        # Get again - should be same object
        conv2 = client._get_or_create_conversation("user123")

        assert conv2["TurnCount"] == 5
        assert conv1 is conv2

    def test_clear_conversation(self):
        """Test clearing a single conversation."""
        client = LLMMockClient(api_key="test")

        client._get_or_create_conversation("user1")
        client._get_or_create_conversation("user2")

        assert "user1" in client._conversations
        assert "user2" in client._conversations

        client.clear_conversation("user1")

        assert "user1" not in client._conversations
        assert "user2" in client._conversations

    def test_clear_all_conversations(self):
        """Test clearing all conversations."""
        client = LLMMockClient(api_key="test")

        client._get_or_create_conversation("user1")
        client._get_or_create_conversation("user2")

        client.clear_all_conversations()

        assert len(client._conversations) == 0


class TestLanguageExtraction:
    """Test language extraction from request_info."""

    def test_get_language_from_language_code(self):
        """Test extracting language from LanguageCode."""
        client = LLMMockClient(api_key="test")

        request_info = {"LanguageCode": "es-ES"}
        lang = client._get_language_from_request(request_info)

        assert lang == "es"

    def test_get_language_from_locale(self):
        """Test extracting language from Locale."""
        client = LLMMockClient(api_key="test")

        request_info = {"Locale": "fr-FR"}
        lang = client._get_language_from_request(request_info)

        assert lang == "fr"

    def test_get_language_missing_raises(self):
        """Test that missing language raises ValueError."""
        client = LLMMockClient(api_key="test")

        with pytest.raises(ValueError, match="LanguageCode must be provided"):
            client._get_language_from_request({})

        with pytest.raises(ValueError, match="LanguageCode must be provided"):
            client._get_language_from_request(None)


class TestErrorSimulation:
    """Test error simulation."""

    def test_should_simulate_error_disabled(self):
        """Test that error simulation is disabled by default."""
        client = LLMMockClient(api_key="test", error_rate=0.0)

        # Should never return True with 0 error rate
        for _ in range(100):
            assert client._should_simulate_error() is False

    def test_should_simulate_error_always(self):
        """Test that error simulation always triggers at 1.0."""
        client = LLMMockClient(api_key="test", error_rate=1.0)

        # Should always return True with 1.0 error rate
        for _ in range(10):
            assert client._should_simulate_error() is True


@pytest.mark.asyncio
class TestVoiceQuery:
    """Test voice_query method."""

    async def test_voice_query_error_simulation(self):
        """Test that voice_query raises error when simulation triggers."""
        client = LLMMockClient(api_key="test", error_rate=1.0)

        with pytest.raises(MockHoundifyError, match="Simulated LLM API error"):
            await client.voice_query(
                audio_data=b"test",
                user_id="user1",
                request_id="req1",
                request_info={"LanguageCode": "en-US", "Prompt": "Hello"},
            )

    async def test_voice_query_response_structure(self):
        """Test that voice_query returns Houndify-compatible structure."""
        client = LLMMockClient(api_key="test")

        # Mock the LLM call (extracted_entities is now an array of {name, value})
        mock_llm_response = {
            "CommandKind": "WeatherCommand",
            "SpokenResponse": "The weather is sunny.",
            "NativeData": {
                "domain": "weather",
                "extracted_entities": [{"name": "location", "value": "Seattle"}]
            }
        }

        with patch.object(client, '_call_llm', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_llm_response

            # Mock synthesize_speech
            with patch(
                'integrations.houndify.llm_mock_client.synthesize_speech'
            ) as mock_tts:
                mock_tts.return_value = b"fake_audio_bytes"

                response = await client.voice_query(
                    audio_data=b"test",
                    user_id="user1",
                    request_id="req1",
                    request_info={"LanguageCode": "en-US", "Prompt": "What's the weather?"},
                )

        # Verify Houndify structure
        assert response["Status"] == "OK"
        assert response["NumToReturn"] == 1
        assert len(response["AllResults"]) == 1

        result = response["AllResults"][0]
        assert result["CommandKind"] == "WeatherCommand"
        assert result["SpokenResponse"] == "The weather is sunny."
        assert result["Transcription"] == "What's the weather?"
        assert "ResponseAudioBytes" in result
        assert "ConversationState" in result

        # Verify native data
        assert result["NativeData"]["llm_mock"] is True
        assert result["NativeData"]["model"] == "openai/gpt-4o-mini"
        assert result["NativeData"]["domain"] == "weather"

        # Verify legacy fields
        assert response["mock"] == "llm_houndify"
        assert response["userId"] == "user1"
        assert response["requestId"] == "req1"


@pytest.mark.asyncio
class TestTextQuery:
    """Test text_query method."""

    async def test_text_query_error_simulation(self):
        """Test that text_query raises error when simulation triggers."""
        client = LLMMockClient(api_key="test", error_rate=1.0)

        with pytest.raises(MockHoundifyError, match="Simulated LLM API error"):
            await client.text_query(
                query="Hello",
                user_id="user1",
                request_id="req1",
                request_info={"LanguageCode": "en-US"},
            )


@pytest.mark.asyncio
class TestLLMCall:
    """Test LLM API call functionality."""

    async def test_call_llm_success(self):
        """Test successful LLM call with mocked OpenAI."""
        client = LLMMockClient(api_key="test-key")

        # Create mock response
        mock_choice = MagicMock()
        mock_choice.message.content = json.dumps({
            "CommandKind": "MusicCommand",
            "SpokenResponse": "Playing jazz music.",
            "NativeData": {
                "domain": "music",
                "extracted_entities": [{"name": "genre", "value": "jazz"}]
            }
        })

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.usage.total_tokens = 100

        # Mock the OpenAI client
        mock_openai_client = AsyncMock()
        mock_openai_client.chat.completions.create = AsyncMock(
            return_value=mock_response
        )
        client._client = mock_openai_client

        result = await client._call_llm(
            utterance="Play some jazz",
            language="en",
        )

        assert result["CommandKind"] == "MusicCommand"
        assert result["SpokenResponse"] == "Playing jazz music."
        assert result["NativeData"]["domain"] == "music"

    async def test_call_llm_invalid_command_kind_defaults(self):
        """Test that invalid CommandKind defaults to UnknownCommand."""
        client = LLMMockClient(api_key="test-key")

        # Create mock response with invalid CommandKind
        mock_choice = MagicMock()
        mock_choice.message.content = json.dumps({
            "CommandKind": "InvalidCommand",  # Not in allowed list
            "SpokenResponse": "Test response",
            "NativeData": {"domain": "test", "extracted_entities": []}
        })

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.usage.total_tokens = 50

        mock_openai_client = AsyncMock()
        mock_openai_client.chat.completions.create = AsyncMock(
            return_value=mock_response
        )
        client._client = mock_openai_client

        result = await client._call_llm(
            utterance="Test",
            language="en",
        )

        # Should default to UnknownCommand
        assert result["CommandKind"] == "UnknownCommand"
