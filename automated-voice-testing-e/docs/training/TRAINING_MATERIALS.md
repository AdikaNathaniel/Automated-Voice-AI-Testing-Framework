# User Training Materials

Prepared by: Enablement Team  
Release date: 2025-02-15  
Audience: Human validators, test case authors, team leads

## Validator Video Tutorials

| Module | Duration | Format | Assets |
| --- | --- | --- | --- |
| V-101: Platform Overview | 6 min | Screencast with voiceover | Script: `docs/training/scripts/V-101-platform-overview.md`; Recording: `https://videos.voiceai.example.com/V-101` |
| V-201: Performing Human Validation | 9 min | Scenario-based walkthrough | Script: `docs/training/scripts/V-201-human-validation.md`; Recording: `https://videos.voiceai.example.com/V-201` |
| V-220: Applying Quality Standards | 7 min | Interactive quiz recap | Script: `docs/training/scripts/V-220-quality-standards.md`; Recording: `https://videos.voiceai.example.com/V-220` |
| V-260: Escalation & Feedback Loop | 5 min | Animated whiteboard | Script: `docs/training/scripts/V-260-escalations.md`; Recording: `https://videos.voiceai.example.com/V-260` |

Checklist:
- [ ] Watch V-101 before receiving sandbox access.
- [ ] Complete in-app quiz tied to V-201 (passing score ≥ 85%).
- [ ] Submit verification screenshot for V-220 interactive quiz.
- [ ] Acknowledge escalation SOP from V-260 by signing Confluence page.

Call to Action: Validators must finish all four modules within their first onboarding week and upload quiz certificates to the team shared drive.

## Test Case Creation Guide

1. **Overview** – Introductory video (T-110) explains the end-to-end lifecycle (`https://videos.voiceai.example.com/T-110`).
2. **Written Guide** – Detailed steps stored at `docs/training/guides/test-case-creation.md` covering:
   - Persona definition
   - Input design (happy path vs. negative)
   - Expected outcome structure
   - Localization requirements
3. **Templates** – Notion template link: `https://notion.voiceai.example.com/templates/test-case`.
4. **Review Flow** – Check with assigned reviewer using the `#qa-review` Slack channel.

Checklist:
- [ ] Draft test case using the latest template version.
- [ ] Run against validation checklist (Section 4 of the written guide).
- [ ] Attach media artifacts (audio/text) to the submission.
- [ ] Request reviewer sign-off and capture comments in Jira ticket.

Call to Action: Before publishing new cases, authors must record a 2-minute Loom summary appended to the Jira issue to accelerate reviewer context-switching.

## Additional Resources

- **Office Hours** – Weekly Thursday 15:00 UTC (`meet.voiceai.example.com/enablement`).  
- **FAQ** – `docs/training/faq.md` maintained with common validator questions.  
- **Support** – Contact `enablement@voiceai.example.com` for access issues or training feedback.

## Next Steps

1. Team leads assign modules via LMS and track completion.  
2. Enablement team to update scripts quarterly with latest product changes.  
3. Collect feedback via post-training survey (`forms.voiceai.example.com/validator-training`).  
4. Measure impact by comparing validation accuracy before/after training (reported in weekly ops review).
