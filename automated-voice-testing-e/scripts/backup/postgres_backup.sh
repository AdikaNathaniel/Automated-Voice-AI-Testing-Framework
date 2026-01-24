#!/bin/bash
# PostgreSQL Automated Backup Script
# Backs up database to S3/MinIO with retention policy

set -euo pipefail

# Configuration from environment
DB_HOST="${DB_HOST:-postgres}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-voiceai_testing}"
DB_USER="${DB_USER:-postgres}"
BACKUP_DIR="${BACKUP_DIR:-/tmp/backups}"
BACKUP_STORAGE_URL="${BACKUP_STORAGE_URL:-s3://voice-ai-testing-backups/postgres}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"

# MinIO/S3 configuration
MINIO_ENDPOINT="${MINIO_ENDPOINT_URL:-http://localhost:9000}"
MINIO_ACCESS_KEY="${MINIO_ACCESS_KEY:-minio_user}"
MINIO_SECRET_KEY="${MINIO_SECRET_KEY:-changeme_minio_s3}"

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# Generate backup filename with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${DB_NAME}_${TIMESTAMP}.sql.gz"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_FILE}"

echo "[$(date)] Starting PostgreSQL backup..."

# Create compressed backup
PGPASSWORD="${DB_PASSWORD:-postgres}" pg_dump \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d "${DB_NAME}" \
    --no-owner \
    --no-acl \
    --format=plain | gzip > "${BACKUP_PATH}"

echo "[$(date)] Backup created: ${BACKUP_PATH}"
echo "[$(date)] Size: $(du -h ${BACKUP_PATH} | cut -f1)"

# Upload to S3/MinIO
if command -v mc &> /dev/null; then
    # Use MinIO client
    mc alias set backup "${MINIO_ENDPOINT}" "${MINIO_ACCESS_KEY}" "${MINIO_SECRET_KEY}" --api S3v4
    mc cp "${BACKUP_PATH}" "backup/${BACKUP_STORAGE_URL#s3://}/${BACKUP_FILE}"
    echo "[$(date)] Backup uploaded to MinIO: ${BACKUP_STORAGE_URL}/${BACKUP_FILE}"
elif command -v aws &> /dev/null; then
    # Use AWS CLI
    aws s3 cp "${BACKUP_PATH}" "${BACKUP_STORAGE_URL}/${BACKUP_FILE}"
    echo "[$(date)] Backup uploaded to S3: ${BACKUP_STORAGE_URL}/${BACKUP_FILE}"
else
    echo "[$(date)] Warning: No S3 client found. Backup stored locally only."
fi

# Clean up local backup
rm -f "${BACKUP_PATH}"

# Apply retention policy - delete old backups
echo "[$(date)] Applying retention policy (${RETENTION_DAYS} days)..."

if command -v mc &> /dev/null; then
    # List and delete old backups from MinIO
    mc find "backup/${BACKUP_STORAGE_URL#s3://}" --older-than "${RETENTION_DAYS}d" --exec "mc rm {}"
elif command -v aws &> /dev/null; then
    # List and delete old backups from S3
    CUTOFF_DATE=$(date -d "${RETENTION_DAYS} days ago" +%Y-%m-%d)
    aws s3 ls "${BACKUP_STORAGE_URL}/" | while read -r line; do
        file_date=$(echo "$line" | awk '{print $1}')
        file_name=$(echo "$line" | awk '{print $4}')
        if [[ "$file_date" < "$CUTOFF_DATE" ]]; then
            aws s3 rm "${BACKUP_STORAGE_URL}/${file_name}"
            echo "[$(date)] Deleted old backup: ${file_name}"
        fi
    done
fi

echo "[$(date)] PostgreSQL backup completed successfully!"
