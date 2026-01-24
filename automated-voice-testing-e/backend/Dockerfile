# Backend Dockerfile for FastAPI Application
# Multi-stage build for optimized production image

# Stage 1: Builder stage
# Using specific version for reproducibility and security
FROM python:3.11.10-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies for building Python packages
# gcc: C compiler
# python3-dev: Python development headers
# libc6-dev: C standard library headers (for stdlib.h, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies with extended timeout for large packages
RUN pip install --no-cache-dir --timeout 600 --retries 3 -r requirements.txt

# Stage 2: Production stage
# Using same pinned version as builder for consistency
FROM python:3.11.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /app

# Install curl for health checks, libpq for PostgreSQL, and ffmpeg for audio processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Copy Python dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create whisper models directory for STT (mounted as volume in docker-compose)
RUN mkdir -p /app/whisper_models

# Copy and set permissions for entrypoint script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh && \
    chown appuser:appgroup /docker-entrypoint.sh

# Adjust permissions for non-root user
RUN chown -R appuser:appgroup /app

# Expose port for FastAPI application
EXPOSE 8000

# Configure health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8000/health || exit 1

# Switch to non-root user
USER appuser

# Use entrypoint script to run migrations and start app
ENTRYPOINT ["/docker-entrypoint.sh"]
