import React from 'react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { render, screen, waitFor, within } from '@testing-library/react';

import RegressionList from '../Regressions/RegressionList';

const mockGetRegressions = vi.fn();

vi.mock('../../services/regression.service', () => ({
  getRegressions: (...args: unknown[]) => mockGetRegressions(...args),
}));

describe('RegressionList page', () => {
  beforeEach(() => {
    mockGetRegressions.mockReset();
  });

  it('renders summary metrics and regression rows', async () => {
    mockGetRegressions.mockResolvedValue({
      summary: {
        totalRegressions: 5,
        statusRegressions: 3,
        metricRegressions: 2,
      },
      items: [
        {
          scriptId: 'case-1',
          category: 'status',
          detail: { baseline_status: 'passed', current_status: 'failed' },
          detectedAt: '2025-02-01T10:00:00Z',
        },
      ],
    });

    render(
      <MemoryRouter>
        <RegressionList />
      </MemoryRouter>
    );

    expect(mockGetRegressions).toHaveBeenCalledTimes(1);

    await screen.findByText(/Total regressions/i);
    expect(screen.getByText('5')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();

    const row = await screen.findByRole('row', { name: /case-1/ });
    expect(within(row).getByText(/status/i)).toBeInTheDocument();
    expect(within(row).getByText(/passed → failed/i)).toBeInTheDocument();

    const viewLink = within(row).getByRole('link', { name: /View comparison/i });
    expect(viewLink).toHaveAttribute('href', '/regressions/case-1/comparison');

    const manageLink = within(row).getByRole('link', { name: /Manage baseline/i });
    expect(manageLink).toHaveAttribute('href', '/regressions/case-1/baselines');
  });

  it('shows empty state when no regressions exist', async () => {
    mockGetRegressions.mockResolvedValue({
      summary: {
        totalRegressions: 0,
        statusRegressions: 0,
        metricRegressions: 0,
      },
      items: [],
    });

    render(
      <MemoryRouter>
        <RegressionList />
      </MemoryRouter>
    );

    await screen.findByText(/No regressions detected/i);
  });

  it('renders error message when load fails', async () => {
    mockGetRegressions.mockRejectedValue(new Error('Network failure'));

    render(
      <MemoryRouter>
        <RegressionList />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Network failure/i)).toBeInTheDocument();
    });
  });
});
