"""
Code Samples Service for voice AI testing.

This service provides code samples in multiple languages
including Python, JavaScript, cURL, and Postman collections.

Key features:
- Python examples
- JavaScript examples
- cURL examples
- Postman collection

Example:
    >>> service = CodeSamplesService()
    >>> result = service.get_python_example('create_test')
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class CodeSamplesService:
    """
    Service for code samples.

    Provides code examples in multiple languages
    and Postman collection generation.

    Example:
        >>> service = CodeSamplesService()
        >>> config = service.get_samples_config()
    """

    def __init__(self):
        """Initialize the code samples service."""
        self._samples: Dict[str, Dict[str, Any]] = {}
        self._collections: Dict[str, Dict[str, Any]] = {}
        self._supported_languages: List[str] = [
            'python', 'javascript', 'curl', 'go', 'ruby'
        ]

    def get_python_example(
        self,
        operation: str,
        endpoint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get Python code example.

        Args:
            operation: Operation name
            endpoint: API endpoint

        Returns:
            Dictionary with Python code

        Example:
            >>> result = service.get_python_example('create_test')
        """
        example_id = str(uuid.uuid4())

        code = f'''import requests

# {operation.replace('_', ' ').title()}
response = requests.post(
    "https://api.voiceai.test{endpoint or '/api/test-cases'}",
    headers={{
        "Authorization": "Bearer <token>",
        "Content-Type": "application/json"
    }},
    json={{
        "name": "Test Case 1",
        "description": "Example test case"
    }}
)

if response.ok:
    data = response.json()
    print(f"Created: {{data['id']}}")
else:
    print(f"Error: {{response.status_code}}")'''

        return {
            'example_id': example_id,
            'operation': operation,
            'language': 'python',
            'code': code,
            'generated_at': datetime.utcnow().isoformat()
        }

    def get_javascript_example(
        self,
        operation: str,
        endpoint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get JavaScript code example.

        Args:
            operation: Operation name
            endpoint: API endpoint

        Returns:
            Dictionary with JavaScript code

        Example:
            >>> result = service.get_javascript_example('create_test')
        """
        example_id = str(uuid.uuid4())

        code = f'''// {operation.replace('_', ' ').title()}
const response = await fetch(
    "https://api.voiceai.test{endpoint or '/api/test-cases'}",
    {{
        method: "POST",
        headers: {{
            "Authorization": "Bearer <token>",
            "Content-Type": "application/json"
        }},
        body: JSON.stringify({{
            name: "Test Case 1",
            description: "Example test case"
        }})
    }}
);

if (response.ok) {{
    const data = await response.json();
    console.log("Created:", data.id);
}} else {{
    console.error("Error:", response.status);
}}'''

        return {
            'example_id': example_id,
            'operation': operation,
            'language': 'javascript',
            'code': code,
            'generated_at': datetime.utcnow().isoformat()
        }

    def get_curl_example(
        self,
        operation: str,
        endpoint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get cURL code example.

        Args:
            operation: Operation name
            endpoint: API endpoint

        Returns:
            Dictionary with cURL command

        Example:
            >>> result = service.get_curl_example('create_test')
        """
        example_id = str(uuid.uuid4())

        code = f'''# {operation.replace('_', ' ').title()}
curl -X POST \\
    "https://api.voiceai.test{endpoint or '/api/test-cases'}" \\
    -H "Authorization: Bearer <token>" \\
    -H "Content-Type: application/json" \\
    -d '{{
        "name": "Test Case 1",
        "description": "Example test case"
    }}'
'''

        return {
            'example_id': example_id,
            'operation': operation,
            'language': 'curl',
            'code': code,
            'generated_at': datetime.utcnow().isoformat()
        }

    def list_languages(self) -> Dict[str, Any]:
        """
        List supported languages.

        Returns:
            Dictionary with languages

        Example:
            >>> result = service.list_languages()
        """
        return {
            'languages': self._supported_languages,
            'count': len(self._supported_languages),
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def generate_postman_collection(
        self,
        name: str = 'Voice AI API'
    ) -> Dict[str, Any]:
        """
        Generate Postman collection.

        Args:
            name: Collection name

        Returns:
            Dictionary with collection

        Example:
            >>> result = service.generate_postman_collection()
        """
        collection_id = str(uuid.uuid4())

        collection = {
            'info': {
                '_postman_id': collection_id,
                'name': name,
                'schema': 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json'
            },
            'item': [
                {
                    'name': 'Test Cases',
                    'item': [
                        {
                            'name': 'Create Test Case',
                            'request': {
                                'method': 'POST',
                                'url': '{{base_url}}/api/test-cases'
                            }
                        },
                        {
                            'name': 'List Test Cases',
                            'request': {
                                'method': 'GET',
                                'url': '{{base_url}}/api/test-cases'
                            }
                        }
                    ]
                }
            ]
        }

        self._collections[collection_id] = collection

        return {
            'collection_id': collection_id,
            'name': name,
            'collection': collection,
            'generated_at': datetime.utcnow().isoformat()
        }

    def export_collection(
        self,
        collection_id: str,
        format: str = 'json'
    ) -> Dict[str, Any]:
        """
        Export Postman collection.

        Args:
            collection_id: Collection identifier
            format: Export format

        Returns:
            Dictionary with export data

        Example:
            >>> result = service.export_collection('collection-1')
        """
        collection = self._collections.get(collection_id)
        if not collection:
            return {
                'collection_id': collection_id,
                'exported': False,
                'error': f'Collection not found: {collection_id}',
                'exported_at': datetime.utcnow().isoformat()
            }

        return {
            'collection_id': collection_id,
            'format': format,
            'data': collection,
            'exported': True,
            'exported_at': datetime.utcnow().isoformat()
        }

    def list_samples(
        self,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List available samples.

        Args:
            language: Filter by language

        Returns:
            Dictionary with samples

        Example:
            >>> result = service.list_samples()
        """
        samples = [
            {'id': 'create_test', 'name': 'Create Test Case'},
            {'id': 'run_test', 'name': 'Run Test'},
            {'id': 'get_results', 'name': 'Get Results'},
            {'id': 'validate', 'name': 'Submit Validation'}
        ]

        return {
            'samples': samples,
            'language': language,
            'count': len(samples),
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def get_sample(
        self,
        sample_id: str,
        language: str = 'python'
    ) -> Dict[str, Any]:
        """
        Get specific sample.

        Args:
            sample_id: Sample identifier
            language: Programming language

        Returns:
            Dictionary with sample

        Example:
            >>> result = service.get_sample('create_test', 'python')
        """
        if language == 'python':
            return self.get_python_example(sample_id)
        elif language == 'javascript':
            return self.get_javascript_example(sample_id)
        elif language == 'curl':
            return self.get_curl_example(sample_id)

        return {
            'sample_id': sample_id,
            'language': language,
            'found': False,
            'error': f'Unsupported language: {language}',
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def get_samples_config(self) -> Dict[str, Any]:
        """
        Get samples configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_samples_config()
        """
        return {
            'total_samples': len(self._samples),
            'total_collections': len(self._collections),
            'supported_languages': self._supported_languages,
            'features': [
                'multi_language', 'postman_export',
                'code_generation', 'sample_library'
            ]
        }
