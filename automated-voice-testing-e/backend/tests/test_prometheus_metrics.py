from importlib import import_module

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram


def _get_metric_family(registry: CollectorRegistry, name: str):
    families = {metric_family.name: metric_family for metric_family in registry.collect()}
    try:
        return families[name]
    except KeyError as exc:  # pragma: no cover - fails the assertion below
        raise AssertionError(f"Metric '{name}' was not registered") from exc


def test_metrics_module_exposes_expected_instruments():
    metrics_module = import_module("api.metrics")

    assert isinstance(metrics_module.registry, CollectorRegistry)

    assert isinstance(metrics_module.test_executions_total, Counter)
    assert isinstance(metrics_module.test_execution_duration_seconds, Histogram)
    assert isinstance(metrics_module.validation_confidence_score, Histogram)
    assert isinstance(metrics_module.queue_depth, Gauge)
    assert isinstance(metrics_module.active_workers, Gauge)
    assert isinstance(metrics_module.houndify_requests_total, Counter)
    assert isinstance(metrics_module.houndify_errors_total, Counter)
    assert isinstance(metrics_module.houndify_latency_seconds, Histogram)

    families = {family.name: family for family in metrics_module.registry.collect()}

    assert set(families) == {
        "test_executions",
        "test_execution_duration_seconds",
        "validation_confidence_score",
        "queue_depth",
        "active_workers",
        "houndify_requests",
        "houndify_errors",
        "houndify_latency_seconds",
    }

    assert families["test_executions"].type == "counter"
    assert (
        families["test_executions"].documentation
        == "Total number of test executions triggered."
    )
    counter_sample_names = {sample.name for sample in families["test_executions"].samples}
    assert "test_executions_total" in counter_sample_names

    duration_family = _get_metric_family(
        metrics_module.registry, "test_execution_duration_seconds"
    )
    assert duration_family.type == "histogram"
    assert (
        duration_family.documentation
        == "Distribution of test execution durations in seconds."
    )
    assert tuple(metrics_module.test_execution_duration_seconds._upper_bounds) == (
        0.1,
        0.5,
        1,
        2,
        5,
        10,
        30,
        60,
        float("inf"),
    )

    confidence_family = _get_metric_family(
        metrics_module.registry, "validation_confidence_score"
    )
    assert confidence_family.type == "histogram"
    assert (
        confidence_family.documentation
        == "Distribution of validation confidence scores (0.0-1.0)."
    )
    assert tuple(metrics_module.validation_confidence_score._upper_bounds) == (
        0.1,
        0.2,
        0.3,
        0.4,
        0.5,
        0.6,
        0.7,
        0.8,
        0.9,
        1.0,
        float("inf"),
    )

    queue_family = _get_metric_family(metrics_module.registry, "queue_depth")
    assert queue_family.type == "gauge"
    assert (
        queue_family.documentation
        == "Current number of pending jobs in the execution queue."
    )

    workers_family = _get_metric_family(metrics_module.registry, "active_workers")
    assert workers_family.type == "gauge"
    assert (
        workers_family.documentation
        == "Number of active worker processes handling executions."
    )

    houndify_requests_family = _get_metric_family(
        metrics_module.registry, "houndify_requests"
    )
    assert houndify_requests_family.type == "counter"
    assert (
        houndify_requests_family.documentation
        == "Total number of Houndify requests issued."
    )

    errors_family = _get_metric_family(
        metrics_module.registry, "houndify_errors"
    )
    assert errors_family.type == "counter"
    assert (
        errors_family.documentation
        == "Total number of failed Houndify requests."
    )

    latency_family = _get_metric_family(
        metrics_module.registry, "houndify_latency_seconds"
    )
    assert latency_family.type == "histogram"
    assert (
        latency_family.documentation
        == "Latency distribution for Houndify requests in seconds."
    )
