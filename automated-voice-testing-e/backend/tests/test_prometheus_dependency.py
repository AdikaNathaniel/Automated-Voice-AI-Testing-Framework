from importlib import metadata


def test_prometheus_client_dependency_available() -> None:
    """Prometheus client library must be available at the expected version."""
    version = metadata.version("prometheus-client")
    assert version == "0.19.0"
