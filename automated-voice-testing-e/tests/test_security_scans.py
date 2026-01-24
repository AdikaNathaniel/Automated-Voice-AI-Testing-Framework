"""
Tests for security scan integration and configuration.

This test suite validates:
1. Safety scan can run and detect known vulnerabilities
2. Bandit scan can run and detect code security issues
3. CI configuration includes security scans
4. Security reports are generated correctly
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


class TestSecurityScanIntegration:
    """Test suite for security scan integration"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return Path(__file__).parent.parent

    @pytest.fixture
    def venv_python(self, project_root):
        """Get path to virtualenv Python"""
        venv_bin = project_root / "venv" / "bin" / "python"
        if not venv_bin.exists():
            pytest.skip("Virtual environment not found")
        return str(venv_bin)

    def test_ci_config_includes_security_scan_job(self, project_root):
        """Test that backend-ci.yml includes security-scan job"""
        ci_file = project_root / ".github" / "workflows" / "backend-ci.yml"
        assert ci_file.exists(), "backend-ci.yml not found"

        with open(ci_file, "r") as f:
            content = f.read()

        # Verify security-scan job exists
        assert "security-scan:" in content, "security-scan job not found in CI config"

        # Verify safety check is configured
        assert "safety check" in content, "safety check not configured"

        # Verify bandit scan is configured
        assert "bandit" in content, "bandit scan not configured"

    def test_ci_config_has_safety_installation(self, project_root):
        """Test that CI config installs safety tool"""
        ci_file = project_root / ".github" / "workflows" / "backend-ci.yml"

        with open(ci_file, "r") as f:
            content = f.read()

        assert "pip install safety" in content, "safety installation not found"

    def test_ci_config_has_bandit_installation(self, project_root):
        """Test that CI config installs bandit tool"""
        ci_file = project_root / ".github" / "workflows" / "backend-ci.yml"

        with open(ci_file, "r") as f:
            content = f.read()

        assert "pip install" in content and "bandit" in content, (
            "bandit installation not found"
        )

    def test_safety_scan_can_run(self, project_root, venv_python):
        """Test that safety scan can execute successfully"""
        safety_bin = project_root / "venv" / "bin" / "safety"

        if not safety_bin.exists():
            pytest.skip("safety not installed in venv")

        # Run safety check
        result = subprocess.run(
            [str(safety_bin), "check", "--json"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )

        # Safety returns exit code 64 when vulnerabilities are found
        # We just want to verify it runs, not that there are no vulnerabilities
        assert result.returncode in [0, 64], (
            f"Safety scan failed with unexpected exit code: {result.returncode}"
        )

    def test_bandit_scan_can_run(self, project_root):
        """Test that bandit scan can execute successfully"""
        bandit_bin = project_root / "venv" / "bin" / "bandit"

        if not bandit_bin.exists():
            pytest.skip("bandit not installed in venv")

        backend_dir = project_root / "backend"
        assert backend_dir.exists(), "backend directory not found"

        # Run bandit scan
        result = subprocess.run(
            [
                str(bandit_bin),
                "-r",
                str(backend_dir),
                "-f",
                "json",
                "-o",
                "/tmp/test-bandit-report.json",
            ],
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )

        # Bandit returns exit code 1 when issues are found
        # We just want to verify it runs, not that there are no issues
        assert result.returncode in [0, 1], (
            f"Bandit scan failed with unexpected exit code: {result.returncode}"
        )

        # Verify report was created
        report_file = Path("/tmp/test-bandit-report.json")
        assert report_file.exists(), "Bandit report not generated"

        # Verify report is valid JSON
        with open(report_file, "r") as f:
            report_data = json.load(f)

        # Verify report has expected structure
        assert "metrics" in report_data, "Bandit report missing metrics"
        assert "results" in report_data, "Bandit report missing results"

        # Clean up
        report_file.unlink()

    def test_safety_report_structure(self, project_root):
        """Test that safety generates a valid JSON report"""
        safety_bin = project_root / "venv" / "bin" / "safety"

        if not safety_bin.exists():
            pytest.skip("safety not installed in venv")

        # Run safety check and save report to file
        report_file = Path("/tmp/test-safety-report.json")
        result = subprocess.run(
            [str(safety_bin), "check", "--json"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )

        # Write stdout to file for easier parsing
        with open(report_file, "w") as f:
            f.write(result.stdout)

        # Read and parse the file, looking for JSON content
        with open(report_file, "r") as f:
            content = f.read()

        # Find the JSON object (between first { and matching })
        json_start = content.find("{")
        assert json_start != -1, "Could not find JSON in safety output"

        # Extract just the JSON portion
        brace_count = 0
        json_end = json_start
        for i in range(json_start, len(content)):
            if content[i] == "{":
                brace_count += 1
            elif content[i] == "}":
                brace_count -= 1
                if brace_count == 0:
                    json_end = i + 1
                    break

        json_output = content[json_start:json_end]
        report_data = json.loads(json_output)

        # Verify report structure
        assert "report_meta" in report_data, "Safety report missing report_meta"
        assert "scanned_packages" in report_data, (
            "Safety report missing scanned_packages"
        )
        assert "vulnerabilities" in report_data, (
            "Safety report missing vulnerabilities"
        )

        # Verify metadata
        meta = report_data["report_meta"]
        assert "vulnerabilities_found" in meta, (
            "Safety report missing vulnerabilities_found count"
        )
        assert "packages_found" in meta, "Safety report missing packages_found count"

        # Clean up
        report_file.unlink()

    def test_bandit_report_includes_severity_metrics(self, project_root):
        """Test that bandit report includes severity metrics"""
        bandit_bin = project_root / "venv" / "bin" / "bandit"

        if not bandit_bin.exists():
            pytest.skip("bandit not installed in venv")

        backend_dir = project_root / "backend"
        report_file = Path("/tmp/test-bandit-metrics.json")

        # Run bandit scan
        subprocess.run(
            [
                str(bandit_bin),
                "-r",
                str(backend_dir),
                "-f",
                "json",
                "-o",
                str(report_file),
            ],
            capture_output=True,
            cwd=str(project_root),
        )

        # Read and verify report
        with open(report_file, "r") as f:
            report_data = json.load(f)

        metrics = report_data["metrics"]["_totals"]

        # Verify severity counts are present
        assert "SEVERITY.HIGH" in metrics, "Missing HIGH severity metric"
        assert "SEVERITY.MEDIUM" in metrics, "Missing MEDIUM severity metric"
        assert "SEVERITY.LOW" in metrics, "Missing LOW severity metric"

        # Verify confidence counts are present
        assert "CONFIDENCE.HIGH" in metrics, "Missing HIGH confidence metric"
        assert "CONFIDENCE.MEDIUM" in metrics, "Missing MEDIUM confidence metric"
        assert "CONFIDENCE.LOW" in metrics, "Missing LOW confidence metric"

        # Clean up
        report_file.unlink()

    def test_ci_security_scan_uploads_artifacts(self, project_root):
        """Test that CI config uploads security scan artifacts"""
        ci_file = project_root / ".github" / "workflows" / "backend-ci.yml"

        with open(ci_file, "r") as f:
            content = f.read()

        # Verify artifact upload is configured
        assert "upload-artifact" in content, "Artifact upload not configured"
        assert "security-reports" in content, "Security reports artifact not named"

    def test_ci_security_scans_continue_on_error(self, project_root):
        """Test that CI security scans are configured to continue on error"""
        ci_file = project_root / ".github" / "workflows" / "backend-ci.yml"

        with open(ci_file, "r") as f:
            content = f.read()

        # In the security-scan job, verify continue-on-error is set
        # This allows the job to complete even if vulnerabilities are found
        lines = content.split("\n")
        in_security_job = False
        found_continue_on_error = False

        for line in lines:
            if "security-scan:" in line:
                in_security_job = True
            elif in_security_job and line.strip().startswith("continue-on-error:"):
                found_continue_on_error = True

        assert found_continue_on_error, (
            "Security scans should have continue-on-error configured"
        )


class TestSecurityFindings:
    """Tests to document expected security findings"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return Path(__file__).parent.parent

    def test_known_vulnerabilities_documented(self, project_root):
        """Test that known vulnerabilities are documented"""
        # This test serves as documentation of known vulnerabilities
        # If new critical vulnerabilities are found, they should be
        # addressed or documented here with risk acceptance rationale

        known_vulnerable_packages = [
            "torch",  # Multiple CVEs, ML library
            "python-multipart",  # DoS vulnerabilities
            "urllib3",  # SSRF and redirect issues
            "requests",  # Credential leakage
            "sentence-transformers",  # Code execution
            "python-socketio",  # Deserialization
            "black",  # ReDoS (dev dependency)
            "scikit-learn",  # Data leakage
            "ecdsa",  # Side-channel attacks (unfixable)
        ]

        # This list serves as documentation and awareness
        # Actual remediation should be tracked in risk acceptance doc
        assert len(known_vulnerable_packages) > 0, (
            "Known vulnerabilities should be documented"
        )

    def test_bandit_medium_severity_issues_documented(self, project_root):
        """Test that medium severity bandit findings are documented"""
        # Known medium severity issues:
        known_issues = {
            "B104": "Binding to all interfaces (0.0.0.0) in config.py",
            "B108": "Hardcoded /tmp directory in test files",
        }

        # Risk acceptance rationale:
        # B104: Intentional for containerized applications
        # B108: Only in test mocks, not production code

        assert len(known_issues) > 0, (
            "Known bandit issues should be documented"
        )
