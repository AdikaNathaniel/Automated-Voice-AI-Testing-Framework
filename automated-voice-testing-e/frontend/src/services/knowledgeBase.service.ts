/**
 * Knowledge base service helpers.
 *
 * Phase 3: Added pattern group integration endpoints and filters
 */

import apiClient from './api';
import type {
  KnowledgeBaseArticle,
  KnowledgeBaseArticleCreateInput,
  KnowledgeBaseArticleUpdateInput,
  KnowledgeBaseListParams,
  KnowledgeBaseListResponse,
  KnowledgeBasePagination,
} from '../types/knowledgeBase';

type ApiKnowledgeBaseArticle = {
  id?: string;
  title?: string;
  category?: string | null;
  content?: string;
  content_format?: string;
  author_id?: string;
  is_published?: boolean;
  views?: number;
  created_at?: string;
  updated_at?: string;
  // Phase 3 fields
  pattern_group_id?: string | null;
  source_type?: string;
  tags?: string[];
};

type ApiKnowledgeBasePagination = {
  total?: number;
  skip?: number;
  limit?: number;
  search_query?: string | null;
};

type ApiKnowledgeBaseListResponse = {
  items?: ApiKnowledgeBaseArticle[];
  pagination?: ApiKnowledgeBasePagination;
};

const mapArticle = (article: ApiKnowledgeBaseArticle): KnowledgeBaseArticle => ({
  id: article.id ?? 'unknown',
  title: article.title ?? 'Untitled article',
  category: article.category ?? null,
  content: article.content ?? '',
  contentFormat: article.content_format ?? 'markdown',
  authorId: article.author_id ?? 'unknown',
  isPublished: article.is_published ?? false,
  views: typeof article.views === 'number' ? article.views : 0,
  createdAt: article.created_at ?? '',
  updatedAt: article.updated_at ?? '',
  // Phase 3 fields
  patternGroupId: article.pattern_group_id ?? null,
  sourceType: (article.source_type as KnowledgeBaseArticle['sourceType']) ?? 'manual',
  tags: Array.isArray(article.tags) ? article.tags : [],
});

const mapPagination = (pagination: ApiKnowledgeBasePagination | undefined): KnowledgeBasePagination => ({
  total: typeof pagination?.total === 'number' ? pagination.total : 0,
  skip: typeof pagination?.skip === 'number' ? pagination.skip : 0,
  limit: typeof pagination?.limit === 'number' ? pagination.limit : 20,
  searchQuery: typeof pagination?.search_query === 'string' ? pagination.search_query : null,
});

export const getKnowledgeBaseArticles = async (
  params: KnowledgeBaseListParams = {}
): Promise<KnowledgeBaseListResponse> => {
  const response = await apiClient.get<ApiKnowledgeBaseListResponse>('/knowledge-base', {
    params: {
      q: params.search ?? null,
      category: params.category ?? null,
      is_published: typeof params.isPublished === 'boolean' ? params.isPublished : null,
      author_id: params.authorId ?? null,
      // Phase 3 filters
      source_type: params.sourceType ?? null,
      pattern_group_id: params.patternGroupId ?? null,
      tags: params.tags?.length ? params.tags : null,
      skip: params.skip ?? 0,
      limit: params.limit ?? 20,
    },
  });

  const payload = response.data ?? {};
  const items = Array.isArray(payload.items) ? payload.items : [];

  return {
    items: items.map(mapArticle),
    pagination: mapPagination(payload.pagination),
  };
};

export const getKnowledgeBaseArticle = async (articleId: string): Promise<KnowledgeBaseArticle> => {
  const response = await apiClient.get<ApiKnowledgeBaseArticle>(`/knowledge-base/${articleId}`);
  const payload = response.data ?? {};
  return mapArticle(payload);
};

/**
 * Get KB articles linked to a specific pattern group.
 * Phase 3 endpoint.
 */
export const getArticlesByPatternGroup = async (
  patternGroupId: string,
  params: { skip?: number; limit?: number } = {}
): Promise<KnowledgeBaseListResponse> => {
  const response = await apiClient.get<ApiKnowledgeBaseListResponse>(
    `/knowledge-base/by-pattern/${patternGroupId}`,
    {
      params: {
        skip: params.skip ?? 0,
        limit: params.limit ?? 20,
      },
    }
  );

  const payload = response.data ?? {};
  const items = Array.isArray(payload.items) ? payload.items : [];

  return {
    items: items.map(mapArticle),
    pagination: mapPagination(payload.pagination),
  };
};

/**
 * Generate a KB article from a pattern group.
 * Phase 3 endpoint.
 */
export const generateArticleFromPattern = async (
  patternGroupId: string,
  options: { autoPublish?: boolean } = {}
): Promise<KnowledgeBaseArticle> => {
  const response = await apiClient.post<ApiKnowledgeBaseArticle>(
    `/knowledge-base/generate-from-pattern/${patternGroupId}`,
    null,
    {
      params: {
        auto_publish: options.autoPublish ?? false,
      },
    }
  );
  const data = response.data ?? {};
  return mapArticle(data);
};

const serialiseArticlePayload = (
  payload: KnowledgeBaseArticleCreateInput | KnowledgeBaseArticleUpdateInput,
  defaults?: { contentFormat?: string; isPublished?: boolean }
): Record<string, unknown> => {
  const body: Record<string, unknown> = {};

  const withDefaults = {
    ...(defaults ?? {}),
    ...payload,
  };

  if (withDefaults.title !== undefined) {
    body.title = withDefaults.title;
  }
  if (withDefaults.category !== undefined) {
    body.category = withDefaults.category;
  }
  if (withDefaults.content !== undefined) {
    body.content = withDefaults.content;
  }
  if (withDefaults.contentFormat !== undefined) {
    body.content_format = withDefaults.contentFormat;
  }
  if (withDefaults.isPublished !== undefined) {
    body.is_published = withDefaults.isPublished;
  }
  // Phase 3 fields
  if ('tags' in withDefaults && withDefaults.tags !== undefined) {
    body.tags = withDefaults.tags;
  }
  if ('patternGroupId' in withDefaults && withDefaults.patternGroupId !== undefined) {
    body.pattern_group_id = withDefaults.patternGroupId;
  }
  if ('sourceType' in withDefaults && withDefaults.sourceType !== undefined) {
    body.source_type = withDefaults.sourceType;
  }

  return body;
};

export const createKnowledgeBaseArticle = async (
  payload: KnowledgeBaseArticleCreateInput
): Promise<KnowledgeBaseArticle> => {
  const body = serialiseArticlePayload(payload, {
    contentFormat: payload.contentFormat ?? 'markdown',
    isPublished: payload.isPublished ?? false,
  });

  const response = await apiClient.post<ApiKnowledgeBaseArticle>('/knowledge-base', body);
  const data = response.data ?? {};
  return mapArticle(data);
};

export const updateKnowledgeBaseArticle = async (
  articleId: string,
  payload: KnowledgeBaseArticleUpdateInput
): Promise<KnowledgeBaseArticle> => {
  const body = serialiseArticlePayload(payload);
  const response = await apiClient.patch<ApiKnowledgeBaseArticle>(`/knowledge-base/${articleId}`, body);
  const data = response.data ?? {};
  return mapArticle(data);
};

export const deleteKnowledgeBaseArticle = async (articleId: string): Promise<void> => {
  await apiClient.delete(`/knowledge-base/${articleId}`);
};
