"""
Language service tests.

Validates functions exposed by backend.services.language_service which wrap the
shared languages configuration.
"""

import pytest

from services.language_service import (
    get_supported_languages,
    validate_language_code,
    get_soundhound_model,
)

EXPECTED = {
    "en-US": "en-US-v3.2",
    "es-ES": "es-ES-v2.8",
    "fr-FR": "fr-FR-v2.7",
    "de-DE": "de-DE-v3.0",
    "it-IT": "it-IT-v2.6",
    "pt-BR": "pt-BR-v2.5",
    "ja-JP": "ja-JP-v2.4",
    "zh-CN": "zh-CN-v2.5",
}


def _lang_by_code(languages):
    return {entry["code"]: entry for entry in languages}


def test_get_supported_languages_returns_all_configured_entries():
    languages = get_supported_languages()

    assert isinstance(languages, list)
    assert len(languages) == len(EXPECTED)

    mapping = _lang_by_code(languages)
    assert set(mapping.keys()) == set(EXPECTED.keys())

    for code, model in EXPECTED.items():
        entry = mapping[code]
        assert entry["soundhound_model"] == model
        assert entry["name"]
        assert entry["native_name"]


def test_validate_language_code_matches_known_codes():
    assert validate_language_code("en-US") is True
    assert validate_language_code("pt-BR") is True
    assert validate_language_code("xx-YY") is False


def test_get_soundhound_model_returns_configured_value():
    assert get_soundhound_model("es-ES") == EXPECTED["es-ES"]


def test_get_soundhound_model_invalid_code_raises_value_error():
    with pytest.raises(ValueError):
        get_soundhound_model("xx-YY")
