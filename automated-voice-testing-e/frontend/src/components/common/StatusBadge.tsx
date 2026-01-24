/**
 * StatusBadge Component (TASK-139)
 *
 * Real-time status indicator with color coding:
 * - Pending: Default gray
 * - Running: Primary blue with pulsing animation
 * - Passed: Success green
 * - Failed: Error red
 * - Needs Review: Warning orange
 *
 * Features:
 * - Material-UI Chip component
 * - Color-coded status indicators
 * - Pulsing animation for running status
 * - TypeScript type safety
 */

import React from 'react';

/**
 * Test execution status type
 */
export type TestStatus = 'pending' | 'running' | 'passed' | 'failed' | 'needs_review';

/**
 * Props interface for StatusBadge component
 */
interface StatusBadgeProps {
  /**
   * Test execution status
   */
  status: TestStatus;

  /**
   * Optional label override (defaults to status)
   */
  label?: string;

  /**
   * Optional size variant
   */
  size?: 'small' | 'medium';
}

/**
 * Get badge classes for status
 *
 * Maps test execution status to Tailwind badge classes.
 *
 * @param status - Test execution status
 * @returns Badge CSS classes
 */
const getStatusClasses = (status: TestStatus): string => {
  switch (status) {
    case 'pending':
      return 'badge bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)]';
    case 'running':
      return 'badge badge-info animate-pulse';
    case 'passed':
      return 'badge badge-success';
    case 'failed':
      return 'badge badge-danger';
    case 'needs_review':
      return 'badge badge-warning';
    default:
      return 'badge bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)]';
  }
};

/**
 * Get display label for status
 *
 * Formats status string for display.
 *
 * @param status - Test execution status
 * @returns Formatted label
 */
const getStatusLabel = (status: TestStatus): string => {
  switch (status) {
    case 'pending':
      return 'Pending';
    case 'running':
      return 'Running';
    case 'passed':
      return 'Passed';
    case 'failed':
      return 'Failed';
    case 'needs_review':
      return 'Needs Review';
    default:
      return status;
  }
};

/**
 * StatusBadge component
 *
 * Displays test execution status with color coding and animation.
 * Running status shows pulsing animation for visual feedback.
 *
 * @param props - Component props
 * @returns Status badge component
 *
 * @example
 * ```tsx
 * <StatusBadge status="running" />
 * <StatusBadge status="passed" size="small" />
 * <StatusBadge status="failed" label="Test Failed" />
 * ```
 */
const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  label,
  size = 'small',
}) => {
  const badgeClasses = getStatusClasses(status);
  const displayLabel = label || getStatusLabel(status);
  const sizeClasses = size === 'small' ? 'text-xs px-2 py-0.5' : 'text-sm px-3 py-1';

  return (
    <span
      className={`${badgeClasses} ${sizeClasses}`}
      role="status"
      aria-label={`Status: ${displayLabel}`}
    >
      {displayLabel}
    </span>
  );
};

export default StatusBadge;
