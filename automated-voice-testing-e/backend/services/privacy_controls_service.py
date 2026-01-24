"""
Privacy Controls Service for voice AI testing.

This service provides privacy controls and data management
for voice AI systems including consent, deletion, and portability.

Key features:
- Data collection consent management
- Profile data deletion
- Anonymization options
- Data portability (export/import)

Example:
    >>> service = PrivacyControlsService()
    >>> consent = service.set_consent(user_id='user_123', consent_type='data_collection')
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import json


class PrivacyControlsService:
    """
    Service for privacy controls and data management.

    Provides tools for managing consent, data deletion,
    anonymization, and data portability.

    Example:
        >>> service = PrivacyControlsService()
        >>> config = service.get_privacy_config()
    """

    def __init__(self):
        """Initialize the privacy controls service."""
        self._consents: Dict[str, Dict[str, Any]] = {}
        self._deletion_requests: Dict[str, Dict[str, Any]] = {}
        self._anonymization_settings: Dict[str, Dict[str, Any]] = {}
        self._user_data: Dict[str, Dict[str, Any]] = {}

    def set_consent(
        self,
        user_id: str,
        consent_type: str,
        granted: bool = True,
        scope: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Set data collection consent for a user.

        Args:
            user_id: User identifier
            consent_type: Type of consent
            granted: Whether consent is granted
            scope: Optional scope of consent

        Returns:
            Dictionary with consent result

        Example:
            >>> result = service.set_consent('user_123', 'analytics', True)
        """
        consent_id = str(uuid.uuid4())

        if user_id not in self._consents:
            self._consents[user_id] = {}

        consent = {
            'consent_id': consent_id,
            'type': consent_type,
            'granted': granted,
            'scope': scope or ['all'],
            'set_at': datetime.utcnow().isoformat(),
            'expires_at': None
        }

        self._consents[user_id][consent_type] = consent

        return {
            'consent_id': consent_id,
            'user_id': user_id,
            'consent_type': consent_type,
            'granted': granted,
            'scope': consent['scope'],
            'success': True,
            'set_at': consent['set_at']
        }

    def get_consent_status(
        self,
        user_id: str,
        consent_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get consent status for a user.

        Args:
            user_id: User identifier
            consent_type: Optional specific consent type

        Returns:
            Dictionary with consent status

        Example:
            >>> status = service.get_consent_status('user_123')
        """
        query_id = str(uuid.uuid4())

        if user_id not in self._consents:
            return {
                'query_id': query_id,
                'user_id': user_id,
                'consents': [],
                'has_any_consent': False,
                'queried_at': datetime.utcnow().isoformat()
            }

        user_consents = self._consents[user_id]

        if consent_type:
            if consent_type in user_consents:
                consents = [user_consents[consent_type]]
            else:
                consents = []
        else:
            consents = list(user_consents.values())

        return {
            'query_id': query_id,
            'user_id': user_id,
            'consents': consents,
            'has_any_consent': any(c['granted'] for c in consents),
            'queried_at': datetime.utcnow().isoformat()
        }

    def revoke_consent(
        self,
        user_id: str,
        consent_type: str
    ) -> Dict[str, Any]:
        """
        Revoke previously granted consent.

        Args:
            user_id: User identifier
            consent_type: Type of consent to revoke

        Returns:
            Dictionary with revocation result

        Example:
            >>> result = service.revoke_consent('user_123', 'analytics')
        """
        revocation_id = str(uuid.uuid4())

        if user_id not in self._consents:
            return {
                'revocation_id': revocation_id,
                'success': False,
                'error': 'No consents found for user',
                'revoked_at': datetime.utcnow().isoformat()
            }

        if consent_type not in self._consents[user_id]:
            return {
                'revocation_id': revocation_id,
                'success': False,
                'error': f'Consent type {consent_type} not found',
                'revoked_at': datetime.utcnow().isoformat()
            }

        self._consents[user_id][consent_type]['granted'] = False
        self._consents[user_id][consent_type]['revoked_at'] = datetime.utcnow().isoformat()

        return {
            'revocation_id': revocation_id,
            'user_id': user_id,
            'consent_type': consent_type,
            'success': True,
            'revoked_at': datetime.utcnow().isoformat()
        }

    def delete_profile_data(
        self,
        user_id: str,
        data_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Delete profile data for a user.

        Args:
            user_id: User identifier
            data_types: Optional specific data types to delete

        Returns:
            Dictionary with deletion result

        Example:
            >>> result = service.delete_profile_data('user_123')
        """
        deletion_id = str(uuid.uuid4())

        types_to_delete = data_types or ['all']
        deleted_types = []

        # Delete from various stores
        if 'all' in types_to_delete or 'consents' in types_to_delete:
            if user_id in self._consents:
                del self._consents[user_id]
                deleted_types.append('consents')

        if 'all' in types_to_delete or 'anonymization' in types_to_delete:
            if user_id in self._anonymization_settings:
                del self._anonymization_settings[user_id]
                deleted_types.append('anonymization')

        if 'all' in types_to_delete or 'user_data' in types_to_delete:
            if user_id in self._user_data:
                del self._user_data[user_id]
                deleted_types.append('user_data')

        return {
            'deletion_id': deletion_id,
            'user_id': user_id,
            'deleted_types': deleted_types,
            'requested_types': types_to_delete,
            'success': True,
            'deleted_at': datetime.utcnow().isoformat()
        }

    def schedule_deletion(
        self,
        user_id: str,
        scheduled_date: str,
        data_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Schedule data deletion for a future date.

        Args:
            user_id: User identifier
            scheduled_date: ISO format date for deletion
            data_types: Optional specific data types

        Returns:
            Dictionary with scheduling result

        Example:
            >>> result = service.schedule_deletion('user_123', '2024-12-31')
        """
        request_id = str(uuid.uuid4())

        request = {
            'request_id': request_id,
            'user_id': user_id,
            'scheduled_date': scheduled_date,
            'data_types': data_types or ['all'],
            'status': 'scheduled',
            'created_at': datetime.utcnow().isoformat()
        }

        self._deletion_requests[request_id] = request

        return {
            'request_id': request_id,
            'user_id': user_id,
            'scheduled_date': scheduled_date,
            'data_types': request['data_types'],
            'status': 'scheduled',
            'success': True,
            'scheduled_at': request['created_at']
        }

    def get_deletion_status(
        self,
        request_id: str
    ) -> Dict[str, Any]:
        """
        Get status of a deletion request.

        Args:
            request_id: Deletion request identifier

        Returns:
            Dictionary with deletion status

        Example:
            >>> status = service.get_deletion_status('req_123')
        """
        query_id = str(uuid.uuid4())

        if request_id not in self._deletion_requests:
            return {
                'query_id': query_id,
                'found': False,
                'error': 'Deletion request not found',
                'queried_at': datetime.utcnow().isoformat()
            }

        request = self._deletion_requests[request_id]

        return {
            'query_id': query_id,
            'request_id': request_id,
            'user_id': request['user_id'],
            'status': request['status'],
            'scheduled_date': request['scheduled_date'],
            'data_types': request['data_types'],
            'found': True,
            'queried_at': datetime.utcnow().isoformat()
        }

    def anonymize_data(
        self,
        user_id: str,
        data: Dict[str, Any],
        fields_to_anonymize: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Anonymize user data.

        Args:
            user_id: User identifier
            data: Data to anonymize
            fields_to_anonymize: Specific fields to anonymize

        Returns:
            Dictionary with anonymized data

        Example:
            >>> result = service.anonymize_data('user_123', {'name': 'John', 'email': 'john@example.com'})
        """
        anonymization_id = str(uuid.uuid4())

        # Get user's anonymization level
        level = 'standard'
        if user_id in self._anonymization_settings:
            level = self._anonymization_settings[user_id].get('level', 'standard')

        anonymized = {}
        fields_anonymized = []

        for key, value in data.items():
            if fields_to_anonymize is None or key in fields_to_anonymize:
                if level == 'full':
                    anonymized[key] = '***'
                elif level == 'partial':
                    if isinstance(value, str) and len(value) > 2:
                        anonymized[key] = value[0] + '*' * (len(value) - 2) + value[-1]
                    else:
                        anonymized[key] = '***'
                else:  # standard
                    anonymized[key] = '[REDACTED]'
                fields_anonymized.append(key)
            else:
                anonymized[key] = value

        return {
            'anonymization_id': anonymization_id,
            'user_id': user_id,
            'anonymized_data': anonymized,
            'fields_anonymized': fields_anonymized,
            'level_used': level,
            'success': True,
            'anonymized_at': datetime.utcnow().isoformat()
        }

    def set_anonymization_level(
        self,
        user_id: str,
        level: str
    ) -> Dict[str, Any]:
        """
        Set anonymization level for a user.

        Args:
            user_id: User identifier
            level: Anonymization level (minimal, standard, full)

        Returns:
            Dictionary with setting result

        Example:
            >>> result = service.set_anonymization_level('user_123', 'full')
        """
        setting_id = str(uuid.uuid4())

        valid_levels = ['minimal', 'partial', 'standard', 'full']
        if level not in valid_levels:
            return {
                'setting_id': setting_id,
                'success': False,
                'error': f'Invalid level. Must be one of: {valid_levels}',
                'set_at': datetime.utcnow().isoformat()
            }

        self._anonymization_settings[user_id] = {
            'level': level,
            'set_at': datetime.utcnow().isoformat()
        }

        return {
            'setting_id': setting_id,
            'user_id': user_id,
            'level': level,
            'success': True,
            'set_at': datetime.utcnow().isoformat()
        }

    def export_data(
        self,
        user_id: str,
        format_type: str = 'json',
        include_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Export user data in specified format.

        Args:
            user_id: User identifier
            format_type: Export format (json, csv, xml)
            include_types: Data types to include

        Returns:
            Dictionary with export result

        Example:
            >>> result = service.export_data('user_123', 'json')
        """
        export_id = str(uuid.uuid4())

        # Gather user data
        export_data = {}
        types_exported = []

        if include_types is None or 'consents' in include_types:
            if user_id in self._consents:
                export_data['consents'] = self._consents[user_id]
                types_exported.append('consents')

        if include_types is None or 'anonymization' in include_types:
            if user_id in self._anonymization_settings:
                export_data['anonymization_settings'] = self._anonymization_settings[user_id]
                types_exported.append('anonymization')

        if include_types is None or 'user_data' in include_types:
            if user_id in self._user_data:
                export_data['user_data'] = self._user_data[user_id]
                types_exported.append('user_data')

        # Format data
        if format_type == 'json':
            formatted_data = json.dumps(export_data, indent=2, default=str)
        elif format_type == 'csv':
            # Simple CSV representation
            formatted_data = "type,data\n" + "\n".join(
                f"{k},{json.dumps(v)}" for k, v in export_data.items()
            )
        else:
            formatted_data = str(export_data)

        return {
            'export_id': export_id,
            'user_id': user_id,
            'format': format_type,
            'data': formatted_data,
            'types_exported': types_exported,
            'size_bytes': len(formatted_data.encode('utf-8')),
            'success': True,
            'exported_at': datetime.utcnow().isoformat()
        }

    def import_data(
        self,
        user_id: str,
        data: str,
        format_type: str = 'json'
    ) -> Dict[str, Any]:
        """
        Import user data from exported format.

        Args:
            user_id: User identifier
            data: Data to import
            format_type: Format of the data

        Returns:
            Dictionary with import result

        Example:
            >>> result = service.import_data('user_123', '{"key": "value"}')
        """
        import_id = str(uuid.uuid4())

        types_imported = []

        try:
            if format_type == 'json':
                parsed_data = json.loads(data)
            else:
                return {
                    'import_id': import_id,
                    'success': False,
                    'error': f'Unsupported format: {format_type}',
                    'imported_at': datetime.utcnow().isoformat()
                }

            # Import into appropriate stores
            if 'consents' in parsed_data:
                self._consents[user_id] = parsed_data['consents']
                types_imported.append('consents')

            if 'anonymization_settings' in parsed_data:
                self._anonymization_settings[user_id] = parsed_data['anonymization_settings']
                types_imported.append('anonymization')

            if 'user_data' in parsed_data:
                self._user_data[user_id] = parsed_data['user_data']
                types_imported.append('user_data')

        except json.JSONDecodeError as e:
            return {
                'import_id': import_id,
                'success': False,
                'error': f'Invalid JSON: {str(e)}',
                'imported_at': datetime.utcnow().isoformat()
            }

        return {
            'import_id': import_id,
            'user_id': user_id,
            'format': format_type,
            'types_imported': types_imported,
            'success': True,
            'imported_at': datetime.utcnow().isoformat()
        }

    def get_export_formats(self) -> Dict[str, Any]:
        """
        Get available export formats.

        Returns:
            Dictionary with available formats

        Example:
            >>> formats = service.get_export_formats()
        """
        return {
            'formats': [
                {
                    'type': 'json',
                    'description': 'JSON format',
                    'mime_type': 'application/json'
                },
                {
                    'type': 'csv',
                    'description': 'CSV format',
                    'mime_type': 'text/csv'
                },
                {
                    'type': 'xml',
                    'description': 'XML format',
                    'mime_type': 'application/xml'
                }
            ],
            'default': 'json'
        }

    def get_privacy_config(self) -> Dict[str, Any]:
        """
        Get privacy controls configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_privacy_config()
        """
        return {
            'total_users_with_consent': len(self._consents),
            'total_deletion_requests': len(self._deletion_requests),
            'total_anonymization_settings': len(self._anonymization_settings),
            'supported_consent_types': [
                'data_collection', 'analytics', 'personalization',
                'marketing', 'third_party_sharing'
            ],
            'anonymization_levels': ['minimal', 'partial', 'standard', 'full'],
            'features': [
                'consent_management', 'data_deletion',
                'scheduled_deletion', 'anonymization',
                'data_export', 'data_import'
            ]
        }
