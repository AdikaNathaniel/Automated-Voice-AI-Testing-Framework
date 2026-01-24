from pathlib import Path


def test_entity_extraction_with_language_models(monkeypatch):
    import importlib
    import sys
    import types

    spacy_module = types.ModuleType("spacy")
    spacy_cli_module = types.ModuleType("spacy.cli")
    spacy_module.cli = spacy_cli_module
    spacy_cli_module.download = lambda name: None
    monkeypatch.setitem(sys.modules, "spacy", spacy_module)
    monkeypatch.setitem(sys.modules, "spacy.cli", spacy_cli_module)
    sentence_module = types.ModuleType("sentence_transformers")
    sentence_module.SentenceTransformer = object
    monkeypatch.setitem(sys.modules, "sentence_transformers", sentence_module)
    transformers_module = types.ModuleType("transformers")
    transformers_module.pipeline = lambda *args, **kwargs: None
    monkeypatch.setitem(sys.modules, "transformers", transformers_module)

    language_map = {
        "en-US": "en_core_web_sm",
        "es-ES": "es_core_news_sm",
    }

    def fake_ensure_spacy_models(cache_dir=None, model_map=None):
        base = Path(cache_dir) if cache_dir is not None else Path("cache")
        return {
            "en-US": base / "spacy" / "en_core_web_sm",
            "es-ES": base / "spacy" / "es_core_news_sm",
        }

    class FakeEntity:
        def __init__(self, text, label_, start=None, end=None):
            self.text = text
            self.label_ = label_
            self.start_char = start or 0
            self.end_char = end or len(text)

    class FakeDoc:
        def __init__(self, text, entities):
            self.text = text
            self._entities = entities

        @property
        def ents(self):
            return self._entities

    class FakeNlp:
        def __init__(self, entities):
            self._entities = entities

        def __call__(self, text):
            if "refund" in text:
                return FakeDoc(text, [FakeEntity("refund", "EVENT", 6, 12)])
            return FakeDoc(text, self._entities)

    registry = {}

    def fake_spacy_load(name):
        return registry[name]

    spacy_module.load = fake_spacy_load

    registry["en_core_web_sm"] = FakeNlp([FakeEntity("Alice", "PERSON")])
    registry["es_core_news_sm"] = FakeNlp([FakeEntity("Madrid", "LOC")])

    intent_module = importlib.import_module("ml.entity_extractor")

    monkeypatch.setattr(intent_module, "SPACY_MODEL_MAP", language_map)
    monkeypatch.setattr(intent_module, "ensure_spacy_models", fake_ensure_spacy_models)

    extractor = intent_module.EntityExtractor()

    en_entities = extractor.extract("Alice requested a refund", locale="en-US")
    es_entities = extractor.extract("Vivo en Madrid", locale="es-ES")
    default_entities = extractor.extract("Bonjour Paris")

    assert en_entities == [
        {
            "text": "refund",
            "label": "EVENT",
            "start": 6,
            "end": 12,
        }
    ]
    assert es_entities == [
        {
            "text": "Madrid",
            "label": "LOC",
            "start": 0,
            "end": 6,
        }
    ]
    assert default_entities == [
        {
            "text": "Alice",
            "label": "PERSON",
            "start": 0,
            "end": 5,
        }
    ]


def test_entity_extractor_handles_missing_locale(monkeypatch):
    import importlib
    import sys
    import types

    spacy_module = types.ModuleType("spacy")
    spacy_cli_module = types.ModuleType("spacy.cli")
    spacy_module.cli = spacy_cli_module
    spacy_cli_module.download = lambda name: None
    monkeypatch.setitem(sys.modules, "spacy", spacy_module)
    monkeypatch.setitem(sys.modules, "spacy.cli", spacy_cli_module)

    sentence_module = types.ModuleType("sentence_transformers")
    sentence_module.SentenceTransformer = object
    monkeypatch.setitem(sys.modules, "sentence_transformers", sentence_module)
    transformers_module = types.ModuleType("transformers")
    transformers_module.pipeline = lambda *args, **kwargs: None
    monkeypatch.setitem(sys.modules, "transformers", transformers_module)

    monkeypatch.setattr("ml.entity_extractor.ensure_spacy_models", lambda cache_dir=None, model_map=None: {})

    class FakeNlp:
        def __call__(self, text):
            return text

    spacy_module.load = lambda name: FakeNlp()

    intent_module = importlib.import_module("ml.entity_extractor")

    monkeypatch.setattr(intent_module, "SPACY_MODEL_MAP", {})

    extractor = intent_module.EntityExtractor()
    result = extractor.extract("No models configured", locale="fr-FR")
    assert result == []
