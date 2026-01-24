"""
Test suite for escalation policy functionality.

This module tests the escalation policy system:
- Low-consensus handling with dissenting judge tracking
- Configurable auto-pass vs escalate thresholds
- Integration with EnsembleJudgeService
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

from uuid import uuid4

import pytest


class TestEscalationPolicyModel:
    """Test EscalationPolicy model for storing escalation configurations"""

    def test_escalation_policy_model_exists(self):
        """Test that EscalationPolicy model can be imported"""
        from models.escalation_policy import EscalationPolicy
        assert EscalationPolicy is not None

    def test_has_name_field(self):
        """Test EscalationPolicy has name field"""
        from models.escalation_policy import EscalationPolicy

        columns = {c.name: c for c in EscalationPolicy.__table__.columns}
        assert 'name' in columns

    def test_has_min_agreement_ratio_field(self):
        """Test EscalationPolicy has min_agreement_ratio field"""
        from models.escalation_policy import EscalationPolicy

        columns = {c.name: c for c in EscalationPolicy.__table__.columns}
        assert 'min_agreement_ratio' in columns

    def test_has_min_confidence_field(self):
        """Test EscalationPolicy has min_confidence field"""
        from models.escalation_policy import EscalationPolicy

        columns = {c.name: c for c in EscalationPolicy.__table__.columns}
        assert 'min_confidence' in columns

    def test_has_auto_pass_threshold_field(self):
        """Test EscalationPolicy has auto_pass_threshold field"""
        from models.escalation_policy import EscalationPolicy

        columns = {c.name: c for c in EscalationPolicy.__table__.columns}
        assert 'auto_pass_threshold' in columns

    def test_has_escalate_threshold_field(self):
        """Test EscalationPolicy has escalate_threshold field"""
        from models.escalation_policy import EscalationPolicy

        columns = {c.name: c for c in EscalationPolicy.__table__.columns}
        assert 'escalate_threshold' in columns

    def test_has_is_active_field(self):
        """Test EscalationPolicy has is_active field"""
        from models.escalation_policy import EscalationPolicy

        columns = {c.name: c for c in EscalationPolicy.__table__.columns}
        assert 'is_active' in columns


class TestEscalationPolicyMethods:
    """Test EscalationPolicy helper methods"""

    def test_has_should_auto_pass_method(self):
        """Test EscalationPolicy has should_auto_pass method"""
        from models.escalation_policy import EscalationPolicy

        assert hasattr(EscalationPolicy, 'should_auto_pass')

    def test_has_should_escalate_method(self):
        """Test EscalationPolicy has should_escalate method"""
        from models.escalation_policy import EscalationPolicy

        assert hasattr(EscalationPolicy, 'should_escalate')

    def test_has_evaluate_consensus_method(self):
        """Test EscalationPolicy has evaluate_consensus method"""
        from models.escalation_policy import EscalationPolicy

        assert hasattr(EscalationPolicy, 'evaluate_consensus')


class TestEnsembleConsensusEnhancements:
    """Test EnsembleJudgeService consensus tracking enhancements"""

    def test_consensus_includes_dissenting_judges(self):
        """Test calculate_consensus returns dissenting judges"""
        from services.ensemble_judge_service import EnsembleJudgeService

        service = EnsembleJudgeService()
        decisions = [
            {'judge_id': 'judge1', 'decision': 'pass', 'confidence': 0.9},
            {'judge_id': 'judge2', 'decision': 'pass', 'confidence': 0.8},
            {'judge_id': 'judge3', 'decision': 'fail', 'confidence': 0.7},
        ]
        result = service.calculate_consensus(decisions)
        assert 'dissenting_judges' in result

    def test_dissenting_judges_correctly_identified(self):
        """Test dissenting judges are correctly identified"""
        from services.ensemble_judge_service import EnsembleJudgeService

        service = EnsembleJudgeService()
        decisions = [
            {'judge_id': 'judge1', 'decision': 'pass', 'confidence': 0.9},
            {'judge_id': 'judge2', 'decision': 'pass', 'confidence': 0.8},
            {'judge_id': 'judge3', 'decision': 'fail', 'confidence': 0.7},
        ]
        result = service.calculate_consensus(decisions)
        assert 'judge3' in result['dissenting_judges']

    def test_no_dissenting_when_unanimous(self):
        """Test no dissenting judges when decision is unanimous"""
        from services.ensemble_judge_service import EnsembleJudgeService

        service = EnsembleJudgeService()
        decisions = [
            {'judge_id': 'judge1', 'decision': 'pass', 'confidence': 0.9},
            {'judge_id': 'judge2', 'decision': 'pass', 'confidence': 0.8},
            {'judge_id': 'judge3', 'decision': 'pass', 'confidence': 0.7},
        ]
        result = service.calculate_consensus(decisions)
        assert result['dissenting_judges'] == []


class TestEscalationPolicyService:
    """Test EscalationPolicyService for applying escalation rules"""

    def test_service_exists(self):
        """Test that EscalationPolicyService can be imported"""
        from services.escalation_policy_service import EscalationPolicyService
        assert EscalationPolicyService is not None

    def test_has_apply_policy_method(self):
        """Test service has apply_policy method"""
        from services.escalation_policy_service import EscalationPolicyService

        assert hasattr(EscalationPolicyService, 'apply_policy')

    def test_has_get_active_policy_method(self):
        """Test service has get_active_policy method"""
        from services.escalation_policy_service import EscalationPolicyService

        assert hasattr(EscalationPolicyService, 'get_active_policy')

    def test_has_determine_action_method(self):
        """Test service has determine_action method"""
        from services.escalation_policy_service import EscalationPolicyService

        assert hasattr(EscalationPolicyService, 'determine_action')


class TestEscalationPolicyLogic:
    """Test escalation policy decision logic"""

    def test_auto_pass_when_high_agreement_and_confidence(self):
        """Test auto-pass when agreement ratio and confidence are high"""
        from services.escalation_policy_service import EscalationPolicyService

        service = EscalationPolicyService()
        consensus = {
            'decision': 'pass',
            'agreement_ratio': 0.8,
            'confidence': 0.85,
            'dissenting_judges': ['judge3']
        }
        policy_config = {
            'min_agreement_ratio': 0.66,
            'min_confidence': 0.8,
            'auto_pass_threshold': 0.75
        }

        result = service.determine_action(consensus, policy_config)
        assert result['action'] == 'auto_pass'

    def test_escalate_when_low_agreement(self):
        """Test escalate when agreement ratio is low"""
        from services.escalation_policy_service import EscalationPolicyService

        service = EscalationPolicyService()
        consensus = {
            'decision': 'pass',
            'agreement_ratio': 0.5,
            'confidence': 0.85,
            'dissenting_judges': ['judge2', 'judge3']
        }
        policy_config = {
            'min_agreement_ratio': 0.66,
            'min_confidence': 0.8,
            'auto_pass_threshold': 0.75
        }

        result = service.determine_action(consensus, policy_config)
        assert result['action'] == 'escalate'

    def test_escalate_when_low_confidence(self):
        """Test escalate when confidence is low"""
        from services.escalation_policy_service import EscalationPolicyService

        service = EscalationPolicyService()
        consensus = {
            'decision': 'pass',
            'agreement_ratio': 0.8,
            'confidence': 0.6,
            'dissenting_judges': ['judge3']
        }
        policy_config = {
            'min_agreement_ratio': 0.66,
            'min_confidence': 0.8,
            'auto_pass_threshold': 0.75
        }

        result = service.determine_action(consensus, policy_config)
        assert result['action'] == 'escalate'

    def test_auto_fail_when_decision_is_fail(self):
        """Test auto-fail when consensus decision is fail"""
        from services.escalation_policy_service import EscalationPolicyService

        service = EscalationPolicyService()
        consensus = {
            'decision': 'fail',
            'agreement_ratio': 0.8,
            'confidence': 0.85,
            'dissenting_judges': ['judge3']
        }
        policy_config = {
            'min_agreement_ratio': 0.66,
            'min_confidence': 0.8,
            'auto_pass_threshold': 0.75
        }

        result = service.determine_action(consensus, policy_config)
        assert result['action'] == 'auto_fail'


class TestEscalationReason:
    """Test escalation reason tracking"""

    def test_action_result_includes_reason(self):
        """Test action result includes reason for decision"""
        from services.escalation_policy_service import EscalationPolicyService

        service = EscalationPolicyService()
        consensus = {
            'decision': 'pass',
            'agreement_ratio': 0.5,
            'confidence': 0.85,
            'dissenting_judges': ['judge2', 'judge3']
        }
        policy_config = {
            'min_agreement_ratio': 0.66,
            'min_confidence': 0.8,
            'auto_pass_threshold': 0.75
        }

        result = service.determine_action(consensus, policy_config)
        assert 'reason' in result

    def test_reason_mentions_low_agreement(self):
        """Test reason mentions low agreement when that's the cause"""
        from services.escalation_policy_service import EscalationPolicyService

        service = EscalationPolicyService()
        consensus = {
            'decision': 'pass',
            'agreement_ratio': 0.5,
            'confidence': 0.85,
            'dissenting_judges': ['judge2', 'judge3']
        }
        policy_config = {
            'min_agreement_ratio': 0.66,
            'min_confidence': 0.8,
            'auto_pass_threshold': 0.75
        }

        result = service.determine_action(consensus, policy_config)
        assert 'agreement' in result['reason'].lower()

    def test_reason_mentions_low_confidence(self):
        """Test reason mentions low confidence when that's the cause"""
        from services.escalation_policy_service import EscalationPolicyService

        service = EscalationPolicyService()
        consensus = {
            'decision': 'pass',
            'agreement_ratio': 0.8,
            'confidence': 0.6,
            'dissenting_judges': ['judge3']
        }
        policy_config = {
            'min_agreement_ratio': 0.66,
            'min_confidence': 0.8,
            'auto_pass_threshold': 0.75
        }

        result = service.determine_action(consensus, policy_config)
        assert 'confidence' in result['reason'].lower()


class TestDefaultEscalationPolicy:
    """Test default escalation policy behavior"""

    def test_default_policy_values(self):
        """Test default policy has reasonable values"""
        from services.escalation_policy_service import EscalationPolicyService

        service = EscalationPolicyService()
        policy = service.get_default_policy()

        assert 'min_agreement_ratio' in policy
        assert 'min_confidence' in policy
        assert policy['min_agreement_ratio'] >= 0.5
        assert policy['min_confidence'] >= 0.5


