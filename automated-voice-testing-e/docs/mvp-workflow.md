# MVP Workflow Documentation

This document describes the core workflow for the Voice AI Automated Testing Framework MVP, including scripted scenarios, LLM ensemble evaluation, and tolerance handling.

## Scripted Scenario Workflow

The framework uses scripted test scenarios to define multi-turn conversations. Each scenario consists of ordered steps that simulate realistic voice AI interactions.

### Scenario Structure

A scenario contains:
- **Name and metadata**: Identification and versioning
- **Steps**: Ordered sequence of user utterances and expected responses
- **Tolerances**: Acceptable variation thresholds per step

### Creating a Scenario

```python
from backend.services.scenario_builder_service import scenario_builder_service

# Create a new scenario
scenario = scenario_builder_service.create_scenario(
    name="Weather Query Flow",
    description="Test weather information retrieval",
    version="1.0.0"
)

# Add steps to the scenario
scenario_builder_service.add_step(
    scenario,
    user_utterance="What's the weather like today?",
    expected_response="The current weather is sunny with a temperature of 72 degrees.",
    tolerances={
        "semantic_similarity": 0.85,
        "keyword_match": ["weather", "temperature"]
    }
)
```

## LLM Ensemble Approach

The framework uses an ensemble of LLM judges to evaluate response quality. This consensus-based approach reduces individual model bias and improves evaluation reliability.

### How the Ensemble Works

1. **Multiple Judges**: Several LLM instances evaluate each response independently
2. **Consensus Calculation**: Individual decisions are aggregated
3. **Confidence Scoring**: Agreement level determines confidence

### Judge Configuration

```python
from backend.services.judge_persona_service import judge_persona_service

# Get default judge personas
personas = judge_persona_service.get_default_personas()

# Create custom persona
custom_persona = {
    "name": "Strict Evaluator",
    "system_prompt": "Evaluate responses with high precision standards.",
    "evaluation_criteria": [
        "semantic_accuracy",
        "completeness",
        "tone_appropriateness"
    ],
    "strictness_level": "strict"
}
```

### Consensus Thresholds

The ensemble requires configurable agreement levels:
- **Unanimous**: All judges agree (highest confidence)
- **Majority**: >50% agreement
- **Weighted**: Judges with higher accuracy get more weight

## Tolerance Handling

Tolerances define acceptable variation between expected and actual responses. The framework supports multiple tolerance types for flexible validation.

### Tolerance Types

1. **Semantic Similarity**: Vector-based meaning comparison
2. **Keyword Matching**: Required terms must be present
3. **Entity Extraction**: Named entities must match
4. **Numeric Tolerance**: Numbers within acceptable range

### Configuring Tolerances

```python
# Step with tolerance configuration
step_tolerances = {
    "semantic_threshold": 0.80,  # 80% semantic similarity required
    "required_keywords": ["temperature", "degrees"],
    "numeric_tolerance": {
        "field": "temperature",
        "tolerance": 5  # +/- 5 degrees acceptable
    }
}
```

### Threshold Levels

| Level | Semantic | Use Case |
|-------|----------|----------|
| Strict | 0.95+ | Critical responses |
| Moderate | 0.85+ | Standard validation |
| Lenient | 0.70+ | Exploratory testing |

## Confirmation Loops

Confirmation loops handle scenarios where the voice AI needs to verify user intent before proceeding.

### Example: Confirmation Flow

```yaml
name: Order Confirmation Flow
steps:
  - step_order: 1
    user_utterance: "I want to order a large pizza"
    expected_response: "You'd like a large pizza. Is that correct?"
    follow_up_action: "await_confirmation"

  - step_order: 2
    user_utterance: "Yes, that's right"
    expected_response: "Great! Your order has been placed."
    alternate_responses:
      - "Perfect! I've submitted your order."
      - "Excellent! Your pizza is on its way."
```

### Handling Confirmation Responses

The framework supports various confirmation patterns:

```python
# Sample confirmation detection
confirmation_patterns = [
    "yes",
    "that's correct",
    "confirm",
    "right",
    "exactly"
]

denial_patterns = [
    "no",
    "that's wrong",
    "cancel",
    "incorrect"
]
```

## Alternate Outcomes

Real conversations can branch based on user responses. The framework models alternative paths to handle different outcomes.

### Example: Branching Scenario

```yaml
name: Account Lookup
steps:
  - step_order: 1
    user_utterance: "Check my account balance"
    expected_response: "I found your account. Your balance is $500."
    alternate_responses:
      - "I couldn't find an account with that information."
      - "I found multiple accounts. Which one would you like?"

  - step_order: 2
    condition: "account_found"
    user_utterance: "Transfer $100 to savings"
    expected_response: "I've transferred $100 to your savings account."

  - step_order: 2
    condition: "account_not_found"
    user_utterance: "Try my email address"
    expected_response: "Please provide your email address."
```

### Alternative Response Validation

When alternate outcomes are defined, the validation considers:
1. Primary expected response
2. All listed alternative responses
3. Semantic similarity to any acceptable response

```python
# Validation with alternates
validation_result = {
    "passed": True,
    "matched_response": "alternate",
    "matched_index": 1,
    "similarity_score": 0.92
}
```

## Complete Workflow Example

Here's a sample end-to-end scenario demonstrating all concepts:

```python
from backend.services.scenario_builder_service import scenario_builder_service
from backend.services.step_orchestration_service import step_orchestration_service

# Create scenario
scenario = scenario_builder_service.create_scenario(
    name="Flight Booking Confirmation",
    description="Test flight booking with confirmation loop"
)

# Step 1: Initial request
scenario_builder_service.add_step(
    scenario,
    user_utterance="Book a flight to New York",
    expected_response="I found flights to New York. The earliest is at 9 AM for $299. Should I book it?",
    tolerances={"semantic_threshold": 0.85}
)

# Step 2: Confirmation with alternates
scenario_builder_service.add_step(
    scenario,
    user_utterance="Yes, book it",
    expected_response="Your flight is booked. Confirmation number is ABC123.",
    alternate_responses=[
        "I've booked your flight. You'll receive a confirmation email.",
        "Flight booked successfully. Your reference is ABC123."
    ],
    follow_up_action="send_confirmation_email"
)

# Execute scenario
responses = [
    "I found several flights to New York. The first available is 9 AM, $299. Want me to book?",
    "Done! Your flight is confirmed. Reference number ABC123."
]

result = step_orchestration_service.execute_scenario(scenario, responses)
print(f"Scenario passed: {result['overall_pass']}")
print(f"Steps passed: {result['passed_steps']}/{result['total_steps']}")
```

## Best Practices

1. **Start with strict tolerances** and loosen as needed
2. **Include 2-3 alternate responses** for variable outputs
3. **Use confirmation loops** for critical actions
4. **Test both success and failure paths**
5. **Version your scenarios** for regression tracking

## Related Documentation

- [STT Scope Clarification](stt-scope.md) - Speech-to-text assumptions
- API Documentation - Endpoint reference
- Configuration Guide - Environment setup
