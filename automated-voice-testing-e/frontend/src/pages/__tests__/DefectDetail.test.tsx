/**
 * DefectDetail page tests.
 *
 * Validates defect detail rendering, including related executions and comments.
 */

import React from 'react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { render, screen, waitFor } from '@testing-library/react';

import DefectDetail from '../Defects/DefectDetail';

const getDefectDetailMock = vi.fn();

vi.mock('../../services/defect.service', () => ({
  getDefectDetail: (...args: unknown[]) => getDefectDetailMock(...args),
}));

const renderWithRoute = (path = '/defects/defect-1') =>
  render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/defects/:defectId" element={<DefectDetail />} />
      </Routes>
    </MemoryRouter>
  );

describe('DefectDetail page', () => {
  beforeEach(() => {
    getDefectDetailMock.mockReset();
  });

  it('renders defect details with executions and comments', async () => {
    getDefectDetailMock.mockResolvedValue({
      id: 'defect-1',
      title: 'Refund flow fails with invalid amount',
      severity: 'high',
      category: 'semantic',
      status: 'open',
      scriptId: 'case-123',
      languageCode: 'en-US',
      detectedAt: '2024-04-10T12:00:00Z',
      description: 'User cannot complete refund due to validation error.',
      relatedExecutions: [
        { id: 'exec-1', status: 'failed', suiteRunId: 'run-1', executedAt: '2024-04-10T11:50:00Z' },
      ],
      comments: [
        { id: 'comment-1', author: 'qa.engineer@example.com', message: 'Needs hotfix.', createdAt: '2024-04-10T12:10:00Z' },
      ],
    });

    renderWithRoute();

    await waitFor(() => expect(getDefectDetailMock).toHaveBeenCalledWith('defect-1'));

    expect(await screen.findByRole('heading', { name: /Refund flow fails/i })).toBeInTheDocument();
    expect(screen.getByTestId('defect-detail-severity')).toHaveTextContent(/high/i);
    expect(screen.getByText(/semantic/i)).toBeInTheDocument();
    expect(screen.getByText(/case-123/i)).toBeInTheDocument();
    expect(screen.getByText(/Needs hotfix/i)).toBeInTheDocument();
    expect(screen.getByText(/exec-1/i)).toBeInTheDocument();
  });

  it('shows error feedback when defect load fails', async () => {
    getDefectDetailMock.mockRejectedValue(new Error('Network error'));

    renderWithRoute();

    await waitFor(() => expect(screen.getByText(/Failed to load defect details/i)).toBeInTheDocument());
  });
});
