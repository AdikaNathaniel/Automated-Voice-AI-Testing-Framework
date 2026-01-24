"""
Ephemeral Environments Service for voice AI testing.

This service provides ephemeral environment management for
PR previews and temporary testing environments.

Key features:
- PR preview environments
- Automatic cleanup
- Resource isolation
- Environment lifecycle management

Example:
    >>> service = EphemeralEnvironmentsService()
    >>> env = service.create_preview_environment(pr_number=123)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid


class EphemeralEnvironmentsService:
    """
    Service for ephemeral environment management.

    Provides temporary environments for PR previews and
    isolated testing with automatic cleanup.

    Example:
        >>> service = EphemeralEnvironmentsService()
        >>> config = service.get_ephemeral_config()
    """

    def __init__(self):
        """Initialize the ephemeral environments service."""
        self._environments: Dict[str, Dict[str, Any]] = {}
        self._cleanup_schedules: Dict[str, Dict[str, Any]] = {}
        self._default_ttl_hours = 24
        self._max_environments = 50

    def create_preview_environment(
        self,
        pr_number: int,
        branch: str = 'feature',
        config: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a PR preview environment.

        Args:
            pr_number: Pull request number
            branch: Branch name
            config: Environment configuration
            tags: Optional list of tags for the environment

        Returns:
            Dictionary with environment details

        Example:
            >>> env = service.create_preview_environment(123, 'feature-x', tags=['test', 'ci'])
        """
        env_id = str(uuid.uuid4())

        # Generate unique subdomain
        subdomain = f'pr-{pr_number}-{env_id[:8]}'
        url = f'https://{subdomain}.preview.example.com'

        environment = {
            'env_id': env_id,
            'pr_number': pr_number,
            'branch': branch,
            'url': url,
            'status': 'provisioning',
            'resources': {
                'cpu': '0.5',
                'memory': '512Mi',
                'storage': '1Gi'
            },
            'config': config or {},
            'tags': tags or [],
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=self._default_ttl_hours)).isoformat()
        }

        self._environments[env_id] = environment

        # Schedule automatic cleanup
        self._cleanup_schedules[env_id] = {
            'scheduled_at': environment['expires_at'],
            'reason': 'ttl_expired'
        }

        return {
            'env_id': env_id,
            'pr_number': pr_number,
            'url': url,
            'status': 'provisioning',
            'expires_at': environment['expires_at'],
            'created_at': environment['created_at']
        }

    def get_environment_url(
        self,
        env_id: str
    ) -> Dict[str, Any]:
        """
        Get URL for an environment.

        Args:
            env_id: Environment identifier

        Returns:
            Dictionary with environment URL

        Example:
            >>> url = service.get_environment_url('env_123')
        """
        query_id = str(uuid.uuid4())

        if env_id not in self._environments:
            return {
                'query_id': query_id,
                'found': False,
                'error': 'Environment not found',
                'queried_at': datetime.utcnow().isoformat()
            }

        env = self._environments[env_id]

        return {
            'query_id': query_id,
            'env_id': env_id,
            'url': env['url'],
            'status': env['status'],
            'found': True,
            'queried_at': datetime.utcnow().isoformat()
        }

    def cleanup_environment(
        self,
        env_id: str,
        reason: str = 'manual'
    ) -> Dict[str, Any]:
        """
        Clean up an environment.

        Args:
            env_id: Environment identifier
            reason: Cleanup reason

        Returns:
            Dictionary with cleanup result

        Example:
            >>> result = service.cleanup_environment('env_123')
        """
        cleanup_id = str(uuid.uuid4())

        if env_id not in self._environments:
            return {
                'cleanup_id': cleanup_id,
                'success': False,
                'error': 'Environment not found',
                'cleaned_at': datetime.utcnow().isoformat()
            }

        env = self._environments[env_id]

        # Remove environment
        del self._environments[env_id]

        # Remove cleanup schedule
        if env_id in self._cleanup_schedules:
            del self._cleanup_schedules[env_id]

        return {
            'cleanup_id': cleanup_id,
            'env_id': env_id,
            'reason': reason,
            'resources_freed': env['resources'],
            'success': True,
            'cleaned_at': datetime.utcnow().isoformat()
        }

    def schedule_cleanup(
        self,
        env_id: str,
        cleanup_at: str,
        reason: str = 'scheduled'
    ) -> Dict[str, Any]:
        """
        Schedule environment cleanup.

        Args:
            env_id: Environment identifier
            cleanup_at: ISO format cleanup time
            reason: Cleanup reason

        Returns:
            Dictionary with schedule result

        Example:
            >>> result = service.schedule_cleanup('env_123', '2024-01-20T00:00:00')
        """
        schedule_id = str(uuid.uuid4())

        if env_id not in self._environments:
            return {
                'schedule_id': schedule_id,
                'success': False,
                'error': 'Environment not found',
                'scheduled_at': datetime.utcnow().isoformat()
            }

        self._cleanup_schedules[env_id] = {
            'schedule_id': schedule_id,
            'scheduled_at': cleanup_at,
            'reason': reason
        }

        # Update environment expiry
        self._environments[env_id]['expires_at'] = cleanup_at

        return {
            'schedule_id': schedule_id,
            'env_id': env_id,
            'cleanup_at': cleanup_at,
            'reason': reason,
            'success': True,
            'scheduled_at': datetime.utcnow().isoformat()
        }

    def cleanup_expired_environments(self) -> Dict[str, Any]:
        """
        Clean up all expired environments.

        Returns:
            Dictionary with cleanup results

        Example:
            >>> result = service.cleanup_expired_environments()
        """
        cleanup_id = str(uuid.uuid4())

        now = datetime.utcnow()
        cleaned = []
        failed = []

        for env_id, env in list(self._environments.items()):
            expires_at = datetime.fromisoformat(env['expires_at'].replace('Z', ''))
            if expires_at <= now:
                try:
                    del self._environments[env_id]
                    if env_id in self._cleanup_schedules:
                        del self._cleanup_schedules[env_id]
                    cleaned.append(env_id)
                except Exception as e:
                    failed.append({'env_id': env_id, 'error': str(e)})

        return {
            'cleanup_id': cleanup_id,
            'cleaned_count': len(cleaned),
            'cleaned_environments': cleaned,
            'failed_count': len(failed),
            'failed': failed,
            'cleaned_at': datetime.utcnow().isoformat()
        }

    def allocate_resources(
        self,
        env_id: str,
        resources: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Allocate resources for an environment.

        Args:
            env_id: Environment identifier
            resources: Resource specifications

        Returns:
            Dictionary with allocation result

        Example:
            >>> result = service.allocate_resources('env_123', {'cpu': '1', 'memory': '1Gi'})
        """
        allocation_id = str(uuid.uuid4())

        if env_id not in self._environments:
            return {
                'allocation_id': allocation_id,
                'success': False,
                'error': 'Environment not found',
                'allocated_at': datetime.utcnow().isoformat()
            }

        # Update resources
        self._environments[env_id]['resources'] = resources

        return {
            'allocation_id': allocation_id,
            'env_id': env_id,
            'resources': resources,
            'success': True,
            'allocated_at': datetime.utcnow().isoformat()
        }

    def get_resource_usage(
        self,
        env_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get resource usage for environments.

        Args:
            env_id: Optional specific environment

        Returns:
            Dictionary with resource usage

        Example:
            >>> usage = service.get_resource_usage('env_123')
        """
        query_id = str(uuid.uuid4())

        if env_id:
            if env_id not in self._environments:
                return {
                    'query_id': query_id,
                    'found': False,
                    'error': 'Environment not found',
                    'queried_at': datetime.utcnow().isoformat()
                }

            env = self._environments[env_id]
            usage = [{
                'env_id': env_id,
                'resources': env['resources'],
                'status': env['status']
            }]
        else:
            usage = [
                {
                    'env_id': eid,
                    'resources': env['resources'],
                    'status': env['status']
                }
                for eid, env in self._environments.items()
            ]

        return {
            'query_id': query_id,
            'usage': usage,
            'environment_count': len(usage),
            'queried_at': datetime.utcnow().isoformat()
        }

    def get_environment_status(
        self,
        env_id: str
    ) -> Dict[str, Any]:
        """
        Get status of an environment.

        Args:
            env_id: Environment identifier

        Returns:
            Dictionary with environment status

        Example:
            >>> status = service.get_environment_status('env_123')
        """
        query_id = str(uuid.uuid4())

        if env_id not in self._environments:
            return {
                'query_id': query_id,
                'found': False,
                'error': 'Environment not found',
                'queried_at': datetime.utcnow().isoformat()
            }

        env = self._environments[env_id]

        return {
            'query_id': query_id,
            'env_id': env_id,
            'status': env['status'],
            'url': env['url'],
            'pr_number': env['pr_number'],
            'created_at': env['created_at'],
            'expires_at': env['expires_at'],
            'resources': env['resources'],
            'found': True,
            'queried_at': datetime.utcnow().isoformat()
        }

    def list_environments(
        self,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List all environments.

        Args:
            status: Optional status filter

        Returns:
            Dictionary with environment list

        Example:
            >>> envs = service.list_environments('running')
        """
        query_id = str(uuid.uuid4())

        if status:
            environments = [
                {
                    'env_id': eid,
                    'pr_number': env['pr_number'],
                    'url': env['url'],
                    'status': env['status'],
                    'created_at': env['created_at'],
                    'expires_at': env['expires_at']
                }
                for eid, env in self._environments.items()
                if env['status'] == status
            ]
        else:
            environments = [
                {
                    'env_id': eid,
                    'pr_number': env['pr_number'],
                    'url': env['url'],
                    'status': env['status'],
                    'created_at': env['created_at'],
                    'expires_at': env['expires_at']
                }
                for eid, env in self._environments.items()
            ]

        return {
            'query_id': query_id,
            'environments': environments,
            'environment_count': len(environments),
            'queried_at': datetime.utcnow().isoformat()
        }

    def get_ephemeral_config(self) -> Dict[str, Any]:
        """
        Get ephemeral environments configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_ephemeral_config()
        """
        return {
            'default_ttl_hours': self._default_ttl_hours,
            'max_environments': self._max_environments,
            'active_environments': len(self._environments),
            'scheduled_cleanups': len(self._cleanup_schedules),
            'features': [
                'pr_preview', 'auto_cleanup', 'resource_isolation',
                'ttl_management', 'resource_allocation'
            ]
        }
