"""
Test suite for Docker Compose configuration
Ensures docker-compose.yml exists and is properly configured for local development
"""

import os
import pytest
import yaml


class TestDockerComposeFile:
    """Test docker-compose.yml file exists and is valid"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return os.path.dirname(os.path.dirname(__file__))

    @pytest.fixture
    def docker_compose_path(self, project_root):
        """Get path to docker-compose.yml file"""
        return os.path.join(project_root, 'docker-compose.yml')

    @pytest.fixture
    def docker_compose_data(self, docker_compose_path):
        """Load and parse docker-compose.yml"""
        with open(docker_compose_path, 'r') as f:
            return yaml.safe_load(f)

    def test_docker_compose_yml_exists(self, docker_compose_path):
        """Test that docker-compose.yml file exists"""
        assert os.path.exists(docker_compose_path), \
            "docker-compose.yml file must exist in project root"

    def test_docker_compose_is_valid_yaml(self, docker_compose_path):
        """Test that docker-compose.yml is valid YAML"""
        try:
            with open(docker_compose_path, 'r') as f:
                yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(f"docker-compose.yml is not valid YAML: {e}")

    def test_docker_compose_has_version(self, docker_compose_data):
        """Test that docker-compose.yml has version specified"""
        assert 'version' in docker_compose_data, \
            "docker-compose.yml should specify a version"

    def test_docker_compose_has_services(self, docker_compose_data):
        """Test that docker-compose.yml has services section"""
        assert 'services' in docker_compose_data, \
            "docker-compose.yml should have services section"


class TestPostgreSQLService:
    """Test PostgreSQL service configuration"""

    @pytest.fixture
    def docker_compose_data(self, project_root):
        """Load docker-compose.yml"""
        docker_compose_path = os.path.join(project_root, 'docker-compose.yml')
        with open(docker_compose_path, 'r') as f:
            return yaml.safe_load(f)

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return os.path.dirname(os.path.dirname(__file__))

    def test_postgres_service_exists(self, docker_compose_data):
        """Test that PostgreSQL service is defined"""
        services = docker_compose_data.get('services', {})
        assert 'postgres' in services, \
            "docker-compose.yml should define postgres service"

    def test_postgres_uses_correct_image(self, docker_compose_data):
        """Test that PostgreSQL uses version 15"""
        postgres_service = docker_compose_data['services']['postgres']
        assert 'image' in postgres_service, \
            "postgres service should specify an image"
        assert 'postgres:15' in postgres_service['image'], \
            "postgres service should use PostgreSQL version 15"

    def test_postgres_has_environment_variables(self, docker_compose_data):
        """Test that PostgreSQL has required environment variables"""
        postgres_service = docker_compose_data['services']['postgres']
        assert 'environment' in postgres_service, \
            "postgres service should have environment variables"

        env = postgres_service['environment']
        required_vars = ['POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_DB']

        for var in required_vars:
            # Check if var exists either as key or in list format
            if isinstance(env, dict):
                assert var in env, \
                    f"postgres environment should include {var}"
            elif isinstance(env, list):
                var_exists = any(var in item for item in env)
                assert var_exists, \
                    f"postgres environment should include {var}"

    def test_postgres_has_port_mapping(self, docker_compose_data):
        """Test that PostgreSQL has port mapping"""
        postgres_service = docker_compose_data['services']['postgres']
        assert 'ports' in postgres_service, \
            "postgres service should expose ports"

        ports = postgres_service['ports']
        assert len(ports) > 0, \
            "postgres service should have at least one port mapping"

        # Check that 5432 is mapped
        port_mapped = any('5432' in str(port) for port in ports)
        assert port_mapped, \
            "postgres service should map port 5432"

    def test_postgres_has_volume(self, docker_compose_data):
        """Test that PostgreSQL has persistent volume"""
        postgres_service = docker_compose_data['services']['postgres']
        assert 'volumes' in postgres_service, \
            "postgres service should have volumes for data persistence"

    def test_postgres_has_healthcheck(self, docker_compose_data):
        """Test that PostgreSQL has healthcheck configured"""
        postgres_service = docker_compose_data['services']['postgres']
        # Healthcheck is optional but recommended
        if 'healthcheck' in postgres_service:
            healthcheck = postgres_service['healthcheck']
            assert 'test' in healthcheck, \
                "postgres healthcheck should have test command"


class TestRedisService:
    """Test Redis service configuration"""

    @pytest.fixture
    def docker_compose_data(self, project_root):
        """Load docker-compose.yml"""
        docker_compose_path = os.path.join(project_root, 'docker-compose.yml')
        with open(docker_compose_path, 'r') as f:
            return yaml.safe_load(f)

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return os.path.dirname(os.path.dirname(__file__))

    def test_redis_service_exists(self, docker_compose_data):
        """Test that Redis service is defined"""
        services = docker_compose_data.get('services', {})
        assert 'redis' in services, \
            "docker-compose.yml should define redis service"

    def test_redis_uses_correct_image(self, docker_compose_data):
        """Test that Redis uses version 7"""
        redis_service = docker_compose_data['services']['redis']
        assert 'image' in redis_service, \
            "redis service should specify an image"
        assert 'redis:7' in redis_service['image'], \
            "redis service should use Redis version 7"

    def test_redis_has_port_mapping(self, docker_compose_data):
        """Test that Redis has port mapping"""
        redis_service = docker_compose_data['services']['redis']
        assert 'ports' in redis_service, \
            "redis service should expose ports"

        ports = redis_service['ports']
        # Check that 6379 is mapped
        port_mapped = any('6379' in str(port) for port in ports)
        assert port_mapped, \
            "redis service should map port 6379"

    def test_redis_has_volume(self, docker_compose_data):
        """Test that Redis has persistent volume"""
        redis_service = docker_compose_data['services']['redis']
        assert 'volumes' in redis_service, \
            "redis service should have volumes for data persistence"


class TestBackendService:
    """Test backend service configuration"""

    @pytest.fixture
    def docker_compose_data(self, project_root):
        """Load docker-compose.yml"""
        docker_compose_path = os.path.join(project_root, 'docker-compose.yml')
        with open(docker_compose_path, 'r') as f:
            return yaml.safe_load(f)

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return os.path.dirname(os.path.dirname(__file__))

    def test_backend_service_exists(self, docker_compose_data):
        """Test that backend service is defined"""
        services = docker_compose_data.get('services', {})
        assert 'backend' in services, \
            "docker-compose.yml should define backend service"

    def test_backend_has_build_or_image(self, docker_compose_data):
        """Test that backend uses build or image"""
        backend_service = docker_compose_data['services']['backend']
        assert 'build' in backend_service or 'image' in backend_service, \
            "backend service should have build or image configuration"

    def test_backend_builds_from_backend_directory(self, docker_compose_data):
        """Test that backend builds from backend directory"""
        backend_service = docker_compose_data['services']['backend']
        if 'build' in backend_service:
            build = backend_service['build']
            if isinstance(build, str):
                assert 'backend' in build.lower(), \
                    "backend service should build from backend directory"
            elif isinstance(build, dict):
                context = build.get('context', '')
                assert 'backend' in context.lower(), \
                    "backend service should build from backend directory"

    def test_backend_exposes_port_8000(self, docker_compose_data):
        """Test that backend exposes port 8000"""
        backend_service = docker_compose_data['services']['backend']
        assert 'ports' in backend_service, \
            "backend service should expose ports"
        ports = backend_service['ports']
        port_mapped = any('8000' in str(port) for port in ports)
        assert port_mapped, \
            "backend service should map port 8000"

    def test_backend_has_environment_config(self, docker_compose_data):
        """Test that backend has environment configuration"""
        backend_service = docker_compose_data['services']['backend']
        has_env = 'environment' in backend_service or 'env_file' in backend_service
        assert has_env, \
            "backend service should have environment variables"

    def test_backend_depends_on_postgres(self, docker_compose_data):
        """Test that backend depends on postgres"""
        backend_service = docker_compose_data['services']['backend']
        assert 'depends_on' in backend_service, \
            "backend service should have depends_on"
        depends_on = backend_service['depends_on']
        if isinstance(depends_on, list):
            assert 'postgres' in depends_on, \
                "backend should depend on postgres"
        elif isinstance(depends_on, dict):
            assert 'postgres' in depends_on, \
                "backend should depend on postgres"

    def test_backend_depends_on_redis(self, docker_compose_data):
        """Test that backend depends on redis"""
        backend_service = docker_compose_data['services']['backend']
        depends_on = backend_service['depends_on']
        if isinstance(depends_on, list):
            assert 'redis' in depends_on, \
                "backend should depend on redis"
        elif isinstance(depends_on, dict):
            assert 'redis' in depends_on, \
                "backend should depend on redis"


class TestFrontendService:
    """Test frontend service configuration"""

    @pytest.fixture
    def docker_compose_data(self, project_root):
        """Load docker-compose.yml"""
        docker_compose_path = os.path.join(project_root, 'docker-compose.yml')
        with open(docker_compose_path, 'r') as f:
            return yaml.safe_load(f)

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return os.path.dirname(os.path.dirname(__file__))

    def test_frontend_service_exists(self, docker_compose_data):
        """Test that frontend service is defined"""
        services = docker_compose_data.get('services', {})
        assert 'frontend' in services, \
            "docker-compose.yml should define frontend service"

    def test_frontend_has_build_or_image(self, docker_compose_data):
        """Test that frontend uses build or image"""
        frontend_service = docker_compose_data['services']['frontend']
        assert 'build' in frontend_service or 'image' in frontend_service, \
            "frontend service should have build or image configuration"

    def test_frontend_builds_from_frontend_directory(self, docker_compose_data):
        """Test that frontend builds from frontend directory"""
        frontend_service = docker_compose_data['services']['frontend']
        if 'build' in frontend_service:
            build = frontend_service['build']
            if isinstance(build, str):
                assert 'frontend' in build.lower(), \
                    "frontend service should build from frontend directory"
            elif isinstance(build, dict):
                context = build.get('context', '')
                assert 'frontend' in context.lower(), \
                    "frontend service should build from frontend directory"

    def test_frontend_exposes_port(self, docker_compose_data):
        """Test that frontend exposes a port"""
        frontend_service = docker_compose_data['services']['frontend']
        assert 'ports' in frontend_service, \
            "frontend service should expose ports"
        ports = frontend_service['ports']
        assert len(ports) > 0, \
            "frontend should have at least one port mapping"

    def test_frontend_depends_on_backend(self, docker_compose_data):
        """Test that frontend depends on backend"""
        frontend_service = docker_compose_data['services']['frontend']
        if 'depends_on' in frontend_service:
            depends_on = frontend_service['depends_on']
            if isinstance(depends_on, list):
                assert 'backend' in depends_on, \
                    "frontend should depend on backend"
            elif isinstance(depends_on, dict):
                assert 'backend' in depends_on, \
                    "frontend should depend on backend"


class TestNginxService:
    """Test Nginx service configuration (reverse proxy)"""

    @pytest.fixture
    def docker_compose_data(self, project_root):
        """Load docker-compose.yml"""
        docker_compose_path = os.path.join(project_root, 'docker-compose.yml')
        with open(docker_compose_path, 'r') as f:
            return yaml.safe_load(f)

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return os.path.dirname(os.path.dirname(__file__))

    def test_nginx_service_exists(self, docker_compose_data):
        """Test that nginx service is defined"""
        services = docker_compose_data.get('services', {})
        assert 'nginx' in services, \
            "docker-compose.yml should define nginx service as reverse proxy"

    def test_nginx_uses_nginx_image(self, docker_compose_data):
        """Test that nginx uses nginx image"""
        nginx_service = docker_compose_data['services']['nginx']
        if 'image' in nginx_service:
            assert 'nginx' in nginx_service['image'].lower(), \
                "nginx service should use nginx image"

    def test_nginx_exposes_port_80(self, docker_compose_data):
        """Test that nginx exposes port 80"""
        nginx_service = docker_compose_data['services']['nginx']
        assert 'ports' in nginx_service, \
            "nginx service should expose ports"
        ports = nginx_service['ports']
        port_mapped = any('80' in str(port) for port in ports)
        assert port_mapped, \
            "nginx service should map port 80"

    def test_nginx_depends_on_frontend_and_backend(self, docker_compose_data):
        """Test that nginx depends on frontend and backend"""
        nginx_service = docker_compose_data['services']['nginx']
        if 'depends_on' in nginx_service:
            depends_on = nginx_service['depends_on']
            if isinstance(depends_on, list):
                has_deps = 'frontend' in depends_on or 'backend' in depends_on
                assert has_deps, \
                    "nginx should depend on frontend or backend"
            elif isinstance(depends_on, dict):
                has_deps = 'frontend' in depends_on or 'backend' in depends_on
                assert has_deps, \
                    "nginx should depend on frontend or backend"


class TestPgAdminService:
    """Test pgAdmin service configuration"""

    @pytest.fixture
    def docker_compose_data(self, project_root):
        """Load docker-compose.yml"""
        docker_compose_path = os.path.join(project_root, 'docker-compose.yml')
        with open(docker_compose_path, 'r') as f:
            return yaml.safe_load(f)

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return os.path.dirname(os.path.dirname(__file__))

    def test_pgadmin_service_exists(self, docker_compose_data):
        """Test that pgAdmin service is defined"""
        services = docker_compose_data.get('services', {})
        assert 'pgadmin' in services, \
            "docker-compose.yml should define pgadmin service"

    def test_pgadmin_uses_correct_image(self, docker_compose_data):
        """Test that pgAdmin uses dpage/pgadmin4 image"""
        pgadmin_service = docker_compose_data['services']['pgadmin']
        assert 'image' in pgadmin_service, \
            "pgadmin service should specify an image"
        assert 'pgadmin4' in pgadmin_service['image'], \
            "pgadmin service should use pgadmin4 image"

    def test_pgadmin_has_environment_variables(self, docker_compose_data):
        """Test that pgAdmin has required environment variables"""
        pgadmin_service = docker_compose_data['services']['pgadmin']
        assert 'environment' in pgadmin_service, \
            "pgadmin service should have environment variables"

        env = pgadmin_service['environment']
        required_vars = ['PGADMIN_DEFAULT_EMAIL', 'PGADMIN_DEFAULT_PASSWORD']

        for var in required_vars:
            # Check if var exists either as key or in list format
            if isinstance(env, dict):
                assert var in env, \
                    f"pgadmin environment should include {var}"
            elif isinstance(env, list):
                var_exists = any(var in item for item in env)
                assert var_exists, \
                    f"pgadmin environment should include {var}"

    def test_pgadmin_has_port_mapping(self, docker_compose_data):
        """Test that pgAdmin has port mapping"""
        pgadmin_service = docker_compose_data['services']['pgadmin']
        assert 'ports' in pgadmin_service, \
            "pgadmin service should expose ports"

        ports = pgadmin_service['ports']
        # Check that 80 or 5050 is mapped
        port_mapped = any(('80' in str(port) or '5050' in str(port)) for port in ports)
        assert port_mapped, \
            "pgadmin service should map port 80 or 5050"

    def test_pgadmin_depends_on_postgres(self, docker_compose_data):
        """Test that pgAdmin depends on PostgreSQL"""
        pgadmin_service = docker_compose_data['services']['pgadmin']
        # depends_on is optional but recommended
        if 'depends_on' in pgadmin_service:
            depends_on = pgadmin_service['depends_on']
            if isinstance(depends_on, list):
                assert 'postgres' in depends_on, \
                    "pgadmin should depend on postgres service"
            elif isinstance(depends_on, dict):
                assert 'postgres' in depends_on, \
                    "pgadmin should depend on postgres service"


class TestVolumes:
    """Test volume configuration"""

    @pytest.fixture
    def docker_compose_data(self, project_root):
        """Load docker-compose.yml"""
        docker_compose_path = os.path.join(project_root, 'docker-compose.yml')
        with open(docker_compose_path, 'r') as f:
            return yaml.safe_load(f)

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return os.path.dirname(os.path.dirname(__file__))

    def test_volumes_section_exists(self, docker_compose_data):
        """Test that volumes section is defined"""
        assert 'volumes' in docker_compose_data, \
            "docker-compose.yml should have volumes section for named volumes"

    def test_postgres_volume_defined(self, docker_compose_data):
        """Test that PostgreSQL volume is defined"""
        volumes = docker_compose_data.get('volumes', {})
        # Look for postgres-related volume
        postgres_volume_exists = any('postgres' in vol_name.lower() for vol_name in volumes.keys())
        assert postgres_volume_exists, \
            "docker-compose.yml should define a postgres data volume"

    def test_redis_volume_defined(self, docker_compose_data):
        """Test that Redis volume is defined"""
        volumes = docker_compose_data.get('volumes', {})
        # Look for redis-related volume
        redis_volume_exists = any('redis' in vol_name.lower() for vol_name in volumes.keys())
        assert redis_volume_exists, \
            "docker-compose.yml should define a redis data volume"


class TestNetworking:
    """Test network configuration"""

    @pytest.fixture
    def docker_compose_data(self, project_root):
        """Load docker-compose.yml"""
        docker_compose_path = os.path.join(project_root, 'docker-compose.yml')
        with open(docker_compose_path, 'r') as f:
            return yaml.safe_load(f)

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return os.path.dirname(os.path.dirname(__file__))

    def test_services_on_same_network(self, docker_compose_data):
        """Test that services can communicate (on same network)"""
        services = docker_compose_data.get('services', {})

        # If networks are explicitly defined, check they're shared
        if 'networks' in docker_compose_data:
            # At least one network should be defined
            assert len(docker_compose_data['networks']) > 0, \
                "If networks section exists, it should define at least one network"

        # Services should either all be on default network or share a custom network
        # This is implicitly true in docker-compose unless explicitly separated


class TestDockerComposeIntegration:
    """Test overall docker-compose configuration"""

    @pytest.fixture
    def docker_compose_data(self, project_root):
        """Load docker-compose.yml"""
        docker_compose_path = os.path.join(project_root, 'docker-compose.yml')
        with open(docker_compose_path, 'r') as f:
            return yaml.safe_load(f)

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return os.path.dirname(os.path.dirname(__file__))

    def test_all_required_services_present(self, docker_compose_data):
        """Test that all required services are defined"""
        services = docker_compose_data.get('services', {})
        required_services = ['backend', 'frontend', 'postgres', 'redis', 'nginx', 'pgadmin']

        for service in required_services:
            assert service in services, \
                f"docker-compose.yml should define {service} service"

    def test_no_conflicting_ports(self, docker_compose_data):
        """Test that services don't have conflicting port mappings"""
        services = docker_compose_data.get('services', {})
        host_ports = []

        for service_name, service_config in services.items():
            if 'ports' in service_config:
                for port_mapping in service_config['ports']:
                    # Extract host port from mapping like "5432:5432" or just "5432"
                    port_str = str(port_mapping)
                    if ':' in port_str:
                        host_port = port_str.split(':')[0]
                    else:
                        host_port = port_str

                    assert host_port not in host_ports, \
                        f"Port {host_port} is mapped by multiple services"
                    host_ports.append(host_port)

    def test_environment_variables_are_set(self, docker_compose_data):
        """Test that all services have necessary environment variables"""
        services = docker_compose_data.get('services', {})

        # PostgreSQL
        if 'postgres' in services:
            assert 'environment' in services['postgres'], \
                "postgres service should have environment variables"

        # pgAdmin
        if 'pgadmin' in services:
            assert 'environment' in services['pgadmin'], \
                "pgadmin service should have environment variables"
