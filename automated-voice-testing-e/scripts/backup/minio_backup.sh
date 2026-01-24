#!/bin/bash
# MinIO Bucket Backup Script
# Mirrors MinIO buckets to external S3 for disaster recovery

set -euo pipefail

# Configuration
MINIO_ENDPOINT="${MINIO_ENDPOINT_URL:-http://localhost:9000}"
MINIO_ACCESS_KEY="${MINIO_ACCESS_KEY:-minio_user}"
MINIO_SECRET_KEY="${MINIO_SECRET_KEY:-changeme_minio_s3}"
BACKUP_STORAGE_URL="${BACKUP_STORAGE_URL:-s3://voice-ai-testing-backups/minio}"

# Buckets to backup
BUCKETS=("input-audio" "output-audio" "artifacts")

echo "[$(date)] Starting MinIO backup..."

# Setup MinIO client alias
if ! command -v mc &> /dev/null; then
    echo "[$(date)] Error: MinIO client (mc) not found"
    exit 1
fi

mc alias set myminio "${MINIO_ENDPOINT}" "${MINIO_ACCESS_KEY}" "${MINIO_SECRET_KEY}" --api S3v4

# If backing up to external S3
if [[ "${BACKUP_STORAGE_URL}" == s3://* ]]; then
    mc alias set backup s3 "${AWS_ACCESS_KEY_ID}" "${AWS_SECRET_ACCESS_KEY}" --api S3v4

    for bucket in "${BUCKETS[@]}"; do
        echo "[$(date)] Mirroring bucket: ${bucket}"
        mc mirror --overwrite "myminio/${bucket}" "backup/${BACKUP_STORAGE_URL#s3://}/${bucket}"
    done
else
    # Local backup
    BACKUP_DIR="${BACKUP_DIR:-/tmp/backups/minio}"
    mkdir -p "${BACKUP_DIR}"

    for bucket in "${BUCKETS[@]}"; do
        echo "[$(date)] Backing up bucket: ${bucket}"
        mc mirror --overwrite "myminio/${bucket}" "${BACKUP_DIR}/${bucket}"
    done
fi

echo "[$(date)] MinIO backup completed successfully!"
