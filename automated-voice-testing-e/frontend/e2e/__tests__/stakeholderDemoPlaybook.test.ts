import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const DOC_PATH = resolve(__dirname, '../../../docs/presentation/STAKEHOLDER_DEMO_PLAYBOOK.md');

describe('stakeholder demo playbook', () => {
  it('covers agenda, demo script, q&a prep, and follow-up actions', () => {
    const contents = readFileSync(DOC_PATH, 'utf-8');

    expect(contents).toMatch(/# Stakeholder Demo Playbook/);
    expect(contents).toMatch(/## Agenda/);
    expect(contents).toMatch(/## Live Demo Script/);
    expect(contents).toMatch(/## Q&A Preparation/);
    expect(contents).toMatch(/## Follow-Up Actions/);
    expect(contents).toMatch(/Call to Action:/i);
  });
});
