############################################################
# Storage: S3 buckets for artifacts and access logs
############################################################

resource "aws_s3_bucket" "logs" {
  bucket = "${local.name_prefix}-logs"

  lifecycle_rule {
    id      = "expire-old-logs"
    enabled = true

    expiration {
      days = var.log_bucket_expiration_days
    }
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-logs"
      Tier = "logging"
    }
  )
}

resource "aws_s3_bucket_public_access_block" "logs" {
  bucket                  = aws_s3_bucket.logs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}

resource "aws_s3_bucket" "artifacts" {
  bucket        = "${local.name_prefix}-artifacts"
  force_destroy = var.artifact_bucket_force_destroy

  logging {
    target_bucket = aws_s3_bucket.logs.id
    target_prefix = "artifacts/"
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-artifacts"
      Tier = "storage"
    }
  )
}

resource "aws_s3_bucket_public_access_block" "artifacts" {
  bucket                  = aws_s3_bucket.artifacts.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_versioning" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  versioning_configuration {
    status = "Enabled"
  }
}
