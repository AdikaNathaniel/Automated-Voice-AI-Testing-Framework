/**
 * Executions List Page
 *
 * Displays all multi-turn scenario executions with:
 * - Filtering by status
 * - Sortable columns
 * - Pagination
 * - Click to view execution details
 */

import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Eye,
  Filter,
  RefreshCw,
  CheckCircle,
  XCircle,
  Clock,
  Play,
  PlayCircle,
} from 'lucide-react';
import { Dropdown, FormLabel, DataTable } from '../../components/common';
import type { Column } from '../../components/common';
import { multiTurnService } from '../../services/multiTurn.service';
import type { MultiTurnExecution } from '../../types/multiTurn';

const ExecutionsList: React.FC = () => {
  const navigate = useNavigate();

  const [executions, setExecutions] = useState<MultiTurnExecution[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);

  const pageSize = 20;

  const loadExecutions = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await multiTurnService.listExecutions({
        status: statusFilter || undefined,
        page: page,
        page_size: pageSize,
      });
      setExecutions(response.executions || []);
      setTotalItems(response.total || 0);
      setTotalPages(Math.ceil((response.total || 0) / pageSize));
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load executions';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadExecutions();
  }, [statusFilter, page]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return { icon: CheckCircle, color: 'text-[var(--color-status-success)]', bg: 'bg-[var(--color-status-success-bg)]', label: 'Completed' };
      case 'failed':
        return { icon: XCircle, color: 'text-[var(--color-status-danger)]', bg: 'bg-[var(--color-status-danger-bg)]', label: 'Failed' };
      case 'in_progress':
        return { icon: PlayCircle, color: 'text-[var(--color-status-info)]', bg: 'bg-[var(--color-status-info-bg)]', label: 'In Progress' };
      case 'pending':
        return { icon: Clock, color: 'text-[var(--color-status-warning)]', bg: 'bg-[var(--color-status-warning-bg)]', label: 'Pending' };
      default:
        return { icon: Clock, color: 'text-[var(--color-content-secondary)]', bg: 'bg-[var(--color-surface-inset)]', label: status };
    }
  };

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return '—';
    return new Date(dateString).toLocaleString();
  };

  const formatDuration = (started: string | null | undefined, completed: string | null | undefined) => {
    if (!started || !completed) return '—';
    const duration = new Date(completed).getTime() - new Date(started).getTime();
    return `${(duration / 1000).toFixed(1)}s`;
  };

  const columns: Column<MultiTurnExecution>[] = useMemo(
    () => [
      {
        key: 'scenario_name',
        header: 'Scenario',
        render: (execution) => (
          <div className="flex items-center gap-2">
            <PlayCircle className="w-4 h-4 text-[#2A6B6E]" />
            <div>
              <div className="text-sm font-medium text-[var(--color-content-primary)]">
                {execution.scenario_name || 'Unknown Scenario'}
              </div>
              <div className="text-xs text-[var(--color-content-muted)] font-mono">
                {execution.id.substring(0, 8)}...
              </div>
            </div>
          </div>
        ),
      },
      {
        key: 'status',
        header: 'Status',
        render: (execution) => {
          const statusBadge = getStatusBadge(execution.status);
          const StatusIcon = statusBadge.icon;
          return (
            <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${statusBadge.bg} ${statusBadge.color}`}>
              <StatusIcon className="w-3.5 h-3.5" />
              {statusBadge.label}
            </span>
          );
        },
      },
      {
        key: 'current_step_order',
        header: 'Steps',
        render: (execution) => (
          <div className="flex items-center gap-2">
            <span className={execution.status === 'failed' ? 'text-[var(--color-status-danger)]' : 'text-[var(--color-status-success)]'}>
              {execution.current_step_order}
            </span>
            <span className="text-[var(--color-content-muted)]">/</span>
            <span className="text-[var(--color-content-secondary)]">{execution.total_steps}</span>
          </div>
        ),
        sortFn: (a, b, direction) => {
          const comparison = (a.current_step_order / a.total_steps) - (b.current_step_order / b.total_steps);
          return direction === 'desc' ? -comparison : comparison;
        },
      },
      {
        key: 'started_at',
        header: 'Started At',
        render: (execution) => (
          <span className="text-[var(--color-content-secondary)]">
            {formatDate(execution.started_at)}
          </span>
        ),
        sortFn: (a, b, direction) => {
          const aTime = a.started_at ? new Date(a.started_at).getTime() : 0;
          const bTime = b.started_at ? new Date(b.started_at).getTime() : 0;
          const comparison = aTime - bTime;
          return direction === 'desc' ? -comparison : comparison;
        },
      },
      {
        key: 'duration',
        header: 'Duration',
        sortable: false,
        render: (execution) => (
          <span className="text-[var(--color-content-secondary)]">
            {formatDuration(execution.started_at, execution.completed_at)}
          </span>
        ),
      },
      {
        key: 'actions',
        header: 'Actions',
        sortable: false,
        render: (execution) => (
          <button
            onClick={(e) => {
              e.stopPropagation();
              navigate(`/scenarios/executions/${execution.id}`);
            }}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 border border-[var(--color-border-strong)] rounded-lg text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)] transition-colors"
          >
            <Eye className="w-4 h-4" />
            View
          </button>
        ),
      },
    ],
    [navigate]
  );

  const emptyStateConfig = useMemo(
    () => ({
      title: 'No Executions Found',
      description: statusFilter
        ? 'No executions match the selected filter. Try selecting a different status.'
        : 'Run a scenario to see execution history here.',
      icon: <Play className="w-8 h-8 text-[var(--color-content-muted)]" />,
      action: {
        label: 'Go to Scenarios',
        onClick: () => navigate('/scenarios'),
      },
    }),
    [statusFilter, navigate]
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-content-primary)] flex items-center gap-3">
            <Play className="w-6 h-6" style={{ color: '#2A6B6E' }} />
            Executions
          </h1>
          <p className="text-sm text-[var(--color-content-secondary)] mt-1">
            {totalItems} Scenario Executions
          </p>
        </div>
        <button
          onClick={loadExecutions}
          className="p-2.5 rounded-lg text-sm font-semibold transition-all inline-flex items-center gap-2 bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)] border border-[var(--color-border-strong)] hover:bg-[var(--color-interactive-active)]"
        >
          <RefreshCw size={18} />
        </button>
      </div>

      {/* Filters */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl border border-[var(--color-border-default)] shadow-sm p-5">
        <div className="flex items-center gap-2 mb-4">
          <Filter className="w-4 h-4 text-[var(--color-content-muted)]" />
          <h3 className="text-sm font-semibold text-[var(--color-content-primary)] uppercase tracking-wide">Filters</h3>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <div>
            <FormLabel>Status</FormLabel>
            <Dropdown
              value={statusFilter}
              onChange={(value) => {
                setStatusFilter(value);
                setPage(1);
              }}
              placeholder="All Statuses"
              options={[
                { value: '', label: 'All Statuses' },
                { value: 'completed', label: 'Completed' },
                { value: 'failed', label: 'Failed' },
                { value: 'in_progress', label: 'In Progress' },
                { value: 'pending', label: 'Pending' },
              ]}
            />
          </div>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm">
          <div className="p-10 text-center text-[var(--color-status-danger)]">{error}</div>
        </div>
      )}

      {/* Data Table */}
      {!error && (
        <DataTable
          data={executions}
          columns={columns}
          getRowKey={(execution) => execution.id}
          loading={loading}
          skeletonRows={5}
          emptyState={emptyStateConfig}
          onRowClick={(execution) => navigate(`/scenarios/executions/${execution.id}`)}
          initialSort={{ column: 'started_at', direction: 'desc' }}
        />
      )}

      {/* Pagination */}
      {totalPages > 1 && !loading && !error && executions.length > 0 && (
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm border border-[var(--color-border-default)]">
          <div className="flex items-center justify-between">
            <div className="text-sm text-[var(--color-content-secondary)]">
              Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, totalItems)} of {totalItems} executions
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setPage(page - 1)}
                disabled={page === 1}
                className="px-4 py-2 border border-[var(--color-border-strong)] rounded-lg text-[var(--color-content-secondary)] bg-[var(--color-surface-raised)] hover:bg-[var(--color-interactive-hover)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Previous
              </button>
              <button
                onClick={() => setPage(page + 1)}
                disabled={page === totalPages}
                className="px-4 py-2 border border-[var(--color-border-strong)] rounded-lg text-[var(--color-content-secondary)] bg-[var(--color-surface-raised)] hover:bg-[var(--color-interactive-hover)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExecutionsList;
