/**
 * ExecutionTable Component (TASK-136)
 *
 * Table displaying test execution results with:
 * - Columns: Test name, language, status, confidence, time
 * - Sortable columns
 * - Filterable data
 * - Real-time updates via WebSocket (ready for integration)
 *
 * Features:
 * - Material-UI Table components
 * - Sort functionality with TableSortLabel
 * - Status indicators with color coding
 * - Responsive design
 */

import React, { useState } from 'react';
import { ChevronUp, ChevronDown } from 'lucide-react';

/**
 * Test execution status type
 */
type ExecutionStatus = 'passed' | 'failed' | 'running' | 'pending';

/**
 * Sort order type
 */
type SortOrder = 'asc' | 'desc';

/**
 * Sort field type
 */
type SortField = 'name' | 'language' | 'status' | 'confidence' | 'duration';

/**
 * Test execution interface
 */
export interface TestExecution {
  /**
   * Execution ID
   */
  id: number;

  /**
   * Test case name
   */
  name: string;

  /**
   * Language variant
   */
  language: string;

  /**
   * Execution status
   */
  status: ExecutionStatus;

  /**
   * Confidence score (0-100)
   */
  confidence?: number;

  /**
   * Execution duration in seconds
   */
  duration?: number;
}

/**
 * Props interface for ExecutionTable component
 */
interface ExecutionTableProps {
  /**
   * Array of test executions to display
   */
  executions: TestExecution[];
}

/**
 * Get status badge classes based on execution status
 */
const getStatusClass = (status: ExecutionStatus): string => {
  switch (status) {
    case 'passed':
      return 'badge-success';
    case 'failed':
      return 'badge-error';
    case 'running':
      return 'badge-info';
    case 'pending':
      return 'badge-warning';
    default:
      return 'badge';
  }
};

/**
 * ExecutionTable component
 *
 * Displays test executions in a sortable table format.
 * Supports sorting by name, language, status, confidence, and duration.
 * Ready for real-time updates via props.
 *
 * @param props - Component props
 * @returns Test execution table
 *
 * @example
 * ```tsx
 * <ExecutionTable executions={testExecutions} />
 * ```
 */
const ExecutionTable: React.FC<ExecutionTableProps> = ({ executions }) => {
  // Sorting state
  const [sortField, setSortField] = useState<SortField>('name');
  const [sortOrder, setSortOrder] = useState<SortOrder>('asc');

  /**
   * Handle sort request
   */
  const handleSort = (field: SortField) => {
    const isAsc = sortField === field && sortOrder === 'asc';
    setSortOrder(isAsc ? 'desc' : 'asc');
    setSortField(field);
  };

  /**
   * Sort executions based on current sort field and order
   */
  const sortedExecutions = [...executions].sort((a, b) => {
    let aValue: string | number | undefined;
    let bValue: string | number | undefined;

    switch (sortField) {
      case 'name':
        aValue = a.name;
        bValue = b.name;
        break;
      case 'language':
        aValue = a.language;
        bValue = b.language;
        break;
      case 'status':
        aValue = a.status;
        bValue = b.status;
        break;
      case 'confidence':
        aValue = a.confidence ?? 0;
        bValue = b.confidence ?? 0;
        break;
      case 'duration':
        aValue = a.duration ?? 0;
        bValue = b.duration ?? 0;
        break;
    }

    // Handle undefined values
    if (aValue === undefined && bValue === undefined) return 0;
    if (aValue === undefined) return 1;
    if (bValue === undefined) return -1;

    // Compare values
    if (aValue < bValue) {
      return sortOrder === 'asc' ? -1 : 1;
    }
    if (aValue > bValue) {
      return sortOrder === 'asc' ? 1 : -1;
    }
    return 0;
  });

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-[var(--color-border-default)]">
        <thead className="bg-[var(--color-surface-inset)]">
          <tr>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-[var(--color-content-muted)] uppercase tracking-wider">
              <button
                type="button"
                onClick={() => handleSort('name')}
                className="inline-flex items-center gap-1 hover:text-[var(--color-content-secondary)]"
              >
                Test Name
                {sortField === 'name' && (
                  sortOrder === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
                )}
              </button>
            </th>

            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-[var(--color-content-muted)] uppercase tracking-wider">
              <button
                type="button"
                onClick={() => handleSort('language')}
                className="inline-flex items-center gap-1 hover:text-[var(--color-content-secondary)]"
              >
                Language
                {sortField === 'language' && (
                  sortOrder === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
                )}
              </button>
            </th>

            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-[var(--color-content-muted)] uppercase tracking-wider">
              <button
                type="button"
                onClick={() => handleSort('status')}
                className="inline-flex items-center gap-1 hover:text-[var(--color-content-secondary)]"
              >
                Status
                {sortField === 'status' && (
                  sortOrder === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
                )}
              </button>
            </th>

            <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-[var(--color-content-muted)] uppercase tracking-wider">
              <button
                type="button"
                onClick={() => handleSort('confidence')}
                className="inline-flex items-center gap-1 hover:text-[var(--color-content-secondary)] ml-auto"
              >
                Confidence
                {sortField === 'confidence' && (
                  sortOrder === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
                )}
              </button>
            </th>

            <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-[var(--color-content-muted)] uppercase tracking-wider">
              <button
                type="button"
                onClick={() => handleSort('duration')}
                className="inline-flex items-center gap-1 hover:text-[var(--color-content-secondary)] ml-auto"
              >
                Time
                {sortField === 'duration' && (
                  sortOrder === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
                )}
              </button>
            </th>
          </tr>
        </thead>

        <tbody className="bg-[var(--color-surface-raised)] divide-y divide-[var(--color-border-default)]">
          {sortedExecutions.map((execution) => (
            <tr key={execution.id} className="hover:bg-[var(--color-interactive-hover)] transition-colors">
              <td className="px-6 py-4 whitespace-nowrap text-sm text-[var(--color-content-primary)]">
                {execution.name}
              </td>

              <td className="px-6 py-4 whitespace-nowrap">
                <span className="badge">
                  {execution.language}
                </span>
              </td>

              <td className="px-6 py-4 whitespace-nowrap">
                <span className={getStatusClass(execution.status)}>
                  {execution.status}
                </span>
              </td>

              <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                {execution.confidence !== undefined ? (
                  <span
                    className={
                      execution.confidence >= 80
                        ? 'text-[var(--color-status-success)] font-medium'
                        : execution.confidence >= 60
                        ? 'text-[var(--color-status-warning)] font-medium'
                        : 'text-[var(--color-status-danger)] font-medium'
                    }
                  >
                    {execution.confidence}%
                  </span>
                ) : (
                  <span className="text-[var(--color-content-muted)]">-</span>
                )}
              </td>

              <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-[var(--color-content-primary)]">
                {execution.duration !== undefined ? `${execution.duration}s` : '-'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ExecutionTable;
