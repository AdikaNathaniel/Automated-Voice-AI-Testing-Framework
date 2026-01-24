/**
 * OrganizationConfigurations page tests.
 *
 * NOTE: These tests are outdated and need to be rewritten to match
 * the new OrganizationConfigurations component functionality (Pattern Analysis, etc.)
 *
 * TODO: Update tests to cover Pattern Analysis configuration tabs
 */

import React from 'react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import OrganizationConfigurations from '../Configurations/OrganizationConfigurations';

const getConfigurationsMock = vi.fn(() =>
  Promise.resolve({
    total: 2,
    items: [
      {
        id: 'config-1',
        configKey: 'smtp.settings',
        type: 'integration',
        environment: 'production',
        description: 'SMTP configuration for production mail delivery',
        isActive: true,
        updatedAt: '2024-04-10T12:00:00Z',
      },
      {
        id: 'config-2',
        configKey: 'feature.flag.voice_navigation',
        type: 'feature',
        environment: 'staging',
        description: 'Voice navigation rollout flag',
        isActive: false,
        updatedAt: '2024-04-11T08:30:00Z',
      },
    ],
  })
);

vi.mock('../../services/configuration.service', () => ({
  getConfigurations: (...args: unknown[]) => getConfigurationsMock(...args),
}));

describe('OrganizationConfigurations page', () => {
  beforeEach(() => {
    getConfigurationsMock.mockClear();
  });

  const renderPage = () =>
    render(
      <MemoryRouter>
        <OrganizationConfigurations />
      </MemoryRouter>
    );

  it('fetches configurations with default filters on mount', async () => {
    renderPage();

    await waitFor(() => {
      expect(getConfigurationsMock).toHaveBeenCalledWith({
        type: null,
        environment: null,
        includeInactive: false,
      });
    });

    expect(await screen.findByText(/smtp configuration for production mail delivery/i)).toBeVisible();
    expect(screen.getByText(/Voice navigation rollout flag/i)).toBeVisible();
  });

  it('refetches configurations when type filter changes', async () => {
    renderPage();

    await waitFor(() => expect(getConfigurationsMock).toHaveBeenCalledTimes(1));
    getConfigurationsMock.mockClear();

    const typeSelect = await screen.findByLabelText(/Configuration Type/i);
    await userEvent.click(typeSelect);

    const featureOption = await screen.findByRole('option', { name: /feature/i });
    await userEvent.click(featureOption);

    await waitFor(() => {
      expect(getConfigurationsMock).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'feature',
        })
      );
    });
  });

  it('refetches configurations when environment filter changes', async () => {
    renderPage();

    await waitFor(() => expect(getConfigurationsMock).toHaveBeenCalledTimes(1));
    getConfigurationsMock.mockClear();

    const environmentSelect = await screen.findByLabelText(/Environment/i);
    await userEvent.click(environmentSelect);

    const stagingOption = await screen.findByRole('option', { name: /staging/i });
    await userEvent.click(stagingOption);

    await waitFor(() => {
      expect(getConfigurationsMock).toHaveBeenCalledWith(
        expect.objectContaining({
          environment: 'staging',
        })
      );
    });
  });

  it('shows empty state when no configurations returned', async () => {
    getConfigurationsMock.mockResolvedValueOnce({ total: 0, items: [] });

    renderPage();

    expect(await screen.findByText(/No configurations found/i)).toBeVisible();
  });

  it('renders error message when fetch fails', async () => {
    getConfigurationsMock.mockRejectedValueOnce(new Error('boom'));

    renderPage();

    expect(await screen.findByText(/Failed to load configurations/i)).toBeVisible();
  });
});
