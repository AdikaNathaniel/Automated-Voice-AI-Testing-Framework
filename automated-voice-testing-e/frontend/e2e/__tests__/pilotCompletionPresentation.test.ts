import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const DOC_PATH = resolve(__dirname, '../../../docs/presentation/PILOT_COMPLETION_PRESENTATION.md');

describe('pilot completion presentation', () => {
  it('documents slide outline, demo script, and metrics for pilot wrap-up', () => {
    const contents = readFileSync(DOC_PATH, 'utf-8');

    expect(contents).toMatch(/# Pilot Completion Presentation/);
    expect(contents).toMatch(/## Slide Outline/);
    expect(contents).toMatch(/## Demo Script/);
    expect(contents).toMatch(/## Metrics Dashboard/);
    expect(contents).toMatch(/Call to Action:/i);
  });
});
