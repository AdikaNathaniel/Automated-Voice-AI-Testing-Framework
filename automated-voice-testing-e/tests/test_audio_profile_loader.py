"""
Test suite for AudioProfileLoader utility.

This module tests the utility for loading and accessing audio profiles:
- Loading profiles from YAML file
- Getting specific profiles by name
- Listing available profiles
- Error handling for invalid profiles
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

import pytest
from pathlib import Path


class TestAudioProfileLoader:
    """Test AudioProfileLoader utility"""

    def test_can_import_loader(self):
        """Test that AudioProfileLoader can be imported"""
        try:
            from config.audio_profile_loader import AudioProfileLoader
            assert AudioProfileLoader is not None
        except ImportError as e:
            pytest.fail(f"Cannot import AudioProfileLoader: {e}")

    def test_can_instantiate_loader(self):
        """Test that AudioProfileLoader can be instantiated"""
        from config.audio_profile_loader import AudioProfileLoader
        loader = AudioProfileLoader()
        assert loader is not None

    def test_get_profile_returns_dict(self):
        """Test that get_profile returns a dictionary"""
        from config.audio_profile_loader import AudioProfileLoader
        loader = AudioProfileLoader()
        profile = loader.get_profile('clean')
        assert isinstance(profile, dict), "Profile should be a dictionary"

    def test_get_clean_profile(self):
        """Test getting clean profile"""
        from config.audio_profile_loader import AudioProfileLoader
        loader = AudioProfileLoader()
        profile = loader.get_profile('clean')

        assert profile['snr_db'] == 25
        assert profile['background_noise'] is None

    def test_get_moderate_profile(self):
        """Test getting moderate profile"""
        from config.audio_profile_loader import AudioProfileLoader
        loader = AudioProfileLoader()
        profile = loader.get_profile('moderate')

        assert profile['snr_db'] == 20
        assert profile['background_noise'] == 'car_ambient'

    def test_get_high_noise_profile(self):
        """Test getting high_noise profile"""
        from config.audio_profile_loader import AudioProfileLoader
        loader = AudioProfileLoader()
        profile = loader.get_profile('high_noise')

        assert profile['snr_db'] == 15
        assert profile['background_noise'] == 'highway_traffic'

    def test_get_invalid_profile_raises_error(self):
        """Test that getting invalid profile raises KeyError"""
        from config.audio_profile_loader import AudioProfileLoader
        loader = AudioProfileLoader()

        with pytest.raises(KeyError):
            loader.get_profile('nonexistent')

    def test_list_profiles_returns_list(self):
        """Test that list_profiles returns a list"""
        from config.audio_profile_loader import AudioProfileLoader
        loader = AudioProfileLoader()
        profiles = loader.list_profiles()

        assert isinstance(profiles, list), "Should return a list of profile names"

    def test_list_profiles_contains_all_profiles(self):
        """Test that list_profiles contains all profile names"""
        from config.audio_profile_loader import AudioProfileLoader
        loader = AudioProfileLoader()
        profiles = loader.list_profiles()

        assert 'clean' in profiles
        assert 'moderate' in profiles
        assert 'high_noise' in profiles

    def test_has_profile_returns_true_for_existing(self):
        """Test that has_profile returns True for existing profiles"""
        from config.audio_profile_loader import AudioProfileLoader
        loader = AudioProfileLoader()

        assert loader.has_profile('clean') is True
        assert loader.has_profile('moderate') is True
        assert loader.has_profile('high_noise') is True

    def test_has_profile_returns_false_for_nonexistent(self):
        """Test that has_profile returns False for non-existent profiles"""
        from config.audio_profile_loader import AudioProfileLoader
        loader = AudioProfileLoader()

        assert loader.has_profile('nonexistent') is False
