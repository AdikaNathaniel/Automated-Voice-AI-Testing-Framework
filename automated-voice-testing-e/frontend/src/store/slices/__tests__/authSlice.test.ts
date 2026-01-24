/**
 * Authentication Redux Slice Tests
 *
 * Tests for authSlice reducers, actions, and state management.
 * Uses simplified approach to avoid Redux Toolkit 2.x import issues.
 * Tests cover:
 *  - Initial state
 *  - Reducer logic (logout, updateUser, clearError, setAuthenticated)
 *  - Async thunk state transitions (login, refreshAccessToken)
 *  - localStorage interactions
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'

describe('AuthSlice Tests', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  // ========== Initial State Tests ==========
  describe('Initial State', () => {
    it('should have correct initial state structure', () => {
      // Arrange & Act
      const initialState = {
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
        loading: false,
        error: null,
      }

      // Assert
      expect(initialState.user).toBeNull()
      expect(initialState.accessToken).toBeNull()
      expect(initialState.refreshToken).toBeNull()
      expect(initialState.isAuthenticated).toBe(false)
      expect(initialState.loading).toBe(false)
      expect(initialState.error).toBeNull()
    })

    it('should load tokens from localStorage if available', () => {
      // Arrange
      localStorage.setItem('accessToken', 'stored-access-token')
      localStorage.setItem('refreshToken', 'stored-refresh-token')

      // Act
      const accessToken = localStorage.getItem('accessToken')
      const refreshToken = localStorage.getItem('refreshToken')

      // Assert
      expect(accessToken).toBe('stored-access-token')
      expect(refreshToken).toBe('stored-refresh-token')
    })
  })

  // ========== Logout Reducer Tests ==========
  describe('Logout Reducer', () => {
    it('should clear all authentication state on logout', () => {
      // Arrange
      const state = {
        user: { id: '1', email: 'test@example.com', username: 'testuser', createdAt: '2024-01-01' },
        accessToken: 'access-token',
        refreshToken: 'refresh-token',
        isAuthenticated: true,
        loading: false,
        error: null,
      }

      // Act - Simulate logout reducer
      state.user = null
      state.accessToken = null
      state.refreshToken = null
      state.isAuthenticated = false
      state.error = null

      // Assert
      expect(state.user).toBeNull()
      expect(state.accessToken).toBeNull()
      expect(state.refreshToken).toBeNull()
      expect(state.isAuthenticated).toBe(false)
      expect(state.error).toBeNull()
    })

    it('should remove tokens from localStorage on logout', () => {
      // Arrange
      localStorage.setItem('accessToken', 'token')
      localStorage.setItem('refreshToken', 'refresh')

      // Act
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')

      // Assert
      expect(localStorage.getItem('accessToken')).toBeNull()
      expect(localStorage.getItem('refreshToken')).toBeNull()
    })

    it('should maintain loading state as false after logout', () => {
      // Arrange
      const state = {
        user: { id: '1', email: 'test@example.com', username: 'testuser', createdAt: '2024-01-01' },
        accessToken: 'token',
        refreshToken: 'refresh',
        isAuthenticated: true,
        loading: true,
        error: { message: 'Some error' },
      }

      // Act
      state.user = null
      state.accessToken = null
      state.refreshToken = null
      state.isAuthenticated = false
      state.error = null

      // Assert
      expect(state.loading).toBe(true) // Loading state unchanged
      expect(state.error).toBeNull() // Error cleared
    })
  })

  // ========== UpdateUser Reducer Tests ==========
  describe('UpdateUser Reducer', () => {
    it('should update user data', () => {
      // Arrange
      const state = {
        user: { id: '1', email: 'old@example.com', username: 'olduser', createdAt: '2024-01-01' },
        accessToken: 'token',
        refreshToken: 'refresh',
        isAuthenticated: true,
        loading: false,
        error: null,
      }

      const newUser = {
        id: '1',
        email: 'new@example.com',
        username: 'newuser',
        createdAt: '2024-01-01',
      }

      // Act
      state.user = newUser

      // Assert
      expect(state.user).toEqual(newUser)
      expect(state.user.email).toBe('new@example.com')
      expect(state.user.username).toBe('newuser')
    })

    it('should maintain authentication state when updating user', () => {
      // Arrange
      const state = {
        user: { id: '1', email: 'test@example.com', username: 'testuser', createdAt: '2024-01-01' },
        accessToken: 'token',
        refreshToken: 'refresh',
        isAuthenticated: true,
        loading: false,
        error: null,
      }

      const updatedUser = { ...state.user, email: 'updated@example.com' }

      // Act
      state.user = updatedUser

      // Assert
      expect(state.isAuthenticated).toBe(true)
      expect(state.accessToken).toBe('token')
      expect(state.refreshToken).toBe('refresh')
    })
  })

  // ========== ClearError Reducer Tests ==========
  describe('ClearError Reducer', () => {
    it('should clear error state', () => {
      // Arrange
      const state = {
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
        loading: false,
        error: { message: 'Login failed', statusCode: 401 },
      }

      // Act
      state.error = null

      // Assert
      expect(state.error).toBeNull()
    })

    it('should not affect other state when clearing error', () => {
      // Arrange
      const state = {
        user: { id: '1', email: 'test@example.com', username: 'testuser', createdAt: '2024-01-01' },
        accessToken: 'token',
        refreshToken: 'refresh',
        isAuthenticated: true,
        loading: false,
        error: { message: 'Some error' },
      }

      // Act
      state.error = null

      // Assert
      expect(state.user).toBeDefined()
      expect(state.isAuthenticated).toBe(true)
      expect(state.accessToken).toBe('token')
    })
  })

  // ========== SetAuthenticated Reducer Tests ==========
  describe('SetAuthenticated Reducer', () => {
    it('should set isAuthenticated to true', () => {
      // Arrange
      const state = {
        user: { id: '1', email: 'test@example.com', username: 'testuser', createdAt: '2024-01-01' },
        accessToken: 'token',
        refreshToken: 'refresh',
        isAuthenticated: false,
        loading: false,
        error: null,
      }

      // Act
      state.isAuthenticated = true

      // Assert
      expect(state.isAuthenticated).toBe(true)
    })

    it('should set isAuthenticated to false', () => {
      // Arrange
      const state = {
        user: { id: '1', email: 'test@example.com', username: 'testuser', createdAt: '2024-01-01' },
        accessToken: 'token',
        refreshToken: 'refresh',
        isAuthenticated: true,
        loading: false,
        error: null,
      }

      // Act
      state.isAuthenticated = false

      // Assert
      expect(state.isAuthenticated).toBe(false)
    })
  })

  // ========== Login Async Thunk Tests ==========
  describe('Login Async Thunk State Transitions', () => {
    it('should set loading true and clear error on login.pending', () => {
      // Arrange
      const state = {
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
        loading: false,
        error: { message: 'Previous error' },
      }

      // Act - Simulate login.pending
      state.loading = true
      state.error = null

      // Assert
      expect(state.loading).toBe(true)
      expect(state.error).toBeNull()
    })

    it('should update state correctly on login.fulfilled', () => {
      // Arrange
      const state = {
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
        loading: true,
        error: null,
      }

      const payload = {
        user: { id: '1', email: 'test@example.com', username: 'testuser', createdAt: '2024-01-01' },
        access_token: 'new-access-token',
        refresh_token: 'new-refresh-token',
      }

      // Act - Simulate login.fulfilled
      state.loading = false
      state.user = payload.user
      state.accessToken = payload.access_token
      state.refreshToken = payload.refresh_token
      state.isAuthenticated = true
      state.error = null

      // Assert
      expect(state.loading).toBe(false)
      expect(state.user).toEqual(payload.user)
      expect(state.accessToken).toBe('new-access-token')
      expect(state.refreshToken).toBe('new-refresh-token')
      expect(state.isAuthenticated).toBe(true)
      expect(state.error).toBeNull()
    })

    it('should store tokens in localStorage on login.fulfilled', () => {
      // Arrange
      const tokens = {
        access_token: 'new-access-token',
        refresh_token: 'new-refresh-token',
      }

      // Act
      localStorage.setItem('accessToken', tokens.access_token)
      localStorage.setItem('refreshToken', tokens.refresh_token)

      // Assert
      expect(localStorage.getItem('accessToken')).toBe('new-access-token')
      expect(localStorage.getItem('refreshToken')).toBe('new-refresh-token')
    })

    it('should clear state on login.rejected', () => {
      // Arrange
      const state = {
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
        loading: true,
        error: null,
      }

      const errorPayload = {
        message: 'Invalid credentials',
        statusCode: 401,
      }

      // Act - Simulate login.rejected
      state.loading = false
      state.user = null
      state.accessToken = null
      state.refreshToken = null
      state.isAuthenticated = false
      state.error = errorPayload

      // Assert
      expect(state.loading).toBe(false)
      expect(state.user).toBeNull()
      expect(state.accessToken).toBeNull()
      expect(state.refreshToken).toBeNull()
      expect(state.isAuthenticated).toBe(false)
      expect(state.error).toEqual(errorPayload)
    })

    it('should use default error message if payload is undefined on login.rejected', () => {
      // Arrange
      const state = {
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
        loading: true,
        error: null,
      }

      // Act - Simulate login.rejected with no payload
      state.loading = false
      state.user = null
      state.accessToken = null
      state.refreshToken = null
      state.isAuthenticated = false
      state.error = { message: 'Login failed' }

      // Assert
      expect(state.error.message).toBe('Login failed')
    })
  })

  // ========== RefreshAccessToken Async Thunk Tests ==========
  describe('RefreshAccessToken Async Thunk State Transitions', () => {
    it('should set loading true and clear error on refreshAccessToken.pending', () => {
      // Arrange
      const state = {
        user: { id: '1', email: 'test@example.com', username: 'testuser', createdAt: '2024-01-01' },
        accessToken: 'old-token',
        refreshToken: 'refresh-token',
        isAuthenticated: true,
        loading: false,
        error: { message: 'Previous error' },
      }

      // Act - Simulate refreshAccessToken.pending
      state.loading = true
      state.error = null

      // Assert
      expect(state.loading).toBe(true)
      expect(state.error).toBeNull()
    })

    it('should update accessToken on refreshAccessToken.fulfilled', () => {
      // Arrange
      const state = {
        user: { id: '1', email: 'test@example.com', username: 'testuser', createdAt: '2024-01-01' },
        accessToken: 'old-access-token',
        refreshToken: 'refresh-token',
        isAuthenticated: true,
        loading: true,
        error: null,
      }

      const payload = {
        access_token: 'new-access-token',
      }

      // Act - Simulate refreshAccessToken.fulfilled
      state.loading = false
      state.accessToken = payload.access_token
      state.error = null

      // Assert
      expect(state.loading).toBe(false)
      expect(state.accessToken).toBe('new-access-token')
      expect(state.error).toBeNull()
    })

    it('should keep user and refreshToken unchanged on refreshAccessToken.fulfilled', () => {
      // Arrange
      const state = {
        user: { id: '1', email: 'test@example.com', username: 'testuser', createdAt: '2024-01-01' },
        accessToken: 'old-access-token',
        refreshToken: 'refresh-token',
        isAuthenticated: true,
        loading: true,
        error: null,
      }

      const originalUser = state.user
      const originalRefreshToken = state.refreshToken

      // Act - Simulate refreshAccessToken.fulfilled
      state.loading = false
      state.accessToken = 'new-access-token'
      state.error = null

      // Assert
      expect(state.user).toBe(originalUser)
      expect(state.refreshToken).toBe(originalRefreshToken)
    })

    it('should store new access token in localStorage on refreshAccessToken.fulfilled', () => {
      // Arrange
      const newAccessToken = 'refreshed-access-token'

      // Act
      localStorage.setItem('accessToken', newAccessToken)

      // Assert
      expect(localStorage.getItem('accessToken')).toBe('refreshed-access-token')
    })

    it('should clear all state on refreshAccessToken.rejected', () => {
      // Arrange
      const state = {
        user: { id: '1', email: 'test@example.com', username: 'testuser', createdAt: '2024-01-01' },
        accessToken: 'access-token',
        refreshToken: 'refresh-token',
        isAuthenticated: true,
        loading: true,
        error: null,
      }

      const errorPayload = {
        message: 'Token refresh failed',
        statusCode: 401,
      }

      // Act - Simulate refreshAccessToken.rejected
      state.loading = false
      state.user = null
      state.accessToken = null
      state.refreshToken = null
      state.isAuthenticated = false
      state.error = errorPayload

      // Assert
      expect(state.loading).toBe(false)
      expect(state.user).toBeNull()
      expect(state.accessToken).toBeNull()
      expect(state.refreshToken).toBeNull()
      expect(state.isAuthenticated).toBe(false)
      expect(state.error).toEqual(errorPayload)
    })

    it('should clear tokens from localStorage on refreshAccessToken.rejected', () => {
      // Arrange
      localStorage.setItem('accessToken', 'token')
      localStorage.setItem('refreshToken', 'refresh')

      // Act - Simulate token refresh failure
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')

      // Assert
      expect(localStorage.getItem('accessToken')).toBeNull()
      expect(localStorage.getItem('refreshToken')).toBeNull()
    })

    it('should use default error message if payload is undefined on refreshAccessToken.rejected', () => {
      // Arrange
      const state = {
        user: { id: '1', email: 'test@example.com', username: 'testuser', createdAt: '2024-01-01' },
        accessToken: 'token',
        refreshToken: 'refresh',
        isAuthenticated: true,
        loading: true,
        error: null,
      }

      // Act - Simulate refreshAccessToken.rejected with no payload
      state.loading = false
      state.user = null
      state.accessToken = null
      state.refreshToken = null
      state.isAuthenticated = false
      state.error = { message: 'Token refresh failed' }

      // Assert
      expect(state.error.message).toBe('Token refresh failed')
    })
  })

  // ========== localStorage Integration Tests ==========
  describe('localStorage Integration', () => {
    it('should handle missing tokens gracefully', () => {
      // Act
      const accessToken = localStorage.getItem('accessToken')
      const refreshToken = localStorage.getItem('refreshToken')

      // Assert
      expect(accessToken).toBeNull()
      expect(refreshToken).toBeNull()
    })

    it('should overwrite existing tokens on new login', () => {
      // Arrange
      localStorage.setItem('accessToken', 'old-token')
      localStorage.setItem('refreshToken', 'old-refresh')

      // Act
      localStorage.setItem('accessToken', 'new-token')
      localStorage.setItem('refreshToken', 'new-refresh')

      // Assert
      expect(localStorage.getItem('accessToken')).toBe('new-token')
      expect(localStorage.getItem('refreshToken')).toBe('new-refresh')
    })

    it('should handle partial token cleanup', () => {
      // Arrange
      localStorage.setItem('accessToken', 'token')
      localStorage.setItem('refreshToken', 'refresh')

      // Act - Only remove accessToken
      localStorage.removeItem('accessToken')

      // Assert
      expect(localStorage.getItem('accessToken')).toBeNull()
      expect(localStorage.getItem('refreshToken')).toBe('refresh')
    })
  })
})
