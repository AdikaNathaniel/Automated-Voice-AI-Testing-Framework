/**
 * MSW Request Handlers
 *
 * Define mock HTTP request handlers for testing.
 * These handlers intercept API requests made during tests
 * and return mock responses.
 */

import { http, HttpResponse } from 'msw'

// Base API URL - adjust if your API uses a different base
const API_BASE = 'http://localhost:3000'

export const handlers = [
  // Mock authentication endpoints
  http.post(`${API_BASE}/api/auth/login`, () => {
    return HttpResponse.json({
      success: true,
      data: {
        token: 'mock-jwt-token',
        user: {
          id: '1',
          email: 'test@example.com',
          name: 'Test User',
        },
      },
    })
  }),

  http.post(`${API_BASE}/api/auth/logout`, () => {
    return HttpResponse.json({
      success: true,
      message: 'Logged out successfully',
    })
  }),

  http.get(`${API_BASE}/api/auth/me`, () => {
    return HttpResponse.json({
      success: true,
      data: {
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
      },
    })
  }),

  // Mock scenarios endpoints
  http.get(`${API_BASE}/api/scenarios`, () => {
    return HttpResponse.json({
      success: true,
      data: [],
      pagination: {
        page: 1,
        pageSize: 10,
        totalItems: 0,
        totalPages: 0,
      },
    })
  }),

  http.get(`${API_BASE}/api/scenarios/:id`, ({ params }) => {
    return HttpResponse.json({
      success: true,
      data: {
        id: params.id,
        name: 'Test Scenario',
        description: 'Test description',
        status: 'active',
      },
    })
  }),

  // Mock suite runs endpoints
  http.get(`${API_BASE}/api/suite-runs`, () => {
    return HttpResponse.json({
      success: true,
      data: [],
      pagination: {
        page: 1,
        pageSize: 10,
        totalItems: 0,
        totalPages: 0,
      },
    })
  }),

  http.get(`${API_BASE}/api/suite-runs/:id`, ({ params }) => {
    return HttpResponse.json({
      success: true,
      data: {
        id: params.id,
        status: 'completed',
        totalTests: 10,
        passedTests: 8,
        failedTests: 2,
      },
    })
  }),

  // Mock configurations endpoints
  http.get(`${API_BASE}/api/configurations`, () => {
    return HttpResponse.json({
      success: true,
      data: [],
    })
  }),

  // Mock analytics endpoints
  http.get(`${API_BASE}/api/analytics/dashboard`, () => {
    return HttpResponse.json({
      success: true,
      data: {
        totalTests: 100,
        passRate: 95.5,
        avgDuration: 45.2,
        trends: [],
      },
    })
  }),

  // Mock defects endpoints
  http.get(`${API_BASE}/api/defects`, () => {
    return HttpResponse.json({
      success: true,
      data: [],
      pagination: {
        page: 1,
        pageSize: 10,
        totalItems: 0,
        totalPages: 0,
      },
    })
  }),

  // Catch-all handler for unhandled requests
  // Comment this out if you want tests to fail on unmocked requests
  http.get('*', ({ request }) => {
    console.warn(`Unmocked GET request: ${request.url}`)
    return HttpResponse.json(
      {
        success: false,
        error: {
          code: 'NOT_IMPLEMENTED',
          message: 'This endpoint is not mocked',
        },
      },
      { status: 501 }
    )
  }),

  http.post('*', ({ request }) => {
    console.warn(`Unmocked POST request: ${request.url}`)
    return HttpResponse.json(
      {
        success: false,
        error: {
          code: 'NOT_IMPLEMENTED',
          message: 'This endpoint is not mocked',
        },
      },
      { status: 501 }
    )
  }),

  http.put('*', ({ request }) => {
    console.warn(`Unmocked PUT request: ${request.url}`)
    return HttpResponse.json(
      {
        success: false,
        error: {
          code: 'NOT_IMPLEMENTED',
          message: 'This endpoint is not mocked',
        },
      },
      { status: 501 }
    )
  }),

  http.delete('*', ({ request }) => {
    console.warn(`Unmocked DELETE request: ${request.url}`)
    return HttpResponse.json(
      {
        success: false,
        error: {
          code: 'NOT_IMPLEMENTED',
          message: 'This endpoint is not mocked',
        },
      },
      { status: 501 }
    )
  }),
]
