/**
 * EmptyState component tests
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Search } from 'lucide-react';
import EmptyState from '../EmptyState';

describe('EmptyState', () => {
  it('renders with title', () => {
    render(<EmptyState title="No Results" />);
    expect(screen.getByText('No Results')).toBeInTheDocument();
  });

  it('renders with description', () => {
    render(
      <EmptyState
        title="No Items"
        description="There are no items to display"
      />
    );
    expect(screen.getByText('There are no items to display')).toBeInTheDocument();
  });

  it('renders action button when provided', () => {
    const onClick = vi.fn();
    render(
      <EmptyState
        title="No Data"
        action={{ label: 'Add Item', onClick }}
      />
    );
    expect(screen.getByRole('button', { name: 'Add Item' })).toBeInTheDocument();
  });

  it('calls action onClick when button is clicked', async () => {
    const user = userEvent.setup();
    const onClick = vi.fn();
    render(
      <EmptyState
        title="No Data"
        action={{ label: 'Create New', onClick }}
      />
    );

    await user.click(screen.getByRole('button', { name: 'Create New' }));
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('renders with preset icon names', () => {
    const { container } = render(
      <EmptyState title="No Search Results" icon="search" />
    );
    // Icon should be rendered (SVG element)
    expect(container.querySelector('svg')).toBeInTheDocument();
  });

  it('renders with custom icon element', () => {
    render(
      <EmptyState
        title="Custom Icon"
        icon={<Search data-testid="custom-icon" className="w-16 h-16" />}
      />
    );
    expect(screen.getByTestId('custom-icon')).toBeInTheDocument();
  });

  it('renders card variant by default', () => {
    const { container } = render(<EmptyState title="Empty" />);
    expect(container.querySelector('.rounded-xl')).toBeInTheDocument();
  });

  it('renders inline variant', () => {
    const { container } = render(
      <EmptyState title="Empty" variant="inline" />
    );
    expect(container.querySelector('.py-8')).toBeInTheDocument();
    expect(container.querySelector('.rounded-xl')).not.toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <EmptyState title="Empty" className="custom-empty" />
    );
    expect(container.querySelector('.custom-empty')).toBeInTheDocument();
  });

  it('renders all preset icon types without error', () => {
    const icons = ['inbox', 'file', 'search', 'folder', 'users', 'alert', 'database', 'calendar'] as const;

    icons.forEach((icon) => {
      const { container, unmount } = render(
        <EmptyState title={`Icon: ${icon}`} icon={icon} />
      );
      expect(container.querySelector('svg')).toBeInTheDocument();
      unmount();
    });
  });
});
