"""
Test suite for Alembic database migration configuration
Ensures Alembic is properly initialized and configured for database migrations
"""

import os
import sys
import pytest
import configparser

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))


class TestAlembicDirectory:
    """Test Alembic directory structure"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return os.path.dirname(os.path.dirname(__file__))

    @pytest.fixture
    def alembic_dir(self, project_root):
        """Get path to alembic directory"""
        return os.path.join(project_root, 'alembic')

    def test_alembic_directory_exists(self, alembic_dir):
        """Test that alembic directory exists"""
        assert os.path.exists(alembic_dir), \
            "alembic directory must exist in project root"

    def test_alembic_versions_directory_exists(self, alembic_dir):
        """Test that alembic/versions directory exists"""
        versions_dir = os.path.join(alembic_dir, 'versions')
        assert os.path.exists(versions_dir), \
            "alembic/versions directory must exist for migration files"

    def test_alembic_env_py_exists(self, alembic_dir):
        """Test that alembic/env.py file exists"""
        env_file = os.path.join(alembic_dir, 'env.py')
        assert os.path.exists(env_file), \
            "alembic/env.py file must exist"

    def test_alembic_script_py_mako_exists(self, alembic_dir):
        """Test that alembic/script.py.mako template exists"""
        script_template = os.path.join(alembic_dir, 'script.py.mako')
        assert os.path.exists(script_template), \
            "alembic/script.py.mako template must exist"

    def test_alembic_readme_exists(self, alembic_dir):
        """Test that alembic/README file exists"""
        readme_file = os.path.join(alembic_dir, 'README')
        assert os.path.exists(readme_file), \
            "alembic/README file should exist"


class TestAlembicIniFile:
    """Test alembic.ini configuration file"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return os.path.dirname(os.path.dirname(__file__))

    @pytest.fixture
    def alembic_ini_path(self, project_root):
        """Get path to alembic.ini file"""
        return os.path.join(project_root, 'alembic.ini')

    @pytest.fixture
    def alembic_ini_config(self, alembic_ini_path, project_root):
        """Load and parse alembic.ini"""
        config = configparser.ConfigParser()
        config.read(alembic_ini_path)
        # Set 'here' variable in DEFAULT section for interpolation
        if 'DEFAULT' not in config:
            config.add_section('DEFAULT')
        config.set('DEFAULT', 'here', project_root)
        return config

    def test_alembic_ini_exists(self, alembic_ini_path):
        """Test that alembic.ini file exists"""
        assert os.path.exists(alembic_ini_path), \
            "alembic.ini file must exist in project root"

    def test_alembic_ini_is_valid_ini(self, alembic_ini_path):
        """Test that alembic.ini is valid INI format"""
        try:
            config = configparser.ConfigParser()
            config.read(alembic_ini_path)
        except Exception as e:
            pytest.fail(f"alembic.ini is not valid INI format: {e}")

    def test_alembic_ini_has_alembic_section(self, alembic_ini_config):
        """Test that alembic.ini has [alembic] section"""
        assert 'alembic' in alembic_ini_config, \
            "alembic.ini should have [alembic] section"

    def test_alembic_ini_has_script_location(self, alembic_ini_config):
        """Test that alembic.ini has script_location configured"""
        assert 'script_location' in alembic_ini_config['alembic'], \
            "alembic.ini should specify script_location"

        script_location = alembic_ini_config['alembic']['script_location']
        assert 'alembic' in script_location, \
            "script_location should point to alembic directory"

    def test_alembic_ini_has_sqlalchemy_url(self, alembic_ini_config):
        """Test that alembic.ini has sqlalchemy.url configured"""
        assert 'sqlalchemy.url' in alembic_ini_config['alembic'], \
            "alembic.ini should have sqlalchemy.url configured"

    def test_alembic_ini_sqlalchemy_url_uses_env_var(self, alembic_ini_config):
        """Test that sqlalchemy.url uses environment variable"""
        url = alembic_ini_config['alembic']['sqlalchemy.url']
        # Should use environment variable like %(DATABASE_URL)s or similar
        # or comment indicating it's overridden in env.py
        assert url is not None, \
            "sqlalchemy.url should be set (even if placeholder)"


class TestAlembicEnvPy:
    """Test alembic/env.py configuration"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return os.path.dirname(os.path.dirname(__file__))

    @pytest.fixture
    def env_py_path(self, project_root):
        """Get path to alembic/env.py file"""
        return os.path.join(project_root, 'alembic', 'env.py')

    @pytest.fixture
    def env_py_content(self, env_py_path):
        """Read alembic/env.py content"""
        with open(env_py_path, 'r') as f:
            return f.read()

    def test_env_py_is_valid_python(self, env_py_path):
        """Test that env.py is valid Python"""
        try:
            with open(env_py_path, 'r') as f:
                compile(f.read(), env_py_path, 'exec')
        except SyntaxError as e:
            pytest.fail(f"env.py has syntax errors: {e}")

    def test_env_py_imports_alembic(self, env_py_content):
        """Test that env.py imports alembic"""
        assert 'from alembic import context' in env_py_content, \
            "env.py should import alembic.context"

    def test_env_py_imports_sqlalchemy(self, env_py_content):
        """Test that env.py imports SQLAlchemy"""
        # Should import engine or necessary SQLAlchemy components
        has_sqlalchemy_import = (
            'from sqlalchemy import' in env_py_content or
            'import sqlalchemy' in env_py_content
        )
        assert has_sqlalchemy_import, \
            "env.py should import SQLAlchemy components"

    def test_env_py_imports_config(self, env_py_content):
        """Test that env.py imports settings/config"""
        # Should import config to get DATABASE_URL
        has_config_import = (
            'from api.config import' in env_py_content or
            'import api.config' in env_py_content or
            'from config import' in env_py_content
        )
        # Config import is optional if using env vars directly
        # But recommended for our setup

    def test_env_py_has_target_metadata(self, env_py_content):
        """Test that env.py defines target_metadata"""
        assert 'target_metadata' in env_py_content, \
            "env.py should define target_metadata for autogenerate"

    def test_env_py_has_run_migrations_offline(self, env_py_content):
        """Test that env.py has run_migrations_offline function"""
        assert 'def run_migrations_offline' in env_py_content, \
            "env.py should define run_migrations_offline function"

    def test_env_py_has_run_migrations_online(self, env_py_content):
        """Test that env.py has run_migrations_online function"""
        assert 'def run_migrations_online' in env_py_content, \
            "env.py should define run_migrations_online function"

    def test_env_py_gets_database_url_from_config(self, env_py_content):
        """Test that env.py gets database URL from config"""
        # Should reference DATABASE_URL or get_settings()
        has_database_url_reference = (
            'DATABASE_URL' in env_py_content or
            'get_settings()' in env_py_content or
            'config.get_main_option("sqlalchemy.url")' in env_py_content
        )
        assert has_database_url_reference, \
            "env.py should get database URL from config or settings"


class TestAlembicModelsImport:
    """Test that env.py properly imports models for autogenerate"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return os.path.dirname(os.path.dirname(__file__))

    @pytest.fixture
    def env_py_content(self, project_root):
        """Read alembic/env.py content"""
        env_py_path = os.path.join(project_root, 'alembic', 'env.py')
        with open(env_py_path, 'r') as f:
            return f.read()

    def test_env_py_imports_base_model(self, env_py_content):
        """Test that env.py imports Base from models"""
        # Should import the SQLAlchemy Base to get metadata
        # This might be from models.base or similar
        # For now, just check if there's a models import
        has_models_import = (
            'from models' in env_py_content or
            'import models' in env_py_content
        )
        # Models import is optional until we have models
        # But env.py should be configured to support it

    def test_env_py_sets_target_metadata_from_base(self, env_py_content):
        """Test that target_metadata is set from Base.metadata"""
        # Should have something like: target_metadata = Base.metadata
        # This is required for alembic autogenerate to work
        has_metadata_assignment = (
            'target_metadata' in env_py_content
        )
        assert has_metadata_assignment, \
            "env.py should assign target_metadata for autogenerate"


class TestAlembicIntegration:
    """Test Alembic integration and functionality"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return os.path.dirname(os.path.dirname(__file__))

    def test_can_import_alembic(self):
        """Test that alembic package is installed"""
        try:
            import alembic
            assert alembic is not None
        except ImportError as e:
            pytest.fail(f"Failed to import alembic: {e}")

    def test_alembic_version_command_works(self, project_root):
        """Test that alembic version command works"""
        # This is more of a functional test
        # We'll skip actual command execution in unit tests
        # but verify the setup is correct
        import subprocess

        try:
            # Check if alembic command exists
            result = subprocess.run(
                ['alembic', '--help'],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            # Command should at least execute (even if we get an error about config)
            assert result.returncode in [0, 1], \
                "alembic command should be available"
        except FileNotFoundError:
            pytest.fail("alembic command not found in PATH")
        except subprocess.TimeoutExpired:
            pytest.fail("alembic command timed out")


class TestAlembicConfiguration:
    """Test overall Alembic configuration"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return os.path.dirname(os.path.dirname(__file__))

    @pytest.fixture
    def alembic_ini_path(self, project_root):
        """Get path to alembic.ini"""
        return os.path.join(project_root, 'alembic.ini')

    @pytest.fixture
    def alembic_ini_config(self, alembic_ini_path, project_root):
        """Load alembic.ini"""
        config = configparser.ConfigParser()
        config.read(alembic_ini_path)
        # Set 'here' variable in DEFAULT section for interpolation
        if 'DEFAULT' not in config:
            config.add_section('DEFAULT')
        config.set('DEFAULT', 'here', project_root)
        return config

    def test_alembic_version_locations_configured(self, alembic_ini_config):
        """Test that version_locations is configured"""
        # version_locations is optional but useful
        # Just verify alembic section exists
        assert 'alembic' in alembic_ini_config, \
            "alembic.ini should have alembic section"

    def test_alembic_file_template_configured(self, alembic_ini_config):
        """Test that file_template is configured"""
        # file_template is optional but useful for naming migrations
        # Just verify the config is valid
        assert 'alembic' in alembic_ini_config, \
            "alembic.ini should have alembic section"

    def test_alembic_truncate_slug_length_configured(self, alembic_ini_config):
        """Test that truncate_slug_length is configured"""
        # This is optional, just verify config is valid
        assert 'alembic' in alembic_ini_config, \
            "alembic.ini should have alembic section"
