"""
ValidatorPerformanceService for tracking validator metrics and inter-rater agreement

This module provides the ValidatorPerformanceService class which manages
validator performance tracking, daily metrics calculation, and inter-rater
agreement analysis using Cohen's Kappa.

The service provides:
    - Daily performance recording: Track metrics per validator per day
    - Metrics update: Update validation counts, time, and agreement percentages
    - Performance history: Retrieve historical performance data
    - Cohen's Kappa calculation: Measure inter-rater agreement quality
    - Upsert pattern: One record per validator per day (update or create)

Example:
    >>> from services.validator_performance_service import ValidatorPerformanceService
    >>> from api.dependencies import get_db
    >>> from datetime import date
    >>> from decimal import Decimal
    >>>
    >>> service = ValidatorPerformanceService()
    >>> # Record daily performance
    >>> performance = await service.record_daily_performance(
    ...     db=db,
    ...     validator_id=user_id,
    ...     date=date.today(),
    ...     validations_completed=15,
    ...     average_time_seconds=Decimal('42.50')
    ... )
    >>>
    >>> # Calculate Cohen's Kappa for agreement
    >>> kappa = await service.calculate_cohens_kappa(
    ...     agreements=85,
    ...     total_comparisons=100
    ... )
    >>> print(f"Cohen's Kappa: {kappa:.3f}")
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from models.validator_performance import ValidatorPerformance


class ValidatorPerformanceService:
    """
    Service for managing validator performance tracking and metrics.

    Handles all operations related to validator performance including daily
    metrics recording, performance history retrieval, and inter-rater agreement
    calculations using Cohen's Kappa statistical measure.

    Methods:
        record_daily_performance: Create or update daily performance record
        update_performance_metrics: Update metrics for existing record
        get_performance_for_date: Get performance for specific date
        get_performance_history: Get historical performance data
        calculate_cohens_kappa: Calculate inter-rater agreement (Cohen's Kappa)
    """

    async def record_daily_performance(
        self,
        db: Session,
        validator_id: UUID,
        date: date,
        validations_completed: int = 0,
        average_time_seconds: Optional[Decimal] = None,
        agreement_with_peers_pct: Optional[Decimal] = None,
        agreement_with_final_pct: Optional[Decimal] = None
    ) -> ValidatorPerformance:
        """
        Record daily performance for a validator (upsert pattern).

        Creates a new daily performance record or updates existing one if
        already exists for the validator and date. UNIQUE constraint on
        (validator_id, date) ensures one record per validator per day.

        Args:
            db: Database session
            validator_id: UUID of the validator
            date: Date for which performance is being recorded
            validations_completed: Number of validations completed (default=0)
            average_time_seconds: Average time per validation in seconds
            agreement_with_peers_pct: Agreement percentage with peers (0.00-100.00)
            agreement_with_final_pct: Agreement percentage with final consensus (0.00-100.00)

        Returns:
            ValidatorPerformance: Created or updated performance record

        Example:
            >>> performance = await service.record_daily_performance(
            ...     db=db,
            ...     validator_id=user_uuid,
            ...     date=date.today(),
            ...     validations_completed=20,
            ...     average_time_seconds=Decimal('38.50'),
            ...     agreement_with_peers_pct=Decimal('88.00'),
            ...     agreement_with_final_pct=Decimal('94.50')
            ... )
        """
        # Check if record already exists for this validator and date
        existing = await self.get_performance_for_date(
            db=db,
            validator_id=validator_id,
            date=date
        )

        if existing:
            # Update existing record
            existing.validations_completed = validations_completed
            existing.average_time_seconds = average_time_seconds
            existing.agreement_with_peers_pct = agreement_with_peers_pct
            existing.agreement_with_final_pct = agreement_with_final_pct
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Create new record
            performance = ValidatorPerformance(
                validator_id=validator_id,
                date=date,
                validations_completed=validations_completed,
                average_time_seconds=average_time_seconds,
                agreement_with_peers_pct=agreement_with_peers_pct,
                agreement_with_final_pct=agreement_with_final_pct
            )
            db.add(performance)
            db.commit()
            db.refresh(performance)
            return performance

    async def update_performance_metrics(
        self,
        db: Session,
        validator_id: UUID,
        date: date,
        validations_completed: Optional[int] = None,
        average_time_seconds: Optional[Decimal] = None,
        agreement_with_peers_pct: Optional[Decimal] = None,
        agreement_with_final_pct: Optional[Decimal] = None
    ) -> Optional[ValidatorPerformance]:
        """
        Update performance metrics for existing record.

        Updates only the provided metrics for an existing performance record.
        If the record doesn't exist, returns None.

        Args:
            db: Database session
            validator_id: UUID of the validator
            date: Date of the performance record to update
            validations_completed: New validation count (optional)
            average_time_seconds: New average time (optional)
            agreement_with_peers_pct: New peer agreement percentage (optional)
            agreement_with_final_pct: New final agreement percentage (optional)

        Returns:
            Optional[ValidatorPerformance]: Updated record, or None if not found

        Example:
            >>> updated = await service.update_performance_metrics(
            ...     db=db,
            ...     validator_id=user_uuid,
            ...     date=date.today(),
            ...     agreement_with_peers_pct=Decimal('90.00')
            ... )
        """
        # Get existing record
        performance = await self.get_performance_for_date(
            db=db,
            validator_id=validator_id,
            date=date
        )

        if not performance:
            return None

        # Update provided metrics
        if validations_completed is not None:
            performance.validations_completed = validations_completed

        if average_time_seconds is not None:
            performance.average_time_seconds = average_time_seconds

        if agreement_with_peers_pct is not None:
            performance.agreement_with_peers_pct = agreement_with_peers_pct

        if agreement_with_final_pct is not None:
            performance.agreement_with_final_pct = agreement_with_final_pct

        db.commit()
        db.refresh(performance)
        return performance

    async def get_performance_for_date(
        self,
        db: Session,
        validator_id: UUID,
        date: date
    ) -> Optional[ValidatorPerformance]:
        """
        Get performance record for a specific validator and date.

        Retrieves the performance record for the given validator on the
        specified date. Returns None if no record exists.

        Args:
            db: Database session
            validator_id: UUID of the validator
            date: Date for which to retrieve performance

        Returns:
            Optional[ValidatorPerformance]: Performance record, or None if not found

        Example:
            >>> performance = await service.get_performance_for_date(
            ...     db=db,
            ...     validator_id=user_uuid,
            ...     date=date.today()
            ... )
            >>> if performance:
            ...     print(f"Validations: {performance.validations_completed}")
        """
        query = select(ValidatorPerformance).where(
            and_(
                ValidatorPerformance.validator_id == validator_id,
                ValidatorPerformance.date == date
            )
        )

        result = db.execute(query)
        return result.scalar_one_or_none()

    async def get_performance_history(
        self,
        db: Session,
        validator_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 30
    ) -> List[ValidatorPerformance]:
        """
        Get performance history for a validator.

        Retrieves historical performance records for the specified validator,
        optionally filtered by date range. Returns records ordered by date
        descending (most recent first).

        Args:
            db: Database session
            validator_id: UUID of the validator
            start_date: Optional start date for filtering (inclusive)
            end_date: Optional end date for filtering (inclusive)
            limit: Maximum number of records to return (default=30)

        Returns:
            List[ValidatorPerformance]: List of performance records

        Example:
            >>> from datetime import date, timedelta
            >>> end = date.today()
            >>> start = end - timedelta(days=30)
            >>> history = await service.get_performance_history(
            ...     db=db,
            ...     validator_id=user_uuid,
            ...     start_date=start,
            ...     end_date=end
            ... )
            >>> for perf in history:
            ...     print(f"{perf.date}: {perf.validations_completed} validations")
        """
        query = select(ValidatorPerformance).where(
            ValidatorPerformance.validator_id == validator_id
        )

        # Apply date filters if provided
        if start_date:
            query = query.where(ValidatorPerformance.date >= start_date)

        if end_date:
            query = query.where(ValidatorPerformance.date <= end_date)

        # Order by date descending (most recent first)
        query = query.order_by(ValidatorPerformance.date.desc()).limit(limit)

        result = db.execute(query)
        return list(result.scalars().all())

    async def calculate_cohens_kappa(
        self,
        agreements: int,
        total_comparisons: int,
        expected_agreement_pct: Optional[float] = None
    ) -> float:
        """
        Calculate Cohen's Kappa coefficient for inter-rater agreement.

        Cohen's Kappa measures inter-rater reliability by comparing observed
        agreement with expected agreement by chance. Values range from -1 to 1:
        - 1.0 = Perfect agreement
        - 0.0 = No agreement beyond chance
        - < 0 = Less agreement than chance (rare)

        Interpretation guidelines:
        - 0.81-1.00: Almost perfect agreement
        - 0.61-0.80: Substantial agreement
        - 0.41-0.60: Moderate agreement
        - 0.21-0.40: Fair agreement
        - 0.00-0.20: Slight agreement
        - < 0.00: Poor agreement

        Args:
            agreements: Number of agreements between raters
            total_comparisons: Total number of comparisons made
            expected_agreement_pct: Expected agreement by chance (default=50%)

        Returns:
            float: Cohen's Kappa coefficient (-1.0 to 1.0)

        Example:
            >>> # 85 agreements out of 100 comparisons
            >>> kappa = await service.calculate_cohens_kappa(
            ...     agreements=85,
            ...     total_comparisons=100
            ... )
            >>> print(f"Cohen's Kappa: {kappa:.3f}")  # Output: 0.700
            >>>
            >>> # Interpretation
            >>> if kappa >= 0.81:
            ...     print("Almost perfect agreement")
            ... elif kappa >= 0.61:
            ...     print("Substantial agreement")
        """
        if total_comparisons == 0:
            return 0.0

        # Calculate observed agreement proportion
        observed_agreement = agreements / total_comparisons

        # Use default 50% expected agreement if not provided
        # (assumes random chance = 0.5 for binary decisions)
        if expected_agreement_pct is None:
            expected_agreement_pct = 50.0

        expected_agreement = expected_agreement_pct / 100.0

        # Cohen's Kappa formula: (Po - Pe) / (1 - Pe)
        # where Po = observed agreement, Pe = expected agreement
        if expected_agreement >= 1.0:
            # If expected agreement is 100%, kappa is undefined
            return 0.0

        kappa = (observed_agreement - expected_agreement) / (1.0 - expected_agreement)

        # Clamp to valid range [-1.0, 1.0]
        return max(-1.0, min(1.0, kappa))

    async def get_validator_summary(
        self,
        db: Session,
        validator_id: UUID,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get comprehensive summary of validator performance.

        Retrieves aggregated performance metrics for the specified validator
        over the given time period, including totals, averages, and trends.

        Args:
            db: Database session
            validator_id: UUID of the validator
            days: Number of days to include in summary (default=30)

        Returns:
            Dict[str, Any]: Summary statistics and metrics

        Example:
            >>> summary = await service.get_validator_summary(
            ...     db=db,
            ...     validator_id=user_uuid,
            ...     days=30
            ... )
            >>> print(summary)
            {
                'total_validations': 150,
                'avg_time_seconds': 42.3,
                'avg_peer_agreement': 87.5,
                'avg_final_agreement': 93.2,
                'days_active': 25,
                'cohens_kappa': 0.75
            }
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # Get performance history
        history = await self.get_performance_history(
            db=db,
            validator_id=validator_id,
            start_date=start_date,
            end_date=end_date,
            limit=days
        )

        if not history:
            return {
                'total_validations': 0,
                'avg_time_seconds': None,
                'avg_peer_agreement': None,
                'avg_final_agreement': None,
                'days_active': 0,
                'cohens_kappa': None
            }

        # Calculate aggregated metrics
        total_validations = sum(p.validations_completed for p in history)
        days_active = len(history)

        # Calculate averages (excluding None values)
        time_values = [float(p.average_time_seconds) for p in history if p.average_time_seconds]
        avg_time = sum(time_values) / len(time_values) if time_values else None

        peer_values = [float(p.agreement_with_peers_pct) for p in history if p.agreement_with_peers_pct]
        avg_peer_agreement = sum(peer_values) / len(peer_values) if peer_values else None

        final_values = [float(p.agreement_with_final_pct) for p in history if p.agreement_with_final_pct]
        avg_final_agreement = sum(final_values) / len(final_values) if final_values else None

        # Calculate Cohen's Kappa from average peer agreement
        kappa = None
        if avg_peer_agreement is not None:
            # Approximate agreements from average percentage
            agreements = int((avg_peer_agreement / 100.0) * total_validations)
            kappa = await self.calculate_cohens_kappa(
                agreements=agreements,
                total_comparisons=total_validations
            ) if total_validations > 0 else None

        return {
            'total_validations': total_validations,
            'avg_time_seconds': round(avg_time, 2) if avg_time else None,
            'avg_peer_agreement': round(avg_peer_agreement, 2) if avg_peer_agreement else None,
            'avg_final_agreement': round(avg_final_agreement, 2) if avg_final_agreement else None,
            'days_active': days_active,
            'cohens_kappa': round(kappa, 3) if kappa is not None else None
        }
