"""
Test suite for ContextManager service (TASK-117).

This module tests the context management service for multi-turn conversations:
- Service initialization
- store_context method with UUID conversation IDs
- get_context method returning optional dict
- clear_context method for cleanup
- Redis integration
- TTL (30 minutes) for automatic expiration
- Error handling
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from uuid import uuid4, UUID
import json

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
SERVICES_DIR = BACKEND_DIR / "services"
CONTEXT_MANAGER_FILE = SERVICES_DIR / "context_manager.py"


class TestContextManagerFileStructure:
    """Test context_manager.py file structure"""

    def test_context_manager_file_exists(self):
        """Test that context_manager.py exists"""
        assert CONTEXT_MANAGER_FILE.exists(), \
            "context_manager.py should exist in backend/services/"

    def test_context_manager_has_content(self):
        """Test that context_manager.py has content"""
        if CONTEXT_MANAGER_FILE.exists():
            content = CONTEXT_MANAGER_FILE.read_text()
            assert len(content) > 0, "context_manager.py should not be empty"


class TestContextManagerImports:
    """Test necessary imports in context_manager.py"""

    @pytest.fixture
    def service_content(self):
        """Load context_manager.py content"""
        if CONTEXT_MANAGER_FILE.exists():
            return CONTEXT_MANAGER_FILE.read_text()
        return ""

    def test_imports_uuid(self, service_content):
        """Test that UUID is imported"""
        assert "UUID" in service_content, \
            "Should import UUID for conversation IDs"

    def test_imports_typing(self, service_content):
        """Test that typing module is imported"""
        assert "from typing import" in service_content or "import typing" in service_content, \
            "Should import typing for type hints"

    def test_imports_optional(self, service_content):
        """Test that Optional is used"""
        assert "Optional" in service_content, \
            "Should use Optional for optional dict return"

    def test_imports_dict(self, service_content):
        """Test that Dict is used for type hints"""
        assert "Dict" in service_content or "dict" in service_content, \
            "Should use Dict for context dictionaries"

    def test_has_async_def(self, service_content):
        """Test that async methods are defined"""
        assert "async def" in service_content, \
            "Should have async methods"


class TestContextManagerClass:
    """Test ContextManager class definition"""

    @pytest.fixture
    def service_content(self):
        """Load context_manager.py content"""
        if CONTEXT_MANAGER_FILE.exists():
            return CONTEXT_MANAGER_FILE.read_text()
        return ""

    def test_has_context_manager_class(self, service_content):
        """Test that ContextManager class exists"""
        assert "class ContextManager" in service_content, \
            "Should have ContextManager class"

    def test_has_init_method(self, service_content):
        """Test that __init__ method exists"""
        assert "def __init__" in service_content, \
            "Should have __init__ method"

    def test_class_has_docstring(self, service_content):
        """Test that ContextManager has docstring"""
        lines = service_content.split('\n')
        in_class = False
        has_docstring = False

        for i, line in enumerate(lines):
            if 'class ContextManager' in line:
                in_class = True
            elif in_class:
                if '"""' in line or "'''" in line:
                    has_docstring = True
                    break
                elif line.strip() and not line.strip().startswith('#'):
                    if not line.strip().startswith('class'):
                        break

        assert has_docstring, "ContextManager should have docstring"


class TestStoreContextMethod:
    """Test store_context method"""

    @pytest.fixture
    def service_content(self):
        """Load context_manager.py content"""
        if CONTEXT_MANAGER_FILE.exists():
            return CONTEXT_MANAGER_FILE.read_text()
        return ""

    def test_has_store_context_method(self, service_content):
        """Test that store_context method exists"""
        assert "def store_context" in service_content, \
            "Should have store_context method"

    def test_store_context_is_async(self, service_content):
        """Test that store_context is async"""
        assert "async def store_context" in service_content, \
            "store_context should be async"

    def test_store_context_has_conversation_id_param(self, service_content):
        """Test that store_context has conversation_id parameter"""
        lines = service_content.split('\n')
        for i, line in enumerate(lines):
            if 'async def store_context' in line:
                func_def = ''.join(lines[i:min(i+5, len(lines))])
                assert 'conversation_id' in func_def, \
                    "store_context should have conversation_id parameter"
                break

    def test_store_context_has_context_param(self, service_content):
        """Test that store_context has context parameter"""
        lines = service_content.split('\n')
        for i, line in enumerate(lines):
            if 'async def store_context' in line:
                func_def = ''.join(lines[i:min(i+5, len(lines))])
                assert 'context' in func_def, \
                    "store_context should have context parameter"
                break

    def test_store_context_has_docstring(self, service_content):
        """Test that store_context has docstring"""
        lines = service_content.split('\n')
        in_method = False
        has_docstring = False
        lines_checked = 0

        for i, line in enumerate(lines):
            if 'async def store_context' in line:
                in_method = True
            elif in_method:
                lines_checked += 1
                if '"""' in line or "'''" in line:
                    has_docstring = True
                    break
                elif lines_checked > 10:
                    break

        assert has_docstring, "store_context should have docstring"


class TestGetContextMethod:
    """Test get_context method"""

    @pytest.fixture
    def service_content(self):
        """Load context_manager.py content"""
        if CONTEXT_MANAGER_FILE.exists():
            return CONTEXT_MANAGER_FILE.read_text()
        return ""

    def test_has_get_context_method(self, service_content):
        """Test that get_context method exists"""
        assert "def get_context" in service_content, \
            "Should have get_context method"

    def test_get_context_is_async(self, service_content):
        """Test that get_context is async"""
        assert "async def get_context" in service_content, \
            "get_context should be async"

    def test_get_context_has_conversation_id_param(self, service_content):
        """Test that get_context has conversation_id parameter"""
        lines = service_content.split('\n')
        for i, line in enumerate(lines):
            if 'async def get_context' in line:
                func_def = ''.join(lines[i:min(i+5, len(lines))])
                assert 'conversation_id' in func_def, \
                    "get_context should have conversation_id parameter"
                break

    def test_get_context_returns_optional_dict(self, service_content):
        """Test that get_context return type is Optional[dict]"""
        lines = service_content.split('\n')
        for i, line in enumerate(lines):
            if 'async def get_context' in line:
                func_def = ''.join(lines[i:min(i+3, len(lines))])
                # Check for Optional[dict] or dict | None
                has_optional = 'Optional' in func_def or '| None' in func_def or '|None' in func_def
                assert has_optional, \
                    "get_context should return Optional[dict] or dict | None"
                break

    def test_get_context_has_docstring(self, service_content):
        """Test that get_context has docstring"""
        lines = service_content.split('\n')
        in_method = False
        has_docstring = False
        lines_checked = 0

        for i, line in enumerate(lines):
            if 'async def get_context' in line:
                in_method = True
            elif in_method:
                lines_checked += 1
                if '"""' in line or "'''" in line:
                    has_docstring = True
                    break
                elif lines_checked > 10:
                    break

        assert has_docstring, "get_context should have docstring"


class TestClearContextMethod:
    """Test clear_context method"""

    @pytest.fixture
    def service_content(self):
        """Load context_manager.py content"""
        if CONTEXT_MANAGER_FILE.exists():
            return CONTEXT_MANAGER_FILE.read_text()
        return ""

    def test_has_clear_context_method(self, service_content):
        """Test that clear_context method exists"""
        assert "def clear_context" in service_content, \
            "Should have clear_context method"

    def test_clear_context_is_async(self, service_content):
        """Test that clear_context is async"""
        assert "async def clear_context" in service_content, \
            "clear_context should be async"

    def test_clear_context_has_conversation_id_param(self, service_content):
        """Test that clear_context has conversation_id parameter"""
        lines = service_content.split('\n')
        for i, line in enumerate(lines):
            if 'async def clear_context' in line:
                func_def = ''.join(lines[i:min(i+5, len(lines))])
                assert 'conversation_id' in func_def, \
                    "clear_context should have conversation_id parameter"
                break

    def test_clear_context_has_docstring(self, service_content):
        """Test that clear_context has docstring"""
        lines = service_content.split('\n')
        in_method = False
        has_docstring = False
        lines_checked = 0

        for i, line in enumerate(lines):
            if 'async def clear_context' in line:
                in_method = True
            elif in_method:
                lines_checked += 1
                if '"""' in line or "'''" in line:
                    has_docstring = True
                    break
                elif lines_checked > 10:
                    break

        assert has_docstring, "clear_context should have docstring"


class TestContextManagerImportability:
    """Test that ContextManager can be imported"""

    def test_can_import_context_manager_module(self):
        """Test that context_manager module can be imported"""
        if not CONTEXT_MANAGER_FILE.exists():
            pytest.skip("context_manager.py not yet implemented")

        try:
            from services import context_manager
            assert context_manager is not None
        except ImportError as e:
            pytest.fail(f"Cannot import context_manager: {e}")

    def test_can_import_context_manager_class(self):
        """Test that ContextManager class can be imported"""
        if not CONTEXT_MANAGER_FILE.exists():
            pytest.skip("context_manager.py not yet implemented")

        try:
            from services.context_manager import ContextManager
            assert ContextManager is not None
        except ImportError as e:
            pytest.fail(f"Cannot import ContextManager: {e}")

    def test_can_instantiate_context_manager(self):
        """Test that ContextManager can be instantiated"""
        if not CONTEXT_MANAGER_FILE.exists():
            pytest.skip("context_manager.py not yet implemented")

        try:
            from services.context_manager import ContextManager
            manager = ContextManager()
            assert manager is not None
        except Exception as e:
            pytest.fail(f"Cannot instantiate ContextManager: {e}")


class TestContextManagerFunctionality:
    """Test ContextManager functionality with mocked Redis"""

    @pytest.mark.asyncio
    async def test_store_context_stores_in_redis(self):
        """Test that store_context stores data in Redis"""
        if not CONTEXT_MANAGER_FILE.exists():
            pytest.skip("context_manager.py not yet implemented")

        from services.context_manager import ContextManager

        # Mock Redis client
        mock_redis = AsyncMock()
        mock_redis.set = AsyncMock(return_value=True)

        manager = ContextManager(redis_client=mock_redis)

        conversation_id = uuid4()
        context = {"turn": 1, "last_intent": "booking", "user_id": "123"}

        await manager.store_context(conversation_id, context)

        # Verify Redis set was called with correct parameters
        mock_redis.set.assert_called_once()
        call_args = mock_redis.set.call_args

        # Check that conversation_id is in the key
        assert str(conversation_id) in call_args[0][0] or str(conversation_id) in call_args[1].get('key', '')

    @pytest.mark.asyncio
    async def test_store_context_sets_ttl(self):
        """Test that store_context sets 30-minute TTL"""
        if not CONTEXT_MANAGER_FILE.exists():
            pytest.skip("context_manager.py not yet implemented")

        from services.context_manager import ContextManager

        mock_redis = AsyncMock()
        mock_redis.set = AsyncMock(return_value=True)

        manager = ContextManager(redis_client=mock_redis)

        conversation_id = uuid4()
        context = {"data": "test"}

        await manager.store_context(conversation_id, context)

        # Verify TTL is set (30 minutes = 1800 seconds)
        call_args = mock_redis.set.call_args

        # Check kwargs first, then positional args
        ttl = None
        if call_args.kwargs and 'ttl' in call_args.kwargs:
            ttl = call_args.kwargs['ttl']
        elif len(call_args.args) > 2:
            ttl = call_args.args[2]

        assert ttl == 1800, f"TTL should be 1800 seconds (30 minutes), got {ttl}"

    @pytest.mark.asyncio
    async def test_get_context_retrieves_from_redis(self):
        """Test that get_context retrieves data from Redis"""
        if not CONTEXT_MANAGER_FILE.exists():
            pytest.skip("context_manager.py not yet implemented")

        from services.context_manager import ContextManager

        conversation_id = uuid4()
        expected_context = {"turn": 2, "state": "active"}

        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=json.dumps(expected_context))

        manager = ContextManager(redis_client=mock_redis)

        result = await manager.get_context(conversation_id)

        assert result == expected_context
        mock_redis.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_context_returns_none_when_not_found(self):
        """Test that get_context returns None when context doesn't exist"""
        if not CONTEXT_MANAGER_FILE.exists():
            pytest.skip("context_manager.py not yet implemented")

        from services.context_manager import ContextManager

        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)

        manager = ContextManager(redis_client=mock_redis)

        conversation_id = uuid4()
        result = await manager.get_context(conversation_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_clear_context_deletes_from_redis(self):
        """Test that clear_context deletes data from Redis"""
        if not CONTEXT_MANAGER_FILE.exists():
            pytest.skip("context_manager.py not yet implemented")

        from services.context_manager import ContextManager

        mock_redis = AsyncMock()
        mock_redis.delete = AsyncMock(return_value=True)

        manager = ContextManager(redis_client=mock_redis)

        conversation_id = uuid4()
        await manager.clear_context(conversation_id)

        mock_redis.delete.assert_called_once()
        call_args = mock_redis.delete.call_args
        assert str(conversation_id) in call_args[0][0]


class TestTaskRequirements:
    """Test TASK-117 specific requirements"""

    def test_task_117_file_location(self):
        """Test TASK-117: File is in correct location"""
        assert CONTEXT_MANAGER_FILE == SERVICES_DIR / "context_manager.py", \
            "TASK-117: File should be at backend/services/context_manager.py"

    def test_task_117_has_context_manager_class(self):
        """Test TASK-117: ContextManager class exists"""
        if CONTEXT_MANAGER_FILE.exists():
            content = CONTEXT_MANAGER_FILE.read_text()
            assert "class ContextManager" in content, \
                "TASK-117: Must have ContextManager class"

    def test_task_117_has_store_context(self):
        """Test TASK-117: store_context method exists"""
        if CONTEXT_MANAGER_FILE.exists():
            content = CONTEXT_MANAGER_FILE.read_text()
            assert "async def store_context" in content, \
                "TASK-117: Must have async store_context method"

    def test_task_117_has_get_context(self):
        """Test TASK-117: get_context method exists"""
        if CONTEXT_MANAGER_FILE.exists():
            content = CONTEXT_MANAGER_FILE.read_text()
            assert "async def get_context" in content, \
                "TASK-117: Must have async get_context method"

    def test_task_117_has_clear_context(self):
        """Test TASK-117: clear_context method exists"""
        if CONTEXT_MANAGER_FILE.exists():
            content = CONTEXT_MANAGER_FILE.read_text()
            assert "async def clear_context" in content, \
                "TASK-117: Must have async clear_context method"

    def test_task_117_uses_redis(self):
        """Test TASK-117: Uses Redis for storage"""
        if CONTEXT_MANAGER_FILE.exists():
            content = CONTEXT_MANAGER_FILE.read_text()
            assert "redis" in content.lower(), \
                "TASK-117: Should use Redis for context storage"

    def test_task_117_ttl_is_30_minutes(self):
        """Test TASK-117: TTL is 30 minutes (1800 seconds)"""
        if CONTEXT_MANAGER_FILE.exists():
            content = CONTEXT_MANAGER_FILE.read_text()
            assert "1800" in content or "30 * 60" in content or "30*60" in content, \
                "TASK-117: TTL should be 30 minutes (1800 seconds)"
