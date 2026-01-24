import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, CheckCircle, XCircle, Database } from 'lucide-react';

import { approveBaseline, getBaselineHistory } from '../../services/regression.service';
import type {
  BaselineHistoryEntry,
  PendingBaselineSnapshot,
  BaselineHistoryResponse,
} from '../../types/regression';

const EMPTY_HISTORY: BaselineHistoryResponse = {
  history: [],
  pending: null,
};

const BaselineManagement: React.FC = () => {
  const { scriptId } = useParams<{ scriptId: string }>();
  const navigate = useNavigate();

  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<BaselineHistoryEntry[]>([]);
  const [pending, setPending] = useState<PendingBaselineSnapshot | null>(null);
  const [note, setNote] = useState<string>('');
  const [statusMessage, setStatusMessage] = useState<{ severity: 'success' | 'info' | 'error'; text: string } | null>(
    null
  );

  const loadHistory = useCallback(async () => {
    if (!scriptId) {
      setError('Missing script identifier.');
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const response = await getBaselineHistory(scriptId);
      setHistory(response.history);
      setPending(response.pending);
    } catch (err: unknown) {
      setError(err?.message ?? 'Failed to load baseline history.');
      setHistory(EMPTY_HISTORY.history);
      setPending(EMPTY_HISTORY.pending);
    } finally {
      setLoading(false);
    }
  }, [scriptId]);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const handleApprove = useCallback(async () => {
    if (!scriptId || !pending) {
      return;
    }

    try {
      await approveBaseline(scriptId, {
        status: pending.status ?? 'unknown',
        metrics: pending.metrics,
        note: note.trim(),
      });

      setStatusMessage({
        severity: 'success',
        text: 'Baseline approved successfully.',
      });
      setNote('');
      await loadHistory();
    } catch (err: unknown) {
      setStatusMessage({
        severity: 'error',
        text: err?.message ?? 'Failed to approve baseline.',
      });
    }
  }, [loadHistory, note, pending, scriptId]);

  const handleReject = useCallback(() => {
    setPending(null);
    setStatusMessage({
      severity: 'info',
      text: 'Baseline rejected. Candidate dismissed.',
    });
  }, []);

  const historyContent = useMemo(() => {
    if (history.length === 0) {
      return (
        <tr>
          <td colSpan={5} className="px-8 py-8 text-center text-[var(--color-content-muted)]">
            No baselines approved yet.
          </td>
        </tr>
      );
    }

    return history.map((entry) => (
      <tr
        key={entry.version}
        className="border-b border-[var(--color-border-default)] transition-colors hover:bg-[var(--color-interactive-hover)]/50"
      >
        <td className="px-4 py-4 text-sm font-semibold text-[var(--color-content-primary)]">
          Version {entry.version}
        </td>
        <td className="px-4 py-4 text-sm text-[var(--color-content-secondary)] capitalize">
          {entry.status}
        </td>
        <td className="px-4 py-4 text-sm text-[var(--color-content-secondary)]">
          {Object.keys(entry.metrics).length === 0 ? (
            '—'
          ) : (
            <ul className="space-y-1">
              {Object.entries(entry.metrics).map(([metric, value]) => (
                <li key={metric}>
                  {metric}: {value ?? '—'}
                </li>
              ))}
            </ul>
          )}
        </td>
        <td className="px-4 py-4 text-sm text-[var(--color-content-secondary)]">
          {entry.approvedAt ? new Date(entry.approvedAt).toLocaleString() : '—'}
        </td>
        <td className="px-4 py-4 text-sm text-[var(--color-content-secondary)]">
          <div className="space-y-1">
            <p>Reviewer: {entry.approvedBy ? entry.approvedBy : 'Unknown'}</p>
            {entry.note && <p className="text-[var(--color-content-muted)]">Note: {entry.note}</p>}
          </div>
        </td>
      </tr>
    ));
  }, [history]);

  return (
    <>
      {/* Header */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 mb-6 shadow-md">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-[var(--color-content-primary)] flex items-center gap-3 mb-2">
              <Database className="w-6 h-6" style={{ color: '#2A6B6E' }} />
              Baseline Management
            </h1>
            <div className="text-sm text-[var(--color-content-muted)]">
              {scriptId ? `Script: ${scriptId}` : 'No script selected'}
            </div>
          </div>
          <button
            onClick={() => navigate(-1)}
            className="inline-flex items-center px-4 py-2.5 rounded-lg text-sm font-semibold transition-all gap-2 bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)] border border-[var(--color-border-strong)] hover:bg-[var(--color-interactive-active)]"
          >
            <ArrowLeft size={16} />
            Back
          </button>
        </div>
      </div>

      {/* Status Message */}
      {statusMessage && (
        <div
          className={`rounded-lg p-4 mb-5 flex items-start justify-between ${
            statusMessage.severity === 'success'
              ? 'bg-success-light  text-[var(--color-status-success)] border-l-4 border-success '
              : statusMessage.severity === 'error'
              ? 'bg-danger-light  text-[var(--color-status-danger)] border-l-4 border-danger '
              : 'bg-info-light  text-[var(--color-status-info)] border-l-4 border-info '
          }`}
        >
          <div className="flex items-start">
            {statusMessage.severity === 'success' && <CheckCircle className="w-5 h-5 mr-2 flex-shrink-0 mt-0.5" />}
            {statusMessage.severity === 'error' && <XCircle className="w-5 h-5 mr-2 flex-shrink-0 mt-0.5" />}
            {statusMessage.severity === 'info' && <span className="text-xl mr-2">ℹ️</span>}
            <span className="font-semibold">{statusMessage.text}</span>
          </div>
          <button
            onClick={() => setStatusMessage(null)}
            className="text-current hover:opacity-70 transition-opacity"
          >
            <XCircle className="w-5 h-5" />
          </button>
        </div>
      )}

      {/* Loading State */}
      {loading ? (
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm">
          <div className="flex flex-col items-center justify-center p-20">
            <div className="w-12 h-12 border-4 border-[var(--color-border-default)] rounded-full animate-spin mb-4" style={{ borderTopColor: '#2A6B6E' }}></div>
            <div className="text-lg font-semibold text-[var(--color-content-primary)] mb-2">Loading Baselines...</div>
          </div>
        </div>
      ) : error ? (
        <div className="p-4 rounded-lg mb-5 flex items-center gap-3 bg-danger-light  text-[var(--color-status-danger)] border-l-4 border-danger ">
          <div className="text-xl">⚠️</div>
          <div className="flex-1">
            <div className="font-semibold">{error}</div>
          </div>
        </div>
      ) : (
        <>
          {pending && (
            <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-sm p-6 mb-5 space-y-4" data-testid="pending-baseline">
              <h2 className="text-xl font-bold text-[var(--color-content-primary)]">Pending Baseline</h2>

              <div>
                <p className="text-sm font-semibold text-[var(--color-content-muted)] mb-1">Status</p>
                <p className="text-base text-[var(--color-content-primary)] capitalize">{pending.status ?? 'Unknown'}</p>
              </div>

              <div>
                <p className="text-sm font-semibold text-[var(--color-content-muted)] mb-1">Metrics</p>
                {Object.keys(pending.metrics).length === 0 ? (
                  <p className="text-sm text-[var(--color-content-secondary)]">No metrics supplied.</p>
                ) : (
                  <ul className="space-y-1">
                    {Object.entries(pending.metrics).map(([metric, value]) => (
                      <li key={metric} className="text-sm text-[var(--color-content-secondary)]">
                        {metric}: {value ?? '—'}
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              <div>
                <label htmlFor="reviewer-note" className="block text-sm font-semibold text-[var(--color-content-primary)] mb-2">
                  Reviewer note
                </label>
                <textarea
                  id="reviewer-note"
                  value={note}
                  onChange={(event) => setNote(event.target.value)}
                  rows={2}
                  className="w-full px-4 py-2.5 border border-[var(--color-border-strong)] rounded-lg text-sm bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10 resize-none"
                />
              </div>

              <div className="flex gap-3 flex-wrap">
                <button
                  onClick={handleApprove}
                  className="inline-flex items-center px-4 py-2.5 rounded-lg text-sm font-semibold transition-all gap-2 text-white hover:shadow-lg hover:-translate-y-0.5"
                  style={{ background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }}
                >
                  Approve baseline
                </button>
                <button
                  onClick={handleReject}
                  className="inline-flex items-center px-4 py-2.5 rounded-lg text-sm font-semibold transition-all gap-2 bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)] border border-[var(--color-border-strong)] hover:bg-[var(--color-interactive-active)]"
                >
                  Reject baseline
                </button>
              </div>
            </div>
          )}

          <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-sm p-6">
            <h2 className="text-xl font-bold text-[var(--color-content-primary)] mb-4">Baseline History</h2>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }} aria-label="Baseline history">
                <thead>
                  <tr className="border-b-2 border-[var(--color-border-default)] bg-[var(--color-surface-inset)]/50">
                    <th className="px-4 py-4 text-left text-xs font-semibold text-[var(--color-content-secondary)] uppercase tracking-wider">
                      Version
                    </th>
                    <th className="px-4 py-4 text-left text-xs font-semibold text-[var(--color-content-secondary)] uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-4 py-4 text-left text-xs font-semibold text-[var(--color-content-secondary)] uppercase tracking-wider">
                      Metrics
                    </th>
                    <th className="px-4 py-4 text-left text-xs font-semibold text-[var(--color-content-secondary)] uppercase tracking-wider">
                      Approved at
                    </th>
                    <th className="px-4 py-4 text-left text-xs font-semibold text-[var(--color-content-secondary)] uppercase tracking-wider">
                      Reviewer
                    </th>
                  </tr>
                </thead>
                <tbody>{historyContent}</tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </>
  );
};

export default BaselineManagement;
