/**
 * LoadingSpinner component tests
 */

import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import LoadingSpinner from '../LoadingSpinner';

describe('LoadingSpinner', () => {
  it('renders with default props', () => {
    render(<LoadingSpinner />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('displays the message when provided', () => {
    render(<LoadingSpinner message="Loading data..." />);
    // Message appears in both visible text and sr-only
    expect(screen.getAllByText('Loading data...')).toHaveLength(2);
  });

  it('renders card variant by default', () => {
    const { container } = render(<LoadingSpinner message="Loading..." />);
    expect(container.querySelector('.rounded-xl')).toBeInTheDocument();
  });

  it('renders page variant with full-screen styling', () => {
    const { container } = render(
      <LoadingSpinner message="Loading..." variant="page" />
    );
    expect(container.querySelector('.min-h-screen')).toBeInTheDocument();
  });

  it('renders inline variant', () => {
    const { container } = render(
      <LoadingSpinner message="Loading..." variant="inline" />
    );
    expect(container.querySelector('.inline-flex')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <LoadingSpinner className="custom-class" />
    );
    expect(container.querySelector('.custom-class')).toBeInTheDocument();
  });

  it('includes accessible sr-only text', () => {
    render(<LoadingSpinner message="Loading items" />);
    expect(screen.getByText('Loading items', { selector: '.sr-only' })).toBeInTheDocument();
  });

  it('shows default sr-only text when no message', () => {
    render(<LoadingSpinner />);
    expect(screen.getByText('Loading...', { selector: '.sr-only' })).toBeInTheDocument();
  });
});
