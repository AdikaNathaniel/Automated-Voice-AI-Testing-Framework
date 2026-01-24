/**
 * EdgeCaseDetail page tests.
 *
 * Validates detail rendering and related script display behaviour.
 */

import React from 'react'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { Routes, Route } from 'react-router-dom'
import { act } from 'react'
import { renderWithProviders, screen } from '../../test/utils'

import EdgeCaseDetail from '../EdgeCases/EdgeCaseDetail'

const getEdgeCaseMock = vi.fn()

vi.mock('../../services/edgeCase.service', () => ({
  getEdgeCase: (...args: unknown[]) => getEdgeCaseMock(...args),
}))

const edgeCaseFixture = {
  id: 'edge-1',
  title: 'External service timeout',
  description: 'Upstream fulfilment API exceeded SLA.',
  scenarioDefinition: {
    failure_reason: 'Timeout exceeded 5000ms',
    steps: ['Invoke order status API', 'Await response'],
  },
  tags: ['timeout', 'external'],
  severity: 'high',
  category: 'timeout',
  status: 'active',
  scriptId: 'script-123',
  discoveredDate: '2024-06-01',
  discoveredBy: 'analyst-1',
  createdAt: '2024-06-01T00:00:00Z',
  updatedAt: '2024-06-02T00:00:00Z',
}

describe('EdgeCaseDetail', () => {
  beforeEach(() => {
    getEdgeCaseMock.mockReset()
  })

  it('renders edge case details including description and status', async () => {
    getEdgeCaseMock.mockResolvedValue(edgeCaseFixture)

    await act(async () => {
      renderWithProviders(
        <Routes>
          <Route path="/edge-cases/:edgeCaseId" element={<EdgeCaseDetail />} />
        </Routes>,
        { route: '/edge-cases/edge-1' }
      )
    })

    expect(getEdgeCaseMock).toHaveBeenCalledWith('edge-1')

    await screen.findByRole('heading', { name: /External service timeout/i })
    expect(screen.getByText(/Upstream fulfilment API exceeded SLA/i)).toBeInTheDocument()
  })

  it('displays related script ID when available', async () => {
    getEdgeCaseMock.mockResolvedValue(edgeCaseFixture)

    await act(async () => {
      renderWithProviders(
        <Routes>
          <Route path="/edge-cases/:edgeCaseId" element={<EdgeCaseDetail />} />
        </Routes>,
        { route: '/edge-cases/edge-1' }
      )
    })

    await screen.findByRole('heading', { name: /External service timeout/i })
    expect(screen.getByText(/script-123/i)).toBeInTheDocument()
  })

  it('renders an error message when loading fails', async () => {
    getEdgeCaseMock.mockRejectedValue(new Error('service unavailable'))

    await act(async () => {
      renderWithProviders(
        <Routes>
          <Route path="/edge-cases/:edgeCaseId" element={<EdgeCaseDetail />} />
        </Routes>,
        { route: '/edge-cases/edge-1' }
      )
    })

    await screen.findByText(/Unable to load edge case/i)
    expect(screen.getByText(/service unavailable/i)).toBeInTheDocument()
  })
})
