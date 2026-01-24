"""
ExpectedOutcome SQLAlchemy model for defining expected test outcomes

This module defines the ExpectedOutcome model which represents the expected
results and validations for test cases in the automated testing framework.

The ExpectedOutcome model includes:
    - Unique identification: Unique outcome_code for each expected outcome
    - Descriptive information: Name and description
    - JSONB fields: Entities, validation rules, and language variations
    - Helper methods: For managing entities, validation rules, and language variations

Example:
    >>> from models.expected_outcome import ExpectedOutcome
    >>>
    >>> # Create an expected outcome
    >>> outcome = ExpectedOutcome(
    ...     outcome_code="NAVIGATE_HOME",
    ...     name="Navigate to Home",
    ...     description="Successfully navigate to home location",
    ...     entities={"action": "navigate", "destination": "home"},
    ...     validation_rules={"min_confidence": 0.8, "required_entities": ["destination"]}
    ... )
    >>>
    >>> # Update validation rules
    >>> outcome.update_validation_rules({"timeout": 30})
"""

from typing import Optional, Dict, Any, TYPE_CHECKING

from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Integer, Float, JSON, UniqueConstraint
from sqlalchemy.dialects import postgresql

from sqlalchemy.orm import relationship

from models.base import Base, BaseModel, GUID
from models.expected_outcome_helpers import ExpectedOutcomeHelpersMixin

if TYPE_CHECKING:
    pass


class ExpectedOutcome(Base, BaseModel, ExpectedOutcomeHelpersMixin):
    """
    ExpectedOutcome model for defining expected test results and validations.

    Represents the expected outcome of a test case, including entities to be
    extracted, validation rules, and language-specific variations.

    Attributes:
        id (UUID): Unique identifier (inherited from BaseModel)
        outcome_code (str): Unique code identifying this expected outcome, required
        name (str): Human-readable name of the outcome, required
        description (str, optional): Detailed description of the expected outcome
        entities (Dict[str, Any], optional): Expected entities to be extracted (JSONB)
        validation_rules (Dict[str, Any], optional): Validation rules for verifying outcome (JSONB)
        language_variations (Dict[str, Any], optional): Language-specific variations (JSONB)
        created_at (datetime): Creation timestamp (inherited)
        updated_at (datetime): Last update timestamp (inherited)

    Example:
        >>> outcome = ExpectedOutcome(
        ...     outcome_code="PLAY_MUSIC",
        ...     name="Play Music Command",
        ...     description="Successfully play music",
        ...     entities={"action": "play", "media_type": "music"},
        ...     validation_rules={
        ...         "required_entities": ["action", "media_type"],
        ...         "min_confidence": 0.75
        ...     }
        ... )
        >>> outcome.add_entity("artist", "Taylor Swift")
        >>> outcome.update_validation_rules({"timeout": 20})
        >>> print(outcome.entities)
        {'action': 'play', 'media_type': 'music', 'artist': 'Taylor Swift'}

    Note:
        - outcome_code must be unique across all expected outcomes
        - JSONB fields store flexible JSON structures for entities and rules
        - validation_rules can define confidence thresholds, required entities, etc.
        - language_variations stores language-specific expected outcomes
    """

    __tablename__ = 'expected_outcomes'
    __table_args__ = (
        UniqueConstraint('tenant_id', 'outcome_code', name='uq_expected_outcome_tenant_code'),
    )

    tenant_id = Column(
        GUID(),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Tenant (organization or user) that owns this expected outcome"
    )

    # Core identification fields
    outcome_code = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Outcome code (unique per tenant)"
    )

    name = Column(
        String(255),
        nullable=False,
        comment="Human-readable name of the outcome"
    )

    description = Column(
        Text,
        nullable=True,
        comment="Detailed description of the expected outcome"
    )

    # JSONB fields for flexible data structures
    entities = Column(
        postgresql.JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        comment="Expected entities to be extracted (JSON structure)"
    )

    validation_rules = Column(
        postgresql.JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        comment="Validation rules for verifying outcome (JSON structure)"
    )

    language_variations = Column(
        postgresql.JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        comment="Language-specific variations of expected outcomes (JSON structure)"
    )

    # Scenario step reference (for linking to scripted scenarios)
    scenario_step_id = Column(
        GUID(),
        ForeignKey('scenario_steps.id'),
        nullable=True,
        index=True,
        comment="Reference to the scenario step this outcome applies to"
    )

    # Acceptable alternates (list of alternative acceptable responses)
    acceptable_alternates = Column(
        postgresql.JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        comment="List of acceptable alternate responses (JSON array)"
    )

    # Confirmation flags
    confirmation_required = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether confirmation is required before success"
    )

    confirmation_prompt = Column(
        Text,
        nullable=True,
        comment="The expected confirmation prompt"
    )

    allow_partial_success = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether partial success is acceptable"
    )

    # Tolerance settings
    tolerance_settings = Column(
        postgresql.JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        comment="Tolerance settings for validation (semantic similarity, entity matching)"
    )

    # Tolerance band fields for per-step definitions
    tolerance_config = Column(
        postgresql.JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        comment="Complete tolerance configuration for this outcome"
    )

    required_entities = Column(
        postgresql.JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        comment="List of entities that must be present in response"
    )

    forbidden_phrases = Column(
        postgresql.JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        comment="List of phrases that must not appear in response"
    )

    tone_requirement = Column(
        String(100),
        nullable=True,
        comment="Required tone for response (polite, professional, etc.)"
    )

    max_response_length = Column(
        Integer,
        nullable=True,
        comment="Maximum allowed response length in characters"
    )

    # Multi-path support
    next_step_on_success = Column(
        GUID(),
        nullable=True,
        comment="Next step ID on successful validation"
    )

    next_step_on_failure = Column(
        GUID(),
        nullable=True,
        comment="Next step ID on failed validation"
    )

    recovery_path = Column(
        postgresql.JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        comment="Recovery path configuration for failed validations"
    )

    # Scenario metadata
    scenario_metadata = Column(
        postgresql.JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        comment="Additional scenario-specific metadata"
    )

    # Dynamic context for references like 'first one'
    dynamic_context = Column(
        postgresql.JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        comment="Dynamic context for resolving references (e.g., search results)"
    )

    # ========================================================================
    # Houndify-Specific Fields
    # ========================================================================

    expected_command_kind = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Expected Houndify CommandKind (WeatherCommand, MusicCommand, NoResultCommand, etc.)"
    )

    expected_asr_confidence_min = Column(
        Float,
        nullable=True,
        comment="Minimum required ASR confidence score from Houndify (0.0 - 1.0)"
    )

    expected_response_content = Column(
        postgresql.JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        comment="Expected content patterns in SpokenResponse/WrittenResponse from Houndify"
    )

    expected_native_data_schema = Column(
        postgresql.JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        comment="Expected structure and value constraints for Houndify NativeData field"
    )

    conversation_requirements = Column(
        postgresql.JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        comment="Conversation state requirements for multi-turn interactions"
    )

    # Relationship to scenario step
    scenario_step = relationship(
        'ScenarioStep',
        back_populates='expected_outcomes',
        foreign_keys=[scenario_step_id],
        lazy='select'
    )
    validation_results = relationship(
        'ValidationResult',
        back_populates='expected_outcome',
        lazy='selectin'
    )

    def __repr__(self) -> str:
        """
        String representation of ExpectedOutcome instance.

        Returns:
            String with outcome code and name

        Example:
            >>> outcome = ExpectedOutcome(outcome_code="NAVIGATE_HOME", name="Navigate to Home")
            >>> print(outcome)
            <ExpectedOutcome(code='NAVIGATE_HOME', name='Navigate to Home')>
        """
        return f"<ExpectedOutcome(code='{self.outcome_code}', name='{self.name}')>"

    def validate_outcome_code(self) -> bool:
        """
        Validate that outcome_code is not empty.

        Returns:
            bool: True if outcome code is valid, False otherwise

        Example:
            >>> outcome = ExpectedOutcome(outcome_code="VALID_CODE")
            >>> outcome.validate_outcome_code()
            True
            >>> outcome.outcome_code = ""
            >>> outcome.validate_outcome_code()
            False
        """
        return bool(self.outcome_code and len(self.outcome_code.strip()) > 0)

    def add_entity(self, key: str, value: Any) -> None:
        """
        Add or update an entity in the entities dictionary.

        Args:
            key: Entity key/name
            value: Entity value

        Example:
            >>> outcome = ExpectedOutcome(
            ...     outcome_code="PLAY_MUSIC",
            ...     entities={"action": "play"}
            ... )
            >>> outcome.add_entity("media_type", "music")
            >>> outcome.entities
            {'action': 'play', 'media_type': 'music'}
        """
        if self.entities is None:
            self.entities = {}
        self.entities[key] = value

    def remove_entity(self, key: str) -> None:
        """
        Remove an entity from the entities dictionary.

        Args:
            key: Entity key to remove

        Example:
            >>> outcome = ExpectedOutcome(
            ...     outcome_code="PLAY_MUSIC",
            ...     entities={"action": "play", "media_type": "music"}
            ... )
            >>> outcome.remove_entity("media_type")
            >>> outcome.entities
            {'action': 'play'}
        """
        if self.entities and key in self.entities:
            del self.entities[key]

    def update_entities(self, entities: Dict[str, Any]) -> None:
        """
        Update multiple entities at once.

        Args:
            entities: Dictionary of entities to add/update

        Example:
            >>> outcome = ExpectedOutcome(outcome_code="PLAY_MUSIC")
            >>> outcome.update_entities({"action": "play", "media_type": "music"})
            >>> outcome.entities
            {'action': 'play', 'media_type': 'music'}
        """
        if self.entities is None:
            self.entities = {}
        self.entities.update(entities)

    def clear_entities(self) -> None:
        """
        Clear all entities.

        Example:
            >>> outcome = ExpectedOutcome(
            ...     outcome_code="PLAY_MUSIC",
            ...     entities={"action": "play"}
            ... )
            >>> outcome.clear_entities()
            >>> outcome.entities
            {}
        """
        self.entities = {}

    def add_validation_rule(self, key: str, value: Any) -> None:
        """
        Add or update a validation rule.

        Args:
            key: Rule key/name
            value: Rule value

        Example:
            >>> outcome = ExpectedOutcome(outcome_code="PLAY_MUSIC")
            >>> outcome.add_validation_rule("min_confidence", 0.8)
            >>> outcome.validation_rules
            {'min_confidence': 0.8}
        """
        if self.validation_rules is None:
            self.validation_rules = {}
        self.validation_rules[key] = value

    def remove_validation_rule(self, key: str) -> None:
        """
        Remove a validation rule.

        Args:
            key: Rule key to remove

        Example:
            >>> outcome = ExpectedOutcome(
            ...     outcome_code="PLAY_MUSIC",
            ...     validation_rules={"min_confidence": 0.8, "timeout": 30}
            ... )
            >>> outcome.remove_validation_rule("timeout")
            >>> outcome.validation_rules
            {'min_confidence': 0.8}
        """
        if self.validation_rules and key in self.validation_rules:
            del self.validation_rules[key]

    def update_validation_rules(self, rules: Dict[str, Any]) -> None:
        """
        Update multiple validation rules at once.

        Args:
            rules: Dictionary of validation rules to add/update

        Example:
            >>> outcome = ExpectedOutcome(outcome_code="PLAY_MUSIC")
            >>> outcome.update_validation_rules({"min_confidence": 0.8, "timeout": 30})
            >>> outcome.validation_rules
            {'min_confidence': 0.8, 'timeout': 30}
        """
        if self.validation_rules is None:
            self.validation_rules = {}
        self.validation_rules.update(rules)

    def clear_validation_rules(self) -> None:
        """
        Clear all validation rules.

        Example:
            >>> outcome = ExpectedOutcome(
            ...     outcome_code="PLAY_MUSIC",
            ...     validation_rules={"min_confidence": 0.8}
            ... )
            >>> outcome.clear_validation_rules()
            >>> outcome.validation_rules
            {}
        """
        self.validation_rules = {}

    def add_language_variation(self, language_code: str, variation: Dict[str, Any]) -> None:
        """
        Add or update a language variation.

        Args:
            language_code: Language code (e.g., 'en', 'es', 'fr')
            variation: Language-specific variation data

        Example:
            >>> outcome = ExpectedOutcome(outcome_code="NAVIGATE_HOME")
            >>> outcome.add_language_variation("es", {
            ...     "expected_text": "Navegar a casa",
            ...     "entities": {"action": "navegar", "destination": "casa"}
            ... })
            >>> outcome.language_variations
            {'es': {'expected_text': 'Navegar a casa', 'entities': {'action': 'navegar', 'destination': 'casa'}}}
        """
        if self.language_variations is None:
            self.language_variations = {}
        self.language_variations[language_code] = variation

    def remove_language_variation(self, language_code: str) -> None:
        """
        Remove a language variation.

        Args:
            language_code: Language code to remove

        Example:
            >>> outcome = ExpectedOutcome(
            ...     outcome_code="NAVIGATE_HOME",
            ...     language_variations={"es": {"expected_text": "Navegar a casa"}}
            ... )
            >>> outcome.remove_language_variation("es")
            >>> outcome.language_variations
            {}
        """
        if self.language_variations and language_code in self.language_variations:
            del self.language_variations[language_code]

    def clear_language_variations(self) -> None:
        """
        Clear all language variations.

        Example:
            >>> outcome = ExpectedOutcome(
            ...     outcome_code="NAVIGATE_HOME",
            ...     language_variations={"es": {"expected_text": "Navegar a casa"}}
            ... )
            >>> outcome.clear_language_variations()
            >>> outcome.language_variations
            {}
        """
        self.language_variations = {}

    def get_language_variation(self, language_code: str) -> Optional[Dict[str, Any]]:
        """
        Get language variation for specific language code.

        Args:
            language_code: Language code to retrieve

        Returns:
            Language variation data or None if not found

        Example:
            >>> outcome = ExpectedOutcome(
            ...     outcome_code="NAVIGATE_HOME",
            ...     language_variations={"es": {"expected_text": "Navegar a casa"}}
            ... )
            >>> outcome.get_language_variation("es")
            {'expected_text': 'Navegar a casa'}
            >>> outcome.get_language_variation("fr")
            None
        """
        if self.language_variations:
            return self.language_variations.get(language_code)
        return None

