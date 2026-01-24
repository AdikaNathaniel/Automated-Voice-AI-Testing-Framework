"""
SQLAlchemy async database connection manager

This module provides async database connectivity using SQLAlchemy 2.0
with asyncpg driver for PostgreSQL. It configures connection pooling,
creates async engine and session factory for database operations.

Components:
    - engine: Async SQLAlchemy engine with connection pooling
    - SessionLocal: Async session factory for creating database sessions
    - get_db(): FastAPI dependency for database session management

Configuration is loaded from api.config.Settings which reads from
environment variables. The DATABASE_URL should be in format:
    postgresql://user:password@host:port/dbname

The URL is automatically converted to use the asyncpg driver:
    postgresql+asyncpg://user:password@host:port/dbname

Connection Pooling (configurable via Settings):
    - pool_size: settings.DB_POOL_SIZE (connections kept open)
    - max_overflow: settings.DB_MAX_OVERFLOW (connections beyond pool_size)
    - pool_timeout: settings.DB_POOL_TIMEOUT (wait time for connection)
    - pool_recycle: settings.DB_POOL_RECYCLE (recycle connections after interval)
    - pool_pre_ping: True (verify connections before use)

Example:
    >>> from api.database import get_db
    >>> from fastapi import Depends
    >>>
    >>> @app.get("/users")
    >>> async def list_users(db: AsyncSession = Depends(get_db)):
    ...     result = await db.execute(select(User))
    ...     users = result.scalars().all()
    ...     return users

Usage with async context manager:
    >>> from api.database import SessionLocal
    >>>
    >>> async with SessionLocal() as session:
    ...     result = await session.execute(select(User))
    ...     users = result.scalars().all()

Note:
    - All database operations must be async
    - Sessions are automatically closed after use with get_db()
    - Transactions are automatically committed unless an exception occurs
    - Connection pool automatically handles reconnection on errors
"""

from typing import AsyncGenerator, Optional
import logging

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)

from api.config import get_settings
from sqlalchemy.orm import Session


# Configure logging
logger = logging.getLogger(__name__)

# Get application settings
settings = get_settings()

# Helper to ensure asyncpg driver usage
def _ensure_asyncpg(url: str) -> str:
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if not url.startswith("postgresql+asyncpg://"):
        logger.warning(
            "DATABASE_URL does not use asyncpg driver: %s. Attempting to use as-is, but may cause issues.",
            url,
        )
    return url


def _get_engine_kwargs(database_url: str) -> dict:
    """
    Build engine kwargs based on database type.

    SQLite doesn't support pool_size, max_overflow, pool_timeout parameters.
    PostgreSQL does support these for connection pooling.
    """
    kwargs = {
        "echo": settings.DEBUG,
        "future": True,
        "pool_pre_ping": True,
    }

    # Only add pool parameters for PostgreSQL (not SQLite)
    if not database_url.startswith("sqlite"):
        kwargs["pool_size"] = settings.DB_POOL_SIZE
        kwargs["max_overflow"] = settings.DB_MAX_OVERFLOW
        kwargs["pool_timeout"] = settings.DB_POOL_TIMEOUT
        kwargs["pool_recycle"] = settings.DB_POOL_RECYCLE

    return kwargs


primary_database_url = _ensure_asyncpg(settings.DATABASE_URL)

# Create async engine with connection pooling for primary database
primary_engine: AsyncEngine = create_async_engine(
    primary_database_url,
    **_get_engine_kwargs(primary_database_url),
)

# Optional read replica engine
replica_engine: Optional[AsyncEngine] = None
if settings.READ_REPLICA_URL:
    replica_database_url = _ensure_asyncpg(settings.READ_REPLICA_URL)
    replica_engine = create_async_engine(
        replica_database_url,
        **_get_engine_kwargs(replica_database_url),
    )
    logger.info("Created async read replica engine")

# Alias maintained for backwards compatibility
engine: AsyncEngine = primary_engine

# Log engine creation
logger.info(
    "Created async database engine with pool_size=%s max_overflow=%s timeout=%s recycle=%s",
    settings.DB_POOL_SIZE,
    settings.DB_MAX_OVERFLOW,
    settings.DB_POOL_TIMEOUT,
    settings.DB_POOL_RECYCLE,
)

# Prepared sync engines for routing session
_primary_sync_engine = primary_engine.sync_engine
_replica_sync_engine = replica_engine.sync_engine if replica_engine else None


class RoutingSession(Session):
    """
    Custom SQLAlchemy session that routes read operations to replica engine.
    """

    def get_bind(self, mapper=None, clause=None, **kwargs):  # type: ignore[override]
        use_replica = False

        if _replica_sync_engine is None:
            return _primary_sync_engine

        force_primary = kwargs.get("force_primary") or self.info.get("use_primary")
        if force_primary:
            return _primary_sync_engine

        if self._flushing or self.in_transaction():
            return _primary_sync_engine

        if clause is not None:
            visit_name = getattr(clause, "__visit_name__", None)
            use_replica = visit_name == "select"
        elif mapper is not None:
            # mapper present implies a load operation such as session.get()
            use_replica = True

        return _replica_sync_engine if use_replica else _primary_sync_engine


# Create async session factory
SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=primary_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit
    autocommit=False,  # Don't autocommit (use explicit transactions)
    autoflush=False,  # Don't autoflush (explicit session.flush())
    sync_session_class=RoutingSession,
)

logger.info("Created async session factory")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database session management.

    Yields an async database session and ensures it's properly closed
    after the request completes. Automatically handles transaction
    rollback on exceptions.

    Yields:
        AsyncSession: Database session for executing queries

    Example:
        >>> from fastapi import Depends, APIRouter
        >>> from api.database import get_db
        >>> from sqlalchemy import select
        >>> from models.user import User
        >>>
        >>> router = APIRouter()
        >>>
        >>> @router.get("/users")
        >>> async def get_users(db: AsyncSession = Depends(get_db)):
        ...     result = await db.execute(select(User))
        ...     users = result.scalars().all()
        ...     return users

    Note:
        - Session is automatically closed after request
        - Transactions are rolled back on exceptions
        - Use with FastAPI's Depends() for automatic injection
        - Sessions are not thread-safe, use one per request
    """
    async with SessionLocal() as session:
        try:
            yield session
            # Session will be closed automatically by context manager
        except Exception as e:
            # Rollback on error
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            # Ensure session is closed
            await session.close()


def get_async_session() -> AsyncSession:
    """
    Get an async database session for use in service layer.

    Returns an async context manager that can be used with `async with`.

    Returns:
        AsyncSession: Async context manager for database session

    Example:
        >>> from api.database import get_async_session
        >>>
        >>> async with get_async_session() as session:
        ...     result = await session.execute(select(User))
        ...     users = result.scalars().all()

    Note:
        - Session must be used with `async with` statement
        - Session is automatically closed after context exits
        - Transactions are automatically committed unless exception occurs
    """
    return SessionLocal()


async def dispose_engine() -> None:
    """
    Dispose of the database engine and close all connections.

    This should be called during application shutdown to cleanly
    close all database connections in the pool.

    Example:
        >>> @app.on_event("shutdown")
        >>> async def shutdown():
        ...     await dispose_engine()

    Note:
        - Waits for all connections to be returned to pool
        - Closes all connections gracefully
        - Should be called only during shutdown
    """
    await primary_engine.dispose()
    if replica_engine is not None:
        await replica_engine.dispose()
    logger.info("Database engines disposed")
