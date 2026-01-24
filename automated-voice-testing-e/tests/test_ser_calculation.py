"""
Test suite for SER (Sentence Error Rate) calculation.

SER calculates the percentage of utterances with any error:
- For a single sentence: 0.0 if perfect match, 1.0 if any error
- Useful for understanding user-perceptible errors

SER is calculated as:
SER = (number of sentences with any error) / (total number of sentences)
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.transcription_validator_service import TranscriptionValidatorService


class TestSerMethodExists:
    """Test that calculate_ser method exists"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_has_calculate_ser_method(self, validator):
        """Test that service has calculate_ser method"""
        assert hasattr(validator, 'calculate_ser'), (
            "TranscriptionValidatorService should have calculate_ser method"
        )

    def test_calculate_ser_is_callable(self, validator):
        """Test that calculate_ser is callable"""
        assert callable(getattr(validator, 'calculate_ser', None)), (
            "calculate_ser should be callable"
        )


class TestSerBasicCases:
    """Test SER calculation with basic cases"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_perfect_match_ser_zero(self, validator):
        """Test that identical strings yield SER = 0.0"""
        reference = "hello world"
        hypothesis = "hello world"

        ser = validator.calculate_ser(reference, hypothesis)

        assert ser == 0.0, f"Perfect match should have SER = 0.0, got {ser}"

    def test_empty_both_ser_zero(self, validator):
        """Test that two empty strings yield SER = 0.0"""
        ser = validator.calculate_ser("", "")

        assert ser == 0.0, f"Empty strings should have SER = 0.0, got {ser}"

    def test_any_error_ser_one(self, validator):
        """Test that any difference yields SER = 1.0"""
        reference = "hello world"
        hypothesis = "hello word"  # One character difference

        ser = validator.calculate_ser(reference, hypothesis)

        assert ser == 1.0, f"Any error should have SER = 1.0, got {ser}"

    def test_single_word_match(self, validator):
        """Test single word perfect match"""
        ser = validator.calculate_ser("hello", "hello")

        assert ser == 0.0, f"Single word match should have SER = 0.0, got {ser}"

    def test_single_word_mismatch(self, validator):
        """Test single word mismatch"""
        ser = validator.calculate_ser("hello", "hallo")

        assert ser == 1.0, f"Single word mismatch should have SER = 1.0, got {ser}"


class TestSerNormalization:
    """Test SER with text normalization"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_case_insensitive_match(self, validator):
        """Test that SER is case-insensitive by default"""
        reference = "Hello World"
        hypothesis = "hello world"

        ser = validator.calculate_ser(reference, hypothesis)

        assert ser == 0.0, f"Case-insensitive match should have SER = 0.0, got {ser}"

    def test_punctuation_ignored(self, validator):
        """Test that punctuation is ignored"""
        reference = "Hello, world!"
        hypothesis = "hello world"

        ser = validator.calculate_ser(reference, hypothesis)

        assert ser == 0.0, f"Punctuation-normalized match should have SER = 0.0, got {ser}"

    def test_whitespace_normalized(self, validator):
        """Test that whitespace is normalized"""
        reference = "hello   world"
        hypothesis = "hello world"

        ser = validator.calculate_ser(reference, hypothesis)

        assert ser == 0.0, f"Whitespace-normalized match should have SER = 0.0, got {ser}"


class TestSerVsWerComparison:
    """Test that SER differs from WER in expected ways"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_ser_is_binary_wer_is_granular(self, validator):
        """Test that SER is 0 or 1 while WER shows proportion"""
        reference = "the cat sat on the mat"  # 6 words
        hypothesis = "the cat sat on the hat"  # 1 word different

        wer = validator.calculate_wer(reference, hypothesis)
        ser = validator.calculate_ser(reference, hypothesis)

        # WER = 1/6 = 0.1667
        # SER = 1.0 (any error)
        assert abs(wer - 1/6) < 0.001, f"WER should be ~0.1667, got {wer}"
        assert ser == 1.0, f"SER should be 1.0 for any error, got {ser}"

    def test_perfect_match_both_zero(self, validator):
        """Test that perfect match gives 0 for both WER and SER"""
        reference = "hello world"
        hypothesis = "hello world"

        wer = validator.calculate_wer(reference, hypothesis)
        ser = validator.calculate_ser(reference, hypothesis)

        assert wer == 0.0, f"WER should be 0.0, got {wer}"
        assert ser == 0.0, f"SER should be 0.0, got {ser}"


class TestSerEdgeCases:
    """Test SER calculation edge cases"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_empty_reference_non_empty_hypothesis(self, validator):
        """Test empty reference with non-empty hypothesis"""
        ser = validator.calculate_ser("", "hello")

        assert ser == 1.0, f"Empty reference should give SER = 1.0, got {ser}"

    def test_non_empty_reference_empty_hypothesis(self, validator):
        """Test non-empty reference with empty hypothesis"""
        ser = validator.calculate_ser("hello", "")

        assert ser == 1.0, f"Empty hypothesis should give SER = 1.0, got {ser}"

    def test_only_punctuation_difference(self, validator):
        """Test that only punctuation difference is normalized away"""
        reference = "hello world"
        hypothesis = "hello, world!"

        ser = validator.calculate_ser(reference, hypothesis)

        assert ser == 0.0, f"Only punctuation difference should give SER = 0.0, got {ser}"

    def test_extra_word(self, validator):
        """Test with extra word in hypothesis"""
        reference = "hello world"
        hypothesis = "hello big world"

        ser = validator.calculate_ser(reference, hypothesis)

        assert ser == 1.0, f"Extra word should give SER = 1.0, got {ser}"

    def test_missing_word(self, validator):
        """Test with missing word in hypothesis"""
        reference = "hello big world"
        hypothesis = "hello world"

        ser = validator.calculate_ser(reference, hypothesis)

        assert ser == 1.0, f"Missing word should give SER = 1.0, got {ser}"


class TestSerKnownValues:
    """Test SER with pre-calculated known values"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    @pytest.mark.parametrize("reference,hypothesis,expected_ser", [
        # Perfect matches
        ("test", "test", 0.0),
        ("hello world", "hello world", 0.0),
        ("the quick brown fox", "the quick brown fox", 0.0),

        # Any error results in SER = 1.0
        ("cat", "car", 1.0),
        ("hello", "helo", 1.0),
        ("the cat sat", "the cat set", 1.0),
        ("hello world", "hello", 1.0),
        ("hello", "hello world", 1.0),
    ])
    def test_known_ser_values(self, validator, reference, hypothesis, expected_ser):
        """Test SER calculation against known values"""
        ser = validator.calculate_ser(reference, hypothesis)

        assert abs(ser - expected_ser) < 0.001, (
            f"Reference: '{reference}', Hypothesis: '{hypothesis}'\n"
            f"Expected SER: {expected_ser}, Got: {ser}"
        )


class TestSerUnicodeSupport:
    """Test SER with Unicode characters"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_chinese_perfect_match(self, validator):
        """Test SER with Chinese characters - perfect match"""
        reference = "你好世界"
        hypothesis = "你好世界"

        ser = validator.calculate_ser(reference, hypothesis)

        assert ser == 0.0, f"Chinese perfect match should have SER = 0.0, got {ser}"

    def test_chinese_mismatch(self, validator):
        """Test SER with Chinese characters - mismatch"""
        reference = "你好世界"
        hypothesis = "你好地球"

        ser = validator.calculate_ser(reference, hypothesis)

        assert ser == 1.0, f"Chinese mismatch should have SER = 1.0, got {ser}"

    def test_emoji_handling(self, validator):
        """Test SER handles emojis"""
        reference = "hello world"
        hypothesis = "hello world"

        ser = validator.calculate_ser(reference, hypothesis)

        assert ser == 0.0, f"Should handle text with emojis, got SER = {ser}"


class TestSerDocumentation:
    """Test that calculate_ser method is documented"""

    def test_calculate_ser_has_docstring(self):
        """Test calculate_ser has docstring"""
        from services.transcription_validator_service import (
            TranscriptionValidatorService
        )

        service = TranscriptionValidatorService()
        docstring = service.calculate_ser.__doc__

        assert docstring is not None, "calculate_ser should have docstring"
        assert "Sentence" in docstring or "sentence" in docstring, (
            "Docstring should mention sentence"
        )

