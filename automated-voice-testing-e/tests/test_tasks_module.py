"""
Test suite for backend/tasks module structure

Validates the tasks module structure:
- Directory existence
- Module files (__init__.py, orchestration.py, execution.py, validation.py)
- File content and structure
- Import statements
- Task decorators
- Module documentation
"""

import pytest
from pathlib import Path
import sys


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
TASKS_DIR = BACKEND_DIR / "tasks"


class TestTasksDirectoryExists:
    """Test that tasks directory exists"""

    def test_backend_directory_exists(self):
        """Test that backend directory exists"""
        assert BACKEND_DIR.exists(), "backend directory should exist"
        assert BACKEND_DIR.is_dir(), "backend should be a directory"

    def test_tasks_directory_exists(self):
        """Test that tasks directory exists"""
        assert TASKS_DIR.exists(), "backend/tasks directory should exist"
        assert TASKS_DIR.is_dir(), "tasks should be a directory"


class TestTasksModuleFiles:
    """Test that required module files exist"""

    def test_init_file_exists(self):
        """Test that __init__.py exists"""
        init_file = TASKS_DIR / "__init__.py"
        assert init_file.exists(), "backend/tasks/__init__.py should exist"
        assert init_file.is_file(), "__init__.py should be a file"

    def test_orchestration_file_exists(self):
        """Test that orchestration.py exists"""
        orchestration_file = TASKS_DIR / "orchestration.py"
        assert orchestration_file.exists(), "backend/tasks/orchestration.py should exist"
        assert orchestration_file.is_file(), "orchestration.py should be a file"

    def test_execution_file_exists(self):
        """Test that execution.py exists"""
        execution_file = TASKS_DIR / "execution.py"
        assert execution_file.exists(), "backend/tasks/execution.py should exist"
        assert execution_file.is_file(), "execution.py should be a file"

    def test_validation_file_exists(self):
        """Test that validation.py exists"""
        validation_file = TASKS_DIR / "validation.py"
        assert validation_file.exists(), "backend/tasks/validation.py should exist"
        assert validation_file.is_file(), "validation.py should be a file"


class TestInitFileContent:
    """Test __init__.py file content"""

    @pytest.fixture
    def init_content(self):
        """Load __init__.py content"""
        init_file = TASKS_DIR / "__init__.py"
        return init_file.read_text()

    def test_init_has_content(self, init_content):
        """Test that __init__.py has content"""
        # Can be empty or have imports/documentation
        assert init_content is not None, "__init__.py should be readable"

    def test_init_has_documentation(self, init_content):
        """Test that __init__.py has module documentation"""
        assert ('"""' in init_content or "'''" in init_content or "#" in init_content), \
            "__init__.py should have documentation"

    def test_init_imports_celery_app(self, init_content):
        """Test that __init__.py imports celery app"""
        assert "celery" in init_content.lower(), \
            "__init__.py should reference celery"


class TestOrchestrationFileContent:
    """Test orchestration.py file content"""

    @pytest.fixture
    def orchestration_content(self):
        """Load orchestration.py content"""
        orchestration_file = TASKS_DIR / "orchestration.py"
        return orchestration_file.read_text()

    def test_orchestration_has_content(self, orchestration_content):
        """Test that orchestration.py has content"""
        assert len(orchestration_content) > 0, "orchestration.py should not be empty"

    def test_orchestration_has_documentation(self, orchestration_content):
        """Test that orchestration.py has documentation"""
        assert ('"""' in orchestration_content or "'''" in orchestration_content or
                "#" in orchestration_content), \
            "orchestration.py should have documentation"

    def test_orchestration_imports_celery(self, orchestration_content):
        """Test that orchestration.py imports celery"""
        assert "celery" in orchestration_content.lower(), \
            "orchestration.py should import celery"

    def test_orchestration_has_task_decorator(self, orchestration_content):
        """Test that orchestration.py uses task decorator"""
        assert "@" in orchestration_content and "task" in orchestration_content.lower(), \
            "orchestration.py should use @task decorator"

    def test_orchestration_is_valid_python(self, orchestration_content):
        """Test that orchestration.py is valid Python"""
        try:
            compile(orchestration_content, TASKS_DIR / "orchestration.py", 'exec')
        except SyntaxError as e:
            pytest.fail(f"orchestration.py has syntax error: {e}")


class TestExecutionFileContent:
    """Test execution.py file content"""

    @pytest.fixture
    def execution_content(self):
        """Load execution.py content"""
        execution_file = TASKS_DIR / "execution.py"
        return execution_file.read_text()

    def test_execution_has_content(self, execution_content):
        """Test that execution.py has content"""
        assert len(execution_content) > 0, "execution.py should not be empty"

    def test_execution_has_documentation(self, execution_content):
        """Test that execution.py has documentation"""
        assert ('"""' in execution_content or "'''" in execution_content or
                "#" in execution_content), \
            "execution.py should have documentation"

    def test_execution_imports_celery(self, execution_content):
        """Test that execution.py imports celery"""
        assert "celery" in execution_content.lower(), \
            "execution.py should import celery"

    def test_execution_has_task_decorator(self, execution_content):
        """Test that execution.py uses task decorator"""
        assert "@" in execution_content and "task" in execution_content.lower(), \
            "execution.py should use @task decorator"

    def test_execution_is_valid_python(self, execution_content):
        """Test that execution.py is valid Python"""
        try:
            compile(execution_content, TASKS_DIR / "execution.py", 'exec')
        except SyntaxError as e:
            pytest.fail(f"execution.py has syntax error: {e}")


class TestValidationFileContent:
    """Test validation.py file content"""

    @pytest.fixture
    def validation_content(self):
        """Load validation.py content"""
        validation_file = TASKS_DIR / "validation.py"
        return validation_file.read_text()

    def test_validation_has_content(self, validation_content):
        """Test that validation.py has content"""
        assert len(validation_content) > 0, "validation.py should not be empty"

    def test_validation_has_documentation(self, validation_content):
        """Test that validation.py has documentation"""
        assert ('"""' in validation_content or "'''" in validation_content or
                "#" in validation_content), \
            "validation.py should have documentation"

    def test_validation_imports_celery(self, validation_content):
        """Test that validation.py imports celery"""
        assert "celery" in validation_content.lower(), \
            "validation.py should import celery"

    def test_validation_has_task_decorator(self, validation_content):
        """Test that validation.py uses task decorator"""
        assert "@" in validation_content and "task" in validation_content.lower(), \
            "validation.py should use @task decorator"

    def test_validation_is_valid_python(self, validation_content):
        """Test that validation.py is valid Python"""
        try:
            compile(validation_content, TASKS_DIR / "validation.py", 'exec')
        except SyntaxError as e:
            pytest.fail(f"validation.py has syntax error: {e}")


class TestModuleImportability:
    """Test that tasks module can be imported"""

    def test_can_import_tasks_module(self):
        """Test that tasks module can be imported"""
        # Add backend to path
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            import tasks
            assert tasks is not None, "tasks module should be importable"
        except ImportError as e:
            pytest.fail(f"Cannot import tasks module: {e}")

    def test_can_import_orchestration(self):
        """Test that orchestration module can be imported"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from tasks import orchestration
            assert orchestration is not None, "orchestration module should be importable"
        except ImportError as e:
            pytest.fail(f"Cannot import orchestration: {e}")

    def test_can_import_execution(self):
        """Test that execution module can be imported"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from tasks import execution
            assert execution is not None, "execution module should be importable"
        except ImportError as e:
            pytest.fail(f"Cannot import execution: {e}")

    def test_can_import_validation(self):
        """Test that validation module can be imported"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from tasks import validation
            assert validation is not None, "validation module should be importable"
        except ImportError as e:
            pytest.fail(f"Cannot import validation: {e}")


class TestModuleStructure:
    """Test overall module structure"""

    def test_all_required_files_present(self):
        """Test that all required files are present"""
        required_files = ["__init__.py", "orchestration.py", "execution.py", "validation.py"]
        for filename in required_files:
            filepath = TASKS_DIR / filename
            assert filepath.exists(), f"{filename} should exist in tasks directory"

    def test_no_extra_python_files(self):
        """Test that there are no unexpected Python files"""
        # Get all .py files in tasks directory
        py_files = list(TASKS_DIR.glob("*.py"))
        filenames = [f.name for f in py_files]

        expected_files = ["__init__.py", "orchestration.py", "execution.py", "validation.py", "worker_scaling.py", "regression.py", "reporting.py"]

        # All files should be in expected list
        for filename in filenames:
            assert filename in expected_files, \
                f"Unexpected file {filename} in tasks directory"
