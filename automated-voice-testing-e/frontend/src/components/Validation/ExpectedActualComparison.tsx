/**
 * Expected vs Actual Comparison Component
 *
 * Displays a set of comparison items, showing expected and actual values side-by-side
 * with optional highlighting for mismatches. Designed for use in validation workflows.
 */

import React from 'react';

type Primitive = string | number | boolean | null | undefined;
type ComplexValue = Record<string, unknown> | Array<unknown>;

export type ComparisonValue = Primitive | ComplexValue;

export interface ComparisonItem {
  label: string;
  expected?: ComparisonValue;
  actual?: ComparisonValue;
  helperText?: string;
}

export interface ExpectedActualComparisonProps {
  /**
   * Optional title rendered above the comparison list.
   */
  title?: string;
  /**
   * Collection of comparison entries to display.
   */
  items: ComparisonItem[];
  /**
   * Fallback text when no items are provided.
   */
  emptyStateText?: string;
  /**
   * When true, mismatched actual values are visually highlighted.
   */
  highlightDifferences?: boolean;
  /**
   * When true, displays skeleton loaders instead of content.
   */
  loading?: boolean;
}

/**
 * Convert values into human-readable strings.
 */
const formatValue = (value: ComparisonValue): string => {
  if (value === null || value === undefined) {
    return 'N/A';
  }

  if (typeof value === 'string') {
    return value.trim() === '' ? 'N/A' : value;
  }

  if (typeof value === 'number' || typeof value === 'boolean') {
    return String(value);
  }

  return JSON.stringify(value, null, 2);
};

/**
 * ExpectedActualComparison Component
 */
const ExpectedActualComparison: React.FC<ExpectedActualComparisonProps> = ({
  title,
  items,
  emptyStateText = 'No comparison data available',
  highlightDifferences = true,
  loading = false,
}) => {
  // Show skeleton loaders while loading
  if (loading) {
    return (
      <div>
        {title && (
          <h2 className="text-xl font-semibold mb-4">
            {title}
          </h2>
        )}
        <div className="space-y-4">
          {[1, 2, 3].map((index) => (
            <div key={index} className="card p-4 bg-[var(--color-surface-inset)]">
              <div className="space-y-2">
                <div className="h-6 bg-[var(--color-interactive-active)] rounded w-1/3 animate-pulse" />
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <div className="h-4 bg-[var(--color-interactive-active)] rounded w-1/5 mb-2 animate-pulse" />
                    <div className="h-5 bg-[var(--color-interactive-active)] rounded w-4/5 animate-pulse" />
                  </div>
                  <div>
                    <div className="h-4 bg-[var(--color-interactive-active)] rounded w-1/5 mb-2 animate-pulse" />
                    <div className="h-5 bg-[var(--color-interactive-active)] rounded w-4/5 animate-pulse" />
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!items.length) {
    return (
      <div>
        {title && (
          <h2 className="text-xl font-semibold mb-4">
            {title}
          </h2>
        )}
        <div className="card p-4 bg-[var(--color-surface-inset)]">
          <p className="text-[var(--color-content-muted)]">{emptyStateText}</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      {title && (
        <h2 className="text-xl font-semibold mb-4">
          {title}
        </h2>
      )}

      <div className="space-y-4">
        {items.map((item, index) => {
          const expectedText = formatValue(item.expected ?? 'N/A');
          const actualText = formatValue(item.actual ?? 'N/A');
          const isMismatch =
            highlightDifferences &&
            expectedText !== actualText &&
            !(expectedText === 'N/A' && actualText === 'N/A');

          return (
            <div key={`${item.label}-${index}`}>
              <div
                data-comparison-item
                className={`card p-4 bg-[var(--color-surface-inset)] ${isMismatch ? 'border-l-4 border-l-red-500' : ''}`}
              >
                <div className="space-y-2">
                  <div className="flex justify-between items-center gap-2">
                    <div>
                      <h3 className="text-sm font-semibold">{item.label}</h3>
                      {item.helperText && (
                        <p className="text-xs text-[var(--color-content-muted)]">
                          {item.helperText}
                        </p>
                      )}
                    </div>
                    {isMismatch && (
                      <span
                        className="badge bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)] border border-[var(--color-status-danger)]"
                        data-testid={`comparison-mismatch-${index}`}
                      >
                        Mismatch
                      </span>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <span className="text-xs text-[var(--color-content-muted)]">
                        Expected
                      </span>
                      <pre className="text-sm whitespace-pre-wrap mt-1">
                        {expectedText}
                      </pre>
                    </div>
                    <div>
                      <span className="text-xs text-[var(--color-content-muted)]">
                        Actual
                      </span>
                      <pre className={`text-sm whitespace-pre-wrap mt-1 ${isMismatch ? 'text-[var(--color-status-danger)]' : ''}`}>
                        {actualText}
                      </pre>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ExpectedActualComparison;
