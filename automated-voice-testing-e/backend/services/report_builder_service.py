"""
Report Builder Service for voice AI testing.

This service provides report building capabilities including
drag-and-drop creation, metric selection, and template management.

Key features:
- Drag-and-drop report creation
- Custom metric selection
- Flexible grouping/filtering
- Template library

Example:
    >>> service = ReportBuilderService()
    >>> report = service.create_report('My Report')
"""

from typing import List, Dict, Any
from datetime import datetime
import uuid


class ReportBuilderService:
    """
    Service for building custom reports.

    Provides report creation, component management,
    and template library functionality.

    Example:
        >>> service = ReportBuilderService()
        >>> config = service.get_builder_config()
    """

    def __init__(self):
        """Initialize the report builder service."""
        self._reports: Dict[str, Dict[str, Any]] = {}
        self._templates: Dict[str, Dict[str, Any]] = {}

    def create_report(
        self,
        name: str,
        description: str = ''
    ) -> Dict[str, Any]:
        """
        Create a new report.

        Args:
            name: Report name
            description: Report description

        Returns:
            Dictionary with report details

        Example:
            >>> report = service.create_report('Weekly Report')
        """
        report_id = str(uuid.uuid4())

        report = {
            'report_id': report_id,
            'name': name,
            'description': description,
            'components': [],
            'metrics': [],
            'grouping': None,
            'filters': {},
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }

        self._reports[report_id] = report

        return {
            'report_id': report_id,
            'name': name,
            'status': 'created',
            'created_at': report['created_at']
        }

    def add_component(
        self,
        report_id: str,
        component_type: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add a component to a report.

        Args:
            report_id: Report identifier
            component_type: Type of component (chart, table, text, etc.)
            config: Component configuration

        Returns:
            Dictionary with component details

        Example:
            >>> result = service.add_component(report_id, 'chart', config)
        """
        component_id = str(uuid.uuid4())

        if report_id not in self._reports:
            return {
                'error': 'Report not found',
                'report_id': report_id
            }

        component = {
            'component_id': component_id,
            'type': component_type,
            'config': config,
            'position': len(self._reports[report_id]['components']),
            'added_at': datetime.utcnow().isoformat()
        }

        self._reports[report_id]['components'].append(component)
        self._reports[report_id]['updated_at'] = datetime.utcnow().isoformat()

        return {
            'component_id': component_id,
            'report_id': report_id,
            'type': component_type,
            'position': component['position'],
            'added_at': component['added_at']
        }

    def reorder_components(
        self,
        report_id: str,
        component_order: List[str]
    ) -> Dict[str, Any]:
        """
        Reorder components in a report.

        Args:
            report_id: Report identifier
            component_order: List of component IDs in new order

        Returns:
            Dictionary with reorder result

        Example:
            >>> result = service.reorder_components(report_id, order)
        """
        if report_id not in self._reports:
            return {
                'error': 'Report not found',
                'report_id': report_id
            }

        components = self._reports[report_id]['components']
        component_map = {c['component_id']: c for c in components}

        reordered = []
        for i, comp_id in enumerate(component_order):
            if comp_id in component_map:
                component = component_map[comp_id]
                component['position'] = i
                reordered.append(component)

        self._reports[report_id]['components'] = reordered
        self._reports[report_id]['updated_at'] = datetime.utcnow().isoformat()

        return {
            'report_id': report_id,
            'new_order': component_order,
            'components_reordered': len(reordered),
            'updated_at': self._reports[report_id]['updated_at']
        }

    def select_metrics(
        self,
        report_id: str,
        metrics: List[str]
    ) -> Dict[str, Any]:
        """
        Select metrics for a report.

        Args:
            report_id: Report identifier
            metrics: List of metric names

        Returns:
            Dictionary with selection result

        Example:
            >>> result = service.select_metrics(report_id, ['accuracy', 'wer'])
        """
        if report_id not in self._reports:
            return {
                'error': 'Report not found',
                'report_id': report_id
            }

        self._reports[report_id]['metrics'] = metrics
        self._reports[report_id]['updated_at'] = datetime.utcnow().isoformat()

        return {
            'report_id': report_id,
            'metrics': metrics,
            'metrics_count': len(metrics),
            'updated_at': self._reports[report_id]['updated_at']
        }

    def get_available_metrics(self) -> Dict[str, Any]:
        """
        Get available metrics for reports.

        Returns:
            Dictionary with available metrics

        Example:
            >>> metrics = service.get_available_metrics()
        """
        return {
            'metrics': [
                {'name': 'accuracy', 'category': 'performance', 'description': 'Overall accuracy'},
                {'name': 'wer', 'category': 'performance', 'description': 'Word error rate'},
                {'name': 'latency', 'category': 'performance', 'description': 'Response latency'},
                {'name': 'error_rate', 'category': 'quality', 'description': 'Error rate'},
                {'name': 'confidence', 'category': 'quality', 'description': 'Confidence score'},
                {'name': 'throughput', 'category': 'capacity', 'description': 'Tests per minute'}
            ],
            'categories': ['performance', 'quality', 'capacity', 'fairness'],
            'generated_at': datetime.utcnow().isoformat()
        }

    def set_grouping(
        self,
        report_id: str,
        grouping: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Set data grouping for a report.

        Args:
            report_id: Report identifier
            grouping: Grouping configuration

        Returns:
            Dictionary with grouping result

        Example:
            >>> result = service.set_grouping(report_id, {'by': 'date'})
        """
        if report_id not in self._reports:
            return {
                'error': 'Report not found',
                'report_id': report_id
            }

        self._reports[report_id]['grouping'] = grouping
        self._reports[report_id]['updated_at'] = datetime.utcnow().isoformat()

        return {
            'report_id': report_id,
            'grouping': grouping,
            'updated_at': self._reports[report_id]['updated_at']
        }

    def set_filters(
        self,
        report_id: str,
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Set data filters for a report.

        Args:
            report_id: Report identifier
            filters: Filter configuration

        Returns:
            Dictionary with filter result

        Example:
            >>> result = service.set_filters(report_id, {'date_range': '7d'})
        """
        if report_id not in self._reports:
            return {
                'error': 'Report not found',
                'report_id': report_id
            }

        self._reports[report_id]['filters'] = filters
        self._reports[report_id]['updated_at'] = datetime.utcnow().isoformat()

        return {
            'report_id': report_id,
            'filters': filters,
            'filter_count': len(filters),
            'updated_at': self._reports[report_id]['updated_at']
        }

    def save_as_template(
        self,
        report_id: str,
        template_name: str
    ) -> Dict[str, Any]:
        """
        Save a report as a template.

        Args:
            report_id: Report identifier
            template_name: Template name

        Returns:
            Dictionary with template details

        Example:
            >>> result = service.save_as_template(report_id, 'Weekly Template')
        """
        template_id = str(uuid.uuid4())

        if report_id not in self._reports:
            return {
                'error': 'Report not found',
                'report_id': report_id
            }

        report = self._reports[report_id]

        template = {
            'template_id': template_id,
            'name': template_name,
            'components': report['components'].copy(),
            'metrics': report['metrics'].copy(),
            'grouping': report['grouping'],
            'filters': report['filters'].copy(),
            'created_at': datetime.utcnow().isoformat()
        }

        self._templates[template_id] = template

        return {
            'template_id': template_id,
            'name': template_name,
            'status': 'saved',
            'created_at': template['created_at']
        }

    def get_templates(self) -> Dict[str, Any]:
        """
        Get available report templates.

        Returns:
            Dictionary with templates

        Example:
            >>> templates = service.get_templates()
        """
        templates_list = [
            {
                'template_id': tid,
                'name': t['name'],
                'components_count': len(t['components']),
                'created_at': t['created_at']
            }
            for tid, t in self._templates.items()
        ]

        return {
            'templates': templates_list,
            'total_templates': len(templates_list),
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def load_template(
        self,
        template_id: str,
        report_name: str
    ) -> Dict[str, Any]:
        """
        Load a report from a template.

        Args:
            template_id: Template identifier
            report_name: Name for the new report

        Returns:
            Dictionary with new report details

        Example:
            >>> report = service.load_template(template_id, 'New Report')
        """
        if template_id not in self._templates:
            return {
                'error': 'Template not found',
                'template_id': template_id
            }

        template = self._templates[template_id]
        report_result = self.create_report(report_name)
        report_id = report_result['report_id']

        self._reports[report_id]['components'] = template['components'].copy()
        self._reports[report_id]['metrics'] = template['metrics'].copy()
        self._reports[report_id]['grouping'] = template['grouping']
        self._reports[report_id]['filters'] = template['filters'].copy()

        return {
            'report_id': report_id,
            'name': report_name,
            'template_id': template_id,
            'status': 'loaded',
            'created_at': self._reports[report_id]['created_at']
        }

    def get_builder_config(self) -> Dict[str, Any]:
        """
        Get report builder configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_builder_config()
        """
        return {
            'total_reports': len(self._reports),
            'total_templates': len(self._templates),
            'component_types': ['chart', 'table', 'text', 'metric_card', 'heatmap'],
            'supported_groupings': ['date', 'test_suite', 'model_version', 'demographic'],
            'available_metrics': self.get_available_metrics()['metrics']
        }
