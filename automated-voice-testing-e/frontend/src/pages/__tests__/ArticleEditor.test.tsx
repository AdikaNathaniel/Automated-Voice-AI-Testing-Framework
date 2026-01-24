import React from 'react';
import { describe, expect, it, beforeEach, vi } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import ArticleEditor from '../KnowledgeBase/ArticleEditor';

const mockGetKnowledgeBaseArticle = vi.fn();
const mockCreateKnowledgeBaseArticle = vi.fn();
const mockUpdateKnowledgeBaseArticle = vi.fn();

vi.mock('../../services/knowledgeBase.service', () => ({
  getKnowledgeBaseArticle: (...args: unknown[]) => mockGetKnowledgeBaseArticle(...args),
  createKnowledgeBaseArticle: (...args: unknown[]) => mockCreateKnowledgeBaseArticle(...args),
  updateKnowledgeBaseArticle: (...args: unknown[]) => mockUpdateKnowledgeBaseArticle(...args),
}));

const renderWithRouter = (initialPath = '/knowledge-base/new') =>
  render(
    <MemoryRouter initialEntries={[initialPath]}>
      <Routes>
        <Route path="/knowledge-base/new" element={<ArticleEditor />} />
        <Route path="/knowledge-base/:articleId/edit" element={<ArticleEditor />} />
      </Routes>
    </MemoryRouter>
  );

describe('ArticleEditor page', () => {
  beforeEach(() => {
    mockGetKnowledgeBaseArticle.mockReset();
    mockCreateKnowledgeBaseArticle.mockReset();
    mockUpdateKnowledgeBaseArticle.mockReset();
  });

  it('submits a new article using the knowledge base service', async () => {
    mockCreateKnowledgeBaseArticle.mockResolvedValueOnce({
      id: 'article-200',
      title: 'Drafting guardrails',
      category: 'best_practices',
      content: '# Draft',
      contentFormat: 'markdown',
      authorId: 'user-1',
      isPublished: true,
      views: 0,
      createdAt: '2025-03-01T12:00:00Z',
      updatedAt: '2025-03-01T12:00:00Z',
    });

    renderWithRouter('/knowledge-base/new');

    const titleInput = screen.getByRole('textbox', { name: /title/i });
    const categoryInput = screen.getByRole('textbox', { name: /category/i });
    const contentInput = screen.getByRole('textbox', { name: /content/i });
    const publishToggle = screen.getByRole('switch', { name: /publish article/i });

    await userEvent.type(titleInput, 'Drafting guardrails');
    await userEvent.type(categoryInput, 'best_practices');
    await userEvent.type(contentInput, '# Draft');
    await userEvent.click(publishToggle);

    const submitButton = screen.getByRole('button', { name: /create article/i });
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(mockCreateKnowledgeBaseArticle).toHaveBeenCalledWith({
        title: 'Drafting guardrails',
        category: 'best_practices',
        content: '# Draft',
        contentFormat: 'markdown',
        isPublished: true,
      });
    });

    expect(
      await screen.findByText(/Article saved successfully. You can continue editing or navigate away/i)
    ).toBeInTheDocument();
  });

  it('toggles a live markdown preview of the article content', async () => {
    renderWithRouter('/knowledge-base/new');

    const contentInput = screen.getByRole('textbox', { name: /content/i });
    await userEvent.type(contentInput, '# Heading\n\nBody copy.');

    const previewToggle = screen.getByRole('button', { name: /show preview/i });
    await userEvent.click(previewToggle);

    const preview = await screen.findByTestId('knowledge-base-editor-preview');
    expect(preview).toHaveTextContent('Heading');
    expect(preview).toHaveTextContent('Body copy.');

    const hidePreview = screen.getByRole('button', { name: /hide preview/i });
    await userEvent.click(hidePreview);

    expect(screen.queryByTestId('knowledge-base-editor-preview')).not.toBeInTheDocument();
  });

  it('loads an existing article for editing and saves updates', async () => {
    mockGetKnowledgeBaseArticle.mockResolvedValueOnce({
      id: 'article-201',
      title: 'Existing doc',
      category: 'troubleshooting',
      content: 'Initial body',
      contentFormat: 'markdown',
      authorId: 'user-1',
      isPublished: false,
      views: 5,
      createdAt: '2025-03-02T08:00:00Z',
      updatedAt: '2025-03-02T09:00:00Z',
    });

    mockUpdateKnowledgeBaseArticle.mockResolvedValueOnce({
      id: 'article-201',
      title: 'Existing doc updated',
      category: 'troubleshooting',
      content: 'Updated body',
      contentFormat: 'markdown',
      authorId: 'user-1',
      isPublished: false,
      views: 5,
      createdAt: '2025-03-02T08:00:00Z',
      updatedAt: '2025-03-02T09:30:00Z',
    });

    renderWithRouter('/knowledge-base/article-201/edit');

    expect(await screen.findByDisplayValue('Existing doc')).toBeInTheDocument();

    const titleInput = screen.getByRole('textbox', { name: /title/i });
    const contentInput = screen.getByRole('textbox', { name: /content/i });

    await userEvent.clear(titleInput);
    await userEvent.type(titleInput, 'Existing doc updated');
    await userEvent.clear(contentInput);
    await userEvent.type(contentInput, 'Updated body');

    const updateButton = screen.getByRole('button', { name: /update article/i });
    await userEvent.click(updateButton);

    await waitFor(() => {
      expect(mockUpdateKnowledgeBaseArticle).toHaveBeenCalledWith('article-201', {
        title: 'Existing doc updated',
        content: 'Updated body',
      });
    });

    expect(await screen.findByText(/Article saved successfully/i)).toBeInTheDocument();
  });
});
