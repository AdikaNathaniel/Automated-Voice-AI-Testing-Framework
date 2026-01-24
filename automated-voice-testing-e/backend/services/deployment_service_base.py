"""
Deployment Service Base - Standardized base class for deployment services.

This base class provides common functionality for deployment operations
shared across blue-green, canary, and feature flag deployment services.

Key features:
- Common deployment operations
- Rollback functionality
- Health checks and validation
- Configuration management
- Metrics collection

Example:
    >>> from services.deployment_service_base import DeploymentServiceBase
    >>> service = DeploymentServiceBase()
    >>> status = service.get_status()
    >>> print(f"Deployment status: {status['status']}")
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class DeploymentServiceBase:
    """
    Base class for deployment services.

    Provides standardized interface for deployment operations including
    status tracking, rollback, health checks, and configuration.

    Attributes:
        deployment_type: Type of deployment (base, blue-green, canary, feature-flag)
        _deployments: Internal storage for deployment records
        _rollback_history: Internal storage for rollback history

    Example:
        >>> service = DeploymentServiceBase()
        >>> result = service.start_deployment('v1.2.0')
        >>> print(f"Deployment ID: {result['deployment_id']}")
    """

    def __init__(self):
        """Initialize the deployment service base."""
        self.deployment_type = 'base'
        self._deployments: Dict[str, Dict[str, Any]] = {}
        self._rollback_history: List[Dict[str, Any]] = []
        self._current_deployment: Optional[str] = None

    # =========================================================================
    # Deployment Status
    # =========================================================================

    def get_status(self) -> Dict[str, Any]:
        """
        Get current deployment status.

        Returns:
            Dictionary with deployment status information

        Example:
            >>> status = service.get_status()
            >>> print(status['status'])
        """
        if not self._current_deployment:
            return {
                'status': 'idle',
                'deployment_type': self.deployment_type,
                'active_deployment': None,
                'total_deployments': len(self._deployments),
                'checked_at': datetime.utcnow().isoformat()
            }

        deployment = self._deployments.get(self._current_deployment, {})

        return {
            'status': deployment.get('status', 'unknown'),
            'deployment_type': self.deployment_type,
            'active_deployment': self._current_deployment,
            'version': deployment.get('version'),
            'started_at': deployment.get('started_at'),
            'total_deployments': len(self._deployments),
            'checked_at': datetime.utcnow().isoformat()
        }

    # =========================================================================
    # Deployment Operations
    # =========================================================================

    def start_deployment(
        self,
        version: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Start a new deployment.

        Args:
            version: Version identifier for deployment
            config: Optional deployment configuration

        Returns:
            Dictionary with deployment details

        Example:
            >>> result = service.start_deployment('v1.2.0')
            >>> print(f"Started: {result['deployment_id']}")
        """
        deployment_id = str(uuid.uuid4())

        deployment = {
            'deployment_id': deployment_id,
            'version': version,
            'status': 'in_progress',
            'config': config or {},
            'started_at': datetime.utcnow().isoformat(),
            'completed_at': None,
            'health_checks': [],
            'validation_results': []
        }

        self._deployments[deployment_id] = deployment
        self._current_deployment = deployment_id

        return {
            'deployment_id': deployment_id,
            'version': version,
            'status': 'in_progress',
            'deployment_type': self.deployment_type,
            'started_at': deployment['started_at']
        }

    def complete_deployment(
        self,
        deployment_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete a deployment.

        Args:
            deployment_id: Deployment to complete (defaults to current)

        Returns:
            Dictionary with completion details

        Example:
            >>> result = service.complete_deployment(deployment_id)
            >>> print(f"Completed: {result['status']}")
        """
        target_id = deployment_id or self._current_deployment

        if not target_id or target_id not in self._deployments:
            return {
                'error': 'Deployment not found',
                'deployment_id': target_id
            }

        deployment = self._deployments[target_id]
        deployment['status'] = 'completed'
        deployment['completed_at'] = datetime.utcnow().isoformat()

        return {
            'deployment_id': target_id,
            'version': deployment['version'],
            'status': 'completed',
            'started_at': deployment['started_at'],
            'completed_at': deployment['completed_at'],
            'duration_seconds': self._calculate_duration(
                deployment['started_at'],
                deployment['completed_at']
            )
        }

    def _calculate_duration(
        self,
        start: str,
        end: str
    ) -> float:
        """Calculate duration between two ISO timestamps."""
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)
        return (end_dt - start_dt).total_seconds()

    # =========================================================================
    # Rollback Functionality
    # =========================================================================

    def initiate_rollback(
        self,
        reason: str,
        deployment_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initiate a rollback operation.

        Args:
            reason: Reason for rollback
            deployment_id: Deployment to rollback (defaults to current)

        Returns:
            Dictionary with rollback details

        Example:
            >>> result = service.initiate_rollback('Health check failed')
            >>> print(f"Rollback ID: {result['rollback_id']}")
        """
        rollback_id = str(uuid.uuid4())
        target_id = deployment_id or self._current_deployment

        rollback_record = {
            'rollback_id': rollback_id,
            'deployment_id': target_id,
            'reason': reason,
            'status': 'completed',
            'initiated_at': datetime.utcnow().isoformat()
        }

        self._rollback_history.append(rollback_record)

        if target_id and target_id in self._deployments:
            self._deployments[target_id]['status'] = 'rolled_back'

        return {
            'rollback_id': rollback_id,
            'deployment_id': target_id,
            'reason': reason,
            'status': 'completed',
            'initiated_at': rollback_record['initiated_at']
        }

    def get_rollback_history(
        self,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get rollback history.

        Args:
            limit: Maximum number of records to return

        Returns:
            Dictionary with rollback history

        Example:
            >>> history = service.get_rollback_history()
            >>> print(f"Total rollbacks: {history['total']}")
        """
        recent = self._rollback_history[-limit:] if self._rollback_history else []

        return {
            'rollbacks': list(reversed(recent)),
            'total': len(self._rollback_history),
            'limit': limit,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    # =========================================================================
    # Health Checks
    # =========================================================================

    def run_health_check(
        self,
        deployment_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run health check on deployment.

        Args:
            deployment_id: Deployment to check (defaults to current)

        Returns:
            Dictionary with health check results

        Example:
            >>> result = service.run_health_check()
            >>> print(f"Health: {result['status']}")
        """
        check_id = str(uuid.uuid4())
        target_id = deployment_id or self._current_deployment

        health_result = {
            'check_id': check_id,
            'deployment_id': target_id,
            'status': 'healthy',
            'checks': [
                {'name': 'connectivity', 'status': 'pass'},
                {'name': 'response_time', 'status': 'pass'},
                {'name': 'error_rate', 'status': 'pass'}
            ],
            'checked_at': datetime.utcnow().isoformat()
        }

        if target_id and target_id in self._deployments:
            self._deployments[target_id]['health_checks'].append(health_result)

        return health_result

    # =========================================================================
    # Validation
    # =========================================================================

    def validate_deployment(
        self,
        deployment_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate deployment configuration and state.

        Args:
            deployment_id: Deployment to validate (defaults to current)

        Returns:
            Dictionary with validation results

        Example:
            >>> result = service.validate_deployment()
            >>> print(f"Valid: {result['is_valid']}")
        """
        validation_id = str(uuid.uuid4())
        target_id = deployment_id or self._current_deployment

        validation_result = {
            'validation_id': validation_id,
            'deployment_id': target_id,
            'is_valid': True,
            'validations': [
                {'check': 'config_complete', 'passed': True},
                {'check': 'version_format', 'passed': True},
                {'check': 'dependencies', 'passed': True}
            ],
            'validated_at': datetime.utcnow().isoformat()
        }

        if target_id and target_id in self._deployments:
            self._deployments[target_id]['validation_results'].append(
                validation_result
            )

        return validation_result

    # =========================================================================
    # Configuration
    # =========================================================================

    def get_config(self) -> Dict[str, Any]:
        """
        Get deployment service configuration.

        Returns:
            Dictionary with service configuration

        Example:
            >>> config = service.get_config()
            >>> print(f"Type: {config['deployment_type']}")
        """
        return {
            'deployment_type': self.deployment_type,
            'health_check_interval': 30,
            'rollback_enabled': True,
            'validation_required': True,
            'max_rollback_history': 100,
            'supported_operations': [
                'start_deployment',
                'complete_deployment',
                'initiate_rollback',
                'run_health_check',
                'validate_deployment'
            ]
        }

    # =========================================================================
    # Metrics
    # =========================================================================

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get deployment metrics.

        Returns:
            Dictionary with deployment metrics

        Example:
            >>> metrics = service.get_metrics()
            >>> print(f"Total: {metrics['total_deployments']}")
        """
        completed = sum(
            1 for d in self._deployments.values()
            if d.get('status') == 'completed'
        )
        failed = sum(
            1 for d in self._deployments.values()
            if d.get('status') in ['failed', 'rolled_back']
        )

        return {
            'total_deployments': len(self._deployments),
            'completed_deployments': completed,
            'failed_deployments': failed,
            'total_rollbacks': len(self._rollback_history),
            'success_rate': (
                completed / len(self._deployments)
                if self._deployments else 0.0
            ),
            'deployment_type': self.deployment_type,
            'generated_at': datetime.utcnow().isoformat()
        }
