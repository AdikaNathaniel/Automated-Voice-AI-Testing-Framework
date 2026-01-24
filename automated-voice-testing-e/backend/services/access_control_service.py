"""
Fine-grained Access Control Service for voice AI.

This service manages fine-grained access control including
resource permissions, project isolation, API key scoping, and IP allowlisting.

Key features:
- Resource-level permissions
- Project/team isolation
- API key scoping
- IP allowlisting

Example:
    >>> service = AccessControlService()
    >>> result = service.check_permission(user_id, resource, action)
"""

from typing import List, Dict, Any
from datetime import datetime
import uuid
import ipaddress
import secrets


class AccessControlService:
    """
    Service for fine-grained access control.

    Provides resource permissions, project isolation,
    API key management, and IP allowlisting.

    Example:
        >>> service = AccessControlService()
        >>> config = service.get_access_control_config()
    """

    def __init__(self):
        """Initialize the access control service."""
        self._permissions: Dict[str, Dict[str, Any]] = {}
        self._projects: Dict[str, Dict[str, Any]] = {}
        self._api_keys: Dict[str, Dict[str, Any]] = {}
        self._ip_allowlists: Dict[str, List[str]] = {}

    def set_resource_permission(
        self,
        resource_id: str,
        user_id: str,
        actions: List[str]
    ) -> Dict[str, Any]:
        """
        Set permission for user on resource.

        Args:
            resource_id: ID of resource
            user_id: ID of user
            actions: List of allowed actions

        Returns:
            Dictionary with permission details

        Example:
            >>> result = service.set_resource_permission(res_id, user_id, ['read'])
        """
        key = f'{resource_id}:{user_id}'
        permission = {
            'permission_id': str(uuid.uuid4()),
            'resource_id': resource_id,
            'user_id': user_id,
            'actions': actions,
            'created_at': datetime.utcnow().isoformat()
        }

        self._permissions[key] = permission
        return permission

    def check_permission(
        self,
        user_id: str,
        resource_id: str,
        action: str
    ) -> Dict[str, Any]:
        """
        Check if user has permission for action.

        Args:
            user_id: ID of user
            resource_id: ID of resource
            action: Action to check

        Returns:
            Dictionary with permission check result

        Example:
            >>> result = service.check_permission(user_id, res_id, 'read')
        """
        key = f'{resource_id}:{user_id}'

        if key in self._permissions:
            permission = self._permissions[key]
            allowed = action in permission['actions']
            return {
                'allowed': allowed,
                'user_id': user_id,
                'resource_id': resource_id,
                'action': action,
                'reason': 'Permission granted' if allowed else 'Action not in allowed list'
            }

        return {
            'allowed': False,
            'user_id': user_id,
            'resource_id': resource_id,
            'action': action,
            'reason': 'No permission record found'
        }

    def get_resource_permissions(
        self,
        resource_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all permissions for a resource.

        Args:
            resource_id: ID of resource

        Returns:
            List of permission records

        Example:
            >>> perms = service.get_resource_permissions(res_id)
        """
        return [
            p for key, p in self._permissions.items()
            if p['resource_id'] == resource_id
        ]

    def create_project(
        self,
        name: str,
        owner_id: str
    ) -> Dict[str, Any]:
        """
        Create a new project for isolation.

        Args:
            name: Project name
            owner_id: ID of project owner

        Returns:
            Dictionary with project details

        Example:
            >>> project = service.create_project('My Project', 'user123')
        """
        project_id = str(uuid.uuid4())
        project = {
            'project_id': project_id,
            'name': name,
            'owner_id': owner_id,
            'members': [owner_id],
            'created_at': datetime.utcnow().isoformat()
        }

        self._projects[project_id] = project
        return project

    def add_team_member(
        self,
        project_id: str,
        user_id: str,
        role: str = 'member'
    ) -> Dict[str, Any]:
        """
        Add team member to project.

        Args:
            project_id: ID of project
            user_id: ID of user to add
            role: Member role

        Returns:
            Dictionary with result

        Example:
            >>> result = service.add_team_member(proj_id, user_id, 'admin')
        """
        if project_id not in self._projects:
            return {
                'success': False,
                'error': f'Project {project_id} not found'
            }

        project = self._projects[project_id]
        if user_id not in project['members']:
            project['members'].append(user_id)

        return {
            'success': True,
            'project_id': project_id,
            'user_id': user_id,
            'role': role,
            'added_at': datetime.utcnow().isoformat()
        }

    def check_project_access(
        self,
        project_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Check if user has access to project.

        Args:
            project_id: ID of project
            user_id: ID of user

        Returns:
            Dictionary with access check result

        Example:
            >>> result = service.check_project_access(proj_id, user_id)
        """
        if project_id not in self._projects:
            return {
                'has_access': False,
                'reason': 'Project not found'
            }

        project = self._projects[project_id]
        has_access = user_id in project['members']

        return {
            'has_access': has_access,
            'project_id': project_id,
            'user_id': user_id,
            'is_owner': user_id == project['owner_id'],
            'reason': 'Member of project' if has_access else 'Not a project member'
        }

    def create_api_key(
        self,
        name: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Create a new API key.

        Args:
            name: Key name
            user_id: ID of key owner

        Returns:
            Dictionary with key details

        Example:
            >>> key = service.create_api_key('Production Key', 'user123')
        """
        key_id = str(uuid.uuid4())
        key_value = secrets.token_urlsafe(32)

        api_key = {
            'key_id': key_id,
            'name': name,
            'key': key_value,
            'user_id': user_id,
            'scopes': [],
            'created_at': datetime.utcnow().isoformat(),
            'active': True
        }

        self._api_keys[key_id] = api_key
        return api_key

    def set_key_scope(
        self,
        key_id: str,
        scopes: List[str]
    ) -> Dict[str, Any]:
        """
        Set scopes for API key.

        Args:
            key_id: ID of API key
            scopes: List of allowed scopes

        Returns:
            Dictionary with updated key

        Example:
            >>> result = service.set_key_scope(key_id, ['read', 'write'])
        """
        if key_id not in self._api_keys:
            return {
                'success': False,
                'error': f'API key {key_id} not found'
            }

        self._api_keys[key_id]['scopes'] = scopes
        return {
            'success': True,
            'key_id': key_id,
            'scopes': scopes,
            'updated_at': datetime.utcnow().isoformat()
        }

    def add_ip_allowlist(
        self,
        entity_id: str,
        ip_addresses: List[str]
    ) -> Dict[str, Any]:
        """
        Add IP addresses to allowlist.

        Args:
            entity_id: ID of entity (user, project, or key)
            ip_addresses: List of IP addresses/CIDRs

        Returns:
            Dictionary with allowlist result

        Example:
            >>> result = service.add_ip_allowlist('user123', ['192.168.1.0/24'])
        """
        if entity_id not in self._ip_allowlists:
            self._ip_allowlists[entity_id] = []

        self._ip_allowlists[entity_id].extend(ip_addresses)

        return {
            'success': True,
            'entity_id': entity_id,
            'ip_addresses': self._ip_allowlists[entity_id],
            'updated_at': datetime.utcnow().isoformat()
        }

    def check_ip_allowed(
        self,
        entity_id: str,
        ip_address: str
    ) -> Dict[str, Any]:
        """
        Check if IP address is allowed.

        Args:
            entity_id: ID of entity
            ip_address: IP address to check

        Returns:
            Dictionary with check result

        Example:
            >>> result = service.check_ip_allowed('user123', '192.168.1.100')
        """
        if entity_id not in self._ip_allowlists:
            # No allowlist means all IPs allowed
            return {
                'allowed': True,
                'reason': 'No allowlist configured'
            }

        allowlist = self._ip_allowlists[entity_id]
        try:
            check_ip = ipaddress.ip_address(ip_address)
            for allowed in allowlist:
                if '/' in allowed:
                    network = ipaddress.ip_network(allowed, strict=False)
                    if check_ip in network:
                        return {
                            'allowed': True,
                            'ip_address': ip_address,
                            'matched_rule': allowed
                        }
                elif ip_address == allowed:
                    return {
                        'allowed': True,
                        'ip_address': ip_address,
                        'matched_rule': allowed
                    }
        except ValueError:
            pass

        return {
            'allowed': False,
            'ip_address': ip_address,
            'reason': 'IP not in allowlist'
        }

    def get_access_control_config(self) -> Dict[str, Any]:
        """
        Get access control configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_access_control_config()
        """
        return {
            'total_permissions': len(self._permissions),
            'total_projects': len(self._projects),
            'total_api_keys': len(self._api_keys),
            'entities_with_ip_allowlist': len(self._ip_allowlists),
            'available_actions': ['read', 'write', 'delete', 'admin']
        }
