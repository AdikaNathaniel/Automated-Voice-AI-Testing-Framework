/**
 * ConfigurationEditor page tests.
 *
 * Verifies loading existing configuration details, JSON validation behaviour,
 * and save interactions.
 */

import React from 'react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import ConfigurationEditor from '../Configurations/ConfigurationEditor';

const getConfigurationMock = vi.fn(() =>
  Promise.resolve({
    id: 'config-1',
    configKey: 'smtp.settings',
    description: 'SMTP configuration',
    isActive: true,
    configData: {
      host: 'smtp.example.com',
      port: 587,
    },
    updatedAt: '2024-04-10T12:00:00Z',
  })
);

const updateConfigurationMock = vi.fn(() =>
  Promise.resolve({
    id: 'config-1',
    configKey: 'smtp.settings',
    description: 'SMTP configuration',
    isActive: true,
    configData: {
      host: 'smtp.mail.local',
      port: 2525,
      use_tls: true,
    },
    updatedAt: '2024-04-11T08:30:00Z',
  })
);

vi.mock('../../services/configuration.service', () => ({
  getConfiguration: (...args: unknown[]) => getConfigurationMock(...args),
  updateConfiguration: (...args: unknown[]) => updateConfigurationMock(...args),
}));

vi.mock('@monaco-editor/react', () => ({
  __esModule: true,
  default: ({ value, onChange }: { value: string; onChange: (value: string) => void }) => (
    <textarea
      data-testid="monaco-editor"
      value={value}
      onChange={(event) => onChange(event.target.value)}
    />
  ),
}));

describe('ConfigurationEditor page', () => {
  beforeEach(() => {
    getConfigurationMock.mockClear();
    updateConfigurationMock.mockClear();
  });

  const renderPage = (configId = 'config-1') =>
    render(
      <MemoryRouter initialEntries={[`/configurations/${configId}`]}>
        <Routes>
          <Route path="/configurations/:configId" element={<ConfigurationEditor />} />
        </Routes>
      </MemoryRouter>
    );

  it('loads configuration detail and populates editor', async () => {
    renderPage();

    await waitFor(() => {
      expect(getConfigurationMock).toHaveBeenCalledWith('config-1');
    });

    expect(await screen.findByDisplayValue('smtp.settings')).toBeVisible();
    const editor = screen.getByTestId('monaco-editor') as HTMLTextAreaElement;
    expect(editor.value).toContain('smtp.example.com');
  });

  it('shows validation error and disables save for invalid JSON', async () => {
    renderPage();
    await waitFor(() => expect(getConfigurationMock).toHaveBeenCalled());

    const editor = (await screen.findByTestId('monaco-editor')) as HTMLTextAreaElement;
    await userEvent.clear(editor);
    fireEvent.change(editor, { target: { value: '{ invalid json' } });

    expect(await screen.findByText(/Invalid JSON/)).toBeVisible();
    expect(screen.getByRole('button', { name: /Save Changes/i })).toBeDisabled();
  });

  it('submits parsed JSON when save is clicked', async () => {
    renderPage();
    await waitFor(() => expect(getConfigurationMock).toHaveBeenCalled());

    const editor = (await screen.findByTestId('monaco-editor')) as HTMLTextAreaElement;
    await userEvent.clear(editor);
    fireEvent.change(editor, {
      target: { value: JSON.stringify({ host: 'smtp.mail.local', port: 2525, use_tls: true }) },
    });

    const saveButton = screen.getByRole('button', { name: /Save Changes/i });
    expect(saveButton).toBeEnabled();
    await userEvent.click(saveButton);

    await waitFor(() => {
      expect(updateConfigurationMock).toHaveBeenCalledWith(
        'config-1',
        expect.objectContaining({
          configData: { host: 'smtp.mail.local', port: 2525, use_tls: true },
        })
      );
    });
  });
});
