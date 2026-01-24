import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import CICDStatus, { CICDStatusProps } from '../CICDStatus';

const baseProps: CICDStatusProps = {
  pipelines: [
    {
      id: 'pipe-1',
      name: 'Nightly Regression',
      status: 'success',
      lastRunAt: '2024-01-01T05:00:00Z',
    },
    {
      id: 'pipe-2',
      name: 'Smoke Tests',
      status: 'running',
      lastRunAt: '2024-01-01T11:50:00Z',
    },
  ],
  incidents: 1,
  loading: false,
  error: null,
};

describe('CICDStatus component', () => {
  it('renders pipelines with status chips and last run information', () => {
    render(<CICDStatus {...baseProps} />);

    expect(screen.getByRole('heading', { name: /CI\/CD Integration Status/i })).toBeInTheDocument();
    expect(screen.getByText(/Active incidents: 1/i)).toBeInTheDocument();

    const nightlyItem = screen.getByTestId('pipeline-item-pipe-1');
    expect(nightlyItem).toHaveTextContent('Nightly Regression');
    expect(nightlyItem).toHaveTextContent('Last run 1/1/2024, 5:00:00 AM');
    expect(screen.getByTestId('pipeline-status-pipe-1')).toHaveTextContent(/success/i);

    const smokeItem = screen.getByTestId('pipeline-item-pipe-2');
    expect(smokeItem).toHaveTextContent(/Smoke Tests/);
    expect(screen.getByTestId('pipeline-status-pipe-2')).toHaveTextContent(/running/i);
  });

  it('shows informative message when no pipelines are configured', () => {
    render(<CICDStatus {...baseProps} pipelines={[]} incidents={0} />);

    expect(
      screen.getByText(/CI\/CD pipeline data is not available yet/i)
    ).toBeInTheDocument();
  });

  it('renders loading spinner and error state with retry support', () => {
    const onRetry = vi.fn();
    const { rerender } = render(<CICDStatus {...baseProps} loading error={null} onRetry={onRetry} />);

    expect(screen.getByTestId('cicd-status-loading')).toBeInTheDocument();

    rerender(
      <CICDStatus
        {...baseProps}
        loading={false}
        error="Unable to load CI/CD status"
        onRetry={onRetry}
      />
    );

    expect(screen.getByText(/Unable to load CI\/CD status/i)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /Retry/i }));
    expect(onRetry).toHaveBeenCalledTimes(1);
  });
});
