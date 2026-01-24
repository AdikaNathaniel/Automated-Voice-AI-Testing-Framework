import { expect, test } from "@playwright/test";

const TEST_EMAIL = process.env.E2E_TEST_EMAIL ?? "user@example.com";
const TEST_PASSWORD = process.env.E2E_TEST_PASSWORD ?? "password123";
const AUTH_BASE = process.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

const LOGIN_ENDPOINT = `${AUTH_BASE.replace(/\/$/, "")}/auth/login`;
const DEFAULT_UI_BASE =
  process.env.PLAYWRIGHT_BASE_URL ?? process.env.VITE_APP_URL ?? "http://localhost:5173";

type ValidationQueueResponse = {
  data: Array<{
    id: string;
    validationResultId: string;
    priority: number;
    confidenceScore: number;
    languageCode: string;
    status: string;
    claimedBy: string | null;
    claimedAt: string | null;
    testCaseName: string;
    inputText: string;
    expectedCommandKind: string;
    actualCommandKind: string;
    expectedResponse: string;
    actualResponse: string;
    context: string;
  }>;
};

function resolveUrl(baseURL: string | undefined, path: string): string {
  const base = baseURL ?? DEFAULT_UI_BASE;
  return new URL(path, base).toString();
}

function attachConsoleListeners(page: Parameters<typeof test>[0]["page"]) {
  page.on("console", (message) => {
    if (message.type() === "error" || message.type() === "warning") {
      console.log(`[browser:${message.type()}] ${message.text()}`);
    }
  });
  page.on("pageerror", (error) => {
    console.error(`[pageerror] ${error.message}`);
  });
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
          role: "validator",
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

async function setupValidationNetwork(
  page: Parameters<typeof test>[0]["page"],
  claimedItemOverrides?: Partial<ValidationQueueResponse["data"][number]>
) {
  const queueItem = {
    id: "queue-1",
    validationResultId: "validation-001",
    priority: 1,
    confidenceScore: 0.56,
    languageCode: "en-US",
    status: "pending",
    claimedBy: null,
    claimedAt: null,
    testCaseName: "Turn on the living room lights",
    inputText: "turn on the lights in the living room",
    expectedCommandKind: "control_lights.on",
    actualCommandKind: "control_lights.on",
    expectedResponse: "Turning on the living room lights.",
    actualResponse: "Turning on the living room lights.",
    context: "User is in the living room",
    ...claimedItemOverrides,
  };

  let isClaimed = false;

  await page.route("**/api/validation/stats**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        data: {
          pendingCount: 1,
          claimedCount: 0,
          completedCount: 24,
          averageConfidence: 0.61,
        },
      }),
    });
  });

  await page.route("**/api/validation/queue**", async (route) => {
    const request = route.request();
    const method = request.method();
    if (method !== "GET") {
      await route.fallback();
      return;
    }
    const pendingQueue = isClaimed ? [] : [queueItem];

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        data: pendingQueue,
      }),
    });
  });

  await page.route(`**/api/validation/queue/${queueItem.id}/claim`, async (route) => {
    isClaimed = true;
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        data: {
          ...queueItem,
          status: "claimed",
          claimedBy: "user-1",
          claimedAt: "2024-02-05T15:30:00Z",
        },
      }),
    });
  });
}

test.describe("Human validation flow", () => {
  test("allows a validator to claim and submit a decision", async ({ page, baseURL }) => {
    attachConsoleListeners(page);
    await authenticate(page, baseURL);
    await setupValidationNetwork(page);

    const submissions: Array<Record<string, unknown>> = [];

    await page.route("**/api/validation/submit", async (route) => {
      submissions.push(route.request().postDataJSON());
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ success: true }),
      });
    });

    await page.goto(resolveUrl(baseURL, "/validation"));
    await expect(page.getByRole("heading", { name: /validation dashboard/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /claim next validation/i })).toBeEnabled();

    await page.getByRole("button", { name: /claim next validation/i }).click();
    await expect(page).toHaveURL(/\/validation\/work$/);
    await expect(page.getByRole("heading", { name: /test case:/i })).toBeVisible();
    await expect(page.getByText(/turn on the living room lights/i)).toBeVisible();

    await page.getByRole("radio", { name: /pass/i }).check();
    await page
      .getByPlaceholder("Enter your feedback or notes here...")
      .fill("Looks good to me!");
    await page.getByRole("button", { name: /submit/i }).click();

    await expect(page.getByText(/no validation item/i)).toBeVisible();
    expect(submissions).toHaveLength(1);
    expect(submissions[0]).toMatchObject({
      validationResultId: "validation-001",
      decision: "approve",
      feedback: "Looks good to me!",
    });
    expect(typeof submissions[0].timeSpent).toBe("number");
  });

  test("allows a validator to release a claimed item", async ({ page, baseURL }) => {
    attachConsoleListeners(page);
    await authenticate(page, baseURL);
    await setupValidationNetwork(page, {
      id: "queue-2",
      validationResultId: "validation-002",
      testCaseName: "Set thermostat to 70 degrees",
      inputText: "set the thermostat to seventy",
    });

    let releaseCalled = false;
    await page.route("**/api/validation/queue/**/release", async (route) => {
      releaseCalled = true;
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ success: true }),
      });
    });

    await page.goto(resolveUrl(baseURL, "/validation"));
    await page.getByRole("button", { name: /claim next validation/i }).click();
    await expect(page).toHaveURL(/\/validation\/work$/);

    await page.getByRole("button", { name: /skip/i }).click();
    await expect(page.getByText(/no validation item/i)).toBeVisible();
    expect(releaseCalled).toBe(true);
  });
});
