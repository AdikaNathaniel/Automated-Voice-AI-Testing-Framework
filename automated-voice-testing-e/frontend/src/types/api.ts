/**
 * API Type Definitions
 *
 * TypeScript interfaces for API data structures used throughout
 * the frontend application for type safety and IDE autocomplete.
 */

/**
 * User Interface
 * Represents a user in the system (matches backend UserResponse schema)
 *
 * Note: For authentication-related User type, prefer importing from './auth'
 */
export interface User {
  id: string;              // UUID
  email: string;
  username: string;
  full_name: string;
  role: string | null;
  is_active: boolean;
  created_at: string;      // ISO 8601 datetime string
  updated_at: string | null;
}

/**
 * SuiteRun Interface
 * Represents a test suite run execution
 */
export interface SuiteRun {
  id: number;
  testSuiteId: number;
  status: 'pending' | 'running' | 'passed' | 'failed' | 'skipped';
  result?: string;
  errorMessage?: string;
  duration?: number;
  startedAt?: string;
  completedAt?: string;
  executedBy?: number;
  createdAt?: string;
  updatedAt?: string;
}

/**
 * ApiResponse Interface
 * Generic API response wrapper
 * @template T - The type of data being returned
 */
export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  statusCode?: number;
}

/**
 * Pagination Interface
 * For paginated API responses
 */
export interface PaginatedResponse<T = unknown> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

/**
 * Error Response Interface
 * Standard error response format
 */
export interface ErrorResponse {
  error: string;
  message: string;
  statusCode: number;
  timestamp?: string;
}
