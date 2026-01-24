"""
Data Retention Service for voice AI.

This service manages data retention policies, deletion jobs,
legal holds, and data export for compliance.

Key features:
- Configurable retention periods
- Automatic data deletion jobs
- Legal hold support
- Data export for deletion requests

Example:
    >>> service = DataRetentionService()
    >>> result = service.set_retention_period('test_runs', 90)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid


class DataRetentionService:
    """
    Service for data retention management.

    Provides retention period configuration, deletion job
    scheduling, legal holds, and data export.

    Example:
        >>> service = DataRetentionService()
        >>> config = service.get_retention_config()
    """

    def __init__(self):
        """Initialize the data retention service."""
        self._retention_periods: Dict[str, int] = {
            'test_runs': 90,
            'audio_files': 30,
            'transcripts': 90,
            'logs': 365,
            'metrics': 180
        }
        self._deletion_jobs: List[Dict[str, Any]] = []
        self._legal_holds: List[Dict[str, Any]] = []
        self._exports: List[Dict[str, Any]] = []

    def set_retention_period(
        self,
        data_type: str,
        days: int
    ) -> Dict[str, Any]:
        """
        Set retention period for a data type.

        Args:
            data_type: Type of data
            days: Number of days to retain

        Returns:
            Dictionary with updated period

        Example:
            >>> result = service.set_retention_period('test_runs', 90)
        """
        old_period = self._retention_periods.get(data_type)
        self._retention_periods[data_type] = days

        return {
            'data_type': data_type,
            'old_period': old_period,
            'new_period': days,
            'updated_at': datetime.utcnow().isoformat()
        }

    def get_retention_periods(self) -> Dict[str, Any]:
        """
        Get all retention periods.

        Returns:
            Dictionary with retention periods

        Example:
            >>> periods = service.get_retention_periods()
        """
        return {
            'periods': self._retention_periods.copy(),
            'units': 'days',
            'data_types': list(self._retention_periods.keys())
        }

    def schedule_deletion(
        self,
        data_type: str,
        criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Schedule a data deletion job.

        Args:
            data_type: Type of data to delete
            criteria: Optional deletion criteria

        Returns:
            Dictionary with job details

        Example:
            >>> job = service.schedule_deletion('audio_files')
        """
        retention_days = self._retention_periods.get(data_type, 90)
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

        job = {
            'job_id': str(uuid.uuid4()),
            'data_type': data_type,
            'status': 'scheduled',
            'cutoff_date': cutoff_date.isoformat(),
            'criteria': criteria or {},
            'scheduled_at': datetime.utcnow().isoformat(),
            'estimated_records': 0
        }

        self._deletion_jobs.append(job)
        return job

    def get_deletion_jobs(
        self,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get deletion jobs.

        Args:
            status: Optional status filter

        Returns:
            List of deletion jobs

        Example:
            >>> jobs = service.get_deletion_jobs('scheduled')
        """
        if status:
            return [j for j in self._deletion_jobs if j['status'] == status]
        return self._deletion_jobs.copy()

    def execute_deletion(
        self,
        job_id: str
    ) -> Dict[str, Any]:
        """
        Execute a deletion job.

        Args:
            job_id: ID of job to execute

        Returns:
            Dictionary with execution result

        Example:
            >>> result = service.execute_deletion(job_id)
        """
        job = None
        for j in self._deletion_jobs:
            if j['job_id'] == job_id:
                job = j
                break

        if not job:
            return {
                'success': False,
                'error': f'Job {job_id} not found'
            }

        # Check for legal holds
        for hold in self._legal_holds:
            if hold['data_type'] == job['data_type'] and hold['active']:
                return {
                    'success': False,
                    'error': 'Data under legal hold',
                    'hold_id': hold['hold_id']
                }

        job['status'] = 'completed'
        job['completed_at'] = datetime.utcnow().isoformat()
        job['records_deleted'] = 0  # Simulated

        return {
            'success': True,
            'job_id': job_id,
            'records_deleted': job['records_deleted'],
            'completed_at': job['completed_at']
        }

    def set_legal_hold(
        self,
        data_type: str,
        reason: str,
        case_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Set legal hold on data type.

        Args:
            data_type: Type of data to hold
            reason: Reason for hold
            case_id: Optional case identifier

        Returns:
            Dictionary with hold details

        Example:
            >>> hold = service.set_legal_hold('audio_files', 'Litigation')
        """
        hold = {
            'hold_id': str(uuid.uuid4()),
            'data_type': data_type,
            'reason': reason,
            'case_id': case_id,
            'active': True,
            'created_at': datetime.utcnow().isoformat(),
            'created_by': 'system'
        }

        self._legal_holds.append(hold)
        return hold

    def get_legal_holds(
        self,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get legal holds.

        Args:
            active_only: Only return active holds

        Returns:
            List of legal holds

        Example:
            >>> holds = service.get_legal_holds()
        """
        if active_only:
            return [h for h in self._legal_holds if h['active']]
        return self._legal_holds.copy()

    def release_legal_hold(
        self,
        hold_id: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        Release a legal hold.

        Args:
            hold_id: ID of hold to release
            reason: Reason for release

        Returns:
            Dictionary with release result

        Example:
            >>> result = service.release_legal_hold(hold_id, 'Case closed')
        """
        for hold in self._legal_holds:
            if hold['hold_id'] == hold_id:
                hold['active'] = False
                hold['released_at'] = datetime.utcnow().isoformat()
                hold['release_reason'] = reason

                return {
                    'success': True,
                    'hold_id': hold_id,
                    'released_at': hold['released_at']
                }

        return {
            'success': False,
            'error': f'Hold {hold_id} not found'
        }

    def export_user_data(
        self,
        user_id: str,
        data_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Export user data for deletion request.

        Args:
            user_id: ID of user
            data_types: Optional specific data types

        Returns:
            Dictionary with export details

        Example:
            >>> export = service.export_user_data('user123')
        """
        if data_types is None:
            data_types = list(self._retention_periods.keys())

        export = {
            'export_id': str(uuid.uuid4()),
            'user_id': user_id,
            'data_types': data_types,
            'status': 'processing',
            'requested_at': datetime.utcnow().isoformat(),
            'format': 'json',
            'estimated_size': '0 MB'
        }

        self._exports.append(export)
        return export

    def get_export_status(
        self,
        export_id: str
    ) -> Dict[str, Any]:
        """
        Get status of data export.

        Args:
            export_id: ID of export

        Returns:
            Dictionary with export status

        Example:
            >>> status = service.get_export_status(export_id)
        """
        for export in self._exports:
            if export['export_id'] == export_id:
                return {
                    'export_id': export_id,
                    'status': export['status'],
                    'user_id': export['user_id'],
                    'requested_at': export['requested_at'],
                    'download_url': None
                }

        return {
            'export_id': export_id,
            'status': 'not_found',
            'error': f'Export {export_id} not found'
        }

    def get_retention_config(self) -> Dict[str, Any]:
        """
        Get retention service configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_retention_config()
        """
        return {
            'retention_periods': self._retention_periods.copy(),
            'active_holds': len([h for h in self._legal_holds if h['active']]),
            'pending_deletions': len([j for j in self._deletion_jobs if j['status'] == 'scheduled']),
            'pending_exports': len([e for e in self._exports if e['status'] == 'processing'])
        }
