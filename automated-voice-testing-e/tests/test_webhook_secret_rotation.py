"""
Test suite for webhook secret rotation support.

Validates that webhook verification accepts both current and previous secrets
during rotation periods for zero-downtime secret updates.
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


class TestGitHubSecretRotation:
    """Test GitHub webhook secret rotation support."""

    @pytest.fixture
    def current_secret(self):
        return "new-github-secret"

    @pytest.fixture
    def previous_secret(self):
        return "old-github-secret"

    @pytest.fixture
    def body(self):
        return b'{"action": "push"}'

    @patch("services.webhook_service.get_settings")
    def test_accepts_current_secret(self, mock_settings, current_secret, previous_secret, body):
        """Should accept signature with current secret."""
        mock_settings.return_value = MagicMock(
            GITHUB_WEBHOOK_SECRET=current_secret,
            GITHUB_WEBHOOK_SECRET_PREVIOUS=previous_secret,
        )

        sig = hmac.new(
            current_secret.encode("utf-8"),
            body,
            hashlib.sha256,
        ).hexdigest()

        headers = {
            "x-github-event": "push",
            "x-hub-signature-256": f"sha256={sig}",
        }

        # Should not raise
        verify_signature("github", headers, body)

    @patch("services.webhook_service.get_settings")
    def test_accepts_previous_secret(self, mock_settings, current_secret, previous_secret, body):
        """Should accept signature with previous secret during rotation."""
        mock_settings.return_value = MagicMock(
            GITHUB_WEBHOOK_SECRET=current_secret,
            GITHUB_WEBHOOK_SECRET_PREVIOUS=previous_secret,
        )

        sig = hmac.new(
            previous_secret.encode("utf-8"),
            body,
            hashlib.sha256,
        ).hexdigest()

        headers = {
            "x-github-event": "push",
            "x-hub-signature-256": f"sha256={sig}",
        }

        # Should not raise - accepts previous secret
        verify_signature("github", headers, body)

    @patch("services.webhook_service.get_settings")
    def test_rejects_unknown_secret(self, mock_settings, current_secret, previous_secret, body):
        """Should reject signature with unknown secret."""
        mock_settings.return_value = MagicMock(
            GITHUB_WEBHOOK_SECRET=current_secret,
            GITHUB_WEBHOOK_SECRET_PREVIOUS=previous_secret,
        )

        sig = hmac.new(
            b"completely-wrong-secret",
            body,
            hashlib.sha256,
        ).hexdigest()

        headers = {
            "x-github-event": "push",
            "x-hub-signature-256": f"sha256={sig}",
        }

        with pytest.raises(SignatureVerificationError):
            verify_signature("github", headers, body)

    @patch("services.webhook_service.get_settings")
    def test_works_without_previous_secret(self, mock_settings, current_secret, body):
        """Should work when no previous secret is configured."""
        mock_settings.return_value = MagicMock(
            GITHUB_WEBHOOK_SECRET=current_secret,
            GITHUB_WEBHOOK_SECRET_PREVIOUS=None,
        )

        sig = hmac.new(
            current_secret.encode("utf-8"),
            body,
            hashlib.sha256,
        ).hexdigest()

        headers = {
            "x-github-event": "push",
            "x-hub-signature-256": f"sha256={sig}",
        }

        # Should not raise
        verify_signature("github", headers, body)


class TestGitLabSecretRotation:
    """Test GitLab webhook secret rotation support."""

    @pytest.fixture
    def current_secret(self):
        return "new-gitlab-token"

    @pytest.fixture
    def previous_secret(self):
        return "old-gitlab-token"

    @pytest.fixture
    def body(self):
        return b'{"object_kind": "push"}'

    @patch("services.webhook_service.get_settings")
    def test_accepts_current_token(self, mock_settings, current_secret, previous_secret, body):
        """Should accept current token."""
        mock_settings.return_value = MagicMock(
            GITLAB_WEBHOOK_SECRET=current_secret,
            GITLAB_WEBHOOK_SECRET_PREVIOUS=previous_secret,
        )

        headers = {
            "x-gitlab-event": "Push Hook",
            "x-gitlab-token": current_secret,
        }

        # Should not raise
        verify_signature("gitlab", headers, body)

    @patch("services.webhook_service.get_settings")
    def test_accepts_previous_token(self, mock_settings, current_secret, previous_secret, body):
        """Should accept previous token during rotation."""
        mock_settings.return_value = MagicMock(
            GITLAB_WEBHOOK_SECRET=current_secret,
            GITLAB_WEBHOOK_SECRET_PREVIOUS=previous_secret,
        )

        headers = {
            "x-gitlab-event": "Push Hook",
            "x-gitlab-token": previous_secret,
        }

        # Should not raise
        verify_signature("gitlab", headers, body)

    @patch("services.webhook_service.get_settings")
    def test_rejects_unknown_token(self, mock_settings, current_secret, previous_secret, body):
        """Should reject unknown token."""
        mock_settings.return_value = MagicMock(
            GITLAB_WEBHOOK_SECRET=current_secret,
            GITLAB_WEBHOOK_SECRET_PREVIOUS=previous_secret,
        )

        headers = {
            "x-gitlab-event": "Push Hook",
            "x-gitlab-token": "wrong-token",
        }

        with pytest.raises(SignatureVerificationError):
            verify_signature("gitlab", headers, body)


class TestJenkinsSecretRotation:
    """Test Jenkins webhook secret rotation support."""

    @pytest.fixture
    def current_secret(self):
        return "new-jenkins-secret"

    @pytest.fixture
    def previous_secret(self):
        return "old-jenkins-secret"

    @pytest.fixture
    def body(self):
        return b'{"build": {"number": 1}}'

    @patch("services.webhook_service.get_settings")
    def test_accepts_current_secret(self, mock_settings, current_secret, previous_secret, body):
        """Should accept signature with current secret."""
        mock_settings.return_value = MagicMock(
            JENKINS_WEBHOOK_SECRET=current_secret,
            JENKINS_WEBHOOK_SECRET_PREVIOUS=previous_secret,
        )

        sig = hmac.new(
            current_secret.encode("utf-8"),
            body,
            hashlib.sha256,
        ).hexdigest()

        headers = {
            "x-jenkins-event": "build",
            "x-jenkins-signature": sig,
        }

        # Should not raise
        verify_signature("jenkins", headers, body)

    @patch("services.webhook_service.get_settings")
    def test_accepts_previous_secret(self, mock_settings, current_secret, previous_secret, body):
        """Should accept signature with previous secret during rotation."""
        mock_settings.return_value = MagicMock(
            JENKINS_WEBHOOK_SECRET=current_secret,
            JENKINS_WEBHOOK_SECRET_PREVIOUS=previous_secret,
        )

        sig = hmac.new(
            previous_secret.encode("utf-8"),
            body,
            hashlib.sha256,
        ).hexdigest()

        headers = {
            "x-jenkins-event": "build",
            "x-jenkins-signature": sig,
        }

        # Should not raise
        verify_signature("jenkins", headers, body)

    @patch("services.webhook_service.get_settings")
    def test_rejects_unknown_secret(self, mock_settings, current_secret, previous_secret, body):
        """Should reject signature with unknown secret."""
        mock_settings.return_value = MagicMock(
            JENKINS_WEBHOOK_SECRET=current_secret,
            JENKINS_WEBHOOK_SECRET_PREVIOUS=previous_secret,
        )

        sig = hmac.new(
            b"wrong-secret",
            body,
            hashlib.sha256,
        ).hexdigest()

        headers = {
            "x-jenkins-event": "build",
            "x-jenkins-signature": sig,
        }

        with pytest.raises(SignatureVerificationError):
            verify_signature("jenkins", headers, body)


class TestProviderConfigRotation:
    """Test secret rotation via provider config."""

    @pytest.fixture
    def body(self):
        return b'{"action": "push"}'

    @patch("services.webhook_service.get_settings")
    def test_provider_config_previous_secret(self, mock_settings, body):
        """Provider config should support previous_secret field."""
        current = "provider-current"
        previous = "provider-previous"

        mock_settings.return_value = MagicMock(
            GITHUB_WEBHOOK_SECRET="global-secret",
            GITHUB_WEBHOOK_SECRET_PREVIOUS=None,
        )

        # Sign with previous secret
        sig = hmac.new(
            previous.encode("utf-8"),
            body,
            hashlib.sha256,
        ).hexdigest()

        headers = {
            "x-github-event": "push",
            "x-hub-signature-256": f"sha256={sig}",
        }

        integration_config = {
            "providers": {
                "github": {
                    "secret": current,
                    "previous_secret": previous,
                }
            }
        }

        # Should accept previous secret from provider config
        verify_signature("github", headers, body, integration_config)
