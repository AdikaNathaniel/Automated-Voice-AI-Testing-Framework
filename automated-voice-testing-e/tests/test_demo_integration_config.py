"""
Test Demo Integration Configuration

Tests verify that the demo configuration for GitHub/Jira/Slack integrations
is properly structured and contains all required fields.

This validates the demo setup referenced in TODOS.md Section 7:
"Integration with GitHub/Jira/Slack configured and tested for a demo repository/project"
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import pytest
import json
from pathlib import Path


class TestDemoConfigurationFile:
    """Test that demo configuration file exists and is valid JSON"""

    def test_demo_config_file_exists(self):
        """Test that integrations.demo.json exists"""
        config_path = Path(__file__).parent.parent / "config" / "integrations.demo.json"
        assert config_path.exists(), f"Demo config not found at {config_path}"

    def test_demo_config_is_valid_json(self):
        """Test that demo config is valid JSON"""
        config_path = Path(__file__).parent.parent / "config" / "integrations.demo.json"

        with open(config_path) as f:
            config = json.load(f)

        assert config is not None
        assert isinstance(config, dict)

    def test_demo_config_has_version(self):
        """Test that config has version field"""
        config_path = Path(__file__).parent.parent / "config" / "integrations.demo.json"

        with open(config_path) as f:
            config = json.load(f)

        assert "version" in config
        assert isinstance(config["version"], str)

    def test_demo_config_has_integrations(self):
        """Test that config has integrations section"""
        config_path = Path(__file__).parent.parent / "config" / "integrations.demo.json"

        with open(config_path) as f:
            config = json.load(f)

        assert "integrations" in config
        assert isinstance(config["integrations"], dict)


class TestGitHubConfiguration:
    """Test GitHub integration configuration"""

    @pytest.fixture
    def github_config(self):
        """Load GitHub configuration from demo file"""
        config_path = Path(__file__).parent.parent / "config" / "integrations.demo.json"

        with open(config_path) as f:
            config = json.load(f)

        return config["integrations"]["github"]

    def test_github_config_exists(self, github_config):
        """Test that GitHub config exists"""
        assert github_config is not None
        assert isinstance(github_config, dict)

    def test_github_config_has_required_fields(self, github_config):
        """Test that GitHub config has all required fields"""
        required_fields = ["enabled", "token", "repo_owner", "repo_name"]

        for field in required_fields:
            assert field in github_config, f"Missing required field: {field}"

    def test_github_config_has_features(self, github_config):
        """Test that GitHub config has features section"""
        assert "features" in github_config
        assert isinstance(github_config["features"], dict)

        # Check for commit_status and issue_creation features
        assert "commit_status" in github_config["features"]
        assert "issue_creation" in github_config["features"]

    def test_github_commit_status_feature(self, github_config):
        """Test that commit status feature is properly configured"""
        commit_status = github_config["features"]["commit_status"]

        assert "enabled" in commit_status
        assert "context" in commit_status
        assert isinstance(commit_status["enabled"], bool)
        assert isinstance(commit_status["context"], str)

    def test_github_issue_creation_feature(self, github_config):
        """Test that issue creation feature is properly configured"""
        issue_creation = github_config["features"]["issue_creation"]

        assert "enabled" in issue_creation
        assert "on_failure" in issue_creation
        assert "labels" in issue_creation
        assert isinstance(issue_creation["labels"], list)

    def test_github_repo_info_valid(self, github_config):
        """Test that repo owner and name are valid strings"""
        assert isinstance(github_config["repo_owner"], str)
        assert len(github_config["repo_owner"]) > 0

        assert isinstance(github_config["repo_name"], str)
        assert len(github_config["repo_name"]) > 0


class TestJiraConfiguration:
    """Test Jira integration configuration"""

    @pytest.fixture
    def jira_config(self):
        """Load Jira configuration from demo file"""
        config_path = Path(__file__).parent.parent / "config" / "integrations.demo.json"

        with open(config_path) as f:
            config = json.load(f)

        return config["integrations"]["jira"]

    def test_jira_config_exists(self, jira_config):
        """Test that Jira config exists"""
        assert jira_config is not None
        assert isinstance(jira_config, dict)

    def test_jira_config_has_required_fields(self, jira_config):
        """Test that Jira config has all required fields"""
        required_fields = ["enabled", "email", "api_token", "base_url", "project"]

        for field in required_fields:
            assert field in jira_config, f"Missing required field: {field}"

    def test_jira_config_has_features(self, jira_config):
        """Test that Jira config has features section"""
        assert "features" in jira_config
        assert isinstance(jira_config["features"], dict)

        # Check for issue_creation and issue_updates features
        assert "issue_creation" in jira_config["features"]
        assert "issue_updates" in jira_config["features"]

    def test_jira_issue_creation_feature(self, jira_config):
        """Test that issue creation feature is properly configured"""
        issue_creation = jira_config["features"]["issue_creation"]

        assert "enabled" in issue_creation
        assert "on_critical_failure" in issue_creation
        assert "issue_type" in issue_creation
        assert "priority_mapping" in issue_creation

        # Validate priority mapping
        priority_mapping = issue_creation["priority_mapping"]
        expected_priorities = ["critical", "high", "medium", "low"]

        for priority in expected_priorities:
            assert priority in priority_mapping, f"Missing priority: {priority}"

    def test_jira_base_url_valid(self, jira_config):
        """Test that Jira base URL is valid"""
        base_url = jira_config["base_url"]

        assert isinstance(base_url, str)
        assert base_url.startswith("https://")
        assert "atlassian.net" in base_url
        assert "/rest/api/" in base_url

    def test_jira_project_key_valid(self, jira_config):
        """Test that Jira project key is valid"""
        project = jira_config["project"]

        assert isinstance(project, str)
        assert len(project) > 0
        assert project.isupper() or project.isalnum()  # Project keys are typically uppercase


class TestSlackConfiguration:
    """Test Slack integration configuration"""

    @pytest.fixture
    def slack_config(self):
        """Load Slack configuration from demo file"""
        config_path = Path(__file__).parent.parent / "config" / "integrations.demo.json"

        with open(config_path) as f:
            config = json.load(f)

        return config["integrations"]["slack"]

    def test_slack_config_exists(self, slack_config):
        """Test that Slack config exists"""
        assert slack_config is not None
        assert isinstance(slack_config, dict)

    def test_slack_config_has_required_fields(self, slack_config):
        """Test that Slack config has all required fields"""
        required_fields = ["enabled", "webhook_url", "default_channel"]

        for field in required_fields:
            assert field in slack_config, f"Missing required field: {field}"

    def test_slack_config_has_features(self, slack_config):
        """Test that Slack config has features section"""
        assert "features" in slack_config
        assert isinstance(slack_config["features"], dict)

        # Check for notification features
        assert "test_run_notifications" in slack_config["features"]
        assert "defect_alerts" in slack_config["features"]
        assert "system_alerts" in slack_config["features"]

    def test_slack_test_run_notifications_feature(self, slack_config):
        """Test that test run notifications feature is configured"""
        notifications = slack_config["features"]["test_run_notifications"]

        assert "enabled" in notifications
        assert "notify_on" in notifications
        assert isinstance(notifications["notify_on"], list)
        assert "failure" in notifications["notify_on"] or "success" in notifications["notify_on"]

    def test_slack_defect_alerts_feature(self, slack_config):
        """Test that defect alerts feature is configured"""
        defect_alerts = slack_config["features"]["defect_alerts"]

        assert "enabled" in defect_alerts
        assert isinstance(defect_alerts["enabled"], bool)

    def test_slack_default_channel_valid(self, slack_config):
        """Test that default channel is valid"""
        channel = slack_config["default_channel"]

        assert isinstance(channel, str)
        assert channel.startswith("#") or channel.startswith("@")

    def test_slack_notification_rules_exist(self, slack_config):
        """Test that notification rules are defined"""
        assert "notification_rules" in slack_config
        rules = slack_config["notification_rules"]

        assert isinstance(rules, dict)
        assert "notify_on_regression" in rules or "success_threshold" in rules


class TestNotificationRouting:
    """Test notification routing configuration"""

    @pytest.fixture
    def routing_config(self):
        """Load notification routing from demo file"""
        config_path = Path(__file__).parent.parent / "config" / "integrations.demo.json"

        with open(config_path) as f:
            config = json.load(f)

        return config["notification_routing"]

    def test_routing_config_exists(self, routing_config):
        """Test that notification routing exists"""
        assert routing_config is not None
        assert isinstance(routing_config, dict)

    def test_routing_has_event_types(self, routing_config):
        """Test that routing defines event types"""
        expected_events = [
            "test_run_complete",
            "test_failure",
            "critical_failure",
            "regression_detected"
        ]

        for event in expected_events:
            assert event in routing_config, f"Missing routing for event: {event}"

    def test_routing_event_has_channels(self, routing_config):
        """Test that each event type specifies which channels to use"""
        for event_name, channels in routing_config.items():
            assert isinstance(channels, dict)

            # Each event should specify github/slack/jira routing
            assert "github" in channels or "slack" in channels or "jira" in channels

    def test_critical_failure_routes_to_all_channels(self, routing_config):
        """Test that critical failures route to all channels"""
        critical_routing = routing_config.get("critical_failure", {})

        # Critical failures should notify all three services
        assert critical_routing.get("github") is True
        assert critical_routing.get("slack") is True
        assert critical_routing.get("jira") is True


class TestDemoMetadata:
    """Test demo metadata section"""

    @pytest.fixture
    def demo_metadata(self):
        """Load demo metadata from config file"""
        config_path = Path(__file__).parent.parent / "config" / "integrations.demo.json"

        with open(config_path) as f:
            config = json.load(f)

        return config.get("demo_metadata", {})

    def test_demo_metadata_exists(self, demo_metadata):
        """Test that demo metadata section exists"""
        assert demo_metadata is not None
        assert isinstance(demo_metadata, dict)

    def test_demo_metadata_has_repository_info(self, demo_metadata):
        """Test that demo metadata includes repository information"""
        assert "demo_repository" in demo_metadata
        assert isinstance(demo_metadata["demo_repository"], str)
        assert demo_metadata["demo_repository"].startswith("https://")

    def test_demo_metadata_has_project_urls(self, demo_metadata):
        """Test that demo metadata includes project URLs"""
        assert "jira_project_url" in demo_metadata or "slack_workspace" in demo_metadata

    def test_demo_metadata_has_test_data(self, demo_metadata):
        """Test that demo metadata includes sample test data"""
        if "test_data" in demo_metadata:
            test_data = demo_metadata["test_data"]

            assert isinstance(test_data, dict)
            # Should have at least one sample identifier
            assert len(test_data) > 0


class TestConfigurationIntegration:
    """Test that configuration integrates with actual clients"""

    def test_can_instantiate_github_client_from_config(self):
        """Test that GitHub client can be instantiated from config"""
        config_path = Path(__file__).parent.parent / "config" / "integrations.demo.json"

        with open(config_path) as f:
            config = json.load(f)

        github_config = config["integrations"]["github"]

        from integrations.github.client import GitHubClient

        # Should be able to instantiate with demo config structure
        # (using placeholder token for test)
        client = GitHubClient(
            token="demo-token",
            repo_owner=github_config["repo_owner"],
            repo_name=github_config["repo_name"]
        )

        assert client is not None

    def test_can_instantiate_jira_client_from_config(self):
        """Test that Jira client can be instantiated from config"""
        config_path = Path(__file__).parent.parent / "config" / "integrations.demo.json"

        with open(config_path) as f:
            config = json.load(f)

        jira_config = config["integrations"]["jira"]

        from integrations.jira.client import JiraClient

        # Should be able to instantiate with demo config structure
        client = JiraClient(
            email="demo@example.com",
            api_token="demo-token",
            base_url=jira_config["base_url"]
        )

        assert client is not None

    def test_can_instantiate_slack_client_from_config(self):
        """Test that Slack client can be instantiated from config"""
        config_path = Path(__file__).parent.parent / "config" / "integrations.demo.json"

        with open(config_path) as f:
            config = json.load(f)

        slack_config = config["integrations"]["slack"]

        from integrations.slack.client import SlackClient

        # Should be able to instantiate with demo config structure
        client = SlackClient(
            webhook_url="https://hooks.slack.com/demo",
            default_channel=slack_config["default_channel"],
            username=slack_config.get("username"),
            icon_emoji=slack_config.get("icon_emoji")
        )

        assert client is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
