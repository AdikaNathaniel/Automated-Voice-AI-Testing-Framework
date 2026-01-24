"""
API Versioning Service for voice AI testing.

This service provides API versioning capabilities including
version management, deprecation policies, and migration guides.

Key features:
- Version registration and management
- Deprecation policy enforcement
- Migration guide generation

Example:
    >>> service = APIVersioningService()
    >>> result = service.register_version('v1')
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid


class APIVersioningService:
    """
    Service for API version management.

    Provides version registration, deprecation
    policies, and migration guides.

    Example:
        >>> service = APIVersioningService()
        >>> config = service.get_versioning_config()
    """

    def __init__(self):
        """Initialize the API versioning service."""
        self._versions: Dict[str, Dict[str, Any]] = {}
        self._migration_guides: List[Dict[str, Any]] = []
        self._current_version: str = 'v1'
        self._deprecation_period_days: int = 180

    def register_version(
        self,
        version: str,
        release_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register a new API version.

        Args:
            version: Version identifier (e.g., 'v1', 'v2')
            release_date: Optional release date

        Returns:
            Dictionary with registration result

        Example:
            >>> result = service.register_version('v2')
        """
        version_id = str(uuid.uuid4())

        self._versions[version] = {
            'id': version_id,
            'version': version,
            'status': 'active',
            'release_date': release_date or datetime.utcnow().isoformat(),
            'deprecation_date': None,
            'sunset_date': None
        }

        return {
            'version_id': version_id,
            'version': version,
            'status': 'registered',
            'registered_at': datetime.utcnow().isoformat()
        }

    def get_version(
        self,
        version: str
    ) -> Dict[str, Any]:
        """
        Get version information.

        Args:
            version: Version identifier

        Returns:
            Dictionary with version info

        Example:
            >>> info = service.get_version('v1')
        """
        ver_info = self._versions.get(version)
        if not ver_info:
            return {
                'version': version,
                'status': 'not_found',
                'retrieved_at': datetime.utcnow().isoformat()
            }

        return {
            **ver_info,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def deprecate_version(
        self,
        version: str,
        sunset_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Mark a version as deprecated.

        Args:
            version: Version to deprecate
            sunset_days: Days until sunset

        Returns:
            Dictionary with deprecation result

        Example:
            >>> result = service.deprecate_version('v1')
        """
        if version not in self._versions:
            return {
                'version': version,
                'status': 'error',
                'error': 'Version not found',
                'deprecated_at': datetime.utcnow().isoformat()
            }

        if sunset_days is None:
            sunset_days = self._deprecation_period_days

        now = datetime.utcnow()
        sunset_date = now + timedelta(days=sunset_days)

        self._versions[version]['status'] = 'deprecated'
        self._versions[version]['deprecation_date'] = now.isoformat()
        self._versions[version]['sunset_date'] = sunset_date.isoformat()

        return {
            'version': version,
            'status': 'deprecated',
            'sunset_date': sunset_date.isoformat(),
            'deprecated_at': now.isoformat()
        }

    def get_deprecation_notice(
        self,
        version: str
    ) -> Dict[str, Any]:
        """
        Get deprecation notice for a version.

        Args:
            version: Version identifier

        Returns:
            Dictionary with deprecation notice

        Example:
            >>> notice = service.get_deprecation_notice('v1')
        """
        ver_info = self._versions.get(version)
        if not ver_info or ver_info['status'] != 'deprecated':
            return {
                'version': version,
                'deprecated': False,
                'notice': None,
                'retrieved_at': datetime.utcnow().isoformat()
            }

        return {
            'version': version,
            'deprecated': True,
            'notice': f"API version {version} is deprecated",
            'sunset_date': ver_info['sunset_date'],
            'migration_recommended': self._current_version,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def create_migration_guide(
        self,
        from_version: str,
        to_version: str,
        breaking_changes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a migration guide between versions.

        Args:
            from_version: Source version
            to_version: Target version
            breaking_changes: List of breaking changes

        Returns:
            Dictionary with migration guide

        Example:
            >>> guide = service.create_migration_guide('v1', 'v2')
        """
        guide_id = str(uuid.uuid4())

        guide = {
            'guide_id': guide_id,
            'from_version': from_version,
            'to_version': to_version,
            'breaking_changes': breaking_changes or [],
            'steps': [],
            'created_at': datetime.utcnow().isoformat()
        }

        self._migration_guides.append(guide)

        return guide

    def get_migration_path(
        self,
        from_version: str,
        to_version: str
    ) -> Dict[str, Any]:
        """
        Get migration path between versions.

        Args:
            from_version: Source version
            to_version: Target version

        Returns:
            Dictionary with migration path

        Example:
            >>> path = service.get_migration_path('v1', 'v3')
        """
        path_id = str(uuid.uuid4())

        # Find applicable guides
        applicable_guides = [
            g for g in self._migration_guides
            if g['from_version'] == from_version
        ]

        return {
            'path_id': path_id,
            'from_version': from_version,
            'to_version': to_version,
            'guides': applicable_guides,
            'direct_path_available': len(applicable_guides) > 0,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def get_versioning_config(self) -> Dict[str, Any]:
        """
        Get versioning configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_versioning_config()
        """
        return {
            'current_version': self._current_version,
            'total_versions': len(self._versions),
            'deprecation_period_days': self._deprecation_period_days,
            'total_migration_guides': len(self._migration_guides),
            'version_format': '/api/v{n}/',
            'supported_versions': list(self._versions.keys())
        }
