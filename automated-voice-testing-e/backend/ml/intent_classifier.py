"""
Intent classification utilities leveraging zero-shot transformers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Mapping, Sequence, Tuple

from transformers import pipeline

from .model_loader import ensure_sentence_transformer_model

DEFAULT_INTENT_MODEL = "joeddav/xlm-roberta-large-xnli"
DEFAULT_TEMPLATE = "This text expresses the intent: {}."


@dataclass(frozen=True)
class IntentClassificationResult:
    label: str | None
    score: float
    alternatives: List[Tuple[str, float]]


class IntentClassifier:
    """
    Zero-shot intent classifier with multilingual label support.
    """

    def __init__(
        self,
        *,
        default_labels: Sequence[str],
        multilingual_labels: Mapping[str, Sequence[str]] | None = None,
        threshold: float = 0.7,
        model_name: str = DEFAULT_INTENT_MODEL,
        hypothesis_template: str = DEFAULT_TEMPLATE,
        device: int | str | None = None,
    ) -> None:
        self.default_labels = list(default_labels)
        self.multilingual_labels = {
            locale: list(labels)
            for locale, labels in (multilingual_labels or {}).items()
        }
        self.threshold = threshold
        self.model_name = model_name
        self.hypothesis_template = hypothesis_template

        ensure_sentence_transformer_model()
        self._pipeline = pipeline(
            "zero-shot-classification",
            model=self.model_name,
            device=device,
        )

    def _resolve_labels(self, locale: str | None) -> List[str]:
        if locale and locale in self.multilingual_labels:
            return self.multilingual_labels[locale]
        return self.default_labels

    def classify(self, text: str, *, locale: str | None = None) -> IntentClassificationResult:
        """
        Classify the provided text into one of the configured intent labels.
        """
        labels = self._resolve_labels(locale)
        if not labels:
            return IntentClassificationResult(label=None, score=0.0, alternatives=[])

        outputs = self._pipeline(
            [text],
            candidate_labels=[labels],
            hypothesis_template=self.hypothesis_template,
        )

        result = outputs[0]
        raw_labels: Sequence[str] = result.get("labels", [])
        raw_scores: Sequence[float] = result.get("scores", [])

        label_scores = sorted(
            zip(raw_labels, raw_scores),
            key=lambda item: item[1],
            reverse=True,
        )

        if not label_scores:
            return IntentClassificationResult(label=None, score=0.0, alternatives=[])

        top_label, top_score = label_scores[0]
        predicted_label: str | None = top_label if top_score >= self.threshold else None

        if predicted_label is None:
            alternatives = [(lbl, score) for lbl, score in label_scores]
        else:
            alternatives = [(lbl, score) for lbl, score in label_scores if lbl != predicted_label]

        return IntentClassificationResult(
            label=predicted_label,
            score=top_score,
            alternatives=alternatives,
        )
