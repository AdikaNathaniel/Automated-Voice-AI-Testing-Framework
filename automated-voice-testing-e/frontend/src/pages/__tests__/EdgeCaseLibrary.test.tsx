/**
 * EdgeCaseLibrary page tests.
 *
 * Verifies the library groups edge cases by category and renders cards for each item.
 */

import React from 'react'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { act } from 'react'
import { renderWithProviders, screen, userEvent, waitFor } from '../../test/utils'

import EdgeCaseLibrary from '../EdgeCases/EdgeCaseLibrary'

const listEdgeCasesMock = vi.fn()
const searchEdgeCasesMock = vi.fn()
const listPatternGroupsMock = vi.fn()
const getTrendingPatternsMock = vi.fn()

vi.mock('../../services/edgeCase.service', () => ({
  listEdgeCases: (...args: unknown[]) => listEdgeCasesMock(...args),
  searchEdgeCases: (...args: unknown[]) => searchEdgeCasesMock(...args),
}))

vi.mock('../../services/patternGroup.service', () => ({
  listPatternGroups: (...args: unknown[]) => listPatternGroupsMock(...args),
  getTrendingPatterns: (...args: unknown[]) => getTrendingPatternsMock(...args),
  triggerPatternAnalysis: vi.fn(),
  checkAnalysisStatus: vi.fn(),
}))

const mockEdgeCases = [
  {
    id: 'edge-1',
    title: 'External service timeout',
    description: 'Upstream fulfilment API exceeded SLA.',
    scenarioDefinition: {},
    tags: ['timeout', 'external'],
    severity: 'high',
    category: 'timeout',
    status: 'active',
    scriptId: 'case-1',
    discoveredDate: '2024-06-01',
    discoveredBy: 'user-1',
    createdAt: '2024-06-01T00:00:00Z',
    updatedAt: '2024-06-01T00:00:00Z',
  },
  {
    id: 'edge-2',
    title: 'Ambiguous slot resolution',
    description: 'Multiple locations matched Springfield.',
    scenarioDefinition: {},
    tags: ['ambiguity'],
    severity: 'medium',
    category: 'ambiguity',
    status: 'active',
    scriptId: 'case-2',
    discoveredDate: '2024-06-02',
    discoveredBy: 'user-2',
    createdAt: '2024-06-02T00:00:00Z',
    updatedAt: '2024-06-02T00:00:00Z',
  },
  {
    id: 'edge-3',
    title: 'Checkout timeout',
    description: 'Payment handoff did not respond within 5s.',
    scenarioDefinition: {},
    tags: ['timeout'],
    severity: 'high',
    category: 'timeout',
    status: 'active',
    scriptId: 'case-3',
    discoveredDate: '2024-06-03',
    discoveredBy: 'user-3',
    createdAt: '2024-06-03T00:00:00Z',
    updatedAt: '2024-06-03T00:00:00Z',
  },
]

describe('EdgeCaseLibrary', () => {
  beforeEach(() => {
    listEdgeCasesMock.mockReset()
    searchEdgeCasesMock.mockReset()
    listPatternGroupsMock.mockReset()
    getTrendingPatternsMock.mockReset()

    listEdgeCasesMock.mockResolvedValue({
      total: mockEdgeCases.length,
      items: mockEdgeCases,
    })
    searchEdgeCasesMock.mockResolvedValue({
      total: 0,
      items: [],
    })
    listPatternGroupsMock.mockResolvedValue({
      total: 0,
      items: [],
    })
    getTrendingPatternsMock.mockResolvedValue([])
  })

  it('lists edge cases grouped by category', async () => {
    await act(async () => {
      renderWithProviders(<EdgeCaseLibrary />)
    })

    expect(listEdgeCasesMock).toHaveBeenCalledWith(
      expect.objectContaining({ limit: 50, skip: 0 })
    )

    // Wait for edge cases to be rendered
    await waitFor(() => {
      expect(screen.getByText('External service timeout')).toBeInTheDocument()
    })

    // Check category headers exist
    expect(screen.getByText(/Timeout/)).toBeInTheDocument()
    expect(screen.getByText(/Ambiguity/)).toBeInTheDocument()

    // Check edge case titles are rendered
    expect(screen.getByText('External service timeout')).toBeInTheDocument()
    expect(screen.getByText('Ambiguous slot resolution')).toBeInTheDocument()
    expect(screen.getByText('Checkout timeout')).toBeInTheDocument()

    // Check descriptions are rendered
    expect(screen.getByText(/Upstream fulfilment API exceeded SLA/)).toBeInTheDocument()
    expect(screen.getByText(/Multiple locations matched Springfield/)).toBeInTheDocument()
  })

  it('searches edge cases by keyword and updates the results', async () => {
    const searchResults = [
      {
        ...mockEdgeCases[0],
        id: 'edge-99',
        title: 'Timeout during escalation handoff',
        tags: ['timeout', 'handoff'],
      },
    ]

    searchEdgeCasesMock.mockResolvedValueOnce({
      total: searchResults.length,
      items: searchResults,
    })

    const user = userEvent.setup()

    await act(async () => {
      renderWithProviders(<EdgeCaseLibrary />)
    })

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('External service timeout')).toBeInTheDocument()
    })

    // Find and use the search input by placeholder text
    const searchInput = screen.getByPlaceholderText(/Search by keyword/i)
    expect(searchInput).toBeInTheDocument()

    await user.clear(searchInput)
    await user.type(searchInput, 'escalation timeout')

    // Submit the form by pressing Enter
    await user.keyboard('{Enter}')

    await waitFor(() => {
      expect(searchEdgeCasesMock).toHaveBeenCalledWith(
        expect.objectContaining({
          query: 'escalation timeout',
          limit: 50,
          skip: 0,
        })
      )
    })
  })

  it('displays loading state while fetching edge cases', async () => {
    // Delay the response to see loading state
    listEdgeCasesMock.mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({
        total: mockEdgeCases.length,
        items: mockEdgeCases,
      }), 100))
    )

    await act(async () => {
      renderWithProviders(<EdgeCaseLibrary />)
    })

    expect(screen.getByText(/Loading Edge Cases/i)).toBeInTheDocument()

    await waitFor(() => {
      expect(screen.queryByText(/Loading Edge Cases/i)).not.toBeInTheDocument()
    })
  })

  it('displays error state when fetch fails', async () => {
    listEdgeCasesMock.mockRejectedValueOnce(new Error('Network error'))

    await act(async () => {
      renderWithProviders(<EdgeCaseLibrary />)
    })

    await waitFor(() => {
      expect(screen.getByText(/Unable to load edge cases/i)).toBeInTheDocument()
    })
  })

  it('displays empty state when no edge cases found', async () => {
    listEdgeCasesMock.mockResolvedValueOnce({
      total: 0,
      items: [],
    })

    await act(async () => {
      renderWithProviders(<EdgeCaseLibrary />)
    })

    await waitFor(() => {
      expect(screen.getByText(/No Edge Cases Found/i)).toBeInTheDocument()
    })
  })
})
