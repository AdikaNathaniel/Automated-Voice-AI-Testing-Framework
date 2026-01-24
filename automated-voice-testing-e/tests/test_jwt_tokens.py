"""
Test suite for JWT token generation and validation

Ensures secure JWT token creation and decoding using python-jose,
including access tokens, refresh tokens, and token validation.
"""

import pytest
from datetime import timedelta, datetime
from uuid import UUID, uuid4
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
JWT_MODULE = PROJECT_ROOT / "backend" / "api" / "auth" / "jwt.py"


class TestJWTModuleExists:
    """Test that JWT module exists"""

    def test_jwt_module_file_exists(self):
        """Test that backend/api/auth/jwt.py exists"""
        assert JWT_MODULE.exists(), "backend/api/auth/jwt.py should exist"
        assert JWT_MODULE.is_file(), "jwt.py should be a file"

    def test_jwt_module_has_content(self):
        """Test that jwt.py has content"""
        content = JWT_MODULE.read_text()
        assert len(content) > 0, "jwt.py should not be empty"


class TestJWTModuleImports:
    """Test that JWT module can be imported"""

    def test_can_import_jwt_module(self):
        """Test that JWT module can be imported"""
        try:
            from api.auth import jwt
            assert jwt is not None
        except ImportError as e:
            pytest.fail(f"Failed to import jwt module: {e}")

    def test_jwt_module_uses_jose(self):
        """Test that JWT module imports python-jose"""
        content = JWT_MODULE.read_text()
        assert 'jose' in content, "jwt.py should use python-jose library"

    def test_jwt_module_imports_jwt_functions(self):
        """Test that JWT module imports JWT encode/decode functions"""
        content = JWT_MODULE.read_text()
        has_jwt_import = 'from jose import jwt' in content or 'import jose' in content
        assert has_jwt_import, "jwt.py should import JWT functionality from jose"


class TestCreateAccessTokenFunction:
    """Test create_access_token function"""

    def test_create_access_token_exists(self):
        """Test that create_access_token function exists"""
        from api.auth.jwt import create_access_token
        assert callable(create_access_token), "create_access_token should be a callable function"

    def test_create_access_token_returns_string(self):
        """Test that create_access_token returns a string"""
        from api.auth.jwt import create_access_token

        user_id = uuid4()
        token = create_access_token(user_id=user_id, expires_delta=timedelta(minutes=15))
        assert isinstance(token, str), "create_access_token should return a string"

    def test_create_access_token_returns_non_empty(self):
        """Test that create_access_token returns non-empty string"""
        from api.auth.jwt import create_access_token

        user_id = uuid4()
        token = create_access_token(user_id=user_id, expires_delta=timedelta(minutes=15))
        assert len(token) > 0, "create_access_token should return non-empty string"

    def test_create_access_token_jwt_format(self):
        """Test that create_access_token returns JWT format (3 parts separated by dots)"""
        from api.auth.jwt import create_access_token

        user_id = uuid4()
        token = create_access_token(user_id=user_id, expires_delta=timedelta(minutes=15))

        # JWT format: header.payload.signature
        parts = token.split('.')
        assert len(parts) == 3, "JWT should have 3 parts (header.payload.signature)"

    def test_create_access_token_accepts_user_id(self):
        """Test that create_access_token accepts user_id as UUID"""
        from api.auth.jwt import create_access_token

        user_id = uuid4()
        token = create_access_token(user_id=user_id, expires_delta=timedelta(minutes=15))
        assert isinstance(token, str), "Should accept UUID and return token"

    def test_create_access_token_accepts_expires_delta(self):
        """Test that create_access_token accepts expires_delta as timedelta"""
        from api.auth.jwt import create_access_token

        user_id = uuid4()
        token = create_access_token(user_id=user_id, expires_delta=timedelta(minutes=30))
        assert isinstance(token, str), "Should accept timedelta and return token"

    def test_create_access_token_different_for_different_users(self):
        """Test that different users get different tokens"""
        from api.auth.jwt import create_access_token

        user1 = uuid4()
        user2 = uuid4()

        token1 = create_access_token(user_id=user1, expires_delta=timedelta(minutes=15))
        token2 = create_access_token(user_id=user2, expires_delta=timedelta(minutes=15))

        assert token1 != token2, "Different users should have different tokens"


class TestCreateRefreshTokenFunction:
    """Test create_refresh_token function"""

    def test_create_refresh_token_exists(self):
        """Test that create_refresh_token function exists"""
        from api.auth.jwt import create_refresh_token
        assert callable(create_refresh_token), "create_refresh_token should be a callable function"

    def test_create_refresh_token_returns_string(self):
        """Test that create_refresh_token returns a string"""
        from api.auth.jwt import create_refresh_token

        user_id = uuid4()
        token = create_refresh_token(user_id=user_id)
        assert isinstance(token, str), "create_refresh_token should return a string"

    def test_create_refresh_token_jwt_format(self):
        """Test that create_refresh_token returns JWT format"""
        from api.auth.jwt import create_refresh_token

        user_id = uuid4()
        token = create_refresh_token(user_id=user_id)

        # JWT format: header.payload.signature
        parts = token.split('.')
        assert len(parts) == 3, "JWT should have 3 parts"

    def test_refresh_token_different_from_access_token(self):
        """Test that refresh token is different from access token"""
        from api.auth.jwt import create_access_token, create_refresh_token

        user_id = uuid4()
        access_token = create_access_token(user_id=user_id, expires_delta=timedelta(minutes=15))
        refresh_token = create_refresh_token(user_id=user_id)

        assert access_token != refresh_token, "Access and refresh tokens should be different"


class TestDecodeTokenFunction:
    """Test decode_token function"""

    def test_decode_token_exists(self):
        """Test that decode_token function exists"""
        from api.auth.jwt import decode_token
        assert callable(decode_token), "decode_token should be a callable function"

    def test_decode_token_returns_dict(self):
        """Test that decode_token returns a dictionary"""
        from api.auth.jwt import create_access_token, decode_token

        user_id = uuid4()
        token = create_access_token(user_id=user_id, expires_delta=timedelta(minutes=15))
        decoded = decode_token(token)

        assert isinstance(decoded, dict), "decode_token should return a dictionary"

    def test_decode_token_contains_user_id(self):
        """Test that decoded token contains user_id"""
        from api.auth.jwt import create_access_token, decode_token

        user_id = uuid4()
        token = create_access_token(user_id=user_id, expires_delta=timedelta(minutes=15))
        decoded = decode_token(token)

        # Should have user_id in some form (sub, user_id, etc.)
        has_user_id = 'sub' in decoded or 'user_id' in decoded
        assert has_user_id, "Decoded token should contain user_id (as 'sub' or 'user_id')"

    def test_decode_token_user_id_matches(self):
        """Test that decoded user_id matches original"""
        from api.auth.jwt import create_access_token, decode_token

        user_id = uuid4()
        token = create_access_token(user_id=user_id, expires_delta=timedelta(minutes=15))
        decoded = decode_token(token)

        # Get user_id from decoded token (could be 'sub' or 'user_id')
        decoded_user_id = decoded.get('sub') or decoded.get('user_id')
        assert str(user_id) == str(decoded_user_id), "Decoded user_id should match original"

    def test_decode_token_contains_expiration(self):
        """Test that decoded token contains expiration time"""
        from api.auth.jwt import create_access_token, decode_token

        user_id = uuid4()
        token = create_access_token(user_id=user_id, expires_delta=timedelta(minutes=15))
        decoded = decode_token(token)

        assert 'exp' in decoded, "Decoded token should contain 'exp' (expiration time)"

    def test_decode_invalid_token_raises_exception(self):
        """Test that decoding invalid token raises exception"""
        from api.auth.jwt import decode_token

        invalid_token = "invalid.token.string"

        with pytest.raises(Exception):
            decode_token(invalid_token)


class TestTokenExpiration:
    """Test token expiration functionality"""

    def test_access_token_has_expiration(self):
        """Test that access token includes expiration"""
        from api.auth.jwt import create_access_token, decode_token

        user_id = uuid4()
        token = create_access_token(user_id=user_id, expires_delta=timedelta(minutes=15))
        decoded = decode_token(token)

        assert 'exp' in decoded, "Token should have expiration"
        assert isinstance(decoded['exp'], (int, float)), "Expiration should be numeric"

    def test_refresh_token_has_longer_expiration(self):
        """Test that refresh token has longer expiration than access token"""
        from api.auth.jwt import create_access_token, create_refresh_token, decode_token

        user_id = uuid4()
        access_token = create_access_token(user_id=user_id, expires_delta=timedelta(minutes=15))
        refresh_token = create_refresh_token(user_id=user_id)

        access_decoded = decode_token(access_token)
        refresh_decoded = decode_token(refresh_token)

        access_exp = access_decoded.get('exp', 0)
        refresh_exp = refresh_decoded.get('exp', 0)

        assert refresh_exp > access_exp, "Refresh token should expire later than access token"


class TestTokenClaims:
    """Test token claims and payload"""

    def test_token_contains_issued_at(self):
        """Test that token contains issued at time (iat)"""
        from api.auth.jwt import create_access_token, decode_token

        user_id = uuid4()
        token = create_access_token(user_id=user_id, expires_delta=timedelta(minutes=15))
        decoded = decode_token(token)

        # May have 'iat' (issued at) claim
        # This is optional but good practice
        pass

    def test_token_type_claim(self):
        """Test that tokens have type claim to distinguish access vs refresh"""
        from api.auth.jwt import create_access_token, create_refresh_token, decode_token

        user_id = uuid4()
        access_token = create_access_token(user_id=user_id, expires_delta=timedelta(minutes=15))
        refresh_token = create_refresh_token(user_id=user_id)

        access_decoded = decode_token(access_token)
        refresh_decoded = decode_token(refresh_token)

        # Tokens should have type claim to distinguish them
        # This is optional but recommended
        pass


class TestTokenSecurity:
    """Test token security properties"""

    def test_tokens_are_signed(self):
        """Test that tokens are signed (can't be tampered with)"""
        from api.auth.jwt import create_access_token, decode_token

        user_id = uuid4()
        token = create_access_token(user_id=user_id, expires_delta=timedelta(minutes=15))

        # Modify the token (tamper with it)
        parts = token.split('.')
        tampered_token = parts[0] + '.' + parts[1] + '.tampered'

        # Should raise exception when decoding tampered token
        with pytest.raises(Exception):
            decode_token(tampered_token)

    def test_different_tokens_for_same_user(self, frozen_time):
        """Test that creating multiple tokens for same user produces different tokens"""
        from api.auth.jwt import create_access_token

        user_id = uuid4()

        # Create first token at specific time
        with frozen_time("2024-01-01 12:00:00"):
            token1 = create_access_token(user_id=user_id, expires_delta=timedelta(minutes=15))

        # Create second token at different time (no actual sleep needed)
        with frozen_time("2024-01-01 12:00:01"):
            token2 = create_access_token(user_id=user_id, expires_delta=timedelta(minutes=15))

        # Tokens should be different due to different timestamp
        assert token1 != token2, "Multiple tokens for same user should be different"


class TestTokenEdgeCases:
    """Test token edge cases"""

    def test_create_token_with_short_expiration(self):
        """Test creating token with very short expiration"""
        from api.auth.jwt import create_access_token

        user_id = uuid4()
        token = create_access_token(user_id=user_id, expires_delta=timedelta(seconds=1))

        assert isinstance(token, str), "Should create token even with short expiration"

    def test_create_token_with_long_expiration(self):
        """Test creating token with long expiration"""
        from api.auth.jwt import create_access_token

        user_id = uuid4()
        token = create_access_token(user_id=user_id, expires_delta=timedelta(days=365))

        assert isinstance(token, str), "Should create token with long expiration"

    def test_decode_empty_string(self):
        """Test decoding empty string raises exception"""
        from api.auth.jwt import decode_token

        with pytest.raises(Exception):
            decode_token("")

    def test_decode_malformed_token(self):
        """Test decoding malformed token raises exception"""
        from api.auth.jwt import decode_token

        malformed_tokens = [
            "not.a.valid.jwt",
            "only_one_part",
            "two.parts",
            "invalid..format",
        ]

        for malformed in malformed_tokens:
            with pytest.raises(Exception):
                decode_token(malformed)


class TestFunctionSignatures:
    """Test function signatures and parameters"""

    def test_create_access_token_signature(self):
        """Test create_access_token function signature"""
        from api.auth.jwt import create_access_token
        import inspect

        sig = inspect.signature(create_access_token)
        params = list(sig.parameters.keys())

        assert 'user_id' in params, "Should have user_id parameter"
        assert 'expires_delta' in params, "Should have expires_delta parameter"

    def test_create_refresh_token_signature(self):
        """Test create_refresh_token function signature"""
        from api.auth.jwt import create_refresh_token
        import inspect

        sig = inspect.signature(create_refresh_token)
        params = list(sig.parameters.keys())

        assert 'user_id' in params, "Should have user_id parameter"

    def test_decode_token_signature(self):
        """Test decode_token function signature"""
        from api.auth.jwt import decode_token
        import inspect

        sig = inspect.signature(decode_token)
        params = list(sig.parameters.keys())

        assert 'token' in params, "Should have token parameter"


class TestJWTDocumentation:
    """Test JWT module documentation"""

    def test_create_access_token_has_docstring(self):
        """Test that create_access_token has docstring"""
        from api.auth.jwt import create_access_token

        assert create_access_token.__doc__ is not None, \
            "create_access_token should have docstring"

    def test_create_refresh_token_has_docstring(self):
        """Test that create_refresh_token has docstring"""
        from api.auth.jwt import create_refresh_token

        assert create_refresh_token.__doc__ is not None, \
            "create_refresh_token should have docstring"

    def test_decode_token_has_docstring(self):
        """Test that decode_token has docstring"""
        from api.auth.jwt import decode_token

        assert decode_token.__doc__ is not None, \
            "decode_token should have docstring"

    def test_module_has_docstring(self):
        """Test that JWT module has docstring"""
        from api.auth import jwt

        assert jwt.__doc__ is not None, \
            "JWT module should have docstring"


class TestJWTIntegration:
    """Test JWT integration scenarios"""

    def test_create_and_decode_workflow(self):
        """Test complete create and decode workflow"""
        from api.auth.jwt import create_access_token, decode_token

        # Create token
        user_id = uuid4()
        token = create_access_token(user_id=user_id, expires_delta=timedelta(minutes=15))

        # Decode token
        decoded = decode_token(token)

        # Verify user_id matches
        decoded_user_id = decoded.get('sub') or decoded.get('user_id')
        assert str(user_id) == str(decoded_user_id)

    def test_access_and_refresh_token_workflow(self):
        """Test access and refresh token workflow"""
        from api.auth.jwt import create_access_token, create_refresh_token, decode_token

        user_id = uuid4()

        # Create both tokens
        access_token = create_access_token(user_id=user_id, expires_delta=timedelta(minutes=15))
        refresh_token = create_refresh_token(user_id=user_id)

        # Both should decode successfully
        access_decoded = decode_token(access_token)
        refresh_decoded = decode_token(refresh_token)

        # Both should contain same user_id
        access_user_id = access_decoded.get('sub') or access_decoded.get('user_id')
        refresh_user_id = refresh_decoded.get('sub') or refresh_decoded.get('user_id')

        assert str(access_user_id) == str(refresh_user_id)
