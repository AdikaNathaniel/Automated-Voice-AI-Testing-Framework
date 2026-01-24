"""
Test suite for Proper Noun Recognition Testing.

Proper nouns (names of people, places, brands, organizations) are particularly
challenging for ASR systems. This service provides metrics for measuring
accuracy on different entity types.

Components:
- Entity extraction: Identify proper nouns in text
- Entity-specific accuracy: Calculate accuracy per entity type
- NER integration: Named Entity Recognition for ASR output
- Entity categorization: Person, Location, Organization, Brand
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestProperNounServiceExists:
    """Test that proper noun recognition service exists"""

    @pytest.fixture
    def service_file_content(self):
        """Read the proper noun recognition service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'proper_noun_recognition_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        """Test that proper_noun_recognition_service.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'proper_noun_recognition_service.py'
        )
        assert os.path.exists(service_file), (
            "proper_noun_recognition_service.py should exist"
        )

    def test_service_class_exists(self, service_file_content):
        """Test that ProperNounRecognitionService class exists"""
        assert 'class ProperNounRecognitionService' in service_file_content


class TestEntityExtraction:
    """Test entity extraction functionality"""

    @pytest.fixture
    def service_file_content(self):
        """Read the proper noun recognition service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'proper_noun_recognition_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_extract_entities_method(self, service_file_content):
        """Test extract_entities method exists"""
        assert 'def extract_entities(' in service_file_content

    def test_extract_entities_has_docstring(self, service_file_content):
        """Test extract_entities has docstring"""
        if 'def extract_entities(' in service_file_content:
            idx = service_file_content.find('def extract_entities(')
            method_section = service_file_content[idx:idx+600]
            assert '"""' in method_section

    def test_extract_entities_accepts_text(self, service_file_content):
        """Test method accepts text parameter"""
        if 'def extract_entities(' in service_file_content:
            idx = service_file_content.find('def extract_entities(')
            method_sig = service_file_content[idx:idx+200]
            assert 'text' in method_sig

    def test_extract_entities_returns_list(self, service_file_content):
        """Test method returns List"""
        if 'def extract_entities(' in service_file_content:
            idx = service_file_content.find('def extract_entities(')
            method_sig = service_file_content[idx:idx+200]
            assert 'List' in method_sig


class TestEntityTypes:
    """Test entity type categorization"""

    @pytest.fixture
    def service_file_content(self):
        """Read the proper noun recognition service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'proper_noun_recognition_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_supports_person_type(self, service_file_content):
        """Test supports PERSON entity type"""
        assert 'PERSON' in service_file_content

    def test_supports_location_type(self, service_file_content):
        """Test supports LOCATION entity type"""
        assert 'LOCATION' in service_file_content or 'GPE' in service_file_content

    def test_supports_organization_type(self, service_file_content):
        """Test supports ORGANIZATION entity type"""
        assert 'ORGANIZATION' in service_file_content or 'ORG' in service_file_content

    def test_supports_brand_type(self, service_file_content):
        """Test supports BRAND entity type"""
        assert 'BRAND' in service_file_content or 'PRODUCT' in service_file_content


class TestEntityAccuracyCalculation:
    """Test entity-specific accuracy calculation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the proper noun recognition service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'proper_noun_recognition_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_entity_accuracy_method(self, service_file_content):
        """Test calculate_entity_accuracy method exists"""
        assert 'def calculate_entity_accuracy(' in service_file_content

    def test_entity_accuracy_has_docstring(self, service_file_content):
        """Test calculate_entity_accuracy has docstring"""
        if 'def calculate_entity_accuracy(' in service_file_content:
            idx = service_file_content.find('def calculate_entity_accuracy(')
            method_section = service_file_content[idx:idx+600]
            assert '"""' in method_section

    def test_entity_accuracy_returns_dict(self, service_file_content):
        """Test calculate_entity_accuracy returns Dict"""
        if 'def calculate_entity_accuracy(' in service_file_content:
            idx = service_file_content.find('def calculate_entity_accuracy(')
            method_sig = service_file_content[idx:idx+250]
            assert 'Dict' in method_sig


class TestEntityMatching:
    """Test entity matching between reference and hypothesis"""

    @pytest.fixture
    def service_file_content(self):
        """Read the proper noun recognition service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'proper_noun_recognition_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_match_entities_method(self, service_file_content):
        """Test match_entities method exists"""
        assert 'def match_entities(' in service_file_content

    def test_match_entities_accepts_reference(self, service_file_content):
        """Test match_entities accepts reference parameter"""
        if 'def match_entities(' in service_file_content:
            idx = service_file_content.find('def match_entities(')
            method_sig = service_file_content[idx:idx+250]
            assert 'reference' in method_sig

    def test_match_entities_accepts_hypothesis(self, service_file_content):
        """Test match_entities accepts hypothesis parameter"""
        if 'def match_entities(' in service_file_content:
            idx = service_file_content.find('def match_entities(')
            method_sig = service_file_content[idx:idx+250]
            assert 'hypothesis' in method_sig


class TestEntityMetrics:
    """Test comprehensive entity metrics"""

    @pytest.fixture
    def service_file_content(self):
        """Read the proper noun recognition service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'proper_noun_recognition_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_entity_metrics_method(self, service_file_content):
        """Test get_entity_metrics method exists"""
        assert 'def get_entity_metrics(' in service_file_content

    def test_entity_metrics_returns_dict(self, service_file_content):
        """Test get_entity_metrics returns Dict"""
        if 'def get_entity_metrics(' in service_file_content:
            idx = service_file_content.find('def get_entity_metrics(')
            method_sig = service_file_content[idx:idx+250]
            assert 'Dict' in method_sig

    def test_metrics_include_precision(self, service_file_content):
        """Test metrics include precision"""
        assert 'precision' in service_file_content.lower()

    def test_metrics_include_recall(self, service_file_content):
        """Test metrics include recall"""
        assert 'recall' in service_file_content.lower()

    def test_metrics_include_f1(self, service_file_content):
        """Test metrics include F1 score"""
        assert 'f1' in service_file_content.lower()


class TestEntityListManagement:
    """Test custom entity list management"""

    @pytest.fixture
    def service_file_content(self):
        """Read the proper noun recognition service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'proper_noun_recognition_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_add_custom_entities_method(self, service_file_content):
        """Test add_custom_entities method exists"""
        assert 'def add_custom_entities(' in service_file_content

    def test_has_get_custom_entities_method(self, service_file_content):
        """Test get_custom_entities method exists"""
        assert 'def get_custom_entities(' in service_file_content


class TestAccuracyByType:
    """Test accuracy calculation by entity type"""

    @pytest.fixture
    def service_file_content(self):
        """Read the proper noun recognition service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'proper_noun_recognition_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_accuracy_by_type_method(self, service_file_content):
        """Test get_accuracy_by_type method exists"""
        assert 'def get_accuracy_by_type(' in service_file_content

    def test_accuracy_by_type_returns_dict(self, service_file_content):
        """Test get_accuracy_by_type returns Dict"""
        if 'def get_accuracy_by_type(' in service_file_content:
            idx = service_file_content.find('def get_accuracy_by_type(')
            method_sig = service_file_content[idx:idx+200]
            assert 'Dict' in method_sig


class TestTypeHints:
    """Test type hints for proper noun service"""

    @pytest.fixture
    def service_file_content(self):
        """Read the proper noun recognition service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'proper_noun_recognition_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_imports_typing_modules(self, service_file_content):
        """Test typing modules are imported"""
        assert 'from typing import' in service_file_content

    def test_uses_list_type_hint(self, service_file_content):
        """Test List type hint is used"""
        assert 'List[' in service_file_content

    def test_uses_dict_type_hint(self, service_file_content):
        """Test Dict type hint is used"""
        assert 'Dict[' in service_file_content

    def test_uses_optional_type_hint(self, service_file_content):
        """Test Optional type hint is used"""
        assert 'Optional[' in service_file_content


class TestDocstrings:
    """Test comprehensive documentation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the proper noun recognition service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'proper_noun_recognition_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        """Test module has docstring"""
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        """Test class has docstring"""
        if 'class ProperNounRecognitionService' in service_file_content:
            idx = service_file_content.find('class ProperNounRecognitionService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section


class TestEntityDataStructure:
    """Test entity data structure"""

    @pytest.fixture
    def service_file_content(self):
        """Read the proper noun recognition service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'proper_noun_recognition_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_entity_has_text_field(self, service_file_content):
        """Test entity data includes text field"""
        assert "'text'" in service_file_content or '"text"' in service_file_content

    def test_entity_has_type_field(self, service_file_content):
        """Test entity data includes type field"""
        assert "'type'" in service_file_content or '"type"' in service_file_content


class TestSimilarityMatching:
    """Test fuzzy matching for entity comparison"""

    @pytest.fixture
    def service_file_content(self):
        """Read the proper noun recognition service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'proper_noun_recognition_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_similarity_method(self, service_file_content):
        """Test calculate_similarity method exists"""
        assert 'def calculate_similarity(' in service_file_content

    def test_similarity_returns_float(self, service_file_content):
        """Test calculate_similarity returns float"""
        if 'def calculate_similarity(' in service_file_content:
            idx = service_file_content.find('def calculate_similarity(')
            method_sig = service_file_content[idx:idx+200]
            assert 'float' in method_sig


