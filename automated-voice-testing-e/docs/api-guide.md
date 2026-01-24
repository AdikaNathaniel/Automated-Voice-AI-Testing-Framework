# API Integration Guide

**Voice AI Automated Testing Framework - API Documentation**

This guide provides comprehensive instructions for integrating with the Voice AI Testing API. Learn how to authenticate, make requests, handle responses, and integrate voice AI testing into your applications.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [Base URL and Versioning](#base-url-and-versioning)
4. [Common Patterns](#common-patterns)
5. [Endpoints](#endpoints)
6. [Error Handling](#error-handling)
7. [Pagination](#pagination)
8. [Rate Limiting](#rate-limiting)
9. [Code Examples](#code-examples)
10. [Best Practices](#best-practices)

---

## Getting Started

### Quick Start

To get started with the Voice AI Testing API:

1. **Register for an account** (or use existing credentials)
2. **Obtain an authentication token** via the login endpoint
3. **Make API requests** using the token in the Authorization header
4. **Handle responses** according to the standardized format

### Base Requirements

- **API Access**: Valid user account with API access
- **HTTPS**: All API requests must use HTTPS
- **JSON**: All request and response bodies use JSON format
- **Authentication**: JWT tokens required for protected endpoints

---

## Authentication

The API uses **JWT (JSON Web Token)** authentication. All protected endpoints require a valid JWT token in the Authorization header.

### Authentication Flow

```
1. Register (if new user) → POST /api/auth/register
2. Login → POST /api/auth/login
3. Receive access_token and refresh_token
4. Use access_token in Authorization header
5. Refresh token when expired → POST /api/auth/refresh
```

### 1. User Registration

Register a new user account.

**Endpoint**: `POST /api/auth/register`

**Request Body**:

```json
{
  "email": "user@example.com",
  "username": "testuser",
  "password": "SecurePassword123!",
  "full_name": "Test User"
}
```

**cURL Example**:

```bash
curl -X POST https://api.voiceai-testing.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "SecurePassword123!",
    "full_name": "Test User"
  }'
```

**Response** (201 Created):

```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "user@example.com",
    "username": "testuser",
    "full_name": "Test User",
    "created_at": "2025-10-25T10:00:00Z"
  },
  "message": "User registered successfully"
}
```

### 2. User Login

Authenticate and receive JWT tokens.

**Endpoint**: `POST /api/auth/login`

**Request Body**:

```json
{
  "username": "testuser",
  "password": "SecurePassword123!"
}
```

**cURL Example**:

```bash
curl -X POST https://api.voiceai-testing.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePassword123!"
  }'
```

**Response** (200 OK):

```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
      "id": 1,
      "email": "user@example.com",
      "username": "testuser",
      "full_name": "Test User"
    }
  },
  "message": "Login successful"
}
```

### 3. Using Bearer Tokens

Include the access token in the `Authorization` header for all protected endpoints:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**cURL Example**:

```bash
curl -X GET https://api.voiceai-testing.com/api/test-cases \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

### 4. Token Refresh

Refresh an expired access token using the refresh token.

**Endpoint**: `POST /api/auth/refresh`

**Request Body**:

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (200 OK):

```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

---

## Base URL and Versioning

### Base URL

All API endpoints are relative to the base URL:

```
https://api.voiceai-testing.com
```

For local development:

```
http://localhost:8000
```

### API Versioning

The API is versioned via URL path prefix:

```
https://api.voiceai-testing.com/api/v1/...
```

Currently, all endpoints use the `/api` prefix without explicit version numbers. Future versions will use `/api/v2`, etc.

### Complete Endpoint Format

```
{base_url}/api/{resource}
```

Example:

```
https://api.voiceai-testing.com/api/test-cases
```

---

## Common Patterns

### Standard Request Headers

All requests should include:

```
Content-Type: application/json
Authorization: Bearer {your_access_token}
```

### Standard Response Format

All responses follow a consistent structure:

#### Success Response

```json
{
  "success": true,
  "data": { ... },
  "message": "Optional success message",
  "request_id": "uuid-for-tracing"
}
```

#### Error Response

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { ... }
  },
  "request_id": "uuid-for-tracing"
}
```

#### Paginated Response

```json
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "page_size": 10,
    "total_items": 100,
    "total_pages": 10
  }
}
```

---

## Endpoints

### Test Cases

#### List Test Cases

Get a paginated list of test cases.

**Endpoint**: `GET /api/test-cases`

**Query Parameters**:
- `page` (integer, optional): Page number (default: 1)
- `page_size` (integer, optional): Items per page (default: 10, max: 100)
- `search` (string, optional): Search by name or description
- `status` (string, optional): Filter by status (active, archived)

**Request Example**:

```bash
curl -X GET "https://api.voiceai-testing.com/api/test-cases?page=1&page_size=20" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

**Response** (200 OK):

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Check Weather Query",
      "description": "Test weather information query",
      "expected_intent": "WeatherQuery",
      "test_phrases": [
        "What's the weather in New York?",
        "Tell me the weather forecast"
      ],
      "status": "active",
      "created_at": "2025-10-25T10:00:00Z",
      "updated_at": "2025-10-25T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 45,
    "total_pages": 3
  }
}
```

#### Create Test Case

Create a new test case.

**Endpoint**: `POST /api/test-cases`

**Request Body**:

```json
{
  "name": "Hotel Booking Test",
  "description": "Test hotel booking conversation",
  "expected_intent": "BookHotel",
  "test_phrases": [
    "Book a hotel in San Francisco",
    "I need a room for tonight"
  ],
  "validation_rules": {
    "required_entities": ["location", "date"],
    "max_duration_seconds": 30
  }
}
```

**cURL Example**:

```bash
curl -X POST https://api.voiceai-testing.com/api/test-cases \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Hotel Booking Test",
    "description": "Test hotel booking conversation",
    "expected_intent": "BookHotel",
    "test_phrases": ["Book a hotel in San Francisco"]
  }'
```

**Response** (201 Created):

```json
{
  "success": true,
  "data": {
    "id": 46,
    "name": "Hotel Booking Test",
    "description": "Test hotel booking conversation",
    "expected_intent": "BookHotel",
    "test_phrases": [
      "Book a hotel in San Francisco",
      "I need a room for tonight"
    ],
    "status": "active",
    "created_at": "2025-10-25T11:00:00Z",
    "updated_at": "2025-10-25T11:00:00Z"
  },
  "message": "Test case created successfully"
}
```

#### Get Test Case by ID

Get details of a specific test case.

**Endpoint**: `GET /api/test-cases/{id}`

**Request Example**:

```bash
curl -X GET https://api.voiceai-testing.com/api/test-cases/1 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response** (200 OK):

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Check Weather Query",
    "description": "Test weather information query",
    "expected_intent": "WeatherQuery",
    "test_phrases": [
      "What's the weather in New York?",
      "Tell me the weather forecast"
    ],
    "validation_rules": {
      "required_entities": ["location"],
      "max_duration_seconds": 20
    },
    "status": "active",
    "created_at": "2025-10-25T10:00:00Z",
    "updated_at": "2025-10-25T10:00:00Z"
  }
}
```

#### Update Test Case

Update an existing test case.

**Endpoint**: `PUT /api/test-cases/{id}`

**Request Body**:

```json
{
  "name": "Updated Test Name",
  "description": "Updated description",
  "status": "active"
}
```

**Response** (200 OK):

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Updated Test Name",
    "description": "Updated description",
    "status": "active",
    "updated_at": "2025-10-25T12:00:00Z"
  },
  "message": "Test case updated successfully"
}
```

#### Delete Test Case

Delete a test case (soft delete).

**Endpoint**: `DELETE /api/test-cases/{id}`

**Response** (200 OK):

```json
{
  "success": true,
  "message": "Test case deleted successfully"
}
```

### Test Runs

#### Create Test Run

Execute a test run from test cases.

**Endpoint**: `POST /api/test-runs`

**Request Body**:

```json
{
  "name": "Nightly Regression Test",
  "test_case_ids": [1, 2, 3, 4, 5],
  "configuration": {
    "environment": "staging",
    "parallel_execution": true,
    "max_retries": 2
  }
}
```

**cURL Example**:

```bash
curl -X POST https://api.voiceai-testing.com/api/test-runs \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Nightly Regression Test",
    "test_case_ids": [1, 2, 3, 4, 5]
  }'
```

**Response** (201 Created):

```json
{
  "success": true,
  "data": {
    "id": 101,
    "name": "Nightly Regression Test",
    "status": "queued",
    "total_tests": 5,
    "completed_tests": 0,
    "passed_tests": 0,
    "failed_tests": 0,
    "created_at": "2025-10-25T13:00:00Z"
  },
  "message": "Test run created and queued for execution"
}
```

#### Get Test Run Status

Check the status of a running test.

**Endpoint**: `GET /api/test-runs/{id}`

**Response** (200 OK):

```json
{
  "success": true,
  "data": {
    "id": 101,
    "name": "Nightly Regression Test",
    "status": "running",
    "total_tests": 5,
    "completed_tests": 3,
    "passed_tests": 2,
    "failed_tests": 1,
    "progress_percentage": 60,
    "started_at": "2025-10-25T13:01:00Z",
    "estimated_completion": "2025-10-25T13:05:00Z"
  }
}
```

#### List Test Runs

Get a paginated list of test runs.

**Endpoint**: `GET /api/test-runs`

**Query Parameters**:
- `page` (integer): Page number
- `page_size` (integer): Items per page
- `status` (string): Filter by status (queued, running, completed, failed)

**Response** (200 OK):

```json
{
  "success": true,
  "data": [
    {
      "id": 101,
      "name": "Nightly Regression Test",
      "status": "completed",
      "total_tests": 5,
      "passed_tests": 4,
      "failed_tests": 1,
      "created_at": "2025-10-25T13:00:00Z",
      "completed_at": "2025-10-25T13:04:30Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 10,
    "total_items": 25,
    "total_pages": 3
  }
}
```

### Test Suites

#### Create Test Suite

Organize test cases into reusable suites.

**Endpoint**: `POST /api/test-suites`

**Request Body**:

```json
{
  "name": "Smoke Test Suite",
  "description": "Quick smoke tests for critical functionality",
  "test_case_ids": [1, 2, 3]
}
```

**Response** (201 Created):

```json
{
  "success": true,
  "data": {
    "id": 10,
    "name": "Smoke Test Suite",
    "description": "Quick smoke tests for critical functionality",
    "test_case_count": 3,
    "created_at": "2025-10-25T14:00:00Z"
  },
  "message": "Test suite created successfully"
}
```

#### List Test Suites

**Endpoint**: `GET /api/test-suites`

**Response** (200 OK):

```json
{
  "success": true,
  "data": [
    {
      "id": 10,
      "name": "Smoke Test Suite",
      "description": "Quick smoke tests for critical functionality",
      "test_case_count": 3,
      "created_at": "2025-10-25T14:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 10,
    "total_items": 5,
    "total_pages": 1
  }
}
```

---

### Regressions

Regression testing endpoints help detect and manage performance/behavior changes across test runs.

#### List Regressions

Get detected regressions with filtering and pagination.

**Endpoint**: `GET /api/v1/regressions`

**Query Parameters**:
- `suite_id` (UUID, optional): Filter by test suite
- `status` (string, optional): Filter by status (unresolved, resolved)
- `skip` (integer, optional): Offset for pagination (default: 0)
- `limit` (integer, optional): Number of results (default: 50)

**Response** (200 OK):

```json
{
  "summary": {
    "total_regressions": 3,
    "status_regressions": 2,
    "metric_regressions": 1
  },
  "items": [
    {
      "script_id": "550e8400-e29b-41d4-a716-446655440000",
      "category": "status",
      "detail": {
        "baseline_status": "passed",
        "current_status": "failed"
      },
      "regression_detected_at": "2025-12-26T10:00:00Z"
    }
  ]
}
```

#### Get Regression Comparison

Compare baseline and current execution for a scenario script.

**Endpoint**: `GET /api/v1/regressions/{script_id}/comparison`

**Response** (200 OK):

```json
{
  "script_id": "550e8400-e29b-41d4-a716-446655440000",
  "baseline": {
    "status": "passed",
    "metrics": {
      "pass_rate": {"value": 0.95, "threshold": null, "unit": null}
    },
    "media_uri": null
  },
  "current": {
    "status": "failed",
    "metrics": {
      "pass_rate": {"value": 0.82, "threshold": null, "unit": null}
    },
    "media_uri": null
  },
  "differences": [
    {
      "metric": "pass_rate",
      "baseline_value": 0.95,
      "current_value": 0.82,
      "delta": -0.13,
      "delta_pct": -13.68
    }
  ]
}
```

#### Approve Baseline

Approve a new baseline for a scenario script. Previous baseline is archived to history.

**Endpoint**: `POST /api/v1/regressions/{script_id}/baseline`

**Request Body**:

```json
{
  "status": "passed",
  "metrics": {"pass_rate": 0.99, "latency_ms": 120},
  "note": "Approved after investigation - new behavior is expected"
}
```

**Response** (200 OK):

```json
{
  "script_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "passed",
  "metrics": {"pass_rate": 0.99, "latency_ms": 120},
  "version": 2,
  "approved_at": "2025-12-26T12:00:00Z",
  "approved_by": "user-uuid",
  "note": "Approved after investigation - new behavior is expected"
}
```

#### Get Baseline History

Retrieve the version history of baselines for a scenario script.

**Endpoint**: `GET /api/v1/regressions/{script_id}/baselines`

**Response** (200 OK):

```json
{
  "script_id": "550e8400-e29b-41d4-a716-446655440000",
  "history": [
    {
      "version": 2,
      "status": "passed",
      "metrics": {"pass_rate": 0.99},
      "approved_at": "2025-12-26T12:00:00Z",
      "approved_by": "user-uuid",
      "note": "Updated baseline after bug fix"
    },
    {
      "version": 1,
      "status": "passed",
      "metrics": {"pass_rate": 0.95},
      "approved_at": "2025-12-01T10:00:00Z",
      "approved_by": "user-uuid",
      "note": "Initial baseline"
    }
  ]
}
```

---

## Error Handling

### HTTP Status Codes

The API uses standard HTTP status codes:

| Status Code | Meaning | Description |
|-------------|---------|-------------|
| 200 | OK | Request succeeded |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### Error Response Format

All errors follow the standard error response format:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "field": "email",
      "reason": "Invalid email format"
    }
  },
  "request_id": "abc-123-def-456"
}
```

### Common Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `VALIDATION_ERROR` | 422 | Invalid request data |
| `UNAUTHORIZED` | 401 | Invalid or missing token |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `DUPLICATE_ENTRY` | 400 | Resource already exists |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

### Example Error Responses

#### Validation Error (422)

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": {
      "email": ["Email is required"],
      "password": ["Password must be at least 8 characters"]
    }
  }
}
```

#### Unauthorized Error (401)

```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired token",
    "details": {}
  }
}
```

#### Not Found Error (404)

```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Test case with ID 999 not found",
    "details": {
      "resource": "test_case",
      "id": 999
    }
  }
}
```

---

## Pagination

List endpoints support pagination via query parameters.

### Pagination Parameters

- `page` (integer, default: 1): Page number to retrieve
- `page_size` (integer, default: 10, max: 100): Number of items per page

### Pagination Response

```json
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "page": 2,
    "page_size": 10,
    "total_items": 45,
    "total_pages": 5,
    "has_next": true,
    "has_previous": true
  }
}
```

### Example Request

```bash
curl -X GET "https://api.voiceai-testing.com/api/test-cases?page=2&page_size=20" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Rate Limiting

The API implements rate limiting to ensure fair usage.

### Rate Limits

- **Authenticated Users**: 1000 requests per hour
- **Unauthenticated Endpoints**: 100 requests per hour

### Rate Limit Headers

Response headers include rate limit information:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1635174000
```

### Rate Limit Exceeded Response (429)

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 3600 seconds.",
    "details": {
      "limit": 1000,
      "reset_at": "2025-10-25T15:00:00Z"
    }
  }
}
```

---

## Code Examples

### Python Example

```python
import requests

class VoiceAITestingClient:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.token = None
        self.login(username, password)

    def login(self, username, password):
        """Authenticate and store token"""
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        data = response.json()
        self.token = data["data"]["access_token"]

    def get_headers(self):
        """Get headers with authentication"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def create_test_case(self, name, description, expected_intent, test_phrases):
        """Create a new test case"""
        response = requests.post(
            f"{self.base_url}/api/test-cases",
            headers=self.get_headers(),
            json={
                "name": name,
                "description": description,
                "expected_intent": expected_intent,
                "test_phrases": test_phrases
            }
        )
        response.raise_for_status()
        return response.json()["data"]

    def run_tests(self, test_case_ids):
        """Create and execute a test run"""
        response = requests.post(
            f"{self.base_url}/api/test-runs",
            headers=self.get_headers(),
            json={"test_case_ids": test_case_ids}
        )
        response.raise_for_status()
        return response.json()["data"]

# Usage
client = VoiceAITestingClient(
    "https://api.voiceai-testing.com",
    "testuser",
    "SecurePassword123!"
)

# Create test case
test_case = client.create_test_case(
    name="Weather Query Test",
    description="Test weather information queries",
    expected_intent="WeatherQuery",
    test_phrases=["What's the weather?", "Tell me the forecast"]
)
print(f"Created test case: {test_case['id']}")

# Run tests
test_run = client.run_tests([test_case["id"]])
print(f"Test run started: {test_run['id']}")
```

### JavaScript Example

```javascript
class VoiceAITestingClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
    this.token = null;
  }

  async login(username, password) {
    const response = await fetch(`${this.baseUrl}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });

    const data = await response.json();
    if (!data.success) throw new Error(data.error.message);

    this.token = data.data.access_token;
    return data.data;
  }

  getHeaders() {
    return {
      'Authorization': `Bearer ${this.token}`,
      'Content-Type': 'application/json'
    };
  }

  async createTestCase(testCaseData) {
    const response = await fetch(`${this.baseUrl}/api/test-cases`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(testCaseData)
    });

    const data = await response.json();
    if (!data.success) throw new Error(data.error.message);

    return data.data;
  }

  async listTestCases(page = 1, pageSize = 10) {
    const response = await fetch(
      `${this.baseUrl}/api/test-cases?page=${page}&page_size=${pageSize}`,
      { headers: this.getHeaders() }
    );

    const data = await response.json();
    if (!data.success) throw new Error(data.error.message);

    return data;
  }
}

// Usage
const client = new VoiceAITestingClient('https://api.voiceai-testing.com');

await client.login('testuser', 'SecurePassword123!');

const testCase = await client.createTestCase({
  name: 'Weather Query Test',
  description: 'Test weather information queries',
  expected_intent: 'WeatherQuery',
  test_phrases: ['What\'s the weather?', 'Tell me the forecast']
});

console.log('Created test case:', testCase.id);
```

---

## Best Practices

### 1. Always Use HTTPS

Never send API requests over unencrypted HTTP in production:

```
✓ https://api.voiceai-testing.com/api/test-cases
✗ http://api.voiceai-testing.com/api/test-cases
```

### 2. Store Tokens Securely

- Never hardcode tokens in source code
- Use environment variables or secure vaults
- Implement token refresh logic
- Clear tokens on logout

### 3. Handle Errors Gracefully

Always check the `success` field and handle errors:

```python
response = requests.post(url, json=data)
result = response.json()

if not result["success"]:
    error = result["error"]
    print(f"Error {error['code']}: {error['message']}")
    # Handle error appropriately
else:
    data = result["data"]
    # Process successful response
```

### 4. Implement Retry Logic

For transient errors (500, 503), implement exponential backoff:

```python
import time

def make_request_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code >= 500 and attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                time.sleep(wait_time)
            else:
                raise
```

### 5. Respect Rate Limits

- Monitor rate limit headers
- Implement client-side rate limiting
- Handle 429 responses gracefully

### 6. Use Pagination for Large Lists

Always paginate when fetching large lists:

```python
def get_all_test_cases(client):
    all_cases = []
    page = 1

    while True:
        response = client.list_test_cases(page=page, page_size=100)
        all_cases.extend(response["data"])

        if not response["pagination"]["has_next"]:
            break
        page += 1

    return all_cases
```

### 7. Validate Request Data

Always validate data before sending requests:

```python
def create_test_case(name, test_phrases):
    # Validate before sending
    if not name or len(name) < 3:
        raise ValueError("Name must be at least 3 characters")

    if not test_phrases or len(test_phrases) == 0:
        raise ValueError("At least one test phrase is required")

    # Make request
    return client.create_test_case(name=name, test_phrases=test_phrases)
```

### 8. Use Request IDs for Debugging

When reporting issues, include the `request_id` from error responses:

```python
try:
    response = client.create_test_case(data)
except Exception as e:
    error_data = e.response.json()
    print(f"Error occurred. Request ID: {error_data.get('request_id')}")
    # Include request_id when contacting support
```

---

## Super Admin Endpoints

The following endpoints are only accessible to users with the `super_admin` role.

### Organizations

#### List Organizations

**Endpoint**: `GET /api/v1/organizations`

**Query Parameters**:
- `page` (integer, optional): Page number (default: 1)
- `page_size` (integer, optional): Items per page (default: 10)

**Response** (200 OK):

```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Acme Corporation",
      "admin_email": "admin@acme.com",
      "admin_username": "acme_admin",
      "is_active": true,
      "member_count": 15,
      "settings": {},
      "created_at": "2025-12-26T10:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10
}
```

#### Create Organization

**Endpoint**: `POST /api/v1/organizations`

**Request Body**:

```json
{
  "name": "Acme Corporation",
  "admin_email": "admin@acme.com",
  "admin_username": "acme_admin",
  "admin_full_name": "John Admin"
}
```

**Response** (201 Created):

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Acme Corporation",
  "admin_email": "admin@acme.com",
  "is_active": true,
  "created_at": "2025-12-26T10:00:00Z"
}
```

#### Update Organization

**Endpoint**: `PUT /api/v1/organizations/{org_id}`

**Request Body**:

```json
{
  "name": "Acme Corp Updated",
  "is_active": true
}
```

#### Delete Organization

**Endpoint**: `DELETE /api/v1/organizations/{org_id}`

**Response** (204 No Content)

### User Management

#### Get User Statistics

**Endpoint**: `GET /api/v1/users/stats`

**Response** (200 OK):

```json
{
  "total_users": 150,
  "active_users": 142,
  "inactive_users": 8,
  "users_by_role": {
    "admin": 5,
    "qa_lead": 12,
    "validator": 45,
    "viewer": 88
  },
  "users_by_organization": 120,
  "individual_users": 30
}
```

#### List Users

**Endpoint**: `GET /api/v1/users`

**Query Parameters**:
- `page` (integer): Page number
- `page_size` (integer): Items per page
- `search` (string): Search by email/username/name
- `role` (string): Filter by role
- `is_active` (boolean): Filter by active status
- `organization_id` (UUID): Filter by organization

**Response** (200 OK):

```json
{
  "items": [
    {
      "id": "user-uuid",
      "email": "user@example.com",
      "username": "johndoe",
      "full_name": "John Doe",
      "role": "qa_lead",
      "is_active": true,
      "tenant_id": "org-uuid",
      "organization_name": "Acme Corp",
      "last_login_at": "2025-12-26T10:00:00Z",
      "created_at": "2025-12-01T10:00:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 20
}
```

#### Create User

**Endpoint**: `POST /api/v1/users`

**Request Body**:

```json
{
  "email": "newuser@example.com",
  "username": "newuser",
  "password": "SecurePassword123!",
  "full_name": "New User",
  "role": "validator",
  "is_active": true,
  "tenant_id": "org-uuid"
}
```

#### Update User

**Endpoint**: `PUT /api/v1/users/{user_id}`

**Request Body**:

```json
{
  "full_name": "Updated Name",
  "role": "qa_lead",
  "tenant_id": "new-org-uuid"
}
```

#### Delete User

**Endpoint**: `DELETE /api/v1/users/{user_id}`

**Response** (204 No Content)

#### Reset User Password

**Endpoint**: `POST /api/v1/users/{user_id}/reset-password`

**Request Body**:

```json
{
  "new_password": "NewSecurePassword123!"
}
```

#### Activate/Deactivate User

**Endpoint**: `POST /api/v1/users/{user_id}/activate`
**Endpoint**: `POST /api/v1/users/{user_id}/deactivate`

**Response** (200 OK): Returns updated user object

---

## Multi-Tenancy

The Voice AI Testing Framework supports multi-tenancy for data isolation between organizations.

### How It Works

1. **Organizations** are created by super admins
2. **Users** can belong to an organization (via `tenant_id`)
3. All data (scenarios, test suites, defects, etc.) is isolated by `tenant_id`
4. Users without an organization operate as their own tenant (individual users)

### Role Hierarchy

| Role | Description |
|------|-------------|
| `super_admin` | Platform-wide admin, manages organizations and users |
| `org_admin` | Organization-level admin |
| `admin` | Tenant admin with full access within tenant |
| `qa_lead` | Can create and manage test resources |
| `validator` | Can perform validation tasks |
| `viewer` | Read-only access |

### Data Isolation

All tenant-scoped endpoints automatically filter data by the current user's tenant:
- Scenarios and test suites
- Test executions and results
- Defects and edge cases
- Configurations and knowledge base articles
- LLM provider configurations

---

## Additional Resources

- **API Reference**: Full endpoint documentation at https://api.voiceai-testing.com/api/docs
- **OpenAPI Specification**: https://api.voiceai-testing.com/api/openapi.json
- **Developer Setup Guide**: See `docs/setup-guide.md`
- **Support**: support@voiceai-testing.com

---

**Happy Integrating!** 🚀

For questions or issues, please contact our support team or create an issue in our GitHub repository.
