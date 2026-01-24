import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const DOC_PATH = resolve(__dirname, '../../../docs/planning/PHASE3_FEEDBACK_BACKLOG.md');

describe('phase 3 feedback & backlog documentation', () => {
  it('includes collected feedback and categorised backlog entries', () => {
    const contents = readFileSync(DOC_PATH, 'utf-8');

    expect(contents).toMatch(/# Phase 3 Feedback & Backlog/);
    expect(contents).toMatch(/## Feedback Summary/);
    expect(contents).toMatch(/## Bug Backlog/);
    expect(contents).toMatch(/## Feature Requests/);
    expect(contents).toMatch(/## Operational Improvements/);
    expect(contents).toMatch(/## Prioritisation & Next Steps/);
    expect(contents).toMatch(/Call to Action:/i);
  });
});
