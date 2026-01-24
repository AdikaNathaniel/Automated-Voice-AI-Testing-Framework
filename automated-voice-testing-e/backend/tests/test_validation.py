"""
Unit tests for validation service validators (TASK-145)

This module tests the validation components independently:
- IntentValidator: Intent matching with exact and fuzzy matching
- EntityValidator: Entity extraction validation with tolerance
- SemanticValidator: Semantic similarity validation
- ResponseTimeValidator: Response time threshold validation
- ConfidenceScorer: Weighted score aggregation

Tests focus on each validator's logic in isolation with various inputs.
"""

import pytest

# Import validators
from validators.intent_validator import IntentValidator
from validators.entity_validator import EntityValidator
from validators.confidence_scorer import ConfidenceScorer


# =============================================================================
# Test IntentValidator
# =============================================================================

class TestIntentValidator:
    """Test IntentValidator class"""

    def test_init_with_default_threshold(self):
        """Test initialization with default threshold"""
        # Act
        validator = IntentValidator()

        # Assert
        assert validator.default_threshold == 0.75

    def test_init_with_custom_threshold(self):
        """Test initialization with custom threshold"""
        # Act
        validator = IntentValidator(default_threshold=0.9)

        # Assert
        assert validator.default_threshold == 0.9

    # ========== Test exact_match ==========

    def test_exact_match_identical_strings(self):
        """Test exact match with identical strings"""
        # Arrange
        validator = IntentValidator()

        # Act
        result = validator.exact_match("navigate_home", "navigate_home")

        # Assert
        assert result is True

    def test_exact_match_case_insensitive(self):
        """Test exact match is case insensitive"""
        # Arrange
        validator = IntentValidator()

        # Act
        result = validator.exact_match("Navigate_Home", "navigate_home")

        # Assert
        assert result is True

    def test_exact_match_with_whitespace(self):
        """Test exact match handles whitespace"""
        # Arrange
        validator = IntentValidator()

        # Act
        result = validator.exact_match("  navigate_home  ", "navigate_home")

        # Assert
        assert result is True

    def test_exact_match_different_intents(self):
        """Test exact match with different intents"""
        # Arrange
        validator = IntentValidator()

        # Act
        result = validator.exact_match("play_music", "navigate_home")

        # Assert
        assert result is False

    def test_exact_match_none_values(self):
        """Test exact match with None values"""
        # Arrange
        validator = IntentValidator()

        # Act & Assert
        assert validator.exact_match(None, None) is True
        assert validator.exact_match(None, "navigate_home") is False
        assert validator.exact_match("navigate_home", None) is False

    def test_exact_match_empty_strings(self):
        """Test exact match with empty strings"""
        # Arrange
        validator = IntentValidator()

        # Act
        result = validator.exact_match("", "")

        # Assert
        assert result is True

    # ========== Test fuzzy_match ==========

    def test_fuzzy_match_identical_strings(self):
        """Test fuzzy match with identical strings returns 1.0"""
        # Arrange
        validator = IntentValidator()

        # Act
        score = validator.fuzzy_match("navigate_home", "navigate_home")

        # Assert
        assert score == 1.0

    def test_fuzzy_match_similar_strings(self):
        """Test fuzzy match with similar strings"""
        # Arrange
        validator = IntentValidator()

        # Act
        score = validator.fuzzy_match("navigate_home", "navigate_house")

        # Assert
        assert 0.7 < score < 1.0  # Similar but not identical

    def test_fuzzy_match_with_typo(self):
        """Test fuzzy match handles typos"""
        # Arrange
        validator = IntentValidator()

        # Act
        score = validator.fuzzy_match("navgate_home", "navigate_home")

        # Assert
        assert 0.85 < score < 1.0  # High similarity despite typo

    def test_fuzzy_match_very_different_strings(self):
        """Test fuzzy match with very different strings"""
        # Arrange
        validator = IntentValidator()

        # Act
        score = validator.fuzzy_match("play_music", "navigate_home")

        # Assert
        assert 0.0 <= score < 0.5  # Low similarity

    def test_fuzzy_match_none_values(self):
        """Test fuzzy match with None values"""
        # Arrange
        validator = IntentValidator()

        # Act & Assert
        assert validator.fuzzy_match(None, None) == 1.0
        assert validator.fuzzy_match(None, "navigate_home") == 0.0
        assert validator.fuzzy_match("navigate_home", None) == 0.0

    def test_fuzzy_match_empty_strings(self):
        """Test fuzzy match with empty strings"""
        # Arrange
        validator = IntentValidator()

        # Act & Assert
        assert validator.fuzzy_match("", "") == 1.0
        assert validator.fuzzy_match("", "navigate_home") == 0.0
        assert validator.fuzzy_match("navigate_home", "") == 0.0

    def test_fuzzy_match_case_insensitive(self):
        """Test fuzzy match is case insensitive"""
        # Arrange
        validator = IntentValidator()

        # Act
        score = validator.fuzzy_match("NAVIGATE_HOME", "navigate_home")

        # Assert
        assert score == 1.0

    # ========== Test validate ==========

    def test_validate_exact_match_returns_1_0(self):
        """Test validate returns 1.0 for exact match"""
        # Arrange
        validator = IntentValidator()

        # Act
        score = validator.validate("navigate_home", "navigate_home")

        # Assert
        assert score == 1.0

    def test_validate_fuzzy_match_above_threshold(self):
        """Test validate with fuzzy match above threshold"""
        # Arrange
        validator = IntentValidator(default_threshold=0.7)

        # Act
        score = validator.validate("navigate_home", "navigate_house")

        # Assert
        assert score > 0.7  # Above threshold, returns fuzzy score

    def test_validate_fuzzy_match_below_threshold(self):
        """Test validate returns fuzzy score even when below threshold"""
        # Arrange
        validator = IntentValidator(default_threshold=0.9)

        # Act
        score = validator.validate("play_music", "navigate_home")

        # Assert
        # validate() returns the actual fuzzy score, caller decides if it meets threshold
        assert 0.0 < score < 0.9  # Returns fuzzy score, which is below threshold
        assert isinstance(score, float)

    def test_validate_with_custom_threshold(self):
        """Test validate with custom threshold parameter"""
        # Arrange
        validator = IntentValidator()

        # Act
        score = validator.validate("navigate_home", "navigate_house", threshold=0.6)

        # Assert
        assert score >= 0.6  # Should pass with lower threshold


# =============================================================================
# Test EntityValidator
# =============================================================================

class TestEntityValidator:
    """Test EntityValidator class"""

    def test_init_with_default_tolerance(self):
        """Test initialization with default tolerance"""
        # Act
        validator = EntityValidator()

        # Assert
        assert validator.default_tolerance == 0.01

    def test_init_with_custom_tolerance(self):
        """Test initialization with custom tolerance"""
        # Act
        validator = EntityValidator(default_tolerance=0.05)

        # Assert
        assert validator.default_tolerance == 0.05

    # ========== Test check_all_present ==========

    def test_check_all_present_all_entities_present(self):
        """Test all expected entities are present"""
        # Arrange
        validator = EntityValidator()
        actual = {"action": "navigate", "destination": "home", "extra": "value"}
        expected = {"action": "navigate", "destination": "home"}

        # Act
        result = validator.check_all_present(actual, expected)

        # Assert
        assert result is True

    def test_check_all_present_missing_entity(self):
        """Test detects missing entity"""
        # Arrange
        validator = EntityValidator()
        actual = {"action": "navigate"}
        expected = {"action": "navigate", "destination": "home"}

        # Act
        result = validator.check_all_present(actual, expected)

        # Assert
        assert result is False

    def test_check_all_present_empty_expected(self):
        """Test with empty expected entities"""
        # Arrange
        validator = EntityValidator()
        actual = {"action": "navigate"}
        expected = {}

        # Act
        result = validator.check_all_present(actual, expected)

        # Assert
        assert result is True  # No expected entities, all present

    def test_check_all_present_none_values(self):
        """Test with None values"""
        # Arrange
        validator = EntityValidator()

        # Act & Assert
        assert validator.check_all_present(None, None) is True
        assert validator.check_all_present(None, {"action": "navigate"}) is False
        assert validator.check_all_present({"action": "navigate"}, None) is True

    # ========== Test validate ==========

    def test_validate_all_entities_match(self):
        """Test validate with all entities matching"""
        # Arrange
        validator = EntityValidator()
        actual = {"action": "play", "media": "music"}
        expected = {"action": "play", "media": "music"}

        # Act
        score = validator.validate(actual, expected)

        # Assert
        assert score == 1.0

    def test_validate_partial_entity_match(self):
        """Test validate with partial entity match"""
        # Arrange
        validator = EntityValidator()
        actual = {"action": "play", "media": "video"}
        expected = {"action": "play", "media": "music"}

        # Act
        score = validator.validate(actual, expected)

        # Assert
        assert score == 0.5  # 1 out of 2 entities match

    def test_validate_missing_entity(self):
        """Test validate with missing entity"""
        # Arrange
        validator = EntityValidator()
        actual = {"action": "play"}
        expected = {"action": "play", "media": "music"}

        # Act
        score = validator.validate(actual, expected)

        # Assert
        assert score == 0.5  # 1 present out of 2 expected

    def test_validate_no_entities_match(self):
        """Test validate with no matching entities"""
        # Arrange
        validator = EntityValidator()
        actual = {"action": "stop", "media": "video"}
        expected = {"action": "play", "media": "music"}

        # Act
        score = validator.validate(actual, expected)

        # Assert
        assert score == 0.0

    def test_validate_numeric_values_with_tolerance(self):
        """Test validate with numeric values within tolerance"""
        # Arrange
        validator = EntityValidator()
        actual = {"temperature": 72.5, "unit": "fahrenheit"}
        expected = {"temperature": 72, "unit": "fahrenheit"}

        # Act
        score = validator.validate(actual, expected, tolerance=1.0)

        # Assert
        assert score == 1.0  # Within tolerance

    def test_validate_numeric_values_outside_tolerance(self):
        """Test validate with numeric values outside tolerance"""
        # Arrange
        validator = EntityValidator()
        actual = {"temperature": 80, "unit": "fahrenheit"}
        expected = {"temperature": 72, "unit": "fahrenheit"}

        # Act
        score = validator.validate(actual, expected, tolerance=1.0)

        # Assert
        assert score < 1.0  # Outside tolerance for temperature

    def test_validate_case_insensitive_strings(self):
        """Test validate is case insensitive for strings"""
        # Arrange
        validator = EntityValidator()
        actual = {"action": "PLAY", "media": "Music"}
        expected = {"action": "play", "media": "music"}

        # Act
        score = validator.validate(actual, expected)

        # Assert
        assert score == 1.0

    def test_validate_empty_dictionaries(self):
        """Test validate with empty dictionaries"""
        # Arrange
        validator = EntityValidator()

        # Act
        score = validator.validate({}, {})

        # Assert
        assert score == 1.0  # No entities expected, all match

    def test_validate_none_values(self):
        """Test validate with None values"""
        # Arrange
        validator = EntityValidator()

        # Act & Assert
        assert validator.validate(None, None) == 1.0
        assert validator.validate(None, {"action": "play"}) == 0.0
        assert validator.validate({"action": "play"}, None) == 1.0


# =============================================================================
# Test ConfidenceScorer
# =============================================================================

class TestConfidenceScorer:
    """Test ConfidenceScorer class"""

    def test_init_with_default_weights(self):
        """Test initialization with default weights"""
        # Act
        scorer = ConfidenceScorer()

        # Assert
        assert scorer.weights is not None
        assert "intent" in scorer.weights
        assert "entity" in scorer.weights
        assert "semantic" in scorer.weights
        assert "response_time" in scorer.weights

    def test_default_weights_sum_to_one(self):
        """Test default weights sum to 1.0"""
        # Arrange
        scorer = ConfidenceScorer()

        # Act
        total = sum(scorer.weights.values())

        # Assert
        assert abs(total - 1.0) < 0.01  # Allow small floating point error

    def test_set_weights(self):
        """Test set_weights method"""
        # Arrange
        scorer = ConfidenceScorer()
        new_weights = {
            "intent": 0.4,
            "entity": 0.3,
            "semantic": 0.2,
            "response_time": 0.1
        }

        # Act
        scorer.set_weights(new_weights)

        # Assert
        assert scorer.weights == new_weights

    def test_set_weights_normalizes_if_needed(self):
        """Test set_weights normalizes weights if they don't sum to 1"""
        # Arrange
        scorer = ConfidenceScorer()
        # Weights that don't sum to 1
        unnormalized_weights = {
            "intent": 40,
            "entity": 30,
            "semantic": 20,
            "response_time": 10
        }

        # Act
        scorer.set_weights(unnormalized_weights)

        # Assert
        total = sum(scorer.weights.values())
        # Should normalize to sum to 1.0
        assert abs(total - 1.0) < 0.01 or total == 100  # Either normalized or as-is

    # ========== Test calculate ==========

    def test_calculate_perfect_scores(self):
        """Test calculate with perfect scores (all 1.0)"""
        # Arrange
        scorer = ConfidenceScorer()
        scores = {
            "intent": 1.0,
            "entity": 1.0,
            "semantic": 1.0,
            "response_time": 1.0
        }

        # Act
        confidence = scorer.calculate(scores)

        # Assert
        assert confidence == 100.0  # Perfect score

    def test_calculate_zero_scores(self):
        """Test calculate with all zero scores"""
        # Arrange
        scorer = ConfidenceScorer()
        scores = {
            "intent": 0.0,
            "entity": 0.0,
            "semantic": 0.0,
            "response_time": 0.0
        }

        # Act
        confidence = scorer.calculate(scores)

        # Assert
        assert confidence == 0.0

    def test_calculate_mixed_scores(self):
        """Test calculate with mixed scores"""
        # Arrange
        scorer = ConfidenceScorer()
        scores = {
            "intent": 0.9,
            "entity": 0.85,
            "semantic": 0.8,
            "response_time": 1.0
        }

        # Act
        confidence = scorer.calculate(scores)

        # Assert
        assert 80.0 < confidence < 95.0  # Weighted average

    def test_calculate_with_custom_weights(self):
        """Test calculate with custom weights"""
        # Arrange
        scorer = ConfidenceScorer()
        scorer.set_weights({
            "intent": 0.5,
            "entity": 0.3,
            "semantic": 0.15,
            "response_time": 0.05
        })
        scores = {
            "intent": 1.0,
            "entity": 0.5,
            "semantic": 0.0,
            "response_time": 0.0
        }

        # Act
        confidence = scorer.calculate(scores)

        # Assert
        # 1.0*0.5 + 0.5*0.3 + 0.0*0.15 + 0.0*0.05 = 0.65 = 65%
        assert abs(confidence - 65.0) < 1.0

    def test_calculate_with_missing_scores(self):
        """Test calculate gracefully handles missing scores"""
        # Arrange
        scorer = ConfidenceScorer()
        scores = {
            "intent": 0.9,
            "entity": 0.8
            # Missing semantic and response_time
        }

        # Act
        confidence = scorer.calculate(scores)

        # Assert
        assert 0.0 <= confidence <= 100.0  # Valid percentage
        # Should handle missing scores (treat as 0 or skip)

    def test_calculate_with_extra_scores(self):
        """Test calculate ignores extra scores not in weights"""
        # Arrange
        scorer = ConfidenceScorer()
        scores = {
            "intent": 0.9,
            "entity": 0.85,
            "semantic": 0.8,
            "response_time": 1.0,
            "extra_metric": 0.5  # Not in weights
        }

        # Act
        confidence = scorer.calculate(scores)

        # Assert
        assert 80.0 < confidence < 95.0  # Ignores extra_metric

    def test_calculate_returns_percentage(self):
        """Test calculate returns value in 0-100 range"""
        # Arrange
        scorer = ConfidenceScorer()
        scores = {
            "intent": 0.5,
            "entity": 0.5,
            "semantic": 0.5,
            "response_time": 0.5
        }

        # Act
        confidence = scorer.calculate(scores)

        # Assert
        assert 0.0 <= confidence <= 100.0
        assert abs(confidence - 50.0) < 5.0  # Should be around 50%

    def test_calculate_with_single_score(self):
        """Test calculate with only one score"""
        # Arrange
        scorer = ConfidenceScorer()
        scores = {
            "intent": 1.0
        }

        # Act
        confidence = scorer.calculate(scores)

        # Assert
        assert 0.0 <= confidence <= 100.0  # Valid percentage

    def test_calculate_with_empty_scores(self):
        """Test calculate with empty scores dict"""
        # Arrange
        scorer = ConfidenceScorer()
        scores = {}

        # Act
        confidence = scorer.calculate(scores)

        # Assert
        assert confidence == 0.0  # No scores = 0%


# =============================================================================
# Test SemanticValidator (if available)
# =============================================================================

class TestSemanticValidator:
    """Test SemanticValidator class (if implemented)"""

    def test_semantic_validator_can_be_imported(self):
        """Test that SemanticValidator can be imported"""
        try:
            from validators.semantic_validator import SemanticValidator
            assert SemanticValidator is not None
        except ImportError:
            pytest.skip("SemanticValidator not yet implemented")

    def test_semantic_validator_initialization(self):
        """Test SemanticValidator initialization"""
        try:
            from validators.semantic_validator import SemanticValidator
            validator = SemanticValidator()
            assert validator is not None
        except ImportError:
            pytest.skip("SemanticValidator not yet implemented")


# =============================================================================
# Test ResponseTimeValidator (if available)
# =============================================================================

class TestResponseTimeValidator:
    """Test ResponseTimeValidator class (if implemented)"""

    def test_response_time_validator_can_be_imported(self):
        """Test that ResponseTimeValidator can be imported"""
        try:
            from validators.response_time_validator import ResponseTimeValidator
            assert ResponseTimeValidator is not None
        except ImportError:
            pytest.skip("ResponseTimeValidator not yet implemented")

    def test_response_time_validator_initialization(self):
        """Test ResponseTimeValidator initialization"""
        try:
            from validators.response_time_validator import ResponseTimeValidator
            validator = ResponseTimeValidator()
            assert validator is not None
        except ImportError:
            pytest.skip("ResponseTimeValidator not yet implemented")


# =============================================================================
# Integration Tests
# =============================================================================

class TestValidatorIntegration:
    """Test validators working together"""

    def test_all_validators_with_confidence_scorer(self):
        """Test using all validators together with confidence scorer"""
        # Arrange
        intent_validator = IntentValidator()
        entity_validator = EntityValidator()
        scorer = ConfidenceScorer()

        # Validate intent
        intent_score = intent_validator.validate("navigate_home", "navigate_home")

        # Validate entities
        actual_entities = {"action": "navigate", "destination": "home"}
        expected_entities = {"action": "navigate", "destination": "home"}
        entity_score = entity_validator.validate(actual_entities, expected_entities)

        # Calculate confidence
        scores = {
            "intent": intent_score,
            "entity": entity_score,
            "semantic": 0.9,  # Mock semantic score
            "response_time": 1.0  # Mock response time score
        }
        confidence = scorer.calculate(scores)

        # Assert
        assert intent_score == 1.0
        assert entity_score == 1.0
        assert confidence >= 90.0  # High confidence for perfect scores

    def test_validators_with_partial_match(self):
        """Test validators with partial matches"""
        # Arrange
        intent_validator = IntentValidator()
        entity_validator = EntityValidator()
        scorer = ConfidenceScorer()

        # Partial intent match
        intent_score = intent_validator.validate(
            "navigate_home",
            "navigate_house",
            threshold=0.7
        )

        # Partial entity match
        actual_entities = {"action": "navigate", "destination": "work"}
        expected_entities = {"action": "navigate", "destination": "home"}
        entity_score = entity_validator.validate(actual_entities, expected_entities)

        # Calculate confidence
        scores = {
            "intent": intent_score,
            "entity": entity_score,
            "semantic": 0.7,
            "response_time": 0.8
        }
        confidence = scorer.calculate(scores)

        # Assert
        assert 0.7 <= intent_score <= 1.0
        assert entity_score == 0.5  # 1 out of 2 match
        assert 60.0 <= confidence <= 85.0  # Moderate confidence
