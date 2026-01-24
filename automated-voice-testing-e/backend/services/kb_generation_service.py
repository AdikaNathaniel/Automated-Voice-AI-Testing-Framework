"""
Knowledge Base Generation Service

Phase 3: Auto-generates Knowledge Base articles from Pattern Groups using LLM.
Creates structured, searchable documentation from edge case patterns.

Uses the configured LLM provider (via KB_GENERATION_LLM_PROVIDER env var) to
generate rich, contextual content. Falls back to template-based generation
if no LLM is configured or if LLM generation fails.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.knowledge_base import KnowledgeBase
from models.pattern_group import PatternGroup, EdgeCasePatternLink
from models.edge_case import EdgeCase

if TYPE_CHECKING:
    from services.llm_providers.base import BaseLLMAdapter

logger = logging.getLogger(__name__)

# System prompt for KB article generation
KB_GENERATION_SYSTEM_PROMPT = """You are a technical documentation expert specializing in Voice AI systems.
Generate clear, well-structured Knowledge Base articles that help engineers understand and resolve issues.
Write in a professional, technical documentation style using markdown formatting.
Focus on actionable insights and practical recommendations."""


class KBGenerationService:
    """
    Generates Knowledge Base articles from Pattern Groups.

    Uses LLM adapter to create structured markdown content that documents:
    - Pattern overview and impact
    - Common triggers from edge cases
    - Root cause analysis
    - Recommended actions

    Falls back to template-based generation if no LLM adapter is provided.
    """

    def __init__(self, llm_adapter: Optional["BaseLLMAdapter"] = None) -> None:
        """
        Initialize the KB generation service.

        Args:
            llm_adapter: Optional LLM adapter for enhanced content generation.
                        Falls back to template-based generation if not provided.
        """
        self.llm_adapter = llm_adapter

    async def generate_from_pattern_group(
        self,
        db: AsyncSession,
        pattern_group_id: UUID,
        author_id: UUID,
        tenant_id: UUID,
        auto_publish: bool = False,
    ) -> KnowledgeBase:
        """
        Generate a KB article from a pattern group.

        Args:
            db: Database session
            pattern_group_id: ID of the pattern group to document
            author_id: User ID to attribute as author
            tenant_id: Tenant ID for multi-tenancy
            auto_publish: Whether to publish the article immediately

        Returns:
            KnowledgeBase: The created article

        Raises:
            ValueError: If pattern group not found
        """
        # Fetch pattern group with edge cases
        pattern = await self._get_pattern_with_edge_cases(db, pattern_group_id)
        if not pattern:
            raise ValueError(f"Pattern group {pattern_group_id} not found")

        # Check if article already exists for this pattern
        existing = await self._get_existing_article(db, pattern_group_id)
        if existing:
            raise ValueError(
                f"KB article already exists for pattern '{pattern.name}'. "
                f"Article ID: {existing.id}"
            )

        # Fetch linked edge cases for content generation
        edge_cases = await self._get_linked_edge_cases(db, pattern_group_id)

        # Generate article content
        title = self._generate_title(pattern)
        content = await self._generate_content(pattern, edge_cases)
        tags = self._generate_tags(pattern, edge_cases)
        category = self._determine_category(pattern)

        # Create the article
        article = KnowledgeBase(
            title=title,
            content=content,
            content_format="markdown",
            category=category,
            author_id=author_id,
            tenant_id=tenant_id,
            is_published=auto_publish,
            pattern_group_id=pattern_group_id,
            source_type="auto_generated",
            tags=tags,
        )

        db.add(article)
        await db.commit()
        await db.refresh(article)

        logger.info(
            f"Generated KB article '{title}' from pattern '{pattern.name}' "
            f"(ID: {article.id})"
        )

        return article

    async def _get_pattern_with_edge_cases(
        self,
        db: AsyncSession,
        pattern_group_id: UUID,
    ) -> Optional[PatternGroup]:
        """Fetch pattern group by ID."""
        result = await db.execute(
            select(PatternGroup).where(PatternGroup.id == pattern_group_id)
        )
        return result.scalar_one_or_none()

    async def _get_existing_article(
        self,
        db: AsyncSession,
        pattern_group_id: UUID,
    ) -> Optional[KnowledgeBase]:
        """Check if an article already exists for this pattern."""
        result = await db.execute(
            select(KnowledgeBase).where(
                KnowledgeBase.pattern_group_id == pattern_group_id
            )
        )
        return result.scalar_one_or_none()

    async def _get_linked_edge_cases(
        self,
        db: AsyncSession,
        pattern_group_id: UUID,
        limit: int = 10,
    ) -> List[EdgeCase]:
        """Fetch edge cases linked to this pattern."""
        result = await db.execute(
            select(EdgeCase)
            .join(EdgeCasePatternLink)
            .where(EdgeCasePatternLink.pattern_group_id == pattern_group_id)
            .order_by(EdgeCasePatternLink.added_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    def _generate_title(self, pattern: PatternGroup) -> str:
        """Generate article title from pattern."""
        # Clean up pattern name for title
        name = pattern.name
        if not name.lower().startswith(("handling", "understanding", "resolving")):
            name = f"Handling {name}"
        return name

    async def _generate_content(
        self,
        pattern: PatternGroup,
        edge_cases: List[EdgeCase],
    ) -> str:
        """
        Generate markdown content for the article.

        Uses LLM adapter if available, otherwise falls back to template.
        """
        if self.llm_adapter:
            try:
                return await self._generate_content_with_llm(pattern, edge_cases)
            except Exception as e:
                logger.warning(f"LLM content generation failed: {e}, using template")

        return self._generate_content_from_template(pattern, edge_cases)

    async def _generate_content_with_llm(
        self,
        pattern: PatternGroup,
        edge_cases: List[EdgeCase],
    ) -> str:
        """
        Use LLM adapter to generate rich article content.

        Args:
            pattern: The pattern group to document
            edge_cases: Related edge cases for context

        Returns:
            Generated markdown content

        Raises:
            Exception: If LLM generation fails
        """
        if not self.llm_adapter:
            raise ValueError("LLM adapter not configured")

        # Build context for LLM
        edge_case_summaries = []
        for ec in edge_cases[:5]:  # Limit to avoid token overflow
            summary = {
                "title": ec.title,
                "description": ec.description,
                "category": ec.category,
                "severity": ec.severity,
            }
            if ec.scenario_definition:
                summary["user_utterance"] = ec.scenario_definition.get("user_utterance")
                summary["expected_response"] = ec.scenario_definition.get("expected_response")
                summary["actual_response"] = ec.scenario_definition.get("actual_response")
            edge_case_summaries.append(summary)

        prompt = f"""Generate a comprehensive knowledge base article about the following edge case pattern.

Pattern Name: {pattern.name}
Pattern Description: {pattern.description or 'No description provided'}
Pattern Type: {pattern.pattern_type or 'General'}
Severity: {pattern.severity}
Occurrence Count: {pattern.occurrence_count}
Suggested Actions: {json.dumps(pattern.suggested_actions or [])}

Example Edge Cases:
{json.dumps(edge_case_summaries, indent=2)}

Generate a well-structured markdown article with these sections:
1. Overview - Brief summary of the pattern
2. Impact - Severity and business impact
3. Common Triggers - What causes this pattern to occur
4. Example Cases - Summarize 2-3 representative examples
5. Root Cause Analysis - Why this pattern happens
6. Recommended Actions - Steps to address the issue
7. Prevention Strategies - How to prevent future occurrences

Use proper markdown formatting with headers, bullet points, and tables where appropriate.
Do NOT include any meta-commentary or instructions in the output - only the article content.
"""

        # Use the LLM adapter's generate_text method
        # OpenRouter adapter now bypasses JSON mode for text generation,
        # so we get pure markdown directly without wrapping
        content = await self.llm_adapter.generate_text(
            prompt=prompt,
            system_prompt=KB_GENERATION_SYSTEM_PROMPT,
            max_tokens=4096,  # Increased limit for complete articles
        )

        logger.info(
            f"Generated KB content with LLM for pattern '{pattern.name}' "
            f"({len(content)} chars)"
        )

        return content.strip()

    def _generate_content_from_template(
        self,
        pattern: PatternGroup,
        edge_cases: List[EdgeCase],
    ) -> str:
        """Generate article content using a template."""
        # Build example cases section
        example_cases = ""
        for i, ec in enumerate(edge_cases[:5], 1):
            example_cases += f"\n### Example {i}: {ec.title}\n"
            if ec.description:
                example_cases += f"{ec.description}\n"
            if ec.scenario_definition:
                sd = ec.scenario_definition
                if sd.get("user_utterance"):
                    example_cases += f"\n**User Said:** \"{sd.get('user_utterance')}\"\n"
                if sd.get("actual_response"):
                    example_cases += f"\n**System Response:** \"{sd.get('actual_response')}\"\n"
            if ec.category:
                example_cases += f"\n*Category: {ec.category}*\n"

        # Build suggested actions section
        actions_section = ""
        if pattern.suggested_actions:
            for i, action in enumerate(pattern.suggested_actions, 1):
                actions_section += f"{i}. {action}\n"
        else:
            actions_section = "No specific actions documented yet. Review edge cases and determine appropriate remediation steps.\n"

        # Build the full article
        content = f"""# {pattern.name}

## Overview

{pattern.description or 'This pattern represents a recurring issue identified through edge case analysis.'}

This pattern was identified through automated analysis of {pattern.occurrence_count} similar edge cases.

## Impact

| Metric | Value |
|--------|-------|
| **Severity** | {pattern.severity.upper()} |
| **Total Occurrences** | {pattern.occurrence_count} |
| **First Detected** | {pattern.first_seen.strftime('%B %d, %Y') if pattern.first_seen else 'Unknown'} |
| **Last Observed** | {pattern.last_seen.strftime('%B %d, %Y') if pattern.last_seen else 'Unknown'} |
| **Status** | {pattern.status.title()} |

## Common Triggers

This pattern typically occurs when:
- Voice AI encounters ambiguous or unexpected user input
- System confidence scores fall below optimal thresholds
- Context from previous conversation turns is lost or misinterpreted

## Example Cases
{example_cases if example_cases else 'No example cases available.'}

## Recommended Actions

{actions_section}

## Prevention Strategies

1. **Enhance Test Coverage**: Create test scenarios that specifically target this pattern
2. **Improve Intent Classification**: Review and refine intent matching rules
3. **Add Disambiguation Steps**: When confidence is low, ask clarifying questions
4. **Monitor Trends**: Track occurrence rate to measure improvement over time

---

*This article was auto-generated from pattern analysis.*
*Pattern ID: {pattern.id}*
*Generated: {datetime.utcnow().strftime('%B %d, %Y')}*
"""
        return content

    def _generate_tags(
        self,
        pattern: PatternGroup,
        edge_cases: List[EdgeCase],
    ) -> List[str]:
        """Generate tags based on pattern and edge cases."""
        tags = set()

        # Add severity as tag
        if pattern.severity:
            tags.add(pattern.severity.lower())

        # Add pattern type as tag
        if pattern.pattern_type:
            tags.add(pattern.pattern_type.lower().replace(" ", "-"))

        # Add status
        tags.add(f"status-{pattern.status}")

        # Add auto-generated marker
        tags.add("auto-generated")

        # Collect unique categories from edge cases
        for ec in edge_cases:
            if ec.category:
                tags.add(ec.category.lower().replace("_", "-"))
            # Add edge case tags (limit to avoid explosion)
            for tag in (ec.tags or [])[:3]:
                tags.add(tag.lower())

        return sorted(list(tags))[:10]  # Limit to 10 tags

    def _determine_category(self, pattern: PatternGroup) -> str:
        """Determine article category based on pattern characteristics."""
        if pattern.severity in ("critical", "high"):
            return "troubleshooting"
        if pattern.pattern_type:
            ptype = pattern.pattern_type.lower()
            if "ambig" in ptype or "intent" in ptype:
                return "edge-cases"
            if "context" in ptype:
                return "conversation-flow"
        return "pattern-insights"


# Module-level function for convenience
async def generate_kb_from_pattern(
    db: AsyncSession,
    pattern_group_id: UUID,
    author_id: UUID,
    auto_publish: bool = False,
    llm_adapter: Optional["BaseLLMAdapter"] = None,
) -> KnowledgeBase:
    """
    Convenience function to generate KB article from pattern.

    Args:
        db: Database session
        pattern_group_id: Pattern group to document
        author_id: Author user ID
        auto_publish: Publish immediately if True
        llm_adapter: Optional LLM adapter for enhanced content generation

    Returns:
        KnowledgeBase: Created article
    """
    service = KBGenerationService(llm_adapter=llm_adapter)
    return await service.generate_from_pattern_group(
        db=db,
        pattern_group_id=pattern_group_id,
        author_id=author_id,
        auto_publish=auto_publish,
    )
