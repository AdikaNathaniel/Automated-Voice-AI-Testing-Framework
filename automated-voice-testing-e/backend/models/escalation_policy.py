"""
EscalationPolicy SQLAlchemy model for escalation configurations.

This model stores configuration for escalation policies that determine
when to auto-pass, auto-fail, or escalate to human review.
"""

from typing import Any, Dict

from sqlalchemy import Column, String, Float, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects import postgresql
from sqlalchemy import JSON

from models.base import Base, BaseModel, GUID


# Use JSONB for PostgreSQL, JSON for SQLite (testing)
JSONB_TYPE = JSONB().with_variant(JSON(), "sqlite")

class EscalationPolicy(Base, BaseModel):
    """
    EscalationPolicy model for storing escalation configurations.

    Represents a policy for determining when validation results should
    be auto-passed, auto-failed, or escalated to human review.

    Attributes:
        id (UUID): Unique identifier (inherited from BaseModel)
        name (str): Human-readable name for the policy
        min_agreement_ratio (float): Minimum agreement ratio for auto-pass
        min_confidence (float): Minimum confidence score for auto-pass
        auto_pass_threshold (float): Threshold for automatic pass
        escalate_threshold (float): Threshold for escalation
        is_active (bool): Whether the policy is active
        config (dict): Additional configuration as JSONB
    """

    __tablename__ = 'escalation_policies'

    tenant_id = Column(
        GUID(),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Tenant (organization or user) that owns this policy"
    )

    name = Column(
        String(255),
        nullable=False,
        comment="Human-readable name for the policy"
    )

    min_agreement_ratio = Column(
        Float,
        nullable=False,
        default=0.66,
        comment="Minimum agreement ratio for auto-pass (0.0 to 1.0)"
    )

    min_confidence = Column(
        Float,
        nullable=False,
        default=0.8,
        comment="Minimum confidence score for auto-pass (0.0 to 1.0)"
    )

    auto_pass_threshold = Column(
        Float,
        nullable=False,
        default=0.75,
        comment="Combined threshold for automatic pass"
    )

    escalate_threshold = Column(
        Float,
        nullable=False,
        default=0.5,
        comment="Threshold below which to escalate to human review"
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Whether the policy is currently active"
    )

    config = Column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        comment="Additional configuration settings"
    )

    def __repr__(self) -> str:
        """String representation of EscalationPolicy."""
        return f"<EscalationPolicy(name='{self.name}')>"

    def should_auto_pass(
        self,
        agreement_ratio: float,
        confidence: float
    ) -> bool:
        """
        Check if result should be auto-passed.

        Args:
            agreement_ratio: Agreement ratio from consensus
            confidence: Confidence score

        Returns:
            True if should auto-pass
        """
        return (
            agreement_ratio >= self.min_agreement_ratio and
            confidence >= self.min_confidence
        )

    def should_escalate(
        self,
        agreement_ratio: float,
        confidence: float
    ) -> bool:
        """
        Check if result should be escalated.

        Args:
            agreement_ratio: Agreement ratio from consensus
            confidence: Confidence score

        Returns:
            True if should escalate
        """
        return (
            agreement_ratio < self.min_agreement_ratio or
            confidence < self.min_confidence
        )

    def evaluate_consensus(
        self,
        consensus: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate a consensus result against this policy.

        Args:
            consensus: Consensus result from ensemble judge

        Returns:
            Dictionary with action, reason, and details
        """
        decision = consensus.get('decision', 'fail')
        agreement_ratio = consensus.get('agreement_ratio', 0.0)
        confidence = consensus.get('confidence', 0.0)
        dissenting = consensus.get('dissenting_judges', [])

        if decision == 'fail':
            return {
                'action': 'auto_fail',
                'reason': 'Consensus decision is fail',
                'dissenting_judges': dissenting
            }

        if self.should_auto_pass(agreement_ratio, confidence):
            return {
                'action': 'auto_pass',
                'reason': 'Agreement and confidence meet thresholds',
                'dissenting_judges': dissenting
            }

        # Determine reason for escalation
        reasons = []
        if agreement_ratio < self.min_agreement_ratio:
            reasons.append(
                f'Agreement ratio {agreement_ratio:.2f} below '
                f'minimum {self.min_agreement_ratio:.2f}'
            )
        if confidence < self.min_confidence:
            reasons.append(
                f'Confidence {confidence:.2f} below '
                f'minimum {self.min_confidence:.2f}'
            )

        return {
            'action': 'escalate',
            'reason': '; '.join(reasons),
            'dissenting_judges': dissenting
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert policy to dictionary.

        Returns:
            Dictionary representation of the policy
        """
        return {
            'id': str(self.id),
            'tenant_id': str(self.tenant_id),
            'name': self.name,
            'min_agreement_ratio': self.min_agreement_ratio,
            'min_confidence': self.min_confidence,
            'auto_pass_threshold': self.auto_pass_threshold,
            'escalate_threshold': self.escalate_threshold,
            'is_active': self.is_active,
            'config': self.config or {}
        }

