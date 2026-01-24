"""
Test suite for audio utilities (TASK-111)

Validates the audio utility functions:
- convert_to_pcm: Convert audio to PCM format at target sample rate
- add_noise: Add noise to audio at specified SNR
- validate_audio_format: Check if audio format is valid
- get_audio_duration: Get duration of audio in seconds
"""

import pytest
import numpy as np
from pathlib import Path
import io
import wave

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
SERVICES_DIR = BACKEND_DIR / "services"
AUDIO_UTILS_FILE = SERVICES_DIR / "audio_utils.py"


class TestAudioUtilsFileStructure:
    """Test audio_utils.py file structure"""

    def test_services_directory_exists(self):
        """Test that services directory exists"""
        assert SERVICES_DIR.exists(), "backend/services directory should exist"
        assert SERVICES_DIR.is_dir(), "services should be a directory"

    def test_audio_utils_file_exists(self):
        """Test that audio_utils.py exists"""
        assert AUDIO_UTILS_FILE.exists(), "audio_utils.py should exist"
        assert AUDIO_UTILS_FILE.is_file(), "audio_utils.py should be a file"

    def test_audio_utils_has_content(self):
        """Test that audio_utils.py has content"""
        content = AUDIO_UTILS_FILE.read_text()
        assert len(content) > 0, "audio_utils.py should not be empty"


class TestAudioUtilsImports:
    """Test necessary imports in audio_utils.py"""

    @pytest.fixture
    def audio_utils_content(self):
        """Load audio_utils.py content"""
        return AUDIO_UTILS_FILE.read_text()

    def test_imports_io(self, audio_utils_content):
        """Test that io is imported for BytesIO"""
        assert "import io" in audio_utils_content or "from io import" in audio_utils_content, \
            "Should import io for BytesIO"

    def test_imports_numpy(self, audio_utils_content):
        """Test that numpy is imported"""
        assert "import numpy" in audio_utils_content or "from numpy import" in audio_utils_content, \
            "Should import numpy for array operations"

    def test_imports_soundfile(self, audio_utils_content):
        """Test that soundfile is imported"""
        assert "import soundfile" in audio_utils_content or "from soundfile import" in audio_utils_content, \
            "Should import soundfile for audio I/O"


class TestConvertToPcmFunction:
    """Test convert_to_pcm function"""

    @pytest.fixture
    def audio_utils_content(self):
        """Load audio_utils.py content"""
        return AUDIO_UTILS_FILE.read_text()

    def test_has_convert_to_pcm_function(self, audio_utils_content):
        """Test that convert_to_pcm function exists"""
        assert "def convert_to_pcm" in audio_utils_content, \
            "Should have convert_to_pcm function"

    def test_convert_to_pcm_has_audio_bytes_param(self, audio_utils_content):
        """Test that convert_to_pcm has audio_bytes parameter"""
        lines = audio_utils_content.split('\n')
        for i, line in enumerate(lines):
            if 'def convert_to_pcm' in line:
                func_def = ''.join(lines[i:min(i+5, len(lines))])
                assert 'audio_bytes' in func_def, \
                    "convert_to_pcm should have audio_bytes parameter"
                break

    def test_convert_to_pcm_has_target_rate_param(self, audio_utils_content):
        """Test that convert_to_pcm has target_rate parameter"""
        lines = audio_utils_content.split('\n')
        for i, line in enumerate(lines):
            if 'def convert_to_pcm' in line:
                func_def = ''.join(lines[i:min(i+5, len(lines))])
                assert 'target_rate' in func_def, \
                    "convert_to_pcm should have target_rate parameter"
                break

    def test_convert_to_pcm_returns_bytes(self, audio_utils_content):
        """Test that convert_to_pcm return type annotation is bytes"""
        assert "-> bytes" in audio_utils_content or "Returns:\n        bytes" in audio_utils_content, \
            "convert_to_pcm should return bytes"

    def test_convert_to_pcm_has_docstring(self, audio_utils_content):
        """Test that convert_to_pcm has docstring"""
        lines = audio_utils_content.split('\n')
        in_function = False
        has_docstring = False
        lines_checked = 0

        for i, line in enumerate(lines):
            if 'def convert_to_pcm' in line:
                in_function = True
            elif in_function:
                lines_checked += 1
                if '"""' in line or "'''" in line:
                    has_docstring = True
                    break
                elif lines_checked > 10:
                    break

        assert has_docstring, "convert_to_pcm should have docstring"


class TestAddNoiseFunction:
    """Test add_noise function"""

    @pytest.fixture
    def audio_utils_content(self):
        """Load audio_utils.py content"""
        return AUDIO_UTILS_FILE.read_text()

    def test_has_add_noise_function(self, audio_utils_content):
        """Test that add_noise function exists"""
        assert "def add_noise" in audio_utils_content, \
            "Should have add_noise function"

    def test_add_noise_has_audio_bytes_param(self, audio_utils_content):
        """Test that add_noise has audio_bytes parameter"""
        lines = audio_utils_content.split('\n')
        for i, line in enumerate(lines):
            if 'def add_noise' in line:
                func_def = ''.join(lines[i:min(i+5, len(lines))])
                assert 'audio_bytes' in func_def, \
                    "add_noise should have audio_bytes parameter"
                break

    def test_add_noise_has_snr_db_param(self, audio_utils_content):
        """Test that add_noise has snr_db parameter"""
        lines = audio_utils_content.split('\n')
        for i, line in enumerate(lines):
            if 'def add_noise' in line:
                func_def = ''.join(lines[i:min(i+5, len(lines))])
                assert 'snr_db' in func_def, \
                    "add_noise should have snr_db parameter"
                break

    def test_add_noise_returns_bytes(self, audio_utils_content):
        """Test that add_noise return type annotation is bytes"""
        assert "-> bytes" in audio_utils_content or "Returns:\n        bytes" in audio_utils_content, \
            "add_noise should return bytes"

    def test_add_noise_has_docstring(self, audio_utils_content):
        """Test that add_noise has docstring"""
        lines = audio_utils_content.split('\n')
        in_function = False
        has_docstring = False
        lines_checked = 0

        for i, line in enumerate(lines):
            if 'def add_noise' in line:
                in_function = True
            elif in_function:
                lines_checked += 1
                if '"""' in line or "'''" in line:
                    has_docstring = True
                    break
                elif lines_checked > 10:
                    break

        assert has_docstring, "add_noise should have docstring"


class TestValidateAudioFormatFunction:
    """Test validate_audio_format function"""

    @pytest.fixture
    def audio_utils_content(self):
        """Load audio_utils.py content"""
        return AUDIO_UTILS_FILE.read_text()

    def test_has_validate_audio_format_function(self, audio_utils_content):
        """Test that validate_audio_format function exists"""
        assert "def validate_audio_format" in audio_utils_content, \
            "Should have validate_audio_format function"

    def test_validate_audio_format_has_audio_bytes_param(self, audio_utils_content):
        """Test that validate_audio_format has audio_bytes parameter"""
        lines = audio_utils_content.split('\n')
        for i, line in enumerate(lines):
            if 'def validate_audio_format' in line:
                func_def = ''.join(lines[i:min(i+5, len(lines))])
                assert 'audio_bytes' in func_def, \
                    "validate_audio_format should have audio_bytes parameter"
                break

    def test_validate_audio_format_returns_bool(self, audio_utils_content):
        """Test that validate_audio_format return type annotation is bool"""
        assert "-> bool" in audio_utils_content or "Returns:\n        bool" in audio_utils_content, \
            "validate_audio_format should return bool"

    def test_validate_audio_format_has_docstring(self, audio_utils_content):
        """Test that validate_audio_format has docstring"""
        lines = audio_utils_content.split('\n')
        in_function = False
        has_docstring = False
        lines_checked = 0

        for i, line in enumerate(lines):
            if 'def validate_audio_format' in line:
                in_function = True
            elif in_function:
                lines_checked += 1
                if '"""' in line or "'''" in line:
                    has_docstring = True
                    break
                elif lines_checked > 10:
                    break

        assert has_docstring, "validate_audio_format should have docstring"


class TestGetAudioDurationFunction:
    """Test get_audio_duration function"""

    @pytest.fixture
    def audio_utils_content(self):
        """Load audio_utils.py content"""
        return AUDIO_UTILS_FILE.read_text()

    def test_has_get_audio_duration_function(self, audio_utils_content):
        """Test that get_audio_duration function exists"""
        assert "def get_audio_duration" in audio_utils_content, \
            "Should have get_audio_duration function"

    def test_get_audio_duration_has_audio_bytes_param(self, audio_utils_content):
        """Test that get_audio_duration has audio_bytes parameter"""
        lines = audio_utils_content.split('\n')
        for i, line in enumerate(lines):
            if 'def get_audio_duration' in line:
                func_def = ''.join(lines[i:min(i+5, len(lines))])
                assert 'audio_bytes' in func_def, \
                    "get_audio_duration should have audio_bytes parameter"
                break

    def test_get_audio_duration_returns_float(self, audio_utils_content):
        """Test that get_audio_duration return type annotation is float"""
        assert "-> float" in audio_utils_content or "Returns:\n        float" in audio_utils_content, \
            "get_audio_duration should return float"

    def test_get_audio_duration_has_docstring(self, audio_utils_content):
        """Test that get_audio_duration has docstring"""
        lines = audio_utils_content.split('\n')
        in_function = False
        has_docstring = False
        lines_checked = 0

        for i, line in enumerate(lines):
            if 'def get_audio_duration' in line:
                in_function = True
            elif in_function:
                lines_checked += 1
                if '"""' in line or "'''" in line:
                    has_docstring = True
                    break
                elif lines_checked > 10:
                    break

        assert has_docstring, "get_audio_duration should have docstring"


class TestAudioUtilsImportability:
    """Test that audio utilities can be imported"""

    def test_can_import_audio_utils_module(self):
        """Test that audio_utils module can be imported"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from services import audio_utils
            assert audio_utils is not None, \
                "audio_utils module should be importable"
        except ImportError as e:
            pytest.fail(f"Cannot import audio_utils: {e}")

    def test_can_import_convert_to_pcm(self):
        """Test that convert_to_pcm can be imported"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from services.audio_utils import convert_to_pcm
            assert convert_to_pcm is not None, \
                "convert_to_pcm should be importable"
            assert callable(convert_to_pcm), \
                "convert_to_pcm should be callable"
        except ImportError as e:
            pytest.fail(f"Cannot import convert_to_pcm: {e}")

    def test_can_import_add_noise(self):
        """Test that add_noise can be imported"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from services.audio_utils import add_noise
            assert add_noise is not None, \
                "add_noise should be importable"
            assert callable(add_noise), \
                "add_noise should be callable"
        except ImportError as e:
            pytest.fail(f"Cannot import add_noise: {e}")

    def test_can_import_validate_audio_format(self):
        """Test that validate_audio_format can be imported"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from services.audio_utils import validate_audio_format
            assert validate_audio_format is not None, \
                "validate_audio_format should be importable"
            assert callable(validate_audio_format), \
                "validate_audio_format should be callable"
        except ImportError as e:
            pytest.fail(f"Cannot import validate_audio_format: {e}")

    def test_can_import_get_audio_duration(self):
        """Test that get_audio_duration can be imported"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from services.audio_utils import get_audio_duration
            assert get_audio_duration is not None, \
                "get_audio_duration should be importable"
            assert callable(get_audio_duration), \
                "get_audio_duration should be callable"
        except ImportError as e:
            pytest.fail(f"Cannot import get_audio_duration: {e}")


class TestConvertToPcmFunctionality:
    """Test convert_to_pcm functionality with real audio data"""

    @pytest.fixture
    def sample_audio_16khz_wav(self):
        """Create sample 16kHz WAV audio for testing"""
        # Create 1 second of silence at 16kHz
        sample_rate = 16000
        duration = 1.0
        samples = int(sample_rate * duration)
        audio_data = np.zeros(samples, dtype=np.float32)

        # Write to WAV in memory
        buffer = io.BytesIO()
        import soundfile as sf
        sf.write(buffer, audio_data, sample_rate, format='WAV')
        return buffer.getvalue()

    def test_convert_to_pcm_returns_bytes(self, sample_audio_16khz_wav):
        """Test that convert_to_pcm returns bytes"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        from services.audio_utils import convert_to_pcm

        result = convert_to_pcm(sample_audio_16khz_wav)
        assert isinstance(result, bytes), "Should return bytes"
        assert len(result) > 0, "Should return non-empty bytes"

    def test_convert_to_pcm_with_target_rate(self, sample_audio_16khz_wav):
        """Test that convert_to_pcm works with custom target rate"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        from services.audio_utils import convert_to_pcm

        result = convert_to_pcm(sample_audio_16khz_wav, target_rate=8000)
        assert isinstance(result, bytes), "Should return bytes"
        assert len(result) > 0, "Should return non-empty bytes"


class TestAddNoiseFunctionality:
    """Test add_noise functionality with real audio data"""

    @pytest.fixture
    def sample_audio_wav(self):
        """Create sample WAV audio for testing"""
        sample_rate = 16000
        duration = 0.5
        samples = int(sample_rate * duration)
        # Create a simple sine wave
        frequency = 440  # A4 note
        t = np.linspace(0, duration, samples, dtype=np.float32)
        audio_data = np.sin(2 * np.pi * frequency * t).astype(np.float32) * 0.3

        buffer = io.BytesIO()
        import soundfile as sf
        sf.write(buffer, audio_data, sample_rate, format='WAV')
        return buffer.getvalue()

    def test_add_noise_returns_bytes(self, sample_audio_wav):
        """Test that add_noise returns bytes"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        from services.audio_utils import add_noise

        result = add_noise(sample_audio_wav, snr_db=10.0)
        assert isinstance(result, bytes), "Should return bytes"
        assert len(result) > 0, "Should return non-empty bytes"

    def test_add_noise_different_snr(self, sample_audio_wav):
        """Test that add_noise works with different SNR values"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        from services.audio_utils import add_noise

        # Test with high SNR (less noise)
        result_high_snr = add_noise(sample_audio_wav, snr_db=30.0)
        assert isinstance(result_high_snr, bytes)

        # Test with low SNR (more noise)
        result_low_snr = add_noise(sample_audio_wav, snr_db=5.0)
        assert isinstance(result_low_snr, bytes)


class TestValidateAudioFormatFunctionality:
    """Test validate_audio_format functionality"""

    @pytest.fixture
    def valid_wav_audio(self):
        """Create valid WAV audio for testing"""
        sample_rate = 16000
        audio_data = np.zeros(1000, dtype=np.float32)
        buffer = io.BytesIO()
        import soundfile as sf
        sf.write(buffer, audio_data, sample_rate, format='WAV')
        return buffer.getvalue()

    def test_validate_audio_format_valid_audio(self, valid_wav_audio):
        """Test that validate_audio_format returns True for valid audio"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        from services.audio_utils import validate_audio_format

        result = validate_audio_format(valid_wav_audio)
        assert result is True, "Should return True for valid audio"

    def test_validate_audio_format_invalid_audio(self):
        """Test that validate_audio_format returns False for invalid audio"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        from services.audio_utils import validate_audio_format

        invalid_audio = b"This is not audio data"
        result = validate_audio_format(invalid_audio)
        assert result is False, "Should return False for invalid audio"

    def test_validate_audio_format_empty_bytes(self):
        """Test that validate_audio_format returns False for empty bytes"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        from services.audio_utils import validate_audio_format

        result = validate_audio_format(b"")
        assert result is False, "Should return False for empty bytes"


class TestGetAudioDurationFunctionality:
    """Test get_audio_duration functionality"""

    @pytest.fixture
    def one_second_audio(self):
        """Create 1 second of audio for testing"""
        sample_rate = 16000
        duration = 1.0
        samples = int(sample_rate * duration)
        audio_data = np.zeros(samples, dtype=np.float32)

        buffer = io.BytesIO()
        import soundfile as sf
        sf.write(buffer, audio_data, sample_rate, format='WAV')
        return buffer.getvalue()

    def test_get_audio_duration_returns_float(self, one_second_audio):
        """Test that get_audio_duration returns float"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        from services.audio_utils import get_audio_duration

        result = get_audio_duration(one_second_audio)
        assert isinstance(result, float), "Should return float"

    def test_get_audio_duration_correct_value(self, one_second_audio):
        """Test that get_audio_duration returns correct duration"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        from services.audio_utils import get_audio_duration

        result = get_audio_duration(one_second_audio)
        assert abs(result - 1.0) < 0.01, \
            f"Should return ~1.0 seconds, got {result}"


class TestTaskRequirements:
    """Test TASK-111 specific requirements"""

    def test_task_111_all_functions_exist(self):
        """Test TASK-111 requirement: All four functions exist"""
        content = AUDIO_UTILS_FILE.read_text()
        assert "def convert_to_pcm" in content, \
            "TASK-111 requirement: Must have convert_to_pcm"
        assert "def add_noise" in content, \
            "TASK-111 requirement: Must have add_noise"
        assert "def validate_audio_format" in content, \
            "TASK-111 requirement: Must have validate_audio_format"
        assert "def get_audio_duration" in content, \
            "TASK-111 requirement: Must have get_audio_duration"

    def test_task_111_correct_signatures(self):
        """Test TASK-111 requirement: Function signatures match specification"""
        content = AUDIO_UTILS_FILE.read_text()

        # Check parameter names
        assert "audio_bytes" in content, "Must use audio_bytes parameter"
        assert "target_rate" in content, "convert_to_pcm must have target_rate"
        assert "snr_db" in content, "add_noise must have snr_db"

    def test_task_111_return_types(self):
        """Test TASK-111 requirement: Correct return types"""
        content = AUDIO_UTILS_FILE.read_text()

        # Should have type hints for return values
        assert "-> bytes" in content or "-> float" in content or "-> bool" in content, \
            "Functions should have return type hints"
