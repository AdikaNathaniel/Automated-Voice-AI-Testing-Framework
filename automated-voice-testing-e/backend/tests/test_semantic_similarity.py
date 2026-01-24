import numpy as np
import pytest


def test_similarity_identical_texts(monkeypatch):
    import importlib
    import sys
    import types

    sentence_module = types.ModuleType("sentence_transformers")
    sentence_module.SentenceTransformer = object  # placeholder until patched
    monkeypatch.setitem(sys.modules, "sentence_transformers", sentence_module)

    similarity = importlib.import_module("ml.semantic_similarity")

    ensure_called = {}

    def fake_ensure(cache_dir=None):
        ensure_called["called"] = cache_dir

    class FakeModel:
        def __init__(self, model_name):
            self.model_name = model_name

        def encode(
            self,
            texts,
            *,
            convert_to_numpy=True,
            normalize_embeddings=True,
        ):
            assert convert_to_numpy is True
            assert normalize_embeddings is True
            vectors = {
                "hello world": np.array([1.0, 0.0]),
            }
            return np.stack([vectors[text] for text in texts])

    monkeypatch.setattr(similarity, "ensure_sentence_transformer_model", fake_ensure)
    monkeypatch.setattr(similarity, "SentenceTransformer", FakeModel)

    matcher = similarity.SemanticSimilarityMatcher()
    score = matcher.calculate_similarity("hello world", "hello world")

    assert ensure_called["called"] is None
    assert score == pytest.approx(1.0)


def test_similarity_returns_zero_for_opposite_embeddings(monkeypatch):
    import importlib
    import sys
    import types

    sentence_module = types.ModuleType("sentence_transformers")
    sentence_module.SentenceTransformer = object
    monkeypatch.setitem(sys.modules, "sentence_transformers", sentence_module)

    similarity = importlib.import_module("ml.semantic_similarity")

    class FakeModel:
        def __init__(self, model_name):
            self.model_name = model_name

        def encode(
            self,
            texts,
            *,
            convert_to_numpy=True,
            normalize_embeddings=True,
        ):
            vectors = {
                "good": np.array([1.0, 0.0]),
                "bad": np.array([-1.0, 0.0]),
            }
            return np.stack([vectors[text] for text in texts])

    monkeypatch.setattr(similarity, "ensure_sentence_transformer_model", lambda cache_dir=None: None)
    monkeypatch.setattr(similarity, "SentenceTransformer", FakeModel)

    matcher = similarity.SemanticSimilarityMatcher()
    score = matcher.calculate_similarity("good", "bad")

    assert 0.0 <= score <= 1.0
    assert score == pytest.approx(0.0)
