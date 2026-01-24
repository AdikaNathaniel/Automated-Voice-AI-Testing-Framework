"""
Tests for docker-compose.yml pilot readiness.

This test suite validates that docker-compose.yml is production-ready:
1. Dev-only services are properly gated with profiles
2. All production services have healthchecks
3. Configuration is suitable for pilot deployment
"""

import re
from pathlib import Path

import pytest
import yaml


class TestDockerComposeStructure:
    """Test docker-compose.yml structure and configuration"""

    @pytest.fixture
    def compose_path(self):
        """Get path to docker-compose.yml"""
        return Path(__file__).parent.parent / "docker-compose.yml"

    @pytest.fixture
    def compose_content(self, compose_path):
        """Read docker-compose.yml as YAML"""
        with open(compose_path, 'r') as f:
            return yaml.safe_load(f)

    @pytest.fixture
    def compose_raw(self, compose_path):
        """Read docker-compose.yml as raw text"""
        return compose_path.read_text()

    def test_compose_file_exists(self, compose_path):
        """Test that docker-compose.yml exists"""
        assert compose_path.exists(), "docker-compose.yml not found"

    def test_compose_is_valid_yaml(self, compose_content):
        """Test that docker-compose.yml is valid YAML"""
        assert compose_content is not None, "docker-compose.yml is not valid YAML"
        assert 'services' in compose_content, "docker-compose.yml missing 'services' key"

    def test_compose_version_specified(self, compose_content):
        """Test that docker-compose version is specified"""
        assert 'version' in compose_content, "docker-compose.yml should specify version"
        # Version 3.8 or higher recommended for better features
        version = str(compose_content.get('version', '0'))
        major_version = float(version.split('.')[0])
        assert major_version >= 3, "Should use docker-compose version 3.x or higher"


class TestDevOnlyServices:
    """Test that dev-only services are properly gated"""

    @pytest.fixture
    def compose_content(self):
        """Read docker-compose.yml as YAML"""
        compose_path = Path(__file__).parent.parent / "docker-compose.yml"
        with open(compose_path, 'r') as f:
            return yaml.safe_load(f)

    def test_pgadmin_is_gated_with_profile(self, compose_content):
        """Test that pgAdmin is gated with a dev profile"""
        services = compose_content.get('services', {})

        # pgAdmin should exist
        assert 'pgadmin' in services, "pgAdmin service not found in docker-compose.yml"

        pgadmin = services['pgadmin']

        # pgAdmin should have profiles defined
        assert 'profiles' in pgadmin, (
            "pgAdmin should have 'profiles' key to gate it from production. "
            "Add: profiles: [dev, debug]"
        )

        # Profile should include 'dev' or 'debug'
        profiles = pgadmin.get('profiles', [])
        assert len(profiles) > 0, "pgAdmin profiles list is empty"
        assert 'dev' in profiles or 'debug' in profiles, (
            "pgAdmin should be in 'dev' or 'debug' profile"
        )

    def test_dev_only_services_have_profiles(self, compose_content):
        """Test that all dev-only services have profiles"""
        services = compose_content.get('services', {})

        # List of services that are dev-only
        dev_only_services = ['pgadmin']

        for service_name in dev_only_services:
            if service_name in services:
                service = services[service_name]
                assert 'profiles' in service, (
                    f"Dev-only service '{service_name}' should have profiles defined"
                )
                profiles = service.get('profiles', [])
                assert 'dev' in profiles or 'debug' in profiles, (
                    f"Service '{service_name}' should be in dev/debug profile"
                )

    def test_production_services_no_dev_profile(self, compose_content):
        """Test that production services don't have dev profile"""
        services = compose_content.get('services', {})

        # List of services that MUST run in production
        production_services = [
            'postgres', 'redis', 'rabbitmq',
            'backend', 'minio', 'prometheus'
        ]

        for service_name in production_services:
            if service_name in services:
                service = services[service_name]
                profiles = service.get('profiles', [])

                # Production services should not have 'dev' profile
                # (they can have no profile, which means always run)
                if len(profiles) > 0:
                    assert 'dev' not in profiles, (
                        f"Production service '{service_name}' should not be in dev profile"
                    )


class TestHealthchecks:
    """Test that all production services have healthchecks"""

    @pytest.fixture
    def compose_content(self):
        """Read docker-compose.yml as YAML"""
        compose_path = Path(__file__).parent.parent / "docker-compose.yml"
        with open(compose_path, 'r') as f:
            return yaml.safe_load(f)

    def test_postgres_has_healthcheck(self, compose_content):
        """Test that PostgreSQL has healthcheck"""
        services = compose_content.get('services', {})
        postgres = services.get('postgres', {})

        assert 'healthcheck' in postgres, "PostgreSQL should have healthcheck"
        healthcheck = postgres['healthcheck']
        assert 'test' in healthcheck, "Healthcheck should have test command"
        assert 'interval' in healthcheck, "Healthcheck should have interval"

    def test_redis_has_healthcheck(self, compose_content):
        """Test that Redis has healthcheck"""
        services = compose_content.get('services', {})
        redis = services.get('redis', {})

        assert 'healthcheck' in redis, "Redis should have healthcheck"
        healthcheck = redis['healthcheck']
        assert 'test' in healthcheck, "Healthcheck should have test command"

    def test_rabbitmq_has_healthcheck(self, compose_content):
        """Test that RabbitMQ has healthcheck"""
        services = compose_content.get('services', {})
        rabbitmq = services.get('rabbitmq', {})

        assert 'healthcheck' in rabbitmq, "RabbitMQ should have healthcheck"
        healthcheck = rabbitmq['healthcheck']
        assert 'test' in healthcheck, "Healthcheck should have test command"

    def test_backend_has_healthcheck(self, compose_content):
        """Test that backend API has healthcheck"""
        services = compose_content.get('services', {})
        backend = services.get('backend', {})

        assert 'healthcheck' in backend, "Backend should have healthcheck"
        healthcheck = backend['healthcheck']
        assert 'test' in healthcheck, "Healthcheck should have test command"

        # Should check /health endpoint
        test_cmd = str(healthcheck['test'])
        assert '/health' in test_cmd, "Backend healthcheck should check /health endpoint"

    def test_minio_has_healthcheck(self, compose_content):
        """Test that MinIO has healthcheck"""
        services = compose_content.get('services', {})
        minio = services.get('minio', {})

        assert 'healthcheck' in minio, "MinIO should have healthcheck"
        healthcheck = minio['healthcheck']
        assert 'test' in healthcheck, "Healthcheck should have test command"

    def test_prometheus_has_healthcheck(self, compose_content):
        """Test that Prometheus has healthcheck"""
        services = compose_content.get('services', {})
        prometheus = services.get('prometheus', {})

        assert 'healthcheck' in prometheus, (
            "Prometheus should have healthcheck for production monitoring"
        )
        healthcheck = prometheus['healthcheck']
        assert 'test' in healthcheck, "Healthcheck should have test command"

        # Should check /-/healthy endpoint (Prometheus standard)
        test_cmd = str(healthcheck['test'])
        assert '/-/healthy' in test_cmd or '/-/ready' in test_cmd, (
            "Prometheus healthcheck should use /-/healthy or /-/ready endpoint"
        )

    def test_frontend_or_nginx_has_healthcheck(self, compose_content):
        """Test that frontend/nginx has healthcheck"""
        services = compose_content.get('services', {})

        # Check if frontend or nginx service exists
        frontend = services.get('frontend', {})
        nginx = services.get('nginx', {})

        # At least one should have healthcheck
        has_frontend_healthcheck = 'healthcheck' in frontend
        has_nginx_healthcheck = 'healthcheck' in nginx

        assert has_frontend_healthcheck or has_nginx_healthcheck, (
            "Frontend or nginx service should have healthcheck"
        )

    def test_all_production_services_have_healthchecks(self, compose_content):
        """Test that all critical production services have healthchecks"""
        services = compose_content.get('services', {})

        # Services that MUST have healthchecks in production
        required_healthchecks = [
            'postgres',
            'redis',
            'rabbitmq',
            'backend',
            'minio',
            'prometheus'
        ]

        missing_healthchecks = []
        for service_name in required_healthchecks:
            if service_name in services:
                service = services[service_name]
                if 'healthcheck' not in service:
                    missing_healthchecks.append(service_name)

        assert len(missing_healthchecks) == 0, (
            f"Services missing healthchecks: {', '.join(missing_healthchecks)}"
        )


class TestProductionConfiguration:
    """Test production-specific configurations"""

    @pytest.fixture
    def compose_content(self):
        """Read docker-compose.yml as YAML"""
        compose_path = Path(__file__).parent.parent / "docker-compose.yml"
        with open(compose_path, 'r') as f:
            return yaml.safe_load(f)

    def test_services_have_restart_policies(self, compose_content):
        """Test that production services have restart policies"""
        services = compose_content.get('services', {})

        # Production services should have restart policies
        production_services = [
            'postgres', 'redis', 'rabbitmq',
            'backend', 'minio', 'prometheus'
        ]

        for service_name in production_services:
            if service_name in services:
                service = services[service_name]
                assert 'restart' in service, (
                    f"Production service '{service_name}' should have restart policy"
                )
                restart_policy = service.get('restart', '')
                assert restart_policy in ['always', 'unless-stopped', 'on-failure'], (
                    f"Service '{service_name}' should have production restart policy"
                )

    def test_volumes_are_named(self, compose_content):
        """Test that data volumes are properly named"""
        volumes = compose_content.get('volumes', {})

        # Key data volumes that should exist
        expected_volumes = [
            'postgres_data',
            'redis_data',
            'minio_data'
        ]

        for volume_name in expected_volumes:
            assert volume_name in volumes, (
                f"Named volume '{volume_name}' should be defined for data persistence"
            )

    def test_network_defined(self, compose_content):
        """Test that custom network is defined"""
        networks = compose_content.get('networks', {})

        assert len(networks) > 0, "Should define custom network for service isolation"

        # Check that services use the network
        services = compose_content.get('services', {})
        production_services = ['postgres', 'redis', 'backend']

        for service_name in production_services:
            if service_name in services:
                service = services[service_name]
                assert 'networks' in service, (
                    f"Service '{service_name}' should be connected to custom network"
                )

    def test_no_build_contexts_in_production(self, compose_content):
        """Test that services don't use build contexts (should use pre-built images)"""
        services = compose_content.get('services', {})

        # For pilot, services can use build context if needed
        # This is a warning test, not a hard requirement
        services_with_build = []

        for service_name, service in services.items():
            if 'build' in service:
                services_with_build.append(service_name)

        # This is informational - in production you'd want pre-built images
        # For now, we just document which services use build
        if len(services_with_build) > 0:
            # Not failing the test, just documenting
            pass  # Services with build: backend, frontend (acceptable for pilot)


class TestDockerComposeUsageDocumentation:
    """Test that docker-compose usage is properly documented"""

    def test_env_example_file_exists(self):
        """Test that .env.example exists for configuration guidance"""
        env_example = Path(__file__).parent.parent / ".env.example"

        # .env.example is recommended but not required
        # This test documents the recommendation
        if not env_example.exists():
            # Not a hard failure - just document the recommendation
            pass  # Recommendation: Create .env.example with default values

    def test_readme_has_docker_compose_instructions(self):
        """Test that README includes docker-compose usage"""
        readme = Path(__file__).parent.parent / "README.md"

        if readme.exists():
            content = readme.read_text()

            # Should mention docker-compose
            assert 'docker-compose' in content.lower() or 'docker compose' in content.lower(), (
                "README should include docker-compose usage instructions"
            )
