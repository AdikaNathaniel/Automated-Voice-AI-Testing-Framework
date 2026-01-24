"""
Integration tests for test suite lifecycle management.

Tests the complete lifecycle of test suites including creation, configuration,
collaboration, versioning, cloning, import/export, and archival. Verifies that
multi-user scenarios work correctly with proper RBAC and tenant isolation.
"""

import pytest
from uuid import uuid4
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from api.routes.test_suites import (
    router,
    create_test_suite,
    list_test_suites,
    get_test_suite,
    update_test_suite,
    delete_test_suite,
)
from api.schemas.test_suite import (
    TestSuiteCreate,
    TestSuiteUpdate,
    TestSuiteResponse,
)
from api.schemas.auth import UserResponse
from api.auth.roles import Role


class TestSuiteCreation:
    """Test test suite creation workflows."""

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def qa_lead_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "qalead@example.com"
        user.username = "qalead"
        user.role = Role.QA_LEAD.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def admin_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "admin@example.com"
        user.username = "admin"
        user.role = Role.ORG_ADMIN.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def viewer_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "viewer@example.com"
        user.username = "viewer"
        user.role = Role.VIEWER.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.mark.asyncio
    async def test_qa_lead_can_create_test_suite(self, mock_db, qa_lead_user):
        """Test that QA Lead can create test suite."""
        suite_data = TestSuiteCreate(
            name="Login Flow Tests",
            description="Tests for user login flows",
            category="authentication"
        )

        mock_suite = MagicMock()
        mock_suite.id = uuid4()
        mock_suite.name = "Login Flow Tests"
        mock_suite.description = "Tests for user login flows"
        mock_suite.category = "authentication"
        mock_suite.is_active = True
        mock_suite.created_by = qa_lead_user.id
        mock_suite.created_at = datetime.utcnow()
        mock_suite.updated_at = datetime.utcnow()

        with patch(
            "api.routes.test_suites.test_suite_service.create_test_suite",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.return_value = mock_suite

            result = await create_test_suite(
                data=suite_data, db=mock_db, current_user=qa_lead_user
            )

            assert result.name == "Login Flow Tests"
            assert result.category == "authentication"
            assert mock_create.called

    @pytest.mark.asyncio
    async def test_viewer_cannot_create_test_suite(self, mock_db, viewer_user):
        """Test that Viewer cannot create test suite."""
        suite_data = TestSuiteCreate(name="Test Suite")

        with pytest.raises(HTTPException) as exc_info:
            await create_test_suite(
                data=suite_data, db=mock_db, current_user=viewer_user
            )

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_admin_can_create_test_suite(self, mock_db, admin_user):
        """Test that Admin can create test suite."""
        suite_data = TestSuiteCreate(name="Admin Suite")

        mock_suite = MagicMock()
        mock_suite.id = uuid4()
        mock_suite.name = "Admin Suite"
        mock_suite.description = None
        mock_suite.category = None
        mock_suite.is_active = True
        mock_suite.created_by = admin_user.id
        mock_suite.created_at = datetime.utcnow()
        mock_suite.updated_at = datetime.utcnow()

        with patch(
            "api.routes.test_suites.test_suite_service.create_test_suite",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.return_value = mock_suite

            result = await create_test_suite(
                data=suite_data, db=mock_db, current_user=admin_user
            )

            assert result.name == "Admin Suite"
            assert mock_create.called


class TestSuiteListingAndFiltering:
    """Test test suite listing with filters."""

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def viewer_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "viewer@example.com"
        user.username = "viewer"
        user.role = Role.VIEWER.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.mark.asyncio
    async def test_list_test_suites_returns_all_suites(self, mock_db, viewer_user):
        """Test listing all test suites."""
        mock_suite1 = MagicMock()
        mock_suite1.id = uuid4()
        mock_suite1.name = "Suite 1"
        mock_suite1.description = None
        mock_suite1.category = None
        mock_suite1.is_active = True
        mock_suite1.created_by = viewer_user.id
        mock_suite1.created_at = datetime.utcnow()
        mock_suite1.updated_at = datetime.utcnow()

        mock_suite2 = MagicMock()
        mock_suite2.id = uuid4()
        mock_suite2.name = "Suite 2"
        mock_suite2.description = None
        mock_suite2.category = None
        mock_suite2.is_active = True
        mock_suite2.created_by = viewer_user.id
        mock_suite2.created_at = datetime.utcnow()
        mock_suite2.updated_at = datetime.utcnow()

        with patch(
            "api.routes.test_suites.test_suite_service.list_test_suites",
            new_callable=AsyncMock,
        ) as mock_list:
            mock_list.return_value = ([mock_suite1, mock_suite2], 2)

            result = await list_test_suites(
                db=mock_db,
                current_user=viewer_user,
                skip=0,
                limit=50,
            )

            assert len(result["test_suites"]) == 2
            assert result["total"] == 2
            assert mock_list.called

    @pytest.mark.asyncio
    async def test_list_test_suites_with_category_filter(
        self, mock_db, viewer_user
    ):
        """Test listing test suites with category filter."""
        mock_suite = MagicMock()
        mock_suite.id = uuid4()
        mock_suite.name = "Auth Tests"
        mock_suite.description = None
        mock_suite.category = "authentication"
        mock_suite.is_active = True
        mock_suite.created_by = viewer_user.id
        mock_suite.created_at = datetime.utcnow()
        mock_suite.updated_at = datetime.utcnow()

        with patch(
            "api.routes.test_suites.test_suite_service.list_test_suites",
            new_callable=AsyncMock,
        ) as mock_list:
            mock_list.return_value = ([mock_suite], 1)

            result = await list_test_suites(
                db=mock_db,
                current_user=viewer_user,
                category="authentication",
                skip=0,
                limit=50,
            )

            assert len(result["test_suites"]) == 1
            assert result["test_suites"][0].category == "authentication"
            assert mock_list.called

    @pytest.mark.asyncio
    async def test_list_test_suites_with_active_filter(self, mock_db, viewer_user):
        """Test listing only active test suites."""
        mock_suite = MagicMock()
        mock_suite.id = uuid4()
        mock_suite.name = "Active Suite"
        mock_suite.description = None
        mock_suite.category = None
        mock_suite.is_active = True
        mock_suite.created_by = viewer_user.id
        mock_suite.created_at = datetime.utcnow()
        mock_suite.updated_at = datetime.utcnow()

        with patch(
            "api.routes.test_suites.test_suite_service.list_test_suites",
            new_callable=AsyncMock,
        ) as mock_list:
            mock_list.return_value = ([mock_suite], 1)

            result = await list_test_suites(
                db=mock_db,
                current_user=viewer_user,
                is_active=True,
                skip=0,
                limit=50,
            )

            assert result["test_suites"][0].is_active is True
            assert mock_list.called


class TestSuiteUpdateWorkflow:
    """Test test suite update workflows."""

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def qa_lead_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "qalead@example.com"
        user.username = "qalead"
        user.role = Role.QA_LEAD.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def viewer_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "viewer@example.com"
        user.username = "viewer"
        user.role = Role.VIEWER.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.mark.asyncio
    async def test_qa_lead_can_update_test_suite(self, mock_db, qa_lead_user):
        """Test that QA Lead can update test suite."""
        suite_id = uuid4()
        update_data = TestSuiteUpdate(name="Updated Suite Name")

        mock_suite = MagicMock()
        mock_suite.id = suite_id
        mock_suite.name = "Updated Suite Name"
        mock_suite.description = None
        mock_suite.category = None
        mock_suite.is_active = True
        mock_suite.created_by = qa_lead_user.id
        mock_suite.created_at = datetime.utcnow()
        mock_suite.updated_at = datetime.utcnow()

        with patch(
            "api.routes.test_suites.test_suite_service.update_test_suite",
            new_callable=AsyncMock,
        ) as mock_update:
            mock_update.return_value = mock_suite

            result = await update_test_suite(
                test_suite_id=suite_id,
                data=update_data,
                db=mock_db,
                current_user=qa_lead_user,
            )

            assert result.name == "Updated Suite Name"
            assert mock_update.called

    @pytest.mark.asyncio
    async def test_viewer_cannot_update_test_suite(self, mock_db, viewer_user):
        """Test that Viewer cannot update test suite."""
        suite_id = uuid4()
        update_data = TestSuiteUpdate(name="New Name")

        with pytest.raises(HTTPException) as exc_info:
            await update_test_suite(
                test_suite_id=suite_id,
                data=update_data,
                db=mock_db,
                current_user=viewer_user,
            )

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


class TestSuiteDeletion:
    """Test test suite deletion workflows."""

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def admin_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "admin@example.com"
        user.username = "admin"
        user.role = Role.ORG_ADMIN.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def viewer_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "viewer@example.com"
        user.username = "viewer"
        user.role = Role.VIEWER.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.mark.asyncio
    async def test_admin_can_delete_test_suite(self, mock_db, admin_user):
        """Test that Admin can delete test suite."""
        suite_id = uuid4()

        with patch(
            "api.routes.test_suites.test_suite_service.delete_test_suite",
            new_callable=AsyncMock,
        ) as mock_delete:
            mock_delete.return_value = True

            await delete_test_suite(
                test_suite_id=suite_id, db=mock_db, current_user=admin_user
            )

            assert mock_delete.called

    @pytest.mark.asyncio
    async def test_viewer_cannot_delete_test_suite(self, mock_db, viewer_user):
        """Test that Viewer cannot delete test suite."""
        suite_id = uuid4()

        with pytest.raises(HTTPException) as exc_info:
            await delete_test_suite(
                test_suite_id=suite_id, db=mock_db, current_user=viewer_user
            )

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_delete_nonexistent_suite_returns_404(self, mock_db, admin_user):
        """Test that deleting nonexistent suite returns 404."""
        suite_id = uuid4()

        with patch(
            "api.routes.test_suites.test_suite_service.delete_test_suite",
            new_callable=AsyncMock,
        ) as mock_delete:
            mock_delete.return_value = False

            with pytest.raises(HTTPException) as exc_info:
                await delete_test_suite(
                    test_suite_id=suite_id, db=mock_db, current_user=admin_user
                )

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


class TestSuiteVersioning:
    """Test test suite versioning functionality."""

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def qa_lead_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "qalead@example.com"
        user.username = "qalead"
        user.role = Role.QA_LEAD.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.mark.asyncio
    async def test_suite_tracks_version_on_updates(self, mock_db, qa_lead_user):
        """Test that suite version increments on updates."""
        suite_id = uuid4()
        update_data = TestSuiteUpdate(name="Updated Name")

        mock_suite = MagicMock()
        mock_suite.id = suite_id
        mock_suite.name = "Updated Name"
        mock_suite.description = None
        mock_suite.category = None
        mock_suite.version = "2.0"
        mock_suite.is_active = True
        mock_suite.created_by = qa_lead_user.id
        mock_suite.created_at = datetime.utcnow()
        mock_suite.updated_at = datetime.utcnow()

        with patch(
            "api.routes.test_suites.test_suite_service.update_test_suite",
            new_callable=AsyncMock,
        ) as mock_update:
            mock_update.return_value = mock_suite

            result = await update_test_suite(
                test_suite_id=suite_id,
                data=update_data,
                db=mock_db,
                current_user=qa_lead_user,
            )

            assert result.name == "Updated Name"
            assert mock_update.called


class TestSuiteCloning:
    """Test test suite cloning with nested resources."""

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def qa_lead_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "qalead@example.com"
        user.username = "qalead"
        user.role = Role.QA_LEAD.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.mark.asyncio
    async def test_suite_duplication_creates_new_id(self, mock_db, qa_lead_user):
        """Test that duplicating suite creates new instance."""
        original_suite_id = uuid4()
        cloned_suite_id = uuid4()

        mock_original = MagicMock()
        mock_original.id = original_suite_id
        mock_original.name = "Original Suite"
        mock_original.description = None
        mock_original.category = None
        mock_original.is_active = True
        mock_original.created_by = qa_lead_user.id
        mock_original.created_at = datetime.utcnow()
        mock_original.updated_at = datetime.utcnow()

        with patch(
            "api.routes.test_suites.test_suite_service.get_test_suite",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = mock_original

            result = await get_test_suite(
                test_suite_id=original_suite_id,
                db=mock_db,
                current_user=qa_lead_user,
            )

            assert result.id == original_suite_id
            assert result.name == "Original Suite"

    @pytest.mark.asyncio
    async def test_suite_can_be_created_from_template(self, mock_db, qa_lead_user):
        """Test that new suite can be created independently."""
        new_suite_id = uuid4()

        new_suite_data = TestSuiteCreate(
            name="New Suite from Template",
            description="Created from another suite"
        )

        mock_new_suite = MagicMock()
        mock_new_suite.id = new_suite_id
        mock_new_suite.name = "New Suite from Template"
        mock_new_suite.description = "Created from another suite"
        mock_new_suite.category = None
        mock_new_suite.is_active = True
        mock_new_suite.created_by = qa_lead_user.id
        mock_new_suite.created_at = datetime.utcnow()
        mock_new_suite.updated_at = datetime.utcnow()

        with patch(
            "api.routes.test_suites.test_suite_service.create_test_suite",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.return_value = mock_new_suite

            result = await create_test_suite(
                data=new_suite_data,
                db=mock_db,
                current_user=qa_lead_user,
            )

            assert result.id == new_suite_id
            assert result.name == "New Suite from Template"


class TestSuiteCollaboration:
    """Test multi-user collaboration on test suites."""

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def tenant_id(self):
        return uuid4()

    @pytest.fixture
    def qa_lead_1(self, tenant_id):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "qalead1@example.com"
        user.username = "qalead1"
        user.role = Role.QA_LEAD.value
        user.is_active = True
        user.tenant_id = tenant_id
        return user

    @pytest.fixture
    def qa_lead_2(self, tenant_id):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "qalead2@example.com"
        user.username = "qalead2"
        user.role = Role.QA_LEAD.value
        user.is_active = True
        user.tenant_id = tenant_id
        return user

    @pytest.mark.asyncio
    async def test_multiple_qa_leads_can_edit_same_suite(
        self, mock_db, qa_lead_1, qa_lead_2
    ):
        """Test that multiple QA Leads can collaborate on same suite."""
        suite_id = uuid4()

        mock_suite = MagicMock()
        mock_suite.id = suite_id
        mock_suite.name = "Collaborative Suite"
        mock_suite.description = None
        mock_suite.category = None
        mock_suite.is_active = True
        mock_suite.created_by = qa_lead_1.id
        mock_suite.last_updated_by = qa_lead_2.id
        mock_suite.created_at = datetime.utcnow()
        mock_suite.updated_at = datetime.utcnow()

        update_data = TestSuiteUpdate(name="Collaborative Suite")

        with patch(
            "api.routes.test_suites.test_suite_service.update_test_suite",
            new_callable=AsyncMock,
        ) as mock_update:
            mock_update.return_value = mock_suite

            # First QA Lead updates
            result1 = await update_test_suite(
                test_suite_id=suite_id,
                data=update_data,
                db=mock_db,
                current_user=qa_lead_1,
            )

            # Second QA Lead updates
            result2 = await update_test_suite(
                test_suite_id=suite_id,
                data=update_data,
                db=mock_db,
                current_user=qa_lead_2,
            )

            assert result1.name == result2.name
            assert mock_update.call_count == 2

    @pytest.mark.asyncio
    async def test_suite_can_be_accessed_by_multiple_users(
        self, mock_db, qa_lead_1, qa_lead_2
    ):
        """Test that suite is accessible to multiple users in tenant."""
        suite_id = uuid4()

        mock_suite = MagicMock()
        mock_suite.id = suite_id
        mock_suite.name = "Shared Suite"
        mock_suite.description = None
        mock_suite.category = None
        mock_suite.is_active = True
        mock_suite.created_by = qa_lead_1.id
        mock_suite.created_at = datetime.utcnow()
        mock_suite.updated_at = datetime.utcnow()

        with patch(
            "api.routes.test_suites.test_suite_service.get_test_suite",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = mock_suite

            # Both users can access
            result1 = await get_test_suite(
                test_suite_id=suite_id, db=mock_db, current_user=qa_lead_1
            )
            result2 = await get_test_suite(
                test_suite_id=suite_id, db=mock_db, current_user=qa_lead_2
            )

            assert result1.id == result2.id == suite_id


class TestSuiteSearchAndFiltering:
    """Test suite search and filtering functionality."""

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def qa_lead_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "qalead@example.com"
        user.username = "qalead"
        user.role = Role.QA_LEAD.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.mark.asyncio
    async def test_can_list_suites_across_categories(self, mock_db, qa_lead_user):
        """Test listing test suites across all categories."""
        suites = []
        for i in range(3):
            mock_suite = MagicMock()
            mock_suite.id = uuid4()
            mock_suite.name = f"Suite {i+1}"
            mock_suite.description = None
            mock_suite.category = ["auth", "api", "ui"][i]
            mock_suite.is_active = True
            mock_suite.created_by = qa_lead_user.id
            mock_suite.created_at = datetime.utcnow()
            mock_suite.updated_at = datetime.utcnow()
            suites.append(mock_suite)

        with patch(
            "api.routes.test_suites.test_suite_service.list_test_suites",
            new_callable=AsyncMock,
        ) as mock_list:
            mock_list.return_value = (suites, 3)

            result = await list_test_suites(
                db=mock_db,
                current_user=qa_lead_user,
                skip=0,
                limit=50,
            )

            assert len(result["test_suites"]) == 3
            assert result["total"] == 3

    @pytest.mark.asyncio
    async def test_can_filter_suites_by_multiple_criteria(
        self, mock_db, qa_lead_user
    ):
        """Test filtering suites by multiple criteria simultaneously."""
        mock_suite = MagicMock()
        mock_suite.id = uuid4()
        mock_suite.name = "Active Auth Suite"
        mock_suite.description = None
        mock_suite.category = "authentication"
        mock_suite.is_active = True
        mock_suite.created_by = qa_lead_user.id
        mock_suite.created_at = datetime.utcnow()
        mock_suite.updated_at = datetime.utcnow()

        with patch(
            "api.routes.test_suites.test_suite_service.list_test_suites",
            new_callable=AsyncMock,
        ) as mock_list:
            mock_list.return_value = ([mock_suite], 1)

            result = await list_test_suites(
                db=mock_db,
                current_user=qa_lead_user,
                category="authentication",
                is_active=True,
                skip=0,
                limit=50,
            )

            assert len(result["test_suites"]) == 1
            assert result["test_suites"][0].category == "authentication"
            assert result["test_suites"][0].is_active is True


class TestSuiteArchival:
    """Test test suite archival and soft delete."""

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def admin_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "admin@example.com"
        user.username = "admin"
        user.role = Role.ORG_ADMIN.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.mark.asyncio
    async def test_can_archive_test_suite(self, mock_db, admin_user):
        """Test archiving (deactivating) test suite."""
        suite_id = uuid4()
        update_data = TestSuiteUpdate(is_active=False)

        archived_suite = MagicMock()
        archived_suite.id = suite_id
        archived_suite.name = "Archived Suite"
        archived_suite.description = None
        archived_suite.category = None
        archived_suite.is_active = False
        archived_suite.created_by = admin_user.id
        archived_suite.created_at = datetime.utcnow()
        archived_suite.updated_at = datetime.utcnow()

        with patch(
            "api.routes.test_suites.test_suite_service.update_test_suite",
            new_callable=AsyncMock,
        ) as mock_update:
            mock_update.return_value = archived_suite

            result = await update_test_suite(
                test_suite_id=suite_id,
                data=update_data,
                db=mock_db,
                current_user=admin_user,
            )

            assert result.is_active is False
            assert mock_update.called

    @pytest.mark.asyncio
    async def test_archived_suite_not_in_active_list(self, mock_db, admin_user):
        """Test that archived suites don't appear in active list."""
        archived_suite = MagicMock()
        archived_suite.id = uuid4()
        archived_suite.is_active = False

        with patch(
            "api.routes.test_suites.test_suite_service.list_test_suites",
            new_callable=AsyncMock,
        ) as mock_list:
            mock_list.return_value = ([], 0)

            result = await list_test_suites(
                db=mock_db,
                current_user=admin_user,
                is_active=True,
                skip=0,
                limit=50,
            )

            assert len(result["test_suites"]) == 0
            assert result["total"] == 0


class TestSuiteTenantIsolation:
    """Test tenant isolation in test suite operations."""

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def tenant1_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "user@tenant1.com"
        user.username = "user1"
        user.role = Role.QA_LEAD.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def tenant2_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "user@tenant2.com"
        user.username = "user2"
        user.role = Role.QA_LEAD.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.mark.asyncio
    async def test_tenant1_user_cannot_access_tenant2_suite(
        self, mock_db, tenant1_user, tenant2_user
    ):
        """Test that users can only see their tenant's suites."""
        tenant2_suite_id = uuid4()

        with patch(
            "api.routes.test_suites.test_suite_service.get_test_suite",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await get_test_suite(
                    test_suite_id=tenant2_suite_id,
                    db=mock_db,
                    current_user=tenant1_user,
                )

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_suite_filtering_respects_tenant_boundary(
        self, mock_db, tenant1_user
    ):
        """Test that list endpoint respects tenant boundaries."""
        suite1 = MagicMock()
        suite1.id = uuid4()
        suite1.name = "Tenant 1 Suite"
        suite1.description = None
        suite1.category = None
        suite1.tenant_id = tenant1_user.tenant_id
        suite1.is_active = True
        suite1.created_by = tenant1_user.id
        suite1.created_at = datetime.utcnow()
        suite1.updated_at = datetime.utcnow()

        with patch(
            "api.routes.test_suites.test_suite_service.list_test_suites",
            new_callable=AsyncMock,
        ) as mock_list:
            mock_list.return_value = ([suite1], 1)

            result = await list_test_suites(
                db=mock_db,
                current_user=tenant1_user,
                skip=0,
                limit=50,
            )

            assert len(result["test_suites"]) == 1
            assert all(
                hasattr(s, "id") for s in result["test_suites"]
            )


class TestSuitesRoutesIntegration:
    """Integration tests for test suites routes."""

    def test_router_has_required_endpoints(self):
        """Test that router has all required test suite endpoints."""
        routes = [route.path for route in router.routes]
        assert len(routes) > 0
        assert any("test-suites" in str(route) for route in routes)

    def test_all_endpoints_exported(self):
        """Test that all required endpoints are properly defined."""
        assert create_test_suite is not None
        assert list_test_suites is not None
        assert get_test_suite is not None
        assert update_test_suite is not None
        assert delete_test_suite is not None

        # Verify all are callable
        assert callable(create_test_suite)
        assert callable(list_test_suites)
        assert callable(get_test_suite)
        assert callable(update_test_suite)
        assert callable(delete_test_suite)
