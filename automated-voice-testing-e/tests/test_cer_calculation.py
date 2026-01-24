"""
Test suite for CER (Character Error Rate) calculation.

CER is calculated at the character level using Levenshtein distance:
CER = (S + D + I) / N
Where: S = substitutions, D = deletions, I = insertions, N = reference characters

CER is critical for:
- Languages without word boundaries (Chinese, Japanese, Thai, Korean)
- Character-level accuracy measurement
- Detailed error analysis
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.transcription_validator_service import TranscriptionValidatorService


class TestCerMethodExists:
    """Test that calculate_cer method exists"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_has_calculate_cer_method(self, validator):
        """Test that service has calculate_cer method"""
        assert hasattr(validator, 'calculate_cer'), (
            "TranscriptionValidatorService should have calculate_cer method"
        )

    def test_calculate_cer_is_callable(self, validator):
        """Test that calculate_cer is callable"""
        assert callable(getattr(validator, 'calculate_cer', None)), (
            "calculate_cer should be callable"
        )


class TestCerBasicCases:
    """Test CER calculation with basic cases"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_perfect_match_cer_zero(self, validator):
        """Test that identical strings yield CER = 0.0"""
        reference = "hello world"
        hypothesis = "hello world"

        cer = validator.calculate_cer(reference, hypothesis)

        assert cer == 0.0, f"Perfect match should have CER = 0.0, got {cer}"

    def test_empty_both_cer_zero(self, validator):
        """Test that two empty strings yield CER = 0.0"""
        cer = validator.calculate_cer("", "")

        assert cer == 0.0, f"Empty strings should have CER = 0.0, got {cer}"

    def test_single_char_match(self, validator):
        """Test single character perfect match"""
        cer = validator.calculate_cer("a", "a")

        assert cer == 0.0, f"Single char match should have CER = 0.0, got {cer}"

    def test_complete_substitution_cer(self, validator):
        """Test all characters substituted yields CER = 1.0"""
        reference = "abc"
        hypothesis = "xyz"  # 3 substitutions, 3 reference chars

        cer = validator.calculate_cer(reference, hypothesis)

        assert cer == 1.0, f"Complete substitution should have CER = 1.0, got {cer}"


class TestCerCharacterSubstitutions:
    """Test CER calculation for character substitution errors"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_single_substitution(self, validator):
        """Test single character substitution"""
        reference = "cat"  # 3 chars
        hypothesis = "car"  # 1 substitution

        cer = validator.calculate_cer(reference, hypothesis)

        # CER = 1/3 = 0.3333
        expected = 1/3
        assert abs(cer - expected) < 0.001, f"Expected CER ~{expected:.4f}, got {cer}"

    def test_multiple_substitutions(self, validator):
        """Test multiple substitutions"""
        reference = "hello"  # 5 chars
        hypothesis = "hxllx"  # 2 substitutions

        cer = validator.calculate_cer(reference, hypothesis)

        # CER = 2/5 = 0.4
        expected = 0.4
        assert abs(cer - expected) < 0.001, f"Expected CER = {expected}, got {cer}"


class TestCerCharacterDeletions:
    """Test CER calculation for character deletion errors"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_single_deletion(self, validator):
        """Test single character deletion"""
        reference = "hello"  # 5 chars
        hypothesis = "hllo"  # 1 deletion

        cer = validator.calculate_cer(reference, hypothesis)

        # CER = 1/5 = 0.2
        expected = 0.2
        assert abs(cer - expected) < 0.001, f"Expected CER = {expected}, got {cer}"

    def test_multiple_deletions(self, validator):
        """Test multiple deletions"""
        reference = "abcdef"  # 6 chars
        hypothesis = "acf"  # 3 deletions

        cer = validator.calculate_cer(reference, hypothesis)

        # CER = 3/6 = 0.5
        expected = 0.5
        assert abs(cer - expected) < 0.001, f"Expected CER = {expected}, got {cer}"

    def test_all_deleted(self, validator):
        """Test all characters deleted"""
        reference = "hello"  # 5 chars
        hypothesis = ""  # All deleted

        cer = validator.calculate_cer(reference, hypothesis)

        # CER = 5/5 = 1.0
        assert cer == 1.0, f"All deleted should have CER = 1.0, got {cer}"


class TestCerCharacterInsertions:
    """Test CER calculation for character insertion errors"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_single_insertion(self, validator):
        """Test single character insertion"""
        reference = "cat"  # 3 chars
        hypothesis = "cart"  # 1 insertion

        cer = validator.calculate_cer(reference, hypothesis)

        # CER = 1/3 = 0.3333
        expected = 1/3
        assert abs(cer - expected) < 0.001, f"Expected CER ~{expected:.4f}, got {cer}"

    def test_multiple_insertions(self, validator):
        """Test multiple insertions"""
        reference = "ab"  # 2 chars
        hypothesis = "axxbxx"  # 4 insertions

        cer = validator.calculate_cer(reference, hypothesis)

        # CER = 4/2 = 2.0
        expected = 2.0
        assert abs(cer - expected) < 0.001, f"Expected CER = {expected}, got {cer}"


class TestCerLanguagesWithoutWordBoundaries:
    """Test CER with languages that don't have word boundaries"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_chinese_perfect_match(self, validator):
        """Test CER with Chinese characters - perfect match"""
        reference = "你好世界"  # 4 characters
        hypothesis = "你好世界"

        cer = validator.calculate_cer(reference, hypothesis)

        assert cer == 0.0, f"Chinese perfect match should have CER = 0.0, got {cer}"

    def test_chinese_single_error(self, validator):
        """Test CER with Chinese characters - single error"""
        reference = "你好世界"  # 4 characters
        hypothesis = "你好地界"  # 1 substitution

        cer = validator.calculate_cer(reference, hypothesis)

        # CER = 1/4 = 0.25
        expected = 0.25
        assert abs(cer - expected) < 0.001, f"Expected CER = {expected}, got {cer}"

    def test_japanese_hiragana(self, validator):
        """Test CER with Japanese hiragana"""
        reference = "こんにちは"  # 5 characters
        hypothesis = "こんにちわ"  # 1 substitution (wa for ha)

        cer = validator.calculate_cer(reference, hypothesis)

        # CER = 1/5 = 0.2
        expected = 0.2
        assert abs(cer - expected) < 0.001, f"Expected CER = {expected}, got {cer}"

    def test_korean(self, validator):
        """Test CER with Korean characters"""
        reference = "안녕하세요"  # 5 characters
        hypothesis = "안녕하세요"

        cer = validator.calculate_cer(reference, hypothesis)

        assert cer == 0.0, f"Korean perfect match should have CER = 0.0, got {cer}"

    def test_thai(self, validator):
        """Test CER with Thai characters"""
        reference = "สวัสดี"  # Thai greeting
        hypothesis = "สวัสดี"

        cer = validator.calculate_cer(reference, hypothesis)

        assert cer == 0.0, f"Thai perfect match should have CER = 0.0, got {cer}"


class TestCerVsWer:
    """Test that CER works at character level vs WER at word level"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_cer_more_granular_than_wer(self, validator):
        """Test that CER is more granular than WER"""
        reference = "hello"
        hypothesis = "helo"  # Missing one 'l'

        wer = validator.calculate_wer(reference, hypothesis)
        cer = validator.calculate_cer(reference, hypothesis)

        # WER treats "helo" as different word from "hello" = 1/1 = 1.0
        # CER counts 1 deletion in 5 chars = 1/5 = 0.2
        assert wer == 1.0, f"WER should be 1.0, got {wer}"
        assert abs(cer - 0.2) < 0.001, f"CER should be ~0.2, got {cer}"

    def test_cer_vs_wer_multiple_words(self, validator):
        """Test CER vs WER with multiple words"""
        reference = "the cat sat"  # 11 chars (including spaces)
        hypothesis = "the cat set"  # 1 char substitution

        wer = validator.calculate_wer(reference, hypothesis)
        cer = validator.calculate_cer(reference, hypothesis)

        # WER: 1 word wrong out of 3 = 1/3 = 0.333
        # CER: 1 char wrong out of 11 = 1/11 = 0.091
        assert abs(wer - 1/3) < 0.001, f"WER should be ~0.333, got {wer}"
        assert abs(cer - 1/11) < 0.001, f"CER should be ~0.091, got {cer}"


class TestCerEdgeCases:
    """Test CER calculation edge cases"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_whitespace_handling(self, validator):
        """Test that whitespace is counted in CER"""
        reference = "a b"  # 3 chars including space
        hypothesis = "ab"  # Missing space

        cer = validator.calculate_cer(reference, hypothesis)

        # CER = 1/3 = 0.3333
        expected = 1/3
        assert abs(cer - expected) < 0.001, f"Expected CER ~{expected:.4f}, got {cer}"

    def test_very_high_cer(self, validator):
        """Test CER can exceed 1.0 with many insertions"""
        reference = "a"  # 1 char
        hypothesis = "abcde"  # 4 insertions

        cer = validator.calculate_cer(reference, hypothesis)

        # CER = 4/1 = 4.0
        expected = 4.0
        assert abs(cer - expected) < 0.001, f"Expected CER = {expected}, got {cer}"

    def test_numbers_and_special_chars(self, validator):
        """Test CER with numbers and special characters"""
        reference = "abc123!@#"  # 9 chars
        hypothesis = "abc123!@#"

        cer = validator.calculate_cer(reference, hypothesis)

        assert cer == 0.0, f"Perfect match should have CER = 0.0, got {cer}"


class TestCerKnownValues:
    """Test CER with pre-calculated known values"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    @pytest.mark.parametrize("reference,hypothesis,expected_cer", [
        # Perfect matches
        ("test", "test", 0.0),
        ("abc", "abc", 0.0),

        # Single errors
        ("cat", "car", 1/3),  # 1 substitution
        ("cat", "at", 1/3),   # 1 deletion
        ("cat", "cart", 1/3), # 1 insertion

        # Multiple errors
        ("hello", "hllo", 0.2),   # 1 deletion in 5 chars
        ("abcd", "axyd", 0.5),    # 2 substitutions in 4 chars

        # All different
        ("abc", "xyz", 1.0),  # 3 substitutions in 3 chars
    ])
    def test_known_cer_values(self, validator, reference, hypothesis, expected_cer):
        """Test CER calculation against known values"""
        cer = validator.calculate_cer(reference, hypothesis)

        assert abs(cer - expected_cer) < 0.001, (
            f"Reference: '{reference}', Hypothesis: '{hypothesis}'\n"
            f"Expected CER: {expected_cer}, Got: {cer}"
        )


class TestCerNormalization:
    """Test CER handles text normalization options"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_cer_case_sensitive_by_default(self, validator):
        """Test that CER is case-sensitive by default (unlike WER)"""
        reference = "Hello"
        hypothesis = "hello"

        cer = validator.calculate_cer(reference, hypothesis)

        # CER should count 'H' vs 'h' as 1 error
        # 1/5 = 0.2
        expected = 0.2
        assert abs(cer - expected) < 0.001, f"Expected CER = {expected}, got {cer}"


class TestCerDocumentation:
    """Test that calculate_cer method is documented"""

    def test_calculate_cer_has_docstring(self):
        """Test calculate_cer has docstring"""
        from services.transcription_validator_service import (
            TranscriptionValidatorService
        )

        service = TranscriptionValidatorService()
        docstring = service.calculate_cer.__doc__

        assert docstring is not None, "calculate_cer should have docstring"
        assert "Character" in docstring or "character" in docstring, (
            "Docstring should mention character"
        )

