import React from 'react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import KnowledgeBaseSearch from '../KnowledgeBase/KnowledgeBaseSearch';

const mockGetKnowledgeBaseArticles = vi.fn();

vi.mock('../../services/knowledgeBase.service', () => ({
  getKnowledgeBaseArticles: (...args: unknown[]) => mockGetKnowledgeBaseArticles(...args),
}));

const renderSearchPage = (initialPath = '/knowledge-base/search') =>
  render(
    <MemoryRouter initialEntries={[initialPath]}>
      <Routes>
        <Route path="/knowledge-base/search" element={<KnowledgeBaseSearch />} />
      </Routes>
    </MemoryRouter>
  );

describe('KnowledgeBaseSearch page', () => {
  beforeEach(() => {
    mockGetKnowledgeBaseArticles.mockReset();
  });

  it('renders initial search results and category filters from service data', async () => {
    mockGetKnowledgeBaseArticles.mockResolvedValueOnce({
      items: [
        {
          id: 'article-1',
          title: 'LLM guardrails',
          category: 'troubleshooting',
          content: '# Guide content',
          contentFormat: 'markdown',
          authorId: 'user-1',
          isPublished: true,
          views: 5,
          createdAt: '2025-03-01T10:00:00Z',
          updatedAt: '2025-03-01T11:00:00Z',
        },
        {
          id: 'article-2',
          title: 'Prompt engineering tips',
          category: 'best_practices',
          content: 'Plain text content',
          contentFormat: 'markdown',
          authorId: 'user-2',
          isPublished: true,
          views: 12,
          createdAt: '2025-03-02T10:00:00Z',
          updatedAt: '2025-03-02T11:00:00Z',
        },
      ],
      pagination: { total: 2, skip: 0, limit: 20, searchQuery: 'llm' },
    });

    renderSearchPage('/knowledge-base/search?q=llm');

    expect(mockGetKnowledgeBaseArticles).toHaveBeenCalledWith({
      search: 'llm',
    });

    await screen.findByRole('heading', { name: /Knowledge Base Search/i });
    expect(screen.getByDisplayValue('llm')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /LLM guardrails/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Prompt engineering tips/i })).toBeInTheDocument();

    expect(screen.getByRole('button', { name: /All categories/i })).toHaveAttribute('aria-pressed', 'true');
    expect(screen.getByRole('button', { name: /troubleshooting/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /best_practices/i })).toBeInTheDocument();
  });

  it('applies category filter and re-fetches results', async () => {
    mockGetKnowledgeBaseArticles
      .mockResolvedValueOnce({
        items: [
          {
            id: 'article-1',
            title: 'LLM guardrails',
            category: 'troubleshooting',
            content: '# Guide content',
            contentFormat: 'markdown',
            authorId: 'user-1',
            isPublished: true,
            views: 5,
            createdAt: '2025-03-01T10:00:00Z',
            updatedAt: '2025-03-01T11:00:00Z',
          },
        ],
        pagination: { total: 1, skip: 0, limit: 20, searchQuery: 'llm' },
      })
      .mockResolvedValueOnce({
        items: [
          {
            id: 'article-3',
            title: 'Handling errors',
            category: 'troubleshooting',
            content: 'Error remediation steps',
            contentFormat: 'markdown',
            authorId: 'user-3',
            isPublished: true,
            views: 8,
            createdAt: '2025-03-03T10:00:00Z',
            updatedAt: '2025-03-03T11:00:00Z',
          },
        ],
        pagination: { total: 1, skip: 0, limit: 20, searchQuery: 'llm' },
      });

    renderSearchPage('/knowledge-base/search?q=llm');

    await screen.findByText('LLM guardrails');

    const troubleshootingFilter = screen.getByRole('button', { name: /troubleshooting/i });
    await userEvent.click(troubleshootingFilter);

    await waitFor(() => {
      expect(mockGetKnowledgeBaseArticles).toHaveBeenLastCalledWith({
        search: 'llm',
        category: 'troubleshooting',
      });
    });

    expect(await screen.findByText('Handling errors')).toBeInTheDocument();
    expect(screen.queryByText('LLM guardrails')).not.toBeInTheDocument();
  });

  it('updates results when submitting a new search query', async () => {
    mockGetKnowledgeBaseArticles
      .mockResolvedValueOnce({
        items: [],
        pagination: { total: 0, skip: 0, limit: 20, searchQuery: 'faq' },
      })
      .mockResolvedValueOnce({
        items: [
          {
            id: 'article-4',
            title: 'Guardrails checklist',
            category: 'best_practices',
            content: 'Checklist content',
            contentFormat: 'markdown',
            authorId: 'user-4',
            isPublished: true,
            views: 3,
            createdAt: '2025-03-04T10:00:00Z',
            updatedAt: '2025-03-04T11:00:00Z',
          },
        ],
        pagination: { total: 1, skip: 0, limit: 20, searchQuery: 'guardrails' },
      });

    renderSearchPage('/knowledge-base/search?q=faq');

    const input = screen.getByRole('textbox', { name: /Search knowledge base/i });
    await userEvent.clear(input);
    await userEvent.type(input, 'guardrails');

    const submitButton = screen.getByRole('button', { name: /Search/i });
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(mockGetKnowledgeBaseArticles).toHaveBeenLastCalledWith({
        search: 'guardrails',
      });
    });

    expect(await screen.findByText('Guardrails checklist')).toBeInTheDocument();
  });
});
