import React from 'react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import KnowledgeBase from '../KnowledgeBase/KnowledgeBase';

const mockGetKnowledgeBaseArticles = vi.fn();

vi.mock('../../services/knowledgeBase.service', () => ({
  getKnowledgeBaseArticles: (...args: unknown[]) => mockGetKnowledgeBaseArticles(...args),
}));

describe('KnowledgeBase page', () => {
  beforeEach(() => {
    mockGetKnowledgeBaseArticles.mockReset();
  });

  it('renders knowledge base articles returned by the service', async () => {
    mockGetKnowledgeBaseArticles.mockResolvedValueOnce({
      items: [
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
      ],
      pagination: { total: 1, skip: 0, limit: 20, searchQuery: null },
    });

    render(
      <MemoryRouter>
        <KnowledgeBase />
      </MemoryRouter>
    );

    expect(mockGetKnowledgeBaseArticles).toHaveBeenCalledTimes(1);

    await screen.findByRole('heading', { name: /Knowledge Base/i });
    expect(screen.getByRole('heading', { name: 'Improving ASR accuracy' })).toBeInTheDocument();
    expect(screen.getByText(/best_practices/i)).toBeInTheDocument();
  });

  it('submits a search query and updates rendered results', async () => {
    mockGetKnowledgeBaseArticles
      .mockResolvedValueOnce({
        items: [
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
        ],
        pagination: { total: 1, skip: 0, limit: 20, searchQuery: null },
      })
      .mockResolvedValueOnce({
        items: [
          {
            id: 'article-2',
            title: 'LLM guardrails',
            category: 'troubleshooting',
            content: 'Body',
            contentFormat: 'markdown',
            authorId: 'user-456',
            isPublished: true,
            views: 5,
            createdAt: '2025-02-12T08:00:00Z',
            updatedAt: '2025-02-12T08:00:00Z',
          },
        ],
        pagination: { total: 1, skip: 0, limit: 20, searchQuery: 'llm' },
      });

    render(
      <MemoryRouter>
        <KnowledgeBase />
      </MemoryRouter>
    );

    await screen.findByText('Improving ASR accuracy');

    const input = screen.getByRole('textbox', { name: /search knowledge base/i });
    await userEvent.clear(input);
    await userEvent.type(input, 'llm');

    const submit = screen.getByRole('button', { name: /search/i });
    await userEvent.click(submit);

    await screen.findByText('LLM guardrails');

    expect(mockGetKnowledgeBaseArticles).toHaveBeenCalledTimes(2);
    expect(mockGetKnowledgeBaseArticles.mock.calls[1][0]).toMatchObject({ search: 'llm' });
  });

  it('displays an error message when the service call fails', async () => {
    mockGetKnowledgeBaseArticles.mockRejectedValueOnce(new Error('Network failure'));

    render(
      <MemoryRouter>
        <KnowledgeBase />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Network failure/i)).toBeInTheDocument();
    });
  });
});
