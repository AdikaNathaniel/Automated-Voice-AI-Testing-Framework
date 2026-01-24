"""
Test suite for backend/celery_app.py

Validates the celery_app.py file includes proper Celery configuration:
- File structure and imports
- Celery instance creation
- Broker configuration (Redis or RabbitMQ)
- Backend configuration (Redis)
- Task serialization settings
- Timezone configuration
- App name and settings
"""

import pytest
from pathlib import Path
import sys


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
CELERY_APP_FILE = BACKEND_DIR / "celery_app.py"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from celery_app import celery  # noqa: E402


class TestCeleryAppFileExists:
    """Test that celery_app.py exists"""

    def test_backend_directory_exists(self):
        """Test that backend directory exists"""
        assert BACKEND_DIR.exists(), "backend directory should exist"
        assert BACKEND_DIR.is_dir(), "backend should be a directory"

    def test_celery_app_file_exists(self):
        """Test that celery_app.py exists"""
        assert CELERY_APP_FILE.exists(), "backend/celery_app.py should exist"
        assert CELERY_APP_FILE.is_file(), "celery_app.py should be a file"

    def test_celery_app_has_content(self):
        """Test that celery_app.py has content"""
        content = CELERY_APP_FILE.read_text()
        assert len(content) > 0, "celery_app.py should not be empty"


class TestCeleryAppImports:
    """Test necessary imports"""

    @pytest.fixture
    def celery_app_content(self):
        """Load celery_app.py content"""
        return CELERY_APP_FILE.read_text()

    def test_imports_celery(self, celery_app_content):
        """Test that Celery is imported"""
        assert "from celery import Celery" in celery_app_content, "Should import Celery"

    def test_imports_os(self, celery_app_content):
        """Test that os module is imported"""
        # May use os for environment variables
        assert "import os" in celery_app_content or "from os import" in celery_app_content, \
            "Should import os for environment variables"


class TestCeleryInstance:
    """Test Celery instance creation"""

    @pytest.fixture
    def celery_app_content(self):
        """Load celery_app.py content"""
        return CELERY_APP_FILE.read_text()

    def test_creates_celery_instance(self, celery_app_content):
        """Test that Celery instance is created"""
        assert "Celery(" in celery_app_content, "Should create Celery instance"

    def test_celery_instance_named_celery(self, celery_app_content):
        """Test that Celery instance is named 'celery' or 'app'"""
        assert ("celery = Celery(" in celery_app_content or
                "app = Celery(" in celery_app_content), \
            "Celery instance should be named 'celery' or 'app'"

    def test_app_name_is_voice_ai_testing(self, celery_app_content):
        """Test that app name is 'voice_ai_testing'"""
        assert "voice_ai_testing" in celery_app_content, \
            "App name should be 'voice_ai_testing'"


class TestBrokerConfiguration:
    """Test broker configuration"""

    @pytest.fixture
    def celery_app_content(self):
        """Load celery_app.py content"""
        return CELERY_APP_FILE.read_text()

    def test_has_broker_configuration(self, celery_app_content):
        """Test that broker is configured"""
        assert "broker" in celery_app_content.lower(), "Should configure broker"

    def test_broker_uses_redis_or_rabbitmq(self, celery_app_content):
        """Test that broker uses Redis or RabbitMQ"""
        content_lower = celery_app_content.lower()
        assert ("redis://" in content_lower or "amqp://" in content_lower), \
            "Broker should use Redis (redis://) or RabbitMQ (amqp://)"

    def test_broker_config_format(self, celery_app_content):
        """Test that broker is configured with proper format"""
        # Should have broker= or broker_url=
        assert ("broker=" in celery_app_content or "broker_url" in celery_app_content), \
            "Should configure broker URL"


class TestBackendConfiguration:
    """Test result backend configuration"""

    @pytest.fixture
    def celery_app_content(self):
        """Load celery_app.py content"""
        return CELERY_APP_FILE.read_text()

    def test_has_backend_configuration(self, celery_app_content):
        """Test that backend is configured"""
        assert "backend" in celery_app_content.lower(), "Should configure backend"

    def test_backend_uses_redis(self, celery_app_content):
        """Test that backend uses Redis"""
        assert "redis://" in celery_app_content.lower(), \
            "Backend should use Redis (redis://)"

    def test_backend_config_format(self, celery_app_content):
        """Test that backend is configured with proper format"""
        # Should have backend= or result_backend=
        assert ("backend=" in celery_app_content or "result_backend" in celery_app_content), \
            "Should configure result backend"


class TestSerializationConfiguration:
    """Test serialization configuration"""

    @pytest.fixture
    def celery_app_content(self):
        """Load celery_app.py content"""
        return CELERY_APP_FILE.read_text()

    def test_configures_task_serializer(self, celery_app_content):
        """Test that task serializer is configured"""
        assert "task_serializer" in celery_app_content, \
            "Should configure task_serializer"

    def test_task_serializer_is_json(self, celery_app_content):
        """Test that task serializer is set to json"""
        assert "task_serializer" in celery_app_content and "'json'" in celery_app_content, \
            "task_serializer should be 'json'"

    def test_configures_result_serializer(self, celery_app_content):
        """Test that result serializer is configured"""
        assert "result_serializer" in celery_app_content, \
            "Should configure result_serializer"

    def test_result_serializer_is_json(self, celery_app_content):
        """Test that result serializer is set to json"""
        assert "result_serializer" in celery_app_content and "'json'" in celery_app_content, \
            "result_serializer should be 'json'"

    def test_configures_accept_content(self, celery_app_content):
        """Test that accept_content is configured"""
        assert "accept_content" in celery_app_content, \
            "Should configure accept_content"

    def test_accept_content_includes_json(self, celery_app_content):
        """Test that accept_content includes json"""
        assert "accept_content" in celery_app_content and "'json'" in celery_app_content, \
            "accept_content should include 'json'"


class TestTimezoneConfiguration:
    """Test timezone configuration"""

    @pytest.fixture
    def celery_app_content(self):
        """Load celery_app.py content"""
        return CELERY_APP_FILE.read_text()

    def test_configures_timezone(self, celery_app_content):
        """Test that timezone is configured"""
        assert "timezone" in celery_app_content.lower(), \
            "Should configure timezone"

    def test_timezone_is_utc(self, celery_app_content):
        """Test that timezone is set to UTC"""
        assert "timezone" in celery_app_content and "'UTC'" in celery_app_content, \
            "timezone should be 'UTC'"

    def test_configures_enable_utc(self, celery_app_content):
        """Test that enable_utc is configured"""
        assert "enable_utc" in celery_app_content, \
            "Should configure enable_utc"

    def test_enable_utc_is_true(self, celery_app_content):
        """Test that enable_utc is set to True"""
        assert "enable_utc" in celery_app_content and "True" in celery_app_content, \
            "enable_utc should be True"


class TestCeleryBeatSchedule:
    """Tests for Celery beat schedule configuration."""

    def test_auto_scaling_task_registered(self):
        """Ensure auto-scaling task is present in beat schedule."""
        schedule = celery.conf.beat_schedule
        assert "auto-scale-workers" in schedule, "auto-scale-workers task should be scheduled"

        entry = schedule["auto-scale-workers"]
        assert entry["task"] == "tasks.worker_scaling.auto_scale_workers", \
            "auto-scale-workers schedule should target the worker scaling task"
        assert float(entry["schedule"]) > 0, "Schedule interval must be positive"


class TestConfUpdate:
    """Test configuration update method"""

    @pytest.fixture
    def celery_app_content(self):
        """Load celery_app.py content"""
        return CELERY_APP_FILE.read_text()

    def test_uses_conf_update(self, celery_app_content):
        """Test that conf.update() is used for configuration"""
        assert "conf.update" in celery_app_content or ".config_from_object" in celery_app_content, \
            "Should use conf.update() or config_from_object() for configuration"

    def test_conf_update_has_settings(self, celery_app_content):
        """Test that conf.update has settings dict"""
        if "conf.update" in celery_app_content:
            assert "task_serializer" in celery_app_content or "timezone" in celery_app_content, \
                "conf.update should include configuration settings"


class TestEnvironmentVariables:
    """Test environment variable usage"""

    @pytest.fixture
    def celery_app_content(self):
        """Load celery_app.py content"""
        return CELERY_APP_FILE.read_text()

    def test_uses_environment_variables(self, celery_app_content):
        """Test that environment variables are used"""
        # Should use os.getenv or similar
        assert ("os.getenv" in celery_app_content or "os.environ" in celery_app_content), \
            "Should use environment variables for configuration"

    def test_has_default_values(self, celery_app_content):
        """Test that default values are provided"""
        # Should have fallback values
        if "os.getenv" in celery_app_content:
            assert "," in celery_app_content, "os.getenv should have default values"


class TestCeleryAppStructure:
    """Test overall app structure"""

    @pytest.fixture
    def celery_app_content(self):
        """Load celery_app.py content"""
        return CELERY_APP_FILE.read_text()

    def test_is_valid_python(self, celery_app_content):
        """Test that file is valid Python"""
        try:
            compile(celery_app_content, CELERY_APP_FILE, 'exec')
        except SyntaxError as e:
            pytest.fail(f"celery_app.py has syntax error: {e}")

    def test_has_documentation(self, celery_app_content):
        """Test that file has documentation"""
        assert ('"""' in celery_app_content or "'''" in celery_app_content or "#" in celery_app_content), \
            "Should have documentation"

    def test_exports_celery_app(self, celery_app_content):
        """Test that Celery app is exported"""
        # Should have celery = or app = at module level
        assert ("celery = Celery" in celery_app_content or "app = Celery" in celery_app_content), \
            "Should export Celery app instance"


class TestImportability:
    """Test that celery_app can be imported"""

    def test_can_import_celery_app(self):
        """Test that celery_app module can be imported"""
        # Add backend to path
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            import celery_app
            assert hasattr(celery_app, 'celery') or hasattr(celery_app, 'app'), \
                "celery_app module should export 'celery' or 'app'"
        except ImportError as e:
            pytest.fail(f"Cannot import celery_app: {e}")

    def test_celery_instance_is_celery_type(self):
        """Test that exported instance is Celery type"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from celery import Celery
            import celery_app

            app = getattr(celery_app, 'celery', None) or getattr(celery_app, 'app', None)
            assert isinstance(app, Celery), "Exported instance should be Celery type"
        except ImportError as e:
            pytest.fail(f"Cannot import for type check: {e}")
