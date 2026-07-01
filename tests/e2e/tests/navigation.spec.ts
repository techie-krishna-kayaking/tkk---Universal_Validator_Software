import { test, expect } from '@playwright/test';

test.describe('Navigation smoke tests', () => {
  test('home page loads with non-empty title', async ({ page }) => {
    await page.goto('/');
    const title = await page.title();
    expect(title.length).toBeGreaterThan(0);
  });

  test('dashboard route renders main content area', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    const body = await page.locator('body').textContent();
    expect(body).not.toBeNull();
    // The SPA should render something beyond an empty shell.
    expect(body!.length).toBeGreaterThan(10);
  });

  test('navigating to unknown route does not crash app', async ({ page }) => {
    const response = await page.goto('/this-route-does-not-exist-42');
    // SPA should serve index.html for all paths; no 5xx.
    expect(response?.status()).not.toBeGreaterThanOrEqual(500);
    await page.waitForLoadState('networkidle');
    const body = await page.locator('body').textContent();
    expect(body!.length).toBeGreaterThan(0);
  });
});
