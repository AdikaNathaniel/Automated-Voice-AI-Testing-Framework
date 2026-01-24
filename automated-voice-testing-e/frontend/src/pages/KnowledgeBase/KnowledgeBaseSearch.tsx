import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Loader2, Search } from 'lucide-react';

import { getKnowledgeBaseArticles } from '../../services/knowledgeBase.service';
import type { KnowledgeBaseArticle, KnowledgeBaseListParams } from '../../types/knowledgeBase';

const buildExcerpt = (content: string): string => {
  const plainText = content.replace(/[#_*`>\\-]/g, '').replace(/\s+/g, ' ').trim();
  if (plainText.length <= 180) {
    return plainText;
  }
  return `${plainText.slice(0, 177)}…`;
};

const KnowledgeBaseSearch: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [articles, setArticles] = useState<KnowledgeBaseArticle[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchInput, setSearchInput] = useState(() => searchParams.get('q') ?? '');

  const searchQuery = searchParams.get('q') ?? '';
  const categoryFilter = searchParams.get('category');

  useEffect(() => {
    setSearchInput(searchQuery);
  }, [searchQuery]);

  const fetchArticles = useCallback(
    async (query: string, category: string | null) => {
      const params: KnowledgeBaseListParams = {};
      if (query) {
        params.search = query;
      }
      if (category) {
        params.category = category;
      }

      try {
        setLoading(true);
        setError(null);
        const response = await getKnowledgeBaseArticles(params);
        setArticles(response.items);

        const uniqueCategories = Array.from(
          new Set(
            response.items
              .map((article) => article.category)
              .filter((value): value is string => typeof value === 'string' && value.trim().length > 0)
          )
        ).sort((a, b) => a.localeCompare(b));
        setCategories(uniqueCategories);
      } catch (err: unknown) {
        setError(err?.message ?? 'Failed to search knowledge base.');
        setArticles([]);
        setCategories([]);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  useEffect(() => {
    void fetchArticles(searchQuery, categoryFilter);
  }, [fetchArticles, searchQuery, categoryFilter]);

  const selectedCategory = categoryFilter ?? 'all';

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = searchInput.trim();
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      if (trimmed) {
        next.set('q', trimmed);
      } else {
        next.delete('q');
      }
      next.delete('category');
      return next;
    });
  };

  const handleCategoryChange = (_event: React.MouseEvent<HTMLElement>, value: string | null) => {
    if (value === null) {
      return;
    }

    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      if (value === 'all') {
        next.delete('category');
      } else {
        next.set('category', value);
      }
      return next;
    });
  };

  const renderedArticles = useMemo(() => {
    if (loading) {
      return (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-[var(--color-status-info)]" data-testid="knowledge-base-search-loading" />
        </div>
      );
    }

    if (error) {
      return (
        <div className="bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] rounded-lg p-4" role="alert">
          <p className="text-[var(--color-status-danger)]">{error}</p>
        </div>
      );
    }

    if (articles.length === 0) {
      return (
        <div className="card">
          <p className="text-[var(--color-content-secondary)]">No articles matched your search. Try a different query or category.</p>
        </div>
      );
    }

    return (
      <div className="flex flex-col gap-5">
        {articles.map((article) => (
          <div key={article.id} className="card flex flex-col gap-3">
            <div className="flex flex-col gap-2">
              <h2 className="text-xl font-semibold text-[var(--color-content-primary)]">
                {article.title}
              </h2>
              <span className="text-xs text-[var(--color-content-muted)]">
                {article.category ? `Category: ${article.category}` : 'No category'}
              </span>
            </div>
            <p className="text-sm text-[var(--color-content-secondary)]">
              {buildExcerpt(article.content)}
            </p>
            <span className="text-xs text-[var(--color-content-muted)]">
              Updated {new Date(article.updatedAt).toLocaleString()}
            </span>
          </div>
        ))}
      </div>
    );
  }, [articles, error, loading]);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex flex-col gap-6">
        <h1 className="header">
          Knowledge Base Search
        </h1>

        <form
          onSubmit={handleSubmit}
          className="card flex flex-col md:flex-row gap-4 items-stretch md:items-center"
        >
          <div className="flex-1 relative">
            <input
              type="text"
              className="search-box w-full pl-10 bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] border-[var(--color-border-strong)] placeholder-[var(--color-content-muted)]"
              placeholder="Search knowledge base"
              value={searchInput}
              onChange={(event) => setSearchInput(event.target.value)}
            />
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--color-content-muted)]" />
          </div>
          <button type="submit" className="btn btn-primary">
            Search
          </button>
        </form>

        <div className="card">
          <h2 className="text-base font-semibold mb-3 text-[var(--color-content-primary)]">
            Filter by category
          </h2>
          <div className="flex flex-wrap gap-2" role="group" aria-label="Filter articles by category">
            <button
              type="button"
              className={`btn ${selectedCategory === 'all' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={(e) => handleCategoryChange(e, 'all')}
            >
              All categories
            </button>
            {categories.map((category) => (
              <button
                key={category}
                type="button"
                className={`btn ${selectedCategory === category ? 'btn-primary' : 'btn-secondary'}`}
                onClick={(e) => handleCategoryChange(e, category)}
              >
                {category}
              </button>
            ))}
          </div>
        </div>

        {renderedArticles}
      </div>
    </div>
  );
};

export default KnowledgeBaseSearch;
