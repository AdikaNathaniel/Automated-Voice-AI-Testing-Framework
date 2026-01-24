"""
User SQLAlchemy model for authentication and user management

This module defines the User model which handles user authentication,
authorization, and profile information for the voice AI testing framework.

The User model includes:
    - Authentication: Email/username and password-based authentication
    - Authorization: Role-based access control
    - Profile: User information and preferences
    - Audit: Login tracking and timestamps

Example:
    >>> from models.user import User
    >>>
    >>> # Create new user
    >>> user = User(
    ...     email="admin@example.com",
    ...     username="admin",
    ...     full_name="Admin User",
    ...     role="admin"
    ... )
    >>> user.set_password("secure_password")
    >>>
    >>> # Verify password
    >>> if user.verify_password("secure_password"):
    ...     print("Authentication successful")
    >>>
    >>> # Check user status
    >>> if user.is_active:
    ...     print("User account is active")
"""


from sqlalchemy import Column, String, Boolean, DateTime, JSON
from sqlalchemy.dialects import postgresql
import bcrypt

from models.base import Base, BaseModel, GUID

# Ensure relationship targets are registered with SQLAlchemy
import models.validation_queue  # noqa: F401
import models.human_validation  # noqa: F401
import models.validator_performance  # noqa: F401
import models.test_suite  # noqa: F401


class User(Base, BaseModel):
    """
    User model for authentication and authorization.

    Represents a user in the system with authentication credentials,
    role-based permissions, and profile information.

    Attributes:
        id (UUID): Unique identifier (inherited from BaseModel)
        email (str): User's email address, unique and required for login
        username (str): User's username, unique and required for display
        full_name (str, optional): User's full legal name
        password_hash (str, optional): Hashed password using bcrypt
        role (str, optional): User's role for access control (admin, user, etc)
        is_active (bool): Whether user account is active, defaults to True
        language_proficiencies (List[str], optional): Language codes user speaks
        last_login_at (datetime, optional): Timestamp of last successful login
        created_at (datetime): Account creation timestamp (inherited)
        updated_at (datetime): Last account update timestamp (inherited)

    Example:
        >>> user = User(
        ...     email="john@example.com",
        ...     username="john_doe",
        ...     full_name="John Doe",
        ...     role="user",
        ...     language_proficiencies=["en", "es"]
        ... )
        >>> user.set_password("my_secure_password")
        >>> print(user.verify_password("my_secure_password"))
        True

    Note:
        - Passwords are never stored in plain text
        - Password hashing uses bcrypt with automatic salt
        - Email and username must be unique across all users
        - Inactive users (is_active=False) should not be able to login
    """

    __tablename__ = 'users'

    tenant_id = Column(
        GUID(),
        nullable=True,
        index=True,
        comment="Tenant identifier for multi-tenant scoping"
    )

    # Authentication fields
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="User's email address for authentication"
    )

    username = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="User's username for display and authentication"
    )

    password_hash = Column(
        String(255),
        nullable=True,
        comment="Bcrypt hashed password"
    )

    # Profile fields
    full_name = Column(
        String(255),
        nullable=True,
        comment="User's full legal name"
    )

    role = Column(
        String(50),
        nullable=True,
        comment="User's role for authorization (admin, user, etc)"
    )

    # Status fields
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether user account is active"
    )

    # Organization fields
    is_organization_owner = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether this user represents an organization (their id becomes tenant_id for members)"
    )

    organization_name = Column(
        String(255),
        nullable=True,
        comment="Organization name (only set if is_organization_owner=True)"
    )

    organization_settings = Column(
        postgresql.JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        comment="Organization-specific settings (billing, limits, features, etc.)"
    )

    # Additional profile fields
    language_proficiencies = Column(
        postgresql.ARRAY(String(10)).with_variant(JSON(), "sqlite"),
        nullable=True,
        comment="Array of language codes user is proficient in"
    )

    last_login_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp of last successful login"
    )

    # Relationships
    # Note: These relationships commented out due to stub table compatibility issues
    # claimed_validations = relationship(
    #     "ValidationQueue",
    #     foreign_keys="ValidationQueue.claimed_by",
    #     primaryjoin="User.id == remote(ValidationQueue.claimed_by)",
    #     viewonly=True
    # )
    # validations_performed = relationship(
    #     "HumanValidation",
    #     foreign_keys="HumanValidation.validator_id",
    #     primaryjoin="User.id == remote(HumanValidation.validator_id)",
    #     viewonly=True
    # )
    # performance_records = relationship(
    #     "ValidatorPerformance",
    #     foreign_keys="ValidatorPerformance.validator_id",
    #     primaryjoin="User.id == remote(ValidatorPerformance.validator_id)",
    #     viewonly=True
    # )

    # Relationships
    # test_suites = relationship(
    #     'TestSuite',
    #     foreign_keys='TestSuite.created_by',
    #     primaryjoin="User.id == remote(TestSuite.created_by)",
    #     viewonly=True,
    #     lazy='select'
    # )

    def set_password(self, password: str) -> None:
        """
        Hash and set the user's password.

        Uses bcrypt to securely hash the password with automatic salt generation.
        The hashed password is stored in password_hash field.

        Args:
            password: Plain text password to hash and store

        Example:
            >>> user = User(email="test@example.com", username="test")
            >>> user.set_password("my_password")
            >>> # Password is now hashed and stored in user.password_hash
            >>> print(len(user.password_hash))  # Bcrypt hashes are 60 chars
            60

        Note:
            - Password is never stored in plain text
            - Each call generates a new salt, so same password produces different hashes
            - Bcrypt is intentionally slow to prevent brute force attacks
        """
        # Convert password to bytes and hash with bcrypt
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        # Store as string
        self.password_hash = hashed.decode('utf-8')

    def verify_password(self, password: str) -> bool:
        """
        Verify a password against the stored hash.

        Args:
            password: Plain text password to verify

        Returns:
            bool: True if password matches, False otherwise

        Example:
            >>> user = User(email="test@example.com", username="test")
            >>> user.set_password("correct_password")
            >>> print(user.verify_password("correct_password"))
            True
            >>> print(user.verify_password("wrong_password"))
            False

        Note:
            - Comparison is timing-attack safe
            - Returns False if password_hash is None
        """
        if not self.password_hash:
            return False
        # Convert both to bytes for comparison
        password_bytes = password.encode('utf-8')
        hash_bytes = self.password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)

    @property
    def is_super_admin(self) -> bool:
        """Check if user has super_admin role."""
        return self.role == "super_admin"

    @property
    def effective_tenant_id(self):
        """Get effective tenant_id for this user.

        Returns:
            - tenant_id if user belongs to an organization
            - user's own id if they are an individual user
        """
        return self.tenant_id if self.tenant_id else self.id

    def __repr__(self) -> str:
        """
        String representation of User instance.

        Returns:
            String with username and active status

        Example:
            >>> user = User(email="test@example.com", username="john_doe")
            >>> print(user)
            <User(username='john_doe', active=True)>
        """
        if self.is_organization_owner:
            return f"<User(org='{self.organization_name}', active={self.is_active})>"
        return f"<User(username='{self.username}', active={self.is_active})>"
