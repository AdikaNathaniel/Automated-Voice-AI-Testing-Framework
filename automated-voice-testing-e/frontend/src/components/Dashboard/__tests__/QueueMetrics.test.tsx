/**
 * Tests for QueueMetrics Component
 *
 * Tests the component that displays queue depth, throughput, and SLA metrics
 * for the validation queue dashboard.
 *
 * TODOS.md Section 7: "Queue depth, throughput, and SLA metrics visible on dashboards"
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import QueueMetrics from '../QueueMetrics';

describe('QueueMetrics', () => {
  describe('Component Structure', () => {
    it('renders without crashing', () => {
      const stats = {
        pendingCount: 10,
        claimedCount: 5,
        completedCount: 100,
        totalCount: 115,
        throughput: {
          last_hour: 5,
          last_24_hours: 80,
          last_7_days: 500,
          avg_per_hour: 2.98,
        },
        sla: {
          avg_time_to_claim_seconds: 120.5,
          avg_time_to_complete_seconds: 450.0,
          avg_total_time_seconds: 570.5,
        },
        priorityDistribution: {},
        languageDistribution: {},
      };

      render(<QueueMetrics stats={stats} />);

      // Component should render
      expect(screen.getByText(/Queue Metrics/i)).toBeInTheDocument();
    });

    it('displays pending count', () => {
      const stats = {
        pendingCount: 25,
        claimedCount: 5,
        completedCount: 100,
        totalCount: 130,
        throughput: {
          last_hour: 5,
          last_24_hours: 80,
          last_7_days: 500,
          avg_per_hour: 2.98,
        },
        sla: {
          avg_time_to_claim_seconds: 120.5,
          avg_time_to_complete_seconds: 450.0,
          avg_total_time_seconds: 570.5,
        },
        priorityDistribution: {},
        languageDistribution: {},
      };

      render(<QueueMetrics stats={stats} />);

      // Should display pending count
      expect(screen.getByText('25')).toBeInTheDocument();
      expect(screen.getByText(/Pending/i)).toBeInTheDocument();
    });

    it('displays claimed count', () => {
      const stats = {
        pendingCount: 10,
        claimedCount: 15,
        completedCount: 100,
        totalCount: 125,
        throughput: {
          last_hour: 5,
          last_24_hours: 80,
          last_7_days: 500,
          avg_per_hour: 2.98,
        },
        sla: {
          avg_time_to_claim_seconds: 120.5,
          avg_time_to_complete_seconds: 450.0,
          avg_total_time_seconds: 570.5,
        },
        priorityDistribution: {},
        languageDistribution: {},
      };

      render(<QueueMetrics stats={stats} />);

      // Should display claimed count
      expect(screen.getByText('15')).toBeInTheDocument();
      expect(screen.getByText(/Claimed/i)).toBeInTheDocument();
    });
  });

  describe('Throughput Metrics', () => {
    it('displays throughput section', () => {
      const stats = {
        pendingCount: 10,
        claimedCount: 5,
        completedCount: 100,
        totalCount: 115,
        throughput: {
          last_hour: 5,
          last_24_hours: 80,
          last_7_days: 500,
          avg_per_hour: 2.98,
        },
        sla: {
          avg_time_to_claim_seconds: 120.5,
          avg_time_to_complete_seconds: 450.0,
          avg_total_time_seconds: 570.5,
        },
        priorityDistribution: {},
        languageDistribution: {},
      };

      render(<QueueMetrics stats={stats} />);

      // Should display throughput section
      expect(screen.getByText(/Throughput/i)).toBeInTheDocument();
    });

    it('displays validations completed in last hour', () => {
      const stats = {
        pendingCount: 10,
        claimedCount: 5,
        completedCount: 100,
        totalCount: 115,
        throughput: {
          last_hour: 8,
          last_24_hours: 80,
          last_7_days: 500,
          avg_per_hour: 2.98,
        },
        sla: {
          avg_time_to_claim_seconds: 120.5,
          avg_time_to_complete_seconds: 450.0,
          avg_total_time_seconds: 570.5,
        },
        priorityDistribution: {},
        languageDistribution: {},
      };

      render(<QueueMetrics stats={stats} />);

      // Should display last hour count
      expect(screen.getByText('8')).toBeInTheDocument();
      expect(screen.getByText(/Last Hour/i)).toBeInTheDocument();
    });

    it('displays validations completed in last 24 hours', () => {
      const stats = {
        pendingCount: 10,
        claimedCount: 5,
        completedCount: 100,
        totalCount: 115,
        throughput: {
          last_hour: 5,
          last_24_hours: 120,
          last_7_days: 500,
          avg_per_hour: 2.98,
        },
        sla: {
          avg_time_to_claim_seconds: 120.5,
          avg_time_to_complete_seconds: 450.0,
          avg_total_time_seconds: 570.5,
        },
        priorityDistribution: {},
        languageDistribution: {},
      };

      render(<QueueMetrics stats={stats} />);

      // Should display last 24 hours count
      expect(screen.getByText('120')).toBeInTheDocument();
      expect(screen.getByText(/Last 24 Hours/i)).toBeInTheDocument();
    });

    it('displays validations completed in last 7 days', () => {
      const stats = {
        pendingCount: 10,
        claimedCount: 5,
        completedCount: 100,
        totalCount: 115,
        throughput: {
          last_hour: 5,
          last_24_hours: 80,
          last_7_days: 750,
          avg_per_hour: 4.46,
        },
        sla: {
          avg_time_to_claim_seconds: 120.5,
          avg_time_to_complete_seconds: 450.0,
          avg_total_time_seconds: 570.5,
        },
        priorityDistribution: {},
        languageDistribution: {},
      };

      render(<QueueMetrics stats={stats} />);

      // Should display last 7 days count
      expect(screen.getByText('750')).toBeInTheDocument();
      expect(screen.getByText(/Last 7 Days/i)).toBeInTheDocument();
    });

    it('displays average validations per hour', () => {
      const stats = {
        pendingCount: 10,
        claimedCount: 5,
        completedCount: 100,
        totalCount: 115,
        throughput: {
          last_hour: 5,
          last_24_hours: 80,
          last_7_days: 500,
          avg_per_hour: 3.42,
        },
        sla: {
          avg_time_to_claim_seconds: 120.5,
          avg_time_to_complete_seconds: 450.0,
          avg_total_time_seconds: 570.5,
        },
        priorityDistribution: {},
        languageDistribution: {},
      };

      render(<QueueMetrics stats={stats} />);

      // Should display average per hour
      expect(screen.getByText(/3\.42/)).toBeInTheDocument();
      expect(screen.getByText(/Avg.*Hour/i)).toBeInTheDocument();
    });
  });

  describe('SLA Metrics', () => {
    it('displays SLA section', () => {
      const stats = {
        pendingCount: 10,
        claimedCount: 5,
        completedCount: 100,
        totalCount: 115,
        throughput: {
          last_hour: 5,
          last_24_hours: 80,
          last_7_days: 500,
          avg_per_hour: 2.98,
        },
        sla: {
          avg_time_to_claim_seconds: 120.5,
          avg_time_to_complete_seconds: 450.0,
          avg_total_time_seconds: 570.5,
        },
        priorityDistribution: {},
        languageDistribution: {},
      };

      render(<QueueMetrics stats={stats} />);

      // Should display SLA section
      expect(screen.getByText(/SLA/i)).toBeInTheDocument();
    });

    it('displays average time to claim in minutes', () => {
      const stats = {
        pendingCount: 10,
        claimedCount: 5,
        completedCount: 100,
        totalCount: 115,
        throughput: {
          last_hour: 5,
          last_24_hours: 80,
          last_7_days: 500,
          avg_per_hour: 2.98,
        },
        sla: {
          avg_time_to_claim_seconds: 180.0,  // 3 minutes
          avg_time_to_complete_seconds: 450.0,
          avg_total_time_seconds: 630.0,
        },
        priorityDistribution: {},
        languageDistribution: {},
      };

      render(<QueueMetrics stats={stats} />);

      // Should display time to claim in minutes (180 seconds = 3 minutes)
      expect(screen.getByText(/3\.0/)).toBeInTheDocument();
      expect(screen.getByText(/Time to Claim/i)).toBeInTheDocument();
    });

    it('displays average time to complete in minutes', () => {
      const stats = {
        pendingCount: 10,
        claimedCount: 5,
        completedCount: 100,
        totalCount: 115,
        throughput: {
          last_hour: 5,
          last_24_hours: 80,
          last_7_days: 500,
          avg_per_hour: 2.98,
        },
        sla: {
          avg_time_to_claim_seconds: 120.5,
          avg_time_to_complete_seconds: 600.0,  // 10 minutes
          avg_total_time_seconds: 720.5,
        },
        priorityDistribution: {},
        languageDistribution: {},
      };

      render(<QueueMetrics stats={stats} />);

      // Should display time to complete in minutes (600 seconds = 10 minutes)
      expect(screen.getByText(/10\.0/)).toBeInTheDocument();
      expect(screen.getByText(/Time to Complete/i)).toBeInTheDocument();
    });

    it('displays average total time in minutes', () => {
      const stats = {
        pendingCount: 10,
        claimedCount: 5,
        completedCount: 100,
        totalCount: 115,
        throughput: {
          last_hour: 5,
          last_24_hours: 80,
          last_7_days: 500,
          avg_per_hour: 2.98,
        },
        sla: {
          avg_time_to_claim_seconds: 120.5,
          avg_time_to_complete_seconds: 450.0,
          avg_total_time_seconds: 900.0,  // 15 minutes
        },
        priorityDistribution: {},
        languageDistribution: {},
      };

      render(<QueueMetrics stats={stats} />);

      // Should display total time in minutes (900 seconds = 15 minutes)
      expect(screen.getByText(/15\.0/)).toBeInTheDocument();
      expect(screen.getByText(/Total Time/i)).toBeInTheDocument();
    });

    it('handles null SLA values gracefully', () => {
      const stats = {
        pendingCount: 10,
        claimedCount: 5,
        completedCount: 0,  // No completed validations yet
        totalCount: 15,
        throughput: {
          last_hour: 0,
          last_24_hours: 0,
          last_7_days: 0,
          avg_per_hour: 0.0,
        },
        sla: {
          avg_time_to_claim_seconds: null,
          avg_time_to_complete_seconds: null,
          avg_total_time_seconds: null,
        },
        priorityDistribution: {},
        languageDistribution: {},
      };

      render(<QueueMetrics stats={stats} />);

      // Should display N/A or similar for null values
      const naElements = screen.getAllByText(/N\/A|—/i);
      expect(naElements.length).toBeGreaterThan(0);
    });
  });

  describe('Loading and Error States', () => {
    it('displays loading state', () => {
      render(<QueueMetrics stats={null} loading={true} />);

      // Should show loading indicator
      expect(screen.getByText(/Loading/i)).toBeInTheDocument();
    });

    it('displays error state', () => {
      render(<QueueMetrics stats={null} error="Failed to load queue metrics" />);

      // Should show error message
      expect(screen.getByText(/Failed to load/i)).toBeInTheDocument();
    });
  });
});
