/**
 * PipelineView component
 *
 * Visual representation of CI/CD pipeline stages.
 */

import React from 'react';
import { AlertCircle, Info } from 'lucide-react';

export type PipelineStageStatus = 'pending' | 'running' | 'success' | 'failed';

export interface PipelineStage {
  id: string;
  name: string;
  status: PipelineStageStatus;
  durationSeconds: number | null;
}

export interface PipelineViewProps {
  stages: PipelineStage[];
  error?: string | null;
}

const formatDuration = (durationSeconds: number | null): string => {
  if (durationSeconds == null || Number.isNaN(durationSeconds)) {
    return '—';
  }

  const totalSeconds = Math.max(0, Math.round(durationSeconds));
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;

  if (minutes === 0) {
    return `${seconds}s`;
  }

  return `${minutes}m ${seconds}s`;
};

const statusColor = (status: PipelineStageStatus) => {
  switch (status) {
    case 'success':
      return 'bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]';
    case 'failed':
      return 'bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)]';
    case 'running':
      return 'bg-[var(--color-status-info-bg)] text-[var(--color-status-info)]';
    case 'pending':
    default:
      return 'bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)]';
  }
};

const PipelineView: React.FC<PipelineViewProps> = ({ stages, error = null }) => {
  return (
    <div className="card p-6 border border-[var(--color-border-default)] rounded-lg">
      <div className="space-y-6">
        <div>
          <h2 className="text-xl font-semibold">
            Pipeline Stages
          </h2>
          <p className="text-sm text-[var(--color-content-muted)]">
            Track the progress of each stage in the CI/CD pipeline.
          </p>
        </div>

        {error ? (
          <div className="bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] text-[var(--color-status-danger)] px-4 py-3 rounded flex items-start gap-2">
            <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        ) : stages.length === 0 ? (
          <div className="bg-[var(--color-status-info-bg)] border border-[var(--color-status-info)] text-[var(--color-status-info)] px-4 py-3 rounded flex items-start gap-2">
            <Info className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <span>No pipeline stages available. Configure your pipeline to visualize the execution flow.</span>
          </div>
        ) : (
          <div className="flex flex-wrap gap-6">
            {stages.map((stage, index) => (
              <div
                key={stage.id}
                className="min-w-[180px] flex-1 rounded-lg border border-[var(--color-border-default)] p-4"
              >
                <div className="space-y-3">
                  <h3 className="font-medium">{stage.name}</h3>
                  <span
                    className={`badge capitalize inline-block ${statusColor(stage.status)}`}
                    data-testid={`pipeline-stage-status-${stage.id}`}
                  >
                    {stage.status}
                  </span>
                  <p className="text-sm text-[var(--color-content-muted)]">
                    Duration: {formatDuration(stage.durationSeconds)}
                  </p>
                  {index !== stages.length - 1 && (
                    <p className="text-xs text-[var(--color-content-muted)] pt-2">
                      ↓ Next stage
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default PipelineView;
