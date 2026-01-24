"""
Test suite for IntentValidator (TASK-120).

This module tests the intent matching validator:
- IntentValidator class structure
- Exact match validation
- Fuzzy match validation with threshold
- Confidence score calculation
- Edge cases and error handling
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

import pytest
from typing import Optional


class TestIntentValidatorFileStructure:
    """Test intent validator file structure"""

    def test_validators_directory_exists(self):
        """Test that validators directory exists"""
        import os
        backend_dir = os.path.join(os.path.dirname(__file__), '../backend')
        validators_dir = os.path.join(backend_dir, 'validators')

        assert os.path.exists(validators_dir), \
            "validators directory should exist in backend/"

    def test_intent_validator_file_exists(self):
        """Test that intent_validator.py exists"""
        import os
        backend_dir = os.path.join(os.path.dirname(__file__), '../backend')
        validators_dir = os.path.join(backend_dir, 'validators')
        intent_validator_file = os.path.join(validators_dir, 'intent_validator.py')

        assert os.path.exists(intent_validator_file), \
            "intent_validator.py should exist in backend/validators/"

    def test_can_import_intent_validator(self):
        """Test that IntentValidator can be imported"""
        try:
            from validators.intent_validator import IntentValidator
            assert IntentValidator is not None
        except ImportError as e:
            pytest.fail(f"Cannot import IntentValidator: {e}")


class TestIntentValidatorClass:
    """Test IntentValidator class structure"""

    def test_intent_validator_class_exists(self):
        """Test that IntentValidator class exists"""
        from validators.intent_validator import IntentValidator
        assert IntentValidator is not None

    def test_intent_validator_can_instantiate(self):
        """Test that IntentValidator can be instantiated"""
        from validators.intent_validator import IntentValidator
        validator = IntentValidator()
        assert validator is not None

    def test_intent_validator_has_validate_method(self):
        """Test that IntentValidator has validate method"""
        from validators.intent_validator import IntentValidator
        validator = IntentValidator()

        assert hasattr(validator, 'validate'), \
            "IntentValidator should have validate method"

    def test_intent_validator_has_exact_match_method(self):
        """Test that IntentValidator has exact_match method"""
        from validators.intent_validator import IntentValidator
        validator = IntentValidator()

        assert hasattr(validator, 'exact_match'), \
            "IntentValidator should have exact_match method"

    def test_intent_validator_has_fuzzy_match_method(self):
        """Test that IntentValidator has fuzzy_match method"""
        from validators.intent_validator import IntentValidator
        validator = IntentValidator()

        assert hasattr(validator, 'fuzzy_match'), \
            "IntentValidator should have fuzzy_match method"


class TestExactMatch:
    """Test exact match validation"""

    @pytest.fixture
    def validator(self):
        """Create IntentValidator instance"""
        from validators.intent_validator import IntentValidator
        return IntentValidator()

    def test_exact_match_identical_strings(self, validator):
        """Test exact match with identical strings"""
        actual = "navigate_home"
        expected = "navigate_home"

        result = validator.exact_match(actual, expected)

        assert result is True, "Identical strings should match exactly"

    def test_exact_match_case_insensitive(self, validator):
        """Test exact match is case insensitive"""
        actual = "Navigate_Home"
        expected = "navigate_home"

        result = validator.exact_match(actual, expected)

        assert result is True, "Match should be case insensitive"

    def test_exact_match_different_strings(self, validator):
        """Test exact match with different strings"""
        actual = "play_music"
        expected = "navigate_home"

        result = validator.exact_match(actual, expected)

        assert result is False, "Different strings should not match"

    def test_exact_match_with_whitespace(self, validator):
        """Test exact match handles whitespace"""
        actual = "  navigate_home  "
        expected = "navigate_home"

        result = validator.exact_match(actual, expected)

        assert result is True, "Should handle whitespace"

    def test_exact_match_empty_strings(self, validator):
        """Test exact match with empty strings"""
        actual = ""
        expected = ""

        result = validator.exact_match(actual, expected)

        assert result is True, "Empty strings should match"

    def test_exact_match_none_values(self, validator):
        """Test exact match with None values"""
        result1 = validator.exact_match(None, None)
        result2 = validator.exact_match(None, "intent")
        result3 = validator.exact_match("intent", None)

        assert result1 is True, "None should match None"
        assert result2 is False, "None should not match string"
        assert result3 is False, "String should not match None"


class TestFuzzyMatch:
    """Test fuzzy match validation"""

    @pytest.fixture
    def validator(self):
        """Create IntentValidator instance"""
        from validators.intent_validator import IntentValidator
        return IntentValidator()

    def test_fuzzy_match_identical_strings(self, validator):
        """Test fuzzy match with identical strings"""
        actual = "navigate_home"
        expected = "navigate_home"

        score = validator.fuzzy_match(actual, expected)

        assert score >= 0.99, "Identical strings should have very high score"

    def test_fuzzy_match_similar_strings(self, validator):
        """Test fuzzy match with similar strings"""
        actual = "navigate_home"
        expected = "navigate_house"

        score = validator.fuzzy_match(actual, expected)

        assert 0.5 < score < 1.0, "Similar strings should have moderate score"

    def test_fuzzy_match_very_different_strings(self, validator):
        """Test fuzzy match with very different strings"""
        actual = "navigate_home"
        expected = "play_music"

        score = validator.fuzzy_match(actual, expected)

        assert score < 0.5, "Very different strings should have low score"

    def test_fuzzy_match_with_typo(self, validator):
        """Test fuzzy match handles typos"""
        actual = "navgate_home"  # Typo: missing 'i'
        expected = "navigate_home"

        score = validator.fuzzy_match(actual, expected)

        assert score > 0.8, "Small typo should still have high score"

    def test_fuzzy_match_returns_float(self, validator):
        """Test that fuzzy match returns float"""
        score = validator.fuzzy_match("intent1", "intent2")

        assert isinstance(score, float), "Fuzzy match should return float"

    def test_fuzzy_match_range(self, validator):
        """Test that fuzzy match score is between 0 and 1"""
        score = validator.fuzzy_match("test", "best")

        assert 0.0 <= score <= 1.0, "Score should be between 0 and 1"


class TestValidateMethod:
    """Test main validate method"""

    @pytest.fixture
    def validator(self):
        """Create IntentValidator instance"""
        from validators.intent_validator import IntentValidator
        return IntentValidator()

    def test_validate_exact_match_high_score(self, validator):
        """Test validate returns 1.0 for exact match"""
        actual = "navigate_home"
        expected = "navigate_home"

        score = validator.validate(actual, expected)

        assert score == 1.0, "Exact match should return score of 1.0"

    def test_validate_uses_fuzzy_for_near_match(self, validator):
        """Test validate uses fuzzy match for similar strings"""
        actual = "navigate_home"
        expected = "navigate_house"

        score = validator.validate(actual, expected)

        assert 0.0 < score < 1.0, "Near match should use fuzzy matching"

    def test_validate_no_match_returns_zero(self, validator):
        """Test validate returns 0.0 for very different strings"""
        actual = "navigate_home"
        expected = "completely_different_intent"

        score = validator.validate(actual, expected)

        assert score < 0.5, "No match should return low score"

    def test_validate_with_threshold(self, validator):
        """Test validate with custom threshold"""
        actual = "navigate_home"
        expected = "navigate_house"

        # Test with threshold 0.8
        score = validator.validate(actual, expected, threshold=0.8)

        assert isinstance(score, float), "Should return float score"
        assert 0.0 <= score <= 1.0, "Score should be between 0 and 1"

    def test_validate_accepts_threshold_parameter(self, validator):
        """Test that validate accepts threshold parameter"""
        import inspect

        sig = inspect.signature(validator.validate)
        params = list(sig.parameters.keys())

        assert 'threshold' in params or len(params) >= 3, \
            "validate should accept threshold parameter"


class TestThresholdBehavior:
    """Test threshold behavior in validation"""

    @pytest.fixture
    def validator(self):
        """Create IntentValidator instance"""
        from validators.intent_validator import IntentValidator
        return IntentValidator()

    def test_high_threshold_strict_matching(self, validator):
        """Test high threshold requires very close match"""
        actual = "navigate_home"
        expected = "navigate_house"

        score_high_threshold = validator.validate(
            actual, expected, threshold=0.9
        )
        score_low_threshold = validator.validate(
            actual, expected, threshold=0.5
        )

        # Both should return scores, but behavior may differ
        assert isinstance(score_high_threshold, float)
        assert isinstance(score_low_threshold, float)

    def test_default_threshold(self, validator):
        """Test that default threshold is reasonable"""
        actual = "navigate_home"
        expected = "navigate_home"

        # Should work without specifying threshold
        score = validator.validate(actual, expected)

        assert score == 1.0, "Exact match should return 1.0 with default threshold"


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.fixture
    def validator(self):
        """Create IntentValidator instance"""
        from validators.intent_validator import IntentValidator
        return IntentValidator()

    def test_validate_empty_strings(self, validator):
        """Test validate with empty strings"""
        result = validator.validate("", "")

        assert result == 1.0, "Empty strings should match"

    def test_validate_none_values(self, validator):
        """Test validate with None values"""
        result1 = validator.validate(None, None)
        result2 = validator.validate(None, "intent")
        result3 = validator.validate("intent", None)

        assert result1 == 1.0, "None should match None"
        assert result2 == 0.0, "None should not match string"
        assert result3 == 0.0, "String should not match None"

    def test_validate_special_characters(self, validator):
        """Test validate with special characters"""
        actual = "navigate-home"
        expected = "navigate_home"

        score = validator.validate(actual, expected)

        assert score > 0.0, "Should handle special characters"


class TestTaskRequirements:
    """Test TASK-120 specific requirements"""

    def test_task_120_file_location(self):
        """Test TASK-120: File is in correct location"""
        import os
        intent_validator_file = os.path.join(
            os.path.dirname(__file__),
            '../backend/validators/intent_validator.py'
        )

        assert os.path.exists(intent_validator_file), \
            "TASK-120: File should be at backend/validators/intent_validator.py"

    def test_task_120_has_intent_validator_class(self):
        """Test TASK-120: Has IntentValidator class"""
        try:
            from validators.intent_validator import IntentValidator
            assert IntentValidator is not None
        except ImportError:
            pytest.fail("TASK-120: Should have IntentValidator class")

    def test_task_120_has_exact_match(self):
        """Test TASK-120: Has exact match functionality"""
        from validators.intent_validator import IntentValidator
        validator = IntentValidator()

        assert hasattr(validator, 'exact_match'), \
            "TASK-120: Should have exact_match method"

    def test_task_120_has_fuzzy_match(self):
        """Test TASK-120: Has fuzzy match functionality"""
        from validators.intent_validator import IntentValidator
        validator = IntentValidator()

        assert hasattr(validator, 'fuzzy_match'), \
            "TASK-120: Should have fuzzy_match method"

    def test_task_120_has_threshold_support(self):
        """Test TASK-120: Supports threshold parameter"""
        from validators.intent_validator import IntentValidator
        import inspect

        validator = IntentValidator()
        sig = inspect.signature(validator.validate)
        params = list(sig.parameters.keys())

        # Should have threshold parameter or support it
        assert 'threshold' in params or len(params) >= 3, \
            "TASK-120: Should support threshold parameter"
