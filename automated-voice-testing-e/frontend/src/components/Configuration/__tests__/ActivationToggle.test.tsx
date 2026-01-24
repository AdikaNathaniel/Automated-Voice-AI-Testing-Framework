/**
 * ActivationToggle component tests.
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import ActivationToggle from '../ActivationToggle';

describe('ActivationToggle', () => {
  it('opens confirmation dialog and calls onToggle for activation', async () => {
    const onToggle = vi.fn(() => Promise.resolve());
    render(<ActivationToggle isActive={false} onToggle={onToggle} configurationName="SMTP" />);

    await userEvent.click(screen.getByTestId('activation-toggle-button'));
    expect(await screen.findByText(/Activate configuration/i)).toBeVisible();

    await userEvent.click(screen.getByTestId('activation-confirm-button'));

    await waitFor(() => {
      expect(onToggle).toHaveBeenCalledWith(true);
    });
  });

  it('shows error when toggle fails', async () => {
    const onToggle = vi.fn(() => Promise.reject(new Error('boom')));
    render(<ActivationToggle isActive onToggle={onToggle} />);

    await userEvent.click(screen.getByTestId('activation-toggle-button'));
    await userEvent.click(screen.getByTestId('activation-confirm-button'));

    expect(await screen.findByText(/Failed to update configuration status/i)).toBeVisible();
  });
});
