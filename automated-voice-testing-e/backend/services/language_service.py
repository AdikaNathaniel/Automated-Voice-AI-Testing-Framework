"""
Language service utilities.

Provides helper functions for working with the SoundHound language
configuration defined in `backend/config/languages.yaml`.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Dict, List

import yaml

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "languages.yaml"


class LanguageService:
    """
    Service class for language management operations.

    Provides utilities for working with SoundHound language configuration.

    Example:
        >>> service = LanguageService()
        >>> languages = service.get_supported_languages()
    """

    def __init__(self):
        """Initialize the language service."""
        pass

    def get_supported_languages(self) -> List[Dict[str, str]]:
        """Return all supported language definitions."""
        return get_supported_languages()

    def validate_language_code(self, code: str) -> bool:
        """Determine whether a language code is supported."""
        return validate_language_code(code)

    def get_soundhound_model(self, code: str) -> str:
        """Get the SoundHound model for a language code."""
        return get_soundhound_model(code)


@lru_cache(maxsize=1)
def _load_languages() -> tuple[Dict[str, str], ...]:
    """
    Load language definitions from the shared YAML configuration.

    Returns:
        Tuple of language metadata dictionaries.

    Raises:
        FileNotFoundError: If the configuration file is missing.
        ValueError: If the configuration does not contain the expected shape.
    """
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Language configuration file not found: {CONFIG_PATH}"
        )

    with CONFIG_PATH.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    languages = data.get("languages")
    if not isinstance(languages, list):
        raise ValueError("languages.yaml must define a list under 'languages'")

    normalized: List[Dict[str, str]] = []
    for entry in languages:
        if not isinstance(entry, dict):
            raise ValueError("Each language entry must be a mapping")

        required_keys = {"code", "name", "native_name", "soundhound_model"}
        if set(entry.keys()) != required_keys:
            raise ValueError(
                "Language entry must contain exactly: "
                "'code', 'name', 'native_name', 'soundhound_model'"
            )

        normalized.append(
            {
                "code": str(entry["code"]),
                "name": str(entry["name"]),
                "native_name": str(entry["native_name"]),
                "soundhound_model": str(entry["soundhound_model"]),
            }
        )

    return tuple(normalized)


def get_supported_languages() -> List[Dict[str, str]]:
    """
    Return all supported language definitions.

    Returns:
        List of dictionaries describing each language.
    """
    return [dict(entry) for entry in _load_languages()]


def validate_language_code(code: str) -> bool:
    """
    Determine whether a language code is supported.

    Args:
        code: Language code (e.g., 'en-US').

    Returns:
        True if the code exists in the configuration, otherwise False.
    """
    return any(entry["code"] == code for entry in _load_languages())


def get_soundhound_model(code: str) -> str:
    """
    Retrieve the SoundHound model identifier associated with a language.

    Args:
        code: Language code (e.g., 'es-ES').

    Returns:
        The configured SoundHound model identifier.

    Raises:
        ValueError: If the language code is not supported.
    """
    for entry in _load_languages():
        if entry["code"] == code:
            return entry["soundhound_model"]

    raise ValueError(f"Unsupported language code: {code}")
