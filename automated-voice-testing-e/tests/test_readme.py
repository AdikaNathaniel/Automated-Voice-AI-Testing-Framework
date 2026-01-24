"""
Test suite for README.md validation
Ensures the README contains all required sections and information
"""

import os
import re
import pytest


class TestReadme:
    """Test README.md file exists and contains required content"""

    @pytest.fixture
    def readme_path(self):
        """Get path to README.md file"""
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'README.md')

    @pytest.fixture
    def readme_content(self, readme_path):
        """Read README.md content"""
        if not os.path.exists(readme_path):
            pytest.fail(f"README.md file not found at {readme_path}")

        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()

    def test_readme_exists(self, readme_path):
        """Test that README.md file exists"""
        assert os.path.exists(readme_path), "README.md file must exist in project root"

    def test_readme_has_title(self, readme_content):
        """Test that README has a main title"""
        # Should have at least one H1 heading
        assert re.search(r'^# .+', readme_content, re.MULTILINE), \
            "README.md must have a main title (H1 heading)"

    def test_readme_has_project_description(self, readme_content):
        """Test that README contains project description"""
        required_keywords = [
            'Voice AI',
            'Testing',
            'Framework',
        ]

        for keyword in required_keywords:
            assert keyword in readme_content, \
                f"README.md must contain '{keyword}' in project description"

    def test_readme_has_features_section(self, readme_content):
        """Test that README has a features or key features section"""
        features_patterns = [
            r'## Features',
            r'## Key Features',
            r'## What We Deliver',
        ]

        has_features = any(re.search(pattern, readme_content, re.IGNORECASE)
                          for pattern in features_patterns)

        assert has_features, "README.md must have a Features section"

    def test_readme_has_architecture_section(self, readme_content):
        """Test that README has architecture overview"""
        architecture_patterns = [
            r'## Architecture',
            r'## System Architecture',
            r'## Overview',
        ]

        has_architecture = any(re.search(pattern, readme_content, re.IGNORECASE)
                              for pattern in architecture_patterns)

        assert has_architecture, "README.md must have an Architecture section"

    def test_readme_has_prerequisites_section(self, readme_content):
        """Test that README has prerequisites section"""
        assert re.search(r'## Prerequisites', readme_content, re.IGNORECASE), \
            "README.md must have a Prerequisites section"

    def test_readme_lists_required_tools(self, readme_content):
        """Test that README lists required development tools"""
        required_tools = [
            'Python',
            'Node.js',
            'PostgreSQL',
            'Redis',
        ]

        for tool in required_tools:
            assert tool in readme_content, \
                f"README.md must mention '{tool}' in prerequisites or setup"

    def test_readme_has_installation_section(self, readme_content):
        """Test that README has installation instructions"""
        installation_patterns = [
            r'## Installation',
            r'## Setup',
            r'## Getting Started',
        ]

        has_installation = any(re.search(pattern, readme_content, re.IGNORECASE)
                              for pattern in installation_patterns)

        assert has_installation, "README.md must have an Installation/Setup section"

    def test_readme_has_running_locally_instructions(self, readme_content):
        """Test that README has instructions for running locally"""
        # Should mention how to run the application
        run_keywords = ['run', 'start', 'launch', 'execute']

        has_run_instructions = any(keyword in readme_content.lower()
                                   for keyword in run_keywords)

        assert has_run_instructions, \
            "README.md must include instructions for running the application"

    def test_readme_has_code_blocks(self, readme_content):
        """Test that README includes code blocks for commands"""
        # Should have at least one code block (```)
        assert '```' in readme_content, \
            "README.md should include code blocks for installation/run commands"

    def test_readme_mentions_docker(self, readme_content):
        """Test that README mentions Docker for easy setup"""
        assert 'docker' in readme_content.lower(), \
            "README.md should mention Docker for containerized setup"

    def test_readme_has_project_structure_section(self, readme_content):
        """Test that README explains project structure"""
        structure_indicators = [
            'backend',
            'frontend',
            'infrastructure',
        ]

        structure_count = sum(1 for indicator in structure_indicators
                             if indicator in readme_content.lower())

        assert structure_count >= 2, \
            "README.md should describe the project structure"

    def test_readme_has_testing_section(self, readme_content):
        """Test that README has testing instructions"""
        testing_patterns = [
            r'## Testing',
            r'## Running Tests',
            r'## Tests',
        ]

        has_testing = any(re.search(pattern, readme_content, re.IGNORECASE)
                         for pattern in testing_patterns)

        assert has_testing, "README.md should have a Testing section"

    def test_readme_mentions_pytest(self, readme_content):
        """Test that README mentions pytest for testing"""
        assert 'pytest' in readme_content.lower(), \
            "README.md should mention pytest as the testing framework"

    def test_readme_has_contributing_or_license(self, readme_content):
        """Test that README has Contributing or License section"""
        has_contributing_or_license = (
            'contributing' in readme_content.lower() or
            'license' in readme_content.lower()
        )

        assert has_contributing_or_license, \
            "README.md should have Contributing or License information"

    def test_readme_has_contact_or_support(self, readme_content):
        """Test that README has contact or support information"""
        contact_indicators = [
            'contact',
            'support',
            'issues',
            'questions',
        ]

        has_contact = any(indicator in readme_content.lower()
                         for indicator in contact_indicators)

        assert has_contact, \
            "README.md should include contact or support information"

    def test_readme_proper_markdown_formatting(self, readme_content):
        """Test that README uses proper markdown formatting"""
        # Check for common markdown elements
        markdown_elements = [
            r'^#+ ',  # Headers
            r'^\* ',  # Unordered lists
            r'^\d+\. ',  # Ordered lists
        ]

        for pattern in markdown_elements:
            assert re.search(pattern, readme_content, re.MULTILINE), \
                f"README.md should use proper markdown formatting (pattern: {pattern})"

    def test_readme_mentions_soundhound(self, readme_content):
        """Test that README mentions SoundHound integration"""
        assert 'soundhound' in readme_content.lower(), \
            "README.md should mention SoundHound as the voice AI provider"

    def test_readme_mentions_accuracy_target(self, readme_content):
        """Test that README mentions the 99.7% accuracy target"""
        # Look for percentage or accuracy mention
        accuracy_patterns = [
            r'99\.7%',
            r'accuracy',
        ]

        has_accuracy = any(re.search(pattern, readme_content, re.IGNORECASE)
                          for pattern in accuracy_patterns)

        assert has_accuracy, \
            "README.md should mention the validation accuracy target"

    def test_readme_has_reasonable_length(self, readme_content):
        """Test that README has substantial content"""
        # Should have at least 100 lines or 3000 characters
        line_count = len(readme_content.splitlines())
        char_count = len(readme_content)

        assert line_count >= 100 or char_count >= 3000, \
            f"README.md should have substantial content (currently {line_count} lines, {char_count} chars)"
