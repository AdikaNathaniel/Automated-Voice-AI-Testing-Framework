"""
Test suite for Houndify API client (TASK-106)

Validates the Houndify client implementation:
- File structure and imports
- HoundifyClient class initialization
- text_query method implementation
- voice_query method implementation
- Conversation state management
- Authentication handling
- Proper async implementation
"""

import pytest
from pathlib import Path
import sys
import hmac
import hashlib
import base64
import json


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
INTEGRATIONS_DIR = BACKEND_DIR / "integrations"
HOUNDIFY_DIR = INTEGRATIONS_DIR / "houndify"
CLIENT_FILE = HOUNDIFY_DIR / "client.py"


class TestHoundifyDirectoryStructure:
    """Test Houndify directory structure"""

    def test_integrations_directory_exists(self):
        """Test that integrations directory exists"""
        assert INTEGRATIONS_DIR.exists(), "backend/integrations directory should exist"
        assert INTEGRATIONS_DIR.is_dir(), "integrations should be a directory"

    def test_houndify_directory_exists(self):
        """Test that houndify directory exists"""
        assert HOUNDIFY_DIR.exists(), "backend/integrations/houndify directory should exist"
        assert HOUNDIFY_DIR.is_dir(), "houndify should be a directory"

    def test_client_file_exists(self):
        """Test that client.py exists"""
        assert CLIENT_FILE.exists(), "client.py should exist"
        assert CLIENT_FILE.is_file(), "client.py should be a file"

    def test_client_has_content(self):
        """Test that client.py has content"""
        content = CLIENT_FILE.read_text()
        assert len(content) > 0, "client.py should not be empty"


class TestHoundifyClientImports:
    """Test necessary imports in client.py"""

    @pytest.fixture
    def client_content(self):
        """Load client.py content"""
        return CLIENT_FILE.read_text()

    def test_imports_httpx(self, client_content):
        """Test that httpx is imported for HTTP requests"""
        assert "import httpx" in client_content or "from httpx import" in client_content, \
            "Should import httpx for async HTTP requests"

    def test_imports_typing(self, client_content):
        """Test that typing is imported"""
        assert "from typing import" in client_content or "import typing" in client_content, \
            "Should import typing for type hints"

    def test_imports_dict_any(self, client_content):
        """Test that Dict and Any are imported"""
        has_types = "Dict" in client_content and "Any" in client_content
        assert has_types, "Should import Dict and Any from typing"


class TestHoundifyClientClass:
    """Test HoundifyClient class definition"""

    @pytest.fixture
    def client_content(self):
        """Load client.py content"""
        return CLIENT_FILE.read_text()

    def test_has_houndify_client_class(self, client_content):
        """Test that HoundifyClient class exists"""
        assert "class HoundifyClient" in client_content, \
            "Should have HoundifyClient class"

    def test_has_init_method(self, client_content):
        """Test that __init__ method exists"""
        assert "def __init__" in client_content, \
            "Should have __init__ method"

    def test_init_has_client_id_param(self, client_content):
        """Test that __init__ accepts client_id"""
        assert "client_id" in client_content, \
            "Should have client_id parameter"

    def test_init_has_client_key_param(self, client_content):
        """Test that __init__ accepts client_key"""
        assert "client_key" in client_content, \
            "Should have client_key parameter"

    def test_has_base_url_attribute(self, client_content):
        """Test that base_url is set"""
        assert "base_url" in client_content, \
            "Should have base_url attribute"

    def test_correct_base_url(self, client_content):
        """Test that base_url points to Houndify API"""
        assert "api.houndify.com" in client_content, \
            "base_url should point to api.houndify.com"


class TestHoundifyAuthHeaders:
    """Behavioral tests for Houndify authentication headers."""

    def _import_client(self):
        sys.path.append(str(BACKEND_DIR))
        from integrations.houndify.client import HoundifyClient

        return HoundifyClient

    def test_auth_headers_include_hmac_signature(self, monkeypatch):
        HoundifyClient = self._import_client()
        client = HoundifyClient("test-client", "secret-key")

        monkeypatch.setattr("integrations.houndify.client.time.time", lambda: 1_600_000_000)

        headers = client._build_auth_headers("request-123")

        assert headers["Hound-Client-ID"] == "test-client"
        assert headers["Hound-Request-ID"] == "request-123"
        assert headers["Content-Type"] == "application/json"
        assert headers["Hound-Request-Timestamp"] == "1600000000"

        expected = hmac.new(
            b"secret-key",
            b"test-client;request-123;1600000000",
            hashlib.sha256
        ).digest()
        expected_b64 = base64.b64encode(expected).decode("utf-8")
        assert headers["Hound-Request-Signature"] == expected_b64

    def test_additional_headers_loaded_from_env(self, monkeypatch):
        extra_headers = {"X-Test": "42", "Accept": "application/json"}
        monkeypatch.setenv("HOUNDIFY_EXTRA_HEADERS", json.dumps(extra_headers))
        HoundifyClient = self._import_client()
        client = HoundifyClient("client", "key")

        headers = client._build_auth_headers("req")

        for key, value in extra_headers.items():
            assert headers[key] == value


class TestTextQueryMethod:
    """Test text_query method"""

    @pytest.fixture
    def client_content(self):
        """Load client.py content"""
        return CLIENT_FILE.read_text()

    def test_has_text_query_method(self, client_content):
        """Test that text_query method exists"""
        assert "def text_query" in client_content, \
            "Should have text_query method"

    def test_text_query_is_async(self, client_content):
        """Test that text_query is async"""
        assert "async def text_query" in client_content, \
            "text_query should be async"

    def test_text_query_has_query_param(self, client_content):
        """Test that text_query has query parameter"""
        lines = client_content.split('\n')
        text_query_line = None
        for i, line in enumerate(lines):
            if 'def text_query' in line:
                # Check this line and next few lines for parameters
                func_def = ''.join(lines[i:min(i+5, len(lines))])
                assert 'query' in func_def, "text_query should have query parameter"
                text_query_line = i
                break
        assert text_query_line is not None, "Should find text_query method"

    def test_text_query_has_user_id_param(self, client_content):
        """Test that text_query has user_id parameter"""
        assert "user_id" in client_content, \
            "text_query should have user_id parameter"

    def test_text_query_has_request_id_param(self, client_content):
        """Test that text_query has request_id parameter"""
        assert "request_id" in client_content, \
            "text_query should have request_id parameter"

    def test_text_query_has_docstring(self, client_content):
        """Test that text_query has docstring"""
        lines = client_content.split('\n')
        in_text_query = False
        has_docstring = False
        lines_checked = 0

        for i, line in enumerate(lines):
            if 'async def text_query' in line:
                in_text_query = True
            elif in_text_query:
                lines_checked += 1
                if '"""' in line or "'''" in line:
                    has_docstring = True
                    break
                # Check up to 10 lines for docstring (allows for multi-line signatures)
                elif lines_checked > 10:
                    break

        assert has_docstring, "text_query should have docstring"


class TestVoiceQueryMethod:
    """Test voice_query method"""

    @pytest.fixture
    def client_content(self):
        """Load client.py content"""
        return CLIENT_FILE.read_text()

    def test_has_voice_query_method(self, client_content):
        """Test that voice_query method exists"""
        assert "def voice_query" in client_content, \
            "Should have voice_query method"

    def test_voice_query_is_async(self, client_content):
        """Test that voice_query is async"""
        assert "async def voice_query" in client_content, \
            "voice_query should be async"

    def test_voice_query_has_audio_data_param(self, client_content):
        """Test that voice_query has audio_data parameter"""
        lines = client_content.split('\n')
        for i, line in enumerate(lines):
            if 'def voice_query' in line:
                func_def = ''.join(lines[i:min(i+10, len(lines))])
                assert 'audio_data' in func_def, "voice_query should have audio_data parameter"
                break

    def test_voice_query_has_user_id_param(self, client_content):
        """Test that voice_query has user_id parameter"""
        assert "user_id" in client_content, \
            "voice_query should have user_id parameter"

    def test_voice_query_has_docstring(self, client_content):
        """Test that voice_query has docstring"""
        lines = client_content.split('\n')
        in_voice_query = False
        has_docstring = False
        lines_checked = 0

        for i, line in enumerate(lines):
            if 'async def voice_query' in line:
                in_voice_query = True
            elif in_voice_query:
                lines_checked += 1
                if '"""' in line or "'''" in line:
                    has_docstring = True
                    break
                # Check up to 10 lines for docstring (allows for multi-line signatures)
                elif lines_checked > 10:
                    break

        assert has_docstring, "voice_query should have docstring"


class TestConversationStateManagement:
    """Test conversation state management methods"""

    @pytest.fixture
    def client_content(self):
        """Load client.py content"""
        return CLIENT_FILE.read_text()

    def test_has_enable_conversation_state(self, client_content):
        """Test that enable_conversation_state method exists"""
        assert "def enable_conversation_state" in client_content, \
            "Should have enable_conversation_state method"

    def test_has_disable_conversation_state(self, client_content):
        """Test that disable_conversation_state method exists"""
        assert "def disable_conversation_state" in client_content, \
            "Should have disable_conversation_state method"

    def test_has_clear_conversation_state(self, client_content):
        """Test that clear_conversation_state method exists"""
        assert "def clear_conversation_state" in client_content, \
            "Should have clear_conversation_state method"

    def test_has_get_conversation_state(self, client_content):
        """Test that get_conversation_state method exists"""
        assert "def get_conversation_state" in client_content, \
            "Should have get_conversation_state method"

    def test_has_set_conversation_state(self, client_content):
        """Test that set_conversation_state method exists"""
        assert "def set_conversation_state" in client_content, \
            "Should have set_conversation_state method"

    def test_has_conversation_state_attribute(self, client_content):
        """Test that conversation_state attribute exists"""
        assert "conversation_state" in client_content, \
            "Should have conversation_state attribute"


class TestDocumentation:
    """Test documentation"""

    @pytest.fixture
    def client_content(self):
        """Load client.py content"""
        return CLIENT_FILE.read_text()

    def test_has_module_docstring(self, client_content):
        """Test that module has docstring"""
        assert '"""' in client_content or "'''" in client_content, \
            "Should have module documentation"

    def test_has_multiple_docstrings(self, client_content):
        """Test that methods have docstrings"""
        docstring_count = client_content.count('"""')
        assert docstring_count >= 6, \
            "Should have docstrings for module and methods"


class TestClientStructure:
    """Test overall client structure"""

    @pytest.fixture
    def client_content(self):
        """Load client.py content"""
        return CLIENT_FILE.read_text()

    def test_is_valid_python(self, client_content):
        """Test that file is valid Python"""
        try:
            compile(client_content, CLIENT_FILE, 'exec')
        except SyntaxError as e:
            pytest.fail(f"client.py has syntax error: {e}")

    def test_has_all_required_methods(self, client_content):
        """Test that all required methods are present"""
        required_methods = [
            "text_query",
            "voice_query",
            "enable_conversation_state",
            "disable_conversation_state",
            "clear_conversation_state",
            "get_conversation_state",
            "set_conversation_state"
        ]
        for method in required_methods:
            assert f"def {method}" in client_content, \
                f"Should have {method} method"


class TestImportability:
    """Test that client module can be imported"""

    def test_can_import_houndify_module(self):
        """Test that houndify module can be imported"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from integrations.houndify import client
            assert client is not None, \
                "houndify.client module should be importable"
        except ImportError as e:
            pytest.fail(f"Cannot import houndify.client: {e}")

    def test_can_import_houndify_client_class(self):
        """Test that HoundifyClient can be imported"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from integrations.houndify.client import HoundifyClient
            assert HoundifyClient is not None, \
                "HoundifyClient class should be importable"
        except ImportError as e:
            pytest.fail(f"Cannot import HoundifyClient: {e}")

    def test_can_instantiate_client(self):
        """Test that HoundifyClient can be instantiated"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from integrations.houndify.client import HoundifyClient
            client = HoundifyClient(
                client_id="test_client_id",
                client_key="test_client_key"
            )
            assert client is not None, \
                "Should be able to instantiate HoundifyClient"
            assert client.client_id == "test_client_id", \
                "Should store client_id"
            assert client.client_key == "test_client_key", \
                "Should store client_key"
        except Exception as e:
            pytest.fail(f"Cannot instantiate HoundifyClient: {e}")


class TestMethodSignatures:
    """Test method signatures with inspection"""

    def test_text_query_signature(self):
        """Test text_query method signature"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from integrations.houndify.client import HoundifyClient
            import inspect

            sig = inspect.signature(HoundifyClient.text_query)
            params = sig.parameters

            assert 'query' in params, "Should have query parameter"
            assert 'user_id' in params, "Should have user_id parameter"
            assert 'request_id' in params, "Should have request_id parameter"

            # Check it's async
            assert inspect.iscoroutinefunction(HoundifyClient.text_query), \
                "text_query should be async"
        except ImportError as e:
            pytest.fail(f"Cannot import HoundifyClient: {e}")

    def test_voice_query_signature(self):
        """Test voice_query method signature"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from integrations.houndify.client import HoundifyClient
            import inspect

            sig = inspect.signature(HoundifyClient.voice_query)
            params = sig.parameters

            assert 'audio_data' in params, "Should have audio_data parameter"
            assert 'user_id' in params, "Should have user_id parameter"
            assert 'request_id' in params, "Should have request_id parameter"

            # Check it's async
            assert inspect.iscoroutinefunction(HoundifyClient.voice_query), \
                "voice_query should be async"
        except ImportError as e:
            pytest.fail(f"Cannot import HoundifyClient: {e}")


class TestTaskRequirements:
    """Test TASK-106 specific requirements"""

    @pytest.fixture
    def client_content(self):
        """Load client.py content"""
        return CLIENT_FILE.read_text()

    def test_task_106_houndify_client_class(self, client_content):
        """Test TASK-106 requirement: HoundifyClient class"""
        assert "class HoundifyClient" in client_content, \
            "TASK-106 requirement: Must implement HoundifyClient class"

    def test_task_106_authentication(self, client_content):
        """Test TASK-106 requirement: Client ID + Client Key authentication"""
        assert "client_id" in client_content and "client_key" in client_content, \
            "TASK-106 requirement: Must use client_id and client_key for auth"

    def test_task_106_text_query(self, client_content):
        """Test TASK-106 requirement: text_query method"""
        assert "async def text_query" in client_content, \
            "TASK-106 requirement: Must implement async text_query method"

    def test_task_106_voice_query(self, client_content):
        """Test TASK-106 requirement: voice_query method"""
        assert "async def voice_query" in client_content, \
            "TASK-106 requirement: Must implement async voice_query method"

    def test_task_106_conversation_state(self, client_content):
        """Test TASK-106 requirement: Conversation state management"""
        methods = [
            "enable_conversation_state",
            "disable_conversation_state",
            "clear_conversation_state",
            "get_conversation_state",
            "set_conversation_state"
        ]
        for method in methods:
            assert f"def {method}" in client_content, \
                f"TASK-106 requirement: Must implement {method}"

    def test_task_106_houndify_endpoints(self, client_content):
        """Test TASK-106 requirement: Houndify API endpoints"""
        assert "api.houndify.com" in client_content, \
            "TASK-106 requirement: Must use api.houndify.com endpoints"
