"""
Coverage Analyzer for Test Coverage Matrix Generation

Analyzes test files to determine coverage across:
- API Routes (20 routes)
- Services (14 categories)
- Models (26 models)
- Cross-cutting concerns (14 concerns)
"""

from pathlib import Path
from typing import Dict, List, Set, Tuple
import re
from collections import defaultdict


class CoverageAnalyzer:
    """Analyzes test files to determine test coverage."""

    # Route patterns to identify route-related tests
    ROUTE_PATTERNS = {
        "auth": [r"auth", r"register", r"login", r"logout", r"token", r"refresh"],
        "test-suites": [r"test_suite", r"test-suite", r"suite"],
        "test-cases": [r"test_case", r"test-case", r"test_cases"],
        "test-runs": [r"test_run", r"test-run", r"test_runs"],
        "scenarios": [r"scenario"],
        "human-validation": [r"human_validation", r"validator", r"validation_queue"],
        "configurations": [r"config"],
        "analytics": [r"analytics", r"dashboard", r"trend"],
        "dashboard": [r"dashboard"],
        "defects": [r"defect"],
        "edge-cases": [r"edge_case", r"edge-case"],
        "knowledge-base": [r"knowledge_base", r"knowledge-base"],
        "metrics": [r"metric"],
        "regressions": [r"regression"],
        "translations": [r"translat"],
        "activity": [r"activity"],
        "reports": [r"report"],
        "webhooks": [r"webhook"],
        "workers": [r"worker"],
        "language-stats": [r"language"],
    }

    # Service patterns
    SERVICE_PATTERNS = {
        "Orchestration": [r"orchestrat"],
        "Validation": [r"validat"],
        "Test Management": [r"test_run", r"test_case", r"test_suite"],
        "Analytics": [r"analytics", r"dashboard", r"trend"],
        "Audio Processing": [r"audio"],
        "Transcription": [r"transcript"],
        "NLU": [r"nlu"],
        "Performance": [r"performance"],
        "Telephony": [r"telephony"],
        "Language": [r"language", r"translat"],
        "Compliance": [r"compliance"],
        "Defect": [r"defect"],
        "Edge Case": [r"edge_case"],
        "Integration": [r"integration"],
    }

    # Model patterns
    MODEL_PATTERNS = {
        "User": [r"user"],
        "TestSuite": [r"test_suite"],
        "TestCase": [r"test_case"],
        "TestCaseLanguage": [r"test_case_language"],
        "TestCaseVersion": [r"test_case_version"],
        "ExpectedOutcome": [r"expected_outcome"],
        "TestRun": [r"test_run"],
        "MultiTurnExecution": [r"multi_turn_execution"],
        "DeviceTestExecution": [r"device_test_execution"],
        "ValidationQueue": [r"validation_queue"],
        "ValidationResult": [r"validation_result"],
        "HumanValidation": [r"human_validation"],
        "ValidatorPerformance": [r"validator"],
        "Configuration": [r"config"],
        "ConfigurationHistory": [r"configuration_history"],
        "Defect": [r"defect"],
        "EdgeCase": [r"edge_case"],
        "KnowledgeBase": [r"knowledge_base"],
        "ScenarioScript": [r"scenario"],
        "EscalationPolicy": [r"escalation"],
        "ActivityLog": [r"activity"],
        "Comment": [r"comment"],
        "TestMetric": [r"metric"],
        "TestExecutionQueue": [r"queue"],
        "RegressionBaseline": [r"regression"],
    }

    # Cross-cutting concerns
    CONCERN_PATTERNS = {
        "Authentication": [r"auth", r"login", r"register"],
        "Authorization (RBAC)": [r"rbac", r"role", r"permission"],
        "Multi-tenancy": [r"tenant"],
        "Rate Limiting": [r"rate_limit"],
        "Caching": [r"cache"],
        "Pagination": [r"pagina"],
        "Filtering": [r"filter"],
        "Sorting": [r"sort"],
        "Error Handling": [r"error", r"exception"],
        "Logging": [r"log"],
        "Metrics": [r"metric"],
        "Webhooks": [r"webhook"],
        "Async Operations": [r"async"],
        "Transactions": [r"transaction"],
        "Audit Trail": [r"audit"],
    }

    # Test type patterns
    TEST_TYPE_PATTERNS = {
        "unit": [r"test_.*\.py$", r"(?<!e2e_)(?<!integration_)test_"],
        "integration": [r"integration", r"test_.*_service\.py", r"test_.*_integration\.py"],
        "e2e": [r"e2e", r"end_to_end"],
        "security": [r"security", r"auth"],
        "performance": [r"performance", r"perf"],
    }

    def find_test_files(self, test_dir: Path) -> List[Path]:
        """Find all test files in a directory."""
        if not test_dir.exists():
            return []
        return list(test_dir.glob("test_*.py"))

    def identify_test_types(self, test_file: Path) -> Set[str]:
        """Identify test types (unit, integration, e2e, security, performance) for a file."""
        test_types = set()
        file_name = test_file.name.lower()
        file_content = test_file.read_text().lower()

        for test_type, patterns in self.TEST_TYPE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, file_name) or re.search(pattern, file_content):
                    test_types.add(test_type)

        # Default to unit if no specific type identified
        if not test_types:
            test_types.add("unit")

        return test_types

    def extract_routes_from_file(self, test_file: Path) -> Set[str]:
        """Extract route names referenced in a test file."""
        routes = set()
        try:
            content = test_file.read_text().lower()
            for route, patterns in self.ROUTE_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, content):
                        routes.add(route)
        except (IOError, UnicodeDecodeError):
            pass
        return routes

    def extract_services_from_file(self, test_file: Path) -> Set[str]:
        """Extract service names referenced in a test file."""
        services = set()
        try:
            content = test_file.read_text().lower()
            for service, patterns in self.SERVICE_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, content):
                        services.add(service)
        except (IOError, UnicodeDecodeError):
            pass
        return services

    def extract_models_from_file(self, test_file: Path) -> Set[str]:
        """Extract model names referenced in a test file."""
        models = set()
        try:
            content = test_file.read_text().lower()
            for model, patterns in self.MODEL_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, content):
                        models.add(model)
        except (IOError, UnicodeDecodeError):
            pass
        return models

    def extract_concerns_from_file(self, test_file: Path) -> Set[str]:
        """Extract cross-cutting concerns referenced in a test file."""
        concerns = set()
        try:
            content = test_file.read_text().lower()
            for concern, patterns in self.CONCERN_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, content):
                        concerns.add(concern)
        except (IOError, UnicodeDecodeError):
            pass
        return concerns

    def build_api_route_coverage_matrix(
        self, test_dir: Path, routes: List[str] = None
    ) -> Dict[str, Dict[str, bool]]:
        """Build coverage matrix for API routes."""
        if routes is None:
            routes = list(self.ROUTE_PATTERNS.keys())

        coverage = {route: {test_type: False for test_type in ["unit", "integration", "e2e", "security", "performance"]} for route in routes}

        test_files = self.find_test_files(test_dir)
        for test_file in test_files:
            test_types = self.identify_test_types(test_file)
            routes_in_file = self.extract_routes_from_file(test_file)

            for route in routes_in_file:
                if route in coverage:
                    for test_type in test_types:
                        if test_type in coverage[route]:
                            coverage[route][test_type] = True

        return coverage

    def build_service_coverage_matrix(
        self, test_dir: Path, services: List[str] = None
    ) -> Dict[str, Dict[str, bool]]:
        """Build coverage matrix for services."""
        if services is None:
            services = list(self.SERVICE_PATTERNS.keys())

        coverage = {service: {test_type: False for test_type in ["unit", "integration", "mocking", "error_handling"]} for service in services}

        test_files = self.find_test_files(test_dir)
        for test_file in test_files:
            test_types = self.identify_test_types(test_file)
            services_in_file = self.extract_services_from_file(test_file)
            content = test_file.read_text().lower()

            for service in services_in_file:
                if service in coverage:
                    # Map test types
                    if "unit" in test_types:
                        coverage[service]["unit"] = True
                    if "integration" in test_types:
                        coverage[service]["integration"] = True
                    # Check for mocking patterns
                    if re.search(r"mock|@patch", content):
                        coverage[service]["mocking"] = True
                    # Check for error handling patterns
                    if re.search(r"except|error|exception", content):
                        coverage[service]["error_handling"] = True

        return coverage

    def build_model_coverage_matrix(
        self, test_dir: Path, models: List[str] = None
    ) -> Dict[str, Dict[str, bool]]:
        """Build coverage matrix for models."""
        if models is None:
            models = list(self.MODEL_PATTERNS.keys())

        coverage = {model: {aspect: False for aspect in ["crud", "relationships", "constraints", "queries"]} for model in models}

        test_files = self.find_test_files(test_dir)
        for test_file in test_files:
            models_in_file = self.extract_models_from_file(test_file)
            content = test_file.read_text().lower()

            for model in models_in_file:
                if model in coverage:
                    # Check for CRUD patterns
                    if re.search(r"create|read|update|delete|crud", content):
                        coverage[model]["crud"] = True
                    # Check for relationship patterns
                    if re.search(r"relationship|foreign|join|cascade", content):
                        coverage[model]["relationships"] = True
                    # Check for constraint patterns
                    if re.search(r"constraint|unique|check|primary", content):
                        coverage[model]["constraints"] = True
                    # Check for query patterns
                    if re.search(r"query|filter|select|aggregate", content):
                        coverage[model]["queries"] = True

        return coverage

    def build_concern_coverage_matrix(
        self, test_dir: Path, concerns: List[str] = None
    ) -> Dict[str, Dict[str, bool]]:
        """Build coverage matrix for cross-cutting concerns."""
        if concerns is None:
            concerns = list(self.CONCERN_PATTERNS.keys())

        coverage = {concern: {test_type: False for test_type in ["unit", "integration", "e2e"]} for concern in concerns}

        test_files = self.find_test_files(test_dir)
        for test_file in test_files:
            test_types = self.identify_test_types(test_file)
            concerns_in_file = self.extract_concerns_from_file(test_file)

            for concern in concerns_in_file:
                if concern in coverage:
                    for test_type in ["unit", "integration", "e2e"]:
                        if test_type in test_types:
                            coverage[concern][test_type] = True

        return coverage

    def format_coverage_matrix(
        self, coverage: Dict[str, Dict[str, bool]], matrix_type: str
    ) -> str:
        """Format coverage matrix as markdown table."""
        if matrix_type == "api_routes":
            columns = ["Route", "Unit", "Integration", "E2E", "Security", "Performance"]
        elif matrix_type == "services":
            columns = ["Service Category", "Unit", "Integration", "Mocking", "Error Handling"]
        elif matrix_type == "models":
            columns = ["Model", "CRUD", "Relationships", "Constraints", "Queries"]
        elif matrix_type == "concerns":
            columns = ["Concern", "Unit Tests", "Integration Tests", "E2E Tests"]
        else:
            columns = list(coverage.get(list(coverage.keys())[0], {}).keys()) if coverage else []

        # Build markdown table
        lines = []
        lines.append("| " + " | ".join(columns) + " |")
        lines.append("|" + "|".join(["----"] * len(columns)) + "|")

        for item, coverage_types in sorted(coverage.items()):
            row = [item]
            for col in columns[1:]:
                col_key = col.lower().replace(" ", "_").replace("(", "").replace(")", "")
                is_covered = coverage_types.get(col_key, False) or coverage_types.get(col.lower(), False)
                row.append("✓" if is_covered else "✗")
            lines.append("| " + " | ".join(row) + " |")

        return "\n".join(lines)

    def find_coverage_gaps(self, coverage: Dict[str, Dict[str, bool]]) -> Dict[str, List[str]]:
        """Identify items with coverage gaps."""
        gaps = {}
        for item, coverage_types in coverage.items():
            uncovered = [ct for ct, is_covered in coverage_types.items() if not is_covered]
            if uncovered:
                gaps[item] = uncovered
        return gaps
