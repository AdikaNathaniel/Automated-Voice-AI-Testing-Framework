"""
PII Detection and Redaction Service for voice AI.

This service provides PII (Personally Identifiable Information)
detection and redaction for voice AI transcripts.

Key features:
- Automatic PII detection in transcripts
- Configurable redaction policies
- PII types: SSN, credit card, phone, email, address

Example:
    >>> service = PIIService()
    >>> result = service.detect_pii(transcript)
"""

from typing import List, Dict, Any, Optional
import re
import uuid


class PIIService:
    """
    Service for PII detection and redaction.

    Provides detection methods for various PII types and
    configurable redaction policies.

    Example:
        >>> service = PIIService()
        >>> config = service.get_pii_config()
    """

    def __init__(self):
        """Initialize the PII service."""
        self._detections: List[Dict[str, Any]] = []
        self._redaction_policies: Dict[str, str] = {
            'ssn': 'mask',
            'credit_card': 'mask',
            'phone': 'mask',
            'email': 'partial',
            'address': 'redact'
        }

    def detect_pii(
        self,
        text: str,
        pii_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Detect PII in text.

        Args:
            text: Text to analyze
            pii_types: Optional list of PII types to detect

        Returns:
            Dictionary with detection results

        Example:
            >>> result = service.detect_pii("My SSN is 123-45-6789")
        """
        if pii_types is None:
            pii_types = ['ssn', 'credit_card', 'phone', 'email', 'address']

        findings = []

        if 'ssn' in pii_types:
            ssn_result = self.detect_ssn(text)
            if ssn_result['found']:
                findings.extend(ssn_result['matches'])

        if 'credit_card' in pii_types:
            cc_result = self.detect_credit_card(text)
            if cc_result['found']:
                findings.extend(cc_result['matches'])

        if 'phone' in pii_types:
            phone_result = self.detect_phone(text)
            if phone_result['found']:
                findings.extend(phone_result['matches'])

        if 'email' in pii_types:
            email_result = self.detect_email(text)
            if email_result['found']:
                findings.extend(email_result['matches'])

        if 'address' in pii_types:
            addr_result = self.detect_address(text)
            if addr_result['found']:
                findings.extend(addr_result['matches'])

        detection = {
            'detection_id': str(uuid.uuid4()),
            'text': text,
            'pii_found': len(findings) > 0,
            'findings': findings,
            'total_pii_count': len(findings)
        }

        self._detections.append(detection)
        return detection

    def get_pii_types(self) -> List[Dict[str, Any]]:
        """
        Get supported PII types.

        Returns:
            List of PII type definitions

        Example:
            >>> types = service.get_pii_types()
        """
        return [
            {
                'type': 'ssn',
                'name': 'Social Security Number',
                'description': 'US Social Security Numbers',
                'pattern': 'XXX-XX-XXXX'
            },
            {
                'type': 'credit_card',
                'name': 'Credit Card Number',
                'description': 'Credit/debit card numbers',
                'pattern': 'XXXX-XXXX-XXXX-XXXX'
            },
            {
                'type': 'phone',
                'name': 'Phone Number',
                'description': 'Phone numbers in various formats',
                'pattern': '(XXX) XXX-XXXX'
            },
            {
                'type': 'email',
                'name': 'Email Address',
                'description': 'Email addresses',
                'pattern': 'user@domain.com'
            },
            {
                'type': 'address',
                'name': 'Physical Address',
                'description': 'Street addresses',
                'pattern': '123 Main St'
            }
        ]

    def detect_ssn(self, text: str) -> Dict[str, Any]:
        """
        Detect Social Security Numbers.

        Supports multiple formats:
        - With dashes: 123-45-6789
        - With spaces: 123 45 6789
        - Without separators: 123456789

        Args:
            text: Text to analyze

        Returns:
            Dictionary with SSN detection result

        Example:
            >>> result = service.detect_ssn("SSN: 123-45-6789")
        """
        # Match SSN with dashes, spaces, or no separators
        pattern = r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b'
        matches = re.findall(pattern, text)

        return {
            'text': text,
            'pii_type': 'ssn',
            'found': len(matches) > 0,
            'matches': [
                {'type': 'ssn', 'value': m, 'confidence': 0.95}
                for m in matches
            ],
            'count': len(matches)
        }

    def detect_credit_card(self, text: str) -> Dict[str, Any]:
        """
        Detect credit card numbers.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with credit card detection result

        Example:
            >>> result = service.detect_credit_card("Card: 4111-1111-1111-1111")
        """
        pattern = r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
        matches = re.findall(pattern, text)

        return {
            'text': text,
            'pii_type': 'credit_card',
            'found': len(matches) > 0,
            'matches': [
                {'type': 'credit_card', 'value': m, 'confidence': 0.90}
                for m in matches
            ],
            'count': len(matches)
        }

    def detect_phone(self, text: str) -> Dict[str, Any]:
        """
        Detect phone numbers.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with phone detection result

        Example:
            >>> result = service.detect_phone("Call (555) 123-4567")
        """
        pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        matches = re.findall(pattern, text)

        return {
            'text': text,
            'pii_type': 'phone',
            'found': len(matches) > 0,
            'matches': [
                {'type': 'phone', 'value': m, 'confidence': 0.85}
                for m in matches
            ],
            'count': len(matches)
        }

    def detect_email(self, text: str) -> Dict[str, Any]:
        """
        Detect email addresses.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with email detection result

        Example:
            >>> result = service.detect_email("Email: user@example.com")
        """
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(pattern, text)

        return {
            'text': text,
            'pii_type': 'email',
            'found': len(matches) > 0,
            'matches': [
                {'type': 'email', 'value': m, 'confidence': 0.95}
                for m in matches
            ],
            'count': len(matches)
        }

    def detect_address(self, text: str) -> Dict[str, Any]:
        """
        Detect physical addresses.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with address detection result

        Example:
            >>> result = service.detect_address("Address: 123 Main St")
        """
        pattern = r'\d+\s+[A-Za-z]+\s+(?:St|Street|Ave|Avenue|Blvd|Boulevard|Rd|Road|Dr|Drive|Ln|Lane)'
        matches = re.findall(pattern, text, re.IGNORECASE)

        return {
            'text': text,
            'pii_type': 'address',
            'found': len(matches) > 0,
            'matches': [
                {'type': 'address', 'value': m, 'confidence': 0.80}
                for m in matches
            ],
            'count': len(matches)
        }

    def redact_pii(
        self,
        text: str,
        pii_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Redact PII from text based on policies.

        Args:
            text: Text to redact
            pii_types: Optional list of PII types to redact

        Returns:
            Dictionary with redacted text

        Example:
            >>> result = service.redact_pii("SSN: 123-45-6789")
        """
        if pii_types is None:
            pii_types = list(self._redaction_policies.keys())

        redacted_text = text
        redactions = []

        if 'ssn' in pii_types:
            pattern = r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b'
            policy = self._redaction_policies.get('ssn', 'mask')
            replacement = '***-**-****' if policy == 'mask' else '[REDACTED]'
            redacted_text = re.sub(pattern, replacement, redacted_text)
            if re.search(pattern, text):
                redactions.append({'type': 'ssn', 'policy': policy})

        if 'credit_card' in pii_types:
            pattern = r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
            policy = self._redaction_policies.get('credit_card', 'mask')
            replacement = '****-****-****-****' if policy == 'mask' else '[REDACTED]'
            redacted_text = re.sub(pattern, replacement, redacted_text)
            if re.search(pattern, text):
                redactions.append({'type': 'credit_card', 'policy': policy})

        if 'phone' in pii_types:
            pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
            policy = self._redaction_policies.get('phone', 'mask')
            replacement = '(***) ***-****' if policy == 'mask' else '[REDACTED]'
            redacted_text = re.sub(pattern, replacement, redacted_text)
            if re.search(pattern, text):
                redactions.append({'type': 'phone', 'policy': policy})

        if 'email' in pii_types:
            pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            policy = self._redaction_policies.get('email', 'partial')
            replacement = '***@***.***' if policy == 'partial' else '[REDACTED]'
            redacted_text = re.sub(pattern, replacement, redacted_text)
            if re.search(pattern, text):
                redactions.append({'type': 'email', 'policy': policy})

        if 'address' in pii_types:
            pattern = r'\d+\s+[A-Za-z]+\s+(?:St|Street|Ave|Avenue|Blvd|Boulevard|Rd|Road|Dr|Drive|Ln|Lane)'
            policy = self._redaction_policies.get('address', 'redact')
            replacement = '[ADDRESS REDACTED]'
            redacted_text = re.sub(pattern, replacement, redacted_text, flags=re.IGNORECASE)
            if re.search(pattern, text, re.IGNORECASE):
                redactions.append({'type': 'address', 'policy': policy})

        return {
            'original': text,
            'redacted': redacted_text,
            'redactions': redactions,
            'was_modified': text != redacted_text
        }

    def get_redaction_policies(self) -> Dict[str, Any]:
        """
        Get current redaction policies.

        Returns:
            Dictionary with redaction policies

        Example:
            >>> policies = service.get_redaction_policies()
        """
        return {
            'policies': self._redaction_policies.copy(),
            'available_modes': ['mask', 'partial', 'redact', 'remove'],
            'description': {
                'mask': 'Replace with asterisks preserving format',
                'partial': 'Partially mask the value',
                'redact': 'Replace with [REDACTED] label',
                'remove': 'Remove entirely'
            }
        }

    def set_redaction_policy(
        self,
        pii_type: str,
        policy: str
    ) -> Dict[str, Any]:
        """
        Set redaction policy for a PII type.

        Args:
            pii_type: Type of PII
            policy: Redaction policy to apply

        Returns:
            Dictionary with updated policy

        Example:
            >>> result = service.set_redaction_policy('ssn', 'redact')
        """
        valid_policies = ['mask', 'partial', 'redact', 'remove']
        valid_types = ['ssn', 'credit_card', 'phone', 'email', 'address']

        if pii_type not in valid_types:
            return {
                'success': False,
                'error': f'Invalid PII type: {pii_type}',
                'valid_types': valid_types
            }

        if policy not in valid_policies:
            return {
                'success': False,
                'error': f'Invalid policy: {policy}',
                'valid_policies': valid_policies
            }

        old_policy = self._redaction_policies.get(pii_type)
        self._redaction_policies[pii_type] = policy

        return {
            'success': True,
            'pii_type': pii_type,
            'old_policy': old_policy,
            'new_policy': policy
        }

    def get_pii_config(self) -> Dict[str, Any]:
        """
        Get PII service configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_pii_config()
        """
        return {
            'supported_pii_types': [
                'ssn', 'credit_card', 'phone', 'email', 'address'
            ],
            'redaction_policies': self._redaction_policies.copy(),
            'total_detections': len(self._detections)
        }
