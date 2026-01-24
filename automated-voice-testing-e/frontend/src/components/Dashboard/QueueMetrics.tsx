/**
 * Queue Metrics Component
 *
 * Displays queue depth, throughput, and SLA metrics for the validation queue.
 * This component visualizes:
 * - Queue depth (pending, claimed counts)
 * - Throughput metrics (validations completed in various time windows)
 * - SLA metrics (average time to claim, complete, and total time)
 *
 * TODOS.md Section 7: "Queue depth, throughput, and SLA metrics visible on dashboards"
 *
 * @module components/Dashboard/QueueMetrics
 */

import React from 'react';
import { Clock, Gauge, Timer } from 'lucide-react';

interface ThroughputMetrics {
  last_hour: number;
  last_24_hours: number;
  last_7_days: number;
  avg_per_hour: number;
}

interface SLAMetrics {
  avg_time_to_claim_seconds: number | null;
  avg_time_to_complete_seconds: number | null;
  avg_total_time_seconds: number | null;
}

interface QueueStats {
  pendingCount: number;
  claimedCount: number;
  completedCount: number;
  totalCount: number;
  throughput: ThroughputMetrics;
  sla: SLAMetrics;
  priorityDistribution: Record<string, number>;
  languageDistribution: Record<string, number>;
}

interface QueueMetricsProps {
  stats: QueueStats | null;
  loading?: boolean;
  error?: string | null;
}

/**
 * Format seconds to minutes with 1 decimal place
 */
const formatSecondsToMinutes = (seconds: number | null): string => {
  if (seconds === null || seconds === undefined) {
    return 'N/A';
  }
  return (seconds / 60).toFixed(1);
};

/**
 * QueueMetrics Component
 *
 * Displays comprehensive queue metrics including depth, throughput, and SLA.
 */
const QueueMetrics: React.FC<QueueMetricsProps> = ({ stats, loading, error }) => {
  // Loading state
  if (loading) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="spinner"></div>
        <p className="ml-4 text-base">
          Loading queue metrics...
        </p>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="p-4 bg-[var(--color-status-danger-bg)] rounded-lg">
        <p className="text-[var(--color-status-danger)]">{error}</p>
      </div>
    );
  }

  // No stats available
  if (!stats) {
    return (
      <div className="p-4 bg-[var(--color-surface-inset)] rounded-lg">
        <p className="text-[var(--color-content-secondary)]">
          Queue metrics not available
        </p>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">
        Queue Metrics
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Queue Depth Card */}
        <div className="card">
          <div className="flex items-center mb-4">
            <Clock className="w-5 h-5 text-[#2A6B6E] mr-2" />
            <h3 className="text-lg font-semibold">Queue Depth</h3>
          </div>
          <div>
            <p className="text-3xl font-bold">
              {stats.pendingCount}
            </p>
            <p className="text-[var(--color-content-secondary)] mb-4">
              Pending
            </p>
            <p className="text-2xl font-bold mt-4">
              {stats.claimedCount}
            </p>
            <p className="text-[var(--color-content-secondary)]">Claimed</p>
          </div>
        </div>

        {/* Throughput Card */}
        <div className="card">
          <div className="flex items-center mb-4">
            <Gauge className="w-5 h-5 text-[#2A6B6E] mr-2" />
            <h3 className="text-lg font-semibold">Throughput</h3>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <p className="text-2xl font-bold">
                {stats.throughput.last_hour}
              </p>
              <p className="text-[var(--color-content-secondary)] text-sm">
                Last Hour
              </p>
            </div>
            <div>
              <p className="text-2xl font-bold">
                {stats.throughput.last_24_hours}
              </p>
              <p className="text-[var(--color-content-secondary)] text-sm">
                Last 24 Hours
              </p>
            </div>
            <div className="mt-2">
              <p className="text-2xl font-bold">
                {stats.throughput.last_7_days}
              </p>
              <p className="text-[var(--color-content-secondary)] text-sm">
                Last 7 Days
              </p>
            </div>
            <div className="mt-2">
              <p className="text-2xl font-bold">
                {stats.throughput.avg_per_hour.toFixed(2)}
              </p>
              <p className="text-[var(--color-content-secondary)] text-sm">
                Avg per Hour
              </p>
            </div>
          </div>
        </div>

        {/* SLA Metrics Card */}
        <div className="card">
          <div className="flex items-center mb-4">
            <Timer className="w-5 h-5 text-[#2A6B6E] mr-2" />
            <h3 className="text-lg font-semibold">SLA Metrics</h3>
          </div>
          <div>
            <p className="text-2xl font-bold">
              {formatSecondsToMinutes(stats.sla.avg_time_to_claim_seconds)}
            </p>
            <p className="text-[var(--color-content-secondary)] text-sm mb-4">
              Avg Time to Claim (min)
            </p>

            <p className="text-2xl font-bold mt-4">
              {formatSecondsToMinutes(stats.sla.avg_time_to_complete_seconds)}
            </p>
            <p className="text-[var(--color-content-secondary)] text-sm mb-4">
              Avg Time to Complete (min)
            </p>

            <p className="text-2xl font-bold mt-4">
              {formatSecondsToMinutes(stats.sla.avg_total_time_seconds)}
            </p>
            <p className="text-[var(--color-content-secondary)] text-sm">
              Avg Total Time (min)
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QueueMetrics;
