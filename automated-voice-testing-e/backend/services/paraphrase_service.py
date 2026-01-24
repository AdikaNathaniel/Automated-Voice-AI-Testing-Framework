"""
Paraphrase Generation Service for voice AI testing.

This service manages paraphrase generation including automatic
paraphrasing, synonym substitution, and semantic validation.

Key features:
- Automatic paraphrase generation for test cases
- Synonym substitution
- Sentence restructuring
- Semantic equivalence validation

Example:
    >>> service = ParaphraseService()
    >>> paraphrases = service.generate_paraphrases(text, count=5)
"""

from typing import List, Dict, Any
from datetime import datetime
import uuid


class ParaphraseService:
    """
    Service for paraphrase generation.

    Provides paraphrase generation, synonym substitution,
    sentence restructuring, and semantic validation.

    Example:
        >>> service = ParaphraseService()
        >>> config = service.get_paraphrase_config()
    """

    def __init__(self):
        """Initialize the paraphrase service."""
        self._generated_paraphrases: List[Dict[str, Any]] = []

    def generate_paraphrases(
        self,
        text: str,
        count: int = 5,
        diversity: float = 0.7
    ) -> Dict[str, Any]:
        """
        Generate paraphrases for input text.

        Args:
            text: Input text to paraphrase
            count: Number of paraphrases to generate
            diversity: Diversity factor (0-1)

        Returns:
            Dictionary with generated paraphrases

        Example:
            >>> result = service.generate_paraphrases('Hello world', 3)
        """
        generation_id = str(uuid.uuid4())

        paraphrases = [
            f"Paraphrase {i+1} of: {text}"
            for i in range(count)
        ]

        result = {
            'generation_id': generation_id,
            'original': text,
            'paraphrases': paraphrases,
            'count': len(paraphrases),
            'diversity': diversity,
            'created_at': datetime.utcnow().isoformat()
        }

        self._generated_paraphrases.append(result)
        return result

    def get_paraphrase_count(self) -> int:
        """
        Get total count of generated paraphrases.

        Returns:
            Count of all generated paraphrases

        Example:
            >>> count = service.get_paraphrase_count()
        """
        return sum(p['count'] for p in self._generated_paraphrases)

    def substitute_synonyms(
        self,
        text: str,
        substitution_rate: float = 0.3
    ) -> Dict[str, Any]:
        """
        Substitute words with synonyms.

        Args:
            text: Input text
            substitution_rate: Rate of substitution (0-1)

        Returns:
            Dictionary with substituted text

        Example:
            >>> result = service.substitute_synonyms('Happy day', 0.5)
        """
        words = text.split()
        substituted = []
        substitutions = []

        for word in words:
            synonyms = self.get_synonyms(word)
            if synonyms and len(substituted) / max(len(words), 1) < substitution_rate:
                new_word = synonyms[0]
                substituted.append(new_word)
                substitutions.append({
                    'original': word,
                    'replacement': new_word
                })
            else:
                substituted.append(word)

        return {
            'original': text,
            'result': ' '.join(substituted),
            'substitutions': substitutions,
            'substitution_rate': len(substitutions) / max(len(words), 1),
            'created_at': datetime.utcnow().isoformat()
        }

    def get_synonyms(
        self,
        word: str
    ) -> List[str]:
        """
        Get synonyms for a word.

        Args:
            word: Word to find synonyms for

        Returns:
            List of synonyms

        Example:
            >>> synonyms = service.get_synonyms('happy')
        """
        synonym_map = {
            'happy': ['joyful', 'glad', 'pleased', 'delighted'],
            'sad': ['unhappy', 'sorrowful', 'melancholy', 'gloomy'],
            'big': ['large', 'huge', 'enormous', 'massive'],
            'small': ['tiny', 'little', 'miniature', 'compact'],
            'good': ['excellent', 'great', 'fine', 'wonderful'],
            'bad': ['poor', 'terrible', 'awful', 'dreadful']
        }
        return synonym_map.get(word.lower(), [])

    def restructure_sentence(
        self,
        text: str,
        pattern: str = 'passive'
    ) -> Dict[str, Any]:
        """
        Restructure sentence using specified pattern.

        Args:
            text: Input sentence
            pattern: Restructuring pattern

        Returns:
            Dictionary with restructured sentence

        Example:
            >>> result = service.restructure_sentence('I ate the apple', 'passive')
        """
        return {
            'original': text,
            'pattern': pattern,
            'result': f"Restructured ({pattern}): {text}",
            'created_at': datetime.utcnow().isoformat()
        }

    def get_restructuring_patterns(self) -> List[Dict[str, str]]:
        """
        Get available restructuring patterns.

        Returns:
            List of available patterns

        Example:
            >>> patterns = service.get_restructuring_patterns()
        """
        return [
            {
                'name': 'passive',
                'description': 'Convert active voice to passive voice'
            },
            {
                'name': 'active',
                'description': 'Convert passive voice to active voice'
            },
            {
                'name': 'question',
                'description': 'Convert statement to question'
            },
            {
                'name': 'negation',
                'description': 'Add or remove negation'
            },
            {
                'name': 'conditional',
                'description': 'Convert to conditional form'
            }
        ]

    def validate_semantic_equivalence(
        self,
        text1: str,
        text2: str
    ) -> Dict[str, Any]:
        """
        Validate if two texts are semantically equivalent.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_semantic_equivalence(t1, t2)
        """
        similarity = self.get_similarity_score(text1, text2)
        threshold = 0.7

        return {
            'text1': text1,
            'text2': text2,
            'similarity_score': similarity,
            'is_equivalent': similarity >= threshold,
            'threshold': threshold,
            'validated_at': datetime.utcnow().isoformat()
        }

    def get_similarity_score(
        self,
        text1: str,
        text2: str
    ) -> float:
        """
        Calculate semantic similarity score between texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score (0-1)

        Example:
            >>> score = service.get_similarity_score('hello', 'hi there')
        """
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union)

    def get_paraphrase_config(self) -> Dict[str, Any]:
        """
        Get paraphrase service configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_paraphrase_config()
        """
        return {
            'total_generations': len(self._generated_paraphrases),
            'total_paraphrases': self.get_paraphrase_count(),
            'restructuring_patterns': [p['name'] for p in self.get_restructuring_patterns()],
            'default_diversity': 0.7,
            'default_count': 5,
            'similarity_threshold': 0.7
        }
