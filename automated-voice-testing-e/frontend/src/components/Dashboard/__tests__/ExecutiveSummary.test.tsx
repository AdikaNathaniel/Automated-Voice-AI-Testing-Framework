import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ExecutiveSummary, { ExecutiveSummaryProps } from '../ExecutiveSummary';

const baseProps: ExecutiveSummaryProps = {
  data: {
    testsExecuted: 1280,
    systemHealthPct: 98.7,
    issuesDetected: 12,
    avgResponseTimeMs: 1180.5,
    updatedAt: '2024-01-01T12:00:00Z',
  },
  loading: false,
  error: null,
};

describe('ExecutiveSummary component', () => {
  it('renders KPI cards with formatted values and last updated timestamp', () => {
    render(<ExecutiveSummary {...baseProps} />);

    expect(screen.getByRole('heading', { name: /Executive Summary/i })).toBeInTheDocument();
    expect(screen.getByText(/Tests Executed/i).nextSibling?.textContent).toContain('1,280');
    expect(screen.getByText(/System Health/i).nextSibling?.textContent).toContain('98.7%');
    expect(screen.getByText(/Issues Detected/i).nextSibling?.textContent).toContain('12');
    expect(screen.getByText(/Avg Response Time/i).nextSibling?.textContent).toContain('1.18s');
    expect(screen.getByText(/Last updated/i)).toBeInTheDocument();
  });

  it('updates displayed values when new data is provided', () => {
    const { rerender } = render(<ExecutiveSummary {...baseProps} />);

    expect(screen.getByText(/Issues Detected/i).nextSibling?.textContent).toContain('12');

    const updatedProps: ExecutiveSummaryProps = {
      ...baseProps,
      data: {
        ...baseProps.data,
        issuesDetected: 4,
        testsExecuted: 2048,
      },
    };

    rerender(<ExecutiveSummary {...updatedProps} />);

    expect(screen.getByText(/Issues Detected/i).nextSibling?.textContent).toContain('4');
    expect(screen.getByText(/Tests Executed/i).nextSibling?.textContent).toContain('2,048');
  });

  it('renders loading and error states with retry support', () => {
    const onRetry = vi.fn();

    const { rerender } = render(
      <ExecutiveSummary {...baseProps} loading error={null} onRetry={onRetry} />
    );

    expect(screen.getByTestId('executive-summary-loading')).toBeInTheDocument();

    rerender(
      <ExecutiveSummary
        {...baseProps}
        loading={false}
        error="Unable to load KPIs"
        onRetry={onRetry}
      />
    );

    expect(screen.getByText(/Unable to load KPIs/i)).toBeInTheDocument();
    const retryButton = screen.getByRole('button', { name: /Retry/i });
    fireEvent.click(retryButton);
    expect(onRetry).toHaveBeenCalledTimes(1);
  });
});
