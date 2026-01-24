"""
Test suite for defects routes resource-level access control.

Validates that tenant_id filtering is enforced on defect endpoints.
"""

import pytest
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent
ROUTES_DIR = PROJECT_ROOT / "backend" / "api" / "routes"
DEFECTS_ROUTES_FILE = ROUTES_DIR / "defects.py"


class TestDefectsRoutesFileExists:
    def test_routes_file_exists(self):
        assert DEFECTS_ROUTES_FILE.exists(), "defects.py should exist"


class TestImportsAccessControl:
    @pytest.fixture
    def route_content(self):
        return DEFECTS_ROUTES_FILE.read_text()

    def test_imports_check_resource_access(self, route_content):
        """Should import check_resource_access from auth module."""
        assert "from api.auth.access_control import check_resource_access" in route_content


class TestGetDefectTenantIsolation:
    """Test that get_defect_endpoint enforces tenant isolation."""

    @pytest.fixture
    def route_content(self):
        return DEFECTS_ROUTES_FILE.read_text()

    def test_get_defect_validates_tenant(self, route_content):
        """get_defect_endpoint should validate tenant access."""
        func_start = route_content.find("async def get_defect_endpoint(")
        func_end = route_content.find("async def ", func_start + 1)
        func_body = route_content[func_start:func_end]

        has_access_check = "check_resource_access" in func_body
        has_tenant_filter = "tenant_id" in func_body

        assert has_access_check or has_tenant_filter, \
            "get_defect_endpoint should validate tenant access"


class TestListDefectsTenantIsolation:
    """Test that list_defects_endpoint filters by tenant."""

    @pytest.fixture
    def route_content(self):
        return DEFECTS_ROUTES_FILE.read_text()

    def test_list_defects_filters_by_tenant(self, route_content):
        """list_defects_endpoint should filter by tenant_id."""
        func_start = route_content.find("async def list_defects_endpoint(")
        func_end = route_content.find("async def ", func_start + 1)
        func_body = route_content[func_start:func_end]

        assert "tenant_id" in func_body, \
            "list_defects_endpoint should filter by tenant_id"


class TestUpdateDefectTenantIsolation:
    """Test that update_defect_endpoint validates tenant."""

    @pytest.fixture
    def route_content(self):
        return DEFECTS_ROUTES_FILE.read_text()

    def test_update_defect_validates_tenant(self, route_content):
        """update_defect_endpoint should validate tenant access."""
        func_start = route_content.find("async def update_defect_endpoint(")
        func_end = route_content.find("async def ", func_start + 1)
        func_body = route_content[func_start:func_end]

        has_access_check = "check_resource_access" in func_body
        has_tenant_filter = "tenant_id" in func_body

        assert has_access_check or has_tenant_filter, \
            "update_defect_endpoint should validate tenant access"


class TestAssignDefectTenantIsolation:
    """Test that assign_defect_endpoint validates tenant."""

    @pytest.fixture
    def route_content(self):
        return DEFECTS_ROUTES_FILE.read_text()

    def test_assign_defect_validates_tenant(self, route_content):
        """assign_defect_endpoint should validate tenant access."""
        func_start = route_content.find("async def assign_defect_endpoint(")
        func_end = route_content.find("async def ", func_start + 1)
        func_body = route_content[func_start:func_end]

        has_access_check = "check_resource_access" in func_body
        has_tenant_filter = "tenant_id" in func_body

        assert has_access_check or has_tenant_filter, \
            "assign_defect_endpoint should validate tenant access"


class TestResolveDefectTenantIsolation:
    """Test that resolve_defect_endpoint validates tenant."""

    @pytest.fixture
    def route_content(self):
        return DEFECTS_ROUTES_FILE.read_text()

    def test_resolve_defect_validates_tenant(self, route_content):
        """resolve_defect_endpoint should validate tenant access."""
        func_start = route_content.find("async def resolve_defect_endpoint(")
        func_end = route_content.find("async def ", func_start + 1)
        if func_end == -1:
            func_end = len(route_content)
        func_body = route_content[func_start:func_end]

        has_access_check = "check_resource_access" in func_body
        has_tenant_filter = "tenant_id" in func_body

        assert has_access_check or has_tenant_filter, \
            "resolve_defect_endpoint should validate tenant access"
