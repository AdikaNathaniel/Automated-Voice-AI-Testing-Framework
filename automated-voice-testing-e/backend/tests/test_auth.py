"""
Unit tests for authentication functionality (TASK-142)

This module tests the authentication business logic including:
- User registration (user_service.create_user)
- User login validation
- Token refresh validation
- Current user retrieval
- Error handling and edge cases

Tests focus on service layer and helper functions, not HTTP endpoints.
HTTP endpoint integration tests are in tests/test_auth_endpoints.py
"""

import pytest
from datetime import timedelta
from uuid import uuid4, UUID

# Import authentication components
from api.schemas.auth import RegisterRequest, LoginRequest
from api.auth.password import hash_password, verify_password
from api.auth.jwt import create_access_token, create_refresh_token, decode_token
from services import user_service


# =============================================================================
# Test Registration (user_service.create_user)
# =============================================================================

class TestUserRegistration:
    """Test user registration functionality"""

    @pytest.mark.asyncio
    async def test_create_user_success(self, db_session):
        """Test successful user creation"""
        # Arrange
        register_data = RegisterRequest(
            email="newuser@example.com",
            username="newuser",
            password="SecurePassword123!",
            full_name="New User"
        )

        # Act
        user = await user_service.create_user(db_session, register_data)

        # Assert
        assert user is not None
        assert user.id is not None
        assert isinstance(user.id, UUID)
        assert user.email == "newuser@example.com"
        assert user.username == "newuser"
        assert user.full_name == "New User"
        assert user.is_active is True
        assert user.password_hash != "SecurePassword123!"  # Password is hashed
        assert user.created_at is not None
        assert verify_password("SecurePassword123!", user.password_hash) is True

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, db_session, test_user):
        """Test that duplicate email raises IntegrityError"""
        # Arrange
        register_data = RegisterRequest(
            email=test_user.email,  # Use existing user's email
            username="differentuser",
            password="SecurePassword123!",
            full_name="Different User"
        )

        # Act & Assert
        from sqlalchemy.exc import IntegrityError
        with pytest.raises(IntegrityError):
            await user_service.create_user(db_session, register_data)

    @pytest.mark.asyncio
    async def test_create_user_duplicate_username(self, db_session, test_user):
        """Test that duplicate username raises IntegrityError"""
        # Arrange
        register_data = RegisterRequest(
            email="different@example.com",
            username=test_user.username,  # Use existing user's username
            password="SecurePassword123!",
            full_name="Different User"
        )

        # Act & Assert
        from sqlalchemy.exc import IntegrityError
        with pytest.raises(IntegrityError):
            await user_service.create_user(db_session, register_data)

    @pytest.mark.asyncio
    async def test_create_user_password_is_hashed(self, db_session):
        """Test that password is hashed before storage"""
        # Arrange
        plain_password = "MySecurePassword123!"
        register_data = RegisterRequest(
            email="hashtest@example.com",
            username="hashtest",
            password=plain_password,
            full_name="Hash Test"
        )

        # Act
        user = await user_service.create_user(db_session, register_data)

        # Assert
        assert user.password_hash != plain_password
        assert user.password_hash.startswith("$2b$")  # bcrypt hash format
        assert len(user.password_hash) == 60  # bcrypt hash length
        assert verify_password(plain_password, user.password_hash) is True

    @pytest.mark.asyncio
    async def test_create_user_sets_active_by_default(self, db_session):
        """Test that new users are active by default"""
        # Arrange
        register_data = RegisterRequest(
            email="activetest@example.com",
            username="activetest",
            password="Password123!",
            full_name="Active Test"
        )

        # Act
        user = await user_service.create_user(db_session, register_data)

        # Assert
        assert user.is_active is True


# =============================================================================
# Test User Retrieval
# =============================================================================

class TestUserRetrieval:
    """Test user retrieval functions"""

    @pytest.mark.asyncio
    async def test_get_user_by_email_success(self, db_session, test_user):
        """Test successful user retrieval by email"""
        # Act
        user = await user_service.get_user_by_email(db_session, test_user.email)

        # Assert
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email
        assert user.username == test_user.username

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, db_session):
        """Test that non-existent email returns None"""
        # Act
        user = await user_service.get_user_by_email(db_session, "nonexistent@example.com")

        # Assert
        assert user is None

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, db_session, test_user):
        """Test successful user retrieval by ID"""
        # Act
        user = await user_service.get_user_by_id(db_session, test_user.id)

        # Assert
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, db_session):
        """Test that non-existent ID returns None"""
        # Act
        random_id = uuid4()
        user = await user_service.get_user_by_id(db_session, random_id)

        # Assert
        assert user is None


# =============================================================================
# Test Login Validation Logic
# =============================================================================

class TestLoginValidation:
    """Test login validation logic"""

    @pytest.mark.asyncio
    async def test_login_valid_credentials(self, db_session, test_user):
        """Test login with valid email and password"""
        # Arrange - test_user has password "password123"
        email = test_user.email
        password = "password123"

        # Act - Simulate login flow
        user = await user_service.get_user_by_email(db_session, email)
        is_valid = verify_password(password, user.password_hash)

        # Assert
        assert user is not None
        assert is_valid is True
        assert user.is_active is True

    @pytest.mark.asyncio
    async def test_login_invalid_email(self, db_session):
        """Test login with non-existent email"""
        # Act
        user = await user_service.get_user_by_email(db_session, "nonexistent@example.com")

        # Assert
        assert user is None

    @pytest.mark.asyncio
    async def test_login_invalid_password(self, db_session, test_user):
        """Test login with incorrect password"""
        # Arrange
        wrong_password = "wrongpassword"

        # Act
        user = await user_service.get_user_by_email(db_session, test_user.email)
        is_valid = verify_password(wrong_password, user.password_hash)

        # Assert
        assert user is not None
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_login_inactive_user_check(self, db_session, test_user):
        """Test that inactive users can be detected"""
        # Arrange - Make user inactive
        test_user.is_active = False
        await db_session.commit()
        await db_session.refresh(test_user)

        # Act
        user = await user_service.get_user_by_email(db_session, test_user.email)
        password_valid = verify_password("password123", user.password_hash)

        # Assert
        assert user is not None
        assert password_valid is True
        assert user.is_active is False  # Can detect inactive status


# =============================================================================
# Test Token Operations
# =============================================================================

class TestTokenOperations:
    """Test JWT token creation and validation"""

    def test_create_access_token(self, test_user):
        """Test access token creation"""
        # Act
        token = create_access_token(
            user_id=test_user.id,
            expires_delta=timedelta(minutes=15)
        )

        # Assert
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

        # Decode and verify payload
        payload = decode_token(token)
        assert payload["sub"] == str(test_user.id)
        assert payload["type"] == "access"

    def test_create_refresh_token(self, test_user):
        """Test refresh token creation"""
        # Act
        token = create_refresh_token(user_id=test_user.id)

        # Assert
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

        # Decode and verify payload
        payload = decode_token(token)
        assert payload["sub"] == str(test_user.id)
        assert payload["type"] == "refresh"

    def test_decode_valid_token(self, test_user):
        """Test decoding a valid token"""
        # Arrange
        token = create_access_token(
            user_id=test_user.id,
            expires_delta=timedelta(minutes=15)
        )

        # Act
        payload = decode_token(token)

        # Assert
        assert payload is not None
        assert "sub" in payload
        assert "exp" in payload
        assert "type" in payload
        assert payload["sub"] == str(test_user.id)

    def test_decode_invalid_token(self):
        """Test decoding an invalid token"""
        # Arrange
        invalid_token = "invalid.token.string"

        # Act & Assert
        from jose import JWTError
        with pytest.raises(JWTError):
            decode_token(invalid_token)

    def test_token_type_in_payload(self, test_user):
        """Test that token type is included in payload"""
        # Act
        access_token = create_access_token(
            user_id=test_user.id,
            expires_delta=timedelta(minutes=15)
        )
        refresh_token = create_refresh_token(user_id=test_user.id)

        # Decode tokens
        access_payload = decode_token(access_token)
        refresh_payload = decode_token(refresh_token)

        # Assert
        assert access_payload["type"] == "access"
        assert refresh_payload["type"] == "refresh"


# =============================================================================
# Test Password Operations
# =============================================================================

class TestPasswordOperations:
    """Test password hashing and verification"""

    def test_hash_password_returns_different_hash(self):
        """Test that hashing same password twice produces different hashes"""
        # Arrange
        password = "MyPassword123!"

        # Act
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Assert
        assert hash1 != hash2  # bcrypt uses random salt
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    def test_hash_password_format(self):
        """Test that password hash has correct bcrypt format"""
        # Arrange
        password = "TestPassword123!"

        # Act
        hashed = hash_password(password)

        # Assert
        assert hashed.startswith("$2b$")  # bcrypt format
        assert len(hashed) == 60  # bcrypt standard length

    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        # Arrange
        password = "CorrectPassword123!"
        hashed = hash_password(password)

        # Act
        is_valid = verify_password(password, hashed)

        # Assert
        assert is_valid is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        # Arrange
        correct_password = "CorrectPassword123!"
        wrong_password = "WrongPassword123!"
        hashed = hash_password(correct_password)

        # Act
        is_valid = verify_password(wrong_password, hashed)

        # Assert
        assert is_valid is False

    def test_verify_password_case_sensitive(self):
        """Test that password verification is case-sensitive"""
        # Arrange
        password = "CaseSensitive123!"
        hashed = hash_password(password)

        # Act
        lowercase_valid = verify_password("casesensitive123!", hashed)
        uppercase_valid = verify_password("CASESENSITIVE123!", hashed)
        correct_valid = verify_password("CaseSensitive123!", hashed)

        # Assert
        assert lowercase_valid is False
        assert uppercase_valid is False
        assert correct_valid is True


# =============================================================================
# Test User Update and Delete
# =============================================================================

class TestUserUpdateDelete:
    """Test user update and delete operations"""

    @pytest.mark.asyncio
    async def test_update_user_success(self, db_session, test_user):
        """Test successful user update"""
        # Arrange
        new_full_name = "Updated Name"
        update_data = {"full_name": new_full_name}

        # Act
        updated_user = await user_service.update_user(
            db_session,
            test_user.id,
            update_data
        )

        # Assert
        assert updated_user.id == test_user.id
        assert updated_user.full_name == new_full_name
        assert updated_user.email == test_user.email  # Unchanged

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, db_session):
        """Test update with non-existent user ID"""
        # Arrange
        random_id = uuid4()

        # Act & Assert
        with pytest.raises(ValueError, match="not found"):
            await user_service.update_user(db_session, random_id, {"full_name": "Test"})

    @pytest.mark.asyncio
    async def test_update_user_multiple_fields(self, db_session, test_user):
        """Test updating multiple fields"""
        # Arrange
        update_data = {
            "full_name": "New Full Name",
            "is_active": False
        }

        # Act
        updated_user = await user_service.update_user(
            db_session,
            test_user.id,
            update_data
        )

        # Assert
        assert updated_user.full_name == "New Full Name"
        assert updated_user.is_active is False

    @pytest.mark.asyncio
    async def test_delete_user_success(self, db_session, test_user):
        """Test successful user deletion"""
        # Arrange
        user_id = test_user.id

        # Act
        result = await user_service.delete_user(db_session, user_id)

        # Assert
        assert result is True

        # Verify user is deleted
        deleted_user = await user_service.get_user_by_id(db_session, user_id)
        assert deleted_user is None

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, db_session):
        """Test delete with non-existent user ID"""
        # Arrange
        random_id = uuid4()

        # Act
        result = await user_service.delete_user(db_session, random_id)

        # Assert
        assert result is False


# =============================================================================
# Test Schema Validation
# =============================================================================

class TestAuthSchemas:
    """Test authentication schema validation"""

    def test_register_request_valid_data(self):
        """Test RegisterRequest with valid data"""
        # Act
        data = RegisterRequest(
            email="valid@example.com",
            username="validuser",
            password="ValidPass123!",
            full_name="Valid User"
        )

        # Assert
        assert data.email == "valid@example.com"
        assert data.username == "validuser"
        assert data.password == "ValidPass123!"
        assert data.full_name == "Valid User"

    def test_register_request_invalid_email(self):
        """Test RegisterRequest with invalid email"""
        # Act & Assert
        from pydantic import ValidationError
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(
                email="not-an-email",
                username="user123",
                password="Password123!",
                full_name="Test User"
            )

        assert "email" in str(exc_info.value).lower()

    def test_register_request_short_username(self):
        """Test RegisterRequest with username too short"""
        # Act & Assert
        from pydantic import ValidationError
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(
                email="test@example.com",
                username="ab",  # Less than 3 characters
                password="Password123!",
                full_name="Test User"
            )

        assert "username" in str(exc_info.value).lower()

    def test_register_request_short_password(self):
        """Test RegisterRequest with password too short"""
        # Act & Assert
        from pydantic import ValidationError
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(
                email="test@example.com",
                username="testuser",
                password="short",  # Less than 8 characters
                full_name="Test User"
            )

        assert "password" in str(exc_info.value).lower()

    def test_register_request_invalid_username_chars(self):
        """Test RegisterRequest with invalid username characters"""
        # Act & Assert
        from pydantic import ValidationError
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(
                email="test@example.com",
                username="invalid@user!",  # Contains special characters
                password="Password123!",
                full_name="Test User"
            )

        assert "username" in str(exc_info.value).lower()

    def test_login_request_valid_data(self):
        """Test LoginRequest with valid data"""
        # Act
        data = LoginRequest(
            email="user@example.com",
            password="password123"
        )

        # Assert
        assert data.email == "user@example.com"
        assert data.password == "password123"

    def test_login_request_missing_password(self):
        """Test LoginRequest with missing password"""
        # Act & Assert
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            LoginRequest(email="user@example.com")
