"""
Test suite for Houndify response models (TASK-107)

Validates the Houndify model implementations:
- HoundifyResponse model structure and validation
- HoundifyRequestInfo model structure and defaults
- HoundifyError exception behavior
- Pydantic integration and serialization
"""

import pytest
from pathlib import Path
import sys

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
INTEGRATIONS_DIR = BACKEND_DIR / "integrations"
HOUNDIFY_DIR = INTEGRATIONS_DIR / "houndify"
MODELS_FILE = HOUNDIFY_DIR / "models.py"


class TestModelsFileStructure:
    """Test models.py file structure"""

    def test_models_file_exists(self):
        """Test that models.py exists"""
        assert MODELS_FILE.exists(), "models.py should exist"
        assert MODELS_FILE.is_file(), "models.py should be a file"

    def test_models_has_content(self):
        """Test that models.py has content"""
        content = MODELS_FILE.read_text()
        assert len(content) > 0, "models.py should not be empty"


class TestModelsImports:
    """Test necessary imports in models.py"""

    @pytest.fixture
    def models_content(self):
        """Load models.py content"""
        return MODELS_FILE.read_text()

    def test_imports_pydantic(self, models_content):
        """Test that pydantic BaseModel is imported"""
        assert "from pydantic import BaseModel" in models_content, \
            "Should import BaseModel from pydantic"

    def test_imports_typing(self, models_content):
        """Test that typing module is imported"""
        assert "from typing import" in models_content or "import typing" in models_content, \
            "Should import typing for type hints"

    def test_imports_optional(self, models_content):
        """Test that Optional is imported"""
        assert "Optional" in models_content, \
            "Should import Optional from typing"

    def test_imports_list_dict_any(self, models_content):
        """Test that List, Dict, Any are imported"""
        has_types = "List" in models_content and "Dict" in models_content and "Any" in models_content
        assert has_types, "Should import List, Dict, and Any from typing"


class TestHoundifyResponseModel:
    """Test HoundifyResponse model"""

    @pytest.fixture
    def models_content(self):
        """Load models.py content"""
        return MODELS_FILE.read_text()

    def test_has_houndify_response_class(self, models_content):
        """Test that HoundifyResponse class exists"""
        assert "class HoundifyResponse" in models_content, \
            "Should have HoundifyResponse class"

    def test_response_inherits_basemodel(self, models_content):
        """Test that HoundifyResponse inherits from BaseModel"""
        assert "class HoundifyResponse(BaseModel)" in models_content, \
            "HoundifyResponse should inherit from BaseModel"

    def test_has_raw_transcription_field(self, models_content):
        """Test that raw_transcription field exists"""
        assert "raw_transcription" in models_content, \
            "Should have raw_transcription field"

    def test_has_formatted_transcription_field(self, models_content):
        """Test that formatted_transcription field exists"""
        assert "formatted_transcription" in models_content, \
            "Should have formatted_transcription field"

    def test_has_command_kind_field(self, models_content):
        """Test that command_kind field exists"""
        assert "command_kind" in models_content, \
            "Should have command_kind field"

    def test_has_command_results_field(self, models_content):
        """Test that command_results field exists"""
        assert "command_results" in models_content, \
            "Should have command_results field"

    def test_has_entities_field(self, models_content):
        """Test that entities field exists"""
        assert "entities" in models_content, \
            "Should have entities field"

    def test_has_confidence_field(self, models_content):
        """Test that confidence field exists"""
        assert "confidence" in models_content, \
            "Should have confidence field"

    def test_has_spoken_response_field(self, models_content):
        """Test that spoken_response field exists"""
        assert "spoken_response" in models_content, \
            "Should have spoken_response field"

    def test_has_conversation_state_field(self, models_content):
        """Test that conversation_state field exists"""
        assert "conversation_state" in models_content, \
            "Should have conversation_state field"

    def test_has_request_id_field(self, models_content):
        """Test that request_id field exists"""
        assert "request_id" in models_content, \
            "Should have request_id field"

    def test_has_all_results_field(self, models_content):
        """Test that all_results field exists"""
        assert "all_results" in models_content, \
            "Should have all_results field"

    def test_has_docstring(self, models_content):
        """Test that HoundifyResponse has docstring"""
        lines = models_content.split('\n')
        in_response_class = False
        has_docstring = False

        for i, line in enumerate(lines):
            if 'class HoundifyResponse' in line:
                in_response_class = True
            elif in_response_class:
                if '"""' in line or "'''" in line:
                    has_docstring = True
                    break
                elif line.strip() and not line.strip().startswith('#'):
                    # Hit non-comment code before docstring
                    if not line.strip().startswith('class'):
                        break

        assert has_docstring, "HoundifyResponse should have docstring"


class TestHoundifyRequestInfoModel:
    """Test HoundifyRequestInfo model"""

    @pytest.fixture
    def models_content(self):
        """Load models.py content"""
        return MODELS_FILE.read_text()

    def test_has_houndify_request_info_class(self, models_content):
        """Test that HoundifyRequestInfo class exists"""
        assert "class HoundifyRequestInfo" in models_content, \
            "Should have HoundifyRequestInfo class"

    def test_request_info_inherits_basemodel(self, models_content):
        """Test that HoundifyRequestInfo inherits from BaseModel"""
        assert "class HoundifyRequestInfo(BaseModel)" in models_content, \
            "HoundifyRequestInfo should inherit from BaseModel"

    def test_has_user_id_field(self, models_content):
        """Test that user_id field exists"""
        assert "user_id" in models_content, \
            "Should have user_id field"

    def test_has_request_id_field(self, models_content):
        """Test that request_id field exists"""
        assert "request_id" in models_content, \
            "Should have request_id field"

    def test_has_latitude_field(self, models_content):
        """Test that latitude field exists"""
        assert "latitude" in models_content, \
            "Should have latitude field"

    def test_has_longitude_field(self, models_content):
        """Test that longitude field exists"""
        assert "longitude" in models_content, \
            "Should have longitude field"

    def test_has_partial_transcripts_desired_field(self, models_content):
        """Test that partial_transcripts_desired field exists"""
        assert "partial_transcripts_desired" in models_content, \
            "Should have partial_transcripts_desired field"

    def test_has_docstring(self, models_content):
        """Test that HoundifyRequestInfo has docstring"""
        lines = models_content.split('\n')
        in_request_info_class = False
        has_docstring = False

        for i, line in enumerate(lines):
            if 'class HoundifyRequestInfo' in line:
                in_request_info_class = True
            elif in_request_info_class:
                if '"""' in line or "'''" in line:
                    has_docstring = True
                    break
                elif line.strip() and not line.strip().startswith('#'):
                    if not line.strip().startswith('class'):
                        break

        assert has_docstring, "HoundifyRequestInfo should have docstring"


class TestHoundifyErrorException:
    """Test HoundifyError exception"""

    @pytest.fixture
    def models_content(self):
        """Load models.py content"""
        return MODELS_FILE.read_text()

    def test_has_houndify_error_class(self, models_content):
        """Test that HoundifyError class exists"""
        assert "class HoundifyError" in models_content, \
            "Should have HoundifyError class"

    def test_error_inherits_exception(self, models_content):
        """Test that HoundifyError inherits from Exception"""
        assert "class HoundifyError(Exception)" in models_content, \
            "HoundifyError should inherit from Exception"

    def test_has_init_method(self, models_content):
        """Test that __init__ method exists"""
        assert "def __init__" in models_content, \
            "Should have __init__ method"

    def test_has_message_param(self, models_content):
        """Test that __init__ has message parameter"""
        lines = models_content.split('\n')
        for i, line in enumerate(lines):
            if 'class HoundifyError' in line:
                # Check next 40 lines for __init__ (accounts for docstring)
                func_def = ''.join(lines[i:min(i+40, len(lines))])
                assert 'message' in func_def, "__init__ should have message parameter"
                break

    def test_has_status_code_param(self, models_content):
        """Test that __init__ has status_code parameter"""
        lines = models_content.split('\n')
        for i, line in enumerate(lines):
            if 'class HoundifyError' in line:
                func_def = ''.join(lines[i:min(i+40, len(lines))])
                assert 'status_code' in func_def, "__init__ should have status_code parameter"
                break

    def test_has_response_param(self, models_content):
        """Test that __init__ has response parameter"""
        lines = models_content.split('\n')
        for i, line in enumerate(lines):
            if 'class HoundifyError' in line:
                func_def = ''.join(lines[i:min(i+40, len(lines))])
                assert 'response' in func_def, "__init__ should have response parameter"
                break

    def test_has_docstring(self, models_content):
        """Test that HoundifyError has docstring"""
        lines = models_content.split('\n')
        in_error_class = False
        has_docstring = False

        for i, line in enumerate(lines):
            if 'class HoundifyError' in line:
                in_error_class = True
            elif in_error_class:
                if '"""' in line or "'''" in line:
                    has_docstring = True
                    break
                elif line.strip() and not line.strip().startswith('#'):
                    if not line.strip().startswith('class'):
                        break

        assert has_docstring, "HoundifyError should have docstring"


class TestModulesStructure:
    """Test overall models.py structure"""

    @pytest.fixture
    def models_content(self):
        """Load models.py content"""
        return MODELS_FILE.read_text()

    def test_is_valid_python(self, models_content):
        """Test that file is valid Python"""
        try:
            compile(models_content, MODELS_FILE, 'exec')
        except SyntaxError as e:
            pytest.fail(f"models.py has syntax error: {e}")

    def test_has_module_docstring(self, models_content):
        """Test that module has docstring"""
        assert '"""' in models_content or "'''" in models_content, \
            "Should have module documentation"

    def test_has_all_three_models(self, models_content):
        """Test that all three models are present"""
        assert "class HoundifyResponse" in models_content, "Should have HoundifyResponse"
        assert "class HoundifyRequestInfo" in models_content, "Should have HoundifyRequestInfo"
        assert "class HoundifyError" in models_content, "Should have HoundifyError"


class TestImportability:
    """Test that models can be imported"""

    def test_can_import_models_module(self):
        """Test that models module can be imported"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from integrations.houndify import models
            assert models is not None, \
                "houndify.models module should be importable"
        except ImportError as e:
            pytest.fail(f"Cannot import houndify.models: {e}")

    def test_can_import_houndify_response(self):
        """Test that HoundifyResponse can be imported"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from integrations.houndify.models import HoundifyResponse
            assert HoundifyResponse is not None, \
                "HoundifyResponse class should be importable"
        except ImportError as e:
            pytest.fail(f"Cannot import HoundifyResponse: {e}")

    def test_can_import_houndify_request_info(self):
        """Test that HoundifyRequestInfo can be imported"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from integrations.houndify.models import HoundifyRequestInfo
            assert HoundifyRequestInfo is not None, \
                "HoundifyRequestInfo class should be importable"
        except ImportError as e:
            pytest.fail(f"Cannot import HoundifyRequestInfo: {e}")

    def test_can_import_houndify_error(self):
        """Test that HoundifyError can be imported"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from integrations.houndify.models import HoundifyError
            assert HoundifyError is not None, \
                "HoundifyError class should be importable"
        except ImportError as e:
            pytest.fail(f"Cannot import HoundifyError: {e}")


class TestHoundifyResponseInstantiation:
    """Test HoundifyResponse instantiation and validation"""

    def test_can_create_response_with_required_fields(self):
        """Test that HoundifyResponse can be instantiated with required fields"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from integrations.houndify.models import HoundifyResponse

            response = HoundifyResponse(
                raw_transcription="weather in paris",
                formatted_transcription="Weather in Paris",
                command_kind="WeatherQuery",
                command_results=[{"Weather": "Sunny", "Temperature": 22}],
                entities={"Location": "Paris"},
                confidence=0.95,
                spoken_response="The weather in Paris is sunny",
                request_id="req123",
                all_results={"AllResults": []}
            )

            assert response is not None, "Should create HoundifyResponse instance"
            assert response.raw_transcription == "weather in paris"
            assert response.formatted_transcription == "Weather in Paris"
            assert response.command_kind == "WeatherQuery"
            assert response.confidence == 0.95
            assert response.request_id == "req123"

        except Exception as e:
            pytest.fail(f"Cannot instantiate HoundifyResponse: {e}")

    def test_can_create_response_with_optional_fields(self):
        """Test that HoundifyResponse accepts optional fields"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from integrations.houndify.models import HoundifyResponse

            response = HoundifyResponse(
                raw_transcription="test",
                formatted_transcription="Test",
                command_kind="TestQuery",
                command_results=[],
                entities={},
                confidence=0.9,
                spoken_response="Test response",
                spoken_response_long="This is a longer test response",
                conversation_state={"state": "active"},
                response_audio_bytes=b"audio_data",
                response_time_ms=150,
                request_id="req456",
                all_results={}
            )

            assert response.spoken_response_long == "This is a longer test response"
            assert response.conversation_state == {"state": "active"}
            assert response.response_audio_bytes == b"audio_data"
            assert response.response_time_ms == 150

        except Exception as e:
            pytest.fail(f"Cannot create HoundifyResponse with optional fields: {e}")


class TestHoundifyRequestInfoInstantiation:
    """Test HoundifyRequestInfo instantiation and defaults"""

    def test_can_create_request_info_with_required_fields(self):
        """Test that HoundifyRequestInfo can be instantiated with required fields"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from integrations.houndify.models import HoundifyRequestInfo

            request_info = HoundifyRequestInfo(
                user_id="user123",
                request_id="req456"
            )

            assert request_info is not None, "Should create HoundifyRequestInfo instance"
            assert request_info.user_id == "user123"
            assert request_info.request_id == "req456"

        except Exception as e:
            pytest.fail(f"Cannot instantiate HoundifyRequestInfo: {e}")

    def test_request_info_has_default_values(self):
        """Test that HoundifyRequestInfo has proper default values"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from integrations.houndify.models import HoundifyRequestInfo

            request_info = HoundifyRequestInfo(
                user_id="user123",
                request_id="req456"
            )

            assert request_info.latitude is None, "latitude should default to None"
            assert request_info.longitude is None, "longitude should default to None"
            assert request_info.partial_transcripts_desired is False, \
                "partial_transcripts_desired should default to False"

        except Exception as e:
            pytest.fail(f"Cannot check default values: {e}")

    def test_can_create_request_info_with_optional_fields(self):
        """Test that HoundifyRequestInfo accepts optional fields"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from integrations.houndify.models import HoundifyRequestInfo

            request_info = HoundifyRequestInfo(
                user_id="user123",
                request_id="req456",
                latitude=37.7749,
                longitude=-122.4194,
                partial_transcripts_desired=True
            )

            assert request_info.latitude == 37.7749
            assert request_info.longitude == -122.4194
            assert request_info.partial_transcripts_desired is True

        except Exception as e:
            pytest.fail(f"Cannot create HoundifyRequestInfo with optional fields: {e}")


class TestHoundifyErrorInstantiation:
    """Test HoundifyError instantiation and behavior"""

    def test_can_create_error_with_message(self):
        """Test that HoundifyError can be instantiated with message"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from integrations.houndify.models import HoundifyError

            error = HoundifyError("Test error message")

            assert error is not None, "Should create HoundifyError instance"
            assert error.message == "Test error message"
            assert str(error) == "Test error message"

        except Exception as e:
            pytest.fail(f"Cannot instantiate HoundifyError: {e}")

    def test_can_create_error_with_status_code(self):
        """Test that HoundifyError accepts status_code"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from integrations.houndify.models import HoundifyError

            error = HoundifyError("API error", status_code=429)

            assert error.status_code == 429

        except Exception as e:
            pytest.fail(f"Cannot create HoundifyError with status_code: {e}")

    def test_can_create_error_with_response(self):
        """Test that HoundifyError accepts response dict"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from integrations.houndify.models import HoundifyError

            response_dict = {"error": "Rate limit exceeded", "retry_after": 60}
            error = HoundifyError("Rate limit error", status_code=429, response=response_dict)

            assert error.response == response_dict
            assert error.response["retry_after"] == 60

        except Exception as e:
            pytest.fail(f"Cannot create HoundifyError with response: {e}")

    def test_error_is_exception(self):
        """Test that HoundifyError is a proper Exception"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from integrations.houndify.models import HoundifyError

            error = HoundifyError("Test error")

            assert isinstance(error, Exception), "HoundifyError should be an Exception"

            # Test that it can be raised and caught
            with pytest.raises(HoundifyError) as exc_info:
                raise error

            assert exc_info.value.message == "Test error"

        except Exception as e:
            pytest.fail(f"HoundifyError is not a proper Exception: {e}")


class TestTaskRequirements:
    """Test TASK-107 specific requirements"""

    @pytest.fixture
    def models_content(self):
        """Load models.py content"""
        return MODELS_FILE.read_text()

    def test_task_107_houndify_response(self, models_content):
        """Test TASK-107 requirement: HoundifyResponse model"""
        assert "class HoundifyResponse(BaseModel)" in models_content, \
            "TASK-107 requirement: Must implement HoundifyResponse model"

    def test_task_107_houndify_request_info(self, models_content):
        """Test TASK-107 requirement: HoundifyRequestInfo model"""
        assert "class HoundifyRequestInfo(BaseModel)" in models_content, \
            "TASK-107 requirement: Must implement HoundifyRequestInfo model"

    def test_task_107_houndify_error(self, models_content):
        """Test TASK-107 requirement: HoundifyError exception"""
        assert "class HoundifyError(Exception)" in models_content, \
            "TASK-107 requirement: Must implement HoundifyError exception"

    def test_task_107_pydantic_integration(self, models_content):
        """Test TASK-107 requirement: Pydantic BaseModel usage"""
        assert "from pydantic import BaseModel" in models_content, \
            "TASK-107 requirement: Must use Pydantic BaseModel"

    def test_task_107_required_response_fields(self, models_content):
        """Test TASK-107 requirement: All required response fields present"""
        required_fields = [
            "raw_transcription",
            "formatted_transcription",
            "command_kind",
            "command_results",
            "entities",
            "confidence",
            "spoken_response",
            "request_id",
            "all_results"
        ]
        for field in required_fields:
            assert field in models_content, \
                f"TASK-107 requirement: Must have {field} field"

    def test_task_107_optional_response_fields(self, models_content):
        """Test TASK-107 requirement: Optional response fields present"""
        optional_fields = [
            "spoken_response_long",
            "conversation_state",
            "response_audio_bytes"
        ]
        for field in optional_fields:
            assert field in models_content, \
                f"TASK-107 requirement: Should have optional {field} field"
