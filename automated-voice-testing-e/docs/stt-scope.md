# Speech-to-Text (STT) Scope Clarification

This document clarifies the assumptions and scope regarding Speech-to-Text processing in the Voice AI Automated Testing Framework.

## STT Fidelity Assumption

The testing framework **assumes that STT fidelity has already been validated** by the client or through external processes. When using this framework:

- Test scenarios provide **reference transcripts** as part of the test definition
- The framework compares system responses against these reference transcripts
- STT accuracy is not measured or validated within the test execution pipeline

### Why This Assumption?

1. **Focus on Voice AI Logic**: The primary goal is to test the voice AI's natural language understanding and response generation, not the underlying speech recognition accuracy.

2. **Reproducibility**: Using reference transcripts ensures tests are deterministic and reproducible.

3. **Separation of Concerns**: ASR (Automatic Speech Recognition) quality is typically validated separately using specialized tools and datasets.

## What the Framework Does NOT Perform

The framework will **skip the following STT-related processing**:

- Real-time audio transcription
- STT accuracy measurement (Word Error Rate)
- Acoustic model evaluation
- Audio quality assessment for speech recognition

Instead, the framework:

- Accepts pre-defined reference transcripts in test scenarios
- Uses these transcripts directly for validation
- Compares system responses against expected outcomes

## External ASR Validation Guidance

If your organization needs to validate ASR/STT quality, consider these approaches:

### Option 1: Dedicated ASR Testing Tools

Use specialized ASR evaluation tools that can:

- Calculate Word Error Rate (WER)
- Measure Character Error Rate (CER)
- Evaluate acoustic model performance
- Test with diverse speaker profiles and accents

### Option 2: Pre-Pipeline Validation

Validate ASR before using this testing framework:

1. Record audio samples with known transcripts
2. Process through your STT system
3. Compare output against ground truth
4. Only proceed to voice AI testing once ASR meets quality thresholds

### Option 3: Hybrid Approach

Combine external ASR validation with this framework:

1. Use external tools for STT accuracy testing
2. Use this framework for voice AI logic testing
3. Correlate results to identify end-to-end issues

## Transcript Comparison Feature

While the framework does not perform STT, it does provide **TranscriptionValidatorService** for comparing reference transcripts:

- Compare expected vs actual transcripts
- Calculate similarity scores
- Identify word-level differences
- Compute Word Error Rate for comparison purposes

This is useful for validating that:

- The system received the correct input
- Transcription consistency across test runs
- Detection of unexpected variations

## Configuration

To use reference transcripts in test scenarios:

```yaml
name: Weather Query Test
steps:
  - user_utterance: "What's the weather like today?"
    expected_response: "The weather is sunny with a high of 75 degrees"
    # The user_utterance is the reference transcript
```

The `user_utterance` field contains the reference transcript that represents what the system should receive as input.

## Summary

- This framework assumes STT quality is validated externally
- Reference transcripts are provided in test scenarios
- The framework bypasses actual TTS/STT processing
- Use dedicated ASR tools for speech recognition validation
- The TranscriptionValidatorService can compare transcripts when needed
