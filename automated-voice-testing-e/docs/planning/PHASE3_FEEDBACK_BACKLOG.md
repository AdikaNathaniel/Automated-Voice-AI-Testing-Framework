# Phase 3 Feedback & Backlog

This document consolidates stakeholder feedback gathered after the pilot, categorises action items, and seeds the Phase 3 backlog for refinement.

## Feedback Summary

- **Stakeholders:** Product leadership, QA managers, validator leads, DevOps, ML team.
- **Highlights:** Appreciation for unified dashboard, ML-assisted scoring promise, and CI/CD visibility.
- **Concerns:** Need clearer rollout timeline, data residency assurances, and more granular validator productivity metrics.
- **Opportunities:** Automate validator coaching, surface multilingual coverage gaps, and improve failure triage workflows.

## Bug Backlog

| Priority | Area | Description | Owner | Notes |
| --- | --- | --- | --- | --- |
| P0 | Validation queue | Claimed validations occasionally reappear in queue when connection drops. | Backend | Requires websocket reconnect handling. |
| P1 | Dashboard metrics | Real-time execution widget shows `NaN` when Redis cache is cold. | DevOps | Add fallback defaults and cache warmup task. |
| P1 | Translation workflow | Status chips sometimes display stale counts after bulk updates. | Frontend | Revalidate queries on mutation success. |
| P2 | CI/CD runs | Commit link broken for self-hosted GitLab pipelines. | Integrations | Add host detection and custom URL templating. |

## Feature Requests

- **Validator productivity insights:** session analytics, streak tracking, and heatmaps for decision distribution.
- **Edge case library:** curated examples with reusable templates and tagging for rapid scenario creation.
- **Automated retraining loop:** schedule ML model retraining when drift detected or accuracy dips below thresholds.
- **Localization support:** dynamic locale packs for UI strings and validator instructions.

## Operational Improvements

- **Runbook maturity:** publish incident response workflows for ML service degradation and redis cache outages.
- **Access governance:** integrate with SSO groups to automate onboarding/offboarding of validators.
- **Testing strategy:** expand smoke test suite for translations and add nightly long-run regression pack.
- **Observability:** add uptime SLO dashboards and alerting for queue depth anomalies.

## Prioritisation & Next Steps

1. Validate priorities during Phase 3 kickoff workshop; confirm success metrics and owners.
2. Groom top 10 backlog items into sprint-ready issues with acceptance criteria.
3. Schedule technical spikes for ML retraining pipeline and edge case detection architecture.
4. Update roadmap to reflect dependencies with infrastructure capacity expansion.

Call to Action: Review this backlog with the Phase 3 core team, capture missing feedback, and align on sprint sequencing before project kickoff.
