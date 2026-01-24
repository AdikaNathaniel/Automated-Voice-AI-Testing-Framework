"""
SQLAlchemy Base and BaseModel for common database model functionality

This module provides:
- Base: Declarative base for all SQLAlchemy models
- BaseModel: Mixin class with common fields (id, created_at, updated_at)

All database models should inherit from both Base and BaseModel to get:
- UUID primary key with automatic generation
- Automatic timestamp tracking for creation and updates
- Consistent field naming and types across all models

Example:
    >>> from models.base import Base, BaseModel
    >>> from sqlalchemy import Column, String
    >>>
    >>> class User(Base, BaseModel):
    ...     __tablename__ = 'users'
    ...     email = Column(String(255), unique=True, nullable=False)
    ...     username = Column(String(100), unique=True, nullable=False)
"""

from typing import Any
import uuid

from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import declarative_base
from sqlalchemy.types import TypeDecorator, CHAR


class GUID(TypeDecorator):
    """
    Platform-independent GUID type.

    Uses PostgreSQL's UUID type when available, otherwise uses CHAR(32)
    storing as hex strings.

    This allows the same models to work with both PostgreSQL (production)
    and SQLite (testing).
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PostgresUUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            else:
                return str(uuid.UUID(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if isinstance(value, uuid.UUID):
                return value
            else:
                return uuid.UUID(value)


# Alias for backward compatibility
UUID = GUID


# Create declarative base for all models
Base = declarative_base()


class BaseModel:
    """
    Base model class with common fields for all database models.

    Provides:
        - id: UUID primary key with automatic generation
        - created_at: Timestamp of record creation (set by database)
        - updated_at: Timestamp of last update (updated by database on change)

    This is a mixin class and should be used alongside Base:

    Example:
        >>> class MyModel(Base, BaseModel):
        ...     __tablename__ = 'my_table'
        ...     name = Column(String(100))

    Note:
        - All timestamps use database server time (func.now()) for consistency
        - UUID v4 is generated automatically at instantiation using uuid.uuid4()
        - updated_at is only set on UPDATE operations, not on INSERT
        - Do not define __tablename__ in BaseModel itself
    """

    id = Column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the record"
    )

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize the model instance.

        Generates UUID for id if not provided in kwargs.

        Args:
            **kwargs: Column values to set on the instance

        Example:
            >>> user = User(email="test@example.com")
            >>> print(user.id)  # UUID is already generated
        """
        # Call parent init first
        super().__init__(**kwargs)

        # Generate UUID if not set (after parent init)
        if self.id is None:
            self.id = uuid.uuid4()

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when the record was created"
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp when the record was last updated"
    )

    def __repr__(self) -> str:
        """
        String representation of the model instance.

        Returns:
            String with class name and id

        Example:
            >>> user = User(email="test@example.com")
            >>> print(user)
            <User(id=550e8400-e29b-41d4-a716-446655440000)>
        """
        return f"<{self.__class__.__name__}(id={self.id})>"

    def to_dict(self) -> dict[str, Any]:
        """
        Convert model instance to dictionary.

        Returns:
            Dictionary with all column values

        Example:
            >>> user = User(email="test@example.com")
            >>> user.to_dict()
            {'id': UUID('...'), 'email': 'test@example.com', ...}

        Note:
            - Includes all columns defined in the model
            - UUID and datetime objects are not serialized to JSON
            - For JSON serialization, convert UUID to str and datetime to ISO format
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
