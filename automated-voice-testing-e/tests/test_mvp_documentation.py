"""
Test suite for MVP documentation.

This module tests that documentation properly covers:
- Scripted scenario workflow
- LLM ensemble approach
- Tolerance handling
- Confirmation loops and alternate outcomes
"""

import os

import pytest


class TestMVPDocumentation:
    """Test MVP documentation exists and covers required topics"""

    @pytest.fixture
    def docs_dir(self):
        """Get docs directory path"""
        return os.path.join(
            os.path.dirname(__file__),
            '..',
            'docs'
        )

    def test_mvp_workflow_doc_exists(self, docs_dir):
        """Test MVP workflow documentation file exists"""
        doc_path = os.path.join(docs_dir, 'mvp-workflow.md')
        assert os.path.exists(doc_path), "mvp-workflow.md should exist in docs/"

    def test_doc_covers_scripted_scenarios(self, docs_dir):
        """Test documentation covers scripted scenario workflow"""
        doc_path = os.path.join(docs_dir, 'mvp-workflow.md')

        with open(doc_path, 'r') as f:
            content = f.read().lower()

        assert 'scenario' in content
        assert 'script' in content or 'step' in content

    def test_doc_covers_llm_ensemble(self, docs_dir):
        """Test documentation covers LLM ensemble approach"""
        doc_path = os.path.join(docs_dir, 'mvp-workflow.md')

        with open(doc_path, 'r') as f:
            content = f.read().lower()

        assert 'ensemble' in content or 'judge' in content
        assert 'llm' in content or 'consensus' in content

    def test_doc_covers_tolerance_handling(self, docs_dir):
        """Test documentation covers tolerance handling"""
        doc_path = os.path.join(docs_dir, 'mvp-workflow.md')

        with open(doc_path, 'r') as f:
            content = f.read().lower()

        assert 'tolerance' in content
        assert 'threshold' in content or 'semantic' in content

    def test_doc_covers_confirmation_loops(self, docs_dir):
        """Test documentation includes confirmation loop examples"""
        doc_path = os.path.join(docs_dir, 'mvp-workflow.md')

        with open(doc_path, 'r') as f:
            content = f.read().lower()

        assert 'confirm' in content
        assert 'example' in content or 'sample' in content

    def test_doc_covers_alternate_outcomes(self, docs_dir):
        """Test documentation covers alternate outcomes"""
        doc_path = os.path.join(docs_dir, 'mvp-workflow.md')

        with open(doc_path, 'r') as f:
            content = f.read().lower()

        assert 'alternate' in content or 'alternative' in content

    def test_doc_has_proper_structure(self, docs_dir):
        """Test documentation has proper markdown structure"""
        doc_path = os.path.join(docs_dir, 'mvp-workflow.md')

        with open(doc_path, 'r') as f:
            content = f.read()

        # Should have a title
        assert content.startswith('#')

        # Should have code examples
        assert '```' in content


