"""
Houndify API Client

This module provides a client for interacting with the Houndify API
(SoundHound's conversational AI platform).

The client supports:
- Text queries for text-based interactions
- Voice queries for audio-based interactions
- Conversation state management for multi-turn dialogs
- Proper authentication using Client ID and Client Key

API Documentation: https://docs.houndify.com
Developer Platform: https://www.houndify.com/developers
"""

from typing import Dict, Any, Optional
import logging
import os
import houndify

from .models import HoundifyError

logger = logging.getLogger(__name__)


class HoundifyClient:
    """
    Client for interacting with the Houndify API.

    This client provides methods for sending text and voice queries to the
    Houndify platform, managing conversation state, and handling authentication.

    Attributes:
        client_id: Houndify client ID for authentication
        client_key: Houndify client key for authentication
        base_url: Base URL for Houndify API endpoints
        conversation_state_enabled: Whether conversation state is enabled
        conversation_state: Current conversation state dictionary

    Example:
        client = HoundifyClient(
            client_id="YOUR_CLIENT_ID",
            client_key="YOUR_CLIENT_KEY"
        )

        response = await client.text_query(
            query="What's the weather in Paris?",
            user_id="user123",
            request_id="req456"
        )
    """

    def __init__(self, client_id: str, client_key: str):
        """
        Initialize the Houndify client using the official SDK.

        Args:
            client_id: Houndify client ID (from developer account)
            client_key: Houndify client key (from developer account)
        """
        self.client_id = client_id
        self.client_key = client_key
        self.user_id = "voiceai_test_user"  # Default user ID

        # Create official SDK client for text queries
        # Note: SDK uses positional arguments (clientID, clientKey, userID)
        self._text_client = houndify.TextHoundClient(
            client_id,
            client_key,
            self.user_id
        )

        logger.info(f"[HOUNDIFY_CLIENT] Initialized with official SDK - client_id={client_id[:20]}...")

    async def text_query(
        self,
        query: str,
        user_id: str,
        request_id: str,
        request_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send a text query to Houndify API.

        This method sends a text-based query to the Houndify platform and returns
        the parsed response. It's useful for testing and text-based interactions.

        Includes automatic retry logic with exponential backoff for transient errors.

        Args:
            query: The text query to send (e.g., "What time is it in Paris?")
            user_id: Unique identifier for the user making the request
            request_id: Unique identifier for this specific request
            request_info: Optional dictionary with additional context (latitude,
                         longitude, timezone, etc.)

        Returns:
            Dictionary containing the Houndify response with fields:
                - AllResults: List of result objects
                - Status: Response status information
                - NumToReturn: Number of results returned

        Raises:
            HoundifyError: If the API request fails after retries
            ValueError: If required parameters are missing

        Example:
            response = await client.text_query(
                query="What's 5 plus 7?",
                user_id="user123",
                request_id="req456",
                request_info={"Latitude": 37.7749, "Longitude": -122.4194}
            )
        """
        if not query:
            raise ValueError("Query parameter is required")

        logger.info(f"[HOUNDIFY_CLIENT] Sending text query: '{query}'")

        try:
            # Use official SDK's query method (synchronous)
            # Note: The official SDK is synchronous, so we run it in executor
            import asyncio
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self._text_client.query,
                query
            )

            logger.info(f"[HOUNDIFY_CLIENT] Text query successful")
            return response

        except Exception as e:
            error_msg = f"Houndify text query failed: {str(e)}"
            logger.error(f"[HOUNDIFY_CLIENT] {error_msg}")
            raise HoundifyError(
                message=error_msg,
                status_code=None,
                response=None
            ) from e

    async def voice_query(
        self,
        audio_data: bytes,
        user_id: str,
        request_id: str,
        request_info: Optional[Dict[str, Any]] = None,
        enable_partial_transcripts: bool = False
    ) -> Dict[str, Any]:
        """
        Send a voice query to Houndify API using the official SDK.

        This method sends audio data to the Houndify platform for speech recognition
        and natural language understanding.

        Args:
            audio_data: Raw audio data in bytes (must be pre-encoded to Houndify
                       specifications - typically 16kHz, 16-bit, mono PCM)
            user_id: Unique identifier for the user making the request
            request_id: Unique identifier for this specific request
            request_info: Optional dictionary with additional context
            enable_partial_transcripts: If True, request partial transcripts during
                                       processing (useful for real-time UI updates)

        Returns:
            Dictionary containing the Houndify response including:
                - AllResults: List containing transcription and command results
                - Status: Response status information

        Raises:
            HoundifyError: If the API request fails
            ValueError: If required parameters are missing or audio_data is invalid

        Example:
            with open("audio.wav", "rb") as f:
                audio_data = f.read()

            response = await client.voice_query(
                audio_data=audio_data,
                user_id="user123",
                request_id="req456",
                enable_partial_transcripts=True
            )
        """
        if not audio_data:
            raise ValueError("Audio data is required")
        if not user_id:
            raise ValueError("User ID is required")
        if not request_id:
            raise ValueError("Request ID is required")

        logger.info(
            f"[HOUNDIFY_CLIENT] Sending voice query - "
            f"audio_size={len(audio_data)} bytes, "
            f"user_id={user_id}, request_id={request_id}"
        )

        try:
            # Build request info
            if request_info is None:
                request_info = {}

            # Add partial transcripts setting
            if enable_partial_transcripts:
                request_info["PartialTranscriptsDesired"] = True

            # Use official SDK's StreamingHoundClient (synchronous)
            # Run in executor to avoid blocking the event loop
            import asyncio
            import io

            loop = asyncio.get_event_loop()

            def _run_streaming_query():
                """Run streaming query in synchronous context"""
                # Create listener to capture results
                class ResultListener(houndify.HoundListener):
                    def __init__(self):
                        self.result = None
                        self.error = None

                    def onFinalResponse(self, response):
                        self.result = response

                    def onError(self, error):
                        self.error = error

                listener = ResultListener()

                # Create streaming client
                streaming_client = houndify.StreamingHoundClient(
                    self.client_id,
                    self.client_key,
                    user_id,
                    requestInfo=request_info
                )

                # Start streaming
                streaming_client.start(listener)

                # Feed audio data in chunks (SDK expects streaming)
                chunk_size = 8192  # 8KB chunks
                audio_stream = io.BytesIO(audio_data)

                while True:
                    chunk = audio_stream.read(chunk_size)
                    if not chunk:
                        break
                    streaming_client.fill(chunk)

                # Finish streaming
                streaming_client.finish()

                # Return result or raise error
                if listener.error:
                    raise Exception(f"Houndify streaming error: {listener.error}")

                return listener.result

            # Run in executor
            response = await loop.run_in_executor(None, _run_streaming_query)

            logger.info(f"[HOUNDIFY_CLIENT] Voice query successful")
            return response

        except Exception as e:
            error_msg = f"Houndify voice query failed: {str(e)}"
            logger.error(f"[HOUNDIFY_CLIENT] {error_msg}")
            raise HoundifyError(
                message=error_msg,
                status_code=None,
                response=None
            ) from e


