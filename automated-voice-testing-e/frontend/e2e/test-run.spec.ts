import { expect, test } from "@playwright/test";

const TEST_EMAIL = process.env.E2E_TEST_EMAIL ?? "user@example.com";
const TEST_PASSWORD = process.env.E2E_TEST_PASSWORD ?? "password123";
const AUTH_BASE = process.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

const LOGIN_ENDPOINT = `${AUTH_BASE.replace(/\/$/, "")}/auth/login`;
const DEFAULT_UI_BASE =
  process.env.PLAYWRIGHT_BASE_URL ?? process.env.VITE_APP_URL ?? "http://localhost:5173";

function resolveUrl(baseURL: string | undefined, path: string): string {
  const base = baseURL ?? DEFAULT_UI_BASE;
  return new URL(path, base).toString();
}

async function authenticate(page: Parameters<typeof test>[0]["page"], baseURL: string | undefined) {
  await page.route(LOGIN_ENDPOINT, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        access_token: "fake-access-token",
        refresh_token: "fake-refresh-token",
        token_type: "bearer",
        expires_in: 3600,
        user: {
          id: "user-1",
          email: TEST_EMAIL,
          username: "e2e.user",
          full_name: "E2E User",
          role: "tester",
          is_active: true,
          created_at: "2023-01-01T00:00:00Z",
          updated_at: null,
        },
      }),
    });
  });

  await page.goto(resolveUrl(baseURL, "/login"));
  await page.getByLabel(/email address/i).fill(TEST_EMAIL);
  await page.getByLabel(/password/i).fill(TEST_PASSWORD);
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page).toHaveURL(/\/$/);
  await expect(page.getByRole("heading", { name: /automated testing platform/i })).toBeVisible();
}

test.describe("Test run overview", () => {
  test("allows a user to view and filter recent test runs", async ({ page, baseURL }) => {
    await authenticate(page, baseURL);

    const initialRuns = [
      {
        id: "run-en",
        testSuiteId: "suite-1",
        status: "completed" as const,
        languageCode: "en-US",
        totalTests: 120,
        passedTests: 118,
        failedTests: 1,
        skippedTests: 1,
        startedAt: "2024-02-01T10:00:00Z",
        completedAt: "2024-02-01T10:07:00Z",
      },
      {
        id: "run-ja",
        testSuiteId: "suite-2",
        status: "failed" as const,
        languageCode: "ja-JP",
        totalTests: 80,
        passedTests: 70,
        failedTests: 8,
        skippedTests: 2,
        startedAt: "2024-02-02T12:00:00Z",
        completedAt: "2024-02-02T12:09:00Z",
      },
    ];

    const requestedLanguages: Array<string | null> = [];

    await page.route("**/v1/test-runs**", async (route) => {
      const url = new URL(route.request().url());
      const param = url.searchParams.get("language_code");
      const normalized = !param || param === "null" || param.trim() === "" ? null : param;
      requestedLanguages.push(normalized);

      const runs =
        normalized === null
          ? initialRuns
          : initialRuns.filter((run) => run.languageCode === normalized);

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          total: runs.length,
          runs,
        }),
      });
    });

    await expect(page.getByRole("button", { name: /view test runs/i })).toBeVisible();
    await page.getByRole("button", { name: /view test runs/i }).click();
    await expect(page).toHaveURL(/\/test-runs$/);
    await expect(page.getByRole("heading", { name: /test runs/i })).toBeVisible();

    await expect(page.getByRole("cell", { name: "run-en" })).toBeVisible();
    await expect(page.getByRole("cell", { name: /completed/i })).toBeVisible();

    await page.getByLabel(/language/i).click();
    await page.getByRole("option", { name: /Japanese \(ja-JP\)/i }).click();

    await expect(page.getByRole("cell", { name: "run-ja" })).toBeVisible();
    await expect(page.getByRole("table")).not.toContainText("run-en");
    expect(requestedLanguages).toContain("ja-JP");
  });
});
