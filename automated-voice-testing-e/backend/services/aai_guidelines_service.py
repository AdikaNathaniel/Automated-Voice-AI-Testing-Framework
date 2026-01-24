"""
Alliance for Automotive Innovation Guidelines Service.

This service provides AAI (formerly AAM) guidelines compliance
testing for automotive voice AI systems.

Key guidelines:
- Statement of Principles for Driver Interactions (2021)
- Menu item limits (4-5 items per AAA Foundation research)

Example:
    >>> service = AAIGuidelinesService()
    >>> result = service.check_driver_interaction_compliance(data)
"""

from typing import List, Dict, Any
from datetime import datetime
import uuid


class AAIGuidelinesService:
    """
    Service for AAI guidelines compliance testing.

    Provides automotive voice AI testing against Alliance for
    Automotive Innovation guidelines for driver interaction.

    Example:
        >>> service = AAIGuidelinesService()
        >>> config = service.get_aai_guidelines_config()
    """

    def __init__(self):
        """Initialize the AAI guidelines service."""
        self._menu_item_limit = 5  # AAA Foundation research
        self._max_glance_time = 2.0  # seconds
        self._max_task_time = 12.0  # seconds
        self._test_results: List[Dict[str, Any]] = []

    def check_driver_interaction_compliance(
        self,
        interaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check driver interaction compliance per AAI principles.

        Args:
            interaction_data: Interaction test data

        Returns:
            Dictionary with compliance result

        Example:
            >>> result = service.check_driver_interaction_compliance({'glance_time': 1.5})
        """
        check_id = str(uuid.uuid4())

        violations: List[Dict[str, str]] = []

        # Glance time check
        glance_time = interaction_data.get('glance_time_seconds', 0)
        if glance_time > self._max_glance_time:
            violations.append({
                'principle': 'visual_demand',
                'message': f'Glance time {glance_time}s exceeds {self._max_glance_time}s limit'
            })

        # Task completion time
        task_time = interaction_data.get('task_time_seconds', 0)
        if task_time > self._max_task_time:
            violations.append({
                'principle': 'task_time',
                'message': f'Task time {task_time}s exceeds {self._max_task_time}s limit'
            })

        # Manual input check while driving
        manual_input = interaction_data.get('requires_manual_input', False)
        is_driving = interaction_data.get('is_driving', False)
        if manual_input and is_driving:
            violations.append({
                'principle': 'manual_input',
                'message': 'Manual input prohibited while driving'
            })

        compliant = len(violations) == 0

        result = {
            'guideline': 'AAI_Driver_Interaction',
            'compliant': compliant,
            'violations': violations
        }
        self._test_results.append(result)

        return {
            'check_id': check_id,
            'guideline': 'Statement of Principles 2021',
            'compliant': compliant,
            'violations': violations,
            'violation_count': len(violations),
            'checked_at': datetime.utcnow().isoformat()
        }

    def validate_interaction_principles(
        self,
        interaction_flow: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate interaction flow against AAI principles.

        Args:
            interaction_flow: Interaction flow data

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_interaction_principles({'steps': 2})
        """
        validation_id = str(uuid.uuid4())

        issues: List[str] = []

        # Check number of steps
        steps = interaction_flow.get('steps', 0)
        if steps > 3:
            issues.append('Too many interaction steps')

        # Check interruptibility
        is_interruptible = interaction_flow.get('is_interruptible', False)
        if not is_interruptible:
            issues.append('Interaction must be interruptible')

        # Check resumability
        is_resumable = interaction_flow.get('is_resumable', False)
        if not is_resumable:
            issues.append('Interaction should be resumable')

        # Check audio feedback
        has_audio_feedback = interaction_flow.get('has_audio_feedback', False)
        if not has_audio_feedback:
            issues.append('Missing audio feedback')

        return {
            'validation_id': validation_id,
            'valid': len(issues) == 0,
            'issues': issues,
            'issue_count': len(issues),
            'validated_at': datetime.utcnow().isoformat()
        }

    def check_menu_item_limits(
        self,
        menu_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check menu item limits per AAA Foundation research.

        Args:
            menu_data: Menu structure data

        Returns:
            Dictionary with compliance result

        Example:
            >>> result = service.check_menu_item_limits({'items': 4})
        """
        check_id = str(uuid.uuid4())

        violations: List[Dict[str, str]] = []

        # Check item count
        item_count = menu_data.get('item_count', 0)
        if item_count > self._menu_item_limit:
            violations.append({
                'guideline': 'menu_items',
                'message': f'Menu has {item_count} items, exceeds {self._menu_item_limit} limit'
            })

        # Check submenu depth
        depth = menu_data.get('max_depth', 0)
        if depth > 3:
            violations.append({
                'guideline': 'menu_depth',
                'message': f'Menu depth {depth} exceeds 3 levels'
            })

        # Check item label length
        max_label_length = menu_data.get('max_label_length', 0)
        if max_label_length > 20:
            violations.append({
                'guideline': 'label_length',
                'message': 'Menu item labels too long'
            })

        compliant = len(violations) == 0

        result = {
            'guideline': 'AAA_Menu_Limits',
            'compliant': compliant,
            'violations': violations
        }
        self._test_results.append(result)

        return {
            'check_id': check_id,
            'guideline': 'AAA Foundation Menu Research',
            'compliant': compliant,
            'item_count': item_count,
            'limit': self._menu_item_limit,
            'violations': violations,
            'checked_at': datetime.utcnow().isoformat()
        }

    def validate_menu_structure(
        self,
        menu_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate menu structure against AAI guidelines.

        Args:
            menu_structure: Menu structure data

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_menu_structure({'levels': 2})
        """
        validation_id = str(uuid.uuid4())

        issues: List[str] = []

        # Check hierarchy
        levels = menu_structure.get('levels', 0)
        if levels > 3:
            issues.append('Menu hierarchy too deep')

        # Check for logical grouping
        has_grouping = menu_structure.get('has_logical_grouping', False)
        if not has_grouping:
            issues.append('Items should be logically grouped')

        # Check for voice shortcuts
        has_shortcuts = menu_structure.get('has_voice_shortcuts', False)
        if not has_shortcuts:
            issues.append('Missing voice shortcuts for frequent items')

        # Check for confirmation
        has_confirmation = menu_structure.get('has_confirmation', False)
        critical_actions = menu_structure.get('has_critical_actions', False)
        if critical_actions and not has_confirmation:
            issues.append('Critical actions need confirmation')

        return {
            'validation_id': validation_id,
            'valid': len(issues) == 0,
            'issues': issues,
            'issue_count': len(issues),
            'validated_at': datetime.utcnow().isoformat()
        }

    def categorize_cognitive_distraction(
        self,
        task_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Categorize task by cognitive distraction level (1-3 scale).

        Args:
            task_data: Task characteristics data

        Returns:
            Dictionary with distraction category

        Example:
            >>> result = service.categorize_cognitive_distraction({'steps': 1})
        """
        category_id = str(uuid.uuid4())

        # Extract task characteristics
        steps = task_data.get('interaction_steps', 1)
        requires_visual = task_data.get('requires_visual_attention', False)
        requires_memory = task_data.get('requires_memory', False)
        time_pressure = task_data.get('time_pressure', False)
        decision_complexity = task_data.get('decision_complexity', 'low')

        # Calculate distraction score
        score = 0

        # Steps contribute to distraction
        if steps <= 1:
            score += 1
        elif steps <= 3:
            score += 2
        else:
            score += 3

        # Visual attention increases distraction
        if requires_visual:
            score += 1

        # Memory load increases distraction
        if requires_memory:
            score += 1

        # Time pressure increases distraction
        if time_pressure:
            score += 1

        # Decision complexity
        if decision_complexity == 'medium':
            score += 1
        elif decision_complexity == 'high':
            score += 2

        # Map score to category (1-3)
        if score <= 2:
            category = 1
            description = 'Low distraction'
        elif score <= 5:
            category = 2
            description = 'Moderate distraction'
        else:
            category = 3
            description = 'High distraction'

        return {
            'category_id': category_id,
            'category': category,
            'description': description,
            'score': score,
            'factors': {
                'steps': steps,
                'requires_visual': requires_visual,
                'requires_memory': requires_memory,
                'time_pressure': time_pressure,
                'decision_complexity': decision_complexity
            },
            'categorized_at': datetime.utcnow().isoformat()
        }

    def assess_task_complexity(
        self,
        task_sequence: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Assess overall complexity of a task sequence.

        Args:
            task_sequence: List of tasks to assess

        Returns:
            Dictionary with complexity assessment

        Example:
            >>> result = service.assess_task_complexity([{'steps': 1}, {'steps': 2}])
        """
        assessment_id = str(uuid.uuid4())

        if not task_sequence:
            return {
                'assessment_id': assessment_id,
                'total_tasks': 0,
                'average_category': 0,
                'assessed_at': datetime.utcnow().isoformat()
            }

        # Categorize each task
        categories = []
        for task in task_sequence:
            result = self.categorize_cognitive_distraction(task)
            categories.append(result['category'])

        average_category = sum(categories) / len(categories)

        # Count by category
        category_counts = {1: 0, 2: 0, 3: 0}
        for cat in categories:
            category_counts[cat] = category_counts.get(cat, 0) + 1

        # Determine overall complexity
        if average_category <= 1.5:
            overall = 'low'
        elif average_category <= 2.5:
            overall = 'moderate'
        else:
            overall = 'high'

        return {
            'assessment_id': assessment_id,
            'total_tasks': len(task_sequence),
            'average_category': round(average_category, 2),
            'category_distribution': category_counts,
            'overall_complexity': overall,
            'max_category': max(categories),
            'min_category': min(categories),
            'assessed_at': datetime.utcnow().isoformat()
        }

    def get_aai_guidelines_config(self) -> Dict[str, Any]:
        """
        Get AAI guidelines service configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_aai_guidelines_config()
        """
        return {
            'menu_item_limit': self._menu_item_limit,
            'max_glance_time_seconds': self._max_glance_time,
            'max_task_time_seconds': self._max_task_time,
            'total_tests': len(self._test_results),
            'distraction_categories': {
                1: 'Low distraction',
                2: 'Moderate distraction',
                3: 'High distraction'
            },
            'features': [
                'driver_interaction_compliance',
                'interaction_principles',
                'menu_item_limits',
                'menu_structure_validation',
                'cognitive_distraction_categorization'
            ]
        }
