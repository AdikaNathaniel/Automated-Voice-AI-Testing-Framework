"""
Test suite for MOS Score Calculation Service.

This service provides Mean Opinion Score calculation for
voice quality assessment using the E-model and R-factor.

Components:
- E-model implementation
- R-factor calculation
- MOS thresholds and alerting
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestMOSScoreServiceExists:
    """Test that MOS score service exists"""

    @pytest.fixture
    def service_file_content(self):
        """Read the MOS score service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'mos_score_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        """Test that mos_score_service.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'mos_score_service.py'
        )
        assert os.path.exists(service_file), (
            "mos_score_service.py should exist"
        )

    def test_service_class_exists(self, service_file_content):
        """Test that MOSScoreService class exists"""
        assert 'class MOSScoreService' in service_file_content


class TestEModel:
    """Test E-model implementation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the MOS score service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'mos_score_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_r_factor_method(self, service_file_content):
        """Test calculate_r_factor method exists"""
        assert 'def calculate_r_factor(' in service_file_content

    def test_has_calculate_mos_method(self, service_file_content):
        """Test calculate_mos method exists"""
        assert 'def calculate_mos(' in service_file_content

    def test_has_r_to_mos_method(self, service_file_content):
        """Test r_to_mos method exists"""
        assert 'def r_to_mos(' in service_file_content

    def test_has_calculate_ie_method(self, service_file_content):
        """Test calculate_ie (equipment impairment) method exists"""
        assert 'def calculate_ie(' in service_file_content

    def test_has_calculate_id_method(self, service_file_content):
        """Test calculate_id (delay impairment) method exists"""
        assert 'def calculate_id(' in service_file_content


class TestMOSCalculation:
    """Test MOS calculation methods"""

    @pytest.fixture
    def service_class(self):
        """Get the MOSScoreService class"""
        from services.mos_score_service import MOSScoreService
        return MOSScoreService

    @pytest.fixture
    def service_file_content(self):
        """Read the MOS score service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'mos_score_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_mos_from_metrics_method(self, service_file_content):
        """Test calculate_mos_from_metrics method exists"""
        assert 'def calculate_mos_from_metrics(' in service_file_content

    def test_has_get_mos_rating_method(self, service_class):
        """Test get_mos_rating method exists"""
        assert hasattr(service_class, 'get_mos_rating')
        assert callable(getattr(service_class, 'get_mos_rating'))

    def test_has_estimate_mos_method(self, service_file_content):
        """Test estimate_mos method exists"""
        assert 'def estimate_mos(' in service_file_content


class TestMOSThresholds:
    """Test MOS thresholds and alerting"""

    @pytest.fixture
    def service_class(self):
        """Get the MOSScoreService class"""
        from services.mos_score_service import MOSScoreService
        return MOSScoreService

    def test_has_set_threshold_method(self, service_class):
        """Test set_threshold method exists"""
        assert hasattr(service_class, 'set_threshold')
        assert callable(getattr(service_class, 'set_threshold'))

    def test_has_check_threshold_method(self, service_class):
        """Test check_threshold method exists"""
        assert hasattr(service_class, 'check_threshold')
        assert callable(getattr(service_class, 'check_threshold'))

    def test_has_get_alerts_method(self, service_class):
        """Test get_alerts method exists"""
        assert hasattr(service_class, 'get_alerts')
        assert callable(getattr(service_class, 'get_alerts'))

    def test_has_clear_alerts_method(self, service_class):
        """Test clear_alerts method exists"""
        assert hasattr(service_class, 'clear_alerts')
        assert callable(getattr(service_class, 'clear_alerts'))


class TestMOSHistory:
    """Test MOS history and reporting"""

    @pytest.fixture
    def service_class(self):
        """Get the MOSScoreService class"""
        from services.mos_score_service import MOSScoreService
        return MOSScoreService

    def test_has_record_mos_method(self, service_class):
        """Test record_mos method exists"""
        assert hasattr(service_class, 'record_mos')
        assert callable(getattr(service_class, 'record_mos'))

    def test_has_get_mos_history_method(self, service_class):
        """Test get_mos_history method exists"""
        assert hasattr(service_class, 'get_mos_history')
        assert callable(getattr(service_class, 'get_mos_history'))

    def test_has_get_mos_statistics_method(self, service_class):
        """Test get_mos_statistics method exists"""
        assert hasattr(service_class, 'get_mos_statistics')
        assert callable(getattr(service_class, 'get_mos_statistics'))


class TestTypeHints:
    """Test type hints for MOS score service"""

    @pytest.fixture
    def service_file_content(self):
        """Read the MOS score service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'mos_score_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_imports_typing_modules(self, service_file_content):
        """Test typing modules are imported"""
        assert 'from typing import' in service_file_content

    def test_uses_dict_type_hint(self, service_file_content):
        """Test Dict type hint is used"""
        assert 'Dict[' in service_file_content

    def test_uses_list_type_hint(self, service_file_content):
        """Test List type hint is used"""
        assert 'List[' in service_file_content


class TestDocstrings:
    """Test comprehensive documentation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the MOS score service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'mos_score_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        """Test module has docstring"""
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        """Test class has docstring"""
        if 'class MOSScoreService' in service_file_content:
            idx = service_file_content.find('class MOSScoreService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
