/**
 * DataTable Component
 *
 * A reusable, feature-rich data table with:
 * - Column sorting (click headers)
 * - Custom cell renderers
 * - Loading skeleton state
 * - Empty state with configurable message/action
 * - Row click handlers for navigation
 * - Responsive horizontal scrolling
 * - TypeScript generics for type safety
 *
 * Uses semantic tokens for consistent theming across light/dark/oled.
 */

import React, { useState, useMemo, useCallback } from 'react';
import { ChevronUp, ChevronDown, ChevronsUpDown } from 'lucide-react';
import EmptyState from './EmptyState';

export type SortDirection = 'asc' | 'desc' | null;

export interface SortState {
  column: string | null;
  direction: SortDirection;
}

export interface Column<T> {
  /** Unique key for the column, used for sorting */
  key: string;
  /** Display header text */
  header: string;
  /** Whether this column is sortable (default: true) */
  sortable?: boolean;
  /** Custom sort function for complex data */
  sortFn?: (a: T, b: T, direction: SortDirection) => number;
  /** Custom cell renderer */
  render?: (row: T, index: number) => React.ReactNode;
  /** Width class (e.g., 'w-48', 'min-w-[200px]') */
  width?: string;
  /** Text alignment */
  align?: 'left' | 'center' | 'right';
  /** Additional header class */
  headerClassName?: string;
  /** Additional cell class */
  cellClassName?: string;
}

export interface EmptyStateConfig {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export interface DataTableProps<T> {
  /** Array of data to display */
  data: T[];
  /** Column definitions */
  columns: Column<T>[];
  /** Unique key extractor for each row */
  getRowKey: (row: T) => string;
  /** Loading state */
  loading?: boolean;
  /** Number of skeleton rows to show when loading */
  skeletonRows?: number;
  /** Empty state configuration */
  emptyState?: EmptyStateConfig;
  /** Row click handler */
  onRowClick?: (row: T) => void;
  /** Initial sort state */
  initialSort?: SortState;
  /** Controlled sort state */
  sort?: SortState;
  /** Sort change callback for controlled mode */
  onSortChange?: (sort: SortState) => void;
  /** Additional table class */
  className?: string;
  /** Whether to use striped rows */
  striped?: boolean;
  /** Whether to show hover effect on rows */
  hoverable?: boolean;
  /** Sticky header */
  stickyHeader?: boolean;
  /** Max height for scrollable table body */
  maxHeight?: string;
}

function DataTable<T>({
  data,
  columns,
  getRowKey,
  loading = false,
  skeletonRows = 5,
  emptyState,
  onRowClick,
  initialSort = { column: null, direction: null },
  sort: controlledSort,
  onSortChange,
  className = '',
  striped = false,
  hoverable = true,
  stickyHeader = false,
  maxHeight,
}: DataTableProps<T>) {
  const [internalSort, setInternalSort] = useState<SortState>(initialSort);

  // Use controlled or internal sort state
  const sortState = controlledSort ?? internalSort;
  const setSortState = onSortChange ?? setInternalSort;

  const handleSort = useCallback(
    (columnKey: string, column: Column<T>) => {
      if (column.sortable === false) return;

      setSortState((prev) => {
        const currentSort = controlledSort ?? prev;
        if (currentSort.column === columnKey) {
          // Cycle: asc -> desc -> null
          if (currentSort.direction === 'asc') {
            return { column: columnKey, direction: 'desc' };
          } else if (currentSort.direction === 'desc') {
            return { column: null, direction: null };
          }
        }
        return { column: columnKey, direction: 'asc' };
      });
    },
    [controlledSort, setSortState]
  );

  const sortedData = useMemo(() => {
    if (!sortState.column || !sortState.direction) {
      return data;
    }

    const column = columns.find((c) => c.key === sortState.column);
    if (!column) return data;

    return [...data].sort((a, b) => {
      // Use custom sort function if provided
      if (column.sortFn) {
        return column.sortFn(a, b, sortState.direction);
      }

      // Default sorting logic
      const aVal = (a as Record<string, unknown>)[sortState.column as string];
      const bVal = (b as Record<string, unknown>)[sortState.column as string];

      let comparison = 0;

      if (aVal === null || aVal === undefined) comparison = 1;
      else if (bVal === null || bVal === undefined) comparison = -1;
      else if (typeof aVal === 'string' && typeof bVal === 'string') {
        comparison = aVal.localeCompare(bVal);
      } else if (typeof aVal === 'number' && typeof bVal === 'number') {
        comparison = aVal - bVal;
      } else if (aVal instanceof Date && bVal instanceof Date) {
        comparison = aVal.getTime() - bVal.getTime();
      } else {
        comparison = String(aVal).localeCompare(String(bVal));
      }

      return sortState.direction === 'desc' ? -comparison : comparison;
    });
  }, [data, sortState, columns]);

  const getSortIcon = (columnKey: string, sortable: boolean) => {
    if (!sortable) return null;

    if (sortState.column !== columnKey) {
      return (
        <ChevronsUpDown className="w-4 h-4 text-[var(--color-content-muted)] opacity-0 group-hover:opacity-100 transition-opacity" />
      );
    }

    if (sortState.direction === 'asc') {
      return <ChevronUp className="w-4 h-4 text-[var(--color-brand-primary)]" />;
    }

    return <ChevronDown className="w-4 h-4 text-[var(--color-brand-primary)]" />;
  };

  const getAlignmentClass = (align?: 'left' | 'center' | 'right') => {
    switch (align) {
      case 'center':
        return 'text-center';
      case 'right':
        return 'text-right';
      default:
        return 'text-left';
    }
  };

  // Loading skeleton
  if (loading) {
    return (
      <div className={`table-container ${className}`}>
        <div className="overflow-x-auto w-full">
          <table className="w-full">
            <thead className="table-header">
              <tr>
                {columns.map((column) => (
                  <th
                    key={column.key}
                    className={`px-6 py-4 text-xs font-semibold text-[var(--color-content-secondary)] uppercase tracking-wider ${getAlignmentClass(column.align)} ${column.width || ''} ${column.headerClassName || ''}`}
                  >
                    {column.header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--color-border-subtle)]">
              {Array.from({ length: skeletonRows }).map((_, rowIndex) => (
                <tr key={rowIndex}>
                  {columns.map((column) => (
                    <td key={column.key} className="px-6 py-4">
                      <div className="animate-pulse">
                        <div className="h-4 bg-[var(--color-surface-inset)] rounded w-3/4"></div>
                      </div>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  // Empty state
  if (data.length === 0) {
    if (emptyState) {
      return (
        <div className={`card-static p-16 text-center ${className}`}>
          {emptyState.icon && (
            <div
              className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6"
              style={{ background: 'var(--color-surface-inset)' }}
            >
              {emptyState.icon}
            </div>
          )}
          <h3 className="text-lg font-semibold text-[var(--color-content-primary)] mb-2">
            {emptyState.title}
          </h3>
          {emptyState.description && (
            <p className="text-sm text-[var(--color-content-secondary)] mb-6 max-w-md mx-auto">
              {emptyState.description}
            </p>
          )}
          {emptyState.action && (
            <button onClick={emptyState.action.onClick} className="btn-primary">
              {emptyState.action.label}
            </button>
          )}
        </div>
      );
    }

    return (
      <EmptyState
        title="No data found"
        description="There are no items to display."
        icon="inbox"
        className={className}
      />
    );
  }

  // Data table
  const tableContent = (
    <table className="w-full">
      <thead className={`table-header ${stickyHeader ? 'sticky top-0 z-10' : ''}`}>
        <tr>
          {columns.map((column) => {
            const isSortable = column.sortable !== false;
            return (
              <th
                key={column.key}
                onClick={() => isSortable && handleSort(column.key, column)}
                className={`px-6 py-4 text-xs font-semibold text-[var(--color-content-secondary)] uppercase tracking-wider ${getAlignmentClass(column.align)} ${column.width || ''} ${column.headerClassName || ''} ${isSortable ? 'cursor-pointer select-none group hover:bg-[var(--color-interactive-hover)] transition-colors' : ''}`}
              >
                <div
                  className={`flex items-center gap-1.5 ${column.align === 'right' ? 'justify-end' : column.align === 'center' ? 'justify-center' : ''}`}
                >
                  <span>{column.header}</span>
                  {getSortIcon(column.key, isSortable)}
                </div>
              </th>
            );
          })}
        </tr>
      </thead>
      <tbody className="divide-y divide-[var(--color-border-subtle)]">
        {sortedData.map((row, index) => (
          <tr
            key={getRowKey(row)}
            onClick={() => onRowClick?.(row)}
            className={`
              ${hoverable ? 'table-row' : ''}
              ${striped && index % 2 === 1 ? 'bg-[var(--color-surface-inset)]' : ''}
              ${onRowClick ? 'cursor-pointer' : ''}
              transition-colors
            `}
          >
            {columns.map((column) => (
              <td
                key={column.key}
                className={`px-6 py-4 whitespace-nowrap text-sm text-[var(--color-content-primary)] ${getAlignmentClass(column.align)} ${column.cellClassName || ''}`}
              >
                {column.render
                  ? column.render(row, index)
                  : String((row as Record<string, unknown>)[column.key] ?? '')}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );

  return (
    <div className={`table-container ${className}`}>
      <div
        className="overflow-x-auto w-full"
        style={maxHeight ? { maxHeight, overflowY: 'auto' } : undefined}
      >
        {tableContent}
      </div>
    </div>
  );
}

export default DataTable;
