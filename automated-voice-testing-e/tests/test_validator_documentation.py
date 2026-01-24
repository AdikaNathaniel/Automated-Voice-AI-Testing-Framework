"""
Test suite for validator documentation.

This module tests that documentation properly covers:
- How rule-based validators and LLM judges interact
- Order of operations and escalation thresholds
- Configuration of new features (run_inline, tolerance definitions, personas)
"""

import os

import pytest


class TestValidatorDocumentation:
    """Test validator documentation exists and covers required topics"""

    @pytest.fixture
    def docs_dir(self):
        """Get docs directory path"""
        return os.path.join(
            os.path.dirname(__file__),
            '..',
            'docs'
        )

    def test_validator_doc_exists(self, docs_dir):
        """Test validator documentation file exists"""
        doc_path = os.path.join(docs_dir, 'validator-guide.md')
        assert os.path.exists(doc_path), "validator-guide.md should exist in docs/"

    def test_doc_covers_rule_based_validators(self, docs_dir):
        """Test documentation explains rule-based validators"""
        doc_path = os.path.join(docs_dir, 'validator-guide.md')

        with open(doc_path, 'r') as f:
            content = f.read().lower()

        assert 'rule' in content or 'rule-based' in content
        assert 'validator' in content

    def test_doc_covers_llm_judges(self, docs_dir):
        """Test documentation explains LLM judges"""
        doc_path = os.path.join(docs_dir, 'validator-guide.md')

        with open(doc_path, 'r') as f:
            content = f.read().lower()

        assert 'llm' in content or 'judge' in content
        assert 'ensemble' in content or 'consensus' in content

    def test_doc_covers_order_of_operations(self, docs_dir):
        """Test documentation explains order of operations"""
        doc_path = os.path.join(docs_dir, 'validator-guide.md')

        with open(doc_path, 'r') as f:
            content = f.read().lower()

        assert 'order' in content or 'sequence' in content or 'step' in content
        assert 'first' in content or '1.' in content

    def test_doc_covers_escalation_thresholds(self, docs_dir):
        """Test documentation explains escalation thresholds"""
        doc_path = os.path.join(docs_dir, 'validator-guide.md')

        with open(doc_path, 'r') as f:
            content = f.read().lower()

        assert 'escalat' in content
        assert 'threshold' in content or 'confidence' in content

    def test_doc_covers_run_inline(self, docs_dir):
        """Test documentation explains run_inline configuration"""
        doc_path = os.path.join(docs_dir, 'validator-guide.md')

        with open(doc_path, 'r') as f:
            content = f.read().lower()

        assert 'inline' in content or 'synchronous' in content

    def test_doc_covers_tolerance_definitions(self, docs_dir):
        """Test documentation explains tolerance definitions"""
        doc_path = os.path.join(docs_dir, 'validator-guide.md')

        with open(doc_path, 'r') as f:
            content = f.read().lower()

        assert 'tolerance' in content
        assert 'semantic' in content or 'threshold' in content

    def test_doc_covers_personas(self, docs_dir):
        """Test documentation explains persona configuration"""
        doc_path = os.path.join(docs_dir, 'validator-guide.md')

        with open(doc_path, 'r') as f:
            content = f.read().lower()

        assert 'persona' in content
        assert 'strictness' in content or 'evaluation' in content

    def test_doc_has_proper_structure(self, docs_dir):
        """Test documentation has proper markdown structure"""
        doc_path = os.path.join(docs_dir, 'validator-guide.md')

        with open(doc_path, 'r') as f:
            content = f.read()

        # Should have a title
        assert content.startswith('#')

        # Should have sections
        assert '##' in content

        # Should have code examples
        assert '```' in content

    def test_doc_covers_interaction_flow(self, docs_dir):
        """Test documentation explains how validators and judges interact"""
        doc_path = os.path.join(docs_dir, 'validator-guide.md')

        with open(doc_path, 'r') as f:
            content = f.read().lower()

        # Should explain interaction between rule-based and LLM
        assert 'interact' in content or 'combine' in content or 'together' in content


