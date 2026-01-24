"""
Celery Application Configuration

This module configures the Celery application for the Voice AI Testing Framework.
Celery is used for asynchronous task processing, including:
- Test execution orchestration
- Scheduled tasks
- Background processing

Configuration:
- Broker: Redis or RabbitMQ for message queue
- Backend: Redis for result storage
- Serialization: JSON for security and compatibility
- Timezone: UTC for consistency
"""

import os
from celery import Celery
from celery.schedules import crontab


# Get configuration from environment variables
BROKER_URL = os.getenv(
    'BROKER_URL',
    os.getenv('RABBITMQ_URL', 'redis://localhost:6379/0')
)

BACKEND_URL = os.getenv(
    'CELERY_RESULT_BACKEND',
    'redis://localhost:6379/0'
)


# Create Celery application instance
celery = Celery(
    'voice_ai_testing',
    broker=BROKER_URL,
    backend=BACKEND_URL
)


# Configure Celery settings
celery.conf.update(
    # Serialization settings for security
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],

    # Timezone settings
    timezone='UTC',
    enable_utc=True,

    # Task execution settings
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes

    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    result_persistent=True,

    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,

    # Task routing
    task_routes={
        'backend.tasks.*': {'queue': 'default'},
    },

    # Task acknowledgement
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)


# Optional: Configure beat schedule for periodic tasks
AUTO_SCALING_INTERVAL = float(os.getenv("AUTO_SCALING_COOLDOWN_SECONDS", "30"))
celery.conf.beat_schedule = {
    # Example: cleanup old results every day
    'cleanup-old-results': {
        'task': 'backend.tasks.cleanup.cleanup_old_results',
        'schedule': 86400.0,  # Every 24 hours
    },
    'auto-scale-workers': {
        'task': 'tasks.worker_scaling.auto_scale_workers',
        'schedule': AUTO_SCALING_INTERVAL,
    },
    'send-scheduled-reports': {
        'task': 'tasks.reporting.send_scheduled_reports',
        'schedule': crontab(hour=7, minute=0),  # 07:00 UTC daily
    },
}


# Import tasks to register them with Celery
# This ensures tasks are discovered and available to workers
try:
    from tasks import execution  # noqa: F401
    from tasks import orchestration  # noqa: F401
    from tasks import edge_case_analysis  # noqa: F401
except ImportError as e:
    import logging
    logging.warning(f"Failed to import tasks: {e}")
