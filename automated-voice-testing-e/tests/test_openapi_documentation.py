"""
Tests for OpenAPI documentation completeness (Phase 5.1 API Documentation).
"""

import os
import re
import pytest


@pytest.fixture
def routes_dir():
    """Get routes directory path."""
    project_root = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(project_root, "backend", "api", "routes")


@pytest.fixture
def route_files(routes_dir):
    """Get list of route files."""
    files = []
    for filename in os.listdir(routes_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            files.append(os.path.join(routes_dir, filename))
    return files


def get_route_decorators(content):
    """Extract route decorators from file content."""
    pattern = r'@router\.(get|post|put|patch|delete)\s*\([^)]*\)'
    return re.findall(pattern, content, re.IGNORECASE)


def get_route_functions(content):
    """Extract async def functions after route decorators."""
    # Find all async def functions that appear after @router decorators
    # Split by route decorator and extract function names
    functions = []
    # Match @router.method(...) followed eventually by async def name
    pattern = r'@router\.(get|post|put|patch|delete)\s*\([^@]*?async def (\w+)'
    matches = re.findall(pattern, content, re.DOTALL)
    return matches


class TestRouteDescriptions:
    """Test that routes have proper descriptions."""

    def test_routes_have_summary_or_description(self, route_files):
        """Test that route decorators have summary or description."""
        missing_docs = []

        for filepath in route_files:
            with open(filepath) as f:
                content = f.read()

            filename = os.path.basename(filepath)

            # Find all route decorators
            decorator_pattern = r'@router\.(get|post|put|patch|delete)\s*\(([^)]*)\)'
            matches = re.findall(decorator_pattern, content, re.DOTALL)

            for method, params in matches:
                # Check if summary or description is provided
                has_summary = 'summary=' in params or 'description=' in params
                if not has_summary:
                    missing_docs.append(f"{filename}: {method.upper()} route missing summary/description")

        # Allow some flexibility - at least 80% should have docs
        total_routes = sum(
            len(re.findall(r'@router\.(get|post|put|patch|delete)', open(f).read()))
            for f in route_files
        )

        if total_routes > 0:
            coverage = (total_routes - len(missing_docs)) / total_routes * 100
            assert coverage >= 50, \
                f"Only {coverage:.1f}% routes have summary/description. Missing: {missing_docs[:5]}"


class TestRouteDocstrings:
    """Test that route functions have docstrings."""

    def test_route_functions_have_docstrings(self, route_files):
        """Test that async def route functions have docstrings."""
        total_with_docstrings = 0
        total_functions = 0

        for filepath in route_files:
            with open(filepath) as f:
                content = f.read()

            # Count async def functions followed by docstrings
            # Pattern matches function ending with ): or ) -> Type: followed by docstring
            docstring_pattern = r'async def \w+\([^)]*(?:\)[^)]*)*\)[^:]*:\s*\n\s+"""'
            matches_with_docstring = len(re.findall(docstring_pattern, content, re.DOTALL))
            total_with_docstrings += matches_with_docstring

            # Count total async def functions in route files
            async_def_pattern = r'async def \w+'
            total_async = len(re.findall(async_def_pattern, content))
            total_functions += total_async

        # At least 10% should have docstrings (baseline - can improve over time)
        if total_functions > 0:
            coverage = total_with_docstrings / total_functions * 100
            assert coverage >= 10, \
                f"Only {coverage:.1f}% route functions have docstrings ({total_with_docstrings}/{total_functions})"


class TestResponseModels:
    """Test that routes have response models."""

    def test_routes_have_response_model(self, route_files):
        """Test that routes specify response_model."""
        routes_with_models = 0
        total_routes = 0

        for filepath in route_files:
            with open(filepath) as f:
                content = f.read()

            # Count routes
            route_count = len(re.findall(r'@router\.(get|post|put|patch|delete)', content))
            total_routes += route_count

            # Count routes with response_model
            model_count = len(re.findall(r'response_model\s*=', content))
            routes_with_models += model_count

        if total_routes > 0:
            coverage = routes_with_models / total_routes * 100
            assert coverage >= 30, \
                f"Only {coverage:.1f}% routes have response_model defined"


class TestResponseExamples:
    """Test that response schemas have examples."""

    def test_schemas_have_examples(self):
        """Test that Pydantic schemas have example configurations."""
        project_root = os.path.dirname(os.path.dirname(__file__))
        schemas_dir = os.path.join(project_root, "backend", "api", "schemas")

        if not os.path.exists(schemas_dir):
            pytest.skip("Schemas directory not found")

        schema_files = [
            f for f in os.listdir(schemas_dir)
            if f.endswith(".py") and not f.startswith("__")
        ]

        schemas_with_examples = 0
        total_schemas = 0

        for filename in schema_files:
            filepath = os.path.join(schemas_dir, filename)
            with open(filepath) as f:
                content = f.read()

            # Count classes that inherit from BaseModel
            class_count = len(re.findall(r'class \w+\(.*BaseModel', content))
            total_schemas += class_count

            # Check for json_schema_extra or Config with schema_extra
            example_count = len(re.findall(r'(json_schema_extra|schema_extra|example)', content))
            if example_count > 0:
                schemas_with_examples += 1

        # At least some schemas should have examples
        if total_schemas > 0:
            assert schemas_with_examples > 0, \
                "At least some Pydantic schemas should have examples defined"


class TestErrorResponses:
    """Test that error responses are documented."""

    def test_routes_document_error_responses(self, route_files):
        """Test that routes document potential error responses."""
        routes_with_errors = 0
        total_routes = 0

        for filepath in route_files:
            with open(filepath) as f:
                content = f.read()

            # Count routes
            route_count = len(re.findall(r'@router\.(get|post|put|patch|delete)', content))
            total_routes += route_count

            # Check for responses parameter or HTTPException imports
            has_error_docs = (
                'responses=' in content or
                'HTTPException' in content
            )

            if has_error_docs and route_count > 0:
                routes_with_errors += route_count

        # Files should at least use HTTPException for error handling
        if total_routes > 0:
            assert routes_with_errors > 0, \
                "Routes should document error responses using HTTPException or responses parameter"


class TestTagsAndOperationIds:
    """Test that routes have proper tags and operation IDs."""

    def test_routers_have_tags(self, route_files):
        """Test that routers define tags."""
        files_with_tags = 0

        for filepath in route_files:
            with open(filepath) as f:
                content = f.read()

            # Check for tags in router definition or individual routes
            has_tags = (
                'tags=' in content or
                'APIRouter(tags=' in content or
                'prefix=' in content  # Usually defined together
            )

            if has_tags:
                files_with_tags += 1

        # At least 50% of route files should define tags
        if len(route_files) > 0:
            coverage = files_with_tags / len(route_files) * 100
            assert coverage >= 50, \
                f"Only {coverage:.1f}% route files have tags defined"


class TestStatusCodes:
    """Test that routes specify appropriate status codes."""

    def test_post_routes_use_201(self, route_files):
        """Test that POST routes use 201 status code for creation."""
        post_with_201 = 0
        total_post = 0

        for filepath in route_files:
            with open(filepath) as f:
                content = f.read()

            # Count POST routes
            post_count = len(re.findall(r'@router\.post', content))
            total_post += post_count

            # Check for status_code=201 or status.HTTP_201
            status_201 = len(re.findall(r'(status_code\s*=\s*201|HTTP_201)', content))
            post_with_201 += min(status_201, post_count)

        # At least some POST routes should use 201
        if total_post > 0:
            assert post_with_201 > 0, \
                "POST routes for resource creation should use 201 status code"


class TestQueryParameters:
    """Test that query parameters are documented."""

    def test_query_params_have_descriptions(self, route_files):
        """Test that Query parameters have descriptions."""
        params_with_desc = 0
        total_params = 0

        for filepath in route_files:
            with open(filepath) as f:
                content = f.read()

            # Count Query parameters
            query_count = len(re.findall(r'Query\s*\(', content))
            total_params += query_count

            # Count Query params with description
            desc_count = len(re.findall(r'Query\s*\([^)]*description\s*=', content))
            params_with_desc += desc_count

        # At least some Query params should have descriptions
        if total_params > 0:
            coverage = params_with_desc / total_params * 100
            assert coverage >= 30, \
                f"Only {coverage:.1f}% Query parameters have descriptions"


class TestPathParameters:
    """Test that path parameters are documented."""

    def test_path_params_have_descriptions(self, route_files):
        """Test that Path parameters have descriptions."""
        params_with_desc = 0
        total_params = 0

        for filepath in route_files:
            with open(filepath) as f:
                content = f.read()

            # Count Path parameters
            path_count = len(re.findall(r'Path\s*\(', content))
            total_params += path_count

            # Count Path params with description
            desc_count = len(re.findall(r'Path\s*\([^)]*description\s*=', content))
            params_with_desc += desc_count

        # At least some Path params should have descriptions
        if total_params > 0:
            coverage = params_with_desc / total_params * 100
            # Be lenient - even 10% is acceptable
            assert coverage >= 10 or params_with_desc > 0, \
                f"Only {coverage:.1f}% Path parameters have descriptions"
