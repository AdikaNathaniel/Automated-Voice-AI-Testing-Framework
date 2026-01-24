import { describe, expect, it } from "vitest";
import type { Config } from "@playwright/test";

let config: Config;

describe("playwright config", () => {
  it("exports default config with expected structure", async () => {
    config = (await import("../playwright.config")).default;
    expect(config).toBeDefined();
    expect(config.testDir).toMatch(/frontend[\\/]+e2e/);
    expect(config.use?.baseURL).toBeDefined();
    expect(config.webServer?.url).toBeDefined();
    expect(config.projects?.length).toBeGreaterThanOrEqual(2);
    expect(config.reporter).toBeDefined();
  });

  it("keeps baseURL and dev server url aligned on the same origin", async () => {
    config = (await import("../playwright.config")).default;
    const baseUrl = new URL(config.use?.baseURL ?? "");
    const serverUrl = new URL(config.webServer?.url ?? "");

    expect(baseUrl.origin).toBe(serverUrl.origin);
    expect(baseUrl.origin).toMatch(/:\d+$/);

    if (!process.env.PLAYWRIGHT_BASE_URL) {
      expect(baseUrl.port).toBe("5173");
      expect(config.webServer?.command).toContain("--port 5173");
    }
  });
});
