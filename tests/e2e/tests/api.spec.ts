import { test, expect } from '@playwright/test';

const BACKEND_URL = process.env.BACKEND_URL ?? 'http://localhost:8000';

test.describe('Backend API contract tests', () => {
  test('POST /api/v1/auth/login returns 422 for empty payload', async ({ request }) => {
    const response = await request.post(`${BACKEND_URL}/api/v1/auth/login`, {
      data: {},
    });
    expect(response.status()).toBe(422);
  });

  test('GET /api/v1/health returns 401 without token', async ({ request }) => {
    const response = await request.get(`${BACKEND_URL}/api/v1/health`, {
      headers: { 'X-Tenant-ID': 'test-tenant' },
    });
    expect(response.status()).toBe(401);
  });

  test('GET /api/v1/metrics returns prometheus text format', async ({ request }) => {
    const response = await request.get(`${BACKEND_URL}/api/v1/metrics`);
    expect(response.status()).toBe(200);
    const body = await response.text();
    expect(body).toContain('http_requests_total');
  });

  test('GET /openapi.json returns valid JSON schema', async ({ request }) => {
    const response = await request.get(`${BACKEND_URL}/openapi.json`);
    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body).toHaveProperty('openapi');
    expect(body).toHaveProperty('paths');
  });
});
