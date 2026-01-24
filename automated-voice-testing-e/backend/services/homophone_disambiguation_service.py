"""
Homophone Disambiguation Service for ASR analysis.

This service provides methods for analyzing homophone usage in ASR
transcriptions. Homophones are words that sound the same but have
different spellings and meanings (e.g., their/there/they're).

ASR systems must use context to select the correct spelling, making
homophone accuracy an important quality metric.

Common homophone sets:
- their/there/they're
- to/too/two
- your/you're
- its/it's
- by/buy/bye
- hear/here

Example:
    >>> service = HomophoneDisambiguationService()
    >>> homophones = service.detect_homophones("They're going there")
    >>> print(homophones)
    [{'word': "They're", 'set': ['their', 'there', "they're"]},
     {'word': 'there', 'set': ['their', 'there', "they're"]}]
"""

from typing import List, Dict, Set, Any, Optional


class HomophoneDisambiguationService:
    """
    Service for homophone disambiguation analysis.

    Provides methods for detecting homophones, calculating accuracy,
    and analyzing context-dependent transcription choices.

    Attributes:
        homophone_sets: Dictionary mapping words to their homophone groups
        custom_sets: User-defined homophone sets

    Example:
        >>> service = HomophoneDisambiguationService()
        >>> metrics = service.get_homophone_metrics(
        ...     "They're going there",
        ...     "Their going their"
        ... )
        >>> print(f"Accuracy: {metrics['accuracy']:.2f}")
    """

    # Default homophone sets
    DEFAULT_SETS = [
        {'their', 'there', "they're"},
        {'to', 'too', 'two'},
        {'your', "you're"},
        {'its', "it's"},
        {'by', 'buy', 'bye'},
        {'hear', 'here'},
        {'know', 'no'},
        {'write', 'right', 'rite'},
        {'way', 'weigh'},
        {'peace', 'piece'},
        {'week', 'weak'},
        {'break', 'brake'},
        {'whether', 'weather'},
        {'principal', 'principle'},
        {'affect', 'effect'},
    ]

    def __init__(self):
        """Initialize the homophone disambiguation service."""
        self.homophone_sets: List[Set[str]] = [
            set(s) for s in self.DEFAULT_SETS
        ]
        self._build_word_to_set_map()

    def _build_word_to_set_map(self) -> None:
        """Build mapping from words to their homophone sets."""
        self._word_to_set: Dict[str, Set[str]] = {}
        for homophone_set in self.homophone_sets:
            for word in homophone_set:
                self._word_to_set[word.lower()] = homophone_set

    def add_homophone_set(self, words: Set[str]) -> None:
        """
        Add a custom homophone set.

        Args:
            words: Set of homophones

        Example:
            >>> service.add_homophone_set({'reign', 'rain', 'rein'})
        """
        normalized = {w.lower() for w in words}
        self.homophone_sets.append(normalized)
        self._build_word_to_set_map()

    def get_homophone_sets(self) -> List[Set[str]]:
        """
        Get all homophone sets.

        Returns:
            List of homophone sets

        Example:
            >>> sets = service.get_homophone_sets()
            >>> print(len(sets))
        """
        return [set(s) for s in self.homophone_sets]

    def get_homophone_group(self, word: str) -> Optional[Set[str]]:
        """
        Get the homophone group for a word.

        Args:
            word: Word to look up

        Returns:
            Set of homophones or None if not a homophone

        Example:
            >>> group = service.get_homophone_group('their')
            >>> print(group)
            {'their', 'there', "they're"}
        """
        return self._word_to_set.get(word.lower())

    def detect_homophones(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect homophones in text.

        Args:
            text: Input text to analyze

        Returns:
            List of dictionaries with 'word', 'position', and 'set'

        Example:
            >>> homophones = service.detect_homophones("They're there")
            >>> print(len(homophones))
            2
        """
        if not text:
            return []

        homophones = []
        words = text.split()

        for i, word in enumerate(words):
            # Clean word of punctuation
            clean_word = ''.join(c for c in word if c.isalnum() or c == "'")
            if not clean_word:
                continue

            group = self.get_homophone_group(clean_word)
            if group:
                homophones.append({
                    'word': clean_word,
                    'position': i,
                    'set': group
                })

        return homophones

    def analyze_context(
        self,
        text: str,
        word_position: int,
        window_size: int = 3
    ) -> Dict[str, Any]:
        """
        Analyze context around a word for disambiguation.

        Args:
            text: Full text
            word_position: Position of word to analyze
            window_size: Number of words before/after to include

        Returns:
            Dictionary with context words and analysis

        Example:
            >>> context = service.analyze_context("They're going home", 0)
            >>> print(context['after'])
            ['going', 'home']
        """
        words = text.split()

        if word_position < 0 or word_position >= len(words):
            return {
                'before': [],
                'after': [],
                'word': ''
            }

        before_start = max(0, word_position - window_size)
        after_end = min(len(words), word_position + window_size + 1)

        return {
            'before': words[before_start:word_position],
            'after': words[word_position + 1:after_end],
            'word': words[word_position]
        }

    def calculate_homophone_accuracy(
        self,
        reference: str,
        hypothesis: str
    ) -> Dict[str, Any]:
        """
        Calculate homophone-specific accuracy.

        Compares homophones in reference and hypothesis to determine
        if the correct form was chosen.

        Args:
            reference: Reference transcription
            hypothesis: Hypothesis transcription

        Returns:
            Dictionary with accuracy metrics

        Example:
            >>> metrics = service.calculate_homophone_accuracy(
            ...     "They're going there",
            ...     "Their going their"
            ... )
            >>> print(f"Accuracy: {metrics['accuracy']:.2f}")
        """
        if not reference or not hypothesis:
            return {
                'accuracy': 1.0 if not reference and not hypothesis else 0.0,
                'total': 0,
                'correct': 0,
                'incorrect': 0
            }

        ref_words = reference.lower().split()
        hyp_words = hypothesis.lower().split()

        total = 0
        correct = 0

        # Compare word by word
        for i, ref_word in enumerate(ref_words):
            # Clean word
            ref_clean = ''.join(c for c in ref_word if c.isalnum() or c == "'")
            if not ref_clean:
                continue

            # Check if it's a homophone
            group = self.get_homophone_group(ref_clean)
            if not group:
                continue

            total += 1

            # Get corresponding hypothesis word
            if i < len(hyp_words):
                hyp_clean = ''.join(
                    c for c in hyp_words[i] if c.isalnum() or c == "'"
                )
                if hyp_clean.lower() == ref_clean.lower():
                    correct += 1

        accuracy = correct / total if total > 0 else 1.0

        return {
            'accuracy': accuracy,
            'total': total,
            'correct': correct,
            'incorrect': total - correct
        }

    def get_accuracy_by_set(
        self,
        reference: str,
        hypothesis: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate accuracy breakdown by homophone set.

        Args:
            reference: Reference transcription
            hypothesis: Hypothesis transcription

        Returns:
            Dictionary mapping set ID to accuracy metrics

        Example:
            >>> by_set = service.get_accuracy_by_set(
            ...     "They're going there and you're happy",
            ...     "Their going their and your happy"
            ... )
        """
        results: Dict[str, Dict[str, Any]] = {}

        ref_words = reference.lower().split()
        hyp_words = hypothesis.lower().split()

        for i, ref_word in enumerate(ref_words):
            ref_clean = ''.join(c for c in ref_word if c.isalnum() or c == "'")
            if not ref_clean:
                continue

            group = self.get_homophone_group(ref_clean)
            if not group:
                continue

            # Create set identifier
            set_id = '/'.join(sorted(group))

            if set_id not in results:
                results[set_id] = {
                    'total': 0,
                    'correct': 0,
                    'accuracy': 0.0
                }

            results[set_id]['total'] += 1

            if i < len(hyp_words):
                hyp_clean = ''.join(
                    c for c in hyp_words[i] if c.isalnum() or c == "'"
                )
                if hyp_clean.lower() == ref_clean.lower():
                    results[set_id]['correct'] += 1

        # Calculate accuracies
        for set_id in results:
            total = results[set_id]['total']
            correct = results[set_id]['correct']
            results[set_id]['accuracy'] = correct / total if total > 0 else 0.0

        return results

    def get_homophone_metrics(
        self,
        reference: str,
        hypothesis: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive homophone metrics.

        Args:
            reference: Reference transcription
            hypothesis: Hypothesis transcription

        Returns:
            Dictionary with overall metrics and breakdown by set

        Example:
            >>> metrics = service.get_homophone_metrics(
            ...     "They're going there",
            ...     "Their going their"
            ... )
            >>> print(f"Overall accuracy: {metrics['accuracy']:.2f}")
        """
        overall = self.calculate_homophone_accuracy(reference, hypothesis)
        by_set = self.get_accuracy_by_set(reference, hypothesis)

        ref_homophones = self.detect_homophones(reference)
        hyp_homophones = self.detect_homophones(hypothesis)

        return {
            'accuracy': overall['accuracy'],
            'total_homophones': overall['total'],
            'correct': overall['correct'],
            'incorrect': overall['incorrect'],
            'by_set': by_set,
            'reference_homophones': ref_homophones,
            'hypothesis_homophones': hyp_homophones
        }
