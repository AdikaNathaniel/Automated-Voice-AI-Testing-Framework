"""
Test Developer Setup Guide Documentation

This module tests that the developer setup guide provides comprehensive
instructions for setting up the development environment.

Test Coverage:
    - File existence and structure
    - Required sections present
    - Prerequisites documented
    - Installation instructions complete
    - Running locally instructions
    - Code examples and commands
    - Troubleshooting guidance
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest


# =============================================================================
# File Structure Tests
# =============================================================================

class TestSetupGuideFileStructure:
    """Test setup guide file structure"""

    def test_setup_guide_file_exists(self):
        """Test that setup-guide.md file exists"""
        # Arrange
        project_root = Path(__file__).parent.parent
        setup_guide_file = project_root / "docs" / "setup-guide.md"

        # Act & Assert
        assert setup_guide_file.exists(), "setup-guide.md should exist in docs/"
        assert setup_guide_file.is_file(), "setup-guide.md should be a file"

    def test_setup_guide_has_content(self):
        """Test that setup-guide.md has substantial content"""
        # Arrange
        project_root = Path(__file__).parent.parent
        setup_guide_file = project_root / "docs" / "setup-guide.md"

        # Act
        content = setup_guide_file.read_text()

        # Assert
        assert len(content) > 1000, \
            "Setup guide should have substantial content (>1000 chars)"

    def test_setup_guide_is_markdown(self):
        """Test that setup guide uses markdown formatting"""
        # Arrange
        project_root = Path(__file__).parent.parent
        setup_guide_file = project_root / "docs" / "setup-guide.md"

        # Act
        content = setup_guide_file.read_text()

        # Assert
        assert "# " in content or "## " in content, \
            "Setup guide should have markdown headers"


# =============================================================================
# Required Sections Tests
# =============================================================================

class TestSetupGuideRequiredSections:
    """Test that setup guide has all required sections"""

    @pytest.fixture
    def content(self):
        """Load setup guide content"""
        project_root = Path(__file__).parent.parent
        setup_guide_file = project_root / "docs" / "setup-guide.md"
        return setup_guide_file.read_text()

    def test_has_title(self, content):
        """Test that setup guide has a title"""
        # Assert
        assert "# " in content, "Setup guide should have a main title"

    def test_has_prerequisites_section(self, content):
        """Test that setup guide has prerequisites section"""
        # Assert
        content_lower = content.lower()
        assert "prerequisite" in content_lower, \
            "Setup guide should have prerequisites section"

    def test_has_installation_section(self, content):
        """Test that setup guide has installation section"""
        # Assert
        content_lower = content.lower()
        assert "install" in content_lower, \
            "Setup guide should have installation section"

    def test_has_running_locally_section(self, content):
        """Test that setup guide has running locally section"""
        # Assert
        content_lower = content.lower()
        assert "running" in content_lower or "run" in content_lower, \
            "Setup guide should have section about running locally"

    def test_has_configuration_section(self, content):
        """Test that setup guide has configuration section"""
        # Assert
        content_lower = content.lower()
        assert "config" in content_lower or "environment" in content_lower, \
            "Setup guide should have configuration section"

    def test_has_troubleshooting_section(self, content):
        """Test that setup guide has troubleshooting section"""
        # Assert
        content_lower = content.lower()
        assert "troubleshoot" in content_lower or "common issue" in content_lower, \
            "Setup guide should have troubleshooting section"


# =============================================================================
# Prerequisites Content Tests
# =============================================================================

class TestSetupGuidePrerequisites:
    """Test that setup guide documents all prerequisites"""

    @pytest.fixture
    def content(self):
        """Load setup guide content"""
        project_root = Path(__file__).parent.parent
        setup_guide_file = project_root / "docs" / "setup-guide.md"
        return setup_guide_file.read_text()

    def test_documents_python_requirement(self, content):
        """Test that setup guide mentions Python requirement"""
        # Assert
        content_lower = content.lower()
        assert "python" in content_lower, \
            "Setup guide should mention Python requirement"

    def test_documents_nodejs_requirement(self, content):
        """Test that setup guide mentions Node.js requirement"""
        # Assert
        content_lower = content.lower()
        assert "node" in content_lower or "npm" in content_lower, \
            "Setup guide should mention Node.js requirement"

    def test_documents_docker_requirement(self, content):
        """Test that setup guide mentions Docker requirement"""
        # Assert
        content_lower = content.lower()
        assert "docker" in content_lower, \
            "Setup guide should mention Docker requirement"

    def test_documents_git_requirement(self, content):
        """Test that setup guide mentions Git requirement"""
        # Assert
        content_lower = content.lower()
        assert "git" in content_lower, \
            "Setup guide should mention Git requirement"


# =============================================================================
# Installation Instructions Tests
# =============================================================================

class TestSetupGuideInstallation:
    """Test that setup guide has complete installation instructions"""

    @pytest.fixture
    def content(self):
        """Load setup guide content"""
        project_root = Path(__file__).parent.parent
        setup_guide_file = project_root / "docs" / "setup-guide.md"
        return setup_guide_file.read_text()

    def test_includes_repository_clone_instructions(self, content):
        """Test that setup guide includes how to clone repository"""
        # Assert
        content_lower = content.lower()
        assert "clone" in content_lower or "git clone" in content_lower, \
            "Setup guide should include repository clone instructions"

    def test_includes_python_setup_instructions(self, content):
        """Test that setup guide includes Python environment setup"""
        # Assert
        content_lower = content.lower()
        assert "venv" in content_lower or "virtual" in content_lower, \
            "Setup guide should include Python virtual environment setup"

    def test_includes_dependency_installation(self, content):
        """Test that setup guide includes dependency installation"""
        # Assert
        content_lower = content.lower()
        assert "pip install" in content_lower or "npm install" in content_lower, \
            "Setup guide should include dependency installation commands"

    def test_includes_docker_setup(self, content):
        """Test that setup guide includes Docker setup"""
        # Assert
        content_lower = content.lower()
        assert "docker-compose" in content_lower or "docker compose" in content_lower, \
            "Setup guide should include Docker setup instructions"

    def test_includes_database_setup(self, content):
        """Test that setup guide includes database setup"""
        # Assert
        content_lower = content.lower()
        assert "database" in content_lower or "postgres" in content_lower, \
            "Setup guide should include database setup instructions"

    def test_includes_environment_variables_setup(self, content):
        """Test that setup guide includes environment variables setup"""
        # Assert
        content_lower = content.lower()
        assert ".env" in content_lower, \
            "Setup guide should include .env file setup instructions"


# =============================================================================
# Code Examples Tests
# =============================================================================

class TestSetupGuideCodeExamples:
    """Test that setup guide includes code examples and commands"""

    @pytest.fixture
    def content(self):
        """Load setup guide content"""
        project_root = Path(__file__).parent.parent
        setup_guide_file = project_root / "docs" / "setup-guide.md"
        return setup_guide_file.read_text()

    def test_has_code_blocks(self, content):
        """Test that setup guide has code blocks"""
        # Assert
        assert "```" in content, \
            "Setup guide should have code blocks (markdown ```)"

    def test_has_bash_commands(self, content):
        """Test that setup guide has bash commands"""
        # Assert
        assert "```bash" in content or "```sh" in content, \
            "Setup guide should have bash code blocks"

    def test_has_multiple_code_examples(self, content):
        """Test that setup guide has multiple code examples"""
        # Assert
        code_block_count = content.count("```")
        assert code_block_count >= 10, \
            f"Setup guide should have at least 5 code blocks (pairs), got {code_block_count // 2}"


# =============================================================================
# Running Locally Tests
# =============================================================================

class TestSetupGuideRunningLocally:
    """Test that setup guide includes instructions for running locally"""

    @pytest.fixture
    def content(self):
        """Load setup guide content"""
        project_root = Path(__file__).parent.parent
        setup_guide_file = project_root / "docs" / "setup-guide.md"
        return setup_guide_file.read_text()

    def test_includes_backend_start_instructions(self, content):
        """Test that setup guide includes how to start backend"""
        # Assert
        content_lower = content.lower()
        assert "uvicorn" in content_lower or "fastapi" in content_lower, \
            "Setup guide should include backend start instructions"

    def test_includes_frontend_start_instructions(self, content):
        """Test that setup guide includes how to start frontend"""
        # Assert
        content_lower = content.lower()
        assert "npm run" in content_lower or "vite" in content_lower, \
            "Setup guide should include frontend start instructions"

    def test_includes_docker_run_instructions(self, content):
        """Test that setup guide includes Docker run instructions"""
        # Assert
        content_lower = content.lower()
        assert "docker-compose up" in content_lower or "docker compose up" in content_lower, \
            "Setup guide should include Docker compose up command"

    def test_includes_migration_instructions(self, content):
        """Test that setup guide includes database migration instructions"""
        # Assert
        content_lower = content.lower()
        assert "alembic" in content_lower or "migration" in content_lower, \
            "Setup guide should include database migration instructions"


# =============================================================================
# Best Practices Tests
# =============================================================================

class TestSetupGuideBestPractices:
    """Test that setup guide follows documentation best practices"""

    @pytest.fixture
    def content(self):
        """Load setup guide content"""
        project_root = Path(__file__).parent.parent
        setup_guide_file = project_root / "docs" / "setup-guide.md"
        return setup_guide_file.read_text()

    def test_has_table_of_contents(self, content):
        """Test that setup guide has table of contents for navigation"""
        # Assert
        content_lower = content.lower()
        # Table of contents OR multiple level-2 headers (good organization)
        has_toc = "table of contents" in content_lower or "## " in content
        assert has_toc, \
            "Setup guide should have table of contents or clear section organization"

    def test_uses_consistent_formatting(self, content):
        """Test that setup guide uses consistent markdown formatting"""
        # Assert
        # Should have headers, code blocks, and lists
        has_headers = "## " in content
        has_code_blocks = "```" in content
        has_lists = "\n- " in content or "\n* " in content or "\n1. " in content

        assert has_headers and has_code_blocks and has_lists, \
            "Setup guide should use consistent markdown formatting (headers, code, lists)"

    def test_provides_step_by_step_instructions(self, content):
        """Test that setup guide provides numbered or clear step instructions"""
        # Assert
        content_lower = content.lower()
        has_numbered_list = "\n1. " in content
        has_step_indicators = "step " in content_lower

        assert has_numbered_list or has_step_indicators, \
            "Setup guide should provide clear step-by-step instructions"
