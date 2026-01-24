"""
StepOrchestrationService for multi-turn conversation orchestration.

This service handles step-level orchestration for scenarios:
- Execute individual steps with timing
- Validate step responses with similarity scoring
- Execute full scenarios with partial success support
- Process follow-up actions
"""

import time
from typing import Any, Dict, List

import logging

logger = logging.getLogger(__name__)


class StepOrchestrationService:
    """
    Service for orchestrating multi-turn conversation scenarios.

    Handles step-by-step execution, validation, and partial success tracking.
    """

    def __init__(self) -> None:
        """Initialize the step orchestration service."""
        self.default_tolerance = 0.8
        logger.info("StepOrchestrationService initialized")

    def execute_step(
        self,
        step: Dict[str, Any],
        actual_response: str
    ) -> Dict[str, Any]:
        """
        Execute a single step and return result.

        Args:
            step: Step configuration with expected_response_content, step_number, etc.
            actual_response: The actual system response

        Returns:
            Dictionary with passed status, step_number, duration_ms, follow_up_action
        """
        start_time = time.time()

        # Validate the step
        validation = self.validate_step(step, actual_response)

        duration_ms = int((time.time() - start_time) * 1000)

        result = {
            'passed': validation['passed'],
            'step_number': step.get('step_number', 1),
            'duration_ms': duration_ms,
            'score': validation.get('score', 0.0)
        }

        # Include follow-up action if specified
        if 'follow_up_action' in step and step['follow_up_action']:
            result['follow_up_action'] = step['follow_up_action']

        return result

    def validate_step(
        self,
        step: Dict[str, Any],
        actual_response: str
    ) -> Dict[str, Any]:
        """
        Validate step response against expected.

        Args:
            step: Step configuration with expected_response_content, tolerance_threshold
            actual_response: The actual system response

        Returns:
            Dictionary with passed status and similarity score
        """
        # Get expected response content (from ExpectedOutcome)
        expected_content = step.get('expected_response_content', {})
        threshold = step.get('tolerance_threshold', self.default_tolerance)

        # If no expected content, auto-pass
        if not expected_content:
            return {
                'passed': True,
                'score': 1.0,
                'method': 'no_validation'
            }

        # If expected_content is a string, use similarity
        if isinstance(expected_content, str):
            score = self._calculate_similarity(expected_content, actual_response)
            return {
                'passed': score >= threshold,
                'score': score
            }

        # If expected_content is a dict with 'contains' patterns
        if isinstance(expected_content, dict) and 'contains' in expected_content:
            patterns = expected_content['contains']
            response_lower = actual_response.lower()
            matches = sum(1 for p in patterns if p.lower() in response_lower)
            score = matches / len(patterns) if patterns else 1.0
            return {
                'passed': score >= threshold,
                'score': score
            }

        # Default: use string comparison if expected_content is something else
        score = self._calculate_similarity(str(expected_content), actual_response)
        return {
            'passed': score >= threshold,
            'score': score
        }

    def execute_scenario(
        self,
        scenario: Dict[str, Any],
        responses: List[str]
    ) -> Dict[str, Any]:
        """
        Execute a full scenario with multiple steps.

        Args:
            scenario: Scenario configuration with steps and settings
            responses: List of actual responses for each step

        Returns:
            Dictionary with overall results and per-step details
        """
        steps = scenario.get('steps', [])
        allow_partial = scenario.get('allow_partial_success', False)

        step_results = []
        successful_steps = 0
        had_failure = False
        recovered = False

        for i, step in enumerate(steps):
            # Get response for this step (or empty if missing)
            actual_response = responses[i] if i < len(responses) else ''

            # Execute the step
            result = self.execute_step(step, actual_response)
            step_results.append(result)

            if result['passed']:
                successful_steps += 1
                # Check if we recovered from a previous failure
                if had_failure and step.get('can_recover', False) is False:
                    recovered = True
                elif had_failure:
                    recovered = True
            else:
                had_failure = True

        total_steps = len(steps)
        all_passed = successful_steps == total_steps

        # Calculate overall score
        overall_score = 0.0
        if step_results:
            overall_score = sum(
                r.get('score', 0.0) for r in step_results
            ) / len(step_results)

        result = {
            'passed': all_passed,
            'step_results': step_results,
            'total_steps': total_steps,
            'successful_steps': successful_steps,
            'overall_score': overall_score
        }

        # Add partial success info if enabled
        if allow_partial and not all_passed and successful_steps > 0:
            result['partial_success'] = True

        # Add recovery info
        if recovered:
            result['recovered'] = True

        return result

    def process_follow_up(self, action: str) -> Dict[str, Any]:
        """
        Process a follow-up action.

        Args:
            action: The follow-up action to process

        Returns:
            Dictionary with action processing result
        """
        logger.info(f"Processing follow-up action: {action}")

        # Define supported actions
        supported_actions = {
            'await_confirmation': self._await_confirmation,
            'retry': self._retry_step,
            'escalate': self._escalate,
            'skip': self._skip_step
        }

        if action in supported_actions:
            return supported_actions[action]()

        return {
            'action': action,
            'status': 'unknown',
            'message': f'Unknown follow-up action: {action}'
        }

    def _calculate_similarity(self, expected: str, actual: str) -> float:
        """
        Calculate similarity between expected and actual responses.

        Uses Jaccard similarity based on word overlap.

        Args:
            expected: Expected response
            actual: Actual response

        Returns:
            Similarity score (0.0 to 1.0)
        """
        if not expected and not actual:
            return 1.0
        if not expected or not actual:
            return 0.0

        # Normalize strings
        expected_words = set(expected.lower().split())
        actual_words = set(actual.lower().split())

        intersection = expected_words.intersection(actual_words)
        union = expected_words.union(actual_words)

        if not union:
            return 1.0

        return len(intersection) / len(union)

    def _await_confirmation(self) -> Dict[str, Any]:
        """
        Handle await_confirmation action.

        TODO (FUTURE): Implement manual approval workflow
        - Pause test execution at this step
        - Emit event to frontend to show approval UI
        - Wait for user confirmation via WebSocket/API
        - Resume execution based on user decision (approve/reject)
        - Handle timeout if user doesn't respond within X seconds
        - Store approval decision in step_execution record

        Currently just returns pending status without actually pausing.
        """
        return {
            'action': 'await_confirmation',
            'status': 'pending',
            'message': 'Waiting for user confirmation'
        }

    def _retry_step(self) -> Dict[str, Any]:
        """Handle retry action."""
        return {
            'action': 'retry',
            'status': 'retry_scheduled',
            'message': 'Step retry scheduled'
        }

    def _escalate(self) -> Dict[str, Any]:
        """Handle escalate action."""
        return {
            'action': 'escalate',
            'status': 'escalated',
            'message': 'Step escalated for review'
        }

    def _skip_step(self) -> Dict[str, Any]:
        """Handle skip action."""
        return {
            'action': 'skip',
            'status': 'skipped',
            'message': 'Step skipped'
        }


# Singleton instance
step_orchestration_service = StepOrchestrationService()
