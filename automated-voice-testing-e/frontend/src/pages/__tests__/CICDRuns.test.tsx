/**
 * CI/CD Runs page tests.
 *
 * Ensures CI/CD runs listing fetches data, renders commit links, and
 * refilters when the status filter changes.
 */

import React from 'react';
import { describe, beforeEach, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import CICDRuns from '../CICD/CICDRuns';

const fetchRunsMock = vi.fn();

vi.mock('../../services/cicd.service', () => ({
  getCICDRuns: (...args: unknown[]) => fetchRunsMock(...args),
}));

describe('CICDRuns page', () => {
  beforeEach(() => {
    fetchRunsMock.mockReset();
  });

  it('renders runs with commit links after loading data', async () => {
    fetchRunsMock.mockResolvedValue({
      runs: [
        {
          id: 'run-1',
          pipelineName: 'Nightly regression',
          status: 'success',
          branch: 'main',
          commitSha: 'abc1234',
          commitUrl: 'https://github.com/example/repo/commit/abc1234',
          triggeredBy: 'CI Bot',
          startedAt: '2024-02-10T12:00:00Z',
          completedAt: '2024-02-10T12:10:00Z',
          totalTests: 200,
          passedTests: 198,
          failedTests: 2,
        },
      ],
    });

    render(
      <MemoryRouter>
        <CICDRuns />
      </MemoryRouter>
    );

    expect(await screen.findByText(/Nightly regression/i)).toBeInTheDocument();
    expect(screen.getByText(/198 passed/i)).toBeInTheDocument();

    const commitLink = screen.getByRole('link', { name: /abc1234/i });
    expect(commitLink).toHaveAttribute(
      'href',
      'https://github.com/example/repo/commit/abc1234'
    );
  });

  it('refetches runs when selecting a different status filter', async () => {
    fetchRunsMock.mockResolvedValue({ runs: [] });

    render(
      <MemoryRouter>
        <CICDRuns />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(fetchRunsMock).toHaveBeenCalledWith({ status: null });
    });
    fetchRunsMock.mockClear();

    const statusSelect = await screen.findByLabelText(/Status/i);
    await userEvent.click(statusSelect);

    const failedOption = await screen.findByRole('option', { name: /Failed/i });
    await userEvent.click(failedOption);

    await waitFor(() => {
      expect(fetchRunsMock).toHaveBeenCalledWith({ status: 'failed' });
    });
  });
});
