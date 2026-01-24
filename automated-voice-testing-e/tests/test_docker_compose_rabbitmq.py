"""
Test suite for docker-compose.yml RabbitMQ configuration

Validates the docker-compose.yml file includes proper RabbitMQ service configuration:
- RabbitMQ service definition
- Correct RabbitMQ image with management plugin
- Port configuration (AMQP and management UI)
- Environment variables (virtual host, users, passwords)
- Volume configuration for data persistence
- Healthcheck configuration
- Network configuration
- Restart policy
- Container name
"""

import pytest
from pathlib import Path
import yaml


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
DOCKER_COMPOSE_FILE = PROJECT_ROOT / "docker-compose.yml"


class TestDockerComposeFileExists:
    """Test that docker-compose.yml exists"""

    def test_docker_compose_file_exists(self):
        """Test that docker-compose.yml exists"""
        assert DOCKER_COMPOSE_FILE.exists(), "docker-compose.yml should exist"
        assert DOCKER_COMPOSE_FILE.is_file(), "docker-compose.yml should be a file"

    def test_docker_compose_has_content(self):
        """Test that docker-compose.yml has content"""
        content = DOCKER_COMPOSE_FILE.read_text()
        assert len(content) > 0, "docker-compose.yml should not be empty"

    def test_docker_compose_is_valid_yaml(self):
        """Test that docker-compose.yml is valid YAML"""
        content = DOCKER_COMPOSE_FILE.read_text()
        try:
            yaml.safe_load(content)
        except yaml.YAMLError as e:
            pytest.fail(f"docker-compose.yml is not valid YAML: {e}")


class TestRabbitMQService:
    """Test RabbitMQ service definition"""

    @pytest.fixture
    def docker_compose(self):
        """Load docker-compose.yml"""
        with open(DOCKER_COMPOSE_FILE, 'r') as f:
            return yaml.safe_load(f)

    def test_rabbitmq_service_exists(self, docker_compose):
        """Test that rabbitmq service exists"""
        assert 'services' in docker_compose, "docker-compose.yml should have services"
        assert 'rabbitmq' in docker_compose['services'], "RabbitMQ service should exist"

    def test_rabbitmq_has_image(self, docker_compose):
        """Test that RabbitMQ service has an image"""
        rabbitmq = docker_compose['services']['rabbitmq']
        assert 'image' in rabbitmq, "RabbitMQ service should have an image"

    def test_rabbitmq_uses_management_image(self, docker_compose):
        """Test that RabbitMQ uses management-enabled image"""
        rabbitmq = docker_compose['services']['rabbitmq']
        image = rabbitmq.get('image', '')
        assert 'rabbitmq' in image.lower(), "RabbitMQ service should use rabbitmq image"
        assert 'management' in image.lower(), "RabbitMQ image should include management plugin"

    def test_rabbitmq_has_container_name(self, docker_compose):
        """Test that RabbitMQ service has a container name"""
        rabbitmq = docker_compose['services']['rabbitmq']
        assert 'container_name' in rabbitmq, "RabbitMQ service should have a container name"
        assert 'rabbitmq' in rabbitmq['container_name'].lower(), "Container name should contain 'rabbitmq'"

    def test_rabbitmq_has_restart_policy(self, docker_compose):
        """Test that RabbitMQ service has a restart policy"""
        rabbitmq = docker_compose['services']['rabbitmq']
        assert 'restart' in rabbitmq, "RabbitMQ service should have a restart policy"
        assert rabbitmq['restart'] in ['always', 'unless-stopped', 'on-failure'], \
            "RabbitMQ restart policy should be valid"


class TestRabbitMQPorts:
    """Test RabbitMQ port configuration"""

    @pytest.fixture
    def docker_compose(self):
        """Load docker-compose.yml"""
        with open(DOCKER_COMPOSE_FILE, 'r') as f:
            return yaml.safe_load(f)

    def test_rabbitmq_has_ports(self, docker_compose):
        """Test that RabbitMQ service has ports defined"""
        rabbitmq = docker_compose['services']['rabbitmq']
        assert 'ports' in rabbitmq, "RabbitMQ service should have ports"
        assert isinstance(rabbitmq['ports'], list), "RabbitMQ ports should be a list"

    def test_rabbitmq_has_amqp_port(self, docker_compose):
        """Test that RabbitMQ exposes AMQP port (5672)"""
        rabbitmq = docker_compose['services']['rabbitmq']
        ports = rabbitmq.get('ports', [])
        port_strings = [str(p) for p in ports]
        assert any('5672' in p for p in port_strings), "RabbitMQ should expose AMQP port 5672"

    def test_rabbitmq_has_management_port(self, docker_compose):
        """Test that RabbitMQ exposes management UI port (15672)"""
        rabbitmq = docker_compose['services']['rabbitmq']
        ports = rabbitmq.get('ports', [])
        port_strings = [str(p) for p in ports]
        assert any('15672' in p for p in port_strings), "RabbitMQ should expose management port 15672"


class TestRabbitMQEnvironment:
    """Test RabbitMQ environment variables"""

    @pytest.fixture
    def docker_compose(self):
        """Load docker-compose.yml"""
        with open(DOCKER_COMPOSE_FILE, 'r') as f:
            return yaml.safe_load(f)

    def test_rabbitmq_has_environment(self, docker_compose):
        """Test that RabbitMQ service has environment variables"""
        rabbitmq = docker_compose['services']['rabbitmq']
        assert 'environment' in rabbitmq, "RabbitMQ service should have environment variables"

    def test_rabbitmq_has_default_user(self, docker_compose):
        """Test that RabbitMQ has default user configured"""
        rabbitmq = docker_compose['services']['rabbitmq']
        env = rabbitmq.get('environment', {})
        assert 'RABBITMQ_DEFAULT_USER' in env, "RabbitMQ should have RABBITMQ_DEFAULT_USER"

    def test_rabbitmq_has_default_pass(self, docker_compose):
        """Test that RabbitMQ has default password configured"""
        rabbitmq = docker_compose['services']['rabbitmq']
        env = rabbitmq.get('environment', {})
        assert 'RABBITMQ_DEFAULT_PASS' in env, "RabbitMQ should have RABBITMQ_DEFAULT_PASS"

    def test_rabbitmq_has_vhost(self, docker_compose):
        """Test that RabbitMQ has virtual host configured"""
        rabbitmq = docker_compose['services']['rabbitmq']
        env = rabbitmq.get('environment', {})
        assert 'RABBITMQ_DEFAULT_VHOST' in env, "RabbitMQ should have RABBITMQ_DEFAULT_VHOST"


class TestRabbitMQVolumes:
    """Test RabbitMQ volume configuration"""

    @pytest.fixture
    def docker_compose(self):
        """Load docker-compose.yml"""
        with open(DOCKER_COMPOSE_FILE, 'r') as f:
            return yaml.safe_load(f)

    def test_rabbitmq_has_volumes(self, docker_compose):
        """Test that RabbitMQ service has volumes defined"""
        rabbitmq = docker_compose['services']['rabbitmq']
        assert 'volumes' in rabbitmq, "RabbitMQ service should have volumes for data persistence"

    def test_rabbitmq_volume_is_list(self, docker_compose):
        """Test that RabbitMQ volumes is a list"""
        rabbitmq = docker_compose['services']['rabbitmq']
        volumes = rabbitmq.get('volumes', [])
        assert isinstance(volumes, list), "RabbitMQ volumes should be a list"

    def test_rabbitmq_has_data_volume(self, docker_compose):
        """Test that RabbitMQ has data volume mounted"""
        rabbitmq = docker_compose['services']['rabbitmq']
        volumes = rabbitmq.get('volumes', [])
        volume_strings = [str(v) for v in volumes]
        # Should have a volume mapped to /var/lib/rabbitmq
        assert any('rabbitmq' in v.lower() and '/var/lib/rabbitmq' in v
                   for v in volume_strings), "RabbitMQ should have data volume"

    def test_rabbitmq_volume_declared_in_volumes_section(self, docker_compose):
        """Test that RabbitMQ volume is declared in volumes section"""
        assert 'volumes' in docker_compose, "docker-compose.yml should have volumes section"
        volumes = docker_compose['volumes']
        assert any('rabbitmq' in v.lower() for v in volumes.keys()), \
            "RabbitMQ data volume should be declared in volumes section"


class TestRabbitMQHealthcheck:
    """Test RabbitMQ healthcheck configuration"""

    @pytest.fixture
    def docker_compose(self):
        """Load docker-compose.yml"""
        with open(DOCKER_COMPOSE_FILE, 'r') as f:
            return yaml.safe_load(f)

    def test_rabbitmq_has_healthcheck(self, docker_compose):
        """Test that RabbitMQ service has healthcheck"""
        rabbitmq = docker_compose['services']['rabbitmq']
        assert 'healthcheck' in rabbitmq, "RabbitMQ service should have healthcheck"

    def test_rabbitmq_healthcheck_has_test(self, docker_compose):
        """Test that RabbitMQ healthcheck has test command"""
        rabbitmq = docker_compose['services']['rabbitmq']
        healthcheck = rabbitmq.get('healthcheck', {})
        assert 'test' in healthcheck, "RabbitMQ healthcheck should have test command"

    def test_rabbitmq_healthcheck_uses_rabbitmqctl(self, docker_compose):
        """Test that RabbitMQ healthcheck uses rabbitmqctl"""
        rabbitmq = docker_compose['services']['rabbitmq']
        healthcheck = rabbitmq.get('healthcheck', {})
        test = str(healthcheck.get('test', ''))
        assert 'rabbitmqctl' in test.lower() or 'rabbitmq' in test.lower(), \
            "RabbitMQ healthcheck should use rabbitmqctl command"

    def test_rabbitmq_healthcheck_has_interval(self, docker_compose):
        """Test that RabbitMQ healthcheck has interval"""
        rabbitmq = docker_compose['services']['rabbitmq']
        healthcheck = rabbitmq.get('healthcheck', {})
        assert 'interval' in healthcheck, "RabbitMQ healthcheck should have interval"

    def test_rabbitmq_healthcheck_has_timeout(self, docker_compose):
        """Test that RabbitMQ healthcheck has timeout"""
        rabbitmq = docker_compose['services']['rabbitmq']
        healthcheck = rabbitmq.get('healthcheck', {})
        assert 'timeout' in healthcheck, "RabbitMQ healthcheck should have timeout"

    def test_rabbitmq_healthcheck_has_retries(self, docker_compose):
        """Test that RabbitMQ healthcheck has retries"""
        rabbitmq = docker_compose['services']['rabbitmq']
        healthcheck = rabbitmq.get('healthcheck', {})
        assert 'retries' in healthcheck, "RabbitMQ healthcheck should have retries"


class TestRabbitMQNetwork:
    """Test RabbitMQ network configuration"""

    @pytest.fixture
    def docker_compose(self):
        """Load docker-compose.yml"""
        with open(DOCKER_COMPOSE_FILE, 'r') as f:
            return yaml.safe_load(f)

    def test_rabbitmq_has_networks(self, docker_compose):
        """Test that RabbitMQ service is connected to networks"""
        rabbitmq = docker_compose['services']['rabbitmq']
        assert 'networks' in rabbitmq, "RabbitMQ service should be connected to networks"

    def test_rabbitmq_on_voiceai_network(self, docker_compose):
        """Test that RabbitMQ is on the voiceai-network"""
        rabbitmq = docker_compose['services']['rabbitmq']
        networks = rabbitmq.get('networks', [])
        assert 'voiceai-network' in networks, "RabbitMQ should be on voiceai-network"


class TestBackendRabbitMQIntegration:
    """Test that backend service is configured to use RabbitMQ"""

    @pytest.fixture
    def docker_compose(self):
        """Load docker-compose.yml"""
        with open(DOCKER_COMPOSE_FILE, 'r') as f:
            return yaml.safe_load(f)

    def test_backend_depends_on_rabbitmq(self, docker_compose):
        """Test that backend service depends on RabbitMQ"""
        backend = docker_compose['services']['backend']
        depends_on = backend.get('depends_on', {})

        # depends_on can be a list or a dict
        if isinstance(depends_on, list):
            assert 'rabbitmq' in depends_on, "Backend should depend on RabbitMQ"
        elif isinstance(depends_on, dict):
            assert 'rabbitmq' in depends_on, "Backend should depend on RabbitMQ"

    def test_backend_has_rabbitmq_url(self, docker_compose):
        """Test that backend has RabbitMQ URL in environment"""
        backend = docker_compose['services']['backend']
        env = backend.get('environment', {})

        # Check for RabbitMQ or message broker URL
        has_rabbitmq_config = any('RABBITMQ' in key.upper() or 'BROKER' in key.upper()
                                   for key in env.keys())
        assert has_rabbitmq_config, "Backend should have RabbitMQ/broker URL in environment"
