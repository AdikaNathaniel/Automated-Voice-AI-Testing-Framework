import React from 'react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { render, screen, waitFor, within } from '@testing-library/react';

import RegressionComparison from '../Regressions/RegressionComparison';

const mockGetRegressionComparison = vi.fn();

vi.mock('../../services/regression.service', () => ({
  getRegressionComparison: (...args: unknown[]) => mockGetRegressionComparison(...args),
}));

describe('RegressionComparison page', () => {
  beforeEach(() => {
    mockGetRegressionComparison.mockReset();
  });

  it('renders baseline and current snapshots side by side with metric deltas', async () => {
    mockGetRegressionComparison.mockResolvedValue({
      scriptId: 'case-1',
      baseline: {
        status: 'passed',
        mediaUri: 'https://example.com/baseline.wav',
        metrics: {
          accuracy: { value: 0.95, threshold: 0.9, unit: null },
        },
      },
      current: {
        status: 'failed',
        mediaUri: null,
        metrics: {
          accuracy: { value: 0.82, threshold: 0.9, unit: null },
        },
      },
      differences: [
        {
          metric: 'accuracy',
          baselineValue: 0.95,
          currentValue: 0.82,
          delta: -0.13,
          deltaPercent: -13.68,
        },
      ],
    });

    render(
      <MemoryRouter initialEntries={['/regressions/case-1/comparison']}>
        <Routes>
          <Route path="/regressions/:scriptId/comparison" element={<RegressionComparison />} />
        </Routes>
      </MemoryRouter>
    );

    expect(mockGetRegressionComparison).toHaveBeenCalledWith('case-1');

    const baselinePanel = await screen.findByTestId('regression-baseline');
    const currentPanel = await screen.findByTestId('regression-current');

    expect(within(baselinePanel).getByText(/Baseline snapshot/i)).toBeInTheDocument();
    expect(within(baselinePanel).getByText(/passed/i)).toBeInTheDocument();
    expect(within(currentPanel).getByText(/Current snapshot/i)).toBeInTheDocument();
    expect(within(currentPanel).getByText(/failed/i)).toBeInTheDocument();

    const metricsTable = screen.getByRole('table', { name: /Metric comparison/i });
    const metricRow = within(metricsTable).getByRole('row', { name: /accuracy/i });
    expect(within(metricRow).getByText('0.95')).toBeInTheDocument();
    expect(within(metricRow).getByText('0.82')).toBeInTheDocument();
    expect(within(metricRow).getByText('-0.13')).toBeInTheDocument();
    expect(within(metricRow).getByText('-13.68%')).toBeInTheDocument();

    const manageLink = screen.getByRole('link', { name: /Manage baseline/i });
    expect(manageLink).toHaveAttribute('href', '/regressions/case-1/baselines');
  });

  it('renders an error message when comparison data fails to load', async () => {
    mockGetRegressionComparison.mockRejectedValue(new Error('Unable to load comparison'));

    render(
      <MemoryRouter initialEntries={['/regressions/case-1/comparison']}>
        <Routes>
          <Route path="/regressions/:scriptId/comparison" element={<RegressionComparison />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Unable to load comparison/i)).toBeInTheDocument();
    });
  });
});
