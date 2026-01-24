"""
Text-to-Speech Service (TASK-112)

This module provides text-to-speech functionality for the Voice AI Testing Framework.
It uses gTTS (Google Text-to-Speech) as the primary TTS engine with caching to avoid
regenerating the same audio multiple times.

Features:
- Text-to-speech conversion using gTTS
- Support for multiple languages
- Caching of generated audio to disk
- Cache key generation based on text and language
- Automatic cache directory creation

Note: SoundHound TTS requires a paid Houndify account, so gTTS is used as the fallback.

Example:
    >>> tts = TTSService()
    >>> audio_bytes = tts.text_to_speech("Hello, world!", lang="en")
    >>> # audio_bytes contains MP3 audio data
    >>> # Subsequent calls with same text will use cached audio
"""

import io
import hashlib
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from gtts import gTTS

logger = logging.getLogger(__name__)


@dataclass
class TTSAudioResult:
    """Container for synthesized audio bytes and cache metadata."""

    audio_bytes: bytes
    cache_key: str
    cache_path: Path
    cache_hit: bool
    audio_format: str
    sample_rate: int


class TTSService:
    """
    Text-to-Speech service using gTTS with caching.

    This service converts text to speech audio using Google's text-to-speech engine.
    Generated audio is cached to disk to avoid regenerating the same audio,
    which improves performance and reduces API calls.

    Attributes:
        cache_dir: Directory path where cached audio files are stored
        default_lang: Default language code for TTS (default: 'en')

    Example:
        >>> tts = TTSService()
        >>> audio = tts.text_to_speech("Hello world")
        >>> # Returns audio bytes in MP3 format
        >>>
        >>> # Use with different language
        >>> audio_es = tts.text_to_speech("Hola mundo", lang="es")
    """

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize the TTS service.

        Args:
            cache_dir: Directory for caching audio files. If None, uses
                      './tts_cache' in the current directory.
        """
        if cache_dir is None:
            # Use default cache directory in /tmp (writable by non-root users)
            cache_dir = Path("/tmp/tts_cache")

        self.cache_dir = Path(cache_dir)
        self.default_lang = "en"
        self.default_audio_format = "mp3"
        # gTTS outputs 22.05 kHz MP3 audio by default
        self.default_sample_rate = 22050

        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"TTSService initialized with cache_dir: {self.cache_dir}")

    def synthesize(self, text: str, lang: str = "en") -> TTSAudioResult:
        """Generate speech audio and return cache metadata."""
        audio_bytes, cache_key, cache_file, cache_hit = self._synthesize_with_cache(text, lang)
        return TTSAudioResult(
            audio_bytes=audio_bytes,
            cache_key=cache_key,
            cache_path=cache_file,
            cache_hit=cache_hit,
            audio_format=self.default_audio_format,
            sample_rate=self.default_sample_rate,
        )

    def text_to_speech(self, text: str, lang: str = "en") -> bytes:
        """
        Convert text to speech audio.

        This method generates audio from text using gTTS. The generated audio
        is cached to disk based on a hash of the text and language. If the
        same text is requested again, the cached audio is returned instead of
        regenerating it.

        Args:
            text: The text to convert to speech
            lang: Language code (ISO 639-1, e.g., 'en', 'es', 'fr', 'de')
                 Default is 'en' (English)

        Returns:
            bytes: Audio data in MP3 format

        Raises:
            ValueError: If text is empty or None
            RuntimeError: If TTS generation fails

        Example:
            >>> tts = TTSService()
            >>> audio = tts.text_to_speech("Good morning!")
            >>> len(audio) > 0  # True, audio was generated
            >>>
            >>> # Different language
            >>> audio_fr = tts.text_to_speech("Bonjour!", lang="fr")
        """
        result = self.synthesize(text, lang)
        return result.audio_bytes

    def _synthesize_with_cache(self, text: str, lang: str) -> tuple[bytes, str, Path, bool]:
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        cache_key = self._generate_cache_key(text, lang)
        cache_file = self.cache_dir / f"{cache_key}.mp3"
        cache_hit = cache_file.exists()

        if cache_hit:
            logger.debug(f"Using cached audio for text: '{text[:50]}...' (lang={lang})")
            with open(cache_file, 'rb') as f:
                audio_bytes = f.read()
            return audio_bytes, cache_key, cache_file, True

        logger.info(f"Generating TTS audio for text: '{text[:50]}...' (lang={lang})")

        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            audio_bytes = audio_buffer.read()

            with open(cache_file, 'wb') as f:
                f.write(audio_bytes)

            logger.debug(f"Cached audio to {cache_file}")
            return audio_bytes, cache_key, cache_file, False

        except Exception as e:
            logger.error(f"Failed to generate TTS audio: {e}")
            raise RuntimeError(f"Text-to-speech generation failed: {str(e)}") from e

    def _generate_cache_key(self, text: str, lang: str) -> str:
        """
        Generate a cache key for the given text and language.

        The cache key is a SHA256 hash of the text and language combined,
        which ensures unique cache files for different text/language pairs
        while keeping filenames manageable.

        Args:
            text: The text to hash
            lang: The language code to hash

        Returns:
            str: Hexadecimal hash string to use as cache key

        Example:
            >>> tts = TTSService()
            >>> key1 = tts._generate_cache_key("hello", "en")
            >>> key2 = tts._generate_cache_key("hello", "en")
            >>> key1 == key2  # True, same text and language
            >>>
            >>> key3 = tts._generate_cache_key("hello", "es")
            >>> key1 == key3  # False, different language
        """
        # Combine text and language for hashing
        cache_input = f"{text}:{lang}"

        # Generate SHA256 hash
        hash_obj = hashlib.sha256(cache_input.encode('utf-8'))
        cache_key = hash_obj.hexdigest()

        logger.debug(f"Generated cache key: {cache_key} for '{text[:30]}...' (lang={lang})")

        return cache_key

    def clear_cache(self) -> int:
        """
        Clear all cached audio files.

        This method removes all MP3 files from the cache directory.
        Useful for freeing up disk space or forcing regeneration of audio.

        Returns:
            int: Number of cache files deleted

        Example:
            >>> tts = TTSService()
            >>> tts.text_to_speech("Test")  # Creates cache file
            >>> deleted = tts.clear_cache()
            >>> deleted >= 1  # True, at least one file deleted
        """
        deleted_count = 0

        for cache_file in self.cache_dir.glob("*.mp3"):
            try:
                cache_file.unlink()
                deleted_count += 1
            except Exception as e:
                logger.warning(f"Failed to delete cache file {cache_file}: {e}")

        logger.info(f"Cleared {deleted_count} cache files from {self.cache_dir}")

        return deleted_count

    def get_cache_size(self) -> int:
        """
        Get the number of files currently in the cache.

        Returns:
            int: Number of cached audio files

        Example:
            >>> tts = TTSService()
            >>> initial_size = tts.get_cache_size()
            >>> tts.text_to_speech("New text")
            >>> new_size = tts.get_cache_size()
            >>> new_size == initial_size + 1  # True if text was not cached
        """
        cache_files = list(self.cache_dir.glob("*.mp3"))
        return len(cache_files)
