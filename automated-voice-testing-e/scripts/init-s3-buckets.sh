#!/bin/bash
# Initialize S3 buckets for Voice AI Testing Framework (TASK-114)
#
# This script creates the required S3 buckets in MinIO (or AWS S3).
# It can be run manually or is automatically executed by the createbuckets
# service in docker-compose.yml.
#
# Required buckets:
# - input-audio: Stores input audio files for testing
# - output-audio: Stores output audio files from TTS
# - artifacts: Stores test artifacts and logs
#
# Usage:
#   ./scripts/init-s3-buckets.sh
#
# Environment variables:
#   MINIO_ENDPOINT: MinIO endpoint URL (default: http://localhost:9000)
#   MINIO_ACCESS_KEY: MinIO access key (default: minioadmin)
#   MINIO_SECRET_KEY: MinIO secret key (default: minioadmin123)

set -e  # Exit on error

# Configuration
MINIO_ENDPOINT=${MINIO_ENDPOINT:-http://localhost:9000}
MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY:-minioadmin}
MINIO_SECRET_KEY=${MINIO_SECRET_KEY:-minioadmin123}
MINIO_ALIAS="myminio"

# Required buckets
BUCKETS=(
  "input-audio"
  "output-audio"
  "artifacts"
)

echo "========================================="
echo "S3 Bucket Initialization Script"
echo "========================================="
echo ""
echo "MinIO Endpoint: $MINIO_ENDPOINT"
echo "Buckets to create: ${BUCKETS[*]}"
echo ""

# Check if mc (MinIO Client) is installed
if ! command -v mc &> /dev/null; then
    echo "Error: MinIO Client (mc) is not installed"
    echo "Please install it from: https://min.io/docs/minio/linux/reference/minio-mc.html"
    echo ""
    echo "Or run this script inside the createbuckets Docker container"
    exit 1
fi

# Configure MinIO client
echo "Configuring MinIO client..."
mc alias set $MINIO_ALIAS $MINIO_ENDPOINT $MINIO_ACCESS_KEY $MINIO_SECRET_KEY

# Wait for MinIO to be ready
echo "Waiting for MinIO to be ready..."
for i in {1..30}; do
    if mc admin info $MINIO_ALIAS &> /dev/null; then
        echo "MinIO is ready!"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 1
done

# Verify connection
if ! mc admin info $MINIO_ALIAS &> /dev/null; then
    echo "Error: Cannot connect to MinIO at $MINIO_ENDPOINT"
    exit 1
fi

# Create buckets
echo ""
echo "Creating buckets..."
for bucket in "${BUCKETS[@]}"; do
    echo "Creating bucket: $bucket"

    # Create bucket (ignore if already exists)
    if mc mb $MINIO_ALIAS/$bucket --ignore-existing; then
        echo "  ✓ Bucket '$bucket' created successfully"
    else
        echo "  ! Bucket '$bucket' already exists"
    fi

    # Set public download policy (for easier access in development)
    # In production, you should use more restrictive policies
    echo "  Setting download policy for '$bucket'"
    mc anonymous set download $MINIO_ALIAS/$bucket
done

# List all buckets
echo ""
echo "========================================="
echo "Bucket Creation Complete!"
echo "========================================="
echo ""
echo "Available buckets:"
mc ls $MINIO_ALIAS

echo ""
echo "Bucket details:"
for bucket in "${BUCKETS[@]}"; do
    echo ""
    echo "Bucket: $bucket"
    mc stat $MINIO_ALIAS/$bucket
done

echo ""
echo "========================================="
echo "MinIO Console URL: http://localhost:9001"
echo "MinIO API URL: http://localhost:9000"
echo "Username: $MINIO_ACCESS_KEY"
echo "========================================="
