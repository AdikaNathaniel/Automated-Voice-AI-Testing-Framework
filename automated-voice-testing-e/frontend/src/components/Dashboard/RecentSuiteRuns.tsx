/**
 * RecentSuiteRuns Widget (TASK-133)
 *
 * Dashboard widget displaying recent suite runs:
 * - Shows last 10 suite runs
 * - Click to navigate to suite run details
 * - Status badges for each suite run
 * - Empty state handling
 *
 * Features:
 * - Material-UI Card and List components
 * - Click handlers for navigation
 * - Mock data for demonstration
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * Suite run status type
 */
type SuiteRunStatus = 'pending' | 'running' | 'passed' | 'failed' | 'needs_review';

/**
 * Suite run interface
 */
interface SuiteRun {
  /**
   * Unique suite run ID
   */
  id: number;

  /**
   * Suite run name
   */
  name: string;

  /**
   * Suite run status
   */
  status: SuiteRunStatus;

  /**
   * Timestamp of suite run
   */
  timestamp: string;

  /**
   * Number of tests passed
   */
  passed?: number;

  /**
   * Total number of tests
   */
  total?: number;
}

/**
 * Get status badge class based on suite run status
 */
const getStatusBadgeClass = (status: SuiteRunStatus): string => {
  switch (status) {
    case 'passed':
      return 'badge badge-success';
    case 'failed':
      return 'badge badge-danger';
    case 'running':
      return 'badge badge-info';
    case 'needs_review':
      return 'badge badge-warning';
    default:
      return 'badge bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)]';
  }
};

/**
 * Mock suite runs data
 * TODO: Replace with API call
 */
const mockSuiteRuns: SuiteRun[] = [
  {
    id: 1,
    name: 'Voice AI Basic Flow Test',
    status: 'passed',
    timestamp: '2 hours ago',
    passed: 15,
    total: 15,
  },
  {
    id: 2,
    name: 'Multi-Language Support Test',
    status: 'failed',
    timestamp: '4 hours ago',
    passed: 8,
    total: 12,
  },
  {
    id: 3,
    name: 'Edge Case Scenarios',
    status: 'running',
    timestamp: '5 hours ago',
    passed: 5,
    total: 10,
  },
];

/**
 * RecentSuiteRuns widget component
 *
 * Displays a list of recent suite runs with navigation to details.
 * Shows status, name, and pass/fail counts for each suite run.
 *
 * @returns Recent suite runs widget
 *
 * @example
 * ```tsx
 * <RecentSuiteRuns />
 * ```
 */
const RecentSuiteRuns: React.FC = () => {
  const navigate = useNavigate();

  /**
   * Handle click on suite run to navigate to details
   */
  const handleSuiteRunClick = (suiteRunId: number) => {
    navigate(`/suite-runs/${suiteRunId}`);
  };

  return (
    <div className="card h-full">
      <h2 className="card-title mb-4">
        Recent Suite Runs
      </h2>

      {mockSuiteRuns.length === 0 ? (
        // Empty state
        <div className="py-8 text-center">
          <p className="text-sm text-[var(--color-content-secondary)]">
            No recent suite runs
          </p>
        </div>
      ) : (
        // Suite runs list
        <div className="flex flex-col">
          {mockSuiteRuns.map((suiteRun, index) => (
            <React.Fragment key={suiteRun.id}>
              {index > 0 && <div className="border-t border-[var(--color-border-subtle)]"></div>}
              <button
                onClick={() => handleSuiteRunClick(suiteRun.id)}
                className="text-left py-3 hover:bg-[var(--color-interactive-hover)] transition-colors"
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-base font-medium text-[var(--color-content-primary)]">{suiteRun.name}</span>
                  <span className={getStatusBadgeClass(suiteRun.status)}>
                    {suiteRun.status}
                  </span>
                </div>
                <div className="flex gap-4 mt-1">
                  <span className="text-xs text-[var(--color-content-muted)]">
                    {suiteRun.timestamp}
                  </span>
                  {suiteRun.passed !== undefined && suiteRun.total !== undefined && (
                    <span className="text-xs text-[var(--color-content-muted)]">
                      {suiteRun.passed}/{suiteRun.total} passed
                    </span>
                  )}
                </div>
              </button>
            </React.Fragment>
          ))}
        </div>
      )}
    </div>
  );
};

export default RecentSuiteRuns;
