"""
Adaptive Behavior Service for voice AI testing.

This service provides adaptive behavior and personalization
for voice AI systems based on user patterns and context.

Key features:
- Command shortcut suggestions
- Proactive notifications
- Context-aware adaptations
- Behavior pattern detection

Example:
    >>> service = AdaptiveBehaviorService()
    >>> shortcut = service.create_shortcut(user_id='user_123', command='navigate home')
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import Counter
import uuid


class AdaptiveBehaviorService:
    """
    Service for adaptive behavior and personalization.

    Provides tools for learning user patterns, suggesting shortcuts,
    and adapting responses based on context.

    Example:
        >>> service = AdaptiveBehaviorService()
        >>> config = service.get_adaptive_config()
    """

    def __init__(self):
        """Initialize the adaptive behavior service."""
        self._shortcuts: Dict[str, List[Dict[str, Any]]] = {}
        self._notifications: Dict[str, List[Dict[str, Any]]] = {}
        self._behavior_history: Dict[str, List[Dict[str, Any]]] = {}
        self._context_cache: Dict[str, Dict[str, Any]] = {}

    def create_shortcut(
        self,
        user_id: str,
        command: str,
        trigger: Optional[str] = None,
        context_conditions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a command shortcut for a user.

        Args:
            user_id: User identifier
            command: Full command to execute
            trigger: Optional trigger phrase
            context_conditions: Conditions for activation

        Returns:
            Dictionary with shortcut creation result

        Example:
            >>> shortcut = service.create_shortcut('user_123', 'navigate to work')
        """
        shortcut_id = str(uuid.uuid4())

        if user_id not in self._shortcuts:
            self._shortcuts[user_id] = []

        shortcut = {
            'shortcut_id': shortcut_id,
            'command': command,
            'trigger': trigger or command[:20],
            'context_conditions': context_conditions or {},
            'usage_count': 0,
            'created_at': datetime.utcnow().isoformat()
        }

        self._shortcuts[user_id].append(shortcut)

        return {
            'shortcut_id': shortcut_id,
            'user_id': user_id,
            'command': command,
            'trigger': shortcut['trigger'],
            'success': True,
            'created_at': shortcut['created_at']
        }

    def suggest_shortcuts(
        self,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Suggest shortcuts based on user behavior.

        Args:
            user_id: User identifier
            context: Current context

        Returns:
            Dictionary with shortcut suggestions

        Example:
            >>> suggestions = service.suggest_shortcuts('user_123')
        """
        suggestion_id = str(uuid.uuid4())

        # Analyze behavior history for patterns
        if user_id not in self._behavior_history:
            return {
                'suggestion_id': suggestion_id,
                'user_id': user_id,
                'suggestions': [],
                'based_on': 'no_history',
                'suggested_at': datetime.utcnow().isoformat()
            }

        history = self._behavior_history[user_id]
        command_counts = Counter(
            item.get('command', '') for item in history
        )
        frequent = command_counts.most_common(5)

        suggestions = [
            {
                'command': cmd,
                'frequency': count,
                'confidence': min(0.9, count / 10),
                'reason': 'frequently_used'
            }
            for cmd, count in frequent if count >= 2
        ]

        return {
            'suggestion_id': suggestion_id,
            'user_id': user_id,
            'suggestions': suggestions,
            'based_on': 'usage_patterns',
            'context_used': context is not None,
            'suggested_at': datetime.utcnow().isoformat()
        }

    def get_user_shortcuts(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get all shortcuts for a user.

        Args:
            user_id: User identifier

        Returns:
            Dictionary with user shortcuts

        Example:
            >>> shortcuts = service.get_user_shortcuts('user_123')
        """
        query_id = str(uuid.uuid4())

        if user_id not in self._shortcuts:
            return {
                'query_id': query_id,
                'user_id': user_id,
                'shortcuts': [],
                'total_shortcuts': 0,
                'queried_at': datetime.utcnow().isoformat()
            }

        shortcuts = self._shortcuts[user_id]

        return {
            'query_id': query_id,
            'user_id': user_id,
            'shortcuts': shortcuts,
            'total_shortcuts': len(shortcuts),
            'queried_at': datetime.utcnow().isoformat()
        }

    def schedule_notification(
        self,
        user_id: str,
        notification_type: str,
        message: str,
        trigger_time: Optional[str] = None,
        conditions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Schedule a proactive notification.

        Args:
            user_id: User identifier
            notification_type: Type of notification
            message: Notification message
            trigger_time: Optional scheduled time
            conditions: Trigger conditions

        Returns:
            Dictionary with scheduling result

        Example:
            >>> result = service.schedule_notification('user_123', 'reminder', 'Meeting in 15 min')
        """
        notification_id = str(uuid.uuid4())

        if user_id not in self._notifications:
            self._notifications[user_id] = []

        notification = {
            'notification_id': notification_id,
            'type': notification_type,
            'message': message,
            'trigger_time': trigger_time,
            'conditions': conditions or {},
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat()
        }

        self._notifications[user_id].append(notification)

        return {
            'notification_id': notification_id,
            'user_id': user_id,
            'type': notification_type,
            'message': message,
            'status': 'scheduled',
            'success': True,
            'scheduled_at': notification['created_at']
        }

    def get_pending_notifications(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get pending notifications for a user.

        Args:
            user_id: User identifier

        Returns:
            Dictionary with pending notifications

        Example:
            >>> pending = service.get_pending_notifications('user_123')
        """
        query_id = str(uuid.uuid4())

        if user_id not in self._notifications:
            return {
                'query_id': query_id,
                'user_id': user_id,
                'notifications': [],
                'total_pending': 0,
                'queried_at': datetime.utcnow().isoformat()
            }

        pending = [
            n for n in self._notifications[user_id]
            if n['status'] == 'pending'
        ]

        return {
            'query_id': query_id,
            'user_id': user_id,
            'notifications': pending,
            'total_pending': len(pending),
            'queried_at': datetime.utcnow().isoformat()
        }

    def trigger_contextual_notification(
        self,
        user_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Trigger notifications based on context.

        Args:
            user_id: User identifier
            context: Current context data

        Returns:
            Dictionary with triggered notifications

        Example:
            >>> result = service.trigger_contextual_notification('user_123', {'location': 'home'})
        """
        trigger_id = str(uuid.uuid4())

        triggered = []

        if user_id in self._notifications:
            for notification in self._notifications[user_id]:
                if notification['status'] == 'pending':
                    conditions = notification.get('conditions', {})
                    # Simple condition matching
                    if all(
                        context.get(k) == v
                        for k, v in conditions.items()
                    ):
                        notification['status'] = 'triggered'
                        triggered.append({
                            'notification_id': notification['notification_id'],
                            'message': notification['message'],
                            'type': notification['type']
                        })

        return {
            'trigger_id': trigger_id,
            'user_id': user_id,
            'triggered_notifications': triggered,
            'trigger_count': len(triggered),
            'context_evaluated': context,
            'triggered_at': datetime.utcnow().isoformat()
        }

    def analyze_context(
        self,
        user_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze context for adaptation opportunities.

        Args:
            user_id: User identifier
            context: Context data to analyze

        Returns:
            Dictionary with analysis results

        Example:
            >>> analysis = service.analyze_context('user_123', {'time': 'morning'})
        """
        analysis_id = str(uuid.uuid4())

        # Store context for learning
        self._context_cache[user_id] = {
            'context': context,
            'analyzed_at': datetime.utcnow().isoformat()
        }

        # Determine adaptations based on context
        adaptations = []

        if context.get('time_of_day') == 'morning':
            adaptations.append({
                'type': 'greeting',
                'suggestion': 'morning_greeting',
                'confidence': 0.9
            })

        if context.get('location') == 'work':
            adaptations.append({
                'type': 'mode',
                'suggestion': 'professional_mode',
                'confidence': 0.85
            })

        if context.get('driving'):
            adaptations.append({
                'type': 'interface',
                'suggestion': 'voice_only',
                'confidence': 0.95
            })

        return {
            'analysis_id': analysis_id,
            'user_id': user_id,
            'context_factors': list(context.keys()),
            'suggested_adaptations': adaptations,
            'adaptation_count': len(adaptations),
            'analyzed_at': datetime.utcnow().isoformat()
        }

    def adapt_response(
        self,
        user_id: str,
        response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Adapt a response based on user preferences and context.

        Args:
            user_id: User identifier
            response: Original response
            context: Optional context

        Returns:
            Dictionary with adapted response

        Example:
            >>> adapted = service.adapt_response('user_123', 'Hello')
        """
        adaptation_id = str(uuid.uuid4())

        # Get cached context if not provided
        if not context and user_id in self._context_cache:
            context = self._context_cache[user_id].get('context', {})

        adapted_response = response
        adaptations_applied = []

        # Apply simple adaptations
        if context:
            if context.get('formality') == 'casual':
                adapted_response = adapted_response.replace(
                    'Hello', 'Hey'
                ).replace(
                    'Goodbye', 'See ya'
                )
                adaptations_applied.append('casual_tone')

            if context.get('verbosity') == 'brief':
                # Shorten response
                if len(adapted_response) > 50:
                    adapted_response = adapted_response[:47] + '...'
                adaptations_applied.append('brief_response')

        return {
            'adaptation_id': adaptation_id,
            'user_id': user_id,
            'original_response': response,
            'adapted_response': adapted_response,
            'adaptations_applied': adaptations_applied,
            'context_used': context is not None,
            'adapted_at': datetime.utcnow().isoformat()
        }

    def detect_patterns(
        self,
        user_id: str,
        behavior_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Detect behavior patterns from user data.

        Args:
            user_id: User identifier
            behavior_data: Optional behavior data to analyze

        Returns:
            Dictionary with detected patterns

        Example:
            >>> patterns = service.detect_patterns('user_123')
        """
        detection_id = str(uuid.uuid4())

        # Store behavior data if provided
        if behavior_data:
            if user_id not in self._behavior_history:
                self._behavior_history[user_id] = []
            self._behavior_history[user_id].extend(behavior_data)

        # Analyze stored history
        if user_id not in self._behavior_history:
            return {
                'detection_id': detection_id,
                'user_id': user_id,
                'patterns': [],
                'data_points': 0,
                'detected_at': datetime.utcnow().isoformat()
            }

        history = self._behavior_history[user_id]
        patterns = []

        # Detect command patterns
        commands = [h.get('command') for h in history if h.get('command')]
        if commands:
            command_counts = Counter(commands)
            for cmd, count in command_counts.most_common(3):
                if count >= 2:
                    patterns.append({
                        'type': 'frequent_command',
                        'value': cmd,
                        'occurrences': count,
                        'confidence': min(0.9, count / len(commands))
                    })

        # Detect time patterns
        times = [h.get('time_of_day') for h in history if h.get('time_of_day')]
        if times:
            time_counts = Counter(times)
            most_common_time = time_counts.most_common(1)
            if most_common_time:
                patterns.append({
                    'type': 'preferred_time',
                    'value': most_common_time[0][0],
                    'occurrences': most_common_time[0][1],
                    'confidence': most_common_time[0][1] / len(times)
                })

        return {
            'detection_id': detection_id,
            'user_id': user_id,
            'patterns': patterns,
            'pattern_count': len(patterns),
            'data_points': len(history),
            'detected_at': datetime.utcnow().isoformat()
        }

    def get_behavior_insights(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get insights from behavior analysis.

        Args:
            user_id: User identifier

        Returns:
            Dictionary with behavior insights

        Example:
            >>> insights = service.get_behavior_insights('user_123')
        """
        query_id = str(uuid.uuid4())

        if user_id not in self._behavior_history:
            return {
                'query_id': query_id,
                'user_id': user_id,
                'insights': [],
                'total_interactions': 0,
                'queried_at': datetime.utcnow().isoformat()
            }

        history = self._behavior_history[user_id]
        insights = []

        # Generate insights
        total = len(history)

        # Command diversity
        unique_commands = len(set(
            h.get('command') for h in history if h.get('command')
        ))
        insights.append({
            'category': 'command_diversity',
            'value': unique_commands,
            'interpretation': 'high' if unique_commands > 10 else 'moderate' if unique_commands > 5 else 'low'
        })

        # Usage frequency
        insights.append({
            'category': 'usage_frequency',
            'value': total,
            'interpretation': 'heavy' if total > 50 else 'moderate' if total > 20 else 'light'
        })

        return {
            'query_id': query_id,
            'user_id': user_id,
            'insights': insights,
            'total_interactions': total,
            'queried_at': datetime.utcnow().isoformat()
        }

    def get_adaptive_config(self) -> Dict[str, Any]:
        """
        Get adaptive behavior configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_adaptive_config()
        """
        return {
            'total_users': len(set(
                list(self._shortcuts.keys()) +
                list(self._notifications.keys()) +
                list(self._behavior_history.keys())
            )),
            'total_shortcuts': sum(len(v) for v in self._shortcuts.values()),
            'total_notifications': sum(len(v) for v in self._notifications.values()),
            'total_behavior_events': sum(len(v) for v in self._behavior_history.values()),
            'features': [
                'command_shortcuts', 'proactive_notifications',
                'context_adaptation', 'behavior_patterns',
                'response_adaptation', 'insights'
            ]
        }
