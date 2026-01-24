"""
Tests for migration testing workflow (Phase 4.4 CI/CD Improvements).
"""

import os
import yaml
import pytest


@pytest.fixture
def workflows_dir():
    """Get path to workflows directory."""
    project_root = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(project_root, ".github", "workflows")


@pytest.fixture
def deploy_staging_workflow(workflows_dir):
    """Load deploy-staging.yml if it exists."""
    workflow_path = os.path.join(workflows_dir, "deploy-staging.yml")
    if os.path.exists(workflow_path):
        with open(workflow_path) as f:
            return yaml.safe_load(f)
    return None


@pytest.fixture
def migration_test_script():
    """Get path to migration test script."""
    project_root = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(project_root, "scripts", "test_migrations.sh")


class TestMigrationTestScript:
    """Test migration test script configuration."""

    def test_migration_test_script_exists(self, migration_test_script):
        """Test that migration test script exists."""
        assert os.path.exists(migration_test_script), \
            f"Migration test script not found at {migration_test_script}"

    def test_migration_test_script_executable(self, migration_test_script):
        """Test that migration test script is executable."""
        assert os.access(migration_test_script, os.X_OK), \
            "Migration test script must be executable"

    def test_migration_test_has_upgrade_downgrade_cycle(self, migration_test_script):
        """Test that script tests upgrade -> downgrade -> upgrade cycle."""
        with open(migration_test_script) as f:
            content = f.read()

        # Should have upgrade command
        has_upgrade = "alembic upgrade" in content
        # Should have downgrade command
        has_downgrade = "alembic downgrade" in content

        assert has_upgrade, "Migration test must include upgrade step"
        assert has_downgrade, "Migration test must include downgrade step"

    def test_migration_test_validates_reversibility(self, migration_test_script):
        """Test that script validates migrations are reversible."""
        with open(migration_test_script) as f:
            content = f.read()

        # Should check downgrade works
        has_validation = (
            "downgrade -1" in content or
            "downgrade base" in content or
            "reversible" in content.lower()
        )
        assert has_validation, "Migration test must validate reversibility"


class TestStagingMigrationDryRun:
    """Test staging workflow has migration dry-run."""

    def test_staging_has_migration_check(self, deploy_staging_workflow):
        """Test that staging deployment has migration dry-run."""
        if deploy_staging_workflow is None:
            pytest.skip("deploy-staging.yml not found")

        workflow_str = yaml.dump(deploy_staging_workflow)

        # Should have migration check/validation
        has_check = (
            "alembic check" in workflow_str or
            "migration dry-run" in workflow_str.lower() or
            "migration-check" in workflow_str
        )

        assert has_check, "Staging workflow should have migration dry-run validation"
