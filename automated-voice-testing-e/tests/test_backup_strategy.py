"""
Tests for backup strategy configuration (Phase 4.3 Backup & Disaster Recovery).
"""

import os
import yaml
import pytest


@pytest.fixture
def docker_compose_path():
    """Get path to docker-compose.yml."""
    project_root = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(project_root, "docker-compose.yml")


@pytest.fixture
def docker_compose_config(docker_compose_path):
    """Load and parse docker-compose.yml."""
    with open(docker_compose_path) as f:
        return yaml.safe_load(f)


@pytest.fixture
def backup_scripts_dir():
    """Get path to backup scripts directory."""
    project_root = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(project_root, "scripts", "backup")


@pytest.fixture
def env_example_path():
    """Get path to .env.example."""
    project_root = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(project_root, ".env.example")


class TestPostgresBackup:
    """Test PostgreSQL backup configuration."""

    def test_postgres_backup_script_exists(self, backup_scripts_dir):
        """Test that PostgreSQL backup script exists."""
        script_path = os.path.join(backup_scripts_dir, "postgres_backup.sh")
        assert os.path.exists(script_path), \
            f"PostgreSQL backup script not found at {script_path}"

    def test_postgres_backup_script_executable(self, backup_scripts_dir):
        """Test that PostgreSQL backup script is executable."""
        script_path = os.path.join(backup_scripts_dir, "postgres_backup.sh")
        assert os.access(script_path, os.X_OK), \
            "PostgreSQL backup script must be executable"

    def test_postgres_backup_script_has_s3_upload(self, backup_scripts_dir):
        """Test that backup script uploads to S3/MinIO."""
        script_path = os.path.join(backup_scripts_dir, "postgres_backup.sh")
        with open(script_path) as f:
            content = f.read()

        # Should have S3 upload command (aws s3 or mc)
        has_s3 = "aws s3" in content or "mc cp" in content or "s3cmd" in content
        assert has_s3, "Backup script must upload to S3/MinIO"

    def test_postgres_backup_script_has_retention(self, backup_scripts_dir):
        """Test that backup script has retention policy."""
        script_path = os.path.join(backup_scripts_dir, "postgres_backup.sh")
        with open(script_path) as f:
            content = f.read()

        # Should have retention policy (cleanup old backups)
        has_retention = "RETENTION" in content or "find" in content and "delete" in content.lower()
        assert has_retention, "Backup script must implement retention policy"


class TestRedisBackup:
    """Test Redis backup configuration."""

    def test_redis_aof_enabled(self, docker_compose_config):
        """Test that Redis has AOF enabled."""
        redis = docker_compose_config["services"]["redis"]
        command = redis.get("command", "")

        has_aof = "appendonly yes" in command
        assert has_aof, "Redis must have AOF enabled for durability"

    def test_redis_backup_script_exists(self, backup_scripts_dir):
        """Test that Redis backup script exists."""
        script_path = os.path.join(backup_scripts_dir, "redis_backup.sh")
        assert os.path.exists(script_path), \
            f"Redis backup script not found at {script_path}"


class TestMinIOBackup:
    """Test MinIO backup/replication configuration."""

    def test_minio_backup_script_exists(self, backup_scripts_dir):
        """Test that MinIO backup script exists."""
        script_path = os.path.join(backup_scripts_dir, "minio_backup.sh")
        assert os.path.exists(script_path), \
            f"MinIO backup script not found at {script_path}"


class TestBackupSchedule:
    """Test backup schedule configuration."""

    def test_backup_cron_file_exists(self, backup_scripts_dir):
        """Test that backup cron configuration exists."""
        cron_path = os.path.join(backup_scripts_dir, "backup.cron")
        assert os.path.exists(cron_path), \
            f"Backup cron configuration not found at {cron_path}"

    def test_backup_cron_has_daily_schedule(self, backup_scripts_dir):
        """Test that backup cron has daily schedule."""
        cron_path = os.path.join(backup_scripts_dir, "backup.cron")
        with open(cron_path) as f:
            content = f.read()

        # Daily backup typically at 2 AM
        has_daily = "0 2 * * *" in content or "0 3 * * *" in content
        assert has_daily, "Backup cron must have daily schedule"


class TestBackupEnvironmentVariables:
    """Test backup-related environment variables."""

    def test_backup_vars_in_env_example(self, env_example_path):
        """Test that backup environment variables are documented."""
        with open(env_example_path) as f:
            content = f.read()

        required_vars = [
            "BACKUP_RETENTION_DAYS",
            "BACKUP_STORAGE_URL",
        ]

        for var in required_vars:
            assert var in content, \
                f"Environment variable {var} must be documented in .env.example"


class TestRestoreScripts:
    """Test restore scripts exist."""

    def test_postgres_restore_script_exists(self, backup_scripts_dir):
        """Test that PostgreSQL restore script exists."""
        script_path = os.path.join(backup_scripts_dir, "postgres_restore.sh")
        assert os.path.exists(script_path), \
            f"PostgreSQL restore script not found at {script_path}"
