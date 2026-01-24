# Task: Audio Upload Feature - Completion & Enhancement

## Overview

The audio upload feature allows testers to upload pre-recorded audio files for test scenarios instead of using TTS (Text-to-Speech). This enables testing with real human speech, specific accents, or audio with background noise.

## Current State Assessment

### What's COMPLETE ✅

| Component | Location | Status |
|-----------|----------|--------|
| Upload Endpoint | `backend/api/routes/scenarios.py:598-780` | Working |
| Audio Transcription | `backend/services/stt_service.py` (Whisper) | Working |
| S3/MinIO Storage | `backend/services/storage_service.py` | Working |
| Audio Utilities | `backend/services/audio_utils.py` | Working |
| Database Model | `backend/models/scenario_script.py` (JSONB) | Working |
| Frontend Upload UI | `frontend/src/pages/Scenarios/StepManager.tsx` | Working |
| Audio Player | `frontend/src/components/Validation/AudioPlayer.tsx` | Working |
| Noise Profiles | `backend/services/noise_profile_library_service.py` | Exists |
| Audio Augmentation | `backend/services/audio_augmentation_service.py` | Exists |

### What Needs Work ⚠️

| Gap | Priority | Effort |
|-----|----------|--------|
| Noise injection UI integration | High | Medium |
| Audio upload route tests | High | Low |
| Error recovery (partial failures) | Medium | Medium |
| Frontend upload component tests | Medium | Low |
| Audio preprocessing (normalization) | Low | Medium |
| Batch upload support | Low | High |

---

## Task 1: Integrate Noise Injection in Upload Flow

### Objective
Allow users to apply noise profiles to uploaded audio before it's used in tests.

### Context
- Noise profiles exist: `GET /api/v1/scenarios/noise-profiles`
- Noise injection service exists: `backend/services/noise_injection_service.py`
- Schema exists: `NoiseConfigCreate` in `backend/api/schemas/scenario.py`

### Requirements

#### Backend
1. **Modify upload endpoint** (`backend/api/routes/scenarios.py`)
   - Add optional `noise_config` parameter to audio upload
   - Apply noise injection after transcription but before storage
   - Store both original and noisy versions (or just noisy with metadata)

2. **Create noise application endpoint** (new)
   ```
   POST /api/v1/scenarios/{scenario_id}/steps/{step_id}/audio/apply-noise
   ```
   - Accept `NoiseConfigCreate` body
   - Apply noise to existing uploaded audio
   - Return new audio info with noise metadata

#### Frontend
1. **Add noise configuration UI** in `StepManager.tsx`
   - Dropdown to select noise profile
   - SNR slider (-10 to 50 dB)
   - Checkbox for "Randomize SNR"
   - Preview button (optional)

2. **Show noise status** in `AudioPlayerCard`
   - Badge showing applied noise profile
   - SNR value display

### Files to Modify
- `backend/api/routes/scenarios.py` - Add noise parameter
- `backend/api/schemas/scenario.py` - May need response schema update
- `frontend/src/pages/Scenarios/StepManager.tsx` - Add noise UI
- `frontend/src/types/scenario.ts` - Add noise config types

### Acceptance Criteria
- [ ] User can select noise profile when uploading audio
- [ ] User can apply noise to already-uploaded audio
- [ ] Noise configuration is saved in step metadata
- [ ] Audio player shows noise profile indicator
- [ ] SNR can be configured (default from profile)

---

## Task 2: Add Test Coverage for Audio Upload

### Objective
Ensure audio upload functionality has comprehensive test coverage.

### Requirements

#### Backend Tests (`backend/tests/test_audio_upload.py` - new file)

```python
# Test cases to implement:

class TestAudioUploadEndpoint:
    """Tests for POST /scenarios/{id}/steps/{step_id}/audio"""

    async def test_upload_mp3_success(self):
        """Upload MP3 file and verify transcription"""

    async def test_upload_wav_success(self):
        """Upload WAV file and verify transcription"""

    async def test_upload_invalid_format_rejected(self):
        """Reject non-audio files (e.g., PDF)"""

    async def test_upload_corrupted_audio_rejected(self):
        """Reject audio files that can't be decoded"""

    async def test_upload_exceeds_size_limit(self):
        """Reject files over size limit"""

    async def test_upload_overwrites_existing(self):
        """Uploading new audio replaces existing"""

    async def test_upload_multi_language_support(self):
        """Different languages can have different audio"""

    async def test_transcription_returns_confidence(self):
        """Verify STT confidence is returned"""


class TestAudioRetrievalEndpoint:
    """Tests for GET /scenarios/{id}/steps/{step_id}/audio/{lang}"""

    async def test_get_audio_returns_presigned_url(self):
        """Verify presigned URL is generated"""

    async def test_get_audio_nonexistent_returns_404(self):
        """Missing audio returns 404"""


class TestAudioDeletionEndpoint:
    """Tests for DELETE /scenarios/{id}/steps/{step_id}/audio/{lang}"""

    async def test_delete_audio_removes_from_s3(self):
        """Verify S3 deletion"""

    async def test_delete_audio_updates_metadata(self):
        """Verify step metadata updated"""

    async def test_delete_reverts_to_tts(self):
        """audio_source reverts to 'tts' after deletion"""
```

#### Frontend Tests (`frontend/src/pages/Scenarios/__tests__/StepManager.test.tsx`)

```typescript
// Test cases to implement:

describe('AudioUploadZone', () => {
  it('renders upload zone when no audio uploaded');
  it('accepts valid audio file on drop');
  it('rejects invalid file type');
  it('shows progress during upload');
  it('displays error on upload failure');
  it('calls API with correct multipart data');
});

describe('AudioPlayerCard', () => {
  it('renders player when audio is uploaded');
  it('displays transcription text');
  it('shows confidence score');
  it('plays audio from S3 URL');
  it('calls delete API on remove click');
});
```

### Acceptance Criteria
- [ ] Backend tests cover all audio endpoints
- [ ] Tests use mocked S3 and Whisper services
- [ ] Frontend tests cover upload and player components
- [ ] All tests pass in CI pipeline
- [ ] Coverage report shows >80% for audio-related code

---

## Task 3: Implement Error Recovery for Partial Failures

### Objective
Handle scenarios where part of the upload process succeeds but another part fails.

### Current Problem
If S3 upload succeeds but database update fails, orphaned files remain in S3.

### Requirements

1. **Implement transaction-like behavior**
   ```python
   # Pseudocode for upload flow
   try:
       # Step 1: Transcribe (can fail early, no cleanup needed)
       transcription = await transcribe(audio_bytes)

       # Step 2: Upload to S3
       s3_key = await storage.upload(audio_bytes)

       # Step 3: Update database
       try:
           await update_step_metadata(step_id, s3_key, transcription)
       except Exception as db_error:
           # Rollback: Delete from S3
           await storage.delete(s3_key)
           raise db_error

   except TranscriptionError:
       # No cleanup needed
       raise
   ```

2. **Add cleanup job for orphaned files** (optional/stretch)
   - Periodic task to find S3 files not referenced in database
   - Log warnings for manual review

### Files to Modify
- `backend/api/routes/scenarios.py` - Add try/except rollback logic
- `backend/services/storage_service.py` - Ensure delete is reliable

### Acceptance Criteria
- [ ] Failed DB update triggers S3 cleanup
- [ ] Failed S3 upload doesn't leave partial state
- [ ] Errors are logged with context for debugging
- [ ] User sees clear error message on failure

---

## Reference: Existing Audio Services

### Audio Processing Services (for reference)
```
backend/services/
├── audio_utils.py                    # Basic utilities (convert, validate, duration)
├── audio_augmentation_service.py     # Speed, pitch, tempo, SpecAugment
├── audio_quality_service.py          # Quality metrics
├── audio_artifact_detection_service.py
├── audio_profile_service.py
├── noise_injection_service.py        # Add noise at specified SNR
├── noise_profile_library_service.py  # Noise profile management
├── iso_voice_audio_service.py
├── road_noise_service.py
├── vehicle_noise_service.py
├── wind_noise_service.py
├── hvac_noise_service.py
├── stt_service.py                    # Whisper transcription
└── storage_service.py                # S3/MinIO storage
```

### Noise Profile Schema
```python
class NoiseConfigCreate(BaseModel):
    enabled: bool = True
    profile: str = "office_ambient"  # Noise profile name
    snr_db: float = 20.0             # Signal-to-noise ratio (-10 to 50)
    randomize_snr: bool = False
    snr_variance: float = 5.0        # Variance when randomizing
```

### API Endpoints
```
POST   /api/v1/scenarios/{id}/steps/{step_id}/audio         # Upload
GET    /api/v1/scenarios/{id}/steps/{step_id}/audio/{lang}  # Get info + URL
DELETE /api/v1/scenarios/{id}/steps/{step_id}/audio/{lang}  # Delete
GET    /api/v1/scenarios/noise-profiles                     # List profiles
```

---

## Getting Started

1. **Set up local environment**
   ```bash
   # Start services
   docker-compose up -d

   # Install backend dependencies
   cd backend && source venv/bin/activate
   pip install -r requirements.txt

   # Install frontend dependencies
   cd frontend && npm install
   ```

2. **Run existing tests**
   ```bash
   # Backend
   cd backend && venv/bin/pytest tests/test_scenarios_routes.py -v

   # Frontend
   cd frontend && npm test
   ```

3. **Test audio upload manually**
   - Start backend: `venv/bin/uvicorn api.main:app --reload`
   - Start frontend: `npm run dev`
   - Navigate to Scenarios → Edit → Steps
   - Try uploading an audio file

---

## Questions?

Contact the team lead for:
- S3/MinIO credentials for local development
- Access to test audio files
- Clarification on noise profile requirements
