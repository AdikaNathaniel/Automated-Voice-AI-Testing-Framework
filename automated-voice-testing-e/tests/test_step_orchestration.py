"""
Test suite for step-level orchestration functionality.

This module tests the step-level orchestration system:
- Explicit modeling of scenario steps
- Per-step validation and success tracking
- Partial success with recovery support
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

from uuid import uuid4

import pytest


class TestStepOrchestrationService:
    """Test StepOrchestrationService for multi-turn conversations"""

    def test_service_exists(self):
        """Test that StepOrchestrationService can be imported"""
        from services.step_orchestration_service import StepOrchestrationService
        assert StepOrchestrationService is not None

    def test_has_execute_step_method(self):
        """Test service has execute_step method"""
        from services.step_orchestration_service import StepOrchestrationService

        assert hasattr(StepOrchestrationService, 'execute_step')

    def test_has_validate_step_method(self):
        """Test service has validate_step method"""
        from services.step_orchestration_service import StepOrchestrationService

        assert hasattr(StepOrchestrationService, 'validate_step')

    def test_has_execute_scenario_method(self):
        """Test service has execute_scenario method"""
        from services.step_orchestration_service import StepOrchestrationService

        assert hasattr(StepOrchestrationService, 'execute_scenario')


class TestScenarioStepModel:
    """Test ScenarioStep model for explicit step modeling"""

    def test_has_user_utterance_field(self):
        """Test ScenarioStep has user_utterance field"""
        from models.scenario_script import ScenarioStep

        columns = {c.name: c for c in ScenarioStep.__table__.columns}
        assert 'user_utterance' in columns

    def test_has_expected_response_field(self):
        """Test ScenarioStep has expected_response field"""
        from models.scenario_script import ScenarioStep

        columns = {c.name: c for c in ScenarioStep.__table__.columns}
        assert 'expected_response' in columns

    def test_has_follow_up_action_field(self):
        """Test ScenarioStep has follow_up_action field"""
        from models.scenario_script import ScenarioStep

        columns = {c.name: c for c in ScenarioStep.__table__.columns}
        assert 'follow_up_action' in columns


class TestStepExecution:
    """Test individual step execution"""

    def test_execute_step_returns_result(self):
        """Test execute_step returns a result dictionary"""
        from services.step_orchestration_service import StepOrchestrationService

        service = StepOrchestrationService()
        step = {
            'user_utterance': 'What is the weather?',
            'expected_response': 'The weather is sunny',
            'step_number': 1
        }
        actual_response = 'The weather is sunny today'

        result = service.execute_step(step, actual_response)
        assert isinstance(result, dict)
        assert 'passed' in result
        assert 'step_number' in result

    def test_execute_step_records_timing(self):
        """Test execute_step records timing information"""
        from services.step_orchestration_service import StepOrchestrationService

        service = StepOrchestrationService()
        step = {
            'user_utterance': 'What is the weather?',
            'expected_response': 'The weather is sunny',
            'step_number': 1
        }
        actual_response = 'The weather is sunny'

        result = service.execute_step(step, actual_response)
        assert 'duration_ms' in result


class TestPerStepValidation:
    """Test per-step validation logic"""

    def test_validate_step_success(self):
        """Test step validation succeeds when response matches"""
        from services.step_orchestration_service import StepOrchestrationService

        service = StepOrchestrationService()
        step = {
            'expected_response': 'The weather is sunny',
            'tolerance_threshold': 0.8
        }
        actual_response = 'The weather is sunny'

        result = service.validate_step(step, actual_response)
        assert result['passed'] is True

    def test_validate_step_failure(self):
        """Test step validation fails when response differs"""
        from services.step_orchestration_service import StepOrchestrationService

        service = StepOrchestrationService()
        step = {
            'expected_response': 'The weather is sunny',
            'tolerance_threshold': 0.9
        }
        actual_response = 'Playing music now'

        result = service.validate_step(step, actual_response)
        assert result['passed'] is False

    def test_validate_step_includes_score(self):
        """Test step validation includes similarity score"""
        from services.step_orchestration_service import StepOrchestrationService

        service = StepOrchestrationService()
        step = {
            'expected_response': 'Hello there',
            'tolerance_threshold': 0.5
        }
        actual_response = 'Hello world'

        result = service.validate_step(step, actual_response)
        assert 'score' in result


class TestPartialSuccess:
    """Test partial success and recovery handling"""

    def test_scenario_allows_partial_success(self):
        """Test scenario can have partial success"""
        from services.step_orchestration_service import StepOrchestrationService

        service = StepOrchestrationService()
        scenario = {
            'steps': [
                {'expected_response': 'Step 1', 'step_number': 1},
                {'expected_response': 'Step 2', 'step_number': 2},
                {'expected_response': 'Step 3', 'step_number': 3}
            ],
            'allow_partial_success': True
        }
        responses = ['Step 1', 'Wrong', 'Step 3']

        result = service.execute_scenario(scenario, responses)
        assert result['partial_success'] is True
        assert result['successful_steps'] == 2

    def test_recovery_from_failed_step(self):
        """Test recovery when later step succeeds"""
        from services.step_orchestration_service import StepOrchestrationService

        service = StepOrchestrationService()
        scenario = {
            'steps': [
                {'expected_response': 'Step 1', 'step_number': 1, 'can_recover': True},
                {'expected_response': 'Step 2', 'step_number': 2}
            ],
            'allow_partial_success': True
        }
        responses = ['Wrong response', 'Step 2']

        result = service.execute_scenario(scenario, responses)
        assert result['recovered'] is True

    def test_full_success_when_all_steps_pass(self):
        """Test full success when all steps pass"""
        from services.step_orchestration_service import StepOrchestrationService

        service = StepOrchestrationService()
        scenario = {
            'steps': [
                {'expected_response': 'Step 1', 'step_number': 1},
                {'expected_response': 'Step 2', 'step_number': 2}
            ],
            'allow_partial_success': False
        }
        responses = ['Step 1', 'Step 2']

        result = service.execute_scenario(scenario, responses)
        assert result['passed'] is True
        assert result['successful_steps'] == 2


class TestScenarioExecution:
    """Test full scenario execution"""

    def test_execute_scenario_returns_complete_result(self):
        """Test execute_scenario returns complete result"""
        from services.step_orchestration_service import StepOrchestrationService

        service = StepOrchestrationService()
        scenario = {
            'steps': [
                {'expected_response': 'Hello', 'step_number': 1}
            ]
        }
        responses = ['Hello']

        result = service.execute_scenario(scenario, responses)
        assert 'passed' in result
        assert 'step_results' in result
        assert 'total_steps' in result
        assert 'successful_steps' in result

    def test_execute_scenario_handles_missing_responses(self):
        """Test scenario handles fewer responses than steps"""
        from services.step_orchestration_service import StepOrchestrationService

        service = StepOrchestrationService()
        scenario = {
            'steps': [
                {'expected_response': 'Step 1', 'step_number': 1},
                {'expected_response': 'Step 2', 'step_number': 2}
            ]
        }
        responses = ['Step 1']  # Only one response for two steps

        result = service.execute_scenario(scenario, responses)
        assert result['passed'] is False


class TestFollowUpActions:
    """Test follow-up action handling"""

    def test_follow_up_action_triggered(self):
        """Test follow-up action is triggered when specified"""
        from services.step_orchestration_service import StepOrchestrationService

        service = StepOrchestrationService()
        step = {
            'expected_response': 'Confirm?',
            'follow_up_action': 'await_confirmation',
            'step_number': 1
        }
        actual_response = 'Confirm?'

        result = service.execute_step(step, actual_response)
        assert 'follow_up_action' in result
        assert result['follow_up_action'] == 'await_confirmation'

    def test_has_process_follow_up_method(self):
        """Test service has process_follow_up method"""
        from services.step_orchestration_service import StepOrchestrationService

        assert hasattr(StepOrchestrationService, 'process_follow_up')


class TestStepMetrics:
    """Test step-level metrics collection"""

    def test_collects_per_step_metrics(self):
        """Test metrics are collected for each step"""
        from services.step_orchestration_service import StepOrchestrationService

        service = StepOrchestrationService()
        scenario = {
            'steps': [
                {'expected_response': 'Step 1', 'step_number': 1},
                {'expected_response': 'Step 2', 'step_number': 2}
            ]
        }
        responses = ['Step 1', 'Step 2']

        result = service.execute_scenario(scenario, responses)
        assert len(result['step_results']) == 2
        for step_result in result['step_results']:
            assert 'score' in step_result

    def test_calculates_overall_score(self):
        """Test overall score is calculated from step scores"""
        from services.step_orchestration_service import StepOrchestrationService

        service = StepOrchestrationService()
        scenario = {
            'steps': [
                {'expected_response': 'Step 1', 'step_number': 1},
                {'expected_response': 'Step 2', 'step_number': 2}
            ]
        }
        responses = ['Step 1', 'Step 2']

        result = service.execute_scenario(scenario, responses)
        assert 'overall_score' in result


