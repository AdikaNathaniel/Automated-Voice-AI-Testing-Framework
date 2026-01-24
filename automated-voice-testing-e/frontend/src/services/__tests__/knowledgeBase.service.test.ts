import { describe, it, expect, beforeEach, vi } from 'vitest';

import {
  createKnowledgeBaseArticle,
  getKnowledgeBaseArticle,
  getKnowledgeBaseArticles,
  updateKnowledgeBaseArticle,
} from '../knowledgeBase.service';

const mockGet = vi.fn();
const mockPost = vi.fn();
const mockPatch = vi.fn();

vi.mock('../api', () => ({
  default: {
    get: (...args: unknown[]) => mockGet(...args),
    post: (...args: unknown[]) => mockPost(...args),
    patch: (...args: unknown[]) => mockPatch(...args),
  },
}));

describe('knowledgeBase.service', () => {
  beforeEach(() => {
    mockGet.mockReset();
    mockPost.mockReset();
    mockPatch.mockReset();
  });

  it('requests knowledge base articles with default parameters and normalises response', async () => {
    mockGet.mockResolvedValueOnce({
      data: {
        items: [
          {
            id: 'article-1',
            title: 'Improving ASR accuracy',
            category: 'best_practices',
            content: '# Content',
            content_format: 'markdown',
            author_id: 'user-123',
            is_published: true,
            views: 42,
            created_at: '2025-02-10T12:00:00Z',
            updated_at: '2025-02-11T09:30:00Z',
          },
        ],
        pagination: {
          total: 1,
          skip: 0,
          limit: 20,
          search_query: null,
        },
      },
    });

    const result = await getKnowledgeBaseArticles();

    expect(mockGet).toHaveBeenCalledWith('/v1/knowledge-base', {
      params: {
        q: null,
        category: null,
        is_published: null,
        author_id: null,
        skip: 0,
        limit: 20,
      },
    });

    expect(result.items).toEqual([
      {
        id: 'article-1',
        title: 'Improving ASR accuracy',
        category: 'best_practices',
        content: '# Content',
        contentFormat: 'markdown',
        authorId: 'user-123',
        isPublished: true,
        views: 42,
        createdAt: '2025-02-10T12:00:00Z',
        updatedAt: '2025-02-11T09:30:00Z',
      },
    ]);

    expect(result.pagination).toEqual({
      total: 1,
      skip: 0,
      limit: 20,
      searchQuery: null,
    });
  });

  it('passes through filters and search parameters when provided', async () => {
    mockGet.mockResolvedValueOnce({
      data: {
        items: [],
        pagination: {
          total: 0,
          skip: 20,
          limit: 10,
          search_query: 'llm',
        },
      },
    });

    await getKnowledgeBaseArticles({
      search: 'llm',
      category: 'troubleshooting',
      isPublished: false,
      authorId: 'user-456',
      skip: 20,
      limit: 10,
    });

    expect(mockGet).toHaveBeenCalledWith('/v1/knowledge-base', {
      params: {
        q: 'llm',
        category: 'troubleshooting',
        is_published: false,
        author_id: 'user-456',
        skip: 20,
        limit: 10,
      },
    });
  });

  it('retrieves a single knowledge base article by id', async () => {
    mockGet.mockResolvedValueOnce({
      data: {
        id: 'article-42',
        title: 'LLM guardrails',
        category: 'troubleshooting',
        content: '# Heading\n\nContent body',
        content_format: 'markdown',
        author_id: 'user-789',
        is_published: true,
        views: 99,
        created_at: '2025-02-14T10:00:00Z',
        updated_at: '2025-02-14T12:00:00Z',
      },
    });

    const article = await getKnowledgeBaseArticle('article-42');

    expect(mockGet).toHaveBeenCalledWith('/v1/knowledge-base/article-42');
    expect(article).toEqual({
      id: 'article-42',
      title: 'LLM guardrails',
      category: 'troubleshooting',
      content: '# Heading\n\nContent body',
      contentFormat: 'markdown',
      authorId: 'user-789',
      isPublished: true,
      views: 99,
      createdAt: '2025-02-14T10:00:00Z',
      updatedAt: '2025-02-14T12:00:00Z',
    });
  });

  it('creates a knowledge base article and normalises response data', async () => {
    mockPost.mockResolvedValueOnce({
      data: {
        id: 'article-100',
        title: 'New Article',
        category: 'best_practices',
        content: 'Markdown body',
        content_format: 'markdown',
        author_id: 'user-123',
        is_published: false,
        views: 0,
        created_at: '2025-03-01T09:00:00Z',
        updated_at: '2025-03-01T09:00:00Z',
      },
    });

    const payload = {
      title: 'New Article',
      category: 'best_practices',
      content: 'Markdown body',
      contentFormat: 'markdown' as const,
      isPublished: false,
    };

    const article = await createKnowledgeBaseArticle(payload);

    expect(mockPost).toHaveBeenCalledWith('/v1/knowledge-base', {
      title: 'New Article',
      category: 'best_practices',
      content: 'Markdown body',
      content_format: 'markdown',
      is_published: false,
    });

    expect(article).toEqual({
      id: 'article-100',
      title: 'New Article',
      category: 'best_practices',
      content: 'Markdown body',
      contentFormat: 'markdown',
      authorId: 'user-123',
      isPublished: false,
      views: 0,
      createdAt: '2025-03-01T09:00:00Z',
      updatedAt: '2025-03-01T09:00:00Z',
    });
  });

  it('updates a knowledge base article and returns the mapped article', async () => {
    mockPatch.mockResolvedValueOnce({
      data: {
        id: 'article-100',
        title: 'Updated Article',
        category: 'best_practices',
        content: 'Updated content',
        content_format: 'markdown',
        author_id: 'user-123',
        is_published: true,
        views: 10,
        created_at: '2025-03-01T09:00:00Z',
        updated_at: '2025-03-02T12:15:00Z',
      },
    });

    const article = await updateKnowledgeBaseArticle('article-100', {
      title: 'Updated Article',
      isPublished: true,
    });

    expect(mockPatch).toHaveBeenCalledWith('/v1/knowledge-base/article-100', {
      title: 'Updated Article',
      is_published: true,
    });

    expect(article).toEqual({
      id: 'article-100',
      title: 'Updated Article',
      category: 'best_practices',
      content: 'Updated content',
      contentFormat: 'markdown',
      authorId: 'user-123',
      isPublished: true,
      views: 10,
      createdAt: '2025-03-01T09:00:00Z',
      updatedAt: '2025-03-02T12:15:00Z',
    });
  });
});
