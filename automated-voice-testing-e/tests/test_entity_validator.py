"""
Test suite for EntityValidator (TASK-121).

This module tests the entity extraction validator:
- EntityValidator class structure
- Check all expected entities present
- Value matching with tolerance
- Different data types support
- Edge cases and error handling
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

import pytest
from typing import Dict, Any


class TestEntityValidatorFileStructure:
    """Test entity validator file structure"""

    def test_validators_directory_exists(self):
        """Test that validators directory exists"""
        import os
        backend_dir = os.path.join(os.path.dirname(__file__), '../backend')
        validators_dir = os.path.join(backend_dir, 'validators')

        assert os.path.exists(validators_dir), \
            "validators directory should exist in backend/"

    def test_entity_validator_file_exists(self):
        """Test that entity_validator.py exists"""
        import os
        backend_dir = os.path.join(os.path.dirname(__file__), '../backend')
        validators_dir = os.path.join(backend_dir, 'validators')
        entity_validator_file = os.path.join(validators_dir, 'entity_validator.py')

        assert os.path.exists(entity_validator_file), \
            "entity_validator.py should exist in backend/validators/"

    def test_can_import_entity_validator(self):
        """Test that EntityValidator can be imported"""
        try:
            from validators.entity_validator import EntityValidator
            assert EntityValidator is not None
        except ImportError as e:
            pytest.fail(f"Cannot import EntityValidator: {e}")


class TestEntityValidatorClass:
    """Test EntityValidator class structure"""

    def test_entity_validator_class_exists(self):
        """Test that EntityValidator class exists"""
        from validators.entity_validator import EntityValidator
        assert EntityValidator is not None

    def test_entity_validator_can_instantiate(self):
        """Test that EntityValidator can be instantiated"""
        from validators.entity_validator import EntityValidator
        validator = EntityValidator()
        assert validator is not None

    def test_entity_validator_has_validate_method(self):
        """Test that EntityValidator has validate method"""
        from validators.entity_validator import EntityValidator
        validator = EntityValidator()

        assert hasattr(validator, 'validate'), \
            "EntityValidator should have validate method"

    def test_entity_validator_has_check_all_present_method(self):
        """Test that EntityValidator has check_all_present method"""
        from validators.entity_validator import EntityValidator
        validator = EntityValidator()

        assert hasattr(validator, 'check_all_present'), \
            "EntityValidator should have check_all_present method"

    def test_entity_validator_has_match_value_method(self):
        """Test that EntityValidator has match_value method"""
        from validators.entity_validator import EntityValidator
        validator = EntityValidator()

        assert hasattr(validator, 'match_value'), \
            "EntityValidator should have match_value method"


class TestCheckAllPresent:
    """Test checking all expected entities are present"""

    @pytest.fixture
    def validator(self):
        """Create EntityValidator instance"""
        from validators.entity_validator import EntityValidator
        return EntityValidator()

    def test_all_entities_present(self, validator):
        """Test when all expected entities are present"""
        actual = {
            "action": "navigate",
            "destination": "home",
            "time": "now"
        }
        expected = {
            "action": "navigate",
            "destination": "home"
        }

        result = validator.check_all_present(actual, expected)

        assert result is True, "All expected entities are present"

    def test_missing_entity(self, validator):
        """Test when expected entity is missing"""
        actual = {
            "action": "navigate"
        }
        expected = {
            "action": "navigate",
            "destination": "home"
        }

        result = validator.check_all_present(actual, expected)

        assert result is False, "Missing entity should return False"

    def test_empty_expected_entities(self, validator):
        """Test with no expected entities"""
        actual = {"action": "navigate"}
        expected = {}

        result = validator.check_all_present(actual, expected)

        assert result is True, "No expected entities means all present"

    def test_empty_actual_entities(self, validator):
        """Test with no actual entities"""
        actual = {}
        expected = {"action": "navigate"}

        result = validator.check_all_present(actual, expected)

        assert result is False, "Missing all entities should return False"

    def test_both_empty(self, validator):
        """Test with both empty"""
        actual = {}
        expected = {}

        result = validator.check_all_present(actual, expected)

        assert result is True, "Both empty should return True"


class TestMatchValue:
    """Test value matching with tolerance"""

    @pytest.fixture
    def validator(self):
        """Create EntityValidator instance"""
        from validators.entity_validator import EntityValidator
        return EntityValidator()

    def test_exact_string_match(self, validator):
        """Test exact string value match"""
        result = validator.match_value("home", "home")

        assert result is True, "Exact strings should match"

    def test_string_case_insensitive(self, validator):
        """Test string matching is case insensitive"""
        result = validator.match_value("Home", "home")

        assert result is True, "String match should be case insensitive"

    def test_string_with_whitespace(self, validator):
        """Test string matching handles whitespace"""
        result = validator.match_value("  home  ", "home")

        assert result is True, "Should handle whitespace"

    def test_different_strings(self, validator):
        """Test different strings don't match"""
        result = validator.match_value("home", "office")

        assert result is False, "Different strings should not match"

    def test_exact_number_match(self, validator):
        """Test exact number match"""
        result = validator.match_value(42, 42)

        assert result is True, "Exact numbers should match"

    def test_number_with_tolerance(self, validator):
        """Test number matching with tolerance"""
        result = validator.match_value(42.1, 42, tolerance=0.2)

        assert result is True, "Numbers within tolerance should match"

    def test_number_outside_tolerance(self, validator):
        """Test number outside tolerance"""
        result = validator.match_value(45, 42, tolerance=0.1)

        assert result is False, "Numbers outside tolerance should not match"

    def test_boolean_match(self, validator):
        """Test boolean value matching"""
        result1 = validator.match_value(True, True)
        result2 = validator.match_value(False, False)
        result3 = validator.match_value(True, False)

        assert result1 is True, "True should match True"
        assert result2 is True, "False should match False"
        assert result3 is False, "True should not match False"

    def test_none_values(self, validator):
        """Test None value matching"""
        result1 = validator.match_value(None, None)
        result2 = validator.match_value(None, "value")
        result3 = validator.match_value("value", None)

        assert result1 is True, "None should match None"
        assert result2 is False, "None should not match value"
        assert result3 is False, "Value should not match None"

    def test_type_mismatch(self, validator):
        """Test mismatched types"""
        result1 = validator.match_value("42", 42)
        result2 = validator.match_value(42, "42")

        # Should handle type conversion or return False
        assert isinstance(result1, bool), "Should return boolean"
        assert isinstance(result2, bool), "Should return boolean"


class TestValidateMethod:
    """Test main validate method"""

    @pytest.fixture
    def validator(self):
        """Create EntityValidator instance"""
        from validators.entity_validator import EntityValidator
        return EntityValidator()

    def test_validate_all_entities_match(self, validator):
        """Test validate with all entities matching"""
        actual = {
            "action": "navigate",
            "destination": "home",
            "confidence": 0.95
        }
        expected = {
            "action": "navigate",
            "destination": "home"
        }

        score = validator.validate(actual, expected)

        assert score == 1.0, "All matching entities should return 1.0"

    def test_validate_partial_match(self, validator):
        """Test validate with partial entity match"""
        actual = {
            "action": "navigate",
            "destination": "office"  # Different value
        }
        expected = {
            "action": "navigate",
            "destination": "home"
        }

        score = validator.validate(actual, expected)

        assert 0.0 < score < 1.0, "Partial match should return score between 0 and 1"

    def test_validate_no_match(self, validator):
        """Test validate with no matching entities"""
        actual = {
            "action": "play",
            "media": "music"
        }
        expected = {
            "action": "navigate",
            "destination": "home"
        }

        score = validator.validate(actual, expected)

        assert score < 0.5, "No match should return low score"

    def test_validate_missing_entities(self, validator):
        """Test validate with missing expected entities"""
        actual = {
            "action": "navigate"
        }
        expected = {
            "action": "navigate",
            "destination": "home",
            "time": "now"
        }

        score = validator.validate(actual, expected)

        assert score < 1.0, "Missing entities should reduce score"

    def test_validate_with_tolerance(self, validator):
        """Test validate with numeric tolerance"""
        actual = {
            "temperature": 72.5,
            "unit": "fahrenheit"
        }
        expected = {
            "temperature": 72,
            "unit": "fahrenheit"
        }

        score = validator.validate(actual, expected, tolerance=1.0)

        assert score == 1.0, "Values within tolerance should match"

    def test_validate_returns_float(self, validator):
        """Test that validate returns float"""
        actual = {"action": "test"}
        expected = {"action": "test"}

        score = validator.validate(actual, expected)

        assert isinstance(score, float), "Validate should return float"

    def test_validate_score_range(self, validator):
        """Test that validate score is between 0 and 1"""
        actual = {"action": "test"}
        expected = {"action": "test"}

        score = validator.validate(actual, expected)

        assert 0.0 <= score <= 1.0, "Score should be between 0 and 1"


class TestToleranceBehavior:
    """Test tolerance behavior for numeric values"""

    @pytest.fixture
    def validator(self):
        """Create EntityValidator instance"""
        from validators.entity_validator import EntityValidator
        return EntityValidator()

    def test_default_tolerance(self, validator):
        """Test default tolerance for numbers"""
        # Small difference should match with default tolerance
        result = validator.match_value(10.01, 10.0)

        assert isinstance(result, bool), "Should return boolean"

    def test_custom_tolerance(self, validator):
        """Test custom tolerance parameter"""
        result1 = validator.match_value(10.5, 10.0, tolerance=1.0)
        result2 = validator.match_value(10.5, 10.0, tolerance=0.1)

        assert result1 is True, "Should match with high tolerance"
        assert result2 is False, "Should not match with low tolerance"

    def test_zero_tolerance(self, validator):
        """Test zero tolerance requires exact match"""
        result1 = validator.match_value(10.0, 10.0, tolerance=0.0)
        result2 = validator.match_value(10.01, 10.0, tolerance=0.0)

        assert result1 is True, "Exact values should match with zero tolerance"
        assert result2 is False, "Different values should not match with zero tolerance"


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.fixture
    def validator(self):
        """Create EntityValidator instance"""
        from validators.entity_validator import EntityValidator
        return EntityValidator()

    def test_validate_empty_dictionaries(self, validator):
        """Test validate with empty dictionaries"""
        result = validator.validate({}, {})

        assert result == 1.0, "Empty dictionaries should match"

    def test_validate_none_dictionaries(self, validator):
        """Test validate with None values"""
        result1 = validator.validate(None, None)
        result2 = validator.validate(None, {"key": "value"})
        result3 = validator.validate({"key": "value"}, None)

        # Should handle None gracefully
        assert isinstance(result1, (float, int)), "Should return numeric score"
        assert isinstance(result2, (float, int)), "Should return numeric score"
        assert isinstance(result3, (float, int)), "Should return numeric score"

    def test_nested_values(self, validator):
        """Test with nested dictionary values"""
        actual = {"location": {"city": "Boston", "state": "MA"}}
        expected = {"location": {"city": "Boston", "state": "MA"}}

        # May or may not support nested dicts - just check it doesn't crash
        result = validator.match_value(actual["location"], expected["location"])

        assert isinstance(result, bool), "Should return boolean"

    def test_list_values(self, validator):
        """Test with list values"""
        result = validator.match_value(["a", "b"], ["a", "b"])

        assert isinstance(result, bool), "Should return boolean"


class TestTaskRequirements:
    """Test TASK-121 specific requirements"""

    def test_task_121_file_location(self):
        """Test TASK-121: File is in correct location"""
        import os
        entity_validator_file = os.path.join(
            os.path.dirname(__file__),
            '../backend/validators/entity_validator.py'
        )

        assert os.path.exists(entity_validator_file), \
            "TASK-121: File should be at backend/validators/entity_validator.py"

    def test_task_121_has_entity_validator_class(self):
        """Test TASK-121: Has EntityValidator class"""
        try:
            from validators.entity_validator import EntityValidator
            assert EntityValidator is not None
        except ImportError:
            pytest.fail("TASK-121: Should have EntityValidator class")

    def test_task_121_checks_all_entities_present(self):
        """Test TASK-121: Checks all expected entities present"""
        from validators.entity_validator import EntityValidator
        validator = EntityValidator()

        assert hasattr(validator, 'check_all_present'), \
            "TASK-121: Should have check_all_present method"

    def test_task_121_value_matching(self):
        """Test TASK-121: Value matching functionality"""
        from validators.entity_validator import EntityValidator
        validator = EntityValidator()

        assert hasattr(validator, 'match_value'), \
            "TASK-121: Should have match_value method"

    def test_task_121_tolerance_support(self):
        """Test TASK-121: Supports tolerance parameter"""
        from validators.entity_validator import EntityValidator
        import inspect

        validator = EntityValidator()
        sig = inspect.signature(validator.match_value)
        params = list(sig.parameters.keys())

        # Should support tolerance parameter
        assert 'tolerance' in params or len(params) >= 3, \
            "TASK-121: Should support tolerance parameter"
