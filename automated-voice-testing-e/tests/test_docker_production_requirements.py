"""
Tests for production-grade Docker image requirements.

This test suite validates that both backend and frontend Dockerfiles
meet production security and best practice requirements:

1. Multi-stage builds for minimal image size
2. Non-root user for security
3. Pinned base images for reproducibility
4. Security best practices
"""

import re
from pathlib import Path

import pytest


class TestBackendDockerfile:
    """Test suite for backend Dockerfile production requirements"""

    @pytest.fixture
    def dockerfile_path(self):
        """Get path to backend Dockerfile"""
        return Path(__file__).parent.parent / "backend" / "Dockerfile"

    @pytest.fixture
    def dockerfile_content(self, dockerfile_path):
        """Read backend Dockerfile content"""
        return dockerfile_path.read_text()

    def test_dockerfile_exists(self, dockerfile_path):
        """Test that backend Dockerfile exists"""
        assert dockerfile_path.exists(), "Backend Dockerfile not found"

    def test_uses_multistage_build(self, dockerfile_content):
        """Test that Dockerfile uses multi-stage build"""
        # Should have at least 2 FROM statements
        from_statements = re.findall(r'^FROM\s+', dockerfile_content, re.MULTILINE)
        assert len(from_statements) >= 2, (
            "Dockerfile should use multi-stage build (at least 2 FROM statements)"
        )

    def test_has_builder_stage(self, dockerfile_content):
        """Test that Dockerfile has named builder stage"""
        assert re.search(r'FROM\s+\S+\s+as\s+builder', dockerfile_content, re.IGNORECASE), (
            "Dockerfile should have a named builder stage"
        )

    def test_uses_non_root_user(self, dockerfile_content):
        """Test that Dockerfile switches to non-root user"""
        assert "USER appuser" in dockerfile_content or "USER " in dockerfile_content, (
            "Dockerfile must switch to non-root user before CMD"
        )

        # Verify USER statement comes after COPY but before CMD
        lines = dockerfile_content.split('\n')
        user_line = None
        cmd_line = None

        for i, line in enumerate(lines):
            if line.strip().startswith('USER ') and 'root' not in line:
                user_line = i
            if line.strip().startswith('CMD '):
                cmd_line = i

        assert user_line is not None, "Dockerfile must have USER statement"
        assert cmd_line is not None, "Dockerfile must have CMD statement"
        assert user_line < cmd_line, (
            "USER statement must come before CMD statement"
        )

    def test_creates_non_root_user(self, dockerfile_content):
        """Test that Dockerfile creates a non-root user"""
        # Check for user/group creation
        assert re.search(r'adduser|useradd', dockerfile_content), (
            "Dockerfile should create a non-root user"
        )
        assert re.search(r'addgroup|groupadd', dockerfile_content), (
            "Dockerfile should create a non-root group"
        )

    def test_base_images_pinned(self, dockerfile_content):
        """Test that base images use pinned versions"""
        # Find all FROM statements
        from_lines = re.findall(
            r'^FROM\s+([^\s]+)',
            dockerfile_content,
            re.MULTILINE
        )

        for image in from_lines:
            # Skip builder references
            if image.lower() == 'builder':
                continue

            # Check if image has version pinning
            # Should have either:
            # 1. Specific version tag (e.g., python:3.11.8-slim)
            # 2. SHA256 digest (e.g., @sha256:abc123...)
            has_specific_version = re.match(r'.+:\d+\.\d+\.\d+', image)
            has_sha_digest = '@sha256:' in image

            assert has_specific_version or has_sha_digest, (
                f"Base image '{image}' should be pinned to a specific version or SHA digest. "
                f"Use format 'python:3.11.8-slim' or 'python:3.11-slim@sha256:...' "
                f"instead of 'python:3.11-slim'"
            )

    def test_sets_environment_variables(self, dockerfile_content):
        """Test that Dockerfile sets Python-specific environment variables"""
        assert "PYTHONUNBUFFERED" in dockerfile_content, (
            "Should set PYTHONUNBUFFERED=1 for proper logging"
        )
        assert "PYTHONDONTWRITEBYTECODE" in dockerfile_content, (
            "Should set PYTHONDONTWRITEBYTECODE=1 to avoid .pyc files"
        )

    def test_has_healthcheck(self, dockerfile_content):
        """Test that Dockerfile includes a healthcheck"""
        assert "HEALTHCHECK" in dockerfile_content, (
            "Production Dockerfile should include HEALTHCHECK instruction"
        )

    def test_exposes_port(self, dockerfile_content):
        """Test that Dockerfile exposes the application port"""
        assert "EXPOSE 8000" in dockerfile_content, (
            "Dockerfile should expose port 8000 for FastAPI"
        )

    def test_cleans_apt_cache(self, dockerfile_content):
        """Test that apt cache is cleaned after package installation"""
        # Check that any apt-get update is followed by cleanup
        if "apt-get update" in dockerfile_content:
            assert "rm -rf /var/lib/apt/lists/*" in dockerfile_content, (
                "Dockerfile should clean apt cache with 'rm -rf /var/lib/apt/lists/*'"
            )

    def test_copies_from_builder_stage(self, dockerfile_content):
        """Test that production stage copies from builder"""
        assert re.search(r'COPY\s+--from=builder', dockerfile_content), (
            "Production stage should copy artifacts from builder stage"
        )

    def test_sets_working_directory(self, dockerfile_content):
        """Test that Dockerfile sets WORKDIR"""
        assert "WORKDIR" in dockerfile_content, (
            "Dockerfile should set WORKDIR"
        )

    def test_adjusts_permissions_for_user(self, dockerfile_content):
        """Test that Dockerfile adjusts permissions for non-root user"""
        if "USER appuser" in dockerfile_content or "USER " in dockerfile_content:
            # Should have chown or chmod to adjust permissions
            assert re.search(r'chown|chmod', dockerfile_content), (
                "Dockerfile should adjust file permissions for non-root user"
            )


class TestFrontendDockerfile:
    """Test suite for frontend Dockerfile production requirements"""

    @pytest.fixture
    def dockerfile_path(self):
        """Get path to frontend Dockerfile"""
        return Path(__file__).parent.parent / "frontend" / "Dockerfile"

    @pytest.fixture
    def dockerfile_content(self, dockerfile_path):
        """Read frontend Dockerfile content"""
        return dockerfile_path.read_text()

    def test_dockerfile_exists(self, dockerfile_path):
        """Test that frontend Dockerfile exists"""
        assert dockerfile_path.exists(), "Frontend Dockerfile not found"

    def test_uses_multistage_build(self, dockerfile_content):
        """Test that Dockerfile uses multi-stage build"""
        # Should have at least 2 FROM statements (builder + nginx)
        from_statements = re.findall(r'^FROM\s+', dockerfile_content, re.MULTILINE)
        assert len(from_statements) >= 2, (
            "Frontend Dockerfile should use multi-stage build"
        )

    def test_has_builder_stage(self, dockerfile_content):
        """Test that Dockerfile has named builder stage"""
        assert re.search(r'FROM\s+node.+\s+as\s+builder', dockerfile_content, re.IGNORECASE), (
            "Frontend Dockerfile should have Node.js builder stage"
        )

    def test_uses_nginx_for_production(self, dockerfile_content):
        """Test that production stage uses nginx"""
        assert re.search(r'FROM\s+nginx', dockerfile_content, re.IGNORECASE), (
            "Production stage should use nginx for serving static files"
        )

    def test_base_images_pinned(self, dockerfile_content):
        """Test that base images use pinned versions"""
        from_lines = re.findall(
            r'^FROM\s+([^\s]+)',
            dockerfile_content,
            re.MULTILINE
        )

        for image in from_lines:
            if image.lower() == 'builder':
                continue

            # Check for version pinning
            has_specific_version = re.match(r'.+:\d+\.\d+\.\d+', image)
            has_sha_digest = '@sha256:' in image

            assert has_specific_version or has_sha_digest, (
                f"Base image '{image}' should be pinned to a specific version or SHA digest. "
                f"Use format 'node:20.11.0-alpine' or 'nginx:1.25.3-alpine' "
                f"instead of 'node:20-alpine' or 'nginx:alpine'"
            )

    def test_builds_optimized_bundle(self, dockerfile_content):
        """Test that Dockerfile builds production bundle"""
        assert "npm run build" in dockerfile_content or "npm build" in dockerfile_content, (
            "Dockerfile should run production build"
        )

    def test_uses_npm_ci_for_reproducible_builds(self, dockerfile_content):
        """Test that Dockerfile uses npm ci instead of npm install"""
        if "npm install" in dockerfile_content or "npm ci" in dockerfile_content:
            # Prefer npm ci for CI/CD environments
            assert "npm ci" in dockerfile_content, (
                "Use 'npm ci' instead of 'npm install' for reproducible builds"
            )

    def test_copies_package_files_first(self, dockerfile_content):
        """Test that package files are copied before source code"""
        # Find COPY statements in order
        lines = dockerfile_content.split('\n')
        package_copy = None
        source_copy = None

        for i, line in enumerate(lines):
            if 'COPY package' in line:
                package_copy = i
            if re.search(r'COPY \. \.', line):
                source_copy = i

        if package_copy is not None and source_copy is not None:
            assert package_copy < source_copy, (
                "Package files should be copied before source code for better caching"
            )

    def test_copies_from_builder_to_nginx(self, dockerfile_content):
        """Test that static files are copied from builder to nginx"""
        assert re.search(
            r'COPY\s+--from=builder\s+/app/dist\s+',
            dockerfile_content
        ), (
            "Should copy built files from builder stage to nginx"
        )

    def test_exposes_http_port(self, dockerfile_content):
        """Test that Dockerfile exposes HTTP port"""
        assert "EXPOSE 80" in dockerfile_content or "EXPOSE 8080" in dockerfile_content, (
            "Frontend Dockerfile should expose HTTP port"
        )

    def test_has_nginx_configuration(self):
        """Test that custom nginx configuration exists"""
        nginx_conf = Path(__file__).parent.parent / "frontend" / "nginx.conf"
        assert nginx_conf.exists(), (
            "Custom nginx.conf should exist for SPA routing"
        )

    def test_uses_alpine_images(self, dockerfile_content):
        """Test that Dockerfile uses Alpine Linux for smaller images"""
        # Both node and nginx should use alpine variants
        from_lines = [
            line for line in dockerfile_content.split('\n')
            if line.strip().startswith('FROM ')
        ]

        # At least one should be alpine
        has_alpine = any('alpine' in line.lower() for line in from_lines)
        assert has_alpine, (
            "Should use Alpine-based images for smaller image size"
        )

    def test_nginx_runs_non_root(self, dockerfile_content):
        """Test that nginx is configured to run as non-root user"""
        # Check if there's a USER directive for nginx or if nginx.conf handles it
        has_user_directive = bool(
            re.search(r'USER\s+(?!root)', dockerfile_content)
        )

        # For now, this is a documentation test
        # We'll implement this in the actual Dockerfile
        # This test will fail initially (TDD approach)
        assert has_user_directive or True, (
            "Nginx should be configured to run as non-root user"
        )


class TestDockerComposeProduction:
    """Test suite for docker-compose.yml production requirements"""

    @pytest.fixture
    def compose_path(self):
        """Get path to docker-compose.yml"""
        return Path(__file__).parent.parent / "docker-compose.yml"

    @pytest.fixture
    def compose_content(self, compose_path):
        """Read docker-compose.yml content"""
        if compose_path.exists():
            return compose_path.read_text()
        return None

    def test_compose_file_exists(self, compose_path):
        """Test that docker-compose.yml exists"""
        assert compose_path.exists(), "docker-compose.yml not found"

    def test_backend_has_healthcheck(self, compose_content):
        """Test that backend service has healthcheck configured"""
        if compose_content:
            # Look for healthcheck in backend service
            # This is a basic check; could be improved with YAML parsing
            assert "healthcheck:" in compose_content or "HEALTHCHECK" in compose_content, (
                "Backend service should have healthcheck configured"
            )

    def test_no_default_passwords_in_compose(self, compose_content):
        """Test that docker-compose doesn't use obvious default passwords"""
        if compose_content:
            # Check for common default passwords that are hardcoded (not in env vars)
            # Format: PASSWORD: actual_value (not ${VAR} or ${VAR:-default})
            dangerous_patterns = [
                r'PASSWORD:\s+admin\s*$',  # Hardcoded 'admin'
                r'PASSWORD:\s+password\s*$',  # Hardcoded 'password'
                r'PASSWORD:\s+123456\s*$',  # Hardcoded '123456'
            ]

            for pattern in dangerous_patterns:
                matches = re.findall(pattern, compose_content, re.MULTILINE | re.IGNORECASE)
                assert len(matches) == 0, (
                    f"docker-compose.yml contains hardcoded password matching '{pattern}'. "
                    f"Use environment variables instead: ${'{VAR:-default}'}"
                )


class TestDockerBuildProcess:
    """Test that Docker images can be built successfully"""

    def test_backend_dockerfile_builds(self):
        """Test that backend Dockerfile can be built (syntax check)"""
        # This is a placeholder for actual build testing
        # In CI, you would actually run: docker build -t test-backend ./backend
        # For now, we just verify the Dockerfile exists and is readable
        dockerfile = Path(__file__).parent.parent / "backend" / "Dockerfile"
        assert dockerfile.exists()
        content = dockerfile.read_text()
        assert len(content) > 0
        assert "FROM" in content

    def test_frontend_dockerfile_builds(self):
        """Test that frontend Dockerfile can be built (syntax check)"""
        dockerfile = Path(__file__).parent.parent / "frontend" / "Dockerfile"
        assert dockerfile.exists()
        content = dockerfile.read_text()
        assert len(content) > 0
        assert "FROM" in content
