/**
 * ConfigHistory component tests.
 */

import React from 'react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import ConfigHistory from '../ConfigHistory';

const historyResponse = {
  total: 2,
  items: [
    {
      id: 'hist-1',
      configurationId: 'config-1',
      configKey: 'smtp.settings',
      oldValue: {
        config_key: 'smtp.settings',
        config_data: { host: 'smtp.old.com' },
        description: 'Old',
        is_active: true,
      },
      newValue: {
        config_key: 'smtp.settings',
        config_data: { host: 'smtp.example.com' },
        description: 'SMTP configuration',
        is_active: true,
      },
      changedBy: 'user-1',
      changeReason: 'Update host',
      createdAt: '2024-04-10T12:00:00Z',
    },
    {
      id: 'hist-2',
      configurationId: 'config-1',
      configKey: 'smtp.settings',
      oldValue: {
        config_key: 'smtp.settings',
        config_data: { host: 'smtp.example.com' },
        description: 'SMTP configuration',
        is_active: true,
      },
      newValue: {
        config_key: 'smtp.settings',
        config_data: { host: 'smtp.example.com', use_tls: true },
        description: 'SMTP configuration',
        is_active: true,
      },
      changedBy: 'user-2',
      changeReason: 'Enable TLS',
      createdAt: '2024-04-11T08:30:00Z',
    },
  ],
};

const getConfigurationHistoryMock = vi.fn(() => Promise.resolve(historyResponse));

vi.mock('../../../services/configuration.service', () => ({
  getConfigurationHistory: (...args: unknown[]) => getConfigurationHistoryMock(...args),
}));

describe('ConfigHistory', () => {
  beforeEach(() => {
    getConfigurationHistoryMock.mockClear();
  });

  it('renders list of history entries after loading', async () => {
    render(<ConfigHistory configurationId="config-1" />);

    expect(screen.getByRole('progressbar')).toBeInTheDocument();

    await waitFor(() => {
      expect(getConfigurationHistoryMock).toHaveBeenCalledWith('config-1');
    });

    expect(await screen.findByText(/Update host/i)).toBeVisible();
    expect(screen.getByText(/Enable TLS/i)).toBeVisible();
  });

  it('shows diff view for selected history entry', async () => {
    render(<ConfigHistory configurationId="config-1" />);
    await waitFor(() => expect(getConfigurationHistoryMock).toHaveBeenCalled());

    expect(await screen.findByText(/Enable TLS/i)).toBeVisible();
    await userEvent.click(screen.getByText(/Enable TLS/i));

    const diffMatches = await screen.findAllByText(/use_tls/);
    expect(diffMatches[0]).toBeVisible();
  });

  it('switches to raw JSON snapshot view', async () => {
    render(<ConfigHistory configurationId="config-1" />);
    await waitFor(() => expect(getConfigurationHistoryMock).toHaveBeenCalled());

    const snapshotToggle = await screen.findByRole('button', { name: /JSON Snapshot/i });
    await userEvent.click(snapshotToggle);

    expect(await screen.findByText(/"use_tls": true/)).toBeVisible();
  });

  it('renders empty state when no history entries exist', async () => {
    getConfigurationHistoryMock.mockResolvedValueOnce({ total: 0, items: [] });
    render(<ConfigHistory configurationId="config-empty" />);

    expect(await screen.findByText(/No history entries available/i)).toBeVisible();
  });

  it('renders error state when fetch fails', async () => {
    getConfigurationHistoryMock.mockRejectedValueOnce(new Error('boom'));
    render(<ConfigHistory configurationId="config-error" />);

    expect(
      await screen.findByText(/Unable to load configuration history/i, { exact: false })
    ).toBeVisible();
  });
});
