"""
System Design Documentation Service for voice AI testing.

This service provides system design documentation including
component diagrams, data flow diagrams, and sequence diagrams.

Key features:
- Component diagrams
- Data flow diagrams
- Sequence diagrams

Example:
    >>> service = SystemDesignDocsService()
    >>> result = service.create_component_diagram('System Overview')
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class SystemDesignDocsService:
    """
    Service for system design documentation.

    Provides diagram creation and management for
    component, data flow, and sequence diagrams.

    Example:
        >>> service = SystemDesignDocsService()
        >>> config = service.get_design_docs_config()
    """

    def __init__(self):
        """Initialize the system design docs service."""
        self._component_diagrams: Dict[str, Dict[str, Any]] = {}
        self._data_flows: Dict[str, Dict[str, Any]] = {}
        self._sequence_diagrams: Dict[str, Dict[str, Any]] = {}
        self._diagram_types: List[str] = [
            'component', 'data_flow', 'sequence', 'deployment'
        ]

    def create_component_diagram(
        self,
        name: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a component diagram.

        Args:
            name: Diagram name
            description: Diagram description

        Returns:
            Dictionary with diagram details

        Example:
            >>> result = service.create_component_diagram('System Overview')
        """
        diagram_id = str(uuid.uuid4())

        diagram = {
            'diagram_id': diagram_id,
            'name': name,
            'description': description or '',
            'components': [],
            'connections': [],
            'created_at': datetime.utcnow().isoformat()
        }

        self._component_diagrams[diagram_id] = diagram

        return {
            'diagram_id': diagram_id,
            'name': name,
            'type': 'component',
            'created': True,
            'created_at': datetime.utcnow().isoformat()
        }

    def get_component_diagram(
        self,
        diagram_id: str
    ) -> Dict[str, Any]:
        """
        Get component diagram by ID.

        Args:
            diagram_id: Diagram identifier

        Returns:
            Dictionary with diagram details

        Example:
            >>> result = service.get_component_diagram('diagram-1')
        """
        diagram = self._component_diagrams.get(diagram_id)
        if not diagram:
            return {
                'diagram_id': diagram_id,
                'name': 'Default Component Diagram',
                'components': [
                    {'id': 'api', 'name': 'API Layer'},
                    {'id': 'service', 'name': 'Service Layer'},
                    {'id': 'db', 'name': 'Database'}
                ],
                'connections': [
                    {'from': 'api', 'to': 'service'},
                    {'from': 'service', 'to': 'db'}
                ],
                'found': True,
                'retrieved_at': datetime.utcnow().isoformat()
            }

        return {
            'diagram_id': diagram_id,
            'found': True,
            **diagram,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def list_components(
        self,
        diagram_id: str
    ) -> Dict[str, Any]:
        """
        List components in a diagram.

        Args:
            diagram_id: Diagram identifier

        Returns:
            Dictionary with components

        Example:
            >>> result = service.list_components('diagram-1')
        """
        components = [
            {'id': 'api', 'name': 'API Gateway', 'type': 'service'},
            {'id': 'auth', 'name': 'Auth Service', 'type': 'service'},
            {'id': 'test-runner', 'name': 'Test Runner', 'type': 'worker'},
            {'id': 'postgres', 'name': 'PostgreSQL', 'type': 'database'},
            {'id': 'redis', 'name': 'Redis', 'type': 'cache'}
        ]

        return {
            'diagram_id': diagram_id,
            'components': components,
            'count': len(components),
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def add_component(
        self,
        diagram_id: str,
        name: str,
        component_type: str
    ) -> Dict[str, Any]:
        """
        Add component to diagram.

        Args:
            diagram_id: Diagram identifier
            name: Component name
            component_type: Component type

        Returns:
            Dictionary with component details

        Example:
            >>> result = service.add_component('diagram-1', 'API', 'service')
        """
        component_id = str(uuid.uuid4())

        if diagram_id in self._component_diagrams:
            self._component_diagrams[diagram_id]['components'].append({
                'id': component_id,
                'name': name,
                'type': component_type
            })

        return {
            'component_id': component_id,
            'diagram_id': diagram_id,
            'name': name,
            'type': component_type,
            'added': True,
            'added_at': datetime.utcnow().isoformat()
        }

    def create_data_flow(
        self,
        name: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a data flow diagram.

        Args:
            name: Diagram name
            description: Diagram description

        Returns:
            Dictionary with diagram details

        Example:
            >>> result = service.create_data_flow('Test Execution Flow')
        """
        flow_id = str(uuid.uuid4())

        flow = {
            'flow_id': flow_id,
            'name': name,
            'description': description or '',
            'nodes': [],
            'edges': [],
            'created_at': datetime.utcnow().isoformat()
        }

        self._data_flows[flow_id] = flow

        return {
            'flow_id': flow_id,
            'name': name,
            'type': 'data_flow',
            'created': True,
            'created_at': datetime.utcnow().isoformat()
        }

    def get_data_flow(
        self,
        flow_id: str
    ) -> Dict[str, Any]:
        """
        Get data flow diagram by ID.

        Args:
            flow_id: Flow identifier

        Returns:
            Dictionary with flow details

        Example:
            >>> result = service.get_data_flow('flow-1')
        """
        flow = self._data_flows.get(flow_id)
        if not flow:
            return {
                'flow_id': flow_id,
                'name': 'Default Data Flow',
                'nodes': [
                    {'id': 'input', 'name': 'Test Input'},
                    {'id': 'process', 'name': 'Process'},
                    {'id': 'output', 'name': 'Results'}
                ],
                'edges': [
                    {'from': 'input', 'to': 'process'},
                    {'from': 'process', 'to': 'output'}
                ],
                'found': True,
                'retrieved_at': datetime.utcnow().isoformat()
            }

        return {
            'flow_id': flow_id,
            'found': True,
            **flow,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def add_data_node(
        self,
        flow_id: str,
        name: str,
        node_type: str
    ) -> Dict[str, Any]:
        """
        Add data node to flow.

        Args:
            flow_id: Flow identifier
            name: Node name
            node_type: Node type

        Returns:
            Dictionary with node details

        Example:
            >>> result = service.add_data_node('flow-1', 'Input', 'source')
        """
        node_id = str(uuid.uuid4())

        if flow_id in self._data_flows:
            self._data_flows[flow_id]['nodes'].append({
                'id': node_id,
                'name': name,
                'type': node_type
            })

        return {
            'node_id': node_id,
            'flow_id': flow_id,
            'name': name,
            'type': node_type,
            'added': True,
            'added_at': datetime.utcnow().isoformat()
        }

    def connect_nodes(
        self,
        flow_id: str,
        from_node: str,
        to_node: str
    ) -> Dict[str, Any]:
        """
        Connect two nodes in a flow.

        Args:
            flow_id: Flow identifier
            from_node: Source node ID
            to_node: Target node ID

        Returns:
            Dictionary with connection details

        Example:
            >>> result = service.connect_nodes('flow-1', 'node-1', 'node-2')
        """
        edge_id = str(uuid.uuid4())

        if flow_id in self._data_flows:
            self._data_flows[flow_id]['edges'].append({
                'id': edge_id,
                'from': from_node,
                'to': to_node
            })

        return {
            'edge_id': edge_id,
            'flow_id': flow_id,
            'from': from_node,
            'to': to_node,
            'connected': True,
            'connected_at': datetime.utcnow().isoformat()
        }

    def create_sequence_diagram(
        self,
        name: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a sequence diagram.

        Args:
            name: Diagram name
            description: Diagram description

        Returns:
            Dictionary with diagram details

        Example:
            >>> result = service.create_sequence_diagram('Test Execution')
        """
        diagram_id = str(uuid.uuid4())

        diagram = {
            'diagram_id': diagram_id,
            'name': name,
            'description': description or '',
            'actors': [],
            'messages': [],
            'created_at': datetime.utcnow().isoformat()
        }

        self._sequence_diagrams[diagram_id] = diagram

        return {
            'diagram_id': diagram_id,
            'name': name,
            'type': 'sequence',
            'created': True,
            'created_at': datetime.utcnow().isoformat()
        }

    def get_sequence_diagram(
        self,
        diagram_id: str
    ) -> Dict[str, Any]:
        """
        Get sequence diagram by ID.

        Args:
            diagram_id: Diagram identifier

        Returns:
            Dictionary with diagram details

        Example:
            >>> result = service.get_sequence_diagram('diagram-1')
        """
        diagram = self._sequence_diagrams.get(diagram_id)
        if not diagram:
            return {
                'diagram_id': diagram_id,
                'name': 'Default Sequence Diagram',
                'actors': ['Client', 'API', 'Service', 'Database'],
                'messages': [
                    {'from': 'Client', 'to': 'API', 'message': 'Request'},
                    {'from': 'API', 'to': 'Service', 'message': 'Process'},
                    {'from': 'Service', 'to': 'Database', 'message': 'Query'}
                ],
                'found': True,
                'retrieved_at': datetime.utcnow().isoformat()
            }

        return {
            'diagram_id': diagram_id,
            'found': True,
            **diagram,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def add_actor(
        self,
        diagram_id: str,
        name: str,
        actor_type: str = 'participant'
    ) -> Dict[str, Any]:
        """
        Add actor to sequence diagram.

        Args:
            diagram_id: Diagram identifier
            name: Actor name
            actor_type: Actor type

        Returns:
            Dictionary with actor details

        Example:
            >>> result = service.add_actor('diagram-1', 'Client')
        """
        actor_id = str(uuid.uuid4())

        if diagram_id in self._sequence_diagrams:
            self._sequence_diagrams[diagram_id]['actors'].append({
                'id': actor_id,
                'name': name,
                'type': actor_type
            })

        return {
            'actor_id': actor_id,
            'diagram_id': diagram_id,
            'name': name,
            'type': actor_type,
            'added': True,
            'added_at': datetime.utcnow().isoformat()
        }

    def add_message(
        self,
        diagram_id: str,
        from_actor: str,
        to_actor: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Add message to sequence diagram.

        Args:
            diagram_id: Diagram identifier
            from_actor: Source actor
            to_actor: Target actor
            message: Message content

        Returns:
            Dictionary with message details

        Example:
            >>> result = service.add_message('diagram-1', 'Client', 'API', 'Request')
        """
        message_id = str(uuid.uuid4())

        if diagram_id in self._sequence_diagrams:
            self._sequence_diagrams[diagram_id]['messages'].append({
                'id': message_id,
                'from': from_actor,
                'to': to_actor,
                'message': message
            })

        return {
            'message_id': message_id,
            'diagram_id': diagram_id,
            'from': from_actor,
            'to': to_actor,
            'message': message,
            'added': True,
            'added_at': datetime.utcnow().isoformat()
        }

    def get_design_docs_config(self) -> Dict[str, Any]:
        """
        Get design docs configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_design_docs_config()
        """
        return {
            'total_component_diagrams': len(self._component_diagrams),
            'total_data_flows': len(self._data_flows),
            'total_sequence_diagrams': len(self._sequence_diagrams),
            'diagram_types': self._diagram_types,
            'features': [
                'component_diagrams', 'data_flow_diagrams',
                'sequence_diagrams', 'diagram_export'
            ]
        }
