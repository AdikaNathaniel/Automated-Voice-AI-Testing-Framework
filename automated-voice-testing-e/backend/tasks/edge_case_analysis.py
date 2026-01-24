"""
Edge Case Pattern Analysis - Celery Background Job

Part of Phase 2: Pattern Recognition & Grouping.
Runs periodically (e.g., nightly) to analyze edge cases and identify patterns.
Uses tenant-specific configuration for analysis parameters.

TODO: Celery Beat Integration
Currently using default schedule. To enable per-tenant schedules:
1. Install: pip install django-celery-beat (or celery-redbeat)
2. Configure dynamic beat schedule
3. Update schedule when configs change via signals
4. Reference: https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html

Example Celery Beat config:
    from celery.schedules import crontab

    beat_schedule = {
        'pattern-analysis-default': {
            'task': 'analyze_edge_case_patterns',
            'schedule': crontab(hour=2, minute=0),  # 2 AM daily
            'options': {'expires': 3600}
        }
    }
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from uuid import UUID

from celery import shared_task
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from models.edge_case import EdgeCase
from models.pattern_group import PatternGroup
from services.edge_case_similarity_service import EdgeCaseSimilarityService
from services.pattern_analysis_config_service import PatternAnalysisConfigService
from services.notification_service import NotificationService
from api.database import get_async_session
import logging

logger = logging.getLogger(__name__)


@shared_task(name="analyze_edge_case_patterns")
def analyze_edge_case_patterns(
    tenant_id: Optional[str] = None,
    override_params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyze edge cases for specific tenant(s) using their configuration.

    This task:
    1. Loads tenant-specific configuration settings
    2. Fetches unprocessed edge cases based on configured time windows
    3. Groups similar cases using EdgeCaseSimilarityService
    4. Creates/updates PatternGroup entries
    5. Marks edge cases as 'grouped'
    6. Returns analysis summary

    Args:
        tenant_id: UUID of specific tenant to analyze (None = all tenants with auto-analysis enabled)
        override_params: Optional parameter overrides for manual runs

    Returns:
        Dict with analysis results and statistics

    Example:
        # Analyze specific tenant
        result = analyze_edge_case_patterns.delay(tenant_id="abc-123")

        # Analyze all tenants with overrides
        result = analyze_edge_case_patterns.delay(
            override_params={"lookback_days": 14}
        )
    """
    import asyncio
    return asyncio.run(_analyze_with_tenant_config(tenant_id, override_params))


async def _analyze_with_tenant_config(
    tenant_id: Optional[str],
    override_params: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Run analysis with tenant-specific configuration.

    Args:
        tenant_id: Optional tenant UUID to analyze
        override_params: Optional parameter overrides

    Returns:
        Dict with analysis results
    """
    async with get_async_session() as db:
        config_service = PatternAnalysisConfigService(db)

        # Get configurations to process
        if tenant_id:
            # Analyze specific tenant
            config = await config_service.get_or_create(UUID(tenant_id))
            configs = [config]
        else:
            # Analyze all tenants with auto-analysis enabled
            configs = await config_service.get_all_active()

        if not configs:
            return {
                'status': 'success',
                'message': 'No tenants configured for auto-analysis',
                'tenants_analyzed': 0,
                'results': []
            }

        results = []

        for config in configs:
            # Build parameters from config
            params = {
                'lookback_days': config.lookback_days,
                'min_pattern_size': config.min_pattern_size,
                'similarity_threshold': config.similarity_threshold,
                'llm_confidence_threshold': config.llm_confidence_threshold,
                'enable_llm_analysis': config.enable_llm_analysis,
                'notify_on_new_patterns': config.notify_on_new_patterns,
                'notify_on_critical_patterns': config.notify_on_critical_patterns,
            }

            # Apply overrides if provided (for manual runs)
            if override_params:
                params.update(override_params)

            # Run analysis for this tenant
            result = await _analyze_tenant_patterns(db, config.tenant_id, params)

            results.append({
                'tenant_id': str(config.tenant_id),
                **result
            })

        return {
            'status': 'success',
            'tenants_analyzed': len(results),
            'results': results
        }


async def _analyze_tenant_patterns(
    db: AsyncSession,
    tenant_id: UUID,
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Analyze patterns for a specific tenant.

    Args:
        db: Database session
        tenant_id: Tenant UUID
        params: Analysis parameters

    Returns:
        Dict with analysis results for this tenant
    """
    from datetime import timezone
    start_time = datetime.now(timezone.utc)

    logger.info(
        f"Starting pattern analysis for tenant {tenant_id} "
        f"(lookback={params['lookback_days']}d, "
        f"min_size={params['min_pattern_size']}, "
        f"threshold={params['similarity_threshold']}, "
        f"llm={params['enable_llm_analysis']})"
    )

    # Initialize similarity service
    similarity_service = EdgeCaseSimilarityService(
        db,
        use_llm=params['enable_llm_analysis']
    )

    # Fetch unprocessed edge cases using configurable time window
    edge_cases = await _fetch_unprocessed_edge_cases(
        db,
        tenant_id,
        params['lookback_days']
    )

    logger.info(f"Found {len(edge_cases)} unprocessed edge cases for tenant {tenant_id}")

    if not edge_cases:
        return {
            'status': 'success',
            'message': 'No edge cases to analyze',
            'patterns_discovered': 0,
            'edge_cases_processed': 0,
            'duration_seconds': 0
        }

    # Group edge cases into patterns
    patterns_created = []
    patterns_updated = []
    edge_cases_processed = set()
    llm_calls_made = 0

    for edge_case in edge_cases:
        # Skip if already processed in this run
        if edge_case.id in edge_cases_processed:
            continue

        # Analyze and group with LLM or semantic fallback
        pattern = await similarity_service.analyze_and_group(
            edge_case,
            threshold=params['similarity_threshold'],
            llm_confidence_threshold=params['llm_confidence_threshold'],
            min_pattern_size=params['min_pattern_size']
        )

        if params['enable_llm_analysis']:
            llm_calls_made += 1  # Count LLM usage for metrics

        if pattern:
            # Track which edge cases were processed
            from models.pattern_group import EdgeCasePatternLink
            result = await db.execute(
                select(EdgeCasePatternLink).where(
                    EdgeCasePatternLink.pattern_group_id == pattern.id
                )
            )
            links = result.scalars().all()

            for link in links:
                edge_cases_processed.add(link.edge_case_id)

            # Check if this is a new or updated pattern
            if pattern.created_at >= start_time:
                patterns_created.append(pattern)
            else:
                patterns_updated.append(pattern)

            logger.info(
                f"Pattern '{pattern.name}': "
                f"{pattern.occurrence_count} edge cases grouped "
                f"(LLM-generated: {pattern.pattern_metadata.get('llm_generated', False)})"
            )

    # Commit all changes
    await db.commit()

    # Send notifications based on config
    notification_service = NotificationService()

    # Notify on new patterns
    if params.get('notify_on_new_patterns') and patterns_created:
        for pattern in patterns_created:
            try:
                await notification_service.send_pattern_notification(
                    tenant_id=tenant_id,
                    pattern_id=pattern.id,
                    pattern_name=pattern.name,
                    pattern_type='new_pattern',
                    occurrence_count=pattern.occurrence_count,
                    severity=pattern.severity
                )
                logger.info(f"Sent new pattern notification for: {pattern.name}")
            except Exception as e:
                logger.error(f"Failed to send notification for pattern {pattern.id}: {e}")

    # Alert on critical patterns
    if params.get('notify_on_critical_patterns'):
        critical_patterns = [p for p in patterns_created if p.severity == 'critical']
        for pattern in critical_patterns:
            try:
                await notification_service.send_pattern_notification(
                    tenant_id=tenant_id,
                    pattern_id=pattern.id,
                    pattern_name=pattern.name,
                    pattern_type='critical_pattern',
                    occurrence_count=pattern.occurrence_count,
                    severity=pattern.severity,
                    priority='high'
                )
                logger.info(f"Sent critical pattern alert for: {pattern.name}")
            except Exception as e:
                logger.error(f"Failed to send critical alert for pattern {pattern.id}: {e}")

    # Calculate duration
    duration = (datetime.now(timezone.utc) - start_time).total_seconds()

    # Analyze trends
    trends = await _analyze_pattern_trends(db, tenant_id)

    summary = {
        'status': 'success',
        'timestamp': datetime.utcnow().isoformat(),
        'patterns_discovered': len(patterns_created),
        'patterns_updated': len(patterns_updated),
        'edge_cases_processed': len(edge_cases_processed),
        'edge_cases_analyzed': len(edge_cases),
        'llm_calls_made': llm_calls_made if params['enable_llm_analysis'] else 0,
        'duration_seconds': round(duration, 2),
        'config': {
            'lookback_days': params['lookback_days'],
            'min_pattern_size': params['min_pattern_size'],
            'similarity_threshold': params['similarity_threshold']
        },
        'trends': trends,
        'new_patterns': [
            {
                'id': str(p.id),
                'name': p.name,
                'severity': p.severity,
                'occurrence_count': p.occurrence_count
            }
            for p in patterns_created
        ]
    }

    logger.info(
        f"Pattern analysis complete for tenant {tenant_id}: "
        f"{summary['patterns_discovered']} new patterns, "
        f"{summary['patterns_updated']} updated, "
        f"{summary['edge_cases_processed']} cases processed "
        f"in {duration:.2f}s"
    )

    return summary


async def _fetch_unprocessed_edge_cases(
    db: AsyncSession,
    tenant_id: UUID,
    lookback_days: int
) -> List[EdgeCase]:
    """
    Fetch edge cases within the configured time window.

    Args:
        db: Database session
        tenant_id: Tenant UUID
        lookback_days: Maximum age of cases to consider (in days)

    Returns:
        List of EdgeCase instances, ordered by creation date (newest first)
    """
    cutoff_date = datetime.utcnow() - timedelta(days=lookback_days)

    # Query edge cases with status='new' within the time window
    query = select(EdgeCase).where(
        and_(
            EdgeCase.tenant_id == tenant_id,
            EdgeCase.status == 'new',
            EdgeCase.created_at >= cutoff_date
        )
    ).order_by(
        EdgeCase.created_at.desc()
    )

    result = await db.execute(query)
    return list(result.scalars().all())


async def _analyze_pattern_trends(
    db: AsyncSession,
    tenant_id: UUID
) -> Dict[str, Any]:
    """
    Analyze trends in pattern groups for specific tenant.

    Args:
        db: Database session
        tenant_id: Tenant UUID

    Returns:
        Dict with trend analysis
    """
    # Get all active patterns for this tenant
    # Note: PatternGroup doesn't have tenant_id directly, inferred from edge cases
    result = await db.execute(
        select(PatternGroup).where(PatternGroup.status == 'active')
    )
    patterns = result.scalars().all()

    if not patterns:
        return {
            'total_active_patterns': 0,
            'critical_patterns': 0,
            'trending_up': [],
            'trending_down': []
        }

    # Count by severity
    severity_counts = {}
    for pattern in patterns:
        severity = pattern.severity
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

    # Identify critical patterns
    critical = [
        p.name for p in patterns
        if p.severity == 'critical'
    ]

    # Identify trending patterns (recent activity)
    recent_threshold = datetime.utcnow() - timedelta(days=3)
    trending_up = [
        p.name for p in patterns
        if p.last_seen >= recent_threshold and p.occurrence_count >= 5
    ]

    return {
        'total_active_patterns': len(patterns),
        'severity_distribution': severity_counts,
        'critical_patterns': len(critical),
        'critical_pattern_names': critical[:5],  # Top 5
        'trending_up': trending_up[:5],  # Top 5
        'most_common_pattern': (
            max(patterns, key=lambda p: p.occurrence_count).name
            if patterns else None
        )
    }


@shared_task(name="cleanup_old_patterns")
def cleanup_old_patterns(days_inactive: int = 90) -> Dict[str, Any]:
    """
    Archive or delete old pattern groups that haven't been seen recently.

    Args:
        days_inactive: Number of days of inactivity before cleanup

    Returns:
        Dict with cleanup statistics
    """
    import asyncio
    return asyncio.run(_cleanup_old_patterns_async(days_inactive))


async def _cleanup_old_patterns_async(days_inactive: int) -> Dict[str, Any]:
    """
    Async implementation of pattern cleanup.

    Args:
        days_inactive: Number of days of inactivity before cleanup

    Returns:
        Dict with cleanup results
    """
    logger.info(f"Starting pattern cleanup (inactive > {days_inactive} days)")

    cutoff_date = datetime.utcnow() - timedelta(days=days_inactive)

    async with get_async_session() as db:
        # Find inactive patterns
        result = await db.execute(
            select(PatternGroup).where(
                and_(
                    PatternGroup.status == 'active',
                    PatternGroup.last_seen < cutoff_date
                )
            )
        )
        inactive_patterns = result.scalars().all()

        # Mark as resolved
        for pattern in inactive_patterns:
            pattern.status = 'resolved'
            logger.info(f"Archiving inactive pattern: {pattern.name}")

        await db.commit()

        return {
            'status': 'success',
            'patterns_archived': len(inactive_patterns),
            'cutoff_date': cutoff_date.isoformat(),
            'timestamp': datetime.utcnow().isoformat()
        }
