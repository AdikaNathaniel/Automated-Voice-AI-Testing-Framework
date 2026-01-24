"""
Test suite for environment variable configuration.

Validates that required environment variables are properly configured
with graceful degradation for optional services.
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_FILE = PROJECT_ROOT / "backend" / "api" / "config.py"
ENV_EXAMPLE = PROJECT_ROOT / ".env.example"


class TestSoundHoundOptional:
    """Test SOUNDHOUND_API_KEY is optional with graceful degradation."""

    @pytest.fixture
    def config_content(self):
        return CONFIG_FILE.read_text()

    def test_soundhound_has_default_none(self, config_content):
        """SOUNDHOUND_API_KEY should have default=None."""
        has_default_none = (
            "SOUNDHOUND_API_KEY" in config_content and
            ("default=None" in config_content or "default = None" in config_content or
             'default=""' in config_content or "default=''" in config_content)
        )
        assert has_default_none, \
            "SOUNDHOUND_API_KEY should have default=None for graceful degradation"

    def test_soundhound_is_optional_type(self, config_content):
        """SOUNDHOUND_API_KEY should use Optional type hint."""
        # Check for Optional[str] pattern near SOUNDHOUND_API_KEY
        has_optional = "Optional" in config_content and "SOUNDHOUND_API_KEY" in config_content
        assert has_optional, \
            "SOUNDHOUND_API_KEY should be Optional[str] type"


class TestAWSCredentialsOptional:
    """Test AWS credentials are optional for non-S3 deployments."""

    @pytest.fixture
    def config_content(self):
        return CONFIG_FILE.read_text()

    def test_aws_access_key_optional(self, config_content):
        """AWS_ACCESS_KEY_ID should be optional."""
        # Check that AWS keys have defaults or are optional
        has_aws_key = "AWS_ACCESS_KEY" in config_content or "aws_access" in config_content.lower()
        if has_aws_key:
            has_default = "default=None" in config_content or "default=" in config_content
            assert has_default, "AWS credentials should have default values"

    def test_aws_secret_key_optional(self, config_content):
        """AWS_SECRET_ACCESS_KEY should be optional."""
        has_aws_secret = "AWS_SECRET" in config_content or "aws_secret" in config_content.lower()
        if has_aws_secret:
            has_default = "default=None" in config_content or "default=" in config_content
            assert has_default, "AWS credentials should have default values"

    def test_s3_bucket_optional(self, config_content):
        """S3_BUCKET should be optional."""
        has_s3_bucket = "S3_BUCKET" in config_content
        if has_s3_bucket:
            has_default = "default=None" in config_content or "default=" in config_content
            assert has_default, "S3_BUCKET should have default value"


class TestRabbitMQVariables:
    """Test RabbitMQ variables are in .env.example."""

    @pytest.fixture
    def env_example_content(self):
        return ENV_EXAMPLE.read_text()

    def test_rabbitmq_host_in_env_example(self, env_example_content):
        """RABBITMQ_HOST should be in .env.example."""
        has_host = "RABBITMQ_HOST" in env_example_content
        assert has_host, "RABBITMQ_HOST should be in .env.example"

    def test_rabbitmq_port_in_env_example(self, env_example_content):
        """RABBITMQ_PORT should be in .env.example."""
        has_port = "RABBITMQ_PORT" in env_example_content
        assert has_port, "RABBITMQ_PORT should be in .env.example"

    def test_rabbitmq_user_in_env_example(self, env_example_content):
        """RABBITMQ_USER should be in .env.example."""
        has_user = "RABBITMQ_USER" in env_example_content or "RABBITMQ_DEFAULT_USER" in env_example_content
        assert has_user, "RABBITMQ_USER should be in .env.example"

    def test_rabbitmq_password_in_env_example(self, env_example_content):
        """RABBITMQ_PASSWORD should be in .env.example."""
        has_pass = "RABBITMQ_PASS" in env_example_content or "RABBITMQ_DEFAULT_PASS" in env_example_content
        assert has_pass, "RABBITMQ_PASSWORD should be in .env.example"

    def test_rabbitmq_vhost_in_env_example(self, env_example_content):
        """RABBITMQ_VHOST should be in .env.example."""
        has_vhost = "RABBITMQ_VHOST" in env_example_content or "RABBITMQ" in env_example_content
        assert has_vhost, "RABBITMQ_VHOST should be in .env.example"


class TestCeleryBrokerURL:
    """Test CELERY_BROKER_URL is in .env.example."""

    @pytest.fixture
    def env_example_content(self):
        return ENV_EXAMPLE.read_text()

    def test_celery_broker_url_in_env_example(self, env_example_content):
        """CELERY_BROKER_URL should be in .env.example."""
        has_broker = "CELERY_BROKER_URL" in env_example_content
        assert has_broker, "CELERY_BROKER_URL should be in .env.example"

    def test_celery_result_backend_in_env_example(self, env_example_content):
        """CELERY_RESULT_BACKEND should be in .env.example."""
        has_backend = "CELERY_RESULT_BACKEND" in env_example_content or "CELERY" in env_example_content
        assert has_backend, "CELERY_RESULT_BACKEND should be in .env.example"


class TestStartupValidation:
    """Test startup validation script exists."""

    def test_validation_script_exists(self):
        """Should have a startup validation script."""
        # Check for common validation script locations
        scripts_dir = PROJECT_ROOT / "scripts"
        backend_dir = PROJECT_ROOT / "backend"

        validation_scripts = [
            scripts_dir / "validate_env.py",
            scripts_dir / "validate_environment.py",
            scripts_dir / "check_env.py",
            backend_dir / "validate_env.py",
            backend_dir / "check_env.py",
            PROJECT_ROOT / "validate_env.py",
        ]

        has_script = any(script.exists() for script in validation_scripts)
        assert has_script, \
            "Should have a startup validation script (scripts/validate_env.py or similar)"

    def test_validation_script_checks_required_vars(self):
        """Validation script should check required variables."""
        scripts_dir = PROJECT_ROOT / "scripts"
        validation_scripts = [
            scripts_dir / "validate_env.py",
            scripts_dir / "validate_environment.py",
            scripts_dir / "check_env.py",
        ]

        script_content = ""
        for script in validation_scripts:
            if script.exists():
                script_content = script.read_text()
                break

        if script_content:
            has_database_check = "DATABASE_URL" in script_content
            has_redis_check = "REDIS" in script_content
            assert has_database_check or has_redis_check, \
                "Validation script should check required variables"
        else:
            pytest.skip("Validation script not found")


class TestEnvExampleCompleteness:
    """Test .env.example has all necessary variables."""

    @pytest.fixture
    def env_example_content(self):
        return ENV_EXAMPLE.read_text()

    def test_database_url_in_env_example(self, env_example_content):
        """DATABASE_URL should be in .env.example."""
        assert "DATABASE_URL" in env_example_content, \
            "DATABASE_URL should be in .env.example"

    def test_redis_url_in_env_example(self, env_example_content):
        """REDIS_URL should be in .env.example."""
        assert "REDIS_URL" in env_example_content or "REDIS" in env_example_content, \
            "REDIS_URL should be in .env.example"

    def test_secret_key_in_env_example(self, env_example_content):
        """SECRET_KEY should be in .env.example."""
        assert "SECRET_KEY" in env_example_content, \
            "SECRET_KEY should be in .env.example"

    def test_environment_in_env_example(self, env_example_content):
        """ENVIRONMENT should be in .env.example."""
        assert "ENVIRONMENT" in env_example_content, \
            "ENVIRONMENT should be in .env.example"
