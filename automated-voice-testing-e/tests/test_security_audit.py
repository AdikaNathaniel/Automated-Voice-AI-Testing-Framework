"""
Test Security Audit Script

This module tests that the security audit script performs comprehensive
security checks for common vulnerabilities.

Test Coverage:
    - Security audit script exists
    - SQL injection prevention checks
    - XSS prevention checks
    - CSRF protection checks
    - Authentication validation
    - Authorization validation
    - Security report generation
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import pytest


# =============================================================================
# Module Existence Tests
# =============================================================================

class TestSecurityAuditModule:
    """Test that security audit module exists"""

    def test_security_audit_script_exists(self):
        """Test that security audit script exists"""
        # Arrange
        project_root = Path(__file__).parent.parent
        script_file = project_root / "backend" / "scripts" / "run_security_audit.py"

        # Act & Assert
        assert script_file.exists(), "run_security_audit.py should exist in backend/scripts/"
        assert script_file.is_file(), "run_security_audit.py should be a file"


# =============================================================================
# SQL Injection Tests
# =============================================================================

class TestSQLInjectionChecks:
    """Test that SQL injection prevention is validated"""

    def test_has_sql_injection_check_function(self):
        """Test that SQL injection check function exists"""
        # Arrange
        from scripts import run_security_audit

        # Act & Assert
        assert hasattr(run_security_audit, 'check_sql_injection_prevention'), \
            "run_security_audit should have check_sql_injection_prevention function"

    def test_validates_parameterized_queries(self):
        """Test that audit validates use of parameterized queries"""
        # Arrange
        from scripts.run_security_audit import check_sql_injection_prevention

        # Act
        results = check_sql_injection_prevention()

        # Assert
        assert 'uses_parameterized_queries' in results, \
            "Should check for parameterized queries"
        assert results['uses_parameterized_queries'] is True, \
            "Should use parameterized queries (SQLAlchemy ORM)"

    def test_checks_no_string_concatenation_in_queries(self):
        """Test that audit checks for string concatenation in queries"""
        # Arrange
        from scripts.run_security_audit import check_sql_injection_prevention

        # Act
        results = check_sql_injection_prevention()

        # Assert
        assert 'no_string_concatenation' in results, \
            "Should check for string concatenation in queries"


# =============================================================================
# XSS Prevention Tests
# =============================================================================

class TestXSSPrevention:
    """Test that XSS prevention measures are validated"""

    def test_has_xss_check_function(self):
        """Test that XSS check function exists"""
        # Arrange
        from scripts import run_security_audit

        # Act & Assert
        assert hasattr(run_security_audit, 'check_xss_prevention'), \
            "run_security_audit should have check_xss_prevention function"

    def test_validates_input_validation(self):
        """Test that audit validates input validation"""
        # Arrange
        from scripts.run_security_audit import check_xss_prevention

        # Act
        results = check_xss_prevention()

        # Assert
        assert 'uses_pydantic_validation' in results, \
            "Should check for Pydantic input validation"
        assert results['uses_pydantic_validation'] is True, \
            "Should use Pydantic for input validation"

    def test_validates_output_encoding(self):
        """Test that audit validates output encoding"""
        # Arrange
        from scripts.run_security_audit import check_xss_prevention

        # Act
        results = check_xss_prevention()

        # Assert
        assert 'uses_json_encoding' in results, \
            "Should check for proper output encoding (JSON)"


# =============================================================================
# CSRF Protection Tests
# =============================================================================

class TestCSRFProtection:
    """Test that CSRF protection measures are validated"""

    def test_has_csrf_check_function(self):
        """Test that CSRF check function exists"""
        # Arrange
        from scripts import run_security_audit

        # Act & Assert
        assert hasattr(run_security_audit, 'check_csrf_protection'), \
            "run_security_audit should have check_csrf_protection function"

    def test_validates_cors_configuration(self):
        """Test that audit validates CORS configuration"""
        # Arrange
        from scripts.run_security_audit import check_csrf_protection

        # Act
        results = check_csrf_protection()

        # Assert
        assert 'cors_configured' in results, \
            "Should check for CORS configuration"

    def test_validates_jwt_for_state_changes(self):
        """Test that audit validates JWT tokens for state changes"""
        # Arrange
        from scripts.run_security_audit import check_csrf_protection

        # Act
        results = check_csrf_protection()

        # Assert
        assert 'uses_jwt_tokens' in results, \
            "Should check that JWT tokens are used for authentication"


# =============================================================================
# Authentication Tests
# =============================================================================

class TestAuthenticationValidation:
    """Test that authentication mechanisms are validated"""

    def test_has_authentication_check_function(self):
        """Test that authentication check function exists"""
        # Arrange
        from scripts import run_security_audit

        # Act & Assert
        assert hasattr(run_security_audit, 'check_authentication'), \
            "run_security_audit should have check_authentication function"

    def test_validates_password_hashing(self):
        """Test that audit validates password hashing"""
        # Arrange
        from scripts.run_security_audit import check_authentication

        # Act
        results = check_authentication()

        # Assert
        assert 'uses_bcrypt_hashing' in results, \
            "Should check for bcrypt password hashing"
        assert results['uses_bcrypt_hashing'] is True, \
            "Should use bcrypt for password hashing"

    def test_validates_jwt_tokens(self):
        """Test that audit validates JWT token usage"""
        # Arrange
        from scripts.run_security_audit import check_authentication

        # Act
        results = check_authentication()

        # Assert
        assert 'uses_jwt_tokens' in results, \
            "Should check for JWT token authentication"
        assert results['uses_jwt_tokens'] is True, \
            "Should use JWT tokens for authentication"

    def test_validates_token_expiration(self):
        """Test that audit validates token expiration"""
        # Arrange
        from scripts.run_security_audit import check_authentication

        # Act
        results = check_authentication()

        # Assert
        assert 'tokens_have_expiration' in results, \
            "Should check that tokens have expiration"


# =============================================================================
# Authorization Tests
# =============================================================================

class TestAuthorizationValidation:
    """Test that authorization mechanisms are validated"""

    def test_has_authorization_check_function(self):
        """Test that authorization check function exists"""
        # Arrange
        from scripts import run_security_audit

        # Act & Assert
        assert hasattr(run_security_audit, 'check_authorization'), \
            "run_security_audit should have check_authorization function"

    def test_validates_protected_routes(self):
        """Test that audit validates protected routes"""
        # Arrange
        from scripts.run_security_audit import check_authorization

        # Act
        results = check_authorization()

        # Assert
        assert 'has_protected_routes' in results, \
            "Should check for protected routes"
        assert results['has_protected_routes'] is True, \
            "Should have protected routes requiring authentication"

    def test_validates_user_ownership(self):
        """Test that audit validates user ownership checks"""
        # Arrange
        from scripts.run_security_audit import check_authorization

        # Act
        results = check_authorization()

        # Assert
        assert 'checks_user_ownership' in results, \
            "Should check for user ownership validation"


# =============================================================================
# Security Report Tests
# =============================================================================

class TestSecurityReport:
    """Test that security audit generates reports"""

    def test_has_run_security_audit_function(self):
        """Test that run_security_audit function exists"""
        # Arrange
        from scripts import run_security_audit

        # Act & Assert
        assert hasattr(run_security_audit, 'run_security_audit'), \
            "run_security_audit should have run_security_audit function"
        assert callable(run_security_audit.run_security_audit), \
            "run_security_audit should be callable"

    def test_has_generate_security_report_function(self):
        """Test that generate_security_report function exists"""
        # Arrange
        from scripts import run_security_audit

        # Act & Assert
        assert hasattr(run_security_audit, 'generate_security_report'), \
            "run_security_audit should have generate_security_report function"

    def test_report_includes_all_security_checks(self):
        """Test that report includes all security check results"""
        # Arrange
        from scripts.run_security_audit import run_security_audit

        # Act
        results = run_security_audit()

        # Assert
        assert 'sql_injection' in results, \
            "Report should include SQL injection check results"
        assert 'xss_prevention' in results, \
            "Report should include XSS prevention check results"
        assert 'csrf_protection' in results, \
            "Report should include CSRF protection check results"
        assert 'authentication' in results, \
            "Report should include authentication check results"
        assert 'authorization' in results, \
            "Report should include authorization check results"

    def test_report_includes_overall_status(self):
        """Test that report includes overall security status"""
        # Arrange
        from scripts.run_security_audit import run_security_audit

        # Act
        results = run_security_audit()

        # Assert
        assert 'overall_status' in results, \
            "Report should include overall security status"
        assert results['overall_status'] in ['PASS', 'FAIL', 'WARNING'], \
            "Overall status should be PASS, FAIL, or WARNING"


# =============================================================================
# Integration Tests
# =============================================================================

class TestSecurityAuditIntegration:
    """Test security audit integration"""

    def test_audit_checks_actual_codebase(self):
        """Test that audit checks actual codebase files"""
        # Arrange
        from scripts.run_security_audit import run_security_audit

        # Act
        results = run_security_audit()

        # Assert
        assert 'files_checked' in results, \
            "Should report number of files checked"
        assert results['files_checked'] > 0, \
            "Should check at least some files"

    def test_audit_runs_without_errors(self):
        """Test that audit runs without errors"""
        # Arrange
        from scripts.run_security_audit import run_security_audit

        # Act & Assert
        try:
            results = run_security_audit()
            assert results is not None, "Should return results"
        except Exception as e:
            pytest.fail(f"Security audit should run without errors: {e}")
