"""
TestSuite SQLAlchemy model for test management

This module defines the TestSuite model which represents a collection
of related scenario scripts in the automated testing framework.

The TestSuite model includes:
    - Test suite metadata: Name, description, and category
    - Organization: Category for grouping related test suites
    - Status: Active/inactive flag for managing test suite lifecycle
    - Relationships: Links to scenarios and creator user
    - Audit: Timestamps and creator tracking

Example:
    >>> from models.test_suite import TestSuite
    >>>
    >>> # Create new test suite
    >>> suite = TestSuite(
    ...     name="Login Flow Tests",
    ...     description="Test suite for user authentication flows",
    ...     category="Authentication",
    ...     created_by=user_id
    ... )
    >>>
    >>> # Check suite status
    >>> if suite.is_active:
    ...     print(f"Suite '{suite.name}' is active")
"""

from typing import TYPE_CHECKING

from sqlalchemy import Column, String, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects import postgresql
from sqlalchemy import JSON
from sqlalchemy.orm import relationship

from models.base import Base, BaseModel, GUID

# Avoid circular imports for type hints
if TYPE_CHECKING:
    pass


# Use JSONB for PostgreSQL, JSON for SQLite (testing)
JSONB_TYPE = JSONB().with_variant(JSON(), "sqlite")

class TestSuite(Base, BaseModel):
    """
    TestSuite model for organizing and managing scenario scripts.

    Represents a collection of related scenarios with common characteristics
    such as category, purpose, or testing domain.

    Attributes:
        id (UUID): Unique identifier (inherited from BaseModel)
        name (str): Test suite name, required and unique within scope
        description (str, optional): Detailed description of test suite purpose
        category (str, optional): Category for grouping test suites
        is_active (bool): Whether test suite is active, defaults to True
        language_config (dict, optional): Language execution configuration with mode, languages, and fallback_behavior
        created_by (UUID, optional): Foreign key to user who created the suite
        creator (User): Relationship to the creating user
        suite_scenarios (List): Relationship to scenarios in this suite
        created_at (datetime): Suite creation timestamp (inherited)
        updated_at (datetime): Last suite update timestamp (inherited)

    Example:
        >>> suite = TestSuite(
        ...     name="Voice AI Integration Tests",
        ...     description="Tests for voice AI service integration",
        ...     category="Integration",
        ...     is_active=True
        ... )
        >>> print(suite.name)
        Voice AI Integration Tests

    Note:
        - Test suites can be deactivated rather than deleted for history
        - Category helps organize suites into logical groups
        - created_by tracks ownership for access control
    """

    __tablename__ = 'test_suites'

    tenant_id = Column(
        GUID(),
        nullable=True,
        index=True,
        comment="Tenant identifier for multi-tenant scoping"
    )

    # Test suite fields
    name = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Test suite name"
    )

    description = Column(
        Text,
        nullable=True,
        comment="Test suite description"
    )

    category = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Test suite category for organization"
    )

    # Status field
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether test suite is active"
    )

    # Language configuration for suite execution
    language_config = Column(
        JSONB_TYPE,
        nullable=True,
        comment="Language execution configuration: mode, languages, fallback_behavior"
    )

    # Foreign key to users
    created_by = Column(
        GUID(),
        ForeignKey('users.id'),
        nullable=True,
        index=True,
        comment="User who created this test suite"
    )

    # Relationships
    creator = relationship(
        'User',
        foreign_keys=[created_by],
        primaryjoin="TestSuite.created_by == remote(User.id)",
        viewonly=True,
        lazy='joined'
    )

    suite_runs = relationship(
        'SuiteRun',
        back_populates='test_suite',
        foreign_keys='SuiteRun.suite_id',
        lazy='select'
    )

    # Relationship to scenarios (via junction table)
    suite_scenarios = relationship(
        'TestSuiteScenario',
        back_populates='suite',
        cascade='all, delete-orphan',
        order_by='TestSuiteScenario.order',
        lazy='select'
    )

    # Multi-turn executions from this suite
    multi_turn_executions = relationship(
        'MultiTurnExecution',
        foreign_keys='MultiTurnExecution.suite_id',
        back_populates='suite',
        lazy='select'
    )

    def __repr__(self) -> str:
        """
        String representation of TestSuite instance.

        Returns:
            String with suite name and active status

        Example:
            >>> suite = TestSuite(name="Login Tests")
            >>> print(suite)
            <TestSuite(name='Login Tests', active=True)>
        """
        return f"<TestSuite(name='{self.name}', active={self.is_active})>"

    def validate_name(self) -> bool:
        """
        Validate that test suite name is not empty.

        Returns:
            bool: True if name is valid, False otherwise

        Example:
            >>> suite = TestSuite(name="Valid Name")
            >>> suite.validate_name()
            True
            >>> suite.name = ""
            >>> suite.validate_name()
            False
        """
        return bool(self.name and len(self.name.strip()) > 0)

    def activate(self) -> None:
        """
        Activate the test suite.

        Example:
            >>> suite = TestSuite(name="Test", is_active=False)
            >>> suite.activate()
            >>> suite.is_active
            True
        """
        self.is_active = True

    def deactivate(self) -> None:
        """
        Deactivate the test suite.

        Example:
            >>> suite = TestSuite(name="Test", is_active=True)
            >>> suite.deactivate()
            >>> suite.is_active
            False
        """
        self.is_active = False
