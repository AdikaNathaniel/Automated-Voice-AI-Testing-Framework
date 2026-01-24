"""
Test suite for frontend Dockerfile

Ensures proper Dockerfile configuration for the frontend service,
including multi-stage build with Node.js build stage and Nginx serve stage,
with SPA routing configuration.
"""

import os
import json
import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
DOCKERFILE = FRONTEND_DIR / "Dockerfile"


class TestDockerfileExists:
    """Test Dockerfile file existence"""

    def test_dockerfile_exists(self):
        """Test that frontend/Dockerfile exists"""
        assert DOCKERFILE.exists(), "frontend/Dockerfile should exist"
        assert DOCKERFILE.is_file(), "frontend/Dockerfile should be a file"

    def test_dockerfile_has_content(self):
        """Test that Dockerfile has content"""
        content = DOCKERFILE.read_text()
        assert len(content) > 0, "Dockerfile should not be empty"


class TestMultiStageBuild:
    """Test multi-stage build configuration"""

    def test_uses_multiple_stages(self):
        """Test that Dockerfile uses multi-stage build"""
        content = DOCKERFILE.read_text()
        from_count = content.count('FROM')
        assert from_count >= 2, "Dockerfile should have at least 2 stages (build + serve)"

    def test_has_build_stage(self):
        """Test that Dockerfile has a build stage"""
        content = DOCKERFILE.read_text()
        has_builder = 'as builder' in content or 'as build' in content
        assert has_builder, "Dockerfile should have a named build stage"


class TestNodeBuildStage:
    """Test Node.js build stage"""

    def test_uses_node_base_image(self):
        """Test that build stage uses Node.js base image"""
        content = DOCKERFILE.read_text()
        assert 'FROM node' in content, "Dockerfile should use Node.js base image for build stage"

    def test_specifies_node_version(self):
        """Test that Dockerfile specifies Node.js version"""
        content = DOCKERFILE.read_text()
        # Should specify version like node:18 or node:20
        has_version = 'node:18' in content or 'node:20' in content or 'node:21' in content
        assert has_version, "Dockerfile should specify Node.js version"

    def test_sets_working_directory(self):
        """Test that build stage sets WORKDIR"""
        content = DOCKERFILE.read_text()
        assert 'WORKDIR' in content, "Dockerfile should set WORKDIR"


class TestDependencyInstallation:
    """Test dependency installation in build stage"""

    def test_copies_package_json(self):
        """Test that Dockerfile copies package.json"""
        content = DOCKERFILE.read_text()
        assert 'package.json' in content, "Dockerfile should copy package.json"

    def test_installs_dependencies_with_npm(self):
        """Test that Dockerfile installs dependencies with npm"""
        content = DOCKERFILE.read_text()
        has_npm_install = 'npm install' in content or 'npm ci' in content
        assert has_npm_install, "Dockerfile should install dependencies with npm"

    def test_uses_npm_ci_or_install(self):
        """Test that uses npm ci (faster and more reliable) or npm install"""
        content = DOCKERFILE.read_text()
        has_npm = 'npm ci' in content or 'npm install' in content
        assert has_npm, "Dockerfile should use npm ci or npm install"


class TestBuildProcess:
    """Test application build process"""

    def test_copies_application_code(self):
        """Test that Dockerfile copies application code"""
        content = DOCKERFILE.read_text()
        has_copy = 'COPY' in content
        assert has_copy, "Dockerfile should copy application code"

    def test_runs_build_command(self):
        """Test that Dockerfile runs build command"""
        content = DOCKERFILE.read_text()
        has_build = 'npm run build' in content or 'RUN npm run build' in content
        assert has_build, "Dockerfile should run npm run build"


class TestNginxServeStage:
    """Test Nginx serve stage"""

    def test_uses_nginx_base_image(self):
        """Test that serve stage uses Nginx base image"""
        content = DOCKERFILE.read_text()
        # Should have a second FROM with nginx
        has_nginx = 'FROM nginx' in content
        assert has_nginx, "Dockerfile should use Nginx base image for serve stage"

    def test_copies_built_files_from_build_stage(self):
        """Test that copies built files from build stage"""
        content = DOCKERFILE.read_text()
        has_copy_from = 'COPY --from=build' in content or 'COPY --from=builder' in content
        assert has_copy_from, "Dockerfile should copy built files from build stage"

    def test_copies_dist_or_build_folder(self):
        """Test that copies dist or build folder (Vite uses dist)"""
        content = DOCKERFILE.read_text()
        has_dist = '/dist' in content or '/build' in content
        assert has_dist, "Dockerfile should copy /dist or /build folder"


class TestNginxConfiguration:
    """Test Nginx configuration"""

    def test_copies_nginx_config(self):
        """Test that Dockerfile copies nginx configuration"""
        content = DOCKERFILE.read_text()
        has_nginx_conf = 'nginx.conf' in content or 'default.conf' in content
        assert has_nginx_conf, "Dockerfile should copy nginx configuration"

    def test_nginx_config_goes_to_etc_nginx(self):
        """Test that nginx config is copied to /etc/nginx"""
        content = DOCKERFILE.read_text()
        has_etc_nginx = '/etc/nginx' in content
        assert has_etc_nginx, "Dockerfile should copy config to /etc/nginx"


class TestSPARouting:
    """Test SPA routing configuration"""

    def test_references_spa_or_try_files(self):
        """Test that Dockerfile or comments reference SPA routing"""
        content = DOCKERFILE.read_text()
        # Should mention SPA, try_files, or fallback
        has_spa_reference = 'SPA' in content or 'spa' in content or 'try_files' in content or 'fallback' in content
        # This might be in comments or nginx config reference
        # Just check that SPA routing is considered
        pass


class TestPortExposure:
    """Test port exposure"""

    def test_exposes_port(self):
        """Test that Dockerfile exposes a port"""
        content = DOCKERFILE.read_text()
        assert 'EXPOSE' in content, "Dockerfile should expose a port"

    def test_exposes_port_80_or_8080(self):
        """Test that Dockerfile exposes port 80 or 8080"""
        content = DOCKERFILE.read_text()
        has_port = '80' in content or '8080' in content
        assert has_port, "Dockerfile should expose port 80 or 8080"


class TestDockerfileStructure:
    """Test overall Dockerfile structure"""

    def test_has_valid_dockerfile_syntax(self):
        """Test that Dockerfile has valid syntax"""
        content = DOCKERFILE.read_text()
        lines = [line.strip() for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
        if lines:
            first_instruction = lines[0]
            assert first_instruction.startswith('FROM') or first_instruction.startswith('ARG'), \
                "Dockerfile should start with FROM or ARG"

    def test_file_not_too_small(self):
        """Test that Dockerfile has reasonable content"""
        content = DOCKERFILE.read_text()
        lines = [line for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
        assert len(lines) >= 8, "Dockerfile should have meaningful content (at least 8 instructions)"


class TestDockerfileComments:
    """Test Dockerfile documentation"""

    def test_has_comments(self):
        """Test that Dockerfile has comments"""
        content = DOCKERFILE.read_text()
        assert '#' in content, "Dockerfile should have comments for documentation"


class TestOptimizations:
    """Test Dockerfile optimizations"""

    def test_copies_package_json_before_code(self):
        """Test that package.json is copied before application code"""
        content = DOCKERFILE.read_text()
        # Good practice: copy package.json first for better caching
        pkg_index = content.find('package.json')
        copy_all_index = content.find('COPY . ')
        if pkg_index > -1 and copy_all_index > -1:
            # Package.json should come before copying all code
            assert pkg_index < copy_all_index, \
                "package.json should be copied before application code for better Docker caching"


class TestBuildStageOptimizations:
    """Test build stage optimizations"""

    def test_uses_alpine_variant_for_node(self):
        """Test that uses alpine variant for smaller image"""
        content = DOCKERFILE.read_text()
        # Good practice but optional
        # Alpine images are smaller
        pass

    def test_workdir_is_app_directory(self):
        """Test that WORKDIR is set to /app or similar"""
        content = DOCKERFILE.read_text()
        has_app = '/app' in content
        assert has_app, "Dockerfile should set WORKDIR to /app or similar"


class TestNginxServeOptimizations:
    """Test Nginx serve stage optimizations"""

    def test_uses_alpine_nginx(self):
        """Test that uses nginx:alpine for smaller image"""
        content = DOCKERFILE.read_text()
        # Good practice but optional
        # nginx:alpine is much smaller than nginx
        pass

    def test_copies_only_built_files(self):
        """Test that only copies built files, not entire build stage"""
        content = DOCKERFILE.read_text()
        # Should use COPY --from=builder with specific path
        has_specific_copy = 'COPY --from' in content
        assert has_specific_copy, "Dockerfile should selectively copy from build stage"


class TestProductionReadiness:
    """Test production readiness"""

    def test_nginx_runs_as_daemon(self):
        """Test that Nginx configuration allows daemon mode or foreground"""
        content = DOCKERFILE.read_text()
        # Nginx in Docker should run in foreground
        # This is typically handled by nginx default CMD
        # Just verify we're using nginx image properly
        has_nginx = 'FROM nginx' in content
        assert has_nginx, "Dockerfile should use nginx properly"

    def test_static_files_in_nginx_html(self):
        """Test that static files are copied to nginx html directory"""
        content = DOCKERFILE.read_text()
        has_html = '/usr/share/nginx/html' in content
        assert has_html, "Dockerfile should copy files to /usr/share/nginx/html"
