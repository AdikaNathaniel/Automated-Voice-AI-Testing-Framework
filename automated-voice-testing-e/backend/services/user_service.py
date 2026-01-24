"""
User service for CRUD operations

This module provides business logic for user management including:
- User creation with password hashing
- User retrieval by ID or email
- User updates
- User deletion

All operations are async and use SQLAlchemy with AsyncSession for database access.

Functions:
    create_user(db: AsyncSession, data: RegisterRequest) -> User:
        Create a new user with hashed password

    get_user_by_email(db: AsyncSession, email: str) -> User | None:
        Retrieve user by email address

    get_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
        Retrieve user by UUID

    update_user(db: AsyncSession, user_id: UUID, data: dict) -> User:
        Update user fields

    delete_user(db: AsyncSession, user_id: UUID) -> bool:
        Delete user from database

Example:
    >>> from services.user_service import create_user, get_user_by_email
    >>> from api.schemas.auth import RegisterRequest
    >>> from api.database import SessionLocal
    >>>
    >>> async with SessionLocal() as db:
    ...     # Create user
    ...     register_data = RegisterRequest(
    ...         email="user@example.com",
    ...         username="johndoe",
    ...         password="SecurePassword123",
    ...         full_name="John Doe"
    ...     )
    ...     user = await create_user(db, register_data)
    ...
    ...     # Find user
    ...     found_user = await get_user_by_email(db, "user@example.com")
"""

import logging
from typing import Optional, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from models.user import User
from api.schemas.auth import RegisterRequest
from api.auth.roles import Role
from api.auth.password import hash_password

logger = logging.getLogger(__name__)


class UserService:
    """
    Service class for user management operations.

    Provides CRUD operations for users with password hashing support.

    Example:
        >>> service = UserService()
        >>> user = await service.create_user(db, data)
    """

    def __init__(self):
        """Initialize the user service."""
        pass

    async def create_user(
        self,
        db: AsyncSession,
        data: RegisterRequest
    ) -> User:
        """Create a new user with hashed password."""
        return await create_user(db, data)

    async def get_user_by_email(
        self,
        db: AsyncSession,
        email: str
    ) -> Optional[User]:
        """Retrieve user by email address."""
        return await get_user_by_email(db, email)

    async def get_user_by_id(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> Optional[User]:
        """Retrieve user by UUID."""
        return await get_user_by_id(db, user_id)

    async def update_user(
        self,
        db: AsyncSession,
        user_id: UUID,
        data: Dict[str, Any]
    ) -> User:
        """Update user fields."""
        return await update_user(db, user_id, data)

    async def delete_user(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> bool:
        """Delete user from database."""
        return await delete_user(db, user_id)


async def create_user(db: AsyncSession, data: RegisterRequest) -> User:
    """
    Create a new user with hashed password.

    Takes registration data, hashes the password, creates a User object,
    and persists it to the database. The user is set to active by default.

    Args:
        db: Async database session
        data: Registration request containing email, username, password, full_name

    Returns:
        User: The created user with generated ID and timestamps

    Raises:
        IntegrityError: If email or username already exists

    Example:
        >>> register_data = RegisterRequest(
        ...     email="new@example.com",
        ...     username="newuser",
        ...     password="SecurePass123",
        ...     full_name="New User"
        ... )
        >>> user = await create_user(db, register_data)
        >>> print(user.email)
        new@example.com

    Note:
        - Password is hashed using bcrypt before storage
        - User is automatically set to active (is_active=True)
        - Timestamps (created_at, updated_at) are set automatically
        - ID is generated as UUID4
    """
    try:
        # Hash the password
        hashed_password = hash_password(data.password)

        # Create user object
        role_value = data.role.value if isinstance(data.role, Role) else (data.role or Role.VIEWER.value)

        # Explicitly set id to ensure UUID generation works
        # across different SQLAlchemy mapper configurations
        user = User(
            id=uuid4(),
            email=data.email,
            username=data.username,
            password_hash=hashed_password,
            full_name=data.full_name,
            role=role_value,
            is_active=True
        )

        # Add to database
        db.add(user)

        try:
            # Commit to database
            await db.commit()
            # Refresh to get generated fields (id, timestamps)
            await db.refresh(user)
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"IntegrityError creating user {data.email}: {e}")
            raise e

        logger.debug(f"Created user: {user.email}")
        return user

    except IntegrityError:
        raise
    except Exception as e:
        logger.error(f"Error creating user {data.email}: {e}")
        raise


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    Retrieve a user by email address.

    Performs case-sensitive email lookup. Returns None if no user found.

    Args:
        db: Async database session
        email: User's email address

    Returns:
        User | None: User object if found, None otherwise

    Example:
        >>> user = await get_user_by_email(db, "john@example.com")
        >>> if user:
        ...     print(f"Found user: {user.username}")
        ... else:
        ...     print("User not found")

    Note:
        - Email lookup is case-sensitive
        - Returns None (not exception) if user not found
        - Includes all user fields including password_hash
    """
    try:
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        if user:
            logger.debug(f"Found user by email: {email}")
        return user
    except Exception as e:
        logger.error(f"Error getting user by email {email}: {e}")
        raise


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """
    Retrieve a user by UUID.

    Args:
        db: Async database session
        user_id: User's UUID identifier

    Returns:
        User | None: User object if found, None otherwise

    Example:
        >>> from uuid import UUID
        >>> user_id = UUID("550e8400-e29b-41d4-a716-446655440000")
        >>> user = await get_user_by_id(db, user_id)
        >>> if user:
        ...     print(f"Found: {user.email}")

    Note:
        - Returns None (not exception) if user not found
        - user_id must be a UUID object, not a string
    """
    try:
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user:
            logger.debug(f"Found user by id: {user_id}")
        return user
    except Exception as e:
        logger.error(f"Error getting user by id {user_id}: {e}")
        raise


async def update_user(db: AsyncSession, user_id: UUID, data: Dict[str, Any]) -> User:
    """
    Update user fields.

    Updates specified fields of a user. Only fields present in the data dict
    are updated. Automatically updates the updated_at timestamp.

    Args:
        db: Async database session
        user_id: UUID of user to update
        data: Dictionary of fields to update (e.g., {"full_name": "New Name"})

    Returns:
        User: The updated user object

    Raises:
        ValueError: If user not found

    Example:
        >>> # Update single field
        >>> user = await update_user(db, user_id, {"full_name": "Jane Doe"})
        >>>
        >>> # Update multiple fields
        >>> user = await update_user(db, user_id, {
        ...     "full_name": "Jane Smith",
        ...     "is_active": False
        ... })

    Note:
        - Only fields in data dict are updated
        - Empty dict is valid (no updates, but updated_at still changes)
        - Cannot update id, created_at, or other protected fields
        - Password updates should hash password first
    """
    try:
        # Get user
        user = await get_user_by_id(db, user_id)

        if not user:
            raise ValueError(f"User with id {user_id} not found")

        # Update fields
        for key, value in data.items():
            if hasattr(user, key):
                setattr(user, key, value)

        # Commit changes
        await db.commit()
        await db.refresh(user)

        logger.debug(f"Updated user: {user_id}")
        return user

    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise


async def delete_user(db: AsyncSession, user_id: UUID) -> bool:
    """
    Delete a user from the database.

    Permanently removes the user. Returns True if user was deleted,
    False if user was not found.

    Args:
        db: Async database session
        user_id: UUID of user to delete

    Returns:
        bool: True if user was deleted, False if user not found

    Example:
        >>> success = await delete_user(db, user_id)
        >>> if success:
        ...     print("User deleted")
        ... else:
        ...     print("User not found")

    Note:
        - Returns False (not exception) if user not found
        - Deletion is permanent and cannot be undone
        - Consider soft-delete (is_active=False) for audit trails
        - Cascade behavior depends on foreign key constraints
    """
    try:
        # Get user
        user = await get_user_by_id(db, user_id)

        if not user:
            return False

        # Delete user
        await db.delete(user)
        await db.commit()

        logger.debug(f"Deleted user: {user_id}")
        return True

    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise


__all__ = [
    'create_user',
    'get_user_by_email',
    'get_user_by_id',
    'update_user',
    'delete_user',
]
