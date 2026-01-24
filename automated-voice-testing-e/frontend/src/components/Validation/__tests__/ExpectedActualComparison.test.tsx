/**
 * ExpectedActualComparison Component Tests
 *
 * Verifies that the component renders comparison items, formats complex values,
 * and highlights mismatches between expected and actual values.
 */

import { describe, it, expect } from 'vitest'
import { render, screen, within } from '@testing-library/react'
import ExpectedActualComparison, {
  type ComparisonItem,
} from '../ExpectedActualComparison'

describe('ExpectedActualComparison', () => {
  const baseItems: ComparisonItem[] = [
    {
      label: 'Intent',
      expected: 'weather_query',
      actual: 'weather_query',
    },
    {
      label: 'Entities',
      expected: { location: 'New York' },
      actual: { location: 'Boston' },
    },
  ]

  it('renders provided comparison items with formatted values', () => {
    render(
      <ExpectedActualComparison title="Expected vs Actual" items={baseItems} />
    )

    expect(
      screen.getByRole('heading', { name: 'Expected vs Actual' })
    ).toBeInTheDocument()
    expect(screen.getByText('Intent')).toBeInTheDocument()
    const intentSection = screen
      .getByText('Intent')
      .closest('[data-comparison-item]')
    expect(intentSection).toBeTruthy()
    if (intentSection) {
      const intentValues = within(intentSection).getAllByText('weather_query')
      expect(intentValues).toHaveLength(2)
    }

    const entitiesSection = screen
      .getByText('Entities')
      .closest('[data-comparison-item]')
    expect(entitiesSection).toBeTruthy()
    if (entitiesSection) {
      expect(within(entitiesSection).getByText(/"New York"/)).toBeInTheDocument()
      expect(within(entitiesSection).getByText(/"Boston"/)).toBeInTheDocument()
    }
  })

  it('highlights mismatched actual values when enabled', () => {
    render(<ExpectedActualComparison items={baseItems} />)

    // Should render mismatch indicator for the entities item only
    const mismatchChips = screen.getAllByText('Mismatch')
    expect(mismatchChips).toHaveLength(1)
    expect(mismatchChips[0]).toBeVisible()
    expect(
      within(mismatchChips[0].closest('[data-comparison-item]')!)
        .getByText(/"Boston"/)
    ).toBeInTheDocument()
  })

  it('renders empty state text when no items provided', () => {
    render(
      <ExpectedActualComparison
        items={[]}
        emptyStateText="No comparison data available"
      />
    )

    expect(
      screen.getByText('No comparison data available')
    ).toBeInTheDocument()
  })
})
