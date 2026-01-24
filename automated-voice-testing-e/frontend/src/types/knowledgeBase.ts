/**
 * Knowledge Base Types
 *
 * Phase 3: Added pattern group integration fields
 */

export interface KnowledgeBaseArticle {
  id: string;
  title: string;
  category: string | null;
  content: string;
  contentFormat: string;
  authorId: string;
  isPublished: boolean;
  views: number;
  createdAt: string;
  updatedAt: string;
  // Phase 3: Pattern group integration
  patternGroupId: string | null;
  sourceType: 'manual' | 'auto_generated' | 'pattern_derived';
  tags: string[];
}

export interface KnowledgeBasePagination {
  total: number;
  skip: number;
  limit: number;
  searchQuery: string | null;
}

export interface KnowledgeBaseListResponse {
  items: KnowledgeBaseArticle[];
  pagination: KnowledgeBasePagination;
}

export interface KnowledgeBaseListParams {
  search?: string;
  category?: string;
  isPublished?: boolean;
  authorId?: string;
  sourceType?: 'manual' | 'auto_generated' | 'pattern_derived';
  patternGroupId?: string;
  tags?: string[];
  skip?: number;
  limit?: number;
}

export interface KnowledgeBaseArticleCreateInput {
  title: string;
  content: string;
  category?: string | null;
  contentFormat?: string;
  isPublished?: boolean;
  patternGroupId?: string | null;
  sourceType?: 'manual' | 'auto_generated' | 'pattern_derived';
  tags?: string[];
}

export interface KnowledgeBaseArticleUpdateInput {
  title?: string;
  content?: string;
  category?: string | null;
  contentFormat?: string;
  isPublished?: boolean;
  tags?: string[];
}

// Source type labels for display
export const SOURCE_TYPE_LABELS: Record<string, string> = {
  manual: 'Manual',
  auto_generated: 'Auto-Generated',
  pattern_derived: 'Pattern Derived',
};

// Source type badge colors
export const SOURCE_TYPE_COLORS: Record<string, string> = {
  manual: 'bg-[var(--color-status-info-bg)] text-[var(--color-status-info)]',
  auto_generated: 'bg-[var(--color-status-purple-bg)] text-[var(--color-status-purple)]',
  pattern_derived: 'bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]',
};
