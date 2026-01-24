"""
ValidatorPerformance SQLAlchemy model for tracking validator metrics

This module defines the ValidatorPerformance model which tracks daily
performance metrics for human validators in the voice AI testing framework,
enabling quality monitoring and inter-rater agreement calculations.

The ValidatorPerformance model includes:
    - Daily metrics: One record per validator per day (UNIQUE constraint)
    - Validation throughput: Count of validations completed
    - Time tracking: Average time spent per validation
    - Quality metrics: Agreement with peers and final consensus
    - Cohen's Kappa support: Agreement percentages for quality calculations

Example:
    >>> from models.validator_performance import ValidatorPerformance
    >>> from uuid import uuid4
    >>> from decimal import Decimal
    >>> from datetime import date
    >>>
    >>> # Create daily performance record
    >>> performance = ValidatorPerformance(
    ...     id=uuid4(),
    ...     validator_id=validator_uuid,
    ...     date=date.today(),
    ...     validations_completed=15,
    ...     average_time_seconds=Decimal('45.50'),
    ...     agreement_with_peers_pct=Decimal('85.50'),
    ...     agreement_with_final_pct=Decimal('92.00')
    ... )
    >>>
    >>> # Check metrics
    >>> print(performance.get_average_time_minutes())
    0.76
    >>> print(performance.has_high_agreement())
    True
"""

from typing import Optional
from datetime import datetime

from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, Numeric

from sqlalchemy.orm import relationship

from models.base import Base, BaseModel, GUID


class ValidatorPerformance(Base, BaseModel):
    """
    ValidatorPerformance model for tracking daily validator metrics.

    Represents one day's worth of performance data for a validator,
    including validation count, time spent, and agreement metrics.
    Note: Only one record per validator per day (UNIQUE constraint).

    Attributes:
        id (UUID): Unique identifier (inherited from BaseModel)
        validator_id (UUID): Reference to the user (validator) whose performance is tracked
        date (date): Date for which performance metrics are recorded
        validations_completed (int): Number of validations completed on this date (default=0)
        average_time_seconds (Decimal, optional): Average time spent per validation in seconds
        agreement_with_peers_pct (Decimal, optional): Percentage agreement with peer validators (0.00-100.00)
        agreement_with_final_pct (Decimal, optional): Percentage agreement with final consensus (0.00-100.00)
        created_at (datetime): When this performance record was created (inherited)
        updated_at (datetime): Last update timestamp (inherited)

    Relationships:
        validator: The User whose performance is being tracked (many-to-one)

    Example:
        >>> performance = ValidatorPerformance(
        ...     validator_id=user_uuid,
        ...     date=date(2025, 10, 25),
        ...     validations_completed=20,
        ...     average_time_seconds=Decimal('38.75'),
        ...     agreement_with_peers_pct=Decimal('88.50'),
        ...     agreement_with_final_pct=Decimal('94.00')
        ... )
        >>> print(f"Average time: {performance.get_average_time_minutes():.2f} minutes")
        Average time: 0.65 minutes
        >>> print(f"High agreement: {performance.has_high_agreement()}")
        High agreement: True

    Note:
        - UNIQUE constraint on (validator_id, date) ensures one record per validator per day
        - agreement_with_peers_pct: Inter-rater agreement, useful for Cohen's Kappa
        - agreement_with_final_pct: Agreement with final consensus decision
        - High agreement threshold is 80% by default
    """

    __tablename__ = 'validator_performance'

    # Foreign key to user (validator)
    validator_id = Column(
        GUID(),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="User (validator) whose performance is being tracked"
    )

    # Date for daily performance tracking
    date = Column(
        Date,
        nullable=False,
        index=True,
        comment="Date for which performance metrics are recorded"
    )

    # Performance metrics
    validations_completed = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of validations completed on this date"
    )

    average_time_seconds = Column(
        Numeric(precision=8, scale=2),
        nullable=True,
        comment="Average time spent per validation in seconds"
    )

    agreement_with_peers_pct = Column(
        Numeric(precision=5, scale=2),
        nullable=True,
        comment="Percentage agreement with peer validators (0.00-100.00)"
    )

    agreement_with_final_pct = Column(
        Numeric(precision=5, scale=2),
        nullable=True,
        comment="Percentage agreement with final consensus (0.00-100.00)"
    )

    # Creation timestamp (updated_at inherited from BaseModel)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        comment="When this performance record was created"
    )

    # Relationships
    validator = relationship(
        "User",
        foreign_keys=[validator_id],
        primaryjoin="ValidatorPerformance.validator_id == remote(User.id)",
        viewonly=True
    )

    # Note: UNIQUE constraint on (validator_id, date) is defined in migration
    # This ensures only one performance record per validator per day

    def get_average_time_minutes(self) -> Optional[float]:
        """
        Get average time spent per validation in minutes.

        Converts the average_time_seconds to minutes for easier reading.

        Returns:
            Optional[float]: Average time in minutes, or None if not set

        Example:
            >>> performance = ValidatorPerformance(
            ...     average_time_seconds=Decimal('90.00')
            ... )
            >>> performance.get_average_time_minutes()
            1.5
        """
        if self.average_time_seconds is None:
            return None
        return float(self.average_time_seconds) / 60.0

    def has_high_agreement(self, threshold: float = 80.0) -> bool:
        """
        Check if validator has high agreement with peers.

        Determines if the validator's peer agreement percentage meets
        or exceeds the specified threshold.

        Args:
            threshold: Minimum agreement percentage (default=80.0)

        Returns:
            bool: True if agreement meets or exceeds threshold, False otherwise

        Example:
            >>> performance = ValidatorPerformance(
            ...     agreement_with_peers_pct=Decimal('85.50')
            ... )
            >>> performance.has_high_agreement()
            True
            >>> performance.has_high_agreement(threshold=90.0)
            False
        """
        if self.agreement_with_peers_pct is None:
            return False
        return float(self.agreement_with_peers_pct) >= threshold

    def get_agreement_scores(self) -> dict:
        """
        Get all agreement scores as a dictionary.

        Returns both peer and final agreement percentages in a
        convenient dictionary format.

        Returns:
            dict: Dictionary with 'peers' and 'final' agreement percentages

        Example:
            >>> performance = ValidatorPerformance(
            ...     agreement_with_peers_pct=Decimal('85.50'),
            ...     agreement_with_final_pct=Decimal('92.00')
            ... )
            >>> scores = performance.get_agreement_scores()
            >>> print(scores)
            {'peers': 85.5, 'final': 92.0}
        """
        return {
            'peers': float(self.agreement_with_peers_pct) if self.agreement_with_peers_pct else None,
            'final': float(self.agreement_with_final_pct) if self.agreement_with_final_pct else None
        }

    def is_productive(self, min_validations: int = 5) -> bool:
        """
        Check if validator met minimum productivity threshold for the day.

        Determines if the number of validations completed meets or
        exceeds the minimum expected productivity.

        Args:
            min_validations: Minimum number of validations expected (default=5)

        Returns:
            bool: True if validations completed meets or exceeds threshold

        Example:
            >>> performance = ValidatorPerformance(
            ...     validations_completed=12
            ... )
            >>> performance.is_productive()
            True
            >>> performance.is_productive(min_validations=15)
            False
        """
        return self.validations_completed >= min_validations

    def get_efficiency_score(self) -> Optional[float]:
        """
        Calculate efficiency score based on validations and time.

        Computes validations per minute as an efficiency metric.
        Higher scores indicate faster validation processing.

        Returns:
            Optional[float]: Validations per minute, or None if time not available

        Example:
            >>> performance = ValidatorPerformance(
            ...     validations_completed=20,
            ...     average_time_seconds=Decimal('45.00')
            ... )
            >>> performance.get_efficiency_score()
            1.3333...  # 20 validations / (20 * 45 seconds / 60)
        """
        if self.average_time_seconds is None or self.validations_completed == 0:
            return None

        total_minutes = (self.validations_completed * float(self.average_time_seconds)) / 60.0
        if total_minutes == 0:
            return None

        return self.validations_completed / total_minutes
