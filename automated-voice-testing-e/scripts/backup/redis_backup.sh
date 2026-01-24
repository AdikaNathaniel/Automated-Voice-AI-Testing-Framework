#!/bin/bash
# Redis Backup Script
# Backs up Redis data to S3/MinIO

set -euo pipefail

# Configuration
REDIS_HOST="${REDIS_HOST:-redis}"
REDIS_PORT="${REDIS_PORT:-6379}"
BACKUP_DIR="${BACKUP_DIR:-/tmp/backups}"
BACKUP_STORAGE_URL="${BACKUP_STORAGE_URL:-s3://voice-ai-testing-backups/redis}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"

# MinIO/S3 configuration
MINIO_ENDPOINT="${MINIO_ENDPOINT_URL:-http://localhost:9000}"
MINIO_ACCESS_KEY="${MINIO_ACCESS_KEY:-minio_user}"
MINIO_SECRET_KEY="${MINIO_SECRET_KEY:-changeme_minio_s3}"

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# Generate backup filename
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="redis_${TIMESTAMP}.rdb.gz"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_FILE}"

echo "[$(date)] Starting Redis backup..."

# Trigger BGSAVE and wait for completion
redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" BGSAVE
sleep 5

# Copy RDB file (typically in /data for Docker)
if [ -f "/data/dump.rdb" ]; then
    gzip -c /data/dump.rdb > "${BACKUP_PATH}"
elif [ -f "/var/lib/redis/dump.rdb" ]; then
    gzip -c /var/lib/redis/dump.rdb > "${BACKUP_PATH}"
else
    echo "[$(date)] Warning: RDB file not found. Attempting to copy from container..."
    docker cp voiceai-redis:/data/dump.rdb /tmp/dump.rdb 2>/dev/null || true
    if [ -f "/tmp/dump.rdb" ]; then
        gzip -c /tmp/dump.rdb > "${BACKUP_PATH}"
        rm -f /tmp/dump.rdb
    else
        echo "[$(date)] Error: Could not locate Redis RDB file"
        exit 1
    fi
fi

echo "[$(date)] Backup created: ${BACKUP_PATH}"
echo "[$(date)] Size: $(du -h ${BACKUP_PATH} | cut -f1)"

# Upload to S3/MinIO
if command -v mc &> /dev/null; then
    mc alias set backup "${MINIO_ENDPOINT}" "${MINIO_ACCESS_KEY}" "${MINIO_SECRET_KEY}" --api S3v4
    mc cp "${BACKUP_PATH}" "backup/${BACKUP_STORAGE_URL#s3://}/${BACKUP_FILE}"
    echo "[$(date)] Backup uploaded to MinIO"
elif command -v aws &> /dev/null; then
    aws s3 cp "${BACKUP_PATH}" "${BACKUP_STORAGE_URL}/${BACKUP_FILE}"
    echo "[$(date)] Backup uploaded to S3"
fi

# Clean up local backup
rm -f "${BACKUP_PATH}"

echo "[$(date)] Redis backup completed successfully!"
