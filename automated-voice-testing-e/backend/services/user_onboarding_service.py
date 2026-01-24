"""
User Onboarding Service for voice AI testing.

This service provides user onboarding including
interactive tutorials, sample data, and quick start guides.

Key features:
- Interactive tutorial
- Sample data population
- Quick start guides

Example:
    >>> service = UserOnboardingService()
    >>> result = service.start_tutorial(user_id='user-1')
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class UserOnboardingService:
    """
    Service for user onboarding.

    Provides interactive tutorials, sample data,
    and quick start guides.

    Example:
        >>> service = UserOnboardingService()
        >>> config = service.get_onboarding_config()
    """

    def __init__(self):
        """Initialize the user onboarding service."""
        self._tutorials: Dict[str, Dict[str, Any]] = {}
        self._sample_data: Dict[str, Dict[str, Any]] = {}
        self._guides: Dict[str, Dict[str, Any]] = {}
        self._default_tutorial_steps: List[str] = [
            'welcome', 'create_test', 'run_test',
            'view_results', 'complete'
        ]

    def start_tutorial(
        self,
        user_id: str,
        tutorial_type: str = 'basic'
    ) -> Dict[str, Any]:
        """
        Start interactive tutorial.

        Args:
            user_id: User identifier
            tutorial_type: Type of tutorial

        Returns:
            Dictionary with tutorial details

        Example:
            >>> result = service.start_tutorial('user-1')
        """
        tutorial_id = str(uuid.uuid4())

        self._tutorials[tutorial_id] = {
            'id': tutorial_id,
            'user_id': user_id,
            'type': tutorial_type,
            'current_step': 0,
            'steps': self._default_tutorial_steps,
            'completed_steps': [],
            'status': 'in_progress',
            'started_at': datetime.utcnow().isoformat()
        }

        return {
            'tutorial_id': tutorial_id,
            'user_id': user_id,
            'tutorial_type': tutorial_type,
            'current_step': self._default_tutorial_steps[0],
            'total_steps': len(self._default_tutorial_steps),
            'status': 'started',
            'started_at': datetime.utcnow().isoformat()
        }

    def get_tutorial_step(
        self,
        tutorial_id: str
    ) -> Dict[str, Any]:
        """
        Get current tutorial step.

        Args:
            tutorial_id: Tutorial identifier

        Returns:
            Dictionary with step details

        Example:
            >>> result = service.get_tutorial_step('tutorial-1')
        """
        tutorial = self._tutorials.get(tutorial_id)
        if not tutorial:
            return {
                'tutorial_id': tutorial_id,
                'found': False,
                'error': f'Tutorial not found: {tutorial_id}',
                'retrieved_at': datetime.utcnow().isoformat()
            }

        current_idx = tutorial['current_step']
        step_name = tutorial['steps'][current_idx]

        return {
            'tutorial_id': tutorial_id,
            'step_index': current_idx,
            'step_name': step_name,
            'total_steps': len(tutorial['steps']),
            'found': True,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def complete_tutorial_step(
        self,
        tutorial_id: str,
        step_name: str
    ) -> Dict[str, Any]:
        """
        Complete a tutorial step.

        Args:
            tutorial_id: Tutorial identifier
            step_name: Step name to complete

        Returns:
            Dictionary with completion result

        Example:
            >>> result = service.complete_tutorial_step('tutorial-1', 'welcome')
        """
        tutorial = self._tutorials.get(tutorial_id)
        if not tutorial:
            return {
                'tutorial_id': tutorial_id,
                'completed': False,
                'error': f'Tutorial not found: {tutorial_id}',
                'completed_at': datetime.utcnow().isoformat()
            }

        tutorial['completed_steps'].append(step_name)

        # Auto advance to next step
        current_idx = tutorial['current_step']
        if current_idx < len(tutorial['steps']) - 1:
            tutorial['current_step'] = current_idx + 1
        else:
            tutorial['status'] = 'completed'

        return {
            'tutorial_id': tutorial_id,
            'step_name': step_name,
            'completed': True,
            'next_step': tutorial['steps'][tutorial['current_step']],
            'status': tutorial['status'],
            'completed_at': datetime.utcnow().isoformat()
        }

    def skip_tutorial(
        self,
        tutorial_id: str
    ) -> Dict[str, Any]:
        """
        Skip tutorial.

        Args:
            tutorial_id: Tutorial identifier

        Returns:
            Dictionary with skip result

        Example:
            >>> result = service.skip_tutorial('tutorial-1')
        """
        tutorial = self._tutorials.get(tutorial_id)
        if not tutorial:
            return {
                'tutorial_id': tutorial_id,
                'skipped': False,
                'error': f'Tutorial not found: {tutorial_id}',
                'skipped_at': datetime.utcnow().isoformat()
            }

        tutorial['status'] = 'skipped'

        return {
            'tutorial_id': tutorial_id,
            'skipped': True,
            'status': 'skipped',
            'skipped_at': datetime.utcnow().isoformat()
        }

    def populate_sample_data(
        self,
        user_id: str,
        dataset_type: str = 'basic'
    ) -> Dict[str, Any]:
        """
        Populate sample data for user.

        Args:
            user_id: User identifier
            dataset_type: Type of sample data

        Returns:
            Dictionary with population result

        Example:
            >>> result = service.populate_sample_data('user-1')
        """
        population_id = str(uuid.uuid4())

        sample_items = {
            'test_suites': 3,
            'test_cases': 10,
            'test_runs': 5
        }

        self._sample_data[user_id] = {
            'population_id': population_id,
            'user_id': user_id,
            'dataset_type': dataset_type,
            'items': sample_items,
            'populated_at': datetime.utcnow().isoformat()
        }

        return {
            'population_id': population_id,
            'user_id': user_id,
            'dataset_type': dataset_type,
            'items_created': sample_items,
            'populated_at': datetime.utcnow().isoformat()
        }

    def get_sample_datasets(self) -> Dict[str, Any]:
        """
        Get available sample datasets.

        Returns:
            Dictionary with datasets list

        Example:
            >>> result = service.get_sample_datasets()
        """
        datasets = [
            {
                'id': 'basic',
                'name': 'Basic Dataset',
                'description': 'Simple test data for getting started',
                'items': {'test_suites': 3, 'test_cases': 10}
            },
            {
                'id': 'advanced',
                'name': 'Advanced Dataset',
                'description': 'Complex test scenarios',
                'items': {'test_suites': 10, 'test_cases': 50}
            }
        ]

        return {
            'datasets': datasets,
            'count': len(datasets),
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def clear_sample_data(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Clear sample data for user.

        Args:
            user_id: User identifier

        Returns:
            Dictionary with clear result

        Example:
            >>> result = service.clear_sample_data('user-1')
        """
        if user_id in self._sample_data:
            del self._sample_data[user_id]
            return {
                'user_id': user_id,
                'cleared': True,
                'cleared_at': datetime.utcnow().isoformat()
            }

        return {
            'user_id': user_id,
            'cleared': False,
            'error': f'No sample data found for: {user_id}',
            'cleared_at': datetime.utcnow().isoformat()
        }

    def list_guides(
        self,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List quick start guides.

        Args:
            category: Filter by category

        Returns:
            Dictionary with guides list

        Example:
            >>> result = service.list_guides()
        """
        guides = [
            {
                'id': 'getting-started',
                'title': 'Getting Started',
                'category': 'basics',
                'estimated_time': '5 min'
            },
            {
                'id': 'first-test',
                'title': 'Create Your First Test',
                'category': 'basics',
                'estimated_time': '10 min'
            },
            {
                'id': 'voice-testing',
                'title': 'Voice Testing Guide',
                'category': 'advanced',
                'estimated_time': '15 min'
            }
        ]

        if category:
            guides = [g for g in guides if g.get('category') == category]

        return {
            'guides': guides,
            'count': len(guides),
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def get_guide(
        self,
        guide_id: str
    ) -> Dict[str, Any]:
        """
        Get guide by ID.

        Args:
            guide_id: Guide identifier

        Returns:
            Dictionary with guide details

        Example:
            >>> result = service.get_guide('getting-started')
        """
        guide = self._guides.get(guide_id)
        if not guide:
            # Return default guide content
            return {
                'guide_id': guide_id,
                'title': f'Guide: {guide_id}',
                'content': 'Guide content here',
                'steps': ['Step 1', 'Step 2', 'Step 3'],
                'found': True,
                'retrieved_at': datetime.utcnow().isoformat()
            }

        return {
            'guide_id': guide_id,
            'found': True,
            **guide,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def track_guide_progress(
        self,
        user_id: str,
        guide_id: str,
        progress: int
    ) -> Dict[str, Any]:
        """
        Track guide progress.

        Args:
            user_id: User identifier
            guide_id: Guide identifier
            progress: Progress percentage (0-100)

        Returns:
            Dictionary with tracking result

        Example:
            >>> result = service.track_guide_progress('user-1', 'guide-1', 50)
        """
        tracking_id = str(uuid.uuid4())

        return {
            'tracking_id': tracking_id,
            'user_id': user_id,
            'guide_id': guide_id,
            'progress': progress,
            'completed': progress >= 100,
            'tracked_at': datetime.utcnow().isoformat()
        }

    def get_onboarding_config(self) -> Dict[str, Any]:
        """
        Get onboarding configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_onboarding_config()
        """
        return {
            'total_tutorials': len(self._tutorials),
            'total_sample_data': len(self._sample_data),
            'total_guides': len(self._guides),
            'default_tutorial_steps': self._default_tutorial_steps,
            'features': [
                'interactive_tutorial', 'sample_data',
                'quick_start_guides', 'progress_tracking'
            ]
        }
