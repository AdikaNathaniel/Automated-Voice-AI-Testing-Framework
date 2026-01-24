"""
ScenarioBuilderService for authoring scripted test scenarios.

This service handles:
- Creating and managing scenarios with steps
- Multi-step conversation trees with tolerances
- Import/export in JSON and YAML formats
- Version control support
"""

import json
from typing import Any, Dict, List, Optional
from uuid import uuid4

import yaml
import logging

logger = logging.getLogger(__name__)


class ScenarioBuilderService:
    """
    Service for building and managing test scenarios.

    Provides tools for creating, editing, exporting, and importing scenarios.
    """

    def __init__(self) -> None:
        """Initialize the scenario builder service."""
        logger.info("ScenarioBuilderService initialized")

    def create_scenario(
        self,
        name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        version: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new scenario.

        Args:
            name: Scenario name
            description: Optional description
            metadata: Optional metadata dictionary
            version: Optional version string

        Returns:
            Created scenario dictionary
        """
        scenario = {
            'id': str(uuid4()),
            'name': name,
            'description': description or '',
            'version': version or '1.0.0',
            'metadata': metadata or {},
            'steps': []
        }

        logger.info(f"Created scenario: {name}")
        return scenario

    def add_step(
        self,
        scenario: Dict[str, Any],
        user_utterance: str,
        step_metadata: Optional[Dict[str, Any]] = None,
        follow_up_action: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a step to a scenario.

        Note: Expected responses are now defined at the ExpectedOutcome level,
        not at the step level. Use create_expected_outcome() to add validation.

        Args:
            scenario: The scenario to add the step to
            user_utterance: User input for this step
            step_metadata: Optional step metadata (language_variants, etc.)
            follow_up_action: Optional follow-up action

        Returns:
            Created step dictionary
        """
        step_order = len(scenario['steps']) + 1

        step = {
            'id': str(uuid4()),
            'step_order': step_order,
            'user_utterance': user_utterance,
            'step_metadata': step_metadata or {}
        }

        if follow_up_action:
            step['follow_up_action'] = follow_up_action

        scenario['steps'].append(step)
        logger.debug(f"Added step {step_order} to scenario {scenario['name']}")

        return step

    def add_branch(
        self,
        scenario: Dict[str, Any],
        parent_step: Dict[str, Any],
        condition: str,
        user_utterance: str,
        step_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a branching path to a scenario.

        Args:
            scenario: The scenario
            parent_step: The parent step for the branch
            condition: Condition for this branch
            user_utterance: User input for the branch
            step_metadata: Optional step metadata

        Returns:
            Created branch step
        """
        branch_step = self.add_step(
            scenario,
            user_utterance,
            step_metadata
        )

        branch_step['parent_step_id'] = parent_step['id']
        branch_step['condition'] = condition

        return branch_step

    def export_scenario(
        self,
        scenario: Dict[str, Any],
        format: str = 'json'
    ) -> str:
        """
        Export scenario to string format.

        Args:
            scenario: Scenario to export
            format: Export format ('json' or 'yaml')

        Returns:
            Exported string
        """
        if format == 'yaml':
            return yaml.dump(scenario, default_flow_style=False, allow_unicode=True)
        else:
            return json.dumps(scenario, indent=2, default=str)

    def import_scenario(
        self,
        data: str,
        format: str = 'json'
    ) -> Dict[str, Any]:
        """
        Import scenario from string format.

        Args:
            data: Scenario data string
            format: Import format ('json' or 'yaml')

        Returns:
            Imported scenario or error dictionary
        """
        try:
            if format == 'yaml':
                scenario = yaml.safe_load(data)
            else:
                scenario = json.loads(data)

            # Validate required fields
            if not scenario.get('name'):
                return {'valid': False, 'error': 'name is required'}

            # Ensure required fields exist
            if 'id' not in scenario:
                scenario['id'] = str(uuid4())
            if 'steps' not in scenario:
                scenario['steps'] = []
            if 'version' not in scenario:
                scenario['version'] = '1.0.0'

            return scenario

        except Exception as e:
            return {'valid': False, 'error': str(e)}

    def validate_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a scenario structure.

        Args:
            scenario: Scenario to validate

        Returns:
            Validation result
        """
        errors = []

        if not scenario.get('name'):
            errors.append('name is required')

        if not scenario.get('steps'):
            errors.append('scenario must have at least one step')

        if errors:
            return {'valid': False, 'errors': errors}

        return {'valid': True}

    def clone_scenario(
        self,
        scenario: Dict[str, Any],
        new_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Clone a scenario.

        Args:
            scenario: Scenario to clone
            new_name: Optional new name for the clone

        Returns:
            Cloned scenario
        """
        import copy

        clone = copy.deepcopy(scenario)
        clone['id'] = str(uuid4())
        clone['name'] = new_name or f"{scenario['name']} (Copy)"

        # Generate new IDs for steps
        for step in clone['steps']:
            step['id'] = str(uuid4())

        return clone

    def bump_version(
        self,
        scenario: Dict[str, Any],
        bump_type: str = 'patch'
    ) -> None:
        """
        Bump scenario version.

        Args:
            scenario: Scenario to update
            bump_type: Type of bump ('major', 'minor', 'patch')
        """
        version = scenario.get('version', '1.0.0')
        parts = version.split('.')

        if len(parts) != 3:
            parts = ['1', '0', '0']

        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

        if bump_type == 'major':
            major += 1
            minor = 0
            patch = 0
        elif bump_type == 'minor':
            minor += 1
            patch = 0
        else:  # patch
            patch += 1

        scenario['version'] = f"{major}.{minor}.{patch}"


# Singleton instance
scenario_builder_service = ScenarioBuilderService()
