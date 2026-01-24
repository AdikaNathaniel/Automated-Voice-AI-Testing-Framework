# Task: Slack & Jira Integrations - Completion & Enhancement

## Overview

The integration system allows the Voice AI Testing Framework to:
- **Slack**: Send notifications for test results, defects, alerts, and edge cases
- **Jira**: Auto-create tickets for defects and sync status

## Current State Assessment

### What's COMPLETE ✅

| Component | Location | Status |
|-----------|----------|--------|
| **Slack** | | |
| SlackClient | `backend/integrations/slack/client.py` | Working |
| SlackBot (slash commands) | `backend/integrations/slack/bot.py` | Working |
| NotificationConfig Model | `backend/models/notification_config.py` | Working |
| NotificationService | `backend/services/notification_service.py` | Working |
| Slack API Routes | `backend/api/routes/integrations.py` | Working |
| Slack UI Page | `frontend/src/pages/Integrations/Slack.tsx` | Working |
| Slack Redux Slice | `frontend/src/store/slices/slackIntegrationSlice.ts` | Working |
| **Jira** | | |
| JiraClient | `backend/integrations/jira/client.py` | Working |
| IntegrationConfig Model | `backend/models/integration_config.py` | Working |
| Defect Model (Jira fields) | `backend/models/defect.py` | Has fields |
| Jira API Routes | `backend/api/routes/integrations.py` | Working |
| Jira UI Page | `frontend/src/pages/Integrations/Jira.tsx` | Working |
| Jira Redux Slice | `frontend/src/store/slices/jiraIntegrationSlice.ts` | Working |

### What Needs Work ⚠️

| Gap | Priority | Effort |
|-----|----------|--------|
| Notification trigger integration points | High | Medium |
| Auto-create Jira ticket from defect flow | High | Medium |
| Slack OAuth flow (vs manual webhook) | Medium | High |
| Integration health monitoring UI | Medium | Low |
| Jira bidirectional sync (status updates) | Low | High |
| Slack interactive messages (buttons) | Low | Medium |

---

## Task 1: Wire Up Notification Triggers

### Objective
Ensure Slack notifications are actually sent when relevant events occur in the system.

### Context
- `NotificationService` exists with methods like `notify_test_run_result()`
- But the service needs to be called from the right places in the codebase

### Requirements

#### Find and Wire Trigger Points

1. **Suite Run Completion**
   - Location: `backend/services/suite_run_service.py` or orchestration service
   - Trigger: When a test suite finishes execution
   - Call: `notification_service.notify_test_run_result()`

2. **Defect Creation**
   - Location: `backend/services/defect_service.py` or `defect_auto_creator.py`
   - Trigger: When a new critical defect is created
   - Call: `notification_service.notify_critical_defect()`

3. **System Alerts**
   - Location: Health check or monitoring service
   - Trigger: When system health degrades
   - Call: `notification_service.notify_system_alert()`

4. **Edge Case Discovery**
   - Location: `backend/services/edge_case_detection_service.py`
   - Trigger: When a new edge case is identified
   - Call: `notification_service.notify_edge_case()`

#### Implementation Steps

```python
# Example: In suite_run_service.py after run completion

from services.notification_service import NotificationService

class SuiteRunService:
    def __init__(self):
        self.notification_service = NotificationService()

    async def complete_suite_run(self, suite_run: SuiteRun):
        # ... existing completion logic ...

        # Send notification
        try:
            await self.notification_service.notify_test_run_result(
                suite_run_id=suite_run.id,
                suite_name=suite_run.suite_name,
                status=suite_run.status,
                passed_count=suite_run.passed_count,
                failed_count=suite_run.failed_count,
                total_count=suite_run.total_count,
                duration_seconds=suite_run.duration_seconds,
            )
        except Exception as e:
            logger.warning(f"Failed to send notification: {e}")
            # Don't fail the run for notification errors
```

### Files to Investigate/Modify
- `backend/services/suite_run_service.py`
- `backend/services/orchestration_service.py`
- `backend/services/defect_service.py`
- `backend/services/defect_auto_creator.py`
- `backend/services/edge_case_detection_service.py`

### Acceptance Criteria
- [ ] Slack notification sent when suite run completes (if enabled)
- [ ] Slack notification sent when critical defect created (if enabled)
- [ ] Notification failures don't break core functionality
- [ ] User can verify via "Test Notification" button in UI

---

## Task 2: Implement Auto-Create Jira Ticket from Defect

### Objective
When a defect is created (manually or automatically), optionally create a corresponding Jira ticket.

### Context
- `JiraClient.create_issue()` exists
- `Defect` model has `jira_issue_key`, `jira_issue_url`, `jira_status` fields
- `IntegrationConfig` stores Jira credentials and `auto_create_tickets` flag

### Requirements

#### Backend Implementation

1. **Enhance DefectService** (`backend/services/defect_service.py`)

```python
from integrations.jira.client import JiraClient

class DefectService:
    def __init__(self, jira_client: Optional[JiraClient] = None):
        self.jira_client = jira_client

    async def create_defect(
        self,
        db: AsyncSession,
        defect_data: DefectCreate,
        auto_create_jira: bool = False,
    ) -> Defect:
        # Create defect in database
        defect = Defect(**defect_data.dict())
        db.add(defect)
        await db.flush()

        # Auto-create Jira ticket if enabled
        if auto_create_jira and self.jira_client:
            try:
                jira_issue = await self._create_jira_issue(defect)
                defect.jira_issue_key = jira_issue['key']
                defect.jira_issue_url = jira_issue['url']
                defect.jira_status = 'Open'
            except JiraClientError as e:
                logger.error(f"Failed to create Jira issue: {e}")
                # Continue without Jira - don't fail defect creation

        await db.commit()
        return defect

    async def _create_jira_issue(self, defect: Defect) -> dict:
        """Create Jira issue from defect."""
        # Map severity to Jira priority
        priority_map = {
            'critical': 'Highest',
            'high': 'High',
            'medium': 'Medium',
            'low': 'Low',
        }

        issue_data = {
            'fields': {
                'summary': defect.title,
                'description': self._format_jira_description(defect),
                'issuetype': {'name': 'Bug'},
                'priority': {'name': priority_map.get(defect.severity, 'Medium')},
                'labels': ['voice-ai-testing', 'auto-created'],
            }
        }

        result = await self.jira_client.create_issue(
            project=self.jira_project_key,
            data=issue_data,
        )

        return {
            'key': result['key'],
            'url': f"{self.jira_base_url}/browse/{result['key']}",
        }

    def _format_jira_description(self, defect: Defect) -> str:
        """Format defect details for Jira description."""
        return f"""
h2. Defect Details

*Severity:* {defect.severity}
*Status:* {defect.status}
*Created:* {defect.created_at}

h3. Description
{defect.description}

h3. Steps to Reproduce
{defect.steps_to_reproduce or 'N/A'}

h3. Expected Result
{defect.expected_result or 'N/A'}

h3. Actual Result
{defect.actual_result or 'N/A'}

----
_Auto-created by Voice AI Testing Framework_
        """
```

2. **Add "Create Jira Ticket" button to Defect UI**
   - For defects without Jira link, show "Create Ticket" button
   - For defects with Jira link, show clickable link to Jira

3. **Load Jira config on service initialization**
   - Check if Jira integration is configured and `auto_create_tickets` is enabled
   - Initialize `JiraClient` with credentials from `IntegrationConfig`

### Files to Modify
- `backend/services/defect_service.py` - Add Jira creation logic
- `backend/api/routes/defects.py` - Add endpoint for manual Jira creation
- `frontend/src/pages/Defects/DefectDetail.tsx` - Add Jira button/link

### Acceptance Criteria
- [ ] New defect auto-creates Jira ticket when enabled
- [ ] Defect record stores Jira issue key and URL
- [ ] Manual "Create Jira Ticket" button works for existing defects
- [ ] Jira link is clickable in defect detail view
- [ ] Jira creation failure doesn't prevent defect creation

---

## Task 3: Add Integration Health Monitoring

### Objective
Show users the health status of their integrations and recent activity.

### Requirements

#### Backend
1. **Health check endpoints** (may already exist)
   ```
   GET /api/v1/integrations/health
   ```
   Returns:
   ```json
   {
     "slack": {
       "configured": true,
       "last_successful_send": "2024-01-15T10:30:00Z",
       "last_error": null,
       "status": "healthy"
     },
     "jira": {
       "configured": true,
       "last_successful_call": "2024-01-15T09:45:00Z",
       "last_error": "401 Unauthorized",
       "status": "error"
     }
   }
   ```

2. **Track integration activity**
   - Log successful/failed API calls
   - Store last N events for display

#### Frontend
1. **Integration status cards** on dashboard
   - Green/Yellow/Red indicator
   - Last activity timestamp
   - Quick link to configuration

2. **Activity log component**
   - Show recent integration events
   - Filter by integration type
   - Show error details

### Files to Create/Modify
- `backend/services/integration_health_service.py` (may exist)
- `backend/api/routes/integrations.py` - Add health endpoint
- `frontend/src/components/Integrations/IntegrationHealthCard.tsx` (new)
- `frontend/src/pages/Integrations/IntegrationsDashboard.tsx` - Add health cards

### Acceptance Criteria
- [ ] Dashboard shows integration health status
- [ ] Users can see when last successful call was made
- [ ] Error messages are displayed clearly
- [ ] Quick access to fix configuration issues

---

## Reference: Existing Integration Architecture

### Backend Structure
```
backend/
├── integrations/
│   ├── jira/
│   │   └── client.py           # JiraClient - REST API wrapper
│   └── slack/
│       ├── client.py           # SlackClient - Webhook notifications
│       └── bot.py              # SlackBot - Slash command handler
├── models/
│   ├── integration_config.py   # GitHub/Jira config storage
│   ├── notification_config.py  # Slack config storage
│   └── defect.py               # Has jira_issue_key, jira_issue_url
├── services/
│   ├── notification_service.py # Dispatch to Slack/GitHub
│   ├── webhook_service.py      # Incoming webhook handling
│   └── defect_service.py       # Defect CRUD
└── api/routes/
    ├── integrations.py         # All integration endpoints
    └── webhooks.py             # Incoming webhook endpoints
```

### Frontend Structure
```
frontend/src/
├── pages/Integrations/
│   ├── IntegrationsDashboard.tsx
│   ├── Slack.tsx
│   └── Jira.tsx
├── store/slices/
│   ├── slackIntegrationSlice.ts
│   └── jiraIntegrationSlice.ts
└── components/Integrations/
    └── IntegrationLogs.tsx
```

### API Endpoints
```
# Slack
GET    /api/v1/integrations/slack/config     # Get config
PUT    /api/v1/integrations/slack/config     # Update config
DELETE /api/v1/integrations/slack/config     # Disconnect
POST   /api/v1/integrations/slack/test       # Test notification

# Jira
GET    /api/v1/integrations/jira/config      # Get config
PUT    /api/v1/integrations/jira/config      # Update config
DELETE /api/v1/integrations/jira/config      # Disconnect

# General
GET    /api/v1/integrations/status           # All integrations status
GET    /api/v1/integrations/logs             # Activity logs
```

### Environment Variables
```bash
# Jira
JIRA_URL=https://your-company.atlassian.net
JIRA_USERNAME=your-email@example.com
JIRA_API_TOKEN=your-api-token

# Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ
SLACK_ALERT_CHANNEL=#voice-ai-alerts
SLACK_NOTIFICATIONS_ENABLED=true
```

---

## Testing Integrations Locally

### Slack Testing
1. Create a Slack webhook URL (Slack App → Incoming Webhooks)
2. Add to `.env`: `SLACK_WEBHOOK_URL=https://hooks.slack.com/...`
3. Use the "Test Notification" button in UI
4. Or call: `POST /api/v1/integrations/slack/test`

### Jira Testing
1. Create Jira API token (Atlassian Account → API Tokens)
2. Configure in UI or `.env`:
   ```
   JIRA_URL=https://your-domain.atlassian.net
   JIRA_USERNAME=your-email
   JIRA_API_TOKEN=your-token
   ```
3. Test by creating a defect with auto-create enabled

### SlackBot Testing (Slash Commands)
1. Create Slack App with slash command
2. Configure request URL: `https://your-domain/api/v1/webhooks/slack/commands`
3. Commands: `/voiceai status`, `/voiceai run <suite_id>`, `/voiceai defects`

---

## Getting Started

1. **Understand existing code**
   ```bash
   # Read the key files
   cat backend/integrations/slack/client.py
   cat backend/integrations/jira/client.py
   cat backend/services/notification_service.py
   ```

2. **Run existing tests**
   ```bash
   cd backend
   venv/bin/pytest tests/test_slack_client.py -v
   venv/bin/pytest tests/test_jira_client.py -v
   venv/bin/pytest tests/test_notification_service.py -v
   ```

3. **Test manually**
   - Configure Slack webhook in UI
   - Click "Test Notification"
   - Check Slack channel

---

## Questions?

Contact the team lead for:
- Slack workspace access for testing
- Jira project access for testing
- Clarification on notification requirements
- Priority of features
