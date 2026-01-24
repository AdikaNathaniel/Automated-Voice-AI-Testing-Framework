"""
Semantic similarity service built on top of sentence-transformer embeddings.
"""

from __future__ import annotations


import numpy as np
from sentence_transformers import SentenceTransformer

from .model_loader import (
    SENTENCE_TRANSFORMER_MODEL,
    ensure_sentence_transformer_model,
)


class SemanticSimilarityMatcher:
    """
    Wraps the project-standard sentence transformer to compute similarity scores.
    """

    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or SENTENCE_TRANSFORMER_MODEL
        ensure_sentence_transformer_model()
        self.model = SentenceTransformer(self.model_name)

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Compute a similarity score between two strings in the range [0, 1].
        """
        if not text1 or not text2:
            return 0.0

        embeddings = self.model.encode(
            [text1, text2],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        first, second = (np.asarray(vec, dtype=np.float64) for vec in embeddings)

        denominator = float(np.linalg.norm(first) * np.linalg.norm(second))
        if denominator == 0.0:
            return 0.0

        cosine = float(np.dot(first, second) / denominator)
        similarity = (cosine + 1.0) / 2.0

        if np.isnan(similarity):
            return 0.0

        return max(0.0, min(1.0, similarity))
