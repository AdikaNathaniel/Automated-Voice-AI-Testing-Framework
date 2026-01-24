"""
Multi-turn Conversation Flows Service for voice AI testing.

This service provides multi-turn conversation testing capabilities
including dialog trees, handoff scenarios, and escalation testing.

Key features:
- Complex dialog tree management
- Handoff scenario orchestration
- Escalation rule testing

Example:
    >>> service = MultiTurnConversationService()
    >>> tree = service.create_dialog_tree(name='support_flow')
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class MultiTurnConversationService:
    """
    Service for multi-turn conversation flow testing.

    Provides tools for testing complex dialog trees, handoff
    scenarios, and escalation rules.

    Example:
        >>> service = MultiTurnConversationService()
        >>> config = service.get_conversation_flow_config()
    """

    def __init__(self):
        """Initialize the multi-turn conversation service."""
        self._dialog_trees: Dict[str, Dict[str, Any]] = {}
        self._handoffs: Dict[str, Dict[str, Any]] = {}
        self._escalation_rules: Dict[str, Dict[str, Any]] = {}
        self._escalation_history: List[Dict[str, Any]] = []

    def create_dialog_tree(
        self,
        name: str,
        description: Optional[str] = None,
        root_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new dialog tree.

        Args:
            name: Name of the dialog tree
            description: Optional description
            root_prompt: Optional root node prompt

        Returns:
            Dictionary with dialog tree details

        Example:
            >>> tree = service.create_dialog_tree('billing_support')
        """
        tree_id = str(uuid.uuid4())

        tree = {
            'tree_id': tree_id,
            'name': name,
            'description': description or f'Dialog tree: {name}',
            'root_prompt': root_prompt or 'How can I help you today?',
            'nodes': {},
            'edges': [],
            'created_at': datetime.utcnow().isoformat()
        }

        self._dialog_trees[tree_id] = tree

        return {
            'tree_id': tree_id,
            'name': name,
            'description': tree['description'],
            'success': True,
            'created_at': tree['created_at']
        }

    def add_dialog_node(
        self,
        tree_id: str,
        node_id: str,
        prompt: str,
        responses: Optional[List[str]] = None,
        parent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a node to a dialog tree.

        Args:
            tree_id: Dialog tree identifier
            node_id: Unique node identifier
            prompt: Node prompt text
            responses: Expected response options
            parent_id: Parent node identifier

        Returns:
            Dictionary with node details

        Example:
            >>> node = service.add_dialog_node('tree_123', 'node_1', 'Select option')
        """
        if tree_id not in self._dialog_trees:
            return {
                'success': False,
                'error': f'Tree {tree_id} not found'
            }

        responses = responses or []

        node = {
            'node_id': node_id,
            'prompt': prompt,
            'responses': responses,
            'parent_id': parent_id,
            'children': [],
            'added_at': datetime.utcnow().isoformat()
        }

        self._dialog_trees[tree_id]['nodes'][node_id] = node

        if parent_id and parent_id in self._dialog_trees[tree_id]['nodes']:
            self._dialog_trees[tree_id]['nodes'][parent_id]['children'].append(node_id)
            self._dialog_trees[tree_id]['edges'].append({
                'from': parent_id,
                'to': node_id
            })

        return {
            'node_id': node_id,
            'tree_id': tree_id,
            'prompt': prompt,
            'response_count': len(responses),
            'success': True,
            'added_at': node['added_at']
        }

    def traverse_dialog(
        self,
        tree_id: str,
        user_inputs: List[str],
        start_node: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Traverse a dialog tree with user inputs.

        Args:
            tree_id: Dialog tree identifier
            user_inputs: Sequence of user inputs
            start_node: Optional starting node

        Returns:
            Dictionary with traversal result

        Example:
            >>> result = service.traverse_dialog('tree_123', ['1', '2', '3'])
        """
        traversal_id = str(uuid.uuid4())

        if tree_id not in self._dialog_trees:
            return {
                'traversal_id': traversal_id,
                'success': False,
                'error': f'Tree {tree_id} not found'
            }

        tree = self._dialog_trees[tree_id]
        nodes_visited = []
        current_node = start_node

        for i, user_input in enumerate(user_inputs):
            if current_node:
                nodes_visited.append(current_node)
                if current_node in tree['nodes']:
                    children = tree['nodes'][current_node].get('children', [])
                    if children:
                        current_node = children[0] if children else None
                    else:
                        current_node = None
            else:
                nodes_visited.append(f'virtual_node_{i}')

        return {
            'traversal_id': traversal_id,
            'tree_id': tree_id,
            'inputs_processed': len(user_inputs),
            'nodes_visited': nodes_visited,
            'final_node': current_node,
            'completed': current_node is None or len(user_inputs) == 0,
            'success': True,
            'traversed_at': datetime.utcnow().isoformat()
        }

    def validate_dialog_flow(
        self,
        tree_id: str,
        expected_path: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Validate a dialog flow structure.

        Args:
            tree_id: Dialog tree identifier
            expected_path: Optional expected node path

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_dialog_flow('tree_123')
        """
        validation_id = str(uuid.uuid4())

        if tree_id not in self._dialog_trees:
            return {
                'validation_id': validation_id,
                'valid': False,
                'error': f'Tree {tree_id} not found'
            }

        tree = self._dialog_trees[tree_id]
        nodes = tree['nodes']
        edges = tree['edges']

        # Check for orphan nodes
        orphans = []
        for node_id, node in nodes.items():
            if not node['parent_id'] and node_id != 'root':
                has_incoming = any(e['to'] == node_id for e in edges)
                if not has_incoming and len(nodes) > 1:
                    orphans.append(node_id)

        # Validate expected path if provided
        path_valid = True
        if expected_path:
            for i, node_id in enumerate(expected_path):
                if node_id not in nodes:
                    path_valid = False
                    break

        return {
            'validation_id': validation_id,
            'tree_id': tree_id,
            'total_nodes': len(nodes),
            'total_edges': len(edges),
            'orphan_nodes': orphans,
            'path_valid': path_valid,
            'valid': len(orphans) == 0 and path_valid,
            'validated_at': datetime.utcnow().isoformat()
        }

    def create_handoff(
        self,
        conversation_id: str,
        source_agent: str,
        target_agent: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a handoff scenario.

        Args:
            conversation_id: Conversation identifier
            source_agent: Source agent type
            target_agent: Target agent type
            reason: Handoff reason

        Returns:
            Dictionary with handoff details

        Example:
            >>> handoff = service.create_handoff('conv_123', 'bot', 'human')
        """
        handoff_id = str(uuid.uuid4())

        handoff = {
            'handoff_id': handoff_id,
            'conversation_id': conversation_id,
            'source_agent': source_agent,
            'target_agent': target_agent,
            'reason': reason or 'User requested',
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat(),
            'triggered_at': None,
            'completed_at': None
        }

        self._handoffs[handoff_id] = handoff

        return {
            'handoff_id': handoff_id,
            'conversation_id': conversation_id,
            'source_agent': source_agent,
            'target_agent': target_agent,
            'status': 'pending',
            'success': True,
            'created_at': handoff['created_at']
        }

    def trigger_handoff(
        self,
        handoff_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Trigger a handoff.

        Args:
            handoff_id: Handoff identifier
            context: Optional context data

        Returns:
            Dictionary with trigger result

        Example:
            >>> result = service.trigger_handoff('handoff_123')
        """
        if handoff_id not in self._handoffs:
            return {
                'success': False,
                'error': f'Handoff {handoff_id} not found'
            }

        handoff = self._handoffs[handoff_id]
        handoff['status'] = 'in_progress'
        handoff['triggered_at'] = datetime.utcnow().isoformat()
        handoff['context'] = context or {}

        return {
            'handoff_id': handoff_id,
            'status': 'in_progress',
            'source_agent': handoff['source_agent'],
            'target_agent': handoff['target_agent'],
            'success': True,
            'triggered_at': handoff['triggered_at']
        }

    def get_handoff_status(
        self,
        handoff_id: str
    ) -> Dict[str, Any]:
        """
        Get handoff status.

        Args:
            handoff_id: Handoff identifier

        Returns:
            Dictionary with handoff status

        Example:
            >>> status = service.get_handoff_status('handoff_123')
        """
        if handoff_id not in self._handoffs:
            return {
                'success': False,
                'error': f'Handoff {handoff_id} not found'
            }

        handoff = self._handoffs[handoff_id]

        return {
            'handoff_id': handoff_id,
            'conversation_id': handoff['conversation_id'],
            'status': handoff['status'],
            'source_agent': handoff['source_agent'],
            'target_agent': handoff['target_agent'],
            'reason': handoff['reason'],
            'created_at': handoff['created_at'],
            'triggered_at': handoff['triggered_at'],
            'completed_at': handoff['completed_at'],
            'success': True
        }

    def complete_handoff(
        self,
        handoff_id: str,
        outcome: str = 'success'
    ) -> Dict[str, Any]:
        """
        Complete a handoff.

        Args:
            handoff_id: Handoff identifier
            outcome: Completion outcome

        Returns:
            Dictionary with completion result

        Example:
            >>> result = service.complete_handoff('handoff_123')
        """
        if handoff_id not in self._handoffs:
            return {
                'success': False,
                'error': f'Handoff {handoff_id} not found'
            }

        handoff = self._handoffs[handoff_id]
        handoff['status'] = 'completed'
        handoff['completed_at'] = datetime.utcnow().isoformat()
        handoff['outcome'] = outcome

        return {
            'handoff_id': handoff_id,
            'status': 'completed',
            'outcome': outcome,
            'duration_ms': 1500,  # Simulated duration
            'success': True,
            'completed_at': handoff['completed_at']
        }

    def create_escalation_rule(
        self,
        name: str,
        conditions: List[str],
        target_level: str,
        priority: int = 1
    ) -> Dict[str, Any]:
        """
        Create an escalation rule.

        Args:
            name: Rule name
            conditions: Trigger conditions
            target_level: Escalation target level
            priority: Rule priority

        Returns:
            Dictionary with rule details

        Example:
            >>> rule = service.create_escalation_rule('urgent', ['keyword:urgent'], 'supervisor')
        """
        rule_id = str(uuid.uuid4())

        rule = {
            'rule_id': rule_id,
            'name': name,
            'conditions': conditions,
            'target_level': target_level,
            'priority': priority,
            'active': True,
            'created_at': datetime.utcnow().isoformat()
        }

        self._escalation_rules[rule_id] = rule

        return {
            'rule_id': rule_id,
            'name': name,
            'conditions_count': len(conditions),
            'target_level': target_level,
            'priority': priority,
            'success': True,
            'created_at': rule['created_at']
        }

    def trigger_escalation(
        self,
        conversation_id: str,
        rule_id: Optional[str] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Trigger an escalation.

        Args:
            conversation_id: Conversation identifier
            rule_id: Optional specific rule ID
            reason: Escalation reason

        Returns:
            Dictionary with escalation result

        Example:
            >>> result = service.trigger_escalation('conv_123', reason='Customer frustrated')
        """
        escalation_id = str(uuid.uuid4())

        # Find matching rule or use default
        target_level = 'supervisor'
        matched_rule = None

        if rule_id and rule_id in self._escalation_rules:
            matched_rule = self._escalation_rules[rule_id]
            target_level = matched_rule['target_level']

        escalation = {
            'escalation_id': escalation_id,
            'conversation_id': conversation_id,
            'rule_id': rule_id,
            'reason': reason or 'Manual escalation',
            'target_level': target_level,
            'status': 'escalated',
            'triggered_at': datetime.utcnow().isoformat()
        }

        self._escalation_history.append(escalation)

        return {
            'escalation_id': escalation_id,
            'conversation_id': conversation_id,
            'target_level': target_level,
            'reason': escalation['reason'],
            'status': 'escalated',
            'success': True,
            'triggered_at': escalation['triggered_at']
        }

    def get_escalation_history(
        self,
        conversation_id: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get escalation history.

        Args:
            conversation_id: Optional conversation filter
            limit: Maximum records to return

        Returns:
            Dictionary with escalation history

        Example:
            >>> history = service.get_escalation_history()
        """
        history = self._escalation_history

        if conversation_id:
            history = [e for e in history if e['conversation_id'] == conversation_id]

        history = history[-limit:]

        # Calculate statistics
        by_level: Dict[str, int] = {}
        for escalation in history:
            level = escalation['target_level']
            by_level[level] = by_level.get(level, 0) + 1

        return {
            'total_escalations': len(history),
            'by_target_level': by_level,
            'escalations': history,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def get_conversation_flow_config(self) -> Dict[str, Any]:
        """
        Get conversation flow configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_conversation_flow_config()
        """
        return {
            'total_dialog_trees': len(self._dialog_trees),
            'total_handoffs': len(self._handoffs),
            'total_escalation_rules': len(self._escalation_rules),
            'total_escalations': len(self._escalation_history),
            'handoff_statuses': ['pending', 'in_progress', 'completed'],
            'escalation_levels': ['tier1', 'tier2', 'supervisor', 'manager'],
            'features': [
                'dialog_trees', 'node_management', 'traversal',
                'handoff_orchestration', 'escalation_rules', 'history_tracking'
            ]
        }
