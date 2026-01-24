"""
Test suite for KnowledgeBaseService class-based implementation.

This ensures the knowledge_base_service.py has been converted from
function-based to class-based pattern.
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestKnowledgeBaseServiceClassExists:
    """Test that class-based service exists"""

    def test_service_file_exists(self):
        """Test that knowledge_base_service.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'knowledge_base_service.py'
        )
        assert os.path.exists(service_file)

    def test_class_exists(self):
        """Test that KnowledgeBaseService class exists"""
        from services.knowledge_base_service import KnowledgeBaseService
        assert KnowledgeBaseService is not None

    def test_class_is_importable(self):
        """Test class can be instantiated"""
        from services.knowledge_base_service import KnowledgeBaseService
        service = KnowledgeBaseService()
        assert service is not None


class TestKnowledgeBaseServiceMethods:
    """Test that class has required methods"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        from services.knowledge_base_service import KnowledgeBaseService
        return KnowledgeBaseService()

    def test_has_create_article_method(self, service):
        """Test create_article method exists"""
        assert hasattr(service, 'create_article')
        assert callable(getattr(service, 'create_article'))

    def test_has_get_article_method(self, service):
        """Test get_article method exists"""
        assert hasattr(service, 'get_article')
        assert callable(getattr(service, 'get_article'))

    def test_has_list_articles_method(self, service):
        """Test list_articles method exists"""
        assert hasattr(service, 'list_articles')
        assert callable(getattr(service, 'list_articles'))

    def test_has_update_article_method(self, service):
        """Test update_article method exists"""
        assert hasattr(service, 'update_article')
        assert callable(getattr(service, 'update_article'))

    def test_has_delete_article_method(self, service):
        """Test delete_article method exists"""
        assert hasattr(service, 'delete_article')
        assert callable(getattr(service, 'delete_article'))

    def test_has_search_articles_method(self, service):
        """Test search_articles method exists"""
        assert hasattr(service, 'search_articles')
        assert callable(getattr(service, 'search_articles'))


class TestKnowledgeBaseServiceConfiguration:
    """Test service configuration"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        from services.knowledge_base_service import KnowledgeBaseService
        return KnowledgeBaseService()

    def test_has_default_page_size(self, service):
        """Test service has default page size"""
        assert hasattr(service, 'default_page_size')

    def test_has_max_page_size(self, service):
        """Test service has max page size"""
        assert hasattr(service, 'max_page_size')


class TestBackwardCompatibility:
    """Test that function-based API still works"""

    def test_create_article_function_exists(self):
        """Test create_article function still exists"""
        from services.knowledge_base_service import create_article
        assert create_article is not None
        assert callable(create_article)

    def test_get_article_function_exists(self):
        """Test get_article function still exists"""
        from services.knowledge_base_service import get_article
        assert get_article is not None
        assert callable(get_article)

    def test_list_articles_function_exists(self):
        """Test list_articles function still exists"""
        from services.knowledge_base_service import list_articles
        assert list_articles is not None
        assert callable(list_articles)


class TestDocumentation:
    """Test documentation quality"""

    @pytest.fixture
    def service_file_content(self):
        """Read the service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'knowledge_base_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_class_docstring(self, service_file_content):
        """Test class has docstring"""
        assert 'class KnowledgeBaseService' in service_file_content
        idx = service_file_content.find('class KnowledgeBaseService')
        class_section = service_file_content[idx:idx+500]
        assert '"""' in class_section
