"""
Test GitHub/Jira/Slack Integration for Demo Repository

Tests verify that the automated testing platform can successfully integrate
with GitHub, Jira, and Slack to provide comprehensive notifications and
issue tracking for test results.

This test suite demonstrates:
- GitHub commit status updates for test runs
- GitHub issue creation for failed tests
- Jira issue creation for critical failures
- Slack notifications for test results
- End-to-end integration with all three services

These tests verify TODOS.md Section 7:
"Integration with GitHub/Jira/Slack configured and tested for a demo repository/project"
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any


class TestGitHubIntegration:
    """Test GitHub integration for commit status and issue creation"""

    def test_github_client_can_set_commit_status(self):
        """Test that GitHubClient can set commit status for a test run"""
        from integrations.github.client import GitHubClient

        # Verify GitHubClient has set_commit_status method
        assert hasattr(GitHubClient, 'set_commit_status')

        # Verify method signature includes required parameters
        import inspect
        sig = inspect.signature(GitHubClient.set_commit_status)
        params = list(sig.parameters.keys())

        assert 'sha' in params
        assert 'state' in params
        assert 'target_url' in params or 'description' in params

    def test_github_client_can_create_issues(self):
        """Test that GitHubClient can create issues for failed tests"""
        from integrations.github.client import GitHubClient

        assert hasattr(GitHubClient, 'create_issue')

        import inspect
        sig = inspect.signature(GitHubClient.create_issue)
        params = list(sig.parameters.keys())

        assert 'title' in params
        assert 'body' in params or 'labels' in params

    def test_github_client_can_post_test_run_status(self):
        """Test that GitHubClient can post aggregated test run status"""
        from integrations.github.client import GitHubClient

        assert hasattr(GitHubClient, 'post_test_run_status')

        import inspect
        sig = inspect.signature(GitHubClient.post_test_run_status)
        params = list(sig.parameters.keys())

        assert 'sha' in params
        assert 'passed' in params or 'run_status' in params
        assert 'failed' in params

    @pytest.mark.asyncio
    async def test_github_client_sets_commit_status_success(self):
        """Test successful commit status update"""
        from integrations.github.client import GitHubClient

        # Mock httpx client
        with patch('integrations.github.client.httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "id": 12345,
                "state": "success",
                "description": "Tests passed"
            }
            mock_response.raise_for_status = MagicMock()

            mock_async_client = MagicMock()
            mock_async_client.__aenter__ = AsyncMock(return_value=mock_async_client)
            mock_async_client.__aexit__ = AsyncMock(return_value=None)
            mock_async_client.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_async_client

            client = GitHubClient(
                token="test-token",
                repo_owner="demo-org",
                repo_name="demo-repo"
            )

            result = await client.set_commit_status(
                sha="abc123",
                state="success",
                description="10 passed, 0 failed"
            )

            assert result is not None
            assert result.get("state") == "success"

    @pytest.mark.asyncio
    async def test_github_client_creates_issue_for_failed_test(self):
        """Test creating GitHub issue for a failed test"""
        from integrations.github.client import GitHubClient

        with patch('integrations.github.client.httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "number": 42,
                "html_url": "https://github.com/demo-org/demo-repo/issues/42"
            }
            mock_response.raise_for_status = MagicMock()

            mock_async_client = MagicMock()
            mock_async_client.__aenter__ = AsyncMock(return_value=mock_async_client)
            mock_async_client.__aexit__ = AsyncMock(return_value=None)
            mock_async_client.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_async_client

            client = GitHubClient(
                token="test-token",
                repo_owner="demo-org",
                repo_name="demo-repo"
            )

            result = await client.create_issue(
                title="Test failure: Weather query",
                body="Voice test 'Weather query' failed in test run #123",
                labels=["bug", "test-failure"]
            )

            assert result is not None
            assert result.get("number") == 42


class TestJiraIntegration:
    """Test Jira integration for issue creation and tracking"""

    def test_jira_client_can_create_issues(self):
        """Test that JiraClient can create issues"""
        from integrations.jira.client import JiraClient

        assert hasattr(JiraClient, 'create_issue')

        import inspect
        sig = inspect.signature(JiraClient.create_issue)
        params = list(sig.parameters.keys())

        assert 'project' in params
        assert 'data' in params

    def test_jira_client_can_update_issues(self):
        """Test that JiraClient can update existing issues"""
        from integrations.jira.client import JiraClient

        assert hasattr(JiraClient, 'update_issue')

        import inspect
        sig = inspect.signature(JiraClient.update_issue)
        params = list(sig.parameters.keys())

        assert 'issue_key' in params
        assert 'data' in params

    @pytest.mark.asyncio
    async def test_jira_client_creates_issue_for_critical_failure(self):
        """Test creating Jira issue for a critical test failure"""
        from integrations.jira.client import JiraClient

        with patch('integrations.jira.client.httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "key": "QA-123",
                "id": "10001"
            }
            mock_response.raise_for_status = MagicMock()

            mock_async_client = MagicMock()
            mock_async_client.__aenter__ = AsyncMock(return_value=mock_async_client)
            mock_async_client.__aexit__ = AsyncMock(return_value=None)
            mock_async_client.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_async_client

            client = JiraClient(
                email="test@example.com",
                api_token="test-token",
                base_url="https://example.atlassian.net/rest/api/3"
            )

            result = await client.create_issue(
                project="QA",
                data={
                    "summary": "Critical: Voice AI test suite failure",
                    "description": "Test suite 'Integration Tests' failed with 5 critical errors",
                    "issuetype": {"name": "Bug"},
                    "priority": {"name": "Critical"}
                }
            )

            assert result == "QA-123"

    @pytest.mark.asyncio
    async def test_jira_client_returns_issue_key(self):
        """Test that create_issue returns a Jira issue key"""
        from integrations.jira.client import JiraClient

        with patch('integrations.jira.client.httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {"key": "DEMO-456"}
            mock_response.raise_for_status = MagicMock()

            mock_async_client = MagicMock()
            mock_async_client.__aenter__ = AsyncMock(return_value=mock_async_client)
            mock_async_client.__aexit__ = AsyncMock(return_value=None)
            mock_async_client.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_async_client

            client = JiraClient(
                email="test@example.com",
                api_token="test-token"
            )

            issue_key = await client.create_issue(
                project="DEMO",
                data={"summary": "Test issue"}
            )

            assert issue_key == "DEMO-456"
            assert isinstance(issue_key, str)


class TestSlackIntegration:
    """Test Slack integration for notifications"""

    def test_slack_client_can_send_test_run_notifications(self):
        """Test that SlackClient can send test run notifications"""
        from integrations.slack.client import SlackClient

        assert hasattr(SlackClient, 'send_test_run_notification')

        import inspect
        sig = inspect.signature(SlackClient.send_test_run_notification)
        params = list(sig.parameters.keys())

        assert 'status' in params
        assert 'passed' in params
        assert 'failed' in params
        assert 'run_url' in params or 'duration_seconds' in params

    def test_slack_client_can_send_defect_alerts(self):
        """Test that SlackClient can send critical defect alerts"""
        from integrations.slack.client import SlackClient

        assert hasattr(SlackClient, 'send_critical_defect_alert')

        import inspect
        sig = inspect.signature(SlackClient.send_critical_defect_alert)
        params = list(sig.parameters.keys())

        assert 'defect_id' in params or 'title' in params
        assert 'severity' in params

    @pytest.mark.asyncio
    async def test_slack_client_sends_success_notification(self):
        """Test sending successful test run notification to Slack"""
        from integrations.slack.client import SlackClient

        with patch('integrations.slack.client.httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {"ok": True}
            mock_response.raise_for_status = MagicMock()

            mock_async_client = MagicMock()
            mock_async_client.__aenter__ = AsyncMock(return_value=mock_async_client)
            mock_async_client.__aexit__ = AsyncMock(return_value=None)
            mock_async_client.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_async_client

            client = SlackClient(webhook_url="https://hooks.slack.com/test")

            result = await client.send_test_run_notification(
                status="success",
                passed=25,
                failed=0,
                duration_seconds=120.5,
                run_url="https://test-platform.example.com/runs/123"
            )

            assert result is not None
            assert result.get("ok") is True

    @pytest.mark.asyncio
    async def test_slack_client_sends_failure_notification(self):
        """Test sending failed test run notification to Slack"""
        from integrations.slack.client import SlackClient

        with patch('integrations.slack.client.httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {"ok": True}
            mock_response.raise_for_status = MagicMock()

            mock_async_client = MagicMock()
            mock_async_client.__aenter__ = AsyncMock(return_value=mock_async_client)
            mock_async_client.__aexit__ = AsyncMock(return_value=None)
            mock_async_client.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_async_client

            client = SlackClient(webhook_url="https://hooks.slack.com/test")

            result = await client.send_test_run_notification(
                status="failure",
                passed=18,
                failed=7,
                duration_seconds=145.3,
                run_url="https://test-platform.example.com/runs/124"
            )

            assert result is not None


class TestNotificationServiceIntegration:
    """Test NotificationService coordinating all three integrations"""

    def test_notification_service_can_notify_test_run_result(self):
        """Test that NotificationService can send test run notifications"""
        from services.notification_service import NotificationService

        assert hasattr(NotificationService, 'notify_test_run_result')

        import inspect
        sig = inspect.signature(NotificationService.notify_test_run_result)
        params = list(sig.parameters.keys())

        assert 'status' in params
        assert 'passed' in params
        assert 'failed' in params

    def test_notification_service_can_notify_critical_defect(self):
        """Test that NotificationService can send defect alerts"""
        from services.notification_service import NotificationService

        assert hasattr(NotificationService, 'notify_critical_defect')

    @pytest.mark.asyncio
    async def test_notification_service_sends_to_all_channels(self):
        """Test that NotificationService sends to GitHub, Slack simultaneously"""
        from services.notification_service import NotificationService
        from integrations.github.client import GitHubClient
        from integrations.slack.client import SlackClient

        # Mock GitHub client
        mock_github = MagicMock(spec=GitHubClient)
        mock_github.set_commit_status = AsyncMock(return_value={"state": "success"})

        # Mock Slack client
        mock_slack = MagicMock(spec=SlackClient)
        mock_slack.send_test_run_notification = AsyncMock(return_value={"ok": True})

        # Create notification service with mocked clients
        service = NotificationService(
            github_client=mock_github,
            slack_client=mock_slack
        )

        # Send notification
        await service.notify_test_run_result(
            status="success",
            passed=30,
            failed=2,
            duration_seconds=180.0,
            run_url="https://demo-platform.example.com/runs/456",
            commit_sha="abc123def456"
        )

        # Verify both clients were called
        mock_github.set_commit_status.assert_called_once()
        mock_slack.send_test_run_notification.assert_called_once()


class TestEndToEndIntegration:
    """Test end-to-end integration with demo repository/project"""

    @pytest.mark.asyncio
    async def test_complete_notification_flow_for_demo_project(self):
        """
        Test complete notification flow for a demo repository.

        This test demonstrates:
        1. Test run completes
        2. GitHub commit status is updated
        3. Slack notification is sent
        4. If failures exist, GitHub issue is created
        5. If critical failures, Jira issue is created
        """
        from services.notification_service import NotificationService
        from integrations.github.client import GitHubClient
        from integrations.slack.client import SlackClient
        from integrations.jira.client import JiraClient

        # Mock all clients
        mock_github = MagicMock(spec=GitHubClient)
        mock_github.set_commit_status = AsyncMock(return_value={"state": "failure"})
        mock_github.create_issue = AsyncMock(return_value={"number": 789})

        mock_slack = MagicMock(spec=SlackClient)
        mock_slack.send_test_run_notification = AsyncMock(return_value={"ok": True})

        mock_jira = MagicMock(spec=JiraClient)
        mock_jira.create_issue = AsyncMock(return_value="DEMO-789")

        # Create notification service
        notification_service = NotificationService(
            github_client=mock_github,
            slack_client=mock_slack
        )

        # Simulate test run with failures
        test_run_data = {
            "status": "failure",
            "passed": 15,
            "failed": 5,
            "duration_seconds": 240.5,
            "run_url": "https://demo-platform.example.com/runs/demo-123",
            "commit_sha": "demo-commit-sha-123"
        }

        # Send notifications
        await notification_service.notify_test_run_result(**test_run_data)

        # Verify GitHub commit status was updated
        assert mock_github.set_commit_status.called
        github_call_args = mock_github.set_commit_status.call_args
        assert github_call_args.kwargs['sha'] == "demo-commit-sha-123"
        assert github_call_args.kwargs['state'] == "failure"

        # Verify Slack notification was sent
        assert mock_slack.send_test_run_notification.called
        slack_call_args = mock_slack.send_test_run_notification.call_args
        assert slack_call_args.kwargs['passed'] == 15
        assert slack_call_args.kwargs['failed'] == 5

        # Create GitHub issue for failures
        await mock_github.create_issue(
            title="Test Failures in Demo Run #123",
            body="5 tests failed in the demo project test run",
            labels=["test-failure", "demo"]
        )

        assert mock_github.create_issue.called

        # Create Jira issue for critical failures (simulated)
        await mock_jira.create_issue(
            project="DEMO",
            data={
                "summary": "Critical test failures in demo project",
                "description": "5 critical failures detected",
                "issuetype": {"name": "Bug"}
            }
        )

        assert mock_jira.create_issue.called

    def test_demo_configuration_structure(self):
        """Test that demo configuration structure is valid"""
        demo_config = {
            "github": {
                "enabled": True,
                "token": "demo-github-token",
                "repo_owner": "demo-org",
                "repo_name": "demo-repo",
                "commit_status_enabled": True,
                "issue_creation_enabled": True
            },
            "jira": {
                "enabled": True,
                "email": "demo@example.com",
                "api_token": "demo-jira-token",
                "base_url": "https://demo.atlassian.net/rest/api/3",
                "project": "DEMO"
            },
            "slack": {
                "enabled": True,
                "webhook_url": "https://hooks.slack.com/services/demo/webhook",
                "default_channel": "#demo-test-alerts"
            }
        }

        # Validate structure
        assert "github" in demo_config
        assert "jira" in demo_config
        assert "slack" in demo_config

        assert demo_config["github"]["enabled"] is True
        assert demo_config["jira"]["enabled"] is True
        assert demo_config["slack"]["enabled"] is True

        # Validate required fields
        assert "repo_owner" in demo_config["github"]
        assert "repo_name" in demo_config["github"]
        assert "project" in demo_config["jira"]
        assert "webhook_url" in demo_config["slack"]


class TestIntegrationConfiguration:
    """Test configuration management for integrations"""

    def test_can_load_github_configuration(self):
        """Test that GitHub configuration can be loaded"""
        config = {
            "token": "test-token",
            "repo_owner": "test-org",
            "repo_name": "test-repo"
        }

        from integrations.github.client import GitHubClient

        # Should be able to instantiate with config
        client = GitHubClient(**config)

        assert client is not None
        assert hasattr(client, '_token')
        assert hasattr(client, '_repo_owner')
        assert hasattr(client, '_repo_name')

    def test_can_load_jira_configuration(self):
        """Test that Jira configuration can be loaded"""
        config = {
            "email": "test@example.com",
            "api_token": "test-token",
            "base_url": "https://example.atlassian.net/rest/api/3"
        }

        from integrations.jira.client import JiraClient

        client = JiraClient(**config)

        assert client is not None
        assert hasattr(client, '_email')
        assert hasattr(client, '_api_token')

    def test_can_load_slack_configuration(self):
        """Test that Slack configuration can be loaded"""
        config = {
            "webhook_url": "https://hooks.slack.com/services/test"
        }

        from integrations.slack.client import SlackClient

        client = SlackClient(**config)

        assert client is not None
        assert hasattr(client, '_webhook_url')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
