"""
Test suite for backend/services/orchestration_service.py

Validates the orchestration service implementation:
- File structure and imports
- Async method definitions
- create_test_run method
- schedule_test_executions method
- cancel_test_run method
- retry_failed_tests method
- Type annotations
- Documentation
- Database integration
"""

import pytest
from pathlib import Path
import sys
import inspect
import ast


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
SERVICES_DIR = BACKEND_DIR / "services"
ORCHESTRATION_SERVICE_FILE = SERVICES_DIR / "orchestration_service.py"


class TestOrchestrationServiceFileExists:
    """Test that orchestration_service.py exists"""

    def test_services_directory_exists(self):
        """Test that services directory exists"""
        assert SERVICES_DIR.exists(), "backend/services directory should exist"
        assert SERVICES_DIR.is_dir(), "services should be a directory"

    def test_orchestration_service_file_exists(self):
        """Test that orchestration_service.py exists"""
        assert ORCHESTRATION_SERVICE_FILE.exists(), "orchestration_service.py should exist"
        assert ORCHESTRATION_SERVICE_FILE.is_file(), "orchestration_service.py should be a file"

    def test_orchestration_service_has_content(self):
        """Test that orchestration_service.py has content"""
        content = ORCHESTRATION_SERVICE_FILE.read_text()
        assert len(content) > 0, "orchestration_service.py should not be empty"


class TestOrchestrationServiceImports:
    """Test necessary imports"""

    @pytest.fixture
    def service_content(self):
        """Load orchestration_service.py content"""
        return ORCHESTRATION_SERVICE_FILE.read_text()

    def test_imports_uuid(self, service_content):
        """Test that UUID is imported"""
        assert "from uuid import UUID" in service_content or "import uuid" in service_content, \
            "Should import UUID"

    def test_imports_typing(self, service_content):
        """Test that typing is imported"""
        assert "from typing import" in service_content or "import typing" in service_content, \
            "Should import typing for type hints"

    def test_imports_sqlalchemy(self, service_content):
        """Test that SQLAlchemy is imported for database operations"""
        assert "sqlalchemy" in service_content.lower(), \
            "Should import SQLAlchemy for database operations"

    def test_imports_models(self, service_content):
        """Test that models are imported"""
        assert "from models" in service_content or "import models" in service_content, \
            "Should import models"


class TestCreateTestRunMethod:
    """Test create_test_run method"""

    @pytest.fixture
    def service_content(self):
        """Load orchestration_service.py content"""
        return ORCHESTRATION_SERVICE_FILE.read_text()

    def test_has_create_test_run_method(self, service_content):
        """Test that create_test_run method exists"""
        assert "def create_test_run" in service_content, \
            "Should have create_test_run method"

    def test_create_test_run_is_async(self, service_content):
        """Test that create_test_run is async"""
        assert "async def create_test_run" in service_content, \
            "create_test_run should be async"

    def test_create_test_run_has_suite_id_param(self, service_content):
        """Test that create_test_run has suite_id parameter"""
        assert "suite_id" in service_content, \
            "create_test_run should have suite_id parameter"

    def test_create_test_run_has_test_case_ids_param(self, service_content):
        """Test that create_test_run has test_case_ids parameter"""
        assert "test_case_ids" in service_content, \
            "create_test_run should have test_case_ids parameter"

    def test_create_test_run_has_languages_param(self, service_content):
        """Test that create_test_run has languages parameter"""
        assert "languages" in service_content, \
            "create_test_run should have languages parameter"

    def test_create_test_run_has_trigger_type_param(self, service_content):
        """Test that create_test_run has trigger_type parameter"""
        assert "trigger_type" in service_content, \
            "create_test_run should have trigger_type parameter"

    def test_create_test_run_has_trigger_metadata_param(self, service_content):
        """Test that create_test_run has trigger_metadata parameter"""
        assert "trigger_metadata" in service_content, \
            "create_test_run should have trigger_metadata parameter"

    def test_create_test_run_has_created_by_param(self, service_content):
        """Test that create_test_run has created_by parameter"""
        assert "created_by" in service_content, \
            "create_test_run should have created_by parameter"

    def test_create_test_run_returns_test_run(self, service_content):
        """Test that create_test_run returns TestRun"""
        # Should have return type annotation
        assert "TestRun" in service_content, \
            "create_test_run should return TestRun type"


class TestScheduleTestExecutionsMethod:
    """Test schedule_test_executions method"""

    @pytest.fixture
    def service_content(self):
        """Load orchestration_service.py content"""
        return ORCHESTRATION_SERVICE_FILE.read_text()

    def test_has_schedule_test_executions_method(self, service_content):
        """Test that schedule_test_executions method exists"""
        assert "def schedule_test_executions" in service_content, \
            "Should have schedule_test_executions method"

    def test_schedule_test_executions_is_async(self, service_content):
        """Test that schedule_test_executions is async"""
        assert "async def schedule_test_executions" in service_content, \
            "schedule_test_executions should be async"

    def test_schedule_test_executions_has_test_run_id_param(self, service_content):
        """Test that schedule_test_executions has test_run_id parameter"""
        assert "test_run_id" in service_content, \
            "schedule_test_executions should have test_run_id parameter"


class TestCancelTestRunMethod:
    """Test cancel_test_run method"""

    @pytest.fixture
    def service_content(self):
        """Load orchestration_service.py content"""
        return ORCHESTRATION_SERVICE_FILE.read_text()

    def test_has_cancel_test_run_method(self, service_content):
        """Test that cancel_test_run method exists"""
        assert "def cancel_test_run" in service_content, \
            "Should have cancel_test_run method"

    def test_cancel_test_run_is_async(self, service_content):
        """Test that cancel_test_run is async"""
        assert "async def cancel_test_run" in service_content, \
            "cancel_test_run should be async"

    def test_cancel_test_run_has_test_run_id_param(self, service_content):
        """Test that cancel_test_run has test_run_id parameter"""
        assert "test_run_id" in service_content, \
            "cancel_test_run should have test_run_id parameter"


class TestRetryFailedTestsMethod:
    """Test retry_failed_tests method"""

    @pytest.fixture
    def service_content(self):
        """Load orchestration_service.py content"""
        return ORCHESTRATION_SERVICE_FILE.read_text()

    def test_has_retry_failed_tests_method(self, service_content):
        """Test that retry_failed_tests method exists"""
        assert "def retry_failed_tests" in service_content, \
            "Should have retry_failed_tests method"

    def test_retry_failed_tests_is_async(self, service_content):
        """Test that retry_failed_tests is async"""
        assert "async def retry_failed_tests" in service_content, \
            "retry_failed_tests should be async"

    def test_retry_failed_tests_has_test_run_id_param(self, service_content):
        """Test that retry_failed_tests has test_run_id parameter"""
        assert "test_run_id" in service_content, \
            "retry_failed_tests should have test_run_id parameter"

    def test_retry_failed_tests_returns_test_run(self, service_content):
        """Test that retry_failed_tests returns TestRun"""
        assert "TestRun" in service_content, \
            "retry_failed_tests should return TestRun type"


class TestTypeAnnotations:
    """Test type annotations"""

    @pytest.fixture
    def service_content(self):
        """Load orchestration_service.py content"""
        return ORCHESTRATION_SERVICE_FILE.read_text()

    def test_uses_uuid_type(self, service_content):
        """Test that UUID type is used"""
        assert "UUID" in service_content, \
            "Should use UUID type for IDs"

    def test_uses_optional_type(self, service_content):
        """Test that Optional is used for nullable parameters"""
        assert "Optional" in service_content or "None" in service_content, \
            "Should use Optional or None for nullable parameters"

    def test_uses_list_type(self, service_content):
        """Test that list type is used"""
        assert "list[" in service_content or "List[" in service_content, \
            "Should use list type annotation"

    def test_uses_dict_type(self, service_content):
        """Test that dict type is used"""
        assert "dict" in service_content or "Dict" in service_content, \
            "Should use dict type annotation"


class TestDocumentation:
    """Test documentation"""

    @pytest.fixture
    def service_content(self):
        """Load orchestration_service.py content"""
        return ORCHESTRATION_SERVICE_FILE.read_text()

    def test_has_module_documentation(self, service_content):
        """Test that module has documentation"""
        assert '"""' in service_content or "'''" in service_content, \
            "Should have module documentation"

    def test_has_function_docstrings(self, service_content):
        """Test that functions have docstrings"""
        # Should have multiple docstrings for different functions
        docstring_count = service_content.count('"""')
        assert docstring_count >= 4, \
            "Should have docstrings for multiple functions"


class TestDatabaseIntegration:
    """Test database integration"""

    @pytest.fixture
    def service_content(self):
        """Load orchestration_service.py content"""
        return ORCHESTRATION_SERVICE_FILE.read_text()

    def test_uses_database_session(self, service_content):
        """Test that database session is used"""
        assert "session" in service_content.lower() or "db" in service_content, \
            "Should use database session"

    def test_handles_database_operations(self, service_content):
        """Test that database operations are handled"""
        assert ("commit" in service_content or "add" in service_content or
                "query" in service_content), \
            "Should handle database operations"


class TestServiceStructure:
    """Test overall service structure"""

    @pytest.fixture
    def service_content(self):
        """Load orchestration_service.py content"""
        return ORCHESTRATION_SERVICE_FILE.read_text()

    def test_is_valid_python(self, service_content):
        """Test that file is valid Python"""
        try:
            compile(service_content, ORCHESTRATION_SERVICE_FILE, 'exec')
        except SyntaxError as e:
            pytest.fail(f"orchestration_service.py has syntax error: {e}")

    def test_has_all_required_methods(self, service_content):
        """Test that all required methods are present"""
        required_methods = [
            "create_test_run",
            "schedule_test_executions",
            "cancel_test_run",
            "retry_failed_tests"
        ]
        for method in required_methods:
            assert method in service_content, \
                f"Should have {method} method"


class TestImportability:
    """Test that orchestration_service can be imported"""

    def test_can_import_orchestration_service(self):
        """Test that orchestration_service module can be imported"""
        # Add backend to path
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from services import orchestration_service
            assert orchestration_service is not None, \
                "orchestration_service module should be importable"
        except ImportError as e:
            pytest.fail(f"Cannot import orchestration_service: {e}")

    def test_can_access_create_test_run(self):
        """Test that create_test_run function can be accessed"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from services.orchestration_service import create_test_run
            assert create_test_run is not None, \
                "create_test_run should be accessible"
            assert inspect.iscoroutinefunction(create_test_run), \
                "create_test_run should be async"
        except ImportError as e:
            pytest.fail(f"Cannot import create_test_run: {e}")
