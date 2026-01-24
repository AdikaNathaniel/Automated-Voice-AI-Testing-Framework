/**
 * Authentication Service
 *
 * Provides authentication-related API calls:
 * - login: Authenticate user with email/password
 * - register: Create new user account
 * - logout: Clear authentication state
 * - refreshToken: Refresh access token using refresh token
 * - getCurrentUser: Fetch current authenticated user
 *
 * All methods use the configured API client with automatic token injection.
 */

import apiClient from './api';
import type {
  LoginResponse,
  RegisterRequest,
  User,
  TokenRefreshResponse,
} from '../types/auth';

/**
 * Login
 *
 * Authenticates user with email and password.
 * Stores access token and refresh token in localStorage on success.
 *
 * @param email - User's email address
 * @param password - User's password
 * @returns Promise resolving to LoginResponse with tokens and user data
 * @throws Error if authentication fails
 *
 * @example
 * ```typescript
 * try {
 *   const response = await authService.login('user@example.com', 'password123');
 *   console.log('Logged in as:', response.user.email);
 * } catch {
 *   console.error('Login failed:', error);
 * }
 * ```
 */
export const login = async (
  email: string,
  password: string
): Promise<LoginResponse> => {
  try {
    const response = await apiClient.post<LoginResponse>('/auth/login', {
      email,
      password,
    });

    // Store tokens in localStorage
    if (response.data.access_token) {
      localStorage.setItem('accessToken', response.data.access_token);
    }
    if (response.data.refresh_token) {
      localStorage.setItem('refreshToken', response.data.refresh_token);
    }

    return response.data;
  } catch (error: unknown) {
    // Re-throw error with user-friendly message
    let message = 'Login failed';
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as { response?: { data?: { detail?: string } } };
      message = axiosError.response?.data?.detail || message;
    }
    throw new Error(message);
  }
};

/**
 * Register
 *
 * Creates a new user account.
 * Does not automatically log in the user.
 *
 * @param data - Registration data (email, username, password, full_name)
 * @returns Promise resolving to created User object
 * @throws Error if registration fails
 *
 * @example
 * ```typescript
 * try {
 *   const user = await authService.register({
 *     email: 'newuser@example.com',
 *     username: 'newuser',
 *     password: 'SecurePass123!',
 *     full_name: 'New User'
 *   });
 *   console.log('Registered user:', user.username);
 * } catch {
 *   console.error('Registration failed:', error);
 * }
 * ```
 */
export const register = async (data: RegisterRequest): Promise<User> => {
  try {
    const response = await apiClient.post<{ user: User }>('/auth/register', data);

    // Return the user object from response
    return response.data.user;
  } catch (error: unknown) {
    // Re-throw error with user-friendly message
    let message = 'Registration failed';
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as { response?: { data?: { detail?: string } } };
      message = axiosError.response?.data?.detail || message;
    }
    throw new Error(message);
  }
};

/**
 * Logout
 *
 * Clears authentication tokens from localStorage.
 * Does not make API call (stateless token-based auth).
 *
 * @example
 * ```typescript
 * authService.logout();
 * // Redirect to login page
 * window.location.href = '/login';
 * ```
 */
export const logout = (): void => {
  // Remove tokens from localStorage
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');
  localStorage.removeItem('authToken'); // Legacy token key if used

  // Note: For server-side session invalidation, you would make an API call here
  // await apiClient.post('/auth/logout');
};

/**
 * Refresh Token
 *
 * Obtains a new access token using the refresh token.
 * Updates the access token in localStorage.
 *
 * @returns Promise resolving to new access token
 * @throws Error if refresh fails or refresh token is missing
 *
 * @example
 * ```typescript
 * try {
 *   const newToken = await authService.refreshToken();
 *   console.log('Token refreshed successfully');
 * } catch {
 *   console.error('Token refresh failed, logging out');
 *   authService.logout();
 * }
 * ```
 */
export const refreshToken = async (): Promise<string> => {
  try {
    // Get refresh token from localStorage
    const refreshToken = localStorage.getItem('refreshToken');

    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await apiClient.post<TokenRefreshResponse>(
      '/auth/refresh',
      {
        refresh_token: refreshToken,
      }
    );

    // Update access token in localStorage
    if (response.data.access_token) {
      localStorage.setItem('accessToken', response.data.access_token);
    }

    return response.data.access_token;
  } catch (error: unknown) {
    // Clear tokens on refresh failure
    logout();

    let message = 'Token refresh failed';
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as { response?: { data?: { detail?: string } } };
      message = axiosError.response?.data?.detail || message;
    }
    throw new Error(message);
  }
};

/**
 * Get Current User
 *
 * Fetches the currently authenticated user's data.
 * Requires valid access token in localStorage.
 *
 * @returns Promise resolving to User object
 * @throws Error if request fails or user is not authenticated
 *
 * @example
 * ```typescript
 * try {
 *   const user = await authService.getCurrentUser();
 *   console.log('Current user:', user.email);
 * } catch {
 *   console.error('Failed to get user:', error);
 *   // Redirect to login
 * }
 * ```
 */
export const getCurrentUser = async (): Promise<User> => {
  try {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  } catch (error: unknown) {
    let message = 'Failed to fetch user';
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as { response?: { data?: { detail?: string } } };
      message = axiosError.response?.data?.detail || message;
    }
    throw new Error(message);
  }
};

/**
 * Auth Service Object
 *
 * Aggregates all auth service methods for convenience.
 * Can be imported as a single object or individual functions.
 */
const authService = {
  login,
  register,
  logout,
  refreshToken,
  getCurrentUser,
};

export default authService;
