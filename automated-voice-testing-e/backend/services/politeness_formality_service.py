"""
Politeness and Formality Service for voice AI.

This service provides politeness and formality testing for
voice AI systems across different cultural contexts.

Key features:
- Formal vs informal register detection
- Honorifics and titles handling
- Cultural politeness norms evaluation

Example:
    >>> service = PolitenessService()
    >>> result = service.detect_formality(text)
"""

from typing import List, Dict, Any
import uuid


class PolitenessService:
    """
    Service for politeness and formality testing.

    Provides formality detection, honorifics handling,
    and cultural politeness evaluation.

    Example:
        >>> service = PolitenessService()
        >>> config = service.get_politeness_config()
    """

    def __init__(self):
        """Initialize the politeness service."""
        self._evaluations: List[Dict[str, Any]] = []

    def detect_formality(
        self,
        text: str,
        language: str = 'en'
    ) -> Dict[str, Any]:
        """
        Detect formality level in text.

        Args:
            text: Text to analyze
            language: Language code

        Returns:
            Dictionary with formality detection result

        Example:
            >>> result = service.detect_formality("Good morning, sir")
        """
        # Simple formality indicators
        formal_indicators = ['sir', 'madam', 'please', 'kindly', 'would you']
        informal_indicators = ['hey', 'yeah', 'gonna', 'wanna', 'cool']

        text_lower = text.lower()
        formal_count = sum(1 for ind in formal_indicators if ind in text_lower)
        informal_count = sum(1 for ind in informal_indicators if ind in text_lower)

        if formal_count > informal_count:
            level = 'formal'
            score = 0.8
        elif informal_count > formal_count:
            level = 'informal'
            score = 0.3
        else:
            level = 'neutral'
            score = 0.5

        return {
            'text': text,
            'language': language,
            'formality_level': level,
            'formality_score': score,
            'confidence': 0.85
        }

    def get_formality_levels(
        self,
        language: str = 'en'
    ) -> List[Dict[str, Any]]:
        """
        Get formality level definitions.

        Args:
            language: Language code

        Returns:
            List of formality level definitions

        Example:
            >>> levels = service.get_formality_levels('en')
        """
        return [
            {
                'level': 'very_formal',
                'score_range': [0.8, 1.0],
                'description': 'Highly formal register',
                'language': language
            },
            {
                'level': 'formal',
                'score_range': [0.6, 0.8],
                'description': 'Formal register',
                'language': language
            },
            {
                'level': 'neutral',
                'score_range': [0.4, 0.6],
                'description': 'Neutral register',
                'language': language
            },
            {
                'level': 'informal',
                'score_range': [0.2, 0.4],
                'description': 'Informal register',
                'language': language
            },
            {
                'level': 'very_informal',
                'score_range': [0.0, 0.2],
                'description': 'Very informal/casual register',
                'language': language
            }
        ]

    def detect_honorifics(
        self,
        text: str,
        language: str = 'en'
    ) -> Dict[str, Any]:
        """
        Detect honorifics and titles in text.

        Args:
            text: Text to analyze
            language: Language code

        Returns:
            Dictionary with honorific detection result

        Example:
            >>> result = service.detect_honorifics("Dr. Smith will see you")
        """
        honorifics = {
            'en': ['Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Prof.', 'Sir', 'Madam'],
            'de': ['Herr', 'Frau', 'Dr.', 'Prof.'],
            'ja': ['san', 'sama', 'kun', 'chan', 'sensei'],
            'es': ['Sr.', 'Sra.', 'Srta.', 'Dr.', 'Don', 'Doña']
        }

        lang_honorifics = honorifics.get(language, honorifics['en'])
        found = [h for h in lang_honorifics if h.lower() in text.lower()]

        return {
            'text': text,
            'language': language,
            'honorifics_found': found,
            'has_honorifics': len(found) > 0,
            'confidence': 0.90
        }

    def get_honorific_patterns(
        self,
        language: str = 'en'
    ) -> List[Dict[str, Any]]:
        """
        Get honorific patterns for language.

        Args:
            language: Language code

        Returns:
            List of honorific patterns

        Example:
            >>> patterns = service.get_honorific_patterns('en')
        """
        patterns = {
            'en': [
                {'pattern': 'Mr.', 'type': 'title', 'gender': 'male'},
                {'pattern': 'Mrs.', 'type': 'title', 'gender': 'female'},
                {'pattern': 'Ms.', 'type': 'title', 'gender': 'female'},
                {'pattern': 'Dr.', 'type': 'professional', 'gender': 'neutral'},
                {'pattern': 'Prof.', 'type': 'professional', 'gender': 'neutral'}
            ],
            'ja': [
                {'pattern': 'san', 'type': 'general', 'formality': 'neutral'},
                {'pattern': 'sama', 'type': 'respect', 'formality': 'high'},
                {'pattern': 'kun', 'type': 'familiar', 'formality': 'low'},
                {'pattern': 'sensei', 'type': 'professional', 'formality': 'high'}
            ]
        }

        return patterns.get(language, patterns['en'])

    def evaluate_politeness(
        self,
        text: str,
        culture: str = 'western'
    ) -> Dict[str, Any]:
        """
        Evaluate politeness according to cultural norms.

        Args:
            text: Text to evaluate
            culture: Cultural context

        Returns:
            Dictionary with politeness evaluation

        Example:
            >>> result = service.evaluate_politeness("Could you please help?")
        """
        evaluation_id = str(uuid.uuid4())

        # Simple politeness indicators
        polite_phrases = ['please', 'thank you', 'excuse me', 'would you mind']
        impolite_indicators = ['must', 'have to', 'now', 'immediately']

        text_lower = text.lower()
        polite_count = sum(1 for p in polite_phrases if p in text_lower)
        impolite_count = sum(1 for i in impolite_indicators if i in text_lower)

        score = 0.5 + (polite_count * 0.15) - (impolite_count * 0.1)
        score = max(0.0, min(1.0, score))

        evaluation = {
            'evaluation_id': evaluation_id,
            'text': text,
            'culture': culture,
            'politeness_score': score,
            'polite_markers': polite_count,
            'issues': [],
            'confidence': 0.80
        }

        self._evaluations.append(evaluation)
        return evaluation

    def get_cultural_norms(
        self,
        culture: str = 'western'
    ) -> Dict[str, Any]:
        """
        Get cultural politeness norms.

        Args:
            culture: Cultural context

        Returns:
            Dictionary with cultural norms

        Example:
            >>> norms = service.get_cultural_norms('japanese')
        """
        norms = {
            'western': {
                'directness': 'moderate',
                'formality_default': 'neutral',
                'honorific_usage': 'professional_only',
                'greeting_importance': 'medium',
                'apology_frequency': 'low'
            },
            'japanese': {
                'directness': 'indirect',
                'formality_default': 'formal',
                'honorific_usage': 'always',
                'greeting_importance': 'high',
                'apology_frequency': 'high'
            },
            'german': {
                'directness': 'high',
                'formality_default': 'formal',
                'honorific_usage': 'common',
                'greeting_importance': 'medium',
                'apology_frequency': 'low'
            },
            'latin_american': {
                'directness': 'moderate',
                'formality_default': 'warm',
                'honorific_usage': 'common',
                'greeting_importance': 'high',
                'apology_frequency': 'moderate'
            }
        }

        return {
            'culture': culture,
            'norms': norms.get(culture, norms['western']),
            'supported_cultures': list(norms.keys())
        }

    def get_politeness_config(self) -> Dict[str, Any]:
        """
        Get politeness service configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_politeness_config()
        """
        return {
            'supported_languages': ['en', 'de', 'ja', 'es', 'fr'],
            'supported_cultures': ['western', 'japanese', 'german', 'latin_american'],
            'formality_levels': 5,
            'total_evaluations': len(self._evaluations)
        }
