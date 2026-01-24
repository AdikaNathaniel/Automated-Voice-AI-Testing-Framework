import React from 'react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { render, screen, waitFor, fireEvent, within } from '@testing-library/react';

import BaselineManagement from '../Regressions/BaselineManagement';

const mockGetBaselineHistory = vi.fn();
const mockApproveBaseline = vi.fn();

vi.mock('../../services/regression.service', () => ({
  getBaselineHistory: (...args: unknown[]) => mockGetBaselineHistory(...args),
  approveBaseline: (...args: unknown[]) => mockApproveBaseline(...args),
}));

describe('BaselineManagement page', () => {
  beforeEach(() => {
    mockGetBaselineHistory.mockReset();
    mockApproveBaseline.mockReset();
  });

  it('renders baseline history and allows approving a pending baseline', async () => {
    mockGetBaselineHistory.mockResolvedValueOnce({
      history: [
        {
          version: 2,
          status: 'passed',
          metrics: { accuracy: 0.95 },
          approvedAt: '2025-02-01T12:00:00Z',
          approvedBy: 'user-123',
          note: 'Updated baseline',
        },
      ],
      pending: {
        status: 'failed',
        metrics: { accuracy: 0.8 },
        detectedAt: '2025-02-02T09:00:00Z',
        proposedBy: 'user-456',
      },
    });

    mockApproveBaseline.mockResolvedValueOnce({
      scriptId: 'case-1',
      status: 'failed',
      metrics: { accuracy: 0.8 },
      version: 3,
      approvedAt: '2025-02-02T10:00:00Z',
      approvedBy: 'user-789',
      note: 'Accepted',
    });

    mockGetBaselineHistory.mockResolvedValueOnce({
      history: [
        {
          version: 3,
          status: 'failed',
          metrics: { accuracy: 0.8 },
          approvedAt: '2025-02-02T10:00:00Z',
          approvedBy: 'user-789',
          note: 'Accepted',
        },
      ],
      pending: null,
    });

    render(
      <MemoryRouter initialEntries={['/regressions/case-1/baselines']}>
        <Routes>
          <Route path="/regressions/:scriptId/baselines" element={<BaselineManagement />} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByText(/Baseline management/i)).toBeInTheDocument();

    const historyTable = screen.getByRole('table', { name: /Baseline history/i });
    expect(within(historyTable).getByText(/version 2/i)).toBeInTheDocument();
    expect(within(historyTable).getByText(/passed/i)).toBeInTheDocument();

    const approveButton = screen.getByRole('button', { name: /Approve baseline/i });
    fireEvent.click(approveButton);

    await waitFor(() => {
      expect(mockApproveBaseline).toHaveBeenCalledWith('case-1', {
        status: 'failed',
        metrics: { accuracy: 0.8 },
        note: '',
      });
    });

    await waitFor(() => {
      expect(mockGetBaselineHistory).toHaveBeenCalledTimes(2);
    });

    expect(await screen.findByText(/Baseline approved successfully/i)).toBeInTheDocument();
  });

  it('allows rejecting a pending baseline without calling the API', async () => {
    mockGetBaselineHistory.mockResolvedValueOnce({
      history: [],
      pending: {
        status: 'failed',
        metrics: { accuracy: 0.75 },
        detectedAt: '2025-02-03T08:00:00Z',
        proposedBy: null,
      },
    });

    render(
      <MemoryRouter initialEntries={['/regressions/case-1/baselines']}>
        <Routes>
          <Route path="/regressions/:scriptId/baselines" element={<BaselineManagement />} />
        </Routes>
      </MemoryRouter>
    );

    const rejectButton = await screen.findByRole('button', { name: /Reject baseline/i });
    fireEvent.click(rejectButton);

    await waitFor(() => {
      expect(screen.queryByText(/Pending baseline/i)).not.toBeInTheDocument();
    });
    expect(mockApproveBaseline).not.toHaveBeenCalled();
  });

  it('renders an error message when history fails to load', async () => {
    mockGetBaselineHistory.mockRejectedValueOnce(new Error('Failed to fetch history'));

    render(
      <MemoryRouter initialEntries={['/regressions/case-1/baselines']}>
        <Routes>
          <Route path="/regressions/:scriptId/baselines" element={<BaselineManagement />} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByText(/Failed to fetch history/i)).toBeInTheDocument();
  });
});
