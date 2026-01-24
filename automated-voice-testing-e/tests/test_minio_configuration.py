"""
Test suite for MinIO configuration (TASK-114).

Tests verify:
- MinIO service configuration in docker-compose.yml
- MinIO bucket initialization
- Environment variable configuration
- Integration with storage service
"""

import pytest
import yaml
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent


class TestMinIODockerCompose:
    """Test MinIO configuration in docker-compose.yml"""

    @pytest.fixture
    def docker_compose_config(self):
        """Load docker-compose.yml configuration"""
        docker_compose_path = PROJECT_ROOT / "docker-compose.yml"
        with open(docker_compose_path) as f:
            return yaml.safe_load(f)

    def test_minio_service_exists(self, docker_compose_config):
        """Test that minio service is defined in docker-compose.yml"""
        assert "minio" in docker_compose_config["services"], \
            "minio service should be defined in docker-compose.yml"

    def test_minio_uses_correct_image(self, docker_compose_config):
        """Test that minio service uses official minio image"""
        minio_service = docker_compose_config["services"]["minio"]
        assert "image" in minio_service, "minio service should have image defined"
        assert "minio/minio" in minio_service["image"], \
            "minio service should use official minio/minio image"

    def test_minio_has_correct_ports(self, docker_compose_config):
        """Test that minio exposes correct ports"""
        minio_service = docker_compose_config["services"]["minio"]
        assert "ports" in minio_service, "minio service should expose ports"

        ports = minio_service["ports"]
        # Convert ports to strings for comparison
        port_mappings = [str(p) for p in ports]

        # Check for API port (9000)
        assert any("9000:9000" in p for p in port_mappings), \
            "minio should expose API port 9000"

        # Check for console port (9001)
        assert any("9001:9001" in p for p in port_mappings), \
            "minio should expose console port 9001"

    def test_minio_has_environment_variables(self, docker_compose_config):
        """Test that minio has required environment variables"""
        minio_service = docker_compose_config["services"]["minio"]
        assert "environment" in minio_service, \
            "minio service should have environment variables"

        env = minio_service["environment"]
        assert "MINIO_ROOT_USER" in env, \
            "minio should have MINIO_ROOT_USER environment variable"
        assert "MINIO_ROOT_PASSWORD" in env, \
            "minio should have MINIO_ROOT_PASSWORD environment variable"

    def test_minio_has_volume(self, docker_compose_config):
        """Test that minio has data volume configured"""
        minio_service = docker_compose_config["services"]["minio"]
        assert "volumes" in minio_service, "minio service should have volumes"

        volumes = minio_service["volumes"]
        assert any("minio_data" in str(v) for v in volumes), \
            "minio should have minio_data volume"

    def test_minio_has_healthcheck(self, docker_compose_config):
        """Test that minio has healthcheck configured"""
        minio_service = docker_compose_config["services"]["minio"]
        assert "healthcheck" in minio_service, \
            "minio service should have healthcheck"

        healthcheck = minio_service["healthcheck"]
        assert "test" in healthcheck, "healthcheck should have test command"

    def test_minio_volume_defined(self, docker_compose_config):
        """Test that minio_data volume is defined"""
        assert "volumes" in docker_compose_config, \
            "docker-compose should define volumes"

        volumes = docker_compose_config["volumes"]
        assert "minio_data" in volumes, \
            "minio_data volume should be defined"


class TestMinIOBucketInitialization:
    """Test MinIO bucket initialization configuration"""

    @pytest.fixture
    def docker_compose_config(self):
        """Load docker-compose.yml configuration"""
        docker_compose_path = PROJECT_ROOT / "docker-compose.yml"
        with open(docker_compose_path) as f:
            return yaml.safe_load(f)

    def test_createbuckets_service_exists(self, docker_compose_config):
        """Test that createbuckets service exists"""
        assert "createbuckets" in docker_compose_config["services"], \
            "createbuckets service should be defined for bucket initialization"

    def test_createbuckets_uses_minio_client(self, docker_compose_config):
        """Test that createbuckets uses minio/mc image"""
        createbuckets = docker_compose_config["services"]["createbuckets"]
        assert "image" in createbuckets, "createbuckets should have image"
        assert "minio/mc" in createbuckets["image"], \
            "createbuckets should use minio/mc (MinIO Client) image"

    def test_createbuckets_depends_on_minio(self, docker_compose_config):
        """Test that createbuckets depends on minio service"""
        createbuckets = docker_compose_config["services"]["createbuckets"]
        assert "depends_on" in createbuckets, \
            "createbuckets should depend on minio service"

        depends_on = createbuckets["depends_on"]
        # depends_on could be a list or dict
        if isinstance(depends_on, list):
            assert "minio" in depends_on
        else:
            assert "minio" in depends_on

    def test_createbuckets_has_entrypoint(self, docker_compose_config):
        """Test that createbuckets has entrypoint script"""
        createbuckets = docker_compose_config["services"]["createbuckets"]
        assert "entrypoint" in createbuckets, \
            "createbuckets should have entrypoint script"

        entrypoint = createbuckets["entrypoint"]
        # Convert to string for searching
        entrypoint_str = str(entrypoint)

        # Check for mc alias setup
        assert "mc alias set" in entrypoint_str, \
            "entrypoint should configure mc alias"

        # Check for required bucket creation commands
        assert "mb" in entrypoint_str, \
            "entrypoint should create buckets using 'mb' command"

    def test_createbuckets_creates_required_buckets(self, docker_compose_config):
        """Test that createbuckets creates all required buckets"""
        createbuckets = docker_compose_config["services"]["createbuckets"]
        entrypoint_str = str(createbuckets["entrypoint"])

        # Check for the three required buckets
        required_buckets = ["input-audio", "output-audio", "artifacts"]

        for bucket in required_buckets:
            assert bucket in entrypoint_str, \
                f"createbuckets should create '{bucket}' bucket"

    def test_createbuckets_sets_bucket_policies(self, docker_compose_config):
        """Test that createbuckets sets appropriate bucket policies"""
        createbuckets = docker_compose_config["services"]["createbuckets"]
        entrypoint_str = str(createbuckets["entrypoint"])

        # Check for policy setting (anonymous set download)
        assert "anonymous set" in entrypoint_str, \
            "createbuckets should set bucket policies"


class TestEnvironmentConfiguration:
    """Test .env.example has MinIO configuration"""

    @pytest.fixture
    def env_example_content(self):
        """Load .env.example content"""
        env_path = PROJECT_ROOT / ".env.example"
        return env_path.read_text()

    def test_env_has_storage_backend(self, env_example_content):
        """Test that .env.example has STORAGE_BACKEND variable"""
        assert "STORAGE_BACKEND" in env_example_content, \
            ".env.example should have STORAGE_BACKEND variable"

    def test_env_has_minio_endpoint(self, env_example_content):
        """Test that .env.example has MINIO_ENDPOINT_URL"""
        assert "MINIO_ENDPOINT_URL" in env_example_content, \
            ".env.example should have MINIO_ENDPOINT_URL"

    def test_env_has_minio_credentials(self, env_example_content):
        """Test that .env.example has MinIO credentials"""
        assert "MINIO_ACCESS_KEY" in env_example_content, \
            ".env.example should have MINIO_ACCESS_KEY"
        assert "MINIO_SECRET_KEY" in env_example_content, \
            ".env.example should have MINIO_SECRET_KEY"

    def test_env_has_minio_bucket_names(self, env_example_content):
        """Test that .env.example has MinIO bucket names"""
        assert "MINIO_INPUT_AUDIO_BUCKET" in env_example_content, \
            ".env.example should have MINIO_INPUT_AUDIO_BUCKET"
        assert "MINIO_OUTPUT_AUDIO_BUCKET" in env_example_content, \
            ".env.example should have MINIO_OUTPUT_AUDIO_BUCKET"
        assert "MINIO_ARTIFACTS_BUCKET" in env_example_content, \
            ".env.example should have MINIO_ARTIFACTS_BUCKET"

    def test_env_has_minio_region(self, env_example_content):
        """Test that .env.example has MINIO_REGION"""
        assert "MINIO_REGION" in env_example_content, \
            ".env.example should have MINIO_REGION"

    def test_env_has_minio_console_url(self, env_example_content):
        """Test that .env.example has MINIO_CONSOLE_URL"""
        assert "MINIO_CONSOLE_URL" in env_example_content, \
            ".env.example should have MINIO_CONSOLE_URL"


class TestMinIOIntegration:
    """Test integration between MinIO and storage service"""

    def test_storage_service_supports_custom_endpoint(self):
        """Test that StorageService supports custom endpoint (for MinIO)"""
        import sys
        from pathlib import Path

        backend_dir = PROJECT_ROOT / "backend"
        if str(backend_dir) not in sys.path:
            sys.path.insert(0, str(backend_dir))

        from services.storage_service import StorageService

        # Should be able to initialize with custom endpoint
        service = StorageService(
            endpoint_url="http://localhost:9000",
            aws_access_key_id="minioadmin",
            aws_secret_access_key="minioadmin123"
        )

        assert service is not None, \
            "StorageService should support custom endpoint for MinIO"

    def test_storage_service_can_use_minio_credentials(self):
        """Test that StorageService works with MinIO credentials"""
        import sys
        from pathlib import Path

        backend_dir = PROJECT_ROOT / "backend"
        if str(backend_dir) not in sys.path:
            sys.path.insert(0, str(backend_dir))

        from services.storage_service import StorageService

        # Create service with MinIO credentials from docker-compose
        service = StorageService(
            endpoint_url="http://localhost:9000",
            aws_access_key_id="minioadmin",
            aws_secret_access_key="minioadmin123",
            region_name="us-east-1"
        )

        # Verify service is configured
        assert service.s3_client is not None, \
            "StorageService should have S3 client configured"


class TestTaskRequirements:
    """Verify TASK-114 requirements are met"""

    def test_task_114_minio_in_docker_compose(self):
        """Test TASK-114: MinIO service in docker-compose"""
        docker_compose_path = PROJECT_ROOT / "docker-compose.yml"
        content = docker_compose_path.read_text()
        assert "minio" in content.lower(), \
            "TASK-114: docker-compose.yml should include MinIO service"

    def test_task_114_three_buckets_configured(self):
        """Test TASK-114: Three required buckets configured"""
        docker_compose_path = PROJECT_ROOT / "docker-compose.yml"
        content = docker_compose_path.read_text()

        required_buckets = ["input-audio", "output-audio", "artifacts"]
        for bucket in required_buckets:
            assert bucket in content, \
                f"TASK-114: '{bucket}' bucket should be configured"

    def test_task_114_boto3_in_requirements(self):
        """Test TASK-114: boto3 in requirements.txt"""
        requirements_path = PROJECT_ROOT / "backend" / "requirements.txt"
        content = requirements_path.read_text()
        assert "boto3" in content, \
            "TASK-114: requirements.txt should include boto3"

    def test_task_114_minio_config_in_env_example(self):
        """Test TASK-114: MinIO config in .env.example"""
        env_path = PROJECT_ROOT / ".env.example"
        content = env_path.read_text()
        assert "MINIO" in content, \
            "TASK-114: .env.example should include MinIO configuration"

    def test_task_114_storage_service_exists(self):
        """Test TASK-114: Storage service exists and works with MinIO"""
        storage_service_path = PROJECT_ROOT / "backend" / "services" / "storage_service.py"
        assert storage_service_path.exists(), \
            "TASK-114: storage_service.py should exist"

        content = storage_service_path.read_text()
        assert "boto3" in content, \
            "TASK-114: storage_service should use boto3 for S3/MinIO"
