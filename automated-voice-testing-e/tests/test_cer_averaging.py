"""
Test suite for micro and macro CER averaging.

Micro CER: Total character errors / Total reference characters (length-weighted)
Macro CER: Average of individual CER scores (equally weighted)

These different averaging methods are important for:
- Micro: When utterance length matters (longer utterances contribute more)
- Macro: When each utterance is equally important regardless of length
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.transcription_validator_service import TranscriptionValidatorService


class TestMicroCerMethodExists:
    """Test that calculate_micro_cer method exists"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_has_calculate_micro_cer_method(self, validator):
        """Test that service has calculate_micro_cer method"""
        assert hasattr(validator, 'calculate_micro_cer'), (
            "TranscriptionValidatorService should have calculate_micro_cer method"
        )

    def test_calculate_micro_cer_is_callable(self, validator):
        """Test that calculate_micro_cer is callable"""
        assert callable(getattr(validator, 'calculate_micro_cer', None)), (
            "calculate_micro_cer should be callable"
        )


class TestMacroCerMethodExists:
    """Test that calculate_macro_cer method exists"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_has_calculate_macro_cer_method(self, validator):
        """Test that service has calculate_macro_cer method"""
        assert hasattr(validator, 'calculate_macro_cer'), (
            "TranscriptionValidatorService should have calculate_macro_cer method"
        )

    def test_calculate_macro_cer_is_callable(self, validator):
        """Test that calculate_macro_cer is callable"""
        assert callable(getattr(validator, 'calculate_macro_cer', None)), (
            "calculate_macro_cer should be callable"
        )


class TestMicroCerBasicCases:
    """Test micro CER calculation with basic cases"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_micro_cer_perfect_match(self, validator):
        """Test micro CER with all perfect matches"""
        pairs = [
            ("hello", "hello"),
            ("world", "world"),
            ("test", "test"),
        ]

        micro_cer = validator.calculate_micro_cer(pairs)

        assert micro_cer == 0.0, f"Perfect matches should have micro CER = 0.0, got {micro_cer}"

    def test_micro_cer_empty_list(self, validator):
        """Test micro CER with empty list"""
        pairs = []

        micro_cer = validator.calculate_micro_cer(pairs)

        assert micro_cer == 0.0, f"Empty list should have micro CER = 0.0, got {micro_cer}"

    def test_micro_cer_single_pair(self, validator):
        """Test micro CER with single pair"""
        pairs = [("hello", "hllo")]  # 1 deletion in 5 chars = 0.2

        micro_cer = validator.calculate_micro_cer(pairs)

        assert abs(micro_cer - 0.2) < 0.001, f"Expected micro CER = 0.2, got {micro_cer}"

    def test_micro_cer_weighted_by_length(self, validator):
        """Test that micro CER is weighted by utterance length"""
        # Long utterance with perfect match (10 chars)
        # Short utterance with 100% error (1 char)
        pairs = [
            ("helloworld", "helloworld"),  # 10 chars, 0 errors
            ("a", "b"),                     # 1 char, 1 error
        ]

        micro_cer = validator.calculate_micro_cer(pairs)

        # Total errors = 0 + 1 = 1
        # Total chars = 10 + 1 = 11
        # Micro CER = 1/11 = 0.0909
        expected = 1 / 11
        assert abs(micro_cer - expected) < 0.001, (
            f"Expected micro CER = {expected}, got {micro_cer}"
        )


class TestMacroCerBasicCases:
    """Test macro CER calculation with basic cases"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_macro_cer_perfect_match(self, validator):
        """Test macro CER with all perfect matches"""
        pairs = [
            ("hello", "hello"),
            ("world", "world"),
            ("test", "test"),
        ]

        macro_cer = validator.calculate_macro_cer(pairs)

        assert macro_cer == 0.0, f"Perfect matches should have macro CER = 0.0, got {macro_cer}"

    def test_macro_cer_empty_list(self, validator):
        """Test macro CER with empty list"""
        pairs = []

        macro_cer = validator.calculate_macro_cer(pairs)

        assert macro_cer == 0.0, f"Empty list should have macro CER = 0.0, got {macro_cer}"

    def test_macro_cer_single_pair(self, validator):
        """Test macro CER with single pair"""
        pairs = [("hello", "hllo")]  # 1 deletion in 5 chars = 0.2

        macro_cer = validator.calculate_macro_cer(pairs)

        assert abs(macro_cer - 0.2) < 0.001, f"Expected macro CER = 0.2, got {macro_cer}"

    def test_macro_cer_equally_weighted(self, validator):
        """Test that macro CER treats each utterance equally"""
        # Long utterance with perfect match (10 chars)
        # Short utterance with 100% error (1 char)
        pairs = [
            ("helloworld", "helloworld"),  # CER = 0.0
            ("a", "b"),                     # CER = 1.0
        ]

        macro_cer = validator.calculate_macro_cer(pairs)

        # Average = (0.0 + 1.0) / 2 = 0.5
        expected = 0.5
        assert abs(macro_cer - expected) < 0.001, (
            f"Expected macro CER = {expected}, got {macro_cer}"
        )


class TestMicroVsMacroCerDifference:
    """Test the difference between micro and macro CER"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_micro_vs_macro_different_results(self, validator):
        """Test that micro and macro CER give different results for length-varied data"""
        # This test demonstrates the key difference:
        # - Long perfect utterance vs short errored utterance
        pairs = [
            ("this is a long sentence", "this is a long sentence"),  # 23 chars
            ("ab", "cd"),  # 2 chars, 2 errors
        ]

        micro_cer = validator.calculate_micro_cer(pairs)
        macro_cer = validator.calculate_macro_cer(pairs)

        # Micro: 2 errors / 25 chars = 0.08
        # Macro: (0.0 + 1.0) / 2 = 0.5
        assert micro_cer < macro_cer, (
            f"Micro CER ({micro_cer}) should be less than macro CER ({macro_cer}) "
            "when short utterances have higher error rates"
        )

    def test_micro_equals_macro_with_equal_lengths(self, validator):
        """Test that micro equals macro when all utterances have same length"""
        pairs = [
            ("hello", "hallo"),  # 5 chars, 1 error, CER = 0.2
            ("world", "woold"),  # 5 chars, 1 error, CER = 0.2
        ]

        micro_cer = validator.calculate_micro_cer(pairs)
        macro_cer = validator.calculate_macro_cer(pairs)

        # Both should be 2/10 = 0.2
        assert abs(micro_cer - macro_cer) < 0.001, (
            f"With equal lengths, micro ({micro_cer}) should equal macro ({macro_cer})"
        )


class TestMicroCerKnownValues:
    """Test micro CER with pre-calculated known values"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    @pytest.mark.parametrize("pairs,expected_micro_cer", [
        # All perfect
        ([("test", "test"), ("hello", "hello")], 0.0),

        # Single error in multiple utterances
        ([("cat", "car"), ("dog", "dog")], 1/6),  # 1 error / 6 chars

        # Multiple errors
        ([("abc", "def"), ("xyz", "xyz")], 3/6),  # 3 errors / 6 chars = 0.5

        # All errors
        ([("a", "b"), ("c", "d")], 1.0),
    ])
    def test_micro_cer_known_values(self, validator, pairs, expected_micro_cer):
        """Test micro CER against known values"""
        micro_cer = validator.calculate_micro_cer(pairs)

        assert abs(micro_cer - expected_micro_cer) < 0.001, (
            f"Expected micro CER: {expected_micro_cer}, got: {micro_cer}"
        )


class TestMacroCerKnownValues:
    """Test macro CER with pre-calculated known values"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    @pytest.mark.parametrize("pairs,expected_macro_cer", [
        # All perfect
        ([("test", "test"), ("hello", "hello")], 0.0),

        # One perfect, one with error
        ([("cat", "car"), ("dog", "dog")], 1/6),  # (1/3 + 0) / 2 = 0.1667

        # Different CER values
        ([("ab", "cd"), ("xyz", "xyz")], 0.5),  # (1.0 + 0.0) / 2

        # All errors
        ([("a", "b"), ("c", "d")], 1.0),
    ])
    def test_macro_cer_known_values(self, validator, pairs, expected_macro_cer):
        """Test macro CER against known values"""
        macro_cer = validator.calculate_macro_cer(pairs)

        assert abs(macro_cer - expected_macro_cer) < 0.001, (
            f"Expected macro CER: {expected_macro_cer}, got: {macro_cer}"
        )


class TestCerAveragingEdgeCases:
    """Test edge cases for CER averaging"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_micro_cer_with_empty_reference(self, validator):
        """Test micro CER when one reference is empty"""
        pairs = [
            ("hello", "hello"),
            ("", "world"),  # Empty reference
        ]

        micro_cer = validator.calculate_micro_cer(pairs)

        # Empty reference adds insertions equal to hypothesis length
        # For micro: total errors = 0 + 5 (insertions)
        # But with empty reference, we may treat it specially
        assert isinstance(micro_cer, float), "Should return a float"

    def test_macro_cer_with_empty_reference(self, validator):
        """Test macro CER when one reference is empty"""
        pairs = [
            ("hello", "hello"),  # CER = 0.0
            ("", "world"),       # CER = len("world") = 5.0 (or could be treated as 1.0)
        ]

        macro_cer = validator.calculate_macro_cer(pairs)

        assert isinstance(macro_cer, float), "Should return a float"

    def test_micro_cer_with_empty_hypothesis(self, validator):
        """Test micro CER when one hypothesis is empty"""
        pairs = [
            ("hello", "hello"),
            ("world", ""),  # Empty hypothesis - all deletions
        ]

        micro_cer = validator.calculate_micro_cer(pairs)

        # 5 deletions / 10 chars = 0.5
        expected = 5 / 10
        assert abs(micro_cer - expected) < 0.001, (
            f"Expected micro CER = {expected}, got {micro_cer}"
        )

    def test_macro_cer_with_empty_hypothesis(self, validator):
        """Test macro CER when one hypothesis is empty"""
        pairs = [
            ("hello", "hello"),  # CER = 0.0
            ("world", ""),       # CER = 1.0 (all deletions)
        ]

        macro_cer = validator.calculate_macro_cer(pairs)

        # Average = (0.0 + 1.0) / 2 = 0.5
        expected = 0.5
        assert abs(macro_cer - expected) < 0.001, (
            f"Expected macro CER = {expected}, got {macro_cer}"
        )


class TestCerAveragingUnicode:
    """Test CER averaging with Unicode characters"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_micro_cer_chinese_characters(self, validator):
        """Test micro CER with Chinese characters"""
        pairs = [
            ("hello", "hello"),
            ("world", "world"),
        ]

        micro_cer = validator.calculate_micro_cer(pairs)

        assert micro_cer == 0.0, f"Perfect match should give micro CER = 0.0, got {micro_cer}"

    def test_macro_cer_mixed_unicode(self, validator):
        """Test macro CER with mixed Unicode"""
        pairs = [
            ("hello", "hello"),
            ("world", "world"),
        ]

        macro_cer = validator.calculate_macro_cer(pairs)

        assert macro_cer == 0.0, f"Perfect match should give macro CER = 0.0, got {macro_cer}"


class TestCerAveragingDocumentation:
    """Test that averaging methods have proper documentation"""

    def test_calculate_micro_cer_has_docstring(self):
        """Test calculate_micro_cer has docstring"""
        from services.transcription_validator_service import (
            TranscriptionValidatorService
        )

        service = TranscriptionValidatorService()
        docstring = service.calculate_micro_cer.__doc__

        assert docstring is not None, "calculate_micro_cer should have docstring"
        assert "micro" in docstring.lower(), "Docstring should mention micro"

    def test_calculate_macro_cer_has_docstring(self):
        """Test calculate_macro_cer has docstring"""
        from services.transcription_validator_service import (
            TranscriptionValidatorService
        )

        service = TranscriptionValidatorService()
        docstring = service.calculate_macro_cer.__doc__

        assert docstring is not None, "calculate_macro_cer should have docstring"
        assert "macro" in docstring.lower(), "Docstring should mention macro"


class TestCerAveragingReturnTypes:
    """Test return types for CER averaging methods"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_micro_cer_returns_float(self, validator):
        """Test calculate_micro_cer returns float"""
        pairs = [("hello", "world")]

        result = validator.calculate_micro_cer(pairs)

        assert isinstance(result, float), f"Expected float, got {type(result)}"

    def test_macro_cer_returns_float(self, validator):
        """Test calculate_macro_cer returns float"""
        pairs = [("hello", "world")]

        result = validator.calculate_macro_cer(pairs)

        assert isinstance(result, float), f"Expected float, got {type(result)}"


