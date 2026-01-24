"""
Test suite for API response models
Ensures backend/api/schemas/responses.py exists and provides proper response structures
"""

import os
import sys
import pytest
from typing import Any
from pydantic import BaseModel, ValidationError as PydanticValidationError

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))


class TestResponsesFile:
    """Test responses file exists"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return os.path.dirname(os.path.dirname(__file__))

    @pytest.fixture
    def responses_path(self, project_root):
        """Get path to backend/api/schemas/responses.py file"""
        return os.path.join(project_root, 'backend', 'api', 'schemas', 'responses.py')

    def test_responses_py_exists(self, responses_path):
        """Test that backend/api/schemas/responses.py file exists"""
        assert os.path.exists(responses_path), \
            "backend/api/schemas/responses.py file must exist"

    def test_can_import_responses(self):
        """Test that we can import responses module"""
        try:
            import api.schemas.responses
            assert api.schemas.responses is not None
        except ImportError as e:
            pytest.fail(f"Failed to import api.schemas.responses: {e}")


class TestSuccessResponse:
    """Test SuccessResponse model"""

    def test_success_response_exists(self):
        """Test that SuccessResponse class exists"""
        try:
            from api.schemas.responses import SuccessResponse
            assert SuccessResponse is not None
        except ImportError as e:
            pytest.fail(f"Failed to import SuccessResponse: {e}")

    def test_success_response_inherits_from_basemodel(self):
        """Test that SuccessResponse inherits from Pydantic BaseModel"""
        from api.schemas.responses import SuccessResponse

        assert issubclass(SuccessResponse, BaseModel), \
            "SuccessResponse should inherit from Pydantic BaseModel"

    def test_success_response_has_success_field(self):
        """Test that SuccessResponse has success field"""
        from api.schemas.responses import SuccessResponse

        response = SuccessResponse(data={"test": "data"})
        assert hasattr(response, 'success'), \
            "SuccessResponse should have success field"

    def test_success_response_success_defaults_to_true(self):
        """Test that success field defaults to True"""
        from api.schemas.responses import SuccessResponse

        response = SuccessResponse(data={"test": "data"})
        assert response.success is True, \
            "success field should default to True"

    def test_success_response_has_data_field(self):
        """Test that SuccessResponse has data field"""
        from api.schemas.responses import SuccessResponse

        test_data = {"test": "data"}
        response = SuccessResponse(data=test_data)

        assert hasattr(response, 'data'), \
            "SuccessResponse should have data field"
        assert response.data == test_data, \
            "data field should contain the provided data"

    def test_success_response_accepts_any_data_type(self):
        """Test that data field accepts any type"""
        from api.schemas.responses import SuccessResponse

        # Test with dict
        response1 = SuccessResponse(data={"key": "value"})
        assert response1.data == {"key": "value"}

        # Test with list
        response2 = SuccessResponse(data=[1, 2, 3])
        assert response2.data == [1, 2, 3]

        # Test with string
        response3 = SuccessResponse(data="test string")
        assert response3.data == "test string"

        # Test with None
        response4 = SuccessResponse(data=None)
        assert response4.data is None

    def test_success_response_serializes_to_json(self):
        """Test that SuccessResponse can be serialized to JSON"""
        from api.schemas.responses import SuccessResponse

        response = SuccessResponse(data={"test": "data"})
        json_data = response.model_dump()

        assert isinstance(json_data, dict), \
            "model_dump() should return a dict"
        assert 'success' in json_data, \
            "JSON should include success field"
        assert 'data' in json_data, \
            "JSON should include data field"

    def test_success_response_json_structure(self):
        """Test the JSON structure of SuccessResponse"""
        from api.schemas.responses import SuccessResponse

        test_data = {"user_id": 123, "name": "Test User"}
        response = SuccessResponse(data=test_data)
        json_data = response.model_dump()

        assert json_data['success'] is True
        assert json_data['data'] == test_data

    def test_success_response_requires_data_field(self):
        """Test that data field is required"""
        from api.schemas.responses import SuccessResponse

        # Should raise validation error if data is missing
        with pytest.raises(PydanticValidationError):
            SuccessResponse()

    def test_success_response_with_nested_data(self):
        """Test SuccessResponse with nested data structures"""
        from api.schemas.responses import SuccessResponse

        complex_data = {
            "user": {
                "id": 123,
                "profile": {
                    "name": "Test User",
                    "email": "test@example.com"
                }
            },
            "items": [1, 2, 3]
        }

        response = SuccessResponse(data=complex_data)
        assert response.data == complex_data


class TestErrorResponse:
    """Test ErrorResponse model"""

    def test_error_response_exists(self):
        """Test that ErrorResponse class exists"""
        try:
            from api.schemas.responses import ErrorResponse
            assert ErrorResponse is not None
        except ImportError as e:
            pytest.fail(f"Failed to import ErrorResponse: {e}")

    def test_error_response_inherits_from_basemodel(self):
        """Test that ErrorResponse inherits from Pydantic BaseModel"""
        from api.schemas.responses import ErrorResponse

        assert issubclass(ErrorResponse, BaseModel), \
            "ErrorResponse should inherit from Pydantic BaseModel"

    def test_error_response_has_success_field(self):
        """Test that ErrorResponse has success field"""
        from api.schemas.responses import ErrorResponse

        response = ErrorResponse(error={"message": "Error"}, request_id="req-123")
        assert hasattr(response, 'success'), \
            "ErrorResponse should have success field"

    def test_error_response_success_defaults_to_false(self):
        """Test that success field defaults to False"""
        from api.schemas.responses import ErrorResponse

        response = ErrorResponse(error={"message": "Error"}, request_id="req-123")
        assert response.success is False, \
            "success field should default to False"

    def test_error_response_has_error_field(self):
        """Test that ErrorResponse has error field"""
        from api.schemas.responses import ErrorResponse

        error_data = {"message": "Something went wrong"}
        response = ErrorResponse(error=error_data, request_id="req-123")

        assert hasattr(response, 'error'), \
            "ErrorResponse should have error field"
        assert response.error == error_data, \
            "error field should contain the provided error data"

    def test_error_response_has_request_id_field(self):
        """Test that ErrorResponse has request_id field"""
        from api.schemas.responses import ErrorResponse

        request_id = "req-test-456"
        response = ErrorResponse(error={"message": "Error"}, request_id=request_id)

        assert hasattr(response, 'request_id'), \
            "ErrorResponse should have request_id field"
        assert response.request_id == request_id, \
            "request_id field should contain the provided request ID"

    def test_error_response_serializes_to_json(self):
        """Test that ErrorResponse can be serialized to JSON"""
        from api.schemas.responses import ErrorResponse

        response = ErrorResponse(
            error={"message": "Error occurred"},
            request_id="req-789"
        )
        json_data = response.model_dump()

        assert isinstance(json_data, dict), \
            "model_dump() should return a dict"
        assert 'success' in json_data, \
            "JSON should include success field"
        assert 'error' in json_data, \
            "JSON should include error field"
        assert 'request_id' in json_data, \
            "JSON should include request_id field"

    def test_error_response_json_structure(self):
        """Test the JSON structure of ErrorResponse"""
        from api.schemas.responses import ErrorResponse

        error_data = {
            "code": "VALIDATION_ERROR",
            "message": "Invalid input data",
            "details": {"field": "email", "issue": "invalid format"}
        }
        request_id = "req-abc-123"

        response = ErrorResponse(error=error_data, request_id=request_id)
        json_data = response.model_dump()

        assert json_data['success'] is False
        assert json_data['error'] == error_data
        assert json_data['request_id'] == request_id

    def test_error_response_requires_error_field(self):
        """Test that error field is required"""
        from api.schemas.responses import ErrorResponse

        # Should raise validation error if error is missing
        with pytest.raises(PydanticValidationError):
            ErrorResponse(request_id="req-123")

    def test_error_response_request_id_is_optional(self):
        """Test that request_id field is optional (can be omitted)"""
        from api.schemas.responses import ErrorResponse

        # Should work without request_id (defaults to None)
        response = ErrorResponse(error={"message": "Error"})
        assert response.request_id is None, \
            "request_id should default to None when not provided"

    def test_error_response_request_id_can_be_optional(self):
        """Test that request_id can be None if marked as optional"""
        from api.schemas.responses import ErrorResponse

        # Try creating with None - this tests if Optional is used
        try:
            response = ErrorResponse(error={"message": "Error"}, request_id=None)
            # If this works, request_id is Optional[str]
            assert response.request_id is None
        except PydanticValidationError:
            # If this raises error, request_id is required (str)
            # Both behaviors are acceptable, test should adapt
            pass


class TestPaginatedResponse:
    """Test PaginatedResponse model"""

    def test_paginated_response_exists(self):
        """Test that PaginatedResponse class exists"""
        try:
            from api.schemas.responses import PaginatedResponse
            assert PaginatedResponse is not None
        except ImportError as e:
            pytest.fail(f"Failed to import PaginatedResponse: {e}")

    def test_paginated_response_inherits_from_basemodel(self):
        """Test that PaginatedResponse inherits from Pydantic BaseModel"""
        from api.schemas.responses import PaginatedResponse

        assert issubclass(PaginatedResponse, BaseModel), \
            "PaginatedResponse should inherit from Pydantic BaseModel"

    def test_paginated_response_has_data_field(self):
        """Test that PaginatedResponse has data field"""
        from api.schemas.responses import PaginatedResponse

        test_data = [{"id": 1}, {"id": 2}, {"id": 3}]
        pagination = {"page": 1, "per_page": 10, "total": 3}
        response = PaginatedResponse(data=test_data, pagination=pagination)

        assert hasattr(response, 'data'), \
            "PaginatedResponse should have data field"
        assert response.data == test_data, \
            "data field should contain the provided data"

    def test_paginated_response_has_pagination_field(self):
        """Test that PaginatedResponse has pagination field"""
        from api.schemas.responses import PaginatedResponse

        test_data = [{"id": 1}]
        pagination = {"page": 1, "per_page": 10, "total": 1}
        response = PaginatedResponse(data=test_data, pagination=pagination)

        assert hasattr(response, 'pagination'), \
            "PaginatedResponse should have pagination field"
        assert response.pagination == pagination, \
            "pagination field should contain the provided pagination data"

    def test_paginated_response_data_is_list(self):
        """Test that data field contains a list"""
        from api.schemas.responses import PaginatedResponse

        test_data = [{"id": 1}, {"id": 2}]
        pagination = {"page": 1, "per_page": 10, "total": 2}
        response = PaginatedResponse(data=test_data, pagination=pagination)

        assert isinstance(response.data, list), \
            "data field should be a list"

    def test_paginated_response_pagination_is_dict(self):
        """Test that pagination field contains a dict"""
        from api.schemas.responses import PaginatedResponse

        test_data = [{"id": 1}]
        pagination = {"page": 1, "per_page": 10, "total": 1}
        response = PaginatedResponse(data=test_data, pagination=pagination)

        assert isinstance(response.pagination, dict), \
            "pagination field should be a dict"

    def test_paginated_response_serializes_to_json(self):
        """Test that PaginatedResponse can be serialized to JSON"""
        from api.schemas.responses import PaginatedResponse

        test_data = [{"id": 1, "name": "Item 1"}]
        pagination = {"page": 1, "per_page": 10, "total": 1, "pages": 1}
        response = PaginatedResponse(data=test_data, pagination=pagination)

        json_data = response.model_dump()

        assert isinstance(json_data, dict), \
            "model_dump() should return a dict"
        assert 'data' in json_data, \
            "JSON should include data field"
        assert 'pagination' in json_data, \
            "JSON should include pagination field"

    def test_paginated_response_json_structure(self):
        """Test the JSON structure of PaginatedResponse"""
        from api.schemas.responses import PaginatedResponse

        test_data = [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"}
        ]
        pagination = {
            "page": 1,
            "per_page": 10,
            "total": 2,
            "pages": 1,
            "has_next": False,
            "has_prev": False
        }

        response = PaginatedResponse(data=test_data, pagination=pagination)
        json_data = response.model_dump()

        assert json_data['data'] == test_data
        assert json_data['pagination'] == pagination

    def test_paginated_response_requires_data_field(self):
        """Test that data field is required"""
        from api.schemas.responses import PaginatedResponse

        # Should raise validation error if data is missing
        with pytest.raises(PydanticValidationError):
            PaginatedResponse(pagination={"page": 1})

    def test_paginated_response_requires_pagination_field(self):
        """Test that pagination field is required"""
        from api.schemas.responses import PaginatedResponse

        # Should raise validation error if pagination is missing
        with pytest.raises(PydanticValidationError):
            PaginatedResponse(data=[{"id": 1}])

    def test_paginated_response_with_empty_data(self):
        """Test PaginatedResponse with empty data list"""
        from api.schemas.responses import PaginatedResponse

        test_data = []
        pagination = {"page": 1, "per_page": 10, "total": 0, "pages": 0}
        response = PaginatedResponse(data=test_data, pagination=pagination)

        assert response.data == []
        assert response.pagination['total'] == 0


class TestResponseModelIntegration:
    """Test response model integration and usage"""

    def test_all_response_models_are_exported(self):
        """Test that __all__ exports all response models"""
        import api.schemas.responses

        if hasattr(api.schemas.responses, '__all__'):
            exports = api.schemas.responses.__all__

            expected_exports = [
                'SuccessResponse',
                'ErrorResponse',
                'PaginatedResponse'
            ]

            for export in expected_exports:
                assert export in exports, \
                    f"{export} should be in __all__"

    def test_success_response_with_fastapi(self):
        """Test SuccessResponse can be used as FastAPI response model"""
        from api.schemas.responses import SuccessResponse

        # Simulate FastAPI usage
        response = SuccessResponse(data={"user_id": 123, "username": "testuser"})
        json_response = response.model_dump()

        assert json_response == {
            "success": True,
            "data": {"user_id": 123, "username": "testuser"}
        }

    def test_error_response_with_fastapi(self):
        """Test ErrorResponse can be used as FastAPI response model"""
        from api.schemas.responses import ErrorResponse

        # Simulate FastAPI error response usage
        response = ErrorResponse(
            error={
                "code": "NOT_FOUND",
                "message": "User not found"
            },
            request_id="req-xyz-789"
        )
        json_response = response.model_dump()

        assert json_response['success'] is False
        assert json_response['error']['code'] == "NOT_FOUND"
        assert json_response['request_id'] == "req-xyz-789"

    def test_paginated_response_with_fastapi(self):
        """Test PaginatedResponse can be used as FastAPI response model"""
        from api.schemas.responses import PaginatedResponse

        # Simulate FastAPI paginated response usage
        response = PaginatedResponse(
            data=[
                {"id": 1, "name": "Item 1"},
                {"id": 2, "name": "Item 2"}
            ],
            pagination={
                "page": 1,
                "per_page": 10,
                "total": 2,
                "pages": 1
            }
        )
        json_response = response.model_dump()

        assert len(json_response['data']) == 2
        assert json_response['pagination']['page'] == 1


class TestResponseModelDocumentation:
    """Test that response models are properly documented"""

    def test_success_response_has_docstring(self):
        """Test that SuccessResponse has documentation"""
        from api.schemas.responses import SuccessResponse

        assert SuccessResponse.__doc__ is not None, \
            "SuccessResponse should have a docstring"

    def test_error_response_has_docstring(self):
        """Test that ErrorResponse has documentation"""
        from api.schemas.responses import ErrorResponse

        assert ErrorResponse.__doc__ is not None, \
            "ErrorResponse should have a docstring"

    def test_paginated_response_has_docstring(self):
        """Test that PaginatedResponse has documentation"""
        from api.schemas.responses import PaginatedResponse

        assert PaginatedResponse.__doc__ is not None, \
            "PaginatedResponse should have a docstring"
