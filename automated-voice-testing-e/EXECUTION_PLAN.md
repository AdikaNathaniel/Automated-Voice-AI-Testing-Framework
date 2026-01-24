# Voice AI Testing Framework - Execution Plan to MVP

**Created**: 2025-11-24
**Target**: 4-6 weeks to functional MVP
**Current Status**: 65% complete (foundation ready, execution missing)

---

## Overview

This plan systematically addresses the **critical 35% gap** to get from "well-architected skeleton" to "functional MVP". We're prioritizing based on dependencies and business value.

### Success Criteria
1. ✅ Execute a voice test end-to-end (audio → Houndify → validation → result)
2. ✅ Automated validation with >85% accuracy (99.7% comes later with tuning)
3. ✅ Human validation queue operational
4. ✅ External integrations firing (Jira tickets, Slack notifications)
5. ✅ Real data flowing through dashboards
6. ✅ Can run 10+ concurrent tests (1000+ comes with optimization)

---

## Phase 1: Core Execution Pipeline (Weeks 1-2)
**Priority**: 🚨 CRITICAL
**Goal**: Tests can actually execute

### Week 1: Test Orchestration & Audio Generation

#### Task 1.1: Implement `create_test_run()` Celery Task
**File**: `backend/tasks/orchestration.py` (lines 18-58)
**Current State**: Returns placeholder message ❌
**Target State**: Creates test run and schedules execution

**Implementation Steps**:
```python
# What to implement in create_test_run():

@celery.task(name='tasks.orchestration.create_test_run', bind=True)
def create_test_run(self, suite_id=None, test_case_ids=None, languages=None, config=None):
    """Create and orchestrate a test run."""

    # STEP 1: Validate inputs
    if not suite_id and not test_case_ids:
        raise ValueError("Either suite_id or test_case_ids required")

    # STEP 2: Get database session
    from api.database import get_sync_db
    db = get_sync_db()

    # STEP 3: Fetch test cases
    if suite_id:
        # Fetch all test cases in the suite
        test_cases = db.query(TestCase).join(TestSuite).filter(
            TestSuite.id == suite_id
        ).all()
    else:
        # Fetch specific test cases
        test_cases = db.query(TestCase).filter(
            TestCase.id.in_(test_case_ids)
        ).all()

    # STEP 4: Create TestRun record
    test_run = TestRun(
        name=f"Test Run {datetime.utcnow().isoformat()}",
        suite_id=suite_id,
        status='pending',
        total_tests=len(test_cases) * len(languages or ['en-US']),
        configuration=config or {}
    )
    db.add(test_run)
    db.commit()

    # STEP 5: Schedule test executions
    result = schedule_test_executions.delay(
        test_run_id=str(test_run.id),
        test_case_ids=[str(tc.id) for tc in test_cases],
        languages=languages
    )

    # STEP 6: Return test run info
    return {
        'test_run_id': str(test_run.id),
        'status': 'scheduled',
        'test_count': test_run.total_tests,
        'task_id': result.id
    }
```

**Acceptance Criteria**:
- [ ] Test run created in database
- [ ] Test cases fetched correctly (from suite or by IDs)
- [ ] Execution tasks scheduled via Celery
- [ ] Returns valid test_run_id (not 'placeholder')
- [ ] Unit tests pass

**Time Estimate**: 1.5 days

---

#### Task 1.2: Implement `schedule_test_executions()` Celery Task
**File**: `backend/tasks/orchestration.py` (lines 61-94)
**Current State**: Returns empty list ❌
**Target State**: Creates execution tasks for each test case

**Implementation Steps**:
```python
@celery.task(name='tasks.orchestration.schedule_test_executions', bind=True)
def schedule_test_executions(self, test_run_id, test_case_ids, languages=None):
    """Schedule execution of multiple test cases."""

    from celery import group
    from tasks.voice_execution import execute_voice_test

    # STEP 1: Default to en-US if no languages specified
    languages = languages or ['en-US']

    # STEP 2: Create execution task for each test case × language combo
    tasks = []
    for test_case_id in test_case_ids:
        for language in languages:
            task = execute_voice_test.s(
                test_case_id=test_case_id,
                language_code=language,
                test_run_id=test_run_id
            )
            tasks.append(task)

    # STEP 3: Execute tasks in parallel using Celery group
    job = group(tasks)
    result = job.apply_async()

    # STEP 4: Return task info
    return {
        'scheduled_count': len(tasks),
        'task_ids': [str(r.id) for r in result.results],
        'group_id': result.id
    }
```

**Acceptance Criteria**:
- [ ] Creates one task per test case × language combination
- [ ] Uses Celery group for parallel execution
- [ ] Returns valid task IDs (not empty list)
- [ ] Tasks actually appear in RabbitMQ queue
- [ ] Unit tests pass

**Time Estimate**: 1 day

---

#### Task 1.3: Create `execute_voice_test()` Celery Task
**File**: `backend/tasks/voice_execution.py` (NEW FILE)
**Current State**: Doesn't exist ❌
**Target State**: Executes a single voice test

**Implementation Steps**:
```python
# Create new file: backend/tasks/voice_execution.py

from celery_app import celery
from uuid import UUID
from typing import Dict, Any

@celery.task(name='tasks.voice_execution.execute_voice_test', bind=True)
def execute_voice_test(
    self,
    test_case_id: str,
    language_code: str,
    test_run_id: str
) -> Dict[str, Any]:
    """
    Execute a single voice test.

    Workflow:
    1. Fetch test case from database
    2. Generate TTS audio from test case text
    3. Store audio in MinIO
    4. Call Houndify API with audio
    5. Store response
    6. Trigger validation
    7. Return execution result
    """

    from api.database import get_sync_db
    from services.voice_execution_service import VoiceExecutionService
    from tasks.validation import validate_test_execution

    db = get_sync_db()

    try:
        # STEP 1: Execute voice test via service
        service = VoiceExecutionService(db=db)
        execution = await service.execute_voice_test(
            test_case_id=UUID(test_case_id),
            language_code=language_code,
            test_run_id=UUID(test_run_id)
        )

        # STEP 2: Trigger validation (async)
        validate_test_execution.delay(str(execution.id))

        # STEP 3: Update test run progress
        from tasks.orchestration import monitor_test_run_progress
        monitor_test_run_progress.delay(test_run_id)

        # STEP 4: Return result
        return {
            'execution_id': str(execution.id),
            'test_case_id': test_case_id,
            'language_code': language_code,
            'status': execution.status,
            'message': 'Voice test executed successfully'
        }

    except Exception as e:
        # Log error and mark execution as failed
        logger.error(f"Voice test execution failed: {e}")
        return {
            'execution_id': None,
            'test_case_id': test_case_id,
            'status': 'failed',
            'error': str(e)
        }
```

**Acceptance Criteria**:
- [ ] Task executes successfully
- [ ] Calls VoiceExecutionService
- [ ] Triggers validation task
- [ ] Updates test run progress
- [ ] Error handling works
- [ ] Integration test passes

**Time Estimate**: 1 day

---

#### Task 1.4: Wire Up TTS Audio Generation
**File**: `backend/services/voice_execution_service.py` (lines 520-556)
**Current State**: `_maybe_invoke_houndify()` returns silently ❌
**Target State**: Generates audio and calls Houndify

**Implementation Steps**:
```python
# Fix in voice_execution_service.py:

async def _maybe_invoke_houndify(...):
    """Trigger Houndify voice query if the service has all dependencies."""

    # STEP 1: Ensure services are initialized (ALREADY EXISTS)
    tts_service = self._ensure_tts_service()
    houndify_client = self._ensure_houndify_client()

    # REMOVE THIS - don't silently return:
    # if not tts_service or not houndify_client:
    #     return

    # REPLACE WITH - raise error if missing:
    if not tts_service:
        raise RuntimeError("TTS service not initialized")
    if not houndify_client:
        raise RuntimeError("Houndify client not initialized")

    # STEP 2: Extract prompt text from test case (ALREADY EXISTS)
    prompt_text = self._extract_prompt_text(test_case)
    if not prompt_text:
        raise ValueError(f"No prompt text in test case {test_case.id}")

    # STEP 3: Generate TTS audio (ALREADY EXISTS BUT MAY NEED FIX)
    try:
        tts_lang = self._tts_language(language_code)
        tts_result = self._synthesize_prompt(tts_service, prompt_text, tts_lang)
        audio_bytes = tts_result.audio_bytes

        # Validate audio was generated
        if not audio_bytes or len(audio_bytes) == 0:
            raise ValueError("TTS generated empty audio")

        # Apply audio profile effects (ALREADY EXISTS)
        audio_bytes = self._apply_audio_profile_effects(audio_bytes, execution, test_case)

        # Record metadata (ALREADY EXISTS)
        self._record_audio_metadata(execution, prompt_text, tts_lang, tts_result, language_code, test_case)

        # NEW: Store audio in MinIO
        audio_url = await self._store_audio_in_minio(audio_bytes, execution.id)
        execution.set_audio_param("audio_url", audio_url)

    except Exception as exc:
        logger.exception("TTS generation failed: %s", exc)
        execution.mark_failed(str(exc))
        raise

    # STEP 4: Call Houndify API (ALREADY EXISTS - lines 557-594)
    # ... rest of existing code continues ...
```

**Additional**: Implement `_store_audio_in_minio()` method:
```python
async def _store_audio_in_minio(self, audio_bytes: bytes, execution_id: UUID) -> str:
    """Store audio in MinIO and return URL."""
    from services.storage_service import StorageService

    storage = StorageService()
    filename = f"audio/{execution_id}.mp3"

    url = await storage.upload(
        bucket="voice-tests",
        key=filename,
        data=audio_bytes,
        content_type="audio/mpeg"
    )

    return url
```

**Acceptance Criteria**:
- [ ] TTS generates audio successfully
- [ ] Audio is not empty
- [ ] Audio stored in MinIO
- [ ] Houndify API called with audio
- [ ] Response stored in execution record
- [ ] Errors handled properly
- [ ] Integration test passes

**Time Estimate**: 1.5 days

---

#### Task 1.5: Implement MinIO Storage Service
**File**: `backend/services/storage_service.py` (NEW FILE)
**Current State**: Doesn't exist ❌
**Target State**: Can store/retrieve files from MinIO

**Implementation Steps**:
```python
# Create new file: backend/services/storage_service.py

from typing import Optional
import boto3
from botocore.exceptions import ClientError
from api.config import get_settings
import logging

logger = logging.getLogger(__name__)

class StorageService:
    """Service for storing files in S3/MinIO."""

    def __init__(self):
        settings = get_settings()

        # Use MinIO for local/dev, S3 for production
        self.client = boto3.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT_URL,  # http://minio:9000 for MinIO
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION or 'us-east-1'
        )

        self.default_bucket = settings.S3_BUCKET or 'voice-tests'

        # Ensure bucket exists
        self._ensure_bucket_exists(self.default_bucket)

    def _ensure_bucket_exists(self, bucket: str):
        """Create bucket if it doesn't exist."""
        try:
            self.client.head_bucket(Bucket=bucket)
        except ClientError:
            self.client.create_bucket(Bucket=bucket)
            logger.info(f"Created bucket: {bucket}")

    async def upload(
        self,
        bucket: str,
        key: str,
        data: bytes,
        content_type: str = 'application/octet-stream'
    ) -> str:
        """Upload file and return URL."""

        self.client.put_object(
            Bucket=bucket,
            Key=key,
            Body=data,
            ContentType=content_type
        )

        # Generate presigned URL (valid for 7 days)
        url = self.client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': key},
            ExpiresIn=604800  # 7 days
        )

        return url

    async def download(self, bucket: str, key: str) -> bytes:
        """Download file."""
        response = self.client.get_object(Bucket=bucket, Key=key)
        return response['Body'].read()

    async def delete(self, bucket: str, key: str):
        """Delete file."""
        self.client.delete_object(Bucket=bucket, Key=key)
```

**Environment Variables Needed**:
```bash
# Add to .env:
S3_ENDPOINT_URL=http://localhost:9000  # MinIO endpoint
S3_BUCKET=voice-tests
AWS_ACCESS_KEY_ID=minioadmin  # MinIO default
AWS_SECRET_ACCESS_KEY=minioadmin  # MinIO default
```

**Acceptance Criteria**:
- [ ] Can upload files to MinIO
- [ ] Can download files from MinIO
- [ ] Can delete files from MinIO
- [ ] Returns valid presigned URLs
- [ ] Bucket auto-created if missing
- [ ] Unit tests pass
- [ ] Integration test with MinIO passes

**Time Estimate**: 1 day

---

#### Task 1.6: Implement `aggregate_results()` Celery Task
**File**: `backend/tasks/orchestration.py` (lines 97-130)
**Current State**: Returns placeholder ❌
**Target State**: Aggregates results and updates test run

**Implementation Steps**:
```python
@celery.task(name='tasks.orchestration.aggregate_results', bind=True)
def aggregate_results(self, test_run_id, execution_results):
    """Aggregate results from multiple test executions."""

    from api.database import get_sync_db
    from models.test_run import TestRun

    db = get_sync_db()

    # STEP 1: Fetch test run
    test_run = db.query(TestRun).filter(TestRun.id == test_run_id).first()
    if not test_run:
        raise ValueError(f"Test run {test_run_id} not found")

    # STEP 2: Calculate statistics
    total = len(execution_results)
    passed = sum(1 for r in execution_results if r.get('status') == 'passed')
    failed = sum(1 for r in execution_results if r.get('status') == 'failed')
    skipped = total - passed - failed

    # STEP 3: Update test run
    test_run.passed_tests = passed
    test_run.failed_tests = failed
    test_run.skipped_tests = skipped

    if failed > 0:
        test_run.mark_as_failed()
    else:
        test_run.mark_as_completed()

    db.commit()

    # STEP 4: Trigger notifications
    from tasks.notifications import send_test_run_notification
    send_test_run_notification.delay(test_run_id)

    # STEP 5: Return summary
    return {
        'test_run_id': test_run_id,
        'total_tests': total,
        'passed': passed,
        'failed': failed,
        'skipped': skipped,
        'status': test_run.status,
        'summary': f"{passed}/{total} tests passed"
    }
```

**Acceptance Criteria**:
- [ ] Correctly counts passed/failed/skipped tests
- [ ] Updates test run status
- [ ] Triggers notifications
- [ ] Returns accurate summary
- [ ] Unit tests pass

**Time Estimate**: 0.5 days

---

### Week 2: Validation Pipeline & Integration

#### Task 2.1: Implement Validation Task Placeholders
**Files**: `backend/tasks/validation.py` (lines 200-346)
**Current State**: 4 tasks return placeholders ❌
**Target State**: All validation tasks functional

**Tasks to Implement**:

1. **`validate_test_result()`** (lines 200-214):
```python
def validate_test_result(self, execution_id, expected_result, actual_result):
    """Validate a test execution result."""

    from services.validation_service import ValidationService

    service = ValidationService()

    # Compare expected vs actual
    validation = service.compare_results(
        expected=expected_result,
        actual=actual_result
    )

    return {
        'validation_id': str(validation.id),
        'passed': validation.passed,
        'confidence': validation.confidence_score,
        'differences': validation.differences
    }
```

2. **`analyze_response_quality()`** (lines 217-257):
```python
def analyze_response_quality(self, execution_id, response_text, criteria=None):
    """Analyze the quality of a voice AI response."""

    from services.quality_analyzer import QualityAnalyzer

    analyzer = QualityAnalyzer()
    quality = analyzer.analyze(response_text, criteria)

    return {
        'quality_score': quality.overall_score,
        'metrics': quality.metrics_dict(),
        'recommendations': quality.recommendations
    }
```

3. **`validate_performance()`** (lines 260-301):
```python
def validate_performance(self, execution_id, performance_data, thresholds=None):
    """Validate performance metrics of test execution."""

    thresholds = thresholds or {
        'response_time': 3.0,  # seconds
        'processing_time': 2.0  # seconds
    }

    violations = []
    for metric, threshold in thresholds.items():
        actual = performance_data.get(metric, 0)
        if actual > threshold:
            violations.append({
                'metric': metric,
                'threshold': threshold,
                'actual': actual
            })

    return {
        'validation_id': str(uuid4()),
        'passed': len(violations) == 0,
        'violations': violations,
        'metrics_summary': performance_data
    }
```

4. **`generate_test_report()`** (lines 304-346):
```python
def generate_test_report(self, test_run_id, format='json', include_details=True):
    """Generate a comprehensive test report."""

    from services.report_generator import ReportGenerator
    from api.database import get_sync_db

    db = get_sync_db()
    generator = ReportGenerator(db)

    report = generator.generate(
        test_run_id=test_run_id,
        format=format,
        include_details=include_details
    )

    return {
        'report_id': str(report.id),
        'format': format,
        'url': report.url,
        'summary': report.summary_dict()
    }
```

**Acceptance Criteria**:
- [ ] All 4 validation tasks implemented
- [ ] No placeholder returns
- [ ] Unit tests pass
- [ ] Integration tests pass

**Time Estimate**: 2 days

---

#### Task 2.2: Test End-to-End Execution Flow
**Type**: Integration Testing
**Goal**: Verify complete workflow works

**Test Scenario**:
```python
# Create integration test: tests/integration/test_e2e_execution.py

@pytest.mark.asyncio
async def test_complete_voice_test_execution(db_session):
    """Test complete execution from test case to result."""

    # STEP 1: Create test case
    test_case = TestCase(
        name="Weather Query Test",
        scenario_definition={
            "input": "What's the weather in San Francisco?",
            "expected_intent": "weather_query",
            "expected_entities": ["location:San Francisco"]
        }
    )
    db_session.add(test_case)
    db_session.commit()

    # STEP 2: Create test run
    from tasks.orchestration import create_test_run
    result = create_test_run.delay(
        test_case_ids=[str(test_case.id)],
        languages=['en-US']
    )
    test_run_id = result.get()['test_run_id']

    # STEP 3: Wait for execution to complete (max 60 seconds)
    import time
    for _ in range(60):
        test_run = db_session.query(TestRun).get(test_run_id)
        if test_run.is_completed():
            break
        time.sleep(1)

    # STEP 4: Verify results
    assert test_run.is_completed()
    assert test_run.total_tests == 1
    assert test_run.passed_tests + test_run.failed_tests == 1

    # STEP 5: Verify execution record
    execution = db_session.query(VoiceTestExecution).filter_by(
        test_run_id=test_run_id
    ).first()
    assert execution is not None
    assert execution.status in ['passed', 'failed']

    # STEP 6: Verify audio was generated
    assert execution.audio_url is not None
    assert 'minio' in execution.audio_url or 's3' in execution.audio_url

    # STEP 7: Verify Houndify was called
    assert execution.response_entities is not None

    # STEP 8: Verify validation happened
    validation = db_session.query(ValidationResult).filter_by(
        execution_id=execution.id
    ).first()
    assert validation is not None
    assert validation.confidence_score > 0
```

**Acceptance Criteria**:
- [ ] Test case → Test run → Execution → Validation → Result
- [ ] Audio generated and stored
- [ ] Houndify called successfully
- [ ] Validation completed
- [ ] Test run marked complete
- [ ] E2E test passes

**Time Estimate**: 1 day

---

### Week 1-2 Deliverable Checklist

By end of Week 2, you should have:
- [x] ~~Phase 1 scope defined~~ ✅
- [ ] Test orchestration working (`create_test_run`, `schedule_test_executions`, `aggregate_results`)
- [ ] Voice execution task created and functional
- [ ] TTS audio generation working
- [ ] MinIO storage operational
- [ ] Houndify API calls happening in workflow
- [ ] Validation tasks implemented (basic)
- [ ] E2E test passing: test case → execution → result
- [ ] Can execute 1 voice test end-to-end manually

**Success Metric**: Execute a single voice test via API and get back actual results (not placeholders)

---

## Phase 2: ML Validation & Accuracy (Week 3)
**Priority**: 🔴 HIGH
**Goal**: Automated validation achieves >85% accuracy

### Task 2.1: Load Sentence-Transformers Model
**File**: `backend/services/validation_service.py`
**Estimated Time**: 1 day

### Task 2.2: Implement Semantic Similarity Matching
**File**: `backend/services/validation_service.py`
**Estimated Time**: 2 days

### Task 2.3: Tune Confidence Thresholds
**Type**: Calibration & Testing
**Estimated Time**: 2 days

**Deliverable**: Automated validation working with >85% accuracy

---

## Phase 3: Integrations & Polish (Week 4)
**Priority**: 🟡 MEDIUM
**Goal**: External systems connected, dashboards show real data

### Task 3.1: Wire Jira Integration
**File**: `backend/integrations/jira/client.py`
**Estimated Time**: 1 day

### Task 3.2: Wire Slack Notifications
**File**: `backend/integrations/slack/client.py`
**Estimated Time**: 0.5 days

### Task 3.3: Connect GitHub Webhooks
**File**: `backend/api/routes/webhooks.py`
**Estimated Time**: 1 day

### Task 3.4: Connect Dashboards to Real Data
**File**: `frontend/src/pages/Dashboard/`
**Estimated Time**: 1 day

### Task 3.5: Add Demo Seed Data
**Type**: Data population
**Estimated Time**: 0.5 days

**Deliverable**: Fully integrated MVP ready for pilot

---

## Phase 4: Scale & Optimize (Weeks 5-6, Optional)
**Priority**: 🟢 LOW
**Goal**: Performance at scale

### Task 4.1: Load Testing (1000+ tests/day)
**Estimated Time**: 2 days

### Task 4.2: Parallel Execution Optimization
**Estimated Time**: 2 days

### Task 4.3: Fine-tune to 99.7% Accuracy
**Estimated Time**: 3 days

**Deliverable**: Production-ready, optimized system

---

## Current Focus: Week 1 - Test Orchestration

### What We're Tackling First:

1. ✅ **Create execution plan** (this document) - DONE
2. ⏳ **Implement `create_test_run()`** - IN PROGRESS
3. ⏳ **Implement `schedule_test_executions()`** - NEXT
4. ⏳ **Create `execute_voice_test()` task** - NEXT
5. ⏳ **Wire up TTS audio generation** - NEXT
6. ⏳ **Implement MinIO storage** - NEXT
7. ⏳ **Test end-to-end** - NEXT

### Daily Checkpoints:
- **Day 1**: `create_test_run()` functional
- **Day 2**: `schedule_test_executions()` + `execute_voice_test()` functional
- **Day 3**: TTS audio generation working
- **Day 4**: MinIO storage operational
- **Day 5**: Houndify calls happening, E2E test passing

---

## Risk Mitigation

### Risk 1: Houndify API Credentials Missing
**Likelihood**: HIGH
**Impact**: CRITICAL
**Mitigation**: Use `MockHoundifyClient` for development, get real credentials before Week 2

### Risk 2: TTS Audio Quality Issues
**Likelihood**: MEDIUM
**Impact**: MEDIUM
**Mitigation**: Start with gTTS (simple), upgrade to better TTS later if needed

### Risk 3: MinIO Configuration Issues
**Likelihood**: LOW
**Impact**: MEDIUM
**Mitigation**: MinIO already running in Docker, just need to wire up client

### Risk 4: Celery Tasks Not Processing
**Likelihood**: MEDIUM
**Impact**: HIGH
**Mitigation**: RabbitMQ already running, verify Celery workers are started

---

## Success Metrics

### Week 1 Success:
- [ ] Can create test run via API
- [ ] Celery tasks appear in RabbitMQ
- [ ] At least 1 test execution attempted (even if it fails)

### Week 2 Success:
- [ ] Can execute 1 voice test end-to-end
- [ ] Audio stored in MinIO
- [ ] Houndify API called
- [ ] Validation result stored
- [ ] Test run marked complete

### Week 3 Success:
- [ ] Automated validation >85% accurate
- [ ] Human validation queue operational

### Week 4 Success:
- [ ] All integrations working
- [ ] Real data in dashboards
- [ ] Can demo to stakeholders

---

## Next Immediate Steps

1. **Start with `create_test_run()`** - This is the entry point
2. **Set up development environment** - Ensure all Docker services running
3. **Verify Celery workers** - Make sure task processing works
4. **Test incrementally** - Don't wait until end to test
5. **Use TDD** - Write test first, then implementation (follow existing pattern)

---

**Ready to start? Let's implement `create_test_run()` first!**
