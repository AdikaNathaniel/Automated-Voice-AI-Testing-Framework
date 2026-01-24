"""
Centralized Configuration Service for threshold management.

This service provides centralized configuration management for all
threshold values, quality levels, and timeout settings used across
the automated testing framework.

Key features:
- SNR threshold configuration
- Confidence score thresholds
- Quality level classifications
- Timeout value management
- Runtime reconfiguration support

Example:
    >>> from services.centralized_config_service import CentralizedConfigService
    >>> config = CentralizedConfigService()
    >>> snr = config.get_snr_threshold('high')
    >>> print(f"High SNR threshold: {snr}")
    High SNR threshold: 30.0
"""

from typing import Dict, Any
from copy import deepcopy


class CentralizedConfigService:
    """
    Service for centralized configuration management.

    Provides centralized access to all threshold values, quality
    levels, and timeout settings used across the framework.

    Attributes:
        _snr_thresholds: SNR level thresholds (high/medium/low)
        _confidence_thresholds: Confidence score thresholds
        _quality_levels: Quality classification boundaries
        _timeouts: Timeout values for various operations

    Example:
        >>> config = CentralizedConfigService()
        >>> config.get_snr_threshold('high')
        30.0
        >>> config.set_snr_threshold('high', 35.0)
        >>> config.get_snr_threshold('high')
        35.0
    """

    def __init__(self):
        """Initialize the centralized configuration service."""
        self._set_defaults()

    def _set_defaults(self) -> None:
        """Set all configuration to default values."""
        # SNR thresholds (dB)
        self._snr_thresholds: Dict[str, float] = {
            'high': 30.0,
            'medium': 20.0,
            'low': 10.0
        }

        # Confidence score thresholds
        self._confidence_thresholds: Dict[str, float] = {
            'minimum': 0.5,
            'recommended': 0.7,
            'high': 0.8,
            'very_high': 0.9
        }

        # Quality level boundaries
        self._quality_levels: Dict[str, Dict[str, float]] = {
            'excellent': {'min': 0.9, 'max': 1.0},
            'good': {'min': 0.8, 'max': 0.9},
            'fair': {'min': 0.7, 'max': 0.8},
            'poor': {'min': 0.0, 'max': 0.7}
        }

        # Timeout values (seconds)
        self._timeouts: Dict[str, int] = {
            'default': 30,
            'api_call': 10,
            'database': 5,
            'audio_processing': 60
        }

    # =========================================================================
    # SNR Threshold Methods
    # =========================================================================

    def get_snr_thresholds(self) -> Dict[str, float]:
        """
        Get all SNR thresholds.

        Returns:
            Dictionary with high/medium/low SNR thresholds

        Example:
            >>> thresholds = config.get_snr_thresholds()
            >>> print(thresholds)
            {'high': 30.0, 'medium': 20.0, 'low': 10.0}
        """
        return dict(self._snr_thresholds)

    def get_snr_threshold(self, level: str) -> float:
        """
        Get specific SNR threshold by level.

        Args:
            level: Threshold level ('high', 'medium', 'low')

        Returns:
            SNR threshold value in dB

        Example:
            >>> value = config.get_snr_threshold('high')
            >>> print(value)
            30.0
        """
        return self._snr_thresholds.get(level, 0.0)

    def set_snr_threshold(self, level: str, value: float) -> None:
        """
        Set SNR threshold for specific level.

        Args:
            level: Threshold level ('high', 'medium', 'low')
            value: SNR threshold value in dB

        Example:
            >>> config.set_snr_threshold('high', 35.0)
        """
        self._snr_thresholds[level] = value

    # =========================================================================
    # Confidence Threshold Methods
    # =========================================================================

    def get_confidence_thresholds(self) -> Dict[str, float]:
        """
        Get all confidence thresholds.

        Returns:
            Dictionary with confidence thresholds

        Example:
            >>> thresholds = config.get_confidence_thresholds()
        """
        return dict(self._confidence_thresholds)

    def get_confidence_threshold(self, level: str) -> float:
        """
        Get specific confidence threshold by level.

        Args:
            level: Threshold level

        Returns:
            Confidence threshold value (0.0 to 1.0)

        Example:
            >>> value = config.get_confidence_threshold('recommended')
            >>> print(value)
            0.7
        """
        return self._confidence_thresholds.get(level, 0.0)

    def set_confidence_threshold(self, level: str, value: float) -> None:
        """
        Set confidence threshold for specific level.

        Args:
            level: Threshold level
            value: Confidence threshold value (0.0 to 1.0)

        Example:
            >>> config.set_confidence_threshold('minimum', 0.6)
        """
        self._confidence_thresholds[level] = value

    # =========================================================================
    # Quality Level Methods
    # =========================================================================

    def get_quality_levels(self) -> Dict[str, Dict[str, float]]:
        """
        Get all quality level definitions.

        Returns:
            Dictionary with quality level boundaries

        Example:
            >>> levels = config.get_quality_levels()
        """
        return deepcopy(self._quality_levels)

    def classify_quality_score(self, score: float) -> str:
        """
        Classify a score into quality level.

        Args:
            score: Score value (0.0 to 1.0)

        Returns:
            Quality level name

        Example:
            >>> level = config.classify_quality_score(0.95)
            >>> print(level)
            'excellent'
        """
        if score >= self._quality_levels['excellent']['min']:
            return 'excellent'
        elif score >= self._quality_levels['good']['min']:
            return 'good'
        elif score >= self._quality_levels['fair']['min']:
            return 'fair'
        else:
            return 'poor'

    # =========================================================================
    # Timeout Methods
    # =========================================================================

    def get_timeouts(self) -> Dict[str, int]:
        """
        Get all timeout values.

        Returns:
            Dictionary with timeout values in seconds

        Example:
            >>> timeouts = config.get_timeouts()
        """
        return dict(self._timeouts)

    def get_timeout(self, name: str) -> int:
        """
        Get specific timeout value.

        Args:
            name: Timeout name

        Returns:
            Timeout value in seconds

        Example:
            >>> value = config.get_timeout('default')
            >>> print(value)
            30
        """
        return self._timeouts.get(name, 30)

    def set_timeout(self, name: str, value: int) -> None:
        """
        Set timeout value.

        Args:
            name: Timeout name
            value: Timeout value in seconds

        Example:
            >>> config.set_timeout('default', 60)
        """
        self._timeouts[name] = value

    # =========================================================================
    # General Configuration Methods
    # =========================================================================

    def get_config(self, key: str) -> Any:
        """
        Get configuration value by key.

        Args:
            key: Configuration key

        Returns:
            Configuration value

        Example:
            >>> value = config.get_config('snr_thresholds')
        """
        config_map = {
            'snr_thresholds': self._snr_thresholds,
            'confidence_thresholds': self._confidence_thresholds,
            'quality_levels': self._quality_levels,
            'timeouts': self._timeouts
        }
        return config_map.get(key)

    def set_config(self, key: str, value: Any) -> None:
        """
        Set configuration value by key.

        Args:
            key: Configuration key
            value: Configuration value

        Example:
            >>> config.set_config('snr_thresholds', {'high': 35.0})
        """
        if key == 'snr_thresholds':
            self._snr_thresholds.update(value)
        elif key == 'confidence_thresholds':
            self._confidence_thresholds.update(value)
        elif key == 'quality_levels':
            self._quality_levels.update(value)
        elif key == 'timeouts':
            self._timeouts.update(value)

    def reset_to_defaults(self) -> None:
        """
        Reset all configuration to default values.

        Example:
            >>> config.set_snr_threshold('high', 50.0)
            >>> config.reset_to_defaults()
            >>> config.get_snr_threshold('high')
            30.0
        """
        self._set_defaults()

    def get_all_config(self) -> Dict[str, Any]:
        """
        Get all configuration as dictionary.

        Returns:
            Dictionary with all configuration

        Example:
            >>> all_config = config.get_all_config()
        """
        return {
            'snr_thresholds': dict(self._snr_thresholds),
            'confidence_thresholds': dict(self._confidence_thresholds),
            'quality_levels': deepcopy(self._quality_levels),
            'timeouts': dict(self._timeouts)
        }

    def update_config(self, updates: Dict[str, Any]) -> None:
        """
        Update configuration from dictionary.

        Args:
            updates: Dictionary with configuration updates

        Example:
            >>> config.update_config({'snr_thresholds': {'high': 35.0}})
        """
        for key, value in updates.items():
            self.set_config(key, value)

    def export_config(self) -> Dict[str, Any]:
        """
        Export configuration for serialization.

        Returns:
            Dictionary suitable for JSON serialization

        Example:
            >>> exported = config.export_config()
        """
        return self.get_all_config()

    def import_config(self, config: Dict[str, Any]) -> None:
        """
        Import configuration from dictionary.

        Args:
            config: Configuration dictionary

        Example:
            >>> config.import_config({'snr_thresholds': {'high': 40.0}})
        """
        self.update_config(config)
