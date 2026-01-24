import { beforeEach, describe, expect, it, vi } from 'vitest';

import { getActivityFeed } from '../activity.service';

const mockGet = vi.fn();

vi.mock('../api', () => ({
  default: {
    get: (...args: unknown[]) => mockGet(...args),
  },
}));

describe('activity.service', () => {
  beforeEach(() => {
    mockGet.mockReset();
  });

  it('fetches the activity feed with default parameters and normalises the response', async () => {
    mockGet.mockResolvedValue({
      data: {
        items: [
          {
            id: 'event-1',
            user_id: 'user-123',
            action_type: 'test_case.created',
            resource_type: 'test_case',
            resource_id: 'case-456',
            action_description: 'Created test case',
            metadata: {
              summary: 'Initial test case creation',
            },
            ip_address: '192.168.0.10',
            created_at: '2025-03-15T10:00:00Z',
          },
        ],
        pagination: {
          limit: 50,
          offset: 0,
          returned: 1,
          user_id: null,
          action_type: null,
          resource_type: null,
          since: null,
        },
      },
    });

    const result = await getActivityFeed();

    expect(mockGet).toHaveBeenCalledWith('/v1/activity', {
      params: {
        limit: 50,
        offset: 0,
      },
    });

    expect(result).toEqual({
      items: [
        {
          id: 'event-1',
          userId: 'user-123',
          actionType: 'test_case.created',
          resourceType: 'test_case',
          resourceId: 'case-456',
          actionDescription: 'Created test case',
          metadata: {
            summary: 'Initial test case creation',
          },
          ipAddress: '192.168.0.10',
          createdAt: '2025-03-15T10:00:00Z',
        },
      ],
      pagination: {
        limit: 50,
        offset: 0,
        returned: 1,
        userId: null,
        actionType: null,
        resourceType: null,
        since: null,
      },
    });
  });

  it('applies filters when provided', async () => {
    mockGet.mockResolvedValue({
      data: {
        items: [],
        pagination: {
          limit: 25,
          offset: 10,
          returned: 0,
          user_id: 'user-789',
          action_type: 'validation.reviewed',
          resource_type: 'validation',
          since: '2025-03-10T00:00:00Z',
        },
      },
    });

    await getActivityFeed({
      userId: 'user-789',
      actionType: 'validation.reviewed',
      resourceType: 'validation',
      since: '2025-03-10T00:00:00Z',
      limit: 25,
      offset: 10,
    });

    expect(mockGet).toHaveBeenCalledWith('/v1/activity', {
      params: {
        limit: 25,
        offset: 10,
        user_id: 'user-789',
        action_type: 'validation.reviewed',
        resource_type: 'validation',
        since: '2025-03-10T00:00:00Z',
      },
    });
  });
});
