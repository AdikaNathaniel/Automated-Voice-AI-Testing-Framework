"""
Test Realistic Test Suite

This test validates that we have a realistic test suite for pilot deployment:
- 50-100 test cases (utterances)
- 2-3 domains (e.g., navigation, media, climate)
- 2+ languages (e.g., en-US, es-MX)
- Can execute end-to-end through the pipeline

TODOS.md Section 7: "At least one realistic suite of test cases executing end-to-end"
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import pytest
from typing import List, Dict, Any
from uuid import UUID


class TestRealisticTestSuiteStructure:
    """
    Test that validates the realistic test suite has the correct structure
    and characteristics for pilot deployment.
    """

    def test_realistic_suite_exists(self):
        """Test that a realistic test suite exists"""
        from tests.fixtures.realistic_suite import REALISTIC_SUITE

        assert REALISTIC_SUITE is not None
        assert 'name' in REALISTIC_SUITE
        assert 'description' in REALISTIC_SUITE
        assert 'test_cases' in REALISTIC_SUITE

    def test_suite_has_50_to_100_test_cases(self):
        """Test that suite has 50-100 test cases as required for pilot"""
        from tests.fixtures.realistic_suite import REALISTIC_SUITE

        test_cases = REALISTIC_SUITE['test_cases']
        num_cases = len(test_cases)

        assert num_cases >= 50, f"Suite has only {num_cases} test cases, need at least 50"
        assert num_cases <= 100, f"Suite has {num_cases} test cases, should be at most 100"

    def test_suite_has_multiple_domains(self):
        """Test that suite covers 2-3 domains (e.g., navigation, media, climate)"""
        from tests.fixtures.realistic_suite import REALISTIC_SUITE

        test_cases = REALISTIC_SUITE['test_cases']

        # Extract domains from test cases
        domains = set()
        for test_case in test_cases:
            domain = test_case.get('domain')
            if domain:
                domains.add(domain)

        num_domains = len(domains)
        assert num_domains >= 2, f"Suite has only {num_domains} domain(s), need at least 2"
        assert num_domains <= 5, f"Suite has {num_domains} domains, keep it focused (2-5)"

    def test_suite_has_multiple_languages(self):
        """Test that suite includes 2+ languages"""
        from tests.fixtures.realistic_suite import REALISTIC_SUITE

        test_cases = REALISTIC_SUITE['test_cases']

        # Extract languages from test cases
        languages = set()
        for test_case in test_cases:
            # Languages can be in 'languages' list or 'language' field
            case_languages = test_case.get('languages', [])
            if not case_languages:
                lang = test_case.get('language')
                if lang:
                    case_languages = [lang]

            for lang in case_languages:
                languages.add(lang)

        num_languages = len(languages)
        assert num_languages >= 2, f"Suite has only {num_languages} language(s), need at least 2"

    def test_suite_domains_are_realistic(self):
        """Test that domains are realistic for automotive voice AI"""
        from tests.fixtures.realistic_suite import REALISTIC_SUITE

        test_cases = REALISTIC_SUITE['test_cases']

        # Common automotive voice AI domains
        valid_domains = {
            'navigation',
            'media',
            'climate',
            'phone',
            'weather',
            'general',
            'search',
            'entertainment',
            'home_automation',
            'calendar',
        }

        domains = set()
        for test_case in test_cases:
            domain = test_case.get('domain')
            if domain:
                domains.add(domain)

        # All domains should be in the valid set
        for domain in domains:
            assert domain in valid_domains, f"Domain '{domain}' is not a recognized automotive domain"

    def test_suite_languages_are_realistic(self):
        """Test that languages are realistic and properly formatted"""
        from tests.fixtures.realistic_suite import REALISTIC_SUITE

        test_cases = REALISTIC_SUITE['test_cases']

        # Common language codes for automotive voice AI
        valid_languages = {
            'en-US',  # English (US)
            'en-GB',  # English (UK)
            'es-MX',  # Spanish (Mexico)
            'es-ES',  # Spanish (Spain)
            'fr-FR',  # French (France)
            'fr-CA',  # French (Canada)
            'de-DE',  # German (Germany)
            'it-IT',  # Italian (Italy)
            'pt-BR',  # Portuguese (Brazil)
            'ja-JP',  # Japanese (Japan)
            'ko-KR',  # Korean (South Korea)
            'zh-CN',  # Chinese (Simplified)
            'zh-TW',  # Chinese (Traditional)
        }

        languages = set()
        for test_case in test_cases:
            case_languages = test_case.get('languages', [])
            if not case_languages:
                lang = test_case.get('language')
                if lang:
                    case_languages = [lang]

            for lang in case_languages:
                languages.add(lang)

        # All languages should be in the valid set
        for lang in languages:
            assert lang in valid_languages, f"Language '{lang}' is not a recognized language code"

    def test_each_test_case_has_required_fields(self):
        """Test that each test case has required fields"""
        from tests.fixtures.realistic_suite import REALISTIC_SUITE

        test_cases = REALISTIC_SUITE['test_cases']

        required_fields = ['query_text', 'domain', 'expected_intent']

        for i, test_case in enumerate(test_cases):
            for field in required_fields:
                assert field in test_case, f"Test case {i} missing required field '{field}'"
                assert test_case[field], f"Test case {i} has empty '{field}'"

    def test_each_test_case_has_expected_outcome(self):
        """Test that each test case has an expected outcome defined"""
        from tests.fixtures.realistic_suite import REALISTIC_SUITE

        test_cases = REALISTIC_SUITE['test_cases']

        for i, test_case in enumerate(test_cases):
            assert 'expected_outcome' in test_case, f"Test case {i} missing 'expected_outcome'"

            outcome = test_case['expected_outcome']
            assert 'intent' in outcome, f"Test case {i} expected_outcome missing 'intent'"

            # Should have at least intent, optionally entities and response
            assert outcome['intent'], f"Test case {i} expected_outcome has empty intent"

    def test_suite_has_balanced_distribution(self):
        """Test that test cases are reasonably distributed across domains"""
        from tests.fixtures.realistic_suite import REALISTIC_SUITE

        test_cases = REALISTIC_SUITE['test_cases']

        # Count test cases per domain
        domain_counts = {}
        for test_case in test_cases:
            domain = test_case.get('domain')
            if domain:
                domain_counts[domain] = domain_counts.get(domain, 0) + 1

        total = len(test_cases)

        # No single domain should have more than 60% of test cases
        for domain, count in domain_counts.items():
            percentage = (count / total) * 100
            assert percentage <= 60, f"Domain '{domain}' has {percentage:.1f}% of cases, should be more balanced"

        # No domain should have less than 10% of test cases
        for domain, count in domain_counts.items():
            percentage = (count / total) * 100
            assert percentage >= 10, f"Domain '{domain}' has only {percentage:.1f}% of cases, too few"

    def test_suite_metadata_is_complete(self):
        """Test that suite has complete metadata"""
        from tests.fixtures.realistic_suite import REALISTIC_SUITE

        assert 'name' in REALISTIC_SUITE
        assert REALISTIC_SUITE['name'], "Suite name is empty"

        assert 'description' in REALISTIC_SUITE
        assert REALISTIC_SUITE['description'], "Suite description is empty"

        assert 'version' in REALISTIC_SUITE or 'created_at' in REALISTIC_SUITE, \
            "Suite should have version or created_at metadata"


class TestRealisticTestSuiteContent:
    """
    Test that validates the realistic test suite content quality.
    """

    def test_navigation_domain_cases_exist(self):
        """Test that navigation domain test cases exist"""
        from tests.fixtures.realistic_suite import REALISTIC_SUITE

        test_cases = REALISTIC_SUITE['test_cases']

        navigation_cases = [tc for tc in test_cases if tc.get('domain') == 'navigation']
        assert len(navigation_cases) >= 15, \
            f"Need at least 15 navigation test cases, found {len(navigation_cases)}"

    def test_media_domain_cases_exist(self):
        """Test that media domain test cases exist"""
        from tests.fixtures.realistic_suite import REALISTIC_SUITE

        test_cases = REALISTIC_SUITE['test_cases']

        media_cases = [tc for tc in test_cases if tc.get('domain') == 'media']
        assert len(media_cases) >= 10, \
            f"Need at least 10 media test cases, found {len(media_cases)}"

    def test_test_cases_have_variety(self):
        """Test that test cases show variety in phrasing and intents"""
        from tests.fixtures.realistic_suite import REALISTIC_SUITE

        test_cases = REALISTIC_SUITE['test_cases']

        # Extract all intents
        intents = set()
        for test_case in test_cases:
            intent = test_case.get('expected_intent')
            if intent:
                intents.add(intent)

        # Should have at least 10 different intents across all domains
        assert len(intents) >= 10, \
            f"Need at least 10 different intents for variety, found {len(intents)}"

    def test_test_cases_are_not_duplicates(self):
        """Test that test cases are not exact duplicates"""
        from tests.fixtures.realistic_suite import REALISTIC_SUITE

        test_cases = REALISTIC_SUITE['test_cases']

        # Check for duplicate query texts (allowing for some variation)
        query_texts = []
        for test_case in test_cases:
            query_text = test_case.get('query_text', '').lower().strip()
            query_texts.append(query_text)

        # Count duplicates
        from collections import Counter
        query_counts = Counter(query_texts)

        duplicates = {text: count for text, count in query_counts.items() if count > 1}

        # Allow up to 5% duplicates (for testing variations)
        max_duplicates = len(test_cases) * 0.05
        actual_duplicates = sum(count - 1 for count in duplicates.values())

        assert actual_duplicates <= max_duplicates, \
            f"Too many duplicate queries: {actual_duplicates} duplicates found"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
