"""
EscalationPolicyService for applying escalation rules.

This service manages escalation policies and determines whether
validation results should be auto-passed, auto-failed, or escalated.
"""

from typing import Any, Dict, Optional

import logging

logger = logging.getLogger(__name__)


class EscalationPolicyService:
    """
    Service for applying escalation policies to validation results.

    Determines actions based on consensus results and policy thresholds.
    """

    def __init__(self) -> None:
        """Initialize the escalation policy service."""
        logger.info("EscalationPolicyService initialized")

    def get_default_policy(self) -> Dict[str, Any]:
        """
        Get the default escalation policy configuration.

        Returns:
            Dictionary with default policy settings
        """
        return {
            'min_agreement_ratio': 0.66,
            'min_confidence': 0.8,
            'auto_pass_threshold': 0.75,
            'escalate_threshold': 0.5
        }

    async def get_active_policy(self) -> Optional[Dict[str, Any]]:
        """
        Get the currently active escalation policy.

        Returns:
            Active policy configuration or None
        """
        # Placeholder - would query database
        return self.get_default_policy()

    def apply_policy(
        self,
        consensus: Dict[str, Any],
        policy_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Apply escalation policy to a consensus result.

        Args:
            consensus: Consensus result from ensemble judge
            policy_config: Optional policy configuration

        Returns:
            Dictionary with action and reason
        """
        if policy_config is None:
            policy_config = self.get_default_policy()

        return self.determine_action(consensus, policy_config)

    def determine_action(
        self,
        consensus: Dict[str, Any],
        policy_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine the action based on consensus and policy.

        Args:
            consensus: Consensus result from ensemble judge
            policy_config: Policy configuration

        Returns:
            Dictionary with action, reason, and details
        """
        decision = consensus.get('decision', 'fail')
        agreement_ratio = consensus.get('agreement_ratio', 0.0)
        confidence = consensus.get('confidence', 0.0)
        dissenting = consensus.get('dissenting_judges', [])

        min_agreement = policy_config.get('min_agreement_ratio', 0.66)
        min_confidence = policy_config.get('min_confidence', 0.8)

        # Auto-fail if consensus decision is fail
        if decision == 'fail':
            return {
                'action': 'auto_fail',
                'reason': 'Consensus decision is fail',
                'dissenting_judges': dissenting
            }

        # Check if should auto-pass
        if agreement_ratio >= min_agreement and confidence >= min_confidence:
            return {
                'action': 'auto_pass',
                'reason': 'Agreement and confidence meet thresholds',
                'dissenting_judges': dissenting
            }

        # Determine reason for escalation
        reasons = []
        if agreement_ratio < min_agreement:
            reasons.append(
                f'Agreement ratio {agreement_ratio:.2f} below '
                f'minimum {min_agreement:.2f}'
            )
        if confidence < min_confidence:
            reasons.append(
                f'Confidence {confidence:.2f} below '
                f'minimum {min_confidence:.2f}'
            )

        return {
            'action': 'escalate',
            'reason': '; '.join(reasons),
            'dissenting_judges': dissenting
        }


# Singleton instance
escalation_policy_service = EscalationPolicyService()

