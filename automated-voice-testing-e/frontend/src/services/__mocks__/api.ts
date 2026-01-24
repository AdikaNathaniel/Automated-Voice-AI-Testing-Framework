/**
 * Mock API Service
 *
 * Provides mock implementations of the API client for testing.
 * This mock is automatically used by Vitest when tests import from '../api'
 */

import { vi } from 'vitest'

// Create mock axios instance
const mockApiClient = {
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  patch: vi.fn(),
  delete: vi.fn(),
  request: vi.fn(),
  interceptors: {
    request: {
      use: vi.fn(),
      eject: vi.fn(),
    },
    response: {
      use: vi.fn(),
      eject: vi.fn(),
    },
  },
}

// Mock API client responses with success by default
mockApiClient.get.mockResolvedValue({
  data: { success: true, data: [] },
  status: 200,
  statusText: 'OK',
  headers: {},
  config: {},
})

mockApiClient.post.mockResolvedValue({
  data: { success: true },
  status: 200,
  statusText: 'OK',
  headers: {},
  config: {},
})

mockApiClient.put.mockResolvedValue({
  data: { success: true },
  status: 200,
  statusText: 'OK',
  headers: {},
  config: {},
})

mockApiClient.patch.mockResolvedValue({
  data: { success: true },
  status: 200,
  statusText: 'OK',
  headers: {},
  config: {},
})

mockApiClient.delete.mockResolvedValue({
  data: { success: true },
  status: 204,
  statusText: 'No Content',
  headers: {},
  config: {},
})

export default mockApiClient
