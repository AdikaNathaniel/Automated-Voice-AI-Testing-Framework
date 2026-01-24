"""
Automated Changelog Service for voice AI testing.

This service provides automated changelog generation including
conventional commits parsing, semantic versioning, and release notes.

Key features:
- Conventional commits parsing
- Semantic versioning
- Release notes generation

Example:
    >>> service = AutomatedChangelogService()
    >>> result = service.generate_changelog('v1.0.0', 'v1.1.0')
"""

from typing import List, Dict, Any
from datetime import datetime
import uuid
import re


class AutomatedChangelogService:
    """
    Service for automated changelog generation.

    Provides commit parsing, version bumping,
    and release notes generation.

    Example:
        >>> service = AutomatedChangelogService()
        >>> config = service.get_changelog_config()
    """

    def __init__(self):
        """Initialize the automated changelog service."""
        self._commits: List[Dict[str, Any]] = []
        self._releases: Dict[str, Dict[str, Any]] = {}
        self._commit_types: List[str] = [
            'feat', 'fix', 'docs', 'style', 'refactor',
            'perf', 'test', 'build', 'ci', 'chore'
        ]

    def parse_commit(
        self,
        message: str
    ) -> Dict[str, Any]:
        """
        Parse a conventional commit message.

        Args:
            message: Commit message

        Returns:
            Dictionary with parsed commit

        Example:
            >>> result = service.parse_commit('feat: add new feature')
        """
        commit_id = str(uuid.uuid4())

        # Parse conventional commit format
        pattern = r'^(\w+)(?:\(([^)]+)\))?(!)?:\s*(.+)$'
        match = re.match(pattern, message)

        if match:
            commit_type = match.group(1)
            scope = match.group(2)
            breaking = match.group(3) is not None
            description = match.group(4)
        else:
            commit_type = 'other'
            scope = None
            breaking = False
            description = message

        return {
            'commit_id': commit_id,
            'type': commit_type,
            'scope': scope,
            'breaking': breaking,
            'description': description,
            'valid': commit_type in self._commit_types,
            'parsed_at': datetime.utcnow().isoformat()
        }

    def parse_commits(
        self,
        messages: List[str]
    ) -> Dict[str, Any]:
        """
        Parse multiple commit messages.

        Args:
            messages: List of commit messages

        Returns:
            Dictionary with parsed commits

        Example:
            >>> result = service.parse_commits(['feat: add', 'fix: bug'])
        """
        parsed = [self.parse_commit(msg) for msg in messages]

        return {
            'commits': parsed,
            'count': len(parsed),
            'valid_count': sum(1 for c in parsed if c['valid']),
            'parsed_at': datetime.utcnow().isoformat()
        }

    def get_commit_type(
        self,
        commit_type: str
    ) -> Dict[str, Any]:
        """
        Get commit type information.

        Args:
            commit_type: Commit type

        Returns:
            Dictionary with type info

        Example:
            >>> result = service.get_commit_type('feat')
        """
        type_info = {
            'feat': {'label': 'Features', 'bump': 'minor'},
            'fix': {'label': 'Bug Fixes', 'bump': 'patch'},
            'docs': {'label': 'Documentation', 'bump': 'patch'},
            'style': {'label': 'Styles', 'bump': 'patch'},
            'refactor': {'label': 'Code Refactoring', 'bump': 'patch'},
            'perf': {'label': 'Performance', 'bump': 'patch'},
            'test': {'label': 'Tests', 'bump': 'patch'},
            'build': {'label': 'Build System', 'bump': 'patch'},
            'ci': {'label': 'CI', 'bump': 'patch'},
            'chore': {'label': 'Chores', 'bump': 'patch'}
        }

        info = type_info.get(commit_type, {'label': 'Other', 'bump': 'patch'})

        return {
            'type': commit_type,
            'label': info['label'],
            'bump': info['bump'],
            'valid': commit_type in self._commit_types,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def validate_conventional_commit(
        self,
        message: str
    ) -> Dict[str, Any]:
        """
        Validate a conventional commit message.

        Args:
            message: Commit message

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_conventional_commit('feat: add')
        """
        parsed = self.parse_commit(message)
        errors = []

        if not parsed['valid']:
            errors.append(f"Invalid commit type: {parsed['type']}")

        if len(parsed['description']) < 3:
            errors.append("Description too short")

        if len(parsed['description']) > 72:
            errors.append("Description too long (max 72 chars)")

        return {
            'message': message,
            'valid': len(errors) == 0,
            'errors': errors,
            'parsed': parsed,
            'validated_at': datetime.utcnow().isoformat()
        }

    def get_next_version(
        self,
        current: str,
        commits: List[str]
    ) -> Dict[str, Any]:
        """
        Determine next version based on commits.

        Args:
            current: Current version
            commits: List of commit messages

        Returns:
            Dictionary with next version

        Example:
            >>> result = service.get_next_version('1.0.0', ['feat: add'])
        """
        parsed = self.parse_commits(commits)

        # Determine bump type
        has_breaking = any(c['breaking'] for c in parsed['commits'])
        has_feat = any(c['type'] == 'feat' for c in parsed['commits'])

        if has_breaking:
            bump = 'major'
        elif has_feat:
            bump = 'minor'
        else:
            bump = 'patch'

        # Parse current version
        parts = current.lstrip('v').split('.')
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

        if bump == 'major':
            major += 1
            minor = 0
            patch = 0
        elif bump == 'minor':
            minor += 1
            patch = 0
        else:
            patch += 1

        next_version = f"{major}.{minor}.{patch}"

        return {
            'current': current,
            'next': next_version,
            'bump': bump,
            'commits_analyzed': len(commits),
            'calculated_at': datetime.utcnow().isoformat()
        }

    def bump_major(
        self,
        version: str
    ) -> Dict[str, Any]:
        """
        Bump major version.

        Args:
            version: Current version

        Returns:
            Dictionary with bumped version

        Example:
            >>> result = service.bump_major('1.2.3')
        """
        parts = version.lstrip('v').split('.')
        major = int(parts[0]) + 1

        return {
            'current': version,
            'next': f"{major}.0.0",
            'bump': 'major',
            'bumped_at': datetime.utcnow().isoformat()
        }

    def bump_minor(
        self,
        version: str
    ) -> Dict[str, Any]:
        """
        Bump minor version.

        Args:
            version: Current version

        Returns:
            Dictionary with bumped version

        Example:
            >>> result = service.bump_minor('1.2.3')
        """
        parts = version.lstrip('v').split('.')
        major, minor = int(parts[0]), int(parts[1]) + 1

        return {
            'current': version,
            'next': f"{major}.{minor}.0",
            'bump': 'minor',
            'bumped_at': datetime.utcnow().isoformat()
        }

    def bump_patch(
        self,
        version: str
    ) -> Dict[str, Any]:
        """
        Bump patch version.

        Args:
            version: Current version

        Returns:
            Dictionary with bumped version

        Example:
            >>> result = service.bump_patch('1.2.3')
        """
        parts = version.lstrip('v').split('.')
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2]) + 1

        return {
            'current': version,
            'next': f"{major}.{minor}.{patch}",
            'bump': 'patch',
            'bumped_at': datetime.utcnow().isoformat()
        }

    def generate_release_notes(
        self,
        version: str,
        commits: List[str]
    ) -> Dict[str, Any]:
        """
        Generate release notes.

        Args:
            version: Release version
            commits: List of commit messages

        Returns:
            Dictionary with release notes

        Example:
            >>> result = service.generate_release_notes('1.1.0', ['feat: add'])
        """
        release_id = str(uuid.uuid4())
        parsed = self.parse_commits(commits)

        # Group by type
        grouped = {}
        for commit in parsed['commits']:
            commit_type = commit['type']
            if commit_type not in grouped:
                grouped[commit_type] = []
            grouped[commit_type].append(commit['description'])

        notes = f"# Release {version}\n\n"
        for commit_type, descriptions in grouped.items():
            type_info = self.get_commit_type(commit_type)
            notes += f"## {type_info['label']}\n\n"
            for desc in descriptions:
                notes += f"- {desc}\n"
            notes += "\n"

        return {
            'release_id': release_id,
            'version': version,
            'notes': notes,
            'commit_count': len(commits),
            'generated_at': datetime.utcnow().isoformat()
        }

    def generate_changelog(
        self,
        from_version: str,
        to_version: str
    ) -> Dict[str, Any]:
        """
        Generate changelog between versions.

        Args:
            from_version: Start version
            to_version: End version

        Returns:
            Dictionary with changelog

        Example:
            >>> result = service.generate_changelog('1.0.0', '1.1.0')
        """
        changelog_id = str(uuid.uuid4())

        changelog = "# Changelog\n\n"
        changelog += f"## [{to_version}] - {datetime.utcnow().strftime('%Y-%m-%d')}\n\n"
        changelog += "### Added\n- New features\n\n"
        changelog += "### Changed\n- Updates\n\n"
        changelog += "### Fixed\n- Bug fixes\n\n"

        return {
            'changelog_id': changelog_id,
            'from_version': from_version,
            'to_version': to_version,
            'changelog': changelog,
            'generated_at': datetime.utcnow().isoformat()
        }

    def export_changelog(
        self,
        changelog_id: str,
        format: str = 'markdown'
    ) -> Dict[str, Any]:
        """
        Export changelog in specified format.

        Args:
            changelog_id: Changelog identifier
            format: Export format

        Returns:
            Dictionary with exported changelog

        Example:
            >>> result = service.export_changelog('cl-1', 'markdown')
        """
        return {
            'changelog_id': changelog_id,
            'format': format,
            'content': '# Changelog\n\nExported changelog content',
            'exported': True,
            'exported_at': datetime.utcnow().isoformat()
        }

    def get_changelog_config(self) -> Dict[str, Any]:
        """
        Get changelog configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_changelog_config()
        """
        return {
            'total_commits': len(self._commits),
            'total_releases': len(self._releases),
            'commit_types': self._commit_types,
            'features': [
                'conventional_commits', 'semantic_versioning',
                'release_notes', 'changelog_generation'
            ]
        }
