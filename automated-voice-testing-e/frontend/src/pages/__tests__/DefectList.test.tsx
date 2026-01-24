/**
 * DefectList page tests.
 *
 * Verifies the defects listing fetches data with filters and renders severity badges.
 */

import React from 'react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import DefectList from '../Defects/DefectList';

const getDefectsMock = vi.fn(() =>
  Promise.resolve({
    total: 1,
    items: [
      {
        id: 'defect-1',
        title: 'Refund flow fails with invalid amount',
        severity: 'high',
        category: 'semantic',
        status: 'open',
        scriptId: 'case-123',
        languageCode: 'en-US',
        detectedAt: '2024-04-10T12:00:00Z',
      },
    ],
  })
);

vi.mock('../../services/defect.service', () => ({
  getDefects: (...args: unknown[]) => getDefectsMock(...args),
}));

describe('DefectList page', () => {
  beforeEach(() => {
    getDefectsMock.mockClear();
  });

  const renderPage = () =>
    render(
      <MemoryRouter>
        <DefectList />
      </MemoryRouter>
    );

  it('fetches defects with default filters on mount', async () => {
    renderPage();

    await waitFor(() => {
      expect(getDefectsMock).toHaveBeenCalledWith({
        status: null,
        severity: null,
        category: null,
        page: 1,
        pageSize: 25,
      });
    });

    expect(await screen.findByText(/Refund flow fails with invalid amount/i)).toBeInTheDocument();
    const severityChip = screen.getByTestId('defect-severity-chip-high');
    expect(severityChip).toHaveTextContent(/high/i);
  });

  it('refetches defects when severity filter changes', async () => {
    renderPage();

    await waitFor(() => expect(getDefectsMock).toHaveBeenCalledTimes(1));
    getDefectsMock.mockClear();

    const severitySelect = await screen.findByLabelText(/Severity/i);
    await userEvent.click(severitySelect);

    const mediumOption = await screen.findByRole('option', { name: /Medium/i });
    await userEvent.click(mediumOption);

    await waitFor(() => {
      expect(getDefectsMock).toHaveBeenCalledWith(
        expect.objectContaining({
          severity: 'medium',
        })
      );
    });
  });
});
