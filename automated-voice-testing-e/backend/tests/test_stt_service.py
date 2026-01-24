"""
Tests for the STT (Speech-to-Text) Service using faster-whisper.

These tests verify:
- Service initialization with various configurations
- Transcription functionality
- Language detection
- Error handling
- Singleton pattern
"""

import io
import os
import tempfile
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

from services.stt_service import (
    STTService,
    TranscriptionResult,
    TranscriptionSegment,
    get_stt_service,
)


class TestSTTServiceInit:
    """Test STTService initialization."""

    def test_init_with_defaults(self):
        """Test initialization with default values from environment."""
        with patch.dict(os.environ, {}, clear=True):
            service = STTService()

        assert service.model_size == "base"
        assert service.device == "auto"
        assert service.compute_type == "int8"  # CPU default
        assert service._model is None  # Lazy loading

    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        service = STTService(
            model_size="small",
            device="cuda",
            compute_type="float16",
            download_root="/tmp/models",
        )

        assert service.model_size == "small"
        assert service.device == "cuda"
        assert service.compute_type == "float16"
        assert service.download_root == "/tmp/models"

    def test_init_from_environment(self):
        """Test initialization reads from environment variables."""
        env_vars = {
            "STT_MODEL_SIZE": "medium",
            "STT_DEVICE": "cpu",
            "STT_DOWNLOAD_ROOT": "/custom/path",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            service = STTService()

        assert service.model_size == "medium"
        assert service.device == "cpu"
        assert service.download_root == "/custom/path"

    def test_init_invalid_model_size(self):
        """Test that invalid model size raises ValueError."""
        with pytest.raises(ValueError, match="Invalid model_size"):
            STTService(model_size="invalid")

    def test_valid_model_sizes(self):
        """Test all valid model sizes are accepted."""
        valid_sizes = ["tiny", "base", "small", "medium", "large-v3", "turbo"]
        for size in valid_sizes:
            service = STTService(model_size=size)
            assert service.model_size == size

    def test_compute_type_auto_selection_cuda(self):
        """Test compute type is float16 for CUDA device."""
        service = STTService(model_size="base", device="cuda")
        assert service.compute_type == "float16"

    def test_compute_type_auto_selection_cpu(self):
        """Test compute type is int8 for CPU device."""
        service = STTService(model_size="base", device="cpu")
        assert service.compute_type == "int8"


class TestSTTServiceModelLoading:
    """Test model loading functionality."""

    def test_lazy_model_loading(self):
        """Test that model is lazily loaded on first access."""
        service = STTService()
        assert service._model is None

        # Accessing the model property should trigger loading
        with patch("services.stt_service.STTService._load_model") as mock_load:
            _ = service.model
            mock_load.assert_called_once()

    def test_model_loading_success(self):
        """Test successful model loading."""
        mock_whisper_model = MagicMock()

        # Patch at the point where it's imported inside the method
        with patch.dict(
            "sys.modules",
            {"faster_whisper": MagicMock(WhisperModel=MagicMock(return_value=mock_whisper_model))}
        ):
            service = STTService(model_size="base", device="cpu")
            service._load_model()

            assert service._model == mock_whisper_model

    def test_model_loading_with_download_root(self):
        """Test model loading with custom download root."""
        mock_whisper_model = MagicMock()
        mock_whisper_class = MagicMock(return_value=mock_whisper_model)

        with patch.dict(
            "sys.modules",
            {"faster_whisper": MagicMock(WhisperModel=mock_whisper_class)}
        ):
            service = STTService(
                model_size="base", device="cpu", download_root="/custom/path"
            )
            service._load_model()

            # Verify the call included download_root
            mock_whisper_class.assert_called_once()
            call_kwargs = mock_whisper_class.call_args[1]
            assert call_kwargs["download_root"] == "/custom/path"

    def test_model_loading_import_error(self):
        """Test handling of missing faster-whisper package."""
        service = STTService()

        # Simulate import error by removing the module
        import sys
        original_modules = sys.modules.copy()

        # Remove faster_whisper if it exists
        if "faster_whisper" in sys.modules:
            del sys.modules["faster_whisper"]

        try:
            # Mock the import to raise ImportError
            with patch.dict("sys.modules", {"faster_whisper": None}):
                with pytest.raises(ImportError, match="faster-whisper is not installed"):
                    service._load_model()
        finally:
            # Restore original modules
            sys.modules.update(original_modules)

    def test_is_model_loaded(self):
        """Test is_model_loaded method."""
        service = STTService()
        assert service.is_model_loaded() is False

        service._model = MagicMock()
        assert service.is_model_loaded() is True


class TestTranscription:
    """Test transcription functionality."""

    @pytest.fixture
    def mock_service(self):
        """Create a service with mocked model."""
        service = STTService()

        # Create mock segment
        mock_segment = MagicMock()
        mock_segment.text = " Hello world "
        mock_segment.start = 0.0
        mock_segment.end = 1.5
        mock_segment.words = [
            MagicMock(word="Hello", start=0.0, end=0.5, probability=0.95),
            MagicMock(word="world", start=0.6, end=1.5, probability=0.92),
        ]

        # Create mock info
        mock_info = MagicMock()
        mock_info.language = "en"
        mock_info.language_probability = 0.98
        mock_info.duration = 1.5

        # Create mock model
        mock_model = MagicMock()
        mock_model.transcribe.return_value = ([mock_segment], mock_info)
        service._model = mock_model

        return service

    def test_transcribe_success(self, mock_service):
        """Test successful transcription."""
        audio_bytes = b"fake audio data"

        with patch("tempfile.NamedTemporaryFile") as mock_temp:
            mock_temp.return_value.__enter__.return_value.name = "/tmp/test.wav"
            with patch("os.unlink"):
                result = mock_service.transcribe(audio_bytes)

        assert isinstance(result, TranscriptionResult)
        assert result.text == "Hello world"
        assert result.language == "en"
        assert result.language_probability == 0.98
        assert result.duration_seconds == 1.5
        assert len(result.segments) == 1

    def test_transcribe_with_language(self, mock_service):
        """Test transcription with specified language."""
        audio_bytes = b"fake audio data"

        with patch("tempfile.NamedTemporaryFile") as mock_temp:
            mock_temp.return_value.__enter__.return_value.name = "/tmp/test.wav"
            with patch("os.unlink"):
                mock_service.transcribe(audio_bytes, language="es")

        # Verify language was passed to model
        mock_service._model.transcribe.assert_called_once()
        call_kwargs = mock_service._model.transcribe.call_args[1]
        assert call_kwargs["language"] == "spanish"

    def test_transcribe_with_region_code(self, mock_service):
        """Test that region codes are stripped (en-US -> en)."""
        audio_bytes = b"fake audio data"

        with patch("tempfile.NamedTemporaryFile") as mock_temp:
            mock_temp.return_value.__enter__.return_value.name = "/tmp/test.wav"
            with patch("os.unlink"):
                mock_service.transcribe(audio_bytes, language="en-US")

        call_kwargs = mock_service._model.transcribe.call_args[1]
        assert call_kwargs["language"] == "english"

    def test_transcribe_empty_audio_raises(self):
        """Test that empty audio raises ValueError."""
        service = STTService()
        with pytest.raises(ValueError, match="Audio data is empty"):
            service.transcribe(b"")

    def test_transcribe_none_audio_raises(self):
        """Test that None audio raises ValueError."""
        service = STTService()
        with pytest.raises(ValueError, match="Audio data is empty"):
            service.transcribe(None)

    def test_transcribe_with_vad_filter(self, mock_service):
        """Test transcription with VAD filter enabled."""
        audio_bytes = b"fake audio data"

        with patch("tempfile.NamedTemporaryFile") as mock_temp:
            mock_temp.return_value.__enter__.return_value.name = "/tmp/test.wav"
            with patch("os.unlink"):
                mock_service.transcribe(audio_bytes, vad_filter=True)

        call_kwargs = mock_service._model.transcribe.call_args[1]
        assert call_kwargs["vad_filter"] is True

    def test_transcribe_word_timestamps(self, mock_service):
        """Test that word timestamps are included."""
        audio_bytes = b"fake audio data"

        with patch("tempfile.NamedTemporaryFile") as mock_temp:
            mock_temp.return_value.__enter__.return_value.name = "/tmp/test.wav"
            with patch("os.unlink"):
                result = mock_service.transcribe(audio_bytes, word_timestamps=True)

        assert result.segments[0].words is not None
        assert len(result.segments[0].words) == 2
        assert result.segments[0].words[0]["word"] == "Hello"


class TestTranscriptionResult:
    """Test TranscriptionResult data class."""

    def test_to_dict(self):
        """Test conversion to dictionary."""
        segment = TranscriptionSegment(
            text="Hello",
            start=0.0,
            end=1.0,
            words=[{"word": "Hello", "start": 0.0, "end": 1.0, "probability": 0.95}],
        )
        result = TranscriptionResult(
            text="Hello",
            language="en",
            language_probability=0.98,
            duration_seconds=1.0,
            segments=[segment],
        )

        d = result.to_dict()

        assert d["text"] == "Hello"
        assert d["language"] == "en"
        assert d["confidence"] == 0.98
        assert d["duration_seconds"] == 1.0
        assert len(d["segments"]) == 1
        assert d["segments"][0]["text"] == "Hello"


class TestLanguageDetection:
    """Test language detection functionality."""

    def test_detect_language(self):
        """Test language detection."""
        service = STTService()

        # Mock the transcribe method
        mock_result = TranscriptionResult(
            text="Hola mundo",
            language="es",
            language_probability=0.95,
            duration_seconds=1.0,
            segments=[],
        )

        with patch.object(service, "transcribe", return_value=mock_result):
            lang, prob = service.detect_language(b"fake audio")

        assert lang == "es"
        assert prob == 0.95

    def test_get_supported_languages(self):
        """Test getting list of supported languages."""
        service = STTService()
        languages = service.get_supported_languages()

        assert "en" in languages
        assert "es" in languages
        assert "fr" in languages
        assert "de" in languages
        assert len(languages) > 5


class TestSingleton:
    """Test singleton pattern."""

    def test_get_stt_service_singleton(self):
        """Test that get_stt_service returns singleton."""
        import services.stt_service as module

        # Reset singleton
        module._stt_service_instance = None

        service1 = get_stt_service()
        service2 = get_stt_service()

        assert service1 is service2

    def test_get_stt_service_creates_instance(self):
        """Test that get_stt_service creates instance if none exists."""
        import services.stt_service as module

        # Reset singleton
        module._stt_service_instance = None

        service = get_stt_service()

        assert service is not None
        assert isinstance(service, STTService)


class TestLanguageMapping:
    """Test language code mapping."""

    def test_language_map_coverage(self):
        """Test that common languages are mapped."""
        service = STTService()

        expected_languages = [
            "en", "es", "fr", "de", "it", "pt",
            "ja", "ko", "zh", "ar", "hi", "ru",
        ]

        for lang in expected_languages:
            assert lang in service.LANGUAGE_MAP, f"Missing language: {lang}"
