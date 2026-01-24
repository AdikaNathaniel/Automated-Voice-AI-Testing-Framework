"""
Mock Houndify client used for offline testing.

Provides the same interface as the real Houndify client but returns
deterministic responses so tests do not require network access.

Returns proper Houndify response structure with AllResults array
containing CommandKind, transcription fields, confidence scores,
and playable TTS audio bytes.

Features:
- Full Houndify response structure matching real API
- Playable WAV audio generation for TTS responses
- Conversation state tracking for multi-turn scenarios
- Multi-language support (EN, ES, FR)
"""

from typing import Dict, Any, Optional, List
import asyncio
import base64
import io
import random
import re
import struct
import time
import wave


class MockHoundifyError(Exception):
    """Simulated error for testing error handling."""
    pass


def synthesize_speech(
    text: str,
    sample_rate: int = 16000,
    language: str = "en",
) -> bytes:
    """
    Synthesize speech audio from text using TTS.

    Attempts to use Google TTS (gTTS) for realistic speech synthesis.
    Falls back to a simple tone generator if gTTS is unavailable.

    Args:
        text: Text to synthesize into speech
        sample_rate: Target audio sample rate in Hz (default 16kHz)
        language: Language code for TTS (en, es, fr, etc.)

    Returns:
        WAV file bytes containing synthesized speech
    """
    # Try gTTS first for realistic speech
    try:
        from gtts import gTTS
        from pydub import AudioSegment

        # Generate speech with gTTS (returns MP3)
        tts = gTTS(text=text, lang=language, slow=False)
        mp3_buffer = io.BytesIO()
        tts.write_to_fp(mp3_buffer)
        mp3_buffer.seek(0)

        # Convert MP3 to WAV at target sample rate
        audio = AudioSegment.from_mp3(mp3_buffer)
        audio = audio.set_frame_rate(sample_rate)
        audio = audio.set_channels(1)
        audio = audio.set_sample_width(2)

        wav_buffer = io.BytesIO()
        audio.export(wav_buffer, format='wav')
        return wav_buffer.getvalue()

    except ImportError:
        # gTTS or pydub not available, use fallback
        pass
    except Exception:
        # Network error or other issue, use fallback
        pass

    # Fallback: Generate simple tone-based audio
    return _generate_fallback_audio(text, sample_rate)


def _generate_fallback_audio(
    text: str,
    sample_rate: int = 16000,
    duration_per_word: float = 0.25,
) -> bytes:
    """
    Generate simple audio as fallback when TTS is unavailable.

    Creates audio with varying tones to roughly simulate speech patterns.
    Not realistic speech, but valid playable audio for testing.

    Args:
        text: Text (used to determine duration)
        sample_rate: Audio sample rate in Hz
        duration_per_word: Duration per word in seconds

    Returns:
        WAV file bytes
    """
    import math

    # Calculate duration based on word count
    word_count = max(len(text.split()), 1)
    duration = word_count * duration_per_word

    # Generate samples with varying frequency to simulate speech
    num_samples = int(sample_rate * duration)
    samples = []

    # Use multiple frequencies to create a more speech-like sound
    base_freq = 200  # Base frequency for voice

    for i in range(num_samples):
        t = i / sample_rate
        # Modulate frequency to simulate speech patterns
        freq_mod = base_freq + (100 * math.sin(2 * math.pi * 3 * t))
        # Add harmonics for richer sound
        sample = (
            0.5 * math.sin(2 * math.pi * freq_mod * t) +
            0.25 * math.sin(2 * math.pi * freq_mod * 2 * t) +
            0.125 * math.sin(2 * math.pi * freq_mod * 3 * t)
        )
        # Apply envelope (fade in/out)
        envelope = min(t * 10, 1.0) * min((duration - t) * 10, 1.0)
        samples.append(int(32767 * 0.4 * sample * envelope))

    # Create WAV file
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(struct.pack(f'{len(samples)}h', *samples))

    return buffer.getvalue()


def generate_silence_audio(duration: float = 0.5, sample_rate: int = 16000) -> bytes:
    """
    Generate silent WAV audio bytes.

    Useful for padding or testing audio handling.

    Args:
        duration: Duration in seconds
        sample_rate: Audio sample rate in Hz

    Returns:
        WAV file bytes of silence
    """
    num_samples = int(sample_rate * duration)
    samples = [0] * num_samples

    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(struct.pack(f'{len(samples)}h', *samples))

    return buffer.getvalue()


class MockHoundifyClient:
    """
    Minimal stand-in for the real HoundifyClient with conversation state tracking.

    This mock client simulates Houndify's conversation state management by:
    - Tracking conversation state per user_id
    - Maintaining collected slots across turns
    - Generating realistic ConversationState objects

    The constructor signature matches HoundifyClient for seamless switching.
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_key: Optional[str] = None,
        response_patterns: Optional[Dict[str, Any]] = None,
        error_rate: float = 0.0,
        latency_ms: int = 0,
    ):
        """
        Initialize mock client with conversation state tracking.

        Args:
            client_id: Houndify client ID (ignored in mock, for interface compatibility)
            client_key: Houndify client key (ignored in mock, for interface compatibility)
            response_patterns: Optional dict of query patterns to custom responses
            error_rate: Probability of simulating an error (0.0 - 1.0)
            latency_ms: Simulated latency in milliseconds

        Raises:
            ValueError: If error_rate is not between 0.0 and 1.0
            ValueError: If latency_ms is negative
        """
        # Store credentials for interface compatibility (not used)
        self.client_id = client_id
        self.client_key = client_key

        # Validate error_rate
        if error_rate < 0.0 or error_rate > 1.0:
            raise ValueError("error_rate must be between 0.0 and 1.0")

        # Validate latency_ms
        if latency_ms < 0:
            raise ValueError("latency_ms must be non-negative")

        self.response_patterns = response_patterns or {}
        self.error_rate = error_rate
        self.latency_ms = latency_ms

        # Track conversation state per user_id
        self._conversations: Dict[str, Dict[str, Any]] = {}

    async def _simulate_latency(self) -> None:
        """Simulate network latency if configured."""
        if self.latency_ms > 0:
            await asyncio.sleep(self.latency_ms / 1000.0)

    def _should_simulate_error(self) -> bool:
        """Determine if an error should be simulated based on error_rate."""
        if self.error_rate > 0:
            return random.random() < self.error_rate
        return False

    def _match_pattern(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Match query against response patterns.

        Args:
            query: The query text to match

        Returns:
            Matched response pattern or None
        """
        if not self.response_patterns:
            return None

        query_lower = query.lower()
        for pattern, response in self.response_patterns.items():
            # Try regex match first
            try:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    return response
            except re.error:
                # If pattern is not valid regex, try simple substring match
                if pattern.lower() in query_lower:
                    return response

        return None

    def _infer_command_kind(self, prompt: str) -> str:
        """
        Infer CommandKind from prompt text for realistic mock responses.

        Maps user utterances to Houndify CommandKind values.
        Supports English, Spanish, and French queries.

        Restaurant Reservation Flow (Custom Command):
        - All reservation-related queries → ClientMatchCommand

        Built-in Houndify Domains:
        - Weather queries → WeatherCommand
        - Music queries → MusicCommand
        - Navigation queries → NavigationCommand
        - Phone queries → PhoneCommand
        - Smart home queries → ClientMatchCommand

        Args:
            prompt: User's input text

        Returns:
            CommandKind string (Houndify's native classification)
        """
        prompt_lower = prompt.lower()

        # Weather queries - English, Spanish, French
        # CHECK FIRST: Weather has priority over generic time words like "tomorrow"
        if any(word in prompt_lower for word in [
            # English
            "weather", "temperature", "forecast", "rain", "sunny", "clima",
            # Spanish
            "tiempo", "temperatura", "pronóstico", "lluvia", "soleado",
            # French
            "météo", "temps", "température", "prévisions", "pluie", "ensoleillé"
        ]):
            return "WeatherCommand"

        # Navigation queries - English, Spanish, French
        # NOTE: Must come BEFORE restaurant check, as both may contain "downtown"
        elif any(word in prompt_lower for word in [
            # English
            "navigate", "directions", "route", "map",
            # Spanish
            "navega", "direcciones", "ruta", "mapa",
            # French
            "navigue", "directions", "itinéraire", "carte"
        ]):
            return "NavigationCommand"

        # Restaurant reservation flow - use ClientMatchCommand for custom domain
        # This covers all steps: initial request, restaurant selection, datetime, party size, confirmation
        elif any(word in prompt_lower for word in [
            # English
            "reservation", "reserve", "book a table", "make a dinner",
            "italian", "chinese", "mexican", "downtown", "place",
            "tomorrow", "tonight", "7 pm", "7pm", "8 pm", "8pm",
            "people", "party", "confirm",
            # Spanish
            "reserva", "reservar", "mesa", "cena",
            "italiano", "chino", "mexicano", "centro",
            "mañana", "noche", "personas", "confirmar",
            # French
            "réservation", "réserver", "table", "dîner",
            "italien", "chinois", "mexicain", "centre-ville",
            "demain", "soir", "personnes", "confirmer"
        ]):
            return "ClientMatchCommand"

        # Music queries - English, Spanish, French
        elif any(word in prompt_lower for word in [
            # English
            "play", "music", "song", "artist", "album", "pause",
            # Spanish
            "reproduce", "música", "canción", "artista", "álbum", "pausa",
            # French
            "joue", "musique", "chanson", "artiste", "album", "pause"
        ]):
            return "MusicCommand"

        # Phone queries - English, Spanish, French
        elif any(word in prompt_lower for word in [
            # English
            "call", "phone", "dial",
            # Spanish
            "llama", "teléfono", "marca",
            # French
            "appelle", "téléphone", "compose"
        ]):
            return "PhoneCommand"

        # Smart home queries - English, Spanish, French
        elif any(word in prompt_lower for word in [
            # English
            "turn on", "turn off", "lights", "living room", "bedroom",
            # Spanish
            "enciende", "apaga", "luces", "sala", "dormitorio",
            # French
            "allume", "éteins", "lumières", "salon", "chambre"
        ]):
            return "ClientMatchCommand"

        else:
            # Default to no result for unknown queries
            return "NoResultCommand"

    async def text_query(
        self,
        query: str,
        user_id: str,
        request_id: str,
        request_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Mock text query method matching the real HoundifyClient interface.

        Args:
            query: The text query to process
            user_id: User identifier for conversation tracking
            request_id: Request identifier
            request_info: Optional additional request context

        Returns:
            Mock Houndify response with conversation state

        Raises:
            MockHoundifyError: If error simulation is triggered
        """
        # Simulate latency
        await self._simulate_latency()

        # Check for simulated error
        if self._should_simulate_error():
            raise MockHoundifyError("Simulated Houndify API error")

        # Check for pattern match
        pattern_response = self._match_pattern(query)
        if pattern_response:
            return pattern_response

        # Build response using the same logic as voice_query
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
        Mock voice query with conversation state tracking.

        Args:
            audio_data: Audio bytes (ignored in mock, size logged for debugging)
            user_id: User identifier for conversation tracking
            request_id: Request identifier
            request_info: Request info including ConversationState and Prompt

        Returns:
            Mock Houndify response with conversation state

        Raises:
            MockHoundifyError: If error simulation is triggered
        """
        # Simulate latency
        await self._simulate_latency()

        # Check for simulated error
        if self._should_simulate_error():
            raise MockHoundifyError("Simulated Houndify API error")

        prompt = ""
        incoming_conversation_state = None

        if request_info:
            prompt = request_info.get("Prompt", "")
            incoming_conversation_state = request_info.get("ConversationState")

        # Check for pattern match
        pattern_response = self._match_pattern(prompt)
        if pattern_response:
            return pattern_response

        # Build response using shared method
        return await self._build_response(
            prompt=prompt,
            user_id=user_id,
            request_id=request_id,
            request_info=request_info,
            incoming_conversation_state=incoming_conversation_state,
        )

    async def _build_response(
        self,
        prompt: str,
        user_id: str,
        request_id: str,
        request_info: Optional[Dict[str, Any]] = None,
        incoming_conversation_state: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Build a mock Houndify response with proper structure.

        Args:
            prompt: The user's query text
            user_id: User identifier for conversation tracking
            request_id: Request identifier
            request_info: Optional additional request context
            incoming_conversation_state: Optional incoming conversation state to merge

        Returns:
            Mock Houndify response dictionary
        """
        # Get conversation state from request_info if not passed directly
        if incoming_conversation_state is None and request_info:
            incoming_conversation_state = request_info.get("ConversationState")

        # Infer CommandKind from prompt
        command_kind = self._infer_command_kind(prompt)

        # Get or create conversation state for this user
        if user_id not in self._conversations:
            self._conversations[user_id] = {
                "ConversationStateId": f"conv_{user_id}_{int(time.time())}",
                "ConversationStateTime": int(time.time()),
                "DialogPhase": "initial",
                "CollectedSlots": {},
                "PendingSlots": [],
                "Domain": "general",
                "TurnCount": 0
            }

        # Update conversation state
        conversation = self._conversations[user_id]
        conversation["TurnCount"] += 1
        conversation["ConversationStateTime"] = int(time.time())

        # If incoming state provided, merge it
        if incoming_conversation_state:
            conversation.update(incoming_conversation_state)

        # Extract entities from prompt and add to collected slots
        self._extract_and_store_entities(prompt, conversation)

        # Get language from request_info (must be explicitly provided)
        language = self._get_language_from_request(request_info)

        # Generate contextual response based on conversation state
        spoken_response = self._generate_contextual_response(prompt, conversation, language)

        # Generate TTS audio for the response (uses gTTS if available)
        tts_audio_bytes = synthesize_speech(
            text=spoken_response,
            sample_rate=16000,
            language=language,
        )
        tts_audio_base64 = base64.b64encode(tts_audio_bytes).decode('utf-8')

        # Generate mock response with proper Houndify structure
        # This matches the real Houndify API response format
        return {
            "Status": "OK",
            "NumToReturn": 1,
            "AllResults": [
                {
                    # Transcription fields (what ASR heard)
                    "RawTranscription": prompt.lower(),
                    "FormattedTranscription": prompt,
                    "Transcription": prompt,  # Primary transcript field

                    # Command classification
                    "CommandKind": command_kind,

                    # Confidence scores
                    "ASRConfidence": 0.95,
                    "Score": 95.0,  # Houndify's overall confidence score

                    # Response text fields
                    "SpokenResponse": spoken_response,
                    "SpokenResponseLong": spoken_response,
                    "WrittenResponse": spoken_response,
                    "WrittenResponseLong": spoken_response,

                    # Audio response data (TTS output) - matches real Houndify API
                    # ResponseAudioBytes is the standard Houndify field for TTS audio
                    # Base64-encoded, format controlled by RequestInfo.ResponseAudioEncoding
                    "ResponseAudioBytes": tts_audio_base64,

                    # Conversation state (for multi-turn)
                    "ConversationState": conversation.copy(),

                    # Native data (domain-specific details)
                    "NativeData": {
                        "mock": True,
                        "prompt": prompt,
                        "turn_count": conversation["TurnCount"],
                        "domain": conversation.get("Domain", "general"),
                        "collected_slots": conversation.get("CollectedSlots", {}),
                    },

                    # Additional metadata
                    "ResultsAreFinal": True,
                    "DisambiguationData": None,
                }
            ],
            # Raw audio bytes (for direct playback)
            "AudioBytes": tts_audio_bytes,
            "AudioBytesBase64": tts_audio_base64,

            # Response metadata
            "Disambiguation": None,
            "ResultsAreFinal": True,

            # Legacy fields for backwards compatibility
            "mock": "houndify",
            "userId": user_id,
            "requestId": request_id,
            "prompt": prompt,
            "transcript": prompt,  # Use prompt as transcript for validation
            "status": "success",
        }

    def _extract_and_store_entities(self, prompt: str, conversation: Dict[str, Any]) -> None:
        """
        Extract entities from prompt and store in conversation state.

        This simulates Houndify's entity extraction and slot filling.
        Supports English, Spanish, and French.
        """
        prompt_lower = prompt.lower()
        collected_slots = conversation.get("CollectedSlots", {})

        # Extract restaurant-related entities (English, Spanish, French)
        if any(word in prompt_lower for word in ["reservation", "restaurant", "reserva", "réservation"]):
            conversation["Domain"] = "dining_reservation"
            # Meal type
            if any(word in prompt_lower for word in ["dinner", "cena", "dîner"]):
                collected_slots["meal_type"] = "dinner"
            elif any(word in prompt_lower for word in ["lunch", "almuerzo", "déjeuner"]):
                collected_slots["meal_type"] = "lunch"

        # Extract cuisine/location entities (English, Spanish, French)
        if any(word in prompt_lower for word in ["italian", "italiano", "italien"]):
            collected_slots["cuisine"] = "italian"
            collected_slots["restaurant_name"] = "Luigi's Italian Restaurant"
        elif any(word in prompt_lower for word in ["downtown", "centro", "centre-ville"]):
            collected_slots["location"] = "downtown"

        # Extract time entities (English, Spanish, French)
        if any(word in prompt_lower for word in ["tomorrow", "mañana", "demain"]):
            collected_slots["date"] = "tomorrow"
        if "7 pm" in prompt_lower or "7pm" in prompt_lower or "19:00" in prompt_lower:
            collected_slots["time"] = "19:00"

        # Extract party size (English, Spanish, French)
        if any(word in prompt_lower for word in ["four", "cuatro", "quatre", "4"]):
            collected_slots["party_size"] = 4
        elif any(word in prompt_lower for word in ["two", "dos", "deux", "2"]):
            collected_slots["party_size"] = 2

        conversation["CollectedSlots"] = collected_slots

    def _generate_contextual_response(
        self,
        prompt: str,
        conversation: Dict[str, Any],
        language: str = "en"
    ) -> str:
        """
        Generate contextual response based on conversation state.

        This simulates Houndify's contextual understanding.
        Supports English, Spanish, and French responses.

        Args:
            prompt: User's query text
            conversation: Conversation state dictionary
            language: Language code (from request_info or detected)
        """
        collected_slots = conversation.get("CollectedSlots", {})
        domain = conversation.get("Domain", "general")
        prompt_lower = prompt.lower()

        # Restaurant reservation flow
        if domain == "dining_reservation":
            if any(word in prompt_lower for word in ["reservation", "reserva", "réservation"]) and not collected_slots.get("restaurant_name"):
                return self._get_translation("which_restaurant", language)
            elif collected_slots.get("cuisine") and not collected_slots.get("date"):
                return self._get_translation("what_date_time", language)
            elif collected_slots.get("date") and not collected_slots.get("party_size"):
                return self._get_translation("how_many_people", language)
            elif collected_slots.get("party_size") and not any(word in prompt_lower for word in ["confirm", "confirmar", "confirmer"]):
                restaurant = collected_slots.get("restaurant_name", "the restaurant")
                date = collected_slots.get("date", "that date")
                time = collected_slots.get("time", "that time")
                party_size = collected_slots.get("party_size", "your party")
                return self._get_translation("reservation_summary", language).format(
                    party_size=party_size, restaurant=restaurant, date=date, time=time
                )
            elif any(word in prompt_lower for word in ["yes", "sí", "si", "oui", "confirm", "confirmar", "confirmer"]):
                return self._get_translation("reservation_confirmed", language)

        # Weather responses
        if any(word in prompt_lower for word in ["weather", "temperature", "forecast", "clima", "tiempo", "météo"]):
            # Extract location if present
            location = "your area"
            locations = ["seattle", "new york", "los angeles", "chicago", "boston", "miami"]
            for loc in locations:
                if loc in prompt_lower:
                    location = loc.title()
                    break
            return self._get_weather_response(location, language)

        # Music responses
        if any(word in prompt_lower for word in ["play", "music", "song", "artist", "jazz", "rock", "pop",
                                                  "reproduce", "música", "canción", "joue", "musique"]):
            genre = "your music"
            genres = ["jazz", "rock", "pop", "classical", "country", "hip hop", "electronic"]
            for g in genres:
                if g in prompt_lower:
                    genre = g
                    break
            return self._get_music_response(genre, language)

        # Navigation responses
        if any(word in prompt_lower for word in ["navigate", "directions", "route", "go to", "drive to",
                                                  "navegar", "direcciones", "naviguer", "itinéraire"]):
            destination = "your destination"
            if "seattle" in prompt_lower:
                destination = "downtown Seattle"
            elif "downtown" in prompt_lower:
                destination = "downtown"
            return self._get_navigation_response(destination, language)

        # Smart home responses
        if any(word in prompt_lower for word in ["light", "lights", "turn on", "turn off", "brightness",
                                                  "luz", "luces", "enciende", "apaga", "lumière", "allume", "éteins"]):
            action = "turn on" if any(word in prompt_lower for word in ["on", "enciende", "allume"]) else "turn off"
            room = "living room"
            rooms = ["bedroom", "kitchen", "bathroom", "living room", "office"]
            for r in rooms:
                if r in prompt_lower:
                    room = r
                    break
            return self._get_smart_home_response(action, room, language)

        # Default response
        return f"I understood: {prompt}. How can I help you further?"

    def _get_weather_response(self, location: str, language: str) -> str:
        """Generate a weather response."""
        responses = {
            "en": f"Currently in {location}, the weather is partly cloudy with a temperature of 72 degrees Fahrenheit. There's a 20% chance of rain later today.",
            "es": f"Actualmente en {location}, el clima está parcialmente nublado con una temperatura de 22 grados Celsius. Hay un 20% de probabilidad de lluvia más tarde.",
            "fr": f"Actuellement à {location}, le temps est partiellement nuageux avec une température de 22 degrés Celsius. Il y a 20% de chance de pluie plus tard."
        }
        return responses.get(language, responses["en"])

    def _get_music_response(self, genre: str, language: str) -> str:
        """Generate a music response."""
        responses = {
            "en": f"Playing {genre} music for you now. Enjoy the tunes!",
            "es": f"Reproduciendo música {genre} para ti ahora. ¡Disfruta la música!",
            "fr": f"Je joue de la musique {genre} pour vous maintenant. Profitez bien!"
        }
        return responses.get(language, responses["en"])

    def _get_navigation_response(self, destination: str, language: str) -> str:
        """Generate a navigation response."""
        responses = {
            "en": f"Navigating to {destination}. Starting route now. The fastest route takes approximately 15 minutes via the highway.",
            "es": f"Navegando hacia {destination}. Iniciando ruta ahora. La ruta más rápida toma aproximadamente 15 minutos por la autopista.",
            "fr": f"Navigation vers {destination}. Démarrage de l'itinéraire. Le trajet le plus rapide prend environ 15 minutes par l'autoroute."
        }
        return responses.get(language, responses["en"])

    def _get_smart_home_response(self, action: str, room: str, language: str) -> str:
        """Generate a smart home response."""
        action_word = "turned on" if "on" in action else "turned off"
        action_es = "encendidas" if "on" in action else "apagadas"
        action_fr = "allumées" if "on" in action else "éteintes"
        responses = {
            "en": f"Done! The {room} lights have been {action_word}.",
            "es": f"¡Listo! Las luces de la {room} están {action_es}.",
            "fr": f"C'est fait! Les lumières du {room} sont {action_fr}."
        }
        return responses.get(language, responses["en"])

    def _get_language_from_request(
        self,
        request_info: Optional[Dict[str, Any]],
    ) -> str:
        """
        Get language from request_info.

        Language must be explicitly provided via scenario configuration.
        No detection or guessing from prompt text.

        Priority:
        1. request_info["LanguageCode"] - explicit language from scenario config
        2. request_info["Locale"] - locale-based (e.g., "en-US" -> "en")

        Args:
            request_info: Request info dict from execution service

        Returns:
            Language code: 'en', 'es', 'fr', etc.

        Raises:
            ValueError: If no language is provided in request_info

        Example:
            >>> info = {"LanguageCode": "es-ES", "Prompt": "..."}
            >>> lang = client._get_language_from_request(info)
            >>> print(lang)  # "es"
        """
        if request_info:
            # Check for explicit LanguageCode (Houndify API format)
            lang_code = request_info.get("LanguageCode")
            if lang_code:
                # Convert "es-ES" to "es", "en-US" to "en", etc.
                return lang_code.split("-")[0].lower()

            # Check for Locale as alternative
            locale = request_info.get("Locale")
            if locale:
                return locale.split("-")[0].lower()

        # No language provided - fail explicitly
        raise ValueError(
            "LanguageCode must be provided in request_info. "
            "Ensure scenario variant includes language configuration."
        )

    def _get_translation(self, key: str, language: str) -> str:
        """
        Get translated response for a given key and language.

        Args:
            key: Translation key
            language: Language code ('en', 'es', 'fr')

        Returns:
            Translated string
        """
        translations = {
            "which_restaurant": {
                "en": "Sure! Which restaurant would you like?",
                "es": "¡Claro! ¿Qué restaurante te gustaría?",
                "fr": "Bien sûr! Quel restaurant souhaitez-vous?"
            },
            "what_date_time": {
                "en": "Great! What date and time?",
                "es": "¡Genial! ¿Qué fecha y hora?",
                "fr": "Super! Quelle date et heure?"
            },
            "how_many_people": {
                "en": "How many people?",
                "es": "¿Cuántas personas?",
                "fr": "Combien de personnes?"
            },
            "reservation_summary": {
                "en": "Perfect! I've reserved a table for {party_size} at {restaurant} {date} at {time}. Would you like to confirm?",
                "es": "¡Perfecto! He reservado una mesa para {party_size} en {restaurant} {date} a las {time}. ¿Quieres confirmar?",
                "fr": "Parfait! J'ai réservé une table pour {party_size} au {restaurant} {date} à {time}. Voulez-vous confirmer?"
            },
            "reservation_confirmed": {
                "en": "Your reservation is confirmed. Confirmation number is #12345",
                "es": "Tu reserva está confirmada. Número de confirmación es #12345",
                "fr": "Votre réservation est confirmée. Numéro de confirmation: #12345"
            }
        }

        return translations.get(key, {}).get(language, translations.get(key, {}).get("en", ""))
