"""
Test Deployment Guide Documentation

This module tests that the deployment guide provides comprehensive
instructions for deploying the application to different environments.

Test Coverage:
    - File existence and structure
    - Required sections present
    - Environment documentation
    - Deployment process documentation
    - Rollback procedures
    - Prerequisites and requirements
    - Best practices
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

class TestDeploymentGuideFileStructure:
    """Test deployment guide file structure"""

    def test_deployment_guide_file_exists(self):
        """Test that deployment.md file exists"""
        # Arrange
        project_root = Path(__file__).parent.parent
        deployment_file = project_root / "docs" / "deployment.md"

        # Act & Assert
        assert deployment_file.exists(), "deployment.md should exist in docs/"
        assert deployment_file.is_file(), "deployment.md should be a file"

    def test_deployment_guide_has_content(self):
        """Test that deployment.md has substantial content"""
        # Arrange
        project_root = Path(__file__).parent.parent
        deployment_file = project_root / "docs" / "deployment.md"

        # Act
        content = deployment_file.read_text()

        # Assert
        assert len(content) > 2000, \
            "Deployment guide should have substantial content (>2000 chars)"

    def test_deployment_guide_is_markdown(self):
        """Test that deployment guide uses markdown formatting"""
        # Arrange
        project_root = Path(__file__).parent.parent
        deployment_file = project_root / "docs" / "deployment.md"

        # Act
        content = deployment_file.read_text()

        # Assert
        assert "# " in content or "## " in content, \
            "Deployment guide should have markdown headers"


# =============================================================================
# Required Sections Tests
# =============================================================================

class TestDeploymentGuideRequiredSections:
    """Test that deployment guide has all required sections"""

    @pytest.fixture
    def content(self):
        """Load deployment guide content"""
        project_root = Path(__file__).parent.parent
        deployment_file = project_root / "docs" / "deployment.md"
        return deployment_file.read_text()

    def test_has_title(self, content):
        """Test that deployment guide has a title"""
        # Assert
        assert "# " in content, "Deployment guide should have a main title"

    def test_has_environments_section(self, content):
        """Test that deployment guide has environments section"""
        # Assert
        content_lower = content.lower()
        assert "environment" in content_lower, \
            "Deployment guide should have environments section"

    def test_has_deployment_process_section(self, content):
        """Test that deployment guide has deployment process section"""
        # Assert
        content_lower = content.lower()
        assert "deploy" in content_lower or "deployment" in content_lower, \
            "Deployment guide should have deployment process section"

    def test_has_rollback_section(self, content):
        """Test that deployment guide has rollback section"""
        # Assert
        content_lower = content.lower()
        assert "rollback" in content_lower, \
            "Deployment guide should have rollback section"

    def test_has_prerequisites_section(self, content):
        """Test that deployment guide has prerequisites section"""
        # Assert
        content_lower = content.lower()
        assert "prerequisite" in content_lower or "requirement" in content_lower, \
            "Deployment guide should have prerequisites section"


# =============================================================================
# Environment Documentation Tests
# =============================================================================

class TestDeploymentGuideEnvironments:
    """Test that deployment guide documents all environments"""

    @pytest.fixture
    def content(self):
        """Load deployment guide content"""
        project_root = Path(__file__).parent.parent
        deployment_file = project_root / "docs" / "deployment.md"
        return deployment_file.read_text()

    def test_documents_staging_environment(self, content):
        """Test that deployment guide documents staging environment"""
        # Assert
        content_lower = content.lower()
        assert "staging" in content_lower, \
            "Deployment guide should document staging environment"

    def test_documents_production_environment(self, content):
        """Test that deployment guide documents production environment"""
        # Assert
        content_lower = content.lower()
        assert "production" in content_lower, \
            "Deployment guide should document production environment"

    def test_documents_environment_variables(self, content):
        """Test that deployment guide documents environment variables"""
        # Assert
        content_lower = content.lower()
        assert "environment variable" in content_lower or "env" in content_lower, \
            "Deployment guide should document environment variables"

    def test_documents_aws_infrastructure(self, content):
        """Test that deployment guide documents AWS infrastructure"""
        # Assert
        content_lower = content.lower()
        assert "aws" in content_lower or "ecs" in content_lower or "ecr" in content_lower, \
            "Deployment guide should document AWS infrastructure"


# =============================================================================
# Deployment Process Tests
# =============================================================================

class TestDeploymentGuideProcess:
    """Test that deployment guide documents deployment process"""

    @pytest.fixture
    def content(self):
        """Load deployment guide content"""
        project_root = Path(__file__).parent.parent
        deployment_file = project_root / "docs" / "deployment.md"
        return deployment_file.read_text()

    def test_documents_github_actions(self, content):
        """Test that deployment guide documents GitHub Actions"""
        # Assert
        content_lower = content.lower()
        assert "github actions" in content_lower or "workflow" in content_lower, \
            "Deployment guide should document GitHub Actions"

    def test_documents_docker_images(self, content):
        """Test that deployment guide documents Docker images"""
        # Assert
        content_lower = content.lower()
        assert "docker" in content_lower, \
            "Deployment guide should document Docker images"

    def test_documents_database_migrations(self, content):
        """Test that deployment guide documents database migrations"""
        # Assert
        content_lower = content.lower()
        assert "migration" in content_lower or "alembic" in content_lower, \
            "Deployment guide should document database migrations"

    def test_documents_health_checks(self, content):
        """Test that deployment guide documents health checks"""
        # Assert
        content_lower = content.lower()
        assert "health" in content_lower or "health check" in content_lower, \
            "Deployment guide should document health checks"

    def test_documents_manual_deployment(self, content):
        """Test that deployment guide documents manual deployment"""
        # Assert
        content_lower = content.lower()
        assert "manual" in content_lower or "workflow_dispatch" in content_lower, \
            "Deployment guide should document manual deployment process"


# =============================================================================
# Rollback Documentation Tests
# =============================================================================

class TestDeploymentGuideRollback:
    """Test that deployment guide documents rollback procedures"""

    @pytest.fixture
    def content(self):
        """Load deployment guide content"""
        project_root = Path(__file__).parent.parent
        deployment_file = project_root / "docs" / "deployment.md"
        return deployment_file.read_text()

    def test_documents_rollback_procedure(self, content):
        """Test that deployment guide documents rollback procedure"""
        # Assert
        content_lower = content.lower()
        assert "rollback" in content_lower, \
            "Deployment guide should document rollback procedure"

    def test_documents_backup_strategy(self, content):
        """Test that deployment guide documents backup strategy"""
        # Assert
        content_lower = content.lower()
        assert "backup" in content_lower or "previous version" in content_lower, \
            "Deployment guide should document backup strategy"

    def test_documents_recovery_steps(self, content):
        """Test that deployment guide documents recovery steps"""
        # Assert
        content_lower = content.lower()
        # Should mention recovery or restoration
        has_recovery = "recovery" in content_lower or "restore" in content_lower or "revert" in content_lower
        assert has_recovery, \
            "Deployment guide should document recovery/restoration steps"


# =============================================================================
# Prerequisites Tests
# =============================================================================

class TestDeploymentGuidePrerequisites:
    """Test that deployment guide documents prerequisites"""

    @pytest.fixture
    def content(self):
        """Load deployment guide content"""
        project_root = Path(__file__).parent.parent
        deployment_file = project_root / "docs" / "deployment.md"
        return deployment_file.read_text()

    def test_documents_aws_credentials(self, content):
        """Test that deployment guide documents AWS credentials"""
        # Assert
        content_lower = content.lower()
        assert "credential" in content_lower or "access" in content_lower, \
            "Deployment guide should document AWS credentials"

    def test_documents_required_permissions(self, content):
        """Test that deployment guide documents required permissions"""
        # Assert
        content_lower = content.lower()
        assert "permission" in content_lower or "role" in content_lower, \
            "Deployment guide should document required permissions"


# =============================================================================
# Code Examples Tests
# =============================================================================

class TestDeploymentGuideCodeExamples:
    """Test that deployment guide includes code examples"""

    @pytest.fixture
    def content(self):
        """Load deployment guide content"""
        project_root = Path(__file__).parent.parent
        deployment_file = project_root / "docs" / "deployment.md"
        return deployment_file.read_text()

    def test_has_code_blocks(self, content):
        """Test that deployment guide has code blocks"""
        # Assert
        assert "```" in content, \
            "Deployment guide should have code blocks (markdown ```)"

    def test_has_command_examples(self, content):
        """Test that deployment guide has command examples"""
        # Assert
        content_lower = content.lower()
        # Should have some CLI commands
        has_commands = "```bash" in content_lower or "```sh" in content_lower
        assert has_commands, \
            "Deployment guide should have command examples"

    def test_has_multiple_code_examples(self, content):
        """Test that deployment guide has multiple code examples"""
        # Assert
        code_block_count = content.count("```")
        assert code_block_count >= 6, \
            f"Deployment guide should have at least 3 code blocks (pairs), got {code_block_count // 2}"


# =============================================================================
# Best Practices Tests
# =============================================================================

class TestDeploymentGuideBestPractices:
    """Test that deployment guide follows documentation best practices"""

    @pytest.fixture
    def content(self):
        """Load deployment guide content"""
        project_root = Path(__file__).parent.parent
        deployment_file = project_root / "docs" / "deployment.md"
        return deployment_file.read_text()

    def test_has_table_of_contents(self, content):
        """Test that deployment guide has table of contents"""
        # Assert
        content_lower = content.lower()
        has_toc = "table of contents" in content_lower or "## " in content
        assert has_toc, \
            "Deployment guide should have table of contents or clear organization"

    def test_uses_consistent_formatting(self, content):
        """Test that deployment guide uses consistent formatting"""
        # Assert
        has_headers = "## " in content
        has_code_blocks = "```" in content
        has_lists = "\n- " in content or "\n* " in content or "\n1. " in content

        assert has_headers and has_code_blocks and has_lists, \
            "Deployment guide should use consistent markdown formatting"

    def test_has_multiple_sections(self, content):
        """Test that deployment guide is well-organized"""
        # Assert
        section_count = content.count("## ")
        assert section_count >= 5, \
            f"Deployment guide should have multiple sections, got {section_count}"

    def test_documents_monitoring(self, content):
        """Test that deployment guide mentions monitoring"""
        # Assert
        content_lower = content.lower()
        has_monitoring = "monitor" in content_lower or "log" in content_lower or "observability" in content_lower
        assert has_monitoring, \
            "Deployment guide should mention monitoring or logging"

    def test_documents_troubleshooting(self, content):
        """Test that deployment guide includes troubleshooting"""
        # Assert
        content_lower = content.lower()
        has_troubleshooting = "troubleshoot" in content_lower or "common issue" in content_lower or "problem" in content_lower
        assert has_troubleshooting, \
            "Deployment guide should include troubleshooting information"
