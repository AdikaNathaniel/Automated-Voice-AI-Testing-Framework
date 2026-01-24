/**
 * SystemHealth Widget (TASK-134)
 *
 * Dashboard widget displaying system health status:
 * - API status
 * - Database status
 * - Queue status
 *
 * Features:
 * - Material-UI Card component
 * - Color-coded status indicators
 * - Real-time status display
 */

import React from 'react';
import { Circle } from 'lucide-react';

/**
 * System component status type
 */
type SystemStatus = 'healthy' | 'degraded' | 'down';

/**
 * System component interface
 */
interface SystemComponent {
  /**
   * Component name
   */
  name: string;

  /**
   * Component status
   */
  status: SystemStatus;

  /**
   * Optional status message
   */
  message?: string;
}

/**
 * Get status color class based on system status
 */
const getStatusColorClass = (status: SystemStatus): string => {
  switch (status) {
    case 'healthy':
      return 'text-[var(--color-status-success)]';
    case 'degraded':
      return 'text-[var(--color-status-warning)]';
    case 'down':
      return 'text-[var(--color-status-danger)]';
    default:
      return 'text-[var(--color-status-danger)]';
  }
};

/**
 * Get status badge class based on system status
 */
const getStatusBadgeClass = (status: SystemStatus): string => {
  switch (status) {
    case 'healthy':
      return 'badge badge-success';
    case 'degraded':
      return 'badge badge-warning';
    case 'down':
      return 'badge badge-danger';
    default:
      return 'badge bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)]';
  }
};

/**
 * Get status label based on system status
 */
const getStatusLabel = (status: SystemStatus): string => {
  switch (status) {
    case 'healthy':
      return 'Healthy';
    case 'degraded':
      return 'Degraded';
    case 'down':
      return 'Down';
    default:
      return 'Unknown';
  }
};

/**
 * Mock system health data
 * TODO: Replace with API call
 */
const mockSystemHealth: SystemComponent[] = [
  {
    name: 'API',
    status: 'healthy',
    message: 'All endpoints responding',
  },
  {
    name: 'Database',
    status: 'healthy',
    message: 'Connection pool: 5/10',
  },
  {
    name: 'Queue',
    status: 'healthy',
    message: 'Processing normally',
  },
];

/**
 * SystemHealth widget component
 *
 * Displays the health status of key system components.
 * Shows color-coded indicators for API, database, and queue status.
 *
 * @returns System health widget
 *
 * @example
 * ```tsx
 * <SystemHealth />
 * ```
 */
const SystemHealth: React.FC = () => {
  return (
    <div className="card h-full">
      <h2 className="card-title mb-4">
        System Health
      </h2>

      <div className="flex flex-col">
        {mockSystemHealth.map((component, index) => (
          <div
            key={component.name}
            className={`py-3 ${index > 0 ? 'border-t border-[var(--color-border-subtle)]' : ''}`}
          >
            <div className="flex items-center gap-4 w-full">
              {/* Status Icon */}
              <Circle
                className={`w-3 h-3 fill-current ${getStatusColorClass(component.status)}`}
              />

              {/* Component Info */}
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-base font-medium text-[var(--color-content-primary)]">
                    {component.name}
                  </span>
                  <span className={getStatusBadgeClass(component.status)}>
                    {getStatusLabel(component.status)}
                  </span>
                </div>
                {component.message && (
                  <p className="text-sm text-[var(--color-content-secondary)]">{component.message}</p>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SystemHealth;
