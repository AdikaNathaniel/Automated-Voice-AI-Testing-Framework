"""
LLM Pattern Analysis Service

Uses LLMs (via OpenRouter) to analyze edge cases and generate intelligent
pattern names, descriptions, and matching logic.

Part of Phase 2 Enhanced: LLM-powered pattern recognition.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID
import json
import logging
import time

import httpx
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from models.edge_case import EdgeCase
from models.pattern_group import PatternGroup
from models.llm_usage_log import LLMUsageLog, calculate_cost
from api.config import get_settings

logger = logging.getLogger(__name__)


class PatternAnalysis(BaseModel):
    """LLM analysis result for a pattern."""
    pattern_name: str
    pattern_type: str
    root_cause: str
    keywords: List[str]
    confidence: float = 0.0


class PatternDetails(BaseModel):
    """Complete pattern information from LLM."""
    name: str
    description: str
    root_cause: str
    suggested_actions: List[str]
    keywords: List[str]


class PatternMatch(BaseModel):
    """Result of matching edge case to existing pattern."""
    matches: bool
    pattern_id: Optional[str] = None
    confidence: float = 0.0
    reasoning: str = ""


class LLMPatternAnalysisService:
    """
    Service for LLM-powered pattern analysis.

    Uses Claude Sonnet (via OpenRouter) for intelligent pattern recognition.
    Automatically tracks API usage and costs for monitoring and budgeting.
    """

    def __init__(self, db: Optional[AsyncSession] = None, tenant_id: Optional[UUID] = None):
        """
        Initialize the LLM pattern analysis service.

        Args:
            db: Database session for cost tracking (optional)
            tenant_id: Tenant ID for cost attribution (optional)
        """
        self.settings = get_settings()
        self.base_url = self.settings.OPENROUTER_BASE_URL
        self.api_key = self.settings.OPENROUTER_API_KEY
        self.model = self.settings.LLM_CURATOR_MODEL  # Use Claude Sonnet
        self.enabled = bool(self.api_key)  # Disable if no API key
        self.db = db
        self.tenant_id = tenant_id

    async def analyze_edge_case(
        self,
        edge_case: EdgeCase
    ) -> PatternAnalysis:
        """
        Analyze a single edge case to understand its failure pattern.

        Uses validator feedback, utterances, and responses to determine
        the root cause and pattern type.

        Args:
            edge_case: The edge case to analyze

        Returns:
            PatternAnalysis with LLM insights
        """
        # Extract data from edge case
        scenario_def = edge_case.scenario_definition or {}
        utterance = scenario_def.get('user_utterance', 'N/A')
        actual = scenario_def.get('actual_response', 'N/A')

        # Get validation criteria
        expected_cmd = scenario_def.get('expected_command_kind')
        expected_patterns = scenario_def.get('expected_response_content')
        expected_confidence = scenario_def.get('expected_asr_confidence_min')

        # Get validation results
        cmd_match = scenario_def.get('command_kind_match_score')
        asr_conf = scenario_def.get('asr_confidence_score')
        houndify_pass = scenario_def.get('houndify_passed')
        llm_pass = scenario_def.get('llm_passed')
        final_dec = scenario_def.get('final_decision')

        # Get validator feedback from description
        feedback = edge_case.description or "No feedback provided"

        # Build validation criteria section
        criteria_lines = []
        if expected_cmd:
            criteria_lines.append(f"- Expected CommandKind: {expected_cmd}")
        if expected_patterns:
            criteria_lines.append(f"- Expected Response Patterns: {json.dumps(expected_patterns)}")
        if expected_confidence:
            criteria_lines.append(f"- Min ASR Confidence: {expected_confidence}")
        criteria_text = '\n'.join(criteria_lines) if criteria_lines else "- Validation based on behavioral criteria"

        # Build validation results section
        results_lines = []
        if cmd_match is not None:
            results_lines.append(f"- CommandKind Match: {cmd_match}")
        if asr_conf is not None:
            results_lines.append(f"- ASR Confidence: {asr_conf}")
        if houndify_pass is not None:
            results_lines.append(f"- Houndify Validation: {'PASSED' if houndify_pass else 'FAILED'}")
        if llm_pass is not None:
            results_lines.append(f"- LLM Validation: {'PASSED' if llm_pass else 'FAILED'}")
        if final_dec:
            results_lines.append(f"- Final Decision: {final_dec}")
        results_text = '\n'.join(results_lines) if results_lines else "- No validation results available"

        prompt = f"""Analyze this voice AI edge case and identify the failure pattern.

USER UTTERANCE: "{utterance}"
AI RESPONSE: "{actual}"

VALIDATION CRITERIA:
{criteria_text}

VALIDATION RESULTS:
{results_text}

VALIDATOR FEEDBACK: "{feedback}"
AUTO-DETECTED CATEGORY: {edge_case.category or 'unknown'}

Determine:
1. What is the root cause pattern? (e.g., "Time reference confusion", "Entity extraction error")
2. What type of pattern is this? (semantic, entity, context, ambiguity, language, other)
3. What are 3-5 keywords that characterize this pattern?

Respond ONLY with valid JSON in this exact format:
{{
    "pattern_name": "concise descriptive name (2-5 words)",
    "pattern_type": "semantic|entity|context|ambiguity|language|other",
    "root_cause": "brief explanation of why this fails",
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "confidence": 0.0-1.0
}}"""

        try:
            response = await self._call_llm(
                prompt,
                temperature=0.3,
                operation="analyze_edge_case",
                metadata={
                    "edge_case_id": str(edge_case.id),
                    "category": edge_case.category,
                    "language": scenario_def.get('language_code')
                }
            )

            # Parse JSON response
            analysis_data = self._parse_json_response(response)

            return PatternAnalysis(**analysis_data)

        except Exception as e:
            logger.error(f"Failed to analyze edge case with LLM: {e}")
            # Fallback to basic analysis
            return PatternAnalysis(
                pattern_name=edge_case.category or "Unknown Pattern",
                pattern_type="other",
                root_cause="Could not determine root cause",
                keywords=[],
                confidence=0.0
            )

    async def generate_pattern_details(
        self,
        edge_cases: List[EdgeCase]
    ) -> PatternDetails:
        """
        Generate comprehensive pattern information from multiple edge cases.

        Analyzes all edge cases together to create a cohesive pattern
        description with actionable recommendations.

        Args:
            edge_cases: List of similar edge cases

        Returns:
            PatternDetails with name, description, and suggestions
        """
        # Collect feedback and utterances
        feedbacks = []
        utterances = []

        for ec in edge_cases:
            if ec.description:
                feedbacks.append(ec.description)

            scenario_def = ec.scenario_definition or {}
            utterance = scenario_def.get('user_utterance')
            if utterance:
                utterances.append(utterance)

        # Limit to first 10 for context window
        feedbacks = feedbacks[:10]
        utterances = utterances[:10]

        prompt = f"""Analyze these {len(edge_cases)} similar voice AI edge cases and create a comprehensive pattern description.

VALIDATOR FEEDBACK:
{self._format_list(feedbacks)}

SAMPLE USER UTTERANCES:
{self._format_list(utterances)}

AUTO-DETECTED CATEGORIES: {', '.join(set(ec.category for ec in edge_cases if ec.category))}

Generate a comprehensive pattern description including:
1. A concise, descriptive pattern name (2-5 words)
2. A detailed description (2-3 sentences explaining the pattern)
3. Root cause analysis (what's causing this pattern)
4. 3-5 specific, actionable suggestions to fix this issue
5. 3-5 keywords that characterize this pattern

Respond ONLY with valid JSON in this exact format:
{{
    "name": "Pattern Name",
    "description": "Detailed description...",
    "root_cause": "Root cause explanation...",
    "suggested_actions": [
        "Specific action 1",
        "Specific action 2",
        "Specific action 3"
    ],
    "keywords": ["keyword1", "keyword2", "keyword3"]
}}"""

        try:
            response = await self._call_llm(
                prompt,
                temperature=0.5,
                operation="generate_pattern_details",
                metadata={
                    "edge_case_count": len(edge_cases),
                    "edge_case_ids": [str(ec.id) for ec in edge_cases[:5]],  # First 5
                    "categories": list(set(ec.category for ec in edge_cases if ec.category))
                }
            )

            # Parse JSON response
            details_data = self._parse_json_response(response)

            return PatternDetails(**details_data)

        except Exception as e:
            logger.error(f"Failed to generate pattern details with LLM: {e}")
            # Fallback to basic pattern
            return self._generate_fallback_pattern(edge_cases)

    async def match_to_existing_pattern(
        self,
        edge_case: EdgeCase,
        llm_analysis: PatternAnalysis,
        existing_patterns: List[PatternGroup]
    ) -> PatternMatch:
        """
        Determine if an edge case matches any existing pattern.

        Uses LLM to intelligently compare the edge case to existing
        patterns based on semantic similarity and context.

        Args:
            edge_case: The edge case to match
            llm_analysis: LLM analysis of the edge case
            existing_patterns: List of existing pattern groups

        Returns:
            PatternMatch indicating if and which pattern matches
        """
        if not existing_patterns:
            return PatternMatch(
                matches=False,
                reasoning="No existing patterns to match against"
            )

        # Build pattern summaries
        pattern_summaries = []
        for p in existing_patterns[:20]:  # Limit to 20 for context
            metadata = p.pattern_metadata or {}
            pattern_summaries.append({
                "id": str(p.id),
                "name": p.name,
                "description": p.description,
                "keywords": metadata.get("keywords", []),
                "sample_utterances": metadata.get("sample_utterances", [])[:3]
            })

        scenario_def = edge_case.scenario_definition or {}
        utterance = scenario_def.get('user_utterance', 'N/A')
        actual = scenario_def.get('actual_response', 'N/A')
        feedback = edge_case.description or "No feedback provided"

        prompt = f"""Determine if this edge case matches any existing pattern.

EDGE CASE TO MATCH:
- User Utterance: "{utterance}"
- AI Response: "{actual}"
- Validator Feedback: "{feedback}"
- LLM Analysis: {llm_analysis.pattern_name}
- Keywords: {', '.join(llm_analysis.keywords)}

EXISTING PATTERNS:
{json.dumps(pattern_summaries, indent=2)}

Does this edge case belong to one of these existing patterns?
Consider semantic similarity, keywords, and failure modes.

Respond ONLY with valid JSON in this exact format:
{{
    "matches": true/false,
    "pattern_id": "id of matching pattern or null",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation of decision"
}}"""

        try:
            response = await self._call_llm(
                prompt,
                temperature=0.3,
                operation="match_to_existing_pattern",
                metadata={
                    "edge_case_id": str(edge_case.id),
                    "pattern_count": len(existing_patterns),
                    "pattern_names": [p.name for p in existing_patterns[:5]]  # First 5
                }
            )

            # Parse JSON response
            match_data = self._parse_json_response(response)

            return PatternMatch(**match_data)

        except Exception as e:
            logger.error(f"Failed to match pattern with LLM: {e}")
            # Fallback: no match
            return PatternMatch(
                matches=False,
                reasoning=f"LLM matching failed: {str(e)}"
            )

    async def _call_llm(
        self,
        prompt: str,
        temperature: float = 0.3,
        operation: str = "llm_call",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Call the LLM via OpenRouter API with automatic cost tracking.

        Args:
            prompt: The prompt to send
            temperature: Sampling temperature
            operation: Operation name for cost tracking
            metadata: Additional metadata for cost tracking

        Returns:
            LLM response text
        """
        start_time = time.time()
        success = False
        error_message = None
        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://voiceai-testing.com",
            "X-Title": "Voice AI Testing Framework"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": temperature,
            "max_tokens": 1000
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()

                data = response.json()

                # Extract token usage
                usage = data.get("usage", {})
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
                total_tokens = usage.get("total_tokens", 0)

                success = True
                content = data["choices"][0]["message"]["content"]

                return content

        except Exception as e:
            error_message = str(e)
            logger.error(f"LLM API call failed: {e}")
            raise

        finally:
            # Track cost regardless of success/failure
            duration_ms = int((time.time() - start_time) * 1000)
            await self._log_llm_usage(
                operation=operation,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                duration_ms=duration_ms,
                success=success,
                error_message=error_message,
                metadata=metadata
            )

    async def _log_llm_usage(
        self,
        operation: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        duration_ms: int,
        success: bool,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log LLM API usage to database for cost tracking.

        Args:
            operation: Operation name
            prompt_tokens: Tokens in prompt
            completion_tokens: Tokens in completion
            total_tokens: Total tokens used
            duration_ms: API call duration in milliseconds
            success: Whether call succeeded
            error_message: Error message if failed
            metadata: Additional metadata
        """
        # Skip logging if no database session
        if not self.db:
            logger.debug(f"Skipping cost tracking (no DB session): {operation}")
            return

        # Use tenant_id if available, otherwise use a placeholder
        tenant_id = self.tenant_id

        if not tenant_id:
            logger.warning(f"No tenant_id for cost tracking: {operation}")
            return

        try:
            # Calculate estimated cost using database-driven pricing
            estimated_cost = calculate_cost(
                model=self.model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                db=self.db,
                provider="openrouter"
            )

            # Create log entry
            log_entry = LLMUsageLog(
                tenant_id=tenant_id,
                service_name="pattern_analysis",
                operation=operation,
                model=self.model,
                provider="openrouter",
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                estimated_cost_usd=estimated_cost,
                request_metadata=metadata or {},
                duration_ms=duration_ms,
                success=success,
                error_message=error_message
            )

            self.db.add(log_entry)
            await self.db.commit()

            logger.info(
                f"LLM usage logged: {operation} | "
                f"Tokens: {total_tokens} | "
                f"Cost: ${estimated_cost:.6f} | "
                f"Duration: {duration_ms}ms"
            )

        except Exception as e:
            logger.error(f"Failed to log LLM usage: {e}")
            # Don't raise - logging failure shouldn't break the main flow

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON from LLM response, handling markdown code blocks.

        Args:
            response: Raw LLM response

        Returns:
            Parsed JSON dict
        """
        # Remove markdown code blocks if present
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]

        response = response.strip()

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}\nResponse: {response}")
            raise

    def _format_list(self, items: List[str]) -> str:
        """Format list items for prompt."""
        if not items:
            return "- None provided"
        return "\n".join(f"- {item}" for item in items)

    def _generate_fallback_pattern(
        self,
        edge_cases: List[EdgeCase]
    ) -> PatternDetails:
        """
        Generate basic pattern details as fallback.

        Args:
            edge_cases: Edge cases to analyze

        Returns:
            Basic PatternDetails
        """
        # Use most common category
        categories = [ec.category for ec in edge_cases if ec.category]
        most_common = max(set(categories), key=categories.count) if categories else "unknown"

        return PatternDetails(
            name=f"Pattern: {most_common.replace('_', ' ').title()}",
            description=f"Pattern identified from {len(edge_cases)} similar edge cases.",
            root_cause="Root cause could not be determined automatically",
            suggested_actions=[
                "Review edge cases manually",
                "Identify common failure mode",
                "Update test scenarios"
            ],
            keywords=[most_common] if most_common != "unknown" else []
        )
