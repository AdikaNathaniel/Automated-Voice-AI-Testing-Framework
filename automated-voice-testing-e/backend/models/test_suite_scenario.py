"""
TestSuiteScenario association model for many-to-many relationship.

This module defines the association table between TestSuite and ScenarioScript,
allowing scenarios to be grouped into test suites for batch execution.

Example:
    >>> from models.test_suite_scenario import TestSuiteScenario
    >>>
    >>> # Add a scenario to a suite
    >>> association = TestSuiteScenario(
    ...     suite_id=suite.id,
    ...     scenario_id=scenario.id,
    ...     order=1
    ... )
"""

from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from models.base import Base, BaseModel, GUID


class TestSuiteScenario(Base, BaseModel):
    """
    TestSuiteScenario association model for suite-scenario relationships.

    Represents the many-to-many relationship between TestSuite and ScenarioScript,
    with an optional order field for controlling execution sequence.

    Attributes:
        id (UUID): Unique identifier (inherited from BaseModel)
        suite_id (UUID): Foreign key to test suite
        scenario_id (UUID): Foreign key to scenario script
        order (int): Order of scenario in the suite (for execution sequence)
        suite (TestSuite): Relationship to test suite
        scenario (ScenarioScript): Relationship to scenario script
        created_at (datetime): Creation timestamp (inherited)
        updated_at (datetime): Last update timestamp (inherited)

    Example:
        >>> association = TestSuiteScenario(
        ...     suite_id=suite.id,
        ...     scenario_id=scenario.id,
        ...     order=1
        ... )
    """

    __tablename__ = 'test_suite_scenarios'

    __table_args__ = (
        UniqueConstraint('suite_id', 'scenario_id', name='uq_suite_scenario'),
    )

    suite_id = Column(
        GUID(),
        ForeignKey('test_suites.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Test suite this scenario belongs to"
    )

    scenario_id = Column(
        GUID(),
        ForeignKey('scenario_scripts.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Scenario script in this suite"
    )

    order = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Order of scenario in suite for execution sequence"
    )

    # Relationships
    suite = relationship(
        'TestSuite',
        foreign_keys=[suite_id],
        back_populates='suite_scenarios',
        lazy='select'
    )

    scenario = relationship(
        'ScenarioScript',
        foreign_keys=[scenario_id],
        back_populates='suite_associations',
        lazy='select'
    )

    def __repr__(self) -> str:
        """String representation of TestSuiteScenario."""
        return f"<TestSuiteScenario(suite_id='{self.suite_id}', scenario_id='{self.scenario_id}', order={self.order})>"
