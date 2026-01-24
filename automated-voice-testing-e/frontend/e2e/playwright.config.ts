import path from "node:path";
import { defineConfig, devices } from "@playwright/test";
import dotenv from "dotenv";

dotenv.config({ path: path.resolve(__dirname, "../.env") });

const DEFAULT_BASE_URL = process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:5173";
const { port: basePort } = new URL(DEFAULT_BASE_URL);
const DEV_SERVER_PORT = basePort || "5173";

export default defineConfig({
  testDir: path.resolve(__dirname),
  testMatch: "*.spec.ts",
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,
  reporter: [
    ["line"],
    ["html", { outputFolder: path.resolve(__dirname, "../test-results/playwright"), open: "never" }],
  ],
  timeout: 60 * 1000,
  outputDir: path.resolve(__dirname, "../test-results/playwright-artifacts"),
  use: {
    baseURL: DEFAULT_BASE_URL,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    actionTimeout: 15 * 1000,
    navigationTimeout: 30 * 1000,
  },
  webServer: {
    command: `npm run dev -- --host --port ${DEV_SERVER_PORT}`,
    url: DEFAULT_BASE_URL,
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: "firefox",
      use: { ...devices["Desktop Firefox"] },
    },
    {
      name: "webkit",
      use: { ...devices["Desktop Safari"] },
    },
  ],
});
