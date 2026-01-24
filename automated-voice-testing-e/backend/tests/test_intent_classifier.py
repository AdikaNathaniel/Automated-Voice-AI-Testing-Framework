import pytest


def _install_transformers_monkeypatch(monkeypatch):
    import sys
    import types

    transformers_module = types.ModuleType("transformers")
    transformers_module.pipeline = lambda *_, **__: None  # placeholder
    monkeypatch.setitem(sys.modules, "transformers", transformers_module)


def test_zero_shot_intent_classification_scores(monkeypatch):
    import importlib

    _install_transformers_monkeypatch(monkeypatch)

    import sys
    import types

    sentence_module = types.ModuleType("sentence_transformers")
    sentence_module.SentenceTransformer = object
    monkeypatch.setitem(sys.modules, "sentence_transformers", sentence_module)

    intent_module = importlib.import_module("ml.intent_classifier")

    captured_model_name = {}

    def fake_ensure(cache_dir=None):
        captured_model_name["called"] = True

    class FakePipeline:
        def __init__(self, task_name, model, device=None):
            self.task_name = task_name
            self.model = model
            self.device = device

        def __call__(self, inputs, candidate_labels, hypothesis_template):
            text = inputs
            labels = candidate_labels
            base_scores = {
                "approve refund": 0.8,
                "escalate": 0.6,
                "report bug": 0.2,
                "aprobar reembolso": 0.75,
            }
            result = []
            for idx, item in enumerate(text):
                scores = []
                for label in labels[idx]:
                    scores.append(base_scores.get(label, 0.0))
                result.append({"labels": labels[idx], "scores": scores})
            return result

    monkeypatch.setattr(intent_module, "ensure_sentence_transformer_model", fake_ensure)
    monkeypatch.setattr(intent_module, "pipeline", FakePipeline)

    classifier = intent_module.IntentClassifier(
        default_labels=["approve refund", "escalate", "report bug"],
        multilingual_labels={
            "es-ES": ["aprobar reembolso", "escalate"],
        },
        threshold=0.7,
    )

    english_result = classifier.classify("Please approve refund and escalate the issue")
    spanish_result = classifier.classify("Necesitamos aprobar reembolso", locale="es-ES")

    assert captured_model_name["called"] is True

    assert english_result.label == "approve refund"
    assert english_result.score == pytest.approx(0.8)
    assert english_result.alternatives == [
        ("escalate", pytest.approx(0.6)),
        ("report bug", pytest.approx(0.2)),
    ]

    assert spanish_result.label == "aprobar reembolso"
    assert spanish_result.score == pytest.approx(0.75)
    assert spanish_result.alternatives == [
        ("escalate", pytest.approx(0.6)),
    ]


def test_classifier_returns_none_below_threshold(monkeypatch):
    import importlib

    _install_transformers_monkeypatch(monkeypatch)

    import sys
    import types

    sentence_module = types.ModuleType("sentence_transformers")
    sentence_module.SentenceTransformer = object
    monkeypatch.setitem(sys.modules, "sentence_transformers", sentence_module)

    intent_module = importlib.import_module("ml.intent_classifier")

    monkeypatch.setattr(intent_module, "ensure_sentence_transformer_model", lambda cache_dir=None: None)

    class FakePipeline:
        def __init__(self, *args, **kwargs):
            pass

        def __call__(self, inputs, candidate_labels, hypothesis_template):
            return [{"labels": ["approve refund"], "scores": [0.3]}]

    monkeypatch.setattr(intent_module, "pipeline", FakePipeline)

    classifier = intent_module.IntentClassifier(
        default_labels=["approve refund"],
        threshold=0.7,
    )

    result = classifier.classify("Just checking status")

    assert result.label is None
    assert result.score == 0.3
    assert result.alternatives == [("approve refund", pytest.approx(0.3))]
