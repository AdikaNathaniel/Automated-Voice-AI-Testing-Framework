import { beforeEach, describe, expect, it, vi } from 'vitest';

import { getDefects, getDefectDetail } from '../defect.service';

const mockGet = vi.fn();

vi.mock('../api', () => ({
  default: {
    get: (...args: unknown[]) => mockGet(...args),
  },
}));

describe('defect.service', () => {
  beforeEach(() => {
    mockGet.mockReset();
  });

  describe('getDefects', () => {
    it('fetches defects with default parameters', async () => {
      mockGet.mockResolvedValue({
        data: {
          total: 1,
          items: [
            {
              id: 'defect-1',
              script_id: 'case-123',
              execution_id: 'exec-456',
              severity: 'high',
              category: 'accuracy',
              title: 'Test Defect',
              description: 'A test defect description',
              language_code: 'en',
              detected_at: '2025-03-15T10:00:00Z',
              status: 'open',
              assigned_to: 'user-789',
              resolved_at: null,
              created_at: '2025-03-15T10:00:00Z',
            },
          ],
        },
      });

      const result = await getDefects();

      expect(mockGet).toHaveBeenCalledWith('/defects', {
        params: {
          status: null,
          severity: null,
          category: null,
          skip: 0,
          limit: 25,
        },
      });

      expect(result).toEqual({
        total: 1,
        items: [
          {
            id: 'defect-1',
            scriptId: 'case-123',
            executionId: 'exec-456',
            severity: 'high',
            category: 'accuracy',
            title: 'Test Defect',
            description: 'A test defect description',
            languageCode: 'en',
            detectedAt: '2025-03-15T10:00:00Z',
            status: 'open',
            assignedTo: 'user-789',
            resolvedAt: null,
            createdAt: '2025-03-15T10:00:00Z',
          },
        ],
      });
    });

    it('applies filters when provided', async () => {
      mockGet.mockResolvedValue({
        data: {
          total: 0,
          items: [],
        },
      });

      await getDefects({
        status: 'resolved',
        severity: 'critical',
        category: 'performance',
        page: 2,
        pageSize: 10,
      });

      expect(mockGet).toHaveBeenCalledWith('/defects', {
        params: {
          status: 'resolved',
          severity: 'critical',
          category: 'performance',
          skip: 10,
          limit: 10,
        },
      });
    });

    it('handles null optional fields', async () => {
      mockGet.mockResolvedValue({
        data: {
          total: 1,
          items: [
            {
              id: 'defect-2',
              script_id: 'case-456',
              execution_id: null,
              severity: 'low',
              category: 'other',
              title: 'Minimal Defect',
              description: null,
              language_code: null,
              detected_at: '2025-03-16T12:00:00Z',
              status: 'open',
              assigned_to: null,
              resolved_at: null,
              created_at: '2025-03-16T12:00:00Z',
            },
          ],
        },
      });

      const result = await getDefects();

      expect(result.items[0]).toEqual({
        id: 'defect-2',
        scriptId: 'case-456',
        executionId: null,
        severity: 'low',
        category: 'other',
        title: 'Minimal Defect',
        description: null,
        languageCode: null,
        detectedAt: '2025-03-16T12:00:00Z',
        status: 'open',
        assignedTo: null,
        resolvedAt: null,
        createdAt: '2025-03-16T12:00:00Z',
      });
    });

    it('calculates correct skip value for pagination', async () => {
      mockGet.mockResolvedValue({
        data: { total: 0, items: [] },
      });

      await getDefects({ page: 5, pageSize: 20 });

      expect(mockGet).toHaveBeenCalledWith('/defects', {
        params: {
          status: null,
          severity: null,
          category: null,
          skip: 80,
          limit: 20,
        },
      });
    });
  });

  describe('getDefectDetail', () => {
    it('fetches defect detail by id', async () => {
      mockGet.mockResolvedValue({
        data: {
          id: 'defect-1',
          script_id: 'case-123',
          execution_id: 'exec-456',
          severity: 'high',
          category: 'accuracy',
          title: 'Test Defect',
          description: 'Detailed description',
          language_code: 'en',
          detected_at: '2025-03-15T10:00:00Z',
          status: 'open',
          assigned_to: 'user-789',
          resolved_at: null,
          created_at: '2025-03-15T10:00:00Z',
          related_executions: [
            {
              id: 'exec-1',
              status: 'failed',
              suite_run_id: 'run-123',
              executed_at: '2025-03-15T09:00:00Z',
            },
          ],
          comments: [
            {
              id: 'comment-1',
              author: 'John Doe',
              message: 'Looking into this',
              created_at: '2025-03-15T11:00:00Z',
            },
          ],
        },
      });

      const result = await getDefectDetail('defect-1');

      expect(mockGet).toHaveBeenCalledWith('/defects/defect-1');

      expect(result).toEqual({
        id: 'defect-1',
        scriptId: 'case-123',
        executionId: 'exec-456',
        severity: 'high',
        category: 'accuracy',
        title: 'Test Defect',
        description: 'Detailed description',
        languageCode: 'en',
        detectedAt: '2025-03-15T10:00:00Z',
        status: 'open',
        assignedTo: 'user-789',
        resolvedAt: null,
        createdAt: '2025-03-15T10:00:00Z',
        relatedExecutions: [
          {
            id: 'exec-1',
            status: 'failed',
            suiteRunId: 'run-123',
            executedAt: '2025-03-15T09:00:00Z',
          },
        ],
        comments: [
          {
            id: 'comment-1',
            author: 'John Doe',
            message: 'Looking into this',
            createdAt: '2025-03-15T11:00:00Z',
          },
        ],
      });
    });

    it('handles empty related executions and comments', async () => {
      mockGet.mockResolvedValue({
        data: {
          id: 'defect-2',
          script_id: 'case-456',
          execution_id: null,
          severity: 'low',
          category: 'other',
          title: 'Simple Defect',
          description: null,
          language_code: null,
          detected_at: '2025-03-16T12:00:00Z',
          status: 'open',
          assigned_to: null,
          resolved_at: null,
          created_at: '2025-03-16T12:00:00Z',
        },
      });

      const result = await getDefectDetail('defect-2');

      expect(result.relatedExecutions).toEqual([]);
      expect(result.comments).toEqual([]);
    });

    it('handles null test_run_id in related executions', async () => {
      mockGet.mockResolvedValue({
        data: {
          id: 'defect-3',
          script_id: 'case-789',
          execution_id: null,
          severity: 'medium',
          category: 'accuracy',
          title: 'Defect with orphan execution',
          description: null,
          language_code: null,
          detected_at: '2025-03-17T08:00:00Z',
          status: 'open',
          assigned_to: null,
          resolved_at: null,
          created_at: '2025-03-17T08:00:00Z',
          related_executions: [
            {
              id: 'exec-2',
              status: 'failed',
              suite_run_id: null,
              executed_at: null,
            },
          ],
          comments: [],
        },
      });

      const result = await getDefectDetail('defect-3');

      expect(result.relatedExecutions[0]).toEqual({
        id: 'exec-2',
        status: 'failed',
        suiteRunId: null,
        executedAt: null,
      });
    });
  });
});
