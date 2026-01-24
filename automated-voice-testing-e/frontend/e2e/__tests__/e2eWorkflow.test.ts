import { describe, expect, it } from "vitest";
import fs from "node:fs";
import path from "node:path";

const WORKFLOW_PATH = path.resolve(
  __dirname,
  "../../../.github/workflows/e2e-tests.yml",
);

describe("E2E CI workflow", () => {
  it("exists and runs Playwright tests via npm script", () => {
    expect(fs.existsSync(WORKFLOW_PATH)).toBe(true);

    const content = fs.readFileSync(WORKFLOW_PATH, "utf8");
    expect(content).toMatch(/name:\s*E2E Tests/i);
    expect(content).toMatch(/actions\/setup-node@v\d+/);
    expect(content).toMatch(/npm (?:ci|install)/);
    expect(content).toMatch(/npx playwright install --with-deps/);
    expect(content).toMatch(/npm run test:e2e/);
  });
});
