/**
 * ConfigHistory component.
 *
 * Displays configuration change history with diff rendering between versions.
 */

import React, { useEffect, useMemo, useState } from 'react';
import { AlertCircle, Loader2 } from 'lucide-react';
import { diffJson } from 'diff';

import { getConfigurationHistory } from '../../services/configuration.service';
import type { ConfigurationHistoryEntry } from '../../types/configuration';

type ConfigHistoryProps = {
  configurationId: string;
};

type DiffSegment = {
  value: string;
  added?: boolean;
  removed?: boolean;
};

const formatTimestamp = (timestamp: string) => {
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) {
    return timestamp;
  }
  return date.toLocaleString();
};

const extractChangeSummary = (entry: ConfigurationHistoryEntry) => {
  if (!entry.oldValue && entry.newValue) {
    return 'Created configuration';
  }

  if (entry.oldValue && entry.newValue) {
    if (entry.oldValue.config_key !== entry.newValue.config_key) {
      return `Renamed from ${entry.oldValue.config_key} to ${entry.newValue.config_key}`;
    }

    const oldActive = entry.oldValue.is_active ?? false;
    const newActive = entry.newValue.is_active ?? false;
    if (oldActive !== newActive) {
      return newActive ? 'Activated configuration' : 'Deactivated configuration';
    }

    if (oldActive === newActive && entry.oldValue.config_data && entry.newValue.config_data) {
      const keys = new Set([
        ...Object.keys(entry.oldValue.config_data),
        ...Object.keys(entry.newValue.config_data),
      ]);
      const changedKeys = Array.from(keys).filter(
        (key) => entry.oldValue?.config_data?.[key] !== entry.newValue?.config_data?.[key]
      );
      if (changedKeys.length > 0) {
        return `Updated: ${changedKeys.join(', ')}`;
      }
    }
  }

  return 'Configuration updated';
};

const ConfigHistory: React.FC<ConfigHistoryProps> = ({ configurationId }) => {
  const [entries, setEntries] = useState<ConfigurationHistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedEntryId, setSelectedEntryId] = useState<string | null>(null);
  const [diffMode, setDiffMode] = useState<'json' | 'raw'>('json');

  useEffect(() => {
    let cancelled = false;

    const fetchHistory = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await getConfigurationHistory(configurationId);
        if (cancelled) {
          return;
        }

        setEntries(response.items);
        setSelectedEntryId(response.items[response.items.length - 1]?.id ?? null);
      } catch (err: unknown) {
        if (!cancelled) {
          const baseMessage = 'Unable to load configuration history.';
          const detail = err?.message;
          setError(detail ? `${baseMessage} ${detail}` : baseMessage);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchHistory();

    return () => {
      cancelled = true;
    };
  }, [configurationId]);

  const selectedEntry = useMemo(
    () => entries.find((entry) => entry.id === selectedEntryId) ?? null,
    [entries, selectedEntryId]
  );

  const diffSegments: DiffSegment[] = useMemo(() => {
    if (!selectedEntry) {
      return [];
    }

    const oldData = selectedEntry.oldValue?.config_data ?? {};
    const newData = selectedEntry.newValue?.config_data ?? {};
    return diffJson(oldData, newData);
  }, [selectedEntry]);

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-[var(--color-status-info)]" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] text-[var(--color-status-danger)] px-4 py-3 rounded flex items-start gap-2">
        <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
        <span>{error}</span>
      </div>
    );
  }

  if (entries.length === 0) {
    return (
      <div className="bg-[var(--color-status-info-bg)] border border-[var(--color-status-info)] text-[var(--color-status-info)] px-4 py-3 rounded">
        No history entries available for this configuration.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">
        Change History
      </h2>

      <div className="card">
        <div className="max-h-80 overflow-y-auto">
          {entries.map((entry, idx) => {
            const summary = extractChangeSummary(entry);
            const isSelected = entry.id === selectedEntryId;

            return (
              <React.Fragment key={entry.id}>
                <button
                  className={`w-full text-left p-4 hover:bg-[var(--color-interactive-hover)] transition-colors ${isSelected ? 'bg-[var(--color-status-info-bg)]' : ''}`}
                  onClick={() => setSelectedEntryId(entry.id)}
                >
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-medium">
                        {summary}
                      </span>
                      {entry.changeReason && (
                        <span className="badge bg-[var(--color-status-info-bg)] text-[var(--color-status-info)]">{entry.changeReason}</span>
                      )}
                    </div>
                    <div className="space-y-1">
                      <p className="text-sm text-[var(--color-content-muted)]">
                        {formatTimestamp(entry.createdAt)}
                      </p>
                      {entry.changedBy && (
                        <p className="text-xs text-[var(--color-content-muted)]">
                          Changed by {entry.changedBy}
                        </p>
                      )}
                    </div>
                  </div>
                </button>
                {idx !== entries.length - 1 && <hr className="border-[var(--color-border-default)]" />}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {selectedEntry && (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-4 justify-between sm:items-center">
            <h3 className="text-lg font-semibold">Selected Change</h3>
            <div className="inline-flex rounded-lg border border-[var(--color-border-default)] p-1">
              <button
                className={`px-3 py-1 text-sm rounded ${diffMode === 'json' ? 'bg-[var(--color-status-info)] text-white' : 'text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)]'}`}
                onClick={() => setDiffMode('json')}
              >
                Diff
              </button>
              <button
                className={`px-3 py-1 text-sm rounded ${diffMode === 'raw' ? 'bg-[var(--color-status-info)] text-white' : 'text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)]'}`}
                onClick={() => setDiffMode('raw')}
              >
                JSON Snapshot
              </button>
            </div>
          </div>

          {diffMode === 'json' ? (
            <div className="card p-4">
              {diffSegments.length === 0 ? (
                <div className="bg-[var(--color-status-info-bg)] border border-[var(--color-status-info)] text-[var(--color-status-info)] px-4 py-3 rounded">
                  No changes detected in configuration data.
                </div>
              ) : (
                <pre className="font-mono text-sm whitespace-pre-wrap break-words bg-[var(--color-surface-inset)] p-4 rounded">
                  {diffSegments.map((segment, index) => (
                    <span
                      key={`${segment.value}-${index}`}
                      className={
                        segment.added
                          ? 'text-[var(--color-status-success)] bg-[var(--color-status-success-bg)]'
                          : segment.removed
                          ? 'text-[var(--color-status-danger)] bg-[var(--color-status-danger-bg)]'
                          : ''
                      }
                    >
                      {segment.value}
                    </span>
                  ))}
                </pre>
              )}
            </div>
          ) : (
            <div className="card p-4">
              <h4 className="font-medium mb-2">
                Snapshot After Change
              </h4>
              <pre className="font-mono text-sm whitespace-pre-wrap break-words bg-[var(--color-surface-inset)] p-4 rounded">
                {JSON.stringify(selectedEntry.newValue?.config_data ?? {}, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ConfigHistory;
