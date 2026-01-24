"""
Test suite for Centralized Configuration Service.

This service provides centralized configuration management
for all threshold values, quality levels, and timeout settings.

Components:
- SNR thresholds
- Confidence score thresholds
- Quality level classifications
- Timeout values
- Runtime reconfiguration
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestConfigurationServiceExists:
    """Test that configuration service exists"""

    def test_service_file_exists(self):
        """Test that centralized_config_service.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'centralized_config_service.py'
        )
        assert os.path.exists(service_file), (
            "centralized_config_service.py should exist"
        )

    def test_service_class_exists(self):
        """Test that CentralizedConfigService class exists"""
        from services.centralized_config_service import CentralizedConfigService
        assert CentralizedConfigService is not None


class TestConfigurationServiceBasic:
    """Test basic configuration service functionality"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        from services.centralized_config_service import CentralizedConfigService
        return CentralizedConfigService()

    def test_service_initialization(self, service):
        """Test service initializes correctly"""
        assert service is not None

    def test_has_get_config_method(self, service):
        """Test get_config method exists"""
        assert hasattr(service, 'get_config')
        assert callable(getattr(service, 'get_config'))

    def test_has_set_config_method(self, service):
        """Test set_config method exists"""
        assert hasattr(service, 'set_config')
        assert callable(getattr(service, 'set_config'))

    def test_has_reset_to_defaults_method(self, service):
        """Test reset_to_defaults method exists"""
        assert hasattr(service, 'reset_to_defaults')
        assert callable(getattr(service, 'reset_to_defaults'))


class TestSNRThresholds:
    """Test SNR threshold configuration"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        from services.centralized_config_service import CentralizedConfigService
        return CentralizedConfigService()

    def test_has_snr_thresholds_property(self, service):
        """Test SNR thresholds are accessible"""
        thresholds = service.get_snr_thresholds()
        assert isinstance(thresholds, dict)

    def test_snr_thresholds_has_high(self, service):
        """Test SNR thresholds has high value"""
        thresholds = service.get_snr_thresholds()
        assert 'high' in thresholds
        assert thresholds['high'] == 30.0

    def test_snr_thresholds_has_medium(self, service):
        """Test SNR thresholds has medium value"""
        thresholds = service.get_snr_thresholds()
        assert 'medium' in thresholds
        assert thresholds['medium'] == 20.0

    def test_snr_thresholds_has_low(self, service):
        """Test SNR thresholds has low value"""
        thresholds = service.get_snr_thresholds()
        assert 'low' in thresholds
        assert thresholds['low'] == 10.0

    def test_set_snr_threshold(self, service):
        """Test setting SNR threshold"""
        service.set_snr_threshold('high', 35.0)
        thresholds = service.get_snr_thresholds()
        assert thresholds['high'] == 35.0

    def test_get_snr_threshold_by_level(self, service):
        """Test getting specific SNR threshold"""
        value = service.get_snr_threshold('high')
        assert value == 30.0


class TestConfidenceThresholds:
    """Test confidence score threshold configuration"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        from services.centralized_config_service import CentralizedConfigService
        return CentralizedConfigService()

    def test_has_confidence_thresholds_property(self, service):
        """Test confidence thresholds are accessible"""
        thresholds = service.get_confidence_thresholds()
        assert isinstance(thresholds, dict)

    def test_confidence_has_minimum(self, service):
        """Test confidence has minimum threshold"""
        thresholds = service.get_confidence_thresholds()
        assert 'minimum' in thresholds
        assert thresholds['minimum'] == 0.5

    def test_confidence_has_recommended(self, service):
        """Test confidence has recommended threshold"""
        thresholds = service.get_confidence_thresholds()
        assert 'recommended' in thresholds
        assert thresholds['recommended'] == 0.7

    def test_confidence_has_high(self, service):
        """Test confidence has high threshold"""
        thresholds = service.get_confidence_thresholds()
        assert 'high' in thresholds
        assert thresholds['high'] == 0.8

    def test_confidence_has_very_high(self, service):
        """Test confidence has very_high threshold"""
        thresholds = service.get_confidence_thresholds()
        assert 'very_high' in thresholds
        assert thresholds['very_high'] == 0.9

    def test_set_confidence_threshold(self, service):
        """Test setting confidence threshold"""
        service.set_confidence_threshold('minimum', 0.6)
        thresholds = service.get_confidence_thresholds()
        assert thresholds['minimum'] == 0.6

    def test_get_confidence_threshold_by_level(self, service):
        """Test getting specific confidence threshold"""
        value = service.get_confidence_threshold('recommended')
        assert value == 0.7


class TestQualityLevels:
    """Test quality level classifications"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        from services.centralized_config_service import CentralizedConfigService
        return CentralizedConfigService()

    def test_has_quality_levels_property(self, service):
        """Test quality levels are accessible"""
        levels = service.get_quality_levels()
        assert isinstance(levels, dict)

    def test_quality_has_excellent(self, service):
        """Test quality has excellent level"""
        levels = service.get_quality_levels()
        assert 'excellent' in levels

    def test_quality_has_good(self, service):
        """Test quality has good level"""
        levels = service.get_quality_levels()
        assert 'good' in levels

    def test_quality_has_fair(self, service):
        """Test quality has fair level"""
        levels = service.get_quality_levels()
        assert 'fair' in levels

    def test_quality_has_poor(self, service):
        """Test quality has poor level"""
        levels = service.get_quality_levels()
        assert 'poor' in levels

    def test_classify_score_excellent(self, service):
        """Test classifying excellent score"""
        level = service.classify_quality_score(0.95)
        assert level == 'excellent'

    def test_classify_score_good(self, service):
        """Test classifying good score"""
        level = service.classify_quality_score(0.85)
        assert level == 'good'

    def test_classify_score_fair(self, service):
        """Test classifying fair score"""
        level = service.classify_quality_score(0.75)
        assert level == 'fair'

    def test_classify_score_poor(self, service):
        """Test classifying poor score"""
        level = service.classify_quality_score(0.5)
        assert level == 'poor'


class TestTimeoutValues:
    """Test timeout value configuration"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        from services.centralized_config_service import CentralizedConfigService
        return CentralizedConfigService()

    def test_has_timeouts_property(self, service):
        """Test timeouts are accessible"""
        timeouts = service.get_timeouts()
        assert isinstance(timeouts, dict)

    def test_timeout_has_default(self, service):
        """Test timeouts has default value"""
        timeouts = service.get_timeouts()
        assert 'default' in timeouts

    def test_timeout_has_api_call(self, service):
        """Test timeouts has api_call value"""
        timeouts = service.get_timeouts()
        assert 'api_call' in timeouts

    def test_timeout_has_database(self, service):
        """Test timeouts has database value"""
        timeouts = service.get_timeouts()
        assert 'database' in timeouts

    def test_timeout_has_audio_processing(self, service):
        """Test timeouts has audio_processing value"""
        timeouts = service.get_timeouts()
        assert 'audio_processing' in timeouts

    def test_set_timeout(self, service):
        """Test setting timeout value"""
        service.set_timeout('default', 60)
        timeouts = service.get_timeouts()
        assert timeouts['default'] == 60

    def test_get_timeout_by_name(self, service):
        """Test getting specific timeout"""
        value = service.get_timeout('default')
        assert isinstance(value, (int, float))


class TestRuntimeReconfiguration:
    """Test runtime reconfiguration support"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        from services.centralized_config_service import CentralizedConfigService
        return CentralizedConfigService()

    def test_reset_to_defaults(self, service):
        """Test resetting all config to defaults"""
        # Modify a value
        service.set_snr_threshold('high', 50.0)
        # Reset
        service.reset_to_defaults()
        # Verify reset
        assert service.get_snr_threshold('high') == 30.0

    def test_get_all_config(self, service):
        """Test getting all configuration"""
        config = service.get_all_config()
        assert isinstance(config, dict)
        assert 'snr_thresholds' in config
        assert 'confidence_thresholds' in config
        assert 'quality_levels' in config
        assert 'timeouts' in config

    def test_update_config_from_dict(self, service):
        """Test updating config from dictionary"""
        updates = {
            'snr_thresholds': {'high': 35.0}
        }
        service.update_config(updates)
        assert service.get_snr_threshold('high') == 35.0

    def test_export_config(self, service):
        """Test exporting configuration"""
        exported = service.export_config()
        assert isinstance(exported, dict)

    def test_import_config(self, service):
        """Test importing configuration"""
        config = {
            'snr_thresholds': {'high': 40.0, 'medium': 25.0, 'low': 15.0}
        }
        service.import_config(config)
        assert service.get_snr_threshold('high') == 40.0


class TestTypeHints:
    """Test type hints for configuration service"""

    @pytest.fixture
    def service_file_content(self):
        """Read the configuration service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'centralized_config_service.py'
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
        """Read the configuration service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'centralized_config_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        """Test module has docstring"""
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        """Test class has docstring"""
        if 'class CentralizedConfigService' in service_file_content:
            idx = service_file_content.find('class CentralizedConfigService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
