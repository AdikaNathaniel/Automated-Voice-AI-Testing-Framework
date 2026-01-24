# Multi-Language Scenario Execution & Edge Case System Documentation

This document provides comprehensive technical documentation for two core systems in the Voice AI Automated Testing Framework:
1. **Multi-Language Scenario Execution** - How scenarios with multiple language variants are stored, selected, and executed
2. **Edge Case System** - How edge cases are detected, categorized, grouped into patterns, and managed

---

## Table of Contents

1. [Multi-Language Scenario Execution](#multi-language-scenario-execution)
   - [Data Model](#1-data-model)
   - [Frontend Language Selection](#2-frontend-language-selection)
   - [API Layer](#3-api-layer)
   - [Backend Execution Service](#4-backend-execution-service)
   - [Complete Flow Diagram](#5-complete-flow-diagram)
2. [Edge Case System](#edge-case-system)
   - [What Triggers Edge Case Auto-Creation](#1-what-triggers-edge-case-auto-creation)
   - [Edge Case Data Model](#2-edge-case-data-model)
   - [Pattern Groups](#3-pattern-groups)
   - [Edge Case Detection Service](#4-edge-case-detection-service)
   - [Edge Case Similarity Service](#5-edge-case-similarity-service)
   - [LLM-Enhanced Pattern Recognition](#6-llm-enhanced-pattern-recognition)
   - [Complete Edge Case Flow](#7-complete-edge-case-flow)

---

# Multi-Language Scenario Execution

## 1. Data Model

### The Key Insight

Language variants are stored **INSIDE each step's metadata**, NOT as separate ScenarioStep records. This is critical to understand.

### Correct Structure

Each ScenarioStep has a `step_metadata` JSONB field containing a `language_variants` array:

```python
# File: backend/scripts/seed_morning_routine_fixed.py (lines 105-124)

step1 = ScenarioStep(
    script_id=scenario.id,
    step_order=1,
    user_utterance="What's the weather in San Francisco today?",  # Primary/default utterance
    step_metadata={
        "primary_language": "en-US",
        "variant_group": "weather_check",
        "context": "User checks weather to decide what to wear",
        "language_variants": [
            {
                "language_code": "en-US",
                "user_utterance": "What's the weather in San Francisco today?"
            },
            {
                "language_code": "fr-FR",
                "user_utterance": "Quel temps fait-il a San Francisco aujourd'hui?"
            }
        ]
    }
)
```

### Database Structure

For a 3-step bilingual scenario:
- **ScenarioScript** table: 1 record (the scenario)
- **ScenarioStep** table: 3 records (one per step_order)
- Language variants: Stored in `step_metadata` JSONB column

**NOT** 6 separate ScenarioStep records (which would be incorrect).

### TypeScript Types

```typescript
// File: frontend/src/types/multiTurn.ts (lines 11-23)

export interface LanguageVariant {
  language_code: string;
  user_utterance: string;
}

export interface StepMetadata {
  is_single_turn?: boolean;
  primary_language?: string;
  language_variants?: LanguageVariant[];
  dialog_phase?: string;
  slot_to_collect?: string;
  [key: string]: any;
}
```

---

## 2. Frontend Language Selection

### 2.1 Scenario List Page - Modal Selection

When a user clicks "Execute" on a multi-language scenario from the list, a modal appears for language selection.

```typescript
// File: frontend/src/pages/Scenarios/ScenarioList.tsx (lines 30-32)

// State for language selection modal
const [executeModal, setExecuteModal] = useState<ScenarioScript | null>(null);
const [selectedLanguages, setSelectedLanguages] = useState<string[]>([]);
```

```typescript
// File: frontend/src/pages/Scenarios/ScenarioList.tsx (lines 53-61)

const handleExecuteClick = (scenario: ScenarioScript) => {
  // If scenario has multiple languages, show selection modal
  if (scenario.languages && scenario.languages.length > 1) {
    setExecuteModal(scenario);     // Show the modal
    setSelectedLanguages([]);       // Empty array = ALL languages
  } else {
    // Single language or no languages - execute directly
    handleExecuteScenario(scenario.id);
  }
};
```

**Key Behavior:**
- `selectedLanguages = []` (empty array) means "execute ALL language variants"
- `selectedLanguages = ["en-US"]` means "execute only English"
- `selectedLanguages = ["en-US", "fr-FR"]` means "execute both"

### 2.2 Scenario Detail Page - LanguageSelector Component

On the scenario detail page, a LanguageSelector component is positioned below the header:

```typescript
// File: frontend/src/pages/Scenarios/ScenarioDetail.tsx (lines 143-150)

const handleExecute = async () => {
  if (!id) return;

  try {
    const result = await multiTurnService.executeScenario(id, {
      script_id: id,
      language_codes: selectedLanguages.length > 0 ? selectedLanguages : undefined,
    });
    navigate(`/scenarios/executions/${result.execution_id}`);
  } catch (err: any) {
    showError(`Failed to execute scenario: ${err.message}`);
  }
};
```

### 2.3 LanguageSelector Component

```typescript
// File: frontend/src/components/common/LanguageSelector.tsx (lines 30-67)

const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  languages,
  value,
  onChange,
  label = 'Language',
  helperText,
  includeAllOption = false,
  disabled = false,
}) => {
  // Special token for "All languages" option
  const ALL_LANG_VALUE = '__ALL_LANGUAGES__';

  const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selected = event.target.value;
    if (selected === ALL_LANG_VALUE) {
      onChange(null);  // null = all languages
      return;
    }
    onChange(selected);
  };
  // ... render dropdown
};
```

---

## 3. API Layer

### 3.1 Frontend Service

```typescript
// File: frontend/src/services/multiTurn.service.ts (lines 162-171)

async executeScenario(
  scriptId: string,
  request?: ExecuteScenarioRequest
): Promise<ExecuteScenarioResponse> {
  const response = await apiClient.post<{ success: boolean; data: ExecuteScenarioResponse }>(
    `${this.baseUrl}/execute/${scriptId}`,
    request || {}
  );
  return response.data.data;
}
```

### 3.2 Request Type

```typescript
// File: frontend/src/types/multiTurn.ts (lines 110-113)

export interface ExecuteScenarioRequest {
  script_id: string;
  language_codes?: string[];  // Optional - undefined = all languages
}
```

### 3.3 Backend Request Schema

```python
# File: backend/api/routes/multi_turn.py (lines 56-66)

class ExecuteScenarioRequest(BaseModel):
    """Request model for executing a scenario."""
    language_codes: Optional[List[str]] = Field(
        None,
        description="Optional list of language codes to execute. If omitted, executes all language variants. "
                    "Examples: ['en-US'], ['fr-FR'], ['en-US', 'fr-FR']"
    )
    suite_run_id: Optional[UUID] = Field(
        None,
        description="Optional suite run ID to associate execution with"
    )
```

### 3.4 Backend Endpoint

```python
# File: backend/api/routes/multi_turn.py (lines 948-1047)

@router.post(
    "/execute/{script_id}",
    response_model=SuccessResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Execute multi-turn scenario",
    description="Execute a multi-turn conversation scenario with optional language filtering"
)
async def execute_multi_turn_scenario(
    script_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
    background_tasks: BackgroundTasks,
    request_body: ExecuteScenarioRequest = Body(default=ExecuteScenarioRequest()),
) -> SuccessResponse:
    # Extract language_codes from request
    language_codes = request_body.language_codes

    # ... create suite run if needed ...

    # Execute with language filtering
    execution = await service.execute_scenario(
        db=db,
        script_id=script_id,
        suite_run_id=suite_run_id,
        socketio=sio,
        language_codes=language_codes  # <-- Passed to service
    )
```

---

## 4. Backend Execution Service

### 4.1 Main Execute Method

```python
# File: backend/services/multi_turn_execution_service.py (lines 85-126)

async def execute_scenario(
    self,
    db: AsyncSession,
    script_id: UUID,
    suite_run_id: UUID,
    socketio=None,
    language_codes: Optional[List[str]] = None,  # <-- Language filter
    suite_id: Optional[UUID] = None
) -> MultiTurnExecution:
    """
    Execute a complete multi-turn scenario.

    Args:
        language_codes: Optional list of language codes to execute (e.g., ["en-US", "fr-FR"])
                      If None, executes all language variants
                      If ["en-US"], executes only English variants
                      If ["en-US", "fr-FR"], executes both
    """
    # 1. Load scenario script with steps
    script = await self._load_script(db, script_id)

    # 2. Create multi-turn execution record
    execution = await self._create_execution(db, script, suite_run_id, suite_id)

    # 3. Execute each step in sequence WITH language filtering
    await self._execute_steps(db, execution, script, socketio, language_codes)
```

### 4.2 Step Filtering (Does NOT Filter Steps)

**Important:** Steps are NOT filtered. ALL steps are executed. Filtering happens at the variant level.

```python
# File: backend/services/multi_turn_execution_service.py (lines 226-251)

def _filter_steps_by_language(
    self,
    steps: List[ScenarioStep],
    language_codes: Optional[List[str]] = None
) -> List[ScenarioStep]:
    """
    Return all steps sorted by step_order.

    IMPORTANT: Language filtering happens at the variant level inside
    _get_language_variants, NOT at the step level. Each step_order should
    have exactly ONE ScenarioStep record, with language variants stored
    in step_metadata['language_variants'].
    """
    if not steps:
        return []

    # Simply return all steps sorted by step_order
    # Language filtering happens in _get_language_variants
    return sorted(steps, key=lambda s: s.step_order)
```

### 4.3 Language Variant Extraction (WHERE FILTERING HAPPENS)

This is the critical method where language filtering actually occurs:

```python
# File: backend/services/multi_turn_execution_service.py (lines 1258-1319)

def _get_language_variants(
    self,
    script: ScenarioScript,
    step: ScenarioStep,
    language_codes: Optional[List[str]] = None
) -> Dict[str, str]:
    """
    Extract language variants from step metadata, optionally filtering by language_codes.

    Returns a dictionary mapping language codes to user utterances.

    Args:
        script: Scenario script
        step: Scenario step
        language_codes: Optional list of language codes to include.
                       None = include all variants
                       ["en-US"] = include only English
                       ["en-US", "fr-FR"] = include both

    Returns:
        Dictionary mapping language codes to utterances
        Example: {
            "en-US": "What's the weather?",
            "fr-FR": "Quel temps fait-il?"
        }
    """
    step_metadata = step.step_metadata or {}

    # Check for language_variants array in metadata
    if 'language_variants' in step_metadata:
        variants = step_metadata['language_variants']
        if isinstance(variants, list) and len(variants) > 0:
            # Convert array to dict, FILTERING by language_codes if specified
            result = {}
            for variant in variants:
                if isinstance(variant, dict):
                    lang_code = variant.get('language_code')
                    utterance = variant.get('user_utterance')
                    if lang_code and utterance:
                        # *** THIS IS WHERE FILTERING HAPPENS ***
                        if language_codes is None or lang_code in language_codes:
                            result[lang_code] = utterance

            if result:
                return result

    # Fallback: single language from primary_language
    primary_lang = self._get_language_code(script, step)
    return {primary_lang: step.user_utterance}
```

### 4.4 Step Execution

Each step iterates over filtered language variants:

```python
# File: backend/services/multi_turn_execution_service.py (lines 362-398)

async def _execute_step(
    self,
    db: AsyncSession,
    execution: MultiTurnExecution,
    step: ScenarioStep,
    conversation_state: Optional[Dict[str, Any]],
    script: ScenarioScript,
    language_codes: Optional[List[str]] = None  # <-- Passed through
) -> Dict[str, Any]:
    """Execute a single step in the scenario."""

    # Get language variants FILTERED by language_codes
    language_variants = self._get_language_variants(script, step, language_codes)
    logger.info(f"Found {len(language_variants)} language variant(s): {list(language_variants.keys())}")

    # Generate and upload audio for EACH language variant
    for lang_code, utterance in language_variants.items():
        # Generate TTS audio
        audio_data = self.tts_service.text_to_speech(text=utterance, lang=lang_code.split('-')[0])

        # Upload to storage
        audio_url = await self._upload_audio_to_storage(audio_data, execution.id, step.step_order, lang_code)

        # Send to Houndify for validation
        response = await self.houndify_client.voice_query(audio_data=pcm_audio, ...)

        # Validate response
        validation_result = await self._validate_step(...)

        # Create ValidationResult for this language
        validation_result_obj = ValidationResult(
            language_code=lang_code,  # Track which language
            ...
        )
```

---

## 5. Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. User clicks "Execute" on ScenarioList or ScenarioDetail                 │
│                         ↓                                                   │
│  2. If scenario.languages.length > 1:                                       │
│     → Show language selection modal/selector                                │
│     → User selects: [] (all), ["en-US"], or ["en-US", "fr-FR"]              │
│                         ↓                                                   │
│  3. Call multiTurnService.executeScenario(scriptId, { language_codes })     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
                          HTTP POST /api/v1/multi-turn/execute/{script_id}
                          Body: { "language_codes": ["en-US"] }
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BACKEND API                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  4. ExecuteScenarioRequest.language_codes parsed from request body          │
│                         ↓                                                   │
│  5. service.execute_scenario(db, script_id, ..., language_codes)            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                     MULTI-TURN EXECUTION SERVICE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  6. Load script with steps (all 3 steps for 3-step scenario)                │
│                         ↓                                                   │
│  7. _filter_steps_by_language() → Returns ALL steps (sorted)                │
│     (Filtering does NOT happen here)                                        │
│                         ↓                                                   │
│  8. FOR EACH step in sorted_steps:                                          │
│     │                                                                       │
│     ├─→ 9. _get_language_variants(script, step, language_codes)             │
│     │       → Reads step.step_metadata['language_variants']                 │
│     │       → FILTERS: if language_codes is None OR lang in language_codes  │
│     │       → Returns: {"en-US": "What's the weather?"}                     │
│     │                                                                       │
│     ├─→ 10. FOR EACH (lang_code, utterance) in filtered_variants:           │
│     │       │                                                               │
│     │       ├─→ Generate TTS audio for utterance                            │
│     │       ├─→ Upload audio to S3/MinIO                                    │
│     │       ├─→ Send to Houndify for voice recognition                      │
│     │       ├─→ Validate response against ExpectedOutcome                   │
│     │       └─→ Create ValidationResult with language_code                  │
│     │                                                                       │
│     └─→ 11. Create StepExecution record with all language results           │
│                                                                             │
│  12. Mark execution as completed                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# Edge Case System

## 1. What Triggers Edge Case Auto-Creation

### The Trigger: Human Validation Decision

Edge cases are **automatically created** when a human validator reviews a validation result and selects **"edge_case"** as their decision.

```python
# File: backend/services/human_validation_service.py (lines 73-83)

# Auto-create edge case if decision is "edge_case"
edge_case_id = None
if validation_data.validation_decision == "edge_case":
    edge_case = await self._create_edge_case_entry(
        db=db,
        queue_item=queue_item,
        validator_id=validator_id,
        feedback=validation_data.feedback,
        human_validation_id=human_validation.id,
    )
    edge_case_id = str(edge_case.id)
```

### The Complete Flow

1. **Scenario Execution** → ValidationResult created with `review_status = "needs_review"`
2. **ValidationResult** → Queued in `validation_queue` table for human review
3. **Human Validator** → Claims the queue item, reviews it
4. **Validator Decision** → Selects one of:
   - `"pass"` - AI response was correct
   - `"fail"` - AI response was incorrect
   - `"edge_case"` - This is a tricky scenario worth documenting ← **TRIGGER**
5. **If "edge_case"** → `HumanValidationService._create_edge_case_entry()` is called

### What Gets Created

```python
# File: backend/services/human_validation_service.py (lines 168-250)

async def _create_edge_case_entry(
    self,
    db: AsyncSession,
    queue_item: ValidationQueue,
    validator_id: UUID,
    feedback: Optional[str],
    human_validation_id: UUID,
) -> EdgeCase:
    """Automatically create an edge case library entry from validation decision."""

    # Get validation result and related scenario
    validation_result = await db.execute(
        select(ValidationResult).where(ValidationResult.id == queue_item.validation_result_id)
    )
    # ... load relationships ...

    # Auto-generate title
    title = f"Edge Case: {scenario.name} - Step {queue_item.step_order}"

    # Build comprehensive scenario definition (JSONB)
    scenario_definition = {
        "scenario_id": str(scenario.id),
        "scenario_name": scenario.name,
        "scenario_description": scenario.description,
        "step_order": queue_item.step_order,
        "user_utterance": queue_item.user_utterance,
        "expected_response": queue_item.expected_response,
        "actual_response": queue_item.actual_response,
        "language_code": queue_item.language_code,
        "validation_result_id": str(validation_result.id),
        "human_validation_id": str(human_validation_id),
        "confidence_score": validation_result.confidence_score,
        "review_status": validation_result.review_status,
        "multi_turn_execution_id": str(multi_turn_execution.id),
    }

    # Auto-detect category using EdgeCaseDetectionService
    category = await self.detection_service.detect_category(validation_result)

    # Auto-determine severity
    severity = self.detection_service.determine_severity(validation_result, category)

    # Auto-generate tags
    tags = await self.detection_service.generate_tags(validation_result, db)

    # Create the EdgeCase record
    edge_case = EdgeCase(
        title=title,
        description=feedback or "Automatically created from human validation.",
        scenario_definition=scenario_definition,
        tags=tags,
        severity=severity,
        category=category,
        status="new",
        script_id=scenario.id,
        discovered_date=date.today(),
        discovered_by=validator_id,
        human_validation_id=human_validation_id,
        validation_result_id=validation_result.id,
        auto_created=True,  # <-- Marked as auto-created
    )

    db.add(edge_case)
    return edge_case
```

---

## 2. Edge Case Data Model

```python
# File: backend/models/edge_case.py (lines 25-145)

class EdgeCase(Base):
    """ORM representation of curated edge cases discovered during testing."""

    __tablename__ = "edge_cases"

    # Primary Key
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)

    # Core Fields
    title = Column(String(255), nullable=False)
    # Human-readable summary, e.g., "Edge Case: Morning Routine - Step 2"

    description = Column(Text, nullable=True)
    # Detailed narrative describing the unexpected behaviour
    # Contains validator feedback if auto-created

    category = Column(String(100), nullable=True)
    # Categories: audio_quality, ambiguity, context_loss, localization,
    #             high_confidence_failure, low_confidence, boundary_condition

    severity = Column(String(50), nullable=True)
    # Impact level: critical, high, medium, low

    scenario_definition = Column(JSONB, nullable=False)
    # Structured definition with:
    # - scenario_id, scenario_name, scenario_description
    # - step_order, user_utterance
    # - expected_response, actual_response
    # - language_code, confidence_score
    # - validation_result_id, human_validation_id

    # Relationships
    script_id = Column(GUID(), ForeignKey("scenario_scripts.id", ondelete='SET NULL'))
    # Link to the ScenarioScript that exhibited this edge case

    discovered_by = Column(GUID(), ForeignKey("users.id", ondelete='SET NULL'))
    # User (validator) who identified the edge case

    human_validation_id = Column(GUID(), ForeignKey("human_validations.id", ondelete='SET NULL'))
    # Link to the HumanValidation record that triggered creation

    validation_result_id = Column(GUID(), ForeignKey("validation_results.id", ondelete='SET NULL'))
    # Link to the ValidationResult being documented

    # Metadata
    discovered_date = Column(Date, nullable=True)
    # When the edge case was first reported

    status = Column(String(50), default="active")
    # Lifecycle: new, active, grouped, resolved, wont_fix

    tags = Column(ARRAY(Text), default=list)
    # Custom tags for searching: ["en-US", "category:weather", "low-confidence"]

    auto_created = Column(Boolean, default=False)
    # True if created automatically from validation decision
    # False if manually created via EdgeCaseCreate page

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

---

## 3. Pattern Groups

Edge cases can be grouped into patterns when multiple similar edge cases are detected.

### PatternGroup Model

```python
# File: backend/models/pattern_group.py (lines 21-138)

class PatternGroup(Base):
    """
    A PatternGroup identifies a recurring pattern across multiple edge cases.

    Examples:
    - Time zone confusion ("tomorrow" vs "today")
    - Ambiguous numbers ("8" could be time or quantity)
    - Regional dialect issues (UK vs US English)
    """

    __tablename__ = "pattern_groups"

    id = Column(GUID(), primary_key=True)

    name = Column(String(200), nullable=False)
    # e.g., "Time Reference Confusion", "Numeric Ambiguity"

    description = Column(Text, nullable=True)
    # Detailed explanation of what the pattern represents

    pattern_type = Column(String(100), nullable=True)
    # Type: semantic, entity, context, ambiguity, boundary, mixed

    severity = Column(String(50), default="medium")
    # Based on occurrence count: critical (10+), high (5+), medium (3+), low

    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    # When this pattern was first detected

    last_seen = Column(DateTime(timezone=True), onupdate=func.now())
    # When this pattern was most recently observed

    occurrence_count = Column(Integer, default=0)
    # Total number of edge cases matching this pattern

    status = Column(String(50), default="active")
    # Lifecycle: active, resolved, monitoring

    suggested_actions = Column(JSONB, nullable=True)
    # Recommendations: ["Review similar edge cases", "Update validation thresholds"]

    pattern_metadata = Column(JSONB, nullable=True)
    # Additional data:
    # - sample_utterances: first 5 example utterances
    # - affected_languages: ["en-US", "fr-FR"]
    # - avg_confidence: average confidence score
    # - keywords: LLM-extracted keywords
    # - root_cause: LLM-identified root cause
    # - llm_generated: true if LLM enhanced
```

### EdgeCasePatternLink (Many-to-Many)

```python
# File: backend/models/pattern_group.py (lines 177-271)

class EdgeCasePatternLink(Base):
    """
    Association table linking edge cases to pattern groups.

    An edge case can match multiple patterns.
    A pattern can contain multiple edge cases.
    """

    __tablename__ = "edge_case_pattern_links"

    id = Column(GUID(), primary_key=True)

    edge_case_id = Column(GUID(), ForeignKey("edge_cases.id", ondelete="CASCADE"))
    # Reference to the edge case

    pattern_group_id = Column(GUID(), ForeignKey("pattern_groups.id", ondelete="CASCADE"))
    # Reference to the pattern group

    similarity_score = Column(Float, nullable=True)
    # How closely this edge case matches the pattern (0.0-1.0)

    added_at = Column(DateTime(timezone=True), server_default=func.now())
    # When this edge case was added to the pattern group

    # Unique constraint: one edge case can only be linked once per pattern
    __table_args__ = (
        UniqueConstraint("edge_case_id", "pattern_group_id", name="uix_edge_case_pattern"),
    )
```

---

## 4. Edge Case Detection Service

Automatically detects categories and generates metadata for edge cases.

### Category Detection

```python
# File: backend/services/edge_case_detection_service.py (lines 23-66)

async def detect_category(self, validation_result: ValidationResult) -> str:
    """
    Auto-detect edge case category based on validation scores and context.

    Categories:
    - high_confidence_failure: High confidence (≥0.8) but needs review
      → AI was confident but wrong - most serious

    - low_confidence: Very low confidence (<0.4)
      → AI wasn't sure - expected to need review

    - boundary_condition: Scores near threshold (0.45-0.55)
      → Edge of pass/fail threshold - ambiguous

    - ambiguous_intent: (future) Low intent match, high semantic similarity

    - language_specific: (future) Specific to certain language/region

    - context_dependent: (future) Multi-turn context issues

    - needs_classification: Default fallback
    """
    confidence = validation_result.confidence_score or 0
    review_status = validation_result.review_status or ""

    # High confidence failures are the most concerning
    if confidence >= 0.8 and review_status == "needs_review":
        return "high_confidence_failure"

    # Low confidence is expected to be uncertain
    if confidence < 0.4:
        return "low_confidence"

    # Boundary conditions are near the threshold
    if 0.45 <= confidence <= 0.55:
        return "boundary_condition"

    return "needs_classification"
```

### Severity Determination

```python
# File: backend/services/edge_case_detection_service.py (lines 128-156)

def determine_severity(self, validation_result: ValidationResult, category: str) -> str:
    """
    Determine severity level based on category.

    Severity Mapping:
    - high_confidence_failure → "high"    (AI was confidently wrong)
    - boundary_condition      → "medium"  (ambiguous, near threshold)
    - low_confidence          → "low"     (expected uncertainty)
    - other                   → "medium"  (default)
    """
    if category == "high_confidence_failure":
        return "high"

    if category == "boundary_condition":
        return "medium"

    if category == "low_confidence":
        return "low"

    return "medium"
```

### Tag Generation

```python
# File: backend/services/edge_case_detection_service.py (lines 68-126)

async def generate_tags(self, validation_result: ValidationResult, db: AsyncSession) -> List[str]:
    """
    Generate relevant tags based on validation result patterns.

    Tags Generated:
    1. Language code: "en-US", "fr-FR"
    2. Scenario category: "category:weather", "category:calendar"
    3. Existing scenario tags (first 3)
    4. Confidence level: "very-low-confidence", "low-confidence", "high-confidence"
    5. Review status: "review:needs_review", "review:auto_pass"

    Returns up to 10 unique tags.
    """
    tags: List[str] = []

    # Get related execution and scenario
    await db.refresh(validation_result, ["multi_turn_execution"])
    multi_turn_execution = validation_result.multi_turn_execution

    if multi_turn_execution:
        # Add language tag
        if multi_turn_execution.language_code:
            tags.append(multi_turn_execution.language_code)

        # Get scenario for category tags
        await db.refresh(multi_turn_execution, ["scenario"])
        scenario = multi_turn_execution.scenario

        if scenario and scenario.script_metadata:
            if scenario.script_metadata.get("category"):
                tags.append(f"category:{scenario.script_metadata['category']}")

            # Add existing scenario tags (limit 3)
            if scenario.script_metadata.get("tags"):
                tags.extend(scenario.script_metadata["tags"][:3])

    # Confidence level tags
    confidence = validation_result.confidence_score or 0
    if confidence < 0.3:
        tags.append("very-low-confidence")
    elif confidence < 0.5:
        tags.append("low-confidence")
    elif confidence > 0.8:
        tags.append("high-confidence")

    # Review status tag
    if validation_result.review_status:
        tags.append(f"review:{validation_result.review_status}")

    # Deduplicate and limit to 10
    return list(dict.fromkeys(tags))[:10]
```

---

## 5. Edge Case Similarity Service

Finds similar edge cases and groups them into patterns.

### Multi-Signal Similarity Calculation

```python
# File: backend/services/edge_case_similarity_service.py (lines 120-173)

def _calculate_similarity(self, case1: EdgeCase, case2: EdgeCase) -> float:
    """
    Calculate overall similarity score between two edge cases.

    Combines multiple signals with weighted average:
    - Semantic similarity: 40% (sentence transformer embeddings)
    - Category match:      20% (exact category match)
    - Language match:      15% (language code match)
    - Confidence similar:  10% (proximity of confidence scores)
    - Tag overlap:         15% (Jaccard similarity of tags)

    Returns: 0.0 to 1.0
    """
    weights = {
        'semantic': 0.40,
        'category': 0.20,
        'language': 0.15,
        'confidence': 0.10,
        'tags': 0.15
    }

    scores = {
        'semantic': self._semantic_similarity(case1, case2),
        'category': self._category_similarity(case1, case2),
        'language': self._language_similarity(case1, case2),
        'confidence': self._confidence_similarity(case1, case2),
        'tags': self._tag_similarity(case1, case2)
    }

    # Weighted average
    return sum(scores[key] * weights[key] for key in weights)
```

### Semantic Similarity (SentenceTransformer)

```python
# File: backend/services/edge_case_similarity_service.py (lines 175-208)

def _semantic_similarity(self, case1: EdgeCase, case2: EdgeCase) -> float:
    """
    Calculate semantic similarity between user utterances.

    Uses sentence-transformers for embedding generation and
    cosine similarity for comparison.

    Model configured via: settings.SEMANTIC_SIMILARITY_MODEL
    """
    # Extract utterances from scenario definitions
    utterance1 = case1.scenario_definition.get('user_utterance', '')
    utterance2 = case2.scenario_definition.get('user_utterance', '')

    if not utterance1 or not utterance2:
        return 0.0

    # Generate embeddings using lazy-loaded model
    embeddings = self.model.encode([utterance1, utterance2])

    # Cosine similarity
    similarity = np.dot(embeddings[0], embeddings[1]) / (
        np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
    )

    # Convert from [-1, 1] to [0, 1]
    return (similarity + 1) / 2
```

### Tag Similarity (Jaccard)

```python
# File: backend/services/edge_case_similarity_service.py (lines 284-313)

def _tag_similarity(self, case1: EdgeCase, case2: EdgeCase) -> float:
    """
    Calculate Jaccard similarity of tags.

    Jaccard Index = |intersection| / |union|

    Example:
    - case1.tags = ["en-US", "weather", "low-confidence"]
    - case2.tags = ["en-US", "calendar", "low-confidence"]
    - intersection = {"en-US", "low-confidence"} = 2
    - union = {"en-US", "weather", "calendar", "low-confidence"} = 4
    - Jaccard = 2/4 = 0.5
    """
    tags1 = set(case1.tags or [])
    tags2 = set(case2.tags or [])

    if not tags1 or not tags2:
        return 0.0

    intersection = len(tags1 & tags2)
    union = len(tags1 | tags2)

    return intersection / union if union > 0 else 0.0
```

---

## 6. LLM-Enhanced Pattern Recognition

The system uses an **LLM-first approach** with semantic similarity as a fallback.

### Priority Order

1. **LLM-based analysis (PRIMARY)** - Uses AI to understand patterns semantically
2. **Semantic similarity (FALLBACK)** - Used only if LLM fails or is unavailable

### Main Entry Point

```python
# File: backend/services/edge_case_similarity_service.py

async def analyze_and_group(
    self,
    edge_case: EdgeCase,
    threshold: float = 0.80
) -> Optional[PatternGroup]:
    """
    Main entry point for pattern recognition.

    PRIORITY ORDER:
    1. LLM-based analysis (PRIMARY) - Uses AI to understand patterns
    2. Semantic similarity (FALLBACK) - Used only if LLM fails or unavailable
    """
    # Try LLM-first approach
    if self.use_llm and self.llm_service:
        try:
            result = await self._analyze_with_llm_primary(edge_case)
            if result:
                return result
        except Exception as e:
            logger.warning(f"LLM-first approach failed: {e}, using semantic fallback")

    # Fallback to semantic similarity approach
    return await self._group_with_semantic_similarity(edge_case, threshold)
```

### LLM-Primary Analysis Flow

```python
async def _analyze_with_llm_primary(self, edge_case: EdgeCase) -> Optional[PatternGroup]:
    """
    LLM-primary pattern recognition.

    Steps:
    1. LLM analyzes the edge case FIRST (understanding the failure pattern)
    2. LLM matches against existing patterns (semantic understanding)
    3. Find similar cases using semantic similarity (LLM guides the search)
    4. Create new pattern if 3+ similar cases found (LLM generates details)
    """
    # Step 1: LLM analyzes the edge case FIRST
    llm_analysis = await self.llm_service.analyze_edge_case(edge_case)

    # Step 2: Check if matches existing pattern (LLM decides)
    existing_patterns = await self._get_active_patterns()
    if existing_patterns:
        pattern_match = await self.llm_service.match_to_existing_pattern(
            edge_case, llm_analysis, existing_patterns
        )
        if pattern_match.matches and pattern_match.confidence > 0.70:
            # Add to existing pattern
            pattern = await self._get_pattern_by_id(pattern_match.pattern_id)
            if pattern:
                await self._add_to_existing_pattern(edge_case, pattern)
                return pattern

    # Step 3: Find similar cases (semantic assists LLM)
    similar_results = await self.find_similar_edge_cases(
        edge_case,
        threshold=0.75,  # Lower threshold when LLM guides
        limit=20,
        time_window_days=30
    )
    similar_cases = [edge_case] + [r['edge_case'] for r in similar_results]

    # Step 4: Create new pattern if enough similar cases
    if len(similar_cases) >= 3:
        return await self._create_pattern_with_llm(similar_cases, llm_analysis)

    return None
```

### Semantic Similarity Fallback

```python
async def _group_with_semantic_similarity(
    self,
    edge_case: EdgeCase,
    threshold: float = 0.80
) -> Optional[PatternGroup]:
    """
    Semantic similarity fallback for pattern recognition.

    Used when:
    - LLM service is not configured (use_llm=False)
    - LLM service fails
    - LLM analysis doesn't find patterns
    """
    similar_results = await self.find_similar_edge_cases(
        edge_case,
        threshold=threshold,  # Stricter threshold without LLM
        limit=20,
        time_window_days=30
    )
    similar_cases = [edge_case] + [r['edge_case'] for r in similar_results]

    if len(similar_cases) >= 3:
        return await self.find_or_create_pattern_group(edge_cases=similar_cases)

    return None
```

### LLM-Generated Pattern Details

```python
# File: backend/services/edge_case_similarity_service.py (lines 614-672)

async def _create_pattern_with_llm(
    self,
    edge_cases: List[EdgeCase],
    initial_analysis: Optional[PatternAnalysis] = None
) -> PatternGroup:
    """
    Create pattern group with LLM-generated details.

    LLM generates:
    - pattern_name: Descriptive name
    - description: Explanation of the pattern
    - keywords: Key terms identifying the pattern
    - root_cause: Why this pattern occurs
    - suggested_actions: How to address it
    """
    # Generate comprehensive pattern details
    pattern_details = await self.llm_service.generate_pattern_details(edge_cases)

    pattern = PatternGroup(
        name=pattern_details.name,
        description=pattern_details.description,
        pattern_type=initial_analysis.pattern_type if initial_analysis else "mixed",
        severity=self._determine_severity(edge_cases),
        occurrence_count=len(edge_cases),
        status='active',
        suggested_actions=pattern_details.suggested_actions,
        pattern_metadata={
            **self._build_pattern_metadata(edge_cases),
            "keywords": pattern_details.keywords,
            "root_cause": pattern_details.root_cause,
            "llm_generated": True
        }
    )

    self.db.add(pattern)
    await self.db.flush()

    # Link all edge cases to this pattern
    for edge_case in edge_cases:
        link = EdgeCasePatternLink(
            edge_case_id=edge_case.id,
            pattern_group_id=pattern.id,
            similarity_score=1.0,
            added_at=datetime.utcnow()
        )
        self.db.add(link)
        edge_case.status = 'grouped'

    await self.db.commit()
    return pattern
```

---

## 7. Complete Edge Case Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SCENARIO EXECUTION                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. MultiTurnExecutionService executes scenario                             │
│                         ↓                                                   │
│  2. For each step, for each language variant:                               │
│     - Generate TTS audio                                                    │
│     - Send to Houndify                                                      │
│     - Validate response                                                     │
│                         ↓                                                   │
│  3. Create ValidationResult with:                                           │
│     - confidence_score, accuracy_score                                      │
│     - houndify_passed, llm_passed                                           │
│     - final_decision: pass | fail | uncertain                               │
│     - review_status: auto_pass | auto_fail | needs_review                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
                            (if review_status = "needs_review")
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                        VALIDATION QUEUE                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  4. ValidationResult added to validation_queue table                         │
│     - priority based on confidence (lower = higher priority)                 │
│     - language_code preserved for native speaker routing                     │
│                         ↓                                                   │
│  5. Human validator claims queue item via ValidationInterface                │
│                         ↓                                                   │
│  6. Validator reviews:                                                       │
│     - User utterance (with audio)                                           │
│     - Expected response                                                     │
│     - Actual AI response                                                    │
│     - Houndify and LLM validation results                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
                        Validator selects decision
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                     HUMAN VALIDATION SERVICE                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  7. HumanValidationService.submit_decision() called                          │
│     - validation_decision: "pass" | "fail" | "edge_case"                     │
│                         ↓                                                   │
│  8. IF decision == "edge_case":                                              │
│     │                                                                       │
│     ├─→ _create_edge_case_entry() called                                     │
│     │                                                                       │
│     ├─→ EdgeCaseDetectionService.detect_category()                           │
│     │   → Returns: "high_confidence_failure" | "low_confidence" | etc.       │
│     │                                                                       │
│     ├─→ EdgeCaseDetectionService.determine_severity()                        │
│     │   → Returns: "critical" | "high" | "medium" | "low"                    │
│     │                                                                       │
│     ├─→ EdgeCaseDetectionService.generate_tags()                             │
│     │   → Returns: ["en-US", "category:weather", "low-confidence"]           │
│     │                                                                       │
│     └─→ EdgeCase record created with:                                        │
│         - title: "Edge Case: {scenario} - Step {n}"                          │
│         - description: validator feedback                                   │
│         - scenario_definition: full context JSONB                           │
│         - auto_created: True                                                │
│         - Links to: scenario, validator, validation_result                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
                        (Background job or on-demand)
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PATTERN RECOGNITION (BATCH)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Triggered by: "Run Analysis" button OR scheduled Celery beat task          │
│  Analyzes: ALL edge cases with status='new' (auto AND manual)               │
│                                                                             │
│  9. EdgeCaseSimilarityService.analyze_and_group()                            │
│                         ↓                                                   │
│  10. Find similar edge cases (threshold ≥ 0.80):                             │
│      - Semantic similarity (40%): sentence-transformers                     │
│      - Category match (20%): exact match                                    │
│      - Language match (15%): same language code                             │
│      - Confidence proximity (10%): similar scores                           │
│      - Tag overlap (15%): Jaccard similarity                                │
│                         ↓                                                   │
│  11. IF LLM enabled:                                                         │
│      - LLM analyzes edge case characteristics                               │
│      - LLM matches to existing patterns                                     │
│      - LLM generates pattern name, description, keywords                    │
│                         ↓                                                   │
│  12. IF 3+ similar cases found:                                              │
│      - Create PatternGroup                                                  │
│      - Link all edge cases via EdgeCasePatternLink                          │
│      - Update occurrence_count                                              │
│      - Mark edge cases as "grouped"                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FRONTEND PAGES                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  EdgeCaseLibrary.tsx                                                         │
│  └─→ List all edge cases with filters (category, severity, status, tags)    │
│                                                                             │
│  EdgeCaseDetail.tsx                                                          │
│  └─→ View full edge case details, scenario definition, linked patterns      │
│                                                                             │
│  EdgeCaseCreate.tsx                                                          │
│  └─→ Manually create edge cases (auto_created = false)                       │
│                                                                             │
│  PatternGroups page (future)                                                 │
│  └─→ View patterns, trending patterns, edge cases per pattern               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Summary

### Multi-Language System
- **Data Model:** Language variants stored in `step_metadata.language_variants[]`, NOT as separate step records
- **Selection:** User selects languages via modal (ScenarioList) or LanguageSelector (ScenarioDetail)
- **API:** `language_codes` array passed to `/execute/{script_id}` endpoint
- **Execution:** `_get_language_variants()` filters variants, all selected languages are processed

### Edge Case System
- **Trigger:** Human validator selects "edge_case" decision during review
- **Auto-Detection:** Category, severity, and tags automatically determined
- **Similarity:** Multi-signal scoring (semantic 40%, category 20%, language 15%, confidence 10%, tags 15%)
- **Pattern Grouping:** 3+ similar cases grouped into PatternGroup with optional LLM enhancement
- **Storage:** Full context preserved in `scenario_definition` JSONB field

---

## Appendix: UI Access Points

### Where to Find Pattern Groups in the UI

**Navigation:** Sidebar → Quality → Edge Cases → "Pattern Groups" tab

**URL:** `/edge-cases?tab=pattern-groups`

> **Note:** Pattern Groups are integrated into the Edge Cases page as a tab, not as a separate page.
> The old URL `/pattern-groups` automatically redirects to `/edge-cases?tab=pattern-groups`.

### Edge Cases Page (with Pattern Groups Tab)

The Edge Cases page has two tabs:

#### Tab 1: "Edge Cases" (default)
- List of all edge cases with filters
- **Pattern Group Filter dropdown** - Filter edge cases by pattern group
- Status, category, severity filters
- Search and pagination

#### Tab 2: "Pattern Groups"
1. **Header with "Run Analysis" Button**
   - Triggers LLM-based pattern recognition on recent edge cases
   - Shows progress with polling for task status
   - Displays results (patterns discovered, new, updated)

2. **Status Filter Tabs**
   - Active, Resolved, Monitoring

3. **Trending Patterns Section**
   - Shows top 5 patterns from last 7 days
   - Quick access to high-activity patterns

4. **Pattern List**
   - Name, description, severity badge
   - Pattern type tag
   - Occurrence count
   - First seen / Last seen dates
   - Suggested actions preview

### Pattern Group Detail Page Features

**URL:** `/pattern-groups/{id}` (still a separate page for individual pattern details)

1. **Metadata Cards**
   - Severity
   - Occurrence count
   - First/Last seen timestamps

2. **Suggested Actions**
   - LLM-generated recommendations
   - Numbered action items

3. **Linked Edge Cases**
   - All edge cases grouped into this pattern
   - Click to navigate to edge case detail

---

## Appendix: Manual Edge Case Creation

### Scenario Selector Feature

When creating edge cases manually at `/edge-cases/new`, you can now:

1. **Select from Existing Scenarios**
   - Dropdown shows all scenarios in the system
   - Loading indicator while fetching

2. **Select a Specific Step**
   - Shows steps for selected scenario
   - Preview of the step utterance

3. **Auto-Population**
   - Scenario definition JSON is auto-populated with:
     - scenario_id, scenario_name, scenario_description
     - step_order, user_utterance
     - language_code, language_variants
   - Title is auto-generated: "Edge Case: {Scenario} - Step {N}"
   - Language tag is auto-added

4. **Manual Override**
   - All auto-populated fields remain editable
   - You can still write custom JSON if needed

---

*Document generated: December 2024*
*Last updated: December 25, 2024*
- Integrated Pattern Groups into Edge Cases page as a tab
- Added pattern group filter to edge cases view
- Updated navigation (removed separate Pattern Groups sidebar link)
- Pattern analysis now includes ALL edge cases (both auto-created and manual)
- Updated LLM-first approach documentation
- Added scenario selector for manual edge case creation
