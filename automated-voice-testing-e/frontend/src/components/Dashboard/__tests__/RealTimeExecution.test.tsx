import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import RealTimeExecution, { RealTimeExecutionProps } from '../RealTimeExecution';

const baseProps: RealTimeExecutionProps = {
  queue: {
    pendingCount: 12,
    claimedCount: 3,
    queueDepth: {
      total: 45,
      queued: 12,
      processing: 6,
      completed: 24,
      failed: 3,
      averagePriority: 7.2,
      oldestQueuedSeconds: 85,
    },
    throughput: {
      testsPerMinute: 3.4,
      sampleSize: 51,
      windowMinutes: 15,
      lastUpdated: '2024-01-01T12:00:00Z',
    },
  },
  runs: [
    {
      id: 'run-1',
      suiteId: 'suite-1',
      suiteName: 'Smoke Suite',
      status: 'running',
      progressPct: 64.3,
      totalTests: 50,
      passedTests: 30,
      failedTests: 5,
      skippedTests: 3,
      startedAt: '2024-01-01T11:30:00Z',
      completedAt: null,
    },
  ],
  loading: false,
  runCounts: {
    pending: 2,
    running: 1,
    completed: 5,
    failed: 0,
    cancelled: 0,
  },
  issueSummary: {
    openDefects: 4,
    criticalDefects: 1,
    edgeCasesActive: 3,
    edgeCasesNew: 1,
  },
};

const renderComponent = (props: Partial<RealTimeExecutionProps> = {}) =>
  render(
    <MemoryRouter>
      <RealTimeExecution {...baseProps} {...props} />
    </MemoryRouter>
  );

describe('RealTimeExecution component', () => {
  it('renders queue snapshot, throughput, and active runs list', () => {
    renderComponent();

    expect(screen.getByRole('heading', { name: /Real-Time Test Execution/i })).toBeInTheDocument();

    expect(screen.getByTestId('pending-count').textContent).toBe('12');
    expect(screen.getByTestId('claimed-count').textContent).toBe('3');
    expect(screen.getByText(/12 queued/i)).toBeInTheDocument();
    expect(screen.getByText(/3.4 tests\/min/i)).toBeInTheDocument();

    expect(screen.getByText(/Smoke Suite/i)).toBeInTheDocument();
    expect(screen.getByText(/64.3% complete/i)).toBeInTheDocument();
    expect(screen.getByTestId('run-status-running').textContent).toBe('1');
    expect(screen.getByTestId('edge-cases-active').textContent).toBe('3');
  });

  it('shows fallback messaging when no active runs exist', () => {
    renderComponent({ runs: [] });

    expect(screen.getByText(/No active runs right now/i)).toBeInTheDocument();
  });

  it('renders loading state while data is fetching', () => {
    renderComponent({ loading: true, runs: [] });

    expect(screen.getByTestId('real-time-execution-loading')).toBeInTheDocument();
  });

  it('shows API error states when provided', () => {
    renderComponent({ error: 'Unable to load' });

    expect(screen.getByText(/Unable to load/i)).toBeInTheDocument();
  });
});
