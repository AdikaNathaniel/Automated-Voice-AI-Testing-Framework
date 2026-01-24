import apiClient from './api';
import type { ActivityFeed, ActivityFeedFilters } from '../types/activity';

interface ApiActivityLog {
  id: string;
  user_id: string;
  action_type: string;
  resource_type: string | null;
  resource_id: string | null;
  action_description: string | null;
  metadata?: Record<string, unknown>;
  ip_address: string | null;
  created_at: string;
}

interface ApiActivityFeedPagination {
  limit: number;
  offset: number;
  returned: number;
  user_id: string | null;
  action_type: string | null;
  resource_type: string | null;
  since: string | null;
}

interface ApiActivityFeedResponse {
  items: ApiActivityLog[];
  pagination: ApiActivityFeedPagination;
}

const toActivityLogEntry = (payload: ApiActivityLog) => ({
  id: payload.id,
  userId: payload.user_id,
  actionType: payload.action_type,
  resourceType: payload.resource_type,
  resourceId: payload.resource_id,
  actionDescription: payload.action_description,
  metadata: payload.metadata ?? {},
  ipAddress: payload.ip_address,
  createdAt: payload.created_at,
});

const toActivityFeedPagination = (payload: ApiActivityFeedPagination) => ({
  limit: payload.limit,
  offset: payload.offset,
  returned: payload.returned,
  userId: payload.user_id,
  actionType: payload.action_type,
  resourceType: payload.resource_type,
  since: payload.since,
});

const toRequestParams = (filters?: ActivityFeedFilters) => {
  const params: Record<string, string | number> = {
    limit: filters?.limit ?? 50,
    offset: filters?.offset ?? 0,
  };

  if (filters?.userId) {
    params.user_id = filters.userId;
  }

  if (filters?.actionType) {
    params.action_type = filters.actionType;
  }

  if (filters?.resourceType) {
    params.resource_type = filters.resourceType;
  }

  if (filters?.since) {
    params.since = filters.since;
  }

  return params;
};

export class ActivityServiceError extends Error {
  constructor(message: string, public readonly cause?: unknown) {
    super(message);
    this.name = 'ActivityServiceError';
  }
}

export const getActivityFeed = async (filters?: ActivityFeedFilters): Promise<ActivityFeed> => {
  try {
    const response = await apiClient.get<ApiActivityFeedResponse>('/activity', {
      params: toRequestParams(filters),
    });

    return {
      items: response.data.items.map(toActivityLogEntry),
      pagination: toActivityFeedPagination(response.data.pagination),
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Failed to fetch activity feed';
    throw new ActivityServiceError(message, error);
  }
};

export default {
  getActivityFeed,
};
