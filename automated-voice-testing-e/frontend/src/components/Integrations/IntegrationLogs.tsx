import { useCallback, useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import { AlertCircle } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

type IntegrationFilter = 'all' | 'slack' | 'jira' | 'github';
type LogLevelFilter = 'all' | 'info' | 'warning' | 'error';

type IntegrationLogEntry = {
  id: string;
  integration: IntegrationFilter;
  level: 'info' | 'warning' | 'error';
  message: string;
  timestamp: string;
  metadata?: Record<string, unknown>;
};

type IntegrationLogResponse = {
  items: IntegrationLogEntry[];
};

const integrationOptions: { value: IntegrationFilter; label: string }[] = [
  { value: 'all', label: 'All integrations' },
  { value: 'slack', label: 'Slack' },
  { value: 'jira', label: 'Jira' },
  { value: 'github', label: 'GitHub' },
];

const levelOptions: { value: LogLevelFilter; label: string }[] = [
  { value: 'all', label: 'All levels' },
  { value: 'info', label: 'Info' },
  { value: 'warning', label: 'Warnings' },
  { value: 'error', label: 'Errors' },
];

const levelChipColor: Record<IntegrationLogEntry['level'], string> = {
  info: 'bg-[var(--color-status-info-bg)] text-[var(--color-status-info)]',
  warning: 'bg-[var(--color-status-warning-bg)] text-[var(--color-status-warning)]',
  error: 'bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)]',
};

const authorizationHeaders = () => {
  const token = localStorage.getItem('accessToken');
  return {
    Authorization: token ? `Bearer ${token}` : 'Bearer ',
  };
};

const IntegrationLogs = () => {
  const [filters, setFilters] = useState<{ integration: IntegrationFilter; level: LogLevelFilter; limit: number }>({
    integration: 'all',
    level: 'all',
    limit: 20,
  });
  const [logs, setLogs] = useState<IntegrationLogEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchLogs = useCallback(
    async (currentFilters: typeof filters) => {
      setLoading(true);
      setError(null);

      try {
        const response = await axios.get<IntegrationLogResponse>(`${API_BASE_URL}/integrations/logs`, {
          headers: authorizationHeaders(),
          params: currentFilters,
        });
        setLogs(response.data.items ?? []);
      } catch (err: unknown) {
        let detail = 'Failed to load integration logs';
        if (err && typeof err === 'object' && 'response' in err) {
          const axiosError = err as { response?: { data?: { detail?: string } } };
          detail = axiosError.response?.data?.detail ?? detail;
        }
        setError(detail);
        setLogs([]);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  useEffect(() => {
    void fetchLogs({
      integration: 'all',
      level: 'all',
      limit: 20,
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const integrationLabel = useMemo(() => {
    const selected = integrationOptions.find((option) => option.value === filters.integration);
    return selected?.label ?? 'All integrations';
  }, [filters.integration]);

  const levelLabel = useMemo(() => {
    const selected = levelOptions.find((option) => option.value === filters.level);
    return selected?.label ?? 'All levels';
  }, [filters.level]);

  const handleIntegrationChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setFilters((current) => ({
      ...current,
      integration: event.target.value as IntegrationFilter,
    }));
  };

  const handleLevelChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setFilters((current) => ({
      ...current,
      level: event.target.value as LogLevelFilter,
    }));
  };

  const handleRefresh = () => {
    void fetchLogs(filters);
  };

  return (
    <div className="card p-6">
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row gap-4 sm:items-center">
          <h2 className="text-xl font-semibold">
            Integration Logs
          </h2>
          <div className="flex-1" />
          <div className="flex flex-col sm:flex-row gap-4">
            <select
              value={filters.integration}
              onChange={handleIntegrationChange}
              className="filter-select"
              aria-label="Filter by integration"
            >
              {integrationOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>

            <select
              value={filters.level}
              onChange={handleLevelChange}
              className="filter-select"
              aria-label="Filter by level"
            >
              {levelOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>

            <button
              className="btn"
              onClick={handleRefresh}
              disabled={loading}
            >
              Refresh
            </button>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-2">
          <span className="badge">{integrationLabel}</span>
          <span className="badge">{levelLabel}</span>
          <span className="badge">{logs.length} entries</span>
        </div>

        {error && (
          <div className="bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] text-[var(--color-status-danger)] px-4 py-3 rounded flex items-start gap-2" role="alert">
            <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <div className="space-y-4">
          {loading && <p className="text-[var(--color-content-muted)]">Loading logs…</p>}
          {!loading && logs.length === 0 && !error && (
            <p className="text-[var(--color-content-muted)]">No log entries match the selected filters.</p>
          )}
          {logs.map((log) => (
            <div key={log.id} className="card p-4">
              <div className="space-y-2">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="badge">{log.integration}</span>
                  <span className={`badge ${levelChipColor[log.level]}`}>{log.level}</span>
                  <span className="text-xs text-[var(--color-content-muted)]">
                    {formatTimestamp(log.timestamp)}
                  </span>
                </div>
                <p className="text-base">{log.message}</p>
                {log.metadata && (
                  <p className="text-sm text-[var(--color-content-muted)]">
                    {formatMetadata(log.metadata)}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const formatTimestamp = (value: string) => {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString();
};

const formatMetadata = (metadata: Record<string, unknown>) => {
  return Object.entries(metadata)
    .map(([key, val]) => `${key}: ${stringifyValue(val)}`)
    .join(' • ');
};

const stringifyValue = (value: unknown): string => {
  if (value === null || value === undefined) {
    return '—';
  }
  if (typeof value === 'object') {
    try {
      return JSON.stringify(value);
    } catch {
      return '[object]';
    }
  }
  return String(value);
};

export type { IntegrationLogEntry };

export default IntegrationLogs;
