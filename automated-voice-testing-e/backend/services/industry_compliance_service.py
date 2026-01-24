"""
Industry-specific Compliance Service for voice AI.

This service manages industry-specific compliance requirements
for healthcare (HIPAA) and payment (PCI-DSS) voice AI systems.

Key features:
- HIPAA for healthcare voice AI
- PCI-DSS for payment voice AI

Example:
    >>> service = IndustryComplianceService()
    >>> result = service.check_hipaa_compliance(transcript)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import re
import uuid


class IndustryComplianceService:
    """
    Service for industry-specific compliance.

    Provides HIPAA and PCI-DSS compliance checking
    for voice AI systems.

    Example:
        >>> service = IndustryComplianceService()
        >>> config = service.get_industry_config()
    """

    def __init__(self):
        """Initialize the industry compliance service."""
        self._compliance_checks: List[Dict[str, Any]] = []

    def check_hipaa_compliance(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Check HIPAA compliance for text.

        Args:
            text: Text to check
            context: Optional context information

        Returns:
            Dictionary with compliance result

        Example:
            >>> result = service.check_hipaa_compliance(transcript)
        """
        phi_result = self.detect_phi(text)
        self.get_hipaa_requirements()

        issues = []
        if phi_result['phi_found']:
            issues.append({
                'type': 'phi_detected',
                'severity': 'high',
                'description': 'Protected Health Information detected',
                'count': len(phi_result['findings'])
            })

        check = {
            'check_id': str(uuid.uuid4()),
            'standard': 'HIPAA',
            'text': text[:100] + '...' if len(text) > 100 else text,
            'is_compliant': len(issues) == 0,
            'issues': issues,
            'phi_detected': phi_result['phi_found'],
            'checked_at': datetime.utcnow().isoformat()
        }

        self._compliance_checks.append(check)
        return check

    def detect_phi(self, text: str) -> Dict[str, Any]:
        """
        Detect Protected Health Information.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with PHI detection result

        Example:
            >>> result = service.detect_phi(transcript)
        """
        phi_patterns = {
            'medical_record': r'\b(?:MRN|medical record)[:\s]*\d+\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'dob': r'\b(?:DOB|date of birth)[:\s]*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            'diagnosis': r'\b(?:diagnosis|diagnosed with)[:\s]*\w+',
            'medication': r'\b(?:medication|prescription|taking)[:\s]*\w+'
        }

        findings = []
        for phi_type, pattern in phi_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                findings.append({
                    'type': phi_type,
                    'value': match,
                    'confidence': 0.85
                })

        return {
            'text': text,
            'phi_found': len(findings) > 0,
            'findings': findings,
            'phi_types': list(set(f['type'] for f in findings))
        }

    def get_hipaa_requirements(self) -> List[Dict[str, Any]]:
        """
        Get HIPAA requirements checklist.

        Returns:
            List of HIPAA requirements

        Example:
            >>> requirements = service.get_hipaa_requirements()
        """
        return [
            {
                'requirement_id': 'HIPAA-164.312(a)',
                'title': 'Access Control',
                'description': 'Implement technical policies for electronic PHI'
            },
            {
                'requirement_id': 'HIPAA-164.312(b)',
                'title': 'Audit Controls',
                'description': 'Implement hardware, software, and procedures for audit trails'
            },
            {
                'requirement_id': 'HIPAA-164.312(c)',
                'title': 'Integrity',
                'description': 'Protect PHI from improper alteration or destruction'
            },
            {
                'requirement_id': 'HIPAA-164.312(d)',
                'title': 'Person Authentication',
                'description': 'Verify that a person seeking access is who they claim to be'
            },
            {
                'requirement_id': 'HIPAA-164.312(e)',
                'title': 'Transmission Security',
                'description': 'Protect PHI during transmission'
            }
        ]

    def check_pcidss_compliance(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Check PCI-DSS compliance for text.

        Args:
            text: Text to check
            context: Optional context information

        Returns:
            Dictionary with compliance result

        Example:
            >>> result = service.check_pcidss_compliance(transcript)
        """
        payment_result = self.detect_payment_data(text)
        self.get_pcidss_requirements()

        issues = []
        if payment_result['payment_data_found']:
            issues.append({
                'type': 'payment_data_detected',
                'severity': 'critical',
                'description': 'Payment card data detected',
                'count': len(payment_result['findings'])
            })

        check = {
            'check_id': str(uuid.uuid4()),
            'standard': 'PCI-DSS',
            'text': text[:100] + '...' if len(text) > 100 else text,
            'is_compliant': len(issues) == 0,
            'issues': issues,
            'payment_data_detected': payment_result['payment_data_found'],
            'checked_at': datetime.utcnow().isoformat()
        }

        self._compliance_checks.append(check)
        return check

    def detect_payment_data(self, text: str) -> Dict[str, Any]:
        """
        Detect payment card data.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with payment data detection result

        Example:
            >>> result = service.detect_payment_data(transcript)
        """
        payment_patterns = {
            'card_number': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'cvv': r'\b(?:CVV|CVC|security code)[:\s]*\d{3,4}\b',
            'expiry': r'\b(?:exp(?:iry)?|valid)[:\s]*\d{1,2}[/-]\d{2,4}\b',
            'cardholder': r'\b(?:name on card|cardholder)[:\s]*[A-Za-z\s]+'
        }

        findings = []
        for data_type, pattern in payment_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                findings.append({
                    'type': data_type,
                    'value': '[REDACTED]',  # Don't expose actual data
                    'confidence': 0.90
                })

        return {
            'text': text,
            'payment_data_found': len(findings) > 0,
            'findings': findings,
            'data_types': list(set(f['type'] for f in findings))
        }

    def get_pcidss_requirements(self) -> List[Dict[str, Any]]:
        """
        Get PCI-DSS requirements checklist.

        Returns:
            List of PCI-DSS requirements

        Example:
            >>> requirements = service.get_pcidss_requirements()
        """
        return [
            {
                'requirement_id': 'PCI-DSS-3.2',
                'title': 'Do not store sensitive authentication data',
                'description': 'Do not store CVV, PIN, or track data after authorization'
            },
            {
                'requirement_id': 'PCI-DSS-3.4',
                'title': 'Render PAN unreadable',
                'description': 'Mask PAN when displayed, show only last 4 digits'
            },
            {
                'requirement_id': 'PCI-DSS-4.1',
                'title': 'Encrypt transmission',
                'description': 'Use strong cryptography for cardholder data transmission'
            },
            {
                'requirement_id': 'PCI-DSS-8.2',
                'title': 'User identification',
                'description': 'Employ proper user identification and authentication'
            },
            {
                'requirement_id': 'PCI-DSS-10.1',
                'title': 'Audit trails',
                'description': 'Implement audit trails for all system components'
            }
        ]

    def get_industry_config(self) -> Dict[str, Any]:
        """
        Get industry compliance configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_industry_config()
        """
        return {
            'supported_standards': ['HIPAA', 'PCI-DSS'],
            'total_checks': len(self._compliance_checks),
            'hipaa_checks': len([c for c in self._compliance_checks if c['standard'] == 'HIPAA']),
            'pcidss_checks': len([c for c in self._compliance_checks if c['standard'] == 'PCI-DSS']),
            'compliance_rate': self._calculate_compliance_rate()
        }

    def _calculate_compliance_rate(self) -> float:
        """Calculate overall compliance rate."""
        if not self._compliance_checks:
            return 1.0
        compliant = sum(1 for c in self._compliance_checks if c['is_compliant'])
        return compliant / len(self._compliance_checks)
