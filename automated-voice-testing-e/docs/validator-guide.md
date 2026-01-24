# Validator Configuration Guide

This guide explains how rule-based validators and LLM judges work together in the Voice AI Automated Testing Framework, including order of operations, escalation thresholds, and configuration options.

## Overview

The validation system combines two approaches that interact to provide comprehensive response evaluation:

1. **Rule-Based Validators**: Fast, deterministic checks
2. **LLM Judge Ensemble**: Semantic understanding and nuanced evaluation

## Validation Order of Operations

The validation pipeline follows a specific sequence to ensure efficient and accurate evaluation:

### Step 1: Rule-Based Validation (First Pass)

Rule-based validators run first because they are:
- Fast and deterministic
- Able to quickly reject clearly invalid responses
- Cost-effective (no API calls required)

```python
from backend.services.validation_service import validation_service

# Rule-based checks are applied automatically
result = await validation_service.validate_voice_response(
    execution_id=execution_id,
    expected_outcome_id=expected_outcome_id
)
```

### Step 2: Tolerance Band Evaluation

After basic rules pass, tolerance bands are evaluated:

1. Entity presence check
2. Forbidden content check
3. Tone validation
4. Length validation
5. Semantic similarity threshold

### Step 3: LLM Judge Ensemble (When Needed)

If rule-based validation passes but confidence is below threshold, the LLM ensemble is invoked:

```python
from backend.services.ensemble_judge_service import ensemble_judge_service

# Ensemble evaluation with multiple judges
ensemble_result = await ensemble_judge_service.evaluate(
    actual_response=response_text,
    expected_response=expected_text,
    context=scenario_context
)
```

### Step 4: Human Escalation (If Required)

Based on consensus and confidence, responses may escalate to human review.

## Rule-Based Validators

### Entity Presence Validation

Checks that required entities appear in the response:

```python
# Configuration in ExpectedOutcome
tolerance_config = {
    "required_entities": ["temperature", "location"],
    "entity_match_threshold": 0.8
}
```

### Forbidden Content Validation

Ensures prohibited terms are absent:

```python
tolerance_config = {
    "forbidden_phrases": ["I don't know", "error", "cannot process"]
}
```

### Tone Validation

Validates response tone matches requirements:

```python
tolerance_config = {
    "tone_requirement": "professional"  # Options: professional, casual, formal
}
```

### Length Validation

Enforces response length constraints:

```python
tolerance_config = {
    "max_response_length": 500,
    "min_response_length": 10
}
```

## LLM Judge Ensemble

The ensemble uses multiple LLM instances as judges, each providing independent evaluation.

### Consensus Calculation

Judges vote on response quality and the system calculates consensus:

```python
from backend.services.ensemble_judge_service import EnsembleJudgeService

service = EnsembleJudgeService()

# Calculate consensus from judge decisions
consensus = service.calculate_consensus(judge_decisions=[
    {"judge_id": "judge_1", "passed": True, "confidence": 0.92},
    {"judge_id": "judge_2", "passed": True, "confidence": 0.88},
    {"judge_id": "judge_3", "passed": False, "confidence": 0.65}
])

# Returns: consensus_type, agreement_ratio, dissenting_judges
```

### Consensus Types

| Type | Definition | Confidence |
|------|------------|------------|
| unanimous | All judges agree | Highest |
| strong_majority | 80%+ agreement | High |
| majority | >50% agreement | Medium |
| split | No clear majority | Low |

## Escalation Thresholds

Escalation determines when validation results need human review.

### Configuration

```python
from backend.services.escalation_policy_service import EscalationPolicyService

policy_service = EscalationPolicyService()

# Define escalation policy
policy = {
    "name": "Standard Escalation",
    "min_consensus_ratio": 0.67,  # At least 2/3 judges agree
    "min_confidence": 0.80,       # Minimum confidence threshold
    "always_escalate_intents": ["payment", "cancellation"],
    "auto_pass_threshold": 0.95   # Auto-pass if confidence > 95%
}

# Evaluate if escalation is needed
should_escalate = policy_service.should_escalate(
    consensus_result=ensemble_result,
    intent_type="booking"
)
```

### Escalation Triggers

Validation escalates to human review when:

1. **Low Consensus**: Agreement ratio below `min_consensus_ratio`
2. **Low Confidence**: Average confidence below `min_confidence`
3. **Critical Intent**: Intent is in `always_escalate_intents` list
4. **Dissenting Judges**: Specific high-accuracy judges dissent

### Auto-Pass Conditions

Validation auto-passes (no escalation) when:
- All judges agree (unanimous)
- Confidence exceeds `auto_pass_threshold`
- Intent is in auto-approve list

## Tolerance Definitions

Tolerances define acceptable variation between expected and actual responses.

### Semantic Similarity

Configure the minimum semantic similarity score required:

```python
# In ExpectedOutcome model
tolerance_config = {
    "semantic_threshold": 0.85,  # 85% similarity required
    "use_embedding_model": "sentence-transformers"
}
```

### Keyword Tolerance

Allow variations while requiring key terms:

```python
tolerance_config = {
    "required_keywords": ["confirmed", "booking"],
    "keyword_case_sensitive": False
}
```

### Numeric Tolerance

Allow variance in numeric values:

```python
tolerance_config = {
    "numeric_fields": {
        "temperature": {"tolerance": 5, "unit": "degrees"},
        "price": {"tolerance": 0.01, "unit": "dollars"}
    }
}
```

## Run Inline Configuration

The `run_inline` option controls whether validation runs synchronously or asynchronously.

### Synchronous (Inline) Mode

Use when immediate results are required:

```python
# Configuration
validation_config = {
    "run_inline": True,  # Synchronous execution
    "timeout_seconds": 30
}

# Validation completes before returning
result = await validation_service.validate_voice_response(
    execution_id=execution_id,
    expected_outcome_id=expected_outcome_id,
    run_inline=True
)
# Result is immediately available
```

### Asynchronous Mode

Use for batch processing or when results can be retrieved later:

```python
# Configuration
validation_config = {
    "run_inline": False,  # Asynchronous execution
    "callback_url": "https://api.example.com/validation-complete"
}

# Returns task ID immediately
task_id = await validation_service.validate_voice_response(
    execution_id=execution_id,
    expected_outcome_id=expected_outcome_id,
    run_inline=False
)
# Result retrieved later via task_id
```

## Persona Configuration

Judge personas define evaluation criteria and strictness levels for LLM judges.

### Creating a Persona

```python
from backend.services.judge_persona_service import judge_persona_service

# Define persona
persona = {
    "name": "Strict Technical Reviewer",
    "system_prompt": "You are a precise technical evaluator. Focus on accuracy and completeness.",
    "evaluation_criteria": [
        "semantic_accuracy",
        "technical_correctness",
        "completeness",
        "clarity"
    ],
    "strictness_level": "strict"
}

# Validate and use
validation = judge_persona_service.validate_persona(persona)
```

### Strictness Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| lenient | Accepts reasonable variations | Exploratory testing |
| moderate | Balanced evaluation | Standard validation |
| strict | Requires precise matches | Critical responses |
| custom | User-defined criteria | Specialized needs |

### Persona Selection per Test Suite

Attach personas to test suites for consistent evaluation:

```python
# In TestSuite model
test_suite = {
    "name": "Payment Flow Tests",
    "judge_persona_id": persona_id,  # Use specific persona
    "config": {
        "require_all_criteria": True
    }
}
```

### Building Judge Prompts

The system builds prompts from persona configuration:

```python
prompt = judge_persona_service.build_prompt(persona)

# Generated prompt includes:
# - System prompt
# - Evaluation criteria
# - Strictness instructions
# - Response format requirements
```

## Default Personas

The framework provides built-in personas:

```python
default_personas = judge_persona_service.get_default_personas()

# Returns:
# - "Balanced Evaluator" (moderate)
# - "Strict Accuracy Judge" (strict)
# - "Lenient Assistant" (lenient)
# - "Technical Specialist" (strict, technical focus)
```

## Complete Configuration Example

Here's a full configuration combining all features:

```python
# Test suite configuration
test_suite_config = {
    "name": "Customer Service Flow",
    "judge_persona_id": strict_persona_id,
    "validation_config": {
        "run_inline": True,
        "timeout_seconds": 45
    }
}

# Expected outcome with tolerances
expected_outcome = {
    "expected_response": "Your appointment is confirmed for tomorrow at 2 PM.",
    "tolerance_config": {
        "semantic_threshold": 0.85,
        "required_entities": ["appointment", "time"],
        "forbidden_phrases": ["sorry", "unable"],
        "tone_requirement": "professional",
        "max_response_length": 200
    },
    "validation_rules": {
        "require_confirmation": True,
        "allow_alternate_phrasing": True
    }
}

# Escalation policy
escalation_policy = {
    "min_consensus_ratio": 0.67,
    "min_confidence": 0.80,
    "always_escalate_intents": ["cancellation", "refund"],
    "auto_pass_threshold": 0.95
}
```

## Monitoring Validation Metrics

Track validation performance using the reporting service:

```python
from backend.services.reporting_metrics_service import reporting_metrics_service

# Get consensus metrics
consensus_stats = reporting_metrics_service.get_consensus_metrics(
    start_date=start_date,
    end_date=end_date,
    group_by="day"
)

# Get tolerance usage stats
tolerance_stats = reporting_metrics_service.get_tolerance_stats(
    test_run_id=test_run_id
)

# Get escalation stats
escalation_stats = reporting_metrics_service.get_escalation_stats(
    start_date=start_date,
    end_date=end_date
)
```

## Troubleshooting

### Low Consensus Issues

If validation frequently shows low consensus:

1. Review judge persona configurations for conflicts
2. Check if expected responses are too specific
3. Consider adjusting strictness levels
4. Analyze dissenting judge patterns

### High Escalation Rates

If too many validations escalate:

1. Adjust `min_confidence` threshold
2. Review `always_escalate_intents` list
3. Consider using more lenient personas
4. Update tolerance definitions

### Slow Validation

If validation takes too long:

1. Use `run_inline: False` for non-critical validations
2. Reduce number of judges in ensemble
3. Optimize rule-based checks to reject early
4. Consider caching common validations

## Related Documentation

- [MVP Workflow](mvp-workflow.md) - Overview of scripted scenarios and workflow
- [STT Scope](stt-scope.md) - Speech-to-text assumptions
- API Documentation - Endpoint reference
