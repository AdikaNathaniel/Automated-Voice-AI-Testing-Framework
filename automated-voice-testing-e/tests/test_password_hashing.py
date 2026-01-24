"""
Test suite for password hashing utilities

Ensures secure password hashing using passlib with bcrypt algorithm,
including hash_password() and verify_password() functions.
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
PASSWORD_MODULE = PROJECT_ROOT / "backend" / "api" / "auth" / "password.py"


class TestPasswordModuleExists:
    """Test that password module exists"""

    def test_password_module_file_exists(self):
        """Test that backend/api/auth/password.py exists"""
        assert PASSWORD_MODULE.exists(), "backend/api/auth/password.py should exist"
        assert PASSWORD_MODULE.is_file(), "password.py should be a file"

    def test_password_module_has_content(self):
        """Test that password.py has content"""
        content = PASSWORD_MODULE.read_text()
        assert len(content) > 0, "password.py should not be empty"


class TestPasswordModuleImports:
    """Test that password module can be imported"""

    def test_can_import_password_module(self):
        """Test that password module can be imported"""
        try:
            from api.auth import password
            assert password is not None
        except ImportError as e:
            pytest.fail(f"Failed to import password module: {e}")

    def test_password_module_uses_passlib(self):
        """Test that password module imports passlib"""
        content = PASSWORD_MODULE.read_text()
        assert 'passlib' in content, "password.py should use passlib"

    def test_password_module_uses_bcrypt(self):
        """Test that password module uses bcrypt"""
        content = PASSWORD_MODULE.read_text()
        assert 'bcrypt' in content.lower(), "password.py should use bcrypt algorithm"


class TestHashPasswordFunction:
    """Test hash_password function"""

    def test_hash_password_function_exists(self):
        """Test that hash_password function exists"""
        from api.auth.password import hash_password
        assert callable(hash_password), "hash_password should be a callable function"

    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string"""
        from api.auth.password import hash_password

        hashed = hash_password("testpassword123")
        assert isinstance(hashed, str), "hash_password should return a string"

    def test_hash_password_returns_non_empty_string(self):
        """Test that hash_password returns non-empty string"""
        from api.auth.password import hash_password

        hashed = hash_password("testpassword123")
        assert len(hashed) > 0, "hash_password should return non-empty string"

    def test_hash_password_different_for_same_input(self):
        """Test that hash_password generates different hashes (due to salt)"""
        from api.auth.password import hash_password

        password = "testpassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Due to salt, hashes should be different
        assert hash1 != hash2, "hash_password should generate different hashes due to salt"

    def test_hash_password_format(self):
        """Test that hash_password returns bcrypt format"""
        from api.auth.password import hash_password

        hashed = hash_password("testpassword123")
        # Bcrypt hashes start with $2b$ or similar
        assert hashed.startswith('$2') or hashed.startswith('$2b$') or hashed.startswith('$2a$'), \
            "hash_password should return bcrypt format (starting with $2b$ or $2a$)"

    def test_hash_password_length(self):
        """Test that hash_password returns hash of expected length"""
        from api.auth.password import hash_password

        hashed = hash_password("testpassword123")
        # Bcrypt hashes are 60 characters
        assert len(hashed) == 60, "bcrypt hash should be 60 characters long"


class TestVerifyPasswordFunction:
    """Test verify_password function"""

    def test_verify_password_function_exists(self):
        """Test that verify_password function exists"""
        from api.auth.password import verify_password
        assert callable(verify_password), "verify_password should be a callable function"

    def test_verify_password_returns_boolean(self):
        """Test that verify_password returns boolean"""
        from api.auth.password import hash_password, verify_password

        hashed = hash_password("testpassword123")
        result = verify_password("testpassword123", hashed)
        assert isinstance(result, bool), "verify_password should return boolean"

    def test_verify_password_correct_password(self):
        """Test that verify_password returns True for correct password"""
        from api.auth.password import hash_password, verify_password

        password = "testpassword123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True, \
            "verify_password should return True for correct password"

    def test_verify_password_incorrect_password(self):
        """Test that verify_password returns False for incorrect password"""
        from api.auth.password import hash_password, verify_password

        password = "testpassword123"
        hashed = hash_password(password)

        assert verify_password("wrongpassword", hashed) is False, \
            "verify_password should return False for incorrect password"

    def test_verify_password_case_sensitive(self):
        """Test that verify_password is case sensitive"""
        from api.auth.password import hash_password, verify_password

        password = "TestPassword123"
        hashed = hash_password(password)

        assert verify_password("testpassword123", hashed) is False, \
            "verify_password should be case sensitive"
        assert verify_password("TestPassword123", hashed) is True, \
            "verify_password should accept correct case"


class TestPasswordEdgeCases:
    """Test password hashing edge cases"""

    def test_hash_empty_string(self):
        """Test that hash_password handles empty string"""
        from api.auth.password import hash_password

        # Empty password should be hashed (but may want to validate elsewhere)
        hashed = hash_password("")
        assert isinstance(hashed, str), "hash_password should handle empty string"
        assert len(hashed) > 0, "hash_password should return hash for empty string"

    def test_hash_long_password(self):
        """Test that hash_password handles very long passwords"""
        from api.auth.password import hash_password

        long_password = "a" * 1000
        hashed = hash_password(long_password)
        assert isinstance(hashed, str), "hash_password should handle long passwords"
        assert len(hashed) == 60, "bcrypt hash should be 60 characters regardless of input length"

    def test_hash_special_characters(self):
        """Test that hash_password handles special characters"""
        from api.auth.password import hash_password, verify_password

        password = "p@ssw0rd!#$%^&*()"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True, \
            "hash_password should handle special characters"

    def test_hash_unicode_characters(self):
        """Test that hash_password handles unicode characters"""
        from api.auth.password import hash_password, verify_password

        password = "пароль密码🔐"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True, \
            "hash_password should handle unicode characters"

    def test_hash_whitespace(self):
        """Test that hash_password preserves whitespace"""
        from api.auth.password import hash_password, verify_password

        password = "password with spaces"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True
        assert verify_password("passwordwithspaces", hashed) is False, \
            "hash_password should preserve whitespace"


class TestPasswordSecurity:
    """Test password security properties"""

    def test_hash_password_produces_different_salts(self):
        """Test that multiple hashes have different salts"""
        from api.auth.password import hash_password

        password = "samepassword"
        hashes = [hash_password(password) for _ in range(5)]

        # All hashes should be unique due to different salts
        assert len(set(hashes)) == 5, "Each hash should have a unique salt"

    def test_verify_password_rejects_plain_password(self):
        """Test that verify_password rejects unhashed password"""
        from api.auth.password import verify_password

        password = "testpassword123"

        # Using plain password as "hash" should return False
        assert verify_password(password, password) is False, \
            "verify_password should reject plain text password as hash"

    def test_hash_doesnt_contain_plain_password(self):
        """Test that hash doesn't contain plain password"""
        from api.auth.password import hash_password

        password = "verysecretpassword"
        hashed = hash_password(password)

        assert password not in hashed, \
            "Hash should not contain plain password"


class TestPasswordFunctionSignatures:
    """Test function signatures and parameters"""

    def test_hash_password_accepts_string(self):
        """Test that hash_password accepts string parameter"""
        from api.auth.password import hash_password
        import inspect

        sig = inspect.signature(hash_password)
        params = list(sig.parameters.keys())

        assert len(params) >= 1, "hash_password should accept at least one parameter"
        # First parameter should be for password
        assert 'password' in params[0].lower() or params[0] in ['plain', 'pwd', 'p'], \
            "First parameter should be for password"

    def test_verify_password_accepts_two_strings(self):
        """Test that verify_password accepts two string parameters"""
        from api.auth.password import verify_password
        import inspect

        sig = inspect.signature(verify_password)
        params = list(sig.parameters.keys())

        assert len(params) >= 2, "verify_password should accept at least two parameters"


class TestPasswordModuleDocumentation:
    """Test password module documentation"""

    def test_hash_password_has_docstring(self):
        """Test that hash_password has docstring"""
        from api.auth.password import hash_password

        assert hash_password.__doc__ is not None, \
            "hash_password should have docstring"

    def test_verify_password_has_docstring(self):
        """Test that verify_password has docstring"""
        from api.auth.password import verify_password

        assert verify_password.__doc__ is not None, \
            "verify_password should have docstring"

    def test_module_has_docstring(self):
        """Test that password module has docstring"""
        from api.auth import password

        assert password.__doc__ is not None, \
            "password module should have docstring"


class TestPasswordIntegration:
    """Test password hashing integration scenarios"""

    def test_hash_and_verify_workflow(self):
        """Test complete hash and verify workflow"""
        from api.auth.password import hash_password, verify_password

        # Simulate user registration
        user_password = "MySecurePassword123!"
        stored_hash = hash_password(user_password)

        # Simulate user login with correct password
        login_attempt_correct = "MySecurePassword123!"
        assert verify_password(login_attempt_correct, stored_hash) is True

        # Simulate user login with incorrect password
        login_attempt_wrong = "WrongPassword"
        assert verify_password(login_attempt_wrong, stored_hash) is False

    def test_multiple_users_same_password(self):
        """Test that same password hashes differently for different users"""
        from api.auth.password import hash_password

        password = "commonpassword123"

        # Two users with same password
        user1_hash = hash_password(password)
        user2_hash = hash_password(password)

        # Hashes should be different due to different salts
        assert user1_hash != user2_hash, \
            "Same password should hash differently for different users"
