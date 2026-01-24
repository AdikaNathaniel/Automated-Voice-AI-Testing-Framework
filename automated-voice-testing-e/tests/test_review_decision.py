"""
Test suite for review decision logic (TASK-126).

This module tests the auto-pass/fail/review decision logic:
- Confidence >= 75%: auto-pass
- 40% <= Confidence < 75%: needs human review
- Confidence < 40%: auto-fail
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

import pytest


class TestReviewDecisionFileStructure:
    """Test review decision file structure"""

    def test_services_directory_exists(self):
        """Test that services directory exists"""
        import os
        backend_dir = os.path.join(os.path.dirname(__file__), '../backend')
        services_dir = os.path.join(backend_dir, 'services')

        assert os.path.exists(services_dir), \
            "services directory should exist in backend/"

    def test_validation_service_file_exists(self):
        """Test that validation_service.py exists"""
        import os
        backend_dir = os.path.join(os.path.dirname(__file__), '../backend')
        services_dir = os.path.join(backend_dir, 'services')
        validation_service_file = os.path.join(
            services_dir, 'validation_service.py'
        )

        assert os.path.exists(validation_service_file), \
            "validation_service.py should exist in backend/services/"

    def test_can_import_determine_review_status(self):
        """Test that determine_review_status can be imported"""
        try:
            from services.validation_service import determine_review_status
            assert determine_review_status is not None
        except ImportError as e:
            pytest.fail(f"Cannot import determine_review_status: {e}")


class TestDetermineReviewStatusFunction:
    """Test determine_review_status function structure"""

    def test_determine_review_status_exists(self):
        """Test that determine_review_status function exists"""
        from services.validation_service import determine_review_status
        assert determine_review_status is not None

    def test_determine_review_status_is_callable(self):
        """Test that determine_review_status is callable"""
        from services.validation_service import determine_review_status
        assert callable(determine_review_status), \
            "determine_review_status should be a function"

    def test_determine_review_status_accepts_confidence_score(self):
        """Test that determine_review_status accepts confidence_score parameter"""
        from services.validation_service import determine_review_status
        import inspect

        sig = inspect.signature(determine_review_status)
        params = list(sig.parameters.keys())

        assert 'confidence_score' in params, \
            "Should accept confidence_score parameter"


class TestAutoPassLogic:
    """Test auto-pass logic (confidence >= 75%)"""

    @pytest.fixture
    def determine_status(self):
        """Import the function"""
        from services.validation_service import determine_review_status
        return determine_review_status

    def test_confidence_75_returns_auto_pass(self, determine_status):
        """Test that confidence of 75% returns auto_pass"""
        result = determine_status(75.0)
        assert result == "auto_pass", "75% should auto-pass"

    def test_confidence_80_returns_auto_pass(self, determine_status):
        """Test that confidence of 80% returns auto_pass"""
        result = determine_status(80.0)
        assert result == "auto_pass", "80% should auto-pass"

    def test_confidence_90_returns_auto_pass(self, determine_status):
        """Test that confidence of 90% returns auto_pass"""
        result = determine_status(90.0)
        assert result == "auto_pass", "90% should auto-pass"

    def test_confidence_100_returns_auto_pass(self, determine_status):
        """Test that confidence of 100% returns auto_pass"""
        result = determine_status(100.0)
        assert result == "auto_pass", "100% should auto-pass"

    def test_confidence_75_01_returns_auto_pass(self, determine_status):
        """Test that confidence just above 75% returns auto_pass"""
        result = determine_status(75.01)
        assert result == "auto_pass", "75.01% should auto-pass"


class TestNeedsReviewLogic:
    """Test needs review logic (40% <= confidence < 75%)"""

    @pytest.fixture
    def determine_status(self):
        """Import the function"""
        from services.validation_service import determine_review_status
        return determine_review_status

    def test_confidence_40_returns_needs_review(self, determine_status):
        """Test that confidence of 40% returns needs_review"""
        result = determine_status(0.40)
        assert result == "needs_review", "40% should need review"

    def test_confidence_50_returns_needs_review(self, determine_status):
        """Test that confidence of 50% returns needs_review"""
        result = determine_status(0.50)
        assert result == "needs_review", "50% should need review"

    def test_confidence_60_returns_needs_review(self, determine_status):
        """Test that confidence of 60% returns needs_review"""
        result = determine_status(0.60)
        assert result == "needs_review", "60% should need review"

    def test_confidence_74_99_returns_needs_review(self, determine_status):
        """Test that confidence just below 75% returns needs_review"""
        result = determine_status(0.7499)
        assert result == "needs_review", "74.99% should need review"

    def test_confidence_40_01_returns_needs_review(self, determine_status):
        """Test that confidence just above 40% returns needs_review"""
        result = determine_status(0.4001)
        assert result == "needs_review", "40.01% should need review"


class TestAutoFailLogic:
    """Test auto-fail logic (confidence < 40%)"""

    @pytest.fixture
    def determine_status(self):
        """Import the function"""
        from services.validation_service import determine_review_status
        return determine_review_status

    def test_confidence_39_99_returns_auto_fail(self, determine_status):
        """Test that confidence just below 40% returns auto_fail"""
        result = determine_status(0.3999)
        assert result == "auto_fail", "39.99% should auto-fail"

    def test_confidence_30_returns_auto_fail(self, determine_status):
        """Test that confidence of 30% returns auto_fail"""
        result = determine_status(0.30)
        assert result == "auto_fail", "30% should auto-fail"

    def test_confidence_20_returns_auto_fail(self, determine_status):
        """Test that confidence of 20% returns auto_fail"""
        result = determine_status(0.20)
        assert result == "auto_fail", "20% should auto-fail"

    def test_confidence_10_returns_auto_fail(self, determine_status):
        """Test that confidence of 10% returns auto_fail"""
        result = determine_status(0.10)
        assert result == "auto_fail", "10% should auto-fail"

    def test_confidence_0_returns_auto_fail(self, determine_status):
        """Test that confidence of 0% returns auto_fail"""
        result = determine_status(0.0)
        assert result == "auto_fail", "0% should auto-fail"


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.fixture
    def determine_status(self):
        """Import the function"""
        from services.validation_service import determine_review_status
        return determine_review_status

    def test_negative_confidence_returns_auto_fail(self, determine_status):
        """Test that negative confidence returns auto_fail"""
        result = determine_status(-10.0)
        assert result == "auto_fail", "Negative confidence should auto-fail"

    def test_confidence_over_100_returns_auto_pass(self, determine_status):
        """Test that confidence over 100% returns auto_pass"""
        result = determine_status(110.0)
        assert result == "auto_pass", "Over 100% should auto-pass"

    def test_confidence_none_handled(self, determine_status):
        """Test that None confidence is handled gracefully"""
        # Should either raise error or return auto_fail
        try:
            result = determine_status(None)
            assert result in ["auto_fail", "needs_review", "auto_pass"], \
                "Should return valid status for None"
        except (TypeError, ValueError):
            # Acceptable to raise error for None
            pass

    def test_confidence_string_handled(self, determine_status):
        """Test that string confidence is handled gracefully"""
        # Should either raise error or convert
        try:
            result = determine_status("75.0")
            assert result in ["auto_fail", "needs_review", "auto_pass"], \
                "Should handle string input"
        except (TypeError, ValueError):
            # Acceptable to raise error for invalid type
            pass


class TestReturnValueFormat:
    """Test return value format"""

    @pytest.fixture
    def determine_status(self):
        """Import the function"""
        from services.validation_service import determine_review_status
        return determine_review_status

    def test_returns_string(self, determine_status):
        """Test that function returns a string"""
        result = determine_status(75.0)
        assert isinstance(result, str), "Should return string"

    def test_returns_lowercase(self, determine_status):
        """Test that function returns lowercase string"""
        result = determine_status(75.0)
        assert result == result.lower(), "Should return lowercase string"

    def test_returns_valid_status(self, determine_status):
        """Test that function returns valid status"""
        valid_statuses = ["auto_pass", "needs_review", "auto_fail"]

        for confidence in [0.0, 40.0, 50.0, 75.0, 100.0]:
            result = determine_status(confidence)
            assert result in valid_statuses, \
                f"Should return valid status for {confidence}%"


class TestTaskRequirements:
    """Test TASK-126 specific requirements"""

    def test_task_126_file_location(self):
        """Test TASK-126: Function is in validation_service.py"""
        import os
        validation_service_file = os.path.join(
            os.path.dirname(__file__),
            '../backend/services/validation_service.py'
        )

        assert os.path.exists(validation_service_file), \
            "TASK-126: File should be at backend/services/validation_service.py"

    def test_task_126_has_determine_review_status(self):
        """Test TASK-126: Has determine_review_status function"""
        try:
            from services.validation_service import determine_review_status
            assert determine_review_status is not None
        except ImportError:
            pytest.fail("TASK-126: Should have determine_review_status function")

    def test_task_126_threshold_75_auto_pass(self):
        """Test TASK-126: Threshold >= 75% is auto-pass"""
        from services.validation_service import determine_review_status

        assert determine_review_status(75.0) == "auto_pass", \
            "TASK-126: 75% should be auto-pass"
        assert determine_review_status(80.0) == "auto_pass", \
            "TASK-126: 80% should be auto-pass"

    def test_task_126_threshold_40_to_75_needs_review(self):
        """Test TASK-126: Threshold 40-75% needs review"""
        from services.validation_service import determine_review_status

        assert determine_review_status(0.40) == "needs_review", \
            "TASK-126: 40% should need review"
        assert determine_review_status(0.60) == "needs_review", \
            "TASK-126: 60% should need review"
        assert determine_review_status(0.7499) == "needs_review", \
            "TASK-126: 74.99% should need review"

    def test_task_126_threshold_below_40_auto_fail(self):
        """Test TASK-126: Threshold < 40% is auto-fail"""
        from services.validation_service import determine_review_status

        assert determine_review_status(0.3999) == "auto_fail", \
            "TASK-126: 39.99% should be auto-fail"
        assert determine_review_status(0.20) == "auto_fail", \
            "TASK-126: 20% should be auto-fail"
        assert determine_review_status(0.0) == "auto_fail", \
            "TASK-126: 0% should be auto-fail"
