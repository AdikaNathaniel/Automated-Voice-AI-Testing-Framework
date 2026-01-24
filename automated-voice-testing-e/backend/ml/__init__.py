"""
Machine learning helper utilities.
"""

from .model_loader import (
    SENTENCE_TRANSFORMER_MODEL,
    SPACY_MODEL_MAP,
    ensure_all_models,
    ensure_sentence_transformer_model,
    ensure_spacy_models,
    ModelAssets,
)
from .semantic_similarity import SemanticSimilarityMatcher
from .intent_classifier import IntentClassifier, IntentClassificationResult
from .entity_extractor import EntityExtractor
from .ab_testing import (
    ABTestManager,
    ABTestVariant,
    VariantMetrics,
    ExperimentSummary,
)
from .training_data_collector import TrainingDataCollector, TrainingDataSample

__all__ = [
    "SENTENCE_TRANSFORMER_MODEL",
    "SPACY_MODEL_MAP",
    "ensure_all_models",
    "ensure_sentence_transformer_model",
    "ensure_spacy_models",
    "ModelAssets",
    "SemanticSimilarityMatcher",
    "IntentClassifier",
    "IntentClassificationResult",
    "EntityExtractor",
    "ABTestManager",
    "ABTestVariant",
    "VariantMetrics",
    "ExperimentSummary",
    "TrainingDataCollector",
    "TrainingDataSample",
]
