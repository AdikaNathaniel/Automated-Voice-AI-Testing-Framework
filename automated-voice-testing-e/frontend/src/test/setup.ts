/**
 * Vitest Global Test Setup
 *
 * This file runs before each test file and sets up:
 * - Custom matchers from @testing-library/jest-dom
 * - Global test utilities and mocks
 * - Environment configuration
 * - MSW (Mock Service Worker) for HTTP request mocking
 */

import { expect, afterEach, beforeAll, afterAll, vi } from 'vitest'
import { cleanup } from '@testing-library/react'
import * as matchers from '@testing-library/jest-dom/matchers'
import { server } from './mocks/server'

// Extend Vitest's expect with jest-dom matchers
expect.extend(matchers)

// Mock axios globally to prevent real HTTP requests
vi.mock('axios', async () => {
  const actual = await vi.importActual<typeof import('axios')>('axios')

  const mockAxiosInstance = {
    get: vi.fn().mockResolvedValue({ data: { success: true, data: [] }, status: 200 }),
    post: vi.fn().mockResolvedValue({ data: { success: true }, status: 200 }),
    put: vi.fn().mockResolvedValue({ data: { success: true }, status: 200 }),
    patch: vi.fn().mockResolvedValue({ data: { success: true }, status: 200 }),
    delete: vi.fn().mockResolvedValue({ data: { success: true }, status: 204 }),
    request: vi.fn().mockResolvedValue({ data: { success: true }, status: 200 }),
    interceptors: {
      request: { use: vi.fn(), eject: vi.fn() },
      response: { use: vi.fn(), eject: vi.fn() },
    },
  }

  return {
    default: {
      ...actual.default,
      create: vi.fn(() => mockAxiosInstance),
      get: mockAxiosInstance.get,
      post: mockAxiosInstance.post,
      put: mockAxiosInstance.put,
      patch: mockAxiosInstance.patch,
      delete: mockAxiosInstance.delete,
      request: mockAxiosInstance.request,
    },
  }
})

// Start MSW server before all tests
beforeAll(() => {
  server.listen({ onUnhandledRequest: 'warn' })
})

// Reset handlers and cleanup after each test
afterEach(() => {
  // Reset MSW handlers to initial state
  server.resetHandlers()
  // Cleanup React trees
  cleanup()
})

// Close MSW server after all tests
afterAll(() => {
  server.close()
})

// Mock window.matchMedia (used by many UI libraries)
// Only mock if window is defined (browser/jsdom environment, not Node)
if (typeof window !== 'undefined') {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation((query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(), // deprecated
      removeListener: vi.fn(), // deprecated
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  })
}

// Mock IntersectionObserver (used by lazy loading, infinite scroll, etc.)
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() {
    return []
  }
  unobserve() {}
} as any

// Mock ResizeObserver (used by responsive components)
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
} as any

// Suppress console errors in tests (optional - uncomment if needed)
// const originalError = console.error
// beforeAll(() => {
//   console.error = (...args: unknown[]) => {
//     if (
//       typeof args[0] === 'string' &&
//       args[0].includes('Warning: ReactDOM.render')
//     ) {
//       return
//     }
//     originalError.call(console, ...args)
//   }
// })

// afterAll(() => {
//   console.error = originalError
// })
