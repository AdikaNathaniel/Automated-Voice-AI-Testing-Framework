"""
Conversation Recovery Service for voice AI testing.

This service provides conversation recovery and flow management
for handling interruptions and partial commands.

Key features:
- Partial command recovery
- Natural conversation flow
- Context preservation
- Conversation state management

Example:
    >>> service = ConversationRecoveryService()
    >>> result = service.recover_partial_command(session_id='sess_123', partial_text='navigate to')
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class ConversationRecoveryService:
    """
    Service for conversation recovery and flow management.

    Provides tools for recovering from interruptions,
    handling partial commands, and maintaining natural flow.

    Example:
        >>> service = ConversationRecoveryService()
        >>> config = service.get_recovery_config()
    """

    def __init__(self):
        """Initialize the conversation recovery service."""
        self._conversations: Dict[str, Dict[str, Any]] = {}
        self._contexts: Dict[str, Dict[str, Any]] = {}
        self._recovery_patterns: List[Dict[str, Any]] = []
        self._context_timeout_seconds = 300

    def recover_partial_command(
        self,
        session_id: str,
        partial_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Recover from a partial or interrupted command.

        Args:
            session_id: Session identifier
            partial_text: Partial command text
            context: Optional context data

        Returns:
            Dictionary with recovery result

        Example:
            >>> result = service.recover_partial_command('sess_123', 'navigate to')
        """
        recovery_id = str(uuid.uuid4())

        # Detect what's missing
        detection = self.detect_incomplete_command(partial_text)

        # Get suggestions for completion
        suggestions = self.suggest_completion(partial_text, context)

        # Build recovery response
        recovery_result = {
            'recovery_id': recovery_id,
            'session_id': session_id,
            'partial_text': partial_text,
            'detection': detection,
            'suggestions': suggestions,
            'prompt': self._generate_recovery_prompt(detection, suggestions),
            'recovered_at': datetime.utcnow().isoformat()
        }

        # Update conversation state
        if session_id in self._conversations:
            self._conversations[session_id]['last_recovery'] = recovery_result

        return recovery_result

    def detect_incomplete_command(
        self,
        text: str
    ) -> Dict[str, Any]:
        """
        Detect what's incomplete about a command.

        Args:
            text: Command text to analyze

        Returns:
            Dictionary with detection result

        Example:
            >>> detection = service.detect_incomplete_command('call')
        """
        detection_id = str(uuid.uuid4())

        # Analyze text for missing components
        words = text.lower().split()
        missing_components = []
        command_type = 'unknown'

        # Detect command type and missing parts
        if 'navigate' in words or 'go to' in text.lower():
            command_type = 'navigation'
            if len(words) <= 2:
                missing_components.append('destination')
        elif 'call' in words or 'phone' in words:
            command_type = 'call'
            if len(words) <= 1:
                missing_components.append('contact')
        elif 'play' in words:
            command_type = 'media'
            if len(words) <= 1:
                missing_components.append('media_item')
        elif 'set' in words:
            command_type = 'setting'
            if len(words) <= 1:
                missing_components.append('setting_name')
                missing_components.append('value')

        is_incomplete = len(missing_components) > 0

        return {
            'detection_id': detection_id,
            'text': text,
            'command_type': command_type,
            'is_incomplete': is_incomplete,
            'missing_components': missing_components,
            'confidence': 0.8 if command_type != 'unknown' else 0.3,
            'detected_at': datetime.utcnow().isoformat()
        }

    def suggest_completion(
        self,
        partial_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Suggest completions for partial command.

        Args:
            partial_text: Partial command text
            context: Optional context data

        Returns:
            Dictionary with suggestions

        Example:
            >>> suggestions = service.suggest_completion('navigate to')
        """
        suggestion_id = str(uuid.uuid4())

        suggestions = []
        words = partial_text.lower().split()

        # Generate suggestions based on context and patterns
        if 'navigate' in words or 'go to' in partial_text.lower():
            suggestions = [
                {'text': 'home', 'confidence': 0.7},
                {'text': 'work', 'confidence': 0.6},
                {'text': 'nearest gas station', 'confidence': 0.5}
            ]
            if context and 'recent_destinations' in context:
                for dest in context['recent_destinations'][:2]:
                    suggestions.insert(0, {'text': dest, 'confidence': 0.9})
        elif 'call' in words:
            suggestions = [
                {'text': 'recent contact', 'confidence': 0.5}
            ]
            if context and 'recent_contacts' in context:
                for contact in context['recent_contacts'][:3]:
                    suggestions.insert(0, {'text': contact, 'confidence': 0.8})
        elif 'play' in words:
            suggestions = [
                {'text': 'my playlist', 'confidence': 0.6},
                {'text': 'radio', 'confidence': 0.5}
            ]

        return {
            'suggestion_id': suggestion_id,
            'partial_text': partial_text,
            'suggestions': suggestions,
            'suggestion_count': len(suggestions),
            'suggested_at': datetime.utcnow().isoformat()
        }

    def continue_conversation(
        self,
        session_id: str,
        user_input: str,
        previous_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Continue a conversation naturally.

        Args:
            session_id: Session identifier
            user_input: User's input text
            previous_context: Previous conversation context

        Returns:
            Dictionary with continuation result

        Example:
            >>> result = service.continue_conversation('sess_123', 'yes, that one')
        """
        continuation_id = str(uuid.uuid4())

        # Get or create conversation
        if session_id not in self._conversations:
            self._conversations[session_id] = {
                'session_id': session_id,
                'turns': [],
                'created_at': datetime.utcnow().isoformat()
            }

        conversation = self._conversations[session_id]

        # Add turn
        turn = {
            'turn_id': str(uuid.uuid4()),
            'user_input': user_input,
            'context': previous_context,
            'timestamp': datetime.utcnow().isoformat()
        }
        conversation['turns'].append(turn)

        # Analyze for natural flow
        is_followup = self._is_followup(user_input, previous_context)
        resolved_reference = None

        if is_followup and previous_context:
            resolved_reference = self._resolve_reference(user_input, previous_context)

        return {
            'continuation_id': continuation_id,
            'session_id': session_id,
            'user_input': user_input,
            'is_followup': is_followup,
            'resolved_reference': resolved_reference,
            'turn_number': len(conversation['turns']),
            'continued_at': datetime.utcnow().isoformat()
        }

    def handle_interruption(
        self,
        session_id: str,
        interruption_type: str,
        interrupted_at: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle a conversation interruption.

        Args:
            session_id: Session identifier
            interruption_type: Type of interruption
            interrupted_at: Point of interruption

        Returns:
            Dictionary with interruption handling result

        Example:
            >>> result = service.handle_interruption('sess_123', 'user_barge_in')
        """
        handling_id = str(uuid.uuid4())

        # Save current state before handling
        if session_id in self._conversations:
            conversation = self._conversations[session_id]
            conversation['interrupted'] = True
            conversation['interruption_point'] = interrupted_at
            conversation['interruption_type'] = interruption_type
        else:
            conversation = None

        # Determine recovery strategy
        recovery_strategy = 'prompt_to_continue'
        if interruption_type == 'user_barge_in':
            recovery_strategy = 'acknowledge_and_switch'
        elif interruption_type == 'system_error':
            recovery_strategy = 'retry_last_action'
        elif interruption_type == 'timeout':
            recovery_strategy = 'prompt_for_input'

        return {
            'handling_id': handling_id,
            'session_id': session_id,
            'interruption_type': interruption_type,
            'recovery_strategy': recovery_strategy,
            'can_resume': conversation is not None,
            'handled_at': datetime.utcnow().isoformat()
        }

    def resume_from_context(
        self,
        session_id: str,
        context_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Resume conversation from saved context.

        Args:
            session_id: Session identifier
            context_id: Optional specific context to resume from

        Returns:
            Dictionary with resume result

        Example:
            >>> result = service.resume_from_context('sess_123')
        """
        resume_id = str(uuid.uuid4())

        # Find context to resume from
        if context_id and context_id in self._contexts:
            context = self._contexts[context_id]
        elif session_id in self._contexts:
            context = self._contexts[session_id]
        else:
            return {
                'resume_id': resume_id,
                'session_id': session_id,
                'success': False,
                'error': 'No context found to resume from',
                'resumed_at': datetime.utcnow().isoformat()
            }

        # Resume conversation
        if session_id in self._conversations:
            self._conversations[session_id]['resumed'] = True
            self._conversations[session_id]['resumed_from'] = context_id

        return {
            'resume_id': resume_id,
            'session_id': session_id,
            'context': context,
            'success': True,
            'resumed_at': datetime.utcnow().isoformat()
        }

    def save_context(
        self,
        session_id: str,
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Save conversation context.

        Args:
            session_id: Session identifier
            context_data: Context data to save

        Returns:
            Dictionary with save result

        Example:
            >>> result = service.save_context('sess_123', {'topic': 'navigation'})
        """
        context_id = str(uuid.uuid4())

        context = {
            'context_id': context_id,
            'session_id': session_id,
            'data': context_data,
            'saved_at': datetime.utcnow().isoformat()
        }

        self._contexts[session_id] = context
        self._contexts[context_id] = context

        return {
            'context_id': context_id,
            'session_id': session_id,
            'success': True,
            'saved_at': datetime.utcnow().isoformat()
        }

    def restore_context(
        self,
        context_id: str
    ) -> Dict[str, Any]:
        """
        Restore saved conversation context.

        Args:
            context_id: Context identifier

        Returns:
            Dictionary with restored context

        Example:
            >>> context = service.restore_context('ctx_123')
        """
        query_id = str(uuid.uuid4())

        if context_id not in self._contexts:
            return {
                'query_id': query_id,
                'found': False,
                'error': 'Context not found',
                'queried_at': datetime.utcnow().isoformat()
            }

        context = self._contexts[context_id]

        return {
            'query_id': query_id,
            'context_id': context_id,
            'context': context,
            'found': True,
            'restored_at': datetime.utcnow().isoformat()
        }

    def merge_contexts(
        self,
        context_ids: List[str],
        merge_strategy: str = 'latest_wins'
    ) -> Dict[str, Any]:
        """
        Merge multiple conversation contexts.

        Args:
            context_ids: List of context identifiers to merge
            merge_strategy: Strategy for merging conflicts

        Returns:
            Dictionary with merged context

        Example:
            >>> result = service.merge_contexts(['ctx_1', 'ctx_2'])
        """
        merge_id = str(uuid.uuid4())

        # Collect contexts
        contexts = []
        missing = []
        for ctx_id in context_ids:
            if ctx_id in self._contexts:
                contexts.append(self._contexts[ctx_id])
            else:
                missing.append(ctx_id)

        if not contexts:
            return {
                'merge_id': merge_id,
                'success': False,
                'error': 'No valid contexts found',
                'missing': missing,
                'merged_at': datetime.utcnow().isoformat()
            }

        # Merge based on strategy
        merged_data = {}
        if merge_strategy == 'latest_wins':
            for ctx in contexts:
                merged_data.update(ctx.get('data', {}))
        elif merge_strategy == 'first_wins':
            for ctx in reversed(contexts):
                merged_data.update(ctx.get('data', {}))

        return {
            'merge_id': merge_id,
            'merged_context': merged_data,
            'source_count': len(contexts),
            'merge_strategy': merge_strategy,
            'success': True,
            'merged_at': datetime.utcnow().isoformat()
        }

    def get_conversation_state(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Get current conversation state.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with conversation state

        Example:
            >>> state = service.get_conversation_state('sess_123')
        """
        query_id = str(uuid.uuid4())

        if session_id not in self._conversations:
            return {
                'query_id': query_id,
                'session_id': session_id,
                'found': False,
                'error': 'Conversation not found',
                'queried_at': datetime.utcnow().isoformat()
            }

        conversation = self._conversations[session_id]

        return {
            'query_id': query_id,
            'session_id': session_id,
            'state': {
                'turn_count': len(conversation.get('turns', [])),
                'interrupted': conversation.get('interrupted', False),
                'resumed': conversation.get('resumed', False),
                'created_at': conversation.get('created_at'),
                'last_activity': conversation['turns'][-1]['timestamp'] if conversation.get('turns') else None
            },
            'found': True,
            'queried_at': datetime.utcnow().isoformat()
        }

    def update_conversation_state(
        self,
        session_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update conversation state.

        Args:
            session_id: Session identifier
            updates: State updates to apply

        Returns:
            Dictionary with update result

        Example:
            >>> result = service.update_conversation_state('sess_123', {'topic': 'music'})
        """
        update_id = str(uuid.uuid4())

        if session_id not in self._conversations:
            self._conversations[session_id] = {
                'session_id': session_id,
                'turns': [],
                'created_at': datetime.utcnow().isoformat()
            }

        # Apply updates
        for key, value in updates.items():
            self._conversations[session_id][key] = value

        self._conversations[session_id]['updated_at'] = datetime.utcnow().isoformat()

        return {
            'update_id': update_id,
            'session_id': session_id,
            'updates_applied': list(updates.keys()),
            'success': True,
            'updated_at': datetime.utcnow().isoformat()
        }

    def get_recovery_config(self) -> Dict[str, Any]:
        """
        Get conversation recovery configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_recovery_config()
        """
        return {
            'context_timeout_seconds': self._context_timeout_seconds,
            'active_conversations': len(self._conversations),
            'saved_contexts': len(self._contexts),
            'recovery_patterns': len(self._recovery_patterns),
            'features': [
                'partial_command_recovery', 'natural_conversation_flow',
                'context_preservation', 'interruption_handling',
                'context_merging', 'state_management'
            ]
        }

    def _generate_recovery_prompt(
        self,
        detection: Dict[str, Any],
        suggestions: Dict[str, Any]
    ) -> str:
        """Generate a prompt for recovery based on detection and suggestions."""
        if not detection.get('is_incomplete'):
            return "How can I help you?"

        missing = detection.get('missing_components', [])
        command_type = detection.get('command_type', 'unknown')

        if command_type == 'navigation' and 'destination' in missing:
            return "Where would you like to go?"
        elif command_type == 'call' and 'contact' in missing:
            return "Who would you like to call?"
        elif command_type == 'media' and 'media_item' in missing:
            return "What would you like to play?"
        else:
            return "Could you please complete your request?"

    def _is_followup(
        self,
        text: str,
        context: Optional[Dict[str, Any]]
    ) -> bool:
        """Determine if text is a followup to previous context."""
        followup_indicators = [
            'yes', 'no', 'that', 'this', 'it', 'there', 'here',
            'the first', 'the second', 'okay', 'sure'
        ]
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in followup_indicators)

    def _resolve_reference(
        self,
        text: str,
        context: Dict[str, Any]
    ) -> Optional[str]:
        """Resolve pronouns and references in text using context."""
        text_lower = text.lower()

        if 'that' in text_lower or 'it' in text_lower:
            if 'last_item' in context:
                return context['last_item']

        if 'the first' in text_lower:
            if 'options' in context and len(context['options']) > 0:
                return context['options'][0]

        if 'the second' in text_lower:
            if 'options' in context and len(context['options']) > 1:
                return context['options'][1]

        return None
