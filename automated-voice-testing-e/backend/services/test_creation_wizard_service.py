"""
Test Creation Wizard Service for voice AI testing.

This service provides guided test creation including
step-by-step configuration, templates, and best practices.

Key features:
- Step-by-step test configuration
- Template-based test creation
- Best practice suggestions

Example:
    >>> service = TestCreationWizardService()
    >>> result = service.start_wizard(test_type='voice')
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class TestCreationWizardService:
    """
    Service for guided test creation.

    Provides step-by-step configuration, templates,
    and best practice suggestions.

    Example:
        >>> service = TestCreationWizardService()
        >>> config = service.get_wizard_config()
    """

    def __init__(self):
        """Initialize the test creation wizard service."""
        self._wizards: Dict[str, Dict[str, Any]] = {}
        self._templates: Dict[str, Dict[str, Any]] = {}
        self._best_practices: List[Dict[str, Any]] = []
        self._default_steps: List[str] = [
            'test_type', 'configuration', 'inputs',
            'expected_outcomes', 'review'
        ]

    def start_wizard(
        self,
        test_type: str = 'voice',
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Start a new test creation wizard.

        Args:
            test_type: Type of test to create
            user_id: User identifier

        Returns:
            Dictionary with wizard session details

        Example:
            >>> result = service.start_wizard(test_type='voice')
        """
        wizard_id = str(uuid.uuid4())

        self._wizards[wizard_id] = {
            'id': wizard_id,
            'test_type': test_type,
            'user_id': user_id,
            'current_step': 0,
            'steps': self._default_steps,
            'data': {},
            'status': 'in_progress',
            'created_at': datetime.utcnow().isoformat()
        }

        return {
            'wizard_id': wizard_id,
            'test_type': test_type,
            'current_step': self._default_steps[0],
            'total_steps': len(self._default_steps),
            'status': 'started',
            'created_at': datetime.utcnow().isoformat()
        }

    def get_current_step(
        self,
        wizard_id: str
    ) -> Dict[str, Any]:
        """
        Get current wizard step.

        Args:
            wizard_id: Wizard session identifier

        Returns:
            Dictionary with current step details

        Example:
            >>> result = service.get_current_step('wizard-1')
        """
        wizard = self._wizards.get(wizard_id)
        if not wizard:
            return {
                'wizard_id': wizard_id,
                'found': False,
                'error': f'Wizard not found: {wizard_id}',
                'retrieved_at': datetime.utcnow().isoformat()
            }

        current_idx = wizard['current_step']
        step_name = wizard['steps'][current_idx]

        return {
            'wizard_id': wizard_id,
            'step_index': current_idx,
            'step_name': step_name,
            'total_steps': len(wizard['steps']),
            'data': wizard['data'].get(step_name, {}),
            'found': True,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def submit_step(
        self,
        wizard_id: str,
        step_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Submit data for current step.

        Args:
            wizard_id: Wizard session identifier
            step_data: Data for current step

        Returns:
            Dictionary with submission result

        Example:
            >>> result = service.submit_step('wizard-1', {'name': 'Test'})
        """
        wizard = self._wizards.get(wizard_id)
        if not wizard:
            return {
                'wizard_id': wizard_id,
                'submitted': False,
                'error': f'Wizard not found: {wizard_id}',
                'submitted_at': datetime.utcnow().isoformat()
            }

        current_idx = wizard['current_step']
        step_name = wizard['steps'][current_idx]

        wizard['data'][step_name] = step_data

        # Auto advance to next step
        if current_idx < len(wizard['steps']) - 1:
            wizard['current_step'] = current_idx + 1

        return {
            'wizard_id': wizard_id,
            'step_name': step_name,
            'submitted': True,
            'next_step': wizard['steps'][wizard['current_step']],
            'submitted_at': datetime.utcnow().isoformat()
        }

    def validate_step(
        self,
        wizard_id: str,
        step_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate step data before submission.

        Args:
            wizard_id: Wizard session identifier
            step_data: Data to validate

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_step('wizard-1', {'name': 'Test'})
        """
        validation_id = str(uuid.uuid4())

        errors = []
        warnings = []

        # Basic validation
        if not step_data:
            errors.append({'field': 'data', 'message': 'No data provided'})

        return {
            'validation_id': validation_id,
            'wizard_id': wizard_id,
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'validated_at': datetime.utcnow().isoformat()
        }

    def navigate_step(
        self,
        wizard_id: str,
        direction: str = 'next'
    ) -> Dict[str, Any]:
        """
        Navigate between wizard steps.

        Args:
            wizard_id: Wizard session identifier
            direction: Navigation direction ('next' or 'prev')

        Returns:
            Dictionary with navigation result

        Example:
            >>> result = service.navigate_step('wizard-1', 'next')
        """
        wizard = self._wizards.get(wizard_id)
        if not wizard:
            return {
                'wizard_id': wizard_id,
                'navigated': False,
                'error': f'Wizard not found: {wizard_id}',
                'navigated_at': datetime.utcnow().isoformat()
            }

        current_idx = wizard['current_step']

        if direction == 'next' and current_idx < len(wizard['steps']) - 1:
            wizard['current_step'] = current_idx + 1
        elif direction == 'prev' and current_idx > 0:
            wizard['current_step'] = current_idx - 1

        return {
            'wizard_id': wizard_id,
            'direction': direction,
            'previous_step': wizard['steps'][current_idx],
            'current_step': wizard['steps'][wizard['current_step']],
            'navigated': True,
            'navigated_at': datetime.utcnow().isoformat()
        }

    def list_templates(
        self,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List available test templates.

        Args:
            category: Filter by category

        Returns:
            Dictionary with templates list

        Example:
            >>> result = service.list_templates()
        """
        templates = list(self._templates.values())

        if category:
            templates = [
                t for t in templates
                if t.get('category') == category
            ]

        return {
            'templates': templates,
            'count': len(templates),
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def get_template(
        self,
        template_id: str
    ) -> Dict[str, Any]:
        """
        Get template by ID.

        Args:
            template_id: Template identifier

        Returns:
            Dictionary with template details

        Example:
            >>> result = service.get_template('template-1')
        """
        template = self._templates.get(template_id)
        if not template:
            return {
                'template_id': template_id,
                'found': False,
                'error': f'Template not found: {template_id}',
                'retrieved_at': datetime.utcnow().isoformat()
            }

        return {
            'template_id': template_id,
            'found': True,
            **template,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def apply_template(
        self,
        wizard_id: str,
        template_id: str
    ) -> Dict[str, Any]:
        """
        Apply template to wizard.

        Args:
            wizard_id: Wizard session identifier
            template_id: Template identifier

        Returns:
            Dictionary with application result

        Example:
            >>> result = service.apply_template('wizard-1', 'template-1')
        """
        wizard = self._wizards.get(wizard_id)
        template = self._templates.get(template_id)

        if not wizard:
            return {
                'wizard_id': wizard_id,
                'applied': False,
                'error': f'Wizard not found: {wizard_id}',
                'applied_at': datetime.utcnow().isoformat()
            }

        if template:
            wizard['data'].update(template.get('data', {}))

        return {
            'wizard_id': wizard_id,
            'template_id': template_id,
            'applied': True,
            'applied_at': datetime.utcnow().isoformat()
        }

    def customize_template(
        self,
        template_id: str,
        customizations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Customize a template.

        Args:
            template_id: Template identifier
            customizations: Customization data

        Returns:
            Dictionary with customization result

        Example:
            >>> result = service.customize_template('template-1', data)
        """
        custom_id = str(uuid.uuid4())

        custom_template = {
            'id': custom_id,
            'base_template': template_id,
            'customizations': customizations,
            'created_at': datetime.utcnow().isoformat()
        }

        self._templates[custom_id] = custom_template

        return {
            'custom_template_id': custom_id,
            'base_template_id': template_id,
            'customized': True,
            'customized_at': datetime.utcnow().isoformat()
        }

    def get_suggestions(
        self,
        wizard_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get best practice suggestions.

        Args:
            wizard_id: Wizard session identifier
            context: Additional context

        Returns:
            Dictionary with suggestions

        Example:
            >>> result = service.get_suggestions('wizard-1')
        """
        suggestions = [
            {
                'id': 'suggestion-1',
                'type': 'best_practice',
                'title': 'Use descriptive test names',
                'description': 'Clear names help identify test purpose'
            },
            {
                'id': 'suggestion-2',
                'type': 'best_practice',
                'title': 'Include timeout settings',
                'description': 'Prevent tests from hanging indefinitely'
            }
        ]

        return {
            'wizard_id': wizard_id,
            'suggestions': suggestions,
            'count': len(suggestions),
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def validate_best_practices(
        self,
        wizard_id: str
    ) -> Dict[str, Any]:
        """
        Validate wizard data against best practices.

        Args:
            wizard_id: Wizard session identifier

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_best_practices('wizard-1')
        """
        validation_id = str(uuid.uuid4())

        wizard = self._wizards.get(wizard_id)
        if not wizard:
            return {
                'validation_id': validation_id,
                'wizard_id': wizard_id,
                'valid': False,
                'error': f'Wizard not found: {wizard_id}',
                'validated_at': datetime.utcnow().isoformat()
            }

        violations = []
        passed = []

        # Check for best practices
        if not wizard['data'].get('test_type', {}).get('name'):
            violations.append({
                'practice': 'descriptive_name',
                'message': 'Test name not provided'
            })
        else:
            passed.append('descriptive_name')

        return {
            'validation_id': validation_id,
            'wizard_id': wizard_id,
            'violations': violations,
            'passed': passed,
            'valid': len(violations) == 0,
            'validated_at': datetime.utcnow().isoformat()
        }

    def get_recommendations(
        self,
        wizard_id: str,
        step_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get recommendations for wizard step.

        Args:
            wizard_id: Wizard session identifier
            step_name: Specific step name

        Returns:
            Dictionary with recommendations

        Example:
            >>> result = service.get_recommendations('wizard-1')
        """
        recommendations = [
            {
                'id': 'rec-1',
                'priority': 'high',
                'recommendation': 'Add retry logic for flaky tests',
                'step': 'configuration'
            },
            {
                'id': 'rec-2',
                'priority': 'medium',
                'recommendation': 'Include cleanup steps',
                'step': 'expected_outcomes'
            }
        ]

        if step_name:
            recommendations = [
                r for r in recommendations
                if r.get('step') == step_name
            ]

        return {
            'wizard_id': wizard_id,
            'recommendations': recommendations,
            'count': len(recommendations),
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def get_wizard_config(self) -> Dict[str, Any]:
        """
        Get wizard configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_wizard_config()
        """
        return {
            'total_wizards': len(self._wizards),
            'total_templates': len(self._templates),
            'default_steps': self._default_steps,
            'features': [
                'step_by_step', 'templates',
                'best_practices', 'recommendations'
            ]
        }
