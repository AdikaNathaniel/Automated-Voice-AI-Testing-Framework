# Voice AI Testing Framework - MVP Timeline (4 Weeks)

## Overview

**Target Customer**: SoundHound (Automotive Voice AI)
**Duration**: 4 weeks (160 hours)
**Resources**: 1 Senior Expert Developer (40 hrs/week)
**Goal**: Deliver a comprehensive, functional pilot system that demonstrates core value

---

## Scope Philosophy

This MVP is designed to give SoundHound a **complete end-to-end experience** of the testing workflow:

1. **Create and manage test cases** with automotive voice commands
2. **Build multi-turn conversation scenarios** with context carryover
3. **Execute voice tests** with audio generation and Houndify integration
4. **Validate results** through human review workflow
5. **View metrics and reports** on a functional dashboard

We prioritize **depth in core testing** - single-turn AND multi-turn conversation testing to demonstrate full voice AI validation capability.

### Key Trade-offs for Multi-Turn Support
- PDF reports removed (CSV export only)
- Regression UI simplified (API + basic view)
- Reduced automotive sample suite (30 vs 50 test cases)
- Compressed polish time

---

## Week 1: Foundation & Core Data Layer (40 hours)

### Day 1-2: Project Setup (16 hours)

| Task | Hours | Description |
|------|-------|-------------|
| Project initialization | 2 | FastAPI + React + TypeScript scaffolding |
| Development environment | 2 | Docker Compose (PostgreSQL, Redis), virtual environment |
| Configuration management | 2 | Pydantic settings, environment variables |
| Database setup | 3 | SQLAlchemy 2.0, Alembic migrations |
| Basic auth foundation | 4 | JWT tokens, password hashing, user model |
| CI/CD pipeline | 3 | GitHub Actions for tests, linting |

**Deliverable**: Running dev environment with database and basic auth

### Day 3-4: Core Models & Migrations (16 hours)

| Task | Hours | Description |
|------|-------|-------------|
| User & Organization models | 2 | Multi-tenant foundation |
| TestSuite model | 2 | Grouping/organization of tests |
| TestCase model | 2 | Commands, expected outcomes, metadata |
| **ConversationScenario model** | 3 | Multi-turn scenario with ordered steps |
| TestRun model | 2 | Execution batches, status tracking |
| VoiceTestExecution model | 2 | Individual results, **conversation_id** for linking turns |
| ValidationResult model | 2 | Human validation data |
| Relationships & indexes | 1 | Foreign keys, performance indexes |

**Deliverable**: Complete database schema with multi-turn conversation support

### Day 5: API Foundation (8 hours)

| Task | Hours | Description |
|------|-------|-------------|
| API response models | 2 | SuccessResponse, ErrorResponse, Paginated |
| Auth endpoints | 3 | Login, register, refresh token |
| Dependency injection | 2 | Database sessions, current user |
| Error handling | 1 | Global exception handlers |

**Deliverable**: Authenticated API foundation

---

## Week 2: Test Management & Execution Engine (40 hours)

### Day 1-2: Test Management CRUD (16 hours)

| Task | Hours | Description |
|------|-------|-------------|
| TestSuite routes | 2 | Create, list, get, update, delete |
| TestCase routes | 3 | Full CRUD with filtering/pagination |
| **ConversationScenario routes** | 4 | Multi-turn scenario CRUD, step ordering |
| TestRun routes | 3 | Create run, list runs, get details |
| Service layer | 4 | Business logic separation |

**Deliverable**: Complete test management API with conversation scenarios

### Day 3-4: Voice Execution Pipeline (16 hours)

| Task | Hours | Description |
|------|-------|-------------|
| TTS Service | 3 | Google Cloud TTS integration for audio generation |
| Houndify Client | 3 | SoundHound API integration (mock + real) |
| Orchestration Service | 4 | Coordinate TTS -> Houndify -> store results |
| **Conversation Context Manager** | 3 | Maintain state between turns, pass context to Houndify |
| Celery task setup | 2 | Async execution with Redis broker |
| Execution routes | 1 | Trigger runs, check status |

**Deliverable**: Working voice test execution pipeline with multi-turn support

### Day 5: Basic Validation & Metrics (8 hours)

| Task | Hours | Description |
|------|-------|-------------|
| Validation service | 2 | Store human validation decisions |
| WER calculation | 2 | Word Error Rate for transcriptions |
| Intent/Entity accuracy | 2 | NLU metric calculations |
| **Dialog success rate** | 2 | Multi-turn completion tracking |

**Deliverable**: Validation storage with ASR + NLU + dialog metrics

---

## Week 3: Frontend Dashboard & Validation UI (40 hours)

### Day 1-2: React Foundation & Dashboard (16 hours)

| Task | Hours | Description |
|------|-------|-------------|
| React project setup | 2 | Vite, TailwindCSS, routing |
| API client layer | 2 | Axios services, auth interceptors |
| Auth UI | 3 | Login, register, protected routes |
| Dashboard layout | 3 | Navigation, sidebar, header |
| Dashboard metrics | 4 | Test run stats, pass/fail rates, recent activity |
| Charts integration | 2 | Recharts for visualizations |

**Deliverable**: Functional dashboard with real-time metrics

### Day 3-4: Test Management UI (16 hours)

| Task | Hours | Description |
|------|-------|-------------|
| Test Suites page | 2 | List, create, edit suites |
| Test Cases page | 3 | List with filters, create/edit forms |
| **Conversation Scenario Builder** | 5 | Visual multi-turn editor, step ordering, context preview |
| Test Run page | 3 | Create run, view executions |
| Test Run Detail | 2 | Results table with conversation flow view |
| Real-time updates | 1 | WebSocket for execution progress |

**Deliverable**: Complete test management interface with conversation builder

### Day 5: Validation Interface (8 hours)

| Task | Hours | Description |
|------|-------|-------------|
| Validation queue UI | 3 | List pending validations |
| Validation form | 3 | Audio playback, approve/reject/modify |
| Validation stats | 2 | Validator performance metrics |

**Deliverable**: Working human validation workflow

---

## Week 4: Polish, Automotive Features & Demo Prep (40 hours)

### Day 1-2: Automotive-Specific Features (16 hours)

| Task | Hours | Description |
|------|-------|-------------|
| Automotive command categories | 2 | Navigation, media, climate, phone, vehicle |
| **Sample multi-turn scenarios** | 6 | 15 single-turn + 15 multi-turn test scenarios |
| Noise profile service | 4 | SNR-based noise injection (car cabin simulation) |
| Audio profile presets | 2 | Highway, city, HVAC (3 core presets) |
| Domain-specific metrics | 2 | Intent accuracy, entity extraction rate |

**Deliverable**: Automotive-tailored testing with conversation scenarios

### Day 3: Regression & Comparison (8 hours)

| Task | Hours | Description |
|------|-------|-------------|
| Regression service | 4 | Compare test runs, detect degradation |
| Basic regression view | 2 | Simple comparison table (no fancy side-by-side) |
| Baseline management | 2 | Set/update baselines for comparison |

**Deliverable**: Basic regression tracking via API + simple UI

### Day 4: Reports & Export (8 hours)

| Task | Hours | Description |
|------|-------|-------------|
| Report generation | 4 | Summary reports for test runs |
| CSV export | 4 | Full results export for external analysis |

**Deliverable**: CSV export (PDF deferred to post-MVP)

### Day 5: Integration, Testing & Demo Prep (8 hours)

| Task | Hours | Description |
|------|-------|-------------|
| End-to-end testing | 3 | Critical path validation |
| Bug fixes & polish | 3 | UI/UX refinements |
| Demo environment | 1 | Seed data, demo credentials |
| Documentation | 1 | Quick start guide, API overview |

**Deliverable**: Demo-ready system

---

## MVP Feature Summary

### Included in MVP

| Category | Features |
|----------|----------|
| **Authentication** | JWT auth, user registration, login/logout |
| **Test Management** | Test suites, test cases, test runs (full CRUD) |
| **Multi-Turn Conversations** | Conversation scenarios, step ordering, context passing |
| **Voice Execution** | TTS audio generation, Houndify integration, conversation context manager |
| **Validation** | Human validation queue, approve/reject/modify workflow |
| **Metrics** | WER, intent accuracy, entity extraction, **dialog success rate** |
| **Dashboard** | Real-time stats, execution progress, recent activity |
| **Automotive** | Command categories, noise profiles, 30 sample scenarios (single + multi-turn) |
| **Regression** | Run comparison, baseline management, basic comparison view |
| **Reports** | Summary reports, CSV export |

### Not Included in MVP (Deferred to Full Build)

- PDF report generation
- Advanced regression UI (side-by-side comparison)
- Multi-tenant organization management
- Role-based access control (RBAC)
- SSO/OAuth integrations
- CER, SER, RTF metrics
- Full audio quality analysis (PESQ, SNR measurement)
- Telephony/SIP/WebRTC integration
- Load testing framework
- PII detection/redaction
- Advanced ML analytics (drift detection, bias analysis)
- GraphQL/gRPC APIs
- SDK/CLI tools
- Advanced reporting (custom builder, scheduled reports)
- Mobile/PWA support
- Real-time collaboration
- Full automotive standard compliance testing
- Extended noise profile library (only 3 presets in MVP)

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Houndify API issues | Mock client for demos, graceful error handling |
| TTS rate limits | Caching, pre-generated audio for demos |
| Time overrun | Core workflow prioritized; polish items can flex |
| Integration complexity | Service layer abstractions for swappability |
| **Multi-turn context complexity** | Start with simple 2-3 turn scenarios; limit context size |
| **Houndify conversation API** | Verify API supports session context; fallback to stateless if needed |

---

## Success Criteria for Pilot

1. **End-to-end workflow**: Create test -> Execute -> Validate -> Report
2. **Multi-turn capability**: Build and execute 3+ turn conversation scenarios
3. **Automotive relevance**: 30 domain-specific scenarios (single + multi-turn)
4. **Visual appeal**: Clean, professional dashboard with conversation flow view
5. **Reliability**: Zero critical bugs in demo path
6. **Performance**: Execution results in <30 seconds per turn
7. **Export capability**: CSV export for stakeholder analysis

---

## Demo Script Outline

1. **Introduction** (2 min): Overview of the platform
2. **Test Suite Creation** (3 min): Create automotive navigation test suite
3. **Single-Turn Test Cases** (3 min): Add simple command test cases
4. **Multi-Turn Conversation Builder** (7 min): Build a 3-turn navigation scenario:
   - Turn 1: "Find coffee shops nearby"
   - Turn 2: "The one on Main Street"
   - Turn 3: "Navigate there"
5. **Execute Test Run** (5 min): Trigger execution, watch real-time progress
6. **Review Results** (5 min): View conversation flow, per-turn metrics, dialog success rate
7. **Human Validation** (5 min): Validate ambiguous results
8. **Regression Comparison** (3 min): Compare with previous run
9. **Export Results** (2 min): Download CSV for analysis
10. **Q&A** (10 min)

**Total Demo Time**: ~45 minutes

**Demo Highlight**: The conversation scenario builder shows context passing between turns - demonstrating we're testing the full NLU stack, not just ASR.

---

## Post-MVP Immediate Priorities

After successful pilot, prioritize based on SoundHound feedback:

1. **Week 5**: PDF report generation, advanced regression UI
2. **Week 6-7**: RBAC, multi-tenant isolation
3. **Week 8-9**: Additional metrics (CER, SER, RTF)
4. **Week 10-11**: Audio quality measurement, SNR analysis
5. **Week 12**: Extended noise profile library, more automotive presets

---

## Technical Debt Acknowledgment

Items intentionally simplified for MVP speed:

- Minimal input validation (expand for production)
- Basic error messages (improve UX in v2)
- Single-region deployment (add HA later)
- In-memory caching only (add Redis caching)
- Basic logging (add structured logging + monitoring)
- Limited test coverage (expand to 80%+ for production)

---

**Total Effort**: 160 hours (4 weeks x 40 hrs/week)

**Confidence Level**: High - scope is aggressive but achievable with expert-level execution and minimal scope creep.
