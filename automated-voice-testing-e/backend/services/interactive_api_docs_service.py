"""
Interactive API Docs Service for voice AI testing.

This service provides interactive API documentation including
try-it-out functionality, examples, and authentication guides.

Key features:
- Try-it-out functionality
- Request/response examples
- Authentication setup guide

Example:
    >>> service = InteractiveApiDocsService()
    >>> result = service.get_examples('/api/test-cases')
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class InteractiveApiDocsService:
    """
    Service for interactive API documentation.

    Provides try-it-out functionality, examples,
    and authentication guides.

    Example:
        >>> service = InteractiveApiDocsService()
        >>> config = service.get_docs_config()
    """

    def __init__(self):
        """Initialize the interactive API docs service."""
        self._endpoints: Dict[str, Dict[str, Any]] = {}
        self._examples: Dict[str, List[Dict[str, Any]]] = {}
        self._request_history: Dict[str, List[Dict[str, Any]]] = {}
        self._auth_types: List[str] = ['bearer', 'api_key', 'oauth2']

    def execute_request(
        self,
        endpoint: str,
        method: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute API request.

        Args:
            endpoint: API endpoint
            method: HTTP method
            headers: Request headers
            body: Request body

        Returns:
            Dictionary with response

        Example:
            >>> result = service.execute_request('/api/tests', 'GET')
        """
        request_id = str(uuid.uuid4())

        # Simulated response
        response = {
            'status': 200,
            'body': {'message': 'Success'},
            'headers': {'Content-Type': 'application/json'}
        }

        # Store in history
        if endpoint not in self._request_history:
            self._request_history[endpoint] = []

        self._request_history[endpoint].append({
            'request_id': request_id,
            'method': method,
            'headers': headers or {},
            'body': body,
            'response': response,
            'executed_at': datetime.utcnow().isoformat()
        })

        return {
            'request_id': request_id,
            'endpoint': endpoint,
            'method': method,
            'response': response,
            'executed_at': datetime.utcnow().isoformat()
        }

    def validate_request(
        self,
        endpoint: str,
        method: str,
        body: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate API request.

        Args:
            endpoint: API endpoint
            method: HTTP method
            body: Request body

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_request('/api/tests', 'POST', data)
        """
        validation_id = str(uuid.uuid4())

        errors = []
        warnings = []

        # Simulated validation
        if not endpoint.startswith('/'):
            errors.append({
                'field': 'endpoint',
                'message': 'Endpoint must start with /'
            })

        return {
            'validation_id': validation_id,
            'endpoint': endpoint,
            'method': method,
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'validated_at': datetime.utcnow().isoformat()
        }

    def get_request_history(
        self,
        endpoint: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get request history.

        Args:
            endpoint: Filter by endpoint
            limit: Maximum items

        Returns:
            Dictionary with history

        Example:
            >>> result = service.get_request_history('/api/tests')
        """
        if endpoint:
            history = self._request_history.get(endpoint, [])[-limit:]
        else:
            history = []
            for ep_history in self._request_history.values():
                history.extend(ep_history)
            history = history[-limit:]

        return {
            'endpoint': endpoint,
            'history': history,
            'count': len(history),
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def get_examples(
        self,
        endpoint: str
    ) -> Dict[str, Any]:
        """
        Get request/response examples.

        Args:
            endpoint: API endpoint

        Returns:
            Dictionary with examples

        Example:
            >>> result = service.get_examples('/api/tests')
        """
        examples = self._examples.get(endpoint, [
            {
                'name': 'Basic Request',
                'request': {
                    'method': 'GET',
                    'headers': {'Authorization': 'Bearer <token>'}
                },
                'response': {
                    'status': 200,
                    'body': {'data': []}
                }
            }
        ])

        return {
            'endpoint': endpoint,
            'examples': examples,
            'count': len(examples),
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def generate_example(
        self,
        endpoint: str,
        method: str,
        language: str = 'python'
    ) -> Dict[str, Any]:
        """
        Generate code example.

        Args:
            endpoint: API endpoint
            method: HTTP method
            language: Programming language

        Returns:
            Dictionary with generated code

        Example:
            >>> result = service.generate_example('/api/tests', 'GET')
        """
        example_id = str(uuid.uuid4())

        code = {
            'python': f'''import requests

response = requests.{method.lower()}(
    "https://api.voiceai.test{endpoint}",
    headers={{"Authorization": "Bearer <token>"}}
)
print(response.json())''',
            'javascript': f'''fetch("https://api.voiceai.test{endpoint}", {{
    method: "{method}",
    headers: {{"Authorization": "Bearer <token>"}}
}})
.then(res => res.json())
.then(data => console.log(data));''',
            'curl': f'''curl -X {method} \\
    "https://api.voiceai.test{endpoint}" \\
    -H "Authorization: Bearer <token>"'''
        }.get(language, '')

        return {
            'example_id': example_id,
            'endpoint': endpoint,
            'method': method,
            'language': language,
            'code': code,
            'generated_at': datetime.utcnow().isoformat()
        }

    def list_endpoints(
        self,
        tag: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List API endpoints.

        Args:
            tag: Filter by tag

        Returns:
            Dictionary with endpoints

        Example:
            >>> result = service.list_endpoints()
        """
        endpoints = [
            {
                'path': '/api/test-cases',
                'methods': ['GET', 'POST'],
                'tags': ['test-cases']
            },
            {
                'path': '/api/test-runs',
                'methods': ['GET', 'POST'],
                'tags': ['test-runs']
            },
            {
                'path': '/api/validations',
                'methods': ['GET', 'POST'],
                'tags': ['validations']
            }
        ]

        if tag:
            endpoints = [e for e in endpoints if tag in e.get('tags', [])]

        return {
            'endpoints': endpoints,
            'count': len(endpoints),
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def get_auth_guide(
        self,
        auth_type: str = 'bearer'
    ) -> Dict[str, Any]:
        """
        Get authentication setup guide.

        Args:
            auth_type: Authentication type

        Returns:
            Dictionary with guide

        Example:
            >>> result = service.get_auth_guide('bearer')
        """
        guides = {
            'bearer': {
                'title': 'Bearer Token Authentication',
                'steps': [
                    'Obtain API key from settings',
                    'Add Authorization header',
                    'Use format: Bearer <token>'
                ],
                'example': 'Authorization: Bearer eyJhbGc...'
            },
            'api_key': {
                'title': 'API Key Authentication',
                'steps': [
                    'Generate API key',
                    'Add X-API-Key header'
                ],
                'example': 'X-API-Key: your-api-key'
            }
        }

        guide = guides.get(auth_type, guides['bearer'])

        return {
            'auth_type': auth_type,
            'guide': guide,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def test_auth(
        self,
        auth_type: str,
        credentials: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Test authentication.

        Args:
            auth_type: Authentication type
            credentials: Auth credentials

        Returns:
            Dictionary with test result

        Example:
            >>> result = service.test_auth('bearer', {'token': '...'})
        """
        test_id = str(uuid.uuid4())

        # Simulated auth test
        valid = bool(credentials.get('token') or credentials.get('api_key'))

        return {
            'test_id': test_id,
            'auth_type': auth_type,
            'valid': valid,
            'message': 'Authentication successful' if valid else 'Invalid credentials',
            'tested_at': datetime.utcnow().isoformat()
        }

    def get_auth_types(self) -> Dict[str, Any]:
        """
        Get supported auth types.

        Returns:
            Dictionary with auth types

        Example:
            >>> result = service.get_auth_types()
        """
        return {
            'auth_types': self._auth_types,
            'count': len(self._auth_types),
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def get_docs_config(self) -> Dict[str, Any]:
        """
        Get docs configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_docs_config()
        """
        return {
            'total_endpoints': len(self._endpoints),
            'total_examples': sum(len(e) for e in self._examples.values()),
            'auth_types': self._auth_types,
            'features': [
                'try_it_out', 'code_examples',
                'auth_guides', 'request_history'
            ]
        }
