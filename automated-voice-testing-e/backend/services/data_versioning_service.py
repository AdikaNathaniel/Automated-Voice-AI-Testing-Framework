"""
Test Data Versioning Service for voice AI testing.

This service manages test data versioning including version control,
dataset versioning, golden datasets, and comparison tools.

Key features:
- Test case version control
- Dataset versioning (DVC integration)
- Golden dataset management
- Dataset comparison tools

Example:
    >>> service = DataVersioningService()
    >>> version = service.create_version(test_case_id, data)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import hashlib


class DataVersioningService:
    """
    Service for test data versioning.

    Provides version control, dataset management,
    golden datasets, and comparison tools.

    Example:
        >>> service = DataVersioningService()
        >>> config = service.get_versioning_config()
    """

    def __init__(self):
        """Initialize the data versioning service."""
        self._versions: Dict[str, List[Dict[str, Any]]] = {}
        self._datasets: Dict[str, Dict[str, Any]] = {}
        self._golden_datasets: Dict[str, str] = {}

    def create_version(
        self,
        entity_id: str,
        data: Dict[str, Any],
        message: str = ''
    ) -> Dict[str, Any]:
        """
        Create a new version for an entity.

        Args:
            entity_id: ID of entity (test case, dataset)
            data: Data to version
            message: Version message

        Returns:
            Dictionary with version details

        Example:
            >>> version = service.create_version('tc_1', data, 'Initial')
        """
        version_id = str(uuid.uuid4())
        data_hash = hashlib.sha256(str(data).encode()).hexdigest()[:16]

        if entity_id not in self._versions:
            self._versions[entity_id] = []

        version_number = len(self._versions[entity_id]) + 1

        version = {
            'version_id': version_id,
            'entity_id': entity_id,
            'version_number': version_number,
            'data': data,
            'hash': data_hash,
            'message': message,
            'created_at': datetime.utcnow().isoformat()
        }

        self._versions[entity_id].append(version)
        return version

    def get_versions(
        self,
        entity_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all versions for an entity.

        Args:
            entity_id: ID of entity

        Returns:
            List of versions

        Example:
            >>> versions = service.get_versions('tc_1')
        """
        if entity_id not in self._versions:
            return []

        return [
            {
                'version_id': v['version_id'],
                'version_number': v['version_number'],
                'hash': v['hash'],
                'message': v['message'],
                'created_at': v['created_at']
            }
            for v in self._versions[entity_id]
        ]

    def restore_version(
        self,
        entity_id: str,
        version_id: str
    ) -> Dict[str, Any]:
        """
        Restore entity to a specific version.

        Args:
            entity_id: ID of entity
            version_id: ID of version to restore

        Returns:
            Dictionary with restore result

        Example:
            >>> result = service.restore_version('tc_1', 'v_123')
        """
        if entity_id not in self._versions:
            return {
                'success': False,
                'error': f'Entity {entity_id} not found'
            }

        for version in self._versions[entity_id]:
            if version['version_id'] == version_id:
                return {
                    'success': True,
                    'entity_id': entity_id,
                    'restored_version': version_id,
                    'data': version['data'],
                    'restored_at': datetime.utcnow().isoformat()
                }

        return {
            'success': False,
            'error': f'Version {version_id} not found'
        }

    def register_dataset(
        self,
        name: str,
        path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Register a dataset for versioning.

        Args:
            name: Dataset name
            path: Path to dataset
            metadata: Optional metadata

        Returns:
            Dictionary with dataset details

        Example:
            >>> dataset = service.register_dataset('Training', '/data/train')
        """
        dataset_id = str(uuid.uuid4())

        dataset = {
            'dataset_id': dataset_id,
            'name': name,
            'path': path,
            'metadata': metadata or {},
            'versions': [],
            'created_at': datetime.utcnow().isoformat()
        }

        self._datasets[dataset_id] = dataset
        return dataset

    def get_dataset_versions(
        self,
        dataset_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get versions for a dataset.

        Args:
            dataset_id: ID of dataset

        Returns:
            List of dataset versions

        Example:
            >>> versions = service.get_dataset_versions('ds_1')
        """
        if dataset_id not in self._datasets:
            return []

        return self._datasets[dataset_id].get('versions', [])

    def set_golden_dataset(
        self,
        name: str,
        dataset_id: str,
        version_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Set a dataset as golden (reference) dataset.

        Args:
            name: Golden dataset name
            dataset_id: ID of dataset
            version_id: Optional specific version

        Returns:
            Dictionary with golden dataset details

        Example:
            >>> result = service.set_golden_dataset('Gold_V1', 'ds_1')
        """
        self._golden_datasets[name] = dataset_id

        return {
            'name': name,
            'dataset_id': dataset_id,
            'version_id': version_id,
            'set_at': datetime.utcnow().isoformat()
        }

    def get_golden_datasets(self) -> List[Dict[str, Any]]:
        """
        Get all golden datasets.

        Returns:
            List of golden datasets

        Example:
            >>> golden = service.get_golden_datasets()
        """
        return [
            {
                'name': name,
                'dataset_id': dataset_id
            }
            for name, dataset_id in self._golden_datasets.items()
        ]

    def compare_datasets(
        self,
        dataset_id_1: str,
        dataset_id_2: str
    ) -> Dict[str, Any]:
        """
        Compare two datasets.

        Args:
            dataset_id_1: First dataset ID
            dataset_id_2: Second dataset ID

        Returns:
            Dictionary with comparison result

        Example:
            >>> result = service.compare_datasets('ds_1', 'ds_2')
        """
        ds1 = self._datasets.get(dataset_id_1, {})
        ds2 = self._datasets.get(dataset_id_2, {})

        return {
            'dataset_1': dataset_id_1,
            'dataset_2': dataset_id_2,
            'identical': ds1 == ds2,
            'differences': {
                'name': ds1.get('name') != ds2.get('name'),
                'path': ds1.get('path') != ds2.get('path')
            },
            'compared_at': datetime.utcnow().isoformat()
        }

    def get_diff(
        self,
        entity_id: str,
        version_id_1: str,
        version_id_2: str
    ) -> Dict[str, Any]:
        """
        Get diff between two versions.

        Args:
            entity_id: ID of entity
            version_id_1: First version ID
            version_id_2: Second version ID

        Returns:
            Dictionary with diff result

        Example:
            >>> diff = service.get_diff('tc_1', 'v_1', 'v_2')
        """
        if entity_id not in self._versions:
            return {
                'error': f'Entity {entity_id} not found'
            }

        v1_data = None
        v2_data = None

        for version in self._versions[entity_id]:
            if version['version_id'] == version_id_1:
                v1_data = version['data']
            if version['version_id'] == version_id_2:
                v2_data = version['data']

        return {
            'entity_id': entity_id,
            'version_1': version_id_1,
            'version_2': version_id_2,
            'has_changes': v1_data != v2_data,
            'diff_at': datetime.utcnow().isoformat()
        }

    def get_versioning_config(self) -> Dict[str, Any]:
        """
        Get versioning configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_versioning_config()
        """
        total_versions = sum(
            len(versions) for versions in self._versions.values()
        )

        return {
            'total_entities': len(self._versions),
            'total_versions': total_versions,
            'total_datasets': len(self._datasets),
            'total_golden_datasets': len(self._golden_datasets),
            'supported_operations': [
                'create_version',
                'restore_version',
                'compare',
                'diff'
            ]
        }
