# Voice AI Automated Testing Framework - Demo Script

This demo script guides you through showcasing the capabilities of the Voice AI Automated Testing Framework. Follow these steps to demonstrate the platform's key features including test case management, multilingual support, test execution, and result analysis.

## Table of Contents

1. [Preparation](#preparation)
2. [Demo Environment Setup](#demo-environment-setup)
3. [Demo Execution Steps](#demo-execution-steps)
4. [Feature Showcase](#feature-showcase)
5. [Troubleshooting](#troubleshooting)

---

## Preparation

### Prerequisites Checklist

Before starting the demo, ensure the following are ready:

- [ ] Docker and Docker Compose installed
- [ ] Git repository cloned locally
- [ ] Python 3.12+ virtual environment activated
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Demo data loader script available
- [ ] Browser ready for UI demonstration

### Estimated Demo Duration

- **Quick Demo**: 10-15 minutes (core features only)
- **Full Demo**: 25-30 minutes (all features with Q&A)
- **Technical Deep Dive**: 45-60 minutes (architecture + features)

---

## Demo Environment Setup

### 1. Start Infrastructure Services

Start Docker Compose services for PostgreSQL, Redis, and pgAdmin:

```bash
# Navigate to project root
cd /path/to/automated-testing

# Start Docker Compose services
docker-compose up -d

# Verify services are running
docker-compose ps
```

**Expected Output**: You should see services running:
- `postgres` (port 5432)
- `redis` (port 6379)
- `pgadmin` (port 5050)

### 2. Run Database Migrations

Apply all database migrations to set up the schema:

```bash
# Run Alembic migrations
venv/bin/alembic upgrade head

# Verify current revision
venv/bin/alembic current
```

**Expected Output**: Current revision matches the latest migration in `alembic/versions/`

### 3. Load Demo Data

Load the comprehensive demo test suite with 10 diverse test cases:

```bash
# Load demo data
cd backend
python -m scripts.load_demo_data
```

**Expected Output**:
```
✅ Demo data loaded successfully!
   Suite: Voice AI Demo Test Suite (ID: <uuid>)
   Test Cases: 10 created
   User: <uuid>
```

The demo data includes:
- **10 test cases** across 7 categories (navigation, media, climate, phone, information, safety, messaging)
- **5 languages**: English, Spanish, French, German, Japanese
- **3 test types**: voice_command, multi_turn, edge_case

### 4. Start Backend Server

Launch the FastAPI backend server:

```bash
# Start backend server (from backend directory)
venv/bin/uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
```

**API Documentation**: Navigate to `http://localhost:8000/docs` to see interactive Swagger UI.

### 5. Start Frontend (Optional)

If demonstrating the UI:

```bash
# Navigate to frontend directory
cd frontend

# Start development server
npm run dev
```

**Expected Output**: Frontend running on `http://localhost:5173`

---

## Demo Execution Steps

### Step 1: Introduction (2 minutes)

**Talking Points**:
- Framework purpose: Automated testing for voice AI systems via realistic phone call simulations
- Key capabilities: Multi-language support, test orchestration, validation, reporting
- Target users: QA teams, voice AI developers, product managers

### Step 2: API Overview (3 minutes)

#### 2.1 Show Interactive API Documentation

Navigate to `http://localhost:8000/docs` in your browser.

**Demonstrate**:
- Swagger UI with all available endpoints
- Organized by feature: Authentication, Test Cases, Test Suites, Test Runs
- Standardized response models

**Talking Points**:
- RESTful API design
- JWT authentication
- OpenAPI/Swagger specification auto-generated

#### 2.2 Test API Health Check

```bash
# Check API health
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "timestamp": "..."}
```

### Step 3: Authentication (2 minutes)

#### 3.1 Register Demo User

```bash
# Register new user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "username": "demo_user",
    "password": "DemoPassword123!",
    "full_name": "Demo User"
  }'
```

**Expected Response**: User created with tokens
```json
{
  "success": true,
  "data": {
    "user": {"id": "...", "email": "demo@example.com"},
    "access_token": "eyJhbGci...",
    "refresh_token": "eyJhbGci..."
  }
}
```

#### 3.2 Login

```bash
# Login to get access token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo@example.com",
    "password": "DemoPassword123!"
  }'
```

**Save the access token** from the response for subsequent requests.

### Step 4: Browse Test Suites (3 minutes)

#### 4.1 List All Test Suites

```bash
# List test suites (replace <TOKEN> with your access token)
curl http://localhost:8000/api/test-suites \
  -H "Authorization: Bearer <TOKEN>"
```

**Expected Response**: List of test suites including the demo suite
- "Voice AI Demo Test Suite" should be visible
- Suite includes metadata: name, description, tags, test case count

#### 4.2 Get Demo Suite Details

```bash
# Get specific test suite (replace <SUITE_ID> with demo suite ID)
curl http://localhost:8000/api/test-suites/<SUITE_ID> \
  -H "Authorization: Bearer <TOKEN>"
```

**Highlight**:
- Suite contains 10 test cases
- Organized by category
- Tags for easy filtering

### Step 5: Explore Test Cases (5 minutes)

#### 5.1 List All Test Cases

```bash
# List test cases with pagination
curl "http://localhost:8000/api/test-cases?page=1&page_size=10" \
  -H "Authorization: Bearer <TOKEN>"
```

**Expected Response**: Paginated list of 10 demo test cases

#### 5.2 View Specific Test Case

```bash
# Get test case details (replace <TEST_CASE_ID>)
curl http://localhost:8000/api/test-cases/<TEST_CASE_ID> \
  -H "Authorization: Bearer <TOKEN>"
```

**Showcase Example**: "Navigate to Home Address" test case
- **Test Type**: voice_command
- **Category**: navigation
- **Languages**: English, Spanish, French
- **Input Variations**: Multiple phrasings per language
- **Scenario Definition**: Expected actions and outcomes

**Talking Points**:
- Realistic voice AI scenarios
- Multi-language support demonstrates global reach
- Input variations handle natural language diversity
- Scenario definitions include expected behaviors

#### 5.3 Demonstrate Multilingual Support

Show how a single test case supports multiple languages:

```json
{
  "name": "Navigate to Home Address",
  "languages": [
    {
      "language_code": "en",
      "input_text": "Navigate home",
      "input_variations": ["Take me home", "Go to my house", "Drive me home"]
    },
    {
      "language_code": "es",
      "input_text": "Navegar a casa",
      "input_variations": ["Llévame a casa", "Ir a mi casa"]
    },
    {
      "language_code": "fr",
      "input_text": "Naviguer vers la maison",
      "input_variations": ["Aller à la maison", "Rentrer chez moi"]
    }
  ]
}
```

**Talking Points**:
- Single test case supports 5 languages (en, es, fr, de, ja)
- Input variations handle different phrasings
- Translations maintained alongside test definitions

### Step 6: Create Custom Test Case (4 minutes)

Demonstrate creating a new test case:

```bash
# Create test case
curl -X POST http://localhost:8000/api/test-cases \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "suite_id": "<SUITE_ID>",
    "name": "Demo: Check Traffic Status",
    "description": "Test voice query for traffic information",
    "test_type": "voice_command",
    "category": "information",
    "scenario_definition": {
      "input": "What is the traffic like?",
      "expected_action": "provide_traffic_info",
      "expected_location": "current_route",
      "timeout_seconds": 15
    },
    "tags": ["traffic", "information", "demo"],
    "languages": [
      {
        "language_code": "en",
        "input_text": "What is the traffic like?",
        "input_variations": [
          "How is traffic?",
          "Is there traffic ahead?",
          "Check traffic conditions"
        ]
      }
    ]
  }'
```

**Expected Response**: Test case created successfully
```json
{
  "success": true,
  "data": {
    "id": "...",
    "name": "Demo: Check Traffic Status",
    "created_at": "..."
  }
}
```

**Talking Points**:
- Easy test case creation via API
- Flexible scenario definitions support various test types
- Tags enable organization and filtering

### Step 7: Test Execution (3 minutes)

#### 7.1 Create Test Run

```bash
# Create test run from suite
curl -X POST http://localhost:8000/api/test-runs \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "suite_id": "<SUITE_ID>",
    "name": "Demo Test Run",
    "description": "Demonstration of test execution",
    "configuration": {
      "language": "en",
      "timeout_seconds": 30,
      "retry_count": 1
    }
  }'
```

**Expected Response**: Test run created
```json
{
  "success": true,
  "data": {
    "id": "...",
    "name": "Demo Test Run",
    "status": "pending",
    "total_tests": 10
  }
}
```

#### 7.2 Start Test Execution

```bash
# Start test run (replace <TEST_RUN_ID>)
curl -X POST http://localhost:8000/api/test-runs/<TEST_RUN_ID>/start \
  -H "Authorization: Bearer <TOKEN>"
```

**Expected Response**: Test run started
```json
{
  "success": true,
  "data": {
    "status": "running",
    "started_at": "..."
  }
}
```

**Talking Points**:
- Automated test orchestration
- Configurable execution parameters
- Background task processing with Celery

#### 7.3 Monitor Test Progress

```bash
# Get test run status
curl http://localhost:8000/api/test-runs/<TEST_RUN_ID> \
  -H "Authorization: Bearer <TOKEN>"
```

**Expected Response**: Test run progress
```json
{
  "success": true,
  "data": {
    "status": "running",
    "total_tests": 10,
    "completed_tests": 5,
    "passed_tests": 4,
    "failed_tests": 1
  }
}
```

### Step 8: View Test Results (3 minutes)

#### 8.1 Get Test Run Results

```bash
# Get results for test run
curl http://localhost:8000/api/test-runs/<TEST_RUN_ID>/results \
  -H "Authorization: Bearer <TOKEN>"
```

**Expected Response**: Detailed results for each test case
- Execution status (passed/failed)
- Validation results
- Audio transcriptions
- Performance metrics

#### 8.2 Analyze Validation Results

Show validation result for a specific test case execution:

```bash
# Get validation result details
curl http://localhost:8000/api/validation-results/<RESULT_ID> \
  -H "Authorization: Bearer <TOKEN>"
```

**Highlight**:
- Expected vs. actual outcomes comparison
- Validation scores and confidence levels
- Transcription accuracy
- Response time metrics

**Talking Points**:
- Automated validation reduces manual review
- Detailed results enable debugging
- Historical tracking for trend analysis

---

## Feature Showcase

### Key Features to Highlight

1. **Comprehensive Test Management**
   - Test suites organize related test cases
   - Tags and categories for easy filtering
   - Version control for test case changes

2. **Multilingual Support**
   - 5+ languages supported out of the box
   - Language variations with input alternatives
   - Scalable for additional languages

3. **Flexible Test Types**
   - **Voice Command**: Single-turn voice interactions
   - **Multi-turn**: Conversational dialog flows
   - **Edge Cases**: Error handling and boundary conditions

4. **Test Orchestration**
   - Background task execution with Celery
   - Configurable retry logic
   - Priority queue for test scheduling

5. **Validation & Results**
   - Automated validation against expected outcomes
   - Audio transcription and analysis
   - Comprehensive reporting with metrics

6. **RESTful API**
   - OpenAPI/Swagger documentation
   - JWT authentication
   - Standardized response models

7. **Scalable Architecture**
   - Docker Compose for easy deployment
   - PostgreSQL for reliable data storage
   - Redis for caching and task queuing

### Optional: Frontend Demo

If demonstrating the React frontend (`http://localhost:5173`):

1. **Login**: Show authentication flow
2. **Dashboard**: Overview of test suites and recent runs
3. **Test Cases**: Browse and create test cases via UI
4. **Test Execution**: Start and monitor test runs
5. **Results Visualization**: Charts and graphs for test metrics

---

## Troubleshooting

### Common Issues

#### Services Not Starting

```bash
# Check Docker service status
docker-compose ps

# View logs for specific service
docker-compose logs postgres
docker-compose logs redis

# Restart services
docker-compose restart
```

#### Database Connection Errors

```bash
# Verify PostgreSQL is accessible
docker exec -it automated-testing_postgres_1 psql -U postgres -d voiceai_testing

# Check database exists
\l

# Exit psql
\q
```

#### API Not Responding

```bash
# Check if backend server is running
curl http://localhost:8000/health

# Check backend logs for errors
# Look for stack traces or error messages in terminal
```

#### Demo Data Not Loading

```bash
# Verify migrations are applied
venv/bin/alembic current

# Re-run demo data loader
cd backend
python -m scripts.load_demo_data
```

---

## Q&A and Next Steps

### Frequently Asked Questions

**Q: Can this framework integrate with existing CI/CD pipelines?**
A: Yes, via GitHub Actions workflows. See `docs/deployment.md` for details.

**Q: What telephony providers are supported?**
A: Currently supports Twilio, Vonage, and Bandwidth via integrations.

**Q: How are test results stored long-term?**
A: All results are persisted in PostgreSQL with historical tracking enabled.

**Q: Can custom validation logic be added?**
A: Yes, validation rules are extensible via Python plugins.

### Next Steps

- **Setup Guide**: See `docs/setup-guide.md` for detailed installation
- **API Documentation**: Explore `http://localhost:8000/docs`
- **Database Schema**: Review `docs/database-schema.md`
- **Deployment**: Production deployment guide in `docs/deployment.md`

---

**Demo Complete!**

For questions or feedback, please reach out to the development team.
