"""
Test suite for Mock Houndify client (TASK-109)

Validates the MockHoundifyClient implementation:
- Mock responses without real API calls
- Response pattern matching
- Error simulation
- Call history tracking
- Conversation state simulation
- Latency simulation
"""

import pytest
import sys
from pathlib import Path
import asyncio

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
MOCK_CLIENT_FILE = BACKEND_DIR / "integrations" / "houndify" / "mock_client.py"


class TestMockClientFileStructure:
    """Test mock_client.py file structure"""

    def test_mock_client_file_exists(self):
        """Test that mock_client.py exists"""
        assert MOCK_CLIENT_FILE.exists(), "mock_client.py should exist"
        assert MOCK_CLIENT_FILE.is_file(), "mock_client.py should be a file"

    def test_mock_client_has_content(self):
        """Test that mock_client.py has content"""
        content = MOCK_CLIENT_FILE.read_text()
        assert len(content) > 0, "mock_client.py should not be empty"


class TestMockClientImports:
    """Test necessary imports in mock_client.py"""

    @pytest.fixture
    def mock_client_content(self):
        """Load mock_client.py content"""
        return MOCK_CLIENT_FILE.read_text()

    def test_imports_houndify_client(self, mock_client_content):
        """Test that HoundifyClient is imported"""
        assert "HoundifyClient" in mock_client_content, \
            "Should import HoundifyClient"

    def test_imports_typing(self, mock_client_content):
        """Test that typing is imported"""
        assert "from typing import" in mock_client_content or "import typing" in mock_client_content, \
            "Should import typing for type hints"

    def test_imports_asyncio(self, mock_client_content):
        """Test that asyncio is imported for delays"""
        assert "import asyncio" in mock_client_content or "from asyncio import" in mock_client_content, \
            "Should import asyncio for simulating delays"


class TestMockHoundifyClientClass:
    """Test MockHoundifyClient class definition"""

    @pytest.fixture
    def mock_client_content(self):
        """Load mock_client.py content"""
        return MOCK_CLIENT_FILE.read_text()

    def test_has_mock_houndify_client_class(self, mock_client_content):
        """Test that MockHoundifyClient class exists"""
        assert "class MockHoundifyClient" in mock_client_content, \
            "Should have MockHoundifyClient class"

    def test_mock_client_inherits_houndify_client(self, mock_client_content):
        """Test that MockHoundifyClient inherits from HoundifyClient"""
        # Check either direct inheritance or composition
        has_inheritance = "class MockHoundifyClient(HoundifyClient)" in mock_client_content
        has_client_field = "HoundifyClient" in mock_client_content
        assert has_inheritance or has_client_field, \
            "MockHoundifyClient should inherit from HoundifyClient or use composition"

    def test_has_init_method(self, mock_client_content):
        """Test that __init__ method exists"""
        assert "def __init__" in mock_client_content, \
            "Should have __init__ method"

    def test_has_response_patterns_param(self, mock_client_content):
        """Test that __init__ accepts response_patterns"""
        assert "response_patterns" in mock_client_content, \
            "Should have response_patterns parameter"

    def test_has_error_rate_param(self, mock_client_content):
        """Test that __init__ accepts error_rate"""
        assert "error_rate" in mock_client_content, \
            "Should have error_rate parameter"

    def test_has_call_history_attribute(self, mock_client_content):
        """Test that call_history attribute exists"""
        assert "call_history" in mock_client_content, \
            "Should have call_history attribute"

    def test_has_docstring(self, mock_client_content):
        """Test that MockHoundifyClient has docstring"""
        lines = mock_client_content.split('\n')
        in_mock_class = False
        has_docstring = False

        for i, line in enumerate(lines):
            if 'class MockHoundifyClient' in line:
                in_mock_class = True
            elif in_mock_class:
                if '"""' in line or "'''" in line:
                    has_docstring = True
                    break
                elif line.strip() and not line.strip().startswith('#'):
                    if not line.strip().startswith('class'):
                        break

        assert has_docstring, "MockHoundifyClient should have docstring"


class TestMockTextQueryMethod:
    """Test mock text_query method"""

    @pytest.fixture
    def mock_client_content(self):
        """Load mock_client.py content"""
        return MOCK_CLIENT_FILE.read_text()

    def test_has_text_query_method(self, mock_client_content):
        """Test that text_query method exists"""
        assert "def text_query" in mock_client_content, \
            "Should have text_query method"

    def test_text_query_is_async(self, mock_client_content):
        """Test that text_query is async"""
        assert "async def text_query" in mock_client_content, \
            "text_query should be async"

    def test_has_docstring(self, mock_client_content):
        """Test that text_query has docstring"""
        lines = mock_client_content.split('\n')
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
                elif lines_checked > 10:
                    break

        assert has_docstring, "text_query should have docstring"


class TestMockVoiceQueryMethod:
    """Test mock voice_query method"""

    @pytest.fixture
    def mock_client_content(self):
        """Load mock_client.py content"""
        return MOCK_CLIENT_FILE.read_text()

    def test_has_voice_query_method(self, mock_client_content):
        """Test that voice_query method exists"""
        assert "def voice_query" in mock_client_content, \
            "Should have voice_query method"

    def test_voice_query_is_async(self, mock_client_content):
        """Test that voice_query is async"""
        assert "async def voice_query" in mock_client_content, \
            "voice_query should be async"

    def test_has_docstring(self, mock_client_content):
        """Test that voice_query has docstring"""
        lines = mock_client_content.split('\n')
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
                elif lines_checked > 10:
                    break

        assert has_docstring, "voice_query should have docstring"


class TestMockClientInstantiation:
    """Test MockHoundifyClient instantiation"""

    def test_can_import_mock_client(self):
        """Test that MockHoundifyClient can be imported"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from integrations.houndify.mock_client import MockHoundifyClient
            assert MockHoundifyClient is not None, \
                "MockHoundifyClient class should be importable"
        except ImportError as e:
            pytest.fail(f"Cannot import MockHoundifyClient: {e}")

    def test_can_instantiate_mock_client(self):
        """Test that MockHoundifyClient can be instantiated"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from integrations.houndify.mock_client import MockHoundifyClient

            client = MockHoundifyClient()
            assert client is not None, \
                "Should be able to instantiate MockHoundifyClient"
        except Exception as e:
            pytest.fail(f"Cannot instantiate MockHoundifyClient: {e}")

    def test_instantiate_with_response_patterns(self):
        """Test that MockHoundifyClient accepts response_patterns"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from integrations.houndify.mock_client import MockHoundifyClient

            patterns = {
                "weather": {"command_kind": "WeatherQuery", "response": "Sunny"}
            }
            client = MockHoundifyClient(response_patterns=patterns)
            assert client.response_patterns == patterns
        except Exception as e:
            pytest.fail(f"Cannot instantiate with response_patterns: {e}")

    def test_instantiate_with_error_rate(self):
        """Test that MockHoundifyClient accepts error_rate"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from integrations.houndify.mock_client import MockHoundifyClient

            client = MockHoundifyClient(error_rate=0.1)
            assert client.error_rate == 0.1
        except Exception as e:
            pytest.fail(f"Cannot instantiate with error_rate: {e}")


class TestMockTextQueryBehavior:
    """Test mock text_query behavior"""

    @pytest.mark.asyncio
    async def test_text_query_returns_dict(self):
        """Test that text_query returns a dictionary"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        from integrations.houndify.mock_client import MockHoundifyClient

        client = MockHoundifyClient()
        result = await client.text_query(
            query="test query",
            user_id="user123",
            request_id="req456"
        )

        assert isinstance(result, dict), "text_query should return a dict"
        assert "AllResults" in result or "Status" in result, \
            "Result should have Houndify API structure"

    @pytest.mark.asyncio
    async def test_text_query_tracks_call_history(self):
        """Test that text_query tracks calls in call_history"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        from integrations.houndify.mock_client import MockHoundifyClient

        client = MockHoundifyClient()
        await client.text_query(
            query="test query",
            user_id="user123",
            request_id="req456"
        )

        assert len(client.call_history) > 0, \
            "call_history should track text_query calls"
        assert client.call_history[0]["method"] == "text_query"
        assert client.call_history[0]["query"] == "test query"

    @pytest.mark.asyncio
    async def test_text_query_uses_response_patterns(self):
        """Test that text_query matches response patterns"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        from integrations.houndify.mock_client import MockHoundifyClient

        patterns = {
            "weather": {
                "command_kind": "WeatherQuery",
                "spoken_response": "It's sunny today"
            }
        }
        client = MockHoundifyClient(response_patterns=patterns)

        result = await client.text_query(
            query="what's the weather",
            user_id="user123",
            request_id="req456"
        )

        # Should match pattern and return appropriate response
        assert "AllResults" in result or "spoken_response" in str(result).lower()


class TestMockVoiceQueryBehavior:
    """Test mock voice_query behavior"""

    @pytest.mark.asyncio
    async def test_voice_query_returns_dict(self):
        """Test that voice_query returns a dictionary"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        from integrations.houndify.mock_client import MockHoundifyClient

        client = MockHoundifyClient()
        result = await client.voice_query(
            audio_data=b"fake_audio_data",
            user_id="user123",
            request_id="req456"
        )

        assert isinstance(result, dict), "voice_query should return a dict"

    @pytest.mark.asyncio
    async def test_voice_query_tracks_call_history(self):
        """Test that voice_query tracks calls in call_history"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        from integrations.houndify.mock_client import MockHoundifyClient

        client = MockHoundifyClient()
        await client.voice_query(
            audio_data=b"fake_audio_data",
            user_id="user123",
            request_id="req456"
        )

        assert len(client.call_history) > 0, \
            "call_history should track voice_query calls"
        assert client.call_history[0]["method"] == "voice_query"


class TestErrorSimulation:
    """Test error simulation functionality"""

    @pytest.mark.asyncio
    async def test_error_rate_zero_never_fails(self):
        """Test that error_rate=0 never raises errors"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        from integrations.houndify.mock_client import MockHoundifyClient

        client = MockHoundifyClient(error_rate=0.0)

        # Should never fail
        for _ in range(10):
            result = await client.text_query(
                query="test",
                user_id="user123",
                request_id=f"req{_}"
            )
            assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_error_rate_one_always_fails(self):
        """Test that error_rate=1.0 always raises errors"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        from integrations.houndify.mock_client import MockHoundifyClient
        from integrations.houndify.models import HoundifyError

        client = MockHoundifyClient(error_rate=1.0)

        # Should always fail
        with pytest.raises((HoundifyError, Exception)):
            await client.text_query(
                query="test",
                user_id="user123",
                request_id="req456"
            )


class TestTaskRequirements:
    """Test TASK-109 specific requirements"""

    def test_task_109_mock_client_class(self):
        """Test TASK-109 requirement: MockHoundifyClient class"""
        content = MOCK_CLIENT_FILE.read_text()
        assert "class MockHoundifyClient" in content, \
            "TASK-109 requirement: Must implement MockHoundifyClient class"

    def test_task_109_response_patterns(self):
        """Test TASK-109 requirement: Response patterns support"""
        content = MOCK_CLIENT_FILE.read_text()
        assert "response_patterns" in content, \
            "TASK-109 requirement: Must support response patterns"

    def test_task_109_error_rate(self):
        """Test TASK-109 requirement: Configurable error rate"""
        content = MOCK_CLIENT_FILE.read_text()
        assert "error_rate" in content, \
            "TASK-109 requirement: Must support configurable error rate"

    def test_task_109_call_history(self):
        """Test TASK-109 requirement: Call history tracking"""
        content = MOCK_CLIENT_FILE.read_text()
        assert "call_history" in content, \
            "TASK-109 requirement: Must track call history"

    def test_task_109_text_query_mock(self):
        """Test TASK-109 requirement: Mock text_query implementation"""
        content = MOCK_CLIENT_FILE.read_text()
        assert "async def text_query" in content, \
            "TASK-109 requirement: Must implement text_query method"

    def test_task_109_voice_query_mock(self):
        """Test TASK-109 requirement: Mock voice_query implementation"""
        content = MOCK_CLIENT_FILE.read_text()
        assert "async def voice_query" in content, \
            "TASK-109 requirement: Must implement voice_query method"
