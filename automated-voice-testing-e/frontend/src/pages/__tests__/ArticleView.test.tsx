import React from 'react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { render, screen, waitFor } from '@testing-library/react';

import ArticleView from '../KnowledgeBase/ArticleView';

const mockGetKnowledgeBaseArticle = vi.fn();

vi.mock('../../services/knowledgeBase.service', () => ({
  getKnowledgeBaseArticle: (...args: unknown[]) => mockGetKnowledgeBaseArticle(...args),
}));

const renderWithRouter = (initialPath = '/knowledge-base/article-1') =>
  render(
    <MemoryRouter initialEntries={[initialPath]}>
      <Routes>
        <Route path="/knowledge-base/:articleId" element={<ArticleView />} />
      </Routes>
    </MemoryRouter>
  );

describe('ArticleView page', () => {
  beforeEach(() => {
    mockGetKnowledgeBaseArticle.mockReset();
  });

  it('renders article content and table of contents from markdown', async () => {
    mockGetKnowledgeBaseArticle.mockResolvedValueOnce({
      id: 'article-1',
      title: 'LLM guardrails',
      category: 'troubleshooting',
      content: '# Heading 1\n\n## Sub heading\n\nSome paragraph text.',
      contentFormat: 'markdown',
      authorId: 'user-789',
      isPublished: true,
      views: 10,
      createdAt: '2025-02-14T10:00:00Z',
      updatedAt: '2025-02-14T12:00:00Z',
    });

    renderWithRouter();

    expect(mockGetKnowledgeBaseArticle).toHaveBeenCalledWith('article-1');

    await screen.findByRole('heading', { level: 1, name: /LLM guardrails/i });
    expect(screen.getByRole('heading', { level: 3, name: /Sub heading/i })).toBeInTheDocument();

    const toc = screen.getByRole('navigation', { name: /Table of contents/i });
    expect(toc).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Heading 1' })).toHaveAttribute('href', '#heading-1');
    expect(screen.getByRole('link', { name: 'Sub heading' })).toHaveAttribute('href', '#sub-heading');
  });

  it('displays an error message when the article fails to load', async () => {
    mockGetKnowledgeBaseArticle.mockRejectedValueOnce(new Error('Failed to load article'));

    renderWithRouter();

    await waitFor(() => {
      expect(screen.getByText(/Failed to load article/i)).toBeInTheDocument();
    });
  });

  it('shows loading indicator while fetching article', () => {
    mockGetKnowledgeBaseArticle.mockReturnValue(new Promise(() => {}));

    renderWithRouter();

    expect(screen.getByTestId('knowledge-base-article-loading')).toBeInTheDocument();
  });
});
