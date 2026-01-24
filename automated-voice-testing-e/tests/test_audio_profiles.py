"""
Test suite for audio simulation profiles (TASK-118).

This module tests the audio profile configuration file:
- YAML file existence and location
- YAML file validity and structure
- Required profiles (clean, moderate, high_noise)
- Profile field validation
- Profile value correctness
- SNR (signal-to-noise ratio) specifications
- Background noise configurations
"""

import pytest
from pathlib import Path
import yaml

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
CONFIG_DIR = BACKEND_DIR / "config"
AUDIO_PROFILES_FILE = CONFIG_DIR / "audio_profiles.yaml"


class TestAudioProfilesFileStructure:
    """Test audio_profiles.yaml file structure"""

    def test_config_directory_exists(self):
        """Test that config directory exists"""
        assert CONFIG_DIR.exists(), "backend/config directory should exist"
        assert CONFIG_DIR.is_dir(), "config should be a directory"

    def test_audio_profiles_file_exists(self):
        """Test that audio_profiles.yaml exists"""
        assert AUDIO_PROFILES_FILE.exists(), \
            "audio_profiles.yaml should exist in backend/config/"

    def test_audio_profiles_is_file(self):
        """Test that audio_profiles.yaml is a file"""
        if AUDIO_PROFILES_FILE.exists():
            assert AUDIO_PROFILES_FILE.is_file(), \
                "audio_profiles.yaml should be a file, not a directory"

    def test_audio_profiles_has_content(self):
        """Test that audio_profiles.yaml is not empty"""
        if AUDIO_PROFILES_FILE.exists():
            content = AUDIO_PROFILES_FILE.read_text()
            assert len(content) > 0, "audio_profiles.yaml should not be empty"


class TestYAMLValidity:
    """Test YAML file validity"""

    @pytest.fixture
    def profiles_content(self):
        """Load audio profiles YAML content"""
        if not AUDIO_PROFILES_FILE.exists():
            pytest.skip("audio_profiles.yaml not yet created")
        return AUDIO_PROFILES_FILE.read_text()

    @pytest.fixture
    def profiles_data(self):
        """Load and parse audio profiles YAML"""
        if not AUDIO_PROFILES_FILE.exists():
            pytest.skip("audio_profiles.yaml not yet created")

        with open(AUDIO_PROFILES_FILE, 'r') as f:
            try:
                data = yaml.safe_load(f)
                return data
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML syntax: {e}")

    def test_yaml_is_valid(self, profiles_data):
        """Test that YAML file is valid and parseable"""
        assert profiles_data is not None, "YAML should parse successfully"

    def test_yaml_is_dict(self, profiles_data):
        """Test that YAML root is a dictionary"""
        assert isinstance(profiles_data, dict), \
            "YAML root should be a dictionary of profiles"

    def test_yaml_is_not_empty(self, profiles_data):
        """Test that YAML contains profiles"""
        assert len(profiles_data) > 0, "YAML should contain at least one profile"


class TestRequiredProfiles:
    """Test that all required profiles exist"""

    @pytest.fixture
    def profiles_data(self):
        """Load and parse audio profiles YAML"""
        if not AUDIO_PROFILES_FILE.exists():
            pytest.skip("audio_profiles.yaml not yet created")

        with open(AUDIO_PROFILES_FILE, 'r') as f:
            return yaml.safe_load(f)

    def test_has_clean_profile(self, profiles_data):
        """Test that 'clean' profile exists"""
        assert 'clean' in profiles_data, "Should have 'clean' profile"

    def test_has_moderate_profile(self, profiles_data):
        """Test that 'moderate' profile exists"""
        assert 'moderate' in profiles_data, "Should have 'moderate' profile"

    def test_has_high_noise_profile(self, profiles_data):
        """Test that 'high_noise' profile exists"""
        assert 'high_noise' in profiles_data, "Should have 'high_noise' profile"

    def test_has_all_three_required_profiles(self, profiles_data):
        """Test that all three required profiles exist"""
        required_profiles = ['clean', 'moderate', 'high_noise']
        for profile in required_profiles:
            assert profile in profiles_data, \
                f"Required profile '{profile}' should exist"


class TestProfileFieldValidation:
    """Test that each profile has required fields"""

    @pytest.fixture
    def profiles_data(self):
        """Load and parse audio profiles YAML"""
        if not AUDIO_PROFILES_FILE.exists():
            pytest.skip("audio_profiles.yaml not yet created")

        with open(AUDIO_PROFILES_FILE, 'r') as f:
            return yaml.safe_load(f)

    def test_clean_profile_has_snr_db(self, profiles_data):
        """Test that clean profile has snr_db field"""
        assert 'snr_db' in profiles_data['clean'], \
            "clean profile should have snr_db field"

    def test_clean_profile_has_background_noise(self, profiles_data):
        """Test that clean profile has background_noise field"""
        assert 'background_noise' in profiles_data['clean'], \
            "clean profile should have background_noise field"

    def test_moderate_profile_has_snr_db(self, profiles_data):
        """Test that moderate profile has snr_db field"""
        assert 'snr_db' in profiles_data['moderate'], \
            "moderate profile should have snr_db field"

    def test_moderate_profile_has_background_noise(self, profiles_data):
        """Test that moderate profile has background_noise field"""
        assert 'background_noise' in profiles_data['moderate'], \
            "moderate profile should have background_noise field"

    def test_high_noise_profile_has_snr_db(self, profiles_data):
        """Test that high_noise profile has snr_db field"""
        assert 'snr_db' in profiles_data['high_noise'], \
            "high_noise profile should have snr_db field"

    def test_high_noise_profile_has_background_noise(self, profiles_data):
        """Test that high_noise profile has background_noise field"""
        assert 'background_noise' in profiles_data['high_noise'], \
            "high_noise profile should have background_noise field"

    def test_all_profiles_have_required_fields(self, profiles_data):
        """Test that all profiles have both required fields"""
        required_fields = ['snr_db', 'background_noise']
        profiles = ['clean', 'moderate', 'high_noise']

        for profile in profiles:
            for field in required_fields:
                assert field in profiles_data[profile], \
                    f"Profile '{profile}' should have '{field}' field"


class TestCleanProfile:
    """Test clean profile configuration"""

    @pytest.fixture
    def profiles_data(self):
        """Load and parse audio profiles YAML"""
        if not AUDIO_PROFILES_FILE.exists():
            pytest.skip("audio_profiles.yaml not yet created")

        with open(AUDIO_PROFILES_FILE, 'r') as f:
            return yaml.safe_load(f)

    def test_clean_snr_db_is_25(self, profiles_data):
        """Test that clean profile has SNR of 25 dB"""
        assert profiles_data['clean']['snr_db'] == 25, \
            "clean profile should have snr_db of 25"

    def test_clean_snr_db_is_numeric(self, profiles_data):
        """Test that clean SNR is numeric"""
        snr = profiles_data['clean']['snr_db']
        assert isinstance(snr, (int, float)), \
            "snr_db should be numeric (int or float)"

    def test_clean_background_noise_is_null(self, profiles_data):
        """Test that clean profile has no background noise"""
        assert profiles_data['clean']['background_noise'] is None, \
            "clean profile should have null background_noise"


class TestModerateProfile:
    """Test moderate profile configuration"""

    @pytest.fixture
    def profiles_data(self):
        """Load and parse audio profiles YAML"""
        if not AUDIO_PROFILES_FILE.exists():
            pytest.skip("audio_profiles.yaml not yet created")

        with open(AUDIO_PROFILES_FILE, 'r') as f:
            return yaml.safe_load(f)

    def test_moderate_snr_db_is_20(self, profiles_data):
        """Test that moderate profile has SNR of 20 dB"""
        assert profiles_data['moderate']['snr_db'] == 20, \
            "moderate profile should have snr_db of 20"

    def test_moderate_snr_db_is_numeric(self, profiles_data):
        """Test that moderate SNR is numeric"""
        snr = profiles_data['moderate']['snr_db']
        assert isinstance(snr, (int, float)), \
            "snr_db should be numeric (int or float)"

    def test_moderate_background_noise_is_car_ambient(self, profiles_data):
        """Test that moderate profile has car_ambient background noise"""
        assert profiles_data['moderate']['background_noise'] == "car_ambient", \
            "moderate profile should have 'car_ambient' background_noise"

    def test_moderate_background_noise_is_string(self, profiles_data):
        """Test that moderate background noise is a string"""
        noise = profiles_data['moderate']['background_noise']
        assert isinstance(noise, str), \
            "background_noise should be a string"


class TestHighNoiseProfile:
    """Test high_noise profile configuration"""

    @pytest.fixture
    def profiles_data(self):
        """Load and parse audio profiles YAML"""
        if not AUDIO_PROFILES_FILE.exists():
            pytest.skip("audio_profiles.yaml not yet created")

        with open(AUDIO_PROFILES_FILE, 'r') as f:
            return yaml.safe_load(f)

    def test_high_noise_snr_db_is_15(self, profiles_data):
        """Test that high_noise profile has SNR of 15 dB"""
        assert profiles_data['high_noise']['snr_db'] == 15, \
            "high_noise profile should have snr_db of 15"

    def test_high_noise_snr_db_is_numeric(self, profiles_data):
        """Test that high_noise SNR is numeric"""
        snr = profiles_data['high_noise']['snr_db']
        assert isinstance(snr, (int, float)), \
            "snr_db should be numeric (int or float)"

    def test_high_noise_background_noise_is_highway_traffic(self, profiles_data):
        """Test that high_noise profile has highway_traffic background noise"""
        assert profiles_data['high_noise']['background_noise'] == "highway_traffic", \
            "high_noise profile should have 'highway_traffic' background_noise"

    def test_high_noise_background_noise_is_string(self, profiles_data):
        """Test that high_noise background noise is a string"""
        noise = profiles_data['high_noise']['background_noise']
        assert isinstance(noise, str), \
            "background_noise should be a string"


class TestSNRProgression:
    """Test that SNR values follow logical progression"""

    @pytest.fixture
    def profiles_data(self):
        """Load and parse audio profiles YAML"""
        if not AUDIO_PROFILES_FILE.exists():
            pytest.skip("audio_profiles.yaml not yet created")

        with open(AUDIO_PROFILES_FILE, 'r') as f:
            return yaml.safe_load(f)

    def test_snr_decreases_from_clean_to_moderate(self, profiles_data):
        """Test that SNR decreases from clean to moderate"""
        clean_snr = profiles_data['clean']['snr_db']
        moderate_snr = profiles_data['moderate']['snr_db']

        assert clean_snr > moderate_snr, \
            "clean SNR should be higher than moderate SNR"

    def test_snr_decreases_from_moderate_to_high_noise(self, profiles_data):
        """Test that SNR decreases from moderate to high_noise"""
        moderate_snr = profiles_data['moderate']['snr_db']
        high_noise_snr = profiles_data['high_noise']['snr_db']

        assert moderate_snr > high_noise_snr, \
            "moderate SNR should be higher than high_noise SNR"

    def test_snr_progression_is_logical(self, profiles_data):
        """Test that SNR values follow clean > moderate > high_noise"""
        clean_snr = profiles_data['clean']['snr_db']
        moderate_snr = profiles_data['moderate']['snr_db']
        high_noise_snr = profiles_data['high_noise']['snr_db']

        assert clean_snr > moderate_snr > high_noise_snr, \
            "SNR should decrease: clean > moderate > high_noise"


class TestTaskRequirements:
    """Test TASK-118 specific requirements"""

    @pytest.fixture
    def profiles_data(self):
        """Load and parse audio profiles YAML"""
        if not AUDIO_PROFILES_FILE.exists():
            pytest.skip("audio_profiles.yaml not yet created")

        with open(AUDIO_PROFILES_FILE, 'r') as f:
            return yaml.safe_load(f)

    def test_task_118_file_location(self):
        """Test TASK-118: File is in correct location"""
        assert AUDIO_PROFILES_FILE == CONFIG_DIR / "audio_profiles.yaml", \
            "TASK-118: File should be at backend/config/audio_profiles.yaml"

    def test_task_118_has_three_profiles(self, profiles_data):
        """Test TASK-118: Has all three required profiles"""
        required = ['clean', 'moderate', 'high_noise']
        for profile in required:
            assert profile in profiles_data, \
                f"TASK-118: Must have '{profile}' profile"

    def test_task_118_clean_specification(self, profiles_data):
        """Test TASK-118: Clean profile matches specification"""
        clean = profiles_data['clean']
        assert clean['snr_db'] == 25, "TASK-118: clean snr_db should be 25"
        assert clean['background_noise'] is None, \
            "TASK-118: clean background_noise should be null"

    def test_task_118_moderate_specification(self, profiles_data):
        """Test TASK-118: Moderate profile matches specification"""
        moderate = profiles_data['moderate']
        assert moderate['snr_db'] == 20, "TASK-118: moderate snr_db should be 20"
        assert moderate['background_noise'] == "car_ambient", \
            "TASK-118: moderate background_noise should be 'car_ambient'"

    def test_task_118_high_noise_specification(self, profiles_data):
        """Test TASK-118: High noise profile matches specification"""
        high_noise = profiles_data['high_noise']
        assert high_noise['snr_db'] == 15, "TASK-118: high_noise snr_db should be 15"
        assert high_noise['background_noise'] == "highway_traffic", \
            "TASK-118: high_noise background_noise should be 'highway_traffic'"
