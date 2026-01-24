"""
Test suite for Paraphrase Generation Service.

Components:
- Automatic paraphrase generation for test cases
- Synonym substitution
- Sentence restructuring
- Semantic equivalence validation
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestParaphraseServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'paraphrase_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'paraphrase_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class ParaphraseService' in service_file_content


class TestParaphraseGeneration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'paraphrase_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_generate_paraphrases_method(self, service_file_content):
        assert 'def generate_paraphrases(' in service_file_content

    def test_has_get_paraphrase_count_method(self, service_file_content):
        assert 'def get_paraphrase_count(' in service_file_content


class TestSynonymSubstitution:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'paraphrase_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_substitute_synonyms_method(self, service_file_content):
        assert 'def substitute_synonyms(' in service_file_content

    def test_has_get_synonyms_method(self, service_file_content):
        assert 'def get_synonyms(' in service_file_content


class TestSentenceRestructuring:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'paraphrase_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_restructure_sentence_method(self, service_file_content):
        assert 'def restructure_sentence(' in service_file_content

    def test_has_get_restructuring_patterns_method(self, service_file_content):
        assert 'def get_restructuring_patterns(' in service_file_content


class TestSemanticEquivalence:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'paraphrase_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_validate_semantic_equivalence_method(self, service_file_content):
        assert 'def validate_semantic_equivalence(' in service_file_content

    def test_has_get_similarity_score_method(self, service_file_content):
        assert 'def get_similarity_score(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'paraphrase_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_paraphrase_config_method(self, service_file_content):
        assert 'def get_paraphrase_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'paraphrase_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_imports_typing_modules(self, service_file_content):
        assert 'from typing import' in service_file_content

    def test_uses_dict_type_hint(self, service_file_content):
        assert 'Dict[' in service_file_content

    def test_uses_list_type_hint(self, service_file_content):
        assert 'List[' in service_file_content


class TestDocstrings:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'paraphrase_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class ParaphraseService' in service_file_content:
            idx = service_file_content.find('class ParaphraseService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
