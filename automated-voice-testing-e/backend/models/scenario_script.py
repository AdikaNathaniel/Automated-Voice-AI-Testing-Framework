"""
ScenarioScript and ScenarioStep SQLAlchemy models for scripted test scenarios.

This module defines models for authoring scripted test scenarios with:
- Multi-step conversation flows
- ExpectedOutcome-based validation (defined separately)
- Version control support

Note: Expected responses are now defined at the ExpectedOutcome level,
not at the step level. Use ExpectedOutcome to define validation criteria.

Example:
    >>> from models.scenario_script import ScenarioScript, ScenarioStep
    >>>
    >>> # Create a navigation scenario
    >>> script = ScenarioScript(
    ...     name="Navigation to Coffee Shop",
    ...     description="Test voice navigation to nearby coffee shop",
    ...     version="1.0.0"
    ... )
    >>>
    >>> # Add steps (validation defined via ExpectedOutcome)
    >>> step1 = ScenarioStep(
    ...     script_id=script.id,
    ...     step_order=1,
    ...     user_utterance="Find me a coffee shop"
    ... )
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Column, String, Boolean, Text, Integer, ForeignKey, DateTime, JSON
from sqlalchemy.dialects import postgresql

from sqlalchemy.orm import relationship

from models.base import Base, BaseModel, GUID

if TYPE_CHECKING:
    pass


class ScenarioScript(Base, BaseModel):
    """
    ScenarioScript model for managing scripted test scenarios.

    Represents a complete test scenario that can contain multiple steps,
    with support for versioning, multi-tenancy, and metadata.

    Attributes:
        id (UUID): Unique identifier (inherited from BaseModel)
        tenant_id (UUID, optional): Tenant identifier for multi-tenancy
        name (str): Scenario name, required
        description (str, optional): Detailed description
        version (str, optional): Version string (e.g., "1.0.0")
        is_active (bool): Whether scenario is active, defaults to True
        script_metadata (dict, optional): Additional metadata as JSONB
        created_by (UUID, optional): User who created the scenario
        steps (List[ScenarioStep]): Relationship to scenario steps
        creator (User): Relationship to creating user
        created_at (datetime): Creation timestamp (inherited)
        updated_at (datetime): Last update timestamp (inherited)

    Example:
        >>> script = ScenarioScript(
        ...     name="Weather Query Scenario",
        ...     description="Test weather-related voice commands",
        ...     version="1.0.0",
        ...     script_metadata={"language": "en-US", "domain": "weather"}
        ... )
    """

    __tablename__ = 'scenario_scripts'

    tenant_id = Column(
        GUID(),
        nullable=True,
        index=True,
        comment="Tenant identifier for multi-tenant scoping"
    )

    name = Column(
        String(255),
        nullable=False,
        comment="Scenario script name"
    )

    description = Column(
        Text,
        nullable=True,
        comment="Detailed description of the scenario"
    )

    version = Column(
        String(50),
        nullable=True,
        comment="Version string (e.g., 1.0.0)"
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether the scenario is active"
    )

    script_metadata = Column(
        postgresql.JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        comment="Additional metadata (language, domain, tags, etc.)"
    )

    created_by = Column(
        GUID(),
        ForeignKey('users.id'),
        nullable=True,
        index=True,
        comment="User who created this scenario"
    )

    # Ownership and approval workflow fields
    owner_id = Column(
        GUID(),
        ForeignKey('users.id'),
        nullable=True,
        index=True,
        comment="User who owns/is responsible for this scenario"
    )

    approval_status = Column(
        String(50),
        nullable=False,
        default='draft',
        index=True,
        comment="Approval status: draft, pending_review, approved, rejected"
    )

    reviewed_by = Column(
        GUID(),
        ForeignKey('users.id'),
        nullable=True,
        index=True,
        comment="User who reviewed this scenario"
    )

    reviewed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when scenario was reviewed"
    )

    review_notes = Column(
        Text,
        nullable=True,
        comment="Reviewer feedback or notes"
    )

    validation_mode = Column(
        String(50),
        nullable=False,
        default='hybrid',
        index=True,
        comment="Validation mode: houndify, llm_ensemble, or hybrid"
    )

    # Relationships
    steps = relationship(
        'ScenarioStep',
        back_populates='script',
        cascade='all, delete-orphan',
        order_by='ScenarioStep.step_order',
        lazy='select'
    )

    creator = relationship(
        'User',
        foreign_keys=[created_by],
        lazy='select'
    )

    owner = relationship(
        'User',
        foreign_keys=[owner_id],
        lazy='select'
    )

    reviewer = relationship(
        'User',
        foreign_keys=[reviewed_by],
        lazy='select'
    )

    # Relationship to test suites (via junction table)
    suite_associations = relationship(
        'TestSuiteScenario',
        back_populates='scenario',
        cascade='all, delete-orphan',
        lazy='select'
    )

    # =========================================================================
    # Approval Workflow Properties
    # =========================================================================

    @property
    def is_approved(self) -> bool:
        """Check if scenario is approved."""
        return self.approval_status == 'approved'

    @property
    def is_pending_review(self) -> bool:
        """Check if scenario is pending review."""
        return self.approval_status == 'pending_review'

    # =========================================================================
    # Approval Workflow Methods
    # =========================================================================

    def submit_for_review(self) -> None:
        """
        Submit scenario for review.

        Changes approval_status to 'pending_review'.

        Example:
            >>> script.submit_for_review()
            >>> script.is_pending_review
            True
        """
        self.approval_status = 'pending_review'

    def approve(self, reviewer_id: UUID, notes: Optional[str] = None) -> None:
        """
        Approve the scenario.

        Args:
            reviewer_id: UUID of the user approving
            notes: Optional approval notes

        Example:
            >>> script.approve(reviewer_id=user.id, notes="Looks good!")
            >>> script.is_approved
            True
        """
        self.approval_status = 'approved'
        self.reviewed_by = reviewer_id
        self.reviewed_at = datetime.utcnow()
        if notes:
            self.review_notes = notes

    def reject(self, reviewer_id: UUID, notes: str) -> None:
        """
        Reject the scenario.

        Args:
            reviewer_id: UUID of the user rejecting
            notes: Reason for rejection (required)

        Example:
            >>> script.reject(reviewer_id=user.id, notes="Missing edge cases")
            >>> script.approval_status
            'rejected'
        """
        self.approval_status = 'rejected'
        self.reviewed_by = reviewer_id
        self.reviewed_at = datetime.utcnow()
        self.review_notes = notes

    def __repr__(self) -> str:
        """String representation of ScenarioScript."""
        return f"<ScenarioScript(name='{self.name}', version='{self.version}')>"

    def add_step(
        self,
        step_order: int,
        user_utterance: str,
        step_metadata: Optional[Dict[str, Any]] = None,
        follow_up_action: Optional[str] = None
    ) -> 'ScenarioStep':
        """
        Add a step to this scenario.

        Note: Expected responses are now defined at the ExpectedOutcome level,
        not at the step level. Create an ExpectedOutcome and link it to the step.

        Args:
            step_order: Order of the step in sequence
            user_utterance: What the user says
            step_metadata: Optional step-specific metadata (language_variants, etc.)
            follow_up_action: Optional follow-up action (await_confirmation, retry, etc.)

        Returns:
            ScenarioStep: The created step

        Example:
            >>> script.add_step(
            ...     step_order=1,
            ...     user_utterance="What's the weather?",
            ...     step_metadata={"language": "en-US"}
            ... )
        """
        step = ScenarioStep(
            script_id=self.id,
            step_order=step_order,
            user_utterance=user_utterance,
            step_metadata=step_metadata,
            follow_up_action=follow_up_action
        )
        self.steps.append(step)
        return step

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert scenario to dictionary for export.

        Returns:
            Dictionary representation including steps
        """
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'is_active': self.is_active,
            'metadata': self.script_metadata,
            'steps': [step.to_dict() for step in self.steps]
        }


class ScenarioStep(Base, BaseModel):
    """
    ScenarioStep model for individual steps within a scenario.

    Represents a single conversation turn with user input. Expected responses
    and validation criteria are defined at the ExpectedOutcome level.

    Attributes:
        id (UUID): Unique identifier (inherited from BaseModel)
        script_id (UUID): Foreign key to parent scenario
        step_order (int): Order in the scenario sequence
        user_utterance (str): What the user says
        step_metadata (dict, optional): Additional step-specific metadata
        follow_up_action (str, optional): Follow-up action after step
        script (ScenarioScript): Relationship to parent scenario
        expected_outcomes (List[ExpectedOutcome]): Validation criteria for this step
        created_at (datetime): Creation timestamp (inherited)
        updated_at (datetime): Last update timestamp (inherited)

    Example:
        >>> step = ScenarioStep(
        ...     script_id=script.id,
        ...     step_order=1,
        ...     user_utterance="Navigate to work",
        ...     step_metadata={"language": "en-US"}
        ... )
    """

    __tablename__ = 'scenario_steps'

    script_id = Column(
        GUID(),
        ForeignKey('scenario_scripts.id'),
        nullable=False,
        index=True,
        comment="Parent scenario script"
    )

    step_order = Column(
        Integer,
        nullable=False,
        comment="Order of this step in the scenario"
    )

    user_utterance = Column(
        Text,
        nullable=False,
        comment="User input/utterance for this step"
    )

    step_metadata = Column(
        postgresql.JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        comment="Additional step-specific metadata"
    )

    follow_up_action = Column(
        String(100),
        nullable=True,
        comment="Follow-up action to trigger after step (await_confirmation, retry, etc.)"
    )

    # Relationships
    script = relationship(
        'ScenarioScript',
        back_populates='steps',
        foreign_keys=[script_id],
        primaryjoin="ScenarioStep.script_id == ScenarioScript.id"
    )
    expected_outcomes = relationship(
        'ExpectedOutcome',
        back_populates='scenario_step',
        lazy='selectin'
    )

    def __repr__(self) -> str:
        """String representation of ScenarioStep."""
        return f"<ScenarioStep(order={self.step_order}, utterance='{self.user_utterance[:30]}...')>"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert step to dictionary for export.

        Returns:
            Dictionary representation of the step
        """
        return {
            'id': str(self.id),
            'step_order': self.step_order,
            'user_utterance': self.user_utterance,
            'metadata': self.step_metadata
        }

