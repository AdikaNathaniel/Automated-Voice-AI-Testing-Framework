"""
Tests for service file docstring coverage (Phase 5.2 Code Documentation).
"""

import os
import re
import pytest


@pytest.fixture
def services_dir():
    """Get services directory path."""
    project_root = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(project_root, "backend", "services")


@pytest.fixture
def service_files(services_dir):
    """Get list of service files."""
    if not os.path.exists(services_dir):
        return []
    files = []
    for filename in os.listdir(services_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            files.append(os.path.join(services_dir, filename))
    return files


class TestServiceModuleDocstrings:
    """Test that service modules have module-level docstrings."""

    def test_service_files_have_module_docstrings(self, service_files):
        """Test that service files have module-level docstrings."""
        if not service_files:
            pytest.skip("No service files found")

        files_with_docstrings = 0

        for filepath in service_files:
            with open(filepath) as f:
                content = f.read()

            # Module docstring should be at the start (after optional comments/encoding)
            # Look for triple quotes near the beginning
            has_module_docstring = bool(re.match(r'^[\s\S]*?"""[\s\S]+?"""', content[:500]))

            if has_module_docstring:
                files_with_docstrings += 1

        # At least 20% should have module docstrings (baseline)
        if len(service_files) > 0:
            coverage = files_with_docstrings / len(service_files) * 100
            assert coverage >= 20, \
                f"Only {coverage:.1f}% service files have module docstrings ({files_with_docstrings}/{len(service_files)})"


class TestServiceClassDocstrings:
    """Test that service classes have docstrings."""

    def test_service_classes_have_docstrings(self, service_files):
        """Test that service classes have docstrings."""
        if not service_files:
            pytest.skip("No service files found")

        classes_with_docstrings = 0
        total_classes = 0

        for filepath in service_files:
            with open(filepath) as f:
                content = f.read()

            # Find all class definitions
            class_pattern = r'class\s+\w+[^:]*:'
            classes = re.findall(class_pattern, content)
            total_classes += len(classes)

            # Check for docstrings after class definitions
            docstring_pattern = r'class\s+\w+[^:]*:\s*\n\s+"""'
            classes_with_docs = len(re.findall(docstring_pattern, content))
            classes_with_docstrings += classes_with_docs

        # At least 30% should have docstrings
        if total_classes > 0:
            coverage = classes_with_docstrings / total_classes * 100
            assert coverage >= 30, \
                f"Only {coverage:.1f}% service classes have docstrings ({classes_with_docstrings}/{total_classes})"


class TestServiceMethodDocstrings:
    """Test that service methods have docstrings."""

    def test_public_methods_have_docstrings(self, service_files):
        """Test that public methods have docstrings."""
        if not service_files:
            pytest.skip("No service files found")

        methods_with_docstrings = 0
        total_methods = 0

        for filepath in service_files:
            with open(filepath) as f:
                content = f.read()

            # Find public methods (not starting with _)
            method_pattern = r'def\s+(?!_)\w+'
            methods = re.findall(method_pattern, content)
            total_methods += len(methods)

            # Check for docstrings after method definitions
            docstring_pattern = r'def\s+(?!_)\w+[^:]*:\s*\n\s+"""'
            methods_with_docs = len(re.findall(docstring_pattern, content, re.DOTALL))
            methods_with_docstrings += methods_with_docs

        # At least 15% should have docstrings (baseline for large codebase)
        if total_methods > 0:
            coverage = methods_with_docstrings / total_methods * 100
            assert coverage >= 15, \
                f"Only {coverage:.1f}% public methods have docstrings ({methods_with_docstrings}/{total_methods})"


class TestModelDocstrings:
    """Test that model classes have docstrings."""

    @pytest.fixture
    def models_dir(self):
        """Get models directory path."""
        project_root = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(project_root, "backend", "models")

    @pytest.fixture
    def model_files(self, models_dir):
        """Get list of model files."""
        if not os.path.exists(models_dir):
            return []
        files = []
        for filename in os.listdir(models_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                files.append(os.path.join(models_dir, filename))
        return files

    def test_model_classes_have_docstrings(self, model_files):
        """Test that model classes have docstrings."""
        if not model_files:
            pytest.skip("No model files found")

        classes_with_docstrings = 0
        total_classes = 0

        for filepath in model_files:
            with open(filepath) as f:
                content = f.read()

            # Find all class definitions
            class_pattern = r'class\s+\w+[^:]*:'
            classes = re.findall(class_pattern, content)
            total_classes += len(classes)

            # Check for docstrings after class definitions
            docstring_pattern = r'class\s+\w+[^:]*:\s*\n\s+"""'
            classes_with_docs = len(re.findall(docstring_pattern, content))
            classes_with_docstrings += classes_with_docs

        # At least 20% should have docstrings
        if total_classes > 0:
            coverage = classes_with_docstrings / total_classes * 100
            assert coverage >= 20, \
                f"Only {coverage:.1f}% model classes have docstrings ({classes_with_docstrings}/{total_classes})"


class TestAPIRouteDocstrings:
    """Test that API route functions have docstrings."""

    @pytest.fixture
    def routes_dir(self):
        """Get routes directory path."""
        project_root = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(project_root, "backend", "api", "routes")

    @pytest.fixture
    def route_files(self, routes_dir):
        """Get list of route files."""
        if not os.path.exists(routes_dir):
            return []
        files = []
        for filename in os.listdir(routes_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                files.append(os.path.join(routes_dir, filename))
        return files

    def test_route_functions_have_docstrings(self, route_files):
        """Test that route functions have docstrings."""
        if not route_files:
            pytest.skip("No route files found")

        functions_with_docstrings = 0
        total_functions = 0

        for filepath in route_files:
            with open(filepath) as f:
                content = f.read()

            # Find async def functions (route handlers)
            function_pattern = r'async def \w+'
            functions = re.findall(function_pattern, content)
            total_functions += len(functions)

            # Check for docstrings after function definitions
            # Pattern handles multi-line signatures with return type annotations
            docstring_pattern = r'async def \w+\([^)]*(?:\)[^)]*)*\)[^:]*:\s*\n\s+"""'
            functions_with_docs = len(re.findall(docstring_pattern, content, re.DOTALL))
            functions_with_docstrings += functions_with_docs

        # At least 5% should have docstrings (baseline - scenarios.py has good coverage)
        if total_functions > 0:
            coverage = functions_with_docstrings / total_functions * 100
            assert coverage >= 5, \
                f"Only {coverage:.1f}% route functions have docstrings ({functions_with_docstrings}/{total_functions})"
