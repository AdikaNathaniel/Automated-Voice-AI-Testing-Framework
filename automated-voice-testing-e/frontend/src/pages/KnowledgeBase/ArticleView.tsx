import React, { useEffect, useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import { getKnowledgeBaseArticle } from '../../services/knowledgeBase.service';
import type { KnowledgeBaseArticle } from '../../types/knowledgeBase';

type ParsedHeading = {
  id: string;
  text: string;
  level: number;
};

const slugify = (value: string): string =>
  value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');

const extractMarkdownFromContent = (content: string): string => {
  /**
   * Extract pure markdown from content that might be JSON-wrapped.
   * Handles cases where LLM returned JSON like: {"article": "markdown content"}
   * Also handles markdown code block wrapper: ```json ... ```
   */
  let cleaned = content.trim();

  // Remove markdown code block wrapper if present (more aggressive cleanup)
  if (cleaned.startsWith('```')) {
    // Remove opening fence (```json or ``` followed by optional whitespace and newlines)
    cleaned = cleaned.replace(/^```(?:json)?\s*\n?/, '');
    // Remove closing fence (``` at end with optional preceding newlines/whitespace)
    cleaned = cleaned.replace(/\n?```\s*$/, '');
    cleaned = cleaned.trim();
  }

  // Try to parse as JSON and extract article field
  if (cleaned.startsWith('{')) {
    try {
      // Parse the JSON string
      const parsed = JSON.parse(cleaned);

      // Extract article field if it exists
      if (parsed && typeof parsed === 'object' && 'article' in parsed) {
        const article = parsed.article;
        console.log('[KB] Extracted article from JSON wrapper, length:', article?.length);
        return article;
      }
    } catch (error) {
      // Log parsing error for debugging
      console.error('[KB] Failed to parse JSON content:', error);
      console.log('[KB] Content preview:', cleaned.substring(0, 200));
    }
  }

  return cleaned;
};

const extractHeadings = (content: string): ParsedHeading[] => {
  const headings: ParsedHeading[] = [];
  const lines = content.split(/\r?\n/);

  lines.forEach((line) => {
    const headingMatch = line.match(/^(#{1,6})\s+(.*)$/);
    if (headingMatch) {
      const level = headingMatch[1].length;
      const text = headingMatch[2].trim();
      if (text) {
        const id = slugify(text);
        headings.push({ id, text, level });
      }
    }
  });

  return headings;
};

const formatDate = (value: string): string => {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return 'Unknown';
  }
  return parsed.toLocaleString();
};

const ArticleView: React.FC = () => {
  const { articleId } = useParams<{ articleId: string }>();
  const [article, setArticle] = useState<KnowledgeBaseArticle | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const fetchArticle = async () => {
      if (!articleId) {
        setError('Article not found');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);

        const result = await getKnowledgeBaseArticle(articleId);
        if (!cancelled) {
          setArticle(result);
        }
      } catch (err: unknown) {
        if (!cancelled) {
          setError(err?.message ?? 'Failed to load article');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchArticle();

    return () => {
      cancelled = true;
    };
  }, [articleId]);

  const cleanedContent = useMemo(() => {
    if (!article) return '';
    return extractMarkdownFromContent(article.content);
  }, [article]);

  const headings = useMemo(() => {
    if (!article || article.contentFormat !== 'markdown') {
      return [];
    }
    return extractHeadings(cleanedContent);
  }, [article, cleanedContent]);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-[var(--color-status-info)]" data-testid="knowledge-base-article-loading" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] rounded-lg p-4" role="alert">
          <p className="text-[var(--color-status-danger)]">{error}</p>
        </div>
      </div>
    );
  }

  if (!article) {
    return null;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 mb-12">
      <div className="flex flex-col lg:flex-row gap-8">
        <div className="flex-[3] flex flex-col gap-6">
          <div className="flex flex-col gap-2">
            <h1 className="text-3xl font-bold text-[var(--color-content-primary)]">
              {article.title}
            </h1>
            <div className="flex items-center gap-4 flex-wrap">
              {article.category && (
                <span className="badge badge-info capitalize">
                  {article.category}
                </span>
              )}
              <span className="text-sm text-[var(--color-content-secondary)]">
                Updated {formatDate(article.updatedAt)}
              </span>
              <span className="text-sm text-[var(--color-content-secondary)]">
                {article.views} views
              </span>
            </div>
          </div>

          <article className="bg-[var(--color-surface-raised)] rounded-lg shadow-sm border border-[var(--color-border-default)] p-8">
            {article.contentFormat === 'markdown' ? (
              <div className="prose prose-lg prose-semantic max-w-none
                prose-headings:font-bold
                prose-h1:text-3xl prose-h1:mt-0 prose-h1:mb-6 prose-h1:pb-3 prose-h1:border-b prose-h1:border-[var(--color-border-default)]
                prose-h2:text-2xl prose-h2:mt-10 prose-h2:mb-4
                prose-h3:text-xl prose-h3:mt-8 prose-h3:mb-3
                prose-h4:text-lg prose-h4:mt-6 prose-h4:mb-2
                prose-p:leading-relaxed prose-p:my-4
                prose-a:font-medium prose-a:no-underline hover:prose-a:underline
                prose-strong:font-semibold
                prose-ul:my-6 prose-ul:list-disc prose-ul:pl-6
                prose-ol:my-6 prose-ol:list-decimal prose-ol:pl-6
                prose-li:my-2 prose-li:leading-relaxed
                prose-table:w-full prose-table:my-8 prose-table:border-collapse
                prose-th:border prose-th:px-4 prose-th:py-3 prose-th:text-left prose-th:font-semibold
                prose-td:border prose-td:px-4 prose-td:py-3
                prose-tr:border-b
                prose-code:text-sm prose-code:font-mono prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded
                prose-pre:p-4 prose-pre:rounded-lg prose-pre:overflow-x-auto prose-pre:my-6
                prose-blockquote:border-l-4 prose-blockquote:pl-4 prose-blockquote:italic
                prose-hr:my-8
                prose-img:rounded-lg prose-img:shadow-md">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    h1: ({ node, ...props }) => <h2 id={slugify(props.children?.toString() || '')} {...props} />,
                    h2: ({ node, ...props }) => <h3 id={slugify(props.children?.toString() || '')} {...props} />,
                    h3: ({ node, ...props }) => <h4 id={slugify(props.children?.toString() || '')} {...props} />,
                    h4: ({ node, ...props }) => <h5 id={slugify(props.children?.toString() || '')} {...props} />,
                    h5: ({ node, ...props }) => <h6 id={slugify(props.children?.toString() || '')} {...props} />,
                  }}
                >
                  {cleanedContent}
                </ReactMarkdown>
              </div>
            ) : (
              <div className="whitespace-pre-wrap text-base text-[var(--color-content-secondary)] leading-relaxed">
                {article.content}
              </div>
            )}
          </article>
        </div>

        {headings.length > 0 && (
          <aside className="hidden lg:block w-64 flex-shrink-0">
            <nav
              aria-label="Table of contents"
              className="sticky top-6 max-h-[calc(100vh-3rem)] overflow-y-auto"
            >
              <div className="bg-[var(--color-surface-raised)] rounded-lg shadow-sm border border-[var(--color-border-default)] p-4">
                <h2 className="text-sm font-bold mb-4 text-[var(--color-content-primary)] pb-2 border-b border-[var(--color-border-default)]">
                  Table of Contents
                </h2>
                <ul className="space-y-2">
                  {headings.map((heading) => (
                    <li
                      key={heading.id}
                      style={{ paddingLeft: heading.level > 1 ? `${(heading.level - 1) * 0.75}rem` : 0 }}
                    >
                      <a
                        href={`#${heading.id}`}
                        className="text-xs text-[var(--color-content-secondary)] hover:text-[var(--color-status-info)] transition-colors block py-1"
                        onClick={(e) => {
                          e.preventDefault();
                          document.getElementById(heading.id)?.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start',
                          });
                        }}
                      >
                        {heading.text}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            </nav>
          </aside>
        )}
      </div>
    </div>
  );
};

export default ArticleView;
