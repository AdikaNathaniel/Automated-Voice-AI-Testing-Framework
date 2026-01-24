"""
Test suite for Capacity Planning Tools Service.

This service provides capacity planning capabilities for
resource projection, cost estimation, and infrastructure sizing.

Components:
- Resource projection based on growth
- Cost estimation per test volume
- Infrastructure right-sizing recommendations
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestCapacityPlanningServiceExists:
    """Test that capacity planning service exists"""

    @pytest.fixture
    def service_file_content(self):
        """Read the capacity planning service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'capacity_planning_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        """Test that capacity_planning_service.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'capacity_planning_service.py'
        )
        assert os.path.exists(service_file), (
            "capacity_planning_service.py should exist"
        )

    def test_service_class_exists(self, service_file_content):
        """Test that CapacityPlanningService class exists"""
        assert 'class CapacityPlanningService' in service_file_content


class TestResourceProjection:
    """Test resource projection based on growth"""

    @pytest.fixture
    def service_file_content(self):
        """Read the capacity planning service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'capacity_planning_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_project_resources_method(self, service_file_content):
        """Test project_resources method exists"""
        assert 'def project_resources(' in service_file_content

    def test_has_set_growth_rate_method(self, service_file_content):
        """Test set_growth_rate method exists"""
        assert 'def set_growth_rate(' in service_file_content

    def test_has_get_projection_method(self, service_file_content):
        """Test get_projection method exists"""
        assert 'def get_projection(' in service_file_content

    def test_has_forecast_capacity_method(self, service_file_content):
        """Test forecast_capacity method exists"""
        assert 'def forecast_capacity(' in service_file_content


class TestCostEstimation:
    """Test cost estimation per test volume"""

    @pytest.fixture
    def service_file_content(self):
        """Read the capacity planning service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'capacity_planning_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_estimate_cost_method(self, service_file_content):
        """Test estimate_cost method exists"""
        assert 'def estimate_cost(' in service_file_content

    def test_has_set_cost_model_method(self, service_file_content):
        """Test set_cost_model method exists"""
        assert 'def set_cost_model(' in service_file_content

    def test_has_get_cost_breakdown_method(self, service_file_content):
        """Test get_cost_breakdown method exists"""
        assert 'def get_cost_breakdown(' in service_file_content

    def test_has_calculate_roi_method(self, service_file_content):
        """Test calculate_roi method exists"""
        assert 'def calculate_roi(' in service_file_content


class TestInfrastructureSizing:
    """Test infrastructure right-sizing recommendations"""

    @pytest.fixture
    def service_file_content(self):
        """Read the capacity planning service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'capacity_planning_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_recommend_sizing_method(self, service_file_content):
        """Test recommend_sizing method exists"""
        assert 'def recommend_sizing(' in service_file_content

    def test_has_analyze_utilization_method(self, service_file_content):
        """Test analyze_utilization method exists"""
        assert 'def analyze_utilization(' in service_file_content

    def test_has_get_optimization_suggestions_method(self, service_file_content):
        """Test get_optimization_suggestions method exists"""
        assert 'def get_optimization_suggestions(' in service_file_content


class TestPlanningReports:
    """Test capacity planning reports"""

    @pytest.fixture
    def service_file_content(self):
        """Read the capacity planning service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'capacity_planning_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_generate_plan_method(self, service_file_content):
        """Test generate_plan method exists"""
        assert 'def generate_plan(' in service_file_content

    def test_has_get_planning_summary_method(self, service_file_content):
        """Test get_planning_summary method exists"""
        assert 'def get_planning_summary(' in service_file_content


class TestTypeHints:
    """Test type hints for capacity planning service"""

    @pytest.fixture
    def service_file_content(self):
        """Read the capacity planning service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'capacity_planning_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_imports_typing_modules(self, service_file_content):
        """Test typing modules are imported"""
        assert 'from typing import' in service_file_content

    def test_uses_dict_type_hint(self, service_file_content):
        """Test Dict type hint is used"""
        assert 'Dict[' in service_file_content

    def test_uses_list_type_hint(self, service_file_content):
        """Test List type hint is used"""
        assert 'List[' in service_file_content


class TestDocstrings:
    """Test comprehensive documentation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the capacity planning service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'capacity_planning_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        """Test module has docstring"""
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        """Test class has docstring"""
        if 'class CapacityPlanningService' in service_file_content:
            idx = service_file_content.find('class CapacityPlanningService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
