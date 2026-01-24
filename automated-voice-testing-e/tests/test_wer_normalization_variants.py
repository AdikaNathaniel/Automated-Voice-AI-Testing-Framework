"""
Test suite for configurable WER normalization variants.

Tests that WER calculation supports different normalization options:
- Case sensitivity (case_sensitive parameter)
- Punctuation handling (remove_punctuation parameter)
- Whitespace normalization (always applied)

These options allow comparing WER metrics with different standards.
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.transcription_validator_service import TranscriptionValidatorService


class TestWerNormalizationParameters:
    """Test that calculate_wer accepts normalization parameters"""

    @pytest.fixture
    def validator(self):
        """Create validator instance"""
        return TranscriptionValidatorService()

    def test_calculate_wer_accepts_case_sensitive_param(self, validator):
        """Test that calculate_wer accepts case_sensitive parameter"""
        import inspect
        sig = inspect.signature(validator.calculate_wer)
        params = list(sig.parameters.keys())

        assert "case_sensitive" in params, (
            "calculate_wer should accept case_sensitive parameter"
        )

    def test_calculate_wer_accepts_remove_punctuation_param(self, validator):
        """Test that calculate_wer accepts remove_punctuation parameter"""
        import inspect
        sig = inspect.signature(validator.calculate_wer)
        params = list(sig.parameters.keys())

        assert "remove_punctuation" in params, (
            "calculate_wer should accept remove_punctuation parameter"
        )

    def test_case_sensitive_defaults_to_false(self, validator):
        """Test that case_sensitive defaults to False (normalized)"""
        import inspect
        sig = inspect.signature(validator.calculate_wer)
        param = sig.parameters.get("case_sensitive")

        assert param is not None, "case_sensitive parameter should exist"
        assert param.default is False, (
            "case_sensitive should default to False"
        )

    def test_remove_punctuation_defaults_to_true(self, validator):
        """Test that remove_punctuation defaults to True"""
        import inspect
        sig = inspect.signature(validator.calculate_wer)
        param = sig.parameters.get("remove_punctuation")

        assert param is not None, "remove_punctuation parameter should exist"
        assert param.default is True, (
            "remove_punctuation should default to True"
        )


class TestWerCaseSensitivity:
    """Test case-sensitive WER calculation"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_default_case_insensitive_wer(self, validator):
        """Test that default WER is case-insensitive"""
        reference = "Hello World"
        hypothesis = "hello world"

        wer = validator.calculate_wer(reference, hypothesis)

        assert wer == 0.0, f"Default should be case-insensitive, got WER={wer}"

    def test_case_sensitive_wer_with_different_case(self, validator):
        """Test case-sensitive WER counts case differences as errors"""
        reference = "Hello World"
        hypothesis = "hello world"

        wer = validator.calculate_wer(
            reference, hypothesis, case_sensitive=True
        )

        # Both words have different case, so 2 substitutions in 2 words = 1.0
        assert wer == 1.0, f"Case-sensitive should have WER=1.0, got {wer}"

    def test_case_sensitive_wer_matching_case(self, validator):
        """Test case-sensitive WER with matching case"""
        reference = "Hello World"
        hypothesis = "Hello World"

        wer = validator.calculate_wer(
            reference, hypothesis, case_sensitive=True
        )

        assert wer == 0.0, f"Matching case should have WER=0.0, got {wer}"

    def test_case_sensitive_wer_partial_case_mismatch(self, validator):
        """Test case-sensitive WER with partial case mismatch"""
        reference = "The Quick Brown Fox"  # 4 words
        hypothesis = "the Quick brown Fox"  # 2 case mismatches

        wer = validator.calculate_wer(
            reference, hypothesis, case_sensitive=True
        )

        # 2 substitutions in 4 words = 0.5
        expected = 0.5
        assert abs(wer - expected) < 0.001, (
            f"Expected WER={expected}, got {wer}"
        )

    def test_case_insensitive_explicit_false(self, validator):
        """Test explicit case_sensitive=False"""
        reference = "HELLO WORLD"
        hypothesis = "hello world"

        wer = validator.calculate_wer(
            reference, hypothesis, case_sensitive=False
        )

        assert wer == 0.0, f"case_sensitive=False should give WER=0.0, got {wer}"


class TestWerPunctuationHandling:
    """Test punctuation handling in WER calculation"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_default_removes_punctuation(self, validator):
        """Test that default WER removes punctuation"""
        reference = "Hello, world!"
        hypothesis = "Hello world"

        wer = validator.calculate_wer(reference, hypothesis)

        assert wer == 0.0, f"Default should remove punctuation, got WER={wer}"

    def test_keep_punctuation_counts_as_error(self, validator):
        """Test WER with punctuation kept counts differences"""
        reference = "Hello, world!"
        hypothesis = "Hello world"

        wer = validator.calculate_wer(
            reference, hypothesis, remove_punctuation=False
        )

        # "Hello," != "Hello" and "world!" != "world"
        # So 2 substitutions in 2 words = 1.0
        assert wer == 1.0, f"Keeping punctuation should give WER=1.0, got {wer}"

    def test_keep_punctuation_matching(self, validator):
        """Test WER with matching punctuation"""
        reference = "Hello, world!"
        hypothesis = "Hello, world!"

        wer = validator.calculate_wer(
            reference, hypothesis, remove_punctuation=False
        )

        assert wer == 0.0, f"Matching punctuation should give WER=0.0, got {wer}"

    def test_keep_punctuation_partial_mismatch(self, validator):
        """Test WER with partial punctuation mismatch"""
        reference = "Hello, world."  # 2 words with punctuation
        hypothesis = "Hello world."  # Missing comma after Hello

        wer = validator.calculate_wer(
            reference, hypothesis, remove_punctuation=False
        )

        # "Hello," != "Hello" = 1 substitution in 2 words = 0.5
        expected = 0.5
        assert abs(wer - expected) < 0.001, (
            f"Expected WER={expected}, got {wer}"
        )

    def test_remove_punctuation_explicit_true(self, validator):
        """Test explicit remove_punctuation=True"""
        reference = "What's up?"
        hypothesis = "Whats up"

        wer = validator.calculate_wer(
            reference, hypothesis, remove_punctuation=True
        )

        assert wer == 0.0, (
            f"remove_punctuation=True should give WER=0.0, got {wer}"
        )


class TestWerCombinedNormalizationOptions:
    """Test combinations of normalization options"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_case_sensitive_with_punctuation_removed(self, validator):
        """Test case-sensitive WER with punctuation removed"""
        reference = "Hello, World!"
        hypothesis = "hello world"

        wer = validator.calculate_wer(
            reference, hypothesis,
            case_sensitive=True,
            remove_punctuation=True
        )

        # Punctuation removed, but case matters
        # "Hello" != "hello" and "World" != "world"
        # 2 substitutions in 2 words = 1.0
        assert wer == 1.0, f"Expected WER=1.0, got {wer}"

    def test_case_insensitive_with_punctuation_kept(self, validator):
        """Test case-insensitive WER with punctuation kept"""
        reference = "HELLO, WORLD!"
        hypothesis = "hello, world!"

        wer = validator.calculate_wer(
            reference, hypothesis,
            case_sensitive=False,
            remove_punctuation=False
        )

        # Case normalized, punctuation kept but matches
        assert wer == 0.0, f"Expected WER=0.0, got {wer}"

    def test_both_strict_with_perfect_match(self, validator):
        """Test strict mode (case-sensitive, keep punctuation) with perfect match"""
        reference = "Hello, World!"
        hypothesis = "Hello, World!"

        wer = validator.calculate_wer(
            reference, hypothesis,
            case_sensitive=True,
            remove_punctuation=False
        )

        assert wer == 0.0, f"Perfect match should give WER=0.0, got {wer}"

    def test_both_relaxed_with_differences(self, validator):
        """Test relaxed mode normalizes everything"""
        reference = "HELLO, WORLD!"
        hypothesis = "hello world"

        wer = validator.calculate_wer(
            reference, hypothesis,
            case_sensitive=False,
            remove_punctuation=True
        )

        assert wer == 0.0, f"Relaxed mode should give WER=0.0, got {wer}"


class TestWerWhitespaceNormalization:
    """Test that whitespace is always normalized"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_whitespace_normalized_in_default_mode(self, validator):
        """Test extra whitespace is normalized by default"""
        reference = "hello   world"
        hypothesis = "hello world"

        wer = validator.calculate_wer(reference, hypothesis)

        assert wer == 0.0, f"Whitespace should be normalized, got WER={wer}"

    def test_whitespace_normalized_in_case_sensitive_mode(self, validator):
        """Test whitespace normalized even in case-sensitive mode"""
        reference = "Hello   World"
        hypothesis = "Hello World"

        wer = validator.calculate_wer(
            reference, hypothesis, case_sensitive=True
        )

        assert wer == 0.0, f"Whitespace should still be normalized, got WER={wer}"

    def test_whitespace_normalized_with_punctuation_kept(self, validator):
        """Test whitespace normalized even with punctuation kept"""
        reference = "Hello,   world!"
        hypothesis = "Hello, world!"

        wer = validator.calculate_wer(
            reference, hypothesis, remove_punctuation=False
        )

        assert wer == 0.0, f"Whitespace should still be normalized, got WER={wer}"


class TestWerNormalizationEdgeCases:
    """Test edge cases with normalization options"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_empty_strings_with_options(self, validator):
        """Test empty strings work with all options"""
        wer = validator.calculate_wer(
            "", "",
            case_sensitive=True,
            remove_punctuation=False
        )

        assert wer == 0.0, f"Empty strings should give WER=0.0, got {wer}"

    def test_only_punctuation_removed_yields_empty(self, validator):
        """Test strings with only punctuation"""
        reference = "..."
        hypothesis = "..."

        wer = validator.calculate_wer(
            reference, hypothesis, remove_punctuation=True
        )

        # After punctuation removal, both are empty
        assert wer == 0.0, f"Only punctuation should give WER=0.0, got {wer}"

    def test_mixed_punctuation_and_words(self, validator):
        """Test mixed punctuation and words"""
        reference = "hello... world!!!"
        hypothesis = "hello world"

        wer = validator.calculate_wer(
            reference, hypothesis, remove_punctuation=True
        )

        assert wer == 0.0, f"Should normalize punctuation, got WER={wer}"


class TestWerNormalizationBackwardCompatibility:
    """Test backward compatibility of WER calculation"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_existing_wer_calls_still_work(self, validator):
        """Test that existing calls without params still work"""
        reference = "the cat sat on the mat"
        hypothesis = "the cat sat on the hat"

        # Old-style call without normalization params
        wer = validator.calculate_wer(reference, hypothesis)

        # Should still work with default behavior
        expected = 1/6
        assert abs(wer - expected) < 0.001, (
            f"Backward compatibility broken: expected {expected}, got {wer}"
        )

    def test_default_behavior_unchanged(self, validator):
        """Test default behavior matches original"""
        reference = "Hello World"
        hypothesis = "HELLO WORLD"

        wer = validator.calculate_wer(reference, hypothesis)

        # Default should be case-insensitive, punctuation removed
        assert wer == 0.0, f"Default behavior should normalize, got WER={wer}"


class TestWerNormalizationServiceIntegration:
    """Test normalization options work with service methods"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_find_differences_respects_normalization(self, validator):
        """Test that _find_differences uses same normalization"""
        reference = "Hello, World!"
        hypothesis = "hello world"

        # Should find no differences with default normalization
        result = validator.validate_transcription(reference, hypothesis)

        assert result['passed'] is True, "Should pass with normalization"


class TestWerNormalizationDocumentation:
    """Test that normalization options are documented"""

    def test_calculate_wer_has_docstring_for_params(self):
        """Test calculate_wer documents normalization parameters"""
        from services.transcription_validator_service import (
            TranscriptionValidatorService
        )

        service = TranscriptionValidatorService()
        docstring = service.calculate_wer.__doc__

        assert "case_sensitive" in docstring, (
            "Docstring should document case_sensitive parameter"
        )
        assert "remove_punctuation" in docstring or "punctuation" in docstring, (
            "Docstring should document punctuation handling"
        )

