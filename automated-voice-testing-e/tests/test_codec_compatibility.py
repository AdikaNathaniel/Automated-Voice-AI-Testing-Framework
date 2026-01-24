"""
Test suite for Codec Compatibility Testing.

Different audio codecs can significantly impact ASR performance due to
compression artifacts and frequency response characteristics. This service
provides tools for testing and analyzing codec impact on transcription.

Supported codecs:
- G.711: mu-law and A-law telephony codecs
- G.722: Wideband codec
- Opus: Versatile codec at various bitrates
- AAC/MP3: Consumer audio codecs
- Speex: Open source speech codec
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestCodecCompatibilityServiceExists:
    """Test that codec compatibility service exists"""

    @pytest.fixture
    def service_file_content(self):
        """Read the codec compatibility service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'codec_compatibility_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        """Test that codec_compatibility_service.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'codec_compatibility_service.py'
        )
        assert os.path.exists(service_file), (
            "codec_compatibility_service.py should exist"
        )

    def test_service_class_exists(self, service_file_content):
        """Test that CodecCompatibilityService class exists"""
        assert 'class CodecCompatibilityService' in service_file_content


class TestCodecDefinitions:
    """Test codec definitions and constants"""

    @pytest.fixture
    def service_file_content(self):
        """Read the codec compatibility service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'codec_compatibility_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_g711_codec(self, service_file_content):
        """Test G.711 codec is defined"""
        assert 'g711' in service_file_content.lower() or 'G711' in service_file_content

    def test_has_g722_codec(self, service_file_content):
        """Test G.722 codec is defined"""
        assert 'g722' in service_file_content.lower() or 'G722' in service_file_content

    def test_has_opus_codec(self, service_file_content):
        """Test Opus codec is defined"""
        assert 'opus' in service_file_content.lower()

    def test_has_aac_codec(self, service_file_content):
        """Test AAC codec is defined"""
        assert 'aac' in service_file_content.lower()

    def test_has_mp3_codec(self, service_file_content):
        """Test MP3 codec is defined"""
        assert 'mp3' in service_file_content.lower()

    def test_has_speex_codec(self, service_file_content):
        """Test Speex codec is defined"""
        assert 'speex' in service_file_content.lower()


class TestCodecInfo:
    """Test codec information retrieval"""

    @pytest.fixture
    def service_file_content(self):
        """Read the codec compatibility service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'codec_compatibility_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_codec_info_method(self, service_file_content):
        """Test get_codec_info method exists"""
        assert 'def get_codec_info(' in service_file_content

    def test_codec_info_returns_dict(self, service_file_content):
        """Test get_codec_info returns Dict"""
        if 'def get_codec_info(' in service_file_content:
            idx = service_file_content.find('def get_codec_info(')
            method_sig = service_file_content[idx:idx+200]
            assert 'Dict' in method_sig


class TestTranscodingImpact:
    """Test transcoding impact measurement"""

    @pytest.fixture
    def service_file_content(self):
        """Read the codec compatibility service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'codec_compatibility_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_measure_transcoding_impact_method(self, service_file_content):
        """Test measure_transcoding_impact method exists"""
        assert 'def measure_transcoding_impact(' in service_file_content

    def test_transcoding_impact_returns_dict(self, service_file_content):
        """Test measure_transcoding_impact returns Dict"""
        if 'def measure_transcoding_impact(' in service_file_content:
            idx = service_file_content.find('def measure_transcoding_impact(')
            method_sig = service_file_content[idx:idx+250]
            assert 'Dict' in method_sig


class TestCodecRecommendation:
    """Test codec recommendation functionality"""

    @pytest.fixture
    def service_file_content(self):
        """Read the codec compatibility service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'codec_compatibility_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_recommend_codec_method(self, service_file_content):
        """Test recommend_codec method exists"""
        assert 'def recommend_codec(' in service_file_content

    def test_recommendation_returns_str_or_dict(self, service_file_content):
        """Test recommend_codec returns appropriate type"""
        if 'def recommend_codec(' in service_file_content:
            idx = service_file_content.find('def recommend_codec(')
            method_sig = service_file_content[idx:idx+200]
            assert 'str' in method_sig or 'Dict' in method_sig


class TestBitrateAnalysis:
    """Test bitrate analysis functionality"""

    @pytest.fixture
    def service_file_content(self):
        """Read the codec compatibility service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'codec_compatibility_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_analyze_bitrate_impact_method(self, service_file_content):
        """Test analyze_bitrate_impact method exists"""
        assert 'def analyze_bitrate_impact(' in service_file_content

    def test_bitrate_analysis_returns_dict(self, service_file_content):
        """Test analyze_bitrate_impact returns Dict"""
        if 'def analyze_bitrate_impact(' in service_file_content:
            idx = service_file_content.find('def analyze_bitrate_impact(')
            method_sig = service_file_content[idx:idx+250]
            assert 'Dict' in method_sig


class TestCodecCompatibilityMetrics:
    """Test comprehensive codec compatibility metrics"""

    @pytest.fixture
    def service_file_content(self):
        """Read the codec compatibility service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'codec_compatibility_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_compatibility_metrics_method(self, service_file_content):
        """Test get_compatibility_metrics method exists"""
        assert 'def get_compatibility_metrics(' in service_file_content

    def test_metrics_returns_dict(self, service_file_content):
        """Test get_compatibility_metrics returns Dict"""
        if 'def get_compatibility_metrics(' in service_file_content:
            idx = service_file_content.find('def get_compatibility_metrics(')
            method_sig = service_file_content[idx:idx+250]
            assert 'Dict' in method_sig


class TestTypeHints:
    """Test type hints for codec compatibility service"""

    @pytest.fixture
    def service_file_content(self):
        """Read the codec compatibility service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'codec_compatibility_service.py'
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
        """Read the codec compatibility service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'codec_compatibility_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        """Test module has docstring"""
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        """Test class has docstring"""
        if 'class CodecCompatibilityService' in service_file_content:
            idx = service_file_content.find('class CodecCompatibilityService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section


class TestSupportedCodecsList:
    """Test supported codecs list"""

    @pytest.fixture
    def service_file_content(self):
        """Read the codec compatibility service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'codec_compatibility_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_supported_codecs_method(self, service_file_content):
        """Test get_supported_codecs method exists"""
        assert 'def get_supported_codecs(' in service_file_content

    def test_supported_codecs_returns_list(self, service_file_content):
        """Test get_supported_codecs returns List"""
        if 'def get_supported_codecs(' in service_file_content:
            idx = service_file_content.find('def get_supported_codecs(')
            method_sig = service_file_content[idx:idx+200]
            assert 'List' in method_sig


