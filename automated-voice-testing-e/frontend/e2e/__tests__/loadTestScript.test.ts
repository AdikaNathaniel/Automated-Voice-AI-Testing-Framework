import { describe, expect, it } from "vitest";

import path from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const currentDir = path.dirname(fileURLToPath(import.meta.url));
const configPath = path.resolve(currentDir, "../../../load-tests/k6/testExecutionConfig.cjs");
const requireModule = createRequire(import.meta.url);

describe("Load testing script", () => {
  it("exports k6 options with 1000+ virtual users and response/error thresholds", async () => {
    const { testExecutionOptions, createSummaryHandler } = requireModule(configPath);

    expect(testExecutionOptions).toBeDefined();
    expect(typeof createSummaryHandler).toBe("function");

    const scenario = testExecutionOptions.scenarios?.test_execution;
    expect(scenario).toBeDefined();
    expect(scenario.executor).toMatch(/vus/i);

    const targetVUs = scenario.stages?.reduce(
      (max: number, stage: { target?: number }) => Math.max(max, stage.target ?? 0),
      0,
    );
    expect(targetVUs).toBeGreaterThanOrEqual(1000);

    expect(testExecutionOptions.thresholds?.http_req_duration).toBeDefined();
    expect(testExecutionOptions.thresholds?.http_req_failed).toBeDefined();

    const summary = createSummaryHandler()({ metrics: {} }, {});
    expect(summary["load-results.json"]).toBeDefined();
    expect(summary.stdout).toMatch(/k6 load test summary/i);
  });
});
