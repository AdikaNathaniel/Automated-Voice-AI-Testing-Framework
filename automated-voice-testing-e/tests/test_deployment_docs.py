"""
Tests for deployment documentation (Phase 5.3 Operational Documentation).
"""

import os
import pytest


@pytest.fixture
def docs_dir():
    """Get docs directory path."""
    project_root = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(project_root, "docs")


@pytest.fixture
def deployment_md_path(docs_dir):
    """Get path to DEPLOYMENT.md."""
    return os.path.join(docs_dir, "DEPLOYMENT.md")


@pytest.fixture
def deployment_content(deployment_md_path):
    """Read DEPLOYMENT.md content."""
    with open(deployment_md_path) as f:
        return f.read()


class TestDeploymentDocumentationExists:
    """Test that deployment documentation file exists."""

    def test_deployment_md_exists(self, deployment_md_path):
        """Test that DEPLOYMENT.md exists."""
        assert os.path.exists(deployment_md_path), \
            "docs/DEPLOYMENT.md should exist"


class TestEnvironmentSetupGuide:
    """Test environment setup documentation."""

    def test_has_prerequisites_section(self, deployment_content):
        """Test that prerequisites are documented."""
        assert "prerequisites" in deployment_content.lower(), \
            "Should document prerequisites"

    def test_has_docker_requirements(self, deployment_content):
        """Test that Docker requirements are documented."""
        assert "docker" in deployment_content.lower(), \
            "Should document Docker requirements"

    def test_has_python_requirements(self, deployment_content):
        """Test that Python requirements are documented."""
        assert "python" in deployment_content.lower(), \
            "Should document Python requirements"

    def test_has_installation_steps(self, deployment_content):
        """Test that installation steps are documented."""
        has_steps = (
            "install" in deployment_content.lower() or
            "setup" in deployment_content.lower()
        )
        assert has_steps, "Should have installation/setup steps"


class TestConfigurationReference:
    """Test configuration reference documentation."""

    def test_has_environment_variables_section(self, deployment_content):
        """Test that environment variables are documented."""
        has_env_vars = (
            "environment variable" in deployment_content.lower() or
            "env var" in deployment_content.lower() or
            ".env" in deployment_content
        )
        assert has_env_vars, "Should document environment variables"

    def test_documents_database_url(self, deployment_content):
        """Test that DATABASE_URL is documented."""
        assert "DATABASE_URL" in deployment_content, \
            "Should document DATABASE_URL"

    def test_documents_redis_url(self, deployment_content):
        """Test that REDIS_URL is documented."""
        assert "REDIS_URL" in deployment_content, \
            "Should document REDIS_URL"

    def test_documents_jwt_secret(self, deployment_content):
        """Test that JWT_SECRET is documented."""
        has_jwt = (
            "JWT_SECRET" in deployment_content or
            "SECRET_KEY" in deployment_content
        )
        assert has_jwt, "Should document JWT secret configuration"

    def test_documents_environment_setting(self, deployment_content):
        """Test that ENVIRONMENT setting is documented."""
        assert "ENVIRONMENT" in deployment_content, \
            "Should document ENVIRONMENT setting"


class TestHealthCheckEndpoints:
    """Test health check endpoint documentation."""

    def test_has_health_check_section(self, deployment_content):
        """Test that health checks are documented."""
        assert "health" in deployment_content.lower(), \
            "Should document health checks"

    def test_documents_health_endpoint(self, deployment_content):
        """Test that /health endpoint is documented."""
        has_health_endpoint = (
            "/health" in deployment_content or
            "health endpoint" in deployment_content.lower()
        )
        assert has_health_endpoint, "Should document health endpoint"

    def test_documents_readiness_check(self, deployment_content):
        """Test that readiness checks are documented."""
        has_readiness = (
            "readiness" in deployment_content.lower() or
            "/ready" in deployment_content or
            "ready endpoint" in deployment_content.lower()
        )
        assert has_readiness, "Should document readiness checks"


class TestMonitoringSetup:
    """Test monitoring setup documentation."""

    def test_has_monitoring_section(self, deployment_content):
        """Test that monitoring is documented."""
        assert "monitor" in deployment_content.lower(), \
            "Should have monitoring section"

    def test_documents_prometheus(self, deployment_content):
        """Test that Prometheus is documented."""
        assert "prometheus" in deployment_content.lower(), \
            "Should document Prometheus"

    def test_documents_grafana(self, deployment_content):
        """Test that Grafana is documented."""
        assert "grafana" in deployment_content.lower(), \
            "Should document Grafana"

    def test_documents_alertmanager(self, deployment_content):
        """Test that Alertmanager is documented."""
        assert "alertmanager" in deployment_content.lower(), \
            "Should document Alertmanager"

    def test_documents_metrics_endpoint(self, deployment_content):
        """Test that metrics endpoint is documented."""
        has_metrics = (
            "/metrics" in deployment_content or
            "metrics endpoint" in deployment_content.lower()
        )
        assert has_metrics, "Should document metrics endpoint"


class TestDeploymentEnvironments:
    """Test deployment environment documentation."""

    def test_documents_development_setup(self, deployment_content):
        """Test that development setup is documented."""
        has_dev = (
            "development" in deployment_content.lower() or
            "local" in deployment_content.lower()
        )
        assert has_dev, "Should document development setup"

    def test_documents_staging_environment(self, deployment_content):
        """Test that staging environment is documented."""
        assert "staging" in deployment_content.lower(), \
            "Should document staging environment"

    def test_documents_production_environment(self, deployment_content):
        """Test that production environment is documented."""
        assert "production" in deployment_content.lower(), \
            "Should document production environment"


class TestDeploymentProcedures:
    """Test deployment procedure documentation."""

    def test_has_deployment_steps(self, deployment_content):
        """Test that deployment steps are documented."""
        has_steps = (
            "deploy" in deployment_content.lower() and
            ("step" in deployment_content.lower() or
             "1." in deployment_content or
             "- " in deployment_content)
        )
        assert has_steps, "Should have deployment steps"

    def test_documents_database_migrations(self, deployment_content):
        """Test that database migrations are documented."""
        has_migrations = (
            "migration" in deployment_content.lower() or
            "alembic" in deployment_content.lower()
        )
        assert has_migrations, "Should document database migrations"

    def test_documents_rollback_procedure(self, deployment_content):
        """Test that rollback procedure is documented."""
        assert "rollback" in deployment_content.lower(), \
            "Should document rollback procedure"
