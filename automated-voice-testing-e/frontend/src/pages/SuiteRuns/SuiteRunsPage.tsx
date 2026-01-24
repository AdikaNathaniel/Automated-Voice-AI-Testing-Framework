/**
 * Suite Runs Page - Polished UI
 *
 * Displays all suite runs with:
 * - Gradient header with stats
 * - Summary cards for key metrics
 * - Sortable, filterable data table
 * - Status badges and progress indicators
 */

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Play,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  RefreshCw,
  Eye,
  Layers,
  Tag,
  PlayCircle,
  TrendingUp,
  Timer,
  Filter,
} from 'lucide-react';
import { LanguageSelector, StatCard, DataTable } from '../../components/common';
import type { Column } from '../../components/common';
import { getSuiteRuns } from '../../services/suiteRun.service';
import type { SuiteRunSummary } from '../../types/suiteRun';

const LANGUAGE_OPTIONS = [
  { code: 'en-US', name: 'English (en-US)' },
  { code: 'es-ES', name: 'Spanish (es-ES)' },
  { code: 'fr-FR', name: 'French (fr-FR)' },
  { code: 'ja-JP', name: 'Japanese (ja-JP)' },
];

const formatTimestamp = (value: string | null | undefined) => {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '—';
  return date.toLocaleString();
};

const getStatusConfig = (status: SuiteRunSummary['status']) => {
  switch (status) {
    case 'completed':
      return {
        icon: CheckCircle,
        color: 'text-[var(--color-status-success)]',
        bg: 'bg-[var(--color-status-success-bg)]',
        label: 'Completed',
      };
    case 'failed':
      return {
        icon: XCircle,
        color: 'text-[var(--color-status-danger)]',
        bg: 'bg-[var(--color-status-danger-bg)]',
        label: 'Failed',
      };
    case 'running':
      return {
        icon: PlayCircle,
        color: 'text-[var(--color-status-info)]',
        bg: 'bg-[var(--color-status-info-bg)]',
        label: 'Running',
      };
    case 'pending':
      return {
        icon: Clock,
        color: 'text-[var(--color-status-warning)]',
        bg: 'bg-[var(--color-status-warning-bg)]',
        label: 'Pending',
      };
    default:
      return {
        icon: AlertTriangle,
        color: 'text-[var(--color-content-secondary)]',
        bg: 'bg-[var(--color-surface-inset)]',
        label: status,
      };
  }
};

const formatDuration = (
  started: string | null | undefined,
  completed: string | null | undefined
) => {
  if (!started || !completed) return '—';
  const startDate = new Date(started);
  const endDate = new Date(completed);
  if (Number.isNaN(startDate.getTime()) || Number.isNaN(endDate.getTime())) return '—';

  const durationMs = endDate.getTime() - startDate.getTime();
  if (durationMs < 0) return '—';

  const seconds = Math.floor(durationMs / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);

  if (hours > 0) {
    return `${hours}h ${minutes % 60}m`;
  }
  if (minutes > 0) {
    return `${minutes}m ${seconds % 60}s`;
  }
  return `${seconds}s`;
};

const SuiteRunsPage: React.FC = () => {
  const navigate = useNavigate();
  const [languageFilter, setLanguageFilter] = useState<string | null>(null);
  const [runs, setRuns] = useState<SuiteRunSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRuns = useCallback(
    async (showRefresh = false) => {
      try {
        if (showRefresh) {
          setRefreshing(true);
        } else {
          setLoading(true);
        }
        setError(null);
        const response = await getSuiteRuns({ languageCode: languageFilter });
        setRuns(response.runs);
      } catch (err: unknown) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to load suite runs.';
        setError(errorMessage);
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    [languageFilter]
  );

  useEffect(() => {
    fetchRuns();
  }, [fetchRuns]);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => fetchRuns(true), 30000);
    return () => clearInterval(interval);
  }, [fetchRuns]);

  const stats = useMemo(() => {
    const completed = runs.filter((r) => r.status === 'completed').length;
    const failed = runs.filter((r) => r.status === 'failed').length;
    const running = runs.filter((r) => r.status === 'running').length;
    const pending = runs.filter((r) => r.status === 'pending').length;

    const passedTests = runs.reduce((sum, r) => sum + (r.passedTests || 0), 0);
    const totalTests = runs.reduce((sum, r) => sum + (r.totalTests || 0), 0);
    const passRate = totalTests > 0 ? ((passedTests / totalTests) * 100).toFixed(1) : '0';

    // Calculate average duration
    const durations = runs
      .filter((r) => r.startedAt && r.completedAt)
      .map((r) => new Date(r.completedAt!).getTime() - new Date(r.startedAt!).getTime());
    const avgDuration =
      durations.length > 0
        ? Math.round(durations.reduce((a, b) => a + b, 0) / durations.length / 1000)
        : 0;

    return { completed, failed, running, pending, passRate, totalTests, avgDuration };
  }, [runs]);

  const columns: Column<SuiteRunSummary>[] = useMemo(
    () => [
      {
        key: 'suiteName',
        header: 'Suite / Category',
        render: (run) => (
          <div className="flex items-center gap-2">
            {run.is_categorical ? (
              <Tag className="w-4 h-4 text-[#2A6B6E]" />
            ) : (
              <Layers className="w-4 h-4 text-[var(--color-content-muted)]" />
            )}
            <div>
              <div className="text-sm font-medium text-[var(--color-content-primary)]">
                {run.suiteName || run.suite_name || run.category_name || 'Unknown'}
              </div>
              <div className="text-xs text-[var(--color-content-muted)] font-mono">
                {run.id.substring(0, 8)}...
              </div>
            </div>
          </div>
        ),
        sortFn: (a, b, direction) => {
          const aName = a.suiteName || a.suite_name || a.category_name || '';
          const bName = b.suiteName || b.suite_name || b.category_name || '';
          const comparison = aName.localeCompare(bName);
          return direction === 'desc' ? -comparison : comparison;
        },
      },
      {
        key: 'type',
        header: 'Type',
        render: (run) =>
          run.is_categorical ? (
            <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-[#2A6B6E]/10 text-[#2A6B6E]">
              Category
            </span>
          ) : (
            <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)]">
              Custom Suite
            </span>
          ),
        sortFn: (a, b, direction) => {
          const comparison = (a.is_categorical ? 1 : 0) - (b.is_categorical ? 1 : 0);
          return direction === 'desc' ? -comparison : comparison;
        },
      },
      {
        key: 'status',
        header: 'Status',
        render: (run) => {
          const statusConfig = getStatusConfig(run.status);
          const StatusIcon = statusConfig.icon;
          return (
            <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${statusConfig.bg} ${statusConfig.color}`}>
              <StatusIcon className="w-3.5 h-3.5" />
              {statusConfig.label}
            </span>
          );
        },
      },
      {
        key: 'progress',
        header: 'Progress',
        render: (run) => (
          <div className="flex items-center gap-2">
            <span className={run.failedTests > 0 ? 'text-[var(--color-status-danger)]' : 'text-[var(--color-status-success)]'}>
              {run.passedTests || 0}
            </span>
            <span className="text-[var(--color-content-muted)]">/</span>
            <span className="text-[var(--color-content-secondary)]">{run.totalTests || 0}</span>
          </div>
        ),
        sortFn: (a, b, direction) => {
          const aRate = a.totalTests > 0 ? (a.passedTests || 0) / a.totalTests : 0;
          const bRate = b.totalTests > 0 ? (b.passedTests || 0) / b.totalTests : 0;
          const comparison = aRate - bRate;
          return direction === 'desc' ? -comparison : comparison;
        },
      },
      {
        key: 'startedAt',
        header: 'Started At',
        render: (run) => (
          <span className="text-[var(--color-content-secondary)]">
            {formatTimestamp(run.startedAt || run.createdAt)}
          </span>
        ),
        sortFn: (a, b, direction) => {
          const aTime = a.startedAt || a.createdAt ? new Date(a.startedAt || a.createdAt!).getTime() : 0;
          const bTime = b.startedAt || b.createdAt ? new Date(b.startedAt || b.createdAt!).getTime() : 0;
          const comparison = aTime - bTime;
          return direction === 'desc' ? -comparison : comparison;
        },
      },
      {
        key: 'duration',
        header: 'Duration',
        sortable: false,
        render: (run) => (
          <span className="text-[var(--color-content-secondary)]">
            {formatDuration(run.startedAt || run.createdAt, run.completedAt)}
          </span>
        ),
      },
      {
        key: 'actions',
        header: 'Actions',
        sortable: false,
        render: (run) => (
          <button
            onClick={(e) => {
              e.stopPropagation();
              navigate(`/suite-runs/${run.id}`);
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
      title: 'No Suite Runs Found',
      description: languageFilter
        ? 'No runs found for the selected language. Try selecting a different filter.'
        : 'Start running test suites to see your execution history here.',
      icon: <Layers className="w-8 h-8 text-[var(--color-content-muted)]" />,
      action: {
        label: 'Start Your First Run',
        onClick: () => navigate('/test-suites'),
      },
    }),
    [languageFilter, navigate]
  );

  if (loading && runs.length === 0) {
    return (
      <div className="space-y-6">
        {/* Header skeleton */}
        <div className="h-24 bg-[var(--color-surface-raised)] rounded-xl shadow-md animate-pulse" />
        {/* Stats skeleton */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-32 bg-[var(--color-surface-raised)] rounded-xl border border-[var(--color-border-subtle)] animate-pulse" />
          ))}
        </div>
        {/* Filter skeleton */}
        <div className="h-16 bg-[var(--color-surface-raised)] rounded-xl border border-[var(--color-border-subtle)] animate-pulse" />
        {/* Table skeleton */}
        <div className="h-96 bg-[var(--color-surface-raised)] rounded-xl border border-[var(--color-border-subtle)] animate-pulse" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-content-primary)] flex items-center gap-3">
            <PlayCircle className="w-6 h-6" style={{ color: '#2A6B6E' }} />
            Suite Runs
          </h1>
          <p className="text-sm text-[var(--color-content-muted)] mt-1">
            {runs.length} total runs • {stats.running > 0 ? `${stats.running} running` : 'All complete'}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/test-suites')}
            className="px-4 py-2.5 rounded-lg text-sm font-semibold transition-all inline-flex items-center gap-2 text-white hover:shadow-lg hover:-translate-y-0.5"
            style={{ background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }}
          >
            <Play className="w-4 h-4" />
            New Suite Run
          </button>
          <button
            onClick={() => fetchRuns(true)}
            disabled={refreshing}
            className="p-2.5 rounded-lg text-sm font-semibold transition-all inline-flex items-center gap-2 bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-active)]"
          >
            <RefreshCw className={`w-5 h-5 ${refreshing ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="flex items-center gap-3 p-4 bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger-bg)] rounded-xl text-[var(--color-status-danger)]">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <div className="flex-1">
            <p className="font-medium">{error}</p>
          </div>
          <button
            onClick={() => fetchRuns()}
            className="text-sm font-medium hover:underline"
          >
            Retry
          </button>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          title="Completed"
          value={stats.completed}
          icon={<CheckCircle className="w-5 h-5" />}
          iconColor="text-[var(--color-status-success)]"
          iconBg="bg-[var(--color-status-success-bg)]"
          variant="vertical"
        />
        <StatCard
          title="Running"
          value={stats.running}
          icon={<PlayCircle className="w-5 h-5" />}
          iconColor="text-[var(--color-status-info)]"
          iconBg="bg-[var(--color-status-info-bg)]"
          subtitle={stats.running > 0 ? 'In progress' : undefined}
          variant="vertical"
        />
        <StatCard
          title="Pass Rate"
          value={`${stats.passRate}%`}
          icon={<TrendingUp className="w-5 h-5" />}
          iconColor="text-primary"
          iconBg="bg-[var(--color-brand-muted)]"
          subtitle={`${stats.totalTests} total tests`}
          variant="vertical"
        />
        <StatCard
          title="Avg Duration"
          value={stats.avgDuration > 0 ? `${stats.avgDuration}s` : '—'}
          icon={<Timer className="w-5 h-5" />}
          iconColor="text-[var(--color-status-purple)]"
          iconBg="bg-[var(--color-status-purple-bg)]"
          variant="vertical"
        />
      </div>

      {/* Filters */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl border border-[var(--color-border-default)] shadow-sm p-5">
        <div className="flex items-center gap-2 mb-4">
          <Filter className="w-4 h-4 text-[var(--color-content-muted)]" />
          <h3 className="text-sm font-semibold text-[var(--color-content-primary)] uppercase tracking-wide">Filters</h3>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <LanguageSelector
            value={languageFilter}
            onChange={setLanguageFilter}
            languages={LANGUAGE_OPTIONS}
            includeAllOption={true}
          />
        </div>
      </div>

      {/* Data Table */}
      <DataTable
        data={runs}
        columns={columns}
        getRowKey={(run) => run.id}
        loading={false}
        emptyState={emptyStateConfig}
        onRowClick={(run) => navigate(`/suite-runs/${run.id}`)}
        initialSort={{ column: 'startedAt', direction: 'desc' }}
      />
    </div>
  );
};

export default SuiteRunsPage;
