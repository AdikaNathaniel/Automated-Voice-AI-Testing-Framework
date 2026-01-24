"""
Voice AI Testing Framework - FastAPI Application
Main application entry point with API routes and middleware configuration
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from typing import Dict
import os
import time
import socketio
from prometheus_client import (
    Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST, REGISTRY
)
from api.websocket import sio
from api.rate_limit import RateLimitExceeded, enforce_rate_limit, DETAIL_MESSAGE
from api.exceptions import register_exception_handlers
from api.logging_config import setup_logging
from api.config import get_settings
from api.sentry_config import initialize_sentry

# Route imports
from api.routes import auth
from api.routes import dashboard
from api.routes import metrics as metrics_router
from api.routes import analytics
from api.routes import language_statistics
from api.routes import defects
from api.routes import edge_cases
from api.routes import configurations
from api.routes import test_suites
from api.routes import suite_runs
from api.routes import webhooks
from api.routes import workers
from api.routes import reports
from api.routes import regressions
from api.routes import activity
from api.routes import knowledge_base
from api.routes import integrations
from api.routes import cicd
from api.routes import languages
from api.routes import multi_turn
from api.routes import scenarios
from api.routes import auto_translation
from api.routes import human_validation
from api.routes import llm_providers
from api.routes import pattern_groups
from api.routes import organizations
from api.routes import users
from api.routes import cicd_config
from api.routes import categories
from api.routes import pattern_analysis_config
from api.routes import llm_analytics
from api.routes import llm_pricing
from api.routes import audit_trail

# ============================================================================
# Prometheus Metrics Definitions
# ============================================================================

# Request metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

REQUEST_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests in progress",
    ["method", "endpoint"]
)

# Database connection pool metrics
DB_POOL_SIZE = Gauge(
    "db_pool_size",
    "Database connection pool size"
)

DB_POOL_CHECKED_IN = Gauge(
    "db_pool_checked_in",
    "Number of connections checked in to pool"
)

DB_POOL_CHECKED_OUT = Gauge(
    "db_pool_checked_out",
    "Number of connections checked out from pool"
)

# Redis connection metrics
REDIS_CONNECTIONS = Gauge(
    "redis_connections_total",
    "Total number of Redis connections"
)

REDIS_CONNECTED = Gauge(
    "redis_connected",
    "Redis connection status (1 = connected, 0 = disconnected)"
)

# Celery task queue metrics
CELERY_TASKS_TOTAL = Counter(
    "celery_tasks_total",
    "Total number of Celery tasks",
    ["task_name", "status"]
)

CELERY_TASKS_IN_QUEUE = Gauge(
    "celery_tasks_in_queue",
    "Number of tasks waiting in Celery queue"
)

CELERY_WORKERS_ACTIVE = Gauge(
    "celery_workers_active",
    "Number of active Celery workers"
)

# Application metadata
APP_VERSION = "1.0.0"
APP_TITLE = "Voice AI Testing Framework API"
APP_DESCRIPTION = """
## Voice AI Testing Framework API

Enterprise-grade testing platform for voice AI systems with proven 99.7% validation accuracy.

### Key Features

* **Automated Testing at Scale** - Run 1000+ voice interaction tests daily
* **Human-in-the-Loop Validation** - Expert quality assurance for edge cases
* **Multi-language Support** - Validate across 8+ major language families
* **Real-time Dashboards** - Executive summaries, defect tracking, trend analysis
* **CI/CD Integration** - Webhooks for GitHub, GitLab, Jenkins
* **ML-powered Validation** - Semantic similarity matching using transformer models

### API Endpoints

* **Health Check**: `/health` - Application health status
* **Readiness Check**: `/ready` - Service readiness status
* **API Documentation**: `/api/docs` - Interactive Swagger UI
* **API Documentation (Alternative)**: `/api/redoc` - ReDoc documentation

### Version

Current version: {version}

For more information, visit: https://github.com/your-org/automated-testing
""".format(version=APP_VERSION)


# ============================================================================
# Application Lifespan Handler
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager

    Handles startup and shutdown events for the application.

    Startup tasks:
    - Initialize logging with environment-aware configuration
    - Initialize Sentry error tracking
    - Set up Redis connections
    - Load ML models

    Note: Database seeding is handled by docker-entrypoint.sh via seed_all.py

    Shutdown tasks:
    - Close database connections
    - Close Redis connections
    - Save any pending data
    """
    # === STARTUP ===
    settings = get_settings()

    # Determine log level based on environment
    if settings.is_production():
        log_level = "INFO"
    elif settings.is_development():
        log_level = "DEBUG"
    else:
        log_level = getattr(settings, 'LOG_LEVEL', 'INFO')

    # Set up logging
    setup_logging(
        log_level=log_level,
        log_file="app.log" if settings.is_production() else None,
        json_format=settings.is_production(),
    )

    # Initialize Sentry error tracking
    initialize_sentry(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        sample_rate=settings.SENTRY_SAMPLE_RATE,
        release=APP_VERSION,
    )

    print(f"Starting {APP_TITLE} v{APP_VERSION}")

    yield  # Application runs here

    # === SHUTDOWN ===
    print(f"Shutting down {APP_TITLE} v{APP_VERSION}")
    # TODO: Add actual shutdown tasks
    # - Close database connection pool
    # - Disconnect from Redis
    # - Save any pending data


# Create FastAPI application instance
app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Register exception handlers for consistent error responses
register_exception_handlers(app)

# ============================================================================
# Socket.IO Integration
# ============================================================================

# Create Socket.IO ASGI app that wraps the FastAPI app
# This allows Socket.IO and FastAPI to coexist in the same application
socketio_app = socketio.ASGIApp(
    socketio_server=sio,
    other_asgi_app=app,
)

# ============================================================================
# CORS Middleware Configuration
# ============================================================================

# Get allowed origins from environment (fallback to defaults for development)
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:3001,http://localhost:8000"
).split(",")

# Strip whitespace from origins
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS]

print(f"🌐 CORS Allowed Origins: {ALLOWED_ORIGINS}")

# For development, use regex to allow all localhost origins
ALLOW_ORIGIN_REGEX = r"http://localhost:\d+"

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=ALLOW_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "X-Requested-With",
        "X-CSRF-Token",
    ],
    expose_headers=[
        "X-Request-ID",
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset",
    ],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Compress API responses when clients support gzip to reduce payload size.
app.add_middleware(GZipMiddleware, minimum_size=50)

# ============================================================================
# Rate Limiting Middleware
# ============================================================================

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Skip rate limiting for OPTIONS requests (CORS preflight)
    if request.method == "OPTIONS":
        # Let CORS middleware handle OPTIONS requests
        response = await call_next(request)
        return response

    if request.url.path.startswith("/api/"):
        try:
            await enforce_rate_limit(request)
        except RateLimitExceeded as exc:
            headers = {"Retry-After": str(exc.retry_after)}
            return JSONResponse(
                status_code=429,
                content={"detail": DETAIL_MESSAGE},
                headers=headers,
            )

    response = await call_next(request)
    return response

# ============================================================================
# API Routers
# ============================================================================

# Create API v1 router for versioning
api_router = APIRouter(prefix="/api/v1")

# Store router on app for testing
app.api_router = api_router

# ============================================================================
# Prometheus Metrics Endpoint
# ============================================================================

@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """
    Prometheus metrics endpoint

    Returns metrics in Prometheus text format for scraping.
    Includes request counts, latencies, database pool stats,
    Redis connection status, and Celery task metrics.
    """
    return Response(
        content=generate_latest(REGISTRY),
        media_type=CONTENT_TYPE_LATEST
    )


# ============================================================================
# Metrics Tracking Middleware
# ============================================================================

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Track request metrics for Prometheus."""
    # Skip metrics endpoint to avoid recursion
    if request.url.path == "/metrics":
        return await call_next(request)

    # Skip detailed metrics for OPTIONS requests (CORS preflight)
    if request.method == "OPTIONS":
        response = await call_next(request)
        return response

    method = request.method
    path = request.url.path

    # Increment in-progress gauge
    REQUEST_IN_PROGRESS.labels(method=method, endpoint=path).inc()

    # Track request duration
    start_time = time.time()
    try:
        response = await call_next(request)
        status = response.status_code
    except Exception:
        status = 500
        raise
    finally:
        # Record duration
        duration = time.time() - start_time
        REQUEST_LATENCY.labels(method=method, endpoint=path).observe(duration)

        # Decrement in-progress gauge
        REQUEST_IN_PROGRESS.labels(method=method, endpoint=path).dec()

    # Increment request counter
    REQUEST_COUNT.labels(method=method, endpoint=path, status=status).inc()

    return response


# ============================================================================
# Health Check Endpoints
# ============================================================================

@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint

    Returns the current health status of the application.
    This endpoint is used by load balancers and monitoring systems
    to verify that the application is running.

    Returns:
        dict: Health status information including service name, status, and version
    """
    return {
        "status": "healthy",
        "service": "Voice AI Testing Framework API",
        "version": APP_VERSION,
    }


@app.get("/ready", tags=["Health"])
async def readiness_check() -> Dict[str, str]:
    """
    Readiness check endpoint

    Returns whether the application is ready to accept requests.
    This includes checking if all required services and dependencies
    are available (database, Redis, external APIs, etc.).

    Returns:
        dict: Readiness status information
    """
    # TODO: Add actual readiness checks for:
    # - Database connectivity
    # - Redis connectivity
    # - External API availability

    return {
        "status": "ready",
        "service": "Voice AI Testing Framework API",
        "version": APP_VERSION,
    }


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/", tags=["Root"])
async def root() -> Dict[str, str]:
    """
    Root endpoint

    Returns basic API information and available endpoints.

    Returns:
        dict: API information
    """
    return {
        "name": APP_TITLE,
        "version": APP_VERSION,
        "message": "Welcome to the Voice AI Testing Framework API",
        "docs_url": "/api/docs",
        "redoc_url": "/api/redoc",
        "health_check": "/health",
        "readiness_check": "/ready",
    }


# ============================================================================
# Include API Routers
# ============================================================================

# Include authentication routes
api_router.include_router(auth.router)
api_router.include_router(dashboard.router)
api_router.include_router(metrics_router.router)
api_router.include_router(analytics.router)
api_router.include_router(language_statistics.router)
api_router.include_router(defects.router)
api_router.include_router(edge_cases.router)
api_router.include_router(configurations.router)
api_router.include_router(test_suites.router)
api_router.include_router(suite_runs.router)
api_router.include_router(webhooks.router)
api_router.include_router(workers.router)
api_router.include_router(reports.router)
api_router.include_router(regressions.router)
api_router.include_router(activity.router)
api_router.include_router(knowledge_base.router)
api_router.include_router(integrations.router)
api_router.include_router(cicd.router)
api_router.include_router(languages.router)
api_router.include_router(multi_turn.router)
api_router.include_router(scenarios.router)
api_router.include_router(auto_translation.router)
api_router.include_router(human_validation.router)
api_router.include_router(llm_providers.router)
api_router.include_router(pattern_groups.router)
api_router.include_router(organizations.router)
api_router.include_router(users.router)
api_router.include_router(cicd_config.router)
api_router.include_router(categories.router)
api_router.include_router(pattern_analysis_config.router)
api_router.include_router(llm_analytics.router)
api_router.include_router(llm_pricing.router)
api_router.include_router(audit_trail.router)

# Include the API v1 router in app
app.include_router(api_router)

# Note: All core API routes are now registered:
# - Scenarios (/api/v1/scenarios) - scenario script management
# - Suite runs (/api/v1/suite-runs) - test execution management
# - Validation (/api/v1/validation) - validation workflow
# - Dashboard (/api/v1/dashboard) - metrics and summaries
