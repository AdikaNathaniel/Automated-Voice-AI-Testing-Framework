import { useCallback, useEffect, useMemo, useState } from 'react';
import { AlertCircle } from 'lucide-react';

import type { ActivityFeed as ActivityFeedResponse, ActivityLogEntry } from '../../types/activity';
import { getActivityFeed } from '../../services/activity.service';
import websocketService from '../../services/websocket.service';

const DEFAULT_LIMIT = 25;

type FilterState = {
  userId: string;
  actionType: string;
};

const initialFilters: FilterState = {
  userId: '',
  actionType: '',
};

const buildServiceFilters = (filters: FilterState) => ({
  limit: DEFAULT_LIMIT,
  offset: 0,
  ...(filters.userId ? { userId: filters.userId } : {}),
  ...(filters.actionType ? { actionType: filters.actionType } : {}),
});

const toActivityLogEntry = (payload: unknown): ActivityLogEntry | null => {
  if (!payload || typeof payload !== 'object') {
    return null;
  }

  const data = payload as Record<string, unknown>;

  const id = (data.id ?? data['event_id']) as string | undefined;
  const userId = (data.userId ?? data['user_id']) as string | undefined;
  const actionType = (data.actionType ?? data['action_type']) as string | undefined;
  const createdAt = (data.createdAt ?? data['created_at']) as string | undefined;

  if (!id || !userId || !actionType || !createdAt) {
    return null;
  }

  const resourceType = (data.resourceType ?? data['resource_type']) as string | null | undefined;
  const resourceId = (data.resourceId ?? data['resource_id']) as string | null | undefined;
  const actionDescription = (data.actionDescription ?? data['action_description']) as
    | string
    | null
    | undefined;
  const ipAddress = (data.ipAddress ?? data['ip_address']) as string | null | undefined;
  const metadata =
    typeof data.metadata === 'object' && data.metadata !== null
      ? (data.metadata as Record<string, unknown>)
      : {};

  return {
    id,
    userId,
    actionType,
    resourceType: resourceType ?? null,
    resourceId: resourceId ?? null,
    actionDescription: actionDescription ?? null,
    metadata,
    ipAddress: ipAddress ?? null,
    createdAt,
  };
};

const matchesFilters = (entry: ActivityLogEntry, filters: FilterState) => {
  if (filters.userId && entry.userId !== filters.userId) {
    return false;
  }

  if (filters.actionType && entry.actionType !== filters.actionType) {
    return false;
  }

  return true;
};

const formatTimestamp = (timestamp: string) => {
  try {
    const date = new Date(timestamp);
    if (Number.isNaN(date.getTime())) {
      return timestamp;
    }
    return date.toLocaleString();
  } catch {
    return timestamp;
  }
};

const ActivityFeed = () => {
  const [events, setEvents] = useState<ActivityLogEntry[]>([]);
  const [pagination, setPagination] = useState<ActivityFeedResponse['pagination'] | null>(null);
  const [filters, setFilters] = useState<FilterState>(initialFilters);
  const [appliedFilters, setAppliedFilters] = useState<FilterState>(initialFilters);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadFeed = useCallback(
    async (activeFilters: FilterState) => {
      setLoading(true);
      setError(null);

      try {
        const response = await getActivityFeed(buildServiceFilters(activeFilters));
        setEvents(response.items);
        setPagination(response.pagination);
      } catch {
        console.error('Failed to load activity feed', err);
        setEvents([]);
        setPagination(null);
        setError('Unable to load the activity feed right now. Please try again in a moment.');
      } finally {
        setLoading(false);
      }
    },
    []
  );

  useEffect(() => {
    void loadFeed(appliedFilters);
  }, [appliedFilters, loadFeed]);

  useEffect(() => {
    const handler = (payload: unknown) => {
      const entry = toActivityLogEntry(payload);
      if (!entry || !matchesFilters(entry, appliedFilters)) {
        return;
      }

      setEvents((current) => {
        const deduped = current.filter((existing) => existing.id !== entry.id);
        return [entry, ...deduped].slice(0, DEFAULT_LIMIT);
      });
    };

    websocketService.on('activity:created', handler);

    return () => {
      websocketService.off('activity:created', handler);
    };
  }, [appliedFilters]);

  const actionTypeSuggestions = useMemo(() => {
    const unique = new Set<string>();
    events.forEach((entry) => unique.add(entry.actionType));
    return Array.from(unique).sort();
  }, [events]);

  const handleFilterChange = (field: keyof FilterState) => (event: React.ChangeEvent<HTMLInputElement>) => {
    const { value } = event.target;
    setFilters((current) => ({
      ...current,
      [field]: value.trim(),
    }));
  };

  const handleApplyFilters = () => {
    setAppliedFilters(filters);
  };

  const handleResetFilters = () => {
    setFilters(initialFilters);
    setAppliedFilters(initialFilters);
  };

  const hasActiveFilters = appliedFilters.userId !== '' || appliedFilters.actionType !== '';

  return (
    <div className="card p-6">
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row gap-4 sm:items-center">
          <h2 className="text-xl font-semibold">
            Activity Feed
          </h2>
          <div className="flex-1" />
          <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto">
            <input
              type="text"
              placeholder="User ID"
              className="search-box w-full sm:w-auto"
              value={filters.userId}
              onChange={handleFilterChange('userId')}
              aria-label="Filter by user"
            />
            <input
              type="text"
              placeholder="e.g. test_case.created"
              className="search-box w-full sm:w-auto"
              value={filters.actionType}
              onChange={handleFilterChange('actionType')}
              aria-label="Action type"
            />
            <div className="flex gap-2 justify-end">
              <button
                className="btn-primary"
                onClick={handleApplyFilters}
                disabled={loading && !hasActiveFilters}
              >
                Apply Filters
              </button>
              <button
                className="btn"
                onClick={handleResetFilters}
                disabled={!hasActiveFilters}
              >
                Reset
              </button>
            </div>
          </div>
        </div>

        {hasActiveFilters && (
          <div className="flex gap-2">
            {appliedFilters.userId && <span className="badge">User: {appliedFilters.userId}</span>}
            {appliedFilters.actionType && <span className="badge">Action: {appliedFilters.actionType}</span>}
          </div>
        )}

        {error && (
          <div className="bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] text-[var(--color-status-danger)] px-4 py-3 rounded flex items-start gap-2" role="alert">
            <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {loading && (
          <p data-testid="activity-feed-loading" className="text-[var(--color-content-muted)]">
            Loading recent activity…
          </p>
        )}

        {!loading && events.length === 0 && !error && (
          <p className="text-[var(--color-content-muted)]">
            No activity events match the selected filters. Try adjusting your criteria.
          </p>
        )}

        {!loading && events.length > 0 && (
          <div className="space-y-0">
            {events.map((entry, idx) => (
              <div
                key={entry.id}
                className={`py-4 ${idx !== events.length - 1 ? 'border-b border-[var(--color-border-default)]' : ''}`}
              >
                <div className="space-y-2">
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="font-medium">
                      {entry.actionDescription ?? entry.actionType}
                    </h3>
                    <span className="badge">{entry.actionType}</span>
                    {entry.resourceType && (
                      <span className="badge">{entry.resourceType}{entry.resourceId ? ` · ${entry.resourceId}` : ''}</span>
                    )}
                  </div>
                  <p className="text-sm text-[var(--color-content-muted)]">
                    {formatTimestamp(entry.createdAt)}
                    {entry.ipAddress ? ` · ${entry.ipAddress}` : ''}
                  </p>
                  {Object.keys(entry.metadata).length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(entry.metadata).map(([key, value]) => (
                        <span key={key} className="badge border border-[var(--color-border-default)]">{key}: {String(value)}</span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {pagination && (
          <>
            <hr className="border-[var(--color-border-default)]" />
            <p className="text-xs text-[var(--color-content-muted)]">
              Showing {events.length} of {pagination.returned} recent events (limit {pagination.limit}).
            </p>
            {actionTypeSuggestions.length > 0 && (
              <p className="text-xs text-[var(--color-content-muted)]">
                Action suggestions: {actionTypeSuggestions.join(', ')}
              </p>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default ActivityFeed;
