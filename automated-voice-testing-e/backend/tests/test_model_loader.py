"""
Tests for the ML model loader utilities.
"""

from __future__ import annotations

from pathlib import Path
import sys
import types
from unittest.mock import MagicMock

import pytest


@pytest.fixture()
def cache_dir(tmp_path: Path) -> Path:
    return tmp_path / "model-cache"


def _configure_sentence_transformer_mock(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    transformer_mock = MagicMock(name="SentenceTransformer")
    monkeypatch.setattr(
        "ml.model_loader.SentenceTransformer",
        transformer_mock,
    )
    return transformer_mock


def _configure_spacy_download_mock(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    download_mock = MagicMock(name="spacy_download")
    monkeypatch.setattr(
        "ml.model_loader.spacy_download",
        download_mock,
    )
    return download_mock


def test_ensure_models_downloads_required_assets_once(monkeypatch: pytest.MonkeyPatch, cache_dir: Path) -> None:
    sentence_module = types.ModuleType("sentence_transformers")
    sentence_module.SentenceTransformer = MagicMock(name="SentenceTransformer")
    monkeypatch.setitem(sys.modules, "sentence_transformers", sentence_module)

    spacy_module = types.ModuleType("spacy")
    spacy_cli_module = types.ModuleType("spacy.cli")
    spacy_cli_module.download = MagicMock(name="spacy_download")
    spacy_module.cli = spacy_cli_module
    monkeypatch.setitem(sys.modules, "spacy", spacy_module)
    monkeypatch.setitem(sys.modules, "spacy.cli", spacy_cli_module)

    from ml import model_loader

    transformer_mock = _configure_sentence_transformer_mock(monkeypatch)
    spacy_download_mock = _configure_spacy_download_mock(monkeypatch)

    model_loader.ensure_all_models(cache_dir=cache_dir)

    expected_transformer_cache = cache_dir / "transformers" / "all-mpnet-base-v2"
    expected_spacy_cache = cache_dir / "spacy"

    transformer_mock.assert_called_once_with(
        model_loader.SENTENCE_TRANSFORMER_MODEL,
        cache_folder=str(expected_transformer_cache),
    )

    assert spacy_download_mock.call_count == len(model_loader.SPACY_MODEL_MAP)
    spacy_download_mock.assert_any_call("en_core_web_sm")
    spacy_download_mock.assert_any_call("ja_core_news_sm")

    assert expected_transformer_cache.joinpath(".downloaded").exists()
    for model_name in model_loader.SPACY_MODEL_MAP.values():
        assert expected_spacy_cache.joinpath(model_name, ".downloaded").exists()

    # Second invocation should not trigger downloads again.
    transformer_mock.reset_mock()
    spacy_download_mock.reset_mock()

    model_loader.ensure_all_models(cache_dir=cache_dir)

    transformer_mock.assert_not_called()
    spacy_download_mock.assert_not_called()
