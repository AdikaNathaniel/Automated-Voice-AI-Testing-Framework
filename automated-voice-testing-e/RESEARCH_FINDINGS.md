# Voice AI Testing Framework - Research Findings

**Date:** 2025-10-25
**Research Focus:** SoundHound/Houndify API, Voice AI Testing Best Practices

## Executive Summary

Based on comprehensive research into SoundHound's Houndify platform and voice AI testing methodologies, this document outlines key findings that inform our testing framework architecture.

---

## 1. Houndify Platform Overview

### Platform Name
**Houndify** (not just "SoundHound API") - This is SoundHound's developer platform for conversational AI.

### Core Technology Stack
- **Speech-to-Meaning®** - Proprietary technology for direct speech interpretation
- **Deep Meaning Understanding®** - Advanced NLU capabilities
- **Polaris ASR Model** - Low word error rate, can be fine-tuned
- **ASR** (Automatic Speech Recognition)
- **NLU** (Natural Language Understanding)
- **TTS** (Text-to-Speech)
- **Wake Words**
- **Custom Domains**

### Recognition
- Named a **Leader in IDC MarketScape: Conversational AI Platforms 2025**
- Processes ~10 billion queries per year

---

## 2. API Architecture

### Authentication
- **Method:** Client ID + Client Key (API Key model)
- **Environment Variables:**
  - `HOUNDIFY_CLIENT_ID`
  - `HOUNDIFY_CLIENT_KEY`
- **SDK handles authentication automatically**

### Endpoints
```
Text Queries:  https://api.houndify.com/v1/text
Audio Queries: https://api.houndify.com/v1/audio
```

### API Types
- **HTTP REST API** - Request/response pattern
- **WebSocket API** - Streaming for real-time interaction

### Request Format

#### Text Request
```python
{
    "Query": "what time is it in paris",
    "UserID": "appUser123",
    "RequestID": "uniqueRequest456",
    "RequestInfoFields": {
        "Latitude": 37.7749,
        "Longitude": -122.4194,
        "PartialTranscriptsDesired": true
        # Additional context fields...
    }
}
```

#### Voice Request
```python
{
    "AudioStream": <bytes>,  # Pre-encoded audio data
    "UserID": "appUser123",
    "RequestID": "uniqueRequest456",
    "RequestInfoFields": {}
}
```

### Response Format

#### Basic Structure
```json
{
    "AllResults": [{
        "RawTranscription": "what time is it in paris",
        "FormattedTranscription": "What time is it in Paris?",
        "CommandResults": [...],
        "ConversationState": {...}
    }],
    "ResponseAudioBytes": "<base64_encoded_audio>"  // If TTS requested
}
```

#### CommandResults Structure
```json
{
    "CommandKind": "WeatherQuery|MapSearch|etc",
    "Entities": {
        "location": "Paris",
        "time": "current"
    },
    "Confidence": 0.95,
    "SpokenResponse": "It's 3:45 PM in Paris",
    "SpokenResponseLong": "The current time in Paris, France is 3:45 PM"
}
```

---

## 3. Key Features

### Conversation State Management
```python
# SDK provides methods:
client.EnableConversationState()
client.DisableConversationState()
client.ClearConversationState()
state = client.GetConversationState()
client.SetConversationState(new_state)
```

**Purpose:** Enable multi-turn conversations with context retention

### Partial Transcripts
- Real-time streaming of transcription as user speaks
- Enabled via `PartialTranscriptsDesired: true` in RequestInfo
- Useful for live UI updates

### Text-to-Speech (TTS)

**Important:** TTS requires **paid account** (not available in free tier)

**Configuration Fields:**
- `ResponseAudioVoice` - Voice selection (e.g., "Mia")
- `ResponseAudioShortOrLong` - Use short or long response
- `ResponseAudioEncoding` - Format (WAV, MP3, etc.)

**TTS Providers:** ReadSpeaker, Acapela, Selvy (multiple language support)

---

## 4. Voice AI Testing Methodologies

### Industry-Standard Metrics

#### 1. Word Error Rate (WER)
**Formula:** `WER = (Substitutions + Deletions + Insertions) / Total Words`

**Limitations:**
- Doesn't capture semantic meaning
- Treats all words equally (ignores importance)
- Focuses on transcription, not interaction quality

#### 2. Semantic Similarity (SeMaScore)
- Evaluates meaning preservation, not just exact words
- More robust than WER for conversational AI
- Measures understanding vs. transcription accuracy

#### 3. Task Success Rate (TSR)
- **Strict Success:** Goal completed with all constraints met
- **Soft Success:** Goal completed with some constraints relaxed
- **Task Completion Time (TCT)**
- **Turns-to-Success:** Number of dialog turns needed

#### 4. Hallucination-Under-Noise (HUN) Rate
- Measures fluent but semantically incorrect outputs
- Critical for safety and reliability
- Tests robustness to acoustic perturbations

### Testing Challenges

**Probabilistic Nature:**
- Voice AI operates probabilistically, not deterministically
- Same input can produce different outputs
- Requires statistical validation approaches

**Speech Recognition Quality Factors:**
- Audio quality variations
- Dialects and accents
- Environmental noise
- Background interference
- Interruptions and cross-talk

**Edge Cases to Test:**
- Ambiguous queries
- Context switching
- Follow-up questions
- Confirmations and clarifications
- Fallback behavior
- Out-of-domain requests

---

## 5. Voice AI Testing Platforms (2025)

### Commercial Solutions
1. **Hamming** - Simulates thousands of calls, audits live conversations, heartbeat checks
2. **Coval** - Simulation and evaluation for Voice & Chat agents
3. **Cekura** - End-to-end testing with diverse persona simulations
4. **Bespoken AI** - Automated testing for IVR, AI, chatbots
5. **Cognigy** - Regression testing and voice UX validation
6. **Botium** - Test automation framework
7. **Cyara** - Enterprise voice testing
8. **Speechly** - Voice UX validation
9. **Voiceflow** - Conversation design testing

### Testing Layers
1. **Model Testing** - ASR/NLU accuracy
2. **Functional Testing** - Feature validation
3. **End-to-End Testing** - Full conversation flows
4. **Manual Testing** - Human validation (essential for natural speech patterns)

---

## 6. Implications for Our Framework

### Architecture Decisions

#### 1. Client Implementation
```python
class HoundifyClient:  # Not "SoundHoundClient"
    def __init__(self, client_id: str, client_key: str):
        self.client_id = client_id
        self.client_key = client_key
        self.base_url = "https://api.houndify.com/v1"

    async def voice_query(
        self,
        audio_data: bytes,
        user_id: str,
        request_id: str,
        request_info: dict = None
    ) -> HoundifyResponse:
        """Send voice query to Houndify"""
        pass

    async def text_query(
        self,
        query: str,
        user_id: str,
        request_id: str,
        request_info: dict = None
    ) -> HoundifyResponse:
        """Send text query to Houndify"""
        pass

    def enable_conversation_state(self):
        """Enable conversation context"""
        pass
```

#### 2. Response Models
```python
class HoundifyResponse(BaseModel):
    raw_transcription: str
    formatted_transcription: str
    command_kind: str  # Not just "intent"
    entities: Dict[str, Any]
    confidence: float
    spoken_response: str
    spoken_response_long: Optional[str]
    conversation_state: Optional[Dict[str, Any]]
    response_audio_bytes: Optional[bytes]  # TTS output
    response_time_ms: int
```

#### 3. Testing Validation
```python
class TestValidation(BaseModel):
    wer: float  # Word Error Rate
    semantic_similarity: float  # SeMaScore or similar
    task_success: bool  # Did it complete the goal?
    turns_to_success: int
    response_time_ms: int
    confidence_score: float
    hallucination_detected: bool
```

### Audio Requirements
- **Pre-encoding required** - Audio must be in specific format before sending
- **Streaming support** - Via WebSocket for real-time interaction
- **Partial transcripts** - For progressive UI updates

### Free Tier Limitations
- ✅ Voice-to-Text (STT)
- ✅ Text queries
- ✅ All SDKs and documentation
- ❌ Text-to-Speech (TTS) - Requires paid account

### Testing Strategy
1. **Deterministic baseline** - Text-based testing for reproducibility
2. **Statistical validation** - Multiple runs for voice testing
3. **Edge case library** - Accents, noise, interruptions
4. **Semantic validation** - Beyond exact match
5. **Human-in-the-loop** - For ambiguous cases

---

## 7. Recommended Implementation Approach

### Phase 1: Foundation (Current - TASK-106/107)
- Implement Houndify client (not generic "SoundHound")
- Focus on text queries first (more deterministic)
- Create response models matching actual Houndify structure
- Mock client for testing without API calls

### Phase 2: Voice Integration
- Add voice query support
- Implement audio encoding utilities
- Add partial transcript handling
- WebSocket streaming support

### Phase 3: Advanced Features
- Conversation state management
- TTS integration (requires paid account or mock)
- Multi-language support
- Custom domain integration

### Phase 4: Validation Framework
- WER calculation utilities
- Semantic similarity scoring
- Task success evaluation
- Statistical analysis tools

---

## 8. Key Corrections to Original Plan

| Original Assumption | Actual Reality |
|---------------------|----------------|
| "SoundHound API" | Houndify Platform |
| Generic `send_voice_command` | `voice_query` + `text_query` separate methods |
| Simple `VoiceResponse` | Complex `HoundifyResponse` with multiple result types |
| TTS always available | TTS requires paid account |
| Single response format | Variable structure based on CommandKind |
| Direct intent/entities | Nested in CommandResults |
| Simple confidence score | Per-command confidence + overall metrics |

---

## 9. References

- **Houndify Developer Platform:** https://www.soundhound.com/voice-ai-products/developer/
- **Houndify Go SDK:** https://github.com/soundhound/houndify-sdk-go
- **Voice AI Testing Best Practices 2025:** Multiple industry sources
- **SeMaScore Paper:** https://arxiv.org/html/2401.07506v1
- **WER Evaluation:** Hugging Face Audio Course

---

## 10. Next Steps

1. **Update TODOS.md** - Reflect Houndify terminology and accurate API patterns
2. **Revise TASK-106** - Implement `HoundifyClient` with correct methods
3. **Revise TASK-107** - Create response models matching actual structure
4. **Add TASK-106A** - Create audio encoding utilities (if needed)
5. **Document free tier limitations** - Note TTS requires paid account
6. **Plan mock implementation** - Separate mock for testing without API access

---

**Research Completed:** 2025-10-25
**Next Review:** As implementation progresses and API access obtained
