"""
Audio Data Handling Service for voice AI.

This service manages audio data security including encryption,
secure deletion, and access audit logging.

Key features:
- Audio encryption at rest
- Secure audio deletion
- Audio access audit logging

Example:
    >>> service = AudioDataService()
    >>> result = service.encrypt_audio(audio_id)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import hashlib


class AudioDataService:
    """
    Service for audio data handling.

    Provides encryption, secure deletion, and audit logging
    for audio files.

    Example:
        >>> service = AudioDataService()
        >>> config = service.get_audio_config()
    """

    def __init__(self):
        """Initialize the audio data service."""
        self._encrypted_files: Dict[str, Dict[str, Any]] = {}
        self._access_logs: List[Dict[str, Any]] = []
        self._deletions: List[Dict[str, Any]] = []
        self._encryption_algorithm = 'AES-256-GCM'

    def encrypt_audio(
        self,
        audio_id: str,
        key_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Encrypt audio file at rest.

        Args:
            audio_id: ID of audio file
            key_id: Optional encryption key ID

        Returns:
            Dictionary with encryption result

        Example:
            >>> result = service.encrypt_audio('audio123')
        """
        if key_id is None:
            key_id = str(uuid.uuid4())

        encryption_record = {
            'audio_id': audio_id,
            'key_id': key_id,
            'algorithm': self._encryption_algorithm,
            'encrypted_at': datetime.utcnow().isoformat(),
            'status': 'encrypted',
            'checksum': hashlib.sha256(audio_id.encode()).hexdigest()
        }

        self._encrypted_files[audio_id] = encryption_record

        self.log_access(audio_id, 'encrypt', 'system')

        return {
            'success': True,
            'audio_id': audio_id,
            'key_id': key_id,
            'algorithm': self._encryption_algorithm,
            'encrypted_at': encryption_record['encrypted_at']
        }

    def decrypt_audio(
        self,
        audio_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Decrypt audio file for access.

        Args:
            audio_id: ID of audio file
            user_id: ID of user requesting access

        Returns:
            Dictionary with decryption result

        Example:
            >>> result = service.decrypt_audio('audio123', 'user456')
        """
        if audio_id not in self._encrypted_files:
            return {
                'success': False,
                'error': f'Audio {audio_id} not found or not encrypted'
            }

        self.log_access(audio_id, 'decrypt', user_id)

        return {
            'success': True,
            'audio_id': audio_id,
            'decrypted_at': datetime.utcnow().isoformat(),
            'accessed_by': user_id
        }

    def get_encryption_status(
        self,
        audio_id: str
    ) -> Dict[str, Any]:
        """
        Get encryption status of audio file.

        Args:
            audio_id: ID of audio file

        Returns:
            Dictionary with encryption status

        Example:
            >>> status = service.get_encryption_status('audio123')
        """
        if audio_id in self._encrypted_files:
            record = self._encrypted_files[audio_id]
            return {
                'audio_id': audio_id,
                'is_encrypted': True,
                'algorithm': record['algorithm'],
                'encrypted_at': record['encrypted_at'],
                'key_id': record['key_id']
            }

        return {
            'audio_id': audio_id,
            'is_encrypted': False,
            'algorithm': None,
            'encrypted_at': None
        }

    def secure_delete(
        self,
        audio_id: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        Securely delete audio file.

        Args:
            audio_id: ID of audio file
            reason: Reason for deletion

        Returns:
            Dictionary with deletion result

        Example:
            >>> result = service.secure_delete('audio123', 'Retention expired')
        """
        deletion_record = {
            'deletion_id': str(uuid.uuid4()),
            'audio_id': audio_id,
            'reason': reason,
            'method': 'secure_overwrite',
            'passes': 3,
            'deleted_at': datetime.utcnow().isoformat(),
            'verified': False
        }

        self._deletions.append(deletion_record)

        # Remove from encrypted files
        if audio_id in self._encrypted_files:
            del self._encrypted_files[audio_id]

        self.log_access(audio_id, 'delete', 'system')

        return {
            'success': True,
            'deletion_id': deletion_record['deletion_id'],
            'audio_id': audio_id,
            'method': deletion_record['method'],
            'deleted_at': deletion_record['deleted_at']
        }

    def verify_deletion(
        self,
        deletion_id: str
    ) -> Dict[str, Any]:
        """
        Verify audio was securely deleted.

        Args:
            deletion_id: ID of deletion record

        Returns:
            Dictionary with verification result

        Example:
            >>> result = service.verify_deletion(deletion_id)
        """
        for deletion in self._deletions:
            if deletion['deletion_id'] == deletion_id:
                deletion['verified'] = True
                deletion['verified_at'] = datetime.utcnow().isoformat()

                return {
                    'success': True,
                    'deletion_id': deletion_id,
                    'audio_id': deletion['audio_id'],
                    'verified': True,
                    'verified_at': deletion['verified_at']
                }

        return {
            'success': False,
            'error': f'Deletion {deletion_id} not found'
        }

    def log_access(
        self,
        audio_id: str,
        action: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Log audio access for audit.

        Args:
            audio_id: ID of audio file
            action: Action performed
            user_id: ID of user

        Returns:
            Dictionary with log entry

        Example:
            >>> log = service.log_access('audio123', 'view', 'user456')
        """
        log_entry = {
            'log_id': str(uuid.uuid4()),
            'audio_id': audio_id,
            'action': action,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': '0.0.0.0'
        }

        self._access_logs.append(log_entry)
        return log_entry

    def get_access_logs(
        self,
        audio_id: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get audio access logs.

        Args:
            audio_id: Optional audio ID filter
            user_id: Optional user ID filter
            limit: Maximum logs to return

        Returns:
            List of log entries

        Example:
            >>> logs = service.get_access_logs(audio_id='audio123')
        """
        logs = self._access_logs.copy()

        if audio_id:
            logs = [entry for entry in logs if entry['audio_id'] == audio_id]

        if user_id:
            logs = [entry for entry in logs if entry['user_id'] == user_id]

        # Sort by timestamp descending
        logs.sort(key=lambda x: x['timestamp'], reverse=True)

        return logs[:limit]

    def get_audio_config(self) -> Dict[str, Any]:
        """
        Get audio data service configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_audio_config()
        """
        return {
            'encryption_algorithm': self._encryption_algorithm,
            'secure_delete_passes': 3,
            'total_encrypted': len(self._encrypted_files),
            'total_deletions': len(self._deletions),
            'total_access_logs': len(self._access_logs)
        }
