"""
Language configuration tests.

Validates the SoundHound language configuration defined in
`backend/config/languages.yaml` so future changes do not accidentally
break multi-language support requirements.
"""

from pathlib import Path
from typing import Dict

import yaml


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "languages.yaml"

EXPECTED_LANGUAGES: Dict[str, Dict[str, str]] = {
    "en-US": {
        "name": "English (United States)",
        "native_name": "English",
        "soundhound_model": "en-US-v3.2",
    },
    "es-ES": {
        "name": "Spanish (Spain)",
        "native_name": "Español",
        "soundhound_model": "es-ES-v2.8",
    },
    "fr-FR": {
        "name": "French (France)",
        "native_name": "Français",
        "soundhound_model": "fr-FR-v2.7",
    },
    "de-DE": {
        "name": "German (Germany)",
        "native_name": "Deutsch",
        "soundhound_model": "de-DE-v3.0",
    },
    "it-IT": {
        "name": "Italian (Italy)",
        "native_name": "Italiano",
        "soundhound_model": "it-IT-v2.6",
    },
    "pt-BR": {
        "name": "Portuguese (Brazil)",
        "native_name": "Português",
        "soundhound_model": "pt-BR-v2.5",
    },
    "ja-JP": {
        "name": "Japanese (Japan)",
        "native_name": "日本語",
        "soundhound_model": "ja-JP-v2.4",
    },
    "zh-CN": {
        "name": "Chinese (Mandarin)",
        "native_name": "中文（普通话）",
        "soundhound_model": "zh-CN-v2.5",
    },
}


def test_languages_config_contains_expected_definitions():
    """Ensure the languages configuration exists and matches expectations."""
    assert CONFIG_PATH.exists(), "languages.yaml should exist under backend/config"

    with CONFIG_PATH.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    assert isinstance(data, dict), "languages.yaml should load into a mapping"
    assert "languages" in data, "languages.yaml must define a 'languages' key"

    languages = data["languages"]
    assert isinstance(languages, list), "'languages' should be a list of mappings"
    assert len(languages) == len(
        EXPECTED_LANGUAGES
    ), "languages list should contain all expected languages"

    by_code = {entry["code"]: entry for entry in languages}
    assert set(by_code.keys()) == set(
        EXPECTED_LANGUAGES.keys()
    ), "language codes should exactly match the expected set"

    for code, expected in EXPECTED_LANGUAGES.items():
        entry = by_code[code]
        assert set(entry.keys()) == {
            "code",
            "name",
            "native_name",
            "soundhound_model",
        }, f"{code} definition should only include required keys"

        assert entry["name"] == expected["name"], f"{code} name mismatch"
        assert entry["native_name"] == expected["native_name"], f"{code} native_name mismatch"
        assert (
            entry["soundhound_model"] == expected["soundhound_model"]
        ), f"{code} soundhound_model mismatch"
