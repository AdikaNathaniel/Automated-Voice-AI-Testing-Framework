"""
TypeScript SDK Service for voice AI testing.

This service provides TypeScript/JavaScript SDK generation
capabilities for browser and Node.js environments.

Key features:
- Browser and Node.js client support
- TypeScript type generation
- Promise-based API
- npm package generation

Example:
    >>> service = TypeScriptSDKService()
    >>> client = service.generate_client('v1')
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class TypeScriptSDKService:
    """
    Service for TypeScript SDK management.

    Provides client generation for browser and Node.js,
    type generation, and npm package support.

    Example:
        >>> service = TypeScriptSDKService()
        >>> config = service.get_sdk_config()
    """

    def __init__(self):
        """Initialize the TypeScript SDK service."""
        self._clients: List[Dict[str, Any]] = []
        self._sdk_version: str = '1.0.0'
        self._typescript_version: str = '5.0'

    def generate_client(
        self,
        api_version: str,
        base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a TypeScript client for the API.

        Args:
            api_version: API version to target
            base_url: Base URL for the API

        Returns:
            Dictionary with client details

        Example:
            >>> client = service.generate_client('v1')
        """
        client_id = str(uuid.uuid4())

        client = {
            'client_id': client_id,
            'api_version': api_version,
            'base_url': base_url or 'https://api.voiceai.com',
            'typescript': True,
            'targets': ['browser', 'node'],
            'generated_at': datetime.utcnow().isoformat()
        }

        self._clients.append(client)

        return client

    def generate_types(
        self,
        api_version: str
    ) -> Dict[str, Any]:
        """
        Generate TypeScript type definitions.

        Args:
            api_version: API version

        Returns:
            Dictionary with type definitions

        Example:
            >>> types = service.generate_types('v1')
        """
        types_id = str(uuid.uuid4())

        return {
            'types_id': types_id,
            'api_version': api_version,
            'files': [
                'index.d.ts',
                'models.d.ts',
                'client.d.ts',
                'responses.d.ts'
            ],
            'strict': True,
            'generated_at': datetime.utcnow().isoformat()
        }

    def create_browser_bundle(
        self,
        format_type: str = 'esm'
    ) -> Dict[str, Any]:
        """
        Create browser-optimized bundle.

        Args:
            format_type: Bundle format (esm, umd, iife)

        Returns:
            Dictionary with bundle details

        Example:
            >>> bundle = service.create_browser_bundle('esm')
        """
        bundle_id = str(uuid.uuid4())

        return {
            'bundle_id': bundle_id,
            'format': format_type,
            'minified': True,
            'sourcemap': True,
            'files': [
                f'voiceai-sdk.{format_type}.js',
                f'voiceai-sdk.{format_type}.min.js',
                f'voiceai-sdk.{format_type}.js.map'
            ],
            'generated_at': datetime.utcnow().isoformat()
        }

    def create_node_package(
        self,
        include_esm: bool = True
    ) -> Dict[str, Any]:
        """
        Create Node.js package.

        Args:
            include_esm: Include ESM support

        Returns:
            Dictionary with package details

        Example:
            >>> package = service.create_node_package()
        """
        package_id = str(uuid.uuid4())

        return {
            'package_id': package_id,
            'cjs': True,
            'esm': include_esm,
            'node_versions': ['18', '20', '22'],
            'files': [
                'dist/index.js',
                'dist/index.mjs' if include_esm else None,
                'dist/index.d.ts'
            ],
            'generated_at': datetime.utcnow().isoformat()
        }

    def generate_npm_package(
        self,
        package_name: str = '@voiceai/sdk'
    ) -> Dict[str, Any]:
        """
        Generate npm package.

        Args:
            package_name: Name for the package

        Returns:
            Dictionary with package details

        Example:
            >>> package = service.generate_npm_package()
        """
        package_id = str(uuid.uuid4())

        return {
            'package_id': package_id,
            'name': package_name,
            'version': self._sdk_version,
            'main': 'dist/index.js',
            'module': 'dist/index.mjs',
            'types': 'dist/index.d.ts',
            'engines': {'node': '>=18'},
            'dependencies': [
                'axios',
                'typescript'
            ],
            'files': [
                'package.json',
                'README.md',
                'dist/',
                'src/'
            ],
            'generated_at': datetime.utcnow().isoformat()
        }

    def get_installation_command(
        self,
        package_name: str = '@voiceai/sdk'
    ) -> Dict[str, Any]:
        """
        Get package installation commands.

        Args:
            package_name: Package name

        Returns:
            Dictionary with installation commands

        Example:
            >>> cmd = service.get_installation_command()
        """
        return {
            'npm': f'npm install {package_name}',
            'yarn': f'yarn add {package_name}',
            'pnpm': f'pnpm add {package_name}',
            'bun': f'bun add {package_name}',
            'cdn': f'https://unpkg.com/{package_name}@latest/dist/voiceai-sdk.esm.js',
            'generated_at': datetime.utcnow().isoformat()
        }

    def get_sdk_config(self) -> Dict[str, Any]:
        """
        Get SDK configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_sdk_config()
        """
        return {
            'sdk_version': self._sdk_version,
            'typescript_version': self._typescript_version,
            'total_clients': len(self._clients),
            'platforms': ['browser', 'node'],
            'bundle_formats': ['esm', 'cjs', 'umd', 'iife'],
            'features': [
                'typescript', 'promise_api',
                'browser_support', 'node_support',
                'tree_shaking'
            ]
        }
