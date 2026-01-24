import { describe, it, expect, beforeEach, vi } from 'vitest';

import {
  getRegressions,
  getRegressionComparison,
  getBaselineHistory,
  approveBaseline,
} from '../regression.service';

const mockGet = vi.fn();
const mockPost = vi.fn();

vi.mock('../api', () => ({
  default: {
    get: (...args: unknown[]) => mockGet(...args),
    post: (...args: unknown[]) => mockPost(...args),
  },
}));

describe('regression.service', () => {
  beforeEach(() => {
    mockGet.mockReset();
    mockPost.mockReset();
  });

  it('requests regressions with default parameters and normalises response', async () => {
    mockGet.mockResolvedValueOnce({
      data: {
        summary: {
          total_regressions: 3,
          status_regressions: 2,
          metric_regressions: 1,
        },
        items: [
          {
            script_id: 'a1',
            category: 'status',
            detail: { baseline_status: 'passed', current_status: 'failed' },
            regression_detected_at: '2025-01-01T00:00:00Z',
          },
        ],
      },
    });

    const result = await getRegressions();

    expect(mockGet).toHaveBeenCalledWith('/regressions', {
      params: {
        status: null,
        suite_id: null,
        skip: 0,
        limit: 50,
      },
    });

    expect(result.summary).toEqual({
      totalRegressions: 3,
      statusRegressions: 2,
      metricRegressions: 1,
    });

    expect(result.items).toEqual([
      {
        scriptId: 'a1',
        category: 'status',
        detail: { baseline_status: 'passed', current_status: 'failed' },
        detectedAt: '2025-01-01T00:00:00Z',
      },
    ]);
  });

  it('fetches regression comparison details and normalises the payload', async () => {
    mockGet.mockResolvedValueOnce({
      data: {
        script_id: 'case-1',
        baseline: {
          status: 'passed',
          metrics: {
            accuracy: {
              value: 0.95,
              threshold: 0.9,
            },
          },
          media_uri: 'https://example.com/baseline.wav',
        },
        current: {
          status: 'failed',
          metrics: {
            accuracy: {
              value: 0.82,
            },
          },
          media_uri: null,
        },
        differences: [
          {
            metric: 'accuracy',
            baseline_value: 0.95,
            current_value: 0.82,
            delta: -0.13,
            delta_pct: -13.68,
          },
        ],
      },
    });

    const result = await getRegressionComparison('case-1');

    expect(mockGet).toHaveBeenCalledWith('/v1/regressions/case-1/comparison');

    expect(result).toEqual({
      scriptId: 'case-1',
      baseline: {
        status: 'passed',
        metrics: {
          accuracy: {
            value: 0.95,
            threshold: 0.9,
            unit: null,
          },
        },
        mediaUri: 'https://example.com/baseline.wav',
      },
      current: {
        status: 'failed',
        metrics: {
          accuracy: {
            value: 0.82,
            threshold: null,
            unit: null,
          },
        },
        mediaUri: null,
      },
      differences: [
        {
          metric: 'accuracy',
          baselineValue: 0.95,
          currentValue: 0.82,
          delta: -0.13,
          deltaPercent: -13.68,
        },
      ],
    });
  });

  it('retrieves baseline history and pending snapshot, normalising the payload', async () => {
    mockGet.mockResolvedValueOnce({
      data: {
        history: [
          {
            version: 2,
            status: 'passed',
            metrics: { accuracy: 0.95 },
            approved_at: '2025-02-01T12:30:00Z',
            approved_by: 'user-123',
            note: 'Updated threshold',
          },
        ],
        pending: {
          status: 'failed',
          metrics: { accuracy: 0.8, latency: 320 },
          detected_at: '2025-02-02T09:00:00Z',
          proposed_by: 'user-456',
        },
      },
    });

    const result = await getBaselineHistory('case-1');

    expect(mockGet).toHaveBeenCalledWith('/v1/regressions/case-1/baselines');
    expect(result).toEqual({
      history: [
        {
          version: 2,
          status: 'passed',
          metrics: { accuracy: 0.95 },
          approvedAt: '2025-02-01T12:30:00Z',
          approvedBy: 'user-123',
          note: 'Updated threshold',
        },
      ],
      pending: {
        status: 'failed',
        metrics: { accuracy: 0.8, latency: 320 },
        detectedAt: '2025-02-02T09:00:00Z',
        proposedBy: 'user-456',
      },
    });
  });

  it('approves a baseline using the API and returns the updated record', async () => {
    mockPost.mockResolvedValueOnce({
      data: {
        script_id: 'case-1',
        status: 'failed',
        metrics: { accuracy: 0.8 },
        version: 3,
        approved_at: '2025-02-02T10:00:00Z',
        approved_by: 'user-789',
        note: 'Accepted as new baseline',
      },
    });

    const payload = {
      status: 'failed',
      metrics: { accuracy: 0.8 },
      note: 'Accepted as new baseline',
    };

    const result = await approveBaseline('case-1', payload);

    expect(mockPost).toHaveBeenCalledWith('/v1/regressions/case-1/baseline', payload);
    expect(result).toEqual({
      scriptId: 'case-1',
      status: 'failed',
      metrics: { accuracy: 0.8 },
      version: 3,
      approvedAt: '2025-02-02T10:00:00Z',
      approvedBy: 'user-789',
      note: 'Accepted as new baseline',
    });
  });

  it('passes filter parameters through to API', async () => {
    mockGet.mockResolvedValueOnce({
      data: {
        summary: {
          total_regressions: 0,
          status_regressions: 0,
          metric_regressions: 0,
        },
        items: [],
      },
    });

    await getRegressions({
      status: 'unresolved',
      suiteId: 'suite-123',
      skip: 25,
      limit: 10,
    });

    expect(mockGet).toHaveBeenCalledWith('/regressions', {
      params: {
        status: 'unresolved',
        suite_id: 'suite-123',
        skip: 25,
        limit: 10,
      },
    });
  });
});
