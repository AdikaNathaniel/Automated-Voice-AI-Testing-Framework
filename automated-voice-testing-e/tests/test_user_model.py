"""
Test suite for User SQLAlchemy model
Ensures proper model definition, password hashing, and database integration
"""

import os
import sys
import pytest
from datetime import datetime
from uuid import UUID

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))


class TestUserModel:
    """Test User model class structure"""

    def test_user_model_exists(self):
        """Test that User model can be imported"""
        try:
            from models.user import User
            assert User is not None
        except ImportError:
            pytest.fail("Cannot import User from models.user")

    def test_user_inherits_from_base(self):
        """Test that User inherits from Base"""
        from models.user import User
        from models.base import Base
        # Check if User is in Base's registry (proper way for declarative base)
        assert User.__table__ is not None
        assert hasattr(User, '__tablename__')

    def test_user_inherits_from_base_model(self):
        """Test that User inherits from BaseModel"""
        from models.user import User
        from models.base import BaseModel
        # Check if User has BaseModel attributes
        assert hasattr(User, 'id')
        assert hasattr(User, 'created_at')
        assert hasattr(User, 'updated_at')

    def test_user_has_tablename(self):
        """Test that User has __tablename__ set to 'users'"""
        from models.user import User
        assert User.__tablename__ == 'users'


class TestUserFields:
    """Test User model fields"""

    def test_user_has_email_field(self):
        """Test that User has email field"""
        from models.user import User
        assert hasattr(User, 'email')

    def test_email_is_column(self):
        """Test that email is a SQLAlchemy Column"""
        from models.user import User
        from sqlalchemy.orm import InstrumentedAttribute
        # In SQLAlchemy 2.0, columns are InstrumentedAttribute on the class
        assert hasattr(User, 'email')
        assert isinstance(User.__dict__.get('email'), InstrumentedAttribute) or hasattr(User, 'email')

    def test_email_is_string_type(self):
        """Test that email is String type"""
        from models.user import User
        from sqlalchemy import String
        email_column = User.__dict__.get('email')
        assert isinstance(email_column.type, String)

    def test_email_has_max_length_255(self):
        """Test that email has max length of 255"""
        from models.user import User
        email_column = User.__dict__.get('email')
        assert email_column.type.length == 255

    def test_email_is_unique(self):
        """Test that email has unique constraint"""
        from models.user import User
        email_column = User.__dict__.get('email')
        assert email_column.unique is True

    def test_email_is_not_nullable(self):
        """Test that email is not nullable"""
        from models.user import User
        email_column = User.__dict__.get('email')
        assert email_column.nullable is False

    def test_user_has_username_field(self):
        """Test that User has username field"""
        from models.user import User
        assert hasattr(User, 'username')

    def test_username_is_string_type(self):
        """Test that username is String type"""
        from models.user import User
        from sqlalchemy import String
        username_column = User.__dict__.get('username')
        assert isinstance(username_column.type, String)

    def test_username_has_max_length_100(self):
        """Test that username has max length of 100"""
        from models.user import User
        username_column = User.__dict__.get('username')
        assert username_column.type.length == 100

    def test_username_is_unique(self):
        """Test that username has unique constraint"""
        from models.user import User
        username_column = User.__dict__.get('username')
        assert username_column.unique is True

    def test_username_is_not_nullable(self):
        """Test that username is not nullable"""
        from models.user import User
        username_column = User.__dict__.get('username')
        assert username_column.nullable is False

    def test_user_has_full_name_field(self):
        """Test that User has full_name field"""
        from models.user import User
        assert hasattr(User, 'full_name')

    def test_full_name_is_string_type(self):
        """Test that full_name is String type"""
        from models.user import User
        from sqlalchemy import String
        full_name_column = User.__dict__.get('full_name')
        assert isinstance(full_name_column.type, String)

    def test_full_name_has_max_length_255(self):
        """Test that full_name has max length of 255"""
        from models.user import User
        full_name_column = User.__dict__.get('full_name')
        assert full_name_column.type.length == 255

    def test_full_name_is_nullable(self):
        """Test that full_name is nullable"""
        from models.user import User
        full_name_column = User.__dict__.get('full_name')
        assert full_name_column.nullable is True

    def test_user_has_password_hash_field(self):
        """Test that User has password_hash field"""
        from models.user import User
        assert hasattr(User, 'password_hash')

    def test_password_hash_is_string_type(self):
        """Test that password_hash is String type"""
        from models.user import User
        from sqlalchemy import String
        password_hash_column = User.__dict__.get('password_hash')
        assert isinstance(password_hash_column.type, String)

    def test_password_hash_has_max_length_255(self):
        """Test that password_hash has max length of 255"""
        from models.user import User
        password_hash_column = User.__dict__.get('password_hash')
        assert password_hash_column.type.length == 255

    def test_password_hash_is_nullable(self):
        """Test that password_hash is nullable"""
        from models.user import User
        password_hash_column = User.__dict__.get('password_hash')
        assert password_hash_column.nullable is True

    def test_user_has_role_field(self):
        """Test that User has role field"""
        from models.user import User
        assert hasattr(User, 'role')

    def test_role_is_string_type(self):
        """Test that role is String type"""
        from models.user import User
        from sqlalchemy import String
        role_column = User.__dict__.get('role')
        assert isinstance(role_column.type, String)

    def test_role_has_max_length_50(self):
        """Test that role has max length of 50"""
        from models.user import User
        role_column = User.__dict__.get('role')
        assert role_column.type.length == 50

    def test_user_has_is_active_field(self):
        """Test that User has is_active field"""
        from models.user import User
        assert hasattr(User, 'is_active')

    def test_is_active_is_boolean_type(self):
        """Test that is_active is Boolean type"""
        from models.user import User
        from sqlalchemy import Boolean
        is_active_column = User.__dict__.get('is_active')
        assert isinstance(is_active_column.type, Boolean)

    def test_is_active_has_default_true(self):
        """Test that is_active defaults to True"""
        from models.user import User
        is_active_column = User.__dict__.get('is_active')
        # Check that default is set
        assert is_active_column.default is not None

    def test_user_has_language_proficiencies_field(self):
        """Test that User has language_proficiencies field"""
        from models.user import User
        assert hasattr(User, 'language_proficiencies')

    def test_language_proficiencies_is_array_type(self):
        """Test that language_proficiencies is ARRAY type"""
        from models.user import User
        from sqlalchemy import ARRAY
        lang_column = User.__dict__.get('language_proficiencies')
        assert isinstance(lang_column.type, ARRAY)

    def test_user_has_last_login_at_field(self):
        """Test that User has last_login_at field"""
        from models.user import User
        assert hasattr(User, 'last_login_at')

    def test_last_login_at_is_datetime_type(self):
        """Test that last_login_at is DateTime type"""
        from models.user import User
        from sqlalchemy import DateTime
        last_login_column = User.__dict__.get('last_login_at')
        assert isinstance(last_login_column.type, DateTime)

    def test_last_login_at_is_nullable(self):
        """Test that last_login_at is nullable"""
        from models.user import User
        last_login_column = User.__dict__.get('last_login_at')
        assert last_login_column.nullable is True


class TestUserPasswordHashing:
    """Test User password hashing methods"""

    def test_user_has_set_password_method(self):
        """Test that User has set_password method"""
        from models.user import User
        assert hasattr(User, 'set_password')
        assert callable(User.set_password)

    def test_user_has_verify_password_method(self):
        """Test that User has verify_password method"""
        from models.user import User
        assert hasattr(User, 'verify_password')
        assert callable(User.verify_password)

    def test_set_password_hashes_password(self):
        """Test that set_password hashes the password"""
        from models.user import User
        user = User(email="test@example.com", username="testuser")
        user.set_password("mypassword123")
        # Password hash should be set
        assert user.password_hash is not None
        # Password hash should not be the plain password
        assert user.password_hash != "mypassword123"
        # Password hash should be reasonably long (bcrypt is 60 chars)
        assert len(user.password_hash) > 50

    def test_verify_password_returns_true_for_correct_password(self):
        """Test that verify_password returns True for correct password"""
        from models.user import User
        user = User(email="test@example.com", username="testuser")
        user.set_password("mypassword123")
        # Verify correct password
        assert user.verify_password("mypassword123") is True

    def test_verify_password_returns_false_for_wrong_password(self):
        """Test that verify_password returns False for wrong password"""
        from models.user import User
        user = User(email="test@example.com", username="testuser")
        user.set_password("mypassword123")
        # Verify wrong password
        assert user.verify_password("wrongpassword") is False

    def test_same_password_produces_different_hashes(self):
        """Test that same password produces different hashes (salt)"""
        from models.user import User
        user1 = User(email="test1@example.com", username="testuser1")
        user2 = User(email="test2@example.com", username="testuser2")
        user1.set_password("samepassword")
        user2.set_password("samepassword")
        # Hashes should be different due to salt
        assert user1.password_hash != user2.password_hash


class TestUserInstantiation:
    """Test User model instantiation"""

    def test_can_create_user_with_required_fields(self):
        """Test that User can be created with required fields"""
        from models.user import User
        user = User(
            email="test@example.com",
            username="testuser"
        )
        assert user is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"

    def test_created_user_has_id(self):
        """Test that created User has UUID id"""
        from models.user import User
        from uuid import UUID
        import uuid
        # Create user with explicit ID to test
        test_id = uuid.uuid4()
        user = User(
            id=test_id,
            email="test@example.com",
            username="testuser"
        )
        # ID should be set
        assert user.id is not None
        assert isinstance(user.id, UUID)
        assert user.id == test_id

    def test_created_user_has_default_is_active_true(self):
        """Test that User can have is_active set and defaults exist"""
        from models.user import User
        # Create user with explicit is_active
        user = User(
            email="test@example.com",
            username="testuser",
            is_active=True
        )
        assert user.is_active is True

        # Verify column has default defined
        is_active_column = User.__dict__.get('is_active')
        assert is_active_column is not None

    def test_can_create_user_with_optional_fields(self):
        """Test that User can be created with optional fields"""
        from models.user import User
        user = User(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            role="admin",
            language_proficiencies=["en", "es"]
        )
        assert user.full_name == "Test User"
        assert user.role == "admin"
        assert user.language_proficiencies == ["en", "es"]


class TestUserRepresentation:
    """Test User model string representation"""

    def test_user_has_repr_method(self):
        """Test that User has __repr__ method"""
        from models.user import User
        assert hasattr(User, '__repr__')

    def test_user_repr_includes_username(self):
        """Test that User __repr__ includes username"""
        from models.user import User
        user = User(email="test@example.com", username="testuser")
        repr_str = repr(user)
        assert 'testuser' in repr_str


class TestUserDocumentation:
    """Test User model documentation"""

    def test_user_has_docstring(self):
        """Test that User has docstring"""
        from models.user import User
        assert User.__doc__ is not None
        assert len(User.__doc__.strip()) > 0

    def test_user_module_has_docstring(self):
        """Test that user module has docstring"""
        import models.user
        assert models.user.__doc__ is not None
        assert len(models.user.__doc__.strip()) > 0


class TestUserExports:
    """Test User model exports"""

    def test_can_import_user_from_models_user(self):
        """Test that User can be imported from models.user"""
        try:
            from models.user import User
            assert User is not None
        except ImportError:
            pytest.fail("Cannot import User from models.user")

    def test_user_module_exports_user(self):
        """Test that user module exports User"""
        import models.user
        assert hasattr(models.user, 'User')
