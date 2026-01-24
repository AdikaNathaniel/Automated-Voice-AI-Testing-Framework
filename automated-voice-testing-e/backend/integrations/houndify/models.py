"""
Houndify API Response Models

This module defines Pydantic models for working with Houndify API responses,
requests, and errors. These models provide type safety, validation, and easy
serialization/deserialization of API data.

Models:
- HoundifyResponse: Main response model matching actual Houndify API structure
- HoundifyRequestInfo: Optional request context for improved accuracy
- HoundifyError: Custom exception for Houndify-specific errors

Based on Houndify API documentation and RESEARCH_FINDINGS.md
API Reference: https://docs.houndify.com
"""

from pydantic import BaseModel, ConfigDict
from typing import Dict, Any, Optional, List


class HoundifyResponse(BaseModel):
    """
    Response from Houndify API matching actual structure.

    This model represents the parsed and structured response from the Houndify
    platform after processing a text or voice query. It extracts key information
    from the complex nested response structure.

    Attributes:
        raw_transcription: Original speech-to-text transcription (from AllResults[0].RawTranscription)
        formatted_transcription: Cleaned transcription with punctuation (from AllResults[0].FormattedTranscription)
        command_kind: Type of command recognized (e.g., "WeatherQuery", "MapSearch")
        command_results: Full array of command result objects with detailed data
        entities: Extracted entities from the query (locations, dates, etc.)
        confidence: Recognition confidence score (0.0 to 1.0)
        spoken_response: Short text response suitable for TTS
        spoken_response_long: Detailed response text (optional)
        conversation_state: State data for multi-turn dialogs (optional)
        response_audio_bytes: Pre-generated audio response bytes (TTS, paid accounts only)
        response_time_ms: API response time in milliseconds
        request_id: Echo of the request ID for tracking
        all_results: Full raw response for advanced use cases

    Example:
        >>> response = HoundifyResponse(
        ...     raw_transcription="what's the weather",
        ...     formatted_transcription="What's the weather?",
        ...     command_kind="WeatherQuery",
        ...     command_results=[{"Temperature": 22, "Condition": "Sunny"}],
        ...     entities={"Location": "Paris"},
        ...     confidence=0.95,
        ...     spoken_response="It's sunny and 22 degrees",
        ...     request_id="req123",
        ...     all_results={"AllResults": [...]}
        ... )
    """

    raw_transcription: str
    formatted_transcription: str
    command_kind: str
    command_results: List[Dict[str, Any]]
    entities: Dict[str, Any]
    confidence: float
    spoken_response: str
    spoken_response_long: Optional[str] = None
    conversation_state: Optional[Dict[str, Any]] = None
    response_audio_bytes: Optional[bytes] = None
    response_time_ms: Optional[int] = None
    request_id: str
    all_results: Dict[str, Any]

    model_config = ConfigDict(arbitrary_types_allowed=True)  # Allow bytes type


class HoundifyRequestInfo(BaseModel):
    """
    Optional request context for better accuracy.

    This model represents additional context that can be sent with Houndify
    requests to improve recognition accuracy and relevance of results.
    Location data helps with local queries, user/request IDs enable tracking.

    Attributes:
        user_id: Unique identifier for the user making the request
        request_id: Unique identifier for this specific request (for logging/tracking)
        latitude: User's latitude coordinate (optional, improves location-based queries)
        longitude: User's longitude coordinate (optional, improves location-based queries)
        partial_transcripts_desired: Whether to receive partial transcripts during processing

    Example:
        >>> request_info = HoundifyRequestInfo(
        ...     user_id="user123",
        ...     request_id="req456",
        ...     latitude=37.7749,
        ...     longitude=-122.4194,
        ...     partial_transcripts_desired=True
        ... )
    """

    user_id: str
    request_id: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    partial_transcripts_desired: bool = False


class HoundifyError(Exception):
    """
    Custom exception for Houndify API errors.

    This exception is raised when the Houndify API returns an error response
    or when request validation fails. It captures the error message, HTTP
    status code, and full response for debugging.

    Attributes:
        message: Human-readable error description
        status_code: HTTP status code from the API (e.g., 400, 429, 500)
        response: Full error response dictionary from the API

    Example:
        >>> raise HoundifyError(
        ...     "Rate limit exceeded",
        ...     status_code=429,
        ...     response={"error": "Too many requests", "retry_after": 60}
        ... )
    """

    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[dict] = None):
        """
        Initialize HoundifyError.

        Args:
            message: Error message describing what went wrong
            status_code: HTTP status code if from API response
            response: Full response dictionary from the API
        """
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)
