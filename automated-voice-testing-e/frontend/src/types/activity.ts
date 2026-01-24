export interface ActivityLogEntry {
  id: string;
  userId: string;
  actionType: string;
  resourceType: string | null;
  resourceId: string | null;
  actionDescription: string | null;
  metadata: Record<string, unknown>;
  ipAddress: string | null;
  createdAt: string;
}

export interface ActivityFeedPagination {
  limit: number;
  offset: number;
  returned: number;
  userId: string | null;
  actionType: string | null;
  resourceType: string | null;
  since: string | null;
}

export interface ActivityFeed {
  items: ActivityLogEntry[];
  pagination: ActivityFeedPagination;
}

export interface ActivityFeedFilters {
  limit?: number;
  offset?: number;
  userId?: string;
  actionType?: string;
  resourceType?: string;
  since?: string;
}
