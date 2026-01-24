#!/bin/bash
# Docker entrypoint script for backend service
# Handles database migrations and optional test data seeding

set -e  # Exit on error

echo "🚀 Starting backend entrypoint..."

# Wait for database to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
until python -c "import psycopg2; psycopg2.connect('${DATABASE_URL}')" 2>/dev/null; do
  echo "   PostgreSQL is unavailable - sleeping"
  sleep 2
done
echo "✅ PostgreSQL is ready!"

# Run database migrations
echo "🔄 Running database migrations..."
alembic upgrade head
echo "✅ Migrations completed!"

# Seed test data if SEED_DATA environment variable is set
if [ "$SEED_DATA" = "true" ]; then
  echo "🌱 Seeding test data..."

  # Run unified seed script (super_admin + demo scenarios)
  if [ -f "scripts/seed_all.py" ]; then
    PYTHONPATH=/app python scripts/seed_all.py
    echo "✅ All seed data created!"
  else
    echo "⚠️  seed_all.py not found, skipping seeding"
  fi

else
  echo "ℹ️  Skipping test data seeding (set SEED_DATA=true to enable)"
fi

# Pre-warm Whisper STT model if enabled (recommended for production)
# This downloads/loads the model at startup so first requests are fast
if [ "$STT_PREWARM" = "true" ]; then
  echo "🎤 Pre-warming Whisper STT model (${STT_MODEL_SIZE:-base})..."
  PYTHONPATH=/app python -c "
from services.stt_service import get_stt_service
import os
print(f'  Model: {os.getenv(\"STT_MODEL_SIZE\", \"base\")}')
print(f'  Device: {os.getenv(\"STT_DEVICE\", \"auto\")}')
print(f'  Download root: {os.getenv(\"STT_DOWNLOAD_ROOT\", \"default cache\")}')
stt = get_stt_service()
# Force model load by accessing the property
_ = stt.model
print('✅ STT model loaded and ready!')
" 2>&1 || echo "⚠️  STT pre-warm failed (non-critical, will load on first request)"
fi

# Start the application (or run custom command if provided)
if [ "$#" -gt 0 ]; then
  echo "🎯 Running custom command: $@"
  exec "$@"
else
  echo "🎯 Starting FastAPI application with Socket.IO..."
  exec uvicorn api.main:socketio_app --host 0.0.0.0 --port 8000
fi
