"""
Entity extraction service built on top of spaCy NER models.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Mapping, MutableMapping

import spacy

from .model_loader import SPACY_MODEL_MAP, ensure_spacy_models


@dataclass(frozen=True)
class ExtractedEntity:
    text: str
    label: str
    start: int
    end: int


class EntityExtractor:
    """
    Load language-specific spaCy models and expose an entity extraction API.
    """

    def __init__(
        self,
        *,
        language_map: Mapping[str, str] | None = None,
        cache_dir: Path | None = None,
    ) -> None:
        self._language_map = dict(language_map) if language_map else dict(SPACY_MODEL_MAP)
        self._cache_dir = cache_dir
        self._pipelines: MutableMapping[str, object] = {}

        self._model_paths = ensure_spacy_models(cache_dir=self._cache_dir, model_map=self._language_map)

        for locale, package_name in self._language_map.items():
            try:
                self._pipelines[locale] = spacy.load(package_name)
            except OSError:
                continue

        if "default" not in self._pipelines and self._language_map:
            fallback_locale = next(iter(self._language_map))
            pipeline = self._pipelines.get(fallback_locale)
            if pipeline is not None:
                self._pipelines["default"] = pipeline

    def extract(self, text: str, *, locale: str | None = None) -> List[Dict[str, object]]:
        """
        Extract named entities from text using the locale-specific pipeline.
        """
        pipeline = None
        if locale and locale in self._pipelines:
            pipeline = self._pipelines[locale]
        else:
            pipeline = self._pipelines.get("default")

        if pipeline is None:
            return []

        doc = pipeline(text)

        entities: List[Dict[str, object]] = []
        for ent in getattr(doc, "ents", []):
            entities.append(
                {
                    "text": ent.text,
                    "label": ent.label_,
                    "start": getattr(ent, "start_char", 0),
                    "end": getattr(ent, "end_char", len(ent.text)),
                }
            )

        return entities
