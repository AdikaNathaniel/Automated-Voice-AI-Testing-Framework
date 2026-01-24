# Voice AI Testing Framework - Implementation Roadmap

**Last Updated:** 2025-12-05
**Current Phase:** Phase 2 - Validation Layer
**Overall Progress:** 65% Complete → Target: 100% MVP

---

## 📊 Quick Status

| Component | Status | Progress | Priority |
|-----------|--------|----------|----------|
| **Infrastructure** | ✅ Complete | 95% | - |
| **Database & Models** | ✅ Complete | 100% | - |
| **Authentication** | ✅ Complete | 100% | - |
| **UI/Frontend** | ✅ Complete | 85% | - |
| **API Routes** | ✅ Complete | 90% | - |
| **Test Execution** | ❌ Missing | 10% | 🔴 CRITICAL |
| **Audio Processing** | ❌ Missing | 20% | 🔴 CRITICAL |
| **Validation Layer** | ⚠️ Partial | 40% | 🟡 HIGH |
| **Integrations** | ⚠️ Partial | 60% | 🟡 MEDIUM |

---

## 🎯 What This System Does

### Core Workflow
```
┌─────────────────────────────────────────────────────────────────┐
│ 1. CREATE TEST CASE                                              │
│    → Define voice query, expected intent, entities, response    │
├─────────────────────────────────────────────────────────────────┤
│ 2. GENERATE AUDIO                                               │
│    → Convert text to speech (TTS)                               │
│    → Store audio file in MinIO                                  │
├─────────────────────────────────────────────────────────────────┤
│ 3. EXECUTE TEST                                                 │
│    → Send voice query to Houndify API                           │
│    → Get response (intent, entities, confidence, text)          │
├─────────────────────────────────────────────────────────────────┤
│ 4. VALIDATE RESULT                                              │
│    → Intent matching (exact/fuzzy)                              │
│    → Entity extraction validation                               │
│    → Confidence threshold check                                 │
│    → Semantic similarity (ML-based)                             │
│    → Custom rules validation                                    │
├─────────────────────────────────────────────────────────────────┤
│ 5. HUMAN REVIEW (if needed)                                     │
│    → Queue items below confidence threshold                     │
│    → Validator reviews and approves/rejects                     │
├─────────────────────────────────────────────────────────────────┤
│ 6. REPORT & NOTIFY                                              │
│    → Update dashboard metrics                                   │
│    → Create Jira ticket for failures                            │
│    → Send Slack notification                                    │
│    → Generate regression report                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔍 Intent Discovery (Already Completed)

### Discovered Intents: 20
- **InformationCommand** (34 queries) - Weather, math, facts, conversions
- **CalendarCommand** (10 queries) - Scheduling, reminders, events
- **MusicCommand** (7 queries) - Music search and playback
- **NoResultCommand** - No results found scenarios
- **ErrorCommand** - Missing context (e.g., "What's the weather?" without location)
- **FlightBookingCommand** - Flight search
- **PhoneCommand** - Make phone calls
- And 13 more...

### Test Query Library: 220+ queries
- Location: `scripts/discovery_queries.txt`
- Results: `discovered_intents.json`
- Documentation: `docs/HOUNDIFY_INTENTS_REFERENCE.md`

---

## 🚦 Implementation Phases

### ✅ Phase 1: Core Execution (COMPLETED)
**Status:** Done
**Completion Date:** November 2024

**Deliverables:**
- ✅ Orchestration layer (`create_test_run`, `schedule_test_executions`, `aggregate_results`)
- ✅ Execution layer (`execute_test_case`, `execute_test_batch`, retry logic)
- ✅ Houndify integration (client fully working, 47/47 tests passing)
- ✅ Intent discovery system (20 intents, 220+ queries)
- ✅ 43 tests for aggregate_results

---

### 🔄 Phase 2: Validation Layer (IN PROGRESS)
**Status:** 40% Complete
**Target:** 2-3 weeks
**Priority:** 🔴 CRITICAL

#### Task Breakdown

##### 2.1 Intent Validation ⬜ NOT STARTED
**File:** `backend/tasks/validation.py`
**Function:** `validate_intent()`
**Estimated:** 2 days

**Requirements:**
- Exact match mode: `"InformationCommand" == "InformationCommand"`
- Fuzzy match mode: Levenshtein distance threshold (handle typos)
- Intent mapping: Custom intent names → Houndify intents
- Return match score (0-1)

**Test Cases:**
- Exact match (case-insensitive)
- Fuzzy matching with typos
- Intent mapping lookups
- Error handling for missing intents
- Edge cases

**Acceptance Criteria:**
- ✅ 10-15 unit tests (all passing)
- ✅ Supports all 3 modes (exact, fuzzy, mapping)
- ✅ Returns validation result with score
- ✅ <50 lines per function

---

##### 2.2 Entity Validation ⬜ NOT STARTED
**File:** `backend/tasks/validation.py`
**Function:** `validate_entities()`
**Estimated:** 2 days

**Requirements:**
- Check all expected entities present
- Validate entity values (exact or fuzzy)
- Track missing entities
- Track extra entities (informative, not failure)
- Calculate entity match score (0-1)

**Example:**
```json
Expected: {"Location": "San Francisco", "Time": "today"}
Detected: {"Location": "San Francisco"}
Result: {
  "is_valid": false,
  "matched_entities": ["Location"],
  "missing_entities": ["Time"],
  "extra_entities": [],
  "entity_match_score": 0.5
}
```

**Test Cases:**
- All entities match
- Missing entities
- Extra entities
- Entity value mismatches
- Partial matches

**Acceptance Criteria:**
- ✅ 10-15 unit tests (all passing)
- ✅ Handles missing/extra entities correctly
- ✅ Returns detailed validation result
- ✅ <50 lines per function

---

##### 2.3 Confidence Validation ⬜ NOT STARTED
**File:** `backend/tasks/validation.py`
**Function:** `validate_confidence()`
**Estimated:** 1 day

**Requirements:**
- Check confidence score meets minimum threshold (default: 0.7)
- Check confidence score below maximum threshold (detect over-confident errors)
- Return validation result with threshold info

**Test Cases:**
- Above threshold (valid)
- Below threshold (invalid)
- Exactly at threshold (edge case)
- Invalid confidence values (<0 or >1)

**Acceptance Criteria:**
- ✅ 8-10 unit tests (all passing)
- ✅ Configurable thresholds
- ✅ Returns clear pass/fail status
- ✅ <30 lines per function

---

##### 2.4 Semantic Similarity Validation ⬜ NOT STARTED
**File:** `backend/tasks/validation.py`
**Function:** `validate_semantic_similarity()`
**Estimated:** 3 days

**Requirements:**
- Use sentence-transformers (SBERT) for embeddings
- Calculate cosine similarity between expected and actual responses
- Fallback to basic text similarity if ML unavailable
- Return similarity score (0-1)

**Example:**
```python
Expected: "It's 72 degrees and sunny in San Francisco"
Actual: "The weather is 72°F with sun"
Result: {
  "is_valid": true,
  "similarity_score": 0.92,
  "threshold": 0.8,
  "comparison_method": "sentence-transformers"
}
```

**Dependencies:**
```txt
sentence-transformers==2.2.2
torch==2.0.1
scikit-learn==1.3.0
```

**Test Cases:**
- Identical responses (100% similarity)
- Similar meaning, different wording (>80%)
- Completely different responses (<20%)
- Empty responses
- Special characters

**Acceptance Criteria:**
- ✅ 12-15 unit tests (all passing)
- ✅ ML model loads successfully
- ✅ Inference time <100ms per comparison
- ✅ Fallback to basic similarity if ML fails
- ✅ <50 lines per function

---

##### 2.5 Custom Rules Validation ⬜ NOT STARTED
**File:** `backend/tasks/validation.py`
**Function:** `validate_custom_rules()`
**Estimated:** 2 days

**Requirements:**
Apply custom validation rules from test case:
```json
{
  "response_contains": ["weather", "San Francisco"],
  "response_not_contains": ["error", "failed"],
  "response_length_min": 10,
  "response_length_max": 200,
  "custom_regex": "\\d{1,3}°F",
  "required_fields": ["temperature", "condition"],
  "numeric_range": {"temperature": {"min": -50, "max": 150}}
}
```

**Test Cases:**
- All rules pass
- Some rules fail
- Invalid rule definitions
- Edge cases (empty lists, null values)
- Regex patterns

**Acceptance Criteria:**
- ✅ 15-20 unit tests (all passing)
- ✅ Supports all rule types
- ✅ Returns detailed rule pass/fail breakdown
- ✅ <50 lines per function

---

##### 2.6 Main Validation Orchestrator ⬜ NOT STARTED
**File:** `backend/tasks/validation.py`
**Function:** `validate_execution_result()`
**Estimated:** 3 days

**Requirements:**
- Orchestrate all validation tasks
- Run validations in parallel (Celery groups)
- Aggregate results from all validators
- Determine overall pass/fail status
- Update database with validation results
- Emit WebSocket event for real-time UI updates

**Workflow:**
```python
1. Fetch execution record and test case from database
2. Run parallel validation tasks:
   - validate_intent()
   - validate_entities()
   - validate_confidence()
   - validate_semantic_similarity() (if configured)
   - validate_custom_rules() (if defined)
3. Aggregate validation results
4. Calculate overall validation score
5. Update VoiceTestExecution with validation status
6. Emit WebSocket event
7. Return comprehensive validation report
```

**Test Cases:**
- All validations pass
- Some validations fail
- Missing test case / execution
- Database errors
- Validation task failures
- Timeout handling

**Acceptance Criteria:**
- ✅ 15-20 unit tests (all passing)
- ✅ Parallel execution working
- ✅ Database updates correctly
- ✅ WebSocket events emitted
- ✅ <50 lines per function

---

### 🔄 Phase 3: Test Execution Pipeline (NEXT)
**Status:** 10% Complete
**Target:** 2 weeks
**Priority:** 🔴 CRITICAL

**Current Problem:**
```python
# backend/tasks/orchestration.py:46-58
def create_test_run(...) -> Dict[str, Any]:
    # TODO: Implement test run creation logic
    return {
        'test_run_id': 'placeholder',
        'status': 'pending',
        'test_count': 0,
        'message': 'Test run orchestration not yet implemented'  # ❌
    }
```

**Tasks:**

#### 3.1 Implement `create_test_run()` ⬜ NOT STARTED
**Estimated:** 2 days

**Requirements:**
1. Validate inputs (suite_id or test_case_ids)
2. Create test run record in database
3. Fetch test cases from suite or use provided IDs
4. Create VoiceTestExecution records for each test case
5. Queue test executions to Celery
6. Return test run information

**Acceptance Criteria:**
- ✅ Creates test run in database
- ✅ Queues test executions to Celery
- ✅ Returns test run ID and metadata
- ✅ Handles errors gracefully

---

#### 3.2 Implement `schedule_test_executions()` ⬜ NOT STARTED
**Estimated:** 2 days

**Requirements:**
1. Fetch pending test executions from queue
2. Group executions by priority
3. Distribute to Celery workers
4. Track execution progress
5. Handle worker failures

**Acceptance Criteria:**
- ✅ Executions run in parallel (up to worker limit)
- ✅ Priority-based scheduling
- ✅ Progress tracking
- ✅ Retry on failure

---

#### 3.3 Implement `aggregate_results()` ⬜ NOT STARTED
**Estimated:** 2 days

**Requirements:**
1. Collect results from all test executions
2. Calculate pass/fail counts
3. Calculate average confidence scores
4. Update test run statistics
5. Mark test run as completed
6. Trigger notifications (Jira, Slack)

**Acceptance Criteria:**
- ✅ Accurate result aggregation
- ✅ Test run marked complete
- ✅ Statistics updated
- ✅ Notifications triggered

---

### 🔄 Phase 4: Audio Processing Pipeline (PARALLEL)
**Status:** 20% Complete
**Target:** 2 weeks
**Priority:** 🔴 CRITICAL

**Current Problem:**
```python
# backend/services/voice_execution_service.py:520-556
async def _maybe_invoke_houndify(...):
    tts_service = self._ensure_tts_service()
    houndify_client = self._ensure_houndify_client()

    if not tts_service or not houndify_client:
        return  # ❌ Silently returns without doing anything
```

**Tasks:**

#### 4.1 TTS Audio Generation ⬜ NOT STARTED
**Estimated:** 2 days

**Requirements:**
1. Implement gTTS integration (Google Text-to-Speech)
2. Generate audio files from test case queries
3. Support multiple languages (8+ languages)
4. Support multiple voices/accents
5. Cache generated audio files

**Acceptance Criteria:**
- ✅ Audio files generated successfully
- ✅ Multiple languages supported
- ✅ Audio quality validated
- ✅ Files stored in MinIO

---

#### 4.2 MinIO Storage Integration ⬜ NOT STARTED
**Estimated:** 1 day

**Requirements:**
1. Upload audio files to MinIO
2. Generate presigned URLs for playback
3. Implement file cleanup policy (delete old files)
4. Track storage usage

**Acceptance Criteria:**
- ✅ Files uploaded to MinIO
- ✅ Presigned URLs work in frontend
- ✅ Cleanup policy configured
- ✅ Storage metrics tracked

---

#### 4.3 Houndify API Integration ⬜ NOT STARTED
**Estimated:** 2 days

**Requirements:**
1. Wire Houndify client into execution pipeline
2. Send audio files to Houndify API
3. Parse response (intent, entities, confidence, text)
4. Store response in database
5. Handle API errors and retries

**Acceptance Criteria:**
- ✅ Houndify API called successfully
- ✅ Response parsed correctly
- ✅ Results stored in database
- ✅ Error handling works

---

### 🔄 Phase 5: Integration Wiring (AFTER PHASE 3-4)
**Status:** 60% Complete
**Target:** 1 week
**Priority:** 🟡 MEDIUM

**Tasks:**

#### 5.1 Jira Integration ⬜ NOT STARTED
**Estimated:** 1 day

Wire Jira client to defect creation:
- Automatically create Jira ticket when test fails
- Include test case details, error message, audio files
- Link to test run in dashboard
- Support custom Jira fields

---

#### 5.2 Slack Notifications ⬜ NOT STARTED
**Estimated:** 1 day

Wire Slack client to test events:
- Send notification on test run completion
- Send alert on critical failures
- Include pass/fail summary
- Link to dashboard

---

#### 5.3 GitHub Webhooks ⬜ NOT STARTED
**Estimated:** 1 day

Connect GitHub integration:
- Trigger regression tests on new commits
- Post test results as PR comments
- Track test coverage changes

---

## 🔄 Multi-Step Conversation Flows (ALREADY SUPPORTED!)

### ✅ Features Already Implemented

The system **already has infrastructure** for multi-step conversations:

#### Services Available:
1. **`multi_turn_conversation_service.py`**
   - Dialog tree management
   - Multi-turn flow orchestration
   - Handoff scenarios
   - Escalation testing

2. **`multi_turn_context_service.py`**
   - Context state management
   - Conversation history tracking
   - Entity persistence across turns

3. **`step_orchestration_service.py`**
   - Step-by-step test execution
   - Branch handling (if/else logic)
   - Loop support (repeat until condition)

4. **`conversation_recovery_service.py`**
   - Error recovery in multi-step flows
   - Fallback strategies
   - Context restoration

#### Database Model:
**`ScenarioScript`** model supports:
```python
class ScenarioScript(Base):
    __tablename__ = "scenario_scripts"

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String, nullable=False)
    steps = Column(JSON)  # List of conversation steps
    branches = Column(JSON)  # Conditional branches
    context = Column(JSON)  # Shared context across steps
```

#### Example Multi-Step Test Case:
```json
{
  "name": "Flight Booking Multi-Step",
  "steps": [
    {
      "step": 1,
      "user_says": "Book a flight to Miami",
      "expected_intent": "FlightBookingCommand",
      "expected_response_contains": ["Where are you flying from?"]
    },
    {
      "step": 2,
      "user_says": "From New York",
      "expected_intent": "FlightBookingCommand",
      "expected_response_contains": ["What date would you like to travel?"],
      "context": {
        "origin": "New York",
        "destination": "Miami"
      }
    },
    {
      "step": 3,
      "user_says": "December 15th",
      "expected_intent": "FlightBookingCommand",
      "expected_response_contains": ["I found flights"],
      "context": {
        "origin": "New York",
        "destination": "Miami",
        "date": "2025-12-15"
      }
    }
  ]
}
```

### 🔧 To Enable Multi-Step Testing:

**What's Needed:**
1. ⬜ Wire `multi_turn_conversation_service` into test execution pipeline
2. ⬜ Implement context state persistence between steps
3. ⬜ Add step validation (validate each step individually)
4. ⬜ Handle branch logic (if/else scenarios)
5. ⬜ Add multi-step test UI components

**Estimated Effort:** 1 week (can be done in parallel with Phase 5)

---

## 📈 Progress Tracking

### Weekly Milestones

#### Week 1 (Dec 5-11): Validation Layer Foundation
- [ ] 2.1 Intent Validation (2 days)
- [ ] 2.2 Entity Validation (2 days)
- [ ] 2.3 Confidence Validation (1 day)

**Deliverable:** Basic validation working for intent, entities, confidence

---

#### Week 2 (Dec 12-18): Advanced Validation + Orchestration
- [ ] 2.4 Semantic Similarity Validation (3 days)
- [ ] 2.5 Custom Rules Validation (2 days)

**Deliverable:** All validation types implemented

---

#### Week 3 (Dec 19-25): Validation Orchestrator + Test Execution
- [ ] 2.6 Main Validation Orchestrator (3 days)
- [ ] 3.1 Implement `create_test_run()` (2 days)

**Deliverable:** End-to-end validation working, test runs can be created

---

#### Week 4 (Dec 26-Jan 1): Test Execution Pipeline
- [ ] 3.2 Implement `schedule_test_executions()` (2 days)
- [ ] 3.3 Implement `aggregate_results()` (2 days)
- [ ] 4.1 TTS Audio Generation (2 days)

**Deliverable:** Test execution pipeline working, audio generation started

---

#### Week 5 (Jan 2-8): Audio Processing + Houndify
- [ ] 4.2 MinIO Storage Integration (1 day)
- [ ] 4.3 Houndify API Integration (2 days)
- [ ] Testing + Bug Fixes (2 days)

**Deliverable:** Full end-to-end test execution working

---

#### Week 6 (Jan 9-15): Integration Wiring + Polish
- [ ] 5.1 Jira Integration (1 day)
- [ ] 5.2 Slack Notifications (1 day)
- [ ] 5.3 GitHub Webhooks (1 day)
- [ ] E2E Testing + Demo Data (2 days)

**Deliverable:** MVP ready for pilot testing

---

## 🧪 Testing Strategy

### Test Coverage Requirements
- **Unit Tests:** 90%+ coverage on all new code
- **Integration Tests:** End-to-end validation pipeline
- **E2E Tests:** Full test execution with real Houndify API
- **Performance Tests:** 100+ concurrent test executions

### Test-Driven Development (TDD)
1. **Red Phase:** Write failing test first
2. **Green Phase:** Write minimal code to pass test
3. **Refactor Phase:** Improve code while keeping tests green

---

## 📝 Next Actions

### TODAY (Dec 5):
1. ✅ Create this tracking document
2. ⬜ Start Phase 2.1: Intent Validation
3. ⬜ Write unit tests for `validate_intent()`
4. ⬜ Implement exact match mode

### THIS WEEK:
1. ⬜ Complete Tasks 2.1, 2.2, 2.3 (Intent, Entity, Confidence validation)
2. ⬜ 40+ unit tests (all passing)
3. ⬜ Update this document with progress

### NEXT WEEK:
1. ⬜ Complete Tasks 2.4, 2.5 (Semantic Similarity, Custom Rules)
2. ⬜ Load ML models for semantic validation
3. ⬜ 60+ additional unit tests

---

## 📚 Documentation References

- [Project Completion Status](./PROJECT_COMPLETION_STATUS.md) - Detailed gap analysis
- [Next Phase Plan](./docs/NEXT_PHASE_PLAN.md) - Phase 2 detailed plan
- [Houndify Intents Reference](./docs/HOUNDIFY_INTENTS_REFERENCE.md) - Intent documentation
- [Houndify Quick Reference](./docs/HOUNDIFY_INTENTS_QUICK_REFERENCE.md) - 20 intents summary
- [CLAUDE.md](./CLAUDE.md) - Development guide and conventions

---

## 🎯 Success Criteria

### MVP Ready When:
- ✅ Can create and execute test runs end-to-end
- ✅ Audio generation working
- ✅ Houndify API integration functional
- ✅ All 6 validation types implemented
- ✅ Human validation queue working
- ✅ Dashboard shows real test data
- ✅ Jira/Slack integrations triggered on events
- ✅ 90%+ test coverage
- ✅ Can run 100+ tests concurrently
- ✅ E2E tests passing with real Houndify API

---

**Document Owner:** Development Team
**Review Frequency:** Weekly (every Monday)
**Last Review:** 2025-12-05
