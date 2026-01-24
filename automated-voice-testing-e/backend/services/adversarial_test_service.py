"""
Adversarial Test Generation Service for voice AI testing.

This service manages adversarial test generation including edge cases,
boundary conditions, typos, and grammar error injection.

Key features:
- Edge case generation
- Boundary condition tests
- Typo/mispronunciation injection
- Grammar error injection

Example:
    >>> service = AdversarialTestService()
    >>> tests = service.generate_edge_cases(base_text)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import random


class AdversarialTestService:
    """
    Service for adversarial test generation.

    Provides edge case, boundary condition, typo,
    and grammar error test generation.

    Example:
        >>> service = AdversarialTestService()
        >>> config = service.get_adversarial_config()
    """

    def __init__(self):
        """Initialize the adversarial test service."""
        self._generated_tests: List[Dict[str, Any]] = []

    def generate_edge_cases(
        self,
        text: str,
        categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate edge case tests from base text.

        Args:
            text: Base text to generate edge cases from
            categories: Categories of edge cases to generate

        Returns:
            Dictionary with generated edge cases

        Example:
            >>> result = service.generate_edge_cases('Hello world')
        """
        generation_id = str(uuid.uuid4())

        if categories is None:
            categories = ['empty', 'long', 'special_chars', 'unicode']

        edge_cases = []
        for category in categories:
            if category == 'empty':
                edge_cases.append({'text': '', 'category': 'empty'})
            elif category == 'long':
                edge_cases.append({'text': text * 10, 'category': 'long'})
            elif category == 'special_chars':
                edge_cases.append({'text': text + '!@#$%', 'category': 'special_chars'})
            elif category == 'unicode':
                edge_cases.append({'text': text + ' \u00e9\u00f1\u00fc', 'category': 'unicode'})

        result = {
            'generation_id': generation_id,
            'original': text,
            'edge_cases': edge_cases,
            'count': len(edge_cases),
            'created_at': datetime.utcnow().isoformat()
        }

        self._generated_tests.append(result)
        return result

    def get_edge_case_categories(self) -> List[str]:
        """
        Get available edge case categories.

        Returns:
            List of category names

        Example:
            >>> categories = service.get_edge_case_categories()
        """
        return [
            'empty',
            'long',
            'special_chars',
            'unicode',
            'whitespace',
            'numbers_only',
            'mixed_case',
            'punctuation'
        ]

    def generate_boundary_tests(
        self,
        text: str,
        boundary_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate boundary condition tests.

        Args:
            text: Base text
            boundary_types: Types of boundaries to test

        Returns:
            Dictionary with boundary tests

        Example:
            >>> result = service.generate_boundary_tests('Test input')
        """
        generation_id = str(uuid.uuid4())

        if boundary_types is None:
            boundary_types = ['min_length', 'max_length', 'char_limit']

        tests = []
        for btype in boundary_types:
            if btype == 'min_length':
                tests.append({'text': text[0] if text else '', 'type': 'min_length'})
            elif btype == 'max_length':
                tests.append({'text': text * 100, 'type': 'max_length'})
            elif btype == 'char_limit':
                tests.append({'text': 'a' * 1000, 'type': 'char_limit'})

        return {
            'generation_id': generation_id,
            'original': text,
            'boundary_tests': tests,
            'count': len(tests),
            'created_at': datetime.utcnow().isoformat()
        }

    def get_boundary_types(self) -> List[str]:
        """
        Get available boundary test types.

        Returns:
            List of boundary types

        Example:
            >>> types = service.get_boundary_types()
        """
        return [
            'min_length',
            'max_length',
            'char_limit',
            'word_limit',
            'sentence_limit',
            'numeric_range',
            'date_range'
        ]

    def inject_typos(
        self,
        text: str,
        error_rate: float = 0.1
    ) -> Dict[str, Any]:
        """
        Inject typos into text.

        Args:
            text: Input text
            error_rate: Rate of typo injection (0-1)

        Returns:
            Dictionary with modified text

        Example:
            >>> result = service.inject_typos('Hello world', 0.2)
        """
        words = list(text)
        num_errors = max(1, int(len(words) * error_rate))
        errors = []

        for _ in range(num_errors):
            if words:
                idx = random.randint(0, len(words) - 1)
                original = words[idx]
                if original.isalpha():
                    words[idx] = chr(ord(original) + 1)
                    errors.append({
                        'position': idx,
                        'original': original,
                        'typo': words[idx]
                    })

        return {
            'original': text,
            'result': ''.join(words),
            'errors': errors,
            'error_rate': error_rate,
            'created_at': datetime.utcnow().isoformat()
        }

    def inject_mispronunciations(
        self,
        text: str,
        phoneme_error_rate: float = 0.15
    ) -> Dict[str, Any]:
        """
        Inject mispronunciations into text.

        Args:
            text: Input text
            phoneme_error_rate: Rate of phoneme errors

        Returns:
            Dictionary with modified text

        Example:
            >>> result = service.inject_mispronunciations('Hello')
        """
        replacements = {
            'th': 'f',
            'r': 'w',
            's': 'sh',
            'v': 'b'
        }

        result = text
        applied = []

        for original, replacement in replacements.items():
            if original in result.lower():
                result = result.replace(original, replacement)
                applied.append({
                    'original': original,
                    'replacement': replacement
                })

        return {
            'original': text,
            'result': result,
            'mispronunciations': applied,
            'phoneme_error_rate': phoneme_error_rate,
            'created_at': datetime.utcnow().isoformat()
        }

    def inject_grammar_errors(
        self,
        text: str,
        error_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Inject grammar errors into text.

        Args:
            text: Input text
            error_types: Types of grammar errors to inject

        Returns:
            Dictionary with modified text

        Example:
            >>> result = service.inject_grammar_errors('I am happy')
        """
        if error_types is None:
            error_types = ['subject_verb', 'tense', 'article']

        errors = []
        result = text

        for error_type in error_types:
            if error_type == 'subject_verb':
                result = result.replace(' am ', ' is ')
                errors.append({'type': 'subject_verb', 'change': 'am -> is'})
            elif error_type == 'tense':
                result = result.replace('ed ', ' ')
                errors.append({'type': 'tense', 'change': 'removed -ed'})
            elif error_type == 'article':
                result = result.replace('the ', 'a ')
                errors.append({'type': 'article', 'change': 'the -> a'})

        return {
            'original': text,
            'result': result,
            'errors': errors,
            'created_at': datetime.utcnow().isoformat()
        }

    def get_grammar_error_types(self) -> List[Dict[str, str]]:
        """
        Get available grammar error types.

        Returns:
            List of error types with descriptions

        Example:
            >>> types = service.get_grammar_error_types()
        """
        return [
            {
                'type': 'subject_verb',
                'description': 'Subject-verb agreement errors'
            },
            {
                'type': 'tense',
                'description': 'Verb tense errors'
            },
            {
                'type': 'article',
                'description': 'Article usage errors'
            },
            {
                'type': 'preposition',
                'description': 'Preposition errors'
            },
            {
                'type': 'plural',
                'description': 'Plural form errors'
            }
        ]

    def get_adversarial_config(self) -> Dict[str, Any]:
        """
        Get adversarial test configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_adversarial_config()
        """
        return {
            'total_generated': len(self._generated_tests),
            'edge_case_categories': self.get_edge_case_categories(),
            'boundary_types': self.get_boundary_types(),
            'grammar_error_types': [e['type'] for e in self.get_grammar_error_types()],
            'default_typo_rate': 0.1,
            'default_phoneme_error_rate': 0.15
        }
