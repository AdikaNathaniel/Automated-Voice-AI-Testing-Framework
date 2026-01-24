"""
Tests for CI/CD security configuration (Phase 4.4 CI/CD Improvements).
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
def deploy_production_workflow(workflows_dir):
    """Load deploy-production.yml."""
    with open(os.path.join(workflows_dir, "deploy-production.yml")) as f:
        return yaml.safe_load(f)


@pytest.fixture
def backend_ci_workflow(workflows_dir):
    """Load backend-ci.yml."""
    workflow_path = os.path.join(workflows_dir, "backend-ci.yml")
    if os.path.exists(workflow_path):
        with open(workflow_path) as f:
            return yaml.safe_load(f)
    return None


class TestSecretsUsage:
    """Test that workflows use GitHub Secrets properly."""

    def test_no_hardcoded_credentials(self, workflows_dir):
        """Test that workflows don't have hardcoded credentials."""
        sensitive_patterns = [
            "password=",
            "secret=",
            "api_key=",
            "token=",
            "AWS_ACCESS_KEY_ID=",
            "AWS_SECRET_ACCESS_KEY=",
        ]

        for workflow_file in os.listdir(workflows_dir):
            if workflow_file.endswith(".yml"):
                with open(os.path.join(workflows_dir, workflow_file)) as f:
                    content = f.read().lower()

                for pattern in sensitive_patterns:
                    # Skip if it's referencing secrets
                    if pattern.lower() in content:
                        # Make sure it's using secrets syntax
                        lines = content.split('\n')
                        for line in lines:
                            if pattern.lower() in line and '${{ secrets.' not in line and '${' not in line:
                                # Allow env var references and secrets
                                if not any(safe in line for safe in ['secrets.', '${', '$(']):
                                    # Skip comments
                                    if not line.strip().startswith('#'):
                                        assert False, \
                                            f"Potential hardcoded credential in {workflow_file}: {pattern}"

    def test_production_uses_secrets(self, deploy_production_workflow):
        """Test that production deployment uses secrets for sensitive data."""
        workflow_str = yaml.dump(deploy_production_workflow)

        # These should be from secrets
        assert "secrets.AWS_ROLE_TO_ASSUME_PRODUCTION" in workflow_str
        assert "secrets.PRODUCTION_DATABASE_URL" in workflow_str


class TestSecretValidation:
    """Test secret validation before deployment."""

    def test_production_has_secret_validation(self, deploy_production_workflow):
        """Test that production deployment validates secrets before proceeding."""
        jobs = deploy_production_workflow.get("jobs", {})
        deploy_job = jobs.get("deploy", {})
        steps = deploy_job.get("steps", [])

        # Look for secret validation step
        step_names = [s.get("name", "").lower() for s in steps]

        has_validation = any(
            "secret" in name and "valid" in name
            for name in step_names
        )
        assert has_validation, "Production workflow must have secret validation step"


class TestAutomaticRollback:
    """Test automatic rollback on health check failure."""

    def test_production_has_rollback_on_health_failure(self, deploy_production_workflow):
        """Test that deployment has rollback step on health check failure."""
        jobs = deploy_production_workflow.get("jobs", {})
        deploy_job = jobs.get("deploy", {})
        steps = deploy_job.get("steps", [])

        # Look for rollback step
        rollback_step = None
        for step in steps:
            name = step.get("name", "").lower()
            if "rollback" in name and ("health" in name or "deployment" in name):
                rollback_step = step
                break

        assert rollback_step is not None, \
            "Production workflow must have automatic rollback on health check failure"

        # Check that rollback runs on failure
        condition = rollback_step.get("if", "")
        assert "failure()" in condition, \
            "Rollback step must run on failure condition"


class TestCoverageEnforcement:
    """Test coverage enforcement in CI."""

    def test_backend_ci_has_coverage(self, backend_ci_workflow):
        """Test that backend CI runs coverage."""
        if backend_ci_workflow is None:
            pytest.skip("backend-ci.yml not found")

        workflow_str = yaml.dump(backend_ci_workflow)

        has_coverage = "coverage" in workflow_str.lower() or "--cov" in workflow_str
        assert has_coverage, "Backend CI must include coverage reporting"


class TestEnvironmentProtection:
    """Test environment protection settings."""

    def test_production_has_environment(self, deploy_production_workflow):
        """Test that production deployment specifies environment."""
        jobs = deploy_production_workflow.get("jobs", {})
        deploy_job = jobs.get("deploy", {})

        environment = deploy_job.get("environment", {})
        if isinstance(environment, str):
            env_name = environment
        else:
            env_name = environment.get("name", "")

        assert env_name == "production", \
            "Production deployment must specify production environment"
