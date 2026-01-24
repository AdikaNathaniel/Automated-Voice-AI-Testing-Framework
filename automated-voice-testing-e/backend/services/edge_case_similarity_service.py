"""
EdgeCaseSimilarityService - Find and group similar edge cases.

Part of Phase 2: Pattern Recognition & Grouping.
Uses semantic similarity, category matching, and failure pattern analysis
to identify related edge cases.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sentence_transformers import SentenceTransformer
import numpy as np

from models.edge_case import EdgeCase
from models.pattern_group import PatternGroup, EdgeCasePatternLink
from api.config import get_settings
from services.llm_pattern_analysis_service import (
    LLMPatternAnalysisService,
    PatternAnalysis,
    PatternDetails
)
import logging

logger = logging.getLogger(__name__)


class EdgeCaseSimilarityService:
    """
    Service for finding similar edge cases and grouping them into patterns.

    Uses multiple similarity signals:
    - Semantic similarity of user utterances (sentence transformers)
    - Category matching
    - Language code matching
    - Confidence score similarity
    - Tag overlap
    """

    def __init__(self, db: AsyncSession, use_llm: bool = True):
        """
        Initialize the similarity service.

        Args:
            db: Database session
            use_llm: Whether to use LLM enhancement (default: True)
        """
        self.db = db
        self.settings = get_settings()
        self._model: Optional[SentenceTransformer] = None

        # Initialize LLM service if requested and API key is available
        # Note: tenant_id will be extracted from edge_case when needed
        if use_llm:
            llm_service = LLMPatternAnalysisService(db=db)
            if llm_service.enabled:
                self.llm_service = llm_service
                self.use_llm = True
            else:
                logger.warning("OPENROUTER_API_KEY not configured, disabling LLM pattern analysis")
                self.llm_service = None
                self.use_llm = False
        else:
            self.llm_service = None
            self.use_llm = False

    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the sentence transformer model."""
        if self._model is None:
            model_name = self.settings.SEMANTIC_SIMILARITY_MODEL
            self._model = SentenceTransformer(model_name)
        return self._model

    async def find_similar_edge_cases(
        self,
        edge_case: EdgeCase,
        threshold: float = 0.85,
        limit: int = 10,
        time_window_days: Optional[int] = 30
    ) -> List[Dict[str, Any]]:
        """
        Find edge cases similar to the given edge case.

        Args:
            edge_case: The edge case to find matches for
            threshold: Minimum similarity score (0.0-1.0)
            limit: Maximum number of similar cases to return
            time_window_days: Only consider cases from last N days (None = all)

        Returns:
            List of dicts with 'edge_case' and 'similarity_score'
        """
        # Build query for candidate edge cases
        query = select(EdgeCase).where(
            and_(
                EdgeCase.id != edge_case.id,  # Exclude self
                EdgeCase.auto_created == True  # Only auto-created cases
            )
        )

        # Filter by time window if specified
        if time_window_days:
            cutoff_date = datetime.utcnow() - timedelta(days=time_window_days)
            query = query.where(EdgeCase.created_at >= cutoff_date)

        # Execute query
        result = await self.db.execute(query)
        candidates = result.scalars().all()

        if not candidates:
            return []

        # Calculate similarity scores for each candidate
        similarities = []
        for candidate in candidates:
            score = self._calculate_similarity(edge_case, candidate)
            if score >= threshold:
                similarities.append({
                    'edge_case': candidate,
                    'similarity_score': score
                })

        # Sort by similarity score (highest first)
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)

        # Return top N
        return similarities[:limit]

    def _calculate_similarity(
        self,
        case1: EdgeCase,
        case2: EdgeCase
    ) -> float:
        """
        Calculate overall similarity score between two edge cases.

        Combines multiple signals with weighted average:
        - Semantic similarity (40%)
        - Category match (20%)
        - Language match (15%)
        - Confidence similarity (10%)
        - Tag overlap (15%)

        Args:
            case1: First edge case
            case2: Second edge case

        Returns:
            Similarity score between 0.0 and 1.0
        """
        weights = {
            'semantic': 0.40,
            'category': 0.20,
            'language': 0.15,
            'confidence': 0.10,
            'tags': 0.15
        }

        scores = {}

        # 1. Semantic similarity of utterances
        scores['semantic'] = self._semantic_similarity(case1, case2)

        # 2. Category matching
        scores['category'] = self._category_similarity(case1, case2)

        # 3. Language matching
        scores['language'] = self._language_similarity(case1, case2)

        # 4. Confidence score similarity
        scores['confidence'] = self._confidence_similarity(case1, case2)

        # 5. Tag overlap
        scores['tags'] = self._tag_similarity(case1, case2)

        # Weighted average
        total_score = sum(
            scores[key] * weights[key]
            for key in weights.keys()
        )

        return total_score

    def _semantic_similarity(
        self,
        case1: EdgeCase,
        case2: EdgeCase
    ) -> float:
        """
        Calculate semantic similarity between user utterances.

        Uses sentence transformer embeddings and cosine similarity.

        Args:
            case1: First edge case
            case2: Second edge case

        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Extract utterances from scenario definitions
        utterance1 = case1.scenario_definition.get('user_utterance', '')
        utterance2 = case2.scenario_definition.get('user_utterance', '')

        if not utterance1 or not utterance2:
            return 0.0

        # Generate embeddings
        embeddings = self.model.encode([utterance1, utterance2])

        # Calculate cosine similarity
        similarity = np.dot(embeddings[0], embeddings[1]) / (
            np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
        )

        # Convert from [-1, 1] to [0, 1]
        return (similarity + 1) / 2

    def _category_similarity(
        self,
        case1: EdgeCase,
        case2: EdgeCase
    ) -> float:
        """
        Check if edge cases have the same category.

        Args:
            case1: First edge case
            case2: Second edge case

        Returns:
            1.0 if categories match, 0.0 otherwise
        """
        if not case1.category or not case2.category:
            return 0.0

        return 1.0 if case1.category == case2.category else 0.0

    def _language_similarity(
        self,
        case1: EdgeCase,
        case2: EdgeCase
    ) -> float:
        """
        Check if edge cases have the same language code.

        Args:
            case1: First edge case
            case2: Second edge case

        Returns:
            1.0 if languages match, 0.0 otherwise
        """
        lang1 = case1.scenario_definition.get('language_code')
        lang2 = case2.scenario_definition.get('language_code')

        if not lang1 or not lang2:
            return 0.0

        return 1.0 if lang1 == lang2 else 0.0

    def _confidence_similarity(
        self,
        case1: EdgeCase,
        case2: EdgeCase
    ) -> float:
        """
        Calculate similarity based on confidence scores.

        Edge cases with similar confidence levels likely share patterns.

        Args:
            case1: First edge case
            case2: Second edge case

        Returns:
            Similarity score between 0.0 and 1.0
        """
        conf1 = case1.scenario_definition.get('confidence_score')
        conf2 = case2.scenario_definition.get('confidence_score')

        if conf1 is None or conf2 is None:
            return 0.0

        # Calculate absolute difference
        diff = abs(conf1 - conf2)

        # Convert to similarity (smaller diff = higher similarity)
        # diff of 0.0 → similarity 1.0
        # diff of 1.0 → similarity 0.0
        return 1.0 - diff

    def _tag_similarity(
        self,
        case1: EdgeCase,
        case2: EdgeCase
    ) -> float:
        """
        Calculate Jaccard similarity of tags.

        Jaccard = |intersection| / |union|

        Args:
            case1: First edge case
            case2: Second edge case

        Returns:
            Similarity score between 0.0 and 1.0
        """
        tags1 = set(case1.tags or [])
        tags2 = set(case2.tags or [])

        if not tags1 and not tags2:
            return 0.0

        if not tags1 or not tags2:
            return 0.0

        intersection = len(tags1 & tags2)
        union = len(tags1 | tags2)

        return intersection / union if union > 0 else 0.0

    async def find_or_create_pattern_group(
        self,
        edge_cases: List[EdgeCase],
        pattern_name: Optional[str] = None,
        pattern_description: Optional[str] = None
    ) -> PatternGroup:
        """
        Find existing pattern group or create a new one for similar edge cases.

        Args:
            edge_cases: List of similar edge cases
            pattern_name: Optional custom name for the pattern
            pattern_description: Optional custom description

        Returns:
            PatternGroup instance
        """
        if not edge_cases:
            raise ValueError("edge_cases list cannot be empty")

        # Auto-generate pattern name if not provided
        if not pattern_name:
            pattern_name = self._generate_pattern_name(edge_cases)

        # Auto-generate description if not provided
        if not pattern_description:
            pattern_description = self._generate_pattern_description(
                edge_cases
            )

        # Check if similar pattern already exists
        # (same name or similar edge cases already grouped)
        existing_pattern = await self._find_existing_pattern(
            pattern_name,
            edge_cases
        )

        if existing_pattern:
            # Update existing pattern
            existing_pattern.occurrence_count = len(edge_cases)
            existing_pattern.last_seen = datetime.utcnow()
            await self.db.commit()
            return existing_pattern

        # Create new pattern group
        pattern = PatternGroup(
            name=pattern_name,
            description=pattern_description,
            pattern_type=self._detect_pattern_type(edge_cases),
            severity=self._determine_severity(edge_cases),
            occurrence_count=len(edge_cases),
            status='active',
            suggested_actions=self._generate_suggested_actions(edge_cases),
            pattern_metadata=self._build_pattern_metadata(edge_cases)
        )

        self.db.add(pattern)
        await self.db.flush()  # Get pattern ID

        # Link all edge cases to this pattern
        for edge_case in edge_cases:
            link = EdgeCasePatternLink(
                edge_case_id=edge_case.id,
                pattern_group_id=pattern.id,
                similarity_score=1.0,  # Within-group similarity
                added_at=datetime.utcnow()
            )
            self.db.add(link)

        await self.db.commit()
        await self.db.refresh(pattern)

        return pattern

    def _generate_pattern_name(self, edge_cases: List[EdgeCase]) -> str:
        """Generate a descriptive name for the pattern."""
        # Use the most common category
        categories = [ec.category for ec in edge_cases if ec.category]
        if categories:
            most_common_category = max(set(categories), key=categories.count)
            return f"Pattern: {most_common_category.replace('_', ' ').title()}"

        return f"Pattern Group {datetime.utcnow().strftime('%Y%m%d')}"

    def _generate_pattern_description(
        self,
        edge_cases: List[EdgeCase]
    ) -> str:
        """Generate a description for the pattern."""
        count = len(edge_cases)
        categories = list(set(ec.category for ec in edge_cases if ec.category))

        return (
            f"Pattern identified from {count} similar edge cases. "
            f"Categories: {', '.join(categories) if categories else 'Mixed'}."
        )

    def _detect_pattern_type(self, edge_cases: List[EdgeCase]) -> str:
        """Detect the type of pattern based on edge case characteristics."""
        # Analyze common characteristics
        categories = [ec.category for ec in edge_cases if ec.category]

        if categories:
            most_common = max(set(categories), key=categories.count)
            return most_common.split('_')[0]  # e.g., "boundary_condition" → "boundary"

        return "mixed"

    def _determine_severity(self, edge_cases: List[EdgeCase]) -> str:
        """Determine severity based on frequency and edge case severities."""
        count = len(edge_cases)

        # More occurrences = higher severity
        if count >= 10:
            return "critical"
        elif count >= 5:
            return "high"
        elif count >= 3:
            return "medium"
        else:
            return "low"

    def _generate_suggested_actions(
        self,
        edge_cases: List[EdgeCase]
    ) -> List[str]:
        """Generate actionable suggestions based on the pattern."""
        actions = [
            "Review similar edge cases to identify root cause",
            "Update test scenarios to cover this pattern",
            "Consider adjusting validation thresholds"
        ]

        # Add category-specific suggestions
        categories = [ec.category for ec in edge_cases if ec.category]
        if 'boundary_condition' in categories:
            actions.append("Review confidence score thresholds")

        if 'high_confidence_failure' in categories:
            actions.append("Investigate false confidence in AI responses")

        return actions

    def _build_pattern_metadata(
        self,
        edge_cases: List[EdgeCase]
    ) -> Dict[str, Any]:
        """Build metadata dictionary for the pattern."""
        # Extract common utterances
        utterances = [
            ec.scenario_definition.get('user_utterance', '')
            for ec in edge_cases
        ]

        # Get language codes
        languages = list(set(
            ec.scenario_definition.get('language_code')
            for ec in edge_cases
            if ec.scenario_definition.get('language_code')
        ))

        # Calculate average confidence
        confidences = [
            ec.scenario_definition.get('confidence_score')
            for ec in edge_cases
            if ec.scenario_definition.get('confidence_score') is not None
        ]
        avg_confidence = (
            sum(confidences) / len(confidences) if confidences else None
        )

        return {
            "sample_utterances": utterances[:5],  # First 5 examples
            "affected_languages": languages,
            "avg_confidence": avg_confidence,
            "edge_case_count": len(edge_cases),
            "trend": "stable"  # Updated by background job
        }

    async def _find_existing_pattern(
        self,
        pattern_name: str,
        edge_cases: List[EdgeCase]
    ) -> Optional[PatternGroup]:
        """
        Find existing pattern group with same name or overlapping edge cases.

        Args:
            pattern_name: Name to search for
            edge_cases: Edge cases to check for overlap

        Returns:
            Existing PatternGroup if found, None otherwise
        """
        # Search by name
        result = await self.db.execute(
            select(PatternGroup).where(
                PatternGroup.name == pattern_name,
                PatternGroup.status == 'active'
            )
        )
        existing = result.scalar_one_or_none()

        return existing

    # ========================================================================
    # Main Entry Point - LLM-First Pattern Recognition
    # ========================================================================

    async def analyze_and_group(
        self,
        edge_case: EdgeCase,
        threshold: float = 0.80,
        llm_confidence_threshold: float = 0.70,
        min_pattern_size: int = 3
    ) -> Optional[PatternGroup]:
        """
        Main entry point for pattern recognition.

        PRIORITY ORDER:
        1. LLM-based analysis (PRIMARY) - Uses AI to understand patterns
        2. Semantic similarity (FALLBACK) - Used only if LLM fails or unavailable

        Args:
            edge_case: The edge case to analyze
            threshold: Similarity threshold for fallback clustering
            llm_confidence_threshold: Minimum LLM confidence for pattern matching
            min_pattern_size: Minimum number of cases required to form a pattern

        Returns:
            PatternGroup if pattern found/created, None otherwise
        """
        # Try LLM-first approach
        if self.use_llm and self.llm_service:
            logger.info(f"Using LLM-first approach for edge case {edge_case.id}")
            try:
                result = await self._analyze_with_llm_primary(
                    edge_case,
                    llm_confidence_threshold=llm_confidence_threshold,
                    min_pattern_size=min_pattern_size
                )
                if result:
                    return result
                logger.info("LLM did not find/create pattern, trying semantic fallback")
            except Exception as e:
                logger.warning(f"LLM-first approach failed: {e}, using semantic fallback")

        # Fallback to semantic similarity approach
        logger.info(f"Using semantic similarity fallback for edge case {edge_case.id}")
        return await self._group_with_semantic_similarity(
            edge_case,
            threshold=threshold,
            min_pattern_size=min_pattern_size
        )

    async def _analyze_with_llm_primary(
        self,
        edge_case: EdgeCase,
        llm_confidence_threshold: float = 0.70,
        min_pattern_size: int = 3
    ) -> Optional[PatternGroup]:
        """
        LLM-primary pattern recognition.

        Uses LLM for:
        1. Analyzing the edge case to understand its failure pattern
        2. Matching against existing patterns using semantic understanding
        3. Creating new patterns with intelligent descriptions

        Args:
            edge_case: The edge case to analyze
            llm_confidence_threshold: Minimum confidence for LLM pattern matching
            min_pattern_size: Minimum cases required to form a pattern

        Returns:
            PatternGroup if pattern found/created, None otherwise
        """
        logger.info(f"LLM analyzing edge case {edge_case.id}")

        # Set tenant_id for cost tracking
        self.llm_service.tenant_id = edge_case.tenant_id

        # Step 1: LLM analyzes the edge case FIRST
        llm_analysis = await self.llm_service.analyze_edge_case(edge_case)
        logger.info(
            f"LLM analysis: {llm_analysis.pattern_name} "
            f"(confidence: {llm_analysis.confidence})"
        )

        # Step 2: Check if matches existing pattern (LLM decides)
        existing_patterns = await self._get_active_patterns()

        if existing_patterns:
            pattern_match = await self.llm_service.match_to_existing_pattern(
                edge_case,
                llm_analysis,
                existing_patterns
            )

            if pattern_match.matches and pattern_match.confidence > llm_confidence_threshold:
                logger.info(
                    f"LLM matched to pattern: {pattern_match.pattern_id} "
                    f"(confidence: {pattern_match.confidence}, threshold: {llm_confidence_threshold})"
                )
                pattern = await self._get_pattern_by_id(pattern_match.pattern_id)
                if pattern:
                    await self._add_to_existing_pattern(edge_case, pattern)
                    return pattern

        # Step 3: Find similar cases to form new pattern (semantic assists LLM)
        similar_results = await self.find_similar_edge_cases(
            edge_case,
            threshold=0.75,  # Lower threshold when LLM guides
            limit=20,
            time_window_days=30
        )

        similar_cases = [edge_case] + [r['edge_case'] for r in similar_results]

        # Step 4: Create new pattern if enough similar cases
        if len(similar_cases) >= min_pattern_size:
            logger.info(f"Creating LLM-generated pattern from {len(similar_cases)} cases (min: {min_pattern_size})")
            return await self._create_pattern_with_llm(similar_cases, llm_analysis)

        logger.info(f"Not enough similar cases ({len(similar_cases)}/{min_pattern_size}) for pattern")
        return None

    async def _group_with_semantic_similarity(
        self,
        edge_case: EdgeCase,
        threshold: float = 0.80,
        min_pattern_size: int = 3
    ) -> Optional[PatternGroup]:
        """
        Semantic similarity fallback for pattern recognition.

        Used when:
        - LLM service is not configured (use_llm=False)
        - LLM service fails
        - LLM analysis doesn't find patterns

        Args:
            edge_case: The edge case to analyze
            threshold: Minimum similarity score for grouping
            min_pattern_size: Minimum cases required to form a pattern

        Returns:
            PatternGroup if pattern found/created, None otherwise
        """
        logger.info(f"Semantic similarity grouping for edge case {edge_case.id}")

        similar_results = await self.find_similar_edge_cases(
            edge_case,
            threshold=threshold,
            limit=20,
            time_window_days=30
        )

        similar_cases = [edge_case] + [r['edge_case'] for r in similar_results]

        if len(similar_cases) >= min_pattern_size:
            logger.info(f"Found {len(similar_cases)} similar cases (min: {min_pattern_size}), creating pattern")
            return await self.find_or_create_pattern_group(edge_cases=similar_cases)

        logger.info(f"Not enough similar cases ({len(similar_cases)}/{min_pattern_size}) for pattern")
        return None

    # Legacy method - delegates to unified entry point
    async def analyze_and_group_with_llm(
        self,
        edge_case: EdgeCase,
        threshold: float = 0.80
    ) -> Optional[PatternGroup]:
        """
        Legacy method for backward compatibility.
        Delegates to analyze_and_group() which uses LLM-first approach.
        """
        return await self.analyze_and_group(edge_case, threshold)

    async def _create_pattern_with_llm(
        self,
        edge_cases: List[EdgeCase],
        initial_analysis: Optional[PatternAnalysis] = None
    ) -> PatternGroup:
        """
        Create a new pattern group using LLM-generated details.

        Args:
            edge_cases: Edge cases to group
            initial_analysis: Optional initial LLM analysis

        Returns:
            Created PatternGroup
        """
        # Set tenant_id for cost tracking (use first edge case's tenant)
        if edge_cases and hasattr(edge_cases[0], 'tenant_id'):
            self.llm_service.tenant_id = edge_cases[0].tenant_id

        # Generate comprehensive pattern details with LLM
        pattern_details = await self.llm_service.generate_pattern_details(
            edge_cases
        )

        logger.info(f"Generated pattern: {pattern_details.name}")

        # Create pattern group with LLM-generated info
        pattern = PatternGroup(
            name=pattern_details.name,
            description=pattern_details.description,
            pattern_type=initial_analysis.pattern_type if initial_analysis else "mixed",
            severity=self._determine_severity(edge_cases),
            occurrence_count=len(edge_cases),
            status='active',
            suggested_actions=pattern_details.suggested_actions,
            pattern_metadata={
                **self._build_pattern_metadata(edge_cases),
                "keywords": pattern_details.keywords,
                "root_cause": pattern_details.root_cause,
                "llm_generated": True
            }
        )

        self.db.add(pattern)
        await self.db.flush()

        # Link all edge cases
        for edge_case in edge_cases:
            link = EdgeCasePatternLink(
                edge_case_id=edge_case.id,
                pattern_group_id=pattern.id,
                similarity_score=1.0,
                added_at=datetime.utcnow()
            )
            self.db.add(link)

            # Mark as grouped
            edge_case.status = 'grouped'

        await self.db.commit()
        await self.db.refresh(pattern)

        return pattern

    async def _add_to_existing_pattern(
        self,
        edge_case: EdgeCase,
        pattern: PatternGroup
    ) -> None:
        """
        Add an edge case to an existing pattern group.

        Args:
            edge_case: Edge case to add
            pattern: Pattern group to add to
        """
        # Check if already linked
        result = await self.db.execute(
            select(EdgeCasePatternLink).where(
                and_(
                    EdgeCasePatternLink.edge_case_id == edge_case.id,
                    EdgeCasePatternLink.pattern_group_id == pattern.id
                )
            )
        )
        existing_link = result.scalar_one_or_none()

        if existing_link:
            logger.info(f"Edge case {edge_case.id} already in pattern {pattern.id}")
            return

        # Create link
        link = EdgeCasePatternLink(
            edge_case_id=edge_case.id,
            pattern_group_id=pattern.id,
            similarity_score=0.9,
            added_at=datetime.utcnow()
        )
        self.db.add(link)

        # Update pattern stats
        pattern.occurrence_count += 1
        pattern.last_seen = datetime.utcnow()

        # Mark edge case as grouped
        edge_case.status = 'grouped'

        await self.db.commit()

        logger.info(f"Added edge case {edge_case.id} to pattern {pattern.id}")

    async def _get_active_patterns(self) -> List[PatternGroup]:
        """Get all active pattern groups."""
        result = await self.db.execute(
            select(PatternGroup).where(
                PatternGroup.status == 'active'
            ).order_by(PatternGroup.last_seen.desc())
        )
        return result.scalars().all()

    async def _get_pattern_by_id(self, pattern_id: str) -> Optional[PatternGroup]:
        """Get pattern by ID."""
        try:
            from uuid import UUID
            result = await self.db.execute(
                select(PatternGroup).where(
                    PatternGroup.id == UUID(pattern_id)
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get pattern {pattern_id}: {e}")
            return None

