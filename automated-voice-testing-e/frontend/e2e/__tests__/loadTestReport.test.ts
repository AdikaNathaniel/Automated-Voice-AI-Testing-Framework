import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const REPORT_PATH = resolve(__dirname, '../../../load-tests/REPORT.md');

describe('load test report documentation', () => {
  it('includes the required sections and actionable insights', () => {
    const contents = readFileSync(REPORT_PATH, 'utf-8');

    expect(contents).toMatch(/# Load Test Report/);
    expect(contents).toMatch(/## Results/);
    expect(contents).toMatch(/## Bottlenecks/);
    expect(contents).toMatch(/## Optimizations/);

    expect(contents).toMatch(/Requests per second/i);
    expect(contents).toMatch(/p95 latency/i);
    expect(contents).toMatch(/next steps/i);
  });
});
