"""
Test Demo Script Documentation

This module tests that the demo script provides comprehensive
steps for showcasing the framework's functionality.

Test Coverage:
    - File existence and structure
    - Required sections present
    - Demo preparation steps
    - Demo execution steps
    - Feature showcase coverage
    - Code examples present
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

class TestDemoScriptFileStructure:
    """Test demo script file structure"""

    def test_demo_script_file_exists(self):
        """Test that demo-script.md file exists"""
        # Arrange
        project_root = Path(__file__).parent.parent
        demo_script_file = project_root / "docs" / "demo-script.md"

        # Act & Assert
        assert demo_script_file.exists(), "demo-script.md should exist in docs/"
        assert demo_script_file.is_file(), "demo-script.md should be a file"

    def test_demo_script_has_content(self):
        """Test that demo-script.md has substantial content"""
        # Arrange
        project_root = Path(__file__).parent.parent
        demo_script_file = project_root / "docs" / "demo-script.md"

        # Act
        content = demo_script_file.read_text()

        # Assert
        assert len(content) > 2000, \
            "Demo script should have substantial content (>2000 chars)"

    def test_demo_script_is_markdown(self):
        """Test that demo script uses markdown formatting"""
        # Arrange
        project_root = Path(__file__).parent.parent
        demo_script_file = project_root / "docs" / "demo-script.md"

        # Act
        content = demo_script_file.read_text()

        # Assert
        assert "# " in content or "## " in content, \
            "Demo script should have markdown headers"


# =============================================================================
# Required Sections Tests
# =============================================================================

class TestDemoScriptRequiredSections:
    """Test that demo script has all required sections"""

    @pytest.fixture
    def content(self):
        """Load demo script content"""
        project_root = Path(__file__).parent.parent
        demo_script_file = project_root / "docs" / "demo-script.md"
        return demo_script_file.read_text()

    def test_has_title(self, content):
        """Test that demo script has a title"""
        # Assert
        assert "# " in content, "Demo script should have a main title"

    def test_has_preparation_section(self, content):
        """Test that demo script has preparation section"""
        # Assert
        content_lower = content.lower()
        assert "preparation" in content_lower or "setup" in content_lower, \
            "Demo script should have preparation/setup section"

    def test_has_demo_steps_section(self, content):
        """Test that demo script has demo steps section"""
        # Assert
        content_lower = content.lower()
        assert "demo" in content_lower or "step" in content_lower, \
            "Demo script should have demo steps section"

    def test_has_features_showcase_section(self, content):
        """Test that demo script showcases features"""
        # Assert
        content_lower = content.lower()
        assert "feature" in content_lower or "showcase" in content_lower, \
            "Demo script should have features showcase section"


# =============================================================================
# Preparation Steps Tests
# =============================================================================

class TestDemoScriptPreparation:
    """Test that demo script documents preparation steps"""

    @pytest.fixture
    def content(self):
        """Load demo script content"""
        project_root = Path(__file__).parent.parent
        demo_script_file = project_root / "docs" / "demo-script.md"
        return demo_script_file.read_text()

    def test_documents_environment_setup(self, content):
        """Test that demo script documents environment setup"""
        # Assert
        content_lower = content.lower()
        assert "environment" in content_lower or "setup" in content_lower, \
            "Demo script should document environment setup"

    def test_documents_data_loading(self, content):
        """Test that demo script documents loading demo data"""
        # Assert
        content_lower = content.lower()
        assert "demo data" in content_lower or "load" in content_lower, \
            "Demo script should document loading demo data"

    def test_documents_starting_services(self, content):
        """Test that demo script documents starting services"""
        # Assert
        content_lower = content.lower()
        has_services = any(term in content_lower for term in [
            "docker", "server", "service", "start", "run"
        ])
        assert has_services, \
            "Demo script should document starting services"


# =============================================================================
# Demo Execution Tests
# =============================================================================

class TestDemoScriptExecution:
    """Test that demo script documents execution steps"""

    @pytest.fixture
    def content(self):
        """Load demo script content"""
        project_root = Path(__file__).parent.parent
        demo_script_file = project_root / "docs" / "demo-script.md"
        return demo_script_file.read_text()

    def test_has_numbered_steps(self, content):
        """Test that demo script has numbered steps"""
        # Assert
        # Check for numbered lists
        has_numbered_list = "1. " in content or "1)" in content
        assert has_numbered_list, \
            "Demo script should have numbered steps"

    def test_documents_api_access(self, content):
        """Test that demo script documents API access"""
        # Assert
        content_lower = content.lower()
        assert "api" in content_lower or "endpoint" in content_lower, \
            "Demo script should document API access"

    def test_documents_frontend_access(self, content):
        """Test that demo script documents frontend access"""
        # Assert
        content_lower = content.lower()
        has_frontend = any(term in content_lower for term in [
            "frontend", "ui", "browser", "interface", "web"
        ])
        assert has_frontend, \
            "Demo script should document frontend access"

    def test_documents_authentication(self, content):
        """Test that demo script documents authentication"""
        # Assert
        content_lower = content.lower()
        has_auth = any(term in content_lower for term in [
            "login", "authentication", "register", "token"
        ])
        assert has_auth, \
            "Demo script should document authentication"


# =============================================================================
# Feature Showcase Tests
# =============================================================================

class TestDemoScriptFeatureShowcase:
    """Test that demo script showcases key features"""

    @pytest.fixture
    def content(self):
        """Load demo script content"""
        project_root = Path(__file__).parent.parent
        demo_script_file = project_root / "docs" / "demo-script.md"
        return demo_script_file.read_text()

    def test_showcases_test_case_creation(self, content):
        """Test that demo script showcases test case creation"""
        # Assert
        content_lower = content.lower()
        assert "test case" in content_lower or "create test" in content_lower, \
            "Demo script should showcase test case creation"

    def test_showcases_test_suite_management(self, content):
        """Test that demo script showcases test suite management"""
        # Assert
        content_lower = content.lower()
        assert "test suite" in content_lower or "suite" in content_lower, \
            "Demo script should showcase test suite management"

    def test_showcases_test_execution(self, content):
        """Test that demo script showcases test execution"""
        # Assert
        content_lower = content.lower()
        has_execution = any(term in content_lower for term in [
            "execute", "run test", "execution", "running"
        ])
        assert has_execution, \
            "Demo script should showcase test execution"

    def test_showcases_multilingual_support(self, content):
        """Test that demo script showcases multilingual support"""
        # Assert
        content_lower = content.lower()
        has_multilingual = any(term in content_lower for term in [
            "language", "multilingual", "translation", "spanish", "french"
        ])
        assert has_multilingual, \
            "Demo script should showcase multilingual support"

    def test_showcases_test_results(self, content):
        """Test that demo script showcases viewing test results"""
        # Assert
        content_lower = content.lower()
        assert "result" in content_lower, \
            "Demo script should showcase test results"


# =============================================================================
# Code Examples Tests
# =============================================================================

class TestDemoScriptCodeExamples:
    """Test that demo script includes code examples"""

    @pytest.fixture
    def content(self):
        """Load demo script content"""
        project_root = Path(__file__).parent.parent
        demo_script_file = project_root / "docs" / "demo-script.md"
        return demo_script_file.read_text()

    def test_has_code_blocks(self, content):
        """Test that demo script has code blocks"""
        # Assert
        assert "```" in content, \
            "Demo script should have code blocks (markdown ```)"

    def test_has_command_examples(self, content):
        """Test that demo script has command examples"""
        # Assert
        content_lower = content.lower()
        # Should have some CLI commands
        has_commands = "```bash" in content_lower or "```sh" in content_lower
        assert has_commands, \
            "Demo script should have command examples"

    def test_has_multiple_code_examples(self, content):
        """Test that demo script has multiple code examples"""
        # Assert
        code_block_count = content.count("```")
        assert code_block_count >= 4, \
            f"Demo script should have at least 2 code blocks (pairs), got {code_block_count // 2}"


# =============================================================================
# Best Practices Tests
# =============================================================================

class TestDemoScriptBestPractices:
    """Test that demo script follows documentation best practices"""

    @pytest.fixture
    def content(self):
        """Load demo script content"""
        project_root = Path(__file__).parent.parent
        demo_script_file = project_root / "docs" / "demo-script.md"
        return demo_script_file.read_text()

    def test_has_clear_organization(self, content):
        """Test that demo script is clearly organized"""
        # Assert
        has_headers = "## " in content
        assert has_headers, \
            "Demo script should have clear section organization"

    def test_uses_consistent_formatting(self, content):
        """Test that demo script uses consistent formatting"""
        # Assert
        has_headers = "## " in content
        has_code_blocks = "```" in content
        has_lists = "\n- " in content or "\n* " in content or "\n1. " in content

        assert has_headers and (has_code_blocks or has_lists), \
            "Demo script should use consistent markdown formatting"

    def test_has_multiple_sections(self, content):
        """Test that demo script is well-organized"""
        # Assert
        section_count = content.count("## ")
        assert section_count >= 4, \
            f"Demo script should have multiple sections, got {section_count}"

    def test_provides_urls_or_paths(self, content):
        """Test that demo script provides URLs or paths"""
        # Assert
        content_lower = content.lower()
        # Should mention URLs or file paths
        has_paths = any(term in content_lower for term in [
            "http://", "https://", "localhost", "/api/", "/docs/"
        ])
        assert has_paths, \
            "Demo script should provide URLs or paths for access"

    def test_includes_expected_outcomes(self, content):
        """Test that demo script includes expected outcomes"""
        # Assert
        content_lower = content.lower()
        # Should mention what to expect
        has_expectations = any(term in content_lower for term in [
            "should see", "expect", "will show", "displays", "response"
        ])
        assert has_expectations, \
            "Demo script should include expected outcomes for steps"
