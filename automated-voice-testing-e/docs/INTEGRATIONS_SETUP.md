# GitHub/Jira/Slack Integrations Setup Guide

This guide explains how to configure and test GitHub, Jira, and Slack integrations for the Voice AI Automated Testing Framework.

## Overview

The platform supports three primary integrations:

1. **GitHub** - Commit status updates and issue creation
2. **Jira** - Issue tracking for test failures
3. **Slack** - Real-time notifications

## Prerequisites

Before setting up integrations, you need:

- GitHub personal access token with `repo` and `issues` permissions
- Jira API token (generated from Atlassian account settings)
- Slack incoming webhook URL

## Configuration

### 1. GitHub Integration

#### Create GitHub Personal Access Token

1. Go to GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)
2. Click "Generate new token"
3. Select scopes:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
4. Copy the generated token

#### Configure GitHub Integration

```bash
# Set environment variable
export GITHUB_TOKEN="your-github-token"

# Or add to .env file
echo "GITHUB_TOKEN=your-github-token" >> .env
```

#### Test GitHub Integration

```python
from integrations.github.client import GitHubClient

# Initialize client
client = GitHubClient(
    token="your-github-token",
    repo_owner="your-org",
    repo_name="your-repo"
)

# Set commit status
await client.set_commit_status(
    sha="commit-sha",
    state="success",
    description="All tests passed"
)

# Create issue for failure
await client.create_issue(
    title="Test failure: Voice recognition",
    body="Test case 'weather_query' failed",
    labels=["test-failure", "bug"]
)
```

### 2. Jira Integration

#### Generate Jira API Token

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a label (e.g., "Voice AI Testing")
4. Copy the generated token

#### Configure Jira Integration

```bash
# Set environment variables
export JIRA_EMAIL="your-email@example.com"
export JIRA_API_TOKEN="your-jira-token"

# Or add to .env file
echo "JIRA_EMAIL=your-email@example.com" >> .env
echo "JIRA_API_TOKEN=your-jira-token" >> .env
```

#### Test Jira Integration

```python
from integrations.jira.client import JiraClient

# Initialize client
client = JiraClient(
    email="your-email@example.com",
    api_token="your-jira-token",
    base_url="https://your-domain.atlassian.net/rest/api/3"
)

# Create issue for critical failure
issue_key = await client.create_issue(
    project="QA",
    data={
        "summary": "Critical: Voice AI test suite failure",
        "description": "Test suite failed with 5 critical errors",
        "issuetype": {"name": "Bug"},
        "priority": {"name": "High"}
    }
)

print(f"Created Jira issue: {issue_key}")
```

### 3. Slack Integration

#### Create Slack Incoming Webhook

1. Go to https://api.slack.com/apps
2. Create a new app or select existing app
3. Navigate to "Incoming Webhooks"
4. Activate Incoming Webhooks
5. Click "Add New Webhook to Workspace"
6. Select the channel for notifications
7. Copy the webhook URL

#### Configure Slack Integration

```bash
# Set environment variable
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Or add to .env file
echo "SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL" >> .env
```

#### Test Slack Integration

```python
from integrations.slack.client import SlackClient

# Initialize client
client = SlackClient(
    webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    default_channel="#test-alerts"
)

# Send test run notification
await client.send_test_run_notification(
    status="success",
    passed=25,
    failed=0,
    duration_seconds=120.5,
    run_url="https://testing-platform.example.com/runs/123"
)

# Send critical defect alert
await client.send_critical_defect_alert(
    defect_id="DEF-456",
    title="Critical voice recognition failure",
    severity="critical",
    defect_url="https://testing-platform.example.com/defects/456"
)
```

## Demo Configuration

A complete demo configuration is available at `config/integrations.demo.json`.

### Load Demo Configuration

```python
import json

# Load configuration
with open('config/integrations.demo.json') as f:
    config = json.load(f)

# Access GitHub settings
github_config = config['integrations']['github']
repo_owner = github_config['repo_owner']
repo_name = github_config['repo_name']

# Access Jira settings
jira_config = config['integrations']['jira']
jira_project = jira_config['project']

# Access Slack settings
slack_config = config['integrations']['slack']
default_channel = slack_config['default_channel']
```

### Environment Variables for Demo

Create a `.env` file with these values:

```bash
# GitHub
GITHUB_TOKEN=your-github-personal-access-token

# Jira
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-jira-api-token

# Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

## Using NotificationService

The `NotificationService` coordinates all three integrations:

```python
from services.notification_service import NotificationService
from integrations.github.client import GitHubClient
from integrations.slack.client import SlackClient

# Initialize clients
github_client = GitHubClient(
    token=os.getenv("GITHUB_TOKEN"),
    repo_owner="demo-org",
    repo_name="voice-ai-testing-demo"
)

slack_client = SlackClient(
    webhook_url=os.getenv("SLACK_WEBHOOK_URL"),
    default_channel="#voice-ai-test-alerts"
)

# Create notification service
notification_service = NotificationService(
    github_client=github_client,
    slack_client=slack_client
)

# Send test run result (updates both GitHub and Slack)
await notification_service.notify_test_run_result(
    status="success",
    passed=30,
    failed=2,
    duration_seconds=180.0,
    run_url="https://demo-platform.example.com/runs/456",
    commit_sha="abc123def456"
)
```

## Integration with Test Runs

Integrations are automatically triggered when test runs complete:

1. **Test run completes** → System calculates metrics
2. **NotificationService** → Sends to configured channels
3. **GitHub** → Commit status updated
4. **Slack** → Team notification sent
5. **Jira** (optional) → Issue created for critical failures

### Example Workflow

```python
from services.orchestration_service import create_test_run

# Create and run tests
test_run = await create_test_run(
    db=db,
    suite_id=suite_id,
    trigger_type="webhook",
    trigger_metadata={
        "provider": "github",
        "commit_sha": "abc123",
        "branch": "main"
    }
)

# After test execution, notifications are sent automatically
# based on notification_routing in config
```

## Notification Routing

Configure which services receive which types of notifications:

```json
{
  "notification_routing": {
    "test_run_complete": {
      "github": true,
      "slack": true,
      "jira": false
    },
    "critical_failure": {
      "github": true,
      "slack": true,
      "jira": true
    }
  }
}
```

## Testing Integrations

Run the integration test suite:

```bash
# Test all integrations
pytest tests/test_github_jira_slack_integration.py -v

# Test specific integration
pytest tests/test_github_jira_slack_integration.py::TestGitHubIntegration -v
pytest tests/test_github_jira_slack_integration.py::TestJiraIntegration -v
pytest tests/test_github_jira_slack_integration.py::TestSlackIntegration -v

# Test end-to-end flow
pytest tests/test_github_jira_slack_integration.py::TestEndToEndIntegration -v
```

## Troubleshooting

### GitHub Issues

**Problem**: "Bad credentials" error

**Solution**: Verify token has correct permissions and hasn't expired

```bash
# Test token validity
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
```

### Jira Issues

**Problem**: "Authentication failed" error

**Solution**: Verify email and API token are correct

```bash
# Test Jira authentication
curl -u YOUR_EMAIL:YOUR_API_TOKEN \
  https://your-domain.atlassian.net/rest/api/3/myself
```

### Slack Issues

**Problem**: Webhook returns "invalid_payload" error

**Solution**: Verify webhook URL and payload structure

```bash
# Test webhook
curl -X POST YOUR_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d '{"text": "Test message"}'
```

## Security Best Practices

1. **Never commit tokens/secrets** to version control
2. **Use environment variables** for sensitive data
3. **Rotate tokens regularly** (every 90 days recommended)
4. **Limit token permissions** to minimum required
5. **Use separate tokens** for dev/staging/production

## Demo Repository Setup

The demo configuration references a demo repository at:
`https://github.com/demo-org/voice-ai-testing-demo`

To test with your own repository:

1. Fork or create a new repository
2. Update `config/integrations.demo.json`:
   - Change `repo_owner` to your GitHub org/user
   - Change `repo_name` to your repository name
3. Set environment variables with your tokens
4. Run integration tests

## Next Steps

After setup:

1. ✅ Configure environment variables
2. ✅ Test each integration individually
3. ✅ Run integration test suite
4. ✅ Configure notification routing
5. ✅ Test end-to-end flow with demo test run
6. ✅ Monitor notifications in GitHub/Jira/Slack
7. ✅ Adjust configuration based on team needs

## Support

For issues or questions:
- Review integration client code: `backend/integrations/`
- Check test examples: `tests/test_github_jira_slack_integration.py`
- Review notification service: `backend/services/notification_service.py`
