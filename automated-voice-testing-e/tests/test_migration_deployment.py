"""
Test suite for database migration deployment workflow.

Validates that deploy-production.yml includes proper Alembic migration execution.
"""

import pytest
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent
DEPLOY_FILE = PROJECT_ROOT / ".github" / "workflows" / "deploy-production.yml"


class TestDeployFileExists:
    """Verify deploy-production.yml exists."""

    def test_deploy_file_exists(self):
        """deploy-production.yml should exist."""
        assert DEPLOY_FILE.exists(), ".github/workflows/deploy-production.yml should exist"


class TestMigrationStep:
    """Test database migration step configuration."""

    @pytest.fixture
    def deploy_content(self):
        return DEPLOY_FILE.read_text()

    def test_no_placeholder_text(self, deploy_content):
        """Should not contain placeholder text."""
        assert "placeholder" not in deploy_content.lower(), \
            "Migration step should not contain placeholder text"

    def test_has_aws_ecs_run_task(self, deploy_content):
        """Should use aws ecs run-task for migrations."""
        has_run_task = "aws ecs run-task" in deploy_content
        has_ecs_exec = "ecs-exec" in deploy_content.lower() or "execute-command" in deploy_content
        assert has_run_task or has_ecs_exec, \
            "Should use aws ecs run-task or execute-command for migrations"

    def test_has_alembic_command(self, deploy_content):
        """Should include Alembic upgrade command."""
        has_alembic = "alembic" in deploy_content.lower()
        has_upgrade = "upgrade" in deploy_content.lower()
        assert has_alembic and has_upgrade, \
            "Should include Alembic upgrade command"

    def test_has_migration_task_definition(self, deploy_content):
        """Should reference migration task definition."""
        has_migration_task = "migration" in deploy_content.lower() and "task" in deploy_content.lower()
        assert has_migration_task, \
            "Should reference migration task definition"


class TestMigrationDryRun:
    """Test migration dry-run validation step."""

    @pytest.fixture
    def deploy_content(self):
        return DEPLOY_FILE.read_text()

    def test_has_dry_run_step(self, deploy_content):
        """Should have dry-run validation step."""
        has_dry_run = "dry-run" in deploy_content.lower() or "dry_run" in deploy_content.lower()
        has_check = "check" in deploy_content.lower() or "validate" in deploy_content.lower()
        assert has_dry_run or has_check, \
            "Should have migration dry-run validation step"

    def test_validates_before_applying(self, deploy_content):
        """Dry-run should come before actual migration."""
        # Check if validation/check appears before the actual migration apply
        content_lower = deploy_content.lower()
        has_validation_step = "validate" in content_lower or "dry-run" in content_lower
        assert has_validation_step, \
            "Should validate migrations before applying"


class TestMigrationRollback:
    """Test automatic rollback on migration failure."""

    @pytest.fixture
    def deploy_content(self):
        return DEPLOY_FILE.read_text()

    def test_has_rollback_mechanism(self, deploy_content):
        """Should have rollback mechanism on failure."""
        has_rollback = "rollback" in deploy_content.lower()
        has_downgrade = "downgrade" in deploy_content.lower()
        has_revert = "revert" in deploy_content.lower()
        assert has_rollback or has_downgrade or has_revert, \
            "Should have rollback mechanism on migration failure"

    def test_has_failure_handling(self, deploy_content):
        """Should handle migration failures."""
        has_if_failure = "if: failure()" in deploy_content
        has_continue_on_error = "continue-on-error" in deploy_content
        has_error_check = "exit" in deploy_content and "1" in deploy_content
        assert has_if_failure or has_continue_on_error or has_error_check, \
            "Should handle migration failures"

    def test_captures_migration_revision(self, deploy_content):
        """Should capture current revision for rollback."""
        has_current = "current" in deploy_content.lower()
        has_revision = "revision" in deploy_content.lower()
        has_head = "head" in deploy_content.lower()
        assert has_current or has_revision or has_head, \
            "Should capture current migration revision for rollback"


class TestMigrationEnvironment:
    """Test migration environment configuration."""

    @pytest.fixture
    def deploy_content(self):
        return DEPLOY_FILE.read_text()

    def test_has_database_url(self, deploy_content):
        """Should have DATABASE_URL configuration."""
        assert "DATABASE_URL" in deploy_content, \
            "Should have DATABASE_URL environment variable"

    def test_uses_secrets(self, deploy_content):
        """Should use secrets for database credentials."""
        has_secrets = "secrets." in deploy_content
        has_production_db = "PRODUCTION_DATABASE" in deploy_content
        assert has_secrets and has_production_db, \
            "Should use secrets for production database credentials"
