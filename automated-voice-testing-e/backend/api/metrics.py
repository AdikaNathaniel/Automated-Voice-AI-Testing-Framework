"""Prometheus metric registry for API and worker instrumentation."""

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram

# Single registry so the API and Celery tasks can record against the same metrics.
registry = CollectorRegistry()

test_executions_total = Counter(
    "test_executions_total",
    "Total number of test executions triggered.",
    registry=registry,
)

test_execution_duration_seconds = Histogram(
    "test_execution_duration_seconds",
    "Distribution of test execution durations in seconds.",
    buckets=(0.1, 0.5, 1, 2, 5, 10, 30, 60),
    registry=registry,
)

validation_confidence_score = Histogram(
    "validation_confidence_score",
    "Distribution of validation confidence scores (0.0-1.0).",
    buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    registry=registry,
)

queue_depth = Gauge(
    "queue_depth",
    "Current number of pending jobs in the execution queue.",
    registry=registry,
)

active_workers = Gauge(
    "active_workers",
    "Number of active worker processes handling executions.",
    registry=registry,
)

houndify_requests_total = Counter(
    "houndify_requests_total",
    "Total number of Houndify requests issued.",
    ("language", "intent", "mode"),
    registry=registry,
)

houndify_errors_total = Counter(
    "houndify_errors_total",
    "Total number of failed Houndify requests.",
    ("language", "intent", "error_type"),
    registry=registry,
)

houndify_latency_seconds = Histogram(
    "houndify_latency_seconds",
    "Latency distribution for Houndify requests in seconds.",
    buckets=(0.1, 0.25, 0.5, 1, 2, 5, 10, 20),
    labelnames=("language", "intent", "mode"),
    registry=registry,
)

__all__ = (
    "registry",
    "test_executions_total",
    "test_execution_duration_seconds",
    "validation_confidence_score",
    "queue_depth",
    "active_workers",
    "houndify_requests_total",
    "houndify_errors_total",
    "houndify_latency_seconds",
)
