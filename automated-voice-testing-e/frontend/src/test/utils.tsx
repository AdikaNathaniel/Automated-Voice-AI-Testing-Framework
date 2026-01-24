/**
 * Test Utilities
 *
 * Common test helpers and utilities for React component testing.
 * Provides custom render function with providers, mock factories, and helpers.
 */

import React from 'react'
import { render } from '@testing-library/react'
import { Provider } from 'react-redux'
import { BrowserRouter } from 'react-router-dom'
import { configureStore } from '@reduxjs/toolkit'
import authReducer from '../store/slices/authSlice'
import githubIntegrationReducer from '../store/slices/githubIntegrationSlice'
import jiraIntegrationReducer from '../store/slices/jiraIntegrationSlice'
import slackIntegrationReducer from '../store/slices/slackIntegrationSlice'
import { ThemeProvider } from '../contexts/ThemeContext'

// Define RenderOptions type locally
type RenderOptions = Parameters<typeof render>[1]
type RenderResult = ReturnType<typeof render>

// Create mock store with actual reducers
const createMockStore = (preloadedState?: any) => {
  return configureStore({
    reducer: {
      auth: authReducer,
      githubIntegration: githubIntegrationReducer,
      jiraIntegration: jiraIntegrationReducer,
      slackIntegration: slackIntegrationReducer,
    },
    preloadedState,
  })
}

// Type for the store
type AppStore = ReturnType<typeof createMockStore>
type RootState = ReturnType<AppStore['getState']>

interface ExtendedRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  preloadedState?: Partial<RootState>
  store?: AppStore
  route?: string
}

/**
 * Custom render function that wraps components with necessary providers
 *
 * @param ui - React component to render
 * @param options - Render options including preloadedState and route
 * @returns Render result with store
 *
 * @example
 * ```tsx
 * const { getByText, store } = renderWithProviders(
 *   <MyComponent />,
 *   { preloadedState: { auth: { user: mockUser } } }
 * )
 * ```
 */
export function renderWithProviders(
  ui: React.ReactElement,
  {
    preloadedState = {},
    store = createMockStore(preloadedState),
    route = '/',
    ...renderOptions
  }: ExtendedRenderOptions = {}
): RenderResult & { store: AppStore } {
  // Set initial route
  window.history.pushState({}, 'Test page', route)

  function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <Provider store={store}>
        <ThemeProvider>
          <BrowserRouter>{children}</BrowserRouter>
        </ThemeProvider>
      </Provider>
    )
  }

  return { store, ...render(ui, { wrapper: Wrapper, ...renderOptions }) }
}

/**
 * Mock user data for tests
 */
export const mockUser = {
  id: '1',
  email: 'test@example.com',
  username: 'testuser',
  createdAt: new Date('2024-01-01').toISOString(),
}

/**
 * Mock scenario data for tests
 */
export const mockScenario = {
  id: '1',
  name: 'Test Weather Query',
  description: 'Test voice query for weather information',
  queryText: "What's the weather in New York?",
  expectedIntent: 'weather_query',
  expectedEntities: {
    location: 'New York',
  },
  tags: ['weather', 'voice'],
  status: 'active' as const,
  createdAt: new Date('2024-01-01').toISOString(),
  updatedAt: new Date('2024-01-01').toISOString(),
}

/**
 * Mock test suite data for tests
 */
export const mockTestSuite = {
  id: '1',
  name: 'Weather Test Suite',
  description: 'Tests for weather-related queries',
  scenarios: [mockScenario],
  status: 'active' as const,
  createdAt: new Date('2024-01-01').toISOString(),
  updatedAt: new Date('2024-01-01').toISOString(),
}

/**
 * Mock test run data for tests
 */
export const mockTestRun = {
  id: '1',
  testSuiteId: '1',
  status: 'completed' as const,
  startedAt: new Date('2024-01-01T10:00:00').toISOString(),
  completedAt: new Date('2024-01-01T10:05:00').toISOString(),
  totalTests: 10,
  passedTests: 8,
  failedTests: 2,
  skippedTests: 0,
}

/**
 * Wait for async state updates
 *
 * @param ms - Milliseconds to wait
 * @returns Promise that resolves after delay
 */
export const wait = (ms: number = 0): Promise<void> => {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

/**
 * Create a mock API response
 *
 * @param data - Response data
 * @param status - HTTP status code
 * @returns Mock response object
 */
export const createMockResponse = <T,>(data: T, status: number = 200) => {
  return {
    data,
    status,
    statusText: status === 200 ? 'OK' : 'Error',
    headers: {},
    config: {} as unknown,
  }
}

// Re-export testing-library utilities
export * from '@testing-library/react'
export { default as userEvent } from '@testing-library/user-event'
