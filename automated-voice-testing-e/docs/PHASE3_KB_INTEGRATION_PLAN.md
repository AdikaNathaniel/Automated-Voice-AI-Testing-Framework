# Phase 3: Knowledge Base Integration - Implementation Plan

## Overview

This document outlines the implementation plan for Phase 3 of the Edge Case Workflow: integrating Pattern Groups with the Knowledge Base system to automatically generate searchable documentation from edge case patterns.

---

## Goals

1. **Auto-generate KB articles** from pattern groups with LLM-powered content
2. **Link patterns to articles** for bidirectional navigation
3. **Revamp KB UI** to match the modern design language of the app
4. **Make patterns searchable** through the knowledge base

---

## Current State Analysis

### Knowledge Base (Current)
- Basic CRUD for articles
- Simple list view with search
- No relationship to patterns or edge cases
- Missing: tabs, filters, categories, modern UI

### Pattern Groups (Implemented)
- LLM-generated pattern names and descriptions
- Suggested actions list
- Linked edge cases
- Severity and occurrence tracking

---

## Implementation Plan

### Part 1: Database Schema Updates

#### 1.1 Add fields to KnowledgeBase model

```python
# backend/models/knowledge_base.py - New fields

pattern_group_id = Column(GUID, ForeignKey('pattern_groups.id'), nullable=True, index=True)
source_type = Column(String(50), default='manual')  # 'manual', 'auto_generated', 'pattern_derived'
tags = Column(ARRAY(String), default=list)  # For multi-label categorization

# Relationship
pattern_group = relationship('PatternGroup', backref='knowledge_base_articles')
```

#### 1.2 Migration

```bash
alembic revision --autogenerate -m "add_pattern_group_link_to_knowledge_base"
alembic upgrade head
```

---

### Part 2: Backend Service Updates

#### 2.1 KB Generation Service

**File**: `backend/services/kb_generation_service.py` (NEW)

```python
class KBGenerationService:
    """
    Generates Knowledge Base articles from Pattern Groups using LLM.
    """

    async def generate_from_pattern_group(
        self,
        db: AsyncSession,
        pattern_group: PatternGroup,
        author_id: UUID
    ) -> KnowledgeBase:
        """
        Auto-generate a KB article from a pattern group.

        Content includes:
        - Pattern overview
        - Impact analysis
        - Common triggers (from edge cases)
        - Suggested resolutions
        - Related scenarios
        """
        pass

    async def _generate_article_content(
        self,
        pattern: PatternGroup,
        edge_cases: List[EdgeCase]
    ) -> str:
        """
        Use LLM to generate structured markdown content.
        """
        pass
```

#### 2.2 Update Knowledge Base Service

**File**: `backend/services/knowledge_base_service.py`

Add methods:
- `list_articles_by_pattern_group(pattern_group_id)`
- `get_articles_with_pattern_info()`
- Filter by `source_type`
- Filter by `tags`

#### 2.3 New API Endpoints

**File**: `backend/api/routes/knowledge_base.py`

```python
@router.post("/generate-from-pattern/{pattern_group_id}")
async def generate_article_from_pattern(
    pattern_group_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db)
) -> KnowledgeBaseResponse:
    """
    Generate a KB article from a pattern group.
    Uses LLM to create structured content.
    """
    pass

@router.get("/by-pattern/{pattern_group_id}")
async def get_articles_by_pattern(
    pattern_group_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> KnowledgeBaseListResponse:
    """Get all articles linked to a pattern group."""
    pass
```

---

### Part 3: Frontend Revamp

#### 3.1 Knowledge Base Page Structure

**New Design** (matching Edge Cases page):

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Knowledge Base                                                          │
│  Documentation, guides, and pattern-generated insights                  │
│                                                           [+ New Article]│
├─────────────────────────────────────────────────────────────────────────┤
│  [All Articles]  [Pattern Insights]  [Guides]  [Troubleshooting]        │
├─────────────────────────────────────────────────────────────────────────┤
│  🔍 Search articles...                    [Source ▼] [Category ▼]       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ 📄 Handling Cancellation Intent Edge Cases          [Auto] [high]│   │
│  │ Common patterns when users attempt to cancel orders...           │   │
│  │ 🔗 Pattern: Cancellation Intent Confusion (15 occurrences)       │   │
│  │ Updated: Dec 20, 2024 • 42 views                                 │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ 📄 Voice AI Testing Best Practices                  [Manual]    │   │
│  │ Guidelines for creating effective test scenarios...              │   │
│  │ Updated: Dec 15, 2024 • 128 views                                │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 3.2 Component Updates

**KnowledgeBase.tsx** - Complete revamp:
- Tabs: All Articles | Pattern Insights | Guides | Troubleshooting
- Source filter dropdown (All, Manual, Auto-Generated)
- Category filter pills
- Pattern link badges on cards
- Modern card design matching Edge Cases
- Stats banner (total articles, pattern-linked, etc.)

**ArticleView.tsx** - Enhancements:
- Show linked pattern group (if exists)
- Navigation to pattern detail
- Related articles section
- Tags display

**ArticleEditor.tsx** - Updates:
- Tags input (comma-separated or chips)
- Category dropdown (predefined options)
- Pattern link selector (optional)

#### 3.3 New Components

**PatternArticleCard.tsx** - Enhanced card for pattern-linked articles:
- Pattern name badge
- Occurrence count indicator
- Severity color coding
- "Auto-generated" indicator

---

### Part 4: Pattern Group Integration

#### 4.1 PatternGroupDetail.tsx Updates

Add "Generate KB Article" button:

```tsx
<button
  onClick={handleGenerateKBArticle}
  className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-primary to-primary-dark text-white rounded-lg"
>
  <BookOpen className="w-4 h-4 mr-2" />
  Generate KB Article
</button>
```

Show linked KB articles section:
```
┌─────────────────────────────────────────────────────────────────────────┐
│ 📚 Related Documentation                                                 │
├─────────────────────────────────────────────────────────────────────────┤
│ • Handling Cancellation Intent Edge Cases (auto-generated)              │
│ • Voice AI Cancellation Workflow Guide (manual)                         │
│                                                       [+ Generate New]  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### Part 5: LLM Content Generation

#### 5.1 Article Template

```markdown
# {Pattern Name}

## Overview
{LLM-generated summary of the pattern}

## Impact
- **Severity**: {severity}
- **Occurrences**: {count} edge cases identified
- **First Detected**: {first_seen}
- **Last Seen**: {last_seen}

## Common Triggers
{LLM analysis of edge case utterances and contexts}

## Example Edge Cases
1. **{edge_case_title}**: {brief description}
2. **{edge_case_title}**: {brief description}
...

## Root Cause Analysis
{LLM-generated analysis of why this pattern occurs}

## Recommended Actions
{From pattern.suggested_actions, enhanced by LLM}

## Prevention Strategies
{LLM-generated recommendations for test improvements}

## Related Patterns
{Links to similar pattern groups if any}

---
*This article was auto-generated from pattern analysis on {date}.*
*Pattern ID: {pattern_id}*
```

---

## File Changes Summary

### New Files
- `backend/services/kb_generation_service.py`
- `backend/alembic/versions/xxx_add_pattern_group_to_kb.py`
- `frontend/src/components/KnowledgeBase/PatternArticleCard.tsx`

### Modified Files
- `backend/models/knowledge_base.py` - Add pattern_group_id, source_type, tags
- `backend/api/routes/knowledge_base.py` - Add generation endpoints
- `backend/api/schemas/knowledge_base.py` - Add new fields to schemas
- `backend/services/knowledge_base_service.py` - Add pattern filtering
- `frontend/src/pages/KnowledgeBase/KnowledgeBase.tsx` - Complete revamp
- `frontend/src/pages/KnowledgeBase/ArticleView.tsx` - Add pattern info
- `frontend/src/pages/KnowledgeBase/ArticleEditor.tsx` - Add tags/category
- `frontend/src/pages/PatternGroups/PatternGroupDetail.tsx` - Add KB section
- `frontend/src/services/knowledgeBase.service.ts` - Add new API calls
- `frontend/src/types/knowledgeBase.ts` - Add new fields

---

## UI Design Guidelines

### Color Scheme
- Primary gradient: `linear-gradient(135deg, #5BA9AC 0%, #11484D 100%)`
- Cards: `bg-white dark:bg-gray-800`
- Borders: `border-gray-200 dark:border-gray-700`

### Component Patterns (from EdgeCaseLibrary)
- Header card with title, description, action buttons
- Tab navigation with counts
- Filter bar with search and dropdowns
- Card grid/list with hover effects
- Badge pills for categories/tags
- Loading spinner (custom styled)
- Empty states with emoji icons

### Typography
- Page title: `text-3xl font-bold`
- Section headers: `text-xl font-semibold`
- Card titles: `text-lg font-semibold`
- Body text: `text-sm`
- Metadata: `text-xs text-gray-500`

---

## LLM Configuration

KB article generation uses the LLM provider infrastructure. Configure via environment variables:

```bash
# Provider: openai, anthropic, or google
# If not set, uses template-based generation (no LLM calls)
KB_GENERATION_LLM_PROVIDER=openai

# Model (optional - defaults to provider's default if not set)
# OpenAI: gpt-4o | Anthropic: claude-sonnet-4-5-20250929 | Google: gemini-1.5-pro
KB_GENERATION_LLM_MODEL=gpt-4o
```

### How It Works

1. When generating a KB article from a pattern group, the route reads config
2. If `KB_GENERATION_LLM_PROVIDER` is set, creates the appropriate adapter
3. The adapter's `generate_text()` method is called with a structured prompt
4. If LLM fails or is not configured, falls back to template-based generation
5. Generated content includes: Overview, Impact, Common Triggers, Examples, Root Cause, Actions, Prevention

### Provider Adapters

| Provider | Adapter File | Default Model |
|----------|-------------|---------------|
| openai | `openai_adapter.py` | gpt-4o |
| anthropic | `anthropic_adapter.py` | claude-sonnet-4-5-20250929 |
| google | `google_adapter.py` | gemini-1.5-pro |

---

## Success Metrics

- [x] KB articles can be auto-generated from pattern groups
- [x] Pattern-linked articles show in KB with proper badges
- [x] KB page has modern UI with tabs and filters
- [x] Pattern detail shows related KB articles
- [x] Search finds both manual and auto-generated articles
- [x] Bidirectional navigation between patterns and articles
- [x] LLM provider configurable via environment variables
- [x] Model override supported per provider

---

## Implementation Order

1. **Database**: Add new fields to KB model + migration
2. **Backend Service**: KB generation service
3. **Backend API**: New endpoints
4. **Frontend Types**: Update TypeScript types
5. **Frontend Service**: Update API client
6. **Frontend UI**: Revamp KnowledgeBase.tsx
7. **Integration**: Pattern detail updates
8. **Testing**: End-to-end verification
9. **Documentation**: Update roadmap

---

*Created: December 25, 2025*
*Completed: December 26, 2025*
*Phase: 3 of Edge Case Workflow*

---

## Changelog

### December 26, 2025
- Added LLM provider configuration (`KB_GENERATION_LLM_PROVIDER`, `KB_GENERATION_LLM_MODEL`)
- Implemented `generate_text()` method in all adapters (OpenAI, Anthropic, Google)
- Updated KB generation service to use LLM adapters
- Added environment variable validation in config
- Falls back to template if LLM not configured or fails

### December 25, 2025
- Initial implementation of Phase 3
- Database schema updates (pattern_group_id, source_type, tags)
- KB generation service with template fallback
- API endpoints for generation and pattern filtering
- Frontend revamp with tabs, stats, and filters
- Pattern Group detail page KB integration
