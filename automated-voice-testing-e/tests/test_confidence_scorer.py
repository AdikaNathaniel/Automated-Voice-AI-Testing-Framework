"""
Test suite for ConfidenceScorer (TASK-124).

This module tests the confidence scoring aggregator:
- ConfidenceScorer class structure
- Weighted average calculation from multiple validators
- Score conversion to 0-100%
- Default and custom weights
- Edge cases and error handling
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

import pytest
from typing import Dict


class TestConfidenceScorerFileStructure:
    """Test confidence scorer file structure"""

    def test_validators_directory_exists(self):
        """Test that validators directory exists"""
        import os
        backend_dir = os.path.join(os.path.dirname(__file__), '../backend')
        validators_dir = os.path.join(backend_dir, 'validators')

        assert os.path.exists(validators_dir), \
            "validators directory should exist in backend/"

    def test_confidence_scorer_file_exists(self):
        """Test that confidence_scorer.py exists"""
        import os
        backend_dir = os.path.join(os.path.dirname(__file__), '../backend')
        validators_dir = os.path.join(backend_dir, 'validators')
        confidence_scorer_file = os.path.join(
            validators_dir, 'confidence_scorer.py'
        )

        assert os.path.exists(confidence_scorer_file), \
            "confidence_scorer.py should exist in backend/validators/"

    def test_can_import_confidence_scorer(self):
        """Test that ConfidenceScorer can be imported"""
        try:
            from validators.confidence_scorer import ConfidenceScorer
            assert ConfidenceScorer is not None
        except ImportError as e:
            pytest.fail(f"Cannot import ConfidenceScorer: {e}")


class TestConfidenceScorerClass:
    """Test ConfidenceScorer class structure"""

    def test_confidence_scorer_class_exists(self):
        """Test that ConfidenceScorer class exists"""
        from validators.confidence_scorer import ConfidenceScorer
        assert ConfidenceScorer is not None

    def test_confidence_scorer_can_instantiate(self):
        """Test that ConfidenceScorer can be instantiated"""
        from validators.confidence_scorer import ConfidenceScorer
        scorer = ConfidenceScorer()
        assert scorer is not None

    def test_confidence_scorer_has_calculate_method(self):
        """Test that ConfidenceScorer has calculate method"""
        from validators.confidence_scorer import ConfidenceScorer
        scorer = ConfidenceScorer()

        assert hasattr(scorer, 'calculate'), \
            "ConfidenceScorer should have calculate method"

    def test_confidence_scorer_has_get_weights_method(self):
        """Test that ConfidenceScorer has get_weights method"""
        from validators.confidence_scorer import ConfidenceScorer
        scorer = ConfidenceScorer()

        assert hasattr(scorer, 'get_weights'), \
            "ConfidenceScorer should have get_weights method"

    def test_confidence_scorer_has_set_weights_method(self):
        """Test that ConfidenceScorer has set_weights method"""
        from validators.confidence_scorer import ConfidenceScorer
        scorer = ConfidenceScorer()

        assert hasattr(scorer, 'set_weights'), \
            "ConfidenceScorer should have set_weights method"


class TestDefaultWeights:
    """Test default weight configuration"""

    @pytest.fixture
    def scorer(self):
        """Create ConfidenceScorer instance"""
        from validators.confidence_scorer import ConfidenceScorer
        return ConfidenceScorer()

    def test_has_default_weights(self, scorer):
        """Test that scorer has default weights"""
        weights = scorer.get_weights()

        assert isinstance(weights, dict), "Weights should be a dictionary"
        assert len(weights) > 0, "Should have default weights"

    def test_default_weights_sum_to_one(self, scorer):
        """Test that default weights sum to 1.0"""
        weights = scorer.get_weights()
        total = sum(weights.values())

        assert abs(total - 1.0) < 0.01, "Weights should sum to approximately 1.0"

    def test_has_intent_weight(self, scorer):
        """Test that default weights include intent validator"""
        weights = scorer.get_weights()

        assert 'intent' in weights or 'intent_match' in weights, \
            "Should have weight for intent validator"

    def test_has_entity_weight(self, scorer):
        """Test that default weights include entity validator"""
        weights = scorer.get_weights()

        assert 'entity' in weights or 'entity_match' in weights, \
            "Should have weight for entity validator"

    def test_has_semantic_weight(self, scorer):
        """Test that default weights include semantic validator"""
        weights = scorer.get_weights()

        assert 'semantic' in weights or 'semantic_similarity' in weights, \
            "Should have weight for semantic validator"


class TestCalculateScore:
    """Test score calculation"""

    @pytest.fixture
    def scorer(self):
        """Create ConfidenceScorer instance"""
        from validators.confidence_scorer import ConfidenceScorer
        return ConfidenceScorer()

    def test_calculate_perfect_scores(self, scorer):
        """Test calculate with all perfect scores"""
        scores = {
            'intent': 1.0,
            'entity': 1.0,
            'semantic': 1.0,
            'response_time': 1.0
        }

        confidence = scorer.calculate(scores)

        assert confidence == 100.0, "Perfect scores should return 100%"

    def test_calculate_zero_scores(self, scorer):
        """Test calculate with all zero scores"""
        scores = {
            'intent': 0.0,
            'entity': 0.0,
            'semantic': 0.0,
            'response_time': 0.0
        }

        confidence = scorer.calculate(scores)

        assert confidence == 0.0, "Zero scores should return 0%"

    def test_calculate_mixed_scores(self, scorer):
        """Test calculate with mixed scores"""
        scores = {
            'intent': 1.0,
            'entity': 0.5,
            'semantic': 0.8,
            'response_time': 1.0
        }

        confidence = scorer.calculate(scores)

        assert 0.0 < confidence < 100.0, "Mixed scores should return value between 0 and 100"

    def test_calculate_returns_float(self, scorer):
        """Test that calculate returns float"""
        scores = {'intent': 0.8, 'entity': 0.7}

        confidence = scorer.calculate(scores)

        assert isinstance(confidence, (float, int)), "Should return numeric value"

    def test_calculate_returns_0_to_100(self, scorer):
        """Test that calculate returns value in 0-100 range"""
        scores = {'intent': 0.5, 'entity': 0.6, 'semantic': 0.7}

        confidence = scorer.calculate(scores)

        assert 0.0 <= confidence <= 100.0, "Score should be between 0 and 100"


class TestWeightedAverage:
    """Test weighted average calculation"""

    @pytest.fixture
    def scorer(self):
        """Create ConfidenceScorer instance"""
        from validators.confidence_scorer import ConfidenceScorer
        return ConfidenceScorer()

    def test_equal_weights_simple_average(self, scorer):
        """Test that equal weights produce simple average"""
        # Set equal weights
        scorer.set_weights({
            'intent': 0.25,
            'entity': 0.25,
            'semantic': 0.25,
            'response_time': 0.25
        })

        scores = {
            'intent': 0.8,
            'entity': 0.6,
            'semantic': 0.4,
            'response_time': 0.2
        }

        confidence = scorer.calculate(scores)

        # Simple average: (0.8 + 0.6 + 0.4 + 0.2) / 4 = 0.5 = 50%
        expected = 50.0
        assert abs(confidence - expected) < 1.0, \
            f"Expected ~{expected}%, got {confidence}%"

    def test_weighted_average_favors_higher_weight(self, scorer):
        """Test that higher weights influence score more"""
        # High weight on intent
        scorer.set_weights({
            'intent': 0.8,
            'entity': 0.2
        })

        scores_high_intent = {'intent': 1.0, 'entity': 0.0}
        scores_high_entity = {'intent': 0.0, 'entity': 1.0}

        confidence_high_intent = scorer.calculate(scores_high_intent)
        confidence_high_entity = scorer.calculate(scores_high_entity)

        # Should favor intent since it has 80% weight
        assert confidence_high_intent > confidence_high_entity, \
            "Higher weight should have more influence"

    def test_missing_scores_handled(self, scorer):
        """Test that missing validator scores are handled"""
        # Only provide some scores
        scores = {
            'intent': 0.8,
            'entity': 0.6
            # semantic and response_time missing
        }

        # Should handle gracefully
        confidence = scorer.calculate(scores)

        assert isinstance(confidence, (float, int)), \
            "Should handle missing scores"


class TestCustomWeights:
    """Test custom weight configuration"""

    @pytest.fixture
    def scorer(self):
        """Create ConfidenceScorer instance"""
        from validators.confidence_scorer import ConfidenceScorer
        return ConfidenceScorer()

    def test_set_custom_weights(self, scorer):
        """Test setting custom weights"""
        custom_weights = {
            'intent': 0.4,
            'entity': 0.3,
            'semantic': 0.2,
            'response_time': 0.1
        }

        scorer.set_weights(custom_weights)
        weights = scorer.get_weights()

        assert weights == custom_weights, "Should use custom weights"

    def test_custom_weights_affect_calculation(self, scorer):
        """Test that custom weights affect calculation"""
        # Default calculation
        scores = {'intent': 1.0, 'entity': 0.0}
        default_confidence = scorer.calculate(scores)

        # Set custom weights favoring entity
        scorer.set_weights({'intent': 0.2, 'entity': 0.8})
        custom_confidence = scorer.calculate(scores)

        # Different weights should produce different results
        assert default_confidence != custom_confidence, \
            "Custom weights should change result"

    def test_weights_must_be_positive(self, scorer):
        """Test that weights must be positive"""
        # Try to set negative weight
        invalid_weights = {'intent': -0.5, 'entity': 1.5}

        # Should either raise error or normalize
        try:
            scorer.set_weights(invalid_weights)
            weights = scorer.get_weights()
            # If accepted, all weights should be non-negative
            assert all(w >= 0 for w in weights.values()), \
                "Weights should be non-negative"
        except ValueError:
            # Acceptable to raise error for invalid weights
            pass


class TestScoreConversion:
    """Test conversion from 0-1 to 0-100"""

    @pytest.fixture
    def scorer(self):
        """Create ConfidenceScorer instance"""
        from validators.confidence_scorer import ConfidenceScorer
        return ConfidenceScorer()

    def test_zero_converts_to_zero(self, scorer):
        """Test that 0.0 converts to 0%"""
        scorer.set_weights({'test': 1.0})
        confidence = scorer.calculate({'test': 0.0})

        assert confidence == 0.0, "0.0 should convert to 0%"

    def test_one_converts_to_hundred(self, scorer):
        """Test that 1.0 converts to 100%"""
        scorer.set_weights({'test': 1.0})
        confidence = scorer.calculate({'test': 1.0})

        assert confidence == 100.0, "1.0 should convert to 100%"

    def test_half_converts_to_fifty(self, scorer):
        """Test that 0.5 converts to 50%"""
        scorer.set_weights({'test': 1.0})
        confidence = scorer.calculate({'test': 0.5})

        assert abs(confidence - 50.0) < 0.1, "0.5 should convert to ~50%"

    def test_conversion_preserves_precision(self, scorer):
        """Test that conversion preserves precision"""
        scorer.set_weights({'test': 1.0})
        confidence = scorer.calculate({'test': 0.853})

        expected = 85.3
        assert abs(confidence - expected) < 0.1, \
            f"0.853 should convert to ~{expected}%"


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.fixture
    def scorer(self):
        """Create ConfidenceScorer instance"""
        from validators.confidence_scorer import ConfidenceScorer
        return ConfidenceScorer()

    def test_empty_scores_dict(self, scorer):
        """Test with empty scores dictionary"""
        scores = {}

        # Should handle gracefully
        try:
            confidence = scorer.calculate(scores)
            assert isinstance(confidence, (float, int)), \
                "Should return numeric value for empty dict"
        except ValueError:
            # Acceptable to raise error for empty scores
            pass

    def test_none_scores(self, scorer):
        """Test with None scores"""
        # Should handle None gracefully
        try:
            confidence = scorer.calculate(None)
            assert isinstance(confidence, (float, int, type(None))), \
                "Should handle None"
        except (ValueError, TypeError, AttributeError):
            # Acceptable to raise error for None
            pass

    def test_scores_out_of_range(self, scorer):
        """Test with scores outside 0-1 range"""
        scorer.set_weights({'test': 1.0})

        # Score > 1.0
        scores_high = {'test': 1.5}
        confidence_high = scorer.calculate(scores_high)

        # Should clamp or handle gracefully
        assert confidence_high <= 100.0, "Should not exceed 100%"

        # Score < 0.0
        scores_low = {'test': -0.5}
        confidence_low = scorer.calculate(scores_low)

        # Should clamp or handle gracefully
        assert confidence_low >= 0.0, "Should not go below 0%"

    def test_single_validator(self, scorer):
        """Test with only one validator score"""
        scorer.set_weights({'intent': 1.0})
        scores = {'intent': 0.75}

        confidence = scorer.calculate(scores)

        assert confidence == 75.0, "Single validator should work correctly"


class TestTaskRequirements:
    """Test TASK-124 specific requirements"""

    def test_task_124_file_location(self):
        """Test TASK-124: File is in correct location"""
        import os
        confidence_scorer_file = os.path.join(
            os.path.dirname(__file__),
            '../backend/validators/confidence_scorer.py'
        )

        assert os.path.exists(confidence_scorer_file), \
            "TASK-124: File should be at backend/validators/confidence_scorer.py"

    def test_task_124_has_confidence_scorer_class(self):
        """Test TASK-124: Has ConfidenceScorer class"""
        try:
            from validators.confidence_scorer import ConfidenceScorer
            assert ConfidenceScorer is not None
        except ImportError:
            pytest.fail("TASK-124: Should have ConfidenceScorer class")

    def test_task_124_weighted_average(self):
        """Test TASK-124: Calculates weighted average"""
        from validators.confidence_scorer import ConfidenceScorer
        scorer = ConfidenceScorer()

        # Should support weighted average calculation
        assert hasattr(scorer, 'calculate'), \
            "TASK-124: Should have calculate method"

    def test_task_124_returns_0_to_100(self):
        """Test TASK-124: Returns score 0-100%"""
        from validators.confidence_scorer import ConfidenceScorer
        scorer = ConfidenceScorer()

        scores = {'intent': 0.5, 'entity': 0.5}
        confidence = scorer.calculate(scores)

        assert 0.0 <= confidence <= 100.0, \
            "TASK-124: Should return score in 0-100% range"

    def test_task_124_supports_all_validators(self):
        """Test TASK-124: Supports all validator types"""
        from validators.confidence_scorer import ConfidenceScorer
        scorer = ConfidenceScorer()

        # Should handle all validator types
        all_scores = {
            'intent': 0.9,
            'entity': 0.8,
            'semantic': 0.85,
            'response_time': 1.0
        }

        confidence = scorer.calculate(all_scores)

        assert isinstance(confidence, (float, int)), \
            "TASK-124: Should handle all validator types"
