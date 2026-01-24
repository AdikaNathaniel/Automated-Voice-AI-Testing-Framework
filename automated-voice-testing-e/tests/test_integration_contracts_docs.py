"""
Tests for integration contracts documentation (Phase 5.2 Code Documentation).
"""

import os
import pytest


@pytest.fixture
def docs_dir():
    """Get docs directory path."""
    project_root = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(project_root, "docs")


@pytest.fixture
def integration_contracts_path(docs_dir):
    """Get path to INTEGRATION_CONTRACTS.md."""
    return os.path.join(docs_dir, "INTEGRATION_CONTRACTS.md")


@pytest.fixture
def integration_contracts_content(integration_contracts_path):
    """Read INTEGRATION_CONTRACTS.md content."""
    with open(integration_contracts_path) as f:
        return f.read()


class TestIntegrationContractsDocumentationExists:
    """Test that integration contracts documentation exists."""

    def test_integration_contracts_md_exists(self, integration_contracts_path):
        """Test that INTEGRATION_CONTRACTS.md exists."""
        assert os.path.exists(integration_contracts_path), \
            "docs/INTEGRATION_CONTRACTS.md should exist"


class TestServiceDependencyGraph:
    """Test service dependency documentation."""

    def test_has_dependency_graph_section(self, integration_contracts_content):
        """Test that dependency graph is documented."""
        has_graph = (
            "dependency" in integration_contracts_content.lower() or
            "graph" in integration_contracts_content.lower()
        )
        assert has_graph, "Should document service dependencies"

    def test_documents_service_relationships(self, integration_contracts_content):
        """Test that service relationships are documented."""
        has_relationships = (
            "service" in integration_contracts_content.lower() and
            ("depends" in integration_contracts_content.lower() or
             "requires" in integration_contracts_content.lower() or
             "uses" in integration_contracts_content.lower())
        )
        assert has_relationships, "Should document service relationships"


class TestDependencyTypes:
    """Test required vs optional dependency documentation."""

    def test_documents_required_dependencies(self, integration_contracts_content):
        """Test that required dependencies are documented."""
        assert "required" in integration_contracts_content.lower(), \
            "Should document required dependencies"

    def test_documents_optional_dependencies(self, integration_contracts_content):
        """Test that optional dependencies are documented."""
        assert "optional" in integration_contracts_content.lower(), \
            "Should document optional dependencies"


class TestAPIContracts:
    """Test API contracts documentation."""

    def test_has_api_contracts_section(self, integration_contracts_content):
        """Test that API contracts are documented."""
        has_contracts = (
            "contract" in integration_contracts_content.lower() or
            "interface" in integration_contracts_content.lower() or
            "api" in integration_contracts_content.lower()
        )
        assert has_contracts, "Should document API contracts"

    def test_documents_request_format(self, integration_contracts_content):
        """Test that request formats are documented."""
        has_request = (
            "request" in integration_contracts_content.lower() or
            "input" in integration_contracts_content.lower()
        )
        assert has_request, "Should document request formats"

    def test_documents_response_format(self, integration_contracts_content):
        """Test that response formats are documented."""
        has_response = (
            "response" in integration_contracts_content.lower() or
            "output" in integration_contracts_content.lower()
        )
        assert has_response, "Should document response formats"


class TestServiceGroups:
    """Test service group documentation."""

    def test_documents_core_services(self, integration_contracts_content):
        """Test that core services are documented."""
        core_services = ["test", "validation", "execution"]
        documented = sum(
            1 for svc in core_services
            if svc in integration_contracts_content.lower()
        )
        assert documented >= 2, "Should document core services"

    def test_documents_infrastructure_services(self, integration_contracts_content):
        """Test that infrastructure services are documented."""
        infra_services = ["database", "redis", "queue", "cache"]
        documented = sum(
            1 for svc in infra_services
            if svc in integration_contracts_content.lower()
        )
        assert documented >= 2, "Should document infrastructure services"


class TestDataFlow:
    """Test data flow documentation."""

    def test_documents_data_flow(self, integration_contracts_content):
        """Test that data flow is documented."""
        has_flow = (
            "flow" in integration_contracts_content.lower() or
            "pipeline" in integration_contracts_content.lower()
        )
        assert has_flow, "Should document data flow"
