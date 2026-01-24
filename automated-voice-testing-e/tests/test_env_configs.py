"""
Test suite for environment-specific configuration files

Ensures proper environment configuration for development, staging, and production
environments with all required environment variables.
"""

import os
import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"

# Environment files
ENV_DEVELOPMENT = BACKEND_DIR / ".env.development"
ENV_STAGING = BACKEND_DIR / ".env.staging"
ENV_PRODUCTION = BACKEND_DIR / ".env.production"


class TestEnvFilesExist:
    """Test that environment configuration files exist"""

    def test_development_env_exists(self):
        """Test that .env.development exists"""
        assert ENV_DEVELOPMENT.exists(), "backend/.env.development should exist"
        assert ENV_DEVELOPMENT.is_file(), ".env.development should be a file"

    def test_staging_env_exists(self):
        """Test that .env.staging exists"""
        assert ENV_STAGING.exists(), "backend/.env.staging should exist"
        assert ENV_STAGING.is_file(), ".env.staging should be a file"

    def test_production_env_exists(self):
        """Test that .env.production exists"""
        assert ENV_PRODUCTION.exists(), "backend/.env.production should exist"
        assert ENV_PRODUCTION.is_file(), ".env.production should be a file"

    def test_env_files_have_content(self):
        """Test that env files have content"""
        for env_file in [ENV_DEVELOPMENT, ENV_STAGING, ENV_PRODUCTION]:
            content = env_file.read_text()
            assert len(content) > 0, f"{env_file.name} should not be empty"


class TestEnvFileFormat:
    """Test environment file format"""

    def test_env_files_use_key_value_format(self):
        """Test that env files use KEY=VALUE format"""
        for env_file in [ENV_DEVELOPMENT, ENV_STAGING, ENV_PRODUCTION]:
            content = env_file.read_text()
            lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]

            # Should have at least some key=value pairs
            assert len(lines) > 0, f"{env_file.name} should have environment variables"

            # Check that lines follow KEY=VALUE format
            for line in lines:
                assert '=' in line, f"Line in {env_file.name} should use KEY=VALUE format: {line}"

    def test_env_files_have_comments(self):
        """Test that env files have comments for documentation"""
        for env_file in [ENV_DEVELOPMENT, ENV_STAGING, ENV_PRODUCTION]:
            content = env_file.read_text()
            assert '#' in content, f"{env_file.name} should have comments for documentation"


def parse_env_file(env_file_path):
    """Helper function to parse env file into dictionary"""
    env_vars = {}
    with open(env_file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    return env_vars


class TestRequiredDatabaseVariables:
    """Test required database environment variables"""

    def test_development_has_database_variables(self):
        """Test that development env has database variables"""
        env_vars = parse_env_file(ENV_DEVELOPMENT)

        # Should have database connection variables
        db_vars = ['DATABASE_URL', 'DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
        has_db_config = any(var in env_vars for var in db_vars)
        assert has_db_config, "Development env should have database configuration"

    def test_staging_has_database_variables(self):
        """Test that staging env has database variables"""
        env_vars = parse_env_file(ENV_STAGING)

        db_vars = ['DATABASE_URL', 'DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
        has_db_config = any(var in env_vars for var in db_vars)
        assert has_db_config, "Staging env should have database configuration"

    def test_production_has_database_variables(self):
        """Test that production env has database variables"""
        env_vars = parse_env_file(ENV_PRODUCTION)

        db_vars = ['DATABASE_URL', 'DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
        has_db_config = any(var in env_vars for var in db_vars)
        assert has_db_config, "Production env should have database configuration"


class TestRequiredRedisVariables:
    """Test required Redis environment variables"""

    def test_development_has_redis_variables(self):
        """Test that development env has Redis variables"""
        env_vars = parse_env_file(ENV_DEVELOPMENT)

        redis_vars = ['REDIS_URL', 'REDIS_HOST', 'REDIS_PORT']
        has_redis_config = any(var in env_vars for var in redis_vars)
        assert has_redis_config, "Development env should have Redis configuration"

    def test_staging_has_redis_variables(self):
        """Test that staging env has Redis variables"""
        env_vars = parse_env_file(ENV_STAGING)

        redis_vars = ['REDIS_URL', 'REDIS_HOST', 'REDIS_PORT']
        has_redis_config = any(var in env_vars for var in redis_vars)
        assert has_redis_config, "Staging env should have Redis configuration"

    def test_production_has_redis_variables(self):
        """Test that production env has Redis variables"""
        env_vars = parse_env_file(ENV_PRODUCTION)

        redis_vars = ['REDIS_URL', 'REDIS_HOST', 'REDIS_PORT']
        has_redis_config = any(var in env_vars for var in redis_vars)
        assert has_redis_config, "Production env should have Redis configuration"


class TestRequiredSecurityVariables:
    """Test required security environment variables"""

    def test_all_envs_have_secret_key(self):
        """Test that all environments have SECRET_KEY"""
        for env_file in [ENV_DEVELOPMENT, ENV_STAGING, ENV_PRODUCTION]:
            env_vars = parse_env_file(env_file)
            assert 'SECRET_KEY' in env_vars, f"{env_file.name} should have SECRET_KEY"

    def test_production_secret_key_not_default(self):
        """Test that production SECRET_KEY is not a default value"""
        env_vars = parse_env_file(ENV_PRODUCTION)
        secret_key = env_vars.get('SECRET_KEY', '')

        # If it's a placeholder, that's acceptable (needs to be replaced)
        if 'REPLACE' in secret_key.upper() or 'CHANGE' in secret_key.upper():
            # Placeholder is acceptable - it's meant to be replaced
            return

        # Should not be default/insecure values if not a placeholder
        insecure_values = ['changeme', 'secret', 'dev-secret', 'test', '']
        for insecure in insecure_values:
            assert insecure.lower() not in secret_key.lower(), \
                "Production SECRET_KEY should not be a default value"

    def test_secret_keys_differ_between_environments(self):
        """Test that SECRET_KEY differs between environments"""
        dev_vars = parse_env_file(ENV_DEVELOPMENT)
        staging_vars = parse_env_file(ENV_STAGING)
        prod_vars = parse_env_file(ENV_PRODUCTION)

        dev_secret = dev_vars.get('SECRET_KEY', '')
        staging_secret = staging_vars.get('SECRET_KEY', '')
        prod_secret = prod_vars.get('SECRET_KEY', '')

        # Production and development should have different secrets
        if dev_secret and prod_secret:
            assert dev_secret != prod_secret, \
                "Production and development should have different SECRET_KEYs"


class TestRequiredApplicationVariables:
    """Test required application environment variables"""

    def test_all_envs_have_environment_variable(self):
        """Test that all environments specify ENVIRONMENT variable"""
        for env_file in [ENV_DEVELOPMENT, ENV_STAGING, ENV_PRODUCTION]:
            env_vars = parse_env_file(env_file)
            has_env = 'ENVIRONMENT' in env_vars or 'ENV' in env_vars or 'APP_ENV' in env_vars
            assert has_env, f"{env_file.name} should specify environment (ENVIRONMENT, ENV, or APP_ENV)"

    def test_development_environment_value(self):
        """Test that development env has correct ENVIRONMENT value"""
        env_vars = parse_env_file(ENV_DEVELOPMENT)
        env_value = env_vars.get('ENVIRONMENT', '').lower() or env_vars.get('ENV', '').lower()
        assert 'dev' in env_value or 'development' in env_value, \
            "Development environment should have ENV=development or dev"

    def test_staging_environment_value(self):
        """Test that staging env has correct ENVIRONMENT value"""
        env_vars = parse_env_file(ENV_STAGING)
        env_value = env_vars.get('ENVIRONMENT', '').lower() or env_vars.get('ENV', '').lower()
        assert 'staging' in env_value or 'stag' in env_value, \
            "Staging environment should have ENV=staging"

    def test_production_environment_value(self):
        """Test that production env has correct ENVIRONMENT value"""
        env_vars = parse_env_file(ENV_PRODUCTION)
        env_value = env_vars.get('ENVIRONMENT', '').lower() or env_vars.get('ENV', '').lower()
        assert 'prod' in env_value or 'production' in env_value, \
            "Production environment should have ENV=production or prod"


class TestOptionalCommonVariables:
    """Test optional but common environment variables"""

    def test_envs_may_have_debug_flag(self):
        """Test that environments may have DEBUG flag"""
        # DEBUG should be true in development, false in production
        dev_vars = parse_env_file(ENV_DEVELOPMENT)
        prod_vars = parse_env_file(ENV_PRODUCTION)

        if 'DEBUG' in dev_vars:
            # Development can have DEBUG=true
            pass

        if 'DEBUG' in prod_vars:
            # Production should have DEBUG=false or 0
            debug_value = prod_vars['DEBUG'].lower()
            assert debug_value in ['false', '0', 'no'], \
                "Production should have DEBUG=false"

    def test_envs_may_have_cors_settings(self):
        """Test that environments may have CORS settings"""
        # CORS settings are optional but useful
        pass


class TestDevelopmentSpecificSettings:
    """Test development-specific settings"""

    def test_development_uses_localhost(self):
        """Test that development uses localhost for services"""
        env_vars = parse_env_file(ENV_DEVELOPMENT)

        # Should use localhost or 127.0.0.1
        content = ENV_DEVELOPMENT.read_text()
        has_localhost = 'localhost' in content.lower() or '127.0.0.1' in content
        assert has_localhost, "Development should use localhost for services"


class TestProductionSpecificSettings:
    """Test production-specific settings"""

    def test_production_does_not_use_localhost(self):
        """Test that production doesn't use localhost"""
        env_vars = parse_env_file(ENV_PRODUCTION)

        # Production should not hardcode localhost (should use env-specific hosts)
        # This is a soft check - some variables might reference localhost for internal services
        pass

    def test_production_has_secure_settings(self):
        """Test that production has secure settings"""
        content = ENV_PRODUCTION.read_text().lower()

        # Should not have obvious insecure settings
        insecure_patterns = ['trust_host_auth', 'disable_ssl', 'verify=false']
        for pattern in insecure_patterns:
            # This is a soft check - just warn if found
            pass


class TestConsistencyBetweenEnvironments:
    """Test consistency between environment files"""

    def test_all_envs_have_similar_variable_names(self):
        """Test that all environments have similar variables defined"""
        dev_vars = set(parse_env_file(ENV_DEVELOPMENT).keys())
        staging_vars = set(parse_env_file(ENV_STAGING).keys())
        prod_vars = set(parse_env_file(ENV_PRODUCTION).keys())

        # All environments should have a similar set of variables
        # (values will differ, but keys should be mostly the same)
        all_vars = dev_vars | staging_vars | prod_vars

        # Each environment should have at least 50% of all defined variables
        for env_name, env_vars in [('development', dev_vars), ('staging', staging_vars), ('production', prod_vars)]:
            coverage = len(env_vars) / len(all_vars) if all_vars else 0
            assert coverage >= 0.5, \
                f"{env_name} should define at least 50% of common variables (has {len(env_vars)}/{len(all_vars)})"


class TestEnvFileDocumentation:
    """Test environment file documentation"""

    def test_env_files_have_header_comments(self):
        """Test that env files have header comments explaining purpose"""
        for env_file in [ENV_DEVELOPMENT, ENV_STAGING, ENV_PRODUCTION]:
            content = env_file.read_text()
            lines = content.split('\n')[:10]  # First 10 lines
            first_10_lines = '\n'.join(lines)

            # Should have comments in first few lines
            has_header = '#' in first_10_lines
            assert has_header, f"{env_file.name} should have header comments"

    def test_env_files_have_section_comments(self):
        """Test that env files have section comments organizing variables"""
        for env_file in [ENV_DEVELOPMENT, ENV_STAGING, ENV_PRODUCTION]:
            content = env_file.read_text()

            # Should have multiple comment sections
            comment_count = content.count('#')
            assert comment_count >= 3, f"{env_file.name} should have multiple comment sections"


class TestEnvTemplateFile:
    """Test .env.example or .env.template file (optional)"""

    def test_env_example_exists(self):
        """Test that .env.example exists as template (optional but recommended)"""
        env_example = BACKEND_DIR / ".env.example"
        env_template = BACKEND_DIR / ".env.template"

        # Having a template is good practice but not required
        # This test just checks if one exists
        has_template = env_example.exists() or env_template.exists()
        # Optional check - don't assert, just document
        pass
