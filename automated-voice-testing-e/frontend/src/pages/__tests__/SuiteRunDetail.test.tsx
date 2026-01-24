/**
 * SuiteRunDetail integration tests.
 *
 * Verifies the page fetches run + execution data and renders tables/links.
 */

import React from 'react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { render, screen, waitFor } from '@testing-library/react';

import SuiteRunDetail from '../SuiteRuns/SuiteRunDetail';

const mockGetDetail = vi.fn();
const mockGetExecutions = vi.fn();

vi.mock('../../services/suiteRun.service', () => ({
  getSuiteRunDetail: (...args: unknown[]) => mockGetDetail(...args),
  getSuiteRunExecutions: (...args: unknown[]) => mockGetExecutions(...args),
}));

const detailResponse = {
  id: 'run-123',
  status: 'completed' as const,
  createdAt: '2024-02-01T10:00:00Z',
  startedAt: '2024-02-01T10:01:00Z',
  completedAt: '2024-02-01T10:07:00Z',
  totalTests: 20,
  passedTests: 18,
  failedTests: 1,
  skippedTests: 1,
  triggerType: 'manual',
};

const executionsResponse = [
  {
    id: 'exec-1',
    scriptId: 'case-1',
    languageCode: 'en-US',
    status: 'passed',
    responseSummary: 'Turn on the lights',
    responseTimeSeconds: 3.2,
    confidenceScore: 0.94,
    validationResultId: 'vr-1',
    validationReviewStatus: 'needs_review',
    latestHumanValidationId: 'hv-1',
  },
  {
    id: 'exec-2',
    scriptId: 'case-2',
    languageCode: 'es-ES',
    status: 'failed',
    responseSummary: 'Intent mismatch',
    responseTimeSeconds: 4.1,
    confidenceScore: 0.52,
    pendingValidationQueueId: 'queue-7',
  },
];

const renderWithRouter = () => {
  return render(
    <MemoryRouter initialEntries={['/suite-runs/run-123']}>
      <Routes>
        <Route path="/suite-runs/:id" element={<SuiteRunDetail />} />
      </Routes>
    </MemoryRouter>
  );
};

describe('SuiteRunDetail page', () => {
  beforeEach(() => {
    mockGetDetail.mockReset();
    mockGetExecutions.mockReset();
  });

  it('renders fetched run summary and execution rows', async () => {
    mockGetDetail.mockResolvedValue(detailResponse);
    mockGetExecutions.mockResolvedValue(executionsResponse);

    renderWithRouter();

    await waitFor(() => {
      expect(mockGetDetail).toHaveBeenCalledWith('run-123');
      expect(mockGetExecutions).toHaveBeenCalledWith('run-123');
    });

    expect(await screen.findByText(/Total Tests/i)).toBeInTheDocument();
    expect(screen.getByText('20')).toBeInTheDocument();
    expect(screen.getByRole('table', { name: /executions/i })).toBeInTheDocument();
    expect(screen.getByText('case-1')).toBeInTheDocument();
    expect(screen.getByText('case-2')).toBeInTheDocument();
    expect(screen.getByText(/needs review/i)).toBeInTheDocument();
    expect(screen.getAllByRole('link', { name: /View AI Validation/i })).toHaveLength(1);
    expect(screen.getByRole('link', { name: /Claim Human Review/i })).toBeInTheDocument();
  });

  it('shows error state when fetch fails', async () => {
    const error = new Error('boom');
    mockGetDetail.mockRejectedValue(error);
    mockGetExecutions.mockResolvedValue([]);

    renderWithRouter();

    expect(await screen.findByRole('alert')).toHaveTextContent('Unable to load suite run');
  });
});
