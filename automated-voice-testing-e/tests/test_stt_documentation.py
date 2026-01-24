"""
Test suite for STT scope documentation.

This module tests that documentation properly covers:
- STT fidelity assumptions (scripts provide reference transcripts)
- Guidance for external ASR validation
"""

import os

import pytest


class TestSTTDocumentation:
    """Test STT documentation exists and covers required topics"""

    @pytest.fixture
    def docs_dir(self):
        """Get docs directory path"""
        return os.path.join(
            os.path.dirname(__file__),
            '..',
            'docs'
        )

    def test_stt_scope_doc_exists(self, docs_dir):
        """Test STT scope documentation file exists"""
        doc_path = os.path.join(docs_dir, 'stt-scope.md')
        assert os.path.exists(doc_path), "stt-scope.md should exist in docs/"

    def test_doc_covers_stt_assumption(self, docs_dir):
        """Test documentation clarifies STT fidelity assumption"""
        doc_path = os.path.join(docs_dir, 'stt-scope.md')

        with open(doc_path, 'r') as f:
            content = f.read().lower()

        assert 'reference transcript' in content or 'reference transcripts' in content
        assert 'assumption' in content or 'assumes' in content

    def test_doc_covers_external_asr(self, docs_dir):
        """Test documentation provides guidance for external ASR"""
        doc_path = os.path.join(docs_dir, 'stt-scope.md')

        with open(doc_path, 'r') as f:
            content = f.read().lower()

        assert 'external' in content or 'asr' in content
        assert 'validation' in content or 'validate' in content

    def test_doc_explains_no_stt_processing(self, docs_dir):
        """Test documentation explains we skip TTS/STT processing"""
        doc_path = os.path.join(docs_dir, 'stt-scope.md')

        with open(doc_path, 'r') as f:
            content = f.read().lower()

        assert 'skip' in content or 'bypass' in content or 'not perform' in content

    def test_doc_has_proper_structure(self, docs_dir):
        """Test documentation has proper markdown structure"""
        doc_path = os.path.join(docs_dir, 'stt-scope.md')

        with open(doc_path, 'r') as f:
            content = f.read()

        # Should have a title
        assert content.startswith('#')

        # Should have sections
        assert '##' in content


