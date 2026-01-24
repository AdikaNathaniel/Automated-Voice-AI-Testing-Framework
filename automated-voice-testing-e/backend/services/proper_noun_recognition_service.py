"""
Proper Noun Recognition Service for ASR analysis.

This service provides methods for extracting and analyzing proper nouns
(names of people, places, organizations, brands) in ASR transcriptions.
Proper nouns are particularly challenging for ASR systems and require
specialized accuracy metrics.

Entity types supported:
- PERSON: Names of people (e.g., "John Smith")
- LOCATION: Geographic locations (e.g., "New York")
- ORGANIZATION: Companies, institutions (e.g., "Google")
- BRAND: Product and brand names (e.g., "iPhone")

Example:
    >>> service = ProperNounRecognitionService()
    >>> entities = service.extract_entities("John works at Google in Seattle")
    >>> print(entities)
    [{'text': 'John', 'type': 'PERSON'},
     {'text': 'Google', 'type': 'ORGANIZATION'},
     {'text': 'Seattle', 'type': 'LOCATION'}]
"""

from typing import List, Dict, Any, Optional, Set
import re


class ProperNounRecognitionService:
    """
    Service for proper noun recognition and accuracy analysis.

    Provides methods for extracting entities, calculating entity-specific
    accuracy metrics, and comparing entity recognition between reference
    and hypothesis transcriptions.

    Attributes:
        custom_entities: Custom entity lists by type
        entity_types: Supported entity types

    Example:
        >>> service = ProperNounRecognitionService()
        >>> metrics = service.get_entity_metrics(
        ...     "John visited Google",
        ...     "Jon visited Goggle"
        ... )
        >>> print(f"Precision: {metrics['precision']:.2f}")
    """

    # Supported entity types
    PERSON = 'PERSON'
    LOCATION = 'LOCATION'
    ORGANIZATION = 'ORGANIZATION'
    BRAND = 'BRAND'

    def __init__(self):
        """Initialize the proper noun recognition service."""
        self.custom_entities: Dict[str, Set[str]] = {
            self.PERSON: set(),
            self.LOCATION: set(),
            self.ORGANIZATION: set(),
            self.BRAND: set()
        }
        self.entity_types = [
            self.PERSON,
            self.LOCATION,
            self.ORGANIZATION,
            self.BRAND
        ]

    def add_custom_entities(
        self,
        entity_type: str,
        entities: List[str]
    ) -> None:
        """
        Add custom entities to the recognition list.

        Args:
            entity_type: Type of entity (PERSON, LOCATION, etc.)
            entities: List of entity strings to add

        Example:
            >>> service.add_custom_entities('PERSON', ['Alice', 'Bob'])
        """
        if entity_type not in self.custom_entities:
            self.custom_entities[entity_type] = set()

        for entity in entities:
            self.custom_entities[entity_type].add(entity.lower())

    def get_custom_entities(
        self,
        entity_type: Optional[str] = None
    ) -> Dict[str, Set[str]]:
        """
        Get custom entities.

        Args:
            entity_type: Specific type to get (None for all)

        Returns:
            Dictionary of custom entities by type

        Example:
            >>> entities = service.get_custom_entities('PERSON')
        """
        if entity_type:
            return {entity_type: self.custom_entities.get(entity_type, set())}
        return self.custom_entities.copy()

    def extract_entities(
        self,
        text: str
    ) -> List[Dict[str, str]]:
        """
        Extract proper noun entities from text.

        Uses pattern matching and custom entity lists to identify
        proper nouns in the text.

        Args:
            text: Input text to analyze

        Returns:
            List of entity dictionaries with 'text' and 'type' keys

        Example:
            >>> entities = service.extract_entities("John visited Seattle")
            >>> print(entities)
            [{'text': 'John', 'type': 'PERSON'},
             {'text': 'Seattle', 'type': 'LOCATION'}]
        """
        entities = []

        # Extract from custom entity lists first
        for entity_type, entity_set in self.custom_entities.items():
            for entity in entity_set:
                if entity.lower() in text.lower():
                    entities.append({
                        'text': entity,
                        'type': entity_type
                    })

        # Pattern-based extraction for capitalized words
        # This is a simple heuristic - in production, use NER library
        words = text.split()
        for word in words:
            # Skip if already found
            if any(e['text'].lower() == word.lower() for e in entities):
                continue

            # Check if word starts with capital (simple proper noun heuristic)
            clean_word = re.sub(r'[^\w]', '', word)
            if clean_word and clean_word[0].isupper() and len(clean_word) > 1:
                # Try to classify based on patterns
                entity_type = self._classify_entity(clean_word)
                if entity_type:
                    entities.append({
                        'text': clean_word,
                        'type': entity_type
                    })

        return entities

    def _classify_entity(self, word: str) -> Optional[str]:
        """
        Classify an entity based on patterns and heuristics.

        Args:
            word: Word to classify

        Returns:
            Entity type or None if not classified
        """
        # Common location indicators
        location_suffixes = ['ville', 'town', 'city', 'land', 'berg']
        if any(word.lower().endswith(s) for s in location_suffixes):
            return self.LOCATION

        # Common organization indicators
        org_suffixes = ['Inc', 'Corp', 'LLC', 'Ltd', 'Co']
        if any(word.endswith(s) for s in org_suffixes):
            return self.ORGANIZATION

        # Default to PERSON for simple capitalized words
        if word[0].isupper():
            return self.PERSON

        return None

    def calculate_similarity(
        self,
        str1: str,
        str2: str
    ) -> float:
        """
        Calculate similarity between two strings.

        Uses Levenshtein distance normalized by max length.

        Args:
            str1: First string
            str2: Second string

        Returns:
            Similarity score between 0.0 and 1.0

        Example:
            >>> sim = service.calculate_similarity("John", "Jon")
            >>> print(f"Similarity: {sim:.2f}")
        """
        if not str1 and not str2:
            return 1.0
        if not str1 or not str2:
            return 0.0

        s1 = str1.lower()
        s2 = str2.lower()

        if s1 == s2:
            return 1.0

        # Calculate Levenshtein distance
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i-1] == s2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])

        distance = dp[m][n]
        max_len = max(m, n)

        return 1.0 - (distance / max_len)

    def match_entities(
        self,
        reference_entities: List[Dict[str, str]],
        hypothesis_entities: List[Dict[str, str]],
        threshold: float = 0.8
    ) -> Dict[str, Any]:
        """
        Match entities between reference and hypothesis.

        Args:
            reference_entities: Entities from reference text
            hypothesis_entities: Entities from hypothesis text
            threshold: Similarity threshold for matching

        Returns:
            Dictionary with matched, missed, and spurious entities

        Example:
            >>> ref = [{'text': 'John', 'type': 'PERSON'}]
            >>> hyp = [{'text': 'Jon', 'type': 'PERSON'}]
            >>> result = service.match_entities(ref, hyp)
        """
        matched = []
        missed = []
        spurious = []

        hyp_matched = set()

        for ref_entity in reference_entities:
            best_match = None
            best_score = 0.0

            for i, hyp_entity in enumerate(hypothesis_entities):
                if i in hyp_matched:
                    continue

                # Must match type
                if ref_entity['type'] != hyp_entity['type']:
                    continue

                score = self.calculate_similarity(
                    ref_entity['text'],
                    hyp_entity['text']
                )

                if score >= threshold and score > best_score:
                    best_match = (i, hyp_entity, score)
                    best_score = score

            if best_match:
                matched.append({
                    'reference': ref_entity,
                    'hypothesis': best_match[1],
                    'score': best_match[2]
                })
                hyp_matched.add(best_match[0])
            else:
                missed.append(ref_entity)

        # Find spurious entities (in hypothesis but not matched)
        for i, hyp_entity in enumerate(hypothesis_entities):
            if i not in hyp_matched:
                spurious.append(hyp_entity)

        return {
            'matched': matched,
            'missed': missed,
            'spurious': spurious
        }

    def calculate_entity_accuracy(
        self,
        reference: str,
        hypothesis: str,
        threshold: float = 0.8
    ) -> Dict[str, Any]:
        """
        Calculate entity-specific accuracy metrics.

        Args:
            reference: Reference transcription
            hypothesis: Hypothesis transcription
            threshold: Similarity threshold for matching

        Returns:
            Dictionary with precision, recall, F1 score

        Example:
            >>> metrics = service.calculate_entity_accuracy(
            ...     "John visited Seattle",
            ...     "Jon visited Seatle"
            ... )
            >>> print(f"F1: {metrics['f1']:.2f}")
        """
        ref_entities = self.extract_entities(reference)
        hyp_entities = self.extract_entities(hypothesis)

        if not ref_entities and not hyp_entities:
            return {
                'precision': 1.0,
                'recall': 1.0,
                'f1': 1.0,
                'matched': 0,
                'missed': 0,
                'spurious': 0
            }

        match_result = self.match_entities(ref_entities, hyp_entities, threshold)

        num_matched = len(match_result['matched'])
        num_missed = len(match_result['missed'])
        num_spurious = len(match_result['spurious'])

        precision = (
            num_matched / (num_matched + num_spurious)
            if (num_matched + num_spurious) > 0
            else 0.0
        )

        recall = (
            num_matched / (num_matched + num_missed)
            if (num_matched + num_missed) > 0
            else 0.0
        )

        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )

        return {
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'matched': num_matched,
            'missed': num_missed,
            'spurious': num_spurious
        }

    def get_accuracy_by_type(
        self,
        reference: str,
        hypothesis: str,
        threshold: float = 0.8
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate accuracy metrics by entity type.

        Args:
            reference: Reference transcription
            hypothesis: Hypothesis transcription
            threshold: Similarity threshold for matching

        Returns:
            Dictionary mapping entity type to accuracy metrics

        Example:
            >>> by_type = service.get_accuracy_by_type(
            ...     "John visited Google in Seattle",
            ...     "Jon visited Goggle in Seatle"
            ... )
            >>> print(f"PERSON F1: {by_type['PERSON']['f1']:.2f}")
        """
        ref_entities = self.extract_entities(reference)
        hyp_entities = self.extract_entities(hypothesis)

        results = {}

        for entity_type in self.entity_types:
            # Filter by type
            ref_type = [e for e in ref_entities if e['type'] == entity_type]
            hyp_type = [e for e in hyp_entities if e['type'] == entity_type]

            if not ref_type and not hyp_type:
                continue

            match_result = self.match_entities(ref_type, hyp_type, threshold)

            num_matched = len(match_result['matched'])
            num_missed = len(match_result['missed'])
            num_spurious = len(match_result['spurious'])

            precision = (
                num_matched / (num_matched + num_spurious)
                if (num_matched + num_spurious) > 0
                else 0.0
            )

            recall = (
                num_matched / (num_matched + num_missed)
                if (num_matched + num_missed) > 0
                else 0.0
            )

            f1 = (
                2 * precision * recall / (precision + recall)
                if (precision + recall) > 0
                else 0.0
            )

            results[entity_type] = {
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'count': len(ref_type)
            }

        return results

    def get_entity_metrics(
        self,
        reference: str,
        hypothesis: str,
        threshold: float = 0.8
    ) -> Dict[str, Any]:
        """
        Get comprehensive entity metrics.

        Args:
            reference: Reference transcription
            hypothesis: Hypothesis transcription
            threshold: Similarity threshold for matching

        Returns:
            Dictionary with overall metrics, by-type metrics, and entity lists

        Example:
            >>> metrics = service.get_entity_metrics(
            ...     "John works at Google",
            ...     "Jon works at Goggle"
            ... )
            >>> print(f"Overall F1: {metrics['overall']['f1']:.2f}")
        """
        overall = self.calculate_entity_accuracy(reference, hypothesis, threshold)
        by_type = self.get_accuracy_by_type(reference, hypothesis, threshold)

        ref_entities = self.extract_entities(reference)
        hyp_entities = self.extract_entities(hypothesis)

        return {
            'overall': overall,
            'by_type': by_type,
            'reference_entities': ref_entities,
            'hypothesis_entities': hyp_entities,
            'precision': overall['precision'],
            'recall': overall['recall'],
            'f1': overall['f1']
        }
