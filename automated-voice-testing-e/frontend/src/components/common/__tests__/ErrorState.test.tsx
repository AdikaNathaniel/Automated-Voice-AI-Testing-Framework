/**
 * ErrorState component tests
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ErrorState from '../ErrorState';

describe('ErrorState', () => {
  it('renders with message', () => {
    render(<ErrorState message="Failed to load data" />);
    expect(screen.getByText('Failed to load data')).toBeInTheDocument();
  });

  it('renders with custom title', () => {
    render(<ErrorState title="Connection Error" message="Unable to connect" />);
    expect(screen.getByText('Connection Error')).toBeInTheDocument();
    expect(screen.getByText('Unable to connect')).toBeInTheDocument();
  });

  it('renders default title when not provided', () => {
    render(<ErrorState message="Error occurred" />);
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
  });

  it('shows retry button when onRetry is provided', () => {
    const onRetry = vi.fn();
    render(<ErrorState message="Error" onRetry={onRetry} />);
    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
  });

  it('calls onRetry when retry button is clicked', async () => {
    const user = userEvent.setup();
    const onRetry = vi.fn();
    render(<ErrorState message="Error" onRetry={onRetry} />);

    await user.click(screen.getByRole('button', { name: /retry/i }));
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it('disables retry button when retryLoading is true', () => {
    const onRetry = vi.fn();
    render(<ErrorState message="Error" onRetry={onRetry} retryLoading />);
    expect(screen.getByRole('button', { name: /retry/i })).toBeDisabled();
  });

  it('renders alert variant', () => {
    const { container } = render(
      <ErrorState message="Alert message" variant="alert" />
    );
    expect(container.querySelector('.border-l-4')).toBeInTheDocument();
  });

  it('renders page variant', () => {
    const { container } = render(
      <ErrorState message="Page error" variant="page" />
    );
    expect(container.querySelector('.min-h-screen')).toBeInTheDocument();
  });

  it('renders card variant by default', () => {
    const { container } = render(<ErrorState message="Card error" />);
    expect(container.querySelector('.rounded-xl')).toBeInTheDocument();
  });

  it('has alert role for accessibility', () => {
    render(<ErrorState message="Error" />);
    expect(screen.getByRole('alert')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <ErrorState message="Error" className="custom-error" />
    );
    expect(container.querySelector('.custom-error')).toBeInTheDocument();
  });
});
