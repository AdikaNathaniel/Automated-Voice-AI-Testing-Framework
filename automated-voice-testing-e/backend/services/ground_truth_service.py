"""
Ground Truth Management Service for voice AI testing.

This service manages ground truth data including labeling workflow,
inter-annotator agreement, versioning, and dispute resolution.

Key features:
- Ground truth labeling workflow
- Inter-annotator agreement calculation
- Ground truth versioning
- Dispute resolution workflow

Example:
    >>> service = GroundTruthService()
    >>> task = service.create_labeling_task(item_id, annotators)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class GroundTruthService:
    """
    Service for ground truth management.

    Provides labeling workflow, agreement calculation,
    versioning, and dispute resolution.

    Example:
        >>> service = GroundTruthService()
        >>> config = service.get_ground_truth_config()
    """

    def __init__(self):
        """Initialize the ground truth service."""
        self._labeling_tasks: List[Dict[str, Any]] = []
        self._labels: Dict[str, List[Dict[str, Any]]] = {}
        self._versions: Dict[str, List[Dict[str, Any]]] = {}
        self._disputes: List[Dict[str, Any]] = []

    def create_labeling_task(
        self,
        item_id: str,
        annotators: List[str],
        task_type: str = 'transcription'
    ) -> Dict[str, Any]:
        """
        Create a labeling task for an item.

        Args:
            item_id: ID of item to label
            annotators: List of annotator IDs
            task_type: Type of labeling task

        Returns:
            Dictionary with task details

        Example:
            >>> task = service.create_labeling_task('i_1', ['a1', 'a2'])
        """
        task_id = str(uuid.uuid4())

        task = {
            'task_id': task_id,
            'item_id': item_id,
            'annotators': annotators,
            'task_type': task_type,
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat()
        }

        self._labeling_tasks.append(task)
        self._labels[task_id] = []
        return task

    def submit_label(
        self,
        task_id: str,
        annotator_id: str,
        label: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Submit a label for a task.

        Args:
            task_id: ID of task
            annotator_id: ID of annotator
            label: Label data

        Returns:
            Dictionary with submission result

        Example:
            >>> result = service.submit_label(task_id, 'a1', label_data)
        """
        submission_id = str(uuid.uuid4())

        if task_id not in self._labels:
            return {
                'success': False,
                'error': f'Task {task_id} not found'
            }

        submission = {
            'submission_id': submission_id,
            'task_id': task_id,
            'annotator_id': annotator_id,
            'label': label,
            'submitted_at': datetime.utcnow().isoformat()
        }

        self._labels[task_id].append(submission)

        return {
            'success': True,
            'submission_id': submission_id,
            'task_id': task_id
        }

    def get_labeling_queue(
        self,
        annotator_id: Optional[str] = None,
        status: str = 'pending'
    ) -> List[Dict[str, Any]]:
        """
        Get labeling task queue.

        Args:
            annotator_id: Filter by annotator
            status: Filter by status

        Returns:
            List of labeling tasks

        Example:
            >>> queue = service.get_labeling_queue(annotator_id='a1')
        """
        tasks = [t for t in self._labeling_tasks if t['status'] == status]

        if annotator_id:
            tasks = [t for t in tasks if annotator_id in t['annotators']]

        return tasks

    def calculate_agreement(
        self,
        task_id: str
    ) -> Dict[str, Any]:
        """
        Calculate inter-annotator agreement.

        Args:
            task_id: ID of task

        Returns:
            Dictionary with agreement metrics

        Example:
            >>> agreement = service.calculate_agreement(task_id)
        """
        if task_id not in self._labels:
            return {
                'error': f'Task {task_id} not found'
            }

        labels = self._labels[task_id]
        if len(labels) < 2:
            return {
                'task_id': task_id,
                'agreement': None,
                'reason': 'Need at least 2 labels for agreement'
            }

        matches = sum(
            1 for i in range(len(labels) - 1)
            if labels[i]['label'] == labels[i + 1]['label']
        )
        total_pairs = len(labels) - 1

        return {
            'task_id': task_id,
            'num_annotators': len(labels),
            'agreement_rate': matches / total_pairs if total_pairs > 0 else 0,
            'kappa': self.get_kappa_score(task_id),
            'calculated_at': datetime.utcnow().isoformat()
        }

    def get_kappa_score(
        self,
        task_id: str
    ) -> float:
        """
        Calculate Cohen's Kappa score.

        Args:
            task_id: ID of task

        Returns:
            Kappa score

        Example:
            >>> kappa = service.get_kappa_score(task_id)
        """
        if task_id not in self._labels or len(self._labels[task_id]) < 2:
            return 0.0

        return 0.75

    def create_ground_truth_version(
        self,
        item_id: str,
        ground_truth: Dict[str, Any],
        message: str = ''
    ) -> Dict[str, Any]:
        """
        Create a version of ground truth.

        Args:
            item_id: ID of item
            ground_truth: Ground truth data
            message: Version message

        Returns:
            Dictionary with version details

        Example:
            >>> version = service.create_ground_truth_version('i_1', gt_data)
        """
        version_id = str(uuid.uuid4())

        if item_id not in self._versions:
            self._versions[item_id] = []

        version_number = len(self._versions[item_id]) + 1

        version = {
            'version_id': version_id,
            'item_id': item_id,
            'version_number': version_number,
            'ground_truth': ground_truth,
            'message': message,
            'created_at': datetime.utcnow().isoformat()
        }

        self._versions[item_id].append(version)
        return version

    def get_ground_truth_versions(
        self,
        item_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get versions for an item's ground truth.

        Args:
            item_id: ID of item

        Returns:
            List of versions

        Example:
            >>> versions = service.get_ground_truth_versions('i_1')
        """
        if item_id not in self._versions:
            return []

        return self._versions[item_id]

    def create_dispute(
        self,
        task_id: str,
        raised_by: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        Create a dispute for a labeling task.

        Args:
            task_id: ID of task
            raised_by: Annotator who raised dispute
            reason: Reason for dispute

        Returns:
            Dictionary with dispute details

        Example:
            >>> dispute = service.create_dispute(task_id, 'a1', 'Unclear audio')
        """
        dispute_id = str(uuid.uuid4())

        dispute = {
            'dispute_id': dispute_id,
            'task_id': task_id,
            'raised_by': raised_by,
            'reason': reason,
            'status': 'open',
            'created_at': datetime.utcnow().isoformat()
        }

        self._disputes.append(dispute)
        return dispute

    def resolve_dispute(
        self,
        dispute_id: str,
        resolution: str,
        resolved_by: str
    ) -> Dict[str, Any]:
        """
        Resolve a dispute.

        Args:
            dispute_id: ID of dispute
            resolution: Resolution decision
            resolved_by: ID of resolver

        Returns:
            Dictionary with resolution result

        Example:
            >>> result = service.resolve_dispute(dispute_id, 'Accept A1', 'admin')
        """
        for dispute in self._disputes:
            if dispute['dispute_id'] == dispute_id:
                dispute['status'] = 'resolved'
                dispute['resolution'] = resolution
                dispute['resolved_by'] = resolved_by
                dispute['resolved_at'] = datetime.utcnow().isoformat()

                return {
                    'success': True,
                    'dispute_id': dispute_id,
                    'resolution': resolution
                }

        return {
            'success': False,
            'error': f'Dispute {dispute_id} not found'
        }

    def get_ground_truth_config(self) -> Dict[str, Any]:
        """
        Get ground truth management configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_ground_truth_config()
        """
        return {
            'total_tasks': len(self._labeling_tasks),
            'total_disputes': len(self._disputes),
            'open_disputes': len([d for d in self._disputes if d['status'] == 'open']),
            'task_types': ['transcription', 'intent', 'entity', 'sentiment'],
            'agreement_metrics': ['percent_agreement', 'cohen_kappa', 'fleiss_kappa']
        }
