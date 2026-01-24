/**
 * ProgressBar Component (TASK-137)
 *
 * Progress indicator for test run execution:
 * - Visual progress bar with percentage
 * - Label and count display
 * - Real-time updates via props
 *
 * Features:
 * - Material-UI LinearProgress component
 * - Percentage calculation
 * - Customizable color variants
 * - Responsive design
 */

import React from 'react';

/**
 * Progress bar color type
 */
type ProgressColor = 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'info';

/**
 * Get color classes for progress bar
 */
const getColorClasses = (color: ProgressColor): string => {
  switch (color) {
    case 'success':
      return 'bg-[var(--color-status-success)]';
    case 'error':
      return 'bg-[var(--color-status-danger)]';
    case 'warning':
      return 'bg-[var(--color-status-warning)]';
    case 'info':
      return 'bg-[var(--color-status-info)]';
    case 'secondary':
      return 'bg-[var(--color-content-muted)]';
    case 'primary':
    default:
      return ''; // Uses gradient from progress-fill class
  }
};

/**
 * Props interface for ProgressBar component
 */
interface ProgressBarProps {
  /**
   * Current value (number of completed items)
   */
  value: number;

  /**
   * Total value (total number of items)
   */
  total: number;

  /**
   * Optional label to display above the progress bar
   */
  label?: string;

  /**
   * Optional color variant for the progress bar
   */
  color?: ProgressColor;

  /**
   * Whether to show the count (e.g., "5 / 10")
   */
  showCount?: boolean;

  /**
   * Whether to show the percentage (e.g., "50%")
   */
  showPercentage?: boolean;
}

/**
 * ProgressBar component
 *
 * Displays a progress bar with optional label, count, and percentage.
 * Updates in real-time as props change.
 *
 * @param props - Component props
 * @returns Progress bar component
 *
 * @example
 * ```tsx
 * <ProgressBar
 *   value={7}
 *   total={10}
 *   label="Test Execution Progress"
 *   showCount
 *   showPercentage
 * />
 * ```
 */
const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  total,
  label,
  color = 'primary',
  showCount = true,
  showPercentage = true,
}) => {
  /**
   * Calculate percentage progress
   */
  const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
  const colorClasses = getColorClasses(color);

  return (
    <div className="w-full">
      {/* Label and Stats Row */}
      {(label || showCount || showPercentage) && (
        <div className="flex justify-between items-center mb-2">
          {/* Label */}
          {label && (
            <p className="text-sm text-[var(--color-content-secondary)]">
              {label}
            </p>
          )}

          {/* Count and Percentage */}
          <div className="flex gap-4 items-center">
            {showCount && (
              <p className="text-sm text-[var(--color-content-secondary)]">
                {value} / {total}
              </p>
            )}

            {showPercentage && (
              <p className={`text-sm font-medium ${percentage === 100 ? 'text-[var(--color-status-success)]' : 'text-[var(--color-content-primary)]'}`}>
                {percentage}%
              </p>
            )}
          </div>
        </div>
      )}

      {/* Progress Bar */}
      <div className="progress-bar">
        <div
          className={`progress-fill ${colorClasses}`}
          style={{ width: `${percentage}%` }}
          role="progressbar"
          aria-valuenow={percentage}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>
    </div>
  );
};

export default ProgressBar;
