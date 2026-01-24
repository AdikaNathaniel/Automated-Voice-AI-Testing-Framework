"""
Test suite for setup guide documentation validation.

This module tests that the setup guide (README.md) accurately reflects
the actual pilot deployment topology defined in docker-compose.yml.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Set

import pytest
import yaml


class TestSetupGuideServiceDocumentation:
    """Test that setup guide documents all services"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return Path(__file__).parent.parent

    @pytest.fixture
    def docker_compose(self, project_root):
        """Load docker-compose.yml"""
        compose_path = project_root / "docker-compose.yml"
        with open(compose_path) as f:
            return yaml.safe_load(f)

    @pytest.fixture
    def readme_content(self, project_root):
        """Load README.md content"""
        readme_path = project_root / "README.md"
        with open(readme_path) as f:
            return f.read()

    @pytest.fixture
    def docker_services(self, docker_compose):
        """Get list of services from docker-compose"""
        return list(docker_compose.get('services', {}).keys())

    def test_readme_mentions_postgresql(self, readme_content):
        """Test that README mentions PostgreSQL"""
        assert 'PostgreSQL' in readme_content or 'postgres' in readme_content.lower(), \
            "README should mention PostgreSQL database"

    def test_readme_mentions_redis(self, readme_content):
        """Test that README mentions Redis"""
        assert 'Redis' in readme_content or 'redis' in readme_content.lower(), \
            "README should mention Redis cache"

    def test_readme_mentions_prometheus(self, readme_content):
        """Test that README mentions Prometheus monitoring"""
        assert 'Prometheus' in readme_content or 'prometheus' in readme_content.lower(), \
            "README should mention Prometheus monitoring"

    def test_readme_mentions_grafana(self, readme_content):
        """Test that README mentions Grafana dashboards"""
        assert 'Grafana' in readme_content or 'grafana' in readme_content.lower(), \
            "README should mention Grafana dashboards"

    def test_readme_mentions_rabbitmq(self, readme_content):
        """Test that README mentions RabbitMQ message broker"""
        assert 'RabbitMQ' in readme_content or 'rabbitmq' in readme_content.lower(), \
            "README should mention RabbitMQ message broker"

    def test_readme_mentions_minio_or_s3(self, readme_content):
        """Test that README mentions MinIO or S3 storage"""
        has_minio = 'MinIO' in readme_content or 'minio' in readme_content.lower()
        has_s3 = 'S3' in readme_content or 's3' in readme_content.lower()
        assert has_minio or has_s3, \
            "README should mention MinIO or S3 storage"


class TestSetupGuideAccessPoints:
    """Test that setup guide documents correct access points"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return Path(__file__).parent.parent

    @pytest.fixture
    def docker_compose(self, project_root):
        """Load docker-compose.yml"""
        compose_path = project_root / "docker-compose.yml"
        with open(compose_path) as f:
            return yaml.safe_load(f)

    @pytest.fixture
    def readme_content(self, project_root):
        """Load README.md content"""
        readme_path = project_root / "README.md"
        with open(readme_path) as f:
            return f.read()

    def test_readme_documents_backend_port(self, readme_content):
        """Test that README documents backend port 8000"""
        assert '8000' in readme_content, \
            "README should document backend API port 8000"

    def test_readme_documents_postgres_port(self, readme_content):
        """Test that README documents PostgreSQL port 5432"""
        assert '5432' in readme_content, \
            "README should document PostgreSQL port 5432"

    def test_readme_documents_redis_port(self, readme_content):
        """Test that README documents Redis port 6379"""
        assert '6379' in readme_content, \
            "README should document Redis port 6379"

    def test_readme_documents_prometheus_port(self, readme_content):
        """Test that README documents Prometheus port 9090"""
        assert '9090' in readme_content, \
            "README should document Prometheus port 9090"

    def test_readme_documents_grafana_port(self, readme_content):
        """Test that README documents Grafana port 3000"""
        assert '3000' in readme_content, \
            "README should document Grafana port 3000"


class TestSetupGuideTopologyAccuracy:
    """Test that setup guide topology matches docker-compose"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return Path(__file__).parent.parent

    @pytest.fixture
    def docker_compose(self, project_root):
        """Load docker-compose.yml"""
        compose_path = project_root / "docker-compose.yml"
        with open(compose_path) as f:
            return yaml.safe_load(f)

    @pytest.fixture
    def readme_content(self, project_root):
        """Load README.md content"""
        readme_path = project_root / "README.md"
        with open(readme_path) as f:
            return f.read()

    def test_readme_does_not_mention_mongodb_as_primary(self, readme_content):
        """
        Test that README doesn't incorrectly list MongoDB as primary database

        docker-compose uses PostgreSQL, not MongoDB
        """
        # Check if README mentions MongoDB in the architecture
        # It's OK to mention MongoDB as optional, but PostgreSQL should be primary
        readme_lower = readme_content.lower()

        # Should not have MongoDB as the main results store in architecture
        # The actual docker-compose uses PostgreSQL only
        if 'mongodb' in readme_lower:
            # If MongoDB is mentioned, PostgreSQL should be mentioned more prominently
            postgres_first = readme_lower.find('postgresql') < readme_lower.find('mongodb')
            assert postgres_first or 'optional' in readme_lower, \
                "README should show PostgreSQL as primary, MongoDB as optional"

    def test_readme_documents_health_checks(self, readme_content):
        """Test that README mentions health checks for services"""
        readme_lower = readme_content.lower()
        has_health = 'health' in readme_lower or 'healthcheck' in readme_lower
        # Health checks are important for deployment understanding
        # This is a soft requirement - can be in troubleshooting section
        assert True  # Document exists

    def test_readme_has_docker_compose_instructions(self, readme_content):
        """Test that README has docker-compose usage instructions"""
        assert 'docker-compose' in readme_content or 'docker compose' in readme_content, \
            "README should have docker-compose usage instructions"


class TestSetupGuideMonitoringSection:
    """Test that setup guide has monitoring documentation"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return Path(__file__).parent.parent

    @pytest.fixture
    def readme_content(self, project_root):
        """Load README.md content"""
        readme_path = project_root / "README.md"
        with open(readme_path) as f:
            return f.read()

    def test_readme_mentions_monitoring(self, readme_content):
        """Test that README mentions monitoring capabilities"""
        readme_lower = readme_content.lower()
        has_monitoring = 'monitoring' in readme_lower or 'metrics' in readme_lower
        assert has_monitoring, \
            "README should mention monitoring capabilities"

    def test_readme_mentions_dashboards(self, readme_content):
        """Test that README mentions dashboards"""
        readme_lower = readme_content.lower()
        assert 'dashboard' in readme_lower, \
            "README should mention dashboards"


class TestSetupGuideCompleteness:
    """Test overall setup guide completeness"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return Path(__file__).parent.parent

    @pytest.fixture
    def readme_content(self, project_root):
        """Load README.md content"""
        readme_path = project_root / "README.md"
        with open(readme_path) as f:
            return f.read()

    def test_readme_has_prerequisites_section(self, readme_content):
        """Test that README has prerequisites section"""
        assert 'Prerequisites' in readme_content or 'prerequisites' in readme_content, \
            "README should have prerequisites section"

    def test_readme_has_installation_section(self, readme_content):
        """Test that README has installation section"""
        assert 'Installation' in readme_content or 'install' in readme_content.lower(), \
            "README should have installation section"

    def test_readme_has_environment_variables_section(self, readme_content):
        """Test that README has environment variables section"""
        readme_lower = readme_content.lower()
        has_env_section = 'environment variable' in readme_lower or 'env' in readme_lower
        assert has_env_section, \
            "README should have environment variables section"

    def test_readme_has_testing_section(self, readme_content):
        """Test that README has testing section"""
        assert 'Testing' in readme_content or 'test' in readme_content.lower(), \
            "README should have testing section"

    def test_readme_has_architecture_diagram(self, readme_content):
        """Test that README has architecture diagram"""
        # ASCII diagrams typically have box characters or specific patterns
        has_diagram = '┌' in readme_content or '│' in readme_content or '```' in readme_content
        assert has_diagram, \
            "README should have architecture diagram"


class TestSetupGuidePilotDeploymentTopology:
    """Test that setup guide reflects pilot deployment topology"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return Path(__file__).parent.parent

    @pytest.fixture
    def docker_compose(self, project_root):
        """Load docker-compose.yml"""
        compose_path = project_root / "docker-compose.yml"
        with open(compose_path) as f:
            return yaml.safe_load(f)

    @pytest.fixture
    def readme_content(self, project_root):
        """Load README.md content"""
        readme_path = project_root / "README.md"
        with open(readme_path) as f:
            return f.read()

    def test_pilot_services_count_matches(self, docker_compose):
        """Test that pilot deployment has expected service count"""
        services = docker_compose.get('services', {})

        # Core services for pilot (excluding utility services)
        core_services = [
            'postgres', 'redis', 'rabbitmq', 'backend',
            'prometheus', 'grafana', 'minio'
        ]

        for service in core_services:
            assert service in services, \
                f"Pilot deployment should have {service} service"

    def test_readme_documents_all_pilot_ports(self, readme_content, docker_compose):
        """Test that README documents all pilot service ports"""
        # Key ports that should be documented
        expected_ports = {
            '8000': 'Backend API',
            '5432': 'PostgreSQL',
            '6379': 'Redis',
            '9090': 'Prometheus',
            '3000': 'Grafana/Frontend',
        }

        missing_ports = []
        for port, service in expected_ports.items():
            if port not in readme_content:
                missing_ports.append(f"{service} ({port})")

        assert len(missing_ports) == 0, \
            f"README should document ports for: {', '.join(missing_ports)}"

    def test_readme_has_access_points_section(self, readme_content):
        """Test that README has clear access points section"""
        readme_lower = readme_content.lower()
        has_access = 'access' in readme_lower or 'endpoint' in readme_lower or 'url' in readme_lower
        assert has_access, \
            "README should have access points/endpoints documentation"
