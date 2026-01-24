/**
 * DefectList Page
 *
 * Displays a tabular overview of tracked defects with filtering options.
 */

import React, { useEffect, useState, useCallback, useMemo } from 'react';
import { RefreshCw, ExternalLink, Bug } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { getDefects } from '../../services/defect.service';
import type { DefectRecord } from '../../types/defect';
import { ErrorState, Dropdown, DataTable } from '../../components/common';
import type { DropdownOption, Column } from '../../components/common';

const PAGE_SIZE = 25;

const SEVERITY_OPTIONS: DropdownOption[] = [
  { value: '', label: 'All severities' },
  { value: 'critical', label: 'Critical' },
  { value: 'high', label: 'High' },
  { value: 'medium', label: 'Medium' },
  { value: 'low', label: 'Low' },
];

const STATUS_OPTIONS: DropdownOption[] = [
  { value: '', label: 'All statuses' },
  { value: 'open', label: 'Open' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'resolved', label: 'Resolved' },
];

const resolveSeverityColor = (severity: string) => {
  switch (severity.toLowerCase()) {
    case 'critical':
      return 'bg-[var(--color-brand-muted)] text-[var(--color-brand-primary)]';
    case 'high':
      return 'bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)]';
    case 'medium':
      return 'bg-[var(--color-status-warning-bg)] text-[var(--color-status-warning)]';
    case 'low':
      return 'bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]';
    default:
      return 'bg-[var(--color-interactive-hover)] text-[var(--color-content-secondary)]';
  }
};

const formatDate = (value: string | null | undefined) => {
  if (!value) {
    return '—';
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return '—';
  }
  return date.toLocaleString();
};

const DefectList: React.FC = () => {
  const navigate = useNavigate();
  const [severityFilter, setSeverityFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [defects, setDefects] = useState<DefectRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let cancelled = false;

    const fetchDefects = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await getDefects({
          severity: severityFilter || null,
          status: statusFilter || null,
          category: null,
          page: 1,
          pageSize: PAGE_SIZE,
        });

        if (!cancelled) {
          setDefects(response.items);
        }
      } catch (err: unknown) {
        if (!cancelled) {
          setError(err?.message ?? 'Failed to load defects.');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchDefects();

    return () => {
      cancelled = true;
    };
  }, [severityFilter, statusFilter, refreshKey]);

  const handleRefresh = useCallback(() => {
    setRefreshKey((prev) => prev + 1);
  }, []);

  const columns: Column<DefectRecord>[] = useMemo(
    () => [
      {
        key: 'title',
        header: 'Title',
        cellClassName: 'max-w-xs',
        render: (row) => (
          <span className="font-semibold text-[var(--color-content-primary)] block truncate" title={row.title}>
            {row.title}
          </span>
        ),
      },
      {
        key: 'severity',
        header: 'Severity',
        render: (row) => (
          <span
            className={`px-2.5 py-1 rounded-md text-xs font-semibold ${resolveSeverityColor(row.severity)} capitalize`}
            data-testid={`defect-severity-chip-${row.severity.toLowerCase()}`}
          >
            {row.severity}
          </span>
        ),
      },
      {
        key: 'category',
        header: 'Category',
        render: (row) => (
          <span className="text-[var(--color-content-secondary)] capitalize">
            {row.category}
          </span>
        ),
      },
      {
        key: 'status',
        header: 'Status',
        render: (row) => (
          <span className="text-[var(--color-content-secondary)] capitalize">
            {row.status}
          </span>
        ),
      },
      {
        key: 'languageCode',
        header: 'Language',
        render: (row) => (
          <span className="text-[var(--color-content-secondary)]">
            {row.languageCode ?? '—'}
          </span>
        ),
      },
      {
        key: 'detectedAt',
        header: 'Detected',
        render: (row) => (
          <span className="text-[var(--color-content-secondary)]">
            {formatDate(row.detectedAt)}
          </span>
        ),
      },
      {
        key: 'actions',
        header: 'Actions',
        sortable: false,
        render: (row) => (
          <button
            onClick={(e) => {
              e.stopPropagation();
              navigate(`/defects/${row.id}`);
            }}
            className="px-3 py-1.5 text-xs font-semibold rounded-lg text-white bg-gradient-to-r from-[#2A6B6E] to-[#11484D] hover:from-[#4a9a9d] hover:to-[#0d3a3d] transition-all inline-flex items-center gap-1"
          >
            <ExternalLink size={12} />
            View
          </button>
        ),
      },
    ],
    [navigate]
  );

  return (
    <div className="w-full overflow-hidden">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-content-primary)] flex items-center gap-3">
            <Bug className="w-6 h-6" style={{ color: '#2A6B6E' }} />
            Defects
          </h1>
          <p className="text-sm text-[var(--color-content-muted)] mt-1">
            Review detected regressions, filter by severity or status, and prioritise fixes.
          </p>
        </div>
        <button
          className="p-2.5 rounded-lg text-sm font-semibold transition-all inline-flex items-center gap-2 bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)] border border-[var(--color-border-default)] hover:bg-[var(--color-interactive-active)]"
          onClick={handleRefresh}
        >
          <RefreshCw size={18} />
        </button>
      </div>

      {/* Filters */}
      <div className="bg-[var(--color-surface-raised)] p-4 rounded-xl mb-5 shadow-sm flex flex-col sm:flex-row gap-3 sm:items-center">
        <Dropdown
          id="severity-filter"
          options={SEVERITY_OPTIONS}
          value={severityFilter}
          onChange={setSeverityFilter}
          placeholder="All severities"
        />
        <Dropdown
          id="status-filter"
          options={STATUS_OPTIONS}
          value={statusFilter}
          onChange={setStatusFilter}
          placeholder="All statuses"
        />
      </div>

      {/* Error State */}
      {error && <ErrorState message={error} variant="alert" />}

      {/* Table */}
      {!error && (
        <DataTable
          data={defects}
          columns={columns}
          getRowKey={(row) => row.id}
          loading={loading}
          skeletonRows={8}
          onRowClick={(row) => navigate(`/defects/${row.id}`)}
          emptyState={{
            title: 'No Defects Found',
            description: 'No defects found for the selected filters.',
            icon: <Bug className="w-8 h-8 text-[var(--color-content-muted)]" />,
          }}
        />
      )}
    </div>
  );
};

export default DefectList;
