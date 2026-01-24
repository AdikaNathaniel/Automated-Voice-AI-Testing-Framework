"""
Test suite for webhook signature verification security.

Validates HMAC signature verification for CI/CD webhook providers.
"""

import hashlib
import hmac
import pytest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.webhook_service import (
    verify_signature,
    SignatureVerificationError,
)


class TestGitHubSignatureVerification:
    """Test GitHub webhook HMAC-SHA256 signature verification."""

    @pytest.fixture
    def secret(self):
        return "test-github-secret"

    @pytest.fixture
    def body(self):
        return b'{"action": "push"}'

    @pytest.fixture
    def valid_signature(self, secret, body):
        sig = hmac.new(
            secret.encode("utf-8"),
            body,
            hashlib.sha256,
        ).hexdigest()
        return f"sha256={sig}"

    @patch("services.webhook_service.get_settings")
    def test_valid_github_signature(self, mock_settings, secret, body, valid_signature):
        """Should accept valid GitHub HMAC signature."""
        mock_settings.return_value = MagicMock(GITHUB_WEBHOOK_SECRET=secret)
        headers = {
            "x-github-event": "push",
            "x-hub-signature-256": valid_signature,
        }

        # Should not raise
        verify_signature("github", headers, body)

    @patch("services.webhook_service.get_settings")
    def test_invalid_github_signature(self, mock_settings, secret, body):
        """Should reject invalid GitHub signature."""
        mock_settings.return_value = MagicMock(
            GITHUB_WEBHOOK_SECRET=secret,
            GITHUB_WEBHOOK_SECRET_PREVIOUS=None,
        )
        headers = {
            "x-github-event": "push",
            "x-hub-signature-256": "sha256=invalid",
        }

        with pytest.raises(SignatureVerificationError) as exc_info:
            verify_signature("github", headers, body)
        assert "Invalid GitHub webhook signature" in str(exc_info.value)

    @patch("services.webhook_service.get_settings")
    def test_missing_github_signature_header(self, mock_settings, secret, body):
        """Should reject missing GitHub signature header."""
        mock_settings.return_value = MagicMock(GITHUB_WEBHOOK_SECRET=secret)
        headers = {"x-github-event": "push"}

        with pytest.raises(SignatureVerificationError) as exc_info:
            verify_signature("github", headers, body)
        assert "Missing GitHub signature header" in str(exc_info.value)

    @patch("services.webhook_service.get_settings")
    def test_missing_github_secret_config(self, mock_settings, body):
        """Should reject when GitHub secret not configured."""
        mock_settings.return_value = MagicMock(GITHUB_WEBHOOK_SECRET=None)
        headers = {
            "x-github-event": "push",
            "x-hub-signature-256": "sha256=somesig",
        }

        with pytest.raises(SignatureVerificationError) as exc_info:
            verify_signature("github", headers, body)
        assert "not configured" in str(exc_info.value)

    @patch("services.webhook_service.get_settings")
    def test_invalid_github_signature_format(self, mock_settings, secret, body):
        """Should reject GitHub signature without sha256= prefix."""
        mock_settings.return_value = MagicMock(GITHUB_WEBHOOK_SECRET=secret)
        headers = {
            "x-github-event": "push",
            "x-hub-signature-256": "invalid-format",
        }

        with pytest.raises(SignatureVerificationError) as exc_info:
            verify_signature("github", headers, body)
        assert "Invalid GitHub signature format" in str(exc_info.value)


class TestGitLabSignatureVerification:
    """Test GitLab webhook token verification."""

    @pytest.fixture
    def secret(self):
        return "test-gitlab-token"

    @pytest.fixture
    def body(self):
        return b'{"object_kind": "push"}'

    @patch("services.webhook_service.get_settings")
    def test_valid_gitlab_token(self, mock_settings, secret, body):
        """Should accept valid GitLab token."""
        mock_settings.return_value = MagicMock(GITLAB_WEBHOOK_SECRET=secret)
        headers = {
            "x-gitlab-event": "Push Hook",
            "x-gitlab-token": secret,
        }

        # Should not raise
        verify_signature("gitlab", headers, body)

    @patch("services.webhook_service.get_settings")
    def test_invalid_gitlab_token(self, mock_settings, secret, body):
        """Should reject invalid GitLab token."""
        mock_settings.return_value = MagicMock(
            GITLAB_WEBHOOK_SECRET=secret,
            GITLAB_WEBHOOK_SECRET_PREVIOUS=None,
        )
        headers = {
            "x-gitlab-event": "Push Hook",
            "x-gitlab-token": "wrong-token",
        }

        with pytest.raises(SignatureVerificationError) as exc_info:
            verify_signature("gitlab", headers, body)
        assert "Invalid GitLab webhook token" in str(exc_info.value)

    @patch("services.webhook_service.get_settings")
    def test_missing_gitlab_token_header(self, mock_settings, secret, body):
        """Should reject missing GitLab token header."""
        mock_settings.return_value = MagicMock(GITLAB_WEBHOOK_SECRET=secret)
        headers = {"x-gitlab-event": "Push Hook"}

        with pytest.raises(SignatureVerificationError) as exc_info:
            verify_signature("gitlab", headers, body)
        assert "Missing GitLab token header" in str(exc_info.value)

    @patch("services.webhook_service.get_settings")
    def test_missing_gitlab_secret_config(self, mock_settings, body):
        """Should reject when GitLab secret not configured."""
        mock_settings.return_value = MagicMock(GITLAB_WEBHOOK_SECRET=None)
        headers = {
            "x-gitlab-event": "Push Hook",
            "x-gitlab-token": "some-token",
        }

        with pytest.raises(SignatureVerificationError) as exc_info:
            verify_signature("gitlab", headers, body)
        assert "not configured" in str(exc_info.value)


class TestJenkinsSignatureVerification:
    """Test Jenkins webhook HMAC-SHA256 signature verification."""

    @pytest.fixture
    def secret(self):
        return "test-jenkins-secret"

    @pytest.fixture
    def body(self):
        return b'{"build": {"number": 1}}'

    @pytest.fixture
    def valid_signature(self, secret, body):
        return hmac.new(
            secret.encode("utf-8"),
            body,
            hashlib.sha256,
        ).hexdigest()

    @patch("services.webhook_service.get_settings")
    def test_valid_jenkins_signature(self, mock_settings, secret, body, valid_signature):
        """Should accept valid Jenkins HMAC signature."""
        mock_settings.return_value = MagicMock(JENKINS_WEBHOOK_SECRET=secret)
        headers = {
            "x-jenkins-event": "build",
            "x-jenkins-signature": valid_signature,
        }

        # Should not raise
        verify_signature("jenkins", headers, body)

    @patch("services.webhook_service.get_settings")
    def test_invalid_jenkins_signature(self, mock_settings, secret, body):
        """Should reject invalid Jenkins signature."""
        mock_settings.return_value = MagicMock(
            JENKINS_WEBHOOK_SECRET=secret,
            JENKINS_WEBHOOK_SECRET_PREVIOUS=None,
        )
        headers = {
            "x-jenkins-event": "build",
            "x-jenkins-signature": "invalid",
        }

        with pytest.raises(SignatureVerificationError) as exc_info:
            verify_signature("jenkins", headers, body)
        assert "Invalid Jenkins webhook signature" in str(exc_info.value)

    @patch("services.webhook_service.get_settings")
    def test_missing_jenkins_signature_header(self, mock_settings, secret, body):
        """Should reject missing Jenkins signature header."""
        mock_settings.return_value = MagicMock(JENKINS_WEBHOOK_SECRET=secret)
        headers = {"x-jenkins-event": "build"}

        with pytest.raises(SignatureVerificationError) as exc_info:
            verify_signature("jenkins", headers, body)
        assert "Missing Jenkins signature header" in str(exc_info.value)

    @patch("services.webhook_service.get_settings")
    def test_missing_jenkins_secret_config(self, mock_settings, body):
        """Should reject when Jenkins secret not configured."""
        mock_settings.return_value = MagicMock(JENKINS_WEBHOOK_SECRET=None)
        headers = {
            "x-jenkins-event": "build",
            "x-jenkins-signature": "somesig",
        }

        with pytest.raises(SignatureVerificationError) as exc_info:
            verify_signature("jenkins", headers, body)
        assert "not configured" in str(exc_info.value)


class TestUnsupportedProvider:
    """Test unsupported provider handling."""

    @patch("services.webhook_service.get_settings")
    def test_unsupported_provider(self, mock_settings):
        """Should reject unsupported providers."""
        mock_settings.return_value = MagicMock()
        headers = {}
        body = b'{}'

        with pytest.raises(SignatureVerificationError) as exc_info:
            verify_signature("unknown", headers, body)
        assert "unsupported" in str(exc_info.value).lower()


class TestProviderConfigOverride:
    """Test that provider config can override global settings."""

    @pytest.fixture
    def body(self):
        return b'{"action": "push"}'

    @patch("services.webhook_service.get_settings")
    def test_provider_config_overrides_global(self, mock_settings, body):
        """Provider config secret should override global settings."""
        global_secret = "global-secret"
        provider_secret = "provider-secret"

        mock_settings.return_value = MagicMock(GITHUB_WEBHOOK_SECRET=global_secret)

        # Create signature with provider secret
        sig = hmac.new(
            provider_secret.encode("utf-8"),
            body,
            hashlib.sha256,
        ).hexdigest()

        headers = {
            "x-github-event": "push",
            "x-hub-signature-256": f"sha256={sig}",
        }

        integration_config = {
            "providers": {
                "github": {"secret": provider_secret}
            }
        }

        # Should accept because we use provider config secret
        verify_signature("github", headers, body, integration_config)


class TestCaseInsensitiveHeaders:
    """Test that header lookup is case-insensitive."""

    @pytest.fixture
    def secret(self):
        return "test-secret"

    @pytest.fixture
    def body(self):
        return b'{}'

    @patch("services.webhook_service.get_settings")
    def test_uppercase_headers_accepted(self, mock_settings, secret, body):
        """Should accept headers regardless of case."""
        mock_settings.return_value = MagicMock(GITLAB_WEBHOOK_SECRET=secret)
        headers = {
            "X-GITLAB-EVENT": "Push Hook",
            "X-GITLAB-TOKEN": secret,
        }

        # Should not raise
        verify_signature("gitlab", headers, body)

    @patch("services.webhook_service.get_settings")
    def test_mixed_case_headers_accepted(self, mock_settings, secret, body):
        """Should accept mixed-case headers."""
        mock_settings.return_value = MagicMock(GITLAB_WEBHOOK_SECRET=secret)
        headers = {
            "X-Gitlab-Event": "Push Hook",
            "X-Gitlab-Token": secret,
        }

        # Should not raise
        verify_signature("gitlab", headers, body)
