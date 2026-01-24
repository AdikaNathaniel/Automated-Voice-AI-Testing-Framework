import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Loader2 } from 'lucide-react';

import {
  createKnowledgeBaseArticle,
  getKnowledgeBaseArticle,
  updateKnowledgeBaseArticle,
} from '../../services/knowledgeBase.service';
import type { KnowledgeBaseArticle, KnowledgeBaseArticleUpdateInput } from '../../types/knowledgeBase';

type EditorFormState = {
  title: string;
  category: string;
  content: string;
  isPublished: boolean;
};

const DEFAULT_FORM_STATE: EditorFormState = {
  title: '',
  category: '',
  content: '',
  isPublished: false,
};

const normaliseCategory = (value: string): string | null => {
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : null;
};

const renderPreviewContent = (content: string): React.ReactNode => {
  if (!content.trim()) {
    return (
      <p className="text-sm text-[var(--color-content-secondary)]">
        Nothing to preview yet. Start typing to see a live preview.
      </p>
    );
  }

  const segments = content.split(/\n{2,}/);

  return segments.map((segment, index) => {
    const cleanSegment = segment.replace(/^#{1,6}\s*/gm, '').trim();
    const isHeading = segment.trim().startsWith('#');
    const className = isHeading ? 'text-lg font-semibold text-[var(--color-content-primary)]' : 'text-base text-[var(--color-content-secondary)]';

    return (
      <p
        key={`preview-${index}`}
        className={`${className} whitespace-pre-wrap ${index === segments.length - 1 ? '' : 'mb-4'}`}
      >
        {cleanSegment}
      </p>
    );
  });
};

const ArticleEditor: React.FC = () => {
  const params = useParams<{ articleId?: string }>();
  const articleId = params.articleId;
  const isEditing = Boolean(articleId);

  const [formState, setFormState] = useState<EditorFormState>(DEFAULT_FORM_STATE);
  const [contentFormat, setContentFormat] = useState<'markdown' | 'html'>('markdown');
  const [originalArticle, setOriginalArticle] = useState<KnowledgeBaseArticle | null>(null);
  const [loading, setLoading] = useState(isEditing);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [showPreview, setShowPreview] = useState(false);

  const loadArticle = useCallback(async () => {
    if (!articleId) {
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const article = await getKnowledgeBaseArticle(articleId);
      setOriginalArticle(article);
      setFormState({
        title: article.title,
        category: article.category ?? '',
        content: article.content,
        isPublished: article.isPublished,
      });
      setContentFormat((article.contentFormat as 'markdown' | 'html') ?? 'markdown');
    } catch (err: unknown) {
      setError((err as any)?.message ?? 'Failed to load article for editing.');
    } finally {
      setLoading(false);
    }
  }, [articleId]);

  useEffect(() => {
    if (isEditing) {
      loadArticle();
    }
  }, [isEditing, loadArticle]);

  const handleChange =
    (field: keyof EditorFormState) =>
    (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>, checked?: boolean) => {
      const value = field === 'isPublished' ? Boolean(checked ?? (event.target as HTMLInputElement).checked) : event.target.value;
      setFormState((prev) => ({
        ...prev,
        [field]: value,
      }));
    };

  const resetMessages = () => {
    setError(null);
    setSuccessMessage(null);
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    resetMessages();
    setSubmitting(true);

    try {
      if (isEditing && articleId) {
        const updates: KnowledgeBaseArticleUpdateInput = {};
        const currentCategory = normaliseCategory(formState.category);

        if (!originalArticle || formState.title !== originalArticle.title) {
          updates.title = formState.title;
        }
        if (!originalArticle || currentCategory !== originalArticle.category) {
          updates.category = currentCategory;
        }
        if (!originalArticle || formState.content !== originalArticle.content) {
          updates.content = formState.content;
        }
        if (!originalArticle || formState.isPublished !== originalArticle.isPublished) {
          updates.isPublished = formState.isPublished;
        }
        if (!originalArticle || contentFormat !== originalArticle.contentFormat) {
          updates.contentFormat = contentFormat;
        }

        const updatedArticle = await updateKnowledgeBaseArticle(articleId, updates);
        setOriginalArticle(updatedArticle);
        setSuccessMessage('Article saved successfully. You can continue editing or navigate away.');
      } else {
        await createKnowledgeBaseArticle({
          title: formState.title,
          category: normaliseCategory(formState.category) ?? undefined,
          content: formState.content,
          contentFormat,
          isPublished: formState.isPublished,
        });
        setFormState((prev) => ({
          ...prev,
          title: prev.title,
          category: prev.category,
          content: prev.content,
          isPublished: prev.isPublished,
        }));
        setSuccessMessage('Article saved successfully. You can continue editing or navigate away.');
      }
    } catch (err: unknown) {
      setError((err as any)?.message ?? 'Failed to save article.');
    } finally {
      setSubmitting(false);
    }
  };

  const previewContent = useMemo(() => renderPreviewContent(formState.content), [formState.content]);

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-8">
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-[var(--color-status-info)]" data-testid="knowledge-base-editor-loading" />
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <form onSubmit={handleSubmit} className="space-y-6">
        <h1 className="header">
          {isEditing ? 'Edit Knowledge Base Article' : 'Create Knowledge Base Article'}
        </h1>

        {error && (
          <div className="bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] rounded-lg p-4" role="alert">
            <p className="text-[var(--color-status-danger)]">{error}</p>
          </div>
        )}

        {successMessage && (
          <div className="bg-[var(--color-status-success-bg)] border border-[var(--color-status-success)] rounded-lg p-4" role="status">
            <p className="text-[var(--color-status-success)]">{successMessage}</p>
          </div>
        )}

        <div className="card space-y-5">
          <div>
            <label htmlFor="title" className="block text-sm font-medium mb-2 text-[var(--color-content-primary)]">
              Title *
            </label>
            <input
              type="text"
              id="title"
              value={formState.title}
              onChange={handleChange('title')}
              required
              className="w-full px-3 py-2 border border-[var(--color-border-strong)] rounded-md bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-status-info)]"
            />
          </div>

          <div>
            <label htmlFor="category" className="block text-sm font-medium mb-2 text-[var(--color-content-primary)]">
              Category
            </label>
            <input
              type="text"
              id="category"
              value={formState.category}
              onChange={handleChange('category')}
              className="w-full px-3 py-2 border border-[var(--color-border-strong)] rounded-md bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-status-info)]"
            />
          </div>

          <div>
            <label htmlFor="content" className="block text-sm font-medium mb-2 text-[var(--color-content-primary)]">
              Content
            </label>
            <textarea
              id="content"
              value={formState.content}
              onChange={handleChange('content')}
              rows={8}
              className="w-full px-3 py-2 border border-[var(--color-border-strong)] rounded-md bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-status-info)]"
            />
          </div>

          <label className="flex items-center gap-2 text-[var(--color-content-primary)]">
            <input
              type="checkbox"
              checked={formState.isPublished}
              onChange={(e) => handleChange('isPublished')(e, e.target.checked)}
              className="rounded border-[var(--color-border-strong)] bg-[var(--color-surface-base)]"
            />
            Publish article
          </label>

          <div className="flex gap-4 flex-wrap">
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {isEditing ? 'Update Article' : 'Create Article'}
            </button>
            <button type="button" className="btn" onClick={() => setShowPreview((prev) => !prev)}>
              {showPreview ? 'Hide preview' : 'Show preview'}
            </button>
          </div>
        </div>

        {showPreview && (
          <div className="card" data-testid="knowledge-base-editor-preview">
            <h2 className="text-lg font-semibold mb-4 text-[var(--color-content-primary)]">Preview</h2>
            <div className="space-y-3">{previewContent}</div>
          </div>
        )}
      </form>
    </div>
  );
};

export default ArticleEditor;
