# Voice AI Testing Framework - Integration Contracts

## Table of Contents
- [Service Dependency Graph](#service-dependency-graph)
- [Dependency Types](#dependency-types)
- [API Contracts](#api-contracts)
- [Service Groups](#service-groups)
- [Data Flow](#data-flow)

---

## Service Dependency Graph

### Overview

The Voice AI Testing Framework is composed of multiple services that work together to provide automated voice testing capabilities. This document describes the dependencies and contracts between these services.

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Layer                        │
│  (React UI, API Clients)                                │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                    API Gateway                           │
│  (FastAPI, Authentication, Rate Limiting)               │
└─────────────────────┬───────────────────────────────────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Test Mgmt   │ │ Execution   │ │ Validation  │
│ Services    │ │ Services    │ │ Services    │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘
       │               │               │
       └───────────────┼───────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│              Infrastructure Layer                        │
│  (PostgreSQL, Redis, RabbitMQ, MinIO)                   │
└─────────────────────────────────────────────────────────┘
```

### Service Relationships

| Service | Depends On | Used By |
|---------|------------|---------|
| Test Case Service | Database, Cache | API Routes, Execution |
| Test Run Service | Database, Queue, Test Case | API Routes, Scheduler |
| Validation Service | Database, Cache, AI Provider | Execution Service |
| Execution Service | Queue, Telephony, Test Run | API Routes, Scheduler |
| Report Service | Database, Test Run, Validation | API Routes, Scheduler |
| Notification Service | Queue, Email/Slack | Execution, Validation |

---

## Dependency Types

### Required Dependencies

These dependencies are essential for the service to function. The service will fail to start without them.

| Service | Required Dependency | Purpose |
|---------|---------------------|---------|
| All Services | PostgreSQL | Primary data storage |
| All Services | Redis | Caching and session storage |
| Execution Service | RabbitMQ | Task queue for async execution |
| Validation Service | AI Provider API | Transcription validation |
| Notification Service | SMTP Server | Email notifications |

### Optional Dependencies

These dependencies enhance functionality but are not required for basic operation.

| Service | Optional Dependency | Purpose | Fallback Behavior |
|---------|---------------------|---------|-------------------|
| Report Service | MinIO | Report storage | Uses local filesystem |
| Notification Service | Slack API | Slack notifications | Logs warning, skips notification |
| Analytics Service | TimescaleDB | Time-series data | Uses PostgreSQL tables |
| Monitoring | Prometheus | Metrics collection | Service runs without metrics |

### Graceful Degradation

Services implement graceful degradation when optional dependencies are unavailable:

```python
# Example: Notification with optional Slack
class NotificationService:
    def send_notification(self, message: str, channels: List[str]):
        """Send notification to available channels."""
        for channel in channels:
            try:
                if channel == "slack" and self.slack_client:
                    self.slack_client.send(message)
                elif channel == "email":
                    self.email_client.send(message)  # Required
            except SlackUnavailable:
                logger.warning(f"Slack unavailable, skipping notification")
```

---

## API Contracts

### Request/Response Formats

All API endpoints use consistent JSON request and response formats.

#### Standard Success Response

```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "name": "string",
        "created_at": "ISO8601 datetime"
    },
    "message": "Optional success message",
    "request_id": "uuid"
}
```

#### Standard Error Response

```json
{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "Human-readable error message",
        "details": {}
    },
    "request_id": "uuid"
}
```

#### Paginated Response

```json
{
    "success": true,
    "data": [],
    "pagination": {
        "page": 1,
        "page_size": 20,
        "total_items": 100,
        "total_pages": 5
    }
}
```

### Service-to-Service Communication

#### Internal API Contract

Services communicate via internal APIs with the following contract:

```python
# Input Schema
class ServiceRequest:
    tenant_id: UUID      # Required for multi-tenancy
    user_id: UUID        # Authenticated user
    payload: dict        # Service-specific data
    correlation_id: str  # Request tracing

# Output Schema
class ServiceResponse:
    success: bool
    data: Optional[dict]
    error: Optional[str]
    correlation_id: str
```

#### Event Contract

Services emit events via RabbitMQ with the following structure:

```python
class Event:
    event_type: str       # e.g., "test_run.completed"
    timestamp: datetime
    tenant_id: UUID
    payload: dict
    metadata: dict        # trace_id, source_service
```

---

## Service Groups

### Core Services

These services implement the main business logic.

#### Test Management Group

| Service | Responsibility | API Base |
|---------|----------------|----------|
| Test Case Service | Manage test cases and variations | `/api/v1/test-cases` |
| Test Suite Service | Group test cases into suites | `/api/v1/test-suites` |
| Scenario Service | Define conversation scenarios | `/api/v1/scenarios` |

#### Execution Group

| Service | Responsibility | Queue |
|---------|----------------|-------|
| Execution Service | Orchestrate test execution | `test_execution` |
| Worker Service | Execute individual tests | `test_worker` |
| Scheduler Service | Schedule recurring tests | `scheduler` |

#### Validation Group

| Service | Responsibility | External Deps |
|---------|----------------|---------------|
| Transcription Validator | Validate speech-to-text | AI Provider |
| Intent Validator | Validate intent classification | AI Provider |
| Human Validation | Queue for human review | - |

### Infrastructure Services

These services provide foundational capabilities.

#### Database Services

| Service | Technology | Purpose |
|---------|------------|---------|
| Primary Database | PostgreSQL | Persistent storage |
| Cache | Redis | Session, rate limiting, caching |
| Queue | RabbitMQ | Async task processing |
| Object Storage | MinIO | Audio files, reports |

#### Monitoring Services

| Service | Technology | Purpose |
|---------|------------|---------|
| Metrics | Prometheus | Performance metrics |
| Dashboards | Grafana | Visualization |
| Alerting | Alertmanager | Alert routing |
| Logging | ELK Stack | Log aggregation |

---

## Data Flow

### Test Execution Pipeline

```
1. Request → API Gateway
   │
   ▼
2. Create Test Run → Test Run Service
   │
   ├── Validate input
   ├── Create test run record
   └── Queue execution tasks
   │
   ▼
3. Queue Tasks → RabbitMQ
   │
   ▼
4. Execute Tests → Worker Service
   │
   ├── Connect to telephony
   ├── Run conversation
   ├── Capture audio
   └── Store results
   │
   ▼
5. Validate Results → Validation Service
   │
   ├── Transcribe audio
   ├── Compare with expected
   ├── Calculate metrics
   └── Update test run
   │
   ▼
6. Notify Completion → Notification Service
   │
   ├── Send to Slack
   ├── Send email
   └── Trigger webhooks
```

### Report Generation Pipeline

```
1. Scheduled/Manual Request
   │
   ▼
2. Aggregate Data → Report Service
   │
   ├── Query test runs
   ├── Calculate statistics
   └── Format data
   │
   ▼
3. Generate Report → Report Generator
   │
   ├── Apply template
   ├── Render PDF/HTML
   └── Store in MinIO
   │
   ▼
4. Deliver Report → Delivery Service
   │
   ├── Send to recipients
   └── Store delivery record
```

### Validation Flow

```
1. Audio Input → Validation Service
   │
   ▼
2. Transcribe → AI Provider (ASR)
   │
   ▼
3. Compare → Validation Engine
   │
   ├── Word Error Rate (WER)
   ├── Character Error Rate (CER)
   └── Confidence Score
   │
   ▼
4. Decide → Validation Decision
   │
   ├── If confidence < threshold → Human Review
   └── Else → Auto Accept/Reject
   │
   ▼
5. Update → Database
   │
   └── Store validation result
```

---

## Contract Versioning

### API Versioning

- APIs are versioned via URL prefix: `/api/v1/`, `/api/v2/`
- Breaking changes require new major version
- Minor changes are backward compatible
- Deprecated endpoints include `Sunset` header

### Event Versioning

Events include schema version in metadata:

```json
{
    "event_type": "test_run.completed",
    "schema_version": "1.0",
    "payload": {}
}
```

---

## Error Handling Contracts

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `AUTH_INVALID_TOKEN` | 401 | Invalid or expired token |
| `AUTH_INSUFFICIENT_PERMISSIONS` | 403 | User lacks required role |
| `RESOURCE_NOT_FOUND` | 404 | Requested resource doesn't exist |
| `VALIDATION_ERROR` | 422 | Request validation failed |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

### Retry Policies

| Service | Retry Strategy | Max Retries |
|---------|----------------|-------------|
| Execution Service | Exponential backoff | 3 |
| Notification Service | Linear backoff | 5 |
| Report Service | Fixed interval | 2 |

---

## Health Check Contracts

### Service Health Response

```json
{
    "status": "healthy|degraded|unhealthy",
    "version": "1.0.0",
    "dependencies": {
        "database": "ok",
        "redis": "ok",
        "rabbitmq": "degraded"
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### Dependency Check Contract

Each service must implement:
- `/health` - Basic liveness
- `/ready` - Full readiness with dependencies
- `/metrics` - Prometheus metrics

---

## Security Contracts

### Authentication

All inter-service communication uses:
- JWT tokens for user context
- Service tokens for service-to-service
- Tenant ID in all requests

### Authorization

Services enforce:
- Role-based access control (RBAC)
- Resource ownership validation
- Tenant isolation

---

## Monitoring Contracts

### Required Metrics

All services must export:

| Metric | Type | Labels |
|--------|------|--------|
| `requests_total` | Counter | method, endpoint, status |
| `request_duration_seconds` | Histogram | method, endpoint |
| `errors_total` | Counter | type, service |

### Required Logs

All services must log:

| Event | Level | Required Fields |
|-------|-------|-----------------|
| Request received | INFO | request_id, user_id, endpoint |
| Request completed | INFO | request_id, status, duration_ms |
| Error occurred | ERROR | request_id, error_type, message |
