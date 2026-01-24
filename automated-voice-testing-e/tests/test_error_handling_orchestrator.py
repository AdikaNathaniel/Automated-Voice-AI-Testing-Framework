"""
Test suite for Error Handling Orchestrator.

This orchestrator consolidates the 4 error handling services into
a coherent workflow for error analysis and recovery.

Components:
- Error categorization (classification, patterns)
- Error attribution (ASR/NLU, audio quality)
- Error prioritization (impact, severity, frequency)
- Error recovery (prompts, timeout, degradation)
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestErrorHandlingOrchestratorExists:
    """Test that error handling orchestrator exists"""

    def test_service_file_exists(self):
        """Test that error_handling_orchestrator.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'error_handling_orchestrator.py'
        )
        assert os.path.exists(service_file), (
            "error_handling_orchestrator.py should exist"
        )

    def test_orchestrator_class_exists(self):
        """Test that ErrorHandlingOrchestrator class exists"""
        from services.error_handling_orchestrator import ErrorHandlingOrchestrator
        assert ErrorHandlingOrchestrator is not None


class TestErrorHandlingOrchestratorBasic:
    """Test basic orchestrator functionality"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance"""
        from services.error_handling_orchestrator import ErrorHandlingOrchestrator
        return ErrorHandlingOrchestrator()

    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initializes correctly"""
        assert orchestrator is not None

    def test_has_categorization_component(self, orchestrator):
        """Test orchestrator has categorization component"""
        assert hasattr(orchestrator, 'categorization')

    def test_has_attribution_component(self, orchestrator):
        """Test orchestrator has attribution component"""
        assert hasattr(orchestrator, 'attribution')

    def test_has_priority_component(self, orchestrator):
        """Test orchestrator has priority component"""
        assert hasattr(orchestrator, 'priority')

    def test_has_recovery_component(self, orchestrator):
        """Test orchestrator has recovery component"""
        assert hasattr(orchestrator, 'recovery')


class TestErrorWorkflow:
    """Test error processing workflow"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance"""
        from services.error_handling_orchestrator import ErrorHandlingOrchestrator
        return ErrorHandlingOrchestrator()

    def test_process_error_method(self, orchestrator):
        """Test process_error method exists"""
        assert hasattr(orchestrator, 'process_error')
        assert callable(getattr(orchestrator, 'process_error'))

    def test_process_error_returns_dict(self, orchestrator):
        """Test process_error returns dictionary"""
        error = {'message': 'Test error', 'type': 'test'}
        result = orchestrator.process_error(error)
        assert isinstance(result, dict)

    def test_process_error_has_workflow_id(self, orchestrator):
        """Test result has workflow_id"""
        error = {'message': 'Test error', 'type': 'test'}
        result = orchestrator.process_error(error)
        assert 'workflow_id' in result

    def test_process_error_has_categorization(self, orchestrator):
        """Test result has categorization"""
        error = {'message': 'Test error', 'type': 'test'}
        result = orchestrator.process_error(error)
        assert 'categorization' in result

    def test_process_error_has_attribution(self, orchestrator):
        """Test result has attribution"""
        error = {'message': 'Test error', 'type': 'test'}
        result = orchestrator.process_error(error)
        assert 'attribution' in result

    def test_process_error_has_priority(self, orchestrator):
        """Test result has priority"""
        error = {'message': 'Test error', 'type': 'test'}
        result = orchestrator.process_error(error)
        assert 'priority' in result


class TestErrorCategorization:
    """Test error categorization functionality"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance"""
        from services.error_handling_orchestrator import ErrorHandlingOrchestrator
        return ErrorHandlingOrchestrator()

    def test_classify_error_method(self, orchestrator):
        """Test classify_error method exists"""
        assert hasattr(orchestrator, 'classify_error')
        assert callable(getattr(orchestrator, 'classify_error'))

    def test_classify_error_returns_dict(self, orchestrator):
        """Test classify_error returns dictionary"""
        error = {'message': 'Transcription failed', 'type': 'asr'}
        result = orchestrator.classify_error(error)
        assert isinstance(result, dict)

    def test_detect_patterns_method(self, orchestrator):
        """Test detect_patterns method exists"""
        assert hasattr(orchestrator, 'detect_patterns')
        assert callable(getattr(orchestrator, 'detect_patterns'))

    def test_get_error_types_method(self, orchestrator):
        """Test get_error_types method exists"""
        assert hasattr(orchestrator, 'get_error_types')
        types = orchestrator.get_error_types()
        assert isinstance(types, list)


class TestErrorAttribution:
    """Test error attribution functionality"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance"""
        from services.error_handling_orchestrator import ErrorHandlingOrchestrator
        return ErrorHandlingOrchestrator()

    def test_attribute_to_component_method(self, orchestrator):
        """Test attribute_to_component method exists"""
        assert hasattr(orchestrator, 'attribute_to_component')
        assert callable(getattr(orchestrator, 'attribute_to_component'))

    def test_attribute_to_component_returns_dict(self, orchestrator):
        """Test attribute_to_component returns dictionary"""
        error = {'message': 'Recognition error', 'type': 'asr'}
        result = orchestrator.attribute_to_component(error)
        assert isinstance(result, dict)

    def test_analyze_audio_impact_method(self, orchestrator):
        """Test analyze_audio_impact method exists"""
        assert hasattr(orchestrator, 'analyze_audio_impact')
        assert callable(getattr(orchestrator, 'analyze_audio_impact'))

    def test_get_asr_nlu_breakdown_method(self, orchestrator):
        """Test get_asr_nlu_breakdown method exists"""
        assert hasattr(orchestrator, 'get_asr_nlu_breakdown')
        errors = [{'message': 'Test error'}]
        result = orchestrator.get_asr_nlu_breakdown(errors)
        assert isinstance(result, dict)


class TestErrorPrioritization:
    """Test error prioritization functionality"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance"""
        from services.error_handling_orchestrator import ErrorHandlingOrchestrator
        return ErrorHandlingOrchestrator()

    def test_prioritize_errors_method(self, orchestrator):
        """Test prioritize_errors method exists"""
        assert hasattr(orchestrator, 'prioritize_errors')
        assert callable(getattr(orchestrator, 'prioritize_errors'))

    def test_prioritize_errors_returns_dict(self, orchestrator):
        """Test prioritize_errors returns dictionary"""
        errors = [{'message': 'Error 1'}, {'message': 'Error 2'}]
        result = orchestrator.prioritize_errors(errors)
        assert isinstance(result, dict)

    def test_calculate_impact_score_method(self, orchestrator):
        """Test calculate_impact_score method exists"""
        assert hasattr(orchestrator, 'calculate_impact_score')
        assert callable(getattr(orchestrator, 'calculate_impact_score'))

    def test_calculate_severity_method(self, orchestrator):
        """Test calculate_severity method exists"""
        assert hasattr(orchestrator, 'calculate_severity')
        assert callable(getattr(orchestrator, 'calculate_severity'))


class TestErrorRecovery:
    """Test error recovery functionality"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance"""
        from services.error_handling_orchestrator import ErrorHandlingOrchestrator
        return ErrorHandlingOrchestrator()

    def test_generate_recovery_prompt_method(self, orchestrator):
        """Test generate_recovery_prompt method exists"""
        assert hasattr(orchestrator, 'generate_recovery_prompt')
        assert callable(getattr(orchestrator, 'generate_recovery_prompt'))

    def test_generate_recovery_prompt_returns_dict(self, orchestrator):
        """Test generate_recovery_prompt returns dictionary"""
        result = orchestrator.generate_recovery_prompt('not_understood')
        assert isinstance(result, dict)

    def test_handle_timeout_method(self, orchestrator):
        """Test handle_timeout method exists"""
        assert hasattr(orchestrator, 'handle_timeout')
        assert callable(getattr(orchestrator, 'handle_timeout'))

    def test_graceful_degrade_method(self, orchestrator):
        """Test graceful_degrade method exists"""
        assert hasattr(orchestrator, 'graceful_degrade')
        assert callable(getattr(orchestrator, 'graceful_degrade'))


class TestBatchProcessing:
    """Test batch error processing"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance"""
        from services.error_handling_orchestrator import ErrorHandlingOrchestrator
        return ErrorHandlingOrchestrator()

    def test_process_batch_method(self, orchestrator):
        """Test process_batch method exists"""
        assert hasattr(orchestrator, 'process_batch')
        assert callable(getattr(orchestrator, 'process_batch'))

    def test_process_batch_returns_dict(self, orchestrator):
        """Test process_batch returns dictionary"""
        errors = [
            {'message': 'Error 1', 'type': 'asr'},
            {'message': 'Error 2', 'type': 'nlu'}
        ]
        result = orchestrator.process_batch(errors)
        assert isinstance(result, dict)

    def test_process_batch_has_results(self, orchestrator):
        """Test process_batch has results"""
        errors = [
            {'message': 'Error 1', 'type': 'asr'}
        ]
        result = orchestrator.process_batch(errors)
        assert 'results' in result

    def test_get_batch_summary_method(self, orchestrator):
        """Test get_batch_summary method exists"""
        assert hasattr(orchestrator, 'get_batch_summary')


class TestOrchestratorConfig:
    """Test orchestrator configuration"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance"""
        from services.error_handling_orchestrator import ErrorHandlingOrchestrator
        return ErrorHandlingOrchestrator()

    def test_get_orchestrator_config_method(self, orchestrator):
        """Test get_orchestrator_config method exists"""
        assert hasattr(orchestrator, 'get_orchestrator_config')

    def test_config_returns_dict(self, orchestrator):
        """Test config returns dictionary"""
        config = orchestrator.get_orchestrator_config()
        assert isinstance(config, dict)

    def test_config_has_components(self, orchestrator):
        """Test config has components"""
        config = orchestrator.get_orchestrator_config()
        assert 'components' in config

    def test_config_has_workflow_stages(self, orchestrator):
        """Test config has workflow stages"""
        config = orchestrator.get_orchestrator_config()
        assert 'workflow_stages' in config


class TestTypeHints:
    """Test type hints for error handling orchestrator"""

    @pytest.fixture
    def service_file_content(self):
        """Read the error handling orchestrator file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'error_handling_orchestrator.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_imports_typing_modules(self, service_file_content):
        """Test typing modules are imported"""
        assert 'from typing import' in service_file_content

    def test_uses_dict_type_hint(self, service_file_content):
        """Test Dict type hint is used"""
        assert 'Dict[' in service_file_content


class TestDocstrings:
    """Test comprehensive documentation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the error handling orchestrator file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'error_handling_orchestrator.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        """Test module has docstring"""
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        """Test class has docstring"""
        if 'class ErrorHandlingOrchestrator' in service_file_content:
            idx = service_file_content.find('class ErrorHandlingOrchestrator')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
