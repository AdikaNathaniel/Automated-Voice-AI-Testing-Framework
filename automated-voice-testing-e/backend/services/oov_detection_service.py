"""
Out-of-Vocabulary (OOV) Detection Service for ASR analysis.

This service provides methods for detecting and analyzing words that are not
in the ASR system's vocabulary. OOV words often cause recognition errors and
tracking them helps identify areas for vocabulary expansion.

Key features:
- OOV word detection: Identify words not in vocabulary
- OOV rate calculation: Percentage of unknown words
- Custom lexicon support: Domain-specific word lists
- Frequency analysis: Track most common OOV words

Example:
    >>> service = OOVDetectionService()
    >>> service.load_vocabulary({'the', 'a', 'cat', 'dog'})
    >>> oov_words = service.detect_oov_words('the elephant jumped')
    >>> print(oov_words)
    ['elephant', 'jumped']
"""

from typing import List, Dict, Set, Any, Optional
import re
from collections import Counter


class OOVDetectionService:
    """
    Service for detecting and analyzing out-of-vocabulary words.

    Provides methods for OOV detection, rate calculation, and vocabulary
    management with support for custom lexicons and domain tracking.

    Attributes:
        vocabulary: Set of known words
        custom_lexicons: Domain-specific word sets
        domain_stats: OOV statistics per domain

    Example:
        >>> service = OOVDetectionService()
        >>> service.load_vocabulary({'hello', 'world'})
        >>> analysis = service.get_oov_analysis('hello universe')
        >>> print(analysis['oov_rate'])
    """

    def __init__(self):
        """Initialize the OOV detection service."""
        self.vocabulary: Set[str] = set()
        self.custom_lexicons: Dict[str, Set[str]] = {}
        self.domain_stats: Dict[str, Dict[str, Any]] = {}

    def normalize_text(self, text: str) -> str:
        """
        Normalize text for OOV detection.

        Converts to lowercase and removes punctuation.

        Args:
            text: Input text to normalize

        Returns:
            Normalized text string

        Example:
            >>> service.normalize_text("Hello, World!")
            'hello world'
        """
        # Convert to lowercase
        text = text.lower()
        # Remove punctuation but keep spaces
        text = re.sub(r'[^\w\s]', '', text)
        return text

    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.

        Args:
            text: Input text to tokenize

        Returns:
            List of word tokens

        Example:
            >>> service.tokenize("hello world")
            ['hello', 'world']
        """
        normalized = self.normalize_text(text)
        return normalized.split()

    def load_vocabulary(self, words: Set[str]) -> None:
        """
        Load vocabulary from a set of words.

        Args:
            words: Set of vocabulary words

        Example:
            >>> service.load_vocabulary({'the', 'a', 'is', 'are'})
        """
        self.vocabulary = {w.lower() for w in words}

    def add_to_vocabulary(self, words: List[str]) -> None:
        """
        Add words to the existing vocabulary.

        Args:
            words: List of words to add

        Example:
            >>> service.add_to_vocabulary(['new', 'words'])
        """
        for word in words:
            self.vocabulary.add(word.lower())

    def get_vocabulary(self) -> Set[str]:
        """
        Get the current vocabulary.

        Returns:
            Set of vocabulary words

        Example:
            >>> vocab = service.get_vocabulary()
            >>> len(vocab)
        """
        return self.vocabulary.copy()

    def load_custom_lexicon(
        self,
        words: Set[str],
        domain: str
    ) -> None:
        """
        Load a custom lexicon for a specific domain.

        Args:
            words: Set of domain-specific words
            domain: Domain name (e.g., 'medical', 'legal')

        Example:
            >>> service.load_custom_lexicon(
            ...     {'aspirin', 'ibuprofen'},
            ...     domain='medical'
            ... )
        """
        self.custom_lexicons[domain] = {w.lower() for w in words}

    def merge_lexicons(
        self,
        domains: Optional[List[str]] = None
    ) -> Set[str]:
        """
        Merge vocabulary with custom lexicons.

        Args:
            domains: List of domains to merge (None = all)

        Returns:
            Combined set of all words

        Example:
            >>> combined = service.merge_lexicons(['medical'])
        """
        combined = self.vocabulary.copy()

        if domains is None:
            domains = list(self.custom_lexicons.keys())

        for domain in domains:
            if domain in self.custom_lexicons:
                combined.update(self.custom_lexicons[domain])

        return combined

    def detect_oov_words(
        self,
        text: str,
        vocabulary: Optional[Set[str]] = None,
        domains: Optional[List[str]] = None
    ) -> List[str]:
        """
        Detect out-of-vocabulary words in text.

        Args:
            text: Input text to analyze
            vocabulary: Custom vocabulary (uses default if None)
            domains: Custom lexicon domains to include

        Returns:
            List of OOV words found in text

        Example:
            >>> service.load_vocabulary({'the', 'cat'})
            >>> oov = service.detect_oov_words('the elephant jumped')
            >>> print(oov)
            ['elephant', 'jumped']
        """
        words = self.tokenize(text)

        if vocabulary is None:
            vocabulary = self.merge_lexicons(domains)

        oov_words = []
        for word in words:
            if word and word not in vocabulary:
                oov_words.append(word)

        return oov_words

    def calculate_oov_rate(
        self,
        text: str,
        vocabulary: Optional[Set[str]] = None,
        domains: Optional[List[str]] = None
    ) -> float:
        """
        Calculate the OOV rate for text.

        OOV rate = number of OOV words / total words

        Args:
            text: Input text to analyze
            vocabulary: Custom vocabulary (uses default if None)
            domains: Custom lexicon domains to include

        Returns:
            OOV rate between 0.0 and 1.0

        Example:
            >>> service.load_vocabulary({'the', 'cat'})
            >>> rate = service.calculate_oov_rate('the elephant jumped')
            >>> print(f"OOV rate: {rate:.2f}")
            OOV rate: 0.67
        """
        words = self.tokenize(text)

        if not words:
            return 0.0

        oov_words = self.detect_oov_words(text, vocabulary, domains)
        return len(oov_words) / len(words)

    def track_oov_by_domain(
        self,
        text: str,
        domain: str,
        vocabulary: Optional[Set[str]] = None
    ) -> None:
        """
        Track OOV statistics for a specific domain.

        Args:
            text: Input text to analyze
            domain: Domain name for tracking
            vocabulary: Custom vocabulary (uses default if None)

        Example:
            >>> service.track_oov_by_domain('medical text', 'healthcare')
        """
        oov_words = self.detect_oov_words(text, vocabulary)
        self.calculate_oov_rate(text, vocabulary)

        if domain not in self.domain_stats:
            self.domain_stats[domain] = {
                'total_samples': 0,
                'total_oov_words': 0,
                'total_words': 0,
                'oov_word_freq': Counter()
            }

        stats = self.domain_stats[domain]
        words = self.tokenize(text)

        stats['total_samples'] += 1
        stats['total_oov_words'] += len(oov_words)
        stats['total_words'] += len(words)
        stats['oov_word_freq'].update(oov_words)

    def get_domain_oov_stats(
        self,
        domain: str
    ) -> Dict[str, Any]:
        """
        Get OOV statistics for a domain.

        Args:
            domain: Domain name

        Returns:
            Dictionary with OOV statistics for the domain

        Example:
            >>> stats = service.get_domain_oov_stats('healthcare')
            >>> print(f"OOV rate: {stats['avg_oov_rate']:.2f}")
        """
        if domain not in self.domain_stats:
            return {
                'domain': domain,
                'total_samples': 0,
                'avg_oov_rate': 0.0,
                'top_oov_words': []
            }

        stats = self.domain_stats[domain]
        avg_rate = (
            stats['total_oov_words'] / stats['total_words']
            if stats['total_words'] > 0
            else 0.0
        )

        return {
            'domain': domain,
            'total_samples': stats['total_samples'],
            'total_oov_words': stats['total_oov_words'],
            'total_words': stats['total_words'],
            'avg_oov_rate': avg_rate,
            'top_oov_words': stats['oov_word_freq'].most_common(10)
        }

    def get_oov_frequency(
        self,
        texts: List[str],
        vocabulary: Optional[Set[str]] = None
    ) -> Dict[str, int]:
        """
        Get frequency distribution of OOV words.

        Args:
            texts: List of texts to analyze
            vocabulary: Custom vocabulary (uses default if None)

        Returns:
            Dictionary mapping OOV words to their frequencies

        Example:
            >>> texts = ['the elephant', 'an elephant ran']
            >>> freq = service.get_oov_frequency(texts)
            >>> print(freq)
            {'elephant': 2, 'ran': 1}
        """
        freq: Counter = Counter()

        for text in texts:
            oov_words = self.detect_oov_words(text, vocabulary)
            freq.update(oov_words)

        return dict(freq)

    def get_oov_analysis(
        self,
        text: str,
        vocabulary: Optional[Set[str]] = None,
        domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive OOV analysis for text.

        Args:
            text: Input text to analyze
            vocabulary: Custom vocabulary (uses default if None)
            domains: Custom lexicon domains to include

        Returns:
            Dictionary with:
                - oov_words: List of OOV words
                - oov_rate: Percentage of OOV words
                - total_words: Total word count
                - oov_count: Number of OOV words
                - unique_oov: Number of unique OOV words

        Example:
            >>> analysis = service.get_oov_analysis('the elephant ran')
            >>> print(f"OOV rate: {analysis['oov_rate']:.2%}")
        """
        words = self.tokenize(text)
        oov_words = self.detect_oov_words(text, vocabulary, domains)
        oov_rate = len(oov_words) / len(words) if words else 0.0

        return {
            'oov_words': oov_words,
            'oov_rate': oov_rate,
            'total_words': len(words),
            'oov_count': len(oov_words),
            'unique_oov': len(set(oov_words))
        }
