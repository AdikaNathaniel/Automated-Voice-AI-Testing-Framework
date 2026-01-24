#!/bin/bash
# PostgreSQL Restore Script
# Restores database from S3/MinIO backup

set -euo pipefail

# Configuration
DB_HOST="${DB_HOST:-postgres}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-voiceai_testing}"
DB_USER="${DB_USER:-postgres}"
BACKUP_DIR="${BACKUP_DIR:-/tmp/backups}"
BACKUP_STORAGE_URL="${BACKUP_STORAGE_URL:-s3://voice-ai-testing-backups/postgres}"

# MinIO/S3 configuration
MINIO_ENDPOINT="${MINIO_ENDPOINT_URL:-http://localhost:9000}"
MINIO_ACCESS_KEY="${MINIO_ACCESS_KEY:-minio_user}"
MINIO_SECRET_KEY="${MINIO_SECRET_KEY:-changeme_minio_s3}"

# Check for backup file argument
if [ -z "${1:-}" ]; then
    echo "Usage: $0 <backup_filename>"
    echo "Example: $0 voiceai_testing_20240101_020000.sql.gz"
    echo ""
    echo "Available backups:"

    if command -v mc &> /dev/null; then
        mc alias set backup "${MINIO_ENDPOINT}" "${MINIO_ACCESS_KEY}" "${MINIO_SECRET_KEY}" --api S3v4
        mc ls "backup/${BACKUP_STORAGE_URL#s3://}/"
    elif command -v aws &> /dev/null; then
        aws s3 ls "${BACKUP_STORAGE_URL}/"
    fi
    exit 1
fi

BACKUP_FILE="$1"
RESTORE_PATH="${BACKUP_DIR}/${BACKUP_FILE}"

echo "[$(date)] Starting PostgreSQL restore..."
echo "[$(date)] Backup file: ${BACKUP_FILE}"

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# Download backup from S3/MinIO
if command -v mc &> /dev/null; then
    mc alias set backup "${MINIO_ENDPOINT}" "${MINIO_ACCESS_KEY}" "${MINIO_SECRET_KEY}" --api S3v4
    mc cp "backup/${BACKUP_STORAGE_URL#s3://}/${BACKUP_FILE}" "${RESTORE_PATH}"
elif command -v aws &> /dev/null; then
    aws s3 cp "${BACKUP_STORAGE_URL}/${BACKUP_FILE}" "${RESTORE_PATH}"
else
    echo "[$(date)] Error: No S3 client found"
    exit 1
fi

echo "[$(date)] Backup downloaded to: ${RESTORE_PATH}"

# Confirm before restore
echo ""
echo "WARNING: This will replace all data in database '${DB_NAME}'"
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "[$(date)] Restore cancelled"
    rm -f "${RESTORE_PATH}"
    exit 0
fi

# Terminate existing connections
echo "[$(date)] Terminating existing connections..."
PGPASSWORD="${DB_PASSWORD:-postgres}" psql \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d postgres \
    -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${DB_NAME}' AND pid <> pg_backend_pid();"

# Drop and recreate database
echo "[$(date)] Recreating database..."
PGPASSWORD="${DB_PASSWORD:-postgres}" psql \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d postgres \
    -c "DROP DATABASE IF EXISTS ${DB_NAME};"

PGPASSWORD="${DB_PASSWORD:-postgres}" psql \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d postgres \
    -c "CREATE DATABASE ${DB_NAME};"

# Restore backup
echo "[$(date)] Restoring database..."
gunzip -c "${RESTORE_PATH}" | PGPASSWORD="${DB_PASSWORD:-postgres}" psql \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d "${DB_NAME}"

# Clean up
rm -f "${RESTORE_PATH}"

echo "[$(date)] PostgreSQL restore completed successfully!"
