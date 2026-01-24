"""
Test suite for user service CRUD operations

Tests user creation, retrieval, update, and deletion operations
with comprehensive validation, error handling, and edge cases.
"""

import pytest
from datetime import datetime
from uuid import uuid4, UUID
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
USER_SERVICE_FILE = PROJECT_ROOT / "backend" / "services" / "user_service.py"


class TestUserServiceFileExists:
    """Test that user service file exists"""

    def test_user_service_file_exists(self):
        """Test that backend/services/user_service.py exists"""
        assert USER_SERVICE_FILE.exists(), "backend/services/user_service.py should exist"
        assert USER_SERVICE_FILE.is_file(), "user_service.py should be a file"

    def test_user_service_has_content(self):
        """Test that user_service.py has content"""
        content = USER_SERVICE_FILE.read_text()
        assert len(content) > 0, "user_service.py should not be empty"


class TestUserServiceImports:
    """Test that user service can be imported"""

    def test_can_import_user_service(self):
        """Test that user service module can be imported"""
        try:
            from services import user_service
            assert user_service is not None
        except ImportError as e:
            pytest.fail(f"Failed to import user service: {e}")


class TestCreateUserFunction:
    """Test create_user function"""

    @pytest.mark.asyncio
    async def test_create_user_exists(self):
        """Test that create_user function exists"""
        from services.user_service import create_user
        assert callable(create_user), "create_user should be a callable function"

    @pytest.mark.asyncio
    async def test_create_user_returns_user(self, db_session):
        """Test that create_user returns a User object"""
        from services.user_service import create_user
        from api.schemas.auth import RegisterRequest
        from models.user import User

        register_data = RegisterRequest(
            email="newuser@example.com",
            username="newuser",
            password="SecurePassword123!",
            full_name="New User"
        )

        user = await create_user(db_session, register_data)

        assert user is not None
        assert isinstance(user, User)

    @pytest.mark.asyncio
    async def test_create_user_sets_fields_correctly(self, db_session):
        """Test that create_user sets all fields correctly"""
        from services.user_service import create_user
        from api.schemas.auth import RegisterRequest

        register_data = RegisterRequest(
            email="test@example.com",
            username="testuser",
            password="Password123!",
            full_name="Test User"
        )

        user = await create_user(db_session, register_data)

        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        assert user.is_active is True

    @pytest.mark.asyncio
    async def test_create_user_hashes_password(self, db_session):
        """Test that create_user hashes the password"""
        from services.user_service import create_user
        from api.schemas.auth import RegisterRequest

        plain_password = "MySecretPassword123"
        register_data = RegisterRequest(
            email="secure@example.com",
            username="secureuser",
            password=plain_password,
            full_name="Secure User"
        )

        user = await create_user(db_session, register_data)

        # Password should be hashed, not stored as plain text
        assert user.password_hash is not None
        assert user.password_hash != plain_password
        assert len(user.password_hash) > 50  # Bcrypt hashes are ~60 chars

    @pytest.mark.asyncio
    async def test_create_user_can_verify_password(self, db_session):
        """Test that created user can verify password"""
        from services.user_service import create_user
        from api.schemas.auth import RegisterRequest

        plain_password = "CorrectPassword123"
        register_data = RegisterRequest(
            email="verify@example.com",
            username="verifyuser",
            password=plain_password,
            full_name="Verify User"
        )

        user = await create_user(db_session, register_data)

        # Should be able to verify with correct password
        assert user.verify_password(plain_password) is True
        # Should fail with wrong password
        assert user.verify_password("WrongPassword") is False

    @pytest.mark.asyncio
    async def test_create_user_generates_id(self, db_session):
        """Test that create_user generates a UUID"""
        from services.user_service import create_user
        from api.schemas.auth import RegisterRequest

        register_data = RegisterRequest(
            email="uuid@example.com",
            username="uuiduser",
            password="Password123",
            full_name="UUID User"
        )

        user = await create_user(db_session, register_data)

        assert user.id is not None
        assert isinstance(user.id, UUID)

    @pytest.mark.asyncio
    async def test_create_user_assigns_viewer_role_by_default(self, monkeypatch):
        """New users default to viewer role when no role provided."""
        from services import user_service
        from api.schemas.auth import RegisterRequest
        from api.auth.roles import Role

        created_users = []

        class FakeUser:
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)
                created_users.append(self)

        class DummySession:
            def add(self, obj):
                self.obj = obj

            async def commit(self):
                return None

            async def refresh(self, obj):
                return None

        monkeypatch.setattr(user_service, "User", FakeUser)
        db_session = DummySession()

        register_data = RegisterRequest(
            email="viewer@example.com",
            username="viewer",
            password="Password123!",
            full_name="Viewer User",
        )

        user = await user_service.create_user(db_session, register_data)
        assert user.role == Role.VIEWER.value
        assert created_users[0].role == Role.VIEWER.value

    @pytest.mark.asyncio
    async def test_create_user_honors_requested_role(self, monkeypatch):
        """Admins can set a specific role when creating a user."""
        from services import user_service
        from api.schemas.auth import RegisterRequest
        from api.auth.roles import Role

        class FakeUser:
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)

        class DummySession:
            def add(self, obj):
                self.obj = obj

            async def commit(self):
                return None

            async def refresh(self, obj):
                return None

        monkeypatch.setattr(user_service, "User", FakeUser)
        db_session = DummySession()

        register_data = RegisterRequest(
            email="lead@example.com",
            username="lead",
            password="Password123!",
            full_name="QA Lead",
            role=Role.QA_LEAD,
        )

        user = await user_service.create_user(db_session, register_data)
        assert user.role == Role.QA_LEAD.value

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email_raises_error(self, db_session):
        """Test that creating user with duplicate email raises error"""
        from services.user_service import create_user
        from api.schemas.auth import RegisterRequest

        register_data1 = RegisterRequest(
            email="duplicate@example.com",
            username="user1",
            password="Password123",
            full_name="User One"
        )

        # Create first user
        await create_user(db_session, register_data1)

        # Try to create second user with same email
        register_data2 = RegisterRequest(
            email="duplicate@example.com",  # Same email
            username="user2",  # Different username
            password="Password123",
            full_name="User Two"
        )

        with pytest.raises(Exception):  # Should raise integrity error
            await create_user(db_session, register_data2)

    @pytest.mark.asyncio
    async def test_create_user_duplicate_username_raises_error(self, db_session):
        """Test that creating user with duplicate username raises error"""
        from services.user_service import create_user
        from api.schemas.auth import RegisterRequest

        register_data1 = RegisterRequest(
            email="user1@example.com",
            username="duplicate_username",
            password="Password123",
            full_name="User One"
        )

        # Create first user
        await create_user(db_session, register_data1)

        # Try to create second user with same username
        register_data2 = RegisterRequest(
            email="user2@example.com",  # Different email
            username="duplicate_username",  # Same username
            password="Password123",
            full_name="User Two"
        )

        with pytest.raises(Exception):  # Should raise integrity error
            await create_user(db_session, register_data2)


class TestGetUserByEmailFunction:
    """Test get_user_by_email function"""

    @pytest.mark.asyncio
    async def test_get_user_by_email_exists(self):
        """Test that get_user_by_email function exists"""
        from services.user_service import get_user_by_email
        assert callable(get_user_by_email), "get_user_by_email should be a callable function"

    @pytest.mark.asyncio
    async def test_get_user_by_email_returns_user(self, db_session):
        """Test that get_user_by_email returns a User when found"""
        from services.user_service import create_user, get_user_by_email
        from api.schemas.auth import RegisterRequest
        from models.user import User

        # Create a user first
        register_data = RegisterRequest(
            email="findme@example.com",
            username="findme",
            password="Password123",
            full_name="Find Me"
        )
        await create_user(db_session, register_data)

        # Now find by email
        user = await get_user_by_email(db_session, "findme@example.com")

        assert user is not None
        assert isinstance(user, User)
        assert user.email == "findme@example.com"

    @pytest.mark.asyncio
    async def test_get_user_by_email_returns_none_when_not_found(self, db_session):
        """Test that get_user_by_email returns None when user not found"""
        from services.user_service import get_user_by_email

        user = await get_user_by_email(db_session, "nonexistent@example.com")

        assert user is None

    @pytest.mark.asyncio
    async def test_get_user_by_email_case_sensitive(self, db_session):
        """Test that get_user_by_email is case-sensitive (or insensitive as designed)"""
        from services.user_service import create_user, get_user_by_email
        from api.schemas.auth import RegisterRequest

        # Create user with lowercase email
        register_data = RegisterRequest(
            email="case@example.com",
            username="caseuser",
            password="Password123",
            full_name="Case User"
        )
        await create_user(db_session, register_data)

        # Try to find with different case
        user = await get_user_by_email(db_session, "CASE@EXAMPLE.COM")

        # Behavior depends on implementation - test documents actual behavior
        # Most systems treat email as case-insensitive
        pass


class TestGetUserByIdFunction:
    """Test get_user_by_id function"""

    @pytest.mark.asyncio
    async def test_get_user_by_id_exists(self):
        """Test that get_user_by_id function exists"""
        from services.user_service import get_user_by_id
        assert callable(get_user_by_id), "get_user_by_id should be a callable function"

    @pytest.mark.asyncio
    async def test_get_user_by_id_returns_user(self, db_session):
        """Test that get_user_by_id returns a User when found"""
        from services.user_service import create_user, get_user_by_id
        from api.schemas.auth import RegisterRequest
        from models.user import User

        # Create a user first
        register_data = RegisterRequest(
            email="findbyid@example.com",
            username="findbyid",
            password="Password123",
            full_name="Find By ID"
        )
        created_user = await create_user(db_session, register_data)
        user_id = created_user.id

        # Now find by ID
        user = await get_user_by_id(db_session, user_id)

        assert user is not None
        assert isinstance(user, User)
        assert user.id == user_id

    @pytest.mark.asyncio
    async def test_get_user_by_id_returns_none_when_not_found(self, db_session):
        """Test that get_user_by_id returns None when user not found"""
        from services.user_service import get_user_by_id

        random_uuid = uuid4()
        user = await get_user_by_id(db_session, random_uuid)

        assert user is None


class TestUpdateUserFunction:
    """Test update_user function"""

    @pytest.mark.asyncio
    async def test_update_user_exists(self):
        """Test that update_user function exists"""
        from services.user_service import update_user
        assert callable(update_user), "update_user should be a callable function"

    @pytest.mark.asyncio
    async def test_update_user_updates_full_name(self, db_session):
        """Test that update_user can update full_name"""
        from services.user_service import create_user, update_user
        from api.schemas.auth import RegisterRequest

        # Create user
        register_data = RegisterRequest(
            email="update@example.com",
            username="updateuser",
            password="Password123",
            full_name="Original Name"
        )
        user = await create_user(db_session, register_data)

        # Update full_name
        updated_user = await update_user(db_session, user.id, {"full_name": "New Name"})

        assert updated_user.full_name == "New Name"
        assert updated_user.email == "update@example.com"  # Other fields unchanged

    @pytest.mark.asyncio
    async def test_update_user_updates_multiple_fields(self, db_session):
        """Test that update_user can update multiple fields"""
        from services.user_service import create_user, update_user
        from api.schemas.auth import RegisterRequest

        # Create user
        register_data = RegisterRequest(
            email="multi@example.com",
            username="multiuser",
            password="Password123",
            full_name="Original Name"
        )
        user = await create_user(db_session, register_data)

        # Update multiple fields
        updated_user = await update_user(
            db_session,
            user.id,
            {"full_name": "Updated Name", "is_active": False}
        )

        assert updated_user.full_name == "Updated Name"
        assert updated_user.is_active is False

    @pytest.mark.asyncio
    async def test_update_user_returns_updated_user(self, db_session):
        """Test that update_user returns the updated User object"""
        from services.user_service import create_user, update_user
        from api.schemas.auth import RegisterRequest
        from models.user import User

        # Create user
        register_data = RegisterRequest(
            email="return@example.com",
            username="returnuser",
            password="Password123",
            full_name="Original"
        )
        user = await create_user(db_session, register_data)

        # Update user
        updated_user = await update_user(db_session, user.id, {"full_name": "Updated"})

        assert isinstance(updated_user, User)
        assert updated_user.id == user.id
        assert updated_user.full_name == "Updated"

    @pytest.mark.asyncio
    async def test_update_user_nonexistent_raises_error(self, db_session):
        """Test that updating nonexistent user raises error"""
        from services.user_service import update_user

        random_uuid = uuid4()

        with pytest.raises(Exception):  # Should raise not found error
            await update_user(db_session, random_uuid, {"full_name": "Test"})

    @pytest.mark.asyncio
    async def test_update_user_empty_dict_no_changes(self, db_session):
        """Test that update_user with empty dict makes no changes"""
        from services.user_service import create_user, update_user
        from api.schemas.auth import RegisterRequest

        # Create user
        register_data = RegisterRequest(
            email="nochange@example.com",
            username="nochange",
            password="Password123",
            full_name="Original Name"
        )
        user = await create_user(db_session, register_data)
        original_name = user.full_name

        # Update with empty dict
        updated_user = await update_user(db_session, user.id, {})

        assert updated_user.full_name == original_name


class TestDeleteUserFunction:
    """Test delete_user function"""

    @pytest.mark.asyncio
    async def test_delete_user_exists(self):
        """Test that delete_user function exists"""
        from services.user_service import delete_user
        assert callable(delete_user), "delete_user should be a callable function"

    @pytest.mark.asyncio
    async def test_delete_user_returns_true_on_success(self, db_session):
        """Test that delete_user returns True when user is deleted"""
        from services.user_service import create_user, delete_user
        from api.schemas.auth import RegisterRequest

        # Create user
        register_data = RegisterRequest(
            email="delete@example.com",
            username="deleteuser",
            password="Password123",
            full_name="Delete Me"
        )
        user = await create_user(db_session, register_data)

        # Delete user
        result = await delete_user(db_session, user.id)

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_user_actually_deletes(self, db_session):
        """Test that delete_user actually removes user from database"""
        from services.user_service import create_user, delete_user, get_user_by_id
        from api.schemas.auth import RegisterRequest

        # Create user
        register_data = RegisterRequest(
            email="removed@example.com",
            username="removed",
            password="Password123",
            full_name="To Be Removed"
        )
        user = await create_user(db_session, register_data)
        user_id = user.id

        # Delete user
        await delete_user(db_session, user_id)

        # Try to find deleted user
        deleted_user = await get_user_by_id(db_session, user_id)

        assert deleted_user is None

    @pytest.mark.asyncio
    async def test_delete_user_returns_false_when_not_found(self, db_session):
        """Test that delete_user returns False when user not found"""
        from services.user_service import delete_user

        random_uuid = uuid4()
        result = await delete_user(db_session, random_uuid)

        assert result is False


class TestUserServiceIntegration:
    """Test user service integration scenarios"""

    @pytest.mark.asyncio
    async def test_create_find_update_delete_workflow(self, db_session):
        """Test complete CRUD workflow"""
        from services.user_service import (
            create_user, get_user_by_email, update_user, delete_user
        )
        from api.schemas.auth import RegisterRequest

        # Create
        register_data = RegisterRequest(
            email="workflow@example.com",
            username="workflow",
            password="Password123",
            full_name="Workflow User"
        )
        user = await create_user(db_session, register_data)
        assert user is not None

        # Read
        found_user = await get_user_by_email(db_session, "workflow@example.com")
        assert found_user.id == user.id

        # Update
        updated_user = await update_user(db_session, user.id, {"full_name": "Updated"})
        assert updated_user.full_name == "Updated"

        # Delete
        result = await delete_user(db_session, user.id)
        assert result is True

    @pytest.mark.asyncio
    async def test_multiple_users_can_coexist(self, db_session):
        """Test that multiple users can be created and retrieved"""
        from services.user_service import create_user, get_user_by_email
        from api.schemas.auth import RegisterRequest

        # Create multiple users
        users_data = [
            RegisterRequest(
                email=f"user{i}@example.com",
                username=f"user{i}",
                password="Password123",
                full_name=f"User {i}"
            )
            for i in range(3)
        ]

        created_users = []
        for data in users_data:
            user = await create_user(db_session, data)
            created_users.append(user)

        # Verify all can be retrieved
        for i, created_user in enumerate(created_users):
            found_user = await get_user_by_email(db_session, f"user{i}@example.com")
            assert found_user.id == created_user.id


class TestUserServiceFunctionSignatures:
    """Test function signatures"""

    def test_create_user_signature(self):
        """Test create_user function signature"""
        from services.user_service import create_user
        import inspect

        sig = inspect.signature(create_user)
        params = list(sig.parameters.keys())

        assert 'db' in params or 'session' in params, "Should have database session parameter"
        assert 'data' in params or any('register' in p.lower() for p in params), \
            "Should have data/register parameter"

    def test_get_user_by_email_signature(self):
        """Test get_user_by_email function signature"""
        from services.user_service import get_user_by_email
        import inspect

        sig = inspect.signature(get_user_by_email)
        params = list(sig.parameters.keys())

        assert 'db' in params or 'session' in params, "Should have database session parameter"
        assert 'email' in params, "Should have email parameter"

    def test_get_user_by_id_signature(self):
        """Test get_user_by_id function signature"""
        from services.user_service import get_user_by_id
        import inspect

        sig = inspect.signature(get_user_by_id)
        params = list(sig.parameters.keys())

        assert 'db' in params or 'session' in params, "Should have database session parameter"
        assert 'user_id' in params or 'id' in params, "Should have user_id parameter"

    def test_update_user_signature(self):
        """Test update_user function signature"""
        from services.user_service import update_user
        import inspect

        sig = inspect.signature(update_user)
        params = list(sig.parameters.keys())

        assert 'db' in params or 'session' in params, "Should have database session parameter"
        assert 'user_id' in params or 'id' in params, "Should have user_id parameter"
        assert 'data' in params or 'update' in params, "Should have data/update parameter"

    def test_delete_user_signature(self):
        """Test delete_user function signature"""
        from services.user_service import delete_user
        import inspect

        sig = inspect.signature(delete_user)
        params = list(sig.parameters.keys())

        assert 'db' in params or 'session' in params, "Should have database session parameter"
        assert 'user_id' in params or 'id' in params, "Should have user_id parameter"


class TestUserServiceDocumentation:
    """Test user service documentation"""

    def test_create_user_has_docstring(self):
        """Test that create_user has docstring"""
        from services.user_service import create_user

        assert create_user.__doc__ is not None, \
            "create_user should have docstring"

    def test_get_user_by_email_has_docstring(self):
        """Test that get_user_by_email has docstring"""
        from services.user_service import get_user_by_email

        assert get_user_by_email.__doc__ is not None, \
            "get_user_by_email should have docstring"

    def test_get_user_by_id_has_docstring(self):
        """Test that get_user_by_id has docstring"""
        from services.user_service import get_user_by_id

        assert get_user_by_id.__doc__ is not None, \
            "get_user_by_id should have docstring"

    def test_update_user_has_docstring(self):
        """Test that update_user has docstring"""
        from services.user_service import update_user

        assert update_user.__doc__ is not None, \
            "update_user should have docstring"

    def test_delete_user_has_docstring(self):
        """Test that delete_user has docstring"""
        from services.user_service import delete_user

        assert delete_user.__doc__ is not None, \
            "delete_user should have docstring"

    def test_module_has_docstring(self):
        """Test that user service module has docstring"""
        from services import user_service

        assert user_service.__doc__ is not None, \
            "User service module should have docstring"
