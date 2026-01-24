"""
Test Data Validation Service for voice AI testing.

This service manages test data validation including schema validation,
audio format validation, transcript consistency, and duplicate detection.

Key features:
- Schema validation for test cases
- Audio format validation
- Transcript consistency checking
- Duplicate detection

Example:
    >>> service = DataValidationService()
    >>> result = service.validate_schema(data, 'test_case')
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import hashlib


class DataValidationService:
    """
    Service for test data validation.

    Provides schema validation, audio format validation,
    transcript consistency, and duplicate detection.

    Example:
        >>> service = DataValidationService()
        >>> config = service.get_validation_config()
    """

    def __init__(self):
        """Initialize the data validation service."""
        self._validation_results: List[Dict[str, Any]] = []
        self._duplicate_cache: Dict[str, str] = {}

    def validate_schema(
        self,
        data: Dict[str, Any],
        schema_type: str
    ) -> Dict[str, Any]:
        """
        Validate data against schema.

        Args:
            data: Data to validate
            schema_type: Type of schema (test_case, dataset, etc.)

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_schema(data, 'test_case')
        """
        validation_id = str(uuid.uuid4())
        schema = self.get_schema(schema_type)

        errors = []
        for field in schema.get('required', []):
            if field not in data:
                errors.append({
                    'field': field,
                    'error': 'Required field missing'
                })

        result = {
            'validation_id': validation_id,
            'schema_type': schema_type,
            'valid': len(errors) == 0,
            'errors': errors,
            'validated_at': datetime.utcnow().isoformat()
        }

        self._validation_results.append(result)
        return result

    def get_schema(
        self,
        schema_type: str
    ) -> Dict[str, Any]:
        """
        Get schema definition.

        Args:
            schema_type: Type of schema

        Returns:
            Dictionary with schema definition

        Example:
            >>> schema = service.get_schema('test_case')
        """
        schemas = {
            'test_case': {
                'required': ['id', 'text'],
                'optional': ['expected_command_kind', 'entities', 'context', 'metadata']
            },
            'dataset': {
                'required': ['name', 'path', 'format'],
                'optional': ['description', 'version', 'metadata']
            },
            'audio': {
                'required': ['file_path', 'format', 'sample_rate'],
                'optional': ['duration', 'channels', 'bit_depth']
            }
        }
        return schemas.get(schema_type, {'required': [], 'optional': []})

    def validate_audio_format(
        self,
        audio_path: str,
        expected_format: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate audio file format.

        Args:
            audio_path: Path to audio file
            expected_format: Expected format (optional)

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_audio_format('/audio.wav', 'wav')
        """
        validation_id = str(uuid.uuid4())

        extension = audio_path.split('.')[-1].lower()
        supported = self.get_supported_formats()

        valid = extension in supported
        if expected_format:
            valid = valid and extension == expected_format.lower()

        return {
            'validation_id': validation_id,
            'audio_path': audio_path,
            'detected_format': extension,
            'expected_format': expected_format,
            'valid': valid,
            'validated_at': datetime.utcnow().isoformat()
        }

    def get_supported_formats(self) -> List[str]:
        """
        Get supported audio formats.

        Returns:
            List of format extensions

        Example:
            >>> formats = service.get_supported_formats()
        """
        return ['wav', 'mp3', 'flac', 'ogg', 'aac', 'm4a', 'wma', 'pcm']

    def validate_transcript_consistency(
        self,
        transcript: str,
        audio_duration: float
    ) -> Dict[str, Any]:
        """
        Validate transcript consistency with audio.

        Args:
            transcript: Transcript text
            audio_duration: Audio duration in seconds

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_transcript_consistency(text, 10.5)
        """
        validation_id = str(uuid.uuid4())

        word_count = len(transcript.split())
        expected_wpm = 150
        expected_words = (audio_duration / 60) * expected_wpm

        ratio = word_count / max(expected_words, 1)
        consistent = 0.5 <= ratio <= 2.0

        return {
            'validation_id': validation_id,
            'word_count': word_count,
            'audio_duration': audio_duration,
            'words_per_minute': (word_count / audio_duration) * 60 if audio_duration > 0 else 0,
            'consistent': consistent,
            'ratio': ratio,
            'validated_at': datetime.utcnow().isoformat()
        }

    def check_transcript_quality(
        self,
        transcript: str
    ) -> Dict[str, Any]:
        """
        Check transcript quality.

        Args:
            transcript: Transcript text

        Returns:
            Dictionary with quality assessment

        Example:
            >>> result = service.check_transcript_quality(text)
        """
        issues = []

        if not transcript.strip():
            issues.append('Empty transcript')
        if '???' in transcript or '[inaudible]' in transcript.lower():
            issues.append('Contains uncertainty markers')
        if len(transcript) < 5:
            issues.append('Very short transcript')

        return {
            'transcript_length': len(transcript),
            'word_count': len(transcript.split()),
            'has_issues': len(issues) > 0,
            'issues': issues,
            'quality_score': max(0, 100 - len(issues) * 20)
        }

    def detect_duplicates(
        self,
        items: List[Dict[str, Any]],
        key_fields: List[str]
    ) -> Dict[str, Any]:
        """
        Detect duplicates in items.

        Args:
            items: List of items to check
            key_fields: Fields to use for duplicate detection

        Returns:
            Dictionary with duplicate detection result

        Example:
            >>> result = service.detect_duplicates(items, ['text'])
        """
        detection_id = str(uuid.uuid4())
        seen = {}
        duplicates = []

        for idx, item in enumerate(items):
            key_values = tuple(str(item.get(f, '')) for f in key_fields)
            key_hash = hashlib.md5(str(key_values).encode()).hexdigest()

            if key_hash in seen:
                duplicates.append({
                    'index': idx,
                    'duplicate_of': seen[key_hash],
                    'key_values': key_values
                })
            else:
                seen[key_hash] = idx

        return {
            'detection_id': detection_id,
            'total_items': len(items),
            'duplicate_count': len(duplicates),
            'duplicates': duplicates,
            'unique_count': len(items) - len(duplicates),
            'detected_at': datetime.utcnow().isoformat()
        }

    def get_duplicate_report(
        self,
        detection_id: str
    ) -> Dict[str, Any]:
        """
        Get duplicate detection report.

        Args:
            detection_id: ID of detection

        Returns:
            Dictionary with report

        Example:
            >>> report = service.get_duplicate_report(det_id)
        """
        return {
            'detection_id': detection_id,
            'status': 'report_generated',
            'generated_at': datetime.utcnow().isoformat()
        }

    def get_validation_config(self) -> Dict[str, Any]:
        """
        Get validation configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_validation_config()
        """
        return {
            'total_validations': len(self._validation_results),
            'supported_formats': self.get_supported_formats(),
            'schema_types': ['test_case', 'dataset', 'audio'],
            'expected_wpm': 150,
            'consistency_ratio_range': {'min': 0.5, 'max': 2.0}
        }
