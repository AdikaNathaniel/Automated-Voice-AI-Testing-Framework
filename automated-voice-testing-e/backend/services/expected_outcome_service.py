"""
ExpectedOutcome Service

This service handles creation and management of ExpectedOutcome records,
including conversion from scenario_definition and merging of global defaults
with test-specific overrides.
"""

from typing import Dict, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.expected_outcome import ExpectedOutcome
from models.scenario_script import ScenarioScript
from api.config import get_settings


class ExpectedOutcomeService:
    """Service for managing ExpectedOutcome records"""

    def __init__(self):
        self.settings = get_settings()

    def _merge_validation_thresholds(
        self,
        test_overrides: Optional[Dict[str, float]] = None
    ) -> Dict[str, float]:
        """
        Merge global default thresholds with test-specific overrides.

        Args:
            test_overrides: Optional test-specific threshold overrides

        Returns:
            Dict of merged validation thresholds
        """
        # Start with global defaults
        merged = {
            "semantic_similarity": self.settings.DEFAULT_SEMANTIC_SIMILARITY_THRESHOLD,
            "intent_match": self.settings.DEFAULT_INTENT_MATCH_THRESHOLD,
            "entity_match": self.settings.DEFAULT_ENTITY_MATCH_THRESHOLD,
            "wer": self.settings.DEFAULT_WER_THRESHOLD,
            "cer": self.settings.DEFAULT_CER_THRESHOLD,
            "confidence_auto_pass": self.settings.DEFAULT_CONFIDENCE_AUTO_PASS,
            "confidence_needs_review": self.settings.DEFAULT_CONFIDENCE_NEEDS_REVIEW,
            "asr_confidence_min": self.settings.DEFAULT_ASR_CONFIDENCE_MIN,
        }

        # Override with test-specific values if provided
        if test_overrides:
            merged.update(test_overrides)

        return merged

    def create_from_scenario_definition(
        self,
        script_id: UUID,
        scenario_def: Dict[str, Any],
        language_code: str,
        tenant_id: UUID = None
    ) -> ExpectedOutcome:
        """
        Create ExpectedOutcome from scenario script definition.

        Args:
            script_id: UUID of the scenario script
            scenario_def: scenario_definition dict from ScenarioScript
            language_code: Language code for this execution
            tenant_id: Tenant ID for multi-tenancy (required)

        Returns:
            ExpectedOutcome instance (not yet added to session)

        Example scenario_def structure:
            {
                "queries": {"en-US": "What's the weather?"},
                "expected_entities": ["location"],
                "expected_command_kind": "WeatherCommand",  # Optional
                "validation_thresholds": {...},  # Optional overrides
                "expected_asr_confidence_min": 0.85,  # Optional
                "expected_response_content": {...},  # Optional
                "conversation_requirements": {...}  # Optional
            }
        """
        # Get expected entities from scenario definition
        expected_entities = scenario_def.get("expected_entities", [])

        # Get Houndify-specific fields
        expected_command_kind = scenario_def.get("expected_command_kind")
        expected_asr_confidence_min = scenario_def.get(
            "expected_asr_confidence_min",
            self.settings.DEFAULT_ASR_CONFIDENCE_MIN
        )

        # Merge validation thresholds
        validation_thresholds = self._merge_validation_thresholds(
            test_overrides=scenario_def.get("validation_thresholds")
        )

        # Create outcome code (unique identifier for this auto-generated outcome)
        outcome_code = f"AUTO_{script_id}_{language_code}_{expected_command_kind or 'generic'}"

        # Create ExpectedOutcome instance
        outcome = ExpectedOutcome(
            tenant_id=tenant_id,
            outcome_code=outcome_code,
            name=f"Auto-generated outcome for scenario {script_id}",
            description=f"Expected outcome for language {language_code}",
            # Core validation fields
            entities={
                "expected_entities": expected_entities,
            },
            validation_rules=validation_thresholds,
            required_entities=expected_entities,
            # Houndify-specific fields (CommandKind only, not intent)
            expected_command_kind=expected_command_kind,
            expected_asr_confidence_min=expected_asr_confidence_min,
            expected_response_content=scenario_def.get("expected_response_content"),
            expected_native_data_schema=scenario_def.get("expected_native_data_schema"),
            conversation_requirements=scenario_def.get("conversation_requirements"),
            # Optional fields from scenario definition
            forbidden_phrases=scenario_def.get("forbidden_responses"),
            acceptable_alternates=scenario_def.get("acceptable_alternates"),
        )

        return outcome

    async def get_or_create_outcome(
        self,
        scenario: ScenarioScript,
        language_code: str,
        db: AsyncSession,
        tenant_id: UUID = None
    ) -> ExpectedOutcome:
        """
        Get existing ExpectedOutcome or create new one from scenario_definition.

        This method checks if the scenario already has an expected_outcome_id.
        If yes, returns the existing outcome. If no, creates a new one from
        scenario_definition.

        Args:
            scenario: ScenarioScript instance
            language_code: Language code for this execution
            db: Database session
            tenant_id: Tenant ID for multi-tenancy (required for new outcomes)

        Returns:
            ExpectedOutcome instance

        Raises:
            ValueError: If scenario has no expected outcome definition
        """
        # If scenario already has expected_outcome_id, use it
        # This supports pre-created reusable ExpectedOutcome records
        if hasattr(scenario, 'expected_outcome_id') and scenario.expected_outcome_id:
            stmt = select(ExpectedOutcome).where(
                ExpectedOutcome.id == scenario.expected_outcome_id
            )
            result = await db.execute(stmt)
            outcome = result.scalar_one_or_none()

            if outcome:
                return outcome

        # Otherwise, create from scenario_definition
        if not scenario.scenario_definition:
            raise ValueError(
                f"Scenario {scenario.id} has no scenario_definition "
                "and no expected_outcome_id"
            )

        # Create new outcome from scenario definition
        outcome = self.create_from_scenario_definition(
            script_id=scenario.id,
            scenario_def=scenario.scenario_definition,
            language_code=language_code,
            tenant_id=tenant_id or scenario.tenant_id
        )

        # Add to session and flush to get ID
        db.add(outcome)
        await db.flush()

        return outcome

    async def get_by_id(
        self,
        outcome_id: UUID,
        db: AsyncSession
    ) -> Optional[ExpectedOutcome]:
        """
        Get ExpectedOutcome by ID.

        Args:
            outcome_id: UUID of the expected outcome
            db: Database session

        Returns:
            ExpectedOutcome instance or None
        """
        stmt = select(ExpectedOutcome).where(ExpectedOutcome.id == outcome_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


__all__ = ["ExpectedOutcomeService"]
