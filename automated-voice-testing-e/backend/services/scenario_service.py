"""
Service layer for scenario script operations.

This module provides the business logic for scenario script management:
- Create, read, update, delete scenarios
- Manage scenario steps
- Handle multi-tenancy scoping

Example:
    >>> from services.scenario_service import ScenarioService
    >>> service = ScenarioService()
    >>> scenario = await service.create(db, data, user_id, tenant_id)
"""

from typing import Optional, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.scenario_script import ScenarioScript, ScenarioStep
from api.schemas.scenario import (
    ScenarioScriptCreate,
    ScenarioScriptUpdate,
    ScenarioStepCreate,
)


class ScenarioService:
    """
    Service for managing scenario scripts and steps.

    Provides CRUD operations with tenant isolation and user tracking.

    Example:
        >>> service = ScenarioService()
        >>> scenarios = await service.list(db, tenant_id=tenant_id)
    """

    async def create(
        self,
        db: AsyncSession,
        data: ScenarioScriptCreate,
        user_id: Optional[UUID] = None,
        tenant_id: Optional[UUID] = None
    ) -> ScenarioScript:
        """
        Create a new scenario script.

        Args:
            db: Database session
            data: Scenario creation data
            user_id: ID of the creating user
            tenant_id: Tenant ID for multi-tenancy

        Returns:
            ScenarioScript: Created scenario

        Example:
            >>> data = ScenarioScriptCreate(name="Navigation Test")
            >>> scenario = await service.create(db, data, user_id)
        """
        # Build script_metadata with noise_config if provided
        script_metadata = {}
        if hasattr(data, 'noise_config') and data.noise_config:
            script_metadata['noise_config'] = data.noise_config.model_dump()

        scenario = ScenarioScript(
            name=data.name,
            description=data.description,
            version=data.version,
            script_metadata=script_metadata if script_metadata else None,
            created_by=user_id,
            tenant_id=tenant_id
        )

        # Add steps if provided
        if data.steps:
            for step_data in data.steps:
                step = ScenarioStep(
                    step_order=step_data.step_order,
                    user_utterance=step_data.user_utterance,
                    step_metadata=step_data.step_metadata,
                    follow_up_action=step_data.follow_up_action
                )
                scenario.steps.append(step)

        db.add(scenario)
        await db.commit()
        await db.refresh(scenario)

        return scenario

    async def get(
        self,
        db: AsyncSession,
        scenario_id: UUID,
        tenant_id: Optional[UUID] = None
    ) -> Optional[ScenarioScript]:
        """
        Get a scenario by ID with tenant isolation.

        Args:
            db: Database session
            scenario_id: Scenario UUID
            tenant_id: Tenant ID for filtering

        Returns:
            ScenarioScript or None if not found
        """
        query = (
            select(ScenarioScript)
            .options(selectinload(ScenarioScript.steps))
            .where(ScenarioScript.id == scenario_id)
        )

        if tenant_id:
            query = query.where(ScenarioScript.tenant_id == tenant_id)

        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def list(
        self,
        db: AsyncSession,
        tenant_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[ScenarioScript]:
        """
        List scenarios with optional filtering.

        Args:
            db: Database session
            tenant_id: Tenant ID for filtering
            skip: Number of records to skip
            limit: Maximum records to return
            is_active: Filter by active status

        Returns:
            List of scenario scripts
        """
        query = (
            select(ScenarioScript)
            .options(selectinload(ScenarioScript.steps))
        )

        if tenant_id:
            query = query.where(ScenarioScript.tenant_id == tenant_id)

        if is_active is not None:
            query = query.where(ScenarioScript.is_active == is_active)

        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        return list(result.scalars().all())

    async def update(
        self,
        db: AsyncSession,
        scenario_id: UUID,
        data: ScenarioScriptUpdate,
        tenant_id: Optional[UUID] = None
    ) -> Optional[ScenarioScript]:
        """
        Update a scenario script.

        Args:
            db: Database session
            scenario_id: Scenario UUID
            data: Update data
            tenant_id: Tenant ID for filtering

        Returns:
            Updated scenario or None if not found
        """
        scenario = await self.get(db, scenario_id, tenant_id)
        if not scenario:
            return None

        # Update fields if provided
        if data.name is not None:
            scenario.name = data.name
        if data.description is not None:
            scenario.description = data.description
        if data.version is not None:
            scenario.version = data.version
        if data.is_active is not None:
            scenario.is_active = data.is_active

        # Update noise_config in script_metadata if provided
        if hasattr(data, 'noise_config') and data.noise_config is not None:
            script_metadata = scenario.script_metadata or {}
            script_metadata['noise_config'] = data.noise_config.model_dump()
            scenario.script_metadata = script_metadata

        # Replace steps if provided
        if data.steps is not None:
            # Clear existing steps
            scenario.steps.clear()

            # Add new steps
            for step_data in data.steps:
                step = ScenarioStep(
                    step_order=step_data.step_order,
                    user_utterance=step_data.user_utterance,
                    step_metadata=step_data.step_metadata,
                    follow_up_action=step_data.follow_up_action
                )
                scenario.steps.append(step)

        await db.commit()
        await db.refresh(scenario)

        return scenario

    async def delete(
        self,
        db: AsyncSession,
        scenario_id: UUID,
        tenant_id: Optional[UUID] = None
    ) -> bool:
        """
        Delete a scenario script.

        Args:
            db: Database session
            scenario_id: Scenario UUID
            tenant_id: Tenant ID for filtering

        Returns:
            True if deleted, False if not found
        """
        scenario = await self.get(db, scenario_id, tenant_id)
        if not scenario:
            return False

        await db.delete(scenario)
        await db.commit()

        return True

    async def add_step(
        self,
        db: AsyncSession,
        scenario_id: UUID,
        data: ScenarioStepCreate,
        tenant_id: Optional[UUID] = None
    ) -> Optional[ScenarioStep]:
        """
        Add a step to an existing scenario.

        Args:
            db: Database session
            scenario_id: Scenario UUID
            data: Step creation data
            tenant_id: Tenant ID for filtering

        Returns:
            Created step or None if scenario not found
        """
        scenario = await self.get(db, scenario_id, tenant_id)
        if not scenario:
            return None

        step = ScenarioStep(
            script_id=scenario_id,
            step_order=data.step_order,
            user_utterance=data.user_utterance,
            step_metadata=data.step_metadata,
            follow_up_action=data.follow_up_action
        )

        db.add(step)
        await db.commit()
        await db.refresh(step)

        return step

    async def get_steps(
        self,
        db: AsyncSession,
        scenario_id: UUID,
        tenant_id: Optional[UUID] = None
    ) -> List[ScenarioStep]:
        """
        Get all steps for a scenario.

        Args:
            db: Database session
            scenario_id: Scenario UUID
            tenant_id: Tenant ID for filtering

        Returns:
            List of scenario steps ordered by step_order
        """
        scenario = await self.get(db, scenario_id, tenant_id)
        if not scenario:
            return []

        return sorted(scenario.steps, key=lambda s: s.step_order)

    async def get_step(
        self,
        db: AsyncSession,
        step_id: UUID,
        scenario_id: Optional[UUID] = None,
        tenant_id: Optional[UUID] = None
    ) -> Optional[ScenarioStep]:
        """
        Get a single step by ID.

        Args:
            db: Database session
            step_id: Step UUID
            scenario_id: Optional scenario UUID for validation
            tenant_id: Tenant ID for filtering

        Returns:
            ScenarioStep or None if not found
        """
        query = select(ScenarioStep).where(ScenarioStep.id == step_id)

        if scenario_id:
            query = query.where(ScenarioStep.script_id == scenario_id)

        # Join with scenario for tenant filtering
        if tenant_id:
            query = (
                query
                .join(ScenarioScript)
                .where(ScenarioScript.tenant_id == tenant_id)
            )

        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def update_step_audio(
        self,
        db: AsyncSession,
        step_id: UUID,
        language_code: str,
        audio_info: dict,
        tenant_id: Optional[UUID] = None
    ) -> Optional[ScenarioStep]:
        """
        Update step metadata with uploaded audio info.

        Args:
            db: Database session
            step_id: Step UUID
            language_code: Language code (e.g., "en-US")
            audio_info: Audio info dict with s3_key, transcription, etc.
            tenant_id: Tenant ID for filtering

        Returns:
            Updated step or None if not found
        """
        step = await self.get_step(db, step_id, tenant_id=tenant_id)
        if not step:
            return None

        # Initialize or update step_metadata
        metadata = step.step_metadata or {}

        # Set audio source to uploaded
        metadata["audio_source"] = "uploaded"

        # Initialize or update uploaded_audio dict
        if "uploaded_audio" not in metadata:
            metadata["uploaded_audio"] = {}

        # Add/update audio info for this language
        metadata["uploaded_audio"][language_code] = audio_info

        # Update the step
        step.step_metadata = metadata
        await db.commit()
        await db.refresh(step)

        return step

    async def remove_step_audio(
        self,
        db: AsyncSession,
        step_id: UUID,
        language_code: str,
        tenant_id: Optional[UUID] = None
    ) -> Optional[ScenarioStep]:
        """
        Remove uploaded audio from step metadata.

        Args:
            db: Database session
            step_id: Step UUID
            language_code: Language code to remove
            tenant_id: Tenant ID for filtering

        Returns:
            Updated step or None if not found
        """
        step = await self.get_step(db, step_id, tenant_id=tenant_id)
        if not step:
            return None

        metadata = step.step_metadata or {}
        uploaded_audio = metadata.get("uploaded_audio", {})

        # Remove the language entry
        if language_code in uploaded_audio:
            del uploaded_audio[language_code]

        # If no more uploaded audio, reset audio_source to tts
        if not uploaded_audio:
            metadata["audio_source"] = "tts"
            if "uploaded_audio" in metadata:
                del metadata["uploaded_audio"]
        else:
            metadata["uploaded_audio"] = uploaded_audio

        step.step_metadata = metadata
        await db.commit()
        await db.refresh(step)

        return step

    async def count(
        self,
        db: AsyncSession,
        tenant_id: Optional[UUID] = None,
        is_active: Optional[bool] = None
    ) -> int:
        """
        Count scenarios with optional filtering.

        Args:
            db: Database session
            tenant_id: Tenant ID for filtering
            is_active: Filter by active status

        Returns:
            Number of matching scenarios
        """
        from sqlalchemy import func

        query = select(func.count(ScenarioScript.id))

        if tenant_id:
            query = query.where(ScenarioScript.tenant_id == tenant_id)

        if is_active is not None:
            query = query.where(ScenarioScript.is_active == is_active)

        result = await db.execute(query)
        return result.scalar() or 0

    # =========================================================================
    # Export Methods
    # =========================================================================

    def export_to_dict(self, scenario: ScenarioScript) -> dict:
        """
        Export scenario to dictionary format.

        Args:
            scenario: Scenario to export

        Returns:
            Dictionary representation for export
        """
        return {
            'name': scenario.name,
            'description': scenario.description,
            'version': scenario.version,
            'metadata': scenario.script_metadata,
            'steps': [
                {
                    'step_order': step.step_order,
                    'user_utterance': step.user_utterance,
                    'step_metadata': step.step_metadata or {},
                    'follow_up_action': step.follow_up_action
                }
                for step in sorted(scenario.steps, key=lambda s: s.step_order)
            ]
        }

    def export_to_json(self, scenario: ScenarioScript, indent: int = 2) -> str:
        """
        Export scenario to JSON string.

        Args:
            scenario: Scenario to export
            indent: JSON indentation level

        Returns:
            JSON string representation
        """
        import json
        return json.dumps(self.export_to_dict(scenario), indent=indent)

    def export_to_yaml(self, scenario: ScenarioScript) -> str:
        """
        Export scenario to YAML string.

        Args:
            scenario: Scenario to export

        Returns:
            YAML string representation
        """
        import yaml
        return yaml.dump(
            self.export_to_dict(scenario),
            default_flow_style=False,
            allow_unicode=True
        )

    # =========================================================================
    # Import Methods
    # =========================================================================

    async def import_from_dict(
        self,
        db: AsyncSession,
        data: dict,
        user_id: Optional[UUID] = None,
        tenant_id: Optional[UUID] = None
    ) -> ScenarioScript:
        """
        Import scenario from dictionary format.

        Args:
            db: Database session
            data: Dictionary with scenario data
            user_id: ID of the importing user
            tenant_id: Tenant ID for multi-tenancy

        Returns:
            Created scenario
        """
        scenario = ScenarioScript(
            name=data['name'],
            description=data.get('description'),
            version=data.get('version'),
            script_metadata=data.get('metadata'),
            created_by=user_id,
            tenant_id=tenant_id
        )

        # Add steps if provided
        if 'steps' in data:
            for step_data in data['steps']:
                step = ScenarioStep(
                    step_order=step_data['step_order'],
                    user_utterance=step_data['user_utterance'],
                    step_metadata=step_data.get('step_metadata', {}),
                    follow_up_action=step_data.get('follow_up_action')
                )
                scenario.steps.append(step)

        db.add(scenario)
        await db.commit()
        await db.refresh(scenario)

        return scenario

    async def import_from_json(
        self,
        db: AsyncSession,
        json_str: str,
        user_id: Optional[UUID] = None,
        tenant_id: Optional[UUID] = None
    ) -> ScenarioScript:
        """
        Import scenario from JSON string.

        Args:
            db: Database session
            json_str: JSON string with scenario data
            user_id: ID of the importing user
            tenant_id: Tenant ID for multi-tenancy

        Returns:
            Created scenario
        """
        import json
        data = json.loads(json_str)
        return await self.import_from_dict(db, data, user_id, tenant_id)

    async def import_from_yaml(
        self,
        db: AsyncSession,
        yaml_str: str,
        user_id: Optional[UUID] = None,
        tenant_id: Optional[UUID] = None
    ) -> ScenarioScript:
        """
        Import scenario from YAML string.

        Args:
            db: Database session
            yaml_str: YAML string with scenario data
            user_id: ID of the importing user
            tenant_id: Tenant ID for multi-tenancy

        Returns:
            Created scenario
        """
        import yaml
        data = yaml.safe_load(yaml_str)
        return await self.import_from_dict(db, data, user_id, tenant_id)


# Module-level instance for convenience
scenario_service = ScenarioService()
