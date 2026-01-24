# LLM Ensemble Validation Pipeline Design

## Overview

This document describes the three-stage LLM validation pipeline for voice AI testing. This approach focuses on **behavioral testing** - assessing whether the agent performed the correct action, not whether it used exact predetermined words.

## Model Configuration

All models are accessed via **OpenRouter API** (`https://openrouter.ai/api`).

| Role | Model ID | Vendor | Speed | Purpose |
|------|----------|--------|-------|---------|
| Evaluator A | `google/gemini-2.5-flash` | Google | ⚡⚡ | Fast, cost-effective evaluation |
| Evaluator B | `openai/gpt-4.1-mini` | OpenAI | ⚡⚡ | Independent second evaluation |
| Curator | `anthropic/claude-sonnet-4.5` | Anthropic | ⚡ | Tie-breaking, conflict resolution |

### Why These Choices?
- **Three different vendors**: Eliminates vendor-specific biases
- **Gemini + GPT-4.1 Mini**: Both fastest generation, optimized for high-volume evaluation
- **Claude Sonnet 4.5 as Curator**: Best balance of intelligence and speed, only called when disagreement occurs
- **All speed-optimized**: No slow models in the pipeline

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         TEST CASE INPUT                                  │
│  - Transcribed response from voice agent                                │
│  - Expected outcome (CommandKind, entities, response patterns)          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      STAGE 1: DUAL EVALUATORS                           │
│                                                                         │
│  ┌─────────────────────┐         ┌─────────────────────┐               │
│  │   LLM Evaluator A   │         │   LLM Evaluator B   │               │
│  │                     │         │                     │               │
│  │  Assesses:          │         │  Assesses:          │               │
│  │  - Intent correct?  │         │  - Intent correct?  │               │
│  │  - Right command?   │         │  - Right command?   │               │
│  │  - Appropriate      │         │  - Appropriate      │               │
│  │    response?        │         │    response?        │               │
│  │                     │         │                     │               │
│  │  Returns:           │         │  Returns:           │               │
│  │  - Score (0.0-1.0)  │         │  - Score (0.0-1.0)  │               │
│  │  - CoT Reasoning    │         │  - CoT Reasoning    │               │
│  └─────────────────────┘         └─────────────────────┘               │
│            │                              │                             │
│            └──────────────┬───────────────┘                             │
│                           ▼                                             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      STAGE 2: CURATOR LLM                               │
│                                                                         │
│  Analyzes both evaluations and applies consensus logic:                 │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ IF score_diff <= 0.15 (HIGH CONSENSUS):                         │   │
│  │    → Accept AVERAGE of both scores                              │   │
│  │    → High confidence in result                                  │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │ IF 0.15 < score_diff < EXTREME_THRESHOLD:                       │   │
│  │    → Curator makes TIE-BREAKING decision                        │   │
│  │    → Reviews reasoning from both evaluators                     │   │
│  │    → Determines which evaluation is more accurate               │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │ IF score_diff >= EXTREME_THRESHOLD (EXTREME DISAGREEMENT):      │   │
│  │    → Flag for HUMAN REVIEW                                      │   │
│  │    → Include both evaluations and reasoning                     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      STAGE 3: DECISION                                  │
│                                                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐ │
│  │  PASS           │  │  FAIL           │  │  HUMAN REVIEW           │ │
│  │  Score >= 0.80  │  │  Score < 0.80   │  │  Curator couldn't       │ │
│  │                 │  │                 │  │  decide / extreme       │ │
│  │                 │  │                 │  │  disagreement           │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Configuration Thresholds

```python
# Consensus thresholds
CONSENSUS_THRESHOLD = 0.15      # Max score difference for high consensus
EXTREME_DISAGREEMENT = 0.40     # Score difference triggering human review

# Decision thresholds
PASS_THRESHOLD = 0.80           # Minimum score to pass
FAIL_THRESHOLD = 0.80           # Below this = fail (same as pass threshold)

# Confidence mapping (based on curator analysis)
HIGH_CONFIDENCE = "high"        # Both evaluators agreed
MEDIUM_CONFIDENCE = "medium"    # Curator made tie-breaking decision
LOW_CONFIDENCE = "low"          # Flagged for human review
```

## Evaluator Assessment Criteria

Each LLM evaluator assesses three key dimensions:

### 1. Intent Understanding
- Did the agent correctly understand what the user wanted?
- Was the user's request interpreted accurately?

### 2. Command Execution
- Did the agent execute the correct system command?
- Was the right action performed (e.g., NavigationCommand, MusicCommand)?
- For Houndify: Does the CommandKind match expectations?

### 3. Response Appropriateness
- Is the response contextually appropriate?
- Does it address the user's actual need?
- Is it helpful and relevant?

## Chain-of-Thought (CoT) Reasoning

Each evaluator returns structured reasoning:

```json
{
  "score": 0.85,
  "reasoning": {
    "intent_analysis": "User asked to play jazz music. Agent correctly identified this as a music playback request.",
    "command_assessment": "MusicCommand was issued with genre=jazz, which matches the user intent.",
    "response_quality": "Agent responded 'Playing jazz music for you' which directly acknowledges the request.",
    "concerns": [],
    "strengths": ["Accurate intent recognition", "Appropriate command", "Natural response"]
  }
}
```

## Benefits of This Architecture

### 1. Reduces Bias
- Two independent evaluators prevent single-point-of-failure judgments
- Different perspectives catch different issues
- No single model's biases dominate the assessment

### 2. Prevents False Positives
- Curator layer validates consensus before accepting results
- Over-confident individual evaluators are balanced out
- Disagreement triggers additional scrutiny

### 3. Behavioral Testing Focus
- Tests whether the agent **did the right thing**
- Not whether it used exact pre-written phrases
- Allows for natural language variation in responses
- More realistic assessment of voice AI performance

## Integration with Validation Modes

The `ScenarioScript.validation_mode` field determines which validation approach is used:

| Mode | Description |
|------|-------------|
| `houndify` | Traditional Houndify-only validation (CommandKind, ASR confidence) |
| `llm_ensemble` | Full LLM ensemble pipeline (this design) |
| `hybrid` | Combines Houndify checks with LLM ensemble for comprehensive validation |

## Data Flow

```python
# Stage 1: Dual Evaluation
evaluator_a_result = await evaluator_a.evaluate(test_case)
evaluator_b_result = await evaluator_b.evaluate(test_case)

# Stage 2: Curator Analysis
score_diff = abs(evaluator_a_result.score - evaluator_b_result.score)

if score_diff <= CONSENSUS_THRESHOLD:
    # High consensus - average the scores
    final_score = (evaluator_a_result.score + evaluator_b_result.score) / 2
    confidence = "high"
elif score_diff < EXTREME_DISAGREEMENT:
    # Curator makes tie-breaking decision
    final_score = await curator.resolve(evaluator_a_result, evaluator_b_result)
    confidence = "medium"
else:
    # Extreme disagreement - human review
    return HumanReviewRequired(evaluator_a_result, evaluator_b_result)

# Stage 3: Decision
if final_score >= PASS_THRESHOLD:
    return ValidationResult(status="pass", score=final_score, confidence=confidence)
else:
    return ValidationResult(status="fail", score=final_score, confidence=confidence)
```

## Human Review Cases

Cases flagged for human review include:

1. **Extreme Evaluator Disagreement** - Scores differ by more than threshold
2. **Curator Uncertainty** - Curator cannot determine which evaluator is correct
3. **Edge Cases** - Unusual scenarios not well-covered by training
4. **Low Overall Confidence** - Both evaluators uncertain

## Implementation

The pipeline is implemented in:
- `backend/services/llm_pipeline_service.py` - Main pipeline orchestrator
- `backend/services/llm_providers/openrouter_adapter.py` - OpenRouter API client
- `backend/services/llm_providers/base.py` - Base adapter with scoring logic

### Environment Variables

All configuration is in `.env.example`:

```bash
# OpenRouter API
OPENROUTER_API_KEY=your-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Model Selection (with alternatives in comments)
LLM_EVALUATOR_A_MODEL=google/gemini-2.5-flash
LLM_EVALUATOR_B_MODEL=openai/gpt-4.1-mini
LLM_CURATOR_MODEL=anthropic/claude-sonnet-4.5

# Thresholds
LLM_CONSENSUS_THRESHOLD=0.15
LLM_EXTREME_DISAGREEMENT_THRESHOLD=0.40
LLM_PASS_THRESHOLD=0.80

# Request Settings
LLM_TEMPERATURE=0.0
LLM_MAX_TOKENS=1024
LLM_TIMEOUT=30
```

## Future Enhancements

1. **Evaluator Calibration** - Track evaluator accuracy over time, weight accordingly
2. **Domain-Specific Evaluators** - Specialized evaluators for different command types
3. **Feedback Loop** - Human review decisions improve evaluator prompts
4. **Confidence Thresholds** - Configurable per test suite or scenario type
