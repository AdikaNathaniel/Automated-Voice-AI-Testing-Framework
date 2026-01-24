# Voice AI Automated Testing Framework - Integrations & Infrastructure Analysis

**Analysis Date**: November 18, 2025
**Repository**: /home/ubuntu/workspace/automated-testing
**Scope**: Complete integration points, infrastructure setup, task queue, monitoring, and database migrations

---

## 1. EXTERNAL INTEGRATIONS

### 1.1 Telephony & Voice AI Integrations

#### Houndify (SoundHound) Integration
**Location**: `backend/integrations/houndify/`
**Purpose**: Speech recognition and natural language understanding for voice AI testing

**Components**:
- **HoundifyClient** (`client.py`):
  - Async HTTP client for Houndify API v1
  - Base URL: `https://api.houndify.com/v1`
  - Authentication: HMAC-SHA256 signature with Client ID and Client Key
  - Methods:
    - `text_query()`: Send text queries for NLU processing
    - `voice_query()`: Send audio data (16kHz, 16-bit, mono PCM) for ASR + NLU
    - Conversation state management for multi-turn dialogs
    - Automatic retry with exponential backoff (3 attempts max)
  - Headers: Client ID, Request ID, Request Timestamp, Request Signature
  - Timeout: 30 seconds (configurable)
  - Error handling: Custom `HoundifyError` exception with status code and response detail

- **MockHoundifyClient** (`mock_client.py`):
  - Offline testing stand-in for real Houndify client
  - Returns deterministic test responses
  - No network dependency

- **Models** (`models.py`):
  - `HoundifyError`: Custom exception for Houndify API failures

**Configuration**:
- Environment variables (from `backend/api/config.py`):
  - `SOUNDHOUND_API_KEY`: Required
  - `SOUNDHOUND_CLIENT_ID`: Required
  - `SOUNDHOUND_ENDPOINT`: Default `https://api.houndify.com/v2`
  - `SOUNDHOUND_TIMEOUT`: Default 10 seconds
  - `SOUNDHOUND_MAX_RETRIES`: Default 3 retries
  - `HOUNDIFY_EXTRA_HEADERS`: Optional JSON-formatted extra headers

---

### 1.2 GitHub Integration

**Location**: `backend/integrations/github/`
**Purpose**: CI/CD integration, commit status updates, issue creation/management

**Components**:
- **GitHubClient** (`client.py`):
  - Async HTTP client for GitHub REST API v3
  - Base URL: `https://api.github.com` (configurable)
  - Authentication: Bearer token (GitHub API token)
  - Methods:
    - `set_commit_status()`: Post commit status (success/failure/error/pending)
      - Required: SHA, state, context (default: "continuous-integration/automated-testing")
      - Optional: target_url, description (max 140 chars per GitHub limits)
      - Valid states: error, failure, pending, success
    - `create_issue()`: Create repository issues
      - Required: title
      - Optional: body, labels, assignees, milestone
    - `post_test_run_status()`: Convert test metrics to commit status
      - Maps internal status to GitHub states
      - Builds description from passed/failed/skipped counts
  - Timeout: 10 seconds (configurable)
  - Error handling: `GitHubClientError` for API failures

- **Error Handling**:
  - `GitHubClientError`: Custom exception for network/API errors

**Configuration**:
- Environment variable: `GITHUB_WEBHOOK_SECRET` (for webhook validation)
- Token: Passed during initialization

**Integration Points**:
- Webhook endpoint: `/webhooks/ci-cd`
- Webhook events: push, pull_request
- Auto-trigger tests on push events

---

### 1.3 Slack Integration

**Location**: `backend/integrations/slack/`
**Purpose**: Team notifications for test results, defects, and system alerts

**Components**:
- **SlackClient** (`client.py`):
  - Async HTTP client for Slack Incoming Webhooks
  - Webhook URL required
  - Methods:
    - `send_test_run_notification()`: Post test run summary
      - Supports status: success, failure, warning
      - Includes metrics: passed, failed, duration
      - Block format with emoji and Slack formatting
    - `send_critical_defect_alert()`: Alert on critical defects
      - Defect ID, title, severity, URL, optional description
      - Rotating light emoji for visibility
    - `send_system_alert()`: System health alerts
      - Severity levels: critical, warning, info
      - Emoji mapping for severity
      - Optional investigation URL
  - Channel override capability per message
  - Custom username and icon emoji
  - Timeout: 10 seconds (configurable)
  - Block-format messages with rich formatting

- **Error Handling**:
  - `SlackClientError`: Custom exception for webhook failures

**Configuration**:
- Environment variables:
  - `SLACK_WEBHOOK_URL`: Slack incoming webhook URL
- Optional settings:
  - Default channel
  - Username/icon for bot identity
  - Success threshold for notification logic

**Features**:
- Duration formatting (hours, minutes, seconds)
- Emoji status indicators
- Slack mention support for team alerts
- Notification routing based on severity

---

### 1.4 Jira Integration

**Location**: `backend/integrations/jira/`
**Purpose**: Defect tracking, issue management, automated bug creation

**Components**:
- **JiraClient** (`client.py`):
  - Async HTTP client for Jira Cloud REST API v3
  - Base URL: `https://example.atlassian.net/rest/api/3` (configurable)
  - Authentication: HTTP Basic (email + API token)
  - Methods:
    - `create_issue()`: Create new Jira issue
      - Required: project key, issue data (fields)
      - Returns: Issue key (e.g., "QA-123")
    - `update_issue()`: Update existing issue
      - Takes issue key and update payload
      - Supports field updates
    - `get_issue()`: Retrieve issue details
      - Supports field filtering via params
  - Timeout: 10 seconds (configurable)
  - Error handling: `JiraClientError` for API failures

- **Error Handling**:
  - `JiraClientError`: Custom exception for authentication/API errors

**Configuration**:
- Environment variables:
  - `JIRA_EMAIL`: User email for authentication
  - `JIRA_API_TOKEN`: Atlassian API token
  - Base URL: Passed during initialization

**Integration Features**:
- Auto-creation of defects on test failures
- Priority mapping (critical → Highest, high → High, etc.)
- Auto-close on fix capability
- Comment addition on retests
- Deep linking from test reports

---

### 1.5 Webhook System (CI/CD Integration)

**Location**: `backend/api/routes/webhooks.py`, `backend/services/webhook_service.py`
**Purpose**: Receive and process webhooks from GitHub, GitLab, Jenkins

**Components**:
- **Webhook Routes** (`routes/webhooks.py`):
  - Endpoint: `POST /webhooks/ci-cd`
  - Status code: 202 ACCEPTED (async processing)
  - Auto-detects provider from headers
  - Payload validation (must be JSON object)
  - Signature verification before processing

- **Webhook Service** (`webhook_service.py`):
  - `verify_signature()`: Validate webhook authenticity
    - GitHub: SHA256 HMAC signature (x-hub-signature-256 header)
    - GitLab: Token comparison (x-gitlab-token header)
    - Jenkins: HMAC signature (x-jenkins-event header)
  - `dispatch_ci_cd_event()`: Route event to appropriate handler
  - Signature verification error handling

**Supported Providers**:
- GitHub: Events - push, pull_request, release
- GitLab: Merge request, push, release
- Jenkins: Custom events

**Security**:
- HMAC signature verification for GitHub/Jenkins
- Token verification for GitLab
- Secrets loaded from environment or integration config
- Constant-time comparison to prevent timing attacks

---

## 2. INFRASTRUCTURE & SERVICES

### 2.1 Docker Compose Architecture

**Location**: `docker-compose.yml`
**Version**: 3.8

#### Services Breakdown:

**Database & Caching**:
1. **PostgreSQL 15**
   - Image: `postgres:15-alpine`
   - Port: 5432
   - Database: `voiceai_testing`
   - User: `postgres`
   - Credentials: `postgres:postgres` (dev only)
   - Volume: `postgres_data:/var/lib/postgresql/data`
   - Health check: `pg_isready`

2. **Redis 7**
   - Image: `redis:7-alpine`
   - Port: 6379
   - AOF persistence: Enabled
   - Volume: `redis_data:/data`
   - Health check: `redis-cli ping`

3. **RabbitMQ 3.12**
   - Image: `rabbitmq:3.12-management-alpine`
   - AMQP Port: 5672
   - Management UI: 15672
   - User: `rabbitmq:rabbitmq`
   - Virtual host: `/voiceai`
   - Volume: `rabbitmq_data:/var/lib/rabbitmq`
   - Health check: `rabbitmqctl status`

**Application Services**:
4. **FastAPI Backend**
   - Dockerfile: `backend/Dockerfile`
   - Port: 8000
   - Health check: `curl http://localhost:8000/health`
   - Dependencies: postgres (healthy), redis (healthy), rabbitmq (healthy)
   - Environment: Full DB/Redis/RabbitMQ configuration
   - Secret key: `dev-secret-key-change-in-production`

5. **Frontend (React + Vite)**
   - Dockerfile: `frontend/Dockerfile`
   - Port: 3000 (internal), 80 (exposed via nginx)
   - Dependencies: backend
   - Health check: `curl http://localhost/health`

**Monitoring & Visualization**:
6. **Prometheus 2.52.0**
   - Port: 9090
   - Config: `infrastructure/prometheus/prometheus.yml`
   - Alerts: `infrastructure/prometheus/alerts.yml`
   - Scrape interval: 15 seconds
   - Evaluation interval: 15 seconds
   - Scrapes backend metrics from `/metrics`
   - Health check: Web endpoint `/-/healthy`

7. **Grafana 10.4.3**
   - Port: 3000
   - Datasource: Prometheus
   - Dashboards: Auto-provisioned from `infrastructure/grafana/dashboards/`
   - Volumes:
     - Datasources provisioning
     - Dashboards provisioning
     - Dashboard JSON files
     - Grafana data persistence

8. **Nginx (Reverse Proxy)**
   - Image: `nginx:alpine`
   - Port: 80
   - Upstreams: frontend + backend
   - Config: `nginx/nginx.conf`, `nginx/conf.d/`

**Additional Services**:
9. **pgAdmin 4** (DEV profile)
   - Port: 5050
   - Email: `pgadmin@voiceai.local`
   - Profile-gated (disabled in production)

10. **MinIO (S3-compatible Storage)** for audio files (TASK-114)
    - Port: 9000 (API), 9001 (Console)
    - Buckets: input-audio, output-audio, artifacts
    - Persistence: `minio_data:/data`
    - Anonymous read access enabled

11. **MinIO Client** (createbuckets)
    - Initializes S3 buckets on startup
    - Sets up anonymous download access

**Network**:
- Bridge network: `voiceai-network`
- All services interconnected
- Service-to-service discovery by hostname

---

### 2.2 Prometheus Monitoring

**Location**: `infrastructure/prometheus/`

**Configuration Files**:

#### prometheus.yml
```yaml
Global settings:
- Scrape interval: 15s
- Evaluation interval: 15s
- Rules file: alerts.yml

Scrape configs:
- Backend service: http://backend:8000/metrics
```

**Metrics Collected**:
- Backend application metrics (FastAPI)
- Custom business metrics

#### alerts.yml
Defined Alert Rules:

1. **LowSuccessRate**
   - Expression: Success rate < 95% over 5 minutes
   - Severity: warning
   - Action: Investigate recent regressions

2. **HighQueueDepth**
   - Expression: Queue depth > 1000
   - Duration: 2 minutes
   - Severity: critical
   - Action: Scale workers or investigate bottlenecks

3. **HighResponseLatency**
   - Expression: P95 latency > 5 seconds
   - Duration: 5 minutes
   - Severity: critical
   - Action: Check backend performance

---

### 2.3 Grafana Dashboards

**Location**: `infrastructure/grafana/`

**Provisioning**:
- Datasources: Prometheus configured auto
- Dashboards: Auto-provisioned from JSON files

**Dashboard Definitions**:
1. **system_overview.json**: System health overview
2. **performance.json**: Performance metrics and latency
3. **quality.json**: Test quality and pass rates

---

### 2.4 Storage Configuration (MinIO)

**Location**: docker-compose.yml (services: minio, createbuckets)

**Buckets**:
- `input-audio`: Test input audio files
- `output-audio`: Test output/response audio
- `artifacts`: Test reports and artifacts

**Access**:
- Anonymous read access for test data
- API credentials for write operations
- S3-compatible interface

---

## 3. CELERY TASK QUEUE SYSTEM

### 3.1 Celery Configuration

**Location**: `backend/celery_app.py`

**Broker & Backend**:
- Broker: RabbitMQ (amqp://rabbitmq:rabbitmq@rabbitmq:5672/voiceai)
  - Or Redis (redis://redis:6379/0) as fallback
- Backend: Redis (redis://redis:6379/0) for result storage
- Serialization: JSON (secure, compatible)
- Timezone: UTC

**Celery Configuration**:
```python
Task serializer: JSON
Accept content: JSON only
Timezone: UTC
Task tracking: Enabled
Time limits:
  - Hard limit: 30 minutes
  - Soft limit: 25 minutes
Result expiration: 1 hour
Result persistence: Enabled

Worker settings:
  - Prefetch multiplier: 4
  - Max tasks per child: 1000
  - Task acknowledgement: Late (after execution)
  - Reject on worker loss: Enabled

Task routing:
  - backend.tasks.*: default queue
```

**Periodic Tasks (Beat Schedule)**:
- `cleanup-old-results`: Daily at 00:00 UTC
- `auto-scale-workers`: Every 30 seconds (configurable)
- `send-scheduled-reports`: Daily at 07:00 UTC

---

### 3.2 Task Types

**Location**: `backend/tasks/`

#### Execution Tasks (`execution.py`)

1. **execute_test_case**
   - Single test case execution
   - Supports language variants
   - Language normalization logic
   - Returns: execution_id, status, result, execution_time

2. **execute_test_batch**
   - Multiple test case batch execution
   - Modes: inline (synchronous) or async
   - Parallel/sequential execution based on config
   - Uses Celery chord for completion callbacks
   - Batch tracking with batch_id

3. **execute_voice_test_task**
   - Main voice test execution workflow (TASK-116)
   - Steps:
     1. Fetch queue item from database
     2. Get associated test case
     3. Generate/fetch audio file
     4. Send to SoundHound/voice AI
     5. Store execution results
     6. Update queue status
     7. Trigger validation
   - Resource monitoring (CPU/memory limits)
   - Auto-retry on failure (max 3 retries)
   - Queue status tracking (pending→running→completed/failed)

4. **finalize_batch_execution**
   - Chord callback for batch completion
   - Aggregates all execution results
   - Updates TestRun statistics
   - Flattens nested execution results
   - Marks test run complete/failed

5. **retry_failed_execution**
   - Retry previously failed executions
   - Max retries configuration
   - (Currently placeholder implementation)

#### Validation Tasks (`validation.py`)

1. **validate_test_execution**
   - Validates voice test against expected outcome
   - Steps:
     1. Fetch VoiceTestExecution
     2. Fetch ExpectedOutcome
     3. Run intent/entity/semantic/response_time validators
     4. Aggregate scores with ConfidenceScorer
     5. Create ValidationResult
     6. Determine review status (auto_pass/manual_review)
   - Enqueues low-confidence results for human review
   - Returns: validation_id, confidence_score, validator_scores

#### Reporting Tasks (`reporting.py`)

1. **send_scheduled_reports**
   - Generates and emails executive reports
   - Data providers:
     - Execution summary
     - Trend analysis
     - Risk assessment
   - PDF rendering
   - SMTP email delivery
   - Scheduled: Daily at 07:00 UTC

#### Regression Tasks (`regression.py`)

1. **run_regression_suite**
   - Auto-executes regression test suites
   - Trigger-based execution (scheduled, webhook, manual)
   - Requires: ENABLE_AUTO_REGRESSION flag
   - Configured via: REGRESSION_SUITE_IDS
   - Metadata tracking for trigger context

#### Worker Scaling Tasks (`worker_scaling.py`)

1. **auto_scale_workers** (Periodic)
   - Monitors queue depth
   - Scales based on:
     - Current queue depth
     - Target tasks per worker
     - Min/max worker limits
   - Configurable cooldown period
   - Scheduled every 30 seconds

---

## 4. DATABASE MIGRATIONS (Alembic)

**Location**: `alembic/versions/`
**Total migrations**: 29 files (~2194 lines total)

### Migration Overview

#### Core Domain Migrations:
1. **005** - Users table
2. **006** - Test suites table
3. **007** - Test cases table
4. **008** - Test case languages
5. **009** - Expected outcomes
6. **010** - Test case outcomes
7. **011** - Test runs table
8. **012** - Test execution queue
9. **013** - Voice test executions
10. **014** - Device test executions
11. **015** - Validation results
12. **016** - Configurations
13. **017** - Configuration history
14. **018** - Environment variables

#### Feature Migrations:
15. **019** - Test metrics
16. **020** - Defects
17. **021** - Test case versions
18. **022** - Database indexes
19. **023** - Edge cases
20. **024** - Jira fields to defects

#### Advanced Migrations:
21. **025** - Knowledge base articles
    - Title, content, category
    - Author linkage (user FK)
    - Publication status, view counter
    - Timestamps (created_at, updated_at)
    - Indexes: category, author_id, is_published

22. **026** - Activity log
    - Audit trail for system events
    - User/entity tracking

23. **027** - Comments
    - Collaborative feedback on results

24. **028** - Voice execution status fields
    - Enhanced status tracking

25. **029** - Review status to validation results
    - Human validation workflow status

### Key Features:
- UUID primary keys for all entities
- PostgreSQL-specific features (JSONB, arrays)
- Foreign key relationships (referential integrity)
- Comprehensive indexing for query performance
- Timestamps with UTC timezone
- Default values for metadata fields

---

## 5. CONFIGURATION MANAGEMENT

### 5.1 Application Configuration

**Location**: `backend/api/config.py`
**Type**: Pydantic BaseSettings
**Source**: Environment variables

#### Configuration Sections:

**Database**:
- DATABASE_URL, READ_REPLICA_URL
- Connection pool settings (size, overflow, timeout, recycle)
- Host, port, credentials

**Redis**:
- REDIS_URL, host, port, password
- Database selection
- Connection pool size
- Cache TTL

**JWT Authentication**:
- JWT_SECRET_KEY (required, min 16 chars)
- JWT_ALGORITHM (HS256)
- Token expiration (30 min access, 14 day refresh)
- Password hashing rounds (12)

**SoundHound Voice AI**:
- SOUNDHOUND_API_KEY (required)
- SOUNDHOUND_CLIENT_ID (required)
- SOUNDHOUND_ENDPOINT
- Timeout (10s default)
- Max retries (3 default)

**AWS Configuration**:
- AWS_ACCESS_KEY_ID (required)
- AWS_SECRET_ACCESS_KEY (required)
- AWS_REGION (default: us-east-1)
- AWS_S3_BUCKET (for artifacts)
- S3 object expiration (90 days)

**Email Reporting**:
- REPORT_EMAIL_RECIPIENTS (list)
- REPORT_EMAIL_SENDER
- SMTP settings (host, port, user, pass, TLS)
- Timeout settings

**Application**:
- ENVIRONMENT (development/staging/production)
- APP_NAME, APP_VERSION
- LOG_LEVEL
- DEBUG mode
- TENANCY_MODE (single_tenant/soft_multi_tenant)

**Auto-scaling**:
- ENABLE_AUTO_SCALING
- MIN_WORKERS, MAX_WORKERS
- Target tasks per worker
- Scale-down threshold
- Cooldown period
- Queue name monitored

**Regression Automation**:
- ENABLE_AUTO_REGRESSION
- REGRESSION_SUITE_IDS (list of test suite UUIDs)

**Execution**:
- EXECUTION_CPU_LIMIT_PERCENT (85% default)
- EXECUTION_MEMORY_LIMIT_MB (2048 MB default)

**Webhook Security**:
- GITHUB_WEBHOOK_SECRET
- GITLAB_WEBHOOK_SECRET
- JENKINS_WEBHOOK_SECRET

**API Server**:
- API_HOST, API_PORT
- API_TIMEOUT
- FRONTEND_URL
- ALLOWED_ORIGINS (CORS)

**Validation**:
- VALIDATION_ACCURACY_THRESHOLD (0.997)
- SIMILARITY_THRESHOLD (0.85)
- ENABLE_HUMAN_VALIDATION
- TEST_EXECUTION_TIMEOUT (300s)
- MAX_CONCURRENT_TESTS (10)
- TEST_RESULT_RETENTION_DAYS (90)

### 5.2 Integration Configuration

**Location**: `config/integrations.demo.json`
**Format**: JSON with environment variable placeholders

**Structure**:
```json
{
  "version": "1.0",
  "integrations": {
    "github": {
      "enabled": boolean,
      "token": "${GITHUB_TOKEN}",
      "repo_owner": string,
      "repo_name": string,
      "features": {
        "commit_status": { enabled, context, auto_update },
        "issue_creation": { enabled, on_failure, labels, assignees, auto_close_on_success },
        "webhooks": { enabled, events, trigger_tests_on }
      }
    },
    "jira": {
      "enabled": boolean,
      "email": "${JIRA_EMAIL}",
      "api_token": "${JIRA_API_TOKEN}",
      "base_url": string,
      "project": string,
      "features": {
        "issue_creation": { enabled, on_critical_failure, issue_type, priority_mapping },
        "issue_updates": { enabled, auto_close_on_fix, add_comment_on_retest }
      }
    },
    "slack": {
      "enabled": boolean,
      "webhook_url": "${SLACK_WEBHOOK_URL}",
      "default_channel": string,
      "username": string,
      "icon_emoji": string,
      "features": {
        "test_run_notifications": { enabled, notify_on, include_metrics },
        "defect_alerts": { enabled, channel_override, mention_team },
        "system_alerts": { enabled, severity_threshold }
      },
      "notification_rules": {
        "success_threshold": float,
        "notify_on_regression": boolean,
        "batch_notifications": boolean
      }
    }
  },
  "notification_routing": {
    "test_run_complete": { github, slack, jira },
    "test_failure": { github, slack, jira },
    "critical_failure": { github, slack, jira },
    "regression_detected": { github, slack, jira }
  },
  "demo_metadata": {
    "setup_date": string,
    "demo_repository": URL,
    "jira_project_url": URL,
    "slack_workspace": string,
    "test_data": { sample IDs and values }
  }
}
```

---

## 6. SERVICE ARCHITECTURE

### 6.1 Key Services

**Voice Execution Service** (`services/voice_execution_service.py`):
- Orchestrates voice test execution
- Integrates with Houndify client
- Handles TTS (text-to-speech) for test input
- Audio file management

**Validation Service** (`services/validation_service.py`):
- Validates test results against expected outcomes
- Runs multiple validators (intent, entity, semantic, response time)
- Confidence score aggregation
- Review status determination

**Webhook Service** (`services/webhook_service.py`):
- Signature verification for CI/CD webhooks
- Event routing and dispatch
- Provider-specific handling

**Regression Suite Executor** (`services/regression_suite_executor.py`):
- Executes regression test suites
- Tracks test execution metrics
- Trigger context handling

**Dashboard Service** (`services/dashboard_service.py`):
- Real-time metrics aggregation
- Test run statistics
- Trend analysis

**Orchestration Service** (`services/orchestration_service.py`):
- Coordinates multi-service workflows
- Task chaining and execution

---

## 7. SECURITY & AUTHENTICATION

### Webhook Signature Verification:
- GitHub: HMAC-SHA256 (x-hub-signature-256)
- GitLab: Token comparison (x-gitlab-token)
- Jenkins: HMAC signature verification
- Constant-time comparison (timing attack resistant)

### API Authentication:
- JWT tokens (HS256)
- Refresh token rotation
- Configurable expiration

### Integration Credentials:
- Environment variable storage
- API tokens for GitHub, Jira, Slack
- Webhook secrets for CI/CD providers

---

## 8. MONITORING & ALERTING

### Prometheus Metrics:
- Test execution success rate
- Queue depth monitoring
- API response latency (P95)
- Custom business metrics

### Alert Rules:
1. **LowSuccessRate** (< 95% for 5 min) → Warning
2. **HighQueueDepth** (> 1000 for 2 min) → Critical
3. **HighResponseLatency** (P95 > 5s for 5 min) → Critical

### Grafana Dashboards:
- System overview
- Performance metrics
- Quality metrics

---

## 9. DEPLOYMENT CONFIGURATION

### Dockerfile Locations:
- Backend: `backend/Dockerfile`
- Frontend: `frontend/Dockerfile`

### Environment Setup:
- Docker Compose for local development
- Production-ready configuration
- Health checks for all services
- Dependency management (service ordering)

### Volume Management:
- PostgreSQL data: `postgres_data:/var/lib/postgresql/data`
- Redis data: `redis_data:/data`
- RabbitMQ data: `rabbitmq_data:/var/lib/rabbitmq`
- MinIO storage: `minio_data:/data`
- Prometheus metrics: `prometheus_data:/prometheus`
- Grafana data: `grafana_data:/var/lib/grafana`

---

## 10. INTEGRATION FLOW DIAGRAMS

### Test Execution Flow:
```
Test Run Request
    ↓
Celery Task (execute_test_batch)
    ↓
For each test case:
  ├→ Audio Generation (TTS)
  ├→ Voice AI Call (Houndify)
  ├→ Result Capture
  └→ Execution Recording
    ↓
Chord Callback (finalize_batch_execution)
    ↓
Statistics Update
    ↓
[Optional] GitHub Status Update
[Optional] Slack Notification
[Optional] Jira Issue Creation
```

### Validation Flow:
```
Execution Complete
    ↓
Validation Task
    ↓
Fetch Expected Outcome
    ↓
Run Validators
    ├→ Intent Validator
    ├→ Entity Validator
    ├→ Semantic Validator
    └→ Response Time Validator
    ↓
Aggregate Confidence Score
    ↓
Determine Review Status
    ├→ auto_pass (high confidence)
    └→ manual_review (human needed)
    ↓
[If manual review] → Queue for Human Validator
```

### Webhook Processing Flow:
```
Incoming Webhook (GitHub/GitLab/Jenkins)
    ↓
Identify Provider (from headers)
    ↓
Verify Signature (HMAC/Token)
    ├→ Valid: Continue
    └→ Invalid: 401 Unauthorized
    ↓
Parse Payload (JSON)
    ↓
Dispatch Event Handler
    ├→ GitHub: Commit status/push detection
    ├→ GitLab: MR/push handling
    └→ Jenkins: Custom event handling
    ↓
[Optional] Auto-trigger Regression Suite
[Optional] Post Status to GitHub
[Optional] Notify Slack
```

---

## 11. KEY METRICS & OBSERVABILITY

### Prometheus Metrics Collected:
- `test_executions_total`: Total test executions (labeled by result)
- `api_response_time_seconds`: API response latency (histogram with buckets)
- `queue_depth`: Current job queue depth
- Custom business metrics (execution time, validation scores)

### Health Check Endpoints:
- Backend: `GET /health` (200 OK)
- Frontend: `GET /health` (200 OK)
- PostgreSQL: `pg_isready`
- Redis: `redis-cli ping`
- RabbitMQ: `rabbitmqctl status`
- Prometheus: `/-/healthy`

---

## 12. SUMMARY TABLE

| Component | Type | Status | Primary Purpose |
|-----------|------|--------|-----------------|
| Houndify | Voice AI API | Integrated | Speech recognition, NLU |
| GitHub | Webhook + API | Integrated | CI/CD status, issue mgmt |
| Slack | Webhook API | Integrated | Team notifications |
| Jira | REST API | Integrated | Defect tracking |
| PostgreSQL | Database | Running | Primary data store |
| Redis | Cache/Queue | Running | Session cache, queue backend |
| RabbitMQ | Message Broker | Running | Task queue system |
| MinIO | Object Storage | Running | Audio file storage |
| Prometheus | Metrics | Running | Monitoring |
| Grafana | Visualization | Running | Dashboard/alerting |
| Celery | Task Queue | Running | Async job processing |

---

## 13. RECOMMENDATIONS

### Current Strengths:
1. Multi-provider integration support (GitHub, Jira, Slack)
2. Comprehensive monitoring stack (Prometheus + Grafana)
3. Scalable task queue with auto-scaling
4. Object storage integration for audio files
5. Webhook signature verification for security
6. Database migration infrastructure in place

### Areas for Enhancement:
1. Complete execute_voice_test_task helper functions (currently placeholders)
2. Add retry_failed_execution implementation
3. Implement missing validation task details
4. Configuration hot-reload for integrations
5. Circuit breaker patterns for external API calls
6. Rate limiting for webhook processing
7. Dead letter queues for failed tasks
8. Metrics export for integration API calls

