/**
 * Authentication Type Definitions
 *
 * TypeScript interfaces for authentication-related data structures
 * that match the backend API schemas for type safety.
 */

/**
 * User Interface
 * Represents an authenticated user (matches backend UserResponse schema)
 */
export interface User {
  id: string;              // UUID
  email: string;
  username: string;
  full_name: string;
  role: string | null;
  is_active: boolean;
  tenant_id: string | null;           // Organization ID (null for super_admin or org_owner)
  is_organization_owner: boolean;     // True if user owns an organization
  organization_name: string | null;   // Name of organization (if owner)
  created_at: string;      // ISO 8601 datetime string
  updated_at: string | null;
}

/**
 * Login Request Interface
 * Data sent to login endpoint
 */
export interface LoginRequest {
  email: string;
  password: string;
}

/**
 * Login Response Interface
 * Data received from successful login
 */
export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;      // "bearer"
  expires_in: number;      // seconds
  user: User;
}

/**
 * Register Request Interface
 * Data sent to registration endpoint
 */
export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  full_name: string;
  role?: string;
}

/**
 * Token Refresh Request Interface
 * Data sent to refresh token endpoint
 */
export interface TokenRefreshRequest {
  refresh_token: string;
}

/**
 * Token Refresh Response Interface
 * Data received from successful token refresh
 */
export interface TokenRefreshResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;      // "bearer"
  expires_in: number;      // seconds
}

/**
 * Auth Error Interface
 * Standard error format for auth operations
 */
export interface AuthError {
  message: string;
  statusCode?: number;
  detail?: string;
}

/**
 * Auth State Interface
 * Redux state for authentication
 */
export interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: AuthError | null;
}
