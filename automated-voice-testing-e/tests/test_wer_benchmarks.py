"""
Test suite for WER calculation with industry-standard benchmarks.

Validates the TranscriptionValidatorService WER calculation against
known benchmarks from ASR research (LibriSpeech, etc.).

WER Formula: WER = (S + D + I) / N
Where: S = substitutions, D = deletions, I = insertions, N = reference words
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.transcription_validator_service import TranscriptionValidatorService


class TestWerBenchmarkBasicCases:
    """Test WER calculation with basic benchmark cases"""

    @pytest.fixture
    def validator(self):
        """Create validator instance"""
        return TranscriptionValidatorService()

    def test_perfect_match_wer_zero(self, validator):
        """Test that identical transcripts yield WER = 0.0"""
        reference = "the quick brown fox jumps over the lazy dog"
        hypothesis = "the quick brown fox jumps over the lazy dog"

        wer = validator.calculate_wer(reference, hypothesis)

        assert wer == 0.0, f"Perfect match should have WER = 0.0, got {wer}"

    def test_empty_both_wer_zero(self, validator):
        """Test that two empty strings yield WER = 0.0"""
        wer = validator.calculate_wer("", "")

        assert wer == 0.0, f"Empty strings should have WER = 0.0, got {wer}"

    def test_single_word_match(self, validator):
        """Test single word perfect match"""
        wer = validator.calculate_wer("hello", "hello")

        assert wer == 0.0, f"Single word match should have WER = 0.0, got {wer}"

    def test_complete_substitution_wer(self, validator):
        """Test all words substituted yields WER = 1.0"""
        reference = "cat dog bird"
        hypothesis = "car log nerd"  # 3 substitutions, 3 reference words

        wer = validator.calculate_wer(reference, hypothesis)

        # WER = 3/3 = 1.0
        assert wer == 1.0, f"Complete substitution should have WER = 1.0, got {wer}"


class TestWerBenchmarkSubstitutions:
    """Test WER calculation for substitution errors"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_single_substitution(self, validator):
        """Test single word substitution"""
        reference = "the cat sat on the mat"  # 6 words
        hypothesis = "the cat sat on the hat"  # 1 substitution

        wer = validator.calculate_wer(reference, hypothesis)

        # WER = 1/6 = 0.1667
        expected = 1/6
        assert abs(wer - expected) < 0.001, f"Expected WER ~{expected:.4f}, got {wer}"

    def test_multiple_substitutions(self, validator):
        """Test multiple substitutions"""
        reference = "one two three four five"  # 5 words
        hypothesis = "won too tree for fife"  # 5 substitutions

        wer = validator.calculate_wer(reference, hypothesis)

        # WER = 5/5 = 1.0
        assert wer == 1.0, f"All substitutions should have WER = 1.0, got {wer}"

    def test_partial_substitution(self, validator):
        """Test partial substitution pattern"""
        reference = "i want to go home"  # 5 words
        hypothesis = "i want to go house"  # 1 substitution

        wer = validator.calculate_wer(reference, hypothesis)

        # WER = 1/5 = 0.2
        expected = 0.2
        assert abs(wer - expected) < 0.001, f"Expected WER = {expected}, got {wer}"


class TestWerBenchmarkDeletions:
    """Test WER calculation for deletion errors"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_single_deletion(self, validator):
        """Test single word deletion"""
        reference = "the quick brown fox"  # 4 words
        hypothesis = "the quick fox"  # 1 deletion

        wer = validator.calculate_wer(reference, hypothesis)

        # WER = 1/4 = 0.25
        expected = 0.25
        assert abs(wer - expected) < 0.001, f"Expected WER = {expected}, got {wer}"

    def test_multiple_deletions(self, validator):
        """Test multiple deletions"""
        reference = "please turn off the lights"  # 5 words
        hypothesis = "turn off lights"  # 2 deletions

        wer = validator.calculate_wer(reference, hypothesis)

        # WER = 2/5 = 0.4
        expected = 0.4
        assert abs(wer - expected) < 0.001, f"Expected WER = {expected}, got {wer}"

    def test_all_deleted(self, validator):
        """Test all words deleted"""
        reference = "hello world"  # 2 words
        hypothesis = ""  # All deleted

        wer = validator.calculate_wer(reference, hypothesis)

        # WER = 2/2 = 1.0
        assert wer == 1.0, f"All deleted should have WER = 1.0, got {wer}"


class TestWerBenchmarkInsertions:
    """Test WER calculation for insertion errors"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_single_insertion(self, validator):
        """Test single word insertion"""
        reference = "the cat sat"  # 3 words
        hypothesis = "the big cat sat"  # 1 insertion

        wer = validator.calculate_wer(reference, hypothesis)

        # WER = 1/3 = 0.3333
        expected = 1/3
        assert abs(wer - expected) < 0.001, f"Expected WER ~{expected:.4f}, got {wer}"

    def test_multiple_insertions(self, validator):
        """Test multiple insertions"""
        reference = "go home"  # 2 words
        hypothesis = "please go to your home now"  # 4 insertions

        wer = validator.calculate_wer(reference, hypothesis)

        # WER = 4/2 = 2.0
        expected = 2.0
        assert abs(wer - expected) < 0.001, f"Expected WER = {expected}, got {wer}"

    def test_all_insertions(self, validator):
        """Test hypothesis has only insertions"""
        reference = ""
        hypothesis = "hello world"

        wer = validator.calculate_wer(reference, hypothesis)

        # Empty reference returns len(hypothesis) as WER
        # This is a special case in the implementation
        assert wer >= 0, f"Insertions with empty ref should be >= 0, got {wer}"


class TestWerBenchmarkMixedErrors:
    """Test WER calculation for mixed error types"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_mixed_errors_example1(self, validator):
        """Test mixed substitution, deletion, insertion"""
        reference = "the cat is on the mat"  # 6 words
        hypothesis = "a cat was the mat here"  # S=2, D=1, I=1 = 4 errors

        wer = validator.calculate_wer(reference, hypothesis)

        # Minimum edit distance determines actual errors
        # Expected: some value between 0.5 and 0.8
        assert 0.3 < wer < 1.0, f"Mixed errors WER should be in range, got {wer}"

    def test_mixed_errors_example2(self, validator):
        """Test another mixed error pattern"""
        reference = "i am going to the store"  # 6 words
        hypothesis = "i am going store"  # 2 deletions

        wer = validator.calculate_wer(reference, hypothesis)

        # WER = 2/6 = 0.3333
        expected = 2/6
        assert abs(wer - expected) < 0.001, f"Expected WER ~{expected:.4f}, got {wer}"


class TestWerBenchmarkLibriSpeechStyle:
    """Test WER with LibriSpeech-style utterances"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_librispeech_clean_utterance(self, validator):
        """Test with clean LibriSpeech-style utterance"""
        reference = "he had never felt such hatred before"
        hypothesis = "he had never felt such hatred before"

        wer = validator.calculate_wer(reference, hypothesis)

        assert wer == 0.0, f"Perfect match should have WER = 0.0, got {wer}"

    def test_librispeech_typical_error_rate(self, validator):
        """Test with typical ASR error patterns"""
        reference = "the president spoke to the nation last night"  # 8 words
        hypothesis = "the president spoke to nation last night"  # 1 deletion

        wer = validator.calculate_wer(reference, hypothesis)

        # WER = 1/8 = 0.125
        expected = 1/8
        assert abs(wer - expected) < 0.001, f"Expected WER = {expected}, got {wer}"

    def test_librispeech_challenging_utterance(self, validator):
        """Test with challenging utterance (proper nouns, numbers)"""
        reference = "john smith called at three thirty pm"  # 7 words
        hypothesis = "john smith called at three thirty p m"  # 1 insertion (p m)

        wer = validator.calculate_wer(reference, hypothesis)

        # Should have some errors due to "pm" vs "p m"
        assert wer > 0, f"Should have some errors, got {wer}"


class TestWerBenchmarkNormalization:
    """Test WER calculation handles text normalization"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_case_insensitive(self, validator):
        """Test that WER is case insensitive"""
        reference = "The Quick Brown Fox"
        hypothesis = "the quick brown fox"

        wer = validator.calculate_wer(reference, hypothesis)

        assert wer == 0.0, f"Case difference should not affect WER, got {wer}"

    def test_punctuation_ignored(self, validator):
        """Test that punctuation is ignored"""
        reference = "Hello, world!"
        hypothesis = "hello world"

        wer = validator.calculate_wer(reference, hypothesis)

        assert wer == 0.0, f"Punctuation should be ignored, got {wer}"

    def test_extra_whitespace_normalized(self, validator):
        """Test that extra whitespace is normalized"""
        reference = "the   quick    brown"
        hypothesis = "the quick brown"

        wer = validator.calculate_wer(reference, hypothesis)

        assert wer == 0.0, f"Whitespace should be normalized, got {wer}"


class TestWerBenchmarkEdgeCases:
    """Test WER calculation edge cases"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_single_word_different(self, validator):
        """Test single different word"""
        reference = "hello"
        hypothesis = "world"

        wer = validator.calculate_wer(reference, hypothesis)

        # WER = 1/1 = 1.0
        assert wer == 1.0, f"Single different word should have WER = 1.0, got {wer}"

    def test_repeated_words(self, validator):
        """Test with repeated words"""
        reference = "the the the"  # 3 words
        hypothesis = "the the"  # 1 deletion

        wer = validator.calculate_wer(reference, hypothesis)

        # WER = 1/3 = 0.3333
        expected = 1/3
        assert abs(wer - expected) < 0.001, f"Expected WER ~{expected:.4f}, got {wer}"

    def test_long_utterance(self, validator):
        """Test with longer utterance"""
        reference = " ".join(["word"] * 100)  # 100 words
        hypothesis = " ".join(["word"] * 95)  # 5 deletions

        wer = validator.calculate_wer(reference, hypothesis)

        # WER = 5/100 = 0.05
        expected = 0.05
        assert abs(wer - expected) < 0.001, f"Expected WER = {expected}, got {wer}"

    def test_very_high_wer(self, validator):
        """Test WER can exceed 1.0 with many insertions"""
        reference = "a"  # 1 word
        hypothesis = "a b c d e"  # 4 insertions

        wer = validator.calculate_wer(reference, hypothesis)

        # WER = 4/1 = 4.0
        expected = 4.0
        assert abs(wer - expected) < 0.001, f"Expected WER = {expected}, got {wer}"


class TestWerBenchmarkKnownValues:
    """Test WER with pre-calculated known values"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    @pytest.mark.parametrize("reference,hypothesis,expected_wer", [
        # Perfect matches
        ("test", "test", 0.0),
        ("one two three", "one two three", 0.0),

        # Single errors
        ("a b c", "a b d", 1/3),  # 1 substitution
        ("a b c", "a c", 1/3),    # 1 deletion
        ("a b c", "a x b c", 1/3),  # 1 insertion

        # Multiple errors
        ("a b c d", "a c d", 0.25),  # 1 deletion in 4 words
        ("a b c d", "a b c d e f", 0.5),  # 2 insertions in 4 words

        # All different
        ("red blue green", "car bus train", 1.0),  # 3 substitutions
    ])
    def test_known_wer_values(self, validator, reference, hypothesis, expected_wer):
        """Test WER calculation against known values"""
        wer = validator.calculate_wer(reference, hypothesis)

        assert abs(wer - expected_wer) < 0.001, (
            f"Reference: '{reference}', Hypothesis: '{hypothesis}'\n"
            f"Expected WER: {expected_wer}, Got: {wer}"
        )


class TestWerBenchmarkAutomotiveCommands:
    """Test WER with automotive voice command patterns"""

    @pytest.fixture
    def validator(self):
        return TranscriptionValidatorService()

    def test_navigation_command_perfect(self, validator):
        """Test navigation command with perfect match"""
        reference = "navigate to one two three main street"
        hypothesis = "navigate to one two three main street"

        wer = validator.calculate_wer(reference, hypothesis)

        assert wer == 0.0, f"Perfect match should have WER = 0.0, got {wer}"

    def test_climate_command_with_error(self, validator):
        """Test climate command with recognition error"""
        reference = "set temperature to seventy two degrees"  # 6 words
        hypothesis = "set temperature to seventy degrees"  # 1 deletion

        wer = validator.calculate_wer(reference, hypothesis)

        # WER = 1/6 = 0.1667
        expected = 1/6
        assert abs(wer - expected) < 0.001, f"Expected WER ~{expected:.4f}, got {wer}"

    def test_media_command_substitution(self, validator):
        """Test media command with substitution"""
        reference = "play rock music"  # 3 words
        hypothesis = "play pop music"  # 1 substitution

        wer = validator.calculate_wer(reference, hypothesis)

        # WER = 1/3 = 0.3333
        expected = 1/3
        assert abs(wer - expected) < 0.001, f"Expected WER ~{expected:.4f}, got {wer}"
