"""
LLM-Powered Mock Houndify Client.

This module provides an LLM-powered alternative to MockHoundifyClient.
Instead of pattern matching and hardcoded templates, it uses an LLM via
OpenRouter to dynamically generate contextual responses.

Key Features:
- Same interface as MockHoundifyClient (drop-in replacement)
- Dynamic response generation via LLM (OpenRouter API)
- Strict CommandKind enforcement (only allowed values)
- Conversation state tracking for multi-turn scenarios
- gTTS audio generation (same as MockHoundifyClient)
- Houndify-compatible response structure

Usage:
    >>> client = LLMMockClient()  # Uses OPENROUTER_API_KEY from env
    >>> response = await client.voice_query(audio_data, user_id, request_id, request_info)
"""

from typing import Dict, Any, Optional, List
import asyncio
import base64
import json
import logging
import os
import time

from .mock_client import synthesize_speech, MockHoundifyError

logger = logging.getLogger(__name__)

# Default model for LLM mock (via OpenRouter)
DEFAULT_LLM_MODEL = "openai/gpt-4o-mini"


# =============================================================================
# Allowed CommandKind Values (Strict Enforcement)
# =============================================================================

ALLOWED_COMMAND_KINDS = [
    "WeatherCommand",
    "MusicCommand",
    "NavigationCommand",
    "PhoneCommand",
    "ClientMatchCommand",
    "NoResultCommand",
    "UnknownCommand",
]

# JSON Schema for LLM response (OpenAI Structured Outputs)
# Note: Strict mode requires additionalProperties: false on all objects,
# so we use an array of entities instead of a dynamic object.
LLM_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "CommandKind": {
            "type": "string",
            "enum": ALLOWED_COMMAND_KINDS,
            "description": "The type of command detected from user utterance"
        },
        "SpokenResponse": {
            "type": "string",
            "description": "The voice AI's spoken response to the user"
        },
        "NativeData": {
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "The domain of the request (e.g., dining, weather, music)"
                },
                "extracted_entities": {
                    "type": "array",
                    "description": "Key entities extracted from the user utterance",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Entity name (e.g., location, date, restaurant)"
                            },
                            "value": {
                                "type": "string",
                                "description": "Entity value"
                            }
                        },
                        "required": ["name", "value"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["domain", "extracted_entities"],
            "additionalProperties": False
        }
    },
    "required": ["CommandKind", "SpokenResponse", "NativeData"],
    "additionalProperties": False
}


# =============================================================================
# System Prompt for Voice AI Simulation
# =============================================================================

SYSTEM_PROMPT = """You are simulating a voice AI assistant. Your task is to:
1. Understand the user's utterance
2. Classify it into the correct CommandKind
3. Generate an appropriate spoken response
4. Extract relevant entities

CRITICAL RULES:
- CommandKind MUST be exactly one of these values (no other values allowed):
  * WeatherCommand - weather queries, temperature, forecast
  * MusicCommand - play music, songs, artists, playlists
  * NavigationCommand - directions, routes, navigation
  * PhoneCommand - make calls, dial numbers
  * ClientMatchCommand - reservations, smart home, custom domains
  * NoResultCommand - when you understand but cannot help
  * UnknownCommand - when you cannot understand or classify the request

- SpokenResponse should be natural, conversational, and concise (1-2 sentences max)
- Response language MUST match the user's language
- For multi-turn conversations, use the provided history for context

DOMAIN GUIDELINES:
- Restaurant reservations: Ask for restaurant, date/time, party size one at a time
- Weather: Provide current conditions and forecast
- Music: Confirm what's being played
- Navigation: Confirm destination and provide brief route info
- Smart home: Confirm the action taken

Respond with valid JSON only."""


def _build_user_prompt(
    utterance: str,
    language: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
) -> str:
    """
    Build the user prompt for the LLM.

    Args:
        utterance: The user's current utterance
        language: Language code (en, es, fr, etc.)
        conversation_history: Previous turns in the conversation

    Returns:
        Formatted user prompt string
    """
    prompt_parts = []

    # Add conversation history if available
    if conversation_history:
        prompt_parts.append("CONVERSATION HISTORY:")
        for i, turn in enumerate(conversation_history, 1):
            prompt_parts.append(f"  Turn {i}:")
            prompt_parts.append(f"    User: {turn.get('user', '')}")
            prompt_parts.append(f"    AI: {turn.get('ai', '')}")
        prompt_parts.append("")

    # Add current utterance
    prompt_parts.append(f"LANGUAGE: {language}")
    prompt_parts.append(f"USER UTTERANCE: {utterance}")
    prompt_parts.append("")
    prompt_parts.append("Generate the voice AI response as JSON.")

    return "\n".join(prompt_parts)


class LLMMockClient:
    """
    LLM-powered mock Houndify client with dynamic response generation.

    This client provides the same interface as MockHoundifyClient but uses
    an LLM via OpenRouter to generate contextual responses instead of
    pattern matching.

    Attributes:
        model: The LLM model to use via OpenRouter (default: openai/gpt-4o-mini)
        temperature: Sampling temperature (default: 0.0 for consistency)
        max_tokens: Maximum response tokens (default: 256)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 256,
        timeout: int = 30,
        error_rate: float = 0.0,
        latency_ms: int = 0,
        base_url: Optional[str] = None,
    ):
        """
        Initialize the LLM mock client.

        Args:
            api_key: OpenRouter API key (uses OPENROUTER_API_KEY env var if not provided)
            model: Model name via OpenRouter (default: openai/gpt-4o-mini)
            temperature: Sampling temperature for response generation
            max_tokens: Maximum tokens in LLM response
            timeout: API request timeout in seconds
            error_rate: Probability of simulating an error (0.0 - 1.0)
            latency_ms: Additional simulated latency in milliseconds
            base_url: OpenRouter API base URL (default: https://openrouter.ai/api/v1)

        Raises:
            ValueError: If error_rate is not between 0.0 and 1.0
            ValueError: If latency_ms is negative
        """
        if error_rate < 0.0 or error_rate > 1.0:
            raise ValueError("error_rate must be between 0.0 and 1.0")
        if latency_ms < 0:
            raise ValueError("latency_ms must be non-negative")

        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.model = model or os.getenv('LLM_MOCK_MODEL', DEFAULT_LLM_MODEL)
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.error_rate = error_rate
        self.latency_ms = latency_ms
        self.base_url = base_url or os.getenv(
            'OPENROUTER_BASE_URL',
            'https://openrouter.ai/api/v1'
        )

        self._client = None
        self._conversations: Dict[str, Dict[str, Any]] = {}

    async def _initialize_client(self) -> None:
        """Initialize the OpenRouter client (OpenAI-compatible)."""
        if self._client is not None:
            return

        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ImportError(
                "openai package is required for LLMMockClient. "
                "Install it with: pip install openai"
            )

        if not self.api_key:
            raise ValueError(
                "OpenRouter API key is required. "
                "Set OPENROUTER_API_KEY environment variable or pass api_key."
            )

        self._client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=float(self.timeout),
            default_headers={
                "HTTP-Referer": os.getenv('APP_URL', 'http://localhost:8000'),
                "X-Title": os.getenv('APP_NAME', 'Voice AI Testing Framework'),
            }
        )
        logger.debug(
            f"Initialized OpenRouter client with model: {self.model}, "
            f"base_url: {self.base_url}"
        )

    async def _simulate_latency(self) -> None:
        """Simulate network latency if configured."""
        if self.latency_ms > 0:
            await asyncio.sleep(self.latency_ms / 1000.0)

    def _should_simulate_error(self) -> bool:
        """Determine if an error should be simulated based on error_rate."""
        if self.error_rate > 0:
            import random
            return random.random() < self.error_rate
        return False

    def _get_language_from_request(
        self,
        request_info: Optional[Dict[str, Any]],
    ) -> str:
        """
        Get language from request_info.

        Args:
            request_info: Request info dict from execution service

        Returns:
            Language code: 'en', 'es', 'fr', etc.

        Raises:
            ValueError: If no language is provided in request_info
        """
        if request_info:
            lang_code = request_info.get("LanguageCode")
            if lang_code:
                return lang_code.split("-")[0].lower()

            locale = request_info.get("Locale")
            if locale:
                return locale.split("-")[0].lower()

        raise ValueError(
            "LanguageCode must be provided in request_info. "
            "Ensure scenario variant includes language configuration."
        )

    def _get_or_create_conversation(self, user_id: str) -> Dict[str, Any]:
        """
        Get or create conversation state for a user.

        Args:
            user_id: User identifier

        Returns:
            Conversation state dictionary
        """
        if user_id not in self._conversations:
            self._conversations[user_id] = {
                "ConversationStateId": f"conv_{user_id}_{int(time.time())}",
                "ConversationStateTime": int(time.time()),
                "History": [],
                "CollectedSlots": {},
                "TurnCount": 0,
            }
        return self._conversations[user_id]

    async def _call_llm(
        self,
        utterance: str,
        language: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Call the LLM to generate a response.

        Args:
            utterance: User's utterance
            language: Language code
            conversation_history: Previous conversation turns

        Returns:
            Parsed LLM response with CommandKind, SpokenResponse, NativeData
        """
        await self._initialize_client()

        user_prompt = _build_user_prompt(utterance, language, conversation_history)

        response = await self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "voice_ai_response",
                    "strict": True,
                    "schema": LLM_RESPONSE_SCHEMA
                }
            }
        )

        content = response.choices[0].message.content or "{}"
        parsed = json.loads(content)

        # Validate CommandKind (should be guaranteed by schema, but double-check)
        if parsed.get("CommandKind") not in ALLOWED_COMMAND_KINDS:
            logger.warning(
                f"Invalid CommandKind from LLM: {parsed.get('CommandKind')}, "
                f"defaulting to UnknownCommand"
            )
            parsed["CommandKind"] = "UnknownCommand"

        logger.debug(
            f"LLM response: CommandKind={parsed.get('CommandKind')}, "
            f"tokens={response.usage.total_tokens if response.usage else 'N/A'}"
        )

        return parsed

    async def text_query(
        self,
        query: str,
        user_id: str,
        request_id: str,
        request_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process a text query using the LLM.

        Args:
            query: The text query to process
            user_id: User identifier for conversation tracking
            request_id: Request identifier
            request_info: Optional additional request context

        Returns:
            Houndify-compatible response dictionary

        Raises:
            MockHoundifyError: If error simulation is triggered
        """
        await self._simulate_latency()

        if self._should_simulate_error():
            raise MockHoundifyError("Simulated LLM API error")

        return await self._build_response(
            prompt=query,
            user_id=user_id,
            request_id=request_id,
            request_info=request_info,
        )

    async def voice_query(
        self,
        audio_data: bytes,
        user_id: str,
        request_id: str,
        request_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process a voice query using the LLM.

        Args:
            audio_data: Audio bytes (ignored, prompt comes from request_info)
            user_id: User identifier for conversation tracking
            request_id: Request identifier
            request_info: Request info including Prompt and LanguageCode

        Returns:
            Houndify-compatible response dictionary

        Raises:
            MockHoundifyError: If error simulation is triggered
        """
        await self._simulate_latency()

        if self._should_simulate_error():
            raise MockHoundifyError("Simulated LLM API error")

        prompt = ""
        if request_info:
            prompt = request_info.get("Prompt", "")

        return await self._build_response(
            prompt=prompt,
            user_id=user_id,
            request_id=request_id,
            request_info=request_info,
        )

    async def _build_response(
        self,
        prompt: str,
        user_id: str,
        request_id: str,
        request_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Build a Houndify-compatible response using the LLM.

        Args:
            prompt: User's utterance
            user_id: User identifier
            request_id: Request identifier
            request_info: Additional request context

        Returns:
            Houndify-compatible response dictionary
        """
        # Get language
        language = self._get_language_from_request(request_info)

        # Get conversation state
        conversation = self._get_or_create_conversation(user_id)
        conversation["TurnCount"] += 1
        conversation["ConversationStateTime"] = int(time.time())

        # Call LLM with conversation history
        llm_response = await self._call_llm(
            utterance=prompt,
            language=language,
            conversation_history=conversation.get("History", []),
        )

        command_kind = llm_response.get("CommandKind", "UnknownCommand")
        spoken_response = llm_response.get("SpokenResponse", "")
        native_data = llm_response.get("NativeData", {})

        # Update conversation history
        conversation["History"].append({
            "user": prompt,
            "ai": spoken_response,
        })

        # Update collected slots from extracted entities
        # LLM returns array of {name, value} objects, convert to dict
        extracted_list = native_data.get("extracted_entities", [])
        extracted = {item["name"]: item["value"] for item in extracted_list}
        conversation["CollectedSlots"].update(extracted)

        # Generate TTS audio
        tts_audio_bytes = synthesize_speech(
            text=spoken_response,
            sample_rate=16000,
            language=language,
        )
        tts_audio_base64 = base64.b64encode(tts_audio_bytes).decode('utf-8')

        # Build Houndify-compatible response
        return {
            "Status": "OK",
            "NumToReturn": 1,
            "AllResults": [
                {
                    # Transcription fields
                    "RawTranscription": prompt.lower(),
                    "FormattedTranscription": prompt,
                    "Transcription": prompt,

                    # Command classification
                    "CommandKind": command_kind,

                    # Confidence scores
                    "ASRConfidence": 0.95,
                    "Score": 95.0,

                    # Response text fields
                    "SpokenResponse": spoken_response,
                    "SpokenResponseLong": spoken_response,
                    "WrittenResponse": spoken_response,
                    "WrittenResponseLong": spoken_response,

                    # Audio response
                    "ResponseAudioBytes": tts_audio_base64,

                    # Conversation state
                    "ConversationState": conversation.copy(),

                    # Native data from LLM
                    "NativeData": {
                        "llm_mock": True,
                        "model": self.model,
                        "prompt": prompt,
                        "turn_count": conversation["TurnCount"],
                        "domain": native_data.get("domain", "general"),
                        "extracted_entities": extracted,
                        "collected_slots": conversation.get("CollectedSlots", {}),
                    },

                    # Metadata
                    "ResultsAreFinal": True,
                    "DisambiguationData": None,
                }
            ],
            # Raw audio bytes
            "AudioBytes": tts_audio_bytes,
            "AudioBytesBase64": tts_audio_base64,

            # Response metadata
            "Disambiguation": None,
            "ResultsAreFinal": True,

            # Legacy fields for compatibility
            "mock": "llm_houndify",
            "userId": user_id,
            "requestId": request_id,
            "prompt": prompt,
            "transcript": prompt,
            "status": "success",
        }

    def clear_conversation(self, user_id: str) -> None:
        """
        Clear conversation state for a user.

        Args:
            user_id: User identifier
        """
        if user_id in self._conversations:
            del self._conversations[user_id]
            logger.debug(f"Cleared conversation state for user: {user_id}")

    def clear_all_conversations(self) -> None:
        """Clear all conversation states."""
        self._conversations.clear()
        logger.debug("Cleared all conversation states")
