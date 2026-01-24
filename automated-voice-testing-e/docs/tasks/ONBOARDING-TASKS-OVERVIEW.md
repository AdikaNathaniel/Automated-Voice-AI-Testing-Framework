# Developer Onboarding Tasks - Overview

## Quick Summary

| Task | Feature | Priority | Estimated Effort | Skills Needed |
|------|---------|----------|------------------|---------------|
| [TASK-AUDIO-UPLOAD](./TASK-AUDIO-UPLOAD.md) | Audio Upload + Noise | High | 3-5 days | Python, React, Audio/DSP basics |
| [TASK-INTEGRATIONS](./TASK-INTEGRATIONS.md) | Slack & Jira | High | 3-5 days | Python, React, REST APIs |

---

## Task 1: Audio Upload Feature

### Current State
**Backend: 95% Complete** | **Frontend: 90% Complete**

The audio upload feature is functionally complete end-to-end. Users can:
- Upload audio files (MP3, WAV, OGG, FLAC)
- Audio is transcribed via Whisper AI
- Audio stored in S3/MinIO
- Play back uploaded audio with waveform visualization

### What's Missing
1. **Noise injection UI** - Backend has noise services, but no UI to apply noise to uploaded audio
2. **Test coverage** - No dedicated tests for audio upload routes
3. **Error recovery** - Partial failure scenarios not handled

### Key Files
```
Backend:
├── api/routes/scenarios.py          # Upload endpoint (lines 598-780)
├── services/stt_service.py          # Whisper transcription
├── services/storage_service.py      # S3/MinIO storage
├── services/noise_injection_service.py  # Noise addition
└── services/audio_utils.py          # Audio utilities

Frontend:
├── pages/Scenarios/StepManager.tsx  # Upload UI + Player
└── components/Validation/AudioPlayer.tsx  # Playback component
```

### Sub-tasks
| # | Task | Priority | Effort |
|---|------|----------|--------|
| 1.1 | Integrate noise injection UI | High | 2 days |
| 1.2 | Add backend tests for audio upload | High | 1 day |
| 1.3 | Implement error recovery for partial failures | Medium | 1 day |

---

## Task 2: Slack & Jira Integrations

### Current State
**Slack: 85% Complete** | **Jira: 80% Complete**

Both integrations have clients, models, API routes, and UI. The infrastructure is solid.

### What's Missing
1. **Notification trigger points** - Services exist but aren't called from test execution flow
2. **Auto-create Jira tickets** - Fields exist on Defect model, but flow not wired up
3. **Integration health monitoring** - No visibility into integration status

### Key Files
```
Backend:
├── integrations/slack/client.py     # Slack webhook client
├── integrations/slack/bot.py        # Slash command handler
├── integrations/jira/client.py      # Jira REST client
├── services/notification_service.py # Notification dispatcher
├── models/notification_config.py    # Slack config (encrypted)
├── models/integration_config.py     # Jira config (encrypted)
└── models/defect.py                 # Has jira_issue_key field

Frontend:
├── pages/Integrations/Slack.tsx     # Slack config UI
├── pages/Integrations/Jira.tsx      # Jira config UI
└── store/slices/slackIntegrationSlice.ts
```

### Sub-tasks
| # | Task | Priority | Effort |
|---|------|----------|--------|
| 2.1 | Wire notification triggers to test execution | High | 2 days |
| 2.2 | Implement auto-create Jira from defect | High | 1.5 days |
| 2.3 | Add integration health monitoring UI | Medium | 1 day |

---

## Recommended Assignment

### For Developer with Audio/Signal Processing Interest
→ **Assign: TASK-AUDIO-UPLOAD**

This task involves:
- Understanding audio file formats
- Working with noise profiles and SNR
- File upload/download flows
- Some DSP concepts (optional but helpful)

### For Developer with API/Integration Interest
→ **Assign: TASK-INTEGRATIONS**

This task involves:
- REST API integration patterns
- OAuth/API token authentication
- Webhook handling
- State management and async flows

---

## Environment Setup

Both tasks require the same environment:

```bash
# 1. Start Docker services
docker-compose up -d

# 2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Frontend setup
cd frontend
npm install

# 4. Environment variables
cp .env.example .env
# Edit .env with your credentials

# 5. Run services
# Terminal 1: Backend
cd backend && venv/bin/uvicorn api.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev
```

---

## Definition of Done

For each task to be considered complete:

- [ ] All acceptance criteria in task spec are met
- [ ] Code follows project conventions (see CLAUDE.md)
- [ ] Tests written and passing
- [ ] No TypeScript/Python type errors
- [ ] PR created with clear description
- [ ] Code reviewed and approved
- [ ] Documentation updated if needed

---

## Support Resources

- **Project conventions**: `/CLAUDE.md`
- **API documentation**: `http://localhost:8000/docs` (when backend running)
- **Existing tests**: `backend/tests/` and `frontend/src/**/__tests__/`
- **Team lead**: For questions, blockers, or clarification
