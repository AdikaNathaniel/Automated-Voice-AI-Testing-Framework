"""
Speech-to-Text Service using faster-whisper.

This service provides local speech-to-text transcription using the faster-whisper
library, which is a reimplementation of OpenAI's Whisper model using CTranslate2.

Key features:
- 4x faster than OpenAI's original Whisper implementation
- Runs locally (no API costs, no latency, no rate limits)
- Supports both CPU and GPU (CUDA) execution
- INT8/FP16 quantization for efficiency
- Word-level timestamps available
- Multi-language support with automatic language detection

Model sizes (approximate):
- tiny: 39M parameters, fastest, lower accuracy
- base: 74M parameters, good balance for quick transcriptions
- small: 244M parameters, better accuracy
- medium: 769M parameters, high accuracy
- large-v3: 1.55B parameters, best accuracy
- turbo: Optimized large-v3, best speed/accuracy tradeoff
"""

import io
import logging
import os
import tempfile
from dataclasses import dataclass
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class TranscriptionSegment:
    """A segment of transcribed text with timing information."""

    text: str
    start: float  # seconds
    end: float  # seconds
    words: Optional[List[dict]] = None  # Word-level timestamps if available


@dataclass
class TranscriptionResult:
    """Complete transcription result with metadata."""

    text: str
    language: str
    language_probability: float
    duration_seconds: float
    segments: List[TranscriptionSegment]

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "text": self.text,
            "language": self.language,
            "confidence": self.language_probability,
            "duration_seconds": self.duration_seconds,
            "segments": [
                {
                    "text": seg.text,
                    "start": seg.start,
                    "end": seg.end,
                    "words": seg.words,
                }
                for seg in self.segments
            ],
        }


class STTService:
    """
    Local speech-to-text service using faster-whisper.

    This service wraps the faster-whisper library to provide efficient
    local transcription without requiring external API calls.

    Example:
        >>> stt = STTService(model_size="base")
        >>> result = stt.transcribe(audio_bytes, language="en")
        >>> print(result.text)
        "What's the weather like today?"
    """

    # Valid model sizes
    VALID_MODEL_SIZES = ["tiny", "base", "small", "medium", "large-v3", "turbo"]

    # Language code mappings (ISO 639-1 to Whisper language names)
    LANGUAGE_MAP = {
        "en": "english",
        "es": "spanish",
        "fr": "french",
        "de": "german",
        "it": "italian",
        "pt": "portuguese",
        "ja": "japanese",
        "ko": "korean",
        "zh": "chinese",
        "ar": "arabic",
        "hi": "hindi",
        "ru": "russian",
    }

    def __init__(
        self,
        model_size: str = None,
        device: str = None,
        compute_type: str = None,
        download_root: str = None,
    ):
        """
        Initialize the STT service.

        Args:
            model_size: Whisper model size. Options: tiny, base, small, medium,
                       large-v3, turbo. Defaults to STT_MODEL_SIZE env var or "base".
            device: Device to use. Options: "cpu", "cuda", "auto".
                   Defaults to STT_DEVICE env var or "auto".
            compute_type: Computation type. Options: "int8", "float16", "float32".
                         Auto-selected based on device if not specified.
            download_root: Directory to cache models. Defaults to STT_DOWNLOAD_ROOT
                          env var or system default.
        """
        # Read from environment or use defaults
        self.model_size = model_size or os.getenv("STT_MODEL_SIZE", "base")
        self.device = device or os.getenv("STT_DEVICE", "auto")
        self.download_root = download_root or os.getenv("STT_DOWNLOAD_ROOT")

        # Validate model size
        if self.model_size not in self.VALID_MODEL_SIZES:
            raise ValueError(
                f"Invalid model_size '{self.model_size}'. "
                f"Valid options: {self.VALID_MODEL_SIZES}"
            )

        # Determine compute type based on device
        if compute_type:
            self.compute_type = compute_type
        elif self.device == "cuda":
            self.compute_type = "float16"  # Best for GPU
        else:
            self.compute_type = "int8"  # Best for CPU

        self._model = None
        logger.info(
            f"STT Service initialized: model={self.model_size}, "
            f"device={self.device}, compute_type={self.compute_type}"
        )

    @property
    def model(self):
        """Lazy-load the Whisper model on first use."""
        if self._model is None:
            self._load_model()
        return self._model

    def _load_model(self):
        """Load the Whisper model."""
        try:
            from faster_whisper import WhisperModel

            logger.info(f"Loading Whisper model '{self.model_size}'...")

            kwargs = {
                "model_size_or_path": self.model_size,
                "device": self.device if self.device != "auto" else "auto",
                "compute_type": self.compute_type,
            }

            if self.download_root:
                kwargs["download_root"] = self.download_root

            self._model = WhisperModel(**kwargs)
            logger.info(f"Whisper model '{self.model_size}' loaded successfully")

        except ImportError:
            raise ImportError(
                "faster-whisper is not installed. "
                "Install with: pip install faster-whisper"
            )
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise

    def transcribe(
        self,
        audio_bytes: bytes,
        language: str = None,
        beam_size: int = 5,
        word_timestamps: bool = True,
        vad_filter: bool = True,
    ) -> TranscriptionResult:
        """
        Transcribe audio to text.

        Args:
            audio_bytes: Audio data in any format supported by PyAV
                        (WAV, MP3, FLAC, OGG, etc.)
            language: ISO 639-1 language code (e.g., "en", "es", "fr").
                     If None, language is auto-detected.
            beam_size: Beam size for decoding (higher = better quality, slower).
                      Default: 5.
            word_timestamps: Whether to include word-level timestamps.
                            Default: True.
            vad_filter: Whether to use Voice Activity Detection to filter
                       non-speech segments. Default: True.

        Returns:
            TranscriptionResult with text, language, confidence, and segments.

        Raises:
            ValueError: If audio is invalid or cannot be processed.
        """
        if not audio_bytes:
            raise ValueError("Audio data is empty")

        # Map language code if provided
        whisper_language = None
        if language:
            # Strip region code if present (en-US -> en)
            lang_code = language.split("-")[0].lower()
            whisper_language = self.LANGUAGE_MAP.get(lang_code, lang_code)

        # Write to temp file (faster-whisper works with file paths)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_path = tmp_file.name
            tmp_file.write(audio_bytes)

        try:
            # Transcribe
            segments, info = self.model.transcribe(
                tmp_path,
                language=whisper_language,
                beam_size=beam_size,
                word_timestamps=word_timestamps,
                vad_filter=vad_filter,
            )

            # Collect segments
            transcription_segments = []
            full_text_parts = []

            for segment in segments:
                seg_text = segment.text.strip()
                if seg_text:
                    full_text_parts.append(seg_text)

                    # Extract word-level timestamps if available
                    words = None
                    if word_timestamps and hasattr(segment, "words") and segment.words:
                        words = [
                            {
                                "word": w.word,
                                "start": w.start,
                                "end": w.end,
                                "probability": w.probability,
                            }
                            for w in segment.words
                        ]

                    transcription_segments.append(
                        TranscriptionSegment(
                            text=seg_text,
                            start=segment.start,
                            end=segment.end,
                            words=words,
                        )
                    )

            # Combine full text
            full_text = " ".join(full_text_parts)

            return TranscriptionResult(
                text=full_text,
                language=info.language,
                language_probability=info.language_probability,
                duration_seconds=info.duration,
                segments=transcription_segments,
            )

        finally:
            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    def transcribe_async(
        self,
        audio_bytes: bytes,
        language: str = None,
        **kwargs,
    ) -> TranscriptionResult:
        """
        Async-compatible transcription (runs in thread pool).

        For true async operation in FastAPI, run this in a thread pool executor:

        Example:
            import asyncio
            result = await asyncio.get_event_loop().run_in_executor(
                None, stt.transcribe, audio_bytes
            )
        """
        # faster-whisper is synchronous, so this is just a wrapper
        return self.transcribe(audio_bytes, language=language, **kwargs)

    def detect_language(self, audio_bytes: bytes) -> Tuple[str, float]:
        """
        Detect the language of audio without full transcription.

        Args:
            audio_bytes: Audio data to analyze.

        Returns:
            Tuple of (language_code, probability).
        """
        # Do a quick transcription with minimal beam size
        result = self.transcribe(audio_bytes, beam_size=1, word_timestamps=False)
        return result.language, result.language_probability

    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes."""
        return list(self.LANGUAGE_MAP.keys())

    def is_model_loaded(self) -> bool:
        """Check if the model is loaded."""
        return self._model is not None


# Singleton instance for reuse across requests
_stt_service_instance: Optional[STTService] = None


def get_stt_service() -> STTService:
    """
    Get or create the singleton STT service instance.

    This function provides a singleton instance for efficiency, as loading
    the Whisper model is expensive and should only be done once.

    Returns:
        STTService instance.
    """
    global _stt_service_instance
    if _stt_service_instance is None:
        _stt_service_instance = STTService()
    return _stt_service_instance
