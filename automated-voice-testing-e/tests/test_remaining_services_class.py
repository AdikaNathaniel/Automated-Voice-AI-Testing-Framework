"""
Test suite for remaining service class-based implementations.

Tests: TestSuiteService, DefectService, LanguageService, AudioUtils
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestTestSuiteServiceClass:
    """Test TestSuiteService class exists"""

    def test_class_exists(self):
        """Test that TestSuiteService class exists"""
        from services.test_suite_service import TestSuiteService
        assert TestSuiteService is not None

    def test_class_is_importable(self):
        """Test class can be instantiated"""
        from services.test_suite_service import TestSuiteService
        service = TestSuiteService()
        assert service is not None

    def test_has_create_test_suite_method(self):
        """Test create_test_suite method exists"""
        from services.test_suite_service import TestSuiteService
        service = TestSuiteService()
        assert hasattr(service, 'create_test_suite')

    def test_backward_compatibility(self):
        """Test function still exists"""
        from services.test_suite_service import create_test_suite
        assert callable(create_test_suite)

    def test_has_all_crud_methods(self):
        """Test service has all CRUD methods"""
        from services.test_suite_service import TestSuiteService
        service = TestSuiteService()
        required_methods = [
            'create_test_suite',
            'get_test_suite',
            'list_test_suites',
            'update_test_suite',
            'delete_test_suite'
        ]
        for method in required_methods:
            assert hasattr(service, method), f"Missing method: {method}"
            assert callable(getattr(service, method)), f"{method} not callable"

    def test_methods_are_async(self):
        """Test that service methods are async coroutines"""
        import inspect
        from services.test_suite_service import TestSuiteService
        service = TestSuiteService()
        async_methods = [
            'create_test_suite',
            'get_test_suite',
            'list_test_suites',
            'update_test_suite',
            'delete_test_suite'
        ]
        for method_name in async_methods:
            method = getattr(service, method_name)
            assert inspect.iscoroutinefunction(method), f"{method_name} should be async"


class TestDefectServiceClass:
    """Test DefectService class exists"""

    def test_class_exists(self):
        """Test that DefectService class exists"""
        from services.defect_service import DefectService
        assert DefectService is not None

    def test_class_is_importable(self):
        """Test class can be instantiated"""
        from services.defect_service import DefectService
        service = DefectService()
        assert service is not None

    def test_has_create_defect_method(self):
        """Test create_defect method exists"""
        from services.defect_service import DefectService
        service = DefectService()
        assert hasattr(service, 'create_defect')

    def test_backward_compatibility(self):
        """Test function still exists"""
        from services.defect_service import create_defect
        assert callable(create_defect)

    def test_has_all_crud_methods(self):
        """Test service has all CRUD methods"""
        from services.defect_service import DefectService
        service = DefectService()
        required_methods = [
            'create_defect',
            'get_defect',
            'list_defects',
            'update_defect',
            'assign_defect',
            'resolve_defect'
        ]
        for method in required_methods:
            assert hasattr(service, method), f"Missing method: {method}"
            assert callable(getattr(service, method)), f"{method} not callable"

    def test_methods_are_async(self):
        """Test that service methods are async coroutines"""
        import inspect
        from services.defect_service import DefectService
        service = DefectService()
        async_methods = [
            'create_defect',
            'get_defect',
            'list_defects',
            'update_defect',
            'assign_defect',
            'resolve_defect'
        ]
        for method_name in async_methods:
            method = getattr(service, method_name)
            assert inspect.iscoroutinefunction(method), f"{method_name} should be async"

    def test_severity_priority_map_exists(self):
        """Test SEVERITY_PRIORITY_MAP is defined"""
        from services.defect_service import SEVERITY_PRIORITY_MAP
        assert isinstance(SEVERITY_PRIORITY_MAP, dict)
        assert 'critical' in SEVERITY_PRIORITY_MAP
        assert 'high' in SEVERITY_PRIORITY_MAP
        assert 'medium' in SEVERITY_PRIORITY_MAP
        assert 'low' in SEVERITY_PRIORITY_MAP

    def test_status_to_jira_status_map_exists(self):
        """Test STATUS_TO_JIRA_STATUS is defined"""
        from services.defect_service import STATUS_TO_JIRA_STATUS
        assert isinstance(STATUS_TO_JIRA_STATUS, dict)
        assert 'open' in STATUS_TO_JIRA_STATUS
        assert 'in_progress' in STATUS_TO_JIRA_STATUS
        assert 'resolved' in STATUS_TO_JIRA_STATUS


class TestLanguageServiceClass:
    """Test LanguageService class exists"""

    def test_class_exists(self):
        """Test that LanguageService class exists"""
        from services.language_service import LanguageService
        assert LanguageService is not None

    def test_class_is_importable(self):
        """Test class can be instantiated"""
        from services.language_service import LanguageService
        service = LanguageService()
        assert service is not None

    def test_has_get_supported_languages_method(self):
        """Test get_supported_languages method exists"""
        from services.language_service import LanguageService
        service = LanguageService()
        assert hasattr(service, 'get_supported_languages')

    def test_backward_compatibility(self):
        """Test function still exists"""
        from services.language_service import get_supported_languages
        assert callable(get_supported_languages)

    def test_get_supported_languages_returns_list(self):
        """Test get_supported_languages returns a list"""
        from services.language_service import LanguageService
        service = LanguageService()
        result = service.get_supported_languages()
        assert isinstance(result, list)

    def test_language_entries_have_required_keys(self):
        """Test each language entry has required keys"""
        from services.language_service import LanguageService
        service = LanguageService()
        languages = service.get_supported_languages()
        required_keys = {'code', 'name', 'native_name', 'soundhound_model'}
        for lang in languages:
            assert required_keys.issubset(lang.keys()), f"Missing keys in {lang}"

    def test_validate_language_code_returns_bool(self):
        """Test validate_language_code returns boolean"""
        from services.language_service import LanguageService
        service = LanguageService()
        result = service.validate_language_code('en-US')
        assert isinstance(result, bool)

    def test_get_soundhound_model_for_valid_code(self):
        """Test get_soundhound_model returns string for valid code"""
        from services.language_service import LanguageService
        service = LanguageService()
        # Get a valid code from supported languages
        languages = service.get_supported_languages()
        if languages:
            valid_code = languages[0]['code']
            model = service.get_soundhound_model(valid_code)
            assert isinstance(model, str)

    def test_get_soundhound_model_raises_for_invalid_code(self):
        """Test get_soundhound_model raises ValueError for invalid code"""
        from services.language_service import LanguageService
        import pytest
        service = LanguageService()
        with pytest.raises(ValueError):
            service.get_soundhound_model('invalid-code-xyz')


class TestAudioUtilsClass:
    """Test AudioUtils class exists"""

    def test_class_exists(self):
        """Test that AudioUtils class exists"""
        from services.audio_utils import AudioUtils
        assert AudioUtils is not None

    def test_class_is_importable(self):
        """Test class can be instantiated"""
        from services.audio_utils import AudioUtils
        service = AudioUtils()
        assert service is not None

    def test_has_convert_to_pcm_method(self):
        """Test convert_to_pcm method exists"""
        from services.audio_utils import AudioUtils
        service = AudioUtils()
        assert hasattr(service, 'convert_to_pcm')

    def test_backward_compatibility(self):
        """Test function still exists"""
        from services.audio_utils import convert_to_pcm
        assert callable(convert_to_pcm)

    def test_has_all_utility_methods(self):
        """Test service has all utility methods"""
        from services.audio_utils import AudioUtils
        service = AudioUtils()
        required_methods = [
            'convert_to_pcm',
            'add_noise',
            'validate_audio_format',
            'get_audio_duration'
        ]
        for method in required_methods:
            assert hasattr(service, method), f"Missing method: {method}"
            assert callable(getattr(service, method)), f"{method} not callable"

    def test_convert_to_pcm_raises_for_empty_bytes(self):
        """Test convert_to_pcm raises ValueError for empty input"""
        from services.audio_utils import AudioUtils
        service = AudioUtils()
        with pytest.raises(ValueError):
            service.convert_to_pcm(b'')

    def test_add_noise_raises_for_empty_bytes(self):
        """Test add_noise raises ValueError for empty input"""
        from services.audio_utils import AudioUtils
        service = AudioUtils()
        with pytest.raises(ValueError):
            service.add_noise(b'', 10.0)

    def test_validate_audio_format_returns_false_for_invalid(self):
        """Test validate_audio_format returns False for invalid data"""
        from services.audio_utils import AudioUtils
        service = AudioUtils()
        result = service.validate_audio_format(b'not valid audio data')
        assert result is False

    def test_validate_audio_format_returns_false_for_empty(self):
        """Test validate_audio_format returns False for empty data"""
        from services.audio_utils import AudioUtils
        service = AudioUtils()
        result = service.validate_audio_format(b'')
        assert result is False

    def test_get_audio_duration_raises_for_empty_bytes(self):
        """Test get_audio_duration raises ValueError for empty input"""
        from services.audio_utils import AudioUtils
        service = AudioUtils()
        with pytest.raises(ValueError):
            service.get_audio_duration(b'')
