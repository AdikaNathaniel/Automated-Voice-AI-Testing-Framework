"""
Audio Profile Loader Utility

This module provides a utility class for loading and accessing audio simulation
profiles from the YAML configuration file. It simplifies profile management and
provides a clean interface for the application.

Key Features:
- Load profiles from YAML file on initialization
- Get specific profiles by name
- List available profile names
- Check profile existence
- Simple, clean API

Example:
    >>> from config.audio_profile_loader import AudioProfileLoader
    >>>
    >>> # Load profiles
    >>> loader = AudioProfileLoader()
    >>>
    >>> # Get a specific profile
    >>> clean = loader.get_profile('clean')
    >>> print(clean['snr_db'])  # 25
    >>>
    >>> # List all available profiles
    >>> profiles = loader.list_profiles()
    >>> print(profiles)  # ['clean', 'moderate', 'high_noise']
    >>>
    >>> # Check if profile exists
    >>> if loader.has_profile('clean'):
    ...     profile = loader.get_profile('clean')
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class AudioProfileLoader:
    """
    Utility for loading and accessing audio simulation profiles.

    This class loads audio profiles from the YAML configuration file and provides
    convenient methods for accessing them. Profiles are loaded once on initialization
    and cached for efficient access.

    Attributes:
        profiles: Dictionary of all loaded audio profiles
        config_file: Path to the audio profiles YAML file

    Example:
        >>> loader = AudioProfileLoader()
        >>>
        >>> # Get clean profile
        >>> clean = loader.get_profile('clean')
        >>> print(f"SNR: {clean['snr_db']} dB")
        >>>
        >>> # List all profiles
        >>> all_profiles = loader.list_profiles()
        >>> for name in all_profiles:
        ...     profile = loader.get_profile(name)
        ...     print(f"{name}: {profile['snr_db']} dB")
    """

    def __init__(self, config_file: Path = None):
        """
        Initialize the AudioProfileLoader and load profiles.

        Args:
            config_file: Optional path to audio profiles YAML file.
                        If not provided, uses default location.

        Example:
            >>> # Use default config file
            >>> loader = AudioProfileLoader()
            >>>
            >>> # Use custom config file
            >>> custom_path = Path("/path/to/profiles.yaml")
            >>> loader = AudioProfileLoader(config_file=custom_path)
        """
        if config_file is None:
            # Default location
            config_dir = Path(__file__).parent
            self.config_file = config_dir / "audio_profiles.yaml"
        else:
            self.config_file = config_file

        self.profiles = self._load_profiles()
        logger.info(f"Loaded {len(self.profiles)} audio profiles from {self.config_file}")

    def _load_profiles(self) -> Dict[str, Dict[str, Any]]:
        """
        Load profiles from YAML file.

        Returns:
            Dictionary of profile name -> profile configuration

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If YAML is invalid
        """
        if not self.config_file.exists():
            raise FileNotFoundError(
                f"Audio profiles config file not found: {self.config_file}"
            )

        with open(self.config_file, 'r') as f:
            try:
                profiles = yaml.safe_load(f)
                logger.debug(f"Loaded profiles: {list(profiles.keys())}")
                return profiles
            except yaml.YAMLError as e:
                logger.error(f"Failed to parse YAML config: {e}")
                raise

    def get_profile(self, name: str) -> Dict[str, Any]:
        """
        Get a specific audio profile by name.

        Args:
            name: Name of the profile (e.g., 'clean', 'moderate', 'high_noise')

        Returns:
            Dictionary containing profile configuration with keys:
                - snr_db: Signal-to-noise ratio in decibels
                - background_noise: Background noise type or null

        Raises:
            KeyError: If profile name doesn't exist

        Example:
            >>> loader = AudioProfileLoader()
            >>>
            >>> # Get clean profile
            >>> clean = loader.get_profile('clean')
            >>> print(clean)
            >>> # {'snr_db': 25, 'background_noise': None}
            >>>
            >>> # Get moderate profile
            >>> moderate = loader.get_profile('moderate')
            >>> print(moderate['snr_db'])  # 20
        """
        if name not in self.profiles:
            available = ', '.join(self.profiles.keys())
            raise KeyError(
                f"Profile '{name}' not found. Available profiles: {available}"
            )

        return self.profiles[name]

    def list_profiles(self) -> List[str]:
        """
        Get list of all available profile names.

        Returns:
            List of profile names

        Example:
            >>> loader = AudioProfileLoader()
            >>> profiles = loader.list_profiles()
            >>> print(profiles)
            >>> # ['clean', 'moderate', 'high_noise']
            >>>
            >>> # Iterate over all profiles
            >>> for name in loader.list_profiles():
            ...     profile = loader.get_profile(name)
            ...     print(f"{name}: SNR={profile['snr_db']} dB")
        """
        return list(self.profiles.keys())

    def has_profile(self, name: str) -> bool:
        """
        Check if a profile exists.

        Args:
            name: Name of the profile to check

        Returns:
            True if profile exists, False otherwise

        Example:
            >>> loader = AudioProfileLoader()
            >>>
            >>> # Check if profile exists before using
            >>> if loader.has_profile('clean'):
            ...     profile = loader.get_profile('clean')
            ...     print("Clean profile found")
            >>>
            >>> if not loader.has_profile('nonexistent'):
            ...     print("Profile not found")
        """
        return name in self.profiles

    def __repr__(self) -> str:
        """
        String representation of AudioProfileLoader.

        Returns:
            String showing number of loaded profiles

        Example:
            >>> loader = AudioProfileLoader()
            >>> print(loader)
            >>> # <AudioProfileLoader: 3 profiles loaded>
        """
        return f"<AudioProfileLoader: {len(self.profiles)} profiles loaded>"
