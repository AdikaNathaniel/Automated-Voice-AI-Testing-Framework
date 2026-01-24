import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import type {
  RealTimeMetrics,
  RealTimeRun,
  RealTimeRunCounts,
  RealTimeIssueSummary,
} from '../../types/dashboard';

export type RealTimeExecutionProps = {
  queue: {
    pendingCount: number;
    claimedCount: number;
    queueDepth: RealTimeMetrics['queueDepth'];
    throughput: RealTimeMetrics['throughput'];
  };
  runs: RealTimeRun[];
  runCounts: RealTimeRunCounts;
  issueSummary: RealTimeIssueSummary;
  loading?: boolean;
  error?: string | null;
};

const RealTimeExecution: React.FC<RealTimeExecutionProps> = ({
  queue,
  runs,
  runCounts,
  issueSummary,
  loading = false,
  error = null,
}) => {
  if (loading) {
    return (
      <div className="card min-h-[240px] flex items-center justify-center">
        <div className="spinner" data-testid="real-time-execution-loading"></div>
      </div>
    );
  }

  return (
    <div className="card h-full">
      <div className="flex flex-col gap-6">
        <h2 className="text-xl font-bold text-[var(--color-content-primary)]">Real-Time Test Execution</h2>

        {error && (
          <div className="bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] rounded-lg p-4">
            <p className="text-[var(--color-status-danger)]">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <ValidationQueueCard pending={queue.pendingCount} claimed={queue.claimedCount} />
          <QueueSnapshotCard depth={queue.queueDepth} throughput={queue.throughput} />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <RunStatusCard counts={runCounts} />
          <IssueSummaryCard summary={issueSummary} />
        </div>

        <div className="flex flex-col gap-4">
          <h3 className="text-lg font-semibold text-[var(--color-content-primary)]">Active Runs</h3>
          {runs.length > 0 ? (
            <div className="flex flex-col gap-4">
              {runs.map((run) => (
                <RunCard run={run} key={run.id} />
              ))}
            </div>
          ) : (
            <div className="bg-[var(--color-status-info-bg)] border border-[var(--color-status-info)] rounded-lg p-4">
              <p className="text-[var(--color-status-info)]">
                No active runs right now. Start a new execution to see progress updates here.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

type ValidationQueueCardProps = {
  pending: number;
  claimed: number;
};

const ValidationQueueCard: React.FC<ValidationQueueCardProps> = ({ pending, claimed }) => (
  <div className="border border-[var(--color-border-default)] rounded-lg p-4">
    <div className="flex flex-col gap-4">
      <h4 className="text-lg font-semibold text-[var(--color-content-primary)]">Validation Queue</h4>
      <div className="flex gap-8">
        <div>
          <div className="text-3xl font-bold text-[var(--color-content-primary)]" data-testid="pending-count">
            {pending}
          </div>
          <div className="text-sm text-[var(--color-content-muted)]">Pending validations</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-[var(--color-content-primary)]" data-testid="claimed-count">
            {claimed}
          </div>
          <div className="text-sm text-[var(--color-content-muted)]">Your claimed</div>
        </div>
      </div>
      <RouterLink to="/validation" className="btn btn-primary self-start">
        Open Validation Interface
      </RouterLink>
    </div>
  </div>
);

type QueueSnapshotCardProps = {
  depth: RealTimeMetrics['queueDepth'];
  throughput: RealTimeMetrics['throughput'];
};

const QueueSnapshotCard: React.FC<QueueSnapshotCardProps> = ({ depth, throughput }) => (
  <div className="border border-[var(--color-border-default)] rounded-lg p-4">
    <div className="flex flex-col gap-2">
      <h4 className="text-lg font-semibold text-[var(--color-content-primary)]">Queue Snapshot</h4>
      <p className="text-sm text-[var(--color-content-secondary)]">
        {depth.queued} queued · {depth.processing} processing · {depth.failed} failed
      </p>
      <p className="text-xs text-[var(--color-content-muted)]">
        Priority avg {depth.averagePriority.toFixed(1)}
      </p>
      <hr className="my-2 border-[var(--color-border-default)]" />
      <h4 className="text-lg font-semibold text-[var(--color-content-primary)]">Throughput</h4>
      <p className="text-sm text-[var(--color-content-secondary)]">
        {throughput.testsPerMinute.toFixed(1)} tests/min · {throughput.sampleSize} samples (
        {throughput.windowMinutes}m window)
      </p>
    </div>
  </div>
);

type RunCardProps = {
  run: RealTimeRun;
};

const RunCard: React.FC<RunCardProps> = ({ run }) => (
  <div className="border border-[var(--color-border-default)] rounded-lg p-4">
    <div className="flex flex-col gap-2">
      <div className="flex justify-between items-center">
        <h4 className="text-lg font-semibold text-[var(--color-content-primary)]">
          {run.suiteName ?? 'Unnamed Suite'}
        </h4>
        <span
          className={`badge ${
            run.status === 'running' ? 'badge-success' : 'badge'
          } capitalize`}
        >
          {run.status}
        </span>
      </div>
      <p className="text-sm text-[var(--color-content-secondary)]">
        {run.passedTests} passed • {run.failedTests} failed • {run.skippedTests} skipped
      </p>
      <div>
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${Math.min(100, Math.max(0, run.progressPct))}%` }}
          ></div>
        </div>
        <p className="text-xs text-[var(--color-content-muted)] mt-1">
          {run.progressPct.toFixed(1)}% complete · {run.totalTests} total tests
        </p>
      </div>
    </div>
  </div>
);

type RunStatusCardProps = {
  counts: RealTimeRunCounts;
};

const RunStatusCard: React.FC<RunStatusCardProps> = ({ counts }) => (
  <div className="border border-[var(--color-border-default)] rounded-lg p-4">
    <div className="flex flex-col gap-2">
      <h4 className="text-lg font-semibold text-[var(--color-content-primary)]">Run Status</h4>
      <div className="flex flex-wrap gap-4">
        {Object.entries(counts).map(([status, value]) => (
          <div key={status} className="min-w-[90px]">
            <div className="text-2xl font-bold text-[var(--color-content-primary)]" data-testid={`run-status-${status}`}>
              {value}
            </div>
            <div className="text-xs text-[var(--color-content-muted)] capitalize">
              {status.replace('_', ' ')}
            </div>
          </div>
        ))}
      </div>
    </div>
  </div>
);

type IssueSummaryCardProps = {
  summary: RealTimeIssueSummary;
};

const IssueSummaryCard: React.FC<IssueSummaryCardProps> = ({ summary }) => (
  <div className="border border-[var(--color-border-default)] rounded-lg p-4">
    <div className="flex flex-col gap-2">
      <h4 className="text-lg font-semibold text-[var(--color-content-primary)]">Issues & Edge Cases</h4>
      <div className="flex flex-wrap gap-4">
        <IssueMetric label="Open defects" value={summary.openDefects} dataTestId="open-defects" />
        <IssueMetric
          label="Critical defects"
          value={summary.criticalDefects}
          dataTestId="critical-defects"
        />
        <IssueMetric
          label="Active edge cases"
          value={summary.edgeCasesActive}
          dataTestId="edge-cases-active"
        />
        <IssueMetric
          label="New edge cases"
          value={summary.edgeCasesNew}
          dataTestId="edge-cases-new"
        />
      </div>
    </div>
  </div>
);

type IssueMetricProps = {
  label: string;
  value: number;
  dataTestId: string;
};

const IssueMetric: React.FC<IssueMetricProps> = ({ label, value, dataTestId }) => (
  <div className="min-w-[120px]">
    <div className="text-2xl font-bold text-[var(--color-content-primary)]" data-testid={dataTestId}>
      {value}
    </div>
    <div className="text-xs text-[var(--color-content-muted)]">{label}</div>
  </div>
);

export default RealTimeExecution;
