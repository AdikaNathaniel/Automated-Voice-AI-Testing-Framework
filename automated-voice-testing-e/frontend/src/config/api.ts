/**
 * Centralized API Configuration
 *
 * Provides consistent API configuration across the application:
 * - Single source of truth for base URL
 * - Environment-aware configuration
 * - Type-safe endpoint definitions
 * - Utility functions for URL building
 */

/**
 * API Configuration interface
 */
export interface ApiConfig {
  /** Base URL without path (e.g., http://localhost:8000) */
  baseUrl: string;
  /** API path prefix (e.g., /api/v1) */
  apiPath: string;
  /** Full base URL including path */
  fullBaseUrl: string;
  /** Request timeout in milliseconds */
  timeout: number;
  /** Upload request timeout in milliseconds */
  uploadTimeout: number;
}

/**
 * Get API configuration based on environment
 * Uses VITE_API_BASE_URL environment variable or defaults to localhost
 */
export const getApiConfig = (): ApiConfig => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
  const apiPath = '/api/v1';

  return {
    baseUrl,
    apiPath,
    fullBaseUrl: `${baseUrl}${apiPath}`,
    timeout: 30000,
    uploadTimeout: 120000,
  };
};

/**
 * API Endpoints
 * Centralized endpoint definitions for all API routes
 */
export const API_ENDPOINTS = {
  /** Authentication endpoints */
  AUTH: {
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
    PROFILE: '/auth/profile',
    REGISTER: '/auth/register',
  },

  /** Suite run endpoints */
  SUITE_RUNS: {
    LIST: '/suite-runs',
    CREATE: '/suite-runs',
    DETAIL: (id: string) => `/suite-runs/${id}`,
    UPDATE: (id: string) => `/suite-runs/${id}`,
    DELETE: (id: string) => `/suite-runs/${id}`,
    START: (id: string) => `/suite-runs/${id}/start`,
    STOP: (id: string) => `/suite-runs/${id}/stop`,
    RESULTS: (id: string) => `/suite-runs/${id}/results`,
    EXECUTIONS: (id: string) => `/suite-runs/${id}/executions`,
  },

  /** Test suite endpoints */
  TEST_SUITES: {
    LIST: '/test-suites',
    CREATE: '/test-suites',
    DETAIL: (id: string) => `/test-suites/${id}`,
    UPDATE: (id: string) => `/test-suites/${id}`,
    DELETE: (id: string) => `/test-suites/${id}`,
  },

  /** Validation endpoints */
  VALIDATION: {
    QUEUE: '/validation/queue',
    SUBMIT: '/validation/submit',
    STATS: '/validation/stats',
    ITEM: (id: string) => `/validation/queue/${id}`,
  },

  /** Defect endpoints */
  DEFECTS: {
    LIST: '/defects',
    CREATE: '/defects',
    DETAIL: (id: string) => `/defects/${id}`,
    UPDATE: (id: string) => `/defects/${id}`,
    DELETE: (id: string) => `/defects/${id}`,
  },

  /** Edge case endpoints */
  EDGE_CASES: {
    LIST: '/edge-cases',
    CREATE: '/edge-cases',
    DETAIL: (id: string) => `/edge-cases/${id}`,
    UPDATE: (id: string) => `/edge-cases/${id}`,
    DELETE: (id: string) => `/edge-cases/${id}`,
  },

  /** Configuration endpoints */
  CONFIGURATIONS: {
    LIST: '/configurations',
    CREATE: '/configurations',
    DETAIL: (id: string) => `/configurations/${id}`,
    UPDATE: (id: string) => `/configurations/${id}`,
    HISTORY: (id: string) => `/configurations/${id}/history`,
  },

  /** Integration endpoints */
  INTEGRATIONS: {
    GITHUB: {
      STATUS: '/integrations/github/status',
      CONNECT: '/integrations/github/connect',
      DISCONNECT: '/integrations/github/disconnect',
      SYNC: '/integrations/github/sync',
    },
    JIRA: {
      STATUS: '/integrations/jira/status',
      CONNECT: '/integrations/jira/connect',
      DISCONNECT: '/integrations/jira/disconnect',
      SYNC: '/integrations/jira/sync',
    },
    SLACK: {
      STATUS: '/integrations/slack/status',
      CONNECT: '/integrations/slack/connect',
      DISCONNECT: '/integrations/slack/disconnect',
      TEST: '/integrations/slack/test',
    },
  },

  /** Knowledge base endpoints */
  KNOWLEDGE_BASE: {
    LIST: '/knowledge-base',
    CREATE: '/knowledge-base',
    SEARCH: '/knowledge-base/search',
    ARTICLE: (id: string) => `/knowledge-base/${id}`,
    UPDATE: (id: string) => `/knowledge-base/${id}`,
    DELETE: (id: string) => `/knowledge-base/${id}`,
  },

  /** Regression endpoints */
  REGRESSIONS: {
    LIST: '/regressions',
    COMPARISON: (scriptId: string) => `/regressions/${scriptId}/comparison`,
    BASELINES: (scriptId: string) => `/regressions/${scriptId}/baselines`,
  },

  /** Analytics endpoints */
  ANALYTICS: {
    OVERVIEW: '/analytics/overview',
    TRENDS: '/analytics/trends',
    PERFORMANCE: '/analytics/performance',
  },

  /** Dashboard endpoints */
  DASHBOARD: {
    SUMMARY: '/dashboard/summary',
    METRICS: '/dashboard/metrics',
    ACTIVITY: '/dashboard/activity',
  },

  /** Reports endpoints */
  REPORTS: {
    LIST: '/reports',
    CREATE: '/reports',
    SECTIONS: '/reports/sections',
  },
} as const;

/**
 * Build full URL from endpoint
 * Combines base URL with endpoint path
 *
 * @param endpoint - API endpoint path
 * @returns Full URL string
 *
 * @example
 * buildUrl(API_ENDPOINTS.AUTH.LOGIN) // => 'http://localhost:8000/api/v1/auth/login'
 */
export const buildUrl = (endpoint: string): string => {
  const config = getApiConfig();
  return `${config.fullBaseUrl}${endpoint}`;
};

/**
 * Default export for convenience
 */
export default {
  getApiConfig,
  API_ENDPOINTS,
  buildUrl,
};
