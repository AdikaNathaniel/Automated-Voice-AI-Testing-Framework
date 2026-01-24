import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import AnalyticsComparisonView, {
  type ComparisonDimensionOption,
  type AnalyticsComparisonData,
} from '../ComparisonView';

const dimensionOptions: ComparisonDimensionOption[] = [
  { id: 'language', label: 'Languages' },
  { id: 'testType', label: 'Test Types' },
  { id: 'timePeriod', label: 'Time Periods' },
];

const baseData: AnalyticsComparisonData = {
  dimension: 'language',
  entries: [
    {
      id: 'en-US',
      label: 'English (US)',
      sampleSize: 420,
      passRatePct: 96.2,
      passRateDeltaPct: 1.4,
      defectRatePct: 2.1,
      defectDeltaPct: -0.6,
      avgResponseTimeMs: 1084,
      responseDeltaMs: -92,
    },
    {
      id: 'es-ES',
      label: 'Spanish (Spain)',
      sampleSize: 210,
      passRatePct: 88.9,
      passRateDeltaPct: -2.3,
      defectRatePct: 6.2,
      defectDeltaPct: 1.8,
      avgResponseTimeMs: 1240,
      responseDeltaMs: 54,
    },
  ],
};

describe('AnalyticsComparisonView', () => {
  it('renders comparison entries with formatted metrics', () => {
    render(
      <AnalyticsComparisonView
        title="Performance by Language"
        options={dimensionOptions}
        data={baseData}
        onDimensionChange={vi.fn()}
      />
    );

    expect(screen.getByRole('heading', { name: /performance by language/i })).toBeInTheDocument();

    const table = screen.getByRole('table', { name: /comparison metrics/i });
    const rows = within(table).getAllByRole('row');
    expect(rows).toHaveLength(baseData.entries.length + 1); // header + entries

    expect(within(rows[1]).getByText('English (US)')).toBeInTheDocument();
    expect(within(rows[1]).getByText('96.2%')).toBeInTheDocument();
    expect(within(rows[1]).getByText('+1.4 pts')).toBeInTheDocument();
    expect(within(rows[1]).getByText('2.1%')).toBeInTheDocument();
    expect(within(rows[1]).getByText('-0.6 pts')).toBeInTheDocument();
    expect(within(rows[1]).getByText('1,084 ms')).toBeInTheDocument();
    expect(within(rows[1]).getByText('-92 ms')).toBeInTheDocument();
    expect(within(rows[1]).getByText('420')).toBeInTheDocument();
  });

  it('invokes dimension change callback when toggles are used', async () => {
    const handleDimensionChange = vi.fn();
    const user = userEvent.setup();

    render(
      <AnalyticsComparisonView
        title="Performance by Language"
        options={dimensionOptions}
        data={baseData}
        onDimensionChange={handleDimensionChange}
      />
    );

    const testTypeButton = screen.getByRole('button', { name: /test types/i });
    await user.click(testTypeButton);

    expect(handleDimensionChange).toHaveBeenCalledWith('testType');
  });

  it('shows helpful empty state when no comparison data', () => {
    render(
      <AnalyticsComparisonView
        title="Performance by Language"
        options={dimensionOptions}
        data={{ dimension: 'language', entries: [] }}
        onDimensionChange={vi.fn()}
      />
    );

    expect(screen.getByText(/no comparison data available/i)).toBeInTheDocument();
  });
});
