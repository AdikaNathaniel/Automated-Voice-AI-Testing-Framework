/**
 * Edge case creation flow tests.
 *
 * Ensures the creation page pre-fills data from failure context and persists new edge cases.
 */

import React from 'react'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { Routes, Route } from 'react-router-dom'
import { act } from 'react'
import { renderWithProviders, screen, userEvent } from '../../test/utils'

import EdgeCaseCreate from '../EdgeCases/EdgeCaseCreate'

const createEdgeCaseMock = vi.fn()

vi.mock('../../services/edgeCase.service', () => ({
  createEdgeCase: (...args: unknown[]) => createEdgeCaseMock(...args),
}))

const navigateMock = vi.fn()

vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal<typeof import('react-router-dom')>()
  return {
    ...actual,
    useNavigate: () => navigateMock,
  }
})

const FAILURE_QUERY =
  '?scriptId=case-321&failureReason=External%20API%20timeout&failureCategory=timeout&failureDetails=%7B%22step%22%3A%22order_status%22%7D'

describe('EdgeCaseCreate', () => {
  beforeEach(() => {
    createEdgeCaseMock.mockReset()
    navigateMock.mockReset()
  })

  it('prefills the form using failure context from the URL parameters', async () => {
    await act(async () => {
      renderWithProviders(
        <Routes>
          <Route path="/edge-cases/new" element={<EdgeCaseCreate />} />
        </Routes>,
        { route: `/edge-cases/new${FAILURE_QUERY}` }
      )
    })

    expect(
      (screen.getByLabelText(/Edge case title/i) as HTMLInputElement).value
    ).toContain('External API timeout')
    expect(
      (screen.getByLabelText(/Description/i) as HTMLTextAreaElement).value
    ).toContain('External API timeout')
    expect(screen.getByLabelText(/Category/i)).toHaveValue('timeout')
    expect(screen.getByLabelText(/Related script/i)).toHaveValue('case-321')
  })

  it('submits the form and navigates to the new edge case detail page', async () => {
    createEdgeCaseMock.mockResolvedValue({
      id: 'edge-999',
    })

    await act(async () => {
      renderWithProviders(
        <Routes>
          <Route path="/edge-cases/new" element={<EdgeCaseCreate />} />
        </Routes>,
        { route: `/edge-cases/new${FAILURE_QUERY}` }
      )
    })

    await userEvent.type(screen.getByLabelText(/Tags/i), 'timeout, external')
    await userEvent.selectOptions(screen.getByLabelText(/Severity/i), 'high')

    await userEvent.click(screen.getByRole('button', { name: /Create edge case/i }))

    expect(createEdgeCaseMock).toHaveBeenCalledWith(
      expect.objectContaining({
        title: expect.stringContaining('External API timeout'),
        description: expect.stringContaining('External API timeout'),
        category: 'timeout',
        severity: 'high',
        scriptId: 'case-321',
        tags: ['timeout', 'external'],
      })
    )

    expect(navigateMock).toHaveBeenCalledWith('/edge-cases/edge-999', { replace: true })
  })

  it('displays an error alert when creation fails', async () => {
    createEdgeCaseMock.mockRejectedValue(new Error('Failed to create edge case'))

    await act(async () => {
      renderWithProviders(
        <Routes>
          <Route path="/edge-cases/new" element={<EdgeCaseCreate />} />
        </Routes>,
        { route: `/edge-cases/new${FAILURE_QUERY}` }
      )
    })

    await userEvent.click(screen.getByRole('button', { name: /Create edge case/i }))

    await screen.findByText(/Failed to create edge case/i)
    expect(navigateMock).not.toHaveBeenCalled()
  })
})
