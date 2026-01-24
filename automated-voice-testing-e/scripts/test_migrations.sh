#!/bin/bash
# Migration Test Script
# Tests upgrade -> downgrade -> upgrade cycle to validate reversibility

set -euo pipefail

# Configuration
DATABASE_URL="${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/voiceai_testing_test}"
ALEMBIC_DIR="${ALEMBIC_DIR:-/home/ubuntu/workspace/automated-testing}"

echo "============================================"
echo "Migration Reversibility Test"
echo "============================================"
echo ""

# Change to project directory
cd "${ALEMBIC_DIR}"

# Ensure we have a clean test database
echo "[1/7] Setting up test database..."
if command -v createdb &> /dev/null; then
    dropdb --if-exists voiceai_testing_test || true
    createdb voiceai_testing_test || true
fi

# Get current revision (if any)
echo ""
echo "[2/7] Getting current migration state..."
CURRENT_REVISION=$(DATABASE_URL="${DATABASE_URL}" venv/bin/alembic current 2>/dev/null | grep -oE '[a-f0-9]+' | head -1 || echo "base")
echo "Current revision: ${CURRENT_REVISION:-base}"

# Apply all migrations
echo ""
echo "[3/7] Upgrading to head..."
DATABASE_URL="${DATABASE_URL}" venv/bin/alembic upgrade head
echo "Upgrade to head: SUCCESS"

# Get head revision
HEAD_REVISION=$(DATABASE_URL="${DATABASE_URL}" venv/bin/alembic current | grep -oE '[a-f0-9]+' | head -1)
echo "Head revision: ${HEAD_REVISION}"

# Test downgrade to base (validates all migrations are reversible)
echo ""
echo "[4/7] Testing full downgrade to base..."
DATABASE_URL="${DATABASE_URL}" venv/bin/alembic downgrade base
echo "Downgrade to base: SUCCESS"

# Verify we're at base
echo ""
echo "[5/7] Verifying at base..."
AFTER_DOWNGRADE=$(DATABASE_URL="${DATABASE_URL}" venv/bin/alembic current 2>/dev/null | grep -oE '[a-f0-9]+' | head -1 || echo "base")
if [ -n "${AFTER_DOWNGRADE}" ] && [ "${AFTER_DOWNGRADE}" != "base" ]; then
    echo "ERROR: Not at base after downgrade"
    exit 1
fi
echo "At base: SUCCESS"

# Upgrade back to head
echo ""
echo "[6/7] Upgrading back to head..."
DATABASE_URL="${DATABASE_URL}" venv/bin/alembic upgrade head
echo "Re-upgrade to head: SUCCESS"

# Verify we're back at head
echo ""
echo "[7/7] Verifying back at head..."
FINAL_REVISION=$(DATABASE_URL="${DATABASE_URL}" venv/bin/alembic current | grep -oE '[a-f0-9]+' | head -1)
if [ "${FINAL_REVISION}" != "${HEAD_REVISION}" ]; then
    echo "ERROR: Not back at head revision"
    echo "Expected: ${HEAD_REVISION}"
    echo "Got: ${FINAL_REVISION}"
    exit 1
fi
echo "Back at head: SUCCESS"

echo ""
echo "============================================"
echo "Migration Test Results"
echo "============================================"
echo "All migrations are reversible!"
echo ""
echo "Test cycle completed:"
echo "  - Upgrade to head: PASSED"
echo "  - Downgrade to base: PASSED"
echo "  - Re-upgrade to head: PASSED"
echo ""
echo "Final revision: ${FINAL_REVISION}"
echo "============================================"

exit 0
