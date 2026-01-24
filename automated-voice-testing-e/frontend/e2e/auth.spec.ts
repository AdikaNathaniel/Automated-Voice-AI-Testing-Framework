import { expect, test } from "@playwright/test";

const TEST_EMAIL = process.env.E2E_TEST_EMAIL ?? "user@example.com";
const TEST_PASSWORD = process.env.E2E_TEST_PASSWORD ?? "password123";
const API_BASE = process.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

const LOGIN_ENDPOINT = `${API_BASE}/auth/login`;
const DEFAULT_UI_BASE =
  process.env.PLAYWRIGHT_BASE_URL ?? process.env.VITE_APP_URL ?? "http://localhost:5173";

function resolveUrl(baseURL: string | undefined, path: string): string {
  const base = baseURL ?? DEFAULT_UI_BASE;
  return new URL(path, base).toString();
}

test.describe("Authentication flow", () => {
  test("allows user to log in and see home page CTA", async ({ page, baseURL }) => {
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
            name: "E2E Tester",
            roles: ["tester"],
          },
        }),
      });
    });

    await page.goto(resolveUrl(baseURL, "/login"));
    await expect(page).toHaveURL(/\/login$/);
    await expect(page.getByRole("heading", { name: /sign in/i })).toBeVisible();
    await page.getByLabel(/email address/i).fill(TEST_EMAIL);
    await page.getByLabel(/password/i).fill(TEST_PASSWORD);
    await page.getByRole("button", { name: /sign in/i }).click();

    await expect(page).toHaveURL(/\/$/);
    await expect(page.getByRole("heading", { name: /automated testing platform/i })).toBeVisible();
  });

  test("shows error on invalid credentials", async ({ page, baseURL }) => {
    await page.route(LOGIN_ENDPOINT, async (route) => {
      await route.fulfill({
        status: 401,
        contentType: "application/json",
        body: JSON.stringify({ detail: "Invalid credentials" }),
      });
    });

    await page.goto(resolveUrl(baseURL, "/login"));
    await expect(page).toHaveURL(/\/login$/);
    await expect(page.getByRole("heading", { name: /sign in/i })).toBeVisible();
    await page.getByLabel(/email address/i).fill("invalid@example.com");
    await page.getByLabel(/password/i).fill("wrong-password");
    await page.getByRole("button", { name: /sign in/i }).click();

    await expect(page.getByText(/invalid credentials/i)).toBeVisible();
  });
});
