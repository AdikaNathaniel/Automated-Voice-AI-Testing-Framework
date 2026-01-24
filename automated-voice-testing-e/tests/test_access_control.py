"""
Test suite for resource-level access control utility.

Validates that check_resource_access() properly enforces tenant isolation
and ownership validation.
"""

import pytest
from uuid import uuid4
from unittest.mock import MagicMock
from fastapi import HTTPException


class TestCheckResourceAccessExists:
    """Verify the access control function can be imported."""

    def test_import_check_resource_access(self):
        """check_resource_access should be importable from auth module."""
        from api.auth.access_control import check_resource_access
        assert callable(check_resource_access)


class TestTenantIsolation:
    """Test tenant_id enforcement between user and resource."""

    @pytest.fixture
    def user_with_tenant(self):
        """Create a mock user with tenant_id."""
        user = MagicMock()
        user.id = uuid4()
        user.tenant_id = uuid4()
        user.role = "viewer"
        return user

    @pytest.fixture
    def matching_resource(self, user_with_tenant):
        """Create a resource with matching tenant_id."""
        resource = MagicMock()
        resource.id = uuid4()
        resource.tenant_id = user_with_tenant.tenant_id
        resource.created_by = uuid4()  # Different user
        return resource

    @pytest.fixture
    def different_tenant_resource(self, user_with_tenant):
        """Create a resource with different tenant_id."""
        resource = MagicMock()
        resource.id = uuid4()
        resource.tenant_id = uuid4()  # Different tenant
        resource.created_by = uuid4()
        return resource

    def test_allows_access_when_tenant_matches(self, user_with_tenant, matching_resource):
        """Should allow access when user's tenant matches resource's tenant."""
        from api.auth.access_control import check_resource_access

        # Should not raise
        check_resource_access(user_with_tenant, matching_resource)

    def test_denies_access_when_tenant_differs(self, user_with_tenant, different_tenant_resource):
        """Should deny access when user's tenant differs from resource's tenant."""
        from api.auth.access_control import check_resource_access

        with pytest.raises(HTTPException) as exc_info:
            check_resource_access(user_with_tenant, different_tenant_resource)

        assert exc_info.value.status_code == 403
        assert "Access denied" in exc_info.value.detail

    def test_denies_access_when_resource_has_no_tenant(self, user_with_tenant):
        """Should deny access when resource has no tenant_id."""
        from api.auth.access_control import check_resource_access

        resource = MagicMock()
        resource.id = uuid4()
        resource.tenant_id = None

        with pytest.raises(HTTPException) as exc_info:
            check_resource_access(user_with_tenant, resource)

        assert exc_info.value.status_code == 403


class TestOwnershipValidation:
    """Test ownership validation when require_ownership is True."""

    @pytest.fixture
    def user(self):
        """Create a mock user."""
        user = MagicMock()
        user.id = uuid4()
        user.tenant_id = uuid4()
        user.role = "viewer"
        return user

    @pytest.fixture
    def owned_resource(self, user):
        """Create a resource owned by the user."""
        resource = MagicMock()
        resource.id = uuid4()
        resource.tenant_id = user.tenant_id
        resource.created_by = user.id
        return resource

    @pytest.fixture
    def unowned_resource(self, user):
        """Create a resource owned by another user in same tenant."""
        resource = MagicMock()
        resource.id = uuid4()
        resource.tenant_id = user.tenant_id
        resource.created_by = uuid4()  # Different user
        return resource

    def test_allows_access_to_owned_resource(self, user, owned_resource):
        """Should allow access when user owns the resource."""
        from api.auth.access_control import check_resource_access

        # Should not raise
        check_resource_access(user, owned_resource, require_ownership=True)

    def test_denies_access_to_unowned_resource(self, user, unowned_resource):
        """Should deny access when user doesn't own the resource and ownership required."""
        from api.auth.access_control import check_resource_access

        with pytest.raises(HTTPException) as exc_info:
            check_resource_access(user, unowned_resource, require_ownership=True)

        assert exc_info.value.status_code == 403
        assert "ownership" in exc_info.value.detail.lower()

    def test_allows_unowned_resource_when_ownership_not_required(self, user, unowned_resource):
        """Should allow access to unowned resource when require_ownership is False."""
        from api.auth.access_control import check_resource_access

        # Should not raise (default is require_ownership=False)
        check_resource_access(user, unowned_resource)


class TestAdminBypassOwnership:
    """Test that admins can bypass ownership requirements."""

    @pytest.fixture
    def admin_user(self):
        """Create an admin user."""
        user = MagicMock()
        user.id = uuid4()
        user.tenant_id = uuid4()
        user.role = "admin"
        return user

    @pytest.fixture
    def unowned_resource(self, admin_user):
        """Create a resource owned by another user in same tenant."""
        resource = MagicMock()
        resource.id = uuid4()
        resource.tenant_id = admin_user.tenant_id
        resource.created_by = uuid4()  # Different user
        return resource

    def test_admin_can_access_unowned_resource(self, admin_user, unowned_resource):
        """Admin should be able to access unowned resources in their tenant."""
        from api.auth.access_control import check_resource_access

        # Should not raise even with require_ownership=True
        check_resource_access(admin_user, unowned_resource, require_ownership=True)

    def test_admin_cannot_access_different_tenant(self, admin_user):
        """Admin should not be able to access resources in different tenant."""
        from api.auth.access_control import check_resource_access

        resource = MagicMock()
        resource.id = uuid4()
        resource.tenant_id = uuid4()  # Different tenant
        resource.created_by = uuid4()

        with pytest.raises(HTTPException) as exc_info:
            check_resource_access(admin_user, resource)

        assert exc_info.value.status_code == 403


class TestQALeadBypassOwnership:
    """Test that QA leads can bypass ownership requirements."""

    @pytest.fixture
    def qa_lead_user(self):
        """Create a QA lead user."""
        user = MagicMock()
        user.id = uuid4()
        user.tenant_id = uuid4()
        user.role = "qa_lead"
        return user

    @pytest.fixture
    def unowned_resource(self, qa_lead_user):
        """Create a resource owned by another user in same tenant."""
        resource = MagicMock()
        resource.id = uuid4()
        resource.tenant_id = qa_lead_user.tenant_id
        resource.created_by = uuid4()
        return resource

    def test_qa_lead_can_access_unowned_resource(self, qa_lead_user, unowned_resource):
        """QA lead should be able to access unowned resources in their tenant."""
        from api.auth.access_control import check_resource_access

        # Should not raise even with require_ownership=True
        check_resource_access(qa_lead_user, unowned_resource, require_ownership=True)


class TestResourceWithoutCreatedBy:
    """Test handling of resources without created_by field."""

    @pytest.fixture
    def user(self):
        """Create a mock user."""
        user = MagicMock()
        user.id = uuid4()
        user.tenant_id = uuid4()
        user.role = "viewer"
        return user

    def test_handles_resource_without_created_by(self, user):
        """Should handle resources that don't have created_by field."""
        from api.auth.access_control import check_resource_access

        resource = MagicMock(spec=['id', 'tenant_id'])
        resource.id = uuid4()
        resource.tenant_id = user.tenant_id

        # Should not raise when ownership not required
        check_resource_access(user, resource, require_ownership=False)

    def test_denies_ownership_check_when_no_created_by(self, user):
        """Should deny access when ownership required but resource has no created_by."""
        from api.auth.access_control import check_resource_access

        resource = MagicMock(spec=['id', 'tenant_id'])
        resource.id = uuid4()
        resource.tenant_id = user.tenant_id

        with pytest.raises(HTTPException) as exc_info:
            check_resource_access(user, resource, require_ownership=True)

        assert exc_info.value.status_code == 403
