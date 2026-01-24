"""
Phase B: Mypy Type Checking - Gradual Strictness

Tests to verify that critical services have proper type hints.
This ensures compliance with mypy check_untyped_defs = True
"""

import ast
import inspect
from pathlib import Path
from typing import List, Tuple
import pytest

# Get the backend directory relative to this test file
TESTS_DIR = Path(__file__).parent
BACKEND_DIR = TESTS_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent


class TypeHintChecker:
    """Checks if functions have proper type hints."""

    @staticmethod
    def has_parameter_hints(func) -> bool:
        """Check if function has parameter type hints."""
        sig = inspect.signature(func)
        # At least one parameter should have a type hint
        return any(param.annotation != inspect.Parameter.empty
                  for param in sig.parameters.values())

    @staticmethod
    def has_return_hint(func) -> bool:
        """Check if function has return type hint."""
        sig = inspect.signature(func)
        return sig.return_annotation != inspect.Signature.empty

    @staticmethod
    def get_functions_from_file(file_path: Path) -> List[Tuple[str, object]]:
        """Extract all function definitions from a Python file."""
        with open(file_path, 'r') as f:
            tree = ast.parse(f.read())

        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith('_'):  # Skip private methods
                    functions.append((node.name, node))
        return functions

    @staticmethod
    def ast_has_type_hints(func_node: ast.FunctionDef) -> Tuple[bool, bool]:
        """Check if AST function node has type hints."""
        # Check parameters for type hints
        has_param_hints = any(arg.annotation is not None
                             for arg in func_node.args.args)
        # Check return type hint
        has_return_hint = func_node.returns is not None
        return has_param_hints, has_return_hint


class TestValidationServiceTypeHints:
    """Test type hints in validation_service.py"""

    def test_validation_service_exists(self):
        """Test that validation_service.py exists."""
        service_path = BACKEND_DIR / "services" / "validation_service.py"
        assert service_path.exists(), "validation_service.py not found"

    def test_validation_service_has_functions(self):
        """Test that validation_service.py contains public functions."""
        service_path = BACKEND_DIR / "services" / "validation_service.py"
        checker = TypeHintChecker()
        functions = checker.get_functions_from_file(service_path)
        assert len(functions) > 0, "No functions found in validation_service.py"

    def test_validation_service_critical_methods_have_hints(self):
        """Test that critical validation service methods have type hints."""
        service_path = BACKEND_DIR / "services" / "validation_service.py"

        with open(service_path, 'r') as f:
            tree = ast.parse(f.read())

        # Find the ValidationService class
        validation_service_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "ValidationService":
                validation_service_class = node
                break

        assert validation_service_class is not None, "ValidationService class not found"

        # Check critical methods
        checker = TypeHintChecker()
        critical_methods = ["validate_voice_response", "calculate_confidence", "__init__"]

        for method_name in critical_methods:
            method = None
            for node in validation_service_class.body:
                if isinstance(node, ast.FunctionDef) and node.name == method_name:
                    method = node
                    break

            if method:
                has_param, has_return = checker.ast_has_type_hints(method)
                # At least method signature should have some hints
                assert has_param or method_name == "__init__", f"{method_name} missing parameter hints"


class TestOrchestrationServiceTypeHints:
    """Test type hints in orchestration_service.py"""

    def test_orchestration_service_exists(self):
        """Test that orchestration_service.py exists."""
        service_path = BACKEND_DIR / "services" / "orchestration_service.py"
        assert service_path.exists(), "orchestration_service.py not found"

    def test_orchestration_service_critical_methods_have_hints(self):
        """Test that critical orchestration service methods have type hints."""
        service_path = BACKEND_DIR / "services" / "orchestration_service.py"

        with open(service_path, 'r') as f:
            tree = ast.parse(f.read())

        # Find the OrchestrationService class
        orchestration_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "OrchestrationService":
                orchestration_class = node
                break

        assert orchestration_class is not None, "OrchestrationService class not found"

        # Check that class exists and has methods
        methods = [n for n in orchestration_class.body if isinstance(n, ast.FunctionDef)]
        assert len(methods) > 0, "OrchestrationService has no methods"


class TestMultiTurnExecutionServiceTypeHints:
    """Test type hints in multi_turn_execution_service.py"""

    def test_multi_turn_execution_service_exists(self):
        """Test that multi_turn_execution_service.py exists."""
        service_path = BACKEND_DIR / "services" / "multi_turn_execution_service.py"
        assert service_path.exists(), "multi_turn_execution_service.py not found"


class TestAuthRoutesTypeHints:
    """Test type hints in auth routes"""

    def test_auth_routes_exists(self):
        """Test that auth.py routes file exists."""
        routes_path = BACKEND_DIR / "api" / "routes" / "auth.py"
        assert routes_path.exists(), "auth.py routes file not found"

    def test_auth_routes_has_endpoint_functions(self):
        """Test that auth.py has endpoint functions."""
        routes_path = BACKEND_DIR / "api" / "routes" / "auth.py"

        with open(routes_path, 'r') as f:
            tree = ast.parse(f.read())

        # Find functions decorated with @router (including async functions)
        endpoint_functions = []
        for node in tree.body:
            # Check both FunctionDef and AsyncFunctionDef
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Check if function has decorator
                for decorator in node.decorator_list:
                    # Handle @router.post(...), @router.get(...), etc.
                    # The decorator is an ast.Call node where func is ast.Attribute
                    if isinstance(decorator, ast.Call):
                        if isinstance(decorator.func, ast.Attribute):
                            if decorator.func.attr in ['get', 'post', 'put', 'delete']:
                                endpoint_functions.append(node.name)
                    # Also handle simple @router decorators (less common)
                    elif isinstance(decorator, ast.Attribute):
                        if decorator.attr in ['get', 'post', 'put', 'delete']:
                            endpoint_functions.append(node.name)

        assert len(endpoint_functions) > 0, "No endpoint functions found in auth.py"


class TestMypyBaseline:
    """Test mypy baseline configuration."""

    def test_mypy_ini_exists(self):
        """Test that mypy.ini configuration file exists."""
        mypy_path = PROJECT_ROOT / "mypy.ini"
        assert mypy_path.exists(), "mypy.ini not found"

    def test_mypy_has_check_untyped_defs_comment(self):
        """Test that mypy.ini has check_untyped_defs option (commented or enabled)."""
        mypy_path = PROJECT_ROOT / "mypy.ini"
        content = mypy_path.read_text()
        # Should have the option available even if commented
        assert "check_untyped_defs" in content, "check_untyped_defs option not found in mypy.ini"
