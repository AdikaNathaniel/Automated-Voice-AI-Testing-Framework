"""
GDPR Compliance Service for voice AI.

This service manages GDPR compliance requirements including
consent, erasure, data portability, and processing records.

Key features:
- Consent management integration
- Right to erasure implementation
- Data portability export
- Processing records

Example:
    >>> service = GDPRService()
    >>> result = service.record_consent(user_id, purposes)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class GDPRService:
    """
    Service for GDPR compliance management.

    Provides consent management, erasure requests,
    data portability, and processing records.

    Example:
        >>> service = GDPRService()
        >>> config = service.get_gdpr_config()
    """

    def __init__(self):
        """Initialize the GDPR service."""
        self._consents: Dict[str, Dict[str, Any]] = {}
        self._erasure_requests: List[Dict[str, Any]] = []
        self._processing_records: List[Dict[str, Any]] = []
        self._exports: List[Dict[str, Any]] = []

    def record_consent(
        self,
        user_id: str,
        purposes: List[str],
        source: str = 'web'
    ) -> Dict[str, Any]:
        """
        Record user consent for data processing.

        Args:
            user_id: ID of user
            purposes: List of consent purposes
            source: Source of consent

        Returns:
            Dictionary with consent record

        Example:
            >>> result = service.record_consent('user123', ['analytics'])
        """
        consent_record = {
            'consent_id': str(uuid.uuid4()),
            'user_id': user_id,
            'purposes': purposes,
            'source': source,
            'granted_at': datetime.utcnow().isoformat(),
            'active': True,
            'version': '1.0'
        }

        self._consents[user_id] = consent_record
        return consent_record

    def get_consent_status(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get consent status for user.

        Args:
            user_id: ID of user

        Returns:
            Dictionary with consent status

        Example:
            >>> status = service.get_consent_status('user123')
        """
        if user_id in self._consents:
            consent = self._consents[user_id]
            return {
                'user_id': user_id,
                'has_consent': consent['active'],
                'purposes': consent['purposes'],
                'granted_at': consent['granted_at'],
                'consent_id': consent['consent_id']
            }

        return {
            'user_id': user_id,
            'has_consent': False,
            'purposes': [],
            'granted_at': None
        }

    def revoke_consent(
        self,
        user_id: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Revoke user consent.

        Args:
            user_id: ID of user
            reason: Optional revocation reason

        Returns:
            Dictionary with revocation result

        Example:
            >>> result = service.revoke_consent('user123')
        """
        if user_id in self._consents:
            self._consents[user_id]['active'] = False
            self._consents[user_id]['revoked_at'] = datetime.utcnow().isoformat()
            self._consents[user_id]['revocation_reason'] = reason

            return {
                'success': True,
                'user_id': user_id,
                'revoked_at': self._consents[user_id]['revoked_at']
            }

        return {
            'success': False,
            'error': f'No consent found for user {user_id}'
        }

    def request_erasure(
        self,
        user_id: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        Request right to erasure (right to be forgotten).

        Args:
            user_id: ID of user
            reason: Reason for erasure request

        Returns:
            Dictionary with request details

        Example:
            >>> request = service.request_erasure('user123', 'User request')
        """
        request = {
            'request_id': str(uuid.uuid4()),
            'user_id': user_id,
            'reason': reason,
            'status': 'pending',
            'requested_at': datetime.utcnow().isoformat(),
            'deadline': None,  # 30 days from request
            'data_types': ['all']
        }

        self._erasure_requests.append(request)
        return request

    def execute_erasure(
        self,
        request_id: str
    ) -> Dict[str, Any]:
        """
        Execute erasure request.

        Args:
            request_id: ID of erasure request

        Returns:
            Dictionary with execution result

        Example:
            >>> result = service.execute_erasure(request_id)
        """
        for request in self._erasure_requests:
            if request['request_id'] == request_id:
                request['status'] = 'completed'
                request['completed_at'] = datetime.utcnow().isoformat()

                # Remove consent record
                if request['user_id'] in self._consents:
                    del self._consents[request['user_id']]

                return {
                    'success': True,
                    'request_id': request_id,
                    'user_id': request['user_id'],
                    'completed_at': request['completed_at']
                }

        return {
            'success': False,
            'error': f'Request {request_id} not found'
        }

    def get_erasure_status(
        self,
        request_id: str
    ) -> Dict[str, Any]:
        """
        Get status of erasure request.

        Args:
            request_id: ID of erasure request

        Returns:
            Dictionary with request status

        Example:
            >>> status = service.get_erasure_status(request_id)
        """
        for request in self._erasure_requests:
            if request['request_id'] == request_id:
                return {
                    'request_id': request_id,
                    'user_id': request['user_id'],
                    'status': request['status'],
                    'requested_at': request['requested_at'],
                    'completed_at': request.get('completed_at')
                }

        return {
            'request_id': request_id,
            'status': 'not_found',
            'error': f'Request {request_id} not found'
        }

    def export_portable_data(
        self,
        user_id: str,
        format: str = 'json'
    ) -> Dict[str, Any]:
        """
        Export user data in portable format.

        Args:
            user_id: ID of user
            format: Export format

        Returns:
            Dictionary with export details

        Example:
            >>> export = service.export_portable_data('user123', 'json')
        """
        export = {
            'export_id': str(uuid.uuid4()),
            'user_id': user_id,
            'format': format,
            'status': 'processing',
            'requested_at': datetime.utcnow().isoformat(),
            'data_categories': [
                'profile',
                'test_runs',
                'audio_files',
                'transcripts',
                'preferences'
            ]
        }

        self._exports.append(export)
        return export

    def get_export_formats(self) -> List[Dict[str, Any]]:
        """
        Get supported export formats.

        Returns:
            List of export formats

        Example:
            >>> formats = service.get_export_formats()
        """
        return [
            {
                'format': 'json',
                'description': 'JSON format (machine-readable)',
                'mime_type': 'application/json'
            },
            {
                'format': 'csv',
                'description': 'CSV format (spreadsheet-compatible)',
                'mime_type': 'text/csv'
            },
            {
                'format': 'xml',
                'description': 'XML format',
                'mime_type': 'application/xml'
            }
        ]

    def log_processing(
        self,
        user_id: str,
        activity: str,
        purpose: str,
        legal_basis: str = 'consent'
    ) -> Dict[str, Any]:
        """
        Log data processing activity.

        Args:
            user_id: ID of user
            activity: Processing activity
            purpose: Purpose of processing
            legal_basis: Legal basis for processing

        Returns:
            Dictionary with log entry

        Example:
            >>> log = service.log_processing('user123', 'analysis', 'testing')
        """
        record = {
            'record_id': str(uuid.uuid4()),
            'user_id': user_id,
            'activity': activity,
            'purpose': purpose,
            'legal_basis': legal_basis,
            'timestamp': datetime.utcnow().isoformat(),
            'data_controller': 'VoiceAI Testing'
        }

        self._processing_records.append(record)
        return record

    def get_processing_records(
        self,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get processing records.

        Args:
            user_id: Optional user ID filter
            limit: Maximum records to return

        Returns:
            List of processing records

        Example:
            >>> records = service.get_processing_records('user123')
        """
        records = self._processing_records.copy()

        if user_id:
            records = [r for r in records if r['user_id'] == user_id]

        records.sort(key=lambda x: x['timestamp'], reverse=True)
        return records[:limit]

    def get_gdpr_config(self) -> Dict[str, Any]:
        """
        Get GDPR service configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_gdpr_config()
        """
        return {
            'consent_version': '1.0',
            'erasure_deadline_days': 30,
            'export_formats': ['json', 'csv', 'xml'],
            'total_consents': len(self._consents),
            'pending_erasures': len([r for r in self._erasure_requests if r['status'] == 'pending']),
            'total_processing_records': len(self._processing_records)
        }
