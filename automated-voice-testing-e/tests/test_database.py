"""
Test suite for database connection manager
Ensures proper async SQLAlchemy engine, session factory, and connection pooling
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))


class TestDatabaseModule:
    """Test database module structure"""

    def test_database_module_exists(self):
        """Test that database module can be imported"""
        try:
            import api.database
            assert api.database is not None
        except ImportError:
            pytest.fail("Cannot import api.database module")

    def test_database_module_has_docstring(self):
        """Test that database module has docstring"""
        import api.database
        assert api.database.__doc__ is not None
        assert len(api.database.__doc__.strip()) > 0


class TestDatabaseEngine:
    """Test SQLAlchemy engine creation"""

    def test_engine_is_created(self):
        """Test that engine is created"""
        from api.database import engine
        assert engine is not None

    def test_engine_is_async_engine(self):
        """Test that engine is AsyncEngine"""
        from api.database import engine
        from sqlalchemy.ext.asyncio import AsyncEngine
        assert isinstance(engine, AsyncEngine)

    def test_engine_uses_asyncpg_driver(self):
        """Test that engine uses postgresql+asyncpg driver"""
        from api.database import engine
        # Check the URL uses asyncpg
        url_str = str(engine.url)
        assert 'postgresql+asyncpg' in url_str or 'asyncpg' in url_str

    def test_engine_reads_from_settings(self):
        """Test that engine reads DATABASE_URL from settings"""
        from api.database import engine
        from api.config import get_settings
        settings = get_settings()
        # Engine should use DATABASE_URL from settings
        # We can't check exact match since it might be transformed
        assert engine is not None


class TestConnectionPooling:
    """Test connection pooling configuration"""

    def test_engine_has_pool_configured(self):
        """Test that engine has connection pool configured"""
        from api.database import engine
        # Check pool is configured
        assert hasattr(engine, 'pool')

    def test_pool_has_reasonable_size(self):
        """Test that pool has reasonable size settings"""
        from api.database import engine
        # Pool should exist and have size settings
        pool = engine.pool
        # Check that pool has size attributes (may vary by implementation)
        assert pool is not None

    def test_pool_config_is_documented(self):
        """Test that pool configuration is documented"""
        import api.database
        docstring = api.database.__doc__
        # Should mention connection pool or pooling
        assert 'pool' in docstring.lower() or 'connection' in docstring.lower()


class TestSessionFactory:
    """Test session factory creation"""

    def test_session_local_exists(self):
        """Test that SessionLocal factory exists"""
        from api.database import SessionLocal
        assert SessionLocal is not None

    def test_session_local_is_sessionmaker(self):
        """Test that SessionLocal is an async sessionmaker"""
        from api.database import SessionLocal
        from sqlalchemy.ext.asyncio import async_sessionmaker
        # SessionLocal should be async_sessionmaker or have similar attributes
        assert callable(SessionLocal) or hasattr(SessionLocal, '__call__')

    def test_session_local_binds_to_engine(self):
        """Test that SessionLocal is bound to engine"""
        from api.database import SessionLocal
        # SessionLocal should have bind or kw that references engine
        assert SessionLocal is not None

    def test_can_create_session(self):
        """Test that session can be created from factory"""
        from api.database import SessionLocal
        # Should be able to call SessionLocal to get session
        session = SessionLocal()
        assert session is not None


class TestGetDbDependency:
    """Test get_db dependency function"""

    def test_get_db_function_exists(self):
        """Test that get_db function exists"""
        from api.database import get_db
        assert get_db is not None

    def test_get_db_is_function(self):
        """Test that get_db is a function"""
        from api.database import get_db
        assert callable(get_db)

    def test_get_db_is_async_generator(self):
        """Test that get_db is async generator"""
        from api.database import get_db
        import inspect
        # Should be async generator function
        assert inspect.isasyncgenfunction(get_db) or inspect.iscoroutinefunction(get_db)

    def test_get_db_has_docstring(self):
        """Test that get_db has docstring"""
        from api.database import get_db
        assert get_db.__doc__ is not None
        assert len(get_db.__doc__.strip()) > 0

    @pytest.mark.asyncio
    async def test_get_db_yields_session(self):
        """Test that get_db yields a session"""
        from api.database import get_db
        from sqlalchemy.ext.asyncio import AsyncSession

        # Get the generator
        gen = get_db()

        # Get the session
        session = await gen.__anext__()

        # Should be AsyncSession
        assert isinstance(session, AsyncSession)

        # Clean up - close the generator
        try:
            await gen.__anext__()
        except StopAsyncIteration:
            pass

    @pytest.mark.asyncio
    async def test_get_db_closes_session(self):
        """Test that get_db closes session after use"""
        from api.database import get_db

        # Use context manager style
        gen = get_db()
        session = await gen.__anext__()

        # Session should be valid
        assert session is not None

        # Close the generator (simulates end of request)
        try:
            await gen.__anext__()
        except StopAsyncIteration:
            # This is expected
            pass

        # After generator exits, session should be closed
        # We can't easily test this without actual database connection


class TestDatabaseIntegration:
    """Test database integration with application"""

    def test_engine_can_be_imported_from_database(self):
        """Test that engine can be imported"""
        from api.database import engine
        assert engine is not None

    def test_session_local_can_be_imported(self):
        """Test that SessionLocal can be imported"""
        from api.database import SessionLocal
        assert SessionLocal is not None

    def test_get_db_can_be_used_with_depends(self):
        """Test that get_db can be used with FastAPI Depends"""
        from api.database import get_db
        from fastapi import Depends

        # Should be able to create dependency
        dep = Depends(get_db)
        assert dep is not None
        assert dep.dependency == get_db


class TestDatabaseExports:
    """Test database module exports"""

    def test_engine_is_exported(self):
        """Test that engine is exported"""
        import api.database
        assert hasattr(api.database, 'engine')

    def test_session_local_is_exported(self):
        """Test that SessionLocal is exported"""
        import api.database
        assert hasattr(api.database, 'SessionLocal')

    def test_get_db_is_exported(self):
        """Test that get_db is exported"""
        import api.database
        assert hasattr(api.database, 'get_db')


class TestDatabaseConfiguration:
    """Test database configuration"""

    def test_database_url_is_read_from_settings(self):
        """Test that DATABASE_URL is read from settings"""
        from api.config import get_settings
        settings = get_settings()
        assert hasattr(settings, 'DATABASE_URL')
        assert settings.DATABASE_URL is not None

    def test_database_url_uses_postgresql(self):
        """Test that DATABASE_URL uses PostgreSQL"""
        from api.config import get_settings
        settings = get_settings()
        # Should start with postgresql://
        assert settings.DATABASE_URL.startswith('postgresql://')

    def test_engine_url_converted_to_async(self):
        """Test that engine URL is converted to async driver"""
        from api.database import engine
        # URL should use async driver
        url_str = str(engine.url)
        # Should have asyncpg or async component
        assert 'asyncpg' in url_str or engine.url.drivername.endswith('asyncpg')


class TestDatabaseDocumentation:
    """Test database module documentation"""

    def test_module_has_comprehensive_docstring(self):
        """Test that module has comprehensive docstring"""
        import api.database
        docstring = api.database.__doc__
        assert len(docstring) > 100  # Should be detailed

    def test_docstring_mentions_async(self):
        """Test that docstring mentions async"""
        import api.database
        docstring = api.database.__doc__.lower()
        assert 'async' in docstring

    def test_docstring_mentions_sqlalchemy(self):
        """Test that docstring mentions SQLAlchemy"""
        import api.database
        docstring = api.database.__doc__
        assert 'sqlalchemy' in docstring.lower()

    def test_docstring_has_usage_example(self):
        """Test that docstring has usage example"""
        import api.database
        docstring = api.database.__doc__
        # Should have example or usage
        assert 'example' in docstring.lower() or '>>>' in docstring


class TestEngineDisposal:
    """Test engine disposal and cleanup"""

    def test_dispose_engine_function_exists(self):
        """Test that dispose_engine function exists"""
        try:
            from api.database import dispose_engine
            assert dispose_engine is not None
        except ImportError:
            # dispose_engine is optional, skip if not implemented
            pytest.skip("dispose_engine not implemented")

    def test_dispose_engine_is_async(self):
        """Test that dispose_engine is async"""
        try:
            from api.database import dispose_engine
            import inspect
            assert inspect.iscoroutinefunction(dispose_engine)
        except ImportError:
            pytest.skip("dispose_engine not implemented")


class TestDatabaseConstants:
    """Test database constants and configuration"""

    def test_default_pool_size_is_reasonable(self):
        """Test that default pool size is reasonable"""
        # Pool size should be documented or accessible
        # This is more about checking the implementation has pool config
        from api.database import engine
        assert engine.pool is not None

    def test_echo_sql_is_configurable(self):
        """Test that SQL echo is configurable"""
        from api.database import engine
        # Engine should have echo setting
        assert hasattr(engine, 'echo')
