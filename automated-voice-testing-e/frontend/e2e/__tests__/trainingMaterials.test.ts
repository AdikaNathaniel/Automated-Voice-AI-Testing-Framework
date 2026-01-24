import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const DOC_PATH = resolve(__dirname, '../../../docs/training/TRAINING_MATERIALS.md');

describe('user training materials documentation', () => {
  it('outlines validator videos and written guides with actionable steps', () => {
    const contents = readFileSync(DOC_PATH, 'utf-8');

    expect(contents).toMatch(/# User Training Materials/);
    expect(contents).toMatch(/## Validator Video Tutorials/);
    expect(contents).toMatch(/## Test Case Creation Guide/);
    expect(contents).toMatch(/Checklist:/i);
    expect(contents).toMatch(/Call to Action:/i);
  });
});
