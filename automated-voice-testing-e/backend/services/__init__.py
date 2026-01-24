"""
Voice AI Testing Framework - Services Module

This module contains business logic and service layer implementations.
"""

__version__ = "0.1.0"

from .notification_service import NotificationService, NotificationServiceError  # noqa: F401
from .execution_resource_manager import (  # noqa: F401
    ExecutionResourceMonitor,
    ResourceLimitExceeded,
    ResourceSnapshot,
)
from .worker_health_service import (  # noqa: F401
    WorkerAlert,
    WorkerHealthReport,
    WorkerHealthService,
    WorkerStatus,
)
from .predictive_analytics_service import (  # noqa: F401
    DefectRiskPrediction,
    PredictiveAnalyticsService,
    PredictiveFeatures,
)
from .report_generator_service import ReportGeneratorService  # noqa: F401
from .scheduled_report_service import (  # noqa: F401
    EmailAttachment,
    ScheduledReportService,
    SendEmailError,
)
from .custom_report_builder import (  # noqa: F401
    CustomReportBuilderService,
    CustomReportRequest,
    CustomReportResult,
    InvalidDateRangeError,
    UnsupportedFormatError,
    UnsupportedMetricError,
)
