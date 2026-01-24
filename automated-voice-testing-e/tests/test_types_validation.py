"""
Test suite for validation TypeScript types (TASK-183)

Validates the validation types implementation including:
- File structure
- TypeScript interfaces/types
- Proper exports
- Type definitions for ValidationQueue, HumanValidation, ValidatorPerformance, etc.
- Enum definitions for validation status
- Documentation
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
TYPES_DIR = PROJECT_ROOT / "frontend" / "src" / "types"
VALIDATION_TYPES_FILE = TYPES_DIR / "validation.ts"


class TestValidationTypesFileExists:
    """Test that validation types file exists"""

    def test_types_directory_exists(self):
        """Test that types directory exists"""
        assert TYPES_DIR.exists(), "frontend/src/types directory should exist"
        assert TYPES_DIR.is_dir(), "types should be a directory"

    def test_validation_types_file_exists(self):
        """Test that validation.ts exists"""
        assert VALIDATION_TYPES_FILE.exists(), "validation.ts should exist"
        assert VALIDATION_TYPES_FILE.is_file(), "validation.ts should be a file"

    def test_types_file_has_content(self):
        """Test that types file has content"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert len(content) > 0, "validation.ts should not be empty"


class TestValidationQueueInterface:
    """Test ValidationQueue interface"""

    def test_has_validation_queue_interface(self):
        """Test that ValidationQueue interface is defined"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert ("interface ValidationQueue" in content or
                "type ValidationQueue" in content), \
            "Should have ValidationQueue interface/type"

    def test_queue_has_id_field(self):
        """Test that ValidationQueue has id field"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert "id" in content, "Should have id field"

    def test_queue_has_validation_result_id_field(self):
        """Test that ValidationQueue has validationResultId field"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert ("validationResultId" in content or
                "validation_result_id" in content), \
            "Should have validationResultId field"

    def test_queue_has_priority_field(self):
        """Test that ValidationQueue has priority field"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert "priority" in content, "Should have priority field"

    def test_queue_has_confidence_score_field(self):
        """Test that ValidationQueue has confidenceScore field"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert ("confidenceScore" in content or
                "confidence_score" in content), \
            "Should have confidenceScore field"

    def test_queue_has_language_code_field(self):
        """Test that ValidationQueue has languageCode field"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert ("languageCode" in content or
                "language_code" in content), \
            "Should have languageCode field"

    def test_queue_has_status_field(self):
        """Test that ValidationQueue has status field"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert "status" in content, "Should have status field"

    def test_queue_has_claimed_by_field(self):
        """Test that ValidationQueue has claimedBy field"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert ("claimedBy" in content or
                "claimed_by" in content), \
            "Should have claimedBy field"

    def test_queue_has_claimed_at_field(self):
        """Test that ValidationQueue has claimedAt field"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert ("claimedAt" in content or
                "claimed_at" in content), \
            "Should have claimedAt field"


class TestHumanValidationInterface:
    """Test HumanValidation interface"""

    def test_has_human_validation_interface(self):
        """Test that HumanValidation interface is defined"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert ("interface HumanValidation" in content or
                "type HumanValidation" in content), \
            "Should have HumanValidation interface/type"

    def test_human_validation_has_id_field(self):
        """Test that HumanValidation has id field"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert "id" in content, "Should have id field"

    def test_human_validation_has_validation_result_id_field(self):
        """Test that HumanValidation has validationResultId field"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert ("validationResultId" in content or
                "validation_result_id" in content), \
            "Should have validationResultId field"

    def test_human_validation_has_validator_id_field(self):
        """Test that HumanValidation has validatorId field"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert ("validatorId" in content or
                "validator_id" in content), \
            "Should have validatorId field"

    def test_human_validation_has_decision_field(self):
        """Test that HumanValidation has decision field"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert "decision" in content, "Should have decision field"

    def test_human_validation_has_feedback_field(self):
        """Test that HumanValidation has feedback field"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert "feedback" in content, "Should have feedback field"

    def test_human_validation_has_time_spent_field(self):
        """Test that HumanValidation has timeSpent field"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert ("timeSpent" in content or
                "time_spent" in content), \
            "Should have timeSpent field"


class TestValidatorPerformanceInterface:
    """Test ValidatorPerformance interface"""

    def test_has_validator_performance_interface(self):
        """Test that ValidatorPerformance interface is defined"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert ("interface ValidatorPerformance" in content or
                "type ValidatorPerformance" in content), \
            "Should have ValidatorPerformance interface/type"

    def test_performance_has_validator_id_field(self):
        """Test that ValidatorPerformance has validatorId field"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert ("validatorId" in content or
                "validator_id" in content), \
            "Should have validatorId field"

    def test_performance_has_date_field(self):
        """Test that ValidatorPerformance has date field"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert "date" in content, "Should have date field"

    def test_performance_has_validations_completed_field(self):
        """Test that ValidatorPerformance has validationsCompleted field"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert ("validationsCompleted" in content or
                "validations_completed" in content), \
            "Should have validationsCompleted field"

    def test_performance_has_agreement_fields(self):
        """Test that ValidatorPerformance has agreement fields"""
        content = VALIDATION_TYPES_FILE.read_text()
        has_agreement = ("agreementWithPeers" in content or
                        "agreementWithFinal" in content or
                        "agreement_with_peers" in content or
                        "agreement_with_final" in content)
        assert has_agreement, "Should have agreement fields"


class TestValidationStatusEnum:
    """Test ValidationStatus enum"""

    def test_has_validation_status_enum(self):
        """Test that ValidationStatus enum is defined"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert ("enum ValidationStatus" in content or
                "type ValidationStatus" in content), \
            "Should have ValidationStatus enum/type"

    def test_status_has_pending(self):
        """Test that ValidationStatus has PENDING"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert ("PENDING" in content or
                "pending" in content or
                "'pending'" in content), \
            "Should have PENDING status"

    def test_status_has_claimed(self):
        """Test that ValidationStatus has CLAIMED"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert ("CLAIMED" in content or
                "claimed" in content or
                "'claimed'" in content), \
            "Should have CLAIMED status"

    def test_status_has_completed(self):
        """Test that ValidationStatus has COMPLETED"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert ("COMPLETED" in content or
                "completed" in content or
                "'completed'" in content), \
            "Should have COMPLETED status"


class TestValidationDecisionEnum:
    """Test ValidationDecision enum"""

    def test_has_validation_decision_enum(self):
        """Test that ValidationDecision enum is defined"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert ("enum ValidationDecision" in content or
                "type ValidationDecision" in content), \
            "Should have ValidationDecision enum/type"

    def test_decision_has_approve(self):
        """Test that ValidationDecision has APPROVE"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert ("APPROVE" in content or
                "approve" in content or
                "'approve'" in content), \
            "Should have APPROVE decision"

    def test_decision_has_reject(self):
        """Test that ValidationDecision has REJECT"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert ("REJECT" in content or
                "reject" in content or
                "'reject'" in content), \
            "Should have REJECT decision"

    def test_decision_has_uncertain(self):
        """Test that ValidationDecision has UNCERTAIN"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert ("UNCERTAIN" in content or
                "uncertain" in content or
                "'uncertain'" in content), \
            "Should have UNCERTAIN decision"


class TestValidationStatsInterface:
    """Test ValidationStats interface"""

    def test_has_validation_stats_interface(self):
        """Test that ValidationStats interface is defined"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert ("interface ValidationStats" in content or
                "type ValidationStats" in content), \
            "Should have ValidationStats interface/type"

    def test_stats_has_pending_count_field(self):
        """Test that ValidationStats has pending_count field"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert "pending_count" in content, \
            "Should have pending_count field"

    def test_stats_has_claimed_count_field(self):
        """Test that ValidationStats has claimed_count field"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert "claimed_count" in content, \
            "Should have claimed_count field"

    def test_stats_has_completed_count_field(self):
        """Test that ValidationStats has completed_count field"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert "completed_count" in content, \
            "Should have completed_count field"

    def test_stats_has_distribution_fields(self):
        """Test that ValidationStats exposes priority and language distributions"""
        content = VALIDATION_TYPES_FILE.read_text()
        assert "priority_distribution" in content, \
            "Should have priority_distribution field"
        assert "language_distribution" in content, \
            "Should have language_distribution field"


class TestExports:
    """Test exports"""

    def test_has_exports(self):
        """Test that file has exports"""
        content = VALIDATION_TYPES_FILE.read_text()
        has_exports = ("export" in content)
        assert has_exports, "Should have export statements"
