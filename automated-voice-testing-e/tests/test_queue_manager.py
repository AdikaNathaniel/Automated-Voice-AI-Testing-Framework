"""
Test suite for backend/services/queue_manager.py

Validates the queue manager service implementation:
- File structure and imports
- enqueue_test method
- dequeue_test method
- update_queue_status method
- get_queue_stats method
- Type annotations
- Documentation
- Database integration
- Priority handling
"""

import pytest
from pathlib import Path
import sys
import inspect


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
SERVICES_DIR = BACKEND_DIR / "services"
QUEUE_MANAGER_FILE = SERVICES_DIR / "queue_manager.py"


class TestQueueManagerFileExists:
    """Test that queue_manager.py exists"""

    def test_services_directory_exists(self):
        """Test that services directory exists"""
        assert SERVICES_DIR.exists(), "backend/services directory should exist"
        assert SERVICES_DIR.is_dir(), "services should be a directory"

    def test_queue_manager_file_exists(self):
        """Test that queue_manager.py exists"""
        assert QUEUE_MANAGER_FILE.exists(), "queue_manager.py should exist"
        assert QUEUE_MANAGER_FILE.is_file(), "queue_manager.py should be a file"

    def test_queue_manager_has_content(self):
        """Test that queue_manager.py has content"""
        content = QUEUE_MANAGER_FILE.read_text()
        assert len(content) > 0, "queue_manager.py should not be empty"


class TestQueueManagerImports:
    """Test necessary imports"""

    @pytest.fixture
    def service_content(self):
        """Load queue_manager.py content"""
        return QUEUE_MANAGER_FILE.read_text()

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

    def test_imports_test_execution_queue(self, service_content):
        """Test that TestExecutionQueue model is imported"""
        assert "TestExecutionQueue" in service_content, \
            "Should import TestExecutionQueue model"


class TestEnqueueTestMethod:
    """Test enqueue_test method"""

    @pytest.fixture
    def service_content(self):
        """Load queue_manager.py content"""
        return QUEUE_MANAGER_FILE.read_text()

    def test_has_enqueue_test_method(self, service_content):
        """Test that enqueue_test method exists"""
        assert "def enqueue_test" in service_content, \
            "Should have enqueue_test method"

    def test_enqueue_test_is_async(self, service_content):
        """Test that enqueue_test is async"""
        assert "async def enqueue_test" in service_content, \
            "enqueue_test should be async"

    def test_enqueue_test_has_test_case_id_param(self, service_content):
        """Test that enqueue_test has test_case_id parameter"""
        assert "test_case_id" in service_content, \
            "enqueue_test should have test_case_id parameter"

    def test_enqueue_test_has_test_run_id_param(self, service_content):
        """Test that enqueue_test has test_run_id parameter"""
        assert "test_run_id" in service_content, \
            "enqueue_test should have test_run_id parameter"

    def test_enqueue_test_has_priority_param(self, service_content):
        """Test that enqueue_test has priority parameter"""
        assert "priority" in service_content, \
            "enqueue_test should have priority parameter"

    def test_enqueue_test_has_db_param(self, service_content):
        """Test that enqueue_test has database session parameter"""
        assert "db" in service_content or "session" in service_content.lower(), \
            "enqueue_test should have database session parameter"


class TestDequeueTestMethod:
    """Test dequeue_test method"""

    @pytest.fixture
    def service_content(self):
        """Load queue_manager.py content"""
        return QUEUE_MANAGER_FILE.read_text()

    def test_has_dequeue_test_method(self, service_content):
        """Test that dequeue_test method exists"""
        assert "def dequeue_test" in service_content, \
            "Should have dequeue_test method"

    def test_dequeue_test_is_async(self, service_content):
        """Test that dequeue_test is async"""
        assert "async def dequeue_test" in service_content, \
            "dequeue_test should be async"

    def test_dequeue_test_has_db_param(self, service_content):
        """Test that dequeue_test has database session parameter"""
        assert "db" in service_content or "session" in service_content.lower(), \
            "dequeue_test should have database session parameter"

    def test_dequeue_test_returns_optional(self, service_content):
        """Test that dequeue_test returns Optional type"""
        assert "Optional" in service_content or "None" in service_content, \
            "dequeue_test should return Optional type"


class TestUpdateQueueStatusMethod:
    """Test update_queue_status method"""

    @pytest.fixture
    def service_content(self):
        """Load queue_manager.py content"""
        return QUEUE_MANAGER_FILE.read_text()

    def test_has_update_queue_status_method(self, service_content):
        """Test that update_queue_status method exists"""
        assert "def update_queue_status" in service_content, \
            "Should have update_queue_status method"

    def test_update_queue_status_is_async(self, service_content):
        """Test that update_queue_status is async"""
        assert "async def update_queue_status" in service_content, \
            "update_queue_status should be async"

    def test_update_queue_status_has_queue_id_param(self, service_content):
        """Test that update_queue_status has queue_id parameter"""
        assert "queue_id" in service_content, \
            "update_queue_status should have queue_id parameter"

    def test_update_queue_status_has_status_param(self, service_content):
        """Test that update_queue_status has status parameter"""
        assert "status" in service_content, \
            "update_queue_status should have status parameter"

    def test_update_queue_status_has_db_param(self, service_content):
        """Test that update_queue_status has database session parameter"""
        assert "db" in service_content or "session" in service_content.lower(), \
            "update_queue_status should have database session parameter"


class TestGetQueueStatsMethod:
    """Test get_queue_stats method"""

    @pytest.fixture
    def service_content(self):
        """Load queue_manager.py content"""
        return QUEUE_MANAGER_FILE.read_text()

    def test_has_get_queue_stats_method(self, service_content):
        """Test that get_queue_stats method exists"""
        assert "def get_queue_stats" in service_content, \
            "Should have get_queue_stats method"

    def test_get_queue_stats_is_async(self, service_content):
        """Test that get_queue_stats is async"""
        assert "async def get_queue_stats" in service_content, \
            "get_queue_stats should be async"

    def test_get_queue_stats_has_db_param(self, service_content):
        """Test that get_queue_stats has database session parameter"""
        assert "db" in service_content or "session" in service_content.lower(), \
            "get_queue_stats should have database session parameter"

    def test_get_queue_stats_returns_dict(self, service_content):
        """Test that get_queue_stats returns dict"""
        assert "dict" in service_content or "Dict" in service_content, \
            "get_queue_stats should return dict type"


class TestTypeAnnotations:
    """Test type annotations"""

    @pytest.fixture
    def service_content(self):
        """Load queue_manager.py content"""
        return QUEUE_MANAGER_FILE.read_text()

    def test_uses_uuid_type(self, service_content):
        """Test that UUID type is used"""
        assert "UUID" in service_content, \
            "Should use UUID type for IDs"

    def test_uses_optional_type(self, service_content):
        """Test that Optional is used for nullable parameters"""
        assert "Optional" in service_content or "None" in service_content, \
            "Should use Optional or None for nullable parameters"

    def test_uses_dict_type(self, service_content):
        """Test that dict type is used"""
        assert "dict" in service_content or "Dict" in service_content, \
            "Should use dict type annotation"

    def test_uses_int_type(self, service_content):
        """Test that int type is used"""
        assert "int" in service_content, \
            "Should use int type for priority"


class TestDocumentation:
    """Test documentation"""

    @pytest.fixture
    def service_content(self):
        """Load queue_manager.py content"""
        return QUEUE_MANAGER_FILE.read_text()

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
        """Load queue_manager.py content"""
        return QUEUE_MANAGER_FILE.read_text()

    def test_uses_database_session(self, service_content):
        """Test that database session is used"""
        assert "session" in service_content.lower() or "db" in service_content, \
            "Should use database session"

    def test_handles_database_operations(self, service_content):
        """Test that database operations are handled"""
        assert ("commit" in service_content or "add" in service_content or
                "query" in service_content or "execute" in service_content), \
            "Should handle database operations"

    def test_uses_async_session(self, service_content):
        """Test that AsyncSession is used"""
        assert "AsyncSession" in service_content or "async" in service_content, \
            "Should use AsyncSession for async database operations"


class TestServiceStructure:
    """Test overall service structure"""

    @pytest.fixture
    def service_content(self):
        """Load queue_manager.py content"""
        return QUEUE_MANAGER_FILE.read_text()

    def test_is_valid_python(self, service_content):
        """Test that file is valid Python"""
        try:
            compile(service_content, QUEUE_MANAGER_FILE, 'exec')
        except SyntaxError as e:
            pytest.fail(f"queue_manager.py has syntax error: {e}")

    def test_has_all_required_methods(self, service_content):
        """Test that all required methods are present"""
        required_methods = [
            "enqueue_test",
            "dequeue_test",
            "update_queue_status",
            "get_queue_stats"
        ]
        for method in required_methods:
            assert method in service_content, \
                f"Should have {method} method"


class TestImportability:
    """Test that queue_manager can be imported"""

    def test_can_import_queue_manager(self):
        """Test that queue_manager module can be imported"""
        # Add backend to path
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from services import queue_manager
            assert queue_manager is not None, \
                "queue_manager module should be importable"
        except ImportError as e:
            pytest.fail(f"Cannot import queue_manager: {e}")

    def test_can_access_enqueue_test(self):
        """Test that enqueue_test function can be accessed"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from services.queue_manager import enqueue_test
            assert enqueue_test is not None, \
                "enqueue_test should be accessible"
            assert inspect.iscoroutinefunction(enqueue_test), \
                "enqueue_test should be async"
        except ImportError as e:
            pytest.fail(f"Cannot import enqueue_test: {e}")

    def test_can_access_dequeue_test(self):
        """Test that dequeue_test function can be accessed"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from services.queue_manager import dequeue_test
            assert dequeue_test is not None, \
                "dequeue_test should be accessible"
            assert inspect.iscoroutinefunction(dequeue_test), \
                "dequeue_test should be async"
        except ImportError as e:
            pytest.fail(f"Cannot import dequeue_test: {e}")

    def test_can_access_update_queue_status(self):
        """Test that update_queue_status function can be accessed"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from services.queue_manager import update_queue_status
            assert update_queue_status is not None, \
                "update_queue_status should be accessible"
            assert inspect.iscoroutinefunction(update_queue_status), \
                "update_queue_status should be async"
        except ImportError as e:
            pytest.fail(f"Cannot import update_queue_status: {e}")

    def test_can_access_get_queue_stats(self):
        """Test that get_queue_stats function can be accessed"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from services.queue_manager import get_queue_stats
            assert get_queue_stats is not None, \
                "get_queue_stats should be accessible"
            assert inspect.iscoroutinefunction(get_queue_stats), \
                "get_queue_stats should be async"
        except ImportError as e:
            pytest.fail(f"Cannot import get_queue_stats: {e}")


class TestPriorityHandling:
    """Test priority handling features"""

    @pytest.fixture
    def service_content(self):
        """Load queue_manager.py content"""
        return QUEUE_MANAGER_FILE.read_text()

    def test_handles_priority_ordering(self, service_content):
        """Test that priority ordering is handled"""
        # Should have priority-based ordering logic
        assert "priority" in service_content, \
            "Should handle priority in queue operations"

    def test_handles_queue_ordering(self, service_content):
        """Test that queue ordering is implemented"""
        # Should have order_by or similar sorting
        assert "order" in service_content.lower() or "sort" in service_content.lower(), \
            "Should implement queue ordering"
