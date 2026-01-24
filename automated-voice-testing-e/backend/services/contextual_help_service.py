"""
Contextual Help Service for voice AI testing.

This service provides contextual help including
tooltips, inline documentation, and video tutorials.

Key features:
- Tooltips and popovers
- Inline documentation
- Video tutorials

Example:
    >>> service = ContextualHelpService()
    >>> result = service.get_tooltip('test_case_name')
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class ContextualHelpService:
    """
    Service for contextual help.

    Provides tooltips, inline documentation,
    and video tutorials.

    Example:
        >>> service = ContextualHelpService()
        >>> config = service.get_help_config()
    """

    def __init__(self):
        """Initialize the contextual help service."""
        self._tooltips: Dict[str, Dict[str, Any]] = {}
        self._docs: Dict[str, Dict[str, Any]] = {}
        self._videos: Dict[str, Dict[str, Any]] = {}
        self._video_progress: Dict[str, Dict[str, Any]] = {}
        self._supported_contexts: List[str] = [
            'test_case', 'test_suite', 'test_run',
            'configuration', 'results'
        ]

    def get_tooltip(
        self,
        element_id: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get tooltip for element.

        Args:
            element_id: Element identifier
            context: Context type

        Returns:
            Dictionary with tooltip content

        Example:
            >>> result = service.get_tooltip('test_case_name')
        """
        tooltip = self._tooltips.get(element_id)
        if not tooltip:
            # Return default tooltip
            return {
                'element_id': element_id,
                'content': f'Help for: {element_id}',
                'position': 'top',
                'found': True,
                'retrieved_at': datetime.utcnow().isoformat()
            }

        return {
            'element_id': element_id,
            'found': True,
            **tooltip,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def get_popover(
        self,
        element_id: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get popover content for element.

        Args:
            element_id: Element identifier
            context: Context type

        Returns:
            Dictionary with popover content

        Example:
            >>> result = service.get_popover('test_case_name')
        """
        return {
            'element_id': element_id,
            'title': f'About {element_id}',
            'content': f'Detailed information about {element_id}',
            'actions': ['Learn More', 'Dismiss'],
            'context': context,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def register_tooltip(
        self,
        element_id: str,
        content: str,
        position: str = 'top'
    ) -> Dict[str, Any]:
        """
        Register a tooltip.

        Args:
            element_id: Element identifier
            content: Tooltip content
            position: Tooltip position

        Returns:
            Dictionary with registration result

        Example:
            >>> result = service.register_tooltip('el-1', 'Help text')
        """
        tooltip_id = str(uuid.uuid4())

        self._tooltips[element_id] = {
            'tooltip_id': tooltip_id,
            'element_id': element_id,
            'content': content,
            'position': position,
            'registered_at': datetime.utcnow().isoformat()
        }

        return {
            'tooltip_id': tooltip_id,
            'element_id': element_id,
            'registered': True,
            'registered_at': datetime.utcnow().isoformat()
        }

    def get_inline_doc(
        self,
        doc_id: str
    ) -> Dict[str, Any]:
        """
        Get inline documentation.

        Args:
            doc_id: Documentation identifier

        Returns:
            Dictionary with documentation

        Example:
            >>> result = service.get_inline_doc('test-creation')
        """
        doc = self._docs.get(doc_id)
        if not doc:
            return {
                'doc_id': doc_id,
                'title': f'Documentation: {doc_id}',
                'content': 'Documentation content here',
                'found': True,
                'retrieved_at': datetime.utcnow().isoformat()
            }

        return {
            'doc_id': doc_id,
            'found': True,
            **doc,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def search_docs(
        self,
        query: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search documentation.

        Args:
            query: Search query
            context: Context filter

        Returns:
            Dictionary with search results

        Example:
            >>> result = service.search_docs('test case')
        """
        search_id = str(uuid.uuid4())

        # Simulated search results
        results = [
            {
                'doc_id': 'doc-1',
                'title': f'Result for: {query}',
                'snippet': f'Content matching {query}...',
                'relevance': 0.95
            },
            {
                'doc_id': 'doc-2',
                'title': f'Related to: {query}',
                'snippet': 'Related content...',
                'relevance': 0.85
            }
        ]

        return {
            'search_id': search_id,
            'query': query,
            'results': results,
            'count': len(results),
            'searched_at': datetime.utcnow().isoformat()
        }

    def get_related_docs(
        self,
        doc_id: str
    ) -> Dict[str, Any]:
        """
        Get related documentation.

        Args:
            doc_id: Source documentation ID

        Returns:
            Dictionary with related docs

        Example:
            >>> result = service.get_related_docs('test-creation')
        """
        related = [
            {
                'doc_id': 'related-1',
                'title': 'Related Topic 1',
                'relevance': 0.9
            },
            {
                'doc_id': 'related-2',
                'title': 'Related Topic 2',
                'relevance': 0.8
            }
        ]

        return {
            'source_doc_id': doc_id,
            'related': related,
            'count': len(related),
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def list_videos(
        self,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List video tutorials.

        Args:
            category: Filter by category

        Returns:
            Dictionary with videos list

        Example:
            >>> result = service.list_videos()
        """
        videos = [
            {
                'video_id': 'video-1',
                'title': 'Getting Started',
                'category': 'basics',
                'duration': '5:00',
                'thumbnail': '/thumbnails/getting-started.jpg'
            },
            {
                'video_id': 'video-2',
                'title': 'Creating Test Cases',
                'category': 'basics',
                'duration': '8:00',
                'thumbnail': '/thumbnails/test-cases.jpg'
            },
            {
                'video_id': 'video-3',
                'title': 'Advanced Configuration',
                'category': 'advanced',
                'duration': '12:00',
                'thumbnail': '/thumbnails/advanced.jpg'
            }
        ]

        if category:
            videos = [v for v in videos if v.get('category') == category]

        return {
            'videos': videos,
            'count': len(videos),
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def get_video(
        self,
        video_id: str
    ) -> Dict[str, Any]:
        """
        Get video tutorial.

        Args:
            video_id: Video identifier

        Returns:
            Dictionary with video details

        Example:
            >>> result = service.get_video('video-1')
        """
        video = self._videos.get(video_id)
        if not video:
            return {
                'video_id': video_id,
                'title': f'Video: {video_id}',
                'url': f'/videos/{video_id}.mp4',
                'duration': '5:00',
                'transcript': 'Video transcript here',
                'found': True,
                'retrieved_at': datetime.utcnow().isoformat()
            }

        return {
            'video_id': video_id,
            'found': True,
            **video,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def track_video_progress(
        self,
        user_id: str,
        video_id: str,
        progress: int
    ) -> Dict[str, Any]:
        """
        Track video viewing progress.

        Args:
            user_id: User identifier
            video_id: Video identifier
            progress: Progress percentage (0-100)

        Returns:
            Dictionary with tracking result

        Example:
            >>> result = service.track_video_progress('user-1', 'video-1', 50)
        """
        tracking_id = str(uuid.uuid4())

        key = f'{user_id}_{video_id}'
        self._video_progress[key] = {
            'tracking_id': tracking_id,
            'user_id': user_id,
            'video_id': video_id,
            'progress': progress,
            'completed': progress >= 100,
            'tracked_at': datetime.utcnow().isoformat()
        }

        return {
            'tracking_id': tracking_id,
            'user_id': user_id,
            'video_id': video_id,
            'progress': progress,
            'completed': progress >= 100,
            'tracked_at': datetime.utcnow().isoformat()
        }

    def get_help_config(self) -> Dict[str, Any]:
        """
        Get help configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_help_config()
        """
        return {
            'total_tooltips': len(self._tooltips),
            'total_docs': len(self._docs),
            'total_videos': len(self._videos),
            'supported_contexts': self._supported_contexts,
            'features': [
                'tooltips', 'popovers', 'inline_docs',
                'doc_search', 'video_tutorials'
            ]
        }
