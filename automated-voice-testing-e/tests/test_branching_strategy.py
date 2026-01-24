"""
Test suite for branching strategy documentation
Ensures docs/branching-strategy.md exists and contains required Git workflow information
"""

import os
import re
import pytest


class TestBranchingStrategy:
    """Test branching strategy documentation exists and is complete"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return os.path.dirname(os.path.dirname(__file__))

    @pytest.fixture
    def docs_dir(self, project_root):
        """Get docs directory path"""
        return os.path.join(project_root, 'docs')

    @pytest.fixture
    def branching_strategy_path(self, docs_dir):
        """Get path to branching-strategy.md file"""
        return os.path.join(docs_dir, 'branching-strategy.md')

    @pytest.fixture
    def branching_content(self, branching_strategy_path):
        """Read branching strategy documentation content"""
        if not os.path.exists(branching_strategy_path):
            pytest.fail(f"branching-strategy.md file not found at {branching_strategy_path}")

        with open(branching_strategy_path, 'r', encoding='utf-8') as f:
            return f.read()

    def test_docs_directory_exists(self, docs_dir):
        """Test that docs directory exists"""
        assert os.path.exists(docs_dir), "docs directory must exist"
        assert os.path.isdir(docs_dir), "docs must be a directory"

    def test_branching_strategy_file_exists(self, branching_strategy_path):
        """Test that branching-strategy.md file exists"""
        assert os.path.exists(branching_strategy_path), \
            "docs/branching-strategy.md file must exist"

    def test_has_title(self, branching_content):
        """Test that document has a main title"""
        assert re.search(r'^# .+', branching_content, re.MULTILINE), \
            "branching-strategy.md must have a main title (H1 heading)"

    def test_has_overview_section(self, branching_content):
        """Test that document has overview/introduction section"""
        overview_patterns = [
            r'## Overview',
            r'## Introduction',
            r'## Branching Model',
        ]

        has_overview = any(re.search(pattern, branching_content, re.IGNORECASE)
                          for pattern in overview_patterns)

        assert has_overview, "Document must have an Overview or Introduction section"

    def test_mentions_main_branch(self, branching_content):
        """Test that document mentions main/master branch"""
        assert re.search(r'\bmain\b', branching_content, re.IGNORECASE) or \
               re.search(r'\bmaster\b', branching_content, re.IGNORECASE), \
            "Document must mention the main/master branch"

    def test_mentions_develop_branch(self, branching_content):
        """Test that document mentions develop/development branch"""
        develop_patterns = [
            r'\bdevelop\b',
            r'\bdevelopment\b',
            r'\bdev\b',
        ]

        has_develop = any(re.search(pattern, branching_content, re.IGNORECASE)
                         for pattern in develop_patterns)

        assert has_develop, "Document must mention the develop/development branch"

    def test_mentions_feature_branches(self, branching_content):
        """Test that document mentions feature branches"""
        feature_patterns = [
            r'feature/',
            r'feature branch',
            r'feature-',
        ]

        has_feature = any(re.search(pattern, branching_content, re.IGNORECASE)
                         for pattern in feature_patterns)

        assert has_feature, "Document must mention feature branches"

    def test_mentions_hotfix_branches(self, branching_content):
        """Test that document mentions hotfix branches"""
        hotfix_patterns = [
            r'hotfix/',
            r'hotfix branch',
            r'hotfix-',
        ]

        has_hotfix = any(re.search(pattern, branching_content, re.IGNORECASE)
                        for pattern in hotfix_patterns)

        assert has_hotfix, "Document must mention hotfix branches"

    def test_has_branch_types_section(self, branching_content):
        """Test that document has a section describing branch types"""
        branch_type_patterns = [
            r'## Branch Types',
            r'## Branch Categories',
            r'## Branches',
        ]

        has_branch_types = any(re.search(pattern, branching_content, re.IGNORECASE)
                              for pattern in branch_type_patterns)

        assert has_branch_types, "Document must have a section describing branch types"

    def test_has_protection_rules_section(self, branching_content):
        """Test that document has branch protection rules section"""
        protection_patterns = [
            r'## Branch Protection',
            r'## Protection Rules',
            r'## Branch Rules',
        ]

        has_protection = any(re.search(pattern, branching_content, re.IGNORECASE)
                            for pattern in protection_patterns)

        assert has_protection, "Document must have a branch protection rules section"

    def test_mentions_pull_requests(self, branching_content):
        """Test that document mentions pull requests"""
        pr_patterns = [
            r'pull request',
            r'PR',
            r'merge request',
        ]

        has_pr = any(re.search(pattern, branching_content, re.IGNORECASE)
                    for pattern in pr_patterns)

        assert has_pr, "Document must mention pull requests/merge requests"

    def test_mentions_code_review(self, branching_content):
        """Test that document mentions code review"""
        review_patterns = [
            r'code review',
            r'review',
            r'approval',
        ]

        has_review = any(re.search(pattern, branching_content, re.IGNORECASE)
                        for pattern in review_patterns)

        assert has_review, "Document must mention code review process"

    def test_has_workflow_section(self, branching_content):
        """Test that document describes the Git workflow"""
        workflow_patterns = [
            r'## Workflow',
            r'## Git Workflow',
            r'## Development Workflow',
            r'## Process',
        ]

        has_workflow = any(re.search(pattern, branching_content, re.IGNORECASE)
                          for pattern in workflow_patterns)

        assert has_workflow, "Document must describe the Git workflow"

    def test_mentions_testing_requirements(self, branching_content):
        """Test that document mentions testing requirements"""
        test_keywords = ['test', 'testing', 'CI', 'continuous integration']

        has_testing = any(keyword in branching_content.lower()
                         for keyword in test_keywords)

        assert has_testing, "Document should mention testing requirements"

    def test_has_proper_markdown_formatting(self, branching_content):
        """Test that document uses proper markdown formatting"""
        markdown_elements = [
            r'^#+ ',  # Headers
            r'^[\*\-] ',  # Unordered lists
        ]

        for pattern in markdown_elements:
            assert re.search(pattern, branching_content, re.MULTILINE), \
                f"Document should use proper markdown formatting (pattern: {pattern})"

    def test_has_naming_conventions(self, branching_content):
        """Test that document describes branch naming conventions"""
        naming_keywords = ['naming', 'convention', 'format', 'pattern']

        has_naming = any(keyword in branching_content.lower()
                        for keyword in naming_keywords)

        assert has_naming, "Document should describe branch naming conventions"

    def test_has_reasonable_length(self, branching_content):
        """Test that document has substantial content"""
        line_count = len(branching_content.splitlines())
        char_count = len(branching_content)

        assert line_count >= 50 or char_count >= 1500, \
            f"Document should have substantial content (currently {line_count} lines, {char_count} chars)"

    def test_mentions_merge_strategy(self, branching_content):
        """Test that document mentions merge strategy"""
        merge_keywords = ['merge', 'rebase', 'squash']

        has_merge_info = any(keyword in branching_content.lower()
                            for keyword in merge_keywords)

        assert has_merge_info, "Document should mention merge strategy"

    def test_has_release_process(self, branching_content):
        """Test that document mentions release process"""
        release_patterns = [
            r'release/',
            r'release branch',
            r'release-',
            r'releasing',
            r'deployment',
        ]

        has_release = any(re.search(pattern, branching_content, re.IGNORECASE)
                         for pattern in release_patterns)

        assert has_release, "Document should mention release process"

    def test_mentions_commit_messages(self, branching_content):
        """Test that document mentions commit message conventions"""
        commit_keywords = ['commit', 'message', 'conventional commits']

        has_commit_info = any(keyword in branching_content.lower()
                             for keyword in commit_keywords)

        assert has_commit_info, "Document should mention commit message conventions"
