"""
Test suite for MOS Score Calculation Service.

This service provides Mean Opinion Score calculation
for voice quality assessment.

Components:
- R-factor calculation
- MOS score computation
- Quality degradation factors
- Quality classification
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


class TestRFactorCalculation:
    """Test R-factor calculation"""

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

    def test_has_get_delay_impairment_method(self, service_file_content):
        """Test get_delay_impairment method exists"""
        assert 'def get_delay_impairment(' in service_file_content

    def test_has_get_equipment_impairment_method(self, service_file_content):
        """Test get_equipment_impairment method exists"""
        assert 'def get_equipment_impairment(' in service_file_content


class TestMOSScoreComputation:
    """Test MOS score computation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the MOS score service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'mos_score_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_mos_method(self, service_file_content):
        """Test calculate_mos method exists"""
        assert 'def calculate_mos(' in service_file_content

    def test_has_calculate_mos_lq_method(self, service_file_content):
        """Test calculate_mos_lq method exists"""
        assert 'def calculate_mos_lq(' in service_file_content

    def test_has_calculate_mos_cq_method(self, service_file_content):
        """Test calculate_mos_cq method exists"""
        assert 'def calculate_mos_cq(' in service_file_content

    def test_has_r_to_mos_method(self, service_file_content):
        """Test r_to_mos method exists"""
        assert 'def r_to_mos(' in service_file_content


class TestQualityDegradation:
    """Test quality degradation factors"""

    @pytest.fixture
    def service_file_content(self):
        """Read the MOS score service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'mos_score_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_packet_loss_impairment_method(self, service_file_content):
        """Test calculate_packet_loss_impairment method exists"""
        assert 'def calculate_packet_loss_impairment(' in service_file_content

    def test_has_calculate_jitter_impairment_method(self, service_file_content):
        """Test calculate_jitter_impairment method exists"""
        assert 'def calculate_jitter_impairment(' in service_file_content

    def test_has_calculate_codec_impairment_method(self, service_file_content):
        """Test calculate_codec_impairment method exists"""
        assert 'def calculate_codec_impairment(' in service_file_content


class TestQualityClassification:
    """Test quality classification"""

    @pytest.fixture
    def service_file_content(self):
        """Read the MOS score service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'mos_score_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_classify_quality_method(self, service_file_content):
        """Test classify_quality method exists"""
        assert 'def classify_quality(' in service_file_content

    def test_has_get_quality_thresholds_method(self, service_file_content):
        """Test get_quality_thresholds method exists"""
        assert 'def get_quality_thresholds(' in service_file_content

    def test_has_is_acceptable_quality_method(self, service_file_content):
        """Test is_acceptable_quality method exists"""
        assert 'def is_acceptable_quality(' in service_file_content


class TestMetricsRecording:
    """Test metrics recording"""

    @pytest.fixture
    def service_file_content(self):
        """Read the MOS score service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'mos_score_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_record_call_metrics_method(self, service_file_content):
        """Test record_call_metrics method exists"""
        assert 'def record_call_metrics(' in service_file_content

    def test_has_get_mos_history_method(self, service_file_content):
        """Test get_mos_history method exists"""
        assert 'def get_mos_history(' in service_file_content

    def test_has_get_average_mos_method(self, service_file_content):
        """Test get_average_mos method exists"""
        assert 'def get_average_mos(' in service_file_content


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
