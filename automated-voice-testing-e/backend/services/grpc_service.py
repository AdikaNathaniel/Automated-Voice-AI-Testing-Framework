"""
gRPC Service for voice AI testing.

This service provides gRPC API capabilities including
protobuf schema definition, service handlers, and audio streaming.

Key features:
- Protobuf schema definition
- gRPC service handlers
- Bidirectional streaming for audio

Example:
    >>> service = GRPCService()
    >>> result = service.define_service('TestRunner')
"""

from typing import List, Dict, Any, Optional, Callable, Iterator
from datetime import datetime
import uuid


class GRPCService:
    """
    Service for gRPC API management.

    Provides protobuf schema definition, service
    registration, and bidirectional streaming.

    Example:
        >>> service = GRPCService()
        >>> config = service.get_grpc_config()
    """

    def __init__(self):
        """Initialize the gRPC service."""
        self._services: Dict[str, Dict[str, Any]] = {}
        self._message_types: Dict[str, Dict[str, Any]] = {}
        self._handlers: Dict[str, Callable] = {}
        self._streams: List[Dict[str, Any]] = []
        self._port: int = 50051

    def define_service(
        self,
        service_name: str,
        methods: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Define a gRPC service.

        Args:
            service_name: Name of the service
            methods: List of method definitions

        Returns:
            Dictionary with service definition

        Example:
            >>> result = service.define_service('TestRunner')
        """
        service_id = str(uuid.uuid4())

        self._services[service_name] = {
            'id': service_id,
            'name': service_name,
            'methods': methods or [],
            'created_at': datetime.utcnow().isoformat()
        }

        return {
            'service_id': service_id,
            'name': service_name,
            'methods_count': len(methods or []),
            'status': 'defined',
            'defined_at': datetime.utcnow().isoformat()
        }

    def register_message_type(
        self,
        type_name: str,
        fields: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Register a protobuf message type.

        Args:
            type_name: Name of the message type
            fields: Field definitions

        Returns:
            Dictionary with registration result

        Example:
            >>> result = service.register_message_type('TestResult', fields)
        """
        self._message_types[type_name] = {
            'name': type_name,
            'fields': fields,
            'registered_at': datetime.utcnow().isoformat()
        }

        return {
            'type_name': type_name,
            'fields_count': len(fields),
            'status': 'registered',
            'registered_at': datetime.utcnow().isoformat()
        }

    def register_handler(
        self,
        service_name: str,
        method_name: str,
        handler: Callable
    ) -> Dict[str, Any]:
        """
        Register a method handler.

        Args:
            service_name: Service name
            method_name: Method name
            handler: Handler function

        Returns:
            Dictionary with registration result

        Example:
            >>> result = service.register_handler('TestRunner', 'Run', handler)
        """
        key = f"{service_name}.{method_name}"
        self._handlers[key] = handler

        return {
            'service': service_name,
            'method': method_name,
            'status': 'registered',
            'total_handlers': len(self._handlers),
            'registered_at': datetime.utcnow().isoformat()
        }

    def call(
        self,
        service_name: str,
        method_name: str,
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call a gRPC method.

        Args:
            service_name: Service name
            method_name: Method name
            request: Request data

        Returns:
            Dictionary with call result

        Example:
            >>> result = service.call('TestRunner', 'Run', request)
        """
        key = f"{service_name}.{method_name}"
        handler = self._handlers.get(key)

        if handler:
            try:
                response = handler(request)
                return {
                    'response': response,
                    'status': 'success',
                    'called_at': datetime.utcnow().isoformat()
                }
            except Exception as e:
                return {
                    'response': None,
                    'status': 'error',
                    'error': str(e),
                    'called_at': datetime.utcnow().isoformat()
                }

        return {
            'response': None,
            'status': 'error',
            'error': f'No handler for {key}',
            'called_at': datetime.utcnow().isoformat()
        }

    def create_stream(
        self,
        stream_type: str = 'bidirectional'
    ) -> Dict[str, Any]:
        """
        Create a streaming connection.

        Args:
            stream_type: Type of stream

        Returns:
            Dictionary with stream details

        Example:
            >>> result = service.create_stream('bidirectional')
        """
        stream_id = str(uuid.uuid4())

        stream = {
            'stream_id': stream_id,
            'type': stream_type,
            'status': 'created',
            'created_at': datetime.utcnow().isoformat()
        }

        self._streams.append(stream)

        return stream

    def stream_audio(
        self,
        stream_id: str,
        audio_chunks: Iterator[bytes]
    ) -> Dict[str, Any]:
        """
        Stream audio data bidirectionally.

        Args:
            stream_id: Stream identifier
            audio_chunks: Iterator of audio data

        Returns:
            Dictionary with streaming result

        Example:
            >>> result = service.stream_audio('stream-123', chunks)
        """
        chunks_processed = 0
        for _ in audio_chunks:
            chunks_processed += 1

        return {
            'stream_id': stream_id,
            'chunks_processed': chunks_processed,
            'status': 'completed',
            'completed_at': datetime.utcnow().isoformat()
        }

    def get_grpc_config(self) -> Dict[str, Any]:
        """
        Get gRPC configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_grpc_config()
        """
        return {
            'port': self._port,
            'total_services': len(self._services),
            'total_message_types': len(self._message_types),
            'total_handlers': len(self._handlers),
            'active_streams': len(self._streams),
            'features': [
                'unary', 'server_streaming',
                'client_streaming', 'bidirectional'
            ]
        }
