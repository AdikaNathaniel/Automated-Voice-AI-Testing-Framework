"""
Test suite for audio processing library dependencies (TASK-110)

Validates that required audio processing libraries are installed:
- pydub==0.25.1 for audio format conversion
- soundfile==0.12.1 for reading/writing audio files
- numpy==1.26.3 for audio data manipulation

These libraries are required for TASK-111 (audio utilities).
"""

import pytest
import sys
import importlib.metadata


class TestAudioLibraryImports:
    """Test that audio processing libraries can be imported"""

    def test_can_import_pydub(self):
        """Test that pydub can be imported"""
        try:
            import pydub
            assert pydub is not None, "pydub should be importable"
        except ImportError as e:
            pytest.fail(f"Cannot import pydub: {e}")

    def test_can_import_soundfile(self):
        """Test that soundfile can be imported"""
        try:
            import soundfile
            assert soundfile is not None, "soundfile should be importable"
        except ImportError as e:
            pytest.fail(f"Cannot import soundfile: {e}")

    def test_can_import_numpy(self):
        """Test that numpy can be imported"""
        try:
            import numpy
            assert numpy is not None, "numpy should be importable"
        except ImportError as e:
            pytest.fail(f"Cannot import numpy: {e}")


class TestAudioLibraryVersions:
    """Test that audio processing libraries have correct versions"""

    def test_pydub_version(self):
        """Test that pydub version is 0.25.1"""
        try:
            version = importlib.metadata.version('pydub')
            assert version == '0.25.1', \
                f"pydub version should be 0.25.1, got {version}"
        except importlib.metadata.PackageNotFoundError:
            pytest.fail("pydub is not installed")

    def test_soundfile_version(self):
        """Test that soundfile version is 0.12.1"""
        try:
            version = importlib.metadata.version('soundfile')
            assert version == '0.12.1', \
                f"soundfile version should be 0.12.1, got {version}"
        except importlib.metadata.PackageNotFoundError:
            pytest.fail("soundfile is not installed")

    def test_numpy_version(self):
        """Test that numpy version is 1.26.3"""
        try:
            version = importlib.metadata.version('numpy')
            assert version == '1.26.3', \
                f"numpy version should be 1.26.3, got {version}"
        except importlib.metadata.PackageNotFoundError:
            pytest.fail("numpy is not installed")


class TestAudioLibraryFunctionality:
    """Test basic functionality of audio libraries"""

    def test_pydub_audiosegment_available(self):
        """Test that pydub.AudioSegment is available"""
        try:
            from pydub import AudioSegment
            assert AudioSegment is not None, \
                "pydub.AudioSegment should be available"
        except ImportError as e:
            pytest.fail(f"Cannot import pydub.AudioSegment: {e}")

    def test_soundfile_read_available(self):
        """Test that soundfile.read is available"""
        try:
            import soundfile as sf
            assert hasattr(sf, 'read'), \
                "soundfile.read should be available"
            assert callable(sf.read), \
                "soundfile.read should be callable"
        except ImportError as e:
            pytest.fail(f"Cannot import soundfile: {e}")

    def test_soundfile_write_available(self):
        """Test that soundfile.write is available"""
        try:
            import soundfile as sf
            assert hasattr(sf, 'write'), \
                "soundfile.write should be available"
            assert callable(sf.write), \
                "soundfile.write should be callable"
        except ImportError as e:
            pytest.fail(f"Cannot import soundfile: {e}")

    def test_numpy_array_available(self):
        """Test that numpy.array is available"""
        try:
            import numpy as np
            assert hasattr(np, 'array'), \
                "numpy.array should be available"
            assert callable(np.array), \
                "numpy.array should be callable"
        except ImportError as e:
            pytest.fail(f"Cannot import numpy: {e}")

    def test_numpy_can_create_audio_array(self):
        """Test that numpy can create audio data arrays"""
        try:
            import numpy as np
            # Create a simple audio array (1 second of silence at 16kHz)
            audio_data = np.zeros(16000, dtype=np.float32)
            assert audio_data.shape == (16000,), \
                "Should be able to create audio data array"
            assert audio_data.dtype == np.float32, \
                "Audio data should be float32"
        except ImportError as e:
            pytest.fail(f"Cannot import numpy: {e}")
        except Exception as e:
            pytest.fail(f"Cannot create audio array: {e}")


class TestRequirementsTxt:
    """Test that requirements.txt has the necessary dependencies"""

    @pytest.fixture
    def requirements_content(self):
        """Load requirements.txt content"""
        from pathlib import Path
        requirements_file = Path(__file__).parent.parent / "backend" / "requirements.txt"
        if not requirements_file.exists():
            pytest.skip("requirements.txt does not exist yet")
        return requirements_file.read_text()

    def test_requirements_has_pydub(self, requirements_content):
        """Test that requirements.txt includes pydub==0.25.1"""
        assert "pydub==0.25.1" in requirements_content, \
            "requirements.txt should include pydub==0.25.1"

    def test_requirements_has_soundfile(self, requirements_content):
        """Test that requirements.txt includes soundfile==0.12.1"""
        assert "soundfile==0.12.1" in requirements_content, \
            "requirements.txt should include soundfile==0.12.1"

    def test_requirements_has_numpy(self, requirements_content):
        """Test that requirements.txt includes numpy==1.26.3"""
        assert "numpy==1.26.3" in requirements_content, \
            "requirements.txt should include numpy==1.26.3"


class TestTaskRequirements:
    """Test TASK-110 specific requirements"""

    def test_task_110_pydub_installed(self):
        """Test TASK-110 requirement: pydub is installed"""
        try:
            import pydub
            assert True
        except ImportError:
            pytest.fail("TASK-110 requirement: pydub must be installed")

    def test_task_110_soundfile_installed(self):
        """Test TASK-110 requirement: soundfile is installed"""
        try:
            import soundfile
            assert True
        except ImportError:
            pytest.fail("TASK-110 requirement: soundfile must be installed")

    def test_task_110_numpy_installed(self):
        """Test TASK-110 requirement: numpy is installed"""
        try:
            import numpy
            assert True
        except ImportError:
            pytest.fail("TASK-110 requirement: numpy must be installed")

    def test_task_110_all_versions_correct(self):
        """Test TASK-110 requirement: All versions are correct"""
        try:
            pydub_version = importlib.metadata.version('pydub')
            soundfile_version = importlib.metadata.version('soundfile')
            numpy_version = importlib.metadata.version('numpy')

            assert pydub_version == '0.25.1', f"pydub version incorrect: {pydub_version}"
            assert soundfile_version == '0.12.1', f"soundfile version incorrect: {soundfile_version}"
            assert numpy_version == '1.26.3', f"numpy version incorrect: {numpy_version}"
        except importlib.metadata.PackageNotFoundError as e:
            pytest.fail(f"TASK-110 requirement: Package not found: {e}")
