"""
Edge Case Detection Service

Automatically detects patterns in validation failures and categorizes edge cases.
Generates relevant tags and metadata for auto-created edge cases.
"""

from __future__ import annotations

from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from models.validation_result import ValidationResult


class EdgeCaseDetectionService:
    """
    Detects patterns in edge cases and auto-categorizes them.
    """

    async def detect_category(
        self,
        validation_result: ValidationResult
    ) -> str:
        """
        Auto-detect edge case category based on validation scores and context.

        Categories:
        - ambiguous_intent: Low intent match, high semantic similarity
        - boundary_condition: Scores near threshold values
        - low_confidence: Very low AI confidence scores
        - high_confidence_failure: High confidence but failed validation
        - language_specific: Specific to certain language/region
        - context_dependent: Multi-turn context issues
        - unexpected_behavior: Pass on one validator, fail on another

        Args:
            validation_result: The validation result being analyzed

        Returns:
            str: Detected category name
        """
        # Get scores
        # Use ASR confidence score as the primary confidence metric
        confidence = validation_result.asr_confidence_score or 0
        review_status = validation_result.review_status or ""

        # Check for high confidence failures
        if confidence >= 0.8 and review_status == "needs_review":
            return "high_confidence_failure"

        # Check for low confidence
        if confidence < 0.4:
            return "low_confidence"

        # Check for boundary conditions (near threshold)
        if 0.45 <= confidence <= 0.55:
            return "boundary_condition"

        # Check for ambiguous intent (if we have LLM scores)
        # This would require accessing the ensemble validation result
        # For now, default to generic

        # Default category
        return "needs_classification"

    async def generate_tags(
        self,
        validation_result: ValidationResult,
        db: AsyncSession
    ) -> List[str]:
        """
        Generate relevant tags based on validation result patterns.

        Args:
            validation_result: The validation result
            db: Database session for querying related data

        Returns:
            List[str]: Generated tags
        """
        tags: List[str] = []

        # Get multi-turn execution to access scenario and language
        await db.refresh(validation_result, ["multi_turn_execution"])
        multi_turn_execution = validation_result.multi_turn_execution

        if multi_turn_execution:
            # Language tag from validation result
            language_code = validation_result.language_code
            if language_code:
                tags.append(language_code)

            # Scenario relationship (it's called "script" not "scenario")
            await db.refresh(multi_turn_execution, ["script"])
            scenario = multi_turn_execution.script

            if scenario:
                # Scenario category tag
                if scenario.script_metadata and scenario.script_metadata.get("category"):
                    category = scenario.script_metadata["category"]
                    tags.append(f"category:{category}")

                # Add existing scenario tags
                if scenario.script_metadata and scenario.script_metadata.get("tags"):
                    existing_tags = scenario.script_metadata["tags"]
                    if isinstance(existing_tags, list):
                        tags.extend(existing_tags[:3])  # Limit to first 3 tags

        # Confidence level tags (use asr_confidence_score)
        confidence = validation_result.asr_confidence_score or 0
        if confidence < 0.3:
            tags.append("very-low-confidence")
        elif confidence < 0.5:
            tags.append("low-confidence")
        elif confidence > 0.8:
            tags.append("high-confidence")

        # Review status tag
        if validation_result.review_status:
            tags.append(f"review:{validation_result.review_status}")

        # Remove duplicates and limit to 10 tags
        unique_tags = list(dict.fromkeys(tags))[:10]

        return unique_tags

    def determine_severity(
        self,
        validation_result: ValidationResult,
        category: str
    ) -> str:
        """
        Determine the severity level of an edge case.

        Args:
            validation_result: The validation result
            category: Detected category

        Returns:
            str: Severity level (critical, high, medium, low)
        """
        # High confidence failures are critical (AI was very wrong)
        if category == "high_confidence_failure":
            return "high"

        # Boundary conditions are medium severity
        if category == "boundary_condition":
            return "medium"

        # Low confidence is expected to need review
        if category == "low_confidence":
            return "low"

        # Default to medium
        return "medium"
