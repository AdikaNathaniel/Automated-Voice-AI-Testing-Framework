"""
Test suite for Nginx configuration files.

Validates that Nginx configuration includes security headers, TLS settings,
and proper proxy configurations for backend API and frontend.
"""

import pytest
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent
NGINX_DIR = PROJECT_ROOT / "nginx"
NGINX_CONF = NGINX_DIR / "nginx.conf"
API_CONF = NGINX_DIR / "conf.d" / "api.conf"
FRONTEND_CONF = NGINX_DIR / "conf.d" / "frontend.conf"


class TestNginxFilesExist:
    """Verify all Nginx configuration files exist."""

    def test_nginx_directory_exists(self):
        """nginx directory should exist."""
        assert NGINX_DIR.exists(), "nginx directory should exist"

    def test_nginx_conf_exists(self):
        """nginx.conf should exist."""
        assert NGINX_CONF.exists(), "nginx/nginx.conf should exist"

    def test_conf_d_directory_exists(self):
        """conf.d directory should exist."""
        conf_d = NGINX_DIR / "conf.d"
        assert conf_d.exists(), "nginx/conf.d directory should exist"

    def test_api_conf_exists(self):
        """api.conf should exist."""
        assert API_CONF.exists(), "nginx/conf.d/api.conf should exist"

    def test_frontend_conf_exists(self):
        """frontend.conf should exist."""
        assert FRONTEND_CONF.exists(), "nginx/conf.d/frontend.conf should exist"


class TestNginxMainConfiguration:
    """Test main nginx.conf configuration."""

    @pytest.fixture
    def nginx_content(self):
        if NGINX_CONF.exists():
            return NGINX_CONF.read_text()
        return ""

    def test_includes_conf_d(self, nginx_content):
        """Should include conf.d/*.conf files."""
        assert "include" in nginx_content and "conf.d" in nginx_content, \
            "nginx.conf should include conf.d configurations"

    def test_has_worker_processes(self, nginx_content):
        """Should configure worker processes."""
        assert "worker_processes" in nginx_content, \
            "nginx.conf should configure worker_processes"

    def test_has_error_log(self, nginx_content):
        """Should configure error logging."""
        assert "error_log" in nginx_content, \
            "nginx.conf should configure error_log"


class TestSecurityHeaders:
    """Test security headers in Nginx configuration."""

    @pytest.fixture
    def all_config_content(self):
        content = ""
        for conf_file in [NGINX_CONF, API_CONF, FRONTEND_CONF]:
            if conf_file.exists():
                content += conf_file.read_text()
        return content

    def test_has_hsts_header(self, all_config_content):
        """Should have HSTS (Strict-Transport-Security) header."""
        assert "Strict-Transport-Security" in all_config_content, \
            "Configuration should include HSTS header"

    def test_has_x_frame_options(self, all_config_content):
        """Should have X-Frame-Options header."""
        assert "X-Frame-Options" in all_config_content, \
            "Configuration should include X-Frame-Options header"

    def test_has_x_content_type_options(self, all_config_content):
        """Should have X-Content-Type-Options header."""
        assert "X-Content-Type-Options" in all_config_content, \
            "Configuration should include X-Content-Type-Options header"

    def test_has_csp_header(self, all_config_content):
        """Should have Content-Security-Policy header."""
        assert "Content-Security-Policy" in all_config_content, \
            "Configuration should include Content-Security-Policy header"

    def test_has_x_xss_protection(self, all_config_content):
        """Should have X-XSS-Protection header."""
        assert "X-XSS-Protection" in all_config_content, \
            "Configuration should include X-XSS-Protection header"


class TestTLSConfiguration:
    """Test TLS/HTTPS configuration."""

    @pytest.fixture
    def all_config_content(self):
        content = ""
        for conf_file in [NGINX_CONF, API_CONF, FRONTEND_CONF]:
            if conf_file.exists():
                content += conf_file.read_text()
        return content

    def test_has_ssl_certificate(self, all_config_content):
        """Should configure SSL certificate path."""
        assert "ssl_certificate" in all_config_content, \
            "Configuration should include ssl_certificate path"

    def test_has_ssl_certificate_key(self, all_config_content):
        """Should configure SSL certificate key path."""
        assert "ssl_certificate_key" in all_config_content, \
            "Configuration should include ssl_certificate_key path"

    def test_has_ssl_protocols(self, all_config_content):
        """Should configure SSL protocols."""
        assert "ssl_protocols" in all_config_content, \
            "Configuration should include ssl_protocols"

    def test_uses_tls12_or_higher(self, all_config_content):
        """Should use TLS 1.2 or higher."""
        has_tls12 = "TLSv1.2" in all_config_content
        has_tls13 = "TLSv1.3" in all_config_content
        assert has_tls12 or has_tls13, \
            "Configuration should use TLS 1.2 or 1.3"


class TestApiProxyConfiguration:
    """Test backend API proxy configuration."""

    @pytest.fixture
    def api_content(self):
        if API_CONF.exists():
            return API_CONF.read_text()
        return ""

    def test_has_upstream_definition(self, api_content):
        """Should define upstream for backend."""
        assert "upstream" in api_content, \
            "api.conf should define upstream for backend"

    def test_has_proxy_pass(self, api_content):
        """Should have proxy_pass directive."""
        assert "proxy_pass" in api_content, \
            "api.conf should have proxy_pass directive"

    def test_has_proxy_headers(self, api_content):
        """Should set proxy headers."""
        has_host = "proxy_set_header" in api_content and "Host" in api_content
        assert has_host, \
            "api.conf should set proxy headers"

    def test_has_websocket_support(self, api_content):
        """Should support WebSocket connections."""
        has_upgrade = "Upgrade" in api_content
        has_connection = "Connection" in api_content
        assert has_upgrade and has_connection, \
            "api.conf should support WebSocket connections"


class TestFrontendConfiguration:
    """Test frontend serving configuration."""

    @pytest.fixture
    def frontend_content(self):
        if FRONTEND_CONF.exists():
            return FRONTEND_CONF.read_text()
        return ""

    def test_has_root_directive(self, frontend_content):
        """Should have root directive for static files."""
        assert "root" in frontend_content, \
            "frontend.conf should have root directive"

    def test_has_index_directive(self, frontend_content):
        """Should have index directive."""
        assert "index" in frontend_content, \
            "frontend.conf should have index directive"

    def test_has_try_files_for_spa(self, frontend_content):
        """Should have try_files for SPA routing."""
        assert "try_files" in frontend_content, \
            "frontend.conf should have try_files for SPA routing"

    def test_has_gzip_configuration(self, frontend_content):
        """Should enable gzip compression."""
        assert "gzip" in frontend_content, \
            "frontend.conf should enable gzip compression"
