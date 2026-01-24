"""
Test suite for exception handling system
Ensures backend/api/exceptions.py exists and provides proper exception handling
"""

import os
import sys
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))

# Use only asyncio backend for anyio tests
pytestmark = pytest.mark.anyio(backend="asyncio")


class TestExceptionsFile:
    """Test exceptions file exists"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return os.path.dirname(os.path.dirname(__file__))

    @pytest.fixture
    def exceptions_path(self, project_root):
        """Get path to backend/api/exceptions.py file"""
        return os.path.join(project_root, 'backend', 'api', 'exceptions.py')

    def test_exceptions_py_exists(self, exceptions_path):
        """Test that backend/api/exceptions.py file exists"""
        assert os.path.exists(exceptions_path), \
            "backend/api/exceptions.py file must exist"

    def test_can_import_exceptions(self):
        """Test that we can import exceptions module"""
        try:
            import api.exceptions
            assert api.exceptions is not None
        except ImportError as e:
            pytest.fail(f"Failed to import api.exceptions: {e}")


class TestCustomExceptions:
    """Test custom exception classes"""

    def test_validation_error_exists(self):
        """Test that ValidationError exception exists"""
        try:
            from api.exceptions import ValidationError
            assert ValidationError is not None
        except ImportError as e:
            pytest.fail(f"Failed to import ValidationError: {e}")

    def test_validation_error_inherits_from_exception(self):
        """Test that ValidationError inherits from Exception"""
        from api.exceptions import ValidationError

        assert issubclass(ValidationError, Exception), \
            "ValidationError should inherit from Exception"

    def test_not_found_error_exists(self):
        """Test that NotFoundError exception exists"""
        try:
            from api.exceptions import NotFoundError
            assert NotFoundError is not None
        except ImportError as e:
            pytest.fail(f"Failed to import NotFoundError: {e}")

    def test_not_found_error_inherits_from_exception(self):
        """Test that NotFoundError inherits from Exception"""
        from api.exceptions import NotFoundError

        assert issubclass(NotFoundError, Exception), \
            "NotFoundError should inherit from Exception"

    def test_unauthorized_error_exists(self):
        """Test that UnauthorizedError exception exists"""
        try:
            from api.exceptions import UnauthorizedError
            assert UnauthorizedError is not None
        except ImportError as e:
            pytest.fail(f"Failed to import UnauthorizedError: {e}")

    def test_unauthorized_error_inherits_from_exception(self):
        """Test that UnauthorizedError inherits from Exception"""
        from api.exceptions import UnauthorizedError

        assert issubclass(UnauthorizedError, Exception), \
            "UnauthorizedError should inherit from Exception"

    def test_forbidden_error_exists(self):
        """Test that ForbiddenError exception exists"""
        try:
            from api.exceptions import ForbiddenError
            assert ForbiddenError is not None
        except ImportError as e:
            pytest.fail(f"Failed to import ForbiddenError: {e}")

    def test_conflict_error_exists(self):
        """Test that ConflictError exception exists"""
        try:
            from api.exceptions import ConflictError
            assert ConflictError is not None
        except ImportError as e:
            pytest.fail(f"Failed to import ConflictError: {e}")


class TestExceptionAttributes:
    """Test exception class attributes"""

    def test_validation_error_has_status_code(self):
        """Test that ValidationError has status_code attribute"""
        from api.exceptions import ValidationError

        error = ValidationError("Test validation error")
        assert hasattr(error, 'status_code'), \
            "ValidationError should have status_code attribute"
        assert error.status_code == 400, \
            "ValidationError status_code should be 400"

    def test_validation_error_has_detail(self):
        """Test that ValidationError has detail attribute"""
        from api.exceptions import ValidationError

        detail_message = "Test validation error"
        error = ValidationError(detail_message)

        assert hasattr(error, 'detail'), \
            "ValidationError should have detail attribute"
        assert error.detail == detail_message, \
            "ValidationError detail should match provided message"

    def test_not_found_error_has_status_code(self):
        """Test that NotFoundError has status_code attribute"""
        from api.exceptions import NotFoundError

        error = NotFoundError("Resource not found")
        assert hasattr(error, 'status_code'), \
            "NotFoundError should have status_code attribute"
        assert error.status_code == 404, \
            "NotFoundError status_code should be 404"

    def test_unauthorized_error_has_status_code(self):
        """Test that UnauthorizedError has status_code attribute"""
        from api.exceptions import UnauthorizedError

        error = UnauthorizedError("Unauthorized access")
        assert hasattr(error, 'status_code'), \
            "UnauthorizedError should have status_code attribute"
        assert error.status_code == 401, \
            "UnauthorizedError status_code should be 401"

    def test_forbidden_error_has_status_code(self):
        """Test that ForbiddenError has status_code attribute"""
        from api.exceptions import ForbiddenError

        error = ForbiddenError("Forbidden access")
        assert hasattr(error, 'status_code'), \
            "ForbiddenError should have status_code attribute"
        assert error.status_code == 403, \
            "ForbiddenError status_code should be 403"

    def test_conflict_error_has_status_code(self):
        """Test that ConflictError has status_code attribute"""
        from api.exceptions import ConflictError

        error = ConflictError("Resource conflict")
        assert hasattr(error, 'status_code'), \
            "ConflictError should have status_code attribute"
        assert error.status_code == 409, \
            "ConflictError status_code should be 409"

    def test_exception_accepts_headers(self):
        """Test that custom exceptions can accept headers"""
        from api.exceptions import UnauthorizedError

        headers = {"WWW-Authenticate": "Bearer"}
        error = UnauthorizedError("Unauthorized", headers=headers)

        assert hasattr(error, 'headers'), \
            "Exception should support headers attribute"
        assert error.headers == headers, \
            "Exception headers should match provided headers"


class TestExceptionHandlers:
    """Test exception handler functions"""

    def test_validation_error_handler_exists(self):
        """Test that validation_error_handler function exists"""
        try:
            from api.exceptions import validation_error_handler
            assert validation_error_handler is not None
        except ImportError as e:
            pytest.fail(f"Failed to import validation_error_handler: {e}")

    def test_not_found_error_handler_exists(self):
        """Test that not_found_error_handler function exists"""
        try:
            from api.exceptions import not_found_error_handler
            assert not_found_error_handler is not None
        except ImportError as e:
            pytest.fail(f"Failed to import not_found_error_handler: {e}")

    def test_unauthorized_error_handler_exists(self):
        """Test that unauthorized_error_handler function exists"""
        try:
            from api.exceptions import unauthorized_error_handler
            assert unauthorized_error_handler is not None
        except ImportError as e:
            pytest.fail(f"Failed to import unauthorized_error_handler: {e}")

    def test_http_exception_handler_exists(self):
        """Test that http_exception_handler function exists"""
        try:
            from api.exceptions import http_exception_handler
            assert http_exception_handler is not None
        except ImportError as e:
            pytest.fail(f"Failed to import http_exception_handler: {e}")

    def test_generic_exception_handler_exists(self):
        """Test that generic_exception_handler function exists"""
        try:
            from api.exceptions import generic_exception_handler
            assert generic_exception_handler is not None
        except ImportError as e:
            pytest.fail(f"Failed to import generic_exception_handler: {e}")


class TestExceptionHandlerBehavior:
    """Test exception handler behavior"""

    @pytest.mark.anyio
    async def test_validation_error_handler_returns_json_response(self):
        """Test that validation_error_handler returns JSONResponse"""
        from api.exceptions import ValidationError, validation_error_handler
        from fastapi import Request

        # Create a mock request
        mock_request = Mock(spec=Request)

        # Create a validation error
        error = ValidationError("Invalid input")

        # Call the handler
        response = await validation_error_handler(mock_request, error)

        # Check response
        assert response is not None, \
            "Handler should return a response"
        assert response.status_code == 400, \
            "Handler should return 400 status code"

    @pytest.mark.anyio
    async def test_not_found_error_handler_returns_json_response(self):
        """Test that not_found_error_handler returns JSONResponse"""
        from api.exceptions import NotFoundError, not_found_error_handler
        from fastapi import Request

        mock_request = Mock(spec=Request)
        error = NotFoundError("Resource not found")

        response = await not_found_error_handler(mock_request, error)

        assert response is not None
        assert response.status_code == 404, \
            "Handler should return 404 status code"

    @pytest.mark.anyio
    async def test_unauthorized_error_handler_returns_json_response(self):
        """Test that unauthorized_error_handler returns JSONResponse"""
        from api.exceptions import UnauthorizedError, unauthorized_error_handler
        from fastapi import Request

        mock_request = Mock(spec=Request)
        error = UnauthorizedError("Unauthorized access")

        response = await unauthorized_error_handler(mock_request, error)

        assert response is not None
        assert response.status_code == 401, \
            "Handler should return 401 status code"

    @pytest.mark.anyio
    async def test_http_exception_handler_returns_json_response(self):
        """Test that http_exception_handler returns JSONResponse"""
        from api.exceptions import http_exception_handler
        from fastapi import Request, HTTPException

        mock_request = Mock(spec=Request)
        error = HTTPException(status_code=403, detail="Forbidden")

        response = await http_exception_handler(mock_request, error)

        assert response is not None
        assert response.status_code == 403, \
            "Handler should return correct status code"

    @pytest.mark.anyio
    async def test_generic_exception_handler_returns_500(self):
        """Test that generic_exception_handler returns 500 for unhandled exceptions"""
        from api.exceptions import generic_exception_handler
        from fastapi import Request

        mock_request = Mock(spec=Request)
        error = Exception("Unexpected error")

        response = await generic_exception_handler(mock_request, error)

        assert response is not None
        assert response.status_code == 500, \
            "Handler should return 500 for generic exceptions"


class TestExceptionResponseFormat:
    """Test exception response format"""

    @pytest.mark.anyio
    async def test_error_response_includes_detail(self):
        """Test that error response includes detail field"""
        from api.exceptions import ValidationError, validation_error_handler
        from fastapi import Request
        import json

        mock_request = Mock(spec=Request)
        error = ValidationError("Invalid input data")

        response = await validation_error_handler(mock_request, error)

        # Parse response body
        body = json.loads(response.body.decode())

        assert 'detail' in body, \
            "Error response should include detail field"
        assert body['detail'] == "Invalid input data", \
            "Detail should match error message"

    @pytest.mark.anyio
    async def test_error_response_includes_request_id(self):
        """Test that error response includes request_id when available"""
        from api.exceptions import ValidationError, validation_error_handler
        from api.logging_config import set_request_id
        from fastapi import Request
        import json

        # Set a request ID
        test_request_id = "req-test-123"
        set_request_id(test_request_id)

        mock_request = Mock(spec=Request)
        error = ValidationError("Invalid input")

        response = await validation_error_handler(mock_request, error)
        body = json.loads(response.body.decode())

        assert 'request_id' in body or 'requestId' in body, \
            "Error response should include request_id field"

    @pytest.mark.anyio
    async def test_error_response_includes_error_type(self):
        """Test that error response includes error type"""
        from api.exceptions import ValidationError, validation_error_handler
        from fastapi import Request
        import json

        mock_request = Mock(spec=Request)
        error = ValidationError("Invalid input")

        response = await validation_error_handler(mock_request, error)
        body = json.loads(response.body.decode())

        assert 'error_type' in body or 'type' in body or 'error' in body, \
            "Error response should include error type field"


class TestExceptionHandlerRegistration:
    """Test exception handler registration with FastAPI"""

    def test_register_exception_handlers_function_exists(self):
        """Test that register_exception_handlers function exists"""
        try:
            from api.exceptions import register_exception_handlers
            assert register_exception_handlers is not None
        except ImportError as e:
            pytest.fail(f"Failed to import register_exception_handlers: {e}")

    def test_register_exception_handlers_accepts_app(self):
        """Test that register_exception_handlers accepts FastAPI app"""
        from api.exceptions import register_exception_handlers
        import inspect

        sig = inspect.signature(register_exception_handlers)
        params = list(sig.parameters.keys())

        assert len(params) >= 1, \
            "register_exception_handlers should accept at least one parameter (app)"

    def test_can_register_handlers_with_fastapi_app(self):
        """Test that handlers can be registered with a FastAPI app"""
        from api.exceptions import register_exception_handlers
        from fastapi import FastAPI

        app = FastAPI()

        # Should not raise an exception
        try:
            register_exception_handlers(app)
        except Exception as e:
            pytest.fail(f"Failed to register exception handlers: {e}")


class TestExceptionIntegration:
    """Test exception handling integration with FastAPI"""

    def test_validation_error_in_endpoint_returns_400(self):
        """Test that raising ValidationError in endpoint returns 400"""
        from api.exceptions import ValidationError, register_exception_handlers
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI()
        register_exception_handlers(app)

        @app.get("/test-validation-error")
        async def test_endpoint():
            raise ValidationError("Test validation error")

        client = TestClient(app)
        response = client.get("/test-validation-error")

        assert response.status_code == 400, \
            "ValidationError should result in 400 status code"

    def test_not_found_error_in_endpoint_returns_404(self):
        """Test that raising NotFoundError in endpoint returns 404"""
        from api.exceptions import NotFoundError, register_exception_handlers
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI()
        register_exception_handlers(app)

        @app.get("/test-not-found-error")
        async def test_endpoint():
            raise NotFoundError("Resource not found")

        client = TestClient(app)
        response = client.get("/test-not-found-error")

        assert response.status_code == 404, \
            "NotFoundError should result in 404 status code"

    def test_unauthorized_error_in_endpoint_returns_401(self):
        """Test that raising UnauthorizedError in endpoint returns 401"""
        from api.exceptions import UnauthorizedError, register_exception_handlers
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI()
        register_exception_handlers(app)

        @app.get("/test-unauthorized-error")
        async def test_endpoint():
            raise UnauthorizedError("Unauthorized access")

        client = TestClient(app)
        response = client.get("/test-unauthorized-error")

        assert response.status_code == 401, \
            "UnauthorizedError should result in 401 status code"


class TestExceptionDocumentation:
    """Test that exceptions are properly documented"""

    def test_validation_error_has_docstring(self):
        """Test that ValidationError has documentation"""
        from api.exceptions import ValidationError

        assert ValidationError.__doc__ is not None, \
            "ValidationError should have a docstring"

    def test_not_found_error_has_docstring(self):
        """Test that NotFoundError has documentation"""
        from api.exceptions import NotFoundError

        assert NotFoundError.__doc__ is not None, \
            "NotFoundError should have a docstring"

    def test_exception_handlers_have_docstrings(self):
        """Test that exception handlers have documentation"""
        from api.exceptions import validation_error_handler

        assert validation_error_handler.__doc__ is not None, \
            "Exception handlers should have docstrings"


class TestExceptionExports:
    """Test that exceptions are properly exported"""

    def test_all_exceptions_exported(self):
        """Test that __all__ exports all exceptions"""
        import api.exceptions

        if hasattr(api.exceptions, '__all__'):
            exports = api.exceptions.__all__

            # Should export custom exceptions
            expected_exports = [
                'ValidationError',
                'NotFoundError',
                'UnauthorizedError',
                'register_exception_handlers'
            ]

            for export in expected_exports:
                assert export in exports, \
                    f"{export} should be in __all__"
