/**
 * API Client Service
 *
 * Configures axios instance with:
 * - Base URL for API requests
 * - Request interceptor for JWT token injection
 * - Response interceptor for error handling and automatic token refresh
 * - 401 Unauthorized error handling with token refresh retry
 * - Logout on refresh failure
 *
 * Token Refresh Flow:
 * 1. API request fails with 401 Unauthorized
 * 2. Interceptor attempts to refresh access token using refresh token
 * 3. If refresh succeeds, original request is retried with new token
 * 4. If refresh fails, user is logged out and redirected to login
 * 5. Infinite retry loops are prevented with retry flag
 */

import axios from 'axios';
import type { AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import { getApiConfig } from '../config/api';

/**
 * Get API configuration from centralized config
 */
const apiConfig = getApiConfig();
const BASE_URL = apiConfig.fullBaseUrl;

/**
 * Create axios instance with base configuration
 */
const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Flag to track if token refresh is in progress
 * Prevents multiple simultaneous refresh requests
 */
let isRefreshing = false;

/**
 * Queue of failed requests waiting for token refresh
 * Requests are retried after successful token refresh
 */
let failedQueue: Array<{
  resolve: (value?: unknown) => void;
  reject: (reason?: unknown) => void;
}> = [];

/**
 * Process queued requests after token refresh
 * @param error - Error if refresh failed, null if successful
 * @param token - New access token if refresh succeeded
 */
const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });

  failedQueue = [];
};

/**
 * Request Interceptor
 * Adds JWT token to Authorization header if available
 */
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Get access token from localStorage
    const token = localStorage.getItem('accessToken');

    // Add Authorization header with Bearer token if token exists
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error: AxiosError) => {
    // Handle request error
    return Promise.reject(error);
  }
);

/**
 * Response Interceptor
 * Handles responses and errors globally, including automatic token refresh
 */
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Return successful response
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Handle response errors
    if (error.response) {
      const status = error.response.status;

      // Handle 401 Unauthorized - token expired or invalid
      if (status === 401 && originalRequest && !originalRequest._retry) {
        // If already refreshing, queue this request
        if (isRefreshing) {
          return new Promise((resolve, reject) => {
            failedQueue.push({ resolve, reject });
          })
            .then((token) => {
              originalRequest.headers.Authorization = `Bearer ${token}`;
              return apiClient(originalRequest);
            })
            .catch((err) => {
              return Promise.reject(err);
            });
        }

        // Mark request as retried to prevent infinite loops
        originalRequest._retry = true;
        isRefreshing = true;

        // Attempt to refresh the token
        const refreshToken = localStorage.getItem('refreshToken');

        if (!refreshToken) {
          // No refresh token available, logout user
          isRefreshing = false;
          processQueue(new Error('No refresh token available'), null);
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');

          // Redirect to login if not already there
          if (window.location.pathname !== '/login') {
            window.location.href = '/login';
          }

          return Promise.reject(error);
        }

        try {
          // Call refresh token endpoint
          const response = await axios.post<{ access_token: string; refresh_token: string }>(
            `${BASE_URL}/auth/refresh`,
            { refresh_token: refreshToken }
          );

          const newAccessToken = response.data.access_token;

          // Update access token in localStorage
          localStorage.setItem('accessToken', newAccessToken);

          // Update authorization header for original request
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;

          // Process queued requests with new token
          processQueue(null, newAccessToken);
          isRefreshing = false;

          // Retry original request with new token
          return apiClient(originalRequest);
        } catch (refreshError) {
          // Token refresh failed, logout user
          processQueue(refreshError as Error, null);
          isRefreshing = false;

          // Clear tokens
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
          localStorage.removeItem('authToken'); // Legacy token

          // Redirect to login if not already there
          if (window.location.pathname !== '/login') {
            window.location.href = '/login';
          }

          return Promise.reject(refreshError);
        }
      }

      // Handle other error status codes
      // 403 Forbidden - user doesn't have permission
      // 404 Not Found - resource doesn't exist
      // 500 Internal Server Error - server error
      // etc.
    }

    // Return rejected promise with error
    return Promise.reject(error);
  }
);

/**
 * Export configured axios instance
 */
export default apiClient;
