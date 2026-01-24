/**
 * Authentication Redux Slice
 *
 * Manages authentication state including user data, tokens, and loading states.
 * Provides async thunks for login and token refresh operations.
 *
 * State:
 *  - user: Current authenticated user or null
 *  - accessToken: JWT access token for API requests
 *  - refreshToken: JWT refresh token for obtaining new access tokens
 *  - isAuthenticated: Boolean indicating if user is logged in
 *  - loading: Boolean indicating if auth operation is in progress
 *  - error: Error object if auth operation failed
 *
 * Actions:
 *  - login (async thunk): Authenticate user with email/password
 *  - refreshToken (async thunk): Refresh access token using refresh token
 *  - logout (reducer): Clear auth state and tokens
 *  - updateUser (reducer): Update current user data
 *  - clearError (reducer): Clear error state
 */

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import type {
  AuthState,
  User,
  LoginRequest,
  LoginResponse,
  TokenRefreshResponse,
  AuthError,
} from '../../types/auth';
import axios from 'axios';
import { getApiConfig } from '../../config/api';
import websocketService from '../../services/websocket.service';

// Use centralized API configuration
const apiConfig = getApiConfig();
const API_BASE_URL = apiConfig.fullBaseUrl;

/**
 * Initial authentication state
 * - Checks localStorage for existing tokens on app load
 * - Sets isAuthenticated to false by default
 * - User will be populated after token validation
 */
const initialState: AuthState = {
  user: null,
  accessToken: localStorage.getItem('accessToken'),
  refreshToken: localStorage.getItem('refreshToken'),
  isAuthenticated: false,
  loading: false,
  error: null,
};

/**
 * Async thunk: Login
 *
 * Authenticates user with email and password.
 * On success:
 *  - Stores tokens in localStorage
 *  - Updates Redux state with user and tokens
 *  - Sets isAuthenticated to true
 *
 * On failure:
 *  - Sets error state with message
 *  - Clears any existing auth data
 *
 * @param credentials - Email and password
 * @returns LoginResponse with user data and tokens
 */
export const login = createAsyncThunk<
  LoginResponse,
  LoginRequest,
  { rejectValue: AuthError }
>(
  'auth/login',
  async (credentials: LoginRequest, { rejectWithValue }) => {
    try {
      const response = await axios.post<LoginResponse>(
        `${API_BASE_URL}/auth/login`,
        credentials
      );

      // Store tokens in localStorage for persistence
      localStorage.setItem('accessToken', response.data.access_token);
      localStorage.setItem('refreshToken', response.data.refresh_token);

      return response.data;
    } catch (error: unknown) {
      // Extract error message from response
      let message = 'Login failed';
      let statusCode: number | undefined;
      let detail: string | undefined;

      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as { response?: { data?: { detail?: string }; status?: number } };
        message = axiosError.response?.data?.detail || message;
        statusCode = axiosError.response?.status;
        detail = axiosError.response?.data?.detail;
      }

      return rejectWithValue({
        message,
        statusCode,
        detail,
      });
    }
  }
);

/**
 * Async thunk: Initialize Auth
 *
 * Validates the stored access token and restores user state on app load.
 * This prevents logout on page refresh.
 *
 * On success:
 *  - Restores user data from token
 *  - Sets isAuthenticated to true
 *
 * On failure:
 *  - Clears tokens (they're invalid)
 *  - User must log in again
 *
 * @returns User data from /auth/me endpoint
 */
export const initializeAuth = createAsyncThunk<
  User,
  void,
  { rejectValue: AuthError }
>(
  'auth/initialize',
  async (_, { rejectWithValue }) => {
    try {
      const accessToken = localStorage.getItem('accessToken');

      if (!accessToken) {
        return rejectWithValue({
          message: 'No access token found',
        });
      }

      // Validate token by fetching current user
      const response = await axios.get<User>(
        `${API_BASE_URL}/auth/me`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );

      return response.data;
    } catch (error: unknown) {
      // Token is invalid - clear it
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');

      let message = 'Authentication initialization failed';
      let statusCode: number | undefined;

      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as { response?: { data?: { detail?: string }; status?: number } };
        message = axiosError.response?.data?.detail || message;
        statusCode = axiosError.response?.status;
      }

      return rejectWithValue({
        message,
        statusCode,
      });
    }
  }
);

/**
 * Async thunk: Refresh Token
 *
 * Obtains a new access token using the refresh token.
 * This should be called when the access token expires.
 *
 * On success:
 *  - Updates accessToken in state and localStorage
 *  - Maintains user authentication state
 *
 * On failure:
 *  - Logs out user (clears all auth state)
 *  - User must log in again
 *
 * @returns TokenRefreshResponse with new access token
 */
export const refreshAccessToken = createAsyncThunk<
  TokenRefreshResponse,
  void,
  { rejectValue: AuthError }
>(
  'auth/refreshToken',
  async (_, { getState, rejectWithValue }) => {
    try {
      // Get refresh token from state
      const state = getState() as { auth: AuthState };
      const refreshToken = state.auth.refreshToken;

      if (!refreshToken) {
        return rejectWithValue({
          message: 'No refresh token available',
        });
      }

      const response = await axios.post<TokenRefreshResponse>(
        `${API_BASE_URL}/auth/refresh`,
        { refresh_token: refreshToken }
      );

      // Update access token in localStorage
      localStorage.setItem('accessToken', response.data.access_token);

      return response.data;
    } catch (error: unknown) {
      // Clear tokens on refresh failure - user must log in again
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');

      let message = 'Token refresh failed';
      let statusCode: number | undefined;

      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as { response?: { data?: { detail?: string }; status?: number } };
        message = axiosError.response?.data?.detail || message;
        statusCode = axiosError.response?.status;
      }

      return rejectWithValue({
        message,
        statusCode,
      });
    }
  }
);

/**
 * Authentication slice
 *
 * Manages all authentication-related state and actions.
 */
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    /**
     * Logout
     * Clears all authentication state and removes tokens from localStorage
     */
    logout: (state) => {
      state.user = null;
      state.accessToken = null;
      state.refreshToken = null;
      state.isAuthenticated = false;
      state.error = null;

      // Clear tokens from localStorage
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');

      // Disconnect WebSocket
      websocketService.disconnect();
    },

    /**
     * Update User
     * Updates the current user data (e.g., after profile update)
     */
    updateUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
    },

    /**
     * Clear Error
     * Clears the error state (e.g., when user dismisses error message)
     */
    clearError: (state) => {
      state.error = null;
    },

    /**
     * Set Authenticated
     * Manually set authentication status (e.g., after token validation)
     */
    setAuthenticated: (state, action: PayloadAction<boolean>) => {
      state.isAuthenticated = action.payload;
    },
  },

  /**
   * Extra Reducers
   * Handle async thunk states (pending, fulfilled, rejected)
   */
  extraReducers: (builder) => {
    // Login thunk states
    builder
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload.user;
        state.accessToken = action.payload.access_token;
        state.refreshToken = action.payload.refresh_token;
        state.isAuthenticated = true;
        state.error = null;

        // Connect to WebSocket for real-time updates
        websocketService.connect({
          token: action.payload.access_token,
          autoReconnect: true,
        }).catch((error) => {
          console.error('Failed to connect WebSocket:', error);
        });
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.user = null;
        state.accessToken = null;
        state.refreshToken = null;
        state.isAuthenticated = false;
        state.error = action.payload || { message: 'Login failed' };
      })

      // Initialize auth thunk states
      .addCase(initializeAuth.pending, (state) => {
        state.loading = true;
      })
      .addCase(initializeAuth.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
        state.isAuthenticated = true;
        state.error = null;

        // Connect to WebSocket if not already connected
        if (state.accessToken) {
          websocketService.connect({
            token: state.accessToken,
            autoReconnect: true,
          }).catch((error) => {
            console.error('Failed to connect WebSocket:', error);
          });
        }
      })
      .addCase(initializeAuth.rejected, (state) => {
        state.loading = false;
        state.user = null;
        state.accessToken = null;
        state.refreshToken = null;
        state.isAuthenticated = false;
        // Don't set error - silent failure on init
      })

      // Refresh token thunk states
      .addCase(refreshAccessToken.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(refreshAccessToken.fulfilled, (state, action) => {
        state.loading = false;
        state.accessToken = action.payload.access_token;
        state.error = null;
        // Keep user and refreshToken as-is
      })
      .addCase(refreshAccessToken.rejected, (state, action) => {
        state.loading = false;
        state.user = null;
        state.accessToken = null;
        state.refreshToken = null;
        state.isAuthenticated = false;
        state.error = action.payload || { message: 'Token refresh failed' };
      });
  },
});

// Export actions
export const { logout, updateUser, clearError, setAuthenticated } = authSlice.actions;

// Export reducer as default
export default authSlice.reducer;
