"""
Environment Parity Service for voice AI testing.

This service provides environment parity management including
configuration comparison, data anonymization, and synthetic data.

Key features:
- Dev/staging/prod configuration comparison
- Data anonymization for lower environments
- Synthetic data for testing

Example:
    >>> service = EnvironmentParityService()
    >>> result = service.compare_environments('dev', 'prod')
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import hashlib


class EnvironmentParityService:
    """
    Service for environment parity management.

    Provides configuration comparison, data anonymization,
    and synthetic data capabilities.

    Example:
        >>> service = EnvironmentParityService()
        >>> config = service.get_parity_config()
    """

    def __init__(self):
        """Initialize the environment parity service."""
        self._environments: Dict[str, Dict[str, Any]] = {}
        self._anonymization_rules: Dict[str, Dict[str, Any]] = {}
        self._data_generators: Dict[str, Dict[str, Any]] = {}
        self._supported_envs: List[str] = ['dev', 'staging', 'prod']

    def compare_environments(
        self,
        env1: str,
        env2: str,
        categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Compare two environments.

        Args:
            env1: First environment
            env2: Second environment
            categories: Configuration categories to compare

        Returns:
            Dictionary with comparison result

        Example:
            >>> result = service.compare_environments('dev', 'prod')
        """
        comparison_id = str(uuid.uuid4())

        config1 = self._environments.get(env1, {})
        config2 = self._environments.get(env2, {})

        differences = []
        similarities = []

        # Compare configurations
        all_keys = set(config1.keys()) | set(config2.keys())
        for key in all_keys:
            val1 = config1.get(key)
            val2 = config2.get(key)

            if val1 == val2:
                similarities.append(key)
            else:
                differences.append({
                    'key': key,
                    f'{env1}_value': val1,
                    f'{env2}_value': val2
                })

        parity_score = (
            len(similarities) / len(all_keys) * 100
            if all_keys else 100
        )

        return {
            'comparison_id': comparison_id,
            'env1': env1,
            'env2': env2,
            'differences': differences,
            'similarities': similarities,
            'parity_score': parity_score,
            'compared_at': datetime.utcnow().isoformat()
        }

    def get_config_diff(
        self,
        env1: str,
        env2: str,
        key: str
    ) -> Dict[str, Any]:
        """
        Get specific configuration difference.

        Args:
            env1: First environment
            env2: Second environment
            key: Configuration key

        Returns:
            Dictionary with diff details

        Example:
            >>> result = service.get_config_diff('dev', 'prod', 'db_host')
        """
        diff_id = str(uuid.uuid4())

        config1 = self._environments.get(env1, {})
        config2 = self._environments.get(env2, {})

        val1 = config1.get(key)
        val2 = config2.get(key)

        return {
            'diff_id': diff_id,
            'key': key,
            env1: val1,
            env2: val2,
            'matches': val1 == val2,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def validate_parity(
        self,
        source_env: str,
        target_env: str,
        required_keys: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Validate environment parity.

        Args:
            source_env: Source environment
            target_env: Target environment
            required_keys: Required configuration keys

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_parity('staging', 'prod')
        """
        validation_id = str(uuid.uuid4())

        comparison = self.compare_environments(source_env, target_env)

        missing_keys = []
        if required_keys:
            target_config = self._environments.get(target_env, {})
            missing_keys = [
                k for k in required_keys
                if k not in target_config
            ]

        return {
            'validation_id': validation_id,
            'source_env': source_env,
            'target_env': target_env,
            'parity_score': comparison['parity_score'],
            'missing_keys': missing_keys,
            'valid': len(missing_keys) == 0 and comparison['parity_score'] >= 90,
            'validated_at': datetime.utcnow().isoformat()
        }

    def anonymize_data(
        self,
        data: Dict[str, Any],
        rules: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Anonymize sensitive data.

        Args:
            data: Data to anonymize
            rules: Anonymization rules

        Returns:
            Dictionary with anonymized data

        Example:
            >>> result = service.anonymize_data({'email': 'test@test.com'})
        """
        anonymization_id = str(uuid.uuid4())

        anonymized = {}
        rules = rules or {}

        for key, value in data.items():
            if key in rules:
                rule = rules[key]
                if rule == 'hash':
                    anonymized[key] = hashlib.sha256(
                        str(value).encode()
                    ).hexdigest()[:16]
                elif rule == 'mask':
                    anonymized[key] = '***'
                elif rule == 'fake':
                    anonymized[key] = f'fake_{key}'
                else:
                    anonymized[key] = value
            else:
                anonymized[key] = value

        return {
            'anonymization_id': anonymization_id,
            'original_fields': len(data),
            'anonymized_data': anonymized,
            'anonymized_at': datetime.utcnow().isoformat()
        }

    def configure_anonymization(
        self,
        config_id: str,
        rules: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Configure anonymization rules.

        Args:
            config_id: Configuration identifier
            rules: Field to rule mapping

        Returns:
            Dictionary with configuration result

        Example:
            >>> result = service.configure_anonymization('c1', rules)
        """
        self._anonymization_rules[config_id] = {
            'id': config_id,
            'rules': rules,
            'configured_at': datetime.utcnow().isoformat()
        }

        return {
            'config_id': config_id,
            'rules_count': len(rules),
            'configured_at': datetime.utcnow().isoformat()
        }

    def verify_anonymization(
        self,
        data: Dict[str, Any],
        sensitive_fields: List[str]
    ) -> Dict[str, Any]:
        """
        Verify data is properly anonymized.

        Args:
            data: Data to verify
            sensitive_fields: Fields that should be anonymized

        Returns:
            Dictionary with verification result

        Example:
            >>> result = service.verify_anonymization(data, ['email'])
        """
        verification_id = str(uuid.uuid4())

        issues = []
        for field in sensitive_fields:
            if field in data:
                value = data[field]
                # Check if value looks like real data
                if '@' in str(value) or len(str(value)) > 20:
                    issues.append({
                        'field': field,
                        'issue': 'possibly_not_anonymized'
                    })

        return {
            'verification_id': verification_id,
            'fields_checked': len(sensitive_fields),
            'issues': issues,
            'verified': len(issues) == 0,
            'verified_at': datetime.utcnow().isoformat()
        }

    def generate_synthetic_data(
        self,
        schema: Dict[str, str],
        count: int = 10
    ) -> Dict[str, Any]:
        """
        Generate synthetic test data.

        Args:
            schema: Data schema
            count: Number of records

        Returns:
            Dictionary with generated data

        Example:
            >>> result = service.generate_synthetic_data({'name': 'string'})
        """
        generation_id = str(uuid.uuid4())

        records = []
        for i in range(count):
            record = {}
            for field, field_type in schema.items():
                if field_type == 'string':
                    record[field] = f'synthetic_{field}_{i}'
                elif field_type == 'int':
                    record[field] = i * 100
                elif field_type == 'email':
                    record[field] = f'user{i}@synthetic.test'
                elif field_type == 'bool':
                    record[field] = i % 2 == 0
                else:
                    record[field] = None
            records.append(record)

        return {
            'generation_id': generation_id,
            'records': records,
            'count': count,
            'schema': schema,
            'generated_at': datetime.utcnow().isoformat()
        }

    def configure_data_generator(
        self,
        generator_id: str,
        schema: Dict[str, str],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Configure data generator.

        Args:
            generator_id: Generator identifier
            schema: Data schema
            options: Generator options

        Returns:
            Dictionary with configuration result

        Example:
            >>> result = service.configure_data_generator('g1', schema)
        """
        self._data_generators[generator_id] = {
            'id': generator_id,
            'schema': schema,
            'options': options or {},
            'configured_at': datetime.utcnow().isoformat()
        }

        return {
            'generator_id': generator_id,
            'fields': len(schema),
            'configured_at': datetime.utcnow().isoformat()
        }

    def validate_synthetic_data(
        self,
        data: List[Dict[str, Any]],
        schema: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Validate synthetic data against schema.

        Args:
            data: Data to validate
            schema: Expected schema

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_synthetic_data(data, schema)
        """
        validation_id = str(uuid.uuid4())

        issues = []
        for i, record in enumerate(data):
            for field, expected_type in schema.items():
                if field not in record:
                    issues.append({
                        'record': i,
                        'field': field,
                        'issue': 'missing_field'
                    })

        return {
            'validation_id': validation_id,
            'records_checked': len(data),
            'issues': issues,
            'valid': len(issues) == 0,
            'validated_at': datetime.utcnow().isoformat()
        }

    def get_parity_config(self) -> Dict[str, Any]:
        """
        Get parity configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_parity_config()
        """
        return {
            'total_environments': len(self._environments),
            'total_anonymization_rules': len(self._anonymization_rules),
            'total_generators': len(self._data_generators),
            'supported_environments': self._supported_envs,
            'features': [
                'config_comparison', 'data_anonymization',
                'synthetic_data', 'parity_validation'
            ]
        }
