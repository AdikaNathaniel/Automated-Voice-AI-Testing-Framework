/**
 * IntegrationHealthCard Component
 *
 * Displays health status for integrations with visual indicators:
 * - Green: Healthy - configured, connected, no recent errors
 * - Yellow: Degraded - has recent errors or configuration issues
 * - Red: Critical - major issues preventing operation
 * - Gray: Unconfigured - integration not set up
 */

import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, Settings } from 'lucide-react';
import type { IntegrationHealthStatus } from '../../store/slices/integrationHealthSlice';

interface IntegrationHealthCardProps {
  title: string;
  icon: React.ReactNode;
  iconBgColor: string;
  health: IntegrationHealthStatus;
  configPath: string;
}

const formatRelativeTime = (isoString: string | null): string => {
  if (!isoString) return 'Never';

  try {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  } catch {
    return 'Unknown';
  }
};

const getStatusConfig = (status: IntegrationHealthStatus['status']) => {
  switch (status) {
    case 'healthy':
      return {
        icon: <CheckCircle2 className="w-5 h-5" />,
        color: 'text-[var(--color-status-success)]',
        bgColor: 'bg-[var(--color-status-success-bg)]',
        borderColor: 'border-[var(--color-status-success)]',
        label: 'Healthy',
        description: 'Operating normally',
      };
    case 'degraded':
      return {
        icon: <AlertTriangle className="w-5 h-5" />,
        color: 'text-[var(--color-status-warning)]',
        bgColor: 'bg-[var(--color-status-warning-bg)]',
        borderColor: 'border-[var(--color-status-warning)]',
        label: 'Degraded',
        description: 'Experiencing issues',
      };
    case 'critical':
      return {
        icon: <XCircle className="w-5 h-5" />,
        color: 'text-[var(--color-status-danger)]',
        bgColor: 'bg-[var(--color-status-danger-bg)]',
        borderColor: 'border-[var(--color-status-danger)]',
        label: 'Critical',
        description: 'Unable to operate',
      };
    case 'unconfigured':
    default:
      return {
        icon: <Settings className="w-5 h-5" />,
        color: 'text-[var(--color-content-muted)]',
        bgColor: 'bg-[var(--color-surface-inset)]',
        borderColor: 'border-[var(--color-border-default)]',
        label: 'Not Configured',
        description: 'Setup required',
      };
  }
};

const IntegrationHealthCard: React.FC<IntegrationHealthCardProps> = ({
  title,
  icon,
  iconBgColor,
  health,
  configPath,
}) => {
  const statusConfig = getStatusConfig(health.status);

  return (
    <div
      className={`bg-[var(--color-surface-raised)] rounded-xl p-4 shadow-sm border-l-4 ${statusConfig.borderColor} transition-all hover:shadow-md`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className={`${iconBgColor} p-2 rounded-lg`}>
            <div className="text-white">{icon}</div>
          </div>
          <div>
            <h3 className="font-semibold text-[var(--color-content-primary)]">{title}</h3>
            <p className="text-xs text-[var(--color-content-muted)]">
              {health.configured ? 'Configured' : 'Not configured'}
            </p>
          </div>
        </div>

        {/* Status Badge */}
        <div
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full ${statusConfig.bgColor} ${statusConfig.color}`}
        >
          {statusConfig.icon}
          <span className="text-xs font-semibold">{statusConfig.label}</span>
        </div>
      </div>

      {/* Health Details */}
      <div className="space-y-2">
        {/* Last Activity */}
        <div className="flex items-center justify-between text-sm">
          <span className="text-[var(--color-content-muted)]">Last activity</span>
          <span className="text-[var(--color-content-secondary)] font-medium">
            {formatRelativeTime(health.lastSuccessfulOperation)}
          </span>
        </div>

        {/* Connection Status */}
        <div className="flex items-center justify-between text-sm">
          <span className="text-[var(--color-content-muted)]">Connection</span>
          <span
            className={`font-medium ${health.connected ? 'text-[var(--color-status-success)]' : 'text-[var(--color-content-muted)]'}`}
          >
            {health.connected ? 'Connected' : 'Disconnected'}
          </span>
        </div>

        {/* Error Display */}
        {health.lastError && (
          <div className="mt-2 p-2 rounded-lg bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger-bg)]">
            <div className="flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 text-[var(--color-status-danger)] flex-shrink-0 mt-0.5" />
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-[var(--color-status-danger)]">
                  Last Error
                </p>
                <p className="text-xs text-[var(--color-status-danger)] opacity-80 truncate">
                  {health.lastError}
                </p>
                {health.lastErrorAt && (
                  <p className="text-xs text-[var(--color-status-danger)] opacity-60 mt-0.5">
                    {formatRelativeTime(health.lastErrorAt)}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Quick Action */}
      <div className="mt-3 pt-3 border-t border-[var(--color-border-default)]">
        <a
          href={configPath}
          className="text-xs font-medium text-[var(--color-accent-primary)] hover:text-[var(--color-accent-primary-hover)] transition-colors"
        >
          {health.configured ? 'View configuration' : 'Configure now'} &rarr;
        </a>
      </div>
    </div>
  );
};

export default IntegrationHealthCard;
