/**
 * API Configuration Tests
 *
 * Tests for centralized API configuration including:
 * - Base URL configuration
 * - Environment-aware settings
 * - Endpoint definitions
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

describe('API Configuration', () => {
  // const originalEnv = import.meta.env;

  beforeEach(() => {
    vi.resetModules();
  });

  afterEach(() => {
    vi.unstubAllEnvs();
  });

  describe('getApiConfig', () => {
    it('returns default configuration when no environment variables set', async () => {
      vi.stubEnv('VITE_API_BASE_URL', '');

      const { getApiConfig } = await import('../api');
      const config = getApiConfig();

      expect(config.baseUrl).toBe('http://localhost:8000');
      expect(config.apiPath).toBe('/api/v1');
      expect(config.fullBaseUrl).toBe('http://localhost:8000/api/v1');
    });

    it('uses environment variable for base URL when set', async () => {
      vi.stubEnv('VITE_API_BASE_URL', 'https://api.production.com');

      const { getApiConfig } = await import('../api');
      const config = getApiConfig();

      expect(config.baseUrl).toBe('https://api.production.com');
      expect(config.fullBaseUrl).toBe('https://api.production.com/api/v1');
    });

    it('returns correct timeout values', async () => {
      const { getApiConfig } = await import('../api');
      const config = getApiConfig();

      expect(config.timeout).toBe(30000);
      expect(config.uploadTimeout).toBe(120000);
    });
  });

  describe('API_ENDPOINTS', () => {
    it('defines all authentication endpoints', async () => {
      const { API_ENDPOINTS } = await import('../api');

      expect(API_ENDPOINTS.AUTH.LOGIN).toBe('/auth/login');
      expect(API_ENDPOINTS.AUTH.LOGOUT).toBe('/auth/logout');
      expect(API_ENDPOINTS.AUTH.REFRESH).toBe('/auth/refresh');
      expect(API_ENDPOINTS.AUTH.PROFILE).toBe('/auth/profile');
    });

    it('defines all suite run endpoints', async () => {
      const { API_ENDPOINTS } = await import('../api');

      expect(API_ENDPOINTS.SUITE_RUNS.LIST).toBe('/suite-runs');
      expect(API_ENDPOINTS.SUITE_RUNS.CREATE).toBe('/suite-runs');
      expect(API_ENDPOINTS.SUITE_RUNS.DETAIL('456')).toBe('/suite-runs/456');
      expect(API_ENDPOINTS.SUITE_RUNS.START('456')).toBe('/suite-runs/456/start');
      expect(API_ENDPOINTS.SUITE_RUNS.STOP('456')).toBe('/suite-runs/456/stop');
      expect(API_ENDPOINTS.SUITE_RUNS.EXECUTIONS('456')).toBe('/suite-runs/456/executions');
    });

    it('defines validation endpoints', async () => {
      const { API_ENDPOINTS } = await import('../api');

      expect(API_ENDPOINTS.VALIDATION.QUEUE).toBe('/validation/queue');
      expect(API_ENDPOINTS.VALIDATION.SUBMIT).toBe('/validation/submit');
      expect(API_ENDPOINTS.VALIDATION.STATS).toBe('/validation/stats');
    });

    it('defines integration endpoints', async () => {
      const { API_ENDPOINTS } = await import('../api');

      expect(API_ENDPOINTS.INTEGRATIONS.GITHUB.STATUS).toBe('/integrations/github/status');
      expect(API_ENDPOINTS.INTEGRATIONS.JIRA.STATUS).toBe('/integrations/jira/status');
      expect(API_ENDPOINTS.INTEGRATIONS.SLACK.STATUS).toBe('/integrations/slack/status');
    });

    it('defines knowledge base endpoints', async () => {
      const { API_ENDPOINTS } = await import('../api');

      expect(API_ENDPOINTS.KNOWLEDGE_BASE.LIST).toBe('/knowledge-base');
      expect(API_ENDPOINTS.KNOWLEDGE_BASE.SEARCH).toBe('/knowledge-base/search');
      expect(API_ENDPOINTS.KNOWLEDGE_BASE.ARTICLE('789')).toBe('/knowledge-base/789');
    });
  });

  describe('buildUrl', () => {
    it('builds full URL from endpoint', async () => {
      vi.stubEnv('VITE_API_BASE_URL', '');

      const { buildUrl, API_ENDPOINTS } = await import('../api');

      const url = buildUrl(API_ENDPOINTS.AUTH.LOGIN);
      expect(url).toBe('http://localhost:8000/api/v1/auth/login');
    });

    it('builds full URL with custom base', async () => {
      vi.stubEnv('VITE_API_BASE_URL', 'https://api.example.com');

      const { buildUrl, API_ENDPOINTS } = await import('../api');

      const url = buildUrl(API_ENDPOINTS.SUITE_RUNS.LIST);
      expect(url).toBe('https://api.example.com/api/v1/suite-runs');
    });
  });
});
