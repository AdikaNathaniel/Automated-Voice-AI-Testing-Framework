"""
Test suite for ResponseTimeValidator (TASK-122).

This module tests the response time validator:
- ResponseTimeValidator class structure
- Compare against expected thresholds
- P95 (95th percentile) calculations
- Performance validation
- Edge cases and error handling
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

import pytest
from typing import List


class TestResponseTimeValidatorFileStructure:
    """Test response time validator file structure"""

    def test_validators_directory_exists(self):
        """Test that validators directory exists"""
        import os
        backend_dir = os.path.join(os.path.dirname(__file__), '../backend')
        validators_dir = os.path.join(backend_dir, 'validators')

        assert os.path.exists(validators_dir), \
            "validators directory should exist in backend/"

    def test_response_time_validator_file_exists(self):
        """Test that response_time_validator.py exists"""
        import os
        backend_dir = os.path.join(os.path.dirname(__file__), '../backend')
        validators_dir = os.path.join(backend_dir, 'validators')
        response_time_validator_file = os.path.join(
            validators_dir, 'response_time_validator.py'
        )

        assert os.path.exists(response_time_validator_file), \
            "response_time_validator.py should exist in backend/validators/"

    def test_can_import_response_time_validator(self):
        """Test that ResponseTimeValidator can be imported"""
        try:
            from validators.response_time_validator import ResponseTimeValidator
            assert ResponseTimeValidator is not None
        except ImportError as e:
            pytest.fail(f"Cannot import ResponseTimeValidator: {e}")


class TestResponseTimeValidatorClass:
    """Test ResponseTimeValidator class structure"""

    def test_response_time_validator_class_exists(self):
        """Test that ResponseTimeValidator class exists"""
        from validators.response_time_validator import ResponseTimeValidator
        assert ResponseTimeValidator is not None

    def test_response_time_validator_can_instantiate(self):
        """Test that ResponseTimeValidator can be instantiated"""
        from validators.response_time_validator import ResponseTimeValidator
        validator = ResponseTimeValidator()
        assert validator is not None

    def test_response_time_validator_has_validate_method(self):
        """Test that ResponseTimeValidator has validate method"""
        from validators.response_time_validator import ResponseTimeValidator
        validator = ResponseTimeValidator()

        assert hasattr(validator, 'validate'), \
            "ResponseTimeValidator should have validate method"

    def test_response_time_validator_has_calculate_p95_method(self):
        """Test that ResponseTimeValidator has calculate_p95 method"""
        from validators.response_time_validator import ResponseTimeValidator
        validator = ResponseTimeValidator()

        assert hasattr(validator, 'calculate_p95'), \
            "ResponseTimeValidator should have calculate_p95 method"

    def test_response_time_validator_has_check_threshold_method(self):
        """Test that ResponseTimeValidator has check_threshold method"""
        from validators.response_time_validator import ResponseTimeValidator
        validator = ResponseTimeValidator()

        assert hasattr(validator, 'check_threshold'), \
            "ResponseTimeValidator should have check_threshold method"


class TestCheckThreshold:
    """Test threshold checking"""

    @pytest.fixture
    def validator(self):
        """Create ResponseTimeValidator instance"""
        from validators.response_time_validator import ResponseTimeValidator
        return ResponseTimeValidator()

    def test_within_threshold(self, validator):
        """Test response time within threshold"""
        actual = 150  # ms
        threshold = 200  # ms

        result = validator.check_threshold(actual, threshold)

        assert result is True, "Response time within threshold should pass"

    def test_exactly_at_threshold(self, validator):
        """Test response time exactly at threshold"""
        actual = 200  # ms
        threshold = 200  # ms

        result = validator.check_threshold(actual, threshold)

        assert result is True, "Response time at threshold should pass"

    def test_exceeds_threshold(self, validator):
        """Test response time exceeds threshold"""
        actual = 250  # ms
        threshold = 200  # ms

        result = validator.check_threshold(actual, threshold)

        assert result is False, "Response time exceeding threshold should fail"

    def test_zero_threshold(self, validator):
        """Test with zero threshold"""
        actual = 10  # ms
        threshold = 0  # ms

        result = validator.check_threshold(actual, threshold)

        assert result is False, "Any positive time should fail zero threshold"

    def test_zero_response_time(self, validator):
        """Test with zero response time"""
        actual = 0  # ms
        threshold = 100  # ms

        result = validator.check_threshold(actual, threshold)

        assert result is True, "Zero response time should pass"


class TestCalculateP95:
    """Test P95 (95th percentile) calculation"""

    @pytest.fixture
    def validator(self):
        """Create ResponseTimeValidator instance"""
        from validators.response_time_validator import ResponseTimeValidator
        return ResponseTimeValidator()

    def test_p95_simple_case(self, validator):
        """Test P95 calculation with simple values"""
        response_times = [100, 200, 300, 400, 500]

        p95 = validator.calculate_p95(response_times)

        assert p95 == 500, "P95 of [100, 200, 300, 400, 500] should be 500"

    def test_p95_larger_dataset(self, validator):
        """Test P95 with larger dataset"""
        # 100 values from 1 to 100
        response_times = list(range(1, 101))

        p95 = validator.calculate_p95(response_times)

        # P95 should be around 95
        assert 94 <= p95 <= 96, f"P95 should be around 95, got {p95}"

    def test_p95_unsorted_values(self, validator):
        """Test P95 with unsorted values"""
        response_times = [500, 100, 300, 200, 400]

        p95 = validator.calculate_p95(response_times)

        assert p95 == 500, "P95 should work with unsorted values"

    def test_p95_single_value(self, validator):
        """Test P95 with single value"""
        response_times = [150]

        p95 = validator.calculate_p95(response_times)

        assert p95 == 150, "P95 of single value should be that value"

    def test_p95_all_same_values(self, validator):
        """Test P95 with all same values"""
        response_times = [100, 100, 100, 100, 100]

        p95 = validator.calculate_p95(response_times)

        assert p95 == 100, "P95 of identical values should be that value"

    def test_p95_returns_numeric(self, validator):
        """Test that P95 returns numeric value"""
        response_times = [100, 200, 300]

        p95 = validator.calculate_p95(response_times)

        assert isinstance(p95, (int, float)), "P95 should return numeric value"


class TestValidateMethod:
    """Test main validate method"""

    @pytest.fixture
    def validator(self):
        """Create ResponseTimeValidator instance"""
        from validators.response_time_validator import ResponseTimeValidator
        return ResponseTimeValidator()

    def test_validate_single_time_within_threshold(self, validator):
        """Test validate with single response time within threshold"""
        actual = 150  # ms
        threshold = 200  # ms

        score = validator.validate(actual, threshold)

        assert score == 1.0, "Time within threshold should return 1.0"

    def test_validate_single_time_exceeds_threshold(self, validator):
        """Test validate with single response time exceeding threshold"""
        actual = 250  # ms
        threshold = 200  # ms

        score = validator.validate(actual, threshold)

        assert score < 1.0, "Time exceeding threshold should return score < 1.0"

    def test_validate_multiple_times_all_pass(self, validator):
        """Test validate with multiple response times all within threshold"""
        actual_times = [100, 150, 180]
        threshold = 200

        score = validator.validate(actual_times, threshold)

        assert score == 1.0, "All times within threshold should return 1.0"

    def test_validate_multiple_times_some_exceed(self, validator):
        """Test validate with some times exceeding threshold"""
        actual_times = [100, 250, 180]  # One exceeds 200ms
        threshold = 200

        score = validator.validate(actual_times, threshold)

        assert 0.0 < score < 1.0, "Partial pass should return score between 0 and 1"

    def test_validate_uses_p95_for_multiple_times(self, validator):
        """Test that validate uses P95 for multiple response times"""
        # Create dataset where P95 is within threshold
        actual_times = [50] * 95 + [250] * 5  # P95 should be around 250
        threshold = 300

        score = validator.validate(actual_times, threshold)

        # P95 (250) is within threshold (300), should pass
        assert score > 0.5, "P95 within threshold should have high score"

    def test_validate_returns_float(self, validator):
        """Test that validate returns float"""
        score = validator.validate(100, 200)

        assert isinstance(score, float), "Validate should return float"

    def test_validate_score_range(self, validator):
        """Test that validate score is between 0 and 1"""
        score1 = validator.validate(100, 200)
        score2 = validator.validate(300, 200)

        assert 0.0 <= score1 <= 1.0, "Score should be between 0 and 1"
        assert 0.0 <= score2 <= 1.0, "Score should be between 0 and 1"


class TestScoreCalculation:
    """Test score calculation logic"""

    @pytest.fixture
    def validator(self):
        """Create ResponseTimeValidator instance"""
        from validators.response_time_validator import ResponseTimeValidator
        return ResponseTimeValidator()

    def test_score_perfect_time(self, validator):
        """Test score for instant response (0ms)"""
        actual = 0
        threshold = 200

        score = validator.validate(actual, threshold)

        assert score == 1.0, "Instant response should get perfect score"

    def test_score_degrades_with_time(self, validator):
        """Test that score degrades as response time increases"""
        threshold = 200

        score_fast = validator.validate(50, threshold)
        score_medium = validator.validate(150, threshold)
        score_slow = validator.validate(199, threshold)

        assert score_fast >= score_medium, "Faster should score >= medium"
        assert score_medium >= score_slow, "Medium should score >= slower"

    def test_score_for_exceeded_threshold(self, validator):
        """Test score when threshold is exceeded"""
        actual = 300
        threshold = 200

        score = validator.validate(actual, threshold)

        assert score < 0.5, "Significantly exceeded threshold should have low score"


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.fixture
    def validator(self):
        """Create ResponseTimeValidator instance"""
        from validators.response_time_validator import ResponseTimeValidator
        return ResponseTimeValidator()

    def test_validate_empty_list(self, validator):
        """Test validate with empty list of response times"""
        actual_times = []
        threshold = 200

        # Should handle empty list gracefully
        score = validator.validate(actual_times, threshold)

        assert isinstance(score, (float, int)), "Should return numeric score"

    def test_validate_negative_threshold(self, validator):
        """Test validate with negative threshold"""
        actual = 100
        threshold = -50

        # Should handle negative threshold (probably all times exceed it)
        score = validator.validate(actual, threshold)

        assert isinstance(score, (float, int)), "Should return numeric score"

    def test_calculate_p95_empty_list(self, validator):
        """Test P95 calculation with empty list"""
        response_times = []

        # Should handle empty list gracefully
        try:
            p95 = validator.calculate_p95(response_times)
            assert isinstance(p95, (int, float, type(None))), \
                "Should return numeric or None"
        except (ValueError, IndexError):
            # Acceptable to raise error for empty list
            pass

    def test_validate_very_large_values(self, validator):
        """Test validate with very large values"""
        actual = 1000000  # 1 second in ms
        threshold = 200

        score = validator.validate(actual, threshold)

        assert isinstance(score, float), "Should handle large values"
        assert 0.0 <= score <= 1.0, "Score should still be in valid range"


class TestTaskRequirements:
    """Test TASK-122 specific requirements"""

    def test_task_122_file_location(self):
        """Test TASK-122: File is in correct location"""
        import os
        response_time_validator_file = os.path.join(
            os.path.dirname(__file__),
            '../backend/validators/response_time_validator.py'
        )

        assert os.path.exists(response_time_validator_file), \
            "TASK-122: File should be at backend/validators/response_time_validator.py"

    def test_task_122_has_response_time_validator_class(self):
        """Test TASK-122: Has ResponseTimeValidator class"""
        try:
            from validators.response_time_validator import ResponseTimeValidator
            assert ResponseTimeValidator is not None
        except ImportError:
            pytest.fail("TASK-122: Should have ResponseTimeValidator class")

    def test_task_122_threshold_comparison(self):
        """Test TASK-122: Has threshold comparison functionality"""
        from validators.response_time_validator import ResponseTimeValidator
        validator = ResponseTimeValidator()

        assert hasattr(validator, 'check_threshold'), \
            "TASK-122: Should have check_threshold method"

    def test_task_122_p95_calculations(self):
        """Test TASK-122: Has P95 calculation functionality"""
        from validators.response_time_validator import ResponseTimeValidator
        validator = ResponseTimeValidator()

        assert hasattr(validator, 'calculate_p95'), \
            "TASK-122: Should have calculate_p95 method"

    def test_task_122_validate_method(self):
        """Test TASK-122: Has validate method"""
        from validators.response_time_validator import ResponseTimeValidator
        validator = ResponseTimeValidator()

        assert hasattr(validator, 'validate'), \
            "TASK-122: Should have validate method"
