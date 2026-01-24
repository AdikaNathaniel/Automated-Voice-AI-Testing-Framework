"""
Keyboard Shortcuts Service for voice AI testing.

This service provides keyboard shortcut management including
comprehensive shortcuts, customization, and cheat sheets.

Key features:
- Comprehensive shortcut system
- Customizable shortcuts
- Shortcut cheat sheet

Example:
    >>> service = KeyboardShortcutsService()
    >>> result = service.register_shortcut('Ctrl+S', 'save')
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class KeyboardShortcutsService:
    """
    Service for keyboard shortcuts.

    Provides shortcut management, customization,
    and cheat sheet features.

    Example:
        >>> service = KeyboardShortcutsService()
        >>> config = service.get_shortcuts_config()
    """

    def __init__(self):
        """Initialize the keyboard shortcuts service."""
        self._shortcuts: Dict[str, Dict[str, Any]] = {}
        self._user_customizations: Dict[str, Dict[str, Any]] = {}
        self._categories: List[str] = [
            'navigation', 'editing', 'test_management',
            'view', 'help'
        ]

    def register_shortcut(
        self,
        key_combo: str,
        action: str,
        category: str = 'general'
    ) -> Dict[str, Any]:
        """
        Register a keyboard shortcut.

        Args:
            key_combo: Key combination (e.g., 'Ctrl+S')
            action: Action to perform
            category: Shortcut category

        Returns:
            Dictionary with registration result

        Example:
            >>> result = service.register_shortcut('Ctrl+S', 'save')
        """
        shortcut_id = str(uuid.uuid4())

        self._shortcuts[key_combo] = {
            'shortcut_id': shortcut_id,
            'key_combo': key_combo,
            'action': action,
            'category': category,
            'enabled': True,
            'registered_at': datetime.utcnow().isoformat()
        }

        return {
            'shortcut_id': shortcut_id,
            'key_combo': key_combo,
            'action': action,
            'registered': True,
            'registered_at': datetime.utcnow().isoformat()
        }

    def get_shortcut(
        self,
        key_combo: str
    ) -> Dict[str, Any]:
        """
        Get shortcut by key combination.

        Args:
            key_combo: Key combination

        Returns:
            Dictionary with shortcut details

        Example:
            >>> result = service.get_shortcut('Ctrl+S')
        """
        shortcut = self._shortcuts.get(key_combo)
        if not shortcut:
            return {
                'key_combo': key_combo,
                'found': False,
                'error': f'Shortcut not found: {key_combo}',
                'retrieved_at': datetime.utcnow().isoformat()
            }

        return {
            'key_combo': key_combo,
            'found': True,
            **shortcut,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def list_shortcuts(
        self,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List all shortcuts.

        Args:
            category: Filter by category

        Returns:
            Dictionary with shortcuts list

        Example:
            >>> result = service.list_shortcuts()
        """
        shortcuts = list(self._shortcuts.values())

        if category:
            shortcuts = [
                s for s in shortcuts
                if s.get('category') == category
            ]

        return {
            'shortcuts': shortcuts,
            'count': len(shortcuts),
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def execute_shortcut(
        self,
        key_combo: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a shortcut action.

        Args:
            key_combo: Key combination
            context: Execution context

        Returns:
            Dictionary with execution result

        Example:
            >>> result = service.execute_shortcut('Ctrl+S')
        """
        execution_id = str(uuid.uuid4())

        shortcut = self._shortcuts.get(key_combo)
        if not shortcut:
            return {
                'execution_id': execution_id,
                'key_combo': key_combo,
                'executed': False,
                'error': f'Shortcut not found: {key_combo}',
                'executed_at': datetime.utcnow().isoformat()
            }

        return {
            'execution_id': execution_id,
            'key_combo': key_combo,
            'action': shortcut['action'],
            'executed': True,
            'executed_at': datetime.utcnow().isoformat()
        }

    def customize_shortcut(
        self,
        user_id: str,
        action: str,
        new_key_combo: str
    ) -> Dict[str, Any]:
        """
        Customize a shortcut for a user.

        Args:
            user_id: User identifier
            action: Action to customize
            new_key_combo: New key combination

        Returns:
            Dictionary with customization result

        Example:
            >>> result = service.customize_shortcut('user-1', 'save', 'Ctrl+Shift+S')
        """
        customization_id = str(uuid.uuid4())

        if user_id not in self._user_customizations:
            self._user_customizations[user_id] = {}

        self._user_customizations[user_id][action] = {
            'customization_id': customization_id,
            'action': action,
            'key_combo': new_key_combo,
            'customized_at': datetime.utcnow().isoformat()
        }

        return {
            'customization_id': customization_id,
            'user_id': user_id,
            'action': action,
            'new_key_combo': new_key_combo,
            'customized': True,
            'customized_at': datetime.utcnow().isoformat()
        }

    def reset_shortcut(
        self,
        user_id: str,
        action: str
    ) -> Dict[str, Any]:
        """
        Reset a shortcut to default.

        Args:
            user_id: User identifier
            action: Action to reset

        Returns:
            Dictionary with reset result

        Example:
            >>> result = service.reset_shortcut('user-1', 'save')
        """
        if user_id in self._user_customizations:
            if action in self._user_customizations[user_id]:
                del self._user_customizations[user_id][action]
                return {
                    'user_id': user_id,
                    'action': action,
                    'reset': True,
                    'reset_at': datetime.utcnow().isoformat()
                }

        return {
            'user_id': user_id,
            'action': action,
            'reset': False,
            'error': 'No customization found',
            'reset_at': datetime.utcnow().isoformat()
        }

    def get_user_shortcuts(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get user's customized shortcuts.

        Args:
            user_id: User identifier

        Returns:
            Dictionary with user shortcuts

        Example:
            >>> result = service.get_user_shortcuts('user-1')
        """
        customizations = self._user_customizations.get(user_id, {})

        return {
            'user_id': user_id,
            'customizations': list(customizations.values()),
            'count': len(customizations),
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def get_cheat_sheet(
        self,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get shortcut cheat sheet.

        Args:
            category: Filter by category

        Returns:
            Dictionary with cheat sheet

        Example:
            >>> result = service.get_cheat_sheet()
        """
        shortcuts = list(self._shortcuts.values())

        if category:
            shortcuts = [
                s for s in shortcuts
                if s.get('category') == category
            ]

        # Group by category
        grouped = {}
        for s in shortcuts:
            cat = s.get('category', 'general')
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append({
                'key_combo': s['key_combo'],
                'action': s['action']
            })

        return {
            'cheat_sheet': grouped,
            'categories': list(grouped.keys()),
            'total_shortcuts': len(shortcuts),
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def search_shortcuts(
        self,
        query: str
    ) -> Dict[str, Any]:
        """
        Search shortcuts.

        Args:
            query: Search query

        Returns:
            Dictionary with search results

        Example:
            >>> result = service.search_shortcuts('save')
        """
        search_id = str(uuid.uuid4())

        results = []
        query_lower = query.lower()

        for shortcut in self._shortcuts.values():
            if (query_lower in shortcut['action'].lower() or
                query_lower in shortcut['key_combo'].lower()):
                results.append(shortcut)

        return {
            'search_id': search_id,
            'query': query,
            'results': results,
            'count': len(results),
            'searched_at': datetime.utcnow().isoformat()
        }

    def get_shortcuts_config(self) -> Dict[str, Any]:
        """
        Get shortcuts configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_shortcuts_config()
        """
        return {
            'total_shortcuts': len(self._shortcuts),
            'total_customizations': sum(
                len(c) for c in self._user_customizations.values()
            ),
            'categories': self._categories,
            'features': [
                'shortcut_registration', 'customization',
                'cheat_sheet', 'search'
            ]
        }
