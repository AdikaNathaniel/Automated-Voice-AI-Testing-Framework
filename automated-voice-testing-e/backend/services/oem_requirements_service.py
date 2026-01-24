"""
OEM-specific Requirements Service for voice AI testing.

This service provides OEM-specific requirements testing for
automotive voice AI systems with brand customization.

Key features:
- Configurable OEM testing profiles
- Brand-specific terminology
- Response style guidelines
- Feature availability by market/trim

Example:
    >>> service = OEMRequirementsService()
    >>> profile = service.get_oem_profile('toyota')
"""

from typing import List, Dict, Any
from datetime import datetime
import uuid


class OEMRequirementsService:
    """
    Service for OEM-specific requirements testing.

    Provides automotive voice AI testing for brand-specific
    requirements and customization.

    Example:
        >>> service = OEMRequirementsService()
        >>> config = service.get_oem_requirements_config()
    """

    def __init__(self):
        """Initialize the OEM requirements service."""
        self._profiles: Dict[str, Dict[str, Any]] = {}
        self._terminology: Dict[str, Dict[str, str]] = {}
        self._feature_matrix: Dict[str, Dict[str, List[str]]] = {}

    def get_oem_profile(
        self,
        oem_name: str
    ) -> Dict[str, Any]:
        """
        Get OEM testing profile.

        Args:
            oem_name: OEM name

        Returns:
            Dictionary with OEM profile

        Example:
            >>> profile = service.get_oem_profile('toyota')
        """
        query_id = str(uuid.uuid4())

        profile = self._profiles.get(oem_name.lower(), {
            'oem_name': oem_name,
            'response_style': 'formal',
            'max_response_length': 50,
            'voice_persona': 'professional'
        })

        return {
            'query_id': query_id,
            'oem_name': oem_name,
            'profile': profile,
            'found': oem_name.lower() in self._profiles,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def configure_oem_profile(
        self,
        oem_name: str,
        profile_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Configure OEM testing profile.

        Args:
            oem_name: OEM name
            profile_config: Profile configuration

        Returns:
            Dictionary with configuration result

        Example:
            >>> result = service.configure_oem_profile('honda', {'style': 'casual'})
        """
        config_id = str(uuid.uuid4())

        self._profiles[oem_name.lower()] = {
            'oem_name': oem_name,
            **profile_config
        }

        return {
            'config_id': config_id,
            'oem_name': oem_name,
            'success': True,
            'profile': self._profiles[oem_name.lower()],
            'configured_at': datetime.utcnow().isoformat()
        }

    def get_brand_terminology(
        self,
        oem_name: str
    ) -> Dict[str, Any]:
        """
        Get brand-specific terminology.

        Args:
            oem_name: OEM name

        Returns:
            Dictionary with terminology

        Example:
            >>> terms = service.get_brand_terminology('bmw')
        """
        query_id = str(uuid.uuid4())

        default_terminology = {
            'navigation': 'Navigation',
            'climate': 'Climate Control',
            'media': 'Entertainment',
            'phone': 'Phone',
            'vehicle': 'Vehicle Settings'
        }

        terminology = self._terminology.get(
            oem_name.lower(),
            default_terminology
        )

        return {
            'query_id': query_id,
            'oem_name': oem_name,
            'terminology': terminology,
            'term_count': len(terminology),
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def validate_terminology(
        self,
        oem_name: str,
        text: str
    ) -> Dict[str, Any]:
        """
        Validate text uses correct brand terminology.

        Args:
            oem_name: OEM name
            text: Text to validate

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_terminology('audi', 'Open navigation')
        """
        validation_id = str(uuid.uuid4())

        issues: List[str] = []
        terminology = self._terminology.get(oem_name.lower(), {})

        # Check for incorrect terms
        incorrect_terms = {
            'gps': 'navigation',
            'ac': 'climate',
            'stereo': 'media',
            'call': 'phone'
        }

        text_lower = text.lower()
        for incorrect, correct in incorrect_terms.items():
            if incorrect in text_lower:
                brand_term = terminology.get(correct, correct)
                issues.append(f'Use "{brand_term}" instead of "{incorrect}"')

        return {
            'validation_id': validation_id,
            'valid': len(issues) == 0,
            'issues': issues,
            'issue_count': len(issues),
            'validated_at': datetime.utcnow().isoformat()
        }

    def get_response_style(
        self,
        oem_name: str
    ) -> Dict[str, Any]:
        """
        Get OEM response style guidelines.

        Args:
            oem_name: OEM name

        Returns:
            Dictionary with style guidelines

        Example:
            >>> style = service.get_response_style('mercedes')
        """
        query_id = str(uuid.uuid4())

        profile = self._profiles.get(oem_name.lower(), {})

        style = {
            'tone': profile.get('response_style', 'professional'),
            'formality': profile.get('formality', 'formal'),
            'max_words': profile.get('max_response_length', 50),
            'use_contractions': profile.get('use_contractions', False),
            'persona': profile.get('voice_persona', 'assistant')
        }

        return {
            'query_id': query_id,
            'oem_name': oem_name,
            'style': style,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def validate_response_style(
        self,
        oem_name: str,
        response_text: str
    ) -> Dict[str, Any]:
        """
        Validate response follows OEM style guidelines.

        Args:
            oem_name: OEM name
            response_text: Response text to validate

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_response_style('lexus', 'Sure thing!')
        """
        validation_id = str(uuid.uuid4())

        issues: List[str] = []
        profile = self._profiles.get(oem_name.lower(), {})

        # Check word count
        word_count = len(response_text.split())
        max_words = profile.get('max_response_length', 50)
        if word_count > max_words:
            issues.append(f'Response has {word_count} words, exceeds {max_words}')

        # Check formality
        formality = profile.get('formality', 'formal')
        informal_phrases = ["sure thing", "no prob", "gotcha", "yep"]
        if formality == 'formal':
            for phrase in informal_phrases:
                if phrase in response_text.lower():
                    issues.append(f'Informal phrase "{phrase}" not allowed')

        # Check contractions
        use_contractions = profile.get('use_contractions', False)
        if not use_contractions:
            contractions = ["don't", "won't", "can't", "isn't", "aren't"]
            for contraction in contractions:
                if contraction in response_text.lower():
                    issues.append(f'Contraction "{contraction}" not allowed')

        return {
            'validation_id': validation_id,
            'valid': len(issues) == 0,
            'issues': issues,
            'issue_count': len(issues),
            'validated_at': datetime.utcnow().isoformat()
        }

    def check_feature_availability(
        self,
        oem_name: str,
        market: str,
        trim: str,
        feature: str
    ) -> Dict[str, Any]:
        """
        Check if feature is available for market/trim.

        Args:
            oem_name: OEM name
            market: Market region
            trim: Vehicle trim level
            feature: Feature to check

        Returns:
            Dictionary with availability result

        Example:
            >>> result = service.check_feature_availability('ford', 'US', 'XLT', 'nav')
        """
        check_id = str(uuid.uuid4())

        # Get feature matrix for OEM
        oem_matrix = self._feature_matrix.get(oem_name.lower(), {})
        market_features = oem_matrix.get(market, {})
        trim_features = market_features.get(trim, [])

        is_available = feature in trim_features

        return {
            'check_id': check_id,
            'oem_name': oem_name,
            'market': market,
            'trim': trim,
            'feature': feature,
            'is_available': is_available,
            'checked_at': datetime.utcnow().isoformat()
        }

    def get_market_features(
        self,
        oem_name: str,
        market: str
    ) -> Dict[str, Any]:
        """
        Get available features for market.

        Args:
            oem_name: OEM name
            market: Market region

        Returns:
            Dictionary with market features

        Example:
            >>> features = service.get_market_features('nissan', 'EU')
        """
        query_id = str(uuid.uuid4())

        oem_matrix = self._feature_matrix.get(oem_name.lower(), {})
        market_data = oem_matrix.get(market, {})

        all_features: List[str] = []
        for trim_features in market_data.values():
            all_features.extend(trim_features)

        unique_features = list(set(all_features))

        return {
            'query_id': query_id,
            'oem_name': oem_name,
            'market': market,
            'features': unique_features,
            'feature_count': len(unique_features),
            'trims': list(market_data.keys()),
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def set_feature_matrix(
        self,
        oem_name: str,
        matrix: Dict[str, Dict[str, List[str]]]
    ) -> Dict[str, Any]:
        """
        Set feature availability matrix.

        Args:
            oem_name: OEM name
            matrix: Feature matrix by market/trim

        Returns:
            Dictionary with update result

        Example:
            >>> result = service.set_feature_matrix('chevy', {'US': {'LT': ['nav']}})
        """
        update_id = str(uuid.uuid4())

        self._feature_matrix[oem_name.lower()] = matrix

        return {
            'update_id': update_id,
            'oem_name': oem_name,
            'success': True,
            'markets': list(matrix.keys()),
            'updated_at': datetime.utcnow().isoformat()
        }

    def get_oem_requirements_config(self) -> Dict[str, Any]:
        """
        Get OEM requirements service configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_oem_requirements_config()
        """
        return {
            'configured_oems': list(self._profiles.keys()),
            'oem_count': len(self._profiles),
            'feature_matrices': len(self._feature_matrix),
            'features': [
                'oem_profiles', 'brand_terminology',
                'response_style', 'feature_availability'
            ]
        }
