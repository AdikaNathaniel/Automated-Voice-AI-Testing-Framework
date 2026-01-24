import React from 'react';
import { AlertCircle, Info } from 'lucide-react';
import type { PipelineStatus } from '../../types/dashboard';

export type CICDStatusProps = {
  pipelines: PipelineStatus[];
  incidents: number;
  loading?: boolean;
  error?: string | null;
  onRetry?: () => void;
};

const formatDateTime = (value: string | null): string => {
  if (!value) return 'No runs recorded';
  const date = new Date(value);
  return `Last run ${date.toLocaleString()}`;
};

const getBadgeClass = (status: string): string => {
  switch (status) {
    case 'success':
      return 'badge badge-success';
    case 'running':
      return 'badge badge-info';
    case 'failed':
      return 'badge badge-danger';
    default:
      return 'badge bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)]';
  }
};

const CICDStatus: React.FC<CICDStatusProps> = ({
  pipelines,
  incidents,
  loading = false,
  error = null,
  onRetry,
}) => {
  if (loading) {
    return (
      <div className="card">
        <div
          className="flex items-center justify-center py-4"
          data-testid="cicd-status-loading"
        >
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="flex items-start gap-3 p-4 bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)] rounded-lg border border-[var(--color-status-danger)]">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm">{error}</p>
          </div>
          {onRetry && (
            <button
              onClick={onRetry}
              className="text-sm font-medium text-[var(--color-status-danger)] hover:opacity-80"
            >
              Retry
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="card h-full">
      <div className="flex flex-col gap-4">
        <h2 className="card-title">
          CI/CD Integration Status
        </h2>
        <p className="text-sm text-[var(--color-content-secondary)]">
          Active incidents: {incidents}
        </p>

        {pipelines.length === 0 ? (
          <div className="flex items-start gap-3 p-4 bg-[var(--color-status-info-bg)] text-[var(--color-status-info)] rounded-lg border border-[var(--color-status-info)]">
            <Info className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <p className="text-sm">
              CI/CD pipeline data is not available yet. Connect your integration to see live status.
            </p>
          </div>
        ) : (
          <div className="flex flex-col">
            {pipelines.map((pipeline, index) => (
              <React.Fragment key={pipeline.id}>
                <div
                  className="flex justify-between items-start py-3"
                  data-testid={`pipeline-item-${pipeline.id}`}
                >
                  <div className="flex-1">
                    <p className="text-sm font-medium text-[var(--color-content-primary)]">{pipeline.name}</p>
                    <p className="text-xs text-[var(--color-content-muted)]">{formatDateTime(pipeline.lastRunAt)}</p>
                  </div>
                  <span
                    className={getBadgeClass(pipeline.status)}
                    data-testid={`pipeline-status-${pipeline.id}`}
                  >
                    {pipeline.status}
                  </span>
                </div>
                {index !== pipelines.length - 1 && <div className="border-t border-[var(--color-border-default)]"></div>}
              </React.Fragment>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default CICDStatus;
