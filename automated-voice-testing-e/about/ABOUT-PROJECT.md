# About: Automated Voice AI Testing Framework

## What This Project Is About

**Automated Voice AI Testing Framework** is an enterprise-grade platform for testing voice AI systems, specifically designed for automotive and enterprise environments.

---

## The Problem It Solves

When companies build voice assistants (like those in cars - "Hey car, navigate to the nearest gas station"), they need to test that:

- The voice AI understands different accents and languages
- It handles background noise (road noise, wind, AC)
- It responds correctly to thousands of different commands
- It maintains quality across updates

Manual testing is slow and inconsistent. This framework automates it at scale.

---

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│  1. Define Test Scenarios                               │
│     "Play music" → expects music to start               │
│     "Navigate home" → expects navigation to begin       │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  2. Execute Tests                                       │
│     - Convert text to speech (TTS) or use real audio   │
│     - Send audio to Voice AI (SoundHound)              │
│     - Capture the response                              │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  3. Validate Results                                    │
│     - AI-powered semantic matching                      │
│     - Human review for edge cases                       │
│     - 99.7% accuracy through ML + human validation      │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  4. Report & Monitor                                    │
│     - Real-time dashboards                              │
│     - Defect tracking                                   │
│     - CI/CD integration                                 │
└─────────────────────────────────────────────────────────┘
```

---

## Key Features

| Feature | Description |
|---------|-------------|
| **High-volume testing** | 1000+ tests/day, scalable to 10,000+ |
| **Multi-language** | 8+ languages supported |
| **Noise simulation** | Test with road noise, wind, HVAC sounds |
| **Human-in-the-loop** | Expert validation for edge cases |
| **Audio upload** | Test with real human recordings |
| **CI/CD integration** | Automated testing in deployment pipelines |

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Validation Accuracy | 99.7% |
| Tests per Day | 1000+ (scalable to 10,000+) |
| Feedback Cycle | < 4 hours |
| Languages Supported | 8+ |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python, FastAPI, SQLAlchemy, PostgreSQL |
| **Frontend** | React, TypeScript, Vite, TailwindCSS |
| **Infrastructure** | Docker, Redis, RabbitMQ, MinIO (S3) |
| **Voice AI** | SoundHound API, Whisper (transcription) |
| **Testing** | pytest (backend), Vitest (frontend) |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Web Dashboard (React)                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway (FastAPI)                     │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ Orchestration│      │  Execution   │      │  Validation  │
│   Service    │      │   Engines    │      │   Service    │
└──────────────┘      └──────────────┘      └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Message Queue (RabbitMQ/Celery)                 │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  PostgreSQL  │      │    MinIO     │      │    Redis     │
│  (Metadata)  │      │  (Storage)   │      │   (Cache)    │
└──────────────┘      └──────────────┘      └──────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 External Integrations                        │
│     SoundHound API │ GitHub │ Jira │ Slack │ AWS S3        │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Components

| Component | Purpose |
|-----------|---------|
| **Test Orchestration** | Manages test execution, scheduling, and coordination |
| **Execution Engines** | Three parallel engines for voice, device, and validation |
| **Human Validation** | Quality assurance for edge cases and low-confidence results |
| **Reporting & Analytics** | Real-time dashboards, defect tracking, trend analysis |
| **Integration Layer** | CI/CD pipelines, external tools, notification systems |

---

## Audio Services

The framework includes comprehensive audio processing capabilities:

| Service | Purpose |
|---------|---------|
| `stt_service.py` | Whisper-based speech-to-text transcription |
| `storage_service.py` | S3/MinIO file storage |
| `noise_injection_service.py` | Add noise at specified SNR levels |
| `audio_augmentation_service.py` | Speed, pitch, tempo modifications |
| `road_noise_service.py` | Simulate road/vehicle noise |
| `wind_noise_service.py` | Simulate wind noise |
| `hvac_noise_service.py` | Simulate HVAC/AC noise |

---

## Project Structure

```
automated-testing/
├── backend/                 # Python/FastAPI backend
│   ├── api/                # API endpoints and routes
│   ├── services/           # Business logic layer
│   ├── models/             # SQLAlchemy database models
│   └── tests/              # Backend test suites
├── frontend/               # React/TypeScript frontend
│   ├── src/               # Source code
│   └── public/            # Static assets
├── infrastructure/         # Infrastructure as Code
├── docs/                  # Documentation
├── about/                 # Project information (this folder)
└── scripts/               # Automation scripts
```

---

## Use Cases

### 1. Automotive Voice Assistant Testing
Test in-car voice commands with realistic conditions:
- Road noise simulation
- Multiple languages/accents
- Navigation, media, climate control commands

### 2. Smart Speaker/Device Testing
Validate voice interactions for home assistants:
- Background noise (TV, music, conversations)
- Far-field voice recognition
- Multi-turn conversations

### 3. Call Center AI Testing
Test automated phone systems:
- Hold music and background noise
- Accent variations
- Intent recognition accuracy

---

## Getting Started

### Quick Start (Docker)
```bash
# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
```

### Development Setup
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn api.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

---

## Login Credentials (Development)

| Account | Email | Password |
|---------|-------|----------|
| Demo User | demo@example.com | DemoPassword123! |
| Demo Admin | demo@voiceai.dev | DemoAdmin123! |
| Admin | admin@voiceai.com | admin123 |

---

## Learn More

- [README.md](../README.md) - Full documentation
- [docs/setup-guide.md](../docs/setup-guide.md) - Detailed setup instructions
- [docs/api-guide.md](../docs/api-guide.md) - API documentation
- [CLAUDE.md](../CLAUDE.md) - Development guide

---

**Built by Productive Playhouse**

*Delivering automotive-grade voice AI testing with proven 99.7% accuracy*
