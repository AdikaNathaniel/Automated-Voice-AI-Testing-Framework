"""
Test suite for Text-to-Speech service (TASK-112)

Validates the TTS service implementation:
- TTSService class with text-to-speech functionality
- Support for multiple languages
- Caching of generated audio to avoid regeneration
- Error handling for invalid inputs
- Fallback to gTTS (since SoundHound TTS requires paid account)
"""

import pytest
from pathlib import Path
import hashlib

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
SERVICES_DIR = BACKEND_DIR / "services"
TTS_SERVICE_FILE = SERVICES_DIR / "tts_service.py"


class TestTTSServiceFileStructure:
    """Test tts_service.py file structure"""

    def test_tts_service_file_exists(self):
        """Test that tts_service.py exists"""
        assert TTS_SERVICE_FILE.exists(), "tts_service.py should exist"
        assert TTS_SERVICE_FILE.is_file(), "tts_service.py should be a file"

    def test_tts_service_has_content(self):
        """Test that tts_service.py has content"""
        content = TTS_SERVICE_FILE.read_text()
        assert len(content) > 0, "tts_service.py should not be empty"


class TestTTSServiceImports:
    """Test necessary imports in tts_service.py"""

    @pytest.fixture
    def tts_service_content(self):
        """Load tts_service.py content"""
        return TTS_SERVICE_FILE.read_text()

    def test_imports_gtts(self, tts_service_content):
        """Test that gTTS is imported"""
        assert "from gtts import gTTS" in tts_service_content or "import gtts" in tts_service_content, \
            "Should import gTTS for text-to-speech"

    def test_imports_io(self, tts_service_content):
        """Test that io is imported for BytesIO"""
        assert "import io" in tts_service_content or "from io import" in tts_service_content, \
            "Should import io for BytesIO"

    def test_imports_hashlib(self, tts_service_content):
        """Test that hashlib is imported for caching"""
        assert "import hashlib" in tts_service_content or "from hashlib import" in tts_service_content, \
            "Should import hashlib for cache key generation"

    def test_imports_pathlib_or_os(self, tts_service_content):
        """Test that pathlib or os is imported for file operations"""
        has_path_lib = "from pathlib import" in tts_service_content or "import pathlib" in tts_service_content
        has_os = "import os" in tts_service_content
        assert has_path_lib or has_os, \
            "Should import pathlib or os for file operations"


class TestTTSServiceClass:
    """Test TTSService class definition"""

    @pytest.fixture
    def tts_service_content(self):
        """Load tts_service.py content"""
        return TTS_SERVICE_FILE.read_text()

    def test_has_tts_service_class(self, tts_service_content):
        """Test that TTSService class exists"""
        assert "class TTSService" in tts_service_content, \
            "Should have TTSService class"

    def test_has_init_method(self, tts_service_content):
        """Test that __init__ method exists"""
        assert "def __init__" in tts_service_content, \
            "Should have __init__ method"

    def test_has_cache_dir_attribute(self, tts_service_content):
        """Test that cache_dir attribute exists"""
        assert "cache_dir" in tts_service_content, \
            "Should have cache_dir attribute for caching"

    def test_has_docstring(self, tts_service_content):
        """Test that TTSService has docstring"""
        lines = tts_service_content.split('\n')
        in_class = False
        has_docstring = False

        for i, line in enumerate(lines):
            if 'class TTSService' in line:
                in_class = True
            elif in_class:
                if '"""' in line or "'''" in line:
                    has_docstring = True
                    break
                elif line.strip() and not line.strip().startswith('#'):
                    if not line.strip().startswith('class'):
                        break

        assert has_docstring, "TTSService should have docstring"


class TestTextToSpeechMethod:
    """Test text_to_speech method"""

    @pytest.fixture
    def tts_service_content(self):
        """Load tts_service.py content"""
        return TTS_SERVICE_FILE.read_text()

    def test_has_text_to_speech_method(self, tts_service_content):
        """Test that text_to_speech method exists"""
        assert "def text_to_speech" in tts_service_content, \
            "Should have text_to_speech method"

    def test_text_to_speech_has_text_param(self, tts_service_content):
        """Test that text_to_speech has text parameter"""
        lines = tts_service_content.split('\n')
        for i, line in enumerate(lines):
            if 'def text_to_speech' in line:
                func_def = ''.join(lines[i:min(i+5, len(lines))])
                assert 'text' in func_def, \
                    "text_to_speech should have text parameter"
                break

    def test_text_to_speech_has_language_param(self, tts_service_content):
        """Test that text_to_speech has language parameter"""
        lines = tts_service_content.split('\n')
        for i, line in enumerate(lines):
            if 'def text_to_speech' in line:
                func_def = ''.join(lines[i:min(i+5, len(lines))])
                assert 'lang' in func_def or 'language' in func_def, \
                    "text_to_speech should have language parameter"
                break

    def test_text_to_speech_returns_bytes(self, tts_service_content):
        """Test that text_to_speech return type is bytes"""
        assert "-> bytes" in tts_service_content, \
            "text_to_speech should return bytes"

    def test_text_to_speech_has_docstring(self, tts_service_content):
        """Test that text_to_speech has docstring"""
        lines = tts_service_content.split('\n')
        in_method = False
        has_docstring = False
        lines_checked = 0

        for i, line in enumerate(lines):
            if 'def text_to_speech' in line:
                in_method = True
            elif in_method:
                lines_checked += 1
                if '"""' in line or "'''" in line:
                    has_docstring = True
                    break
                elif lines_checked > 10:
                    break

        assert has_docstring, "text_to_speech should have docstring"


class TestCachingFunctionality:
    """Test caching functionality"""

    @pytest.fixture
    def tts_service_content(self):
        """Load tts_service.py content"""
        return TTS_SERVICE_FILE.read_text()

    def test_has_cache_key_generation(self, tts_service_content):
        """Test that cache key generation is implemented"""
        # Should use hashlib for generating cache keys
        assert "hashlib" in tts_service_content, \
            "Should use hashlib for cache key generation"

    def test_has_cache_file_check(self, tts_service_content):
        """Test that cache file existence check is implemented"""
        # Should check if cached file exists
        has_exists_check = ".exists()" in tts_service_content or "os.path.exists" in tts_service_content
        assert has_exists_check, \
            "Should check if cached file exists"

    def test_has_cache_read(self, tts_service_content):
        """Test that cache reading is implemented"""
        # Should read from cache if it exists
        has_read = "read" in tts_service_content or "open" in tts_service_content
        assert has_read, \
            "Should read from cache file"

    def test_has_cache_write(self, tts_service_content):
        """Test that cache writing is implemented"""
        # Should write to cache after generation
        has_write = "write" in tts_service_content or "open" in tts_service_content
        assert has_write, \
            "Should write to cache file"


class TestTTSServiceImportability:
    """Test that TTS service can be imported"""

    def test_can_import_tts_service_module(self):
        """Test that tts_service module can be imported"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from services import tts_service
            assert tts_service is not None, \
                "tts_service module should be importable"
        except ImportError as e:
            pytest.fail(f"Cannot import tts_service: {e}")

    def test_can_import_tts_service_class(self):
        """Test that TTSService class can be imported"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from services.tts_service import TTSService
            assert TTSService is not None, \
                "TTSService class should be importable"
        except ImportError as e:
            pytest.fail(f"Cannot import TTSService: {e}")

    def test_can_instantiate_tts_service(self):
        """Test that TTSService can be instantiated"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from services.tts_service import TTSService
            service = TTSService()
            assert service is not None, \
                "Should be able to instantiate TTSService"
        except Exception as e:
            pytest.fail(f"Cannot instantiate TTSService: {e}")


class TestTextToSpeechFunctionality:
    """Test text_to_speech functionality"""

    def test_text_to_speech_returns_bytes(self):
        """Test that text_to_speech returns bytes"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        from services.tts_service import TTSService

        service = TTSService()
        result = service.text_to_speech("Hello, world!")

        assert isinstance(result, bytes), "Should return bytes"
        assert len(result) > 0, "Should return non-empty bytes"

    def test_text_to_speech_generates_valid_audio(self):
        """Test that text_to_speech generates valid audio"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        from services.tts_service import TTSService
        from services.audio_utils import validate_audio_format

        service = TTSService()
        audio = service.text_to_speech("This is a test.")

        # Validate the generated audio is in a valid format
        is_valid = validate_audio_format(audio)
        assert is_valid, "Generated audio should be in valid format"

    def test_text_to_speech_with_different_languages(self):
        """Test that text_to_speech works with different languages"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        from services.tts_service import TTSService

        service = TTSService()

        # English
        audio_en = service.text_to_speech("Hello", lang="en")
        assert isinstance(audio_en, bytes)
        assert len(audio_en) > 0

        # Spanish
        audio_es = service.text_to_speech("Hola", lang="es")
        assert isinstance(audio_es, bytes)
        assert len(audio_es) > 0

    def test_text_to_speech_with_empty_text(self):
        """Test that text_to_speech handles empty text"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        from services.tts_service import TTSService

        service = TTSService()

        # Should raise ValueError for empty text
        with pytest.raises(ValueError):
            service.text_to_speech("")


class TestCachingBehavior:
    """Test caching behavior"""

    def test_caching_same_text_returns_same_audio(self):
        """Test that caching returns same audio for same text"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        from services.tts_service import TTSService

        service = TTSService()
        text = "Test caching functionality"

        # Generate audio twice
        audio1 = service.text_to_speech(text)
        audio2 = service.text_to_speech(text)

        # Should be identical (from cache)
        assert audio1 == audio2, "Cached audio should be identical"

    def test_caching_different_text_returns_different_audio(self):
        """Test that different text returns different audio"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        from services.tts_service import TTSService

        service = TTSService()

        audio1 = service.text_to_speech("First text")
        audio2 = service.text_to_speech("Second text")

        # Should be different
        assert audio1 != audio2, "Different text should produce different audio"

    def test_caching_different_languages_returns_different_audio(self):
        """Test that same text in different languages returns different audio"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        from services.tts_service import TTSService

        service = TTSService()
        text = "Hello"

        audio_en = service.text_to_speech(text, lang="en")
        audio_es = service.text_to_speech(text, lang="es")

        # Should be different (different language)
        assert audio_en != audio_es, "Different languages should produce different audio"

    def test_cache_files_are_created(self):
        """Test that cache files are created"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        from services.tts_service import TTSService

        service = TTSService()
        text = "Cache file test"

        # Generate audio
        service.text_to_speech(text)

        # Check that cache directory exists
        assert service.cache_dir.exists(), "Cache directory should exist"
        assert service.cache_dir.is_dir(), "Cache directory should be a directory"

        # Check that at least one cache file exists
        cache_files = list(service.cache_dir.glob("*.mp3")) + list(service.cache_dir.glob("*.wav"))
        assert len(cache_files) > 0, "At least one cache file should exist"


class TestTaskRequirements:
    """Test TASK-112 specific requirements"""

    def test_task_112_tts_service_class(self):
        """Test TASK-112 requirement: TTSService class exists"""
        content = TTS_SERVICE_FILE.read_text()
        assert "class TTSService" in content, \
            "TASK-112 requirement: Must have TTSService class"

    def test_task_112_text_to_speech_method(self):
        """Test TASK-112 requirement: text_to_speech method exists"""
        content = TTS_SERVICE_FILE.read_text()
        assert "def text_to_speech" in content, \
            "TASK-112 requirement: Must have text_to_speech method"

    def test_task_112_gtts_fallback(self):
        """Test TASK-112 requirement: Uses gTTS (fallback)"""
        content = TTS_SERVICE_FILE.read_text()
        assert "gTTS" in content or "gtts" in content, \
            "TASK-112 requirement: Must use gTTS for text-to-speech"

    def test_task_112_caching_implemented(self):
        """Test TASK-112 requirement: Caching is implemented"""
        content = TTS_SERVICE_FILE.read_text()
        has_cache = "cache" in content.lower()
        assert has_cache, \
            "TASK-112 requirement: Must implement caching"

    def test_task_112_cache_directory(self):
        """Test TASK-112 requirement: Cache directory is used"""
        content = TTS_SERVICE_FILE.read_text()
        has_cache_dir = "cache_dir" in content or "cache_path" in content
        assert has_cache_dir, \
            "TASK-112 requirement: Must have cache directory"
