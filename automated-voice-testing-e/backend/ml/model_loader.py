"""
Utilities for downloading and caching ML models required by the validation pipeline.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Mapping, MutableMapping

from sentence_transformers import SentenceTransformer
from spacy.cli import download as spacy_download

SENTENCE_TRANSFORMER_MODEL = "sentence-transformers/all-mpnet-base-v2"

# Mapping of project language codes to spaCy packages.
SPACY_MODEL_MAP: Mapping[str, str] = {
    "en-US": "en_core_web_sm",
    "es-ES": "es_core_news_sm",
    "fr-FR": "fr_core_news_sm",
    "de-DE": "de_core_news_sm",
    "it-IT": "it_core_news_sm",
    "pt-BR": "pt_core_news_sm",
    "ja-JP": "ja_core_news_sm",
    "zh-CN": "zh_core_web_sm",
}

DEFAULT_CACHE_DIR = Path(
    os.getenv("MODEL_CACHE_DIR", Path(__file__).resolve().parent / "cache")
)


@dataclass(frozen=True)
class ModelAssets:
    """Paths to cached model resources."""

    sentence_transformer_path: Path
    spacy_models: Dict[str, Path]


def _ensure_cache_dir(base: Path | str | None = None) -> Path:
    cache_dir = Path(base) if base is not None else DEFAULT_CACHE_DIR
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def _marker_path(target_dir: Path) -> Path:
    return target_dir / ".downloaded"


def ensure_sentence_transformer_model(cache_dir: Path | str | None = None) -> Path:
    """
    Ensure the sentence transformer model is cached locally.

    Returns:
        Path: directory containing the cached model weights.
    """
    cache_dir_path = _ensure_cache_dir(cache_dir)
    model_dir = cache_dir_path / "transformers" / "all-mpnet-base-v2"
    marker = _marker_path(model_dir)

    if not marker.exists():
        model_dir.mkdir(parents=True, exist_ok=True)
        SentenceTransformer(
            SENTENCE_TRANSFORMER_MODEL,
            cache_folder=str(model_dir),
        )
        marker.touch()

    return model_dir


def ensure_spacy_models(
    cache_dir: Path | str | None = None,
    model_map: Mapping[str, str] | None = None,
) -> Dict[str, Path]:
    """
    Ensure required spaCy models are downloaded and cached.

    Args:
        cache_dir: Optional base directory to store cached models.
        model_map: Optional override mapping of language codes to spaCy packages.

    Returns:
        Dictionary mapping language code to cached spaCy path.
    """
    cache_dir_path = _ensure_cache_dir(cache_dir)
    resolved_map: Mapping[str, str]
    resolved_map = model_map if model_map is not None else SPACY_MODEL_MAP

    spacy_base = cache_dir_path / "spacy"
    spacy_paths: MutableMapping[str, Path] = {}

    for language_code, package_name in resolved_map.items():
        package_dir = spacy_base / package_name
        marker = _marker_path(package_dir)
        if not marker.exists():
            package_dir.mkdir(parents=True, exist_ok=True)
            spacy_download(package_name)
            marker.touch()
        spacy_paths[language_code] = package_dir

    return dict(spacy_paths)


def ensure_all_models(cache_dir: Path | str | None = None) -> ModelAssets:
    """
    Ensure all ML models required by the application are cached locally.

    Args:
        cache_dir: Optional base directory to override the default cache location.

    Returns:
        ModelAssets dataclass describing cached resources.
    """
    cache_dir_path = _ensure_cache_dir(cache_dir)
    transformer_path = ensure_sentence_transformer_model(cache_dir_path)
    spacy_paths = ensure_spacy_models(cache_dir_path)

    return ModelAssets(
        sentence_transformer_path=transformer_path,
        spacy_models=spacy_paths,
    )
