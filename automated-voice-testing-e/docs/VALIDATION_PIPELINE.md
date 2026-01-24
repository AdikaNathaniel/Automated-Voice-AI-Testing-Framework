# Validation Pipeline Documentation

This document describes the complete validation pipeline from test execution through human validation, including all decision logic and thresholds.

## Table of Contents

1. [Overview](#overview)
2. [Test Execution Flow](#test-execution-flow)
3. [Validation Modes](#validation-modes)
4. [Deterministic Validation (Houndify)](#deterministic-validation-houndify)
5. [LLM Ensemble Validation](#llm-ensemble-validation)
6. [Combined Decision Logic](#combined-decision-logic)
7. [Review Status Determination](#review-status-determination)
8. [Human Validation Queue](#human-validation-queue)
9. [Dashboard Metrics](#dashboard-metrics)
10. [Configuration](#configuration)

---

## Overview

The validation pipeline uses a **hybrid approach** combining:
- **Deterministic validation** (Houndify): Fast, rule-based checks for CommandKind, ASR confidence, and response patterns
- **LLM ensemble validation**: Three-stage AI evaluation using multiple models (Gemini, GPT, Claude)

The combined decision from both systems determines whether a validation passes automatically or requires human review.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         VALIDATION PIPELINE FLOW                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Test Execution                                                              │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────┐    ┌─────────────────┐                                 │
│  │  Deterministic  │    │  LLM Ensemble   │                                 │
│  │   (Houndify)    │    │   (3-stage)     │                                 │
│  └────────┬────────┘    └────────┬────────┘                                 │
│           │                      │                                           │
│           │    houndify_passed   │    llm_decision                          │
│           │    (true/false)      │    (pass/fail/needs_review)              │
│           │                      │    llm_confidence                        │
│           │                      │    (high/medium/low)                     │
│           └──────────┬───────────┘                                          │
│                      │                                                       │
│                      ▼                                                       │
│           ┌─────────────────────┐                                           │
│           │  Combined Decision  │                                           │
│           │   (final_decision)  │                                           │
│           └──────────┬──────────┘                                           │
│                      │                                                       │
│                      ▼                                                       │
│           ┌─────────────────────┐                                           │
│           │   Review Status     │                                           │
│           │  (auto_pass/fail/   │                                           │
│           │   needs_review)     │                                           │
│           └──────────┬──────────┘                                           │
│                      │                                                       │
│        ┌─────────────┴─────────────┐                                        │
│        │                           │                                         │
│        ▼                           ▼                                         │
│  ┌───────────┐           ┌─────────────────┐                                │
│  │ Auto Pass │           │  Human Review   │                                │
│  │ (95% skip │           │     Queue       │                                │
│  │  5% sample)│          └─────────────────┘                                │
│  └───────────┘                                                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Test Execution Flow

### 1. Scenario Execution

Tests are executed as **multi-turn conversation scenarios**:

```python
# MultiTurnExecutionService.execute_scenario()
1. Load scenario script with steps
2. Initialize conversation state
3. For each step:
   a. Generate TTS audio for user utterance
   b. Send to Houndify API with conversation state
   c. Parse response and update conversation state
   d. Run validation for each language variant
   e. Store results
```

### 2. Step Execution

Each step in a scenario:
1. Sends user utterance to voice AI (Houndify)
2. Receives AI response with:
   - CommandKind (e.g., "WeatherCommand", "NavigationCommand")
   - ASR confidence score (0.0-1.0)
   - Response content (spoken text, entities)
3. Validates response against expected outcomes

---

## Validation Modes

Three validation modes are supported per scenario script:

| Mode | Description | When to Use |
|------|-------------|-------------|
| `houndify` | Deterministic only | Fast checks, simple scenarios |
| `llm_ensemble` | LLM pipeline only | Behavioral evaluation, complex responses |
| `hybrid` | Both systems | Maximum accuracy, production use |

Set via `ScenarioScript.validation_mode` field.

---

## Deterministic Validation (Houndify)

### Checks Performed

1. **CommandKind Match**
   - Compares actual CommandKind to expected
   - Score: 1.0 (match) or 0.0 (mismatch)

2. **ASR Confidence**
   - Minimum threshold check
   - Default minimum: 0.7 (70%)
   - Score: actual confidence value

3. **Response Content Patterns**
   - `contains`: Response must contain substring
   - `not_contains`: Response must not contain substring
   - `regex`: Response must match regex pattern

### Confidence Score Calculation

```python
# Weighted average of all checks
confidence_score = weighted_average([
    command_kind_match_score,  # weight: 0.4
    asr_confidence_score,      # weight: 0.3
    response_content_score,    # weight: 0.3
])
```

### Result

```python
houndify_passed: bool  # True if all critical checks pass
```

---

## LLM Ensemble Validation

### Three-Stage Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    LLM VALIDATION PIPELINE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Stage 1: Dual Evaluators (Parallel)                            │
│  ┌─────────────────┐    ┌─────────────────┐                     │
│  │  Evaluator A    │    │  Evaluator B    │                     │
│  │  (Gemini 1.5)   │    │  (GPT-4o-mini)  │                     │
│  │                 │    │                 │                     │
│  │  Score: 0-10    │    │  Score: 0-10    │                     │
│  │  + Reasoning    │    │  + Reasoning    │                     │
│  └────────┬────────┘    └────────┬────────┘                     │
│           │                      │                               │
│           └──────────┬───────────┘                              │
│                      │                                           │
│                      ▼                                           │
│           ┌─────────────────────┐                               │
│           │  Score Difference   │                               │
│           │  (normalized 0-1)   │                               │
│           └──────────┬──────────┘                               │
│                      │                                           │
│     ┌────────────────┼────────────────┐                         │
│     │                │                │                          │
│     ▼                ▼                ▼                          │
│  ≤ 0.15          0.16 - 0.39      ≥ 0.40                        │
│  (1.5/10)        (curator)        (4.0/10)                      │
│  HIGH            MODERATE          EXTREME                       │
│  CONSENSUS       DISAGREEMENT      DISAGREEMENT                  │
│     │                │                │                          │
│     ▼                ▼                ▼                          │
│  Average         Stage 2:         → needs_review                │
│  Scores          Curator             (confidence=low)           │
│     │                │                                           │
│     │                ▼                                           │
│     │     ┌─────────────────┐                                   │
│     │     │   Curator       │                                   │
│     │     │   (Claude 3.5)  │                                   │
│     │     │                 │                                   │
│     │     │  Reviews both   │                                   │
│     │     │  evaluations    │                                   │
│     │     │  + Tie-breaks   │                                   │
│     │     └────────┬────────┘                                   │
│     │              │                                             │
│     └──────────────┼──────────────────────────────────────────  │
│                    ▼                                             │
│           ┌─────────────────────┐                               │
│           │  Score → Decision   │                               │
│           │  ≥0.80 → pass       │                               │
│           │  <0.80 → fail       │                               │
│           └─────────────────────┘                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Thresholds

Scores from evaluators are on a 0-10 scale, normalized to 0-1 internally.

| Threshold | Value (0-1) | Value (0-10) | Description |
|-----------|-------------|--------------|-------------|
| `consensus_threshold` | 0.15 | 1.5 | Score difference at or below this = high consensus |
| `extreme_disagreement_threshold` | 0.40 | 4.0 | Score difference at or above this = human review |
| `pass_threshold` | 0.80 | 8.0 | Score at or above this = pass |

Environment variables:
- `LLM_CONSENSUS_THRESHOLD` (default: 0.15)
- `LLM_EXTREME_DISAGREEMENT_THRESHOLD` (default: 0.40)
- `LLM_PASS_THRESHOLD` (default: 0.80)

### Score to Decision Mapping

```python
def _score_to_decision(score: float) -> str:
    """Convert score to pass/fail (no needs_review from score alone)."""
    if score >= self.pass_threshold:  # Default: 0.80
        return "pass"
    return "fail"
```

| Score Range | Decision |
|-------------|----------|
| >= 0.80 (8/10) | `pass` |
| < 0.80 (8/10) | `fail` |

**Note:** The LLM pipeline does NOT return 'needs_review' based on score alone.
'needs_review' only occurs when there is **extreme disagreement** between evaluators
(score difference >= 0.40).

### Confidence Levels

| Consensus Type | Confidence | Description |
|----------------|------------|-------------|
| `high_consensus` | `high` | Evaluators agreed (diff < 1.5) |
| `curator_resolved` | `medium` | Curator resolved disagreement |
| `human_review` | `low` | Extreme disagreement (diff > 3.0) |

### Result

```python
llm_passed: bool        # True if decision='pass' AND confidence in ('high', 'medium')
llm_decision: str       # 'pass', 'fail', or 'needs_review'
llm_confidence: str     # 'high', 'medium', or 'low'
```

---

## Combined Decision Logic

The combined decision (`final_decision`) merges both validation systems.

### Hybrid Mode Logic

```python
def _compute_combined_decision(
    houndify_passed: bool,
    llm_decision: str,
    validation_mode: str,
) -> str:
    if validation_mode == 'houndify':
        return 'pass' if houndify_passed else 'fail'

    if validation_mode == 'llm_ensemble':
        if llm_decision == 'needs_review':
            return 'uncertain'
        return llm_decision

    # Hybrid mode - require agreement
    if llm_decision == 'needs_review':
        return 'uncertain'  # LLM uncertain

    llm_passed = (llm_decision == 'pass')

    if houndify_passed and llm_passed:
        return 'pass'       # Both agree: pass
    elif not houndify_passed and not llm_passed:
        return 'fail'       # Both agree: fail
    else:
        return 'uncertain'  # Disagreement
```

### Decision Matrix (Hybrid Mode)

**Important:** `final_decision` is determined ONLY by Houndify result and LLM decision (not LLM confidence).
LLM confidence only affects `review_status` in the next step.

| Houndify | LLM Decision | → `final_decision` |
|----------|--------------|-------------------|
| pass | pass | **pass** |
| pass | fail | **uncertain** (disagreement) |
| pass | needs_review | **uncertain** |
| fail | pass | **uncertain** (disagreement) |
| fail | fail | **fail** |
| fail | needs_review | **uncertain** |

**Then**, `review_status` is determined from `final_decision` + `llm_confidence`:

| `final_decision` | LLM Confidence | → `review_status` |
|------------------|----------------|-------------------|
| pass | high/medium | **auto_pass** |
| pass | low | **needs_review** |
| fail | high/medium | **auto_fail** |
| fail | low | **needs_review** |
| uncertain | any | **needs_review** |

---

## Review Status Determination

Review status determines whether human review is needed.

```python
def _compute_review_status(
    final_decision: str,
    llm_confidence: str,
) -> str:
    if final_decision == 'uncertain':
        return 'needs_review'

    if llm_confidence == 'low':
        return 'needs_review'  # Low confidence always needs review

    if final_decision == 'pass':
        return 'auto_pass'
    elif final_decision == 'fail':
        return 'auto_fail'
    else:
        return 'needs_review'
```

### Review Status Values

| Status | Description | Goes to Human Queue |
|--------|-------------|---------------------|
| `auto_pass` | AI confident it passed | No (95%), Yes (5% sample) |
| `auto_fail` | AI confident it failed | Yes |
| `needs_review` | AI uncertain | Yes |

---

## Human Validation Queue

### Queue Logic

```python
# Items that go to human queue:
needs_human_review = review_status != "auto_pass"

# 5% random sampling of auto_pass for calibration
if review_status == "auto_pass" and random.random() < 0.05:
    needs_human_review = True
    is_sampled = True
```

### Priority Levels

| Priority | Condition | Description |
|----------|-----------|-------------|
| 1 | `final_decision == 'fail'` | Confirmed failure - highest urgency |
| 2 | `final_decision == 'uncertain'` | Systems disagreed - needs human judgment |
| 5 | Other `needs_review` | General review |
| 10 | Sampled `auto_pass` | Random sample - lowest priority (calibration) |

### Queue Item Data

```python
queue_item = await queue_service.enqueue_for_human_review(
    validation_result_id=validation_result.id,
    priority=priority,
    confidence_score=confidence_percentage,
    language_code=lang_code,
    requires_native_speaker=False
)
```

### Human Validation Decisions

When a human reviews an item, they can decide:

| Decision | Description |
|----------|-------------|
| `pass` | Validation should pass |
| `fail` | Validation should fail |
| `edge_case` | Unusual case, needs special handling |

---

## Dashboard Metrics

### Human Agreement Rate

Measures how often the **combined AI decision** matches human decisions.

```python
async def _calculate_human_agreement_rate(db, start_time, end_time):
    # Query: final_decision vs human validation_decision

    for ai_decision, human_decision in rows:
        if human_decision == "edge_case":
            edge_cases_found += 1
            if ai_decision in ("pass", "fail"):
                ai_overturned += 1
                disagreements += 1
            continue

        if ai_decision == "uncertain" or ai_decision is None:
            uncertain_resolved += 1
            continue

        if ai_decision in ("pass", "fail"):
            comparable_reviews += 1
            if human_decision == ai_decision:
                agreements += 1
            else:
                disagreements += 1
                ai_overturned += 1

    agreement_rate = (agreements / comparable_reviews * 100) if comparable_reviews > 0 else 0
```

### Metrics Returned

| Metric | Description |
|--------|-------------|
| `agreement_rate_pct` | % of time AI and human agreed (when AI was confident) |
| `total_human_reviews` | Total items reviewed by humans |
| `agreements` | Cases where AI and human agreed |
| `disagreements` | Cases where AI and human disagreed |
| `ai_overturned` | Cases where human changed AI's decision |
| `edge_cases_found` | Cases human marked as edge case |
| `uncertain_resolved` | Cases where AI was uncertain, human decided |

### Time Saved Calculation

```python
# Time saved = items that didn't need human review × avg review time
time_saved_hours = auto_approved_count * AVG_HUMAN_VALIDATION_TIME_MINUTES / 60

AVG_HUMAN_VALIDATION_TIME_MINUTES = 2.0  # 2 minutes per item
```

---

## Configuration

### Environment Variables

```bash
# Enable LLM ensemble validation
ENABLE_LLM_ENSEMBLE_VALIDATION=true

# Default validation mode
DEFAULT_VALIDATION_MODE=hybrid

# OpenRouter API key (for LLM access)
OPENROUTER_API_KEY=your_key_here
```

### LLM Model Configuration

Models used in the pipeline:

| Role | Default Model | Provider |
|------|---------------|----------|
| Evaluator A | `google/gemini-flash-1.5` | Google |
| Evaluator B | `openai/gpt-4o-mini` | OpenAI |
| Curator | `anthropic/claude-sonnet-4-5` | Anthropic |

### Thresholds Summary

| Threshold | Value | Env Variable | Location |
|-----------|-------|--------------|----------|
| ASR confidence minimum | 0.7 | - | Houndify validation |
| LLM pass score | >= 0.80 | `LLM_PASS_THRESHOLD` | LLM pipeline |
| LLM fail score | < 0.80 | `LLM_PASS_THRESHOLD` | LLM pipeline |
| High consensus difference | <= 0.15 (1.5/10) | `LLM_CONSENSUS_THRESHOLD` | LLM pipeline |
| Curator trigger difference | 0.15 - 0.39 | - | LLM pipeline |
| Extreme disagreement | >= 0.40 (4.0/10) | `LLM_EXTREME_DISAGREEMENT_THRESHOLD` | LLM pipeline |
| Random sample rate | 5% | - | Queue logic |
| Avg human validation time | 2 min | - | Dashboard metrics |

**Note:** LLM 'needs_review' only comes from extreme disagreement between evaluators, not from score alone.

---

## File References

| Component | File |
|-----------|------|
| Execution service | `backend/services/multi_turn_execution_service.py` |
| Validation service | `backend/services/validation_service.py` |
| Houndify validation | `backend/services/validation_houndify.py` |
| LLM validation mixin | `backend/services/validation_llm.py` |
| LLM pipeline | `backend/services/llm_pipeline_service.py` |
| Dashboard metrics | `backend/services/dashboard_service.py` |
| Queue service | `backend/services/validation_queue_service.py` |
| ValidationResult model | `backend/models/validation_result.py` |
| HumanValidation model | `backend/models/human_validation.py` |

---

## Example Flow

### Scenario: User asks for weather

1. **Test Execution**
   - User utterance: "What's the weather in San Francisco?"
   - Expected: CommandKind=WeatherCommand, response contains "San Francisco"

2. **Houndify Response**
   - CommandKind: "WeatherCommand" ✓
   - ASR confidence: 0.92 ✓
   - Response: "It's 65°F and sunny in San Francisco"
   - **Result**: `houndify_passed = True`

3. **LLM Evaluation**
   - Evaluator A (Gemini): 8.5/10 - "Correctly identified location and provided weather"
   - Evaluator B (GPT): 8.2/10 - "Accurate response with relevant information"
   - Score difference: 0.03 (normalized) ≤ 0.15 = **high consensus**
   - Final score: 8.35/10 = 0.835 ≥ 0.80 = **pass**
   - **Result**: `llm_decision = 'pass'`, `llm_confidence = 'high'`

4. **Combined Decision**
   - Houndify: pass, LLM: pass → both agree
   - **Result**: `final_decision = 'pass'`

5. **Review Status**
   - final_decision='pass', confidence='high' (not 'low')
   - **Result**: `review_status = 'auto_pass'`

6. **Queue Decision**
   - review_status='auto_pass'
   - Random check: 0.87 (> 0.05, not sampled)
   - **Result**: Not queued (passed automatically)

### Scenario: Disagreement between systems

1. **Houndify**: `houndify_passed = False` (wrong CommandKind)
2. **LLM**: `llm_decision = 'pass'`, `llm_confidence = 'high'`
3. **Combined**: `final_decision = 'uncertain'` (disagreement)
4. **Review Status**: `review_status = 'needs_review'`
5. **Queue**: Queued with priority 2

Human validator reviews and decides the final outcome.
