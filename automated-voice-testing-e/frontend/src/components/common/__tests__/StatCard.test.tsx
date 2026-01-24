/**
 * StatCard component tests
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Activity } from 'lucide-react';
import StatCard from '../StatCard';

describe('StatCard', () => {
  const defaultProps = {
    title: 'Total Users',
    value: '1,234',
    icon: <Activity data-testid="stat-icon" />,
    iconColor: 'text-blue-600',
    iconBg: 'bg-blue-100',
  };

  it('renders with required props', () => {
    render(<StatCard {...defaultProps} />);
    expect(screen.getByText('Total Users')).toBeInTheDocument();
    expect(screen.getByText('1,234')).toBeInTheDocument();
    expect(screen.getByTestId('stat-icon')).toBeInTheDocument();
  });

  it('renders with subtitle', () => {
    render(<StatCard {...defaultProps} subtitle="Last 30 days" />);
    expect(screen.getByText('Last 30 days')).toBeInTheDocument();
  });

  it('renders up trend indicator', () => {
    render(
      <StatCard
        {...defaultProps}
        trend={{ value: '12%', direction: 'up', isPositive: true }}
      />
    );
    expect(screen.getByText('12%')).toBeInTheDocument();
  });

  it('renders down trend indicator', () => {
    render(
      <StatCard
        {...defaultProps}
        trend={{ value: '5%', direction: 'down', isPositive: false }}
      />
    );
    expect(screen.getByText('5%')).toBeInTheDocument();
  });

  it('renders flat trend indicator', () => {
    render(
      <StatCard
        {...defaultProps}
        trend={{ value: '0%', direction: 'flat', isPositive: true }}
      />
    );
    expect(screen.getByText('0%')).toBeInTheDocument();
  });

  it('applies positive trend color for positive trends', () => {
    const { container } = render(
      <StatCard
        {...defaultProps}
        trend={{ value: '10%', direction: 'up', isPositive: true }}
      />
    );
    // Check for green color class
    expect(container.querySelector('.text-green-600')).toBeInTheDocument();
  });

  it('applies negative trend color for negative trends', () => {
    const { container } = render(
      <StatCard
        {...defaultProps}
        trend={{ value: '8%', direction: 'down', isPositive: false }}
      />
    );
    // Check for red color class
    expect(container.querySelector('.text-red-600')).toBeInTheDocument();
  });

  it('renders as button when onClick is provided', () => {
    const onClick = vi.fn();
    render(<StatCard {...defaultProps} onClick={onClick} />);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('renders as div when onClick is not provided', () => {
    render(<StatCard {...defaultProps} />);
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });

  it('calls onClick when clicked', async () => {
    const user = userEvent.setup();
    const onClick = vi.fn();
    render(<StatCard {...defaultProps} onClick={onClick} />);

    await user.click(screen.getByRole('button'));
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('applies custom className', () => {
    const { container } = render(
      <StatCard {...defaultProps} className="custom-stat" />
    );
    expect(container.querySelector('.custom-stat')).toBeInTheDocument();
  });

  it('applies icon colors correctly', () => {
    const { container } = render(
      <StatCard
        {...defaultProps}
        iconColor="text-green-600"
        iconBg="bg-green-100"
      />
    );
    expect(container.querySelector('.bg-green-100')).toBeInTheDocument();
    expect(container.querySelector('.text-green-600')).toBeInTheDocument();
  });
});
